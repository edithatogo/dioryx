# Real-image fixture contract

No filesystem images or filesystem qualification results ship with the initial
core bootstrap. Tests of regular-file storage and bounded transforms establish
their own contracts; they are not substitutes for backend fixture tests.
Before a backend's first accepted feature, add genuine images produced by the
native OS or its maintained formatter and verify them independently. Synthetic
and deliberately corrupted inputs supplement those images.

The [synthetic rejection corpus](negative/) and
[conformance preflight checks](../conformance/README.md) exercise fixture admission
rejections for track006/p1. They do not supply a native master or complete native
admission; the accepted track001/r0 checkpoint and genuine native artifacts remain
required.

## Inventory and evidence

Keep reproducible recipes, small payload sources and manifests in this directory.
Keep image binaries, temporary mounts, extracted payloads and tool output under
ignored `tests/fixtures/generated/` or a checksum-addressed fixture store.
Never commit personal disks or images containing proprietary installed software.

Each admitted fixture manifest records its stable ID, formatter and OS versions,
creation commands, container and filesystem variants, sector/cluster sizes,
SHA-256 of the final image, expected file bytes/hashes, raw names, timestamps,
links/xattrs, native checker result and provenance/redistribution rights. Record
expected negative results for unsupported features. Hash only after clean
unmount and final conversion. Snapshot expectations are versioned separately
from the live tree. Decompression and temporary-file budgets are part of tests.

Tests must fail with an actionable missing-fixture error when a required fixture
is absent or its checksum differs. They must not return early, become ignored,
or treat a missing external checker as a pass. Backend CI downloads pinned
fixtures before `cargo test --workspace --locked`; creating images is a separate
job. A platform job without its required runtime is incomplete qualification.

## macOS: basic native APFS image

Run this on a Mac with `hdiutil`, `diskutil` and `shasum`. It creates only a new
temporary fixture and attaches that file. It does not select a physical disk.
The recipe is provided for execution on macOS; it was not run in this bootstrap.

```bash
set -euo pipefail
fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/universal-fs-apfs.XXXXXX")
mkdir "$fixture_dir/mount"
attached=0
trap 'if [ "$attached" = 1 ]; then hdiutil detach "$fixture_dir/mount"; fi' EXIT
sw_vers > "$fixture_dir/macos-version.txt"
hdiutil create -size 256m -fs APFS -volname UFSTEST \
  -type SPARSE -layout GPTSPUD "$fixture_dir/apfs-basic.sparseimage"
hdiutil attach -nobrowse -mountpoint "$fixture_dir/mount" \
  "$fixture_dir/apfs-basic.sparseimage"
attached=1
mkdir "$fixture_dir/mount/example"
printf 'native APFS fixture\n' > "$fixture_dir/mount/example/hello.txt"
printf 'Unicode fixture\n' > "$fixture_dir/mount/example/café.txt"
ln -s hello.txt "$fixture_dir/mount/example/link"
shasum -a 256 "$fixture_dir/mount/example/hello.txt" \
  "$fixture_dir/mount/example/café.txt" > "$fixture_dir/payload-sha256.txt"
diskutil verifyVolume "$fixture_dir/mount" > "$fixture_dir/verify-volume.txt"
hdiutil detach "$fixture_dir/mount"
attached=0
hdiutil convert "$fixture_dir/apfs-basic.sparseimage" -format UDZO \
  -o "$fixture_dir/apfs-basic.dmg"
hdiutil verify "$fixture_dir/apfs-basic.dmg" > "$fixture_dir/verify-dmg.txt"
shasum -a 256 "$fixture_dir/apfs-basic.sparseimage" \
  "$fixture_dir/apfs-basic.dmg" > "$fixture_dir/image-sha256.txt"
printf '%s\n' "$fixture_dir"
```

This basic recipe does not prove snapshot, compression, clone or sparseimage
reader support. The native sparseimage is a source artifact; our initial UDIF
adapter qualifies the converted DMG separately. A raw GPT derivative must be
captured from this identified virtual disk by an OS-specific fixture harness,
with independent partition offsets and hashes. Do not rename a sparseimage or
DMG and call it raw.

Track 002 extends the native recipe with snapshots, before/after contents,
multiple volumes, case-sensitive variants, clones, large and sparse files,
resource forks and verified decmpfs encodings. A compression copy command alone
does not prove compression. Inspect the native compressed flag and capture
hidden compression metadata using `getxattr` with `XATTR_SHOWCOMPRESSION`;
ordinary `xattr -l` can hide it. Reject or explicitly report unsupported
encodings and dataless files. Unsupported snapshot browsing must never silently
return the current live tree.

## Linux: independently formatted exFAT

The following safe baseline formats only a newly created regular file. Install
`exfatprogs` first. This empty native image is necessary but insufficient for
file-read or mutation acceptance.

```bash
set -euo pipefail
fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/universal-fs-exfat.XXXXXX")
truncate -s 128M "$fixture_dir/exfat-basic.img"
mkfs.exfat -L UFSTEST "$fixture_dir/exfat-basic.img"
fsck.exfat -n "$fixture_dir/exfat-basic.img" > "$fixture_dir/fsck-before.txt" 2>&1
sha256sum "$fixture_dir/exfat-basic.img" > "$fixture_dir/image-sha256.txt"
printf '%s\n' "$fixture_dir"
```

Populate additional fixture copies through a native exFAT mount in a disposable
test VM, recording the exact attached-file identity before any mount. Include
empty, fragmented, contiguous, Unicode, large-directory and near-full cases.
Track 003 operates on copies and checks expected contents plus `fsck.exfat -n`
after orderly unmount. Check before repairing; a repair must not hide a defect.
Crash tests cut power-equivalent writes at every ordered step and preserve the
failed copy and seed. A clean fsck is not proof that acknowledged data survived.

## Windows and release qualification

Create/attach a disposable VHD or VHDX in a dedicated VM and format its identified
test volume with Windows exFAT. Use `chkdsk` on that volume's drive letter or
mount point, not an arbitrary `.img` filename; `/scan` is NTFS-only. Record the
volume identity, Windows build, checker output and content hashes. This fixture
harness does not advertise VHDX support in our engine.

Compare native reads with mountless extraction first, then with the selected
WinFsp, Linux FUSE and macOS frontend. Release evidence must include all claimed
OS/format combinations. Keep permissions, raw names and normalization collisions
in the oracle; compare bytes rather than display strings alone.

Primary references: [Apple APFS tools](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/ToolsandAPIs/ToolsandAPIs.html),
[cmpfs fixture guidance](https://docs.rs/crate/cmpfs/latest),
[exfatprogs](https://github.com/exfatprogs/exfatprogs),
[Microsoft chkdsk](https://learn.microsoft.com/windows-server/administration/windows-commands/chkdsk).

## Revision 0.2: consistency, oracle independence and recovery

Capture a coherent source before hashing its final bytes. A hash does not freeze
a changing image. Keep immutable master fixtures and generate expendable copies
for native mounting, journal replay, repair and every writer/fault run. Hash
before and after probe/open/failed-open/list/read, not only after extraction.

Record upstream parser/formatter provenance: forks and packages sharing code are
not independent oracles. A ferrosys or other Rust-generated image can extend a
corpus but cannot satisfy native provenance by itself. Dirty/journal-required
images must reject read-only opening unless a recovered view is qualified; never
allow a native checker/mounter to repair the original corpus unnoticed.

Include host backing-path escapes, backing cycles, source/destination aliases,
external mutation, wrong overlay base, truncated overlay commits and exhausted
budgets. Fault schedules and acknowledged-operation manifests must be deterministic
and reusable across candidate writers. Protect the host by using disposable VMs
for malformed-image native-driver qualification.
