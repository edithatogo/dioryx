import tempfile
import unittest
from pathlib import Path

from native_oracle import populate, observe


class NativeOracleTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.mount = Path(directory.name)
        populate(self.mount)

    def test_known_bytes_and_os_metadata(self):
        result = observe(self.mount)
        self.assertEqual([item['name'] for item in result], ['empty.txt', 'hello.txt'])
        self.assertEqual(result[0]['size'], 0)
        self.assertEqual(result[1]['sha256'], 'c25b540364225542c5597358145ea71cf6427e66f6abc9e382bfc51740de2adc')
        self.assertEqual(result[1]['os_name_hex'], '68656c6c6f2e747874')
        self.assertIsInstance(result[1]['os_mtime_ns'], int)

    def test_changed_same_length_payload_rejected(self):
        (self.mount / 'example' / 'hello.txt').write_bytes(b'X' * len(b'Dioryx native fixture\n'))
        with self.assertRaises(ValueError):
            observe(self.mount)

    def test_missing_or_extra_file_rejected(self):
        (self.mount / 'example' / 'empty.txt').unlink()
        with self.assertRaises(ValueError):
            observe(self.mount)
        (self.mount / 'example' / 'empty.txt').touch()
        (self.mount / 'example' / 'extra.txt').touch()
        with self.assertRaises(ValueError):
            observe(self.mount)

    def test_nonregular_entry_rejected(self):
        (self.mount / 'example' / 'empty.txt').unlink()
        (self.mount / 'example' / 'empty.txt').mkdir()
        with self.assertRaises(ValueError):
            observe(self.mount)
