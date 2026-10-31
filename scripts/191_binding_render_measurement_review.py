#!/usr/bin/env python
"""Repair table continuity in a new edition without changing diagnostic results."""
import hashlib
import json
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


if __name__ == '__main__':
    root = Path('artifacts/binding/arithmetic_state_diagnostics/20261031_v1')
    receipt = json.loads((root / 'completion_review_v1.json').read_text())
    entry = receipt['artifacts']['report']
    assert pin(entry['path'])['sha256'] == entry['sha256']
    original = Path(entry['path']).read_text().splitlines()
    header = next(line for line in original if line.startswith('| Model |'))
    separator = next(line for line in original if line.startswith('|---'))
    lines, in_table = [], False
    for line in original:
        if line.startswith('|') and not in_table and line != header:
            lines.extend([header, separator])
        lines.append(line)
        in_table = line.startswith('|')
    target = Path('reports/binding/arithmetic_measurement_diagnostics_v2.md')
    proof = root / 'render_review_v1.json'
    if target.exists() or proof.exists():
        raise ValueError('preserve existing render edition')
    target.write_text('\n'.join(lines).rstrip() + '\n')
    proof.write_text(json.dumps(dict(status='complete_exploratory', input=entry,
        output=pin(target), renderer=pin(__file__), scientific_changes=0,
        new_fits=0, new_model_queries=0), sort_keys=True, indent=2) + '\n')
