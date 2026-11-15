#[path = "../../storage-io/tests/support/rejecting_writer.rs"]
mod rejecting_writer;
#[path = "../../storage-io/tests/support/mod.rs"]
mod support;

use dioryx_containers::{Container, ContainerError, RawContainer};
use dioryx_storage::{FileDevice, FlushBarrier, WriteFailure};
use std::sync::Arc;

#[test]
fn raw_container_exposes_exactly_one_unchanged_disk() -> Result<(), Box<dyn std::error::Error>> {
    let fixture = support::TempFile::new(b"raw image bytes")?;
    let source = Arc::new(FileDevice::open(&fixture.path, 1)?);
    let container = RawContainer::new(source);
    assert_eq!(container.format(), "raw");
    assert_eq!(container.disk_count(), 1);
    let disk = container.open_disk(0)?;
    let mut bytes = [0; 15];
    disk.read_exact_at(0, &mut bytes)?;
    assert_eq!(&bytes, b"raw image bytes");
    assert!(matches!(
        container.open_disk(1),
        Err(ContainerError::DiskNotFound)
    ));
    Ok(())
}

#[test]
fn container_preserves_mutation_access_and_propagates_failure()
-> Result<(), Box<dyn std::error::Error>> {
    let fixture = support::TempFile::new(b"unchanged")?;
    let source = Arc::new(rejecting_writer::RejectingWriter::new(&fixture.path, 1)?);
    let disk = RawContainer::new(source).open_disk(0)?;
    let writer = disk
        .writable()
        .ok_or_else(|| std::io::Error::other("writer was erased"))?;
    assert!(matches!(
        writer.flush(FlushBarrier::Data),
        Err(WriteFailure::Rejected(_))
    ));
    assert_eq!(std::fs::read(&fixture.path)?, b"unchanged");
    Ok(())
}
