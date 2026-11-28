#!/usr/bin/env bash
# Only run in a disposable GitHub-hosted runner; no physical-disk arguments.
set -euo pipefail
kind=$1
profile=${2:-baseline}
case "$profile" in baseline|expanded) ;; *) exit 2 ;; esac
test "${GITHUB_ACTIONS:-}" = true
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
case "$kind:$(uname -s)" in apfs:Darwin|exfat:Linux) ;; *) exit 2 ;; esac
out="$RUNNER_TEMP/dioryx-native-$kind"
mkdir "$out"
work=$(mktemp -d "$RUNNER_TEMP/dioryx-fixture.XXXXXX")
mp="$work/mount"
mkdir "$mp"
attached=0
run() { printf '%q ' "$@" >> "$out/commands.log"; printf '\n' >> "$out/commands.log"; printf '%q ' "$@" >&2; printf '\n' >&2; "$@"; }
detach() {
    if [ "$kind" = apfs ]; then run hdiutil detach "$mp"; else run sudo umount "$mp"; fi
    attached=0
}
trap 'if [ "$attached" = 1 ]; then detach; fi' EXIT
hashfile() { python3 -c 'import hashlib,sys; f=open(sys.argv[1],"rb"); print(hashlib.file_digest(f,"sha256").hexdigest())' "$1"; }
attach_apfs() {
    local label=$1 image=$2; shift 2
    run hdiutil attach -plist -nobrowse -mountpoint "$mp" "$@" "$image" > "$out/$label-attach.plist"
    attached=1
    python3 -c 'import os,plistlib,sys; p=plistlib.load(open(sys.argv[1],"rb")); assert any(os.path.realpath(x.get("mount-point","/"))==os.path.realpath(sys.argv[2]) for x in p["system-entities"])' "$out/$label-attach.plist" "$mp"
    run diskutil info -plist "$mp" > "$out/$label-volume.plist"
}
attach_exfat() {
    local label=$1 image=$2 mode=$3
    run sudo mount -t exfat -o "loop,$mode,nosuid,nodev,noexec,uid=$(id -u),gid=$(id -g)" "$image" "$mp"
    attached=1
    test "$(findmnt --mountpoint "$mp" -n -o FSTYPE)" = exfat
    run findmnt --mountpoint "$mp" -J > "$out/$label-mount.json"
}
observe() { run python3 tests/conformance/native_oracle.py observe "$mp" "$profile" > "$out/$1-oracle.json"; }
populate() { run python3 tests/conformance/native_oracle.py populate "$mp" "$profile"; }
assert_unchanged() {
    local image=$1 before=$2 after
    after=$(hashfile "$image")
    printf '%s %s %s\n' "$(basename "$image")" "$before" "$after" >> "$out/preservation.txt"
    test "$before" = "$after"
}
printf 'schema=dioryx-native-candidate-v1\nrepository=%s\nsource=%s\nrun=%s\nattempt=%s\nkind=%s\nrunner_image=%s\nrunner_image_version=%s\nstatus=candidate-only\nrights=generated from repository-authored synthetic payload; redistribution review pending\n' "$GITHUB_REPOSITORY" "$GITHUB_SHA" "$GITHUB_RUN_ID" "$GITHUB_RUN_ATTEMPT" "$kind" "${ImageOS:-unknown}" "${ImageVersion:-unknown}" > "$out/provenance.txt"
printf 'payload_profile=%s\n' "$profile" >> "$out/provenance.txt"
run uname -a > "$out/host.txt"
if [ "$kind" = apfs ]; then
    run sw_vers > "$out/os-version.txt"
    run shasum -a 256 /usr/bin/hdiutil /usr/sbin/diskutil > "$out/tool-hashes.txt"
    master="$out/apfs.sparseimage"
    run hdiutil create -size 256m -fs APFS -volname DIORYXTEST -type SPARSE -layout GPTSPUD "$master"
    attach_apfs create "$master"
    populate
    detach
    before=$(hashfile "$master")
    run hdiutil convert "$master" -format UDZO -o "$out/apfs.dmg"
    assert_unchanged "$master" "$before"
    images=(apfs.sparseimage apfs.dmg)
    if [ "$profile" = expanded ]; then
        run hdiutil convert "$master" -format UDTO -o "$out/apfs-raw.cdr"
        assert_unchanged "$master" "$before"
        images+=(apfs-raw.cdr)
    fi
    for name in "${images[@]}"; do
        copy="$work/check-$name"
        original=$(hashfile "$out/$name")
        run cp "$out/$name" "$copy"
        if [ "$name" = apfs.dmg ]; then run hdiutil verify "$copy" > "$out/dmg-checker.txt" 2>&1; fi
        if [ "$name" = apfs-raw.cdr ]; then
            run gpt -r show "$copy" > "$out/raw-gpt-native.txt"
            run python3 tests/conformance/native_oracle.py raw-gpt "$copy" "$out/raw-gpt-native.txt" > "$out/raw-gpt-geometry.json"
        fi
        attach_apfs "$name" "$copy" -readonly
        run diskutil verifyVolume "$mp" > "$out/$name-checker.txt" 2>&1
        observe "$name"
        detach
        assert_unchanged "$copy" "$original"
        assert_unchanged "$out/$name" "$original"
    done
else
    run cat /etc/os-release > "$out/os-version.txt"
    run dpkg-query -W exfatprogs > "$out/tool-version.txt"
    run sha256sum "$(command -v mkfs.exfat)" "$(command -v fsck.exfat)" "$(command -v dump.exfat)" > "$out/tool-hashes.txt"
    master="$out/exfat.img"
    run truncate -s 128M "$master"
    run mkfs.exfat -L DIORYXTEST "$master"
    attach_exfat create "$master" rw
    populate
    detach
    before=$(hashfile "$master")
    copy="$work/check-exfat.img"
    run cp "$master" "$copy"
    run fsck.exfat -n "$copy" > "$out/checker.txt" 2>&1
    run dump.exfat "$copy" > "$out/geometry.txt"
    attach_exfat readback "$copy" ro
    observe exfat
    detach
    assert_unchanged "$copy" "$before"
    assert_unchanged "$master" "$before"
fi
python3 - "$out" <<'PY'
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
with (root / 'SHA256SUMS').open('x', encoding='ascii') as manifest:
    for file in sorted(root.iterdir()):
        if file.name == 'SHA256SUMS':
            continue
        with file.open('rb') as stream:
            manifest.write(f'{hashlib.file_digest(stream, "sha256").hexdigest()}  {file.name}\n')
PY
