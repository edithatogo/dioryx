"""Independent synthetic preflight regressions, not native admission evidence."""

import hashlib
import tempfile
import unittest
from pathlib import Path

import fixture_validation as validation

from fixture_validation import (
    FixtureRejected,
    NativeProvenance,
    check_feature_manifest,
    check_oracle_ancestry,
)


class CompositePreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="dioryx-preflight-")
        self.addCleanup(temporary.cleanup)
        self.fixture = Path(temporary.name) / "synthetic-data.txt"
        self.fixture.write_bytes(b"Synthetic test bytes. No filesystem image.\n")
        self.sha = hashlib.sha256(self.fixture.read_bytes()).hexdigest()
        self.record = NativeProvenance(
            origin="native-os", generator_os="macos",
            os_version="test-only", formatter="hdiutil", formatter_version="test-only",
            creation_commands=("test-only inert command",),
            checker="diskutil", checker_version="test-only",
            checker_result="test-only", redistribution_rights="test-only",
        )
        self.features = {"filesystem": "test-only", "view": "controlled", "features": {"snapshots": False}}
        self.candidate = ["test-only:candidate", "test-only:ancestor"]
        self.oracle = ["test-only:independent"]

    def preflight(self, **changes):
        params = dict(
            path=self.fixture, expected_sha256=self.sha, max_bytes=4096,
            filesystem="apfs", native_provenance=self.record,
            actual_features=self.features, expected_features=self.features,
            candidate_ancestry=self.candidate, oracle_ancestry=self.oracle,
        )
        params.update(changes)
        return validation.check_fixture_preflight(**params)

    def assertRejected(self, code, **changes):
        with self.assertRaises(FixtureRejected) as caught:
            self.preflight(**changes)
        self.assertEqual(caught.exception.code, code)

    def test_preflight_requires_fixture(self):
        self.assertRejected("missing-fixture", path=self.fixture.with_suffix(".missing"))

    def test_preflight_requires_pinned_actual_bytes(self):
        self.assertRejected("bad-hash", expected_sha256="0" * 64)

    def test_preflight_requires_native_generator_record(self):
        self.assertRejected("absent-native-provenance", native_provenance=None)

    def test_preflight_requires_exact_feature_manifest(self):
        self.assertRejected("wrong-feature-manifest", actual_features={"view": "different"})

    def test_preflight_requires_disjoint_declared_oracle_ancestry(self):
        self.assertRejected("shared-oracle-ancestry", oracle_ancestry=["test-only:ancestor"])

    def test_preflight_never_emits_acceptance_or_changes_source(self):
        initial = self.fixture.read_bytes()
        self.assertIsNone(self.preflight())
        self.assertEqual(self.fixture.read_bytes(), initial)

    def test_preflight_does_not_allow_absent_independent_expectation(self):
        self.assertRejected("wrong-feature-manifest", expected_features={})


class BoundedInputTests(unittest.TestCase):
    def test_large_feature_string_rejected_even_when_equal(self):
        huge = {"view": "x" * 1_048_577}
        with self.assertRaises(FixtureRejected) as caught:
            check_feature_manifest(huge, expected=huge)
        self.assertEqual(caught.exception.code, "wrong-feature-manifest")

    def test_large_feature_key_rejected_even_when_equal(self):
        huge = {"key" * 350000: True}
        with self.assertRaises(FixtureRejected) as caught:
            check_feature_manifest(huge, expected=huge)
        self.assertEqual(caught.exception.code, "wrong-feature-manifest")

    def test_oversized_ancestry_record_rejected(self):
        with self.assertRaises(FixtureRejected) as caught:
            check_oracle_ancestry(["test-only:" + "x" * 4096], ["test-only:independent"])
        self.assertEqual(caught.exception.code, "incomplete-oracle-ancestry")

    def test_duplicate_ancestry_record_rejected(self):
        with self.assertRaises(FixtureRejected) as caught:
            check_oracle_ancestry(["test-only:root", "test-only:root"], ["test-only:other"])
        self.assertEqual(caught.exception.code, "incomplete-oracle-ancestry")

    def test_invalid_unicode_ancestry_returns_typed_rejection(self):
        with self.assertRaises(FixtureRejected) as caught:
            check_oracle_ancestry(["test-only:\ud800"], ["test-only:independent"])
        self.assertEqual(caught.exception.code, "incomplete-oracle-ancestry")

    def test_many_ancestry_records_rejected(self):
        with self.assertRaises(FixtureRejected) as caught:
            check_oracle_ancestry([f"test-only:{i}" for i in range(300)], ["test-only:other"])
        self.assertEqual(caught.exception.code, "incomplete-oracle-ancestry")

    def test_small_pinned_features_and_ancestry_remain_valid_preflight_inputs(self):
        feature = {"filesystem": "test-only", "features": {"snapshots": False}}
        self.assertIsNone(check_feature_manifest(feature, expected=feature))
        self.assertIsNone(check_oracle_ancestry(["test-only:one"], ["test-only:other"]))


if __name__ == "__main__":
    unittest.main()
