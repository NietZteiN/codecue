"""Read-only audits and paired summaries for the next discovery experiments."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

from .checkpoint_suite import audit, prepared
from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, sha
from .registry import code_identity


def load(spec):
    if sha(spec['config']) != spec['sha256']:
        raise ValueError('review configuration checksum changed')
    config = json.loads(Path(spec['config']).read_text())
    checked = audit(config)
    _, cases = prepared(config, checked['preflight']['source_sha256'])
    rows = read_jsonl(Path(config['run_dir']) / 'checkpoint_suite/responses.jsonl')
    return config, checked, cases, rows


def serialization(config):
    results = {}
    for name, spec in config['models'].items():
        native, naudit, ncases, nrows = load(spec['native'])
        raw, raudit, rcases, rrows = load(spec['completion'])
        for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'max_new_tokens', 'eos_token_ids'):
            if native[key] != raw[key]:raise ValueError('serialization review contract differs: ' + key)
        old = {(r['task'], r['id']): r for r in nrows if r['section'] == 'cruxeval'}
        if set(old) != {(r['task'], r['id']) for r in rrows}:raise ValueError('serialization coverage differs')
        old_cases = {(r['task'], r['id']): r for r in ncases if r['section'] == 'cruxeval'}
        if any(old_cases[c['task'], c['id']]['record'] != c['record'] for c in rcases):
            raise ValueError('serialization changed released records')
        tasks = []
        for task in ('cruxeval_o_direct', 'cruxeval_o_cot'):
            new = [r for r in rrows if r['task'] == task]
            before = [old[r['task'], r['id']] for r in new]
            pairs = Counter(('both_correct' if a['score']['correct'] and b['score']['correct'] else
                             'native_only' if a['score']['correct'] else 'completion_only' if b['score']['correct']
                             else 'neither_correct') for a, b in zip(before, new))
            tasks.append(dict(task=task, n=len(new), paired_correctness=dict(pairs),
                native_correct=sum(r['score']['correct'] for r in before), completion_correct=sum(r['score']['correct'] for r in new),
                native_valid=sum(r['score']['valid'] for r in before), completion_valid=sum(r['score']['valid'] for r in new),
                native_program_echo=sum('[PYTHON]' in r['raw_response'] for r in before),
                completion_program_echo=sum('[PYTHON]' in r['raw_response'] for r in new),
                native_upstream_literal_correct=sum(r['score']['upstream_postprocessing_literal_correct'] for r in before),
                completion_upstream_literal_correct=sum(r['score']['upstream_postprocessing_literal_correct'] for r in new)))
        results[name] = dict(tasks=tasks, native_identity=naudit['identity_hash'], completion_identity=raudit['identity_hash'])
    result = dict(status='passed', complete=True, config_hash=digest(config), analysis_source=code_identity(),
                  results=results, generated_holdouts_opened=False, model_inference=False)
    lines = ['# Llama CRUXEval completion-interface follow-up', '',
             'This follow-up was motivated by the observed chat-wrapper program echoes. It keeps the checkpoint, '
             'released question content, greedy BF16 decoding, token ceilings and literal-only scorers fixed. '
             'Only the completion boundary changes. Existing native-chat results are preserved.', '',
             '| Model | Task | Native correct | Completion correct | Native parseable | Completion parseable |',
             '|---|---|---:|---:|---:|---:|']
    for name, record in results.items():
        for row in record['tasks']:
            lines.append(f"| {name} | {row['task']} | {row['native_correct']}/{row['n']} | {row['completion_correct']}/{row['n']} | {row['native_valid']} | {row['completion_valid']} |")
    lines += ['', 'The JSON artifact retains both scoring methods, paired correctness overlap and program-echo '
              'counts. A gain after fixing output format does not measure an equivalent gain in underlying reasoning. '
              'No downloaded programs or model outputs were executed. These remain literal-equality baselines, '
              'not official sampled execution pass@k. No generated final outcomes were opened.', '']
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    immutable(config['report'], '\n'.join(lines).encode())
    return result


def clustered_delta(pairs, seed=2026102602):
    """Weighted paired accuracy difference; bootstrap structural components."""
    sums = defaultdict(lambda: [0, 0])
    for component, left, right in pairs:
        sums[component][0] += int(left) - int(right)
        sums[component][1] += 1
    if not pairs:raise ValueError('paired contrast is empty')
    estimate = sum(v[0] for v in sums.values()) / len(pairs)
    interval = None
    if len(sums) >= 8:
        rng = random.Random(seed)
        values = list(sums.values())
        draws = []
        for _ in range(2000):
            selected = rng.choices(values, k=len(values))
            draws.append(sum(v[0] for v in selected) / sum(v[1] for v in selected))
        draws.sort()
        interval = [draws[49], draws[1949]]
    return dict(estimate=estimate, pairs=len(pairs), structural_components=len(sums),
                exploratory_cluster_bootstrap_95_interval=interval)


def competition(config):
    results = {}
    for name, spec in config['models'].items():
        _, checked, cases, rows = load(spec)
        cells, alternatives = defaultdict(list), Counter()
        versions, owner = {}, defaultdict(list)
        for case, output in zip(cases, rows):
            row = case['record']
            key = (row['family'], row['available_bindings'], row['updates'], row['tail_placement'],
                   row['query_role'], row['condition'], row['lexical_realization'], row['split'])
            cells[key].append(output)
            if not output['score']['correct']:
                labels = output['score']['compatible_error_labels']
                alternatives[' | '.join(labels) if labels else 'unclassified_or_invalid'] += 1
            if row['family'] == 'versions':
                key = (row['base_id'], row['updates'], row['tail_placement'], row['query_role'],
                       row['condition'], row['lexical_realization'])
                if key in versions:raise ValueError('duplicate competition contrast key')
                versions[key] = (row['template_id'], output['score']['correct'])
            else:owner[row['base_id'], row['lexical_realization']].append((row, output))
        effects = []
        for query in ('current', 'saved'):
            for effect in ('three_minus_one_updates', 'tail_after_minus_before', 'misleading_minus_informative'):
                pairs = []
                for key, (component, value) in versions.items():
                    base, updates, tail, role, condition, lexical = key
                    if role != query:continue
                    if effect == 'three_minus_one_updates' and updates == 3:
                        other = (base, 1, tail, role, condition, lexical)
                    elif effect == 'tail_after_minus_before' and tail == 'after':
                        other = (base, updates, 'before', role, condition, lexical)
                    elif effect == 'misleading_minus_informative' and condition == 'misleading':
                        other = (base, updates, tail, role, 'informative', lexical)
                    else:continue
                    pairs.append((component, value, versions[other][1]))
                effects.append(dict(query_role=query, contrast=effect, **clustered_delta(pairs)))
        ownership = dict(groups=len(owner), all_four_correct=0, constant_valid_guess=0, value_sets_right_but_ownership_wrong=0)
        for group in owner.values():
            if len(group) != 4:raise ValueError('ownership group incomplete')
            ownership['all_four_correct'] += all(output['score']['correct'] for _, output in group)
            predictions = [out['score']['prediction'] for _, out in group]
            ownership['constant_valid_guess'] += None not in predictions and len(set(predictions)) == 1
            sets_right = all(sorted(out['score']['prediction'] for row, out in group if row['ownership_swapped'] == swapped)
                             == sorted(row['expected_answer'] for row, out in group if row['ownership_swapped'] == swapped)
                             for swapped in (False, True)) if None not in predictions else False
            ownership['value_sets_right_but_ownership_wrong'] += sets_right and not all(out['score']['correct'] for _, out in group)
        fields = ('family', 'available_bindings', 'updates', 'tail_placement', 'query_role', 'condition', 'lexical_realization', 'split')
        results[name] = dict(identity_hash=checked['identity_hash'], evaluated=checked['evaluated'], gpu=checked['gpu'],
            cells=[dict(zip(fields, key), n=len(group), correct=sum(r['score']['correct'] for r in group),
                        valid=sum(r['score']['valid'] for r in group)) for key, group in sorted(cells.items())],
            paired_effects=effects, ownership=ownership, compatible_error_combinations=dict(alternatives))
    result = dict(status='passed', complete=True, results=results, config_hash=digest(config),
                  analysis_source=code_identity(), generated_holdouts_opened=False, model_inference=False)
    lines = ['# Arithmetic-free binding competition discovery', '',
             'Both checkpoints passed their recorded elementary arithmetic-free validation before this experiment. '
             'The bank holds literal exposure, statement count and final states fixed across version/tail contrasts; '
             'ownership swaps preserve value multisets while changing their associations. Full prompt token lengths '
             'were matched for naming, version and tail contrasts before inference.', '',
             '| Model | Query | Contrast | Paired accuracy change | Pairs | Structural components |',
             '|---|---|---|---:|---:|---:|']
    for name, record in results.items():
        for effect in record['paired_effects']:
            lines.append(f"| {name} | {effect['query_role']} | {effect['contrast']} | {100*effect['estimate']:+.2f} pp | {effect['pairs']} | {effect['structural_components']} |")
    lines += ['', 'Changes are exploratory paired differences within the complete bank. JSON includes all factorial '
              'cells, structural-component bootstrap intervals, invalid responses, four-question ownership checks '
              'and overlapping counterfactual-consistent error labels. A compatible wrong answer does not identify '
              'its internal cause. Available bindings include irrelevant competitors and are not a manipulation '
              'of the number of live output dependencies. This uses one selected readout and two lexical realizations; '
              'it does not establish robustness across instructions. No final outcomes, probes or causal interventions '
              'were used in this analysis.', '']
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    immutable(config['report'], '\n'.join(lines).encode())
    return result
