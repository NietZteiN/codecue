"""Isolated adapter of the audited resumable prefill capture engine."""
from copy import deepcopy
import importlib.util
from pathlib import Path

from . import overnight_relationship_capture as durable, arithmetic_graph_programs as programs

ROLE = 'discovery_arithmetic_graph_capture_v1'
spec = importlib.util.spec_from_file_location(__package__+'._arithmetic_capture_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.DATASET_ROLE = programs.ROLE
_CORE.PROFILES = deepcopy(durable.PROFILES)
_CORE.RECORD_FIELDS = (*durable.RECORD_FIELDS, 'operation_family')
_old_config = _CORE._config
_old_dataset = _CORE._dataset


def _config(config):
    checksum = config.get('dataset_manifest_sha256', '')
    if len(checksum) != 64 or any(c not in '0123456789abcdef' for c in checksum):
        raise ValueError('pinned arithmetic dataset manifest required')
    return _old_config({k: v for k, v in config.items() if k != 'dataset_manifest_sha256'})


def _validate_row(row):
    if row.get('evaluation_role') != programs.ROLE or row.get('condition') != 'neutral':
        raise ValueError('neutral arithmetic discovery rows required')
    if row.get('variable_slots') != programs.SLOTS or row.get('query_slot') not in range(4):
        raise ValueError('four declared variable/query slots required')
    if programs.oracle(row['canonical_source']) != row['oracle']:
        raise ValueError('arithmetic provenance oracle differs')


def _dataset(config):
    _CORE._json(Path(config['dataset']).with_suffix('.manifest.json'), config['dataset_manifest_sha256'])
    rows, review = _old_dataset(config)
    programs.validate(rows, independent=False)
    return rows, review


_CORE._config, _CORE._validate_row, _CORE._dataset = _config, _validate_row, _dataset
metadata, prepare, run, audit = _CORE.metadata, _CORE.prepare, _CORE.run, _CORE.audit
inputs, completed_metadata, load_chunk = _CORE.inputs, _CORE.completed_metadata, _CORE.load_chunk
PROFILES = _CORE.PROFILES
