# exFAT engine selection and staged mutation

**Goal:** Use exFAT to validate reusable reads and admit writes first in overlays, then directly.
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

## p1 — exFAT read adapter and bounded engine selection

Prerequisites: `track-001-workspace-and-core-traits#p2`, `track-001-workspace-and-core-traits#p4`, `track-006-conformance-and-release#p1`.

Files: functional `crates/backend-exfat`, `tests/native_candidates.rs`, native
fixture manifests and one candidate decision section in this plan.

- [ ] Source-screen the existing shortlist, including exact package names, ancestry, licenses and unsafe paths. Advance at most two viable candidates to the same genuine-image corpus; unresolved safety conflicts block admission.
- [ ] Implement read/list/stat through the same contract as APFS, with contiguous/fragmented data, upcase/names, metadata precision, malformed checksum and source-preservation tests. Add parser fuzzing; a reader can qualify while writer selection remains blocked.
- [ ] Evaluate write APIs, private buffering, barriers and transaction ownership independently of read scores. Choose a reusable writer or one bounded upstream fix; custom mutation requires a named failed requirement and fresh review. Record no winner when evidence is insufficient.

## p2 — Overlay-only mutations

Prerequisites: `track-003-exfat-read-write-engine#p1`, `track-001-workspace-and-core-traits#p6`, `track-005-overlay-and-recovery#p2`.

Files: `crates/backend-exfat/src/`, `tests/mutation_invariants.rs`.
Consumes actual p6 write sessions and the functional overlay; experimental until p3.

- [ ] Add operation traces for create/extend/truncate/delete/rename, NoFatChain transitions, valid-data length, zero initialization, directory expansion, entry checksums and no-space outcomes.
- [ ] Adapt the selected writer to the overlay with single dirty ownership and preflight capability checks. Unsupported TexFAT/dirty/unknown features fail before effects. Base writer handles must not be reachable.
- [ ] Implement only documented missing operations locally using checked layouts. Native readback and unchanged-base hashes are required; store transactions do not imply direct exFAT crash atomicity.

## p3 — Independent writer fault qualification

Prerequisites: `track-003-exfat-read-write-engine#p2`, `track-005-overlay-and-recovery#p3`, `track-006-conformance-and-release#p1`.

Files: `crates/backend-exfat/tests/crash_traces.rs`, `tests/native/exfat/`.
Keep overlay-mode and disposable direct-file-mode results distinct.

- [ ] Inject each admitted write/barrier fault, stale generation, full media, cancellation and worker death into the filesystem I/O path; reopen persisted bytes and compare all acknowledged content/metadata.
- [ ] Join the separate overlay-store persistence suite from 005/p3. For direct-file qualification, rerun traces without the overlay; it cannot inherit overlay rollback or atomicity guarantees.
- [ ] Run fsck.exfat without repair and Windows chkdsk/native readback on fresh copies. Preserve failing images and model permitted dirty/recovery outcomes precisely. A clean checker is not proof that acknowledged user data survived.

## p4 — Per-host direct writes and mounts

Prerequisites: `track-003-exfat-read-write-engine#p3`, `track-002-apfs-readonly-and-mount#p3`, `track-006-conformance-and-release#p3`.

Files: CLI explicit write-admission path and `tests/native/mounts/` exFAT runners.

- [ ] Require exact device identity, exclusivity, supported features, permitted ranges and no conflicting OS mount. Deny unsupported ownership guarantees; no implicit elevation, raw merge or repair.
- [ ] Qualify actual write mounts independently on Windows/Linux/macOS, including real mutable handle lifetimes, concurrent read-after-write, rename/unlink, fsync, disconnect and failed unmount. Reuse 002 frontend contracts without assuming its read qualification proves writes.
- [ ] Run G, direct-mode fault/native suites and host broker tests. Keep each target blocked until its own evidence exists; final full-MVP acceptance requires all required host cells.
