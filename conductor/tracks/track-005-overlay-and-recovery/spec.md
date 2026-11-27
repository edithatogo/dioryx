# Base-preserving overlay

## Intent and binding context

Reuse a qualified transactional store or viable image engine, provide bounded changed-block views and instrument the store persistence path. Export a frozen view to a new image.

[REQUIREMENTS](../../../REQUIREMENTS.md), [DESIGN](../../../DESIGN.md),
[delivery plan](../../delivery-plan.md), [workflow](../../workflow.md) and the
[identity mapping](../../../docs/identity.md) apply. This specification refines
execution order without relaxing the original full-MVP or safety requirements.
Current code remains the seed; specifications do not implement the new contracts.

## Scope, interfaces and acceptance

A changing base is invalid; no automatic merge or repair. Logical operation faults and real store-I/O faults are distinct. Database atomicity is not automatically filesystem-operation atomicity or hardware power-loss proof.

Exact phase prerequisites are in this track's `metadata.json`; per-task paths,
regression names and gates are in [plan](plan.md). Core APIs do not expose upstream
mount or parser types. Dependencies are admitted only with source/feature safety
review and a real consumer. Handwritten bytes may test invariant/fault cases but
never stand in for genuine filesystem fixtures.

Every completed task passes G and its stated native, fault or host checks on the
actual reviewed tree. Known version-0.2 limitations and dependency observations
remain open until retested; this revision does not admit new packages or waivers.
Preserve old evidence as historical, and keep current profile results separate.

## Ownership and stopping boundary

The existing integrator controls root manifests, lockfile, shared interfaces, CI
and registry. Dedicated owners change only claimed paths. A newly needed shared
change is handed to that owner rather than duplicated. Stop at the phase boundary
with accept/reject/blocked evidence; no new workers, publication, raw-device action
or unplanned writer is authorized by this document.

## Serde suitability (planning clarification, 18 November 2026)

Serde does not replace filesystem byte parsers, on-disk encodings, bounds checks, storage-engine WAL semantics or native evidence. The present six-crate dependency-light seed is appropriate. **Conditional adoption only** for versioned *control-plane* overlay manifests and recovery metadata at the first real persistence consumer; preserve raw names/source identities and strict recovery invariants. The qualified store's native serialization is preferred unless evidence shows typed Serde reduces code without changing bytes or guarantees. See the new unchecked 005/p1 tasks in [plan.md](plan.md); no new dependency, phase, publisher or owner is created.
