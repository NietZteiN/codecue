#!/usr/bin/env python
"""Exploratory matched overwrite contrasts on completed calibration responses."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True); parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args(); own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    if own_sha != args.script_sha256: raise ValueError('queued retention review changed')
    snapshot = Path(args.source_root).resolve(); sys.path.insert(0, str(snapshot / 'src'))
    from codecue.binding.snapshots import verify
    frozen = verify(snapshot)
    from codecue.binding import arithmetic_paired_exploration as study
    study.base._slurm()
    root = Path('artifacts/binding/arithmetic_paired_exploration/20261101_v2')
    folder = root / 'retention_review'
    if (folder / 'results.json').exists(): raise ValueError('preserve completed review editions')
    audits = {a: study.base._json(root / (a + '_postrun') / 'results.json') for a in ('llama8b', 'codellama34b')}
    source_pin = audits['llama8b']['input_pins']['source_dataset']
    if source_pin != audits['codellama34b']['input_pins']['source_dataset'] or study.base._sha(source_pin['path']) != source_pin['sha256']:
        raise ValueError('same hash-pinned calibration source required')
    sources, paired_sources = {}, defaultdict(dict)
    with Path(source_pin['path']).open() as stream:
        for line in stream:
            r = json.loads(line)
            if r['split'] != 'calibration' or r['delay'] != 0: continue
            if r['contrast'] != 'retention' or r['mutation'] not in ('operand', 'irrelevant'): raise ValueError('paired retention source required')
            lines = r['body'].splitlines(); at = r['roles'].index('mutation'); lhs, rhs = lines[at].split(' = ')
            expected_lhs = r['slot_names'][0 if r['mutation'] == 'operand' else 3]
            if lhs != expected_lhs: raise ValueError('mutation destination label differs')
            lines[at] = '__matched_destination__ = ' + rhs
            key = '\n'.join(lines)
            if r['mutation'] in paired_sources[key]: raise ValueError('duplicate source pair member')
            paired_sources[key][r['mutation']] = r; sources[r['id']] = r
    if len(sources) != 72 or len(paired_sources) != 36: raise ValueError('complete delay-zero calibration source pairs required')
    for pair in paired_sources.values():
        if set(pair) != {'operand', 'irrelevant'}: raise ValueError('incomplete mutation source pair')
        a, b = pair['operand'], pair['irrelevant']
        if a['expected_answer'] != b['expected_answer'] or a['component_id'] != b['component_id']:
            raise ValueError('retained target or structural component changed across mutation pair')
    key_for = {r['id']: key for key, pair in paired_sources.items() for r in pair.values()}
    models, inputs = {}, dict(source_dataset=source_pin)
    for alias in ('llama8b', 'codellama34b'):
        audit_path = root / (alias + '_postrun') / 'results.json'; audit = audits[alias]
        if audit['status'] != 'complete_audited_exploratory': raise ValueError('completed native-token audit required')
        if study.base._sha(audit['worker_results']['path']) != audit['worker_results']['sha256']: raise ValueError('audited worker changed')
        cfg = study.base._json(f'configs/binding/arithmetic_paired_exploration_20261101_v2/{alias}_continuation.json')
        proof = study.common.completed(cfg); pin = proof['artifacts']['diagnostic_rows']
        rows = json.loads(Path(pin['path']).read_text())
        if len(rows) != 1296 or len({r['id'] for r in rows}) != 1296: raise ValueError('complete unique response cohort required')
        pairs = defaultdict(dict)
        for r in rows:
            source = sources[r['record_id']]; expected = [source['expected_answer']] if r['scope'] == 'single' else source['final_values']
            if r['expected'] != expected: raise ValueError('target/source join differs')
            key = (key_for[r['record_id']], r['protocol'], r['scope'], r['instruction'])
            if r['mutation'] in pairs[key]: raise ValueError('duplicate response pair member')
            pairs[key][r['mutation']] = r
        if len(pairs) != 648 or any(set(p) != {'operand', 'irrelevant'} for p in pairs.values()):
            raise ValueError('complete source/protocol/scope/wording mutation factorial required')
        cells = defaultdict(Counter)
        for mode in ('strict', 'diagnostic'):
            for (_, protocol, scope, _), pair in pairs.items():
                outcomes = {}
                for mutation, r in pair.items():
                    values = r['strict_values' if mode == 'strict' else 'diagnostic_values']
                    valid = values is not None and not r['truncated']
                    index = 0 if scope == 'single' else 2
                    guess = values[index] if valid else None; src = sources[r['record_id']]
                    correct = valid and guess == src['expected_answer']; matches = []
                    if valid and not correct:
                        matches = [k for k, value in src['error_candidates'].items() if k != 'correct' and guess == value]
                        if any(guess == v for j, v in enumerate(src['final_values']) if j != 2): matches.append('other_current_binding')
                    outcomes[mutation] = dict(valid=valid, guess=guess, correct=correct, matches=matches)
                a, b = outcomes['operand'], outcomes['irrelevant']; r = pair['operand']
                recomputed = 'recomputed_current_operands' in a['matches']; unique = a['matches'] == ['recomputed_current_operands']
                values = dict(pairs=1, operand_correct=int(a['correct']), irrelevant_correct=int(b['correct']),
                    operand_only_correct=int(a['correct'] and not b['correct']), irrelevant_only_correct=int(b['correct'] and not a['correct']),
                    accepted_values_disagree=int(a['valid'] and b['valid'] and a['guess'] != b['guess']),
                    operand_invalid=int(not a['valid']), irrelevant_invalid=int(not b['valid']),
                    operand_recomputed_wrong=int(recomputed), operand_unique_recomputed_wrong=int(unique),
                    irrelevant_correct_operand_recomputed_wrong=int(b['correct'] and recomputed),
                    irrelevant_correct_operand_unique_recomputed_wrong=int(b['correct'] and unique))
                for cell in (mode + '/' + protocol + '/' + scope,
                        mode + '/' + protocol + '/' + scope + '/' + r['kind'] + '/depth' + str(r['depth'])):
                    cells[cell].update(values)
        models[alias] = {k: dict(v) for k, v in sorted(cells.items())}
        inputs[alias] = dict(audit=study.storage._pin(audit_path), diagnostic_rows=pin)
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('retention review changed during execution')
    result = dict(status='complete_audited_exploratory', source_snapshot_id=frozen['snapshot_id'],
        source_sha256=frozen['code']['source_sha256'], utility=dict(path=str(own), sha256=own_sha), inputs=inputs,
        source_pairs=len(paired_sources), source_components=len({r['component_id'] for r in sources.values()}),
        pairs_per_model_and_grammar=648, models=models, new_model_queries=0, new_fits=0,
        generated_holdouts_opened=False, formal_capture_submitted=False,
        limitations='finite calibration only; contexts/wordings/seeds correlated; same recomputed number can match stale/wrong-binding alternatives; no identified neural mechanism')
    lines = ['# Exploratory retained-target overwrite contrasts', '',
        'All36 calibration source pairs differ only in the destination of one later assignment: overwrite an operand '
        'or the matched irrelevant slot with the SAME constant. The retained target is unchanged. '
        'Compare that target under both query scopes, all protocols and all three wordings. '
        'All predictions come from the completed, native-token-audited continuation outputs. No new model calls or fits. '
        'These are correlated calibration cases, not formal-family confirmation or an internal causal mechanism test.', '',
        '| Model | Grammar | Protocol | Scope | Pairs | Operand correct | Irrelevant correct | Irrelevant-only correct | Correct irrelevant + uniquely recomputed wrong operand |',
        '|---|---|---|---|---:|---:|---:|---:|---:|']
    for alias, table in models.items():
        for key, c in table.items():
            if key.count('/') != 2: continue
            mode, protocol, scope = key.split('/')
            lines.append(f"| {alias} | {mode} | {protocol} | {scope} | {c['pairs']} | {c['operand_correct']} | "
                f"{c['irrelevant_correct']} | {c['irrelevant_only_correct']} | {c['irrelevant_correct_operand_unique_recomputed_wrong']} |")
    lines += ['', 'The last column requires a wrong operand-condition target equal to recomputation from current operands, '
        'with no coincidence with the stored stale/opposite-operator/other-current-binding candidates, while the irrelevant '
        'partner is correct. This is unique only among this finite candidate list; other explanations remain possible. '
        'Copy controls often make recomputation and another-current-binding numerically identical and cannot distinguish them. '
        'Every invalid/truncated output remains a failure. JSON also retains accepted-value disagreements, ambiguous matches '
        'and kind/depth strata. Original pilot scores, failed output-only gates and formal data remain untouched.', '']
    text = '\n'.join(lines).replace('All36', 'All 36')
    report = Path('reports/binding/arithmetic_calibration_retention_review_20261101_v1.md')
    study.base._publish(report, text.encode()); study.base._put(folder / 'results.json', result)
    study.base._put(folder / 'completion_manifest_v1.json', dict(status=result['status'], utility=result['utility'],
        artifacts=dict(results=study.storage._pin(folder / 'results.json'), report=study.storage._pin(report)), new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status=result['status'], source_pairs=result['source_pairs'], source_components=result['source_components'])))


if __name__ == '__main__': main()
