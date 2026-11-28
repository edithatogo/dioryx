"""Known-answer native mount observations, not on-disk parsing or admission."""
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

PAYLOADS = {'hello.txt': b'Dioryx native fixture\n', 'empty.txt': b''}


def populate(mount: Path) -> None:
    example = mount / 'example'
    example.mkdir()
    for name, data in PAYLOADS.items():
        with (example / name).open('xb') as stream:
            stream.write(data)


def observe(mount: Path) -> list[dict]:
    example = mount / 'example'
    if not stat.S_ISDIR(example.lstat().st_mode) or set(os.listdir(example)) != set(PAYLOADS):
        raise ValueError('Unexpected known-answer subtree')
    result = []
    for name, expected in sorted(PAYLOADS.items()):
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


if __name__ == '__main__':
    action, mount = sys.argv[1:3]
    if action == 'populate' and len(sys.argv) == 3:
        populate(Path(mount))
    elif action == 'observe' and len(sys.argv) == 3:
        print(json.dumps(observe(Path(mount)), indent=2, sort_keys=True))
    else:
        raise SystemExit('Expected populate or observe and a disposable mount path')
