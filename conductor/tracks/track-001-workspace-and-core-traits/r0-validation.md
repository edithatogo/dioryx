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
3. Scoped checkpoint matching: a subsequent change must reject historical,
   mismatched source/contract, target, mode and other required dimensions. Structural
   validity alone does not implement this step or admit dependent native work.

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
reports will be separate from the plan, and will need explicit expected scope.

The 23 structural regressions cover the actual 27-phase/eight-profile graph,
unknown and cyclic edges, malformed and duplicate data, dropped gates/dimensions,
plan drift, attempted profile promotion and both CLI and top-level gate wiring.
The first 22 tests failed before implementation; the top-level wiring regression
then failed before the checker was connected. All 23 pass locally, alongside the
10 namespace regressions. Hosted acceptance is still required for this head.
