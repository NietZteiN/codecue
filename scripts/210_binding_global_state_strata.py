#!/usr/bin/env python
"""Publish predeclared slot/relationship strata from completed global fit banks."""
from pathlib import Path
import json
import numpy as np
from codecue.binding import arithmetic_global_state as study


def main():
    config_path = Path('configs/binding/arithmetic_global_state_20261031_v1/report.json')
    config = study.base._json(config_path); study.common.completed(config)
    output = Path('reports/binding/arithmetic_global_state_strata_v1.md')
    review = Path('artifacts/binding/arithmetic_global_state/20261031_v1/strata_review_v1.json')
    if output.exists() or review.exists(): raise ValueError('preserve completed stratum editions')
    lines = ['# Global-state readouts: computed values and queried slots', '',
        'These are the predeclared evaluation annotations from the completed seven-cell assay. '
        'No additional fitting, selection or model calls. Average three fitting seeds after each seed\'s '
        'TRAIN-only alpha selection. Every annotation stays outside the probe inputs. '
        'These tables are descriptive adaptive DEV summaries; no additional intervals or mechanism claim.', '',
        '| Features | Width | Scalar computed exact | Scalar untouched exact | Scalar queried exact | Scalar unqueried exact | Categorical computed exact | Categorical untouched exact |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    cells, inputs = [], dict(report_config=study.storage._pin(config_path),
        report=study.storage._pin(Path(config['run_dir']) / 'results.json'))
    for request in config['workers']:
        worker = study.base._json(request['path'], request['sha256']); study.common.completed(worker)
        path = Path(worker['run_dir']) / 'results.json'; data = study.base._json(path)
        inputs[request['path']] = study.storage._pin(path)
        selected = {name: [b for b in data['fits'] if name in b['selected_groups']] for name in study.GROUPS}
        for name, banks in selected.items():
            if banks and sorted(b['seed'] for b in banks) != list(study.numeric.SEEDS):
                raise ValueError('unique complete selected seeds required')
        def mean(kind, *keys):
            values = []
            for bank in selected[kind]:
                value = bank['panels']['development']['real']
                for key in keys: value = value[key]
                values.append(value)
            return float(np.mean(values)) if len(values) == 3 and all(v is not None for v in values) else None
        values = [mean('scalar', 'scalar', 'strata', key, 'exact') for key in ('computed', 'untouched', 'queried', 'unqueried')]
        values += [mean('categorical', 'categorical', 'strata', key, 'exact') for key in ('computed', 'untouched')]
        def percent(value): return f'{100*value:.2f}%' if value is not None else 'unsupported'
        lines.append(f"| {worker['alias']} | {worker['width']} | " + ' | '.join(map(percent, values)) + ' |')
        cells.append(dict(alias=worker['alias'], width=worker['width'], value_strata=values,
            computed_relation_ba=mean('relations', 'direct_relations_involving_computed', 'type_macro_balanced_accuracy')))
    lines += ['', '## Direct relationships involving at least one computed value', '',
        '| Features | Width | Relation-type macro BA |', '|---|---:|---:|']
    for cell in cells:
        lines.append(f"| {cell['alias']} | {cell['width']} | {percent(cell['computed_relation_ba'])} |")
    lines += ['', 'Computed means the current definition is an arithmetic update rather than an initial root. '
        'Untouched values can remain visible as source literals, so overall slot accuracy can hide weak computation recovery. '
        'Queried/unqueried comparisons are observational: query choice and value difficulty can differ. '
        'They do not establish a causal query effect; matched query-scope/timing captures are still needed. '
        'Family weighting within a stratum can differ from the overall four-slot metric. '
        'For direct relationships, the saved banks retain each head\'s unique-TRAIN-body eligibility and evaluation class counts. '
        'Undefined cells are excluded within type, and BA is undefined if a type lacks support. '
        'The main report retains direct-versus-external-derived, shuffled/prior controls and matched source contrasts.', '']
    study.base._publish(output, '\n'.join(lines).encode())
    result = dict(status='rendered_existing_results', script=study.storage._pin(__file__), inputs=inputs, cells=cells,
        output=study.storage._pin(output), new_fits=0, new_model_queries=0, generated_holdouts_opened=False)
    study.base._put(review, result)
    print(json.dumps(dict(status=result['status'], report=str(output))))


if __name__ == '__main__': main()
