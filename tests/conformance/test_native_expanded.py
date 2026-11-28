import tempfile
import unittest
from pathlib import Path

from native_oracle import populate, observe, check_raw_gpt


class ExpandedFixtureTests(unittest.TestCase):
    def test_expanded_profile_preserves_baseline_and_checks_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            populate(root, 'expanded')
            sizes = {r['name']: r['size'] for r in observe(root, 'expanded')}
            self.assertEqual(sizes, {'empty.txt': 0, 'hello.txt': 22, '\u4e2d.txt': 3,
                                     '4095.bin': 4095, '4096.bin': 4096, '4097.bin': 4097})
            with self.assertRaises(ValueError):
                observe(root)
            (root / 'example' / '4097.bin').write_bytes(b'X' * 4097)
            with self.assertRaises(ValueError):
                observe(root, 'expanded')

    def test_raw_gpt_cross_checks_native_offsets_and_signatures(self):
        # Synthetic structural test, not native APFS evidence.
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'test.cdr'
            data = bytearray(10 * 512)
            data[512:520] = b'EFI PART'
            data[9*512:9*512+8] = b'EFI PART'
            data[4*512+32:4*512+36] = b'NXSB'
            image.write_bytes(data)
            listing = ('1 1 Pri GPT header\n4 3 1 GPT part - '
                       '7C3457EF-0000-11AA-AA11-00306543ECAC\n9 1 Sec GPT header\n')
            self.assertEqual(check_raw_gpt(image, listing),
                             {'sector_size': 512, 'image_bytes': 5120,
                              'partition_start_bytes': 2048, 'partition_bytes': 1536})
            for changed in (listing.replace('9 1 Sec', '8 1 Sec'),
                            listing.replace('4 3 1', '4 7 1'),
                            listing.replace('4 3 1', '5 3 1')):
                with self.assertRaises(ValueError):
                    check_raw_gpt(image, changed)
            data[512] ^= 1
            image.write_bytes(data)
            with self.assertRaises(ValueError):
                check_raw_gpt(image, listing)
