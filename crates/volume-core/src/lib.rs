#![forbid(unsafe_code)]
//! Checked logical volume slices. Partition-table and pool discovery are not implemented.

use dioryx_storage::{BlockDevice, Geometry, StorageCapabilities, StorageError};
use std::sync::Arc;
use thiserror::Error;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct VolumeId(pub u128);

#[derive(Clone, Copy, Debug)]
pub struct VolumeInfo {
    pub id: VolumeId,
    pub geometry: Geometry,
}

#[derive(Debug, Error)]
pub enum VolumeError {
    #[error("volume is not present")]
    NotFound,
    #[error("volume discovery limit exceeded")]
    Limit,
    #[error(transparent)]
    Storage(#[from] StorageError),
}

pub trait VolumePool: Send + Sync {
    fn volumes(&self, limit: usize) -> Result<Vec<VolumeInfo>, VolumeError>;
    fn open(&self, id: VolumeId) -> Result<Arc<dyn BlockDevice>, VolumeError>;
}

pub struct SliceDevice {
    source: Arc<dyn BlockDevice>,
    offset: u64,
    geometry: Geometry,
}

impl SliceDevice {
    pub fn new(source: Arc<dyn BlockDevice>, offset: u64, len: u64) -> Result<Self, StorageError> {
        dioryx_storage::validate_device(source.as_ref())?;
        let upstream = source.geometry();
        if !offset.is_multiple_of(u64::from(upstream.logical_sector())) {
            return Err(StorageError::Misaligned);
        }
        if offset
            .checked_add(len)
            .is_none_or(|end| end > upstream.len())
        {
            return Err(StorageError::OutOfBounds);
        }
        let geometry = Geometry::new(len, upstream.logical_sector(), upstream.physical_sector())?;
        Ok(Self {
            source,
            offset,
            geometry,
        })
    }
}

impl BlockDevice for SliceDevice {
    fn geometry(&self) -> Geometry {
        self.geometry
    }
    fn capabilities(&self) -> StorageCapabilities {
        StorageCapabilities::READ_ONLY
    }
    fn generation(&self) -> u64 {
        self.source.generation()
    }
    fn read_exact_at(&self, offset: u64, output: &mut [u8]) -> Result<(), StorageError> {
        self.geometry.check_range(offset, output.len())?;
        let absolute = self
            .offset
            .checked_add(offset)
            .ok_or(StorageError::OutOfBounds)?;
        self.source.read_exact_at(absolute, output)
    }
    fn writable(&self) -> Option<&dyn dioryx_storage::WritableBlockDevice> {
        None
    }
}

pub struct SingleVolumePool {
    id: VolumeId,
    device: Arc<dyn BlockDevice>,
}

impl SingleVolumePool {
    pub fn new(id: VolumeId, device: Arc<dyn BlockDevice>) -> Self {
        Self { id, device }
    }
}

impl VolumePool for SingleVolumePool {
    fn volumes(&self, limit: usize) -> Result<Vec<VolumeInfo>, VolumeError> {
        if limit == 0 {
            return Err(VolumeError::Limit);
        }
        Ok(vec![VolumeInfo {
            id: self.id,
            geometry: self.device.geometry(),
        }])
    }
    fn open(&self, id: VolumeId) -> Result<Arc<dyn BlockDevice>, VolumeError> {
        if id != self.id {
            return Err(VolumeError::NotFound);
        }
        dioryx_storage::validate_device(self.device.as_ref())?;
        Ok(Arc::clone(&self.device))
    }
}
