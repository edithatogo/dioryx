# Dioryx repository import — 15 November 2026

## Scope and authority

The user created `https://github.com/edithatogo/dioryx` and explicitly requested all
previously prepared project files here. Repository inspection found no branches,
issues or pull requests. This import installs the existing v0.3 project; it does
not implement all planned tracks or grant authority to publish packages, install
drivers, access physical disks, merge overlays or mutate native filesystems.

## Provenance

- Input: supplied `dioryx-v0.3.tar.gz`.
- Archive SHA-256: `0a765a4960533344b0e9f1db124dd9e406116e9c12ecf881512cd4d4d6afd7e7`.
- Historical seed commit in the supplied archive: `e0bcbfe774803401aba54e7d25d4ee9271a4e387`.
- Conductor gitlink: `7a5c560a4fdf5297be58594cc37527eb12790272` from the official
  `https://github.com/gemini-cli-extensions/conductor.git` repository.
- The archive's Git metadata is not copied into the GitHub tree. The original
  snapshot and historical receipts are retained in the supplied archive; this
  empty remote receives a new GitHub import history.

The import preserves every Rust source/test file, Cargo manifest, lockfile,
compiler pin, check script and CI workflow. Changes from the archive are limited
to current repository/naming instructions in README, identity, the context index
and this record. Future package names are still a tested mechanical migration,
not empty reservation crates. All packages remain `publish = false`.

## Verification at import preparation

- Input archive SHA-256 entries: checked against the supplied SHA256SUMS.
- `python3 scripts/check_contracts.py`: passed (compiled-contract text consistency,
  links, track-level dependencies, core policy and Conductor checkout).
- `git diff --check`: passed.
- `bash scripts/check.sh`: blocked locally with exit 127 (`cargo: command not found`).
- This local runtime has no Rust toolchain and cannot resolve the download host.
  The original 19-test receipt is historical, not new execution evidence.
- Hosted workflow: `.github/workflows/core.yml`, with Linux, macOS and Windows
  running the pinned compiler and all gate-G commands. Consult the exact-commit
  Actions results and import PR for executed outcomes; configured jobs are not passes.

The unchanged contract checker validates track-level edges but does not yet
implement the planned scoped phase/profile evidence validator. That extension,
its regressions and the namespace migration remain in track 001/r0. No gate is
weakened and no pending task is marked complete by transporting its files.

## Next bounded work

Reproduce gate G on the imported head, then execute the separately reviewed
namespace and validator tasks in track 001/r0. Native APFS fixture admission and
the direct upstream-reader proof follow the phase dependencies. No APFS/exFAT,
mount, sandbox, raw-device, overlay, write, fuzz-campaign or benchmark qualification
is implied by this repository bootstrap.
