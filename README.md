# Dioryx

A composable Rust framework for cross-platform filesystem access. **Dioryx** is
the project name; the six existing Cargo packages now use the
[`dioryx-*` namespace](docs/identity.md). This repository starts with executable core contracts, a read-only
regular-file device, bounded raw/volume views, identity transforms and filename
semantics. It does not yet parse or mount APFS, exFAT or any other filesystem.

Read [requirements](REQUIREMENTS.md), [design](DESIGN.md), and the
[Conductor index](conductor/index.md). The [track registry](conductor/tracks.md)
contains the implementation sequence and all remaining acceptance work.

## Build

Clone the repository with its pinned Conductor submodule, then install the pinned
Rust toolchain and run the gates:

```bash
git clone --recurse-submodules https://github.com/edithatogo/dioryx.git
cd dioryx
rustup toolchain install 1.100.0 --profile minimal --component rustfmt,clippy
git submodule update --init --recursive
cargo check --workspace --locked
cargo test --workspace --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
python3 -m unittest discover -s scripts/tests -v
cargo metadata --locked --no-deps --format-version 1 | python3 scripts/check_contracts.py --cargo-metadata -
```

The bootstrap requires no FUSE, macFUSE, WinFsp, elevated access or external disk
image. That is sufficient for core contract tests only. Each future backend must
pass mandatory genuine-image tests; a missing image is a failure, not a skipped
acceptance result. See [fixture policy](tests/fixtures/README.md).

## Conductor

The official submodule is pinned to release `conductor-v0.4.1`, commit
`7a5c560a4fdf5297be58594cc37527eb12790272`. When Gemini CLI is installed, register
the local checkout:

```bash
gemini extensions link ./.gemini/extensions/conductor
gemini extensions list
```

Restart Gemini CLI, then use `/conductor:status` or `/conductor:implement` with
the selected track. Root `AGENTS.md` and `.claude/CLAUDE.md` expose the same
protocol to other agents. A Git submodule alone does not register the extension.

## Scope and distribution

All Cargo packages are `publish = false`. No upstream code from the rejected APFS
experiment is included. Third-party licenses remain theirs; repository licensing
and redistributable driver packaging must be settled before publication. No
license selection or distribution permission is inferred from dependency licenses.

## Planning revision 0.3

Read the [refined delivery plan](conductor/delivery-plan.md) for R0–R5, ownership,
bounded dependency decisions and per-profile acceptance. The existing six tracks
are retained. APFS upstream proof and native fixture admission now precede rich
mount/write infrastructure. exFAT validates reuse of the read API before stability.

The initial repository import preserves the v0.3 workspace, including all six
Conductor tracks and the original Rust source, manifests, lockfile, toolchain and
pinned Conductor checkout. The package namespace migration, phase/profile structure validation and scoped
checkpoint matcher are implemented. Filesystem features remain planned; no future backend or frontend crate is fabricated.

See the [repository import record](conductor/tracks/track-001-workspace-and-core-traits/repository-import.md)
for provenance and verification boundaries, and the GitHub Actions results on the
exact commit for current build status. Historical [revision evidence](conductor/tracks/track-001-workspace-and-core-traits/revision-0.3.md)
is retained, not substituted for a fresh gate. The three-host core workflow does
not establish native filesystem, raw-device, mount or write compatibility.

## Track 001/r0 integration

This existing Dioryx chat is the sole integration owner. See the current
[track plan](conductor/tracks/track-001-workspace-and-core-traits/plan.md) for
scoped ownership and exact-head review/CI receipts. The namespace change retains
the existing directories and all public behavior; it does not create an umbrella
package, CLI or backend. `cargo test -p dioryx-storage --locked` selects the storage
package; the public library import is `dioryx_storage`. All packages remain private
to this workspace (`publish = false`).

`bash scripts/check.sh` runs the full gate, including Python regressions, a locked
offline lockfile regeneration after the build, and validation of actual Cargo
metadata. No native-fixture, mount, sandbox or write qualification follows from
these namespace/contract checks.

## Planning validation versus runtime qualification

The [r0 validator record](conductor/tracks/track-001-workspace-and-core-traits/r0-validation.md)
describes the structural check now included in the existing gate. It rejects
unknown/cyclic phase references, duplicate or malformed metadata, profile gates
that do not resolve, missing evidence dimensions and plan/metadata drift.
`python3 scripts/conductor_graph.py` runs it separately. A successful check does
not accept a source checkpoint, native fixture, mount or writer; profile status
remains `not_qualified`.

The separate `scripts/conductor_evidence.py` command compares a caller-reviewed
request against pinned checkpoint metadata, including source/contract, dependency,
target/runtime, fixture/oracle, operation/view and fault scope. It checks every
prerequisite and rejects stale or mismatched declarations. The catalog pin
covers normative phase completion policies and profile scope/evidence requirements
as well as topology; changing status labels alone cannot create acceptance.
Its result is
`declared_scope_only`, not evidence authentication, fixture admission or runtime
qualification. See the validator record for the exact schema and trust boundary.
No native checkpoint or accepted profile is generated by the synthetic tests.
