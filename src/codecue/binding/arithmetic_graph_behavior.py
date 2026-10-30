"""Same-prompt generated-answer controls for the arithmetic graph cohort."""
from collections import defaultdict
import importlib.util
import numpy as np

from . import overnight_relationship_behavior as durable, arithmetic_graph_capture as capture

ROLE = 'discovery_arithmetic_graph_behavior_v1'
spec = importlib.util.spec_from_file_location(__package__+'._arithmetic_behavior_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE, _CORE.capture = ROLE, capture._CORE
_CORE.LIMITATION = 'Adaptive discovery on two-input arithmetic programs. Numeric, lexical and query relatives are dependent. No causal or confirmatory claim.'
_CORE.REPORT_TITLE = 'Two-input arithmetic generated answers'
_CORE.COMPARISON_LABEL = 'DEV family accuracy uncertainty'


def protocol():
    return dict(selection='all source rows with numeric_draw == 0', do_sample=False,
                max_new_tokens=12, use_cache=True,
                parser='full signed decimal integer with whitespace only',
                uncertainty='12 whole development structural families; fixed fits, 2000 draws, seed117')


def summarize(rows):
    cells = defaultdict(list)
    grouped = defaultdict(list)
    for row in rows:
        for name in ('overall', 'split/'+row['split'], 'query/'+str(row['query_slot'])):
            cells[name].append(row)
        if row['split'] == 'development':
            grouped[row['component_id']].append(row['correct'])
    metrics = {k: dict(rows=len(v), accuracy=sum(r['correct'] for r in v)/len(v),
                      invalid_fraction=sum(r['parsed'] is None for r in v)/len(v)) for k, v in cells.items()}
    comparison = None
    if grouped:
        means = np.asarray([np.mean(grouped[k]) for k in sorted(grouped)])
        draws = np.random.default_rng(117).integers(0, len(means), (2000, len(means)))
        comparison = dict(accuracy=float(means.mean()), families=len(means),
                          conditional_family_bootstrap_95=np.quantile(means[draws].mean(axis=1), [.025, .975]).tolist())
    # Retain this schema key for the shared publisher; the overridden label and
    # protocol explicitly identify a family interval, not a format contrast.
    return dict(cells=metrics, computed_literal=comparison)


_CORE.protocol, _CORE.summarize = protocol, summarize
run, audit = _CORE.run, _CORE.audit
