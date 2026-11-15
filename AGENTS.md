# Agent protocol

Read `conductor/index.md`, then the selected entry in `conductor/tracks.md`, its
`index.md`, specification and plan before changing code. The project contract is
`REQUIREMENTS.md` and `DESIGN.md`; execution rules are `conductor/workflow.md`.

Use the pinned official Conductor protocol at
`.gemini/extensions/conductor/GEMINI.md` and its
`commands/conductor/{setup,newTrack,implement,review,status,revert}.toml` files.
This project is already set up: do not rerun setup over existing context.
Other coding agents follow the same files; native slash-command support is optional.

Mark tasks `[~]` before work, `[x]` only after gate G and their acceptance evidence.
Use `[!]` with a concrete blocker when a platform, fixture or dependency prevents
verification. Preserve other work and commit only the current logical change.

Never add empty backend crates, fabricated disk images presented as OS fixtures,
successful placeholder methods, `todo!`, `unimplemented!`, or root audit reports.
Never claim a mount or filesystem works from a contract/unit test. Do not import
the rejected `edithatogo/apfs-rs` experiment. Any narrowly reused algorithm needs
an independent specification, license attribution and known-answer tests.

First-party core and backend crates forbid unsafe Rust. Future raw OS shims and
mount FFI are the only possible exceptions and require documented safety proof
and scoped review; wrapper lints do not establish dependency safety.

No publication, remote repository creation, release, driver installation or raw
device mutation is implied by local bootstrap work. Tests write disposable files
or explicitly identified disposable fixture devices only.
