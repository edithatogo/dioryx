# APFS proof, mountless delivery and read mounts

**Goal:** Prove genuine APFS reads before adapting them, then qualify each delivery mode.
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

## p1 — Direct native APFS proof

Prerequisites: `track-001-workspace-and-core-traits#r0`, `track-006-conformance-and-release#p1`.

Files: functional `crates/backend-apfs` with `tests/native_reader.rs`, fixture
manifests under `tests/fixtures/`. New package only alongside real reader behavior.
Consumes a native raw image and oracle, not an already-complete universal VFS.

- [ ] Create a genuine macOS raw APFS/GPT fixture and oracle through 006/p1. Add a failing known-file hash/tree comparison, then call the pinned upstream reader directly. No new APFS binary parser and no mock success facade.
- [ ] Test `compressed_file_never_becomes_empty_success`, `snapshot_request_never_opens_live_tree`, required-feature denial and before/after source hashes for success/failure. Keep live, compressed and historical-snapshot support as different claims.
- [ ] Add bounded malformed-image regression/fuzz entry with native seeds. Record exact admitted subset and stop/revise the engine choice if essential bytes cannot be read. This phase does not wait for UDIF, mount handles, caching or overlays.

## p2 — APFS VFS and mountless CLI

Prerequisites: `track-002-apfs-readonly-and-mount#p1`, `track-001-workspace-and-core-traits#p3`, `track-001-workspace-and-core-traits#p4`.

Files: `crates/backend-apfs/src/lib.rs`, a functional `crates/fs-cli`,
`crates/fs-cli/tests/native_cli.rs`, `crates/fs-cli/tests/extraction_authority.rs`.
Produces the first image-backed library/CLI consumer and versioned diagnostics.

- [ ] Expose proved reads through VirtualFs; run raw/GPT then qualified UDIF list/stat/read/extract comparisons. Demonstrate the application-facing library from a real consumer before creating an umbrella package.
- [ ] Add `source_alias_is_never_overwritten`, `destination_symlink_race_cannot_escape`, normalization collision, unrepresentable metadata, global temporary quota and no-clobber publication tests before adapting cap-std/cap-tempfile.
- [ ] Implement bounded inspect/list/stat/extract and truthful profile reports. Mountless builds require no driver. Controlled in-process/library results do not advertise a sandbox; the hostile-image CLI profile additionally needs 006/p2.

## p3 — Read frontend contract

Prerequisites: `track-002-apfs-readonly-and-mount#p2`, `track-001-workspace-and-core-traits#p5`.

Files: functional `crates/mount-unifuse` and `tests/frontend_contract.rs`.
Consumes project VFS/handle contracts; no backend imports the mount library.

- [ ] Recheck the exact upstream adapter for error/name/access behavior; convert each live defect into a failing reproduction. Historical source observations are not current runtime evidence.
- [ ] Implement supported read-operation translation with `denied_write_never_reaches_backend`, `stale_handle_is_rejected`, `host_error_is_not_success` and cancellation/unmount regressions. No synthetic flush/capacity success or lossy name substitution.
- [ ] Accept upstream fixes, bounded patches or another adapter when necessary. Keep the bridge thin by responsibility, not an arbitrary line count; write-mount operation coverage is a later consumer gate.

## p4 — Per-host image read mounts

Prerequisites: `track-002-apfs-readonly-and-mount#p3`, `track-006-conformance-and-release#p2`.

Files: `tests/native/mounts/` host runners and profile evidence.

- [ ] Independently execute image-backed Linux FUSE, Windows WinFsp and macOS macFUSE read mounts with actual driver versions and real images. Native lanes cover names, handles, content, denied writes, disconnect and unmount errors.
- [ ] Keep per-host status: not run, failed, blocked or qualified. A qualified image mount does not authorize raw devices. Missing privileges/runners block only their profiles and never close the whole phase.
- [ ] Run G on each supported profile and link exact evidence to the fixture/dependency/runtime tuple. Full phase completion requires all originally required hosts; narrower release profiles may qualify sooner.
