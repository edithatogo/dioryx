# Additional readers and consumed transforms

**Goal:** Expand verified read coverage without making optional formats a core critical-path dependency.
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

## p1 — Narrow reader admission

Prerequisites: `track-001-workspace-and-core-traits#p4`, `track-006-conformance-and-release#p1`.

Files: this track's dependency decision section and native fixture manifests.

- [ ] Admit one narrow read-only candidate at a time: ntfs, ext4-view, then hfsplus. Define supported clean-image features and typed rejection of unsupported dirty/recovery states before importing code.
- [ ] Source-screen full rust-fs-* alternatives only for demonstrated gaps. They do not automatically enter the dependency graph or expand MVP write scope. Native source preservation is a hard gate.

## p2 — Independent reader consumers

Prerequisites: `track-004-multi-fs-expansion-and-transforms#p1`.

Files: one functional `crates/backend-<format>` plus its `tests/native_read.rs` and
parser fuzz target; no placeholder backlog packages.

- [ ] Write failing content/metadata/name/bounds tests from native images, then implement a thin read-only adapter. Use a genuinely independent oracle and record code ancestry.
- [ ] Deny every mutation/replay path, including when writer features are accidentally unified. Run G and the real-image/fuzz/profile gates separately for each new reader.

## p3 — Consumed shared transforms

Prerequisites: `track-004-multi-fs-expansion-and-transforms#p1`.

Files: consumed modules in `crates/transform-core/src/`, `tests/codec_bounds.rs`.

- [ ] Add independent known-answer and truncation/output/scratch-limit tests for each actual checksum/codec consumer. Earlier APFS codecs belong to its delivering task, not a delayed prerequisite here.
- [ ] Reuse qualified implementations; distinguish exact framing and checksum algorithms. Do not add unconsumed XTS, unlockers or a broad binary-parser dependency stack. Cross-layer resource limits remain shared.

## p4 — Expanded conformance and future decisions

Prerequisites: `track-004-multi-fs-expansion-and-transforms#p2`, `track-004-multi-fs-expansion-and-transforms#p3`.

Files: expanded fixture/fuzz manifests and this track's decision section.

- [ ] Run registered readers on native malformed derivatives and cross-layer ambiguity cases; report failed/unsupported inputs honestly. Each release profile needs its own reader completion evidence.
- [ ] Record future NTFS/ext4 write or Btrfs decisions only when useful evidence exists. They remain outside the current direct-write product scope; no speculative writer implementation or new track proliferation.
