# Dependency evidence

Checked on 15 November 2026 against primary upstream documentation and published
source. This is a selection record, not a security audit or compatibility test.
None of the candidates below is admitted merely because it appears in a table.
The seed's actual dependency graph is defined by Cargo manifests and lockfile.

| Candidate | Verified observation | Decision / acceptance gap |
| --- | --- | --- |
| [`apfs` 0.4.1](https://docs.rs/crate/apfs/latest) | MIT; read-only `Read + Seek`; decmpfs, xattrs and checkpoints documented | First nonempty volume only; no snapshot browsing, clones, encryption or compressed extents. Qualify a bounded live-tree subset first; retain broader requirements as open. |
| [`udif` 0.4.2](https://docs.rs/crate/udif/latest) | DMG container parsing; raw/zlib/bzip2/LZFSE/XZ codecs documented | No assumption of encrypted DMG, sparseimage, sparsebundle or ASIF support. |
| [`DmgReader<R>`](https://docs.rs/udif/latest/udif/reader/struct.DmgReader.html) | Generic `Read + Seek`; `decompress_partition_to` streams to a writer | Initial integration uses bounded temporary storage for random access; no documented logical `ReadAt` API was found. |
| [`cmpfs` 0.1.0](https://docs.rs/crate/cmpfs/latest) | MIT; shared Apple decmpfs decoder; used by `apfs` and `hfsplus` | Unsupported LZBITMAP and dataless states need typed errors. Compression xattrs require special extraction treatment and real native fixtures. |
| [`embedded-exfat` 0.4.0](https://docs.rs/crate/embedded-exfat/0.4.0) | MIT; crate import `exfat`; synchronous default, optional async/Tokio; checksums/upcase logic | Read-only admission first; upstream mutation availability is not our durability qualification. |
| [`embedded-exfat` published source](https://docs.rs/embedded-exfat/latest/src/exfat/lib.rs.html) | Boot-sector/checksum handling contains `unsafe` transmutation; tests exercise create/delete | Contradicts a whole-stack zero-unsafe claim. Resolve before admission; wrapper `forbid` does not inspect dependencies. |
| [`exfat::io::IO`](https://docs.rs/embedded-exfat/latest/exfat/io/trait.IO.html) | GAT block type, sector reads/writes, sector-size negotiation, flush; not dyn-compatible | Concrete adapter over our storage trait; enforce bounds and deny writes during the read-only phase. |
| [`newtua-apfs` 0.2.0-newtua.2](https://docs.rs/crate/newtua-apfs/latest) | Apache-2.0; import `apfs_core`; removes forensicnomicon; no independent maintenance promise | Reference/fallback evaluation only. Fork also removed inherited lint settings; no inherited panic-free guarantee. |
| [`gpt` 4.1.0](https://docs.rs/crate/gpt/latest) | MIT; generic device requires `Read + Write + Seek + Debug` | Denied-write adapter, read-only opening, checked offsets and both GPT copies. |
| [`bootsector` 0.2.0](https://docs.rs/crate/bootsector/latest) | Published July 2022; basic MBR/GPT | No extended MBR traversal, backup-GPT validation, or strong non-512-sector evidence. Limit initial scope. |
| [`ntfs` 0.4.0](https://docs.rs/crate/ntfs/latest) | MIT OR Apache-2.0; read-only; crate source forbids unsafe | Published June 2023. No write, compression, encryption, journal, reparse-point or security-descriptor support claimed. Recheck maintenance at admission. |
| [`hfsplus` 0.4.0](https://docs.rs/crate/hfsplus/latest) | MIT; HFS+/HFSX reader with `Read + Seek`, extent overflow and decmpfs | Not legacy HFS; hard links and other advanced features need explicit qualification. |
| [`filer-ext4` 0.0.4](https://docs.rs/filer-ext4/latest/filer_ext4/) | Current opened docs contain a real ext2/3/4 reader and in-memory journal handling | Experimental Filer API coupling; evaluate against real images. Older indexed 0.0.1 documentation was reservation-only. |
| [`ext4-fs`](https://docs.rs/ext4-fs/latest/ext4_fs/) | Opened docs show 0.1.2, MIT, basic reader; other indexed manifests mention 0.2.0 | Version conflict remains unresolved; resolve the registry/source before selecting a pin. |
| [`unifuse` 0.3.0 manifest](https://docs.rs/crate/unifuse/0.3.0/source/Cargo.toml) | MIT; Rust 2024; Unix `rfuse3` 0.0.9; Windows `winfsp` 0.12; Tokio | Qualify actual stable builds and runtime prerequisites; README nightly wording alone is not a compiler requirement. |
| [`unifuse` Windows adapter](https://docs.rs/crate/unifuse/0.3.0/source/src/winfsp_adapter.rs) | Static source inspection found discarded flush errors, unconditional read/write opens, lossy name conversion and fabricated capacity after statfs errors | Reproduce and fix or replace the adapter before advertising corresponding semantics. These are source observations, not executed runtime results. |

## Cross-cutting corrections

`moka`'s weighted capacity is best-effort, so admission budgets must independently
bound memory. `crc32fast` is CRC-32, not Castagnoli CRC32C. `zstd` includes native
FFI; evaluate `ruzstd` for a pure-Rust decoder where its supported frame/features
fit. Pure-Rust source, absence of first-party unsafe, absence of transitive
unsafe and absence of parser panics are four separate claims.

Each candidate's next review checks license and selected features in the exact
resolved source, records Cargo's checksum, exercises genuine fixture cases,
and runs bounded fuzzing. Dependency readmes and passing upstream unit tests
cannot establish our advertised cross-platform filesystem support.

Additional primary references: [Moka cache](https://docs.rs/moka/latest/moka/sync/struct.Cache.html),
[crc32fast](https://docs.rs/crc32fast/latest/crc32fast/),
[zstd](https://docs.rs/crate/zstd/latest),
[ruzstd](https://docs.rs/crate/ruzstd/latest),
[Filer status](https://github.com/artob/filer),
[DPP upstream licenses and modules](https://github.com/Dil4rd/dpp),
[WinFsp licensing](https://winfsp.dev/src/),
[Apple macOS 15.4 / FSKit](https://developer.apple.com/documentation/macos-release-notes/macos-15_4-release-notes?language=objc),
[Microsoft ProjFS](https://learn.microsoft.com/en-us/windows/win32/projfs/projected-file-system).

## Revision 0.2 evidence — checked 15 November 2026

These are primary upstream documentation/source observations, not independent
runtime qualification. Versions below are observed pages, not an assertion that
every cached `/latest` page agrees. Resolve the exact manifest, source commit,
features and lockfile again during admission. No new package is in Cargo.lock.

| Candidate | Observed evidence and limits | Decision |
| --- | --- | --- |
| ext4-view 1.0.0 | [Package/README](https://docs.rs/crate/ext4-view/1.0.0) describes read-only ext2/3/4, no unsafe in the main package, and excludes writing/corrupt-filesystem recovery; [Ext4Read](https://docs.rs/ext4-view/1.0.0/ext4_view/trait.Ext4Read.html) is the storage seam | Preferred ext4 read-only evaluation; dependencies and real feature corpus still require admission |
| cap-std 4.0.3 / cap-tempfile 4.0.3 | [cap-std](https://docs.rs/crate/cap-std/4.0.3) provides directory capabilities on target hosts; [cap-tempfile](https://docs.rs/crate/cap-tempfile/4.0.3) supplies capability-oriented temporary files/directories | Evaluate for extraction and UDIF spool; no inference of process sandboxing, no-clobber policy or zero unsafe |
| redb, observed 4.6.0 package | [Package](https://docs.rs/crate/redb/4.6.0) describes a Rust ACID store using CoW B+trees; [durability API](https://docs.rs/redb/latest/redb/enum.Durability.html) exposes commit modes | Candidate overlay block/index persistence; verify selected-version APIs, host crash behavior and write amplification; no raw-device atomicity implication |
| positioned-io 0.3.5 | [API](https://docs.rs/positioned-io/0.3.5/positioned_io/) offers positional I/O and cursor/slice adapters | Compare with std APIs and shared substrate; not a flush protocol or raw-device geometry provider |
| rust-fs-core 0.4.6 | [Package](https://docs.rs/crate/rust-fs-core/0.4.6) documents reusable devices, slices, caches, counters and write/flush API, using library name fs_core | Conditional substrate spike with private Cargo alias; original contract remains authoritative; existing guarantees do not follow from write_at/flush |
| rust-fs-ext4 / rust-fs-ntfs / rust-fs-btrfs | [ext4](https://docs.rs/crate/rust-fs-ext4/latest), [NTFS](https://docs.rs/crate/rust-fs-ntfs/latest), [Btrfs](https://docs.rs/crate/rust-fs-btrfs/latest) advertise broader format engines | Candidate comparisons only; journaling/native-checker claims must be independently reproduced; assess shared code/common-mode risk |
| fs-pc / fs_pc | [Package documentation](https://docs.rs/fs-pc/latest/fs_pc/) advertises broad FAT/exFAT/NTFS tools; package/library spelling must be resolved from the actual manifest | Provenance, exact API, license, safety and native claims not independently qualified here; do not rank as a production-ready winner |
| fstool, observed 0.5.4 | [Package](https://docs.rs/crate/fstool/0.5.4) advertises modular filesystem tooling | Evaluate library-only feature subset, not CLI/UI framework adoption. The 0.5.4 APFS table says compressed files read empty and fsck cleanliness is incomplete: reject those paths unless fixed and independently qualified |
| ferrosys | [Upstream](https://github.com/gregordinary/ferrosys) describes Rust filesystem formatting/reading | Optional comparator/fixture helper after admission; its generated images do not replace native OS provenance |
| rust-img-* / rust-disk-partitions | [VHDX package](https://docs.rs/crate/rust-img-vhdx/latest) and [partition package](https://docs.rs/crate/rust-disk-partitions/latest) are additional reusable-format candidates | Require source-preserving open, recovery policy and explicit backing/member resolution; no format capability admitted |
| slotmap-careful | [API](https://docs.rs/slotmap-careful/latest/slotmap_careful/) targets handle reuse concerns | Optional ephemeral handle helper only; bound retained slots and keep persistent identity separate |
| binrw / Loom | [binrw](https://docs.rs/binrw/latest/binrw/) declarative parsing; [Loom](https://docs.rs/loom/latest/loom/) concurrency modeling | Use only at a real consumer: parser bounds remain ours, and concurrency modeling is not storage crash simulation |

### External consistency and recovery warnings

[QEMU image-tool guidance](https://www.qemu.org/docs/master/tools/qemu-img.html)
warns that querying a changing image may see inconsistent state and distinguishes
backing storage from an explicit commit. Its
[backing-format security guidance](https://www.qemu.org/docs/master/about/removed-features.html)
also warns against blindly probing untrusted backing images. These support the
explicit resolver and immutable-view policies; QEMU is not a new runtime dependency.

[Linux ext4 documentation](https://docs.kernel.org/admin-guide/ext4.html) notes
that journal replay may write even with a read-only mount. Consequently native
oracle mounting/recovery always uses disposable copies. This is not a claim that
all Rust readers replay or that all read-only modes write.

### Evidence discipline

Only the original seed dependencies are admitted. No performance, full-stack
zero-unsafe or independent-correctness conclusion is drawn from these pages.
The owning track must preserve source provenance and exact results, and must
requalify affected behavior on updates. Repository and driver distribution
licensing remain unresolved until explicitly decided; do not infer permission
from an MIT/Apache candidate dependency.

## Planning revision 0.3 — additional primary-source checks

Consulted 15 November 2026; no dependency admitted or changed.

- Cargo features are unified additively; runtime read-only authority must survive a writer-enabled graph: https://doc.rust-lang.org/cargo/reference/features.html
- redb exposes a storage backend extension point that is a candidate fault-injection seam: https://docs.rs/redb/latest/redb/trait.StorageBackend.html and https://docs.rs/redb/latest/redb/struct.Builder.html
- ext4-view describes read-only access and explicitly excludes writes; its main-package unsafe policy is not a transitive claim: https://docs.rs/crate/ext4-view/1.0.0

The exact selected source, enabled features and APIs must be pinned and compiled
when consumed. Newer version numbers, prose claims and existing package names are
not substitutions for native-image, safety or persistence evidence.
