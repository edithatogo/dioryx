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
