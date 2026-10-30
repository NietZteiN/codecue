"""Computed-expression and late dead-reference routing discovery protocols."""
import ast
from collections import defaultdict
from itertools import product
import json
from pathlib import Path

from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle
from .published_benchmarks import immutable, sha
from .registry import code_identity


def numeric_bank(config):
    candidates = []
    for x, y, u, v in product(range(1, 5), repeat=4):
        for c in range(4, 10):
            a, b, z, w = x + y, u + v, c - y, c - v
            if (len({a, b, c}) == 3 and 1 <= z <= 5 and 1 <= w <= 5
                    and not {a, b, c} & {0, x, y, u, v, z, w}):
                candidates.append((x, y, u, v, z, w, a, b, c))
    seen, selected = set(), []
    for item in sorted(candidates, key=lambda item: digest([config['generation']['seed'], item])):
        x, y, u, v, z, w, *_ = item
        keys = {(x, y, u, v), (z, y, u, v), (x, y, w, v)}
        if keys & seen:
            continue
        selected.append(item)
        seen.update(keys)
        if len(selected) == config['generation']['numeric_groups']:
            return selected
    raise ValueError('not enough disjoint computed numeric groups')


def computed_rows(config):
    rows = []
    for index, (x, y, u, v, z, w, a, b, c) in enumerate(numeric_bank(config)):
        for family, mapping, lexical, query in product(('ownership', 'versions'), (0, 1), (0, 1), (0, 1)):
            n0, n1, scratch, saved = [('v0', 'v1', 'buffer', 's0'), ('n0', 'n1', 'temp', 's1')][lexical]
            group = f'{family}:m{mapping}:lex{lexical}:n{index}:q{query}'
            for variant, first, second, values in [('base', x, u, [a, b]), ('slot0', z, u, [c, b]), ('slot1', x, w, [a, c])]:
                lines = [f'{scratch} = 0', f'{n0} = {first} + {y}', f'{n1} = {second} + {v}']
                if family == 'ownership':
                    lines += [f'{scratch} = {n0}', f'{n0} = {n1 if mapping else n0}',
                              f'{n1} = {scratch if mapping else n1}', f'{scratch} = 0']
                    output, role = [n0, n1][query], ['v0', 'v1'][query]
                else:
                    old, other = (n0, n1) if mapping == 0 else (n1, n0)
                    lines += [f'{saved} = {old}', f'{old} = {other}', f'{scratch} = 0']
                    output, role = [old, saved][query], ['current', 'saved'][query]
                source = '\n'.join(lines + [output])
                rows.append(dict(id='computed-routing:' + digest(source)[:24], group_id=group,
                    numeric_group=str(index), family=family, mapping=mapping, lexical_realization=lexical,
                    query=query, query_role=role, variant=variant, source=source, binding_values=values,
                    expected_answer=execute(source)['expected_answer'], split='development',
                    evaluation_role='computed_expression_routing_discovery'))
    return rows


def swap_rows(config):
    path = config['generation']['anchor_prepared']
    if sha(path) != config['generation']['anchor_prepared_sha256']:
        raise ValueError('swap discovery anchor checksum differs')
    anchors = json.loads(Path(path).read_text())['cases']
    rows = []
    for key, case in sorted(anchors.items()):
        original = case['record']
        if original['family'] != 'ownership':
            continue
        for target in ('buffer', 'unused'):
            source = original['source']
            if target == 'unused':
                lines = source.splitlines()
                lines[-2] = config['generation']['unused_name'] + ' = 0'
                source = '\n'.join(lines)
            row = {k: original[k] for k in ('numeric_group', 'mapping', 'lexical_realization', 'query', 'query_role')}
            row.update(id='swap-reset:' + digest(source)[:24], anchor_id=key, group_id=key,
                source=source, variant=target, reset_target=target, family='ownership',
                binding_values=original['literal_values'], expected_answer=execute(source)['expected_answer'],
                split='development', evaluation_role='dead_reset_reference_discovery')
            rows.append(row)
    return rows


def make_rows(config):
    rows = computed_rows(config) if config['assay'] == 'computed_routing' else swap_rows(config)
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('extension programs must be unique')
    return rows


def pairs_for(config, rows):
    groups = defaultdict(dict)
    for row in rows:
        if row['variant'] in groups[row['group_id']]:
            raise ValueError('duplicate extension counterfactual')
        groups[row['group_id']][row['variant']] = row
    pairs = []
    for group, variants in sorted(groups.items()):
        computed = config['assay'] == 'computed_routing'
        expected = {'base', 'slot0', 'slot1'} if computed else {'buffer', 'unused'}
        if set(variants) != expected:
            raise ValueError('incomplete extension counterfactual group')
        for slot in ((0, 1) if computed else (1,)):
            a, b = (variants['base'], variants[f'slot{slot}']) if computed else (variants['buffer'], variants['unused'])
            for reverse in (False, True):
                recipient, donor = (b, a) if reverse else (a, b)
                pairs.append(dict(id=digest([recipient['id'], donor['id']]), group_id=group,
                    recipient=recipient['id'], donor=donor['id'], slot=slot, reverse=reverse,
                    replacement=donor['binding_values'][slot] if computed else recipient['expected_answer'],
                    baseline_answer=recipient['expected_answer'] if computed else
                        next(value for value in recipient['binding_values'] if value != recipient['expected_answer']),
                    counterfactual_answer=donor['expected_answer'], affected=recipient['expected_answer'] != donor['expected_answer'],
                    family=recipient['family'], query_role=recipient['query_role'], mapping=recipient['mapping'],
                    numeric_group=recipient['numeric_group'], lexical_realization=recipient['lexical_realization']))
    return pairs


def validate(config, rows, independent=False):
    if rows != make_rows(config):
        raise ValueError('extension dataset differs from registered sources/labels')
    by_id = {r['id']: r for r in rows}
    pairs = pairs_for(config, rows)
    for pair in pairs:
        a, b = [by_id[pair[k]] for k in ('recipient', 'donor')]
        if config['assay'] == 'computed_routing':
            if len(a['source']) != len(b['source']) or sum(x != y for x, y in zip(a['source'], b['source'])) != 1:
                raise ValueError('computed donors must change precisely one operand digit')
            literals = {n.value for row in (a, b) for n in ast.walk(ast.parse(row['source'])) if isinstance(n, ast.Constant)}
            if (set(a['binding_values']) | set(b['binding_values'])) & literals:
                raise ValueError('computed result occurs as a literal')
            if sum(isinstance(n, ast.BinOp) for n in ast.walk(ast.parse(a['source']))) != 2:
                raise ValueError('computed assay must retain both additions')
        elif a['expected_answer'] != b['expected_answer'] or a['source'].splitlines()[:-2] != b['source'].splitlines()[:-2]:
            raise ValueError('late reset contrast changed a relevant assignment or answer')
    if independent:
        for start in range(0, len(rows), 128):
            selected = rows[start:start + 128]
            if any(r['expected_answer'] != o['answer'] for r, o in zip(selected, python_oracle([r['source'] for r in selected]))):
                raise ValueError('independent extension oracle disagrees')
    return pairs


def build(config):
    rows = make_rows(config)
    pairs = validate(config, rows, independent=True)
    path = Path(config['dataset'])
    immutable(path, ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows).encode())
    manifest = dict(sha256=sha(path), generation_config_hash=digest(config['generation']),
        rows=len(rows), directed_pairs=len(pairs), independent_oracle_passed=True,
        role=config['assay'] + '_discovery', generated_holdouts_opened=False)
    immutable(path.with_suffix('.manifest.json'), (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return manifest


def layout(tokenizer, row, config):
    from .calibration import prompt
    text, source = prompt(tokenizer, row, 'print_direct_v3')
    text += config['answer_prefix_suffix']
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    start, lines = text.index(source), source.splitlines(keepends=True)
    positions = []
    for line_index in ([1, 2, 0] if config['assay'] == 'computed_routing' else [3, 6, 0]):
        line = lines[line_index]
        length = len(line.split(' = ')[0]) if config['assay'] == 'swap_reset' and line_index == 6 else len(line.rstrip('\n'))
        end = start + sum(map(len, lines[:line_index])) + length
        matches = [i for i, (a, b) in enumerate(encoded['offset_mapping']) if a < end == b]
        if len(matches) != 1:
            raise ValueError('extension site crosses a statement/identifier boundary')
        positions.append(matches[0])
    positions.append(len(encoded['input_ids']) - 1)
    return dict(record=row, prompt=text, input_token_ids=encoded['input_ids'], positions=positions)


def validate_layouts(config, cases, pairs):
    for pair in pairs:
        a, b = [cases[pair[k]] for k in ('recipient', 'donor')]
        differences = [i for i, (x, y) in enumerate(zip(a['input_token_ids'], b['input_token_ids'])) if x != y]
        if (len(a['input_token_ids']) != len(b['input_token_ids']) or a['positions'] != b['positions']
                or len(differences) != 1):
            raise ValueError('extension token layouts differ beyond one registered input token')
        site = a['positions'][pair['slot']]
        if config['assay'] == 'computed_routing':
            if not a['positions'][2] < differences[0] < site:
                raise ValueError('computed intervention must follow changed operand at an unchanged token')
        elif differences != [site]:
            raise ValueError('dead reset intervention must target its one changed identifier token')


def prepare(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    if sha(config['hook_proof']) != config['hook_proof_sha256']:
        raise ValueError('pinned hook proof changed')
    rows = read_jsonl(config['dataset'])
    pairs = validate(config, rows)
    tok = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tok, config)
    cases = {r['id']: layout(tok, r, config) for r in rows}
    validate_layouts(config, cases, pairs)
    if len(cases) % config['batch_size'] or len(pairs) % config['batch_size']:
        raise ValueError('extension must use complete equal-size batches')
    if config['assay'] == 'swap_reset':
        anchors = json.loads(Path(config['generation']['anchor_prepared']).read_text())['cases']
        if any(c['input_token_ids'] != anchors[c['record']['anchor_id']]['input_token_ids'] for c in cases.values() if c['record']['variant'] == 'buffer'):
            raise ValueError('original swap anchor prompt changed')
    answer_ids = {}
    for value in range(10):
        ids = tok(str(value), add_special_tokens=False)['input_ids']
        if len(ids) != 1:
            raise ValueError('extension requires one-token digits')
        answer_ids[str(value)] = ids[0]
    payload = dict(cases=cases, pairs=pairs, answer_token_ids=answer_ids,
                   padded_width=max(len(c['input_token_ids']) for c in cases.values()))
    immutable(config['prepared_cases'], (json.dumps(payload, sort_keys=True) + '\n').encode())
    result = dict(status='passed', config_hash=digest(config), source_sha256=code_identity()['source_sha256'],
        dataset_sha256=sha(config['dataset']), prepared_sha256=sha(config['prepared_cases']),
        cases=len(cases), directed_pairs=len(pairs), generated_holdouts_opened=False)
    write_json(config['preflight_result'], result)
    return result


def audit_names(config):
    """Choose a matched identifier using tokenization alone, before any inference."""
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    tok=AutoTokenizer.from_pretrained(config['model'],revision=config['tokenizer_revision'],local_files_only=True)
    configure_tokenizer(tok,config)
    originals=[r for r in make_rows(config) if r['variant']=='buffer']
    results=[]
    for name in ('cache','state','other','unused','value','dummy','spare'):
        passed=0;example=None
        for original in originals:
            alternate=dict(original)
            lines=original['source'].splitlines();lines[-2]=name+' = 0';alternate['source']='\n'.join(lines)
            a,b=layout(tok,original,config),layout(tok,alternate,config)
            try:
                validate_layouts(config,{'a':a,'b':b},[dict(recipient='a',donor='b',slot=1)])
                passed+=1
            except ValueError:
                if example is None:
                    example=dict(anchor_id=original['anchor_id'],original_length=len(a['input_token_ids']),alternate_length=len(b['input_token_ids']))
        results.append(dict(name=name,matched=passed,total=len(originals),example_failure=example))
    eligible=[r['name'] for r in results if r['matched']==r['total']]
    result=dict(status='passed' if eligible else 'needs_attention',results=results,recommended=eligible[0] if eligible else None,
                model_inference=False,purpose='Identifier selection by complete prompt token layout only; no model accuracy observed.')
    write_json(Path(config['run_dir']).parent/'name_audit_v1.json',result)
    return result


def inputs(config, source_hash=None):
    qa = json.loads(Path(config['preflight_result']).read_text())
    if (qa['status'] != 'passed' or qa['config_hash'] != digest(config)
            or qa['source_sha256'] != (source_hash or code_identity()['source_sha256'])
            or qa['prepared_sha256'] != sha(config['prepared_cases']) or qa['dataset_sha256'] != sha(config['dataset'])):
        raise ValueError('matching frozen extension tokenizer preflight required')
    data = json.loads(Path(config['prepared_cases']).read_text())
    rows = read_jsonl(config['dataset'])
    if data['pairs'] != validate(config, rows) or {r['id']: r for r in rows} != {k: c['record'] for k, c in data['cases'].items()}:
        raise ValueError('prepared extension identities differ')
    validate_layouts(config, data['cases'], data['pairs'])
    if data['padded_width'] != max(len(c['input_token_ids']) for c in data['cases'].values()):
        raise ValueError('extension fixed padding width differs')
    return qa, data


def run(config):
    from .value_transfer import run as engine_run
    return engine_run(config)


def audit(config):
    import numpy as np
    from .behavior import parse_answer
    from .value_transfer import audit as engine_audit, qualification, verify_answer_boundary, inputs as engine_inputs
    root = Path(config['run_dir']) / 'interventions'
    manifest, summary = [json.loads((root / name).read_text()) for name in ('manifest.json', 'summary.json')]
    if (manifest['status'] != 'complete' or manifest['identity_hash'] != digest(manifest['identity'])
            or manifest['identity']['config'] != config):
        raise ValueError('complete pinned extension run required')
    qa, data = engine_inputs(config, manifest['identity']['code']['source_sha256'])
    baselines = json.loads((root / 'baselines.json').read_text())
    if set(baselines) != set(data['cases']):
        raise ValueError('extension baseline coverage differs')
    verify_answer_boundary(config, baselines, data['answer_token_ids'])
    for key, row in baselines.items():
        if (parse_answer(row['raw_response']) != row['prediction']
                or row['correct'] != (row['prediction'] == data['cases'][key]['record']['expected_answer'])
                or not row['output_token_ids'] or row['first_token'] != row['output_token_ids'][0]):
            raise ValueError('extension baseline score or digit boundary differs')
    with np.load(root / 'baseline_vectors.npz', allow_pickle=False) as cache:
        bank, ids = cache['vectors'], cache['case_ids'].tolist()
    if ids != sorted(data['cases']) or bank.shape != (len(ids), len(config['layers']), 4, config['hidden_size']) or not np.isfinite(bank).all():
        raise ValueError('extension baseline tensor shape or identity differs')
    groups = defaultdict(list)
    for i, key in enumerate(ids):
        c = data['cases'][key]
        groups[digest([c['input_token_ids'][:c['positions'][1] + 1], len(c['input_token_ids'])])].append(i)
    if any(not np.array_equal(bank[g[0], :, :3], bank[i, :, :3]) for g in groups.values() for i in g[1:]):
        raise ValueError('extension prefix invariance audit failed')
    gate = qualification(config, data['cases'], baselines)
    if gate != summary['baseline_gate'] or gate != json.loads((root / 'baseline_gate.json').read_text()):
        raise ValueError('registered reliability gate differs')
    if any(p['family'] in gate['eligible_families'] for p in data['pairs']):
        return engine_audit(config)
    if summary['intervention_forwards'] != 0 or (root / 'replays.json').exists() or list((root / 'chunks').glob('*.json')):
        raise ValueError('failed gate must preserve baselines without interventions')
    result = dict(status='passed', identity_hash=manifest['identity_hash'], preflight=qa,
        baseline_cases=len(ids), baseline_correct=sum(r['correct'] for r in baselines.values()),
        intervention_forwards=0, baseline_gate=gate, baseline_sha256=sha(root / 'baselines.json'),
        vector_bank_sha256=sha(root / 'baseline_vectors.npz'), generated_holdouts_opened=False,
        interpretation=('Behavior-only capture audit passed; no interventions requested.' if config.get('baseline_only')
                        else 'Baseline audit passed; no family qualified for interventions.'))
    immutable(root / 'audit.json', (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return result


def review(config, analysis_revision=None):
    """Report every registered cell, including gated families and both directions."""
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .value_transfer import conditions
    root = Path(config['run_dir']) / 'interventions'
    checked = json.loads((root / 'audit.json').read_text())
    manifest = json.loads((root / 'manifest.json').read_text())
    if (checked['status'] != 'passed' or checked['identity_hash'] != manifest['identity_hash']
            or manifest['identity']['config'] != config or manifest['identity_hash'] != digest(manifest['identity'])
            or checked['baseline_sha256'] != sha(root / 'baselines.json')):
        raise ValueError('review requires a completed pinned extension audit')
    _, data = inputs(config, manifest['identity']['code']['source_sha256'])
    baselines = json.loads((root / 'baselines.json').read_text())
    pairs = {p['id']: p for p in data['pairs']}
    replays = json.loads((root / 'replays.json').read_text()) if (root / 'replays.json').exists() else {}
    collected, positive, negative, shams, max_norm_error = [], 0, 0, 0, 0.
    for path, expected in checked.get('chunk_checksums', {}).items():
        if sha(path) != expected:
            raise ValueError('audited extension chunk changed')
        for row in json.loads(Path(path).read_text()):
            pair = pairs[row['pair_id']]
            collected.append((pair, row))
            if row['layer'] == 31 and row['condition'] == 'answer_vector':
                if row['first_token'] != baselines[pair['donor']]['first_token']:
                    raise ValueError('answer-vector software control did not copy donor digit')
                positive += 1
            elif row['condition'] == 'identity_sham' or row['layer'] == 31:
                if row['first_token'] != replays[pair['id']]['first_token']:
                    raise ValueError('analytic zero-effect control changed recipient digit')
                if row['condition'] == 'identity_sham': shams += 1
                else: negative += 1
            if row['condition'].startswith('random_') or row['condition'] == 'unrelated_position':
                target = row['target_effective_norm']
                error = abs(row['actual_effective_norm'] - target)
                max_norm_error = max(max_norm_error, error / target if target else error)
    summary = json.loads((root / 'summary.json').read_text())
    n_pairs = summary['directed_pairs']
    if (positive, negative, shams) != (n_pairs, 5 * n_pairs, len(config['layers']) * n_pairs):
        raise ValueError('analytic control coverage differs')
    controls = dict(status='passed' if n_pairs else 'not_run_gate_failed', answer_vector_donor_matches=positive,
        final_earlier_token_unchanged=negative, identity_shams_unchanged=shams,
        max_relative_effective_norm_error=max_norm_error)
    lines = ['# ' + config['report_title'], '',
        f"All {checked['baseline_cases']:,} baseline responses are audited ({checked['baseline_correct']} correct). "
        f"The answer-digit boundary and generation-prefill checks passed on every baseline. "
        f"The registered workload completed {checked['intervention_forwards']:,} intervention forwards. "
        'All cases are discovery data; generated final/extrapolation outcomes remain sealed.', '']
    baseline_cells = []
    for family in sorted({c['record']['family'] for c in data['cases'].values()}):
        for mapping, query in product((0, 1), (0, 1)):
            targets = ('buffer', 'unused') if config['assay'] == 'swap_reset' else (None,)
            for reset in targets:
                selected = [baselines[key] for key, c in data['cases'].items() if c['record']['family'] == family
                    and c['record']['mapping'] == mapping and c['record']['query'] == query
                    and (reset is None or c['record']['reset_target'] == reset)]
                baseline_cells.append(dict(family=family, mapping=mapping, query=query, reset_target=reset,
                    n=len(selected), correct=sum(b['correct'] for b in selected), invalid=sum(b['prediction'] is None for b in selected)))
    lines += ['| Family | Mapping | Query | Reset | Correct / n | Invalid |', '|---|---:|---:|---|---:|---:|']
    for cell in baseline_cells:
        lines.append(f"| {cell['family']} | {cell['mapping']} | {cell['query']} | {cell['reset_target'] or 'fixed'} | {cell['correct']}/{cell['n']} | {cell['invalid']} |")
    lines += ['', '![Registered intervention cells](' + Path(config['figure']).name + ')', ''] if collected else ['']
    baseline_pair_changes, detail, anchor_comparison = [], [], None
    if config['assay'] == 'swap_reset':
        if config['generation'].get('anchor_baselines'):
            path=config['generation']['anchor_baselines']
            if sha(path)!=config['generation']['anchor_baselines_sha256']:
                raise ValueError('original anchor responses changed')
            previous=json.loads(Path(path).read_text())
            anchors=[(key,c) for key,c in data['cases'].items() if c['record']['reset_target']=='buffer']
            changes=[dict(id=key,anchor_id=c['record']['anchor_id'],old_prediction=previous[c['record']['anchor_id']]['prediction'],new_prediction=baselines[key]['prediction'])
                for key,c in anchors if previous[c['record']['anchor_id']]['prediction']!=baselines[key]['prediction']]
            anchor_comparison=dict(cases=len(anchors),matching_predictions=len(anchors)-len(changes),
                old_correct=sum(previous[c['record']['anchor_id']]['correct'] for key,c in anchors),
                new_correct=sum(baselines[key]['correct'] for key,c in anchors),changed_predictions=changes,
                interpretation='Identical registered anchor inputs, different execution batch/hardware if granted; every prediction difference retained.')
            lines += [f"Original anchor replay: {anchor_comparison['matching_predictions']}/{len(anchors)} parsed predictions match "
                f"({anchor_comparison['old_correct']} previously correct, {anchor_comparison['new_correct']} now correct). "
                'Paired reset effects below use the two conditions measured together in this run.', '']
        lines += ['The two prompts differ only in the final, output-irrelevant assignment identifier. '
            'All live query values, statement counts, literals and token lengths match. Full final states and the number of distinct identifiers differ; '
            'the effect cannot separate lexical cues from resetting a reused temporary. '
            'The prior failure cell (swapped mapping, second-variable query) was nominated from earlier discovery results.', '']
        for mapping, query in product((0, 1), (0, 1)):
            selected = [p for p in pairs.values() if not p['reverse'] and p['mapping'] == mapping and data['cases'][p['recipient']]['record']['query'] == query]
            counts = dict(mapping=mapping, query=query, n=len(selected),
                both_correct=sum(baselines[p['recipient']]['correct'] and baselines[p['donor']]['correct'] for p in selected),
                buffer_only_correct=sum(baselines[p['recipient']]['correct'] and not baselines[p['donor']]['correct'] for p in selected),
                unused_only_correct=sum(not baselines[p['recipient']]['correct'] and baselines[p['donor']]['correct'] for p in selected),
                both_wrong=sum(not baselines[p['recipient']]['correct'] and not baselines[p['donor']]['correct'] for p in selected))
            baseline_pair_changes.append(counts)
        lines += ['Paired baseline changes (unused-only correct denotes improvement after changing the dead identifier):', '',
            '| Mapping | Query | n | Both correct | Buffer only | Unused only | Both wrong |', '|---:|---:|---:|---:|---:|---:|---:|']
        for cell in baseline_pair_changes:
            lines.append('| ' + ' | '.join(str(cell[k]) for k in ('mapping','query','n','both_correct','buffer_only_correct','unused_only_correct','both_wrong')) + ' |')
        lines += ['', 'Intervention targets are the correct digit versus the other binding, not a changed oracle output. '
            'Each direction includes every paired case. The corresponding unpatched token accuracy is shown with the patched accuracy; '
            'a high patched accuracy alone is not a repair effect.', '',
            '| Mapping | Query | Donor → recipient | Block | Condition | n | Unpatched correct (%) | Patched correct (%) | Correct-vs-other log-odds change |',
            '|---:|---:|---|---:|---|---:|---:|---:|---:|']
        for mapping, query, reverse, layer, condition in product((0,1),(0,1),(False,True),config['layers'],conditions(config)):
            selected = [(p,r) for p,r in collected if p['mapping']==mapping and data['cases'][p['recipient']]['record']['query']==query
                        and p['reverse']==reverse and r['layer']==layer and r['condition']==condition]
            if not selected: continue
            n=len(selected)
            before=sum(replays[p['id']]['first_token']==r['target_token'] for p,r in selected)/n
            after=sum(r['first_token']==r['target_token'] for p,r in selected)/n
            delta=sum(r['target_logprob']-r['original_logprob']-(replays[p['id']]['digit_logprobs'][p['replacement']-1]
                -replays[p['id']]['digit_logprobs'][p['baseline_answer']-1]) for p,r in selected)/n
            item=dict(mapping=mapping,query=query,reverse=reverse,layer=layer,condition=condition,n=n,
                      unpatched_correct_rate=before,patched_correct_rate=after,logodds_change=delta)
            detail.append(item)
            lines.append(f"| {mapping} | {query} | {'buffer → unused' if reverse else 'unused → buffer'} | {layer} | {condition} | {n} | {100*before:.2f} | {100*after:.2f} | {delta:.3f} |")
    else:
        gate=checked['baseline_gate']
        lines += ['The reliability gate requires ≥90% accuracy, ≤5% invalid outputs and at least 24 cases in every mapping/query cell of a family. '
            'Failed families retain all baseline outcomes and receive no interventions. '
            f"Eligible families: {', '.join(gate['eligible_families']) or 'none'}. "
            'The planned transfer site is an unchanged final operand token after one changed earlier operand. '
            'All relevant results are absent from every literal in both programs. This need not isolate an abstract sum representation; '
            'the vector could transport operand information for later recomputation.', '',
            '| Family | Block | Condition | n affected / unchanged | Replacement, affected (%) | Replacement, unchanged (%) |',
            '|---|---:|---|---:|---:|---:|']
        lookup={(r['family'],r['layer'],r['condition'],r['affected']):r for r in checked.get('results',[]) if not r['both_baselines_correct_only']}
        for family in ('ownership','versions'):
            if family not in gate['eligible_families']:
                lines.append(f'| {family} | — | skipped: gate failed | 0 | — | — |')
                continue
            for layer,condition in product(config['layers'],conditions(config)):
                a,b=[lookup[family,layer,condition,affected] for affected in (True,False)]
                lines.append(f"| {family} | {layer} | {condition} | {a['n']}/{b['n']} | {100*a['replacement_token_rate']:.2f} | {100*b['replacement_token_rate']:.2f} |")
    if collected:
        labels=['Primary','Unrelated','Answer','Sham','Random 11','Random 29','Random 47']
        fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
        for i in range(2):
            for j in range(2):
                ax=axes[i,j]
                if config['assay']=='swap_reset':
                    selected={(r['layer'],r['condition']):r['patched_correct_rate'] for r in detail if r['mapping']==1 and r['query']==i and r['reverse']==bool(j)}
                    title=f"Swapped query {i}: " + ('buffer → unused' if j else 'unused → buffer')
                else:
                    family=['ownership','versions'][i];affected=j==0
                    selected={(r['layer'],r['condition']):r['replacement_token_rate'] for r in checked.get('results',[])
                        if r['family']==family and r['affected']==affected and not r['both_baselines_correct_only'] and r['n']}
                    title=family+(': affected' if affected else ': unchanged answer')
                if not selected:
                    ax.set_axis_off();ax.text(.5,.5,title+'\nSkipped: reliability gate',ha='center',va='center');continue
                values=np.array([[100*selected[layer,condition] for condition in conditions(config)] for layer in config['layers']])
                ax.imshow(values,vmin=0,vmax=100,cmap='viridis',aspect='auto')
                ax.set_title(title);ax.set_xticks(range(7),labels,rotation=35,ha='right');ax.set_yticks(range(len(config['layers'])),config['layers']);ax.set_ylabel('Raw block')
                for x,y in product(range(len(config['layers'])),range(7)):
                    ax.text(y,x,f'{values[x,y]:.1f}',ha='center',va='center',fontsize=9,color='black' if values[x,y]>55 else 'white')
        fig.suptitle(config['report_title']+' (%)')
        fig.savefig(config['figure']);fig.savefig(Path(config['figure']).with_suffix('.png'),dpi=150);plt.close(fig)
    control_text=(f"Analytic controls passed: {positive} final answer-vector donor copies, {negative} final-block earlier-token controls and {shams} identity shams. "
        f"Maximum relative norm mismatch: {100*max_norm_error:.4f}% (allowed 3%). ") if n_pairs else 'No intervention or analytic intervention-control tests ran because the reliability gate failed. '
    lines += ['',control_text+
        'The final answer-vector condition is an answer-copy software control. '
        'These are next-token interventions, not complete-output intervention accuracy. '
        'Numeric variants, directions and two lexical realizations are not independent structural replications. '
        'No general binding register, computed-value abstraction or held-out error predictor is established.', '',
        f"Audit: `{root/'audit.json'}`. [Design](routing_extension_plan.md). "
        f"Reproduce with `PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/112_binding_routing_extension.py review {config['config_path']}`."]
    report,artifact=Path(config['report']),Path(config['review_artifact'])
    if analysis_revision is not None:
        if not analysis_revision.isalnum(): raise ValueError('analysis revision must be alphanumeric')
        report=report.with_stem(report.stem+'_analysis_'+analysis_revision)
        artifact=artifact.with_stem(artifact.stem+'_analysis_'+analysis_revision)
    immutable(report, ('\n'.join(lines)+'\n').encode())
    result=dict(status='complete_audited',assay=config['assay'],report=str(report),audit=str(root/'audit.json'),
        audit_sha256=sha(root/'audit.json'),baseline_cases=checked['baseline_cases'],baseline_correct=checked['baseline_correct'],
        baseline_cells=baseline_cells,baseline_pair_changes=baseline_pair_changes,intervention_forwards=checked['intervention_forwards'],
        baseline_gate=checked['baseline_gate'],analytic_controls=controls,intervention_cells=detail,
        anchor_replay_comparison=anchor_comparison,
        full_counterfactual_rows=checked.get('results',[]),generated_holdouts_opened=False)
    immutable(artifact,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return {k:v for k,v in result.items() if k not in ('baseline_cells','baseline_pair_changes','intervention_cells','full_counterfactual_rows')}
