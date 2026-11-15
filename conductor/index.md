# Dioryx project context

- [Delivery plan and milestones](delivery-plan.md)
- [Identity and namespace](../docs/identity.md)
- [Product](product.md)
- [Product guidelines](product-guidelines.md)
- [Technology stack](tech-stack.md)
- [Workflow](workflow.md)
- [Rust style](code_styleguides/rust.md)
- [Tracks registry](tracks.md)
- [Requirements](../REQUIREMENTS.md)
- [Design and compiled contracts](../DESIGN.md)
- [Dependency evidence](../docs/dependency-evidence.md)
- [Real-image fixtures](../tests/fixtures/README.md)

Tracks live in `tracks/`; completed tracks move to `archive/` only after explicit
review and a recorded commit. The upstream protocol is the pinned Git submodule
at `../.gemini/extensions/conductor/`. This index is authoritative for file
resolution. Relative links resolve from the containing index.

Revision 0.3 status and verification are in the
[track 001 revision record](tracks/track-001-workspace-and-core-traits/revision-0.3.md).
The same [track registry](tracks.md) now owns tracks 005 and 006; there is no second
execution-plan hierarchy.

Current repository installation and its verification boundaries are recorded in
[the import record](tracks/track-001-workspace-and-core-traits/repository-import.md).
Earlier archive-only status statements are historical; no feature status is upgraded by import.
