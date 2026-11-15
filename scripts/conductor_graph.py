#!/usr/bin/env python3
"""Validate Conductor planning structure; never infer runtime qualification."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import graphlib
import json
from pathlib import Path
import re
import sys

DIMENSIONS = frozenset({
    'source_tree', 'dependency_lock_and_features', 'target_and_os',
    'runtime_or_driver_when_applicable', 'fixture_and_oracle',
    'operation_and_view_mode', 'fault_model_when_applicable',
})
PHASE_FIELDS = frozenset({'id', 'name', 'status', 'depends_on', 'completion_policy'})
PROFILE_FIELDS = frozenset({'requires_phases', 'status', 'scope', 'required_evidence_dimensions'})
PHASE_STATUSES = frozenset({'pending', 'in_progress', 'blocked', 'complete', 'complete_historical'})


class ValidationError(ValueError):
    """Invalid or contradictory planning data, not a failed native test."""


@dataclass(frozen=True)
class Catalog:
    # Status is deliberately absent: it cannot be used as prerequisite evidence.
    phases: dict[str, tuple[str, ...]]
    profiles: dict[str, tuple[str, ...]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path: Path) -> object:
    def invalid_constant(value: str) -> None:
        raise ValidationError(f'non-finite JSON value: {value}')

    # Repository metadata only; limit accidental giant input before parsing.
    with path.open('rb') as stream:
        raw = stream.read(1024 * 1024 + 1)
    require(len(raw) <= 1024 * 1024, f'metadata exceeds 1 MiB: {path}')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def strings(value: object, label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    require(isinstance(value, list), f'{label} must be a list')
    require(all(isinstance(x, str) and x.strip() == x and x for x in value),
            f'{label} must contain nonempty strings')
    require(len(value) == len(set(value)), f'duplicate {label}')
    require(not nonempty or bool(value), f'{label} must be nonempty')
    return tuple(value)


def text(value: object, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f'{label} must be nonempty text')


def acyclic(graph: dict[str, tuple[str, ...]], label: str) -> None:
    for node, dependencies in graph.items():
        for dependency in dependencies:
            require(dependency in graph, f'unknown {label}: {node} -> {dependency}')
    try:
        tuple(graphlib.TopologicalSorter(graph).static_order())
    except graphlib.CycleError as error:
        raise ValidationError(f'{label} cycle: {error.args[1]}') from error


def plan_edges(path: Path, expected: dict[str, tuple[str, ...]]) -> None:
    content = path.read_text(encoding='utf-8')
    sections = re.split(r'^## ([pr][0-9]+) — [^\n]+\n', content, flags=re.MULTILINE)
    identifiers = sections[1::2]
    require(len(identifiers) == len(set(identifiers)) and set(identifiers) == set(expected),
            f'plan phases differ from metadata: {path}')
    for phase, body in zip(identifiers, sections[2::2]):
        matches = re.findall(r'^Prerequisites: ([^\n]+)\.$', body, flags=re.MULTILINE)
        require(len(matches) == 1, f'plan prerequisites missing/ambiguous: {path}#{phase}')
        line = matches[0]
        refs = re.findall(r'`([^`]+)`', line)
        if line == 'none':
            refs = []
        else:
            require(re.fullmatch(r'`[^`]+`(?:, `[^`]+`)*', line) is not None,
                    f'invalid plan prerequisites: {path}#{phase}')
        require(len(refs) == len(set(refs)) and set(refs) == set(expected[phase]),
                f'plan prerequisites differ from metadata: {path}#{phase}')


def load_catalog(root: Path) -> Catalog:
    directories = sorted(p for p in (root / 'conductor/tracks').iterdir() if p.is_dir())
    require(bool(directories), 'no tracks found')
    tracks, phases, profiles, plans = {}, {}, {}, {}
    for directory in directories:
        metadata = directory / 'metadata.json'
        item = read_json(metadata)
        require(isinstance(item, dict), f'track metadata must be an object: {metadata}')
        track = item.get('track_id')
        require(track == directory.name, f'track ID differs from directory: {metadata}')
        require(track not in tracks, f'duplicate track ID: {track}')
        tracks[track] = strings(item.get('dependencies'), 'track dependencies')
        values = item.get('phases')
        require(isinstance(values, list) and bool(values), f'phases must be a nonempty list: {track}')
        local = {}
        for value in values:
            require(isinstance(value, dict) and set(value) == PHASE_FIELDS,
                    f'phase fields differ from schema: {track}')
            name = value['id']
            require(isinstance(name, str) and re.fullmatch(r'[pr][0-9]+', name) is not None,
                    f'invalid phase ID: {track}')
            ref = f'{track}#{name}'
            require(ref not in phases, f'duplicate phase: {ref}')
            require(isinstance(value['status'], str) and value['status'] in PHASE_STATUSES,
                    f'invalid phase status: {ref}')
            text(value['name'], 'phase name')
            text(value['completion_policy'], 'phase completion_policy')
            phases[ref] = strings(value['depends_on'], 'phase dependencies')
            local[name] = phases[ref]
        plans[directory / 'plan.md'] = local
        values = item.get('qualification_profiles', {})
        require(isinstance(values, dict), f'qualification_profiles must be an object: {track}')
        for name, value in values.items():
            text(name, 'profile name')
            require(name not in profiles, f'duplicate profile: {name}')
            require(isinstance(value, dict) and set(value) == PROFILE_FIELDS,
                    f'profile fields differ from schema: {name}')
            require(value['status'] == 'not_qualified',
                    f'planning profile must remain not_qualified: {name}')
            text(value['scope'], 'profile scope')
            dimensions = strings(value['required_evidence_dimensions'], 'evidence dimensions')
            require(set(dimensions) == DIMENSIONS, f'evidence dimensions differ from required set: {name}')
            profiles[name] = strings(value['requires_phases'], 'profile gates', nonempty=True)
        for required in ('index.md', 'spec.md', 'plan.md'):
            require((directory / required).is_file(), f'missing track file: {directory / required}')
    require(bool(profiles), 'no qualification profiles found')
    acyclic(tracks, 'track')
    acyclic(phases, 'phase')
    for profile, gates in profiles.items():
        for gate in gates:
            require(gate in phases, f'unknown phase in profile {profile}: {gate}')
    for path, expected in plans.items():
        plan_edges(path, expected)
    return Catalog(phases, profiles)


def check(root: Path) -> list[str]:
    try:
        load_catalog(root)
    except (OSError, ValueError, RecursionError) as error:
        return [str(error)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check(args.root)
    if errors:
        for error in errors:
            print(f'ERROR: {error}', file=sys.stderr)
        return 1
    print('Conductor phase/profile structure: OK (no runtime qualification)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
