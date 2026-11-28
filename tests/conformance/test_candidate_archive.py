import hashlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from candidate_archive import verify_candidate, retain_candidate


def sha(data):
    return hashlib.sha256(data).hexdigest()


def case(members, extra=()):
    manifest = ''.join(f'{sha(data)}  {name}\n' for name, data in members.items()).encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for name, data in [*members.items(), *extra, ('SHA256SUMS', manifest)]:
            z.writestr(name, data)
    data = out.getvalue()
    pin = {'archive_sha256': sha(data), 'manifest_sha256': sha(manifest),
           'images': {'fixture.img': {'fixture_sha256': sha(members['fixture.img']),
                                     'oracle_sha256': sha(members['fixture.img-oracle.json']),
                                     'oracle_member': 'fixture.img-oracle.json'}}}
    return data, pin


class CandidateArchiveTests(unittest.TestCase):
    def setUp(self):
        self.data, self.pin = case({'fixture.img': b'fixture', 'fixture.img-oracle.json': b'{}'})

    def test_verified_mapping_does_not_claim_admission(self):
        result = verify_candidate(self.data, self.pin)
        self.assertEqual(result['status'], 'candidate_integrity_only')
        self.assertEqual(result['fixture_and_oracle']['fixture.img'], {
            'kind': 'specified', 'fixture_sha256': sha(b'fixture'), 'oracle_sha256': sha(b'{}')})

    def test_archive_and_manifest_pins_are_external(self):
        with self.assertRaises(ValueError):
            verify_candidate(self.data + b'changed', self.pin)
        with self.assertRaises(ValueError):
            verify_candidate(self.data, dict(self.pin, manifest_sha256='0'*64))

    def test_unlisted_member_rejected_even_with_matching_archive_pin(self):
        data, pin = case({'fixture.img': b'fixture', 'fixture.img-oracle.json': b'{}'}, [('extra.txt', b'X')])
        with self.assertRaises(ValueError):
            verify_candidate(data, pin)

    def test_path_traversal_member_rejected(self):
        data, pin = case({'fixture.img': b'fixture', 'fixture.img-oracle.json': b'{}', '../outside': b'X'})
        with self.assertRaises(ValueError):
            verify_candidate(data, pin)

    def test_oracle_pin_cannot_be_substituted(self):
        self.pin['images']['fixture.img']['oracle_sha256'] = '0'*64
        with self.assertRaises(ValueError):
            verify_candidate(self.data, self.pin)

    def test_retain_verified_bytes_by_digest_without_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            p = retain_candidate(self.data, self.pin, root)
            self.assertEqual(p.name, sha(self.data) + '.zip')
            self.assertEqual(p.read_bytes(), self.data)
            self.assertEqual(retain_candidate(self.data, self.pin, root), p)
            p.write_bytes(b'wrong')
            with self.assertRaises(ValueError):
                retain_candidate(self.data, self.pin, root)
            self.assertEqual(p.read_bytes(), b'wrong')

    def test_bad_candidate_leaves_store_untouched(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            with self.assertRaises(ValueError):
                retain_candidate(self.data + b'changed', self.pin, root)
            self.assertEqual(list(root.iterdir()), [])
