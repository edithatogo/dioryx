#![forbid(unsafe_code)]
//! Container interface and real raw-image passthrough. UDIF is a later admission gate.

use dioryx_storage::BlockDevice;
use std::sync::Arc;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ContainerError {
    #[error("logical disk index is out of range")]
    DiskNotFound,
    #[error("unsupported container feature: {0}")]
    Unsupported(&'static str),
    #[error(transparent)]
    Storage(#[from] dioryx_storage::StorageError),
}

pub trait Container: Send + Sync {
    fn format(&self) -> &'static str;
    fn disk_count(&self) -> usize;
    fn open_disk(&self, index: usize) -> Result<Arc<dyn BlockDevice>, ContainerError>;
}

pub struct RawContainer {
    source: Arc<dyn BlockDevice>,
}

impl RawContainer {
    pub fn new(source: Arc<dyn BlockDevice>) -> Self {
        Self { source }
    }
}

impl Container for RawContainer {
    fn format(&self) -> &'static str {
        "raw"
    }
    fn disk_count(&self) -> usize {
        1
    }
    fn open_disk(&self, index: usize) -> Result<Arc<dyn BlockDevice>, ContainerError> {
        if index != 0 {
            return Err(ContainerError::DiskNotFound);
        }
        dioryx_storage::validate_device(self.source.as_ref())?;
        Ok(Arc::clone(&self.source))
    }
}
