# Dioryx

A composable Rust framework for cross-platform filesystem access. **Dioryx** is
the project name; the [namespace plan](docs/identity.md) has not yet renamed
Cargo packages. This repository starts with executable core contracts, a read-only
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
python3 scripts/check_contracts.py
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
pinned Conductor checkout. The Dioryx package rename and subsequent features remain
explicit implementation tasks; no future backend or frontend crate is fabricated.

See the [repository import record](conductor/tracks/track-001-workspace-and-core-traits/repository-import.md)
for provenance and verification boundaries, and the GitHub Actions results on the
exact commit for current build status. Historical [revision evidence](conductor/tracks/track-001-workspace-and-core-traits/revision-0.3.md)
is retained, not substituted for a fresh gate. The three-host core workflow does
not establish native filesystem, raw-device, mount or write compatibility.
