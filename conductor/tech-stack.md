# Technical stack

## Build and workspace policy

Use Rust 2024, Cargo resolver 3, the pinned Rust 1.100.0 toolchain, and a committed
`Cargo.lock`. The initial verification target is Linux; successful checks there
do not qualify Windows, macOS, their raw-device APIs, or their mount runtimes.
Run `cargo check --workspace --locked` and `cargo test --workspace --locked` for
every completed task, including context-only changes. The required formatting,
lint, fixture, and platform gates are defined in [workflow.md](workflow.md).

The seed deliberately contains six useful core crates. Backend, CLI and mount
crate directories become Cargo members only when their first real operation
and its tests exist. An interface contract is not filesystem support.

| Crate | Initial responsibility | Planned addition |
| --- | --- | --- |
| `storage-io` | Read-only regular-file device; bounds and durability contracts | Raw-device shims, positional cursor adapters, read cache, write batches |
| `container-core` | Raw-container identity adapter and container contract | Validated UDIF unwrapping |
| `volume-core` | Bounded slices and single-volume pool | GPT, simple MBR, later logical pools |
| `transform-core` | Bounded identity transform and transform contracts | Shared checksums, codecs and qualified encryption |
| `semantics-core` | Raw-name policy, NFC/NFD utilities and timestamp types | OS projection, identity maps and AppleDouble policy |
| `fs-core` | Capability negotiation, VFS contracts and bounded probing | Backend registry integration and stable mounted identity |

`fs-core` depends on our contracts, never on a mount crate. Backends consume
logical storage and implement `VirtualFs`. Frontends consume `VirtualFs`; the
CLI is the composition root. Container, partition, pool and transform layers
may recur where a format requires nesting. ISO9660 and UDF are filesystems,
whereas an ISO-named file may simply be their raw byte source.

Only `thiserror` 2 and `unicode-normalization` 0.1 are admitted external code
dependencies in the seed. Cargo records exact resolved versions and checksums.
The latter offers the smaller initial Unicode surface; ICU4X
`icu_normalizer` remains an alternative if measured requirements justify its
data and integration cost. Generic Unicode normalization must not replace
APFS, HFS+, NTFS or exFAT's format-specific comparison rules.

## Reuse-first selection (revision 0.2)

The current Cargo dependency set is unchanged. Candidate selection is deliberately
separate from admission: docs and feature lists are evidence to investigate, not
permission to enable a writer. Compare narrow standard-library/small-crate adapters
against larger shared substrates; preserve project-owned interfaces in either case.
No framework migration or dependency exception has been approved.

| Role | Preferred evaluation | Code potentially avoided | Gate |
| --- | --- | --- | --- |
| Positional I/O | Standard FileExt APIs; positioned-io if a shared adapter helps | Cursor/slice glue | Short/interrupted reads, concurrency, Windows/Unix behavior; flush remains explicit |
| Shared block substrate | rust-fs-core versus existing small storage-io implementation | File/slice/count/cache adapters | Private Cargo alias for its fs_core library name; no lost barriers, identity or uncertainty; disable duplicate caching |
| NTFS read-only | ntfs; compare rust-fs-ntfs only on demonstrated benefit | NTFS parsing | Exact-feature native-image qualification; write support not admitted by reader success |
| ext4 read-only | ext4-view first; compare rust-fs-ext4 for gaps | ext2/3/4 read structures | Clean-image feature coverage; dirty/recovery-required images reject until recovery is qualified |
| exFAT | Compare fs-pc/fs_pc, fstool and safety-resolved embedded-exfat | Potentially most custom mutation | Provenance/license/unsafe/API checks plus identical native and crash corpus; no preselected winner |
| Future images/partitions | rust-img-* / rust-disk-partitions versus existing choices | Virtual-disk/partition parsers | Backing-resource authority, no implicit replay/write, exact format features, dependency scope |
| Extraction and spooling | cap-std and cap-tempfile | Destination confinement and private temporary-file glue | Reparse/symlink races, source aliases, no-clobber publication and quotas; not a process sandbox |
| Durable overlay | redb versus one qualified image-engine implementation | Custom WAL/index/B-tree | Coherent base, durable block+index transaction, crash/reopen, disk-full and amplification measurements |
| Missing binary layouts | zerocopy fixed structures; binrw only when useful | Repetitive decoding/encoding | Bounds, allocation counts, endian/semantic checks and fuzzing; do not reparse formats an admitted engine already handles |
| Ephemeral handles | Existing checked IDs; slotmap-careful only if justified | Handle-slot bookkeeping | No reuse/wrap alias, bounded tombstones; not persistent inode identity |
| Test/tooling | proptest, cargo-fuzz, Loom, criterion; cargo-deny/audit/vet | Test generation and supply-chain tooling | Exact versions/features pinned at admission; no tool output is itself correctness proof |

An optional upstream FFI API must not be enabled merely because it exists. Reuse
its safe Rust API where possible; audit transitive unsafe under the unchanged
policy. Process sandboxing and raw-device authorization are host-specific work,
not capabilities provided by a Rust dependency name.

## Original candidates and admission constraints

Historical seed observations and newly checked candidate documentation are recorded in
[dependency evidence](../docs/dependency-evidence.md). These are prospective
choices, not dependencies silently enabled by the bootstrap. Each admission
records the resolved version, features, license, unsafe/FFI boundary, supported
formats, real-fixture results and fuzz entry point in its owning track.

| Area | Choice and reason | Admission condition |
| --- | --- | --- |
| APFS | `apfs` 0.4.1; existing read-only parser over `Read + Seek` | Prove supported live-tree reads; explicitly handle unsupported snapshots, clones, encryption and additional volumes |
| Apple compression | `cmpfs` 0.1.0; shared decmpfs decoding, already used by `apfs` | Qualify each encoding; preserve user forks without restoring compression metadata onto decompressed files |
| DMG | `udif` 0.4.2; existing checksummed codec/container support | Stream into a quota-controlled temporary file initially; no undocumented random-access claim |
| exFAT reads | Compare the above engines; embedded-exfat remains a conditional baseline candidate | Resolve its unsafe-source findings and actual I/O API before admission; no winner is predetermined |
| exFAT writes | Qualified existing engine first; bounded upstream fix or focused zerocopy mutation only for proved gaps | Same native, fault, flush and semantic gates regardless of implementation owner |
| GPT / MBR | `gpt` 4.1.0 and restricted `bootsector` 0.2.0 | Validate both GPT copies and bounds; restrict MBR until extended chains and sector variants are tested |
| Cache | `moka` 0.12 sync cache with byte weights | Cache clean reads only; enforce a separate hard memory-admission budget |
| Mounts | `unifuse` 0.3.0 plus Tokio, behind `mount-unifuse` | Qualify Unix `rfuse3` and Windows `winfsp` adapters independently |
| Later readers | `ntfs`, `ext4-view`, then `hfsplus`; compare broader engines | Read-only real-image qualification before capability advertisement |

The proposed APFS dependency does not supply snapshot browsing or general
multi-volume support. Track 002 retains these acceptance gaps explicitly; it
must not turn the upstream feature table into a whole-format promise.
`newtua-apfs` 0.2.0-newtua.2 is a comparison/fallback candidate, not an assumed
maintained replacement: its author disclaims independent maintenance.
`filer-ext4` 0.0.4 has a reader but retains experimental API and Filer coupling;
`filer-exfat` is only monitored. Do not build against a reserved crate name.

`gpt` requires a `Write` bound even for read inspection. Its adapter returns
permission errors for writes and opens the underlying source read-only.
`bootsector` does not validate backup GPT or traverse extended MBR partitions;
the wrapper must not imply otherwise. APFS/UDIF cursor APIs receive separate
logical cursors over positional storage. Blocking readers run on bounded
worker threads when called by an async frontend.

The seed review of `unifuse` Windows source flagged admission issues:
that inspection found discarded flush errors, ignored granted-access
mode and lossy path conversion. Reproduce these against the selected release;
never advertise durability or exact-name preservation through that path first.

## Safety, transforms and durability

Every first-party filesystem, container, volume, transform, semantics and VFS
crate uses `#![forbid(unsafe_code)]`. Dependencies are evaluated separately;
safe wrappers do not make their dependency graph zero-unsafe. The current
`embedded-exfat` source contains unsafe transmutation. No exception is admitted
by this document. Admission must resolve that conflict under the project's
documented safety boundary.

Any necessary raw-device FFI belongs only in reviewed, feature-gated platform
modules of `storage-io`; mount FFI belongs only in mount frontends. Those crates
must narrow any future lint exception to the actual platform module and retain
`// SAFETY:` invariants, native tests and an unsafe inventory. All other modules
retain the prohibition. `rustix` or `nix`, and `windows-sys`, are candidates for those shims; avoid adopting both Unix wrappers without need.

Use endian-aware `zerocopy` layouts for mutation records. Consider `bytemuck`
only where its layout requirements have been proved; casting never substitutes
for length, alignment, checksum or semantic validation. Typed errors use
`thiserror`. Check all arithmetic, traversal budgets and decompressed lengths.

Choose checksums by format: `crc32fast` implements CRC-32, not CRC32C; ext4-style
CRC32C requires a Castagnoli implementation. Validate APFS Fletcher-64 against
independent known answers before sharing it. `sha2` hashes fixture payloads
and supports future integrity schemes; it is not a substitute for on-disk
checksum algorithms. Codec candidates are `flate2`, `lz4_flex`, `lzfse_rust`
and Zstandard support. The `zstd` crate brings a native C implementation through
FFI; evaluate read-only `ruzstd` when pure Rust is required, or record an
explicit dependency-boundary decision. Never label the former a zero-FFI stack.

`aes` and `xts-mode` are building blocks, not BitLocker, LUKS or APFS unlockers.
Those require format-specific key derivation, metadata, keybags and address/tweak
rules. XTS is not authenticated encryption. Future keys use bounded lifetimes,
redacted diagnostics and a reviewed zeroization policy.

Moka admission/eviction is best-effort; its weighted capacity is not a strict
resident-memory guarantee. Dirty write batches live outside the evictable read
cache. Flush groups express ordering and reported durability, not atomicity.
Storage barriers cannot make nonjournaled exFAT transactions crash-atomic.

## Platform prerequisites and delivery

| Host | Mountless build/run | Planned mounting and raw devices |
| --- | --- | --- |
| Linux | Rust toolchain, linker and ordinary image-file permissions | FUSE kernel support, `/dev/fuse` access and `fusermount3`; `libfuse3` development files only if the selected binding requires them; raw-device permissions are separate |
| macOS | Rust plus Xcode Command Line Tools; `hdiutil`/`diskutil` for native fixtures | macFUSE runtime and its installation requirements for that adapter; raw devices need appropriate privileges; FSKit is a separate future app-extension frontend |
| Windows | MSVC Rust target and Visual Studio C++ build tools | WinFsp runtime and SDK/binding prerequisites; administrative installation and raw-device access are separate from image inspection |

Mountless operation must not load mount-driver libraries or require elevation.
Driver distribution licenses are separate from Rust crate licenses: `unifuse`
is MIT, while the selected WinFsp distribution has GPLv3 FLOSS-exception/commercial
terms. Review those terms and macFUSE's
current binary/source terms before packaging. Installing Conductor does not
install or authorize drivers. FSKit avoids a third-party kernel extension but
still requires an app extension and its deployment contract; Apple's macOS 15.4
release notes announce its availability. Windows ProjFS is
a projected namespace candidate, not a general raw filesystem mount equivalent.

Do not use a 75–80% reuse target or a 150-line bridge as an acceptance criterion.
Measure maintained format-specific code, adapter complexity, independent evidence,
resource behavior and upgrade cost. Correctness takes precedence over line counts.

## Revision 0.3 selection discipline

The [delivery plan](delivery-plan.md) bounds comparisons to at most two executable
candidates per subsystem at a time, after source screening. Retain the small I/O
seed until a replacement wins on concrete semantics and maintenance. Caching,
framework migration and broad transform adoption do not gate the first APFS proof.
The proposed `dioryx-*` names are mapped in [identity](../docs/identity.md); no current
package or lockfile is renamed by this document.

Cargo features are additive code-selection mechanisms, not permission controls.
Test read-only behavior with writers enabled in the resolved feature graph. A redb
comparison must use its qualified backend extension point or equivalent instrumentation
so fault tests reach its own storage I/O, not just our outer block interface.
The ext4-view reader remains a narrow candidate, not a reason to expand write scope.
Relevant current upstream pages are in [dependency evidence](../docs/dependency-evidence.md).
