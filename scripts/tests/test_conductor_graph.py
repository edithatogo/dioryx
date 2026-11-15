"""Plan metadata regressions; no native disk images or qualification receipts."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
T1 = 'track-001-workspace-and-core-traits'
T2 = 'track-002-apfs-readonly-and-mount'
T6 = 'track-006-conformance-and-release'


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'conductor/tracks', self.root / 'conductor/tracks')

    def path(self, track=T1):
        return self.root / 'conductor/tracks' / track / 'metadata.json'

    def edit(self, mutation, track=T1):
        path = self.path(track)
        data = json.loads(path.read_text(encoding='utf-8'))
        mutation(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def validate(self):
        self.assertIsNotNone(importlib.util.find_spec('conductor_graph'), 'phase/profile validator missing')
        import conductor_graph
        return conductor_graph.check(self.root)

    def rejected(self, word):
        errors = self.validate()
        self.assertTrue(any(word in error for error in errors), errors)

    def test_actual_phase_profile_graph(self):
        self.assertEqual(self.validate(), [])
        from conductor_graph import load_catalog
        catalog = load_catalog(self.root)
        self.assertEqual(len(catalog.phases), 27)
        self.assertEqual(len(catalog.profiles), 8)

    def test_unknown_phase_rejected(self):
        self.edit(lambda d: d['phases'][1]['depends_on'].append(T1 + '#absent'))
        self.rejected('unknown phase')

    def test_phase_cycle_rejected(self):
        self.edit(lambda d: d['phases'][0]['depends_on'].append(T2 + '#p1'))
        self.rejected('phase cycle')

    def test_self_cycle_rejected(self):
        self.edit(lambda d: d['phases'][0]['depends_on'].append(T1 + '#p1'))
        self.rejected('phase cycle')

    def test_duplicate_phase_rejected(self):
        self.edit(lambda d: d['phases'].append(d['phases'][0]))
        self.rejected('duplicate phase')

    def test_duplicate_edge_rejected(self):
        self.edit(lambda d: d['phases'][1]['depends_on'].append(T1 + '#p1'))
        self.rejected('duplicate')

    def test_missing_edge_field_rejected(self):
        self.edit(lambda d: d['phases'][1].pop('depends_on'))
        self.rejected('phase fields')

    def test_malformed_phase_shapes_rejected(self):
        for value in (None, True, {}, ['bad']):
            with self.subTest(value=value):
                original = self.path().read_text(encoding='utf-8')
                self.edit(lambda d: d.update(phases=value))
                self.rejected('phase')
                self.path().write_text(original, encoding='utf-8')

    def test_unknown_status_rejected(self):
        self.edit(lambda d: d['phases'][0].update(status='pass-ish'))
        self.rejected('phase status')

    def test_profile_cannot_reference_missing_gate(self):
        self.edit(lambda d: d['qualification_profiles']['controlled-apfs-proof']['requires_phases'].append(T1 + '#absent'), T6)
        self.rejected('unknown phase')

    def test_profile_cannot_drop_evidence_dimensions(self):
        self.edit(lambda d: d['qualification_profiles']['controlled-apfs-proof']['required_evidence_dimensions'].pop(), T6)
        self.rejected('evidence dimensions')

    def test_profile_cannot_have_empty_gates(self):
        self.edit(lambda d: d['qualification_profiles']['controlled-apfs-proof'].update(requires_phases=[]), T6)
        self.rejected('nonempty')

    def test_duplicate_profile_across_tracks_rejected(self):
        profiles = json.loads(self.path(T6).read_text())['qualification_profiles']
        self.edit(lambda d: d.update(qualification_profiles=profiles))
        self.rejected('duplicate profile')

    def test_static_profile_promotion_rejected(self):
        self.edit(lambda d: d['qualification_profiles']['controlled-apfs-proof'].update(status='qualified'), T6)
        self.rejected('not_qualified')

    def test_duplicate_json_key_rejected(self):
        text = self.path().read_text(encoding='utf-8')
        self.path().write_text(text.replace('{', '{"phases": [],', 1), encoding='utf-8')
        self.rejected('duplicate JSON key')

    def test_nonfinite_json_rejected(self):
        self.path().write_text('{"phases": NaN}', encoding='utf-8')
        self.rejected('non-finite')

    def test_track_directory_identity_rejected(self):
        self.edit(lambda d: d.update(track_id='other'))
        self.rejected('track ID')

    def test_missing_track_metadata_rejected(self):
        self.path(T2).unlink()
        self.rejected('metadata.json')

    def test_empty_registry_rejected(self):
        shutil.rmtree(self.root / 'conductor/tracks')
        (self.root / 'conductor/tracks').mkdir()
        self.rejected('no tracks')

    def test_plan_prerequisite_drift_rejected(self):
        path = self.path().with_name('plan.md')
        text = path.read_text(encoding='utf-8')
        text = text.replace('Prerequisites: `' + T1 + '#p1`.', 'Prerequisites: none.', 1)
        path.write_text(text, encoding='utf-8')
        self.rejected('plan prerequisites')

    def test_plan_phase_omission_rejected(self):
        path = self.path().with_name('plan.md')
        path.write_text(path.read_text(encoding='utf-8').replace('## r0 —', '## renamed —'), encoding='utf-8')
        self.rejected('plan phases')

    def test_contract_gate_includes_phase_validation(self):
        # Exercise the real top-level checker, not a mocked validator call.
        for path in ROOT.iterdir():
            if path.name in ('.git', 'conductor', 'target', 'artifacts'):
                continue
            target = self.root / path.name
            if path.is_dir():
                shutil.copytree(path, target, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            else:
                shutil.copyfile(path, target)
        for path in (ROOT / 'conductor').iterdir():
            if path.name == 'tracks':
                continue
            target = self.root / 'conductor' / path.name
            if path.is_dir():
                shutil.copytree(path, target)
            else:
                shutil.copyfile(path, target)
        self.edit(lambda d: d['phases'][1]['depends_on'].append(T1 + '#absent'))
        result = subprocess.run([sys.executable, str(self.root / 'scripts/check_contracts.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('unknown phase', result.stderr)

    def test_cli_rejects_malformed_metadata(self):
        self.assertTrue((ROOT / 'scripts/conductor_graph.py').exists(), 'phase/profile CLI missing')
        self.path().write_text('[]', encoding='utf-8')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/conductor_graph.py'), '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('ERROR:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
