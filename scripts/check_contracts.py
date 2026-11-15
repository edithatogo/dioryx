#!/usr/bin/env python3
"""Validate project links, Cargo/track boundaries and verbatim design contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PIN = "7a5c560a4fdf5297be58594cc37527eb12790272"
CONTRACTS = {
    "storage-io": [
        "Geometry", "FlushBarrier", "StorageCapabilities", "BlockDevice",
        "WriteOp", "FlushGroup", "WriteBatch", "CommitReceipt", "WriteFailure",
        "WritableBlockDevice",
    ],
    "container-core": ["Container"],
    "volume-core": ["VolumeId", "VolumeInfo", "VolumePool"],
    "transform-core": ["BlockTransform", "StreamTransform"],
    "semantics-core": [
        "RawName", "Normalization", "OwnershipPolicy", "AppleDoublePolicy",
        "SemanticsPolicy", "Timestamp",
    ],
    "fs-core": [
        "Durability", "FsCapabilities", "CapabilityRequest", "NodeId",
        "Metadata", "DirectoryPage", "LinkTarget", "VirtualFs", "Mutation",
        "MutationOptions", "MutationOutcome", "MutationReceipt", "SyncReceipt",
        "MutationError", "WritableFs",
    ],
}


def declaration(source: str, name: str) -> str:
    pattern = rf"^pub (?:struct|enum|trait|type|fn) {re.escape(name)}\b"
    found = re.search(pattern, source, flags=re.MULTILINE)
    if found is None:
        raise ValueError(f"missing declaration: {name}")
    start = found.start()
    brace = source.find("{", start)
    semicolon = source.find(";", start)
    if semicolon != -1 and (brace == -1 or semicolon < brace):
        return source[start : semicolon + 1]
    # These selected declarations contain no brace-bearing string literals.
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise ValueError(f"unbalanced declaration: {name}")


def blocks() -> str:
    parts = []
    for crate, names in CONTRACTS.items():
        relative = f"crates/{crate}/src/lib.rs"
        source = (ROOT / relative).read_text()
        body = "\n\n".join(declaration(source, name) for name in names)
        parts.append(f"### {crate}\n\nSource: `{relative}`.\n\n```rust\n{body}\n```")
    return "\n\n".join(parts)


def check() -> list[str]:
    errors = []
    manifest = tomllib.loads((ROOT / "Cargo.toml").read_text())
    members = manifest["workspace"]["members"]
    expected = {f"crates/{name}" for name in CONTRACTS}
    if set(members) != expected:
        errors.append("workspace membership changed: review and update the contract inventory")
    for member in members:
        path = ROOT / member
        package = tomllib.loads((path / "Cargo.toml").read_text())
        if package["package"]["name"] != path.name:
            errors.append(f"crate name mismatch: {member}")
        source = (path / "src/lib.rs").read_text()
        if "#![forbid(unsafe_code)]" not in source:
            errors.append(f"unsafe policy missing: {member}")
        if re.search(r"\b(?:panic|todo|unimplemented)!|\.(?:unwrap|expect)\s*\(", source):
            errors.append(f"forbidden production panic construct: {member}")
        if any(dep in package.get("dependencies", {}) for dep in ("unifuse", "winfsp", "rfuse3")):
            errors.append(f"frontend dependency in core: {member}")

    for path in [ROOT / "README.md", ROOT / "DESIGN.md", ROOT / "REQUIREMENTS.md", * (ROOT / "conductor").rglob("*.md")]:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            if not (path.parent / target).exists():
                errors.append(f"broken link in {path.relative_to(ROOT)}: {target}")

    tracks = {}
    for metadata in (ROOT / "conductor/tracks").glob("*/metadata.json"):
        item = json.loads(metadata.read_text())
        if item["track_id"] != metadata.parent.name:
            errors.append(f"track ID mismatch: {metadata}")
        tracks[item["track_id"]] = item
        for required in ("index.md", "spec.md", "plan.md"):
            if not (metadata.parent / required).is_file():
                errors.append(f"missing track file: {metadata.parent / required}")
    active, finished = set(), set()

    def visit(track: str) -> None:
        if track in active:
            errors.append(f"cyclic track dependency: {track}")
            return
        if track in finished:
            return
        active.add(track)
        for dependency in tracks[track].get("dependencies", []):
            if dependency not in tracks:
                errors.append(f"unknown dependency: {track} -> {dependency}")
            else:
                visit(dependency)
        active.remove(track)
        finished.add(track)

    for track in tracks:
        visit(track)
    content = (ROOT / "DESIGN.md").read_text()
    expected_blocks = blocks()
    start = "<!-- BEGIN COMPILED CONTRACTS -->\n"
    end = "\n<!-- END COMPILED CONTRACTS -->"
    if start not in content or end not in content:
        errors.append("missing design contract delimiters")
    elif content.split(start, 1)[1].split(end, 1)[0] != expected_blocks:
        errors.append("DESIGN contract drift: run python3 scripts/check_contracts.py --sync-design")
    submodule = ROOT / ".gemini/extensions/conductor"
    result = subprocess.run(
        ["git", "-C", str(submodule), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != PIN:
        errors.append("Conductor checkout missing or differs from reviewed pin")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync-design", action="store_true")
    args = parser.parse_args()
    if args.sync_design:
        path = ROOT / "DESIGN.md"
        text = path.read_text()
        start = "<!-- BEGIN COMPILED CONTRACTS -->\n"
        end = "\n<!-- END COMPILED CONTRACTS -->"
        replacement = start + blocks() + end
        if "<!-- CONTRACT_BLOCKS -->" in text:
            text = text.replace("<!-- CONTRACT_BLOCKS -->", replacement)
        elif start in text and end in text:
            before, remaining = text.split(start, 1)
            _, after = remaining.split(end, 1)
            text = before + replacement + after
        else:
            raise ValueError("design contract insertion point missing")
        path.write_text(text)
    failures = check()
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("Contract declarations, links, track DAG, core boundaries and Conductor pin: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
