#![forbid(unsafe_code)]
//! Mount-independent filesystem contracts, capability negotiation, and bounded probes.

use dioryx_semantics::{RawName, Timestamp};
use dioryx_storage::{BlockDevice, StorageError};
use std::collections::{BTreeSet, HashSet};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum FsError {
    #[error("read-only filesystem or pipeline")]
    ReadOnly,
    #[error("unsupported operation or guarantee: {0}")]
    Unsupported(&'static str),
    #[error("object not found")]
    NotFound,
    #[error("corrupt filesystem: {0}")]
    Corrupt(&'static str),
    #[error("resource limit exceeded")]
    Limit,
    #[error("cycle detected")]
    Cycle,
    #[error("traversal enter/leave order is inconsistent")]
    TraversalOrder,
    #[error(transparent)]
    Storage(#[from] StorageError),
    #[error(transparent)]
    Semantics(#[from] dioryx_semantics::SemanticsError),
}

pub type Result<T> = std::result::Result<T, FsError>;

#[derive(Clone, Copy, Debug, Default, Eq, Ord, PartialEq, PartialOrd)]
pub enum Durability {
    #[default]
    None,
    /// Backend ordering is enforced; persistence after power loss is not promised.
    Ordered,
    /// The requested changes have reached the admitted persistent storage boundary.
    /// This guarantee does not imply atomic recovery of multiple changes.
    Durable,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct FsCapabilities {
    pub read: bool,
    pub write: bool,
    pub create: bool,
    pub remove: bool,
    pub rename: bool,
    pub durability: Durability,
    /// Rename is indivisible to concurrent namespace observers. This says
    /// nothing about which state survives a crash.
    pub atomic_rename: bool,
    /// An accepted batch recovers entirely to its old or new state after a
    /// crash. Ordered flushes and namespace-atomic rename do not imply this.
    pub crash_atomic_batch: bool,
    pub snapshots: bool,
    pub symlinks: bool,
    pub xattrs: bool,
}

impl FsCapabilities {
    pub fn validate(self) -> Result<()> {
        if (!self.write
            && (self.create
                || self.remove
                || self.rename
                || self.atomic_rename
                || self.crash_atomic_batch))
            || (self.atomic_rename && !self.rename)
        {
            return Err(FsError::Unsupported("inconsistent mutation capabilities"));
        }
        Ok(())
    }

    pub fn intersection(self, other: Self) -> Self {
        Self {
            read: self.read && other.read,
            write: self.write && other.write,
            create: self.create && other.create,
            remove: self.remove && other.remove,
            rename: self.rename && other.rename,
            durability: self.durability.min(other.durability),
            atomic_rename: self.atomic_rename && other.atomic_rename,
            crash_atomic_batch: self.crash_atomic_batch && other.crash_atomic_batch,
            snapshots: self.snapshots && other.snapshots,
            symlinks: self.symlinks && other.symlinks,
            xattrs: self.xattrs && other.xattrs,
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct CapabilityRequest {
    pub writable: bool,
    pub minimum_durability: Durability,
    pub atomic_rename: bool,
    pub require_atomic_batch: bool,
}

/// Layers contain backend, device/container/transform, frontend, and user-policy
/// masks. A read-only request removes mutation access even if every layer can
/// write. Unsupported writable requests fail without silently falling back.
pub fn negotiate(layers: &[FsCapabilities], request: CapabilityRequest) -> Result<FsCapabilities> {
    for layer in layers {
        layer.validate()?;
    }
    let (first, rest) = layers.split_first().ok_or(FsError::Limit)?;
    let mut effective = rest
        .iter()
        .fold(*first, |caps, layer| caps.intersection(*layer));
    if !effective.read {
        return Err(FsError::Unsupported("read"));
    }
    if request.writable && !effective.write {
        return Err(FsError::ReadOnly);
    }
    if !request.writable {
        effective.write = false;
        effective.create = false;
        effective.remove = false;
        effective.rename = false;
        effective.atomic_rename = false;
        effective.crash_atomic_batch = false;
        effective.durability = Durability::None;
    }
    if effective.durability < request.minimum_durability {
        return Err(FsError::Unsupported("durability"));
    }
    if request.atomic_rename && !(effective.rename && effective.atomic_rename) {
        return Err(FsError::Unsupported("atomic rename"));
    }
    if request.require_atomic_batch && !effective.crash_atomic_batch {
        return Err(FsError::Unsupported("crash-atomic batch"));
    }
    Ok(effective)
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub struct NodeId {
    pub mount: u64,
    pub object: u128,
    pub generation: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum NodeKind {
    File,
    Directory,
    Symlink,
}

#[derive(Clone, Debug)]
pub struct Metadata {
    pub id: NodeId,
    pub kind: NodeKind,
    pub len: u64,
    pub modified: Option<Timestamp>,
}

#[derive(Clone, Debug)]
pub struct DirectoryEntry {
    pub name: RawName,
    pub id: NodeId,
    pub kind: NodeKind,
}

#[derive(Clone, Debug)]
pub struct DirectoryPage {
    pub entries: Vec<DirectoryEntry>,
    pub next_cookie: Option<u64>,
}

/// A symlink target may contain separators and parent components. It must never
/// be interpreted as a validated extraction path or passed through RawName validation.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum LinkTarget {
    Bytes(Vec<u8>),
    Utf16(Vec<u16>),
}

/// Blocking, object-safe contract. Async frontends use a bounded blocking pool.
/// Each implementation must enforce supplied output limits and its own budgets.
pub trait VirtualFs: Send + Sync {
    fn capabilities(&self) -> FsCapabilities;
    fn root(&self) -> Result<NodeId>;
    fn stat(&self, node: NodeId) -> Result<Metadata>;
    fn lookup(&self, parent: NodeId, name: &RawName) -> Result<NodeId>;
    fn read_dir(
        &self,
        directory: NodeId,
        cookie: Option<u64>,
        limit: usize,
    ) -> Result<DirectoryPage>;
    fn read_at(&self, file: NodeId, offset: u64, output: &mut [u8]) -> Result<usize>;
    fn read_link(&self, node: NodeId, max_bytes: usize) -> Result<LinkTarget>;
    fn writable(&self) -> Option<&dyn WritableFs>;
}

#[derive(Clone, Debug)]
pub enum Mutation {
    Create {
        parent: NodeId,
        name: RawName,
        kind: NodeKind,
    },
    Remove {
        parent: NodeId,
        name: RawName,
    },
    Rename {
        parent: NodeId,
        name: RawName,
        new_parent: NodeId,
        new_name: RawName,
        replace: bool,
    },
    Write {
        file: NodeId,
        offset: u64,
        data: Vec<u8>,
    },
    SetLen {
        file: NodeId,
        len: u64,
    },
}

#[derive(Clone, Copy, Debug, Default)]
pub struct MutationOptions {
    pub minimum_durability: Durability,
    pub require_atomic_batch: bool,
}

impl MutationOptions {
    /// Backends must perform this admission check, operation-specific validation,
    /// and resource admission before any mutation. A receipt cannot weaken it.
    pub fn validate(self, capabilities: FsCapabilities) -> Result<()> {
        capabilities.validate()?;
        if !capabilities.write {
            return Err(FsError::ReadOnly);
        }
        if capabilities.durability < self.minimum_durability {
            return Err(FsError::Unsupported("durability"));
        }
        if self.require_atomic_batch && !capabilities.crash_atomic_batch {
            return Err(FsError::Unsupported("crash-atomic batch"));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum MutationOutcome {
    Created { node: NodeId },
    Removed,
    Renamed,
    Written { bytes: usize },
    Resized,
}

#[derive(Clone, Debug)]
pub struct MutationReceipt {
    pub generation: u64,
    /// Exactly one result per submitted command, in input order. Created node
    /// handles and actual write byte counts must be returned to the caller.
    pub outcomes: Vec<MutationOutcome>,
    pub durability: Durability,
    pub crash_atomic_batch: bool,
}

#[derive(Clone, Copy, Debug)]
pub struct SyncReceipt {
    pub generation: u64,
    pub durability: Durability,
}

#[derive(Debug, Error)]
pub enum MutationError {
    #[error("rejected before mutation: {0}")]
    Rejected(#[source] FsError),
    #[error("indeterminate mutation; recovery is required before further writes")]
    Indeterminate {
        confirmed_operations: usize,
        invalidated_generation: u64,
    },
}

/// A command batch is not inherently atomic. Validate options and every command
/// before I/O; unsupported atomicity must be rejected before mutation. A receipt
/// reports the actual guarantee, and possibly visible changes require an
/// Indeterminate error. fsync cannot retroactively make earlier changes atomic.
pub trait WritableFs: Send + Sync {
    fn mutate(
        &self,
        operations: &[Mutation],
        options: MutationOptions,
    ) -> std::result::Result<MutationReceipt, MutationError>;
    fn fsync(
        &self,
        node: NodeId,
        durability: Durability,
    ) -> std::result::Result<SyncReceipt, MutationError>;
}

#[derive(Clone, Debug)]
pub struct Signature {
    pub format: String,
    pub offset: u64,
    pub magic: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ProbeResult {
    NoMatch,
    Unique(String),
    Ambiguous(Vec<String>),
}

#[derive(Default)]
pub struct ProbeRegistry {
    signatures: Vec<Signature>,
}

impl ProbeRegistry {
    pub fn register(&mut self, signature: Signature) -> Result<()> {
        if self.signatures.len() >= 128
            || signature.format.is_empty()
            || signature.format.len() > 128
            || signature.magic.is_empty()
            || signature.magic.len() > 256
            || signature
                .offset
                .checked_add(signature.magic.len() as u64)
                .is_none_or(|end| end > 1024 * 1024)
        {
            return Err(FsError::Limit);
        }
        self.signatures.push(signature);
        Ok(())
    }

    /// Magic is a candidate signal only. The selected parser must validate the format.
    pub fn probe(&self, source: &dyn BlockDevice, byte_budget: usize) -> Result<ProbeResult> {
        let mut remaining = byte_budget;
        let mut matches = BTreeSet::new();
        for signature in &self.signatures {
            if source
                .geometry()
                .check_range(signature.offset, signature.magic.len())
                .is_err()
            {
                continue;
            }
            remaining = remaining
                .checked_sub(signature.magic.len())
                .ok_or(FsError::Limit)?;
            let mut bytes = vec![0; signature.magic.len()];
            source.read_exact_at(signature.offset, &mut bytes)?;
            if bytes == signature.magic {
                matches.insert(signature.format.clone());
            }
        }
        match matches.len() {
            0 => Ok(ProbeResult::NoMatch),
            1 => matches
                .into_iter()
                .next()
                .map(ProbeResult::Unique)
                .ok_or(FsError::Limit),
            _ => Ok(ProbeResult::Ambiguous(matches.into_iter().collect())),
        }
    }
}

/// Counts every node visit while detecting cycles only on the active DFS path.
/// Re-entering a shared subtree after leaving it is legal and consumes budget.
pub struct TraversalBudget {
    remaining: u32,
    max_depth: u32,
    active: HashSet<u64>,
    stack: Vec<u64>,
}

impl TraversalBudget {
    pub fn new(max_nodes: u32, max_depth: u32) -> Result<Self> {
        if max_nodes == 0 || max_nodes > 1_000_000 || max_depth == 0 || max_depth > 4096 {
            return Err(FsError::Limit);
        }
        Ok(Self {
            remaining: max_nodes,
            max_depth,
            active: HashSet::new(),
            stack: Vec::new(),
        })
    }
    pub fn enter(&mut self, object: u64, depth: u32) -> Result<()> {
        if depth > self.max_depth || self.remaining == 0 {
            return Err(FsError::Limit);
        }
        if depth as usize != self.stack.len() {
            return Err(FsError::TraversalOrder);
        }
        if !self.active.insert(object) {
            return Err(FsError::Cycle);
        }
        self.remaining -= 1;
        self.stack.push(object);
        Ok(())
    }

    pub fn leave(&mut self, object: u64) -> Result<()> {
        if self.stack.last() != Some(&object) {
            return Err(FsError::TraversalOrder);
        }
        self.stack.pop();
        self.active.remove(&object);
        Ok(())
    }
}
