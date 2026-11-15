# Synthetic rejection corpus

`payload.txt` is an ordinary text file, not an APFS, exFAT or other disk image.
Its pinned SHA-256 is recorded in `cases.json`. The conformance tests copy these
bytes into disposable temporary files; mutation tests change only those copies.

`cases.json` contains test-only feature and ancestry values. Its `purpose` field
labels the data as synthetic. It is not a fixture manifest, a native provenance
record, a shared qualification schema or an acceptance artifact. The invented
macOS/tool fields in `test_evidence.py` are structural test inputs only; no native
generator ran and no OS-generated master was fabricated.

The tests cover missing fixture, bad hash, absent native provenance, wrong feature
manifest and shared parser/oracle ancestry. Positive controls demonstrate local
preflight behavior only. See [the conformance scope and handoff](../../conformance/README.md)
for the accepted-contract and native-artifact blockers that remain.
