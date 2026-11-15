"""Synthetic checkpoint-matching tests, never native or authenticated receipts."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from conductor_graph import load_catalog

T1 = 'track-001-workspace-and-core-traits'
T6 = 'track-006-conformance-and-release'


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('conductor_evidence'), 'scoped checkpoint matcher missing')
        import conductor_evidence
        self.api = conductor_evidence
        self.catalog = load_catalog(ROOT)
        self.subject = {'kind': 'profile', 'id': 'apfs-image-read-mount'}
        # Artificial metadata for unit tests. No execution or provenance is claimed.
        self.scope = {
            'source_tree': 'a' * 40,
            'contract_revision': 'b' * 64,
            'dependency_lock_and_features': {'lock_sha256': 'c' * 64, 'features': [], 'toolchain': 'synthetic-rust'},
            'target_and_os': {'target': 'synthetic-linux-target', 'os': 'synthetic-os'},
            'runtime_or_driver_when_applicable': {'kind': 'specified', 'identity': 'synthetic-driver'},
            'fixture_and_oracle': {'kind': 'specified', 'fixture_sha256': 'd' * 64, 'oracle_sha256': 'e' * 64},
            'operation_and_view_mode': {'operation': 'read', 'view_mode': 'immutable-image'},
            'fault_model_when_applicable': {'kind': 'not_applicable', 'reason': 'synthetic read-only matching test'},
        }
        self.gates = self.api.required_phases(self.catalog, self.subject)
        self.bundle = {'schema_version': 1, 'checkpoints': [
            {'phase': gate, 'scope': copy.deepcopy(self.scope), 'result': 'passed',
             'evidence_kind': 'executed', 'review_status': 'accepted',
             'review_reference': 'synthetic-review-not-an-approval',
             'evidence_reference': 'synthetic-evidence-not-an-execution'}
            for gate in self.gates
        ]}
        self.request = {
            'schema_version': 1, 'catalog_sha256': self.api.catalog_digest(self.catalog),
            'subject': self.subject,
            'requirements': [{'phase': r['phase'], 'scope': copy.deepcopy(self.scope),
                              'checkpoint_sha256': self.api.checkpoint_digest(r)}
                             for r in self.bundle['checkpoints']],
        }

    def match(self):
        return self.api.match_checkpoints(self.catalog, self.request, self.bundle)

    def repin_first(self):
        # Isolate scope/status validation from the independent digest-tamper test.
        self.request['requirements'][0]['checkpoint_sha256'] = self.api.checkpoint_digest(self.bundle['checkpoints'][0])

    def reject(self, fragment):
        with self.assertRaisesRegex(ValueError, fragment):
            self.match()

    def test_current_matching_profile_returns_metadata_only(self):
        result = self.match()
        self.assertEqual(result.assurance, 'declared_scope_only')
        self.assertEqual(result.matched_phases, self.gates)
        self.assertGreater(len(self.gates), len(self.catalog.profiles[self.subject['id']]))

    def test_phase_request_checks_ancestors_not_its_own_completion(self):
        self.subject.update(kind='phase', id=T6 + '#p1')
        self.gates = self.api.required_phases(self.catalog, self.subject)
        self.assertEqual(set(self.gates), {T1 + '#p1', T1 + '#r0'})
        self.bundle['checkpoints'] = [r for r in self.bundle['checkpoints'] if r['phase'] in self.gates]
        self.request['requirements'] = [r for r in self.request['requirements'] if r['phase'] in self.gates]
        self.assertEqual(set(self.match().matched_phases), set(self.gates))

    def test_historical_pass_cannot_promote_current_profile(self):
        self.bundle['checkpoints'][0]['evidence_kind'] = 'historical'
        self.repin_first()
        self.reject('executed')

    def test_different_target_or_mode_cannot_satisfy_edge(self):
        for key, field, value in [('target_and_os', 'target', 'synthetic-windows-target'),
                                  ('operation_and_view_mode', 'view_mode', 'direct-write')]:
            with self.subTest(key=key):
                original = copy.deepcopy(self.bundle['checkpoints'][0])
                self.bundle['checkpoints'][0]['scope'][key][field] = value
                self.repin_first()
                self.reject('scope mismatch')
                self.bundle['checkpoints'][0] = original
                self.repin_first()

    def test_every_dimension_and_contract_revision_must_match(self):
        changes = {
            'source_tree': 'f' * 40, 'contract_revision': 'f' * 64,
            'dependency_lock_and_features': {'lock_sha256': 'f' * 64, 'features': ['writer'], 'toolchain': 'other'},
            'target_and_os': {'target': 'other', 'os': 'other'},
            'runtime_or_driver_when_applicable': {'kind': 'specified', 'identity': 'other'},
            'fixture_and_oracle': {'kind': 'specified', 'fixture_sha256': 'f' * 64, 'oracle_sha256': 'f' * 64},
            'operation_and_view_mode': {'operation': 'write', 'view_mode': 'live'},
            'fault_model_when_applicable': {'kind': 'specified', 'model_sha256': 'f' * 64},
        }
        for key, value in changes.items():
            with self.subTest(key=key):
                original = copy.deepcopy(self.bundle['checkpoints'][0]['scope'][key])
                self.bundle['checkpoints'][0]['scope'][key] = value
                self.repin_first()
                self.reject('scope mismatch')
                self.bundle['checkpoints'][0]['scope'][key] = original
                self.repin_first()

    def test_one_host_can_match_while_other_host_lanes_remain_pending(self):
        self.assertEqual(self.match().assurance, 'declared_scope_only')
        self.assertTrue(all(r['scope']['target_and_os']['target'] == 'synthetic-linux-target'
                            for r in self.bundle['checkpoints']))
        # The actual planning profiles remain not_qualified; no status is consulted.
        self.assertNotIn('status', self.catalog.__dict__)

    def test_missing_receipt_rejected(self):
        self.bundle['checkpoints'].pop()
        self.reject('checkpoint set')

    def test_missing_transitive_requirement_rejected(self):
        index = next(i for i, r in enumerate(self.request['requirements']) if r['phase'] == T1 + '#p1')
        self.request['requirements'].pop(index)
        self.reject('requirement set')

    def test_empty_receipts_cannot_use_historical_phase_status(self):
        self.bundle['checkpoints'] = []
        self.reject('checkpoint set')

    def test_duplicate_receipt_rejected(self):
        self.bundle['checkpoints'].append(self.bundle['checkpoints'][0])
        self.reject('duplicate phase')

    def test_duplicate_requirement_rejected(self):
        self.request['requirements'].append(self.request['requirements'][0])
        self.reject('duplicate phase')

    def test_unknown_subject_rejected(self):
        self.subject['id'] = 'missing-profile'
        self.reject('unknown profile')

    def test_replaced_receipt_rejected_by_pinned_digest(self):
        self.bundle['checkpoints'][0]['evidence_reference'] = 'substituted-evidence'
        self.reject('checkpoint digest')

    def test_unaccepted_or_failed_receipts_rejected(self):
        for key, value, fragment in [('review_status', 'pending', 'accepted'), ('result', 'failed', 'passed'),
                                     ('result', 'skipped', 'passed')]:
            with self.subTest(key=key, value=value):
                old = self.bundle['checkpoints'][0][key]
                self.bundle['checkpoints'][0][key] = value
                self.repin_first()
                self.reject(fragment)
                self.bundle['checkpoints'][0][key] = old
                self.repin_first()

    def test_catalog_revision_must_match(self):
        self.request['catalog_sha256'] = 'f' * 64
        self.reject('catalog digest')

    def test_required_scope_field_cannot_be_omitted(self):
        self.request['requirements'][0]['scope'].pop('contract_revision')
        self.reject('scope fields')

    def test_inapplicable_is_explicit_not_null_or_wildcard(self):
        for value in (None, '*', {'kind': 'not_applicable', 'reason': ''}):
            with self.subTest(value=value):
                self.request['requirements'][0]['scope']['fault_model_when_applicable'] = value
                self.reject('fault_model_when_applicable')

    def test_schema_version_is_not_boolean(self):
        self.request['schema_version'] = True
        self.reject('schema_version')

    def test_unknown_receipt_fields_rejected(self):
        self.bundle['checkpoints'][0]['qualified'] = True
        self.reject('checkpoint fields')

    def test_features_require_unique_canonical_strings(self):
        self.request['requirements'][0]['scope']['dependency_lock_and_features']['features'] = ['z', 'a', 'a']
        self.reject('features')

    def test_malformed_json_has_nonzero_cli_result(self):
        with tempfile.TemporaryDirectory() as directory:
            request, evidence = Path(directory) / 'request.json', Path(directory) / 'evidence.json'
            request.write_text('{"schema_version":1,"schema_version":1}', encoding='utf-8')
            evidence.write_text(json.dumps(self.bundle), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/conductor_evidence.py'),
                                     '--request', str(request), '--evidence', str(evidence)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('duplicate JSON key', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_prerequisite_roles_can_have_different_explicit_scopes(self):
        receipt = self.bundle['checkpoints'][0]
        receipt['scope']['fixture_and_oracle'] = {'kind': 'not_applicable', 'reason': 'core interface checkpoint'}
        receipt['scope']['operation_and_view_mode'] = {'operation': 'core-contract-tests', 'view_mode': 'none'}
        self.request['requirements'][0]['scope'] = copy.deepcopy(receipt['scope'])
        self.repin_first()
        self.assertEqual(self.match().assurance, 'declared_scope_only')

    def test_source_or_contract_digest_cannot_be_abbreviated(self):
        for field in ('source_tree', 'contract_revision'):
            with self.subTest(field=field):
                original = self.request['requirements'][0]['scope'][field]
                self.request['requirements'][0]['scope'][field] = 'abcdef0'
                self.reject('full lowercase digest')
                self.request['requirements'][0]['scope'][field] = original

    def test_unknown_or_extra_checkpoint_is_not_silently_ignored(self):
        receipt = copy.deepcopy(self.bundle['checkpoints'][0])
        receipt['phase'] = 'other-track#p1'
        self.bundle['checkpoints'].append(receipt)
        self.reject('checkpoint set')

    def test_cli_matching_reports_only_declared_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            request, evidence = Path(directory) / 'request.json', Path(directory) / 'evidence.json'
            request.write_text(json.dumps(self.request), encoding='utf-8')
            evidence.write_text(json.dumps(self.bundle), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/conductor_evidence.py'),
                                     '--request', str(request), '--evidence', str(evidence)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('declared_scope_only', result.stdout)
            self.assertIn('not runtime qualification', result.stdout)


if __name__ == '__main__':
    unittest.main()
