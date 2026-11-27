#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
cargo fmt --all -- --check
cargo check --workspace --locked
cargo test --workspace --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
# Regenerate from the already fetched, pinned graph; never update registry versions.
lock_before=$(git hash-object Cargo.lock)
cargo generate-lockfile --offline --locked
test "$lock_before" = "$(git hash-object Cargo.lock)"
python3 -m unittest discover -s scripts/tests -v
python3 -m unittest discover -s tests/conformance -v
cargo metadata --locked --no-deps --format-version 1 | python3 scripts/check_contracts.py --cargo-metadata -
