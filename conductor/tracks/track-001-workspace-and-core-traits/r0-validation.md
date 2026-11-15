# R0 validator implementation and boundaries

This record supplements [the track plan](plan.md), not a second task registry.
The existing Dioryx chat is the sole integration owner. Fixture/conformance PR #3
owns its seven `tests/fixtures` and `tests/conformance` paths; they are untouched.
Renovate PR #2 remains separate. No native profile is qualified by this increment.

## Independently reviewed increments

1. Namespace PR #4: six existing package/import names, unchanged behavior,
   namespace regressions and actual Cargo metadata/lock regeneration gates.
2. Phase/profile structure: `scripts/conductor_graph.py`, its regression suite and
   integration into the existing contract checker. No source/crate/CI pin changes.
3. Scoped checkpoint matching: `scripts/conductor_evidence.py` rejects historical,
   mismatched source/contract, target, mode and other required dimensions. Its
   separate exact-head gates remain required; matching is not native admission.

Each head requires G on Linux, macOS and Windows plus exact-head review before
integration. The Python suite runs through `scripts/check.sh`; it is not native
fixture evidence. This runtime cannot execute Cargo locally. CI outcomes and
source SHAs are recorded in each PR rather than guessed here.

## Structural contract

`python3 scripts/conductor_graph.py` checks all current track directories. The
same check runs inside `python3 scripts/check_contracts.py`. JSON must be UTF-8,
no larger than 1 MiB per document, with unique object keys and finite constants.
Malformed shapes return a nonzero exit and diagnostic, never a success fallback.

Phase fields are exactly `id`, `name`, `status`, `depends_on`, `completion_policy`.
IDs use `p` or `r` followed by digits. Dependencies are unique nonempty strings in
`track-id#phase-id` form and must resolve. The phase and track graphs must be
acyclic. Phase status is descriptive; it is deliberately absent from the resolved
catalog used by consumers. Plan headings and `Prerequisites:` lines must agree
with metadata, including duplicate/omitted phases and edges.

Profiles require unique names, nonempty phase gates, a scope and exactly the seven
existing evidence-dimension identifiers. Their planning status stays
`not_qualified`. A stored status edit cannot manufacture acceptance. Checkpoint
reports are separate from the plan and require explicit independently reviewed scope.

The 23 structural regressions cover the actual 27-phase/eight-profile graph,
unknown and cyclic edges, malformed and duplicate data, dropped gates/dimensions,
plan drift, attempted profile promotion and both CLI and top-level gate wiring.
The first 22 tests failed before implementation; the top-level wiring regression
then failed before the checker was connected. All 23 pass locally, alongside the
10 namespace regressions. Hosted acceptance for that structural head is recorded below.

## Scoped checkpoint contract (schema version 1)

The matcher is implemented in `scripts/conductor_evidence.py`. Its 25 regression
cases are synthetic metadata tests, not admitted fixture or execution receipts.
The first 22 failed before implementation; three further boundary tests cover
explicitly different prerequisite roles, full digests and unexpected receipts.

```bash
python3 scripts/conductor_evidence.py --request /path/to/reviewed-request.json --evidence /path/to/checkpoint-bundle.json
```

The caller must obtain the request from an independently reviewed policy/checkpoint
selection. Never construct its expectations or content pins by trusting the bundle
being checked. The matcher does not fetch evidence, authenticate a reviewer, verify
that tests really ran, attest a host, or admit a native fixture. Exit zero means
`declared_scope_only`; the output explicitly says it is not runtime qualification.
No files, statuses, devices or permissions are changed.

A request has exactly `schema_version` (integer 1), `catalog_sha256`, `subject`,
and `requirements`. Subject is `{kind, id}`, with kind `phase` or `profile`.
A phase request checks entry prerequisites, not that phase's completion. A profile
request starts at its required phases. Both expand the full prerequisite closure;
requirements and receipts must cover it exactly, without duplicates or extra rows.
An initial phase with no prerequisites has an empty closure, not automatic acceptance.

Each requirement has exactly `phase`, `scope`, `checkpoint_sha256`. The bundle has
exactly `schema_version` and `checkpoints`. Each checkpoint has exactly `phase`,
`scope`, `result`, `evidence_kind`, `review_status`, `review_reference`, and
`evidence_reference`. Result must be `passed`, kind `executed`, review `accepted`,
and both references nonempty. These are declarations, not verified signatures.
Historical, failed, skipped, unreviewed, missing and substituted records fail.

Each scope has the following exact fields. All eight must match the independently
specified requirement, including explicit reasons where a dimension does not apply.

| Field | Required shape |
| --- | --- |
| `source_tree` | Full lowercase Git tree digest (40 or 64 hexadecimal characters) |
| `contract_revision` | 64-character SHA-256 of the reviewed interface/schema bundle |
| `dependency_lock_and_features` | `{lock_sha256, features, toolchain}`; features are sorted unique strings, possibly empty; toolchain is nonempty |
| `target_and_os` | `{target, os}`; explicit target triple and versioned OS identity |
| `runtime_or_driver_when_applicable` | `{kind: specified, identity}` or `{kind: not_applicable, reason}` |
| `fixture_and_oracle` | `{kind: specified, fixture_sha256, oracle_sha256}` or explicit not-applicable reason |
| `operation_and_view_mode` | `{operation, view_mode}`; neither is inferred from phase status |
| `fault_model_when_applicable` | `{kind: specified, model_sha256}` or explicit not-applicable reason |

All SHA-256 fields require 64 lowercase hexadecimal characters. Values described
as identities or reasons are nonempty strings. Optionality is explicit, not null,
omission or a wildcard. Applicability decisions belong to the trusted request:
this primitive cannot decide that a native-read profile genuinely needs no fixture.
The future qualification assembler must validate those policy decisions and the
underlying evidence before accepting a profile.

`catalog_digest(load_catalog(root))` binds the current graph topology, sorting each
edge list. Descriptive statuses are intentionally excluded. `checkpoint_digest`
pins the complete checkpoint object. Both hash UTF-8 JSON emitted with sorted keys,
compact comma/colon separators, ASCII escapes and disallowed non-finite values.
They are content identifiers, not signatures. Field shapes are validated before
matching. Prerequisite roles may have different reviewed scopes; one host's matched
checkpoint does not require unrelated host lanes or mark them complete.

No trusted request or executed/native checkpoint is manufactured by these tests.
The fixture lane keeps ownership of provenance validation and its synthetic tests;
its eventual mapping into this shared contract needs review and hosted coverage.

## Qualified increment references

Namespace PR #4 head `39c25288193b9b5454fefdeb745b5993f71511cc`, merged as
`1610c1bdd1ada27e2494180fa13bd3088307d252`: push 43708279112 and PR 43708308049
passed all three hosts, 19 Rust and 10 Python tests. Locked offline regeneration
and actual Cargo metadata validation passed; all runtime behavior is unchanged.

Structural PR #5 head `c7ae1dae399305be94c8c5df347308840491212d`, merged as
`bc2cdedd7e6248852f960b2f65270b2d547ba123`: push 43709323287 and PR 43709344426
passed all three hosts, 19 Rust and 33 Python tests. Exact-head automated repository
reviews of both PRs completed without findings. Integration reviews are recorded
on those exact heads. Scoped matching requires its own head's G before acceptance;
none of these results qualifies an APFS/exFAT image, native sandbox, mount or writer.
