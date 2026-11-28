"""Known-answer native mount observations, not on-disk parsing or admission."""
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

PAYLOADS = {'hello.txt': b'Dioryx native fixture\n', 'empty.txt': b''}


EXPANDED = PAYLOADS | {'\u4e2d.txt': b'ok\n', **{f'{n}.bin': (bytes(range(256)) * 17)[:n] for n in (4095, 4096, 4097)}}


def payloads(profile):
    return {'baseline': PAYLOADS, 'expanded': EXPANDED}[profile]


def populate(mount: Path, profile='baseline') -> None:
    example = mount / 'example'
    example.mkdir()
    for name, data in payloads(profile).items():
        with (example / name).open('xb') as stream:
            stream.write(data)


def observe(mount: Path, profile='baseline') -> list[dict]:
    expected_files = payloads(profile)
    example = mount / 'example'
    if not stat.S_ISDIR(example.lstat().st_mode) or set(os.listdir(example)) != set(expected_files):
        raise ValueError('Unexpected known-answer subtree')
    result = []
    for name, expected in sorted(expected_files.items()):
        path = example / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size != len(expected):
            raise ValueError(f'Unexpected file type or size: {name}')
        with path.open('rb') as stream:
            observed = stream.read(len(expected) + 1)
        if observed != expected:
            raise ValueError(f'Known-answer content mismatch: {name}')
        result.append({'name': name, 'os_name_hex': os.fsencode(name).hex(),
                       'size': info.st_size, 'sha256': hashlib.sha256(observed).hexdigest(),
                       'os_mode': info.st_mode, 'os_mtime_ns': info.st_mtime_ns})
    return result


def check_raw_gpt(image, listing):
    """Cross-check native gpt show geometry against a controlled regular image.

    This is not a GPT parser or a CRC validator. The native tool supplies the
    partition map; signatures and bounds prevent a mere extension rename.
    """
    if not stat.S_ISREG(image.lstat().st_mode) or len(listing) > 65536:
        raise ValueError('Invalid fixture or native listing')
    size = image.stat().st_size
    if not 1024 <= size <= 512 * 1024 * 1024 or size % 512:
        raise ValueError('Unsupported raw fixture geometry')
    primary = re.findall(r'^\s*(\d+)\s+1\s+Pri GPT header\s*$', listing, re.M)
    backup = re.findall(r'^\s*(\d+)\s+1\s+Sec GPT header\s*$', listing, re.M)
    parts = re.findall(r'^\s*(\d+)\s+(\d+)\s+\d+\s+GPT part - (?:7C3457EF-0000-11AA-AA11-00306543ECAC|Apple_APFS|Apple APFS)\s*$', listing, re.M | re.I)
    if primary != ['1'] or backup != [str(size // 512 - 1)] or len(parts) != 1:
        raise ValueError('Expected one native APFS partition and both GPT headers')
    start, count = map(int, parts[0])
    if start <= 1 or count <= 0 or start + count >= size // 512:
        raise ValueError('Native partition outside raw image bounds')
    with image.open('rb') as stream:
        for offset, signature in ((512, b'EFI PART'), (size - 512, b'EFI PART'),
                                  (start * 512 + 32, b'NXSB')):
            stream.seek(offset)
            if stream.read(len(signature)) != signature:
                raise ValueError('Raw bytes disagree with native GPT geometry')
    return {'sector_size': 512, 'image_bytes': size,
            'partition_start_bytes': start * 512, 'partition_bytes': count * 512}


if __name__ == '__main__':
    action, path, *args = sys.argv[1:]
    if action == 'raw-gpt' and len(args) == 1:
        result = check_raw_gpt(Path(path), Path(args[0]).read_text(encoding='utf-8'))
        print(json.dumps(result, indent=2, sort_keys=True))
    elif action in ('populate', 'observe') and len(args) <= 1:
        profile = args[0] if args else 'baseline'
        if action == 'populate':
            populate(Path(path), profile)
        else:
            print(json.dumps(observe(Path(path), profile), indent=2, sort_keys=True))
    else:
        raise SystemExit('Expected populate/observe with a disposable mount or raw-gpt with image and listing')
