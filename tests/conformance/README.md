# Fixture preflight checks — track006/p1

[~] Synthetic rejection checks were merged in PR #3 and this bounded follow-on
adds a single fail-closed preflight entry point with input-size regressions.
[!] Track001/r0 implementation is now qualified and merged (PRs #4–#6), but
native fixture admission and track006/p1 completion still lack reviewed
fixture-to-checkpoint mapping and authentic native artifacts.
The sole core/integration owner remains `6af91d18-4240-83ec-b004-f06031d5fecd`.

This implements the independent negative cases in
[track006/p1](../../conductor/tracks/track-006-conformance-and-release/plan.md).
The requirements are pinned to repository base
`f4bb9d38b371375e31e418838b958a4bad4b14a8`: [M16/M18/M25](../../REQUIREMENTS.md),
[fixture provenance](../fixtures/README.md),
[workflow](../../conductor/workflow.md) and
[delivery ownership](../../conductor/delivery-plan.md).
The fixture contract at that base has Git blob
`5470db2effc925978a6103ecd7aa8a804f79b6ef`; retain that historic pin.
The accepted r0 schema and its exact limitations are documented in
[r0-validation](../../conductor/tracks/track-001-workspace-and-core-traits/r0-validation.md)
and implemented by `scripts/conductor_evidence.py`. Its
`declared_scope_only` result does **not** authenticate generator provenance or
qualify a filesystem image.

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
| `check_oracle_ancestry` | Missing, duplicated, oversized or shared declared parser ancestry, including forks and direct reuse | Requires source-reviewed canonical identities and complete relevant ancestry; disjoint declarations alone do not prove independence |
| `check_fixture_preflight` | Runs file/hash, provenance, features and ancestry rejections in one required sequence | Still only a preflight: success returns `None`, not an admission, checkpoint, phase or profile record |

Checks raise `FixtureRejected` with a reason and next-step message. The
feature comparison now caps the combined UTF-8 text of decoded keys and values
at 256 KiB, in addition to the existing depth and node limits. Ancestry lists
are limited to 256 entries with 256 UTF-8 bytes per identity and reject
duplicates. These resource bounds are local checks, not a native evidence schema.
A successful preflight returns `None`, never a phase, profile, qualification
or admission record. `NativeProvenance` only groups function arguments in memory; it is not a
versioned serialization format. No real native manifest ships with this change.

The caller must pin expected digests and feature data separately from a proposed
fixture, provide authorised paths in a stable directory and review the full
relevant parser/formatter ancestry, including the implementation itself. Do not
derive the expected oracle from the candidate or infer file authority from image
metadata. The hash checker rejects final-component links and checks opened-file
identity; it is not a hostile-path sandbox or a way to freeze a changing master.

## Coordinator handoff and remaining prerequisites

The preflight module deliberately has no phase/profile evaluator, accepted boolean,
shared result envelope or importer. The qualified r0 matcher supplies versioned
scope fields and checked prerequisite declarations; it does not independently
verify execution, reviewer identity, host or native provenance.

Before native admission, the coordinator must provide:

1. **Reviewed mapping and trusted request:** approve how fixture digests, feature
   manifests, generator/oracle evidence and source/contract revision map into
   the accepted r0 scope. The caller must independently pin expected values and
   checkpoint hashes; the proposed fixture cannot define its own expectations.
2. **Authentic native evidence:** authorised masters with executed generator and
   checker logs, OS/tool versions, final hashes, precise features, expected
   file/raw-name/metadata oracles, redistribution rights and source-reviewed
   complete parser ancestry. Preserve original masters and use copies for checking.
   The macOS and exFAT recipes remain unexecuted in this lane.
3. **CI and independent admission review:** the owner-authorized integration change adds conformance discovery to the
   existing gate. Verify the actual suite on each host and mapped evidence
   against native artifacts at the matching source/host/profile. Green synthetic
   G cannot substitute for native admission.

The original PR #3 authoring runtime lacked Cargo and native generator tools.
For this follow-on, Python 3.13.5 on Linux runs the local conformance suite,
but Cargo and native APFS/exFAT generator tools remain unavailable. No native
masters are present in the repository. These are blockers, not skips or passes.
Fresh hosted G on the exact PR head must be checked separately from the local
Python conformance result.

The fixture implementation does not modify shared schema, root manifests,
lockfile, core source or native recipes. The owner-authorized integration change
adds one existing-gate invocation; the incumbent coordinator retains ongoing
shared ownership. No native admission or phase completion follows.
