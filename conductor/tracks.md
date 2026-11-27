# Dioryx execution tracks

[Delivery plan](delivery-plan.md) owns milestone/prioritisation decisions;
[requirements](../REQUIREMENTS.md) and [design](../DESIGN.md) remain binding.
The six original track IDs are retained; no second execution hierarchy is created.

`[ ]` pending; `[~]` active; `[x]` complete only with G and required evidence;
`[!]` blocked. Historical seed completion is not current-head acceptance.

| Track | Main delivery | Ordering change in revision 0.3 |
| --- | --- | --- |
| 001 | Minimal read contracts, later mount/write contracts | r0 reproduces baseline; p2 read core; p3 layers and p4 read metadata branch; p5 mounts and p6 writes do not block native proof |
| 002 | APFS proof -> library/CLI -> read mounts | p1 needs baseline and native fixture admission, not complete core; p2 needs actual read/layer contracts |
| 003 | exFAT reads/selection -> overlay mutation -> direct writes | Read admission independent of APFS; writer admission uses actual overlay/write contracts and later native authority |
| 004 | Additional read-only consumers | Optional expansion; no automatic journaled writers or unused crypto |
| 005 | Store decision -> overlay -> persistence tests -> new-image export | No dependency on its eventual exFAT consumer; actual store-I/O fault seam is mandatory |
| 006 | Early corpus -> image isolation -> raw broker -> release join | Fixture admission starts at r0; image reads do not wait for the privileged broker |

Metadata phase references (`track-id#phase-id`) are executable prerequisites.
Top-level track references are only context. The phase graph is authoritative;
per-host profile evidence is additionally required. The implemented `scripts/conductor_graph.py` validates phase/profile structure,
acyclic dependencies, plan alignment and exact evidence dimension requirements.
The separate `scripts/conductor_evidence.py` matches independently reviewed
checkpoint requests against exact scope and content pins. The catalog digest
binds normative completion and profile policy, excluding descriptive status.
Neither script verifies native execution or promotes a profile to qualified.

The release-profile table is in track 006 metadata. Its phase prerequisites do not
assert those phases are passed: every result must also bind host/runtime, source,
features, fixture, mode and fault model. Full three-host phases remain open until
all required cells pass; narrower qualified previews may be released only after
their own gates and separate publication approval.

## [~] 001 — Minimal read foundation and later storage contracts

[Track](tracks/track-001-workspace-and-core-traits/index.md).

## [ ] 002 — APFS native proof and delivery

[Track](tracks/track-002-apfs-readonly-and-mount/index.md).

## [ ] 003 — exFAT reuse and staged writes

[Track](tracks/track-003-exfat-read-write-engine/index.md).

## [ ] 004 — Narrow additional readers

[Track](tracks/track-004-multi-fs-expansion-and-transforms/index.md).

## [ ] 005 — Base-preserving overlay

[Track](tracks/track-005-overlay-and-recovery/index.md).

## [~] 006 — Native evidence and authority qualification

[Track](tracks/track-006-conformance-and-release/index.md).

## [!] Revision 0.3 acceptance

The Dioryx identity and refined plans are authored. Rust/Cargo/lock/toolchain/CI
and repository validation scripts are unchanged. Cargo acceptance cannot run in
this runtime because cargo/rustc/rustup are absent. No new feature task is complete.
[Revision record](tracks/track-001-workspace-and-core-traits/revision-0.3.md).

## Scoped prerequisite resolution

A phase edge requires its accepted interface checkpoint and, for native work, the
matching target/profile evidence. It does not require unrelated host lanes to pass.
For example, a qualified Linux image worker can admit the Linux image-mount lane
while Windows isolation remains blocked; aggregate 006/p2 stays pending until all
required hosts pass. An unreviewed partial implementation cannot satisfy an edge.
The r0 phase/profile checker must reject evidence with a different target, mode or
source/contract revision, and must never use a historical phase status as evidence.
