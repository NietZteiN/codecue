#!/usr/bin/env python
"""Audit prefix-visible discovery relationship labels without model access."""
import argparse
import json
from pathlib import Path

from codecue.binding.relationship_audit import run

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('config')
args = parser.parse_args()
path = Path(args.config)
if path.stat().st_size > 8*1024**2:
    raise ValueError('bounded relationship-audit configuration required')
result = run(json.loads(path.read_text()))
print(json.dumps({key: result[key] for key in ('status', 'rows', 'structural_groups',
    'nontrivial_current_slot_pair_cells', 'learned_relationship_decoder_fitted', 'new_model_queries')},
    sort_keys=True, indent=2))
