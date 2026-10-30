"""Independent readout engine for the balanced 60-family overwrite cohort.

The tested schedule runner supplies fitting, resumption, immutable publication
and exact score/metric replay. An isolated module supplies the new source role,
strict source/capture hooks and explicit cohort constants. Existing schedule
modules, frozen snapshots and scientific artifacts are never mutated.
"""
from __future__ import annotations

import importlib.util
import sys

from . import schedule_readouts as original

ROLE = 'discovery_diversity_readouts_v1'
SOURCE_ROWS = 5760
TRAIN_ROWS = 4320
DEV_ROWS = 1440
TRAIN_GROUPS = 45
DEV_GROUPS = 15


def _targets():
    from . import diversity_targets
    return diversity_targets


def _capture():
    from . import diversity_capture
    return diversity_capture


def _isolated_engine():
    name = __package__+'._diversity_readout_engine'
    spec = importlib.util.spec_from_file_location(name, original.__file__)
    if spec is None or spec.loader is None:
        raise ValueError('tested schedule readout engine is unavailable')
    engine = importlib.util.module_from_spec(spec)
    sys.modules[name] = engine
    spec.loader.exec_module(engine)
    engine.ROLE = ROLE
    for field in ('SOURCE_ROWS','TRAIN_ROWS','DEV_ROWS','TRAIN_GROUPS','DEV_GROUPS'):
        setattr(engine,field,globals()[field])
    engine.COHORT_DESCRIPTION = '5,760 source cases; 45 TRAIN and 15 DEV canonical graph families.'
    engine.COHORT_ERROR = '45 TRAIN and 15 DEV disjoint graph families required'
    engine.PROTOCOL_INTERVAL = 'none; all 15 development graph outcomes retained'
    engine.SUMMARY_AGGREGATION = 'Mean of three weighting-seed point estimates; 15 dependent DEV graph families; no interval or reliability qualification.'
    engine.LIMITATIONS = list(original.LIMITATIONS)
    engine.LIMITATIONS[0] = 'Adaptive discovery on 60 canonical SSA graph families: 45 TRAIN and 15 DEV, each containing 96 dependent source rows; numeric, lexical and query relatives are dependent.'
    engine.LIMITATIONS[8] = 'Point estimates and all 15 DEV graph outcomes are descriptive; no confirmatory or multiplicity-adjusted interval is claimed.'
    # Per-case prefix/version metadata scales with source rows. Compact summary,
    # audit and completion files remain small; the rich result has its own bound.
    engine.MAX_RESULT = 192 * 1024**2
    engine._targets = _targets
    engine._capture = _capture
    return engine


_CORE = _isolated_engine()
SITES = _CORE.SITES
SEEDS = _CORE.SEEDS
MAX_RESULT = _CORE.MAX_RESULT
LIMITATIONS = _CORE.LIMITATIONS
COMPLETION = _CORE.COMPLETION
protocol = _CORE.protocol
preflight = _CORE.preflight
run = _CORE.run
audit = _CORE.audit
completed_result = _CORE.completed_result
_config = _CORE._config
_metadata = _CORE._metadata
_bundles = _CORE._bundles
_summary = _CORE._summary
_report = _CORE._report
fit_masked_columns = _CORE.fit_masked_columns
metrics = _CORE.metrics
