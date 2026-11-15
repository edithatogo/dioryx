# Fixture preflight checks — track006/p1

[~] Independent synthetic rejection checks are implemented. Review and exact-head
gate evidence belong in the focused PR receipt; this does not complete p1.
[!] Native fixture admission and dependent phase completion remain blocked on an
accepted matching track001/r0 checkpoint, its shared evidence interface and
authentic native artifacts. The sole core/integration owner remains
`6af91d18-4240-83ec-b004-f06031d5fecd`.

This implements the independent negative cases in
[track006/p1](../../conductor/tracks/track-006-conformance-and-release/plan.md).
The requirements are pinned to repository base
`f4bb9d38b371375e31e418838b958a4bad4b14a8`: [M16/M18/M25](../../REQUIREMENTS.md),
[fixture provenance](../fixtures/README.md),
[workflow](../../conductor/workflow.md) and
[delivery ownership](../../conductor/delivery-plan.md).
The fixture contract at that base has Git blob
`5470db2effc925978a6103ecd7aa8a804f79b6ef`; verify the base blob when reconciling
this lane with a later shared contract.

## Execution and scope

Run from the repository root:

```bash
python3 -m unittest discover -s tests/conformance
```

The test vectors and payload in [the negative corpus](../fixtures/negative/) are
synthetic. They are not native filesystem images or accepted provenance records.

The Python standard library is the only dependency. Tests create disposable
ordinary files and exercise the validator directly. They do not run the native
recipes, mount images, access raw devices, install drivers or execute recorded
commands. The native generator OS is a recorded input, separate from the consumer
host; Linux cannot become an APFS generator by consuming macOS metadata.

| Check | Enforced rejection | Limit of the check |
| --- | --- | --- |
| `check_fixture_file` | Missing fixture, malformed/mismatched SHA-256, nonregular file, exceeded byte limit, observed source change or I/O failure | Integrity of an explicitly authorised stable file only; no filesystem-format proof or coherent-capture guarantee |
| `check_native_provenance` | Absent/incomplete generator record, synthetic origin, generator incompatible with the pinned basic APFS/exFAT recipes | Field presence and recipe identity only; strings do not authenticate a native artifact, checker result or redistribution right |
| `check_feature_manifest` | Missing, extra or different feature/container/geometry/view data; type differences; invalid or over-budget structures | Exact comparison with a separately pinned decoded object; no manifest parser or shared schema is defined |
| `check_oracle_ancestry` | Missing declarations or any shared declared parser ancestry, including forks and direct reuse | Requires source-reviewed canonical identities and complete relevant ancestry; disjoint declarations alone do not prove independence |

Checks raise `FixtureRejected` with a reason and next-step message. A successful
preflight returns `None`, never a phase, profile, qualification or admission
record. `NativeProvenance` only groups function arguments in memory; it is not a
versioned serialization format. No real native manifest ships with this change.

The caller must pin expected digests and feature data separately from a proposed
fixture, provide authorised paths in a stable directory and review the full
relevant parser/formatter ancestry, including the implementation itself. Do not
derive the expected oracle from the candidate or infer file authority from image
metadata. The hash checker rejects final-component links and checks opened-file
identity; it is not a hostile-path sandbox or a way to freeze a changing master.

## Coordinator handoff and remaining prerequisites

The preflight module deliberately has no phase/profile evaluator, accepted boolean,
shared result envelope or importer. Those remain with the coordinator. Before
native admission, the coordinator needs to supply:

1. The accepted track001/r0 interface checkpoint and its exact source/contract
   revision, plus the schema/API for binding source tree, dependency lock/features,
   target/runtime, fixture/oracle identity, operation/view and applicable fault model.
2. The approved mapping of fixture/provenance data into that shared schema,
   including canonical ancestry identities and review of their completeness.
   The negative test vector format is not an input to phase/profile acceptance.
3. Authentic, authorised native masters and generation logs: OS/tool versions,
   executed commands, final image hashes after clean unmount/conversion, exact
   container/filesystem features, native checker output, expected file/raw-name/
   metadata oracles and rights. Preserve masters and use fresh copies for native
   mounting or checking. The existing macOS and exFAT recipes remain unexecuted here.
4. Integration of the conformance command into the coordinator-owned checks/CI at
   the matching checkpoint. The baseline core workflow runs G but does not discover
   `tests/conformance`; no hosted conformance coverage is implied by its green jobs.

The authoring Linux runtime has Python 3.12.14 but no Cargo, rustc, rustup,
`hdiutil`, `diskutil`, `mkfs.exfat` or `fsck.exfat`. There are no native masters in
the pinned repository. Missing generators/artifacts are blockers, not skips or
passes. Local `bash scripts/check.sh` stops at missing Cargo; fresh hosted G on
the PR head is required separately from the Python rejection results.

No shared schema, registry, CI, root manifest/lockfile, core source or existing
recipe is modified by this lane. The coordinator retains integration; this lane
does not merge its PR or mark track006/p1 complete.
