#!/usr/bin/env python
"""Publish saved local results while independent activation replay is pending."""
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from codecue.binding import relationship_capture as base
from codecue.binding import arithmetic_graph_readouts as storage

OUT = Path('artifacts/binding/arithmetic_state_followup/20261030_v2')
REPORT = Path('reports/binding/arithmetic_local_completion_snapshot_v1.md')


def main():
    if (OUT / 'completion_snapshot_review_v1.json').exists():
        raise ValueError('completed snapshot must be preserved')
    integrity = base._json(OUT / 'local_integrity_review_v1.json')
    if integrity['status'] != 'passed':
        raise ValueError('saved-model/score/response integrity check must pass first')
    text = ['# Completed local-dependency discovery: saved-result snapshot', '',
        'All original local-suite jobs completed successfully. Saved dependency model/score checksums and behavioral parsing/counts passed their postrun integrity checks. Independent activation-to-score replay is queued in the follow-up suite; this snapshot summarizes the saved measurements without fitting or querying a language model.', '',
        '| Model | Features | TRAIN-selected architecture | Parent accuracy | Complete graph | Random-family accuracy |',
        '|---|---|---|---:|---:|---:|']
    summaries, inputs = {}, {}
    for name in ('llama8b', 'codellama34b'):
        folder = Path('artifacts/binding/arithmetic_local/20261030_v1') / name
        receipt = base._json(folder / 'probes/completion_manifest_v1.json')
        entry = receipt['artifacts']['results']
        data = base._json(entry['path'], entry['sha256'])
        inputs[name + '_probes'] = entry
        summaries[name] = {}
        for backend in ('hidden_local', 'hidden_global', 'source_local'):
            real = [b for b in data['fits'] if b['backend'] == backend and b['target'] == 'real' and b['training_families'] == 216]
            control = [b for b in data['fits'] if b['backend'] == backend and b['target'] == 'random_family' and b['training_families'] == 216]
            score = float(np.mean([b['development']['family_macro_accuracy'] for b in real]))
            whole = float(np.mean([b['development']['whole_program_graph_accuracy'] for b in real]))
            shuffled = float(np.mean([b['development']['family_macro_accuracy'] for b in control]))
            summaries[name][backend] = dict(parent_accuracy=score, whole_graph=whole, control=shuffled)
            text.append(f"| {name} | {backend} | {data['selected_methods'][backend]} | {100 * score:.2f}% | {100 * whole:.2f}% | {100 * shuffled:.2f}% |")
        path = folder / 'behavior/summary.json'
        inputs[name + '_behavior'] = storage._pin(path)
    text += ['', 'These are family-macro parent accuracies on 72 new structural DEV families, averaged over three weighting seeds. Complete graphs contain four/eight/twelve ordered parents at two/four/six arithmetic updates. The answer-query comparison also receives earlier candidate-definition states. Exact source-name/recency parsing solves these labels at 100%; character features are a limited learned comparator. Architectures were selected separately inside TRAIN, so capacity-matched counterparts remain a separate queued sensitivity.', '',
        'Data diversity, decoder architectures, candidate masks and token access all differ from the initial global study. This result cannot isolate localization as the cause of the gain, and it does not establish a complete numeric state or natural causal use.', '',
        '| Model | Wording | Split/depth/query | Correct / cases | Invalid |', '|---|---:|---|---:|---:|']
    for name in ('llama8b', 'codellama34b'):
        data = base._json(inputs[name + '_behavior']['path'], inputs[name + '_behavior']['sha256'])
        for row in data['metrics']:
            if row['split'] == 'train':
                continue
            text.append(f"| {name} | I{row['instruction']} | {row['split']} / {row['depth']} / {row['query_kind']} | {row['correct']}/{row['cases']} | {row['invalid']} |")
    text += ['', 'Computed answers remain unreliable and wording-sensitive. All wording results and invalid responses are retained. Representation captures use I0 only. Calibration families never train a probe.', '',
        'The [CPU follow-up protocol](arithmetic_state_followup_plan_v2.md) queues independent replay, capacity-matched counterparts, current-definition lookup, role-conditioned numeric decoding and predicted-state algebraic relationships. Its primary composed pipeline uses predicted binding pointers. Oracle routing and arithmetic performed externally on decoded operands are separately labeled ceilings/diagnostics.', '']
    base._publish(REPORT, ('\n'.join(text) + '\n').encode())
    base._put(OUT / 'completion_snapshot_review_v1.json', dict(status='complete_exploratory',
        recorded_utc=datetime.now(timezone.utc).isoformat(), inputs=inputs, summary=summaries,
        report=storage._pin(REPORT), renderer=storage._pin(Path(__file__)), new_model_queries=0, new_fits=0,
        scope='Saved-result summary after checksum/parser audit; independent activation replay remains queued.'))


if __name__ == '__main__':
    main()
