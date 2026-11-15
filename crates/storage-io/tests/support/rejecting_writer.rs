//! Test-only capability/failure double. It never claims successful persistence.
use std::path::Path;
use storage_io::*;

pub struct RejectingWriter {
    pub file: FileDevice,
    pub caps: StorageCapabilities,
    pub expose_writer: bool,
}

impl RejectingWriter {
    pub fn new(path: &Path, sector: u32) -> Result<Self> {
        Ok(Self {
            file: FileDevice::open(path, sector)?,
            caps: StorageCapabilities {
                writable: true,
                strongest_barrier: Some(FlushBarrier::DataAndMetadata),
                atomic_write_bytes: 0,
            },
            expose_writer: true,
        })
    }
}

impl BlockDevice for RejectingWriter {
    fn geometry(&self) -> Geometry {
        self.file.geometry()
    }
    fn capabilities(&self) -> StorageCapabilities {
        self.caps
    }
    fn generation(&self) -> u64 {
        7
    }
    fn read_exact_at(&self, offset: u64, output: &mut [u8]) -> Result<()> {
        self.file.read_exact_at(offset, output)
    }
    fn writable(&self) -> Option<&dyn WritableBlockDevice> {
        if self.expose_writer { Some(self) } else { None }
    }
}

impl WritableBlockDevice for RejectingWriter {
    fn submit(&self, _batch: WriteBatch) -> std::result::Result<CommitReceipt, WriteFailure> {
        Err(WriteFailure::Rejected(StorageError::Io(
            std::io::Error::other("test double refuses all writes"),
        )))
    }
    fn flush(&self, _barrier: FlushBarrier) -> std::result::Result<CommitReceipt, WriteFailure> {
        Err(WriteFailure::Rejected(StorageError::Io(
            std::io::Error::other("test double refuses all flushes"),
        )))
    }
}
