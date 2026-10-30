"""Frozen prefill capture adapter for the varied copy/overwrite source bank.

The durable overnight capture implementation is loaded into a private module
namespace. Only its role, source validation, record whitelist and configuration
entry points change. The imported legacy module and its globals remain untouched;
batching, selected-tensor transfers, prefix checks, model boundaries, journals,
recovery, chunk audits and completion receipts retain their tested implementation.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from . import overnight_relationship_capture as durable
from . import relationship_schedule_programs as programs
from . import relationships
from .datasets import digest
from .programs import rename

ROLE = 'discovery_schedule_capture_v1'
DATASET_ROLE = programs.ROLE
DATASET_SHA256 = '4021f720282fbd7b1344a4a92d5da02abf5269cd9b62d13eebbd5e40e2f4e287'
SOURCE_ROWS = 2016
SITES = durable.SITES
PROFILES = deepcopy(durable.PROFILES)
INSTRUCTION = durable.INSTRUCTION
RECORD_FIELDS = tuple(dict.fromkeys((*durable.RECORD_FIELDS,
    'paired_group_id', 'raw_template_id', 'schedule_id', 'schedule_kind', 'destination_schedule',
    'parent_pattern', 'copy_parent_slots', 'ordered_schedule_canonical_id',
    'ssa_graph_canonical_id', 'statement_spans')))


def _isolated_engine():
    spec = importlib.util.spec_from_file_location(__package__+'._schedule_capture_engine', durable.__file__)
    if spec is None or spec.loader is None: raise ValueError('durable capture implementation unavailable')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.ROLE = ROLE
    engine.DATASET_ROLE = DATASET_ROLE
    engine.PROFILES = deepcopy(PROFILES)
    engine.RECORD_FIELDS = RECORD_FIELDS
    # Tests and future adapters can isolate injectable dependencies too. Functions
    # retain their original modules; no shared base-module attribute is mutated.
    engine.base = SimpleNamespace(**vars(engine.base))
    return engine


_CORE = _isolated_engine()
_durable_config = _CORE._config
_durable_dataset = _CORE._dataset
_VALIDATED = {}


def _config(config):
    if not isinstance(config, dict) or 'dataset_manifest_sha256' not in config:
        raise ValueError('explicit pinned schedule dataset manifest required')
    checksum = config['dataset_manifest_sha256']
    if (not isinstance(checksum, str) or len(checksum) != 64
            or any(c not in '0123456789abcdef' for c in checksum)):
        raise ValueError('explicit schedule manifest SHA256 required')
    if config.get('dataset_sha256') != DATASET_SHA256:
        raise ValueError('exact frozen 2016-row schedule source bank required')
    if len(json.dumps(config, allow_nan=False).encode()) > 16*1024:
        raise ValueError('bounded complete schedule configuration required')
    for key in ('dataset', 'run_dir'):
        if not isinstance(config.get(key), str): raise ValueError('explicit schedule path strings required')
    trimmed = {key:value for key,value in config.items() if key != 'dataset_manifest_sha256'}
    recipe, folder = _durable_config(trimmed)
    if recipe['layers'] != PROFILES[recipe['model']]['layers']:
        raise ValueError('the four prospectively fixed schedule capture layers are required')
    dataset = Path(config['dataset']).resolve(); output = folder.resolve()
    for source in (dataset, dataset.with_suffix('.manifest.json')):
        if source == output or source in output.parents or output in source.parents:
            raise ValueError('schedule source files and capture directory cannot overlap')
    return recipe, folder


def _validate_row(row):
    if (not isinstance(row, dict) or row.get('evaluation_role') != DATASET_ROLE
            or row.get('split') not in ('train', 'development') or row.get('condition') != 'neutral'
            or row.get('source_form') != 'literal' or row.get('variable_slots') != programs.SLOTS):
        raise ValueError('neutral literal TRAIN/DEV schedule source rows required')
    for key in ('id', 'template_id', 'source', 'canonical_source', 'component_id'):
        if not isinstance(row.get(key), str) or not row[key] or len(row[key]) > 16384:
            raise ValueError('bounded complete schedule source identity required')
    if (row['component_id'] != row['template_id'] or row.get('cluster_id') != row['component_id']
            or row.get('ssa_graph_canonical_id') != row['component_id']
            or type(row.get('query_slot')) is not int or row['query_slot'] not in range(4)
            or row.get('query_role') != f"v{row['query_slot']}" or row.get('query_count') != 1):
        raise ValueError('actual schedule group and query identities required')
    mapping = row.get('rename_map')
    if (not isinstance(mapping, dict) or set(mapping) != set(programs.SLOTS)
            or len(set(mapping.values())) != 4):
        raise ValueError('bijective canonical/surface schedule names required')
    canonical = relationships._tree(row['canonical_source'])
    surface = relationships._tree(row['source'])
    if (len(row['source'].splitlines()) != 9 or len(canonical.body) != 9
            or ast.dump(ast.parse(rename(row['canonical_source'], mapping))) != ast.dump(surface)):
        raise ValueError('eight single-line assignments and an exact renamed query required')
    assignments = canonical.body[:-1]
    for i, node in enumerate(assignments):
        if (not isinstance(node, ast.Assign) or len(node.targets) != 1
                or not isinstance(node.targets[0], ast.Name) or node.targets[0].id not in programs.SLOTS):
            raise ValueError('eight actual four-slot assignments required')
        if i < 4:
            value = node.value.operand if isinstance(node.value, ast.UnaryOp) and isinstance(node.value.op, ast.USub) else node.value
            if (node.targets[0].id != f'v{i}' or not isinstance(value, ast.Constant)
                    or type(value.value) is not int):
                raise ValueError('four literal initial roots required')
        elif (not isinstance(node.value, ast.Name) or node.value.id not in programs.SLOTS
                or node.value.id == node.targets[0].id):
            raise ValueError('four declared distinct-slot copies required')
    destinations = [programs.SLOTS[node.targets[0].id] for node in assignments[4:]]
    parents = [programs.SLOTS[node.value.id] for node in assignments[4:]]
    if (destinations != row.get('destination_schedule') or parents != row.get('copy_parent_slots')
            or row.get('parent_pattern') not in programs.PARENT_PATTERNS
            or destinations not in [list(item) for item in (*programs.SLOT_PERMUTATIONS, *programs.REPEATED_SCHEDULES)]
            or parents != [(slot + programs.PARENT_PATTERNS[row['parent_pattern']]) % 4 for slot in destinations]):
        raise ValueError('actual source destinations/parents differ from registered schedule')
    query = canonical.body[-1]
    if not isinstance(query, ast.Expr) or not isinstance(query.value, ast.Name) or query.value.id != row['query_role']:
        raise ValueError('actual final schedule query differs')
    labels = relationships.labels_at(row['canonical_source'], 7, programs.SLOTS)
    graph, _ = programs._canonical_graph(labels)
    if 'schedule-graph:'+digest(graph)[:24] != row['component_id']:
        raise ValueError('actual SSA graph differs from registered canonical family')


def _dataset(config):
    _config(config)
    manifest_path = Path(config['dataset']).with_suffix('.manifest.json')
    manifest = _CORE._json(manifest_path, config['dataset_manifest_sha256'])
    if (manifest.get('learned_readout_compatible') is not False or manifest.get('targets_prepared_only') is not True
            or manifest.get('rows') != SOURCE_ROWS
            or manifest.get('effective_canonical_graph_units') != 15
            or manifest.get('split_canonical_graph_units') != {'train':10, 'development':5}):
        raise ValueError('complete varied-schedule target preparation manifest required')
    rows, review = _durable_dataset(config)
    if (len(rows) != SOURCE_ROWS or review['components'] != {'train':10, 'development':5}
            or review['split_rows'] != {'train':1320, 'development':696}
            or review['dataset_manifest_sha256'] != config['dataset_manifest_sha256']):
        raise ValueError('exact grouped schedule cohort coverage required')
    key = (config['dataset_sha256'], config['dataset_manifest_sha256'])
    if key not in _VALIDATED:
        checked = programs.validate_rows(manifest['generation_config'], rows, independent=False)
        if (checked['cross_split_overlap'] != manifest['cross_split_overlap']
                or checked['effective_canonical_graph_units'] != 15
                or checked['maximum_assignment_version'] != 4):
            raise ValueError('schedule builder and generic prefix-label validation differ')
        _VALIDATED[key] = True
    review.update(raw_schedule_count=28, raw_schedule_parent_templates=84,
        effective_ordered_schedule_units=21, effective_canonical_graph_units=15,
        split_canonical_graph_units={'train':10,'development':5}, maximum_assignment_version=4,
        source_targets_prepared_only=True, existing_fixed_readouts_compatible=False,
        actual_generic_ssa_labels_validated=True)
    return rows, review


_CORE._config = _config
_CORE._validate_row = _validate_row
_CORE._dataset = _dataset

# Public compatibility surface. Each durable function resolves its private
# engine globals, including the schedule-specific validators above.
metadata = _CORE.metadata
prepare = _CORE.prepare
run = _CORE.run
audit = _CORE.audit
completed_metadata = _CORE.completed_metadata
inputs = _CORE.inputs
load_chunk = _CORE.load_chunk
validate_chunk = _CORE.validate_chunk
layout_case = _CORE.layout_case
memory_requirements = _CORE.memory_requirements
_json = _CORE._json
