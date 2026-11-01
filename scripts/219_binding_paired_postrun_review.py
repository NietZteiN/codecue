#!/usr/bin/env python
"""Audit completed continuation tokens and compare matched scope/protocol cases."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys


def success(row, mode, target_only=False):
    if mode not in ('strict', 'diagnostic'): raise ValueError('known scoring mode required')
    values = row['strict_values' if mode == 'strict' else 'diagnostic_values']
    if row['truncated'] or values is None: return False
    if len(values) != len(row['expected']): raise ValueError('answer shape differs from expected scope')
    if target_only:
        index = 0 if row['scope'] == 'single' else 2
        return values[index] == row['expected'][index]
    return values == row['expected']


def scope_panel(rows, mode):
    pairs = defaultdict(dict)
    for row in rows:
        key = (row['record_id'], row['protocol'], row['instruction'])
        if row['scope'] in pairs[key]: raise ValueError('duplicate matched scope')
        pairs[key][row['scope']] = row
    output = {}
    for protocol in ('output_only', 'intermediate_query', 'stepwise'):
        group = [p for (_, kind, _), p in pairs.items() if kind == protocol]
        if not group or any(set(p) != {'single', 'all'} for p in group): raise ValueError('complete scope pairs required')
        if any(p['single']['expected'][0] != p['all']['expected'][2] for p in group): raise ValueError('paired target differs')
        single = [success(p['single'], mode, True) for p in group]
        all_target = [success(p['all'], mode, True) for p in group]
        output[protocol] = dict(pairs=len(group), single_correct=sum(single), all_target_correct=sum(all_target),
            all_only_correct=sum(b and not a for a, b in zip(single, all_target)),
            single_only_correct=sum(a and not b for a, b in zip(single, all_target)))
    return output


def protocol_panel(rows, mode):
    triples = defaultdict(dict)
    for row in rows:
        key = (row['record_id'], row['scope'], row['instruction'])
        if row['protocol'] in triples[key]: raise ValueError('duplicate protocol relative')
        triples[key][row['protocol']] = row
    output = {}
    for scope in ('single', 'all'):
        group = [p for (_, kind, _), p in triples.items() if kind == scope]
        if not group or any(set(p) != {'output_only', 'intermediate_query', 'stepwise'} for p in group):
            raise ValueError('complete protocol triples required')
        for p in group:
            if any(r['expected'] != p['output_only']['expected'] for r in p.values()): raise ValueError('protocol targets differ')
        for protocol in ('intermediate_query', 'stepwise'):
            a = [success(p['output_only'], mode) for p in group]; b = [success(p[protocol], mode) for p in group]
            output[scope + '/' + protocol] = dict(pairs=len(group), output_only_correct=sum(a), other_correct=sum(b),
                other_only_correct=sum(y and not x for x, y in zip(a, b)),
                output_only_exclusive_correct=sum(x and not y for x, y in zip(a, b)))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--alias', required=True, choices=['llama8b', 'codellama34b'])
    parser.add_argument('--source-root', required=True); parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args(); own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    if own_sha != args.script_sha256: raise ValueError('queued review utility changed')
    snapshot = Path(args.source_root).resolve(); sys.path.insert(0, str(snapshot / 'src'))
    from codecue.binding.snapshots import verify
    frozen = verify(snapshot)
    from codecue.binding import arithmetic_paired_exploration as study
    study.base._slurm(); alias = args.alias
    root = Path('artifacts/binding/arithmetic_paired_exploration/20261101_v2')
    folder = root / (alias + '_postrun')
    if (folder / 'results.json').exists(): raise ValueError('preserve completed review editions')
    path = f'configs/binding/arithmetic_paired_exploration_20261101_v2/{alias}_continuation.json'
    config = study.base._json(path); proof = study.common.completed(config)
    worker = study.base._json(Path(config['run_dir']) / 'results.json')
    cfg, cases, old, sources, pins = study.load_pilot(config['pilot'])
    profile = study.base._json(cfg['profile']['path'], cfg['profile']['sha256'])
    tokenizer = study.capture._CORE._tokenizer(profile)
    from transformers import GenerationConfig, AutoConfig
    try:
        gen = GenerationConfig.from_pretrained(profile['model'], revision=profile['model_revision'], local_files_only=True)
        eos_origin = 'cached_generation_config'
    except OSError:
        gen = GenerationConfig.from_model_config(AutoConfig.from_pretrained(
            profile['model'], revision=profile['model_revision'], local_files_only=True))
        eos_origin = 'cached_model_config_default'
    eos = gen.eos_token_id if gen.eos_token_id is not None else tokenizer.eos_token_id
    eos = set(eos if isinstance(eos, list) else [eos])
    current, continuation_pins = {}, {}
    for name, pin in proof['artifacts'].items():
        if not name.startswith('continuation_'): continue
        continuation_pins[name] = pin; batch = study.base._json(pin['path'], pin['sha256'])
        if batch['source'] != worker['source'] or batch['config_hash'] != study.digest(config):
            raise ValueError('continuation batch source/config differs')
        if [r['id'] for r in batch['records']] != batch['ids']: raise ValueError('continuation batch IDs differ')
        for row in batch['records']:
            key = row['id']; original = old[key]; ids = row['output_token_ids']; prefix = original['output_token_ids']
            if key in current or not original['truncated']: raise ValueError('duplicate or unrequested continuation')
            if (ids[:len(prefix)] != prefix or row['prefix_tokens'] != len(prefix) or row['added_tokens'] != len(ids) - len(prefix)
                    or not len(prefix) < len(ids) <= study.CAP or any(t in eos for t in prefix)):
                raise ValueError('generated prefix/length invariant differs')
            if tokenizer.decode(ids, skip_special_tokens=True) != row['raw_response']:
                raise ValueError('response text differs from saved native output tokens')
            stops = [i for i, token in enumerate(ids) if token in eos]
            if row['truncated']:
                if stops or len(ids) != study.CAP: raise ValueError('truncation flags differ from EOS/ceiling')
            elif stops != [len(ids) - 1]: raise ValueError('completed continuation must stop exactly at first EOS')
            check = study.independent_score(cases[key], row['raw_response'], ids, row['truncated'])
            if any(row[k] != v for k, v in check.items()): raise ValueError('strict response replay differs')
            for field in ('record_id', 'component_id', 'scope', 'protocol', 'instruction', 'expected', 'mutation', 'depth', 'calibration_kind'):
                if row[field] != original[field]: raise ValueError('continued label identity differs')
            current[key] = row
    if set(current) != {k for k, r in old.items() if r['truncated']}: raise ValueError('full truncated cohort required')
    merged = {k: current.get(k, r) for k, r in old.items()}
    details = [study.describe(cases[k], merged[k], sources[cases[k]['record_id']]) for k in sorted(cases)]
    if study.cells(details) != worker['cells'] or study.paired_scopes(details) != worker['scope_pairs']:
        raise ValueError('reported continuation metrics differ from native-token replay')
    panels = {mode: dict(scope=scope_panel(details, mode), protocol=protocol_panel(details, mode)) for mode in ('strict', 'diagnostic')}
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('review source changed during execution')
    result = dict(status='complete_audited_exploratory', alias=alias, source_snapshot_id=frozen['snapshot_id'],
        source_sha256=frozen['code']['source_sha256'], utility=dict(path=str(own), sha256=own_sha),
        config=study.storage._pin(path), worker_results=study.storage._pin(Path(config['run_dir']) / 'results.json'),
        input_pins=pins, continuation_pins=continuation_pins, eos_ids=sorted(eos), eos_origin=eos_origin,
        audited_continuations=len(current), reused_completed_responses=len(merged) - len(current), cases=len(details),
        panels=panels, cells=worker['cells'], new_model_queries=0, new_fits=0, generated_holdouts_opened=False,
        formal_capture_submitted=False, original_scores_unchanged=True)
    lines = [f'# {alias}: audited continuation and matched query/protocol review', '',
        f"Verified all **{len(current)}** continuations against exact saved native prefixes, output-token decoding, EOS/ceiling flags, "
        f"source labels and independently reconstructed strict scores. Reused **{len(merged)-len(current)}** completed responses. "
        'This review made no model calls or fits. Only this completed checkpoint is reported; other jobs remain separate. '
        'Original pilot scores and failed output-only gates are unchanged.', '',
        '| Protocol | Scope | Cases | Strict complete | Heading-grammar complete | Truncated |',
        '|---|---|---:|---:|---:|---:|']
    for protocol in ('output_only', 'intermediate_query', 'stepwise'):
        for scope in ('single', 'all'):
            cell = worker['cells'][protocol + '/' + scope]; n = cell['rows']
            lines.append(f"| {protocol} | {scope} | {n} | {100*cell['strict_correct']/n:.2f}% | "
                f"{100*cell['diagnostic_complete_correct']/n:.2f}% | {cell['truncated']} |")
    lines += ['', '## Same target under single/all query scope', '',
        'Both columns score the retained target, including incomplete/invalid responses as failures. '
        'The heading diagnostic is target-blind and does not change official scores.', '',
        '| Grammar | Protocol | Pairs | Single correct | All-query target correct | All-only correct | Single-only correct |',
        '|---|---|---:|---:|---:|---:|---:|']
    for mode, panel in panels.items():
        for protocol, p in panel['scope'].items():
            lines.append(f"| {mode} | {protocol} | {p['pairs']} | {p['single_correct']} | {p['all_target_correct']} | {p['all_only_correct']} | {p['single_only_correct']} |")
    lines += ['', '## Matched protocol contrasts', '',
        '| Grammar | Scope | Other protocol | Pairs | Output-only correct | Other correct | Other-only correct | Output-only exclusive correct |',
        '|---|---|---|---:|---:|---:|---:|---:|']
    for mode, panel in panels.items():
        for key, p in panel['protocol'].items():
            scope, protocol = key.split('/')
            lines.append(f"| {mode} | {scope} | {protocol} | {p['pairs']} | {p['output_only_correct']} | {p['other_correct']} | {p['other_only_correct']} | {p['output_only_exclusive_correct']} |")
    lines += ['', 'All conditions have a1,024-token total ceiling after continuation, while completed EOS outputs are reused. '
        'Fixed generated prefixes, instructions, assistant answer prefixes and requested behavior differ across protocols. '
        'This is not a monolithic rerun, an isolated effect of reasoning, a hidden-state readout or a causal mechanism result. '
        'Finite calibration templates/seeds are correlated; no significance tests or novel-family claims. '
        'The original output-only competence gate remains failed. Before formal collection with a revised protocol, '
        'freeze its generation/parsing/site rules and check prospectively declared fresh calibration without selecting a best wording.', '']
    report = Path(f'reports/binding/arithmetic_paired_{alias}_postrun_20261101_v1.md')
    study.base._publish(report, '\n'.join(lines).encode()); study.base._put(folder / 'results.json', result)
    study.base._put(folder / 'completion_manifest_v1.json', dict(status=result['status'], utility=result['utility'],
        artifacts=dict(results=study.storage._pin(folder / 'results.json'), report=study.storage._pin(report)),
        new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status=result['status'], alias=alias, audited_continuations=len(current), matched_scope=panels)))


if __name__ == '__main__': main()
