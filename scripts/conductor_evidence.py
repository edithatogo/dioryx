#!/usr/bin/env python3
"""Match caller-pinned checkpoint metadata; never authenticate native evidence."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

from conductor_graph import Catalog, DIMENSIONS, load_catalog, read_json, require, strings, text

SCOPE_FIELDS = DIMENSIONS | {'contract_revision'}
RECEIPT_FIELDS = frozenset({'phase', 'scope', 'result', 'evidence_kind', 'review_status',
                          'review_reference', 'evidence_reference'})


@dataclass(frozen=True)
class MatchResult:
    subject_kind: str
    subject_id: str
    matched_phases: tuple[str, ...]
    assurance: str = 'declared_scope_only'


def fields(value: object, expected: set | frozenset, label: str) -> dict:
    require(isinstance(value, dict) and set(value) == expected, f'{label} fields differ from schema')
    return value


def digest_string(value: object, label: str, lengths: tuple[int, ...] = (64,)) -> None:
    require(isinstance(value, str) and len(value) in lengths and
            re.fullmatch('[0-9a-f]+', value) is not None, f'{label} must be a full lowercase digest')


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=True, allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def checkpoint_digest(receipt: dict) -> str:
    """Canonical content pin, not a signature or proof that execution occurred."""
    return canonical_digest(receipt)


def catalog_digest(catalog: Catalog) -> str:
    """Bind graph topology; descriptive statuses cannot create acceptance."""
    return canonical_digest({
        'phases': {key: sorted(value) for key, value in catalog.phases.items()},
        'profiles': {key: sorted(value) for key, value in catalog.profiles.items()},
    })


def required_phases(catalog: Catalog, subject: dict) -> tuple[str, ...]:
    """Return all required ancestors; a phase request checks entry, not completion."""
    fields(subject, {'kind', 'id'}, 'subject')
    text(subject['id'], 'subject id')
    if subject['kind'] == 'profile':
        require(subject['id'] in catalog.profiles, f"unknown profile: {subject['id']}")
        pending = list(catalog.profiles[subject['id']])
    else:
        require(subject['kind'] == 'phase', 'subject kind must be phase or profile')
        require(subject['id'] in catalog.phases, f"unknown phase: {subject['id']}")
        pending = list(catalog.phases[subject['id']])
    required = set()
    while pending:
        phase = pending.pop()
        require(phase in catalog.phases, f'unknown prerequisite: {phase}')
        if phase not in required:
            required.add(phase)
            pending.extend(catalog.phases[phase])
    return tuple(sorted(required))


def applicable(value: object, label: str, specified: set[str]) -> None:
    require(isinstance(value, dict), f'{label} must explicitly specify applicability')
    if value.get('kind') == 'not_applicable':
        fields(value, {'kind', 'reason'}, label)
        text(value['reason'], f'{label} reason')
    else:
        fields(value, {'kind'} | specified, label)
        require(value['kind'] == 'specified', f'{label} kind must be specified or not_applicable')
        for name in specified:
            if name.endswith('_sha256'):
                digest_string(value[name], f'{label}.{name}')
            else:
                text(value[name], f'{label}.{name}')


def validate_scope(scope: object) -> None:
    scope = fields(scope, SCOPE_FIELDS, 'scope')
    digest_string(scope['source_tree'], 'source_tree', (40, 64))
    digest_string(scope['contract_revision'], 'contract_revision')
    dependency = fields(scope['dependency_lock_and_features'],
                        {'lock_sha256', 'features', 'toolchain'}, 'dependency_lock_and_features')
    digest_string(dependency['lock_sha256'], 'lock_sha256')
    features = strings(dependency['features'], 'features')
    require(list(features) == sorted(features), 'features must be canonically sorted')
    text(dependency['toolchain'], 'toolchain')
    target = fields(scope['target_and_os'], {'target', 'os'}, 'target_and_os')
    text(target['target'], 'target')
    text(target['os'], 'os')
    applicable(scope['runtime_or_driver_when_applicable'], 'runtime_or_driver_when_applicable', {'identity'})
    applicable(scope['fixture_and_oracle'], 'fixture_and_oracle', {'fixture_sha256', 'oracle_sha256'})
    mode = fields(scope['operation_and_view_mode'], {'operation', 'view_mode'}, 'operation_and_view_mode')
    text(mode['operation'], 'operation')
    text(mode['view_mode'], 'view_mode')
    applicable(scope['fault_model_when_applicable'], 'fault_model_when_applicable', {'model_sha256'})


def version(document: dict) -> None:
    require(type(document['schema_version']) is int and document['schema_version'] == 1,
            'schema_version must be integer 1')


def indexed(values: object, expected_fields: set | frozenset, label: str) -> dict[str, dict]:
    require(isinstance(values, list), f'{label} must be a list')
    result = {}
    for value in values:
        value = fields(value, expected_fields, label)
        text(value['phase'], f'{label} phase')
        require(value['phase'] not in result, f"duplicate phase in {label}: {value['phase']}")
        validate_scope(value['scope'])
        result[value['phase']] = value
    return result


def match_checkpoints(catalog: Catalog, request: dict, bundle: dict) -> MatchResult:
    """The caller supplies independently reviewed expectations and content pins.

    Exact matching cannot verify review authority, evidence provenance or native
    behavior. This function does not read sources, fetch URLs, or update statuses.
    Different prerequisite roles may have different explicitly requested scopes.
    """
    fields(request, {'schema_version', 'catalog_sha256', 'subject', 'requirements'}, 'request')
    fields(bundle, {'schema_version', 'checkpoints'}, 'bundle')
    version(request)
    version(bundle)
    digest_string(request['catalog_sha256'], 'catalog_sha256')
    require(request['catalog_sha256'] == catalog_digest(catalog), 'catalog digest mismatch')
    gates = required_phases(catalog, request['subject'])
    requirements = indexed(request['requirements'], {'phase', 'scope', 'checkpoint_sha256'}, 'requirement')
    require(set(requirements) == set(gates), 'requirement set differs from prerequisite closure')
    receipts = indexed(bundle['checkpoints'], RECEIPT_FIELDS, 'checkpoint')
    require(set(receipts) == set(gates), 'checkpoint set differs from prerequisite closure')
    for gate in gates:
        expected, receipt = requirements[gate], receipts[gate]
        digest_string(expected['checkpoint_sha256'], 'checkpoint_sha256')
        require(receipt['result'] == 'passed', f'checkpoint must have passed: {gate}')
        require(receipt['evidence_kind'] == 'executed', f'checkpoint must be executed, not historical: {gate}')
        require(receipt['review_status'] == 'accepted', f'checkpoint review must be accepted: {gate}')
        text(receipt['review_reference'], 'review_reference')
        text(receipt['evidence_reference'], 'evidence_reference')
        require(receipt['scope'] == expected['scope'], f'scope mismatch: {gate}')
        require(checkpoint_digest(receipt) == expected['checkpoint_sha256'], f'checkpoint digest mismatch: {gate}')
    return MatchResult(request['subject']['kind'], request['subject']['id'], gates)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = match_checkpoints(load_catalog(args.root), read_json(args.request), read_json(args.evidence))
    except (OSError, ValueError, RecursionError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    print(f'{result.assurance}: {len(result.matched_phases)} prerequisite checkpoints match; not runtime qualification')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
