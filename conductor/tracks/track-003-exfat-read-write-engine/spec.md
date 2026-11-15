# exFAT reuse and staged writes

## Intent and binding context

Qualify a reusable read adapter, source-screen writer candidates, then enable mutation only through the overlay. Test direct disposable-file behavior separately before raw/device write mounts.

[REQUIREMENTS](../../../REQUIREMENTS.md), [DESIGN](../../../DESIGN.md),
[delivery plan](../../delivery-plan.md), [workflow](../../workflow.md) and the
[identity mapping](../../../docs/identity.md) apply. This specification refines
execution order without relaxing the original full-MVP or safety requirements.
Current code remains the seed; specifications do not implement the new contracts.

## Scope, interfaces and acceptance

Safety conflicts remain blockers. Preserve allocation/FAT/entry/valid-data invariants and native fsck/chkdsk plus content evidence. Ordinary exFAT is not made crash-atomic by an overlay; unsupported TexFAT/dirty features deny writes.

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
