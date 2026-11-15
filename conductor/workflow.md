# Development workflow

## Contract and task lifecycle

Read the project index, requirements, design, track specification and plan. Mark
the chosen task `[~]`; write an observable failing test, implement the smallest
working change, then refactor. Interface-only work needs executable invariant
tests, not empty success-returning implementations. A test double may inject
storage faults, but cannot establish filesystem compatibility.

Every task, including documentation and dependency tasks, ends with gate G on
the complete Cargo workspace. Record command, commit/tree, compiler, OS and
result in the existing track's verification section. `[x]` requires all task
acceptance criteria; `[!]` records a concrete missing capability, fixture or
runtime. A deferred or unavailable test is never a pass.

## Gate G

```bash
cargo fmt --all -- --check
cargo check --workspace --locked
cargo test --workspace --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
python3 scripts/check_contracts.py
```

Run doc tests through `cargo test`. Code snippets in DESIGN.md are synchronized
with compiled declarations by `scripts/check_contracts.py`. Never bypass
`--locked`; dependency changes update Cargo.lock deliberately and rerun G.
When a platform-specific frontend exists, also build and test its supported
feature selection on that host. Default workspace tests must remain useful,
but do not substitute for required backend/driver lanes.

## Real images and oracles

Before a filesystem backend's first completed task, import a genuine OS-generated
fixture with provenance, image SHA-256, generator/tool version, feature manifest,
expected tree and per-file hashes. See `tests/fixtures/README.md`. Required backend
tests fail when their fixture is absent; local skips never satisfy acceptance.
Use small licensed, nonpersonal corpora. Large images and test artifacts stay in
an artifact store or ignored local fixture directory, not the repository root.

APFS qualification uses hdiutil-created sparseimages, separately captured raw/GPT
and UDIF derivatives, snapshot-bearing images and proven compressed files.
Unsupported snapshot browsing or codecs return typed errors and remain separate
roadmap gaps. Hand-built byte fixtures supplement genuine images for malformed
input coverage; they cannot replace them.

For exFAT, start with disposable images created by mkfs.exfat or native Windows
formatting. Compare reads against a native mount. After clean writes and remount,
run `fsck.exfat -n IMAGE` and Windows `chkdsk` against the attached fixture volume,
without repair first. Preserve failing images before any repair. chkdsk does not
accept arbitrary raw image paths; `/scan` is not an exFAT option.

## Durability and failure testing

Inject failures before/after each write and barrier; include short I/O, torn
sectors, reordered persistence where permitted by the declared storage model,
device removal, full media, corrupt checksums and process termination. Reopen
from persisted bytes, not surviving in-memory state. Confirm dirty-state
detection, errors, bounded recovery and absence of cross-linked allocation.

Unjournaled exFAT cannot promise all-or-nothing multi-sector crash recovery.
Distinguish clean-shutdown validity, recoverable dirty state, data durability,
runtime rename semantics and power-failure atomicity. Do not clear dirty state
or issue a durable receipt until all required barriers succeed. Failure after
submission fences writes, invalidates cached generations and requires reopen or
recovery. Do not replay uncertain transactions blindly.

## Security and fuzzing

Add cargo-fuzz support with the first binary parser/probe in track 001, and a
target for each later parser before admitting its backend. Include truncated,
overflowing, cyclic and decompression-bomb cases. Bound bytes, steps, depth,
nodes, output and time; test cancellation. Run short corpus regression in normal
CI and longer sanitizer-enabled jobs on supported toolchains. Pin the nightly
toolchain when fuzzing is introduced; a tool absent locally is a blocked gate.

Review direct and transitive dependencies for licenses, RustSec advisories,
unsafe code, panic paths and maintenance before admission. cargo-deny/audit and
geiger are evidence tools, not proofs. Do not relax first-party unsafe bans to
make upstream integration compile. Put any approved platform exception in the
scoped platform module with explicit safety invariants and tests.

## Review, commits and repository hygiene

At each phase checkpoint, review against its spec and REQUIREMENTS.md, inspect
the diff, run G plus required image/platform lanes, and record the actual result.
Use a small conventional commit; no shared-history rewriting. A final review
updates plan, metadata and registry together. Archive only completed reviewed
tracks; preserve their evidence and links. Register a follow-on track for
deferred capability work rather than declaring it complete.

Root files are limited to entrypoint documentation, manifests/toolchain, agent
instructions and normal project configuration. Put decisions in DESIGN.md or
the owning track, dependency evidence in `docs/`, temporary logs in ignored
`artifacts/`, and fixtures under `tests/fixtures/`. Do not generate repeated
JSON/Markdown audits, empty future crates, status badges without evidence, or
competing copies of the specification. Keep upstream submodule modifications
out of project commits; change its pinned commit deliberately.

## Reuse-first dependency admission

Before adding a parser, writer, cache or persistence engine, compare existing
components against the same required operations and genuine-image corpus. Record
one concise decision in the owning track: exact source/version and package/library
names, feature set, license/provenance, unsafe/FFI, public API fit, buffering,
resource limits, maintenance, known gaps, native tests and fault results. Prefer a
small adapter or bounded upstream contribution; new format logic requires a
specific demonstrated gap. Do not enable experimental dependencies in the main
workspace merely to make an evaluation table look complete.

Separate advertised, source-reviewed, compiled, native-qualified and fault-qualified
evidence. Keep source/checksum and host/runtime identities. A fork or shared parser
is not an independent oracle. Native checker cleanliness does not establish data
retention; compare acknowledged operation traces and original byte/metadata oracles.
Native recovery/mount tools operate only on disposable copies.

## Cross-cutting safety gates

Before coherent read/export, establish the source-view consistency contract.
Before container backing/member access, verify the explicit resolver authority.
Before overlay writes, verify base immutability, separate-store recovery and quotas.
Before direct raw writes, require the applicable 005 overlay/fault gates and 006
native broker/exclusivity gates. Do not block ordinary clean-image mountless reads
on those unrelated write gates.

Each parser consumer joins the shared corpus and resource/fuzz harness immediately;
track 006 is not a reason to defer first-day tests. Test explicit supported feature
profiles, with default mountless operation, rather than blindly requiring all
features on all hosts. Run the unchanged G on every final task tree, even for docs.
No toolchain means blocked, not a waived gate. Preserve prior evidence as historical
and never relabel it as a fresh run. No new task is checked complete in this revision.

## Revision 0.3 execution controls

Use the [delivery plan](delivery-plan.md) and phase metadata; do not wait for an
entire referenced track when its required phase is qualified. Shared manifests,
contracts, CI and registry have one integrator. Default WIP is one shared-core
change plus one nonoverlapping backend/fixture change; verify actual ownership.

A dependency comparison has predefined hard gates and no more than two executable
candidates at once. Write its accept/reject/blocked result in the owning track.
Do not add separate status reports that duplicate existing evidence. Missing native
fixtures/runtimes block only the affected profile, but never satisfy its test.

Every new parsing boundary needs malformed-input regression/fuzz entry at admission.
Maintain separate filesystem-ordering and overlay-store-I/O fault suites. A worker
kill is not proof of all power-loss outcomes. Preserve failing images and explicitly
record fault-model exclusions. No publication or driver/device action follows from
writing or accepting this plan.
