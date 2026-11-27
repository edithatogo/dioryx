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
