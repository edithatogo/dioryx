# Rust style and safety

- Use Rust 2024, the pinned toolchain and workspace lints. Every first-party
  container, volume, transform, semantics, VFS and backend crate begins with
  `#![forbid(unsafe_code)]`. The bootstrap storage crate also forbids unsafe.
- If native raw-device operations later require FFI, the storage crate switches
  only to a reviewed crate-level `deny(unsafe_code)` with a narrow platform-module
  allowance. Safe modules retain `forbid`. Never lower the workspace policy for
  all crates. Prefer safe std/nix wrappers; every necessary unsafe block states
  `// SAFETY:` obligations for handles, lifetimes, alignment, buffer bounds,
  initialization and concurrency. Mount FFI follows the same boundary.
- Parse external bytes using checked slices and explicit endian reads. For
  zerocopy 0.8 layouts, use `U16/U32/U64<LittleEndian>` or `<BigEndian>` and derive
  `FromBytes`, `IntoBytes`, `KnownLayout`, `Immutable`, `Unaligned` only when valid.
  Validate lengths, tags and offsets after decoding. Avoid native-endian integer
  fields, packed-field references, transmute and raw-pointer casts. bytemuck is
  optional, not a second mandatory casting system; never add unsafe Pod impls.
- Return typed `Result` errors using thiserror. Include a stable class and safe
  offset/context; preserve lower-layer causes. A malformed input must not invoke
  panic, unwrap, expect, todo, unimplemented, unchecked indexing, oversized shifts
  or unbounded recursion. Test assertions are permitted; parser assertions are not.
- Use checked arithmetic and checked integer conversions for offsets, counts,
  timestamps, allocation sizes and sector geometry. Use fallible allocation or
  admission limits before allocating from untrusted lengths. A checksum match
  validates integrity only to that algorithm's extent; it is not authentication.
- Traversals carry explicit resource budgets and visited-object identities.
  Distinguish an on-path cycle from legal shared nodes; legitimate hard links or
  CoW references are not globally forbidden duplicates. Parse untrusted trees
  iteratively or with bounded depth.
- Keep core traits synchronous and object-safe. Mutable upstream Read+Seek
  parsers receive private cursors over positional devices. Frontends place
  blocking work on bounded workers; never block a Tokio reactor or hold a mutex
  across an await. Do not expose unifuse or OS handles in backend contracts.
- Raw names retain bytes or UTF-16 code units. Unicode normalization is a
  presentation/export policy. Filesystem lookup follows its versioned native
  collation/upcase rules. Preserve precision and unknown time offsets; do not
  clamp pre-epoch times or conflate POSIX ctime with birth time.
- Documentation states ownership, limits, failure and durability behavior.
  Separate unsupported capabilities from I/O failures and from unavailable
  evidence. No successful no-op write/flush or fabricated metadata fallback.
- Test invariants and observed behavior. Temporary ordinary files are appropriate
  for storage tests; only real generated disk images prove filesystem behavior.

## Adapter and authority rules

Do not leak upstream types in project-owned public contracts. Alias dependencies
whose library names collide with fs_core. Do not maintain a second parser or cache
for the same purpose without a recorded reason. Use standard positional I/O when
it meets the contract, and keep flush/uncertainty semantics explicit above it.

Pass approved directory/device capabilities rather than reconstructing ambient
paths. Retain raw names and on-disk identity separately from display strings.
Model open-handle IDs separately from persistent nodes and refuse counter overflow.
Keep source generation, snapshot/checkpoint and overlay generation distinct.

Propagate a shared budget/cancellation context through nested parsing; never multiply
limits by creating fresh full budgets at every layer. Charge allocations and counts
before consuming them; catch_unwind is not a safe-parser or sandbox guarantee.
After possible writes, cancellation and I/O errors must preserve indeterminate
outcomes. No automatic retry can assume an operation had no effects.
