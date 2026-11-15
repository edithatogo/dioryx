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

## Proposed namespace, not an executed Cargo rename

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

Retain existing directories and track IDs to preserve links and history. Perform
all six existing package-name changes as one mechanical, separately reviewed
track-001/r0 task after reproducing the baseline. Update dependency package aliases,
Cargo.lock, the contract checker's explicit directory-to-package mapping and its
regressions together. Internal aliases may preserve existing imports during this
mechanical change; they must not expose third-party types in the public API.
Tests specified by manifest path continue to work across the package-name change.
Do not create the umbrella package until it has a real open/list/read consumer.
Do not create any future package merely to reserve a name. All packages remain
`publish = false`; licensing and publication remain explicit later decisions.

The present revision changes documentation only. Current Cargo names and source
remain exactly those of the supplied version 0.2 workspace. Product/document
revision 0.3 is not a release version or a claim of API stability.
