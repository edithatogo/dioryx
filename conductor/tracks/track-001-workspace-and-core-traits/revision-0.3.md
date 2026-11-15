# Planning revision 0.3 — Dioryx

Date: 15 November 2026. Input: supplied Universal FS 0.2 archive; not a remote HEAD.
This revision proposes the working name Dioryx, records a bounded collision check,
and refines existing six-track execution into independently useful read, mount,
overlay and direct-write milestones. It does not rename Cargo packages or admit
new dependencies. Namespace migration is an explicit r0 implementation task.

## Scope preserved

All production/test Rust files, Cargo manifests, lockfile, toolchain, CI, scripts,
agent settings and the pinned Conductor content are unchanged. The original Git
history is retained; changes remain uncommitted. Historical 19-test evidence belongs
to the original bootstrap commit and has not been reused as a current pass.

## Verification boundary

Static artifact verification covers compiled-declaration equality, local links,
JSON/TOML parsing, phase and profile references/acyclicity, unchanged protected
files, patch application and packaged bytes. Those checks cannot establish Cargo,
native images, mount runtimes, durability, fuzzing or performance acceptance.

The current runtime has no cargo, rustc or rustup. G's Rust commands are blocked;
no task or profile has been promoted to complete. The supplied artifact-level
verification.json records actual commands/results and the file manifest. On a
Rust-enabled host, run unchanged G before accepting this documentation revision,
then execute r0's implementation tasks individually. No remote action, package or
domain reservation, publication, driver installation or disk write was performed.
