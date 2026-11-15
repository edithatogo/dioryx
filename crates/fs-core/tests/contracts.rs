#[path = "../../storage-io/tests/support/mod.rs"]
mod support;

use dioryx_storage::FileDevice;
use dioryx_vfs::*;

#[test]
fn a_read_only_layer_denies_write_requests() -> Result<()> {
    let rw = FsCapabilities {
        read: true,
        write: true,
        create: true,
        remove: true,
        rename: true,
        durability: Durability::Durable,
        atomic_rename: true,
        crash_atomic_batch: true,
        ..FsCapabilities::default()
    };
    let ro = FsCapabilities {
        read: true,
        ..FsCapabilities::default()
    };
    assert!(matches!(
        negotiate(
            &[rw, ro],
            CapabilityRequest {
                writable: true,
                ..CapabilityRequest::default()
            }
        ),
        Err(FsError::ReadOnly)
    ));
    let effective = negotiate(&[rw, ro], CapabilityRequest::default())?;
    assert!(!effective.write);
    assert!(!effective.atomic_rename);
    assert_eq!(effective.durability, Durability::None);
    let readonly_request = negotiate(&[rw, rw], CapabilityRequest::default())?;
    assert!(!readonly_request.write);
    assert!(!readonly_request.create);
    assert!(!readonly_request.remove);
    assert!(!readonly_request.rename);
    assert!(!readonly_request.atomic_rename);
    assert!(!readonly_request.crash_atomic_batch);
    assert_eq!(readonly_request.durability, Durability::None);
    assert!(matches!(
        negotiate(
            &[rw, ro],
            CapabilityRequest {
                minimum_durability: Durability::Durable,
                ..CapabilityRequest::default()
            }
        ),
        Err(FsError::Unsupported("durability"))
    ));
    assert!(negotiate(&[], CapabilityRequest::default()).is_err());
    let inconsistent = FsCapabilities {
        read: true,
        create: true,
        ..FsCapabilities::default()
    };
    assert!(matches!(
        negotiate(&[inconsistent], CapabilityRequest::default()),
        Err(FsError::Unsupported("inconsistent mutation capabilities"))
    ));
    Ok(())
}

#[test]
fn crash_atomicity_is_admitted_before_mutation_and_not_inferred_from_rename() -> Result<()> {
    let ordered_backend = FsCapabilities {
        read: true,
        write: true,
        rename: true,
        durability: Durability::Durable,
        atomic_rename: true,
        ..FsCapabilities::default()
    };
    let request = CapabilityRequest {
        writable: true,
        minimum_durability: Durability::Durable,
        atomic_rename: true,
        require_atomic_batch: true,
    };
    assert!(matches!(
        negotiate(&[ordered_backend], request),
        Err(FsError::Unsupported("crash-atomic batch"))
    ));
    let options = MutationOptions {
        minimum_durability: Durability::Durable,
        require_atomic_batch: true,
    };
    assert!(matches!(
        options.validate(ordered_backend),
        Err(FsError::Unsupported("crash-atomic batch"))
    ));
    let journaled = FsCapabilities {
        crash_atomic_batch: true,
        ..ordered_backend
    };
    let effective = negotiate(&[journaled], request)?;
    options.validate(effective)?;
    let ro = negotiate(&[journaled], CapabilityRequest::default())?;
    assert!(matches!(options.validate(ro), Err(FsError::ReadOnly)));
    Ok(())
}

#[test]
fn matching_magic_never_silently_resolves_ambiguity()
-> std::result::Result<(), Box<dyn std::error::Error>> {
    let fixture = support::TempFile::new(b"prefixMAGICsuffix")?;
    let device = FileDevice::open(&fixture.path, 1)?;
    let mut registry = ProbeRegistry::default();
    registry.register(Signature {
        format: "format-a".into(),
        offset: 6,
        magic: b"MAGIC".to_vec(),
    })?;
    assert_eq!(
        registry.probe(&device, 5)?,
        ProbeResult::Unique("format-a".into())
    );
    registry.register(Signature {
        format: "format-b".into(),
        offset: 6,
        magic: b"MAGIC".to_vec(),
    })?;
    assert_eq!(
        registry.probe(&device, 10)?,
        ProbeResult::Ambiguous(vec!["format-a".into(), "format-b".into()])
    );
    assert!(matches!(registry.probe(&device, 9), Err(FsError::Limit)));
    assert!(
        registry
            .register(Signature {
                format: "overflow".into(),
                offset: u64::MAX,
                magic: vec![1]
            })
            .is_err()
    );
    Ok(())
}

#[test]
fn traversal_stops_on_cycles_and_resource_exhaustion() -> Result<()> {
    let mut budget = TraversalBudget::new(3, 2)?;
    assert!(matches!(budget.enter(1, 1), Err(FsError::TraversalOrder)));
    budget.enter(1, 0)?;
    budget.enter(2, 1)?;
    assert!(matches!(budget.enter(1, 2), Err(FsError::Cycle)));
    assert!(matches!(budget.enter(3, 3), Err(FsError::Limit)));
    assert!(matches!(budget.leave(1), Err(FsError::TraversalOrder)));
    budget.enter(3, 2)?;
    budget.leave(3)?;
    budget.leave(2)?;
    budget.leave(1)?;
    assert!(matches!(budget.enter(4, 0), Err(FsError::Limit)));
    Ok(())
}

#[test]
fn shared_dag_nodes_are_valid_after_leaving_the_previous_path() -> Result<()> {
    let mut budget = TraversalBudget::new(5, 2)?;
    budget.enter(1, 0)?;
    budget.enter(2, 1)?;
    budget.enter(4, 2)?;
    budget.leave(4)?;
    budget.leave(2)?;
    budget.enter(3, 1)?;
    budget.enter(4, 2)?;
    budget.leave(4)?;
    budget.leave(3)?;
    budget.leave(1)?;
    assert!(matches!(budget.enter(5, 0), Err(FsError::Limit)));
    Ok(())
}
