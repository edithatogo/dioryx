# Product guidelines

1. Show the selected source, container, volume, snapshot and effective access
   mode before operations. Source files open read-only unless write access is
   explicitly requested and every layer permits it.
2. Capability output distinguishes available, unsupported, unverified, and
   disabled by policy. Explain why a requested capability is unavailable.
   Never silently fall back from read/write to read-only or from a snapshot to
   the live tree. A user may explicitly request fallback.
3. Errors identify the failing layer, stable error class and safe next step.
   Corrupt metadata, encrypted content, unsupported features, ambiguous probes,
   exhausted budgets and I/O failures remain distinct. Do not print secrets or
   full recovered filenames in ordinary diagnostic telemetry.
4. Preserve raw names and metadata. Normalized display is a view; it never
   changes lookup identity. Reject collisions or use an explicitly requested,
   reversible mapping accompanied by a manifest. Do not silently truncate names.
5. Default permission presentation is conservative and owner-scoped. UID/GID,
   SID, ACL and AppleDouble mapping requires a named policy; synthetic ownership
   is labeled. Never imply these permission systems are interchangeable.
6. Long reads, discovery, decompression and extraction report progress and allow
   cancellation. Keep resident buffers and outstanding operations bounded.
7. CLI text is concise; a versioned machine-readable format provides exact raw
   names, identifiers, feature flags and error codes when implemented. Do not
   claim JSON stability before that schema has a contract and tests.
8. State the supported format subset and tested OS/runtime versions in release
   notes. Avoid marketing labels, unsupported speed claims and line-count
   promises for adapters. No network service or telemetry is required for use.

## Revision 0.2 interaction rules

Report source consistency and selected view before export/mount. Label a live
best-effort read distinctly from a snapshot. Explain the specific layer that
prevents a requested feature. Never silently substitute a live tree for a snapshot,
overlay persistence for raw-device persistence, or advertised upstream support for
qualified behavior.

Backing files and missing pool members require explicit authorized handles; do not
follow image-supplied host paths. Default output is a new destination with no-clobber
semantics. Warn through structured diagnostics about omitted metadata and naming
projection; preserve raw identity in machine-readable output.

Cancellation before submission has no effects; cancellation after possible write
submission may be indeterminate. Show that outcome and required recovery rather
than a misleading successful cancellation. No automatic repair, elevation or raw
merge is a convenience default.
