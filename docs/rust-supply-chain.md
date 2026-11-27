# Rust dependency assurance decision (2026-11-22)

Scope: the root Cargo workspace and its committed lockfile. This change adds no
application dependency and does not replace Gate G or owner-controlled Conductor
acceptance. It follows the Ponytail reuse-first ladder: prefer existing Cargo,
RustSec and cargo-deny controls over a new abstraction or quality framework.

- **cargo-deny**: run on dependency-related PRs, main changes and weekly. Deny
  unapproved registry/Git sources and disallowed licences; flag duplicates.
- **cargo-audit**: scheduled/on-demand second RustSec client. This is not an
  independent advisory database; avoid running it on every PR without value.
- **cargo-vet**: defer admission until an owner defines audit criteria, trusted
  imports, exemption review and approval; no fabricated review attestations.
- **cargo-quality**: not adopted. Existing rustfmt/Clippy and Gate G suffice.

Before promoting the workflow to a required check, verify hosted execution on the
exact PR SHA, current RustSec results and licences against the current Cargo.lock.
Do not silence findings using broad exceptions. Record any exception with an
advisory, dependency path, owner, reason, review date and removal condition.

This is a tool-policy check, not APFS/exFAT/native-image acceptance, a parser
security proof, a full transitive unsafe audit or permission to change release
status. No tests were run by the authoring connector. The existing owner retains
Track 006 and release decisions.

Reference: https://github.com/DietrichGebert/ponytail
