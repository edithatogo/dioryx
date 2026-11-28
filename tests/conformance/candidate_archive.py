"""Verify and retain externally pinned native candidates; never admit a profile."""
import argparse
import hashlib
import io
import json
import os
import re
import stat
import tempfile
import zipfile
from pathlib import Path

# The present sparse/native baseline archives are small. Larger corpora need a
# reviewed streaming input path, not a silent increase to the compressed budget.
MAX_ARCHIVE = 8 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024
MAX_MANIFEST = 64 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_archive(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Candidate must be an authorised regular file')
    with path.open('rb') as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE:
        raise ValueError('Candidate exceeds compressed byte budget')
    return data


def verify_candidate(data, pin):
    """Use only pins from independently reviewed repository inputs, not the ZIP."""
    if len(data) > MAX_ARCHIVE or sha(data) != pin['archive_sha256']:
        raise ValueError('Candidate archive digest or byte budget mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        names = {entry.filename for entry in infos}
        if (len(infos) > 256 or len(names) != len(infos)
                or sum(entry.file_size for entry in infos) > MAX_EXPANDED
                or any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', entry.filename)
                       or entry.flag_bits & 1
                       or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG)
                       for entry in infos)):
            raise ValueError('Unsafe, duplicate or over-budget candidate members')
        if 'SHA256SUMS' not in names or archive.getinfo('SHA256SUMS').file_size > MAX_MANIFEST:
            raise ValueError('Missing or oversized manifest')
        manifest = archive.read('SHA256SUMS')
        if sha(manifest) != pin['manifest_sha256']:
            raise ValueError('Manifest differs from independently pinned bytes')
        hashes = {}
        for line in manifest.decode('ascii').splitlines():
            match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9_.-]{0,127})', line)
            if not match or match[2] in hashes:
                raise ValueError('Invalid or duplicate manifest entry')
            hashes[match[2]] = match[1]
        if set(hashes) != names - {'SHA256SUMS'}:
            raise ValueError('Manifest does not cover exact archive inventory')
        for name, expected in hashes.items():
            with archive.open(name) as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
                    raise ValueError(f'Member digest mismatch: {name}')
    scopes = {}
    for name, expected in pin['images'].items():
        if (hashes.get(name) != expected['fixture_sha256']
                or hashes.get(expected['oracle_member']) != expected['oracle_sha256']):
            raise ValueError('Fixture or oracle differs from independent pin')
        scopes[name] = {'kind': 'specified', 'fixture_sha256': expected['fixture_sha256'],
                        'oracle_sha256': expected['oracle_sha256']}
    if not scopes:
        raise ValueError('No independently pinned fixture/oracle pairs')
    return {'status': 'candidate_integrity_only', 'archive_sha256': pin['archive_sha256'],
            'members_verified': len(hashes), 'fixture_and_oracle': scopes}


def retain_candidate(data, pin, root):
    """Publish only verified bytes to a caller-owned store, without overwriting."""
    verify_candidate(data, pin)
    target = root / (pin['archive_sha256'] + '.zip')
    # Stage on the same filesystem and use an atomic, no-clobber hard link.
    # Storage without hard-link support fails rather than silently overwriting.
    with tempfile.TemporaryDirectory(dir=root) as scratch:
        staging = Path(scratch) / 'candidate.zip'
        with staging.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(staging, target)
        except FileExistsError:
            if read_archive(target) != data:
                raise ValueError('Existing checksum-addressed object differs')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    pins = json.loads((Path(__file__).resolve().parents[1] / 'fixtures' /
                       'candidate-pins.json').read_text(encoding='utf-8'))
    if pins['schema_version'] != 1:
        raise ValueError('Unsupported candidate pin schema')
    parser.add_argument('kind', choices=tuple(pins['candidates']))
    parser.add_argument('archive', type=Path)
    parser.add_argument('--retain-dir', type=Path)
    args = parser.parse_args()
    data, pin = read_archive(args.archive), pins['candidates'][args.kind]
    result = verify_candidate(data, pin)
    if args.retain_dir:
        result['retained_path'] = str(retain_candidate(data, pin, args.retain_dir))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
