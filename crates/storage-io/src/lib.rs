#![forbid(unsafe_code)]
//! Bounded positional I/O and an ordered-write contract. The seed implements reads only.

use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;
use std::sync::{Arc, Mutex};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum StorageError {
    #[error("I/O: {0}")]
    Io(#[from] std::io::Error),
    #[error("invalid sector geometry")]
    InvalidGeometry,
    #[error("range exceeds the source")]
    OutOfBounds,
    #[error("operation is not sector aligned")]
    Misaligned,
    #[error("poisoned source lock")]
    Poisoned,
    #[error("source is not a regular file")]
    NotRegularFile,
    #[error("read-only source")]
    ReadOnly,
    #[error("unsupported durability barrier")]
    UnsupportedBarrier,
    #[error("invalid or overlapping write batch")]
    InvalidBatch,
    #[error("resource limit exceeded")]
    ResourceLimit,
    #[error("stale source generation")]
    StaleGeneration,
    #[error("writable capability and mutation access disagree")]
    InvalidCapabilities,
}

pub type Result<T> = std::result::Result<T, StorageError>;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Geometry {
    len: u64,
    logical_sector: u32,
    physical_sector: u32,
}

impl Geometry {
    pub fn new(len: u64, logical_sector: u32, physical_sector: u32) -> Result<Self> {
        if !logical_sector.is_power_of_two()
            || !physical_sector.is_power_of_two()
            || physical_sector < logical_sector
            || !len.is_multiple_of(u64::from(logical_sector))
        {
            return Err(StorageError::InvalidGeometry);
        }
        Ok(Self {
            len,
            logical_sector,
            physical_sector,
        })
    }

    pub fn len(self) -> u64 {
        self.len
    }
    pub fn is_empty(self) -> bool {
        self.len == 0
    }
    pub fn logical_sector(self) -> u32 {
        self.logical_sector
    }
    pub fn physical_sector(self) -> u32 {
        self.physical_sector
    }

    pub fn check_range(self, offset: u64, len: usize) -> Result<()> {
        let len = u64::try_from(len).map_err(|_| StorageError::OutOfBounds)?;
        if offset.checked_add(len).is_none_or(|end| end > self.len) {
            return Err(StorageError::OutOfBounds);
        }
        Ok(())
    }

    pub fn check_aligned(self, offset: u64, len: usize) -> Result<()> {
        self.check_range(offset, len)?;
        if !offset.is_multiple_of(u64::from(self.logical_sector))
            || !len.is_multiple_of(self.logical_sector as usize)
        {
            return Err(StorageError::Misaligned);
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum FlushBarrier {
    Data,
    DataAndMetadata,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct StorageCapabilities {
    pub writable: bool,
    pub strongest_barrier: Option<FlushBarrier>,
    /// Zero means no atomic-write guarantee. A barrier never implies atomicity.
    pub atomic_write_bytes: u32,
}

impl StorageCapabilities {
    pub const READ_ONLY: Self = Self {
        writable: false,
        strongest_barrier: None,
        atomic_write_bytes: 0,
    };
}

pub trait BlockDevice: Send + Sync {
    fn geometry(&self) -> Geometry;
    fn capabilities(&self) -> StorageCapabilities;
    /// Changes invalidate every cache entry for the previous generation.
    fn generation(&self) -> u64;
    /// Fill the entire buffer or return an error; a partial buffer is not valid data.
    fn read_exact_at(&self, offset: u64, output: &mut [u8]) -> Result<()>;
    /// Preserves mutation access through trait-object container/volume handles.
    /// Must be Some exactly when capabilities().writable is true.
    fn writable(&self) -> Option<&dyn WritableBlockDevice>;
}

/// Admit a device before returning it from a container/pool or accepting writes.
pub fn validate_device(device: &dyn BlockDevice) -> Result<()> {
    if device.capabilities().writable != device.writable().is_some() {
        return Err(StorageError::InvalidCapabilities);
    }
    Ok(())
}

pub struct FileDevice {
    file: Mutex<File>,
    geometry: Geometry,
}

impl FileDevice {
    /// Opens a regular image read-only. The caller must prevent external mutation.
    /// This seed does not provide a cross-process lock, raw devices, or a cache.
    pub fn open(path: impl AsRef<Path>, logical_sector: u32) -> Result<Self> {
        let file = File::open(path)?;
        let metadata = file.metadata()?;
        if !metadata.is_file() {
            return Err(StorageError::NotRegularFile);
        }
        let geometry = Geometry::new(metadata.len(), logical_sector, logical_sector)?;
        Ok(Self {
            file: Mutex::new(file),
            geometry,
        })
    }
}

impl BlockDevice for FileDevice {
    fn geometry(&self) -> Geometry {
        self.geometry
    }
    fn capabilities(&self) -> StorageCapabilities {
        StorageCapabilities::READ_ONLY
    }
    fn generation(&self) -> u64 {
        0
    }
    fn read_exact_at(&self, offset: u64, output: &mut [u8]) -> Result<()> {
        self.geometry.check_range(offset, output.len())?;
        let mut file = self.file.lock().map_err(|_| StorageError::Poisoned)?;
        file.seek(SeekFrom::Start(offset))?;
        file.read_exact(output)?;
        Ok(())
    }
    fn writable(&self) -> Option<&dyn WritableBlockDevice> {
        None
    }
}

#[derive(Clone, Debug)]
pub struct WriteOp {
    pub offset: u64,
    pub bytes: Arc<[u8]>,
}

#[derive(Clone, Debug)]
pub struct FlushGroup {
    pub writes: Vec<WriteOp>,
    pub barrier: FlushBarrier,
}

#[derive(Clone, Debug)]
pub struct WriteBatch {
    pub expected_generation: u64,
    pub groups: Vec<FlushGroup>,
}

impl WriteBatch {
    /// Validate everything before I/O. Cross-group overwrites are intentional;
    /// overlapping writes within one group have ambiguous ordering and are rejected.
    pub fn validate(&self, device: &dyn BlockDevice, max_bytes: u64) -> Result<()> {
        validate_device(device)?;
        let caps = device.capabilities();
        if !caps.writable {
            return Err(StorageError::ReadOnly);
        }
        if self.expected_generation != device.generation() {
            return Err(StorageError::StaleGeneration);
        }
        if self.groups.is_empty() || self.groups.len() > 64 {
            return Err(StorageError::ResourceLimit);
        }
        let mut total = 0_u64;
        for group in &self.groups {
            if caps
                .strongest_barrier
                .is_none_or(|barrier| barrier < group.barrier)
            {
                return Err(StorageError::UnsupportedBarrier);
            }
            if group.writes.is_empty() || group.writes.len() > 4096 {
                return Err(StorageError::ResourceLimit);
            }
            let mut ranges = Vec::with_capacity(group.writes.len());
            for write in &group.writes {
                if write.bytes.is_empty() {
                    return Err(StorageError::InvalidBatch);
                }
                device
                    .geometry()
                    .check_aligned(write.offset, write.bytes.len())?;
                let len =
                    u64::try_from(write.bytes.len()).map_err(|_| StorageError::ResourceLimit)?;
                total = total.checked_add(len).ok_or(StorageError::ResourceLimit)?;
                if total > max_bytes {
                    return Err(StorageError::ResourceLimit);
                }
                let end = write
                    .offset
                    .checked_add(len)
                    .ok_or(StorageError::OutOfBounds)?;
                ranges.push((write.offset, end));
            }
            ranges.sort_unstable();
            if ranges.windows(2).any(|pair| pair[0].1 > pair[1].0) {
                return Err(StorageError::InvalidBatch);
            }
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct CommitReceipt {
    pub generation: u64,
    pub durable_groups: usize,
    pub barrier: FlushBarrier,
}

#[derive(Debug, Error)]
pub enum WriteFailure {
    #[error("rejected before any write: {0}")]
    Rejected(#[source] StorageError),
    #[error("indeterminate write; {durable_groups} groups confirmed, source fenced")]
    Indeterminate {
        durable_groups: usize,
        invalidated_generation: u64,
        #[source]
        source: StorageError,
    },
}

/// Implementations serialize batches, persist each group before the next group,
/// and return a receipt only after the final requested hardware/OS barrier succeeds.
/// Any possibly partial failure changes the generation, invalidates cached data,
/// and fences further writes until explicit recovery. This is ordered persistence,
/// not rollback or filesystem transaction atomicity. No implementation ships yet.
pub trait WritableBlockDevice: BlockDevice {
    fn submit(&self, batch: WriteBatch) -> std::result::Result<CommitReceipt, WriteFailure>;
    fn flush(&self, barrier: FlushBarrier) -> std::result::Result<CommitReceipt, WriteFailure>;
}
