# Dioryx — identity and namespace

**Decision:** use **Dioryx** as the project name for this framework.
**Descriptor:** a composable Rust framework for cross-platform filesystem access.
**Short line:** one interface, many filesystems, explicit guarantees.
**Suggested English pronunciation:** dye-OR-iks. This is a proposed brand pronunciation,
not a claim about historical or modern Greek pronunciation.

The name is drawn from Greek διῶρυξ, a canal or conduit: a constructed passage
between otherwise separated systems. The metaphor describes interoperability
without implying a new on-disk format, universal write support, automatic repair,
or a distributed storage service. It also sits comfortably alongside Kairos,
Paignia and Dapane without introducing an actual dependency on those projects.

## Alternatives and bounded collision check

Perasma was attractive for its meaning of passage, but an existing public project
`Malti2/Perasma` describes a native macOS launcher/library for Windows software.
That is close enough to cross-platform tooling to prefer another name. Gephyra
already has software uses, including an editor extension. Neither is selected.

On 15 November 2026, a public GitHub name search for `dioryx in:name` returned
`mitishraina/Dioryxis`, but no exact Dioryx repository in the returned results.
The crates.io index path `di/or/dioryx` returned 404 through the GitHub connector.
Direct crates.io API checks could not be completed in this runtime. These are
limited collision checks, not proof of availability, registry reservation, domain
availability or trademark clearance. Dioryx has non-software uses, including a
maritime company. Recheck exact and confusingly similar names before publication.
No repository, package, domain or trademark was registered by that planning revision.
The user subsequently created `edithatogo/dioryx` and authorised this repository import.
Package publication, domain registration and trademark clearance remain separate decisions.

Sources consulted:
- Greek lexical entry: https://plato.johnhboyer.com/lemma/dioryx/
- University of Copenhagen epigraphic corpus, canal usage: https://ancientassociations.ku.dk/assoc/viewing.php?id=646&view=resultassoc
- Perasma project metadata: https://api.github.com/repos/Malti2/Perasma
- Gephyra extension: https://marketplace.visualstudio.com/items?itemName=alkisyuv.gephyra
- Registry index check: https://api.github.com/repos/rust-lang/crates.io-index/contents/di/or/dioryx

## Current namespace and future packages

| Existing directory / responsibility | Target package | Public Rust import / executable |
| --- | --- | --- |
| `crates/storage-io` | `dioryx-storage` | `dioryx_storage` |
| `crates/container-core` | `dioryx-containers` | `dioryx_containers` |
| `crates/volume-core` | `dioryx-volumes` | `dioryx_volumes` |
| `crates/transform-core` | `dioryx-transforms` | `dioryx_transforms` |
| `crates/semantics-core` | `dioryx-semantics` | `dioryx_semantics` |
| `crates/fs-core` | `dioryx-vfs` | `dioryx_vfs` |
| Future `crates/backend-apfs` | `dioryx-apfs` | `dioryx_apfs` |
| Future `crates/backend-exfat` | `dioryx-exfat` | `dioryx_exfat` |
| Future `crates/storage-overlay` | `dioryx-overlay` | `dioryx_overlay` |
| Future `crates/mount-unifuse` | `dioryx-mount-unifuse` | adapter only |
| Future `crates/fs-cli` | `dioryx-cli` | binary `dioryx` |
| Future `crates/dioryx` | `dioryx` | application-facing library |

The first six package names above are implemented. Existing directories and track
IDs are retained. Workspace dependency keys and Rust imports use the same
`dioryx-*` / `dioryx_*` names; no legacy alias or old public library name is kept.
The namespace validator has an explicit directory-to-package map and checks actual
Cargo metadata, including public library target names and disabled publishing.

The remaining rows are future packages, not empty reservations. Do not create the
umbrella package until it has a real open/list/read consumer. All packages remain
`publish = false`; licensing and publication remain explicit later decisions.

The original revision 0.3 was documentation-only. Namespace execution and its
qualification now belong to [track 001/r0](../conductor/tracks/track-001-workspace-and-core-traits/plan.md).
Neither planning revision 0.3 nor this rename is a release or API-stability claim.
