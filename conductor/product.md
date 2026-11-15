# Dioryx — product

## Vision and users

Provide one composable userspace Rust engine for inspecting, extracting and,
after qualification, mounting filesystems across Windows, Linux and macOS.
Target users are people moving external media between operating systems, data
recovery and forensic practitioners, developers of backup/import tools, and
administrators needing controlled access to otherwise unreadable images.

Preserve evidence and report unsupported features precisely. Ease of mounting
must not come at the expense of source integrity or truthful file content.
The proposed working product name is Dioryx; this is a greenfield project, with no
dependency on the rejected `edithatogo/apfs-rs` experiment.

## Interoperability goals

The following is our planned delivery matrix, not a claim about implemented
support or every host's native drivers. `R` means read/list/stat/extract plus
read-only mounts after platform qualification. `W` is separately qualified writes.

| Format | Windows target | Linux target | macOS target | Priority |
| --- | --- | --- | --- | --- |
| APFS, raw/GPT and supported DMG | R | R | R | 1 |
| exFAT | R then W | R then W | R then W | 1 |
| NTFS | R, later W | R, later W | R, later W | 2 |
| ext4 | R, later W | R, later W | R, later W | 2 |
| HFS+/HFSX, Btrfs, UDF/ISO9660 | R | R | R | 3 |
| ZFS, XFS, F2FS, multi-device pools | Research | Research | Research | 4 |

Every cell requires format-version, feature and host-runtime evidence. APFS
snapshots, clones, multiple volumes and encryption are separate capabilities.
Current `apfs` candidate limitations are recorded in `tech-stack.md`. Their
absence must remain visible; the supported live-tree subset cannot stand in for
complete APFS support.

## Execution modes

**Mountless:** an unprivileged library and future `fs-cli` inspect ordinary image
files, select containers/partitions/volumes, list metadata and stream extraction.
Raw devices retain host access-control requirements. Extraction creates files
beneath an explicitly selected destination, rejects traversal and collisions,
and never follows source symlinks outside it. Read-only is the default.

**Mounted:** optional `mount-unifuse` and a daemon translate host requests into
`fs-core`. Driver installation, permissions and signing are host-specific. The
daemon uses bounded workers and handles cancellation/unmount without inventing
successful flushes. Mountless builds never require these drivers.

**Future delivery:** FSKit is a userspace app extension, ProjFS projects a tree
into Windows storage, and WASM offers a constrained viewer. Each has distinct
semantics and its own capability filter.

## Roadmap and outcomes

1. Track 001 establishes compiled contracts, file I/O, layer discovery,
   normalization policy, read caching, OS shims and parser resource limits.
2. Track 002 proves an APFS subset against real macOS images before adding
   cross-platform read mounts. Unsupported variants remain explicit blockers.
3. Track 003 qualifies exFAT reads, then safe write mutation, recovery behavior,
   independent filesystem checks and write mounts.
4. Track 004 extends qualified readers and shared transforms. NTFS/ext4 writes,
   whole-disk unlockers and multi-device writable pools require later tracks.

Success means reproducible content and metadata comparisons with host-native
oracles, bounded resource use, and no false success on corruption or durability
failure. Measure maintained format-specific code, adapter complexity, independent
evidence and upgrade cost; no fixed reuse percentage is an acceptance target.

## Revision 0.2: delivery and reuse policy

The project primarily owns interoperability, semantic projection, source authority
and qualification. Existing filesystem engines are evaluated before custom writers.
Initial delivery remains useful mountless APFS; NTFS/ext4 writers are not added to
MVP by their presence on a dependency shortlist.

Modes are read-only coherent view, explicitly labeled best-effort live read,
base-preserving overlay, and independently qualified direct write. Overlay export
creates a new image and never implicitly merges into the original. Recovered views
are distinct from live and snapshot views. A missing pool member, unknown feature
or required recovery is reported rather than concealed.

The added tracks are overlay/recovery (005) and conformance/release (006), with the
latter's corpus infrastructure beginning early. Claims remain per exact host,
filesystem feature, storage mode and dependency revision. See the revised
[requirements](../REQUIREMENTS.md) and [design](../DESIGN.md).

## Revision 0.3: evidence-led vertical delivery

Use the [delivery milestones](delivery-plan.md) rather than requiring whole-track
completion before the next useful behavior. R1 proves native APFS bytes; R2 delivers
mountless APFS and then exFAT through the same contract; R3 mounts and R4 overlay
writes have independent prerequisites. R5 preserves the original full exFAT direct-
write ambition. Names and package migration are in [identity](../docs/identity.md).

No first release promises universal compatibility, forensic completeness, full
metadata preservation, sandboxing of in-process callers or safe direct writes merely
because the framework can compose those interfaces. Profiles disclose limitations.
