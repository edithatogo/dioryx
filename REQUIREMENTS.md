# Dioryx — requirements

Version 0.3 planning revision, 15 November 2026. The accepted direction is to own
interoperability, safety policy and qualification, reusing qualified format
engines rather than assuming new writers are necessary. This revision changes
specifications and plans, not the compiled seed or dependency lockfile.

Bootstrap, useful read-only delivery and the full product MVP are separate
milestones. Full MVP retains the original cross-host read/write requirements. The R0–R5
milestones and profile gates in [delivery plan](conductor/delivery-plan.md) allow
useful read-only acceptance without waiting for unrelated writer or broker work. Additional readers in 004
and journal recovery beyond exFAT remain independently phased. A successful
core test run does not establish filesystem or mounting compatibility.

## Must

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| M01 | Cargo-first; every completed task passes gate G, including documentation tasks. No empty feature crates or root audit bloat. | Locked check/test, format, clippy and contract/link validation on the final tree. |
| M02 | Project-owned storage, container, pool, transform, semantics and VFS interfaces; format engines never depend on frontends. | Compiled contracts and dependency DAG; no upstream public types crossing the adapter boundary. |
| M03 | Bounded positional reads, checked geometry and explicit access mode for files and qualified raw devices. | Overflow, alignment, truncation, removal and native source tests; no writes during probe/open/read. |
| M04 | Qualified raw/UDIF and GPT/simple MBR composition; optional layers in format-dependent order. | Native images, backup GPT/bounds checks; named rejection of unsupported features and ambiguous probes. |
| M05 | APFS supported-subset read/list/stat/extract using native macOS images, including snapshot-bearing and compressed variants. | Per-feature content and metadata oracles; no live-tree substitution for requested snapshots; unknown required features reject opening. |
| M06 | exFAT read qualification precedes writes. Evaluate existing engines before custom bitmap/FAT/directory mutation. | Same genuine-image, operation-trace, fault and native-checker suite for each candidate; custom implementation justified only by demonstrated gaps. |
| M07 | Independently qualified APFS read mounts and exFAT write mounts on Windows, Linux and macOS. | Actual native runtime lanes, error propagation, handle lifetime, names, fsync and unmount tests; mountless mode remains unprivileged. |
| M08 | Separate storage guarantees, filesystem operations, semantic projection and frontend limits. Negotiate only relevant constraints and explain every denial. | Monotone reduction tests; required features fail before effects; read-only intent and unsupported lower-layer writes cannot be bypassed. |
| M09 | Separate ordering, durability, operation visibility and crash atomicity. Retain generation-checked batches and typed uncertain outcomes. | Short/torn I/O, failed barriers, cancellation after submission and removal; invalidate/fence on uncertainty, never blind retry. |
| M10 | Preserve native filename identity/collation and timestamp precision, offset provenance and raw unknown values. | Non-UTF8, unpaired UTF16, normalization/case collisions and unknown-local-time fixtures; no silent UTC conversion. |
| M11 | Explicit ownership, ACL, SID and AppleDouble policy; synthesized metadata is labeled. | Stored versus projected versus unavailable fields, owner-scoped defaults and no silent privilege escalation. |
| M12 | Stable node and open-handle identity within a selected view; IDs survive rename and detect stale reuse. | Hardlink, unlink-while-open, cookie pagination, snapshot switch and exhausted identifier tests. |
| M13 | First-party parsing/core crates forbid unsafe; only reviewed platform modules may make scoped exceptions. Dependency safety is assessed separately. | Exact-feature transitive inventory, license/provenance review and native boundary tests; no zero-unsafe claim inferred from a wrapper. |
| M14 | Typed errors and bounded parsing, decompression, traversal and probing with cancellation. | Parser fuzzing from first integration; global resource accounting and malformed native-image derivatives; no panic/loop acceptance. |
| M15 | Extraction is destination-handle-relative and rejects escape, aliases of the source, unsafe special files and silent collisions. | Symlink/reparse substitution races, hardlink aliases, reserved names, quotas and no-clobber publication tests on each host. |
| M16 | Genuine native-image provenance, content/metadata oracles and independent checkers. | Tool/OS versions, creation commands, feature manifest and final hash; missing required fixtures fail acceptance. |
| M17 | One coherent clean-cache policy per address space, immutable view/generation keys and a separate dirty owner. | Concurrent fill/invalidation tests; no hidden competing write-back cache; account retained buffers and codec/index memory. |
| M18 | Pin accepted dependencies and Conductor; qualify exact version, features, target and storage mode. | Lockfile/gitlink, reproducible build inputs and scoped admission records; updates re-run affected gates. |
| M19 | Choose existing components through a measured comparison, not a reuse percentage or feature-table claim. | Adapter complexity, safety, correctness, resource use, licenses, maintenance and fallback decision recorded in the owning track. |
| M20 | Explicit source-consistency and view identity contract. A read-only handle is not a snapshot. | Immutable capture/snapshot or qualified exclusive ownership for coherent views; external modification and stale-generation tests; live best-effort mode labeled and opt-in. |
| M21 | Image-specified backing files, pool members and external resources never confer host authority. | Resolver accepts only authorized handles/ranges; reject path/URL/device discovery, ambiguous members, cycles and excess nesting by default. |
| M22 | Add a base-preserving overlay before direct raw writes. Its own persistence/recovery must be qualified separately. | Hash-preserved base, torn/crash/reopen tests, overlay identity/geometry/version checks, quota/disk-full tests and frozen-view export to a new image. |
| M23 | Separate unprivileged parsing from privileged raw-device access and destructive operations. | Per-host broker/worker isolation, bounded/versioned IPC, range/access checks and verified exclusive-device admission; no silent elevation. |
| M24 | Enforce a session-wide resource budget across nested layers and parser workers. | Shared accounting for buffers, decompressed output, indexes, handles, temporary storage and work; deterministic cancellation and no-write fencing after uncertain submission. |
| M25 | Capability evidence distinguishes advertised, source-reviewed, compiled, native-qualified and fault-qualified status. | Machine-readable compatibility report keyed by exact version/target/format feature/view mode; shared upstream/forks do not count as independent oracles. |
| M26 | Recovery is an explicit view, not an implicit source write. Dirty unsupported volumes fail closed. | Source unchanged across probe/open/failed open/list; native mount/recovery tools run only on expendable copies; replay requires a qualified overlay or explicitly authorized write session. |

| M27 | Build features do not grant runtime authority; unified writer features cannot upgrade a read-only session. | Read-only regressions in writer-enabled builds; explicit session admission, revocation and no writes after fencing. |
| M28 | Fault qualification reaches both filesystem operation I/O and the overlay store's actual persistence I/O. | Distinct failure schedules, real commit/reopen, stated persistence model and honest separation of process-kill from power-loss evidence. |
| M29 | Release claims are per host, image/device mode, operation and feature subset; in-process libraries do not imply parser process isolation. | Profile prerequisites checked against exact evidence; hostile-image CLI/privileged profiles enforce their own native security gates; no universal success badge. |

All Must requirements remain gates if an upstream dependency cannot meet them.
A declared limitation is not a passing test. The original seed remains narrower
than this specification until its owning tasks are implemented and qualified.

## Should

| ID | Requirement | Acceptance target |
| --- | --- | --- |
| S01 | Bounded streaming and read caching. | Default clean-cache weight 128 MiB, inflight payloads 32 MiB and transfer size at most 1 MiB, with independent hard admission. Report total RSS including indexes and codec state. |
| S02 | Competitive transparent-wrapper performance. | Recorded-host 1 GiB sequential read no more than 15% slower than buffered direct-file baseline; controlled repeated 4 KiB random set at most half cache budget saves at least 90% of source reads. These targets remain unmeasured. |
| S03 | Bounded probes and materialization. | At most 1 MiB probe bytes per source and a session-wide admission budget, nesting at most 8, default spool quota 8 GiB; explicit configurable node/output/time limits. Child budgets cannot multiply the parent allowance. |
| S04 | NTFS/ext4 read-only readers, then HFS+; Btrfs remains medium priority. | Prefer narrow read-only implementations when they meet the feature corpus; compare whole-engine alternatives without assuming writes are safe. |
| S05 | APFS snapshot browsing and additional volumes. | Separate feature qualification; snapshot-bearing live-tree access alone does not satisfy this. |
| S06 | Versioned machine-readable metadata, evidence and diagnostics. | Lossless names, stable error categories and limits, redaction and explicit synthesized fields; no host-path/key leakage. |
| S07 | Minimize format-specific code and framework duplication. | Benchmark a standard-library/small-crate path against a shared substrate; one selected parser/cache/transaction owner per role, with documented exceptions. |
| S08 | Overlay implementation reuses a qualified transactional store or disk-image engine. | Compare redb-backed blocks with one suitable existing image implementation; no new general-purpose WAL, B-tree or disk format without a demonstrated missing requirement. |
| S09 | Property, concurrency and fault testing complement fuzzing. | Operation traces and proptest invariants; Loom for applicable synchronization models; deterministic storage faults remain separate from thread-interleaving tests. |

## Could

- C01: FSKit app-extension frontend, ProjFS projection or WASM mountless viewer.
- C02: Btrfs subvolumes, UDF/ISO9660 and richer HFS+ resource-fork projection.
- C03: Indexed random-access UDIF after bounded spooling is correct and profiled.
- C04: Reversible names/stream export manifests, explicit identity maps and AppleDouble.
- C05: Read-ahead, async device I/O and additional image formats justified by measurements.
- C06: Read-only journal-recovered ext4/NTFS views after independent recovery qualification.

## Won't for MVP

- W01: APFS, NTFS, ext4, Btrfs or ZFS direct writes; kernel filesystem drivers.
- W02: Whole-disk unlocking; XTS primitives alone are not BitLocker/LUKS/APFS unlockers.
- W03: Universal crash-atomic exFAT transactions or transparent crash-atomic rename.
- W04: VHDX/VMDK/QCOW2/sparseimage compatibility merely because test tools can attach them.
- W05: Writable multi-device pools, RAID repair, automatic filesystem repair or destructive discovery.
- W06: Whole-stack zero-unsafe claims, universal compatibility or a fixed 150-line bridge.
- W07: Automatic overlay merge into the original raw device, silent recovery replay or external backing-resource discovery.
- W08: A new generic storage database, an unneeded plugin ABI or wholesale migration to one unqualified filesystem ecosystem.

## Traceability and acceptance

001 owns core M01–04/M08–14/M17–21/M24 foundations. 002 owns APFS M05/M07,
extraction M15 and its native corpus. 003 owns exFAT M06/M07 and mutation
M09/M17. 004 owns S04 and each added reader's inherited safety gates. 005 owns
M22/M26 overlay/recovery and export. 006 owns M16/M18/M23/M25 qualification
infrastructure and release evidence; it starts early, not after all backends.
Detailed phase dependencies are in [tracks](conductor/tracks.md).
M27 is owned by 001/p2 and 001/p6; M28 by 005/p3 and 003/p3; M29 by 006/p2–p4.
Scoped host/profile prerequisites are defined in the delivery plan; they never substitute
a narrower result for full three-host MVP completion.

The revision's verification status is recorded in the
[track 001 revision record](conductor/tracks/track-001-workspace-and-core-traits/revision-0.3.md).
No task is complete until the unchanged Cargo gate passes on the revised tree.
