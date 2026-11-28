# Native candidate acquisition — Track 006/p1

This bounded increment uses GitHub-hosted disposable macOS and Linux runners,
native hdiutil/diskutil and exfatprogs/kernel exFAT. It generates ordinary
synthetic-content images, not data from personal disks, then checks and reads
copies natively against the two fixed known-answer files (including an empty
file). Master and readback-copy hashes must remain unchanged after creation.
The script rejects a non-GitHub-hosted environment; it accepts no device or
image path arguments. Only the controlled runner-created temporary mount is used.

The workflow is manually dispatchable after integration and initially runs on
the named acquisition branch. It does not run elevated fixture creation on
untrusted pull requests. Every candidate artifact contains actual source/run
identity, host/tool versions or binary hashes, commands, checker output, native
mount metadata, scoped OS-visible names and content hashes, preservation checks,
and a SHA256SUMS manifest. The artifact retention is 30 days; review and retain
approved exact bytes in the checksum-addressed corpus before expiry. A workflow
success is candidate acquisition, not Track 006 admission, independent parser
lineage review, a signed receipt, or a filesystem feature qualification.

APFS sparseimage and converted UDZO are distinct container candidates. Neither
is renamed or claimed as a raw GPT image. Raw GPT capture, snapshot and
compression oracles, richer exFAT corpus, redistribution review, independently
pinned expectations, accepted r0 scope mapping and independent receiving review
remain required. OS-visible names are not claimed to be raw on-disk names.
No raw physical-device access, publication or new dependencies in Cargo.

## Candidate acquisition receipt — first run

- Source: `a800a4bab081d894f60c12d0a687c7f72b27375f`.
- [Native workflow 46083992900](https://github.com/edithatogo/dioryx/actions/runs/46083992900).
- macOS 26.7.2 (25G332), runner image macos26 20261123.0526.1:
  APFS sparseimage and UDZO generated; native copies mounted read-only, both
  fsck_apfs exit 0, UDZO checksum verification succeeded, both known-answer
  files and observed metadata matched. Independent ZIP readback in Linux
  verified all 19 manifest entries and archive SHA-256.
- [Candidate artifact 15238416929](https://github.com/edithatogo/dioryx/actions/runs/46083992900/artifacts/15238416929)
  (expiry 2026-12-27T23:43:06Z).
- ZIP SHA-256 `288eb3f8420a01bbe1c0570f407ede150f761151093a1a526694e7bf9263f4ed`;
  sparseimage `cd3b9d47648170d771456ae061ecb4e4ac57ef2cc3f8659fa6ea16b4056d24ae`;
  DMG `ae1ff5226dad4bba212b68e9c61ddb7f46304339ddfb7b73f9ad341a43133927`.
  Before/after hashes matched for both masters and readback copies; no raw
  derivative, parser acceptance, licensing or profile qualification.
- Linux failed before a candidate was retained. Upstream mkfs.exfat version-only
  command can exit failure; the bounded next run obtains exact installed
  package and binary identities instead and prints actual command diagnostics.
  Do not treat an incomplete generation or missing artifact as a pass.

## Candidate acquisition receipt — corrected run

- Source: `a1c1619168d77913c8f24b855d6dff3fb0e44938`; [native workflow 46084151438](https://github.com/edithatogo/dioryx/actions/runs/46084151438), both hosted native lanes passed.
- Linux Ubuntu 26.04.1 LTS, kernel 7.0.0-1020-azure, runner ubuntu26 20261122.9.1, exfatprogs 1.3.2-1. 128 MiB exFAT image, 512-byte sectors, 4096-byte clusters; native fsck.exfat -n reported clean, native kernel readback mounted ro and matched both fixed files. The master and copy before/after digests were identical.
- [exFAT candidate artifact 15238636193](https://github.com/edithatogo/dioryx/actions/runs/46084151438/artifacts/15238636193), expiry 2026-12-27T23:44:36Z; ZIP SHA-256 `8ef779a36bbe57c0042e33ec7d5dddec1f8201b801d0e150c2fd2eee4efcbd8a`; image SHA-256 `05fb6afe56f2f26478a0a97525887fedfc5bf9dd2f6863c71a8a436b0d1c79d7`. Independent download verified all 13 manifest entries and archive digest, geometry, checker, native readback oracle and preservation receipts.
- Corrected macOS run also passed; [artifact 15238371676](https://github.com/edithatogo/dioryx/actions/runs/46084151438/artifacts/15238371676), GitHub-reported ZIP SHA-256 `937a21d55351774551a49824840c2e8784004e3633dfd71046dae774c4faaf34` (not independently downloaded; first-run APFS bytes remain the independently checked candidates).
- Known-answer oracle: empty file SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; 22-byte hello file SHA-256 `c25b540364225542c5597358145ea71cf6427e66f6abc9e382bfc51740de2adc`. Observations are native OS-visible metadata only.
- Disposition: candidate-only. Retention, rights, independent candidate-parser ancestry, trusted pins and exact accepted checkpoint mapping still required; no native profile admission.

## Independent candidate integrity and retention (28 November)

PR #13 merged at `4e7617496b99165769e62a9cae8d7a8954f708fb` with exact receiving-tree G and independent review.
The separately checked [candidate pins](candidate-pins.json) bind original
archive, manifest, image and native oracle digests from runs 46083992900 and
46084151438. They are not derived from an untrusted archive at verification time.

```bash
mkdir -p /path/to/private/fixture-store
python3 tests/conformance/candidate_archive.py apfs /path/to/original-apfs.zip --retain-dir /path/to/private/fixture-store
python3 tests/conformance/candidate_archive.py exfat /path/to/original-exfat.zip --retain-dir /path/to/private/fixture-store
```

Both actual archives verified locally: 19 and 13 manifest entries, respectively,
with all three image/oracle pairs matching. The verifier produces the exact
`fixture_and_oracle` field shape required by the existing r0 matcher, but no
checkpoint, accepted review or runtime qualification. It limits compressed and
expanded sizes and member count, rejects unknown/duplicate/path-like entries,
does not extract paths, and publishes verified archive bytes under their SHA-256
names without overwriting an existing object. The caller owns the input/store
directory; a filesystem without hard links is unsupported. This is not a
hostile-directory sandbox or a power-loss durability guarantee.

Source review confirms generation used only two repository-authored known-answer
payloads on fresh disposable images, no personal disks or installed software.
That supports private candidate retention, not a legal conclusion about
redistribution. The public repository has no selected licence; retain the
original archives privately until the owner records a rights decision. No
binary publication, licence grant or persistent remote storage is claimed.
The exact copies were staged in the execution environment; the GitHub artifacts
expire on 27 December UTC. Transfer the verified digest-named objects into an
authorised durable private store before expiry.

Remaining admission: independent parser ancestry, explicit feature scope
(including absence/unsupported evidence), reviewed rights and retained store,
and integrator-reviewed full r0 checkpoint request. No fixture is marked admitted.

## Expanded native candidate acquisition

Source `756b433d43899b60096174cd2c0f06554a4c0947`, [native run 46090612295](https://github.com/edithatogo/dioryx/actions/runs/46090612295):
both hosted native lanes passed. The native macOS UDTO conversion produced a
268435456-byte raw disk image. Native `gpt -r show` on a disposable regular-file
copy reported primary and backup GPT, one APFS partition at LBA 40 with 524208
512-byte sectors (offset 20480, length 268394496). Both GPT signatures and the
NXSB signature at the native offset were cross-checked; this does not replace
the later full GPT CRC/overlap validator. Native read-only mounted checkers
and preservation hashes passed for raw, sparseimage, DMG and exFAT.
Six known-answer files per filesystem include an empty file, 22-byte text,
Unicode U+4E2D filename and 4095/4096/4097-byte boundaries; observed OS names
and hashes matched. No snapshot, compression, fragmentation or malformed
filesystem consumer qualification is claimed.

- [Expanded APFS artifact 15240991891](https://github.com/edithatogo/dioryx/actions/runs/46090612295/artifacts/15240991891):
  ZIP SHA-256 `af6bd48552328827ad03a0bcca9ba8f966baa88d0bd588721cb0c7db6dd8bc86`,
  26 manifest entries independently verified, raw SHA-256
  `73fcddcba062325184c05c8f5776c6995b959a852137e4049923513c0b3eb044`.
- [Expanded exFAT artifact 15241215522](https://github.com/edithatogo/dioryx/actions/runs/46090612295/artifacts/15241215522):
  ZIP SHA-256 `2348a9cc932604a7ef31d515c23721090f1706d402f73b2a725a5b824f5138f6`,
  13 manifest entries independently verified, raw SHA-256
  `d034e0b716a5b6240cfbf0485dbca64e33b317f68f1ffb5f5e0cef106fb11ce3`.

Added expanded entries to candidate-pins.json, retaining original baselines.
Actual expanded ZIPs were independently verified and stored by digest locally
through candidate_archive.py with `apfs-expanded` and `exfat-expanded`.
GitHub artifact expiry 28 December 00:57 UTC; no public binary upload or
durable remote-store claim. Rights screen: exfatprogs is GPL-2.0 (see
https://github.com/exfatprogs/exfatprogs); GPL program output is not automatically
covered unless it copies protected program content (see
https://www.gnu.org/licenses/gpl-faq.html#WhatCaseIsOutputGPL). Native payloads
are generated from repository-authored data, not installed software.
The applicable Apple software terms are at https://www.apple.com/legal/sla/.
No final redistribution grant or licence has been selected. Preserve private
candidate retention and require explicit owner rights disposition. The full
accepted r0 checkpoint mapping and selected parser ancestry remain outstanding.
