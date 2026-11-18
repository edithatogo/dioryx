# Overlay selection, persistence qualification and export

**Goal:** Reuse persistence without creating a second storage-engine project or modifying the base.
**Architecture:** retain project-owned interfaces and admit qualified dependencies at their first real consumer.
**Spec:** [track specification](spec.md), [design](../../../DESIGN.md), [requirements](../../../REQUIREMENTS.md).
**Execution:** follow the pinned Conductor protocol and [workflow](../../workflow.md), not a second plan hierarchy.

## Global constraints and task cycle

All new work below is pending. Existing directory paths remain stable; the proposed
package names are in [identity](../../../docs/identity.md). No empty packages, new
public ABI, unqualified writer, mock filesystem evidence or dependency safety waiver.

For each checkbox: write/run its named failing regression, make the smallest real
change, rerun that test, run G, obtain its additional native/fault evidence, inspect
the diff and record the exact source/host/result before marking complete. A phase
checkpoint joins all tasks; it does not replace their individual gates. Run Rust
tests via the package's manifest path so the planned rename does not invalidate
commands, for example `cargo test --manifest-path crates/storage-io/Cargo.toml --locked`.
The unchanged G commands are in [workflow](../../workflow.md).

Review focus: stale or changed views, writer-feature escalation, source/destination
aliases, unsupported decoding returning success, and fault tests missing the real
persistence I/O. Each applicable task below pins the corresponding behavior.

## p1 — Persistence decision

Prerequisites: `track-001-workspace-and-core-traits#p2`.

Files: a working, testable overlay-store experiment and this track's selection
record. Create `crates/storage-overlay` only with actual behavior, not a facade.

- [ ] Define atomic payload/map update, bounded partial writes, wrong-base, quota and real reopen tests. Ordinary immutable files are valid storage test inputs, but not filesystem fixtures.
- [ ] Evaluate redb first, including its actual StorageBackend or equivalent I/O injection seam. Source-screen one image engine; run a second executable comparison only if viable and relevant. Do not force a weaker dependency just to populate a comparison table.
- [ ] Select or block on explicit correctness/safety/durability criteria, then compare amplification and resource cost. No new WAL/B-tree; checkpoint G and pinned candidate results.

### Serde persistence decision (existing p1; 18 November 2026)

This is a clarification of **existing track 005/p1**, not a new track, phase or acceptance claim. No current Dioryx crate declares Serde; the six read-only seed crates appropriately depend only on narrow core utilities. Do not add Serde to `dioryx-storage`, `dioryx-vfs`, format decoders, block transforms or the raw filesystem byte path.

- [ ] Before a concrete overlay/persistence consumer is admitted, inventory the external storage engine's *actual* metadata encoding, checksums, failure semantics and Serde integration. A typed `serde::{Serialize, Deserialize}` contract is conditional on evidence of a real control-plane metadata consumer, not convenience.
- [ ] If needed, isolate versioned overlay metadata/source identity/recovery receipts in the first persistence adapter, with explicit bounds, structural validation, duplicate keys, unknown versions, corrupt/truncated bytes, base-generation/source-hash checks and compatibility/migration fixtures. Serde alone cannot prove storage consistency or filesystem integrity.
- [ ] Compare existing store codec and typed Serde adapter for code eliminated, dependencies/features/MSRV, binary size, round-trip and recovery results. Document a **no-go** when the store's native format is adequate.
- [ ] Keep raw on-disk APFS/exFAT parsing, lossless raw names, sector bounds, persistence fault injection and qualified native fixture acceptance separate. Do not enable writes, mounts, raw devices, publish or weaken the mandatory evidence gates.
- [ ] Record exact accepted version/profile, tests, native fixture provenance and the incumbent integration owner's review as part of 005/p1 and 005/p3; do not tick these items until implementation has independently passed.

## p2 — Bounded transactional block overlay

Prerequisites: `track-005-overlay-and-recovery#p1`, `track-001-workspace-and-core-traits#p6`.

Files: actual overlay implementation and `tests/overlay_contract.rs`.
Consumes 001/p6 writer authority; produces a block view, not generic filesystem atomicity.

- [ ] Add `wrong_base_is_rejected`, `allocated_corrupt_block_never_falls_back`, `partial_block_preserves_neighbors`, `base_is_unchanged` and quota-before-allocation tests.
- [ ] Implement immutable base/schema/geometry binding, coherent payload/index commits, explicit zero/sparse behavior and stable selected generations. Document the exact transaction boundary.
- [ ] Enforce one writer and no writable-base handle. Reopen and compare against an independent block map. Mutation consumers remain experimental until persistence qualification.

## p3 — Actual persistence fault qualification

Prerequisites: `track-005-overlay-and-recovery#p2`, `track-006-conformance-and-release#p1`.

Files: `crates/storage-overlay/tests/crash_reopen.rs`, `tests/store_faults.rs`.

- [ ] Prove fault hooks reach the selected store's own writes and sync operations, not just the outer BlockDevice. Inject short/torn writes, lost/reordered persistence where permitted, failed sync, no-space and termination around real commits.
- [ ] Reopen from persisted state, preserving acknowledged generations and rejecting corruption. Record distinct process-kill and persistence-model results; neither is an unqualified hardware power-loss claim.
- [ ] Leave compaction disabled until its reference-retention and disk-quota tests pass. Record G plus actual per-host store behavior; no automatic journal recovery or base repair.

## p4 — Frozen new-image export

Prerequisites: `track-005-overlay-and-recovery#p3`, `track-002-apfs-readonly-and-mount#p2`.

Files: `crates/fs-cli/tests/overlay_export.rs` and actual export command path.

- [ ] Add frozen-generation, changing-base, destination-alias, interrupted/full-disk and no-clobber publication tests. Use the admitted extraction/staging authority.
- [ ] Export only to a new image and compare full logical bytes on reopen. The consuming filesystem independently supplies native checker and metadata/content evidence.
- [ ] Base and overlay masters remain intact. No commit-to-original command, raw merge, automatic repair or claim that file rename gives whole-device atomicity.

