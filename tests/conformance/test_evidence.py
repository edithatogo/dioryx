"""Synthetic rejection regressions; no native filesystem qualification."""

import json
import os
import tempfile
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from fixture_validation import (
    FixtureRejected,
    NativeProvenance,
    check_feature_manifest,
    check_fixture_file,
    check_native_provenance,
    check_oracle_ancestry,
)


NEGATIVE = Path(__file__).resolve().parents[1] / "fixtures" / "negative"
CASES = json.loads((NEGATIVE / "cases.json").read_text(encoding="utf-8"))
PAYLOAD = (NEGATIVE / "payload.txt").read_bytes()
PAYLOAD_SHA256 = CASES["payload_sha256"]


class EvidenceRejectionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="dioryx-rejections-")
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.fixture = self.directory / "synthetic.txt"
        self.fixture.write_bytes(PAYLOAD)

    def rejected(self, code, function, *args, **kwargs):
        with self.assertRaises(FixtureRejected) as raised:
            function(*args, **kwargs)
        self.assertEqual(raised.exception.code, code, str(raised.exception))
        self.assertTrue(str(raised.exception))
        return raised.exception

    def check_file(self, path=None, digest=PAYLOAD_SHA256, budget=4096):
        return check_fixture_file(
            self.fixture if path is None else path,
            expected_sha256=digest,
            max_bytes=budget,
        )

    def provenance(self):
        # Invented field values exercise structure only. There is no OS master.
        return NativeProvenance(
            origin="native-os",
            generator_os="macos",
            os_version="synthetic-test-only-os-version",
            formatter="hdiutil",
            formatter_version="synthetic-test-only-tool-version",
            creation_commands=("synthetic command text; never executed",),
            checker="diskutil",
            checker_version="synthetic-test-only-checker-version",
            checker_result="synthetic-test-only-result",
            redistribution_rights="synthetic-test-only-rights-record",
        )

    def test_missing_fixture_rejected(self):
        error = self.rejected(
            "missing-fixture", self.check_file, self.directory / "missing.img"
        )
        self.assertIn("restore", str(error).lower())

    def test_bad_hash_rejected(self):
        self.rejected("bad-hash", self.check_file, digest="0" * 64)
        self.assertEqual(self.fixture.read_bytes(), PAYLOAD)

    def test_absent_native_provenance_rejected(self):
        self.rejected("absent-native-provenance", check_native_provenance, "apfs", None)

    def test_wrong_feature_manifest_rejected(self):
        changed = deepcopy(CASES["feature_manifest"])
        changed["features"]["snapshots"] = True
        self.rejected(
            "wrong-feature-manifest",
            check_feature_manifest,
            changed,
            expected=CASES["feature_manifest"],
        )

    def test_shared_oracle_ancestry_rejected(self):
        self.rejected(
            "shared-oracle-ancestry",
            check_oracle_ancestry,
            CASES["candidate_ancestry"],
            CASES["fork_oracle_ancestry"],
        )

    def test_matching_hash_is_only_an_integrity_check(self):
        self.assertIsNone(self.check_file())
        self.assertEqual(self.fixture.read_bytes(), PAYLOAD)

    def test_hash_is_computed_from_current_bytes(self):
        self.fixture.write_bytes(PAYLOAD + b"changed")
        self.rejected("bad-hash", self.check_file)

    def test_malformed_hash_rejected_before_file_access(self):
        with patch("fixture_validation.os.open") as opened:
            for digest in (None, "", "a" * 63, "g" * 64, "A" * 64):
                with self.subTest(digest=digest):
                    self.rejected("invalid-hash", self.check_file, digest=digest)
            opened.assert_not_called()

    def test_directory_is_not_a_fixture(self):
        self.rejected("not-regular-file", self.check_file, self.directory)

    def test_symlink_is_not_a_fixture(self):
        link = self.directory / "alias"
        link.symlink_to(self.fixture)
        self.rejected("not-regular-file", self.check_file, link)

    def test_budget_checked_before_open(self):
        with patch("fixture_validation.os.open") as opened:
            self.rejected("fixture-too-large", self.check_file, budget=len(PAYLOAD) - 1)
            opened.assert_not_called()

    def test_invalid_budget_rejected(self):
        for budget in (None, True, 0, -1, 1.0):
            with self.subTest(budget=budget):
                self.rejected("invalid-budget", self.check_file, budget=budget)

    def test_exact_size_budget_is_enough(self):
        self.assertIsNone(self.check_file(budget=len(PAYLOAD)))

    def test_io_failure_is_not_a_missing_fixture_pass(self):
        with patch("fixture_validation.os.open", side_effect=PermissionError("denied")):
            self.rejected("fixture-io", self.check_file)

    def test_short_reads_are_hashed_completely(self):
        read = os.read
        with patch(
            "fixture_validation.os.read",
            side_effect=lambda fd, size: read(fd, min(size, 7)),
        ):
            self.assertIsNone(self.check_file())

    def test_truncation_during_hashing_rejected(self):
        read = os.read

        def truncate_then_read(descriptor, size):
            self.fixture.write_bytes(b"")
            return read(descriptor, size)

        with patch("fixture_validation.os.read", side_effect=truncate_then_read):
            self.rejected("fixture-changed", self.check_file)

    def test_growth_during_hashing_rejected_without_unbounded_reads(self):
        read = os.read
        requested = []

        def append_then_read(descriptor, size):
            requested.append(size)
            with self.fixture.open("ab") as writer:
                writer.write(b"growth")
            return read(descriptor, size)

        with patch("fixture_validation.os.read", side_effect=append_then_read):
            self.rejected("fixture-changed", self.check_file)
        self.assertEqual(sum(requested), len(PAYLOAD))

    def test_change_before_open_rejected(self):
        open_file = os.open

        def change_then_open(path, flags):
            self.fixture.write_bytes(PAYLOAD + b"changed before open")
            return open_file(path, flags)

        with patch("fixture_validation.os.open", side_effect=change_then_open):
            self.rejected("fixture-changed", self.check_file)

    def test_synthetic_origin_rejected_despite_native_looking_fields(self):
        record = replace(self.provenance(), origin="synthetic")
        self.rejected("absent-native-provenance", check_native_provenance, "apfs", record)

    def test_linux_cannot_be_an_apfs_native_generator(self):
        record = replace(self.provenance(), generator_os="linux")
        self.rejected("absent-native-provenance", check_native_provenance, "apfs", record)

    def test_apfs_formatter_must_match_pinned_native_recipe(self):
        record = replace(self.provenance(), formatter="synthetic-parser")
        self.rejected("absent-native-provenance", check_native_provenance, "apfs", record)

    def test_missing_provenance_fields_rejected(self):
        for name in (
            "generator_os", "os_version", "formatter", "formatter_version",
            "checker", "checker_version", "checker_result", "redistribution_rights",
        ):
            with self.subTest(field=name):
                record = replace(self.provenance(), **{name: " "})
                self.rejected(
                    "absent-native-provenance", check_native_provenance, "apfs", record
                )

    def test_missing_or_malformed_creation_commands_rejected(self):
        for commands in ((), None, "not a command list", ("",), (42,)):
            with self.subTest(commands=commands):
                record = replace(self.provenance(), creation_commands=commands)
                self.rejected(
                    "absent-native-provenance", check_native_provenance, "apfs", record
                )

    def test_complete_record_checks_presence_without_native_acceptance(self):
        self.assertIsNone(check_native_provenance("apfs", self.provenance()))

    def test_exfat_formatter_record_only_checks_structure(self):
        record = replace(
            self.provenance(), origin="maintained-formatter", generator_os="linux",
            formatter="mkfs.exfat", checker="fsck.exfat",
        )
        self.assertIsNone(check_native_provenance("exfat", record))
        self.rejected("absent-native-provenance", check_native_provenance, "apfs", record)

    def test_unpinned_filesystem_recipe_rejected(self):
        self.rejected(
            "absent-native-provenance", check_native_provenance, "unknown", self.provenance()
        )

    def test_generation_commands_are_never_executed(self):
        marker = self.directory / "must-not-exist"
        record = replace(self.provenance(), creation_commands=(f"touch {marker}",))
        self.assertIsNone(check_native_provenance("apfs", record))
        self.assertFalse(marker.exists())

    def test_feature_comparison_checks_extra_missing_and_nested_fields(self):
        for change in ("extra", "missing", "container", "geometry", "view"):
            actual = deepcopy(CASES["feature_manifest"])
            if change == "extra":
                actual["unreviewed-feature"] = True
            elif change == "missing":
                del actual["container"]
            elif change == "container":
                actual["container"] = "wrong-container"
            elif change == "geometry":
                actual["sector_size"] = 4096
            else:
                actual["view"] = "wrong-view"
            with self.subTest(change=change):
                self.rejected(
                    "wrong-feature-manifest", check_feature_manifest,
                    actual, expected=CASES["feature_manifest"],
                )

    def test_boolean_and_integer_features_are_distinct(self):
        self.rejected(
            "wrong-feature-manifest", check_feature_manifest,
            {"snapshots": 0}, expected={"snapshots": False},
        )

    def test_invalid_or_empty_feature_manifests_rejected(self):
        for actual in ({}, None, [], {"feature": float("nan")}, {1: "value"}):
            with self.subTest(actual=actual):
                self.rejected(
                    "wrong-feature-manifest", check_feature_manifest,
                    actual, expected=CASES["feature_manifest"],
                )
        self.rejected(
            "wrong-feature-manifest", check_feature_manifest, {}, expected={}
        )

    def test_cyclic_oversized_or_ambiguous_feature_objects_rejected(self):
        cyclic = {"feature": None}
        cyclic["feature"] = cyclic
        for actual in (cyclic, {"feature": [False] * 10001}, {"feature": {1: "value"}}):
            with self.subTest(kind=type(actual["feature"]).__name__):
                self.rejected(
                    "wrong-feature-manifest", check_feature_manifest,
                    actual, expected=CASES["feature_manifest"],
                )

    def test_equal_feature_maps_allow_key_reordering_without_mutation(self):
        actual = dict(reversed(list(CASES["feature_manifest"].items())))
        before = deepcopy(actual)
        self.assertIsNone(check_feature_manifest(actual, expected=CASES["feature_manifest"]))
        self.assertEqual(actual, before)

    def test_parser_identity_in_other_ancestry_rejected(self):
        self.rejected(
            "shared-oracle-ancestry", check_oracle_ancestry,
            ["synthetic:root"], ["synthetic:fork", "synthetic:root"],
        )

    def test_incomplete_oracle_ancestry_rejected(self):
        for ancestry in (None, [], "synthetic:parser", [""], [" unnormalised "]):
            with self.subTest(ancestry=ancestry):
                self.rejected(
                    "incomplete-oracle-ancestry", check_oracle_ancestry,
                    CASES["candidate_ancestry"], ancestry,
                )
                self.rejected(
                    "incomplete-oracle-ancestry", check_oracle_ancestry,
                    ancestry, CASES["separate_oracle_ancestry"],
                )

    def test_disjoint_declared_ancestry_is_not_proof_of_independence(self):
        self.assertIsNone(check_oracle_ancestry(
            CASES["candidate_ancestry"], CASES["separate_oracle_ancestry"]
        ))


if __name__ == "__main__":
    unittest.main()
