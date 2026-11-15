#[path = "../../storage-io/tests/support/rejecting_writer.rs"]
mod rejecting_writer;
#[path = "../../storage-io/tests/support/mod.rs"]
mod support;

use std::sync::Arc;
use storage_io::{BlockDevice, FileDevice, FlushBarrier, StorageError, WriteFailure};
use volume_core::*;

#[test]
fn nested_slices_cannot_read_adjacent_volume_bytes() -> Result<(), Box<dyn std::error::Error>> {
    let fixture = support::TempFile::new(b"beforePAYLOADafter")?;
    let source: Arc<dyn BlockDevice> = Arc::new(FileDevice::open(&fixture.path, 1)?);
    let slice = Arc::new(SliceDevice::new(Arc::clone(&source), 6, 7)?);
    let nested = SliceDevice::new(slice, 1, 3)?;
    let mut output = [0; 3];
    nested.read_exact_at(0, &mut output)?;
    assert_eq!(&output, b"AYL");
    assert!(matches!(
        nested.read_exact_at(1, &mut output),
        Err(StorageError::OutOfBounds)
    ));
    assert!(matches!(
        SliceDevice::new(source, u64::MAX, 2),
        Err(StorageError::OutOfBounds)
    ));
    Ok(())
}

#[test]
fn pool_preserves_mutation_access_but_read_only_slice_removes_it()
-> Result<(), Box<dyn std::error::Error>> {
    let fixture = support::TempFile::new(b"unchanged")?;
    let source = Arc::new(rejecting_writer::RejectingWriter::new(&fixture.path, 1)?);
    let pool = SingleVolumePool::new(VolumeId(7), source);
    let device = pool.open(VolumeId(7))?;
    let writer = device
        .writable()
        .ok_or_else(|| std::io::Error::other("writer was erased"))?;
    assert!(matches!(
        writer.flush(FlushBarrier::Data),
        Err(WriteFailure::Rejected(_))
    ));
    let slice = SliceDevice::new(device, 0, 9)?;
    assert!(slice.writable().is_none());
    assert!(!slice.capabilities().writable);
    assert_eq!(std::fs::read(&fixture.path)?, b"unchanged");
    Ok(())
}

#[test]
fn pool_requires_explicit_identity_and_bounded_discovery() -> Result<(), Box<dyn std::error::Error>>
{
    let fixture = support::TempFile::new(b"source")?;
    let source = Arc::new(FileDevice::open(&fixture.path, 1)?);
    let pool = SingleVolumePool::new(VolumeId(7), source);
    assert!(matches!(pool.volumes(0), Err(VolumeError::Limit)));
    assert!(matches!(pool.open(VolumeId(8)), Err(VolumeError::NotFound)));
    assert_eq!(pool.volumes(1)?[0].geometry.len(), 6);
    Ok(())
}
