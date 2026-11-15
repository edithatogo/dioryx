"""Namespace regressions; these are not filesystem compatibility tests."""
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_contracts as checker

NAMES = {
    "storage-io": "dioryx-storage",
    "container-core": "dioryx-containers",
    "volume-core": "dioryx-volumes",
    "transform-core": "dioryx-transforms",
    "semantics-core": "dioryx-semantics",
    "fs-core": "dioryx-vfs",
}


class NamespaceTests(unittest.TestCase):
    def test_existing_packages_have_dioryx_names(self):
        actual = {
            directory: tomllib.loads(
                (checker.ROOT / "crates" / directory / "Cargo.toml").read_text()
            )["package"]["name"]
            for directory in NAMES
        }
        self.assertEqual(actual, NAMES)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("Cargo.toml", "Cargo.lock"):
            shutil.copyfile(checker.ROOT / name, self.root / name)
        for directory in NAMES:
            dest = self.root / "crates" / directory
            dest.mkdir(parents=True)
            shutil.copyfile(checker.ROOT / "crates" / directory / "Cargo.toml", dest / "Cargo.toml")

    def validate(self):
        self.assertTrue(callable(getattr(checker, "check_namespace", None)), "namespace validator missing")
        return checker.check_namespace(self.root)

    def replace(self, relative, before, after):
        path = self.root / relative
        text = path.read_text()
        self.assertIn(before, text)
        path.write_text(text.replace(before, after))

    def test_valid_namespace(self):
        self.assertEqual(self.validate(), [])

    def test_wrong_package_rejected(self):
        path = self.root / "crates/storage-io/Cargo.toml"
        old = tomllib.loads(path.read_text())["package"]["name"]
        self.replace(path.relative_to(self.root), f'name = "{old}"', 'name = "unexpected-storage"')
        self.assertTrue(any("package name" in error for error in self.validate()))

    def test_duplicate_workspace_member_rejected(self):
        self.replace("Cargo.toml", '    "crates/storage-io",', '    "crates/storage-io",\n    "crates/storage-io",')
        self.assertTrue(any("workspace membership" in error for error in self.validate()))

    def test_publish_cannot_be_enabled(self):
        self.replace("Cargo.toml", "publish = false", "publish = true")
        self.assertTrue(any("publish" in error for error in self.validate()))

    def test_stale_lock_name_rejected(self):
        path = self.root / "Cargo.lock"
        text = path.read_text()
        # Deliberately mutate one local lock entry, not a registry package.
        name = next(p["name"] for p in tomllib.loads(text)["package"] if "source" not in p)
        self.replace("Cargo.lock", f'name = "{name}"', 'name = "stale-local-name"')
        self.assertTrue(any("lockfile" in error for error in self.validate()))

    def metadata(self):
        return {
            "workspace_members": list(NAMES.values()),
            "packages": [
                {"id": name, "name": name, "source": None, "publish": [],
                 "manifest_path": str(checker.ROOT / "crates" / directory / "Cargo.toml"),
                 "targets": [{"kind": ["lib"], "name": name.replace("-", "_")}]}
                for directory, name in NAMES.items()
            ],
        }

    def validate_metadata(self, metadata):
        self.assertTrue(callable(getattr(checker, "check_cargo_metadata", None)), "Cargo metadata validator missing")
        return checker.check_cargo_metadata(metadata, checker.ROOT)

    def test_cargo_metadata_public_imports(self):
        self.assertEqual(self.validate_metadata(self.metadata()), [])

    def test_cargo_metadata_rejects_legacy_library_name(self):
        metadata = self.metadata()
        metadata["packages"][0]["targets"][0]["name"] = "storage_io"
        self.assertTrue(any("library target" in error for error in self.validate_metadata(metadata)))

    def test_cargo_metadata_rejects_nonworkspace_member(self):
        metadata = self.metadata()
        metadata["workspace_members"].pop()
        self.assertTrue(any("workspace members" in error for error in self.validate_metadata(metadata)))

    def test_cargo_metadata_rejects_wrong_manifest(self):
        metadata = self.metadata()
        metadata["packages"][0]["manifest_path"] = str(checker.ROOT / "other/Cargo.toml")
        self.assertTrue(any("manifest path" in error for error in self.validate_metadata(metadata)))


if __name__ == "__main__":
    unittest.main()
