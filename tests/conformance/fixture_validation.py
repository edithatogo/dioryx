"""Local rejection checks for the pinned fixture requirements.

These functions return no qualification or admission record. The coordinator
owns the versioned evidence schema and accepted track001/r0 checkpoint. Inputs
must come from an explicitly authorised fixture and a separately pinned oracle;
metadata in an image never grants host-file or command-execution authority.
"""

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path


class FixtureRejected(ValueError):
    """A preflight rejection with a testable reason and an actionable message."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class NativeProvenance:
    """In-memory arguments for presence checks, not a serialized evidence schema."""

    origin: str
    generator_os: str
    os_version: str
    formatter: str
    formatter_version: str
    creation_commands: tuple[str, ...]
    checker: str
    checker_version: str
    checker_result: str
    redistribution_rights: str


def _file_identity(info, *, same_accessor=False):
    identity = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    # CPython Windows path stat and fstat may disagree on deprecated ctime.
    # Compare creation time across accessors; retain ctime within each accessor.
    # https://github.com/python/cpython/issues/157671
    if os.name == "nt":
        identity += (info.st_birthtime_ns,)
        if not same_accessor:
            return identity
    return (*identity, info.st_ctime_ns)


def check_fixture_file(path: Path, *, expected_sha256: str, max_bytes: int) -> None:
    """Hash one authorised, stable regular file without writing or mounting it.

    The caller owns the containing directory and pins the digest independently.
    This is not a hostile-path sandbox or a mechanism for freezing a live source.
    Reads are bounded by the initially observed size and the explicit byte limit.
    """
    if not isinstance(expected_sha256, str) or re.fullmatch(
        r"[0-9a-f]{64}", expected_sha256
    ) is None:
        raise FixtureRejected("invalid-hash", "Pin a lowercase 64-digit SHA-256 digest.")
    if type(max_bytes) is not int or max_bytes <= 0:
        raise FixtureRejected("invalid-budget", "Supply a positive integer byte limit.")

    path = Path(path)
    try:
        before = path.lstat()
    except FileNotFoundError as error:
        raise FixtureRejected(
            "missing-fixture", "Restore the required pinned fixture before retrying."
        ) from error
    except OSError as error:
        raise FixtureRejected("fixture-io", "Cannot inspect the authorised fixture.") from error
    if not stat.S_ISREG(before.st_mode):
        raise FixtureRejected("not-regular-file", "Use a regular file, not a link or device.")
    if before.st_size > max_bytes:
        raise FixtureRejected("fixture-too-large", "The fixture exceeds its byte limit.")

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise FixtureRejected("not-regular-file", "The opened fixture is not regular.")
            if _file_identity(opened) != _file_identity(before):
                raise FixtureRejected("fixture-changed", "The fixture changed before hashing.")
            digest = hashlib.sha256()
            remaining = opened.st_size
            while remaining:
                chunk = os.read(descriptor, min(remaining, 1024 * 1024))
                if not chunk:
                    raise FixtureRejected("fixture-changed", "The fixture was truncated.")
                digest.update(chunk)
                remaining -= len(chunk)
            if (
                _file_identity(os.fstat(descriptor), same_accessor=True)
                != _file_identity(opened, same_accessor=True)
                or _file_identity(path.lstat(), same_accessor=True)
                != _file_identity(before, same_accessor=True)
            ):
                raise FixtureRejected("fixture-changed", "The fixture changed while hashing.")
        finally:
            os.close(descriptor)
    except FileNotFoundError as error:
        raise FixtureRejected(
            "fixture-changed", "The fixture disappeared while hashing."
        ) from error
    except OSError as error:
        raise FixtureRejected("fixture-io", "Cannot read the authorised fixture.") from error
    if digest.hexdigest() != expected_sha256:
        raise FixtureRejected("bad-hash", "Fixture bytes differ from the pinned SHA-256.")


def _nonblank(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_native_provenance(filesystem: str, record: NativeProvenance | None) -> None:
    """Reject missing native-generator fields; do not authenticate their claims.

    Check the recorded generator, never the consumer's current operating system.
    Creation commands are inert text. Genuine artifacts, reviewed generator logs
    and the coordinator's matching checkpoint are still required for admission.
    """
    if not isinstance(record, NativeProvenance):
        raise FixtureRejected("absent-native-provenance", "Supply the native generator record.")
    fields = (
        record.os_version, record.formatter_version, record.checker,
        record.checker_version, record.checker_result, record.redistribution_rights,
    )
    if not all(_nonblank(value) for value in fields):
        raise FixtureRejected(
            "absent-native-provenance", "Record OS/tool versions, checker result and rights."
        )
    commands = record.creation_commands
    if (
        not isinstance(commands, (tuple, list))
        or not commands
        or not all(_nonblank(command) for command in commands)
    ):
        raise FixtureRejected("absent-native-provenance", "Record the actual creation commands.")

    if filesystem == "apfs":
        native_recipe = (
            record.origin == "native-os"
            and record.generator_os == "macos"
            and record.formatter == "hdiutil"
        )
    elif filesystem == "exfat":
        native_recipe = (
            record.origin == "maintained-formatter"
            and record.generator_os == "linux"
            and record.formatter == "mkfs.exfat"
        ) or (
            record.origin == "native-os"
            and record.generator_os == "windows"
            and _nonblank(record.formatter)
        )
    else:
        native_recipe = False
    if not native_recipe:
        raise FixtureRejected(
            "absent-native-provenance",
            "Record the native generator from a pinned recipe; synthetic bytes do not qualify.",
        )


# Input-size limits apply to decoded test/fixture objects, not raw disk images.
MAX_FEATURE_TEXT_BYTES = 256 * 1024
MAX_ANCESTRY_ENTRIES = 256
MAX_ANCESTRY_ID_BYTES = 256


def _canonical_features(value) -> str:
    if type(value) is not dict or not value:
        raise ValueError("a nonempty feature object is required")
    pending = [(value, 0)]
    visited = 0
    remaining_text_bytes = MAX_FEATURE_TEXT_BYTES

    def charge(value: str) -> None:
        nonlocal remaining_text_bytes
        if len(value) > remaining_text_bytes:
            raise ValueError("feature text exceeds byte budget")
        remaining_text_bytes -= len(value.encode("utf-8"))
        if remaining_text_bytes < 0:
            raise ValueError("feature text exceeds byte budget")
    while pending:
        item, depth = pending.pop()
        visited += 1
        if depth > 32 or visited > 10000:
            raise ValueError("feature object exceeds structural limits")
        if type(item) is dict:
            if any(not _nonblank(key) for key in item):
                raise ValueError("feature keys must be nonblank strings")
            for key in item:
                charge(key)
            if len(item) > 10000 - visited - len(pending):
                raise ValueError("feature object exceeds structural limits")
            pending.extend((child, depth + 1) for child in item.values())
        elif type(item) is list:
            if len(item) > 10000 - visited - len(pending):
                raise ValueError("feature object exceeds structural limits")
            pending.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            charge(item)
        elif type(item) not in (int, float, bool, type(None)):
            raise ValueError("feature values must be JSON values")
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def check_feature_manifest(actual: dict, *, expected: dict) -> None:
    """Require exact JSON feature equality to a separately pinned expectation.

    Object key order is irrelevant; value types and list order are significant.
    No defaults, subset matching or feature/name normalization is applied.
    This compares decoded objects; it does not define or load a shared schema.
    """
    try:
        matches = _canonical_features(actual) == _canonical_features(expected)
    except (TypeError, ValueError, RecursionError, UnicodeError) as error:
        raise FixtureRejected(
            "wrong-feature-manifest", "Supply valid pinned feature objects."
        ) from error
    if not matches:
        raise FixtureRejected(
            "wrong-feature-manifest",
            "Features differ from the pinned container/filesystem/view manifest.",
        )


def _valid_ancestry_identity(value) -> bool:
    if not _nonblank(value) or value != value.strip():
        return False
    if len(value) > MAX_ANCESTRY_ID_BYTES:
        return False
    try:
        return len(value.encode("utf-8")) <= MAX_ANCESTRY_ID_BYTES
    except UnicodeError:
        return False


def _ancestry(values) -> set[str]:
    if (
        not isinstance(values, (list, tuple, set, frozenset))
        or not values
        or len(values) > MAX_ANCESTRY_ENTRIES
        or not all(_valid_ancestry_identity(value) for value in values)
        or len(set(values)) != len(values)
    ):
        raise FixtureRejected(
            "incomplete-oracle-ancestry",
            "Record canonical implementation and transitive parser ancestry IDs.",
        )
    return set(values)


def check_oracle_ancestry(candidate, oracle) -> None:
    """Reject shared declared parser ancestry, including forks and direct reuse.

    Each collection includes its own implementation and every relevant ancestor.
    Completeness and canonical identity need source review; disjoint declarations
    alone do not authenticate independence. No package names are inferred here.
    """
    if _ancestry(candidate) & _ancestry(oracle):
        raise FixtureRejected(
            "shared-oracle-ancestry",
            "The comparator shares parser ancestry; obtain an independent oracle.",
        )


def check_fixture_preflight(
    *,
    path: Path,
    expected_sha256: str,
    max_bytes: int,
    filesystem: str,
    native_provenance: NativeProvenance | None,
    actual_features: dict,
    expected_features: dict,
    candidate_ancestry,
    oracle_ancestry,
) -> None:
    """Run all four local rejection checks; never return an admission decision.

    The caller separately pins the digest and expected features and authorises
    the stable regular-file path. Native provenance and oracle independence still
    require source review; an r0 checkpoint must be verified independently.
    Passing preflight returns None, not acceptance or evidence of execution.
    """
    check_fixture_file(path, expected_sha256=expected_sha256, max_bytes=max_bytes)
    check_native_provenance(filesystem, native_provenance)
    check_feature_manifest(actual_features, expected=expected_features)
    check_oracle_ancestry(candidate_ancestry, oracle_ancestry)
