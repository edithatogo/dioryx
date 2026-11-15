#[path = "support/rejecting_writer.rs"]
mod rejecting_writer;
mod support;

use rejecting_writer::RejectingWriter;
use std::sync::Arc;
use storage_io::*;
use support::TempFile;

#[test]
fn regular_file_reads_are_bounded_and_read_only()
-> std::result::Result<(), Box<dyn std::error::Error>> {
    let fixture = TempFile::new(&vec![0x4f; 1024])?;
    let device = FileDevice::open(&fixture.path, 512)?;
    let mut output = [0; 8];
    device.read_exact_at(511, &mut output)?;
    assert_eq!(output, [0x4f; 8]);
    assert!(!device.capabilities().writable);
    assert!(matches!(
        device.read_exact_at(1020, &mut output),
        Err(StorageError::OutOfBounds)
    ));
    assert!(matches!(
        device.read_exact_at(u64::MAX, &mut output),
        Err(StorageError::OutOfBounds)
    ));
    assert!(matches!(
        FileDevice::open(&fixture.path, 0),
        Err(StorageError::InvalidGeometry)
    ));
    Ok(())
}

#[test]
fn concurrent_reads_do_not_share_a_visible_cursor()
-> std::result::Result<(), Box<dyn std::error::Error>> {
    let bytes: Vec<u8> = (0..8).flat_map(|value| [value; 512]).collect();
    let fixture = TempFile::new(&bytes)?;
    let device = Arc::new(FileDevice::open(&fixture.path, 512)?);
    let threads: Vec<_> = (0_u8..8)
        .map(|value| {
            let reader = Arc::clone(&device);
            std::thread::spawn(move || -> Result<()> {
                let mut output = [0; 512];
                for _ in 0..32 {
                    reader.read_exact_at(u64::from(value) * 512, &mut output)?;
                    assert_eq!(output, [value; 512]);
                }
                Ok(())
            })
        })
        .collect();
    for thread in threads {
        thread
            .join()
            .map_err(|_| std::io::Error::other("reader thread failed"))??;
    }
    Ok(())
}

#[test]
fn batches_reject_overlap_stale_epochs_and_unavailable_barriers()
-> std::result::Result<(), Box<dyn std::error::Error>> {
    let fixture = TempFile::new(&vec![0; 2048])?;
    let mut device = RejectingWriter::new(&fixture.path, 512)?;
    let write = WriteOp {
        offset: 0,
        bytes: Arc::from([1_u8; 512]),
    };
    let mut batch = WriteBatch {
        expected_generation: 7,
        groups: vec![FlushGroup {
            writes: vec![write.clone()],
            barrier: FlushBarrier::DataAndMetadata,
        }],
    };
    batch.validate(&device, 1024)?;
    batch.groups[0].writes.push(write);
    assert!(matches!(
        batch.validate(&device, 1024),
        Err(StorageError::InvalidBatch)
    ));
    batch.groups[0].writes.pop();
    batch.expected_generation = 6;
    assert!(matches!(
        batch.validate(&device, 1024),
        Err(StorageError::StaleGeneration)
    ));
    batch.expected_generation = 7;
    device.caps.strongest_barrier = Some(FlushBarrier::Data);
    assert!(matches!(
        batch.validate(&device, 1024),
        Err(StorageError::UnsupportedBarrier)
    ));
    device.caps.strongest_barrier = Some(FlushBarrier::DataAndMetadata);
    assert!(matches!(
        batch.validate(&device, 511),
        Err(StorageError::ResourceLimit)
    ));
    assert!(matches!(
        batch.validate(&device.file, 1024),
        Err(StorageError::ReadOnly)
    ));
    device.expose_writer = false;
    assert!(matches!(
        batch.validate(&device, 1024),
        Err(StorageError::InvalidCapabilities)
    ));
    device.expose_writer = true;
    device.caps.writable = false;
    assert!(matches!(
        validate_device(&device),
        Err(StorageError::InvalidCapabilities)
    ));
    Ok(())
}

#[test]
fn geometry_rejects_misalignment_and_overflow() -> Result<()> {
    let geometry = Geometry::new(4096, 512, 4096)?;
    assert!(matches!(
        geometry.check_aligned(1, 512),
        Err(StorageError::Misaligned)
    ));
    assert!(matches!(
        geometry.check_range(u64::MAX, 1),
        Err(StorageError::OutOfBounds)
    ));
    assert!(Geometry::new(4097, 512, 4096).is_err());
    assert!(Geometry::new(4096, 4096, 512).is_err());
    geometry.check_range(4096, 0)?;
    Ok(())
}
