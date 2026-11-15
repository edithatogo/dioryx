# Core delivery implementation plan

**Goal:** Prove the baseline and minimal read path without gating it on mount/write infrastructure.
**Architecture:** retain project-owned interfaces and admit qualified dependencies at their first real consumer.
**Spec:** [track specification](spec.md), [design](../../../DESIGN.md), [requirements](../../../REQUIREMENTS.md).
**Execution:** follow the pinned Conductor protocol and [workflow](../../workflow.md), not a second plan hierarchy.

## Global constraints and task cycle

R0 execution status is recorded below; other new work remains pending. Existing directory paths remain stable; the proposed
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

## p1 — Historical compiled seed

Prerequisites: none.

Historical seed only; retain the verification receipt at the end of this plan. No new completion is inferred.

## r0 — Reproduce baseline and apply identity

Prerequisites: `track-001-workspace-and-core-traits#p1`.

Files: `Cargo.toml`, six existing crate manifests, `Cargo.lock`,
`scripts/check_contracts.py`, new `scripts/tests/test_check_contracts.py`, and
only affected namespace documentation. No production behavior change in this phase.

- [x] **R0.1 Reproduce the baseline.** Run unchanged G on the supplied exact tree; record actual compiler/target and lock resolution. A missing compiler/dependency is blocked, not repaired by silently changing pins. Reconcile any failure before feature work.
- [x] **R0.2 Mechanical namespace migration.** First make a manifest/mapping regression fail for the proposed six names. Rename existing packages using the explicit identity table, keep directories and internal dependency aliases deliberate, regenerate the lockfile with Cargo and update the checker's mapping. G plus `cargo metadata --locked --no-deps` must show only the intended package changes. No new umbrella/CLI crate.
- [~] **R0.3 Phase/profile validation.** Add failing `unknown_phase_rejected`, `phase_cycle_rejected`, `profile_cannot_reference_missing_gate` and `historical_pass_cannot_promote_current_profile` and `different_target_or_mode_cannot_satisfy_edge`. Extend the existing checker and its Python tests; preserve compiled-declaration matching. Run `python3 -m unittest discover -s scripts/tests` plus G. Metadata edges are data, not completion evidence.

## p2 — Minimal read-only source/view/budget contracts

Prerequisites: `track-001-workspace-and-core-traits#r0`.

Files: `crates/storage-io/src/lib.rs`, `crates/fs-core/src/lib.rs`,
`crates/storage-io/tests/source_sessions.rs`, `crates/fs-core/tests/capability_domains.rs`.
Consumes seed BlockDevice/read-only wrappers. Produces read-scoped source/view,
mode and budget contracts; this is not implementation of physical-device writes.

- [ ] Add `read_only_is_not_a_snapshot`, `external_change_invalidates_view`, `snapshot_selection_changes_identity` and `stale_view_rejects_cache_fill`. Implement immutable/captured versus opt-in best-effort identity without treating a read-only handle or hash alone as a snapshot.
- [ ] Add `neutral_layer_preserves_xattrs`, `writer_feature_does_not_grant_write` and `nested_work_draws_parent_budget`. Implement only relevant read capability/domain constraints and shared bounds; run the read-only tests in a resolved writer-enabled build once that profile exists.
- [ ] Preserve typed short/truncated reads and independent cursors. Keep the correct small file path as the baseline; substrate migration, writer submission and Moka optimisation belong in p6 and do not block this phase.

## p3 — Consumed container and partition adapters

Prerequisites: `track-001-workspace-and-core-traits#p2`.

Files: `crates/container-core/src/lib.rs`, `crates/volume-core/src/lib.rs`,
`crates/container-core/tests/backing_authority.rs`, `crates/volume-core/tests/native_partitions.rs`.
Consumes p2 bounded reads; produces only the formats used by the next backend.

- [ ] Admit genuine raw/GPT images first. Add `probe_and_failed_open_preserve_source`, invalid primary/backup GPT, overlapping/out-of-range partition and bounded MBR regressions. Select a qualified partition reader; native images accompany the first completed adapter.
- [ ] Add `backing_path_requires_authorized_handle`, aliased/missing member and cycle tests. Resolver authority is explicit handles/ranges; no implicit paths, network requests or host-device scans.
- [ ] Add UDIF only for the APFS DMG consumer with `spool_limit_precedes_write`, decompressor truncation and parent-budget tests. Use private bounded staging, not an invented random-access decoder; no sparseimage claim from native fixture provenance. Add parser fuzz entry points now.

## p4 — Read metadata and capability projection

Prerequisites: `track-001-workspace-and-core-traits#p2`.

Files: `crates/semantics-core/src/lib.rs`, `crates/fs-core/src/lib.rs`,
`crates/semantics-core/tests/projection_fidelity.rs`, `crates/fs-core/tests/read_contract.rs`.
Produces read/list/stat/name/metadata semantics, not the complete mounted mutation API.

- [ ] Pin `raw_names_survive_display_normalization`, `unknown_local_time_is_not_utc`, `unsupported_differs_from_absent_metadata` and `required_feature_fails_before_effects`. Implement typed precision/provenance and declared content-only versus faithful export policy.
- [ ] Pin bounded read-directory pagination, view-scoped node identity and stale-cookie errors. Test against APFS, then exFAT before proposing read API stability; do not require unimplemented rename/unlink to finish the first reader.
- [ ] Synchronize DESIGN declarations only from real compiled code. Preserve no frontend types in core signatures and defer mounted lifetimes to p5.

## p5 — Mounted handle semantics

Prerequisites: `track-001-workspace-and-core-traits#p4`.

Files: `crates/fs-core/src/lib.rs`, `crates/fs-core/tests/handle_lifetimes.rs`;
frontend callers consume this contract in 002/p3.

- [ ] Add stale-handle/generation, bounded handle-table, stable inode, exhausted identifier and directory-cookie tests needed for real read mounts. Distinguish node identity from ephemeral handles and never derive identity solely from paths.
- [ ] Add rename/hardlink/unlink-open lifetime regressions when their real backend consumer arrives; unsupported operations remain explicitly denied. Read-mount acceptance needs its supported operations, not pretend mutation success. Track mutable lifetime coverage separately for 003/p4.
- [ ] Review common semantics against both reader adapters before freezing any public surface; qualifying one mount does not validate all hosts or future writers.

## p6 — Write sessions and measured storage reuse

Prerequisites: `track-001-workspace-and-core-traits#p2`.

Files: `crates/storage-io/src/lib.rs`, `crates/fs-core/src/lib.rs`,
`crates/storage-io/tests/write_sessions.rs`, `crates/storage-io/tests/cache_coherence.rs`.
Consumes p2 source/session contracts; produces the actual writer/flush boundary used by 005.

- [ ] Add missing-flush denial, generation race, overlapping groups, short write, failed barrier, `cancel_after_submission_fences_session` and `revocation_survives_handle_clone`. Implement one serialization/dirty owner with typed uncertain outcomes; no automatic retry.
- [ ] Compare standard positional I/O/small adapters against rust-fs-core only for demonstrated duplication. Hard-gate barriers, aliasing, buffers, safety and API isolation before benchmarking. Select one, or retain the seed; test any upstream `fs_core` alias explicitly.
- [ ] Introduce one clean cache only with measured demand. Test retained/inflight allocation accounting and generation-coherent invalidation independently of eviction weights. Record performance baselines, not invented targets met. Raw OS handles are admitted with 006/p3, not by this file-backed phase.

## Phase 1 verification — 15 November 2026

All five commands in G passed on Linux x86_64 using rustc 1.100.0
(0ef1bc386, 2026-11-09) and the committed lockfile. Nineteen integration tests
passed, zero ignored. The Rust crates have no filesystem backend implementations.
Regular-file test data establishes positional I/O and view bounds only.

Independent source review identified writer-handle erasure through container and
volume trait objects; the accessor and rejecting-writer roundtrip tests resolve
it. Read-only intent, preflight crash-atomic requests and active-path cycle
tracking also have explicit regressions. Full timestamp/permission metadata,
inode/open-handle identity and native policy projection remain phase 4 work.

The source/DESIGN declaration checker, internal links, track dependency DAG and
Conductor gitlink were verified. APFS/exFAT images, native driver mounts, raw
devices, actual writes, fuzz campaigns and benchmarks were not run or claimed.
The configured three-host core CI has not been executed on GitHub. Gemini CLI
registration requires the documented `gemini extensions link` command on a host
with Gemini CLI installed. This closes the bootstrap phase only.


## Revision 0.3 status

The revision-0.3 receipt below is historical. Current R0 execution is recorded in this plan; other feature tasks remain pending. [Revision evidence](revision-0.3.md) records static checks and the unavailable Cargo toolchain.

## R0 execution — sole integration owner

Owner: this existing Dioryx integration chat, explicitly retained by Dylan. No
additional chats/workers are authorised. Reconciled live main
`f4bb9d38b371375e31e418838b958a4bad4b14a8`, all branches/PRs/issues and track owners
on 15 November 2026. PR #2 owns only `renovate.json` and remains untouched.
The durable scope claim is in PR #1 comment 6893339865.

R0.1: freshly rerun Core contracts run 43700815288 on the exact imported main
passed all three hosts. Locally reconstructed tree
`30d613ef47f14656a6a6da7a3eb3a4d5fe74034c` matches GitHub; contract validation passed.
Local Cargo remains unavailable, so hosted execution is required for every head.

R0.2: mechanical six-package/import migration; directories, public behavior,
external dependency versions/checksums, compiler and Conductor pin are unchanged.
Namespace regressions were first run on the baseline: 10 failed as expected.
The staged lockfile rename is provisional until hosted Cargo regenerates identical
bytes under `--offline --locked`; locked check/test and real Cargo metadata are
mandatory. No task is complete until its exact-head review and G pass.

R0.2 is qualified and merged at `1610c1bdd1ada27e2494180fa13bd3088307d252`;
its push/PR runs 43708279112 and 43708308049 passed all three hosts. Structural
R0.3a is qualified and merged at `bc2cdedd7e6248852f960b2f65270b2d547ba123`;
push/PR runs 43709323287 and 43709344426 passed all three hosts. Each head has an
exact-head integration review and a repository automated review without findings.

R0.3b implements scoped prerequisite matching with 25 synthetic regressions and
58 total Python tests passing locally. Exact-head hosted G is required before this
remaining subtask or aggregate r0 is complete. See [schema and evidence](r0-validation.md).
No native profile is promoted. Regression tests live under `scripts/tests`;
validator code stays under `scripts`. PR #3's seven fixture/conformance paths remain
owned by its existing lane; native provenance and conformance CI wiring are not
claimed by these shared contract changes.
