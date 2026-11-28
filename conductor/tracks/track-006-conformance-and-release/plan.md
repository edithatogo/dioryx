# Early evidence, separated authority and scoped release

**Goal:** Start native evidence immediately and qualify only the authority each delivery profile uses.
**Architecture:** retain project-owned interfaces and admit qualified dependencies at their first real consumer.
**Spec:** [track specification](spec.md), [design](../../../DESIGN.md), [requirements](../../../REQUIREMENTS.md).
**Execution:** follow the pinned Conductor protocol and [workflow](../../workflow.md), not a second plan hierarchy.

## Global constraints and task cycle

Unmarked work below is pending. Existing directory paths remain stable; the proposed
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

## p1 — Native corpus and evidence admission

Prerequisites: `track-001-workspace-and-core-traits#r0`.

Files: `tests/fixtures/` manifests, functional `tests/conformance/` validators and
`tests/conformance/test_evidence.py`; reuse existing baseline fixture recipes.

- [x] Make missing fixture, bad hash, absent native provenance, wrong feature manifest and shared-oracle ancestry regressions fail before admitting the first fixture. PR #10 merged at `259a822b56008d2c0de05d5cd4a026f81a5bbef9`; [exact merge-tree G](https://github.com/edithatogo/dioryx/actions/runs/46083930742) and [post-merge G](https://github.com/edithatogo/dioryx/actions/runs/46084058994) passed with 53 conformance tests on each of three hosts and independent review. No native admission is implied.
- [~] Import small native masters and expected file/metadata oracles; keep original masters immutable and mount/check fresh copies. A downstream host consumes provenance rather than claiming to be its native generator. PR #13 acquired genuine baseline candidates, #14 merged independently pinned archive verification and local no-clobber retention, and #15 acquired expanded native raw GPT/APFS and exFAT candidates; see [receipts](../../../tests/fixtures/native-acquisition.md). Durable private remote corpus, snapshot/compression/fragmentation/malformed coverage, reviewed rights and accepted qualification remain outstanding.
- [ ] Implement minimal versioned evidence tied to source/features/host/view/fault model; never promote advertised or compile-only results. G plus `python3 -m unittest discover -s tests/conformance` and actual native admission are required.

## p2 — Image-worker isolation by host

Prerequisites: `track-006-conformance-and-release#p1`, `track-001-workspace-and-core-traits#p2`, `track-001-workspace-and-core-traits#p4`.

Files: functional CLI worker path and `tests/native/authority/image_worker/`.
This phase owns image-only isolation, not physical-device brokerage.

- [ ] Add unauthorized path/network/process requests, oversized IPC, escaping extraction and stuck-parser budget tests. Model in-process library behavior separately; it cannot claim worker isolation.
- [ ] Implement bounded/versioned IPC and per-host low-privilege image-worker policy with explicit handles. A simple subprocess without confinement is not qualification. Missing native confinement blocks that hostile-image profile, not the controlled fixture experiment.
- [ ] Run actual Linux/Windows/macOS host evidence independently, including worker death and no silent fallback to broader authority. G remains mandatory; scope reports to the actual qualified host.

## p3 — Raw-device broker and write authority

Prerequisites: `track-006-conformance-and-release#p2`, `track-001-workspace-and-core-traits#p6`.

Files: reviewed OS device/broker modules and `tests/native/authority/raw_device/`.
Consumes actual write-session fencing and p2 worker isolation.

- [ ] Add changed-device identity, unsupported exclusivity, conflicting mount, unauthorized/out-of-range I/O, permission revocation and write-after-worker-death regressions.
- [ ] Implement only explicit device/range/access authority with narrow reviewed FFI and SAFETY invariants. Do not treat mount permission or a writer-enabled build as permission to mutate physical disks.
- [ ] Qualify native disposable-device ownership and failure behavior independently per host. No live user device is a test fixture; unsupported ownership or removal behavior leaves raw writes disabled.

## p4 — Profile release assembly and full-scope join

Prerequisites: `track-002-apfs-readonly-and-mount#p4`, `track-003-exfat-read-write-engine#p4`, `track-005-overlay-and-recovery#p4`, `track-006-conformance-and-release#p3`.

Files: supported-profile CI and generated release evidence, only when remote
execution/distribution is explicitly authorized. Full phase closure joins the
original full product scope; narrower profiles are assessed by their own table.

- [ ] Evaluate `qualification_profiles` against exact phase and native result evidence. Produce separate Linux/Windows/macOS and image/device/read/overlay/direct cells; no aggregate green result fills a missing cell.
- [ ] Run G plus relevant parser/fault/native/resource gates on exact release inputs. Inspect licenses, advisories, source provenance and resolved Cargo features; unsafe inventory is not a proof of safety. Optional track-004 readers add their own gates.
- [ ] Generate compatibility reports from existing evidence, validate artifact identity and obtain release authorization. No paid jobs, driver installation, signing, package reservation or publication is implied by planning acceptance.
