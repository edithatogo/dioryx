# Dioryx — refined delivery plan

**Planning revision 0.3 · 15 November 2026**

**Goal:** deliver a reusable Rust library and mountless tool that can read a
qualified APFS subset, prove the same interfaces with exFAT, then add independently
qualified mounts, overlay mutation and direct exFAT writes.

**Architecture:** project-owned interfaces and authority policy; qualified external
parsers and storage components behind narrow adapters. Keep the synchronous core,
optional delivery adapters and existing six Conductor tracks. No new on-disk
filesystem, general-purpose database, dynamic plugin ABI or parallel planning system.

**Specs:** [requirements](../REQUIREMENTS.md), [design](../DESIGN.md),
[name and namespace](../docs/identity.md). The [track registry](tracks.md) and each
track's `plan.md` own executable tasks; this document is the delivery and priority
view, not another task checklist.

## 1. Historical planning baseline and current execution

The input is the supplied Universal FS revision 0.2 archive, not a live remote.
The original seed receipt reports 19 tests at bootstrap commit
`e0bcbfe774803401aba54e7d25d4ee9271a4e387`; it is historical evidence, not this
revision's test result. All Rust, Cargo, lockfile, toolchain and CI files remain
unchanged in this documentation revision. Nothing is remotely created or published.

The first implementation action is to reproduce the pinned baseline. Do not build
new work on an assumed toolchain, dependency API or historical green receipt.
That planning revision did not perform the rename. Current namespace execution
and exact-head gates are recorded in [track 001/r0](tracks/track-001-workspace-and-core-traits/plan.md);
its status supersedes only those historical implementation statements, not their evidence.

## 2. Choose vertical delivery over infrastructure completion

An infrastructure-first approach would finish raw devices, caching, rich mounted
handles, overlays and every capability domain before demonstrating useful reads.
It delays the highest-risk fact: can the selected APFS reader return correct bytes
from a genuine image? Wholesale adoption of one filesystem suite reduces glue but
makes one upstream ecosystem's limitations our own.

Select the hybrid vertical approach: prove native bytes first, add only the core
contracts required to expose them, validate those contracts against a second
filesystem, and qualify more powerful modes separately. Reuse comparisons must
answer an imminent implementation decision; they are not a new research programme.

## 3. Delivery milestones

Milestones are acceptance boundaries, not promised dates or software version numbers.
An individual host/feature profile may qualify before the full three-host product.
A phase marked complete must meet all of its own gates; partial profile evidence
must not silently close an entire multi-platform phase.

| Milestone | User-visible result | Required evidence | Explicitly excluded |
| --- | --- | --- | --- |
| R0 — Reproducible foundation | Rebuilt seed; planned namespace applied in its own tested change; native fixture admission running | Exact-tree G; reviewed manifest/lock/name mapping; real fixture provenance and hashes | No backend or mount compatibility claim |
| R1 — Native APFS proof | A compiled upstream-backed reader returns selected file bytes from a macOS-generated raw APFS/GPT image | Native tree/content oracle; zero source mutation; unsupported-feature rejection; parser regression/fuzz entry | No VFS facade, custom APFS parser or requirement to finish cache/writes/UDIF first |
| R2 — Mountless reader | Library and CLI inspect/list/stat/extract; APFS raw/GPT and qualified DMG; exFAT validates the same public contract | Per-format/host readback, safe extraction, metadata fidelity, bounded resources and scoped compatibility output | No mount driver, direct device write or general recovery |
| R3 — Read mounts | Qualified image-backed read mounts, independently on Linux, Windows and macOS | Actual runtime and driver; worker isolation; names, handles, cancellation, removal and denied writes | No raw-device broker dependency for ordinary image-only profiles; no implied write support |
| R4 — Overlay writes | exFAT create/write/truncate/rename/delete against an immutable base; export a frozen result to a new image | Both overlay-store and filesystem fault suites, unchanged base, reopened data and native checkers | No merge into the original, raw write or inherited direct-mode atomicity |
| R5 — Qualified direct exFAT | Disposable direct-image qualification, then explicitly admitted device/write mounts | Independent direct-mode faults, native checker plus content retention, exclusivity, broker tests and each host's write-mount evidence | No APFS/NTFS/ext4 writes, unsupported TexFAT, implicit repair or whole-disk unlockers |

R2's APFS image-reader profile can be accepted before the exFAT profile; the
application-facing read API is not declared stable until both have exercised it.
R3 and R4 proceed independently after their prerequisites. Full original MVP
acceptance still requires the original three-host APFS-read and exFAT-write goals;
these smaller milestones do not downgrade those requirements.

## 4. Critical path and actual parallelism

```text
001/r0 baseline and namespace
  + 006/p1 native fixture admission
      -> 002/p1 direct APFS proof
  + 001/p2 read-only source/view/budget contracts
      -> 001/p3 raw/GPT/UDIF adapters
      -> 001/p4 read metadata and capability projection
          -> 002/p2 APFS library + CLI (R2 APFS)
          -> 003/p1 exFAT reader and writer selection (R2 exFAT)
          -> 004 readers only after current priorities have an owner

001/p5 mounted handle semantics + 006/p2 image-worker isolation
  -> 002/p3 frontend -> 002/p4 per-host read mounts (R3)

001/p6 write-session contracts + 005/p1 store selection
  -> 005/p2 overlay -> 003/p2 exFAT overlay mutation
  -> 005/p3 persistence fault qualification + 003/p3 writer qualification
  -> 005/p4 frozen image export (R4)

006/p3 raw-device broker + direct-mode qualification
  -> 003/p4 per-host direct write mounts (R5)
  -> 006/p4 joins only evidence required by the advertised release profile
```

The exact phase edges are in each `metadata.json`. Track-level dependencies are
context references, not a demand to finish whole tracks. Native APFS proof does
not wait for 001/p3/p4; fixture infrastructure no longer waits for container work.
The overlay does not wait for its exFAT consumer. Full-suite release assembly does
not hold back a narrower profile that has met all of its own gates.

## 5. Bounded dependency decisions

Use a staged screen, not an unlimited bake-off. Inspect the shortlist's manifests,
source boundaries, licenses and read/write APIs. Take at most two viable candidates
per subsystem into executable comparison at once. A third enters only after a
recorded failure or material missing capability. Pin the source/version/features
at the experiment; do not turn this plan's candidate list into Cargo dependencies.

Hard rejection criteria precede scoring: missing required semantics, uncontrolled
source writes, unresolved safety/license incompatibility, silent data substitution,
unbounded critical behavior or untestable persistence. No weighted score may hide
a failing hard gate. Then compare maintained adapter code, dependency graph,
resource use, benchmarked overhead and upgrade effort on the same fixtures.

| Decision | First comparison | Exit and fallback |
| --- | --- | --- |
| APFS | `apfs` on a genuine raw image; `cmpfs`/`udif` only for their actual consumers | Correct bytes and explicit rejected features; one bounded upstream fix or justified alternate reader, never a mock facade |
| exFAT | Source-screen `fs-pc`/`fs_pc`, `fstool`, and a safety-resolved `embedded-exfat`; advance only two | Select read and write engines separately if necessary; their metadata/flush ownership must not conflict; custom mutation only for a demonstrated gap |
| File I/O | Existing small implementation plus standard positional I/O versus `rust-fs-core` | Keep the seed unless replacement measurably reduces code without losing policy; no early whole-stack migration |
| Overlay | `redb` changed-block map; compare one image engine only if it passes the source screen and meets a real interoperability need | One durable store, one writer; no bespoke WAL/B-tree and no forced unsuitable competitor |
| Extraction | `cap-std` / `cap-tempfile` behind the existing semantics policy | Required alias/race/no-clobber tests; dependency alone is not sandbox evidence |
| Later readers | `ntfs`, then `ext4-view`, then HFS+; Btrfs remains lower priority | One supported subset per consumer; no automatic write-engine activation |

Keep one clean-cache policy per logical address space and one dirty transaction
owner. A second cache needs measured justification and explicit coherence. Retain
zerocopy for suitable fixed layouts; do not add several binary-parser frameworks
until an actual remaining parser requires them. Performance targets stay unmeasured
until recorded; cache optimisation does not block correct uncached reads.

## 6. Three design refinements that affect execution

### 6.1 Separate included code from permission to perform I/O

Cargo features choose compiled capabilities, not runtime authority. They are
additive and can be unified by another dependency. Enabling a writer must never
make a read-only session writable. Negotiation requires explicit request intent,
source/session authority, supported filesystem features, view consistency and
frontend limits. Tests run the read-only path in a build where writers are enabled.

Use a small admission state model: proposed -> admitted -> open -> fenced -> closed.
No I/O beyond bounded inspection before admission; destructive authority must be
explicit. Fenced sessions cannot regain write permission by retrying, cloning a
handle or reopening a worker. A new qualified session is required.

### 6.2 Distinguish library isolation from the CLI's process boundary

The embeddable library is in-process and reports its caller's isolation duties.
It does not promise a process sandbox. The first reader experiment runs against
controlled fixtures in a disposable test environment. A CLI profile advertised for
hostile images requires its host-qualified low-privilege worker. Ordinary image
reads do not require the privileged raw-device broker; raw/elevated access does.
No unavailable sandbox silently falls back to a supposedly isolated profile.

### 6.3 Fault-test both persistence paths

A wrapper around the filesystem's BlockDevice does not necessarily intercept a
transactional store's own writes. The overlay candidate must expose its persistence
I/O to a deterministic fault seam or an equivalent instrumented environment.
For redb, evaluate the documented StorageBackend/create_with_backend extension
point at the pinned release. Exercise real commit/reopen behavior through it.

Use two named suites: filesystem operation ordering and overlay-store durability.
Process-kill tests are useful but not power-loss proof: persistence models must
state permitted reordering, torn writes, cache survival and barrier semantics.
Each result records fault coverage and exclusions. Hardware claims require their
own evidence; neither suite upgrades ordinary exFAT into a journaled filesystem.

## 7. A compact native corpus, expanded by demonstrated risk

Start with one small native baseline and one feature-rich fixture for each of
APFS and exFAT, plus an explicitly unsupported case. For APFS, capture separately
identified live-tree, compressed-file and snapshot-bearing variants; exact selected
snapshot reading is a different claim. For exFAT, include contiguous/fragmented
files, directory growth, Unicode/upcase behavior and near-full allocation.
Do not force an exact small image count if the native format requires more images
to cover those cases. Native tools generate masters; fuzzer mutations are derivatives.

Every manifest binds generator host/tool/version/commands, container/partition and
filesystem feature set, image hash, expected file hashes and relevant metadata.
Keep immutable masters out of write/checker mounts; use fresh copies, because a
native mount can perform recovery. Authoritative oracle creation and cross-host
consumer execution are separate jobs: a Linux runner can consume a macOS-generated
APFS image but cannot claim it generated one natively.

Metadata has three explicit states: present, absent, unsupported. Content-only
extraction can omit metadata only when the selected mode discloses the losses;
faithful export fails if a required field cannot be represented. Never return an
empty successful file for an unsupported codec or normalize away raw-name identity.

## 8. Ownership and work-in-progress limits

One integrator owns root manifests/lockfile, compiled contracts, source API changes,
CI, the track registry and qualification schema. Backend owners own their dedicated
adapters/tests. Native qualification owners own host runners and append scoped
results; they do not change backend semantics to pass a checker. These are roles,
not workers created or people assigned by this document.

Default active work is one shared-core change and at most one nonoverlapping
backend or fixture change. Confirm ownership before changing shared paths. Expand
parallelism only after contracts and paths are stable. A task implements one
independently reviewable behavior, with its failing test, minimal change and exact
head evidence. Do not combine dependency migration, public API redesign and a new
filesystem writer in the same change.

## 9. Gates, stop rules and deferred scope

G remains mandatory for every completed task, including planning changes:

```bash
cargo fmt --all -- --check
cargo check --workspace --locked
cargo test --workspace --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
python3 scripts/check_contracts.py
```

Every feature also has its real-image, fault or host gate. Fixture absence, native
runner absence, a safety conflict or a mismatched source digest blocks the affected
acceptance; it is never counted as a skip/pass. A blocked Windows mount does not
falsely fail a qualified Linux image reader, or falsely complete the Windows task.

The existing contract checker needs a tested extension for phase/profile edges in
001/r0. This revision validates that graph separately without claiming the
unchanged repository checker already understands it. Evidence keys bind source
tree, dependency lock/features, target/runtime, fixture/oracle identity, mode and
fault model. Reports are generated from existing results, not copied dashboards.

Stop a dependency experiment after its predefined decision is answered; keep a
short accept/reject/blocked record in the owning track. Do not create another
engine because a desirable feature lacks evidence. Defer public API freeze until
APFS and exFAT have both consumed the contracts, and defer final API stability until
write and frontend requirements have been exercised. Narrow preview releases may
remain explicitly unstable.

Deferred: raw-device overlay merge, journal recovery beyond a qualified overlay,
NTFS/ext4/APFS writers, multi-device write pools, cloud/object-store sources, broad
ABI bindings, FSKit/ProjFS/WASM, a plugin marketplace and new general-purpose
cryptography. None becomes necessary to complete R1/R2.

## 10. Immediate implementation order

1. **001/r0:** reproduce baseline G; apply/test the namespace migration and phase
   checker in separate mechanical/validation changes; preserve the source-derived
   DESIGN contracts and historical receipt.
2. **006/p1 + 002/p1:** obtain the first genuine macOS fixture and native oracle;
   compile the upstream APFS proof and compare actual bytes before implementing VFS.
3. **001/p2 + p4:** add only source/view/budget and read-metadata contracts needed by
   that proof; preserve write-ready seed interfaces without building a writer.
4. **001/p3 + 002/p2:** add the real GPT/UDIF path and capability-scoped extraction;
   deliver an image-backed library/CLI profile and its exact limitations.
5. **003/p1:** repeat the same read contract with exFAT and decide the writer reuse
   question; do not begin custom allocation work before the decision.
6. **001/p5 + 006/p2 + 002/p3/p4**, or **001/p6 + 005**: advance read mounts and
   overlay infrastructure as independent bounded lanes, respecting shared ownership.

Steps describe ordering, not tasks already executed. The individual track plans
provide exact file scopes, regression names and gate expectations. Current review
focus is stale views, feature-unified write escalation, aliases of the source,
false successful decoding and fault injection that misses the actual store I/O.

## Scoped prerequisite resolution

A phase edge requires its accepted interface checkpoint and, for native work, the
matching target/profile evidence. It does not require unrelated host lanes to pass.
For example, a qualified Linux image worker can admit the Linux image-mount lane
while Windows isolation remains blocked; aggregate 006/p2 stays pending until all
required hosts pass. An unreviewed partial implementation cannot satisfy an edge.
The r0 phase/profile checker must reject evidence with a different target, mode or
source/contract revision, and must never use a historical phase status as evidence.
