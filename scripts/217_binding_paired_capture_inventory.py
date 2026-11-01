#!/usr/bin/env python
"""Metadata-only planning audit of potential native causal-prefix reuse."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True)
    parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args()
    own_path = Path(__file__).resolve(); own_sha = hashlib.sha256(own_path.read_bytes()).hexdigest()
    if own_sha != args.script_sha256: raise ValueError('queued planning utility changed')
    snapshot = Path(args.source_root).resolve(); sys.path.insert(0, str(snapshot / 'src'))
    from codecue.binding.snapshots import verify
    manifest = verify(snapshot)
    from codecue.binding import relationship_capture as base, arithmetic_state_common as common
    from codecue.binding import arithmetic_graph_readouts as storage
    from codecue.binding.datasets import digest
    base._slurm()
    out = Path('artifacts/binding/arithmetic_capture_preparation/20261101_v1')
    if (out / 'results.json').exists(): raise ValueError('preserve completed planning edition')
    models, inputs = {}, {}
    for alias, width in [('llama8b', 4096), ('codellama34b', 8192)]:
        path = f'configs/binding/arithmetic_paired_20261101_v1/{alias}_native.json'
        config = base._json(path); common.completed(config)
        native = base._json(Path(config['run_dir']) / 'results.json')
        prepared = native['prepared_cases']; inputs[alias] = dict(config=storage._pin(path), prepared=prepared)
        unique, by_site, counts, labels = {}, defaultdict(set), Counter(), {}
        seen = set()
        with Path(prepared['path']).open() as stream:
            for line in stream:
                row = json.loads(line)
                if row['id'] in seen: raise ValueError('duplicate native case')
                seen.add(row['id']); counts['cases/' + row['split']] += 1
                tokens = row['input_token_ids']
                points = list(row['sites']) + [dict(kind='generation', available=True, position=len(tokens) - 1,
                    prefix_sha256=digest(tokens), values=row['sites'][-1]['values'], versions=row['sites'][-1]['versions'])]
                for point in points:
                    site = point['kind']; key = row['split'] + '/' + site
                    if not point['available']:
                        counts['unavailable/' + key] += 1; continue
                    position = point['position']; prefix = tokens[:position + 1]
                    if not 0 <= position < len(tokens) or digest(prefix) != point['prefix_sha256']:
                        raise ValueError('native causal prefix pin differs')
                    identity = point['prefix_sha256']; truth = (tuple(point['values']), tuple(point['versions']))
                    if identity in labels and labels[identity] != truth:
                        raise ValueError('same native prefix has conflicting assignment-result labels')
                    labels[identity] = truth
                    entry = unique.setdefault(identity, dict(tokens=len(prefix), uses=0, splits=set(), sites=set()))
                    if entry['tokens'] != len(prefix): raise ValueError('prefix hash length collision')
                    entry['uses'] += 1; entry['splits'].add(row['split']); entry['sites'].add(site)
                    by_site[key].add(identity); counts['requested/' + key] += 1
        if len(seen) != 45360 or base._sha(prepared['path']) != prepared['sha256']:
            raise ValueError('complete immutable native bank required')
        formal_splits = {'train', 'development'}
        formal_unique = {k for k, v in unique.items() if v['splits'] & formal_splits}
        formal_requests = sum(v for k, v in counts.items() if k.startswith(('requested/train/', 'requested/development/')))
        totals = dict(unique_prefixes=len(unique), requested_site_rows=sum(v for k, v in counts.items() if k.startswith('requested/')),
            formal_unique_prefixes=len(formal_unique), formal_requested_site_rows=formal_requests,
            formal_reuse_factor=formal_requests / len(formal_unique),
            full_native_input_tokens_if_prefixes_separate=sum(v['tokens'] for v in unique.values()),
            prefixes_shared_across_train_dev=sum({'train', 'development'} <= v['splits'] for v in unique.values()),
            prefixes_shared_formal_calibration=sum(bool(v['splits'] & formal_splits) and 'calibration' in v['splits'] for v in unique.values()))
        models[alias] = dict(width=width, counts=dict(counts), site_unique_counts={k: len(v) for k, v in sorted(by_site.items())},
            totals=totals, four_layer_full_width_storage_bytes={dtype: dict(
                requested=formal_requests * width * 4 * size, unique=len(formal_unique) * width * 4 * size)
                for dtype, size in [('float32', 4), ('bfloat16', 2)]})
    if hashlib.sha256(own_path.read_bytes()).hexdigest() != own_sha: raise ValueError('planning code changed during run')
    result = dict(status='complete_exploratory', source_snapshot=str(snapshot), source_snapshot_id=manifest['snapshot_id'],
        source_sha256=manifest['code']['source_sha256'], utility=dict(path=str(own_path), sha256=own_sha),
        inputs=inputs, models=models, new_model_queries=0, new_fits=0, generated_holdouts_opened=False,
        formal_capture_submitted=False,
        policy='potential prefix reuse only; oracle labels stay outside model inputs; no independent-family or numerical-identity claim; future capture must audit padding/backend tolerance before reuse')
    lines = ['# Native capture preparation: potential prefix reuse', '',
        'Metadata-only audit of the existing paired native layouts. No model calls or fits. '
        'Exact native token-prefix pins and assignment-result label consistency are checked. '
        'Reusing a prefix computationally does not merge examples, change family weights or turn shared prefixes into independent evidence. '
        'RHS labels describe the assignment result; they do not establish that the write has already occurred internally.', '',
        '| Model | Formal requested site rows | Unique causal prefixes | Potential reuse factor | Four-layer FP32 requested / unique GiB |',
        '|---|---:|---:|---:|---:|']
    for alias, model in models.items():
        t = model['totals']; s = model['four_layer_full_width_storage_bytes']['float32']
        lines.append(f"| {alias} | {t['formal_requested_site_rows']} | {t['formal_unique_prefixes']} | {t['formal_reuse_factor']:.2f} | {s['requested']/1024**3:.2f} / {s['unique']/1024**3:.2f} |")
    lines += ['', 'These are output-vector storage estimates, not total storage or GPU-runtime savings. '
        'A shared-prefill implementation could capture multiple sites per source; separate-prefix counts do not establish '
        'the fastest batching strategy. Generation-prefix rows here cover only formal output-only layouts. '
        'Generated-trace answer states remain unimplemented. Before using this plan, compare full-prompt versus truncated-prefix '
        'states with matched padding/native tokens and explicit numerical tolerance; retain versioned-label semantics and site masks. '
        'Shared TRAIN/DEV prefixes are reported in JSON and do not justify fitting on DEV or weakening structural closure.', '']
    report = Path('reports/binding/arithmetic_capture_preparation_20261101_v1.md')
    base._publish(report, '\n'.join(lines).encode()); base._put(out / 'results.json', result)
    base._put(out / 'completion_manifest_v1.json', dict(status='complete_exploratory', source=result['source_sha256'],
        utility=result['utility'], artifacts=dict(results=storage._pin(out / 'results.json'), report=storage._pin(report)),
        new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status=result['status'], models={k: v['totals'] for k, v in models.items()})))


if __name__ == '__main__': main()
