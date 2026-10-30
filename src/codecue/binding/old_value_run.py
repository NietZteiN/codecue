"""Discovery calibration of previous versus current assignment-value queries.

An isolated adapter reuses the audited native preparation, vLLM, checkpoint,
response-repair and invocation-accounting paths.  The historical question is
new: prompts show the full assignment body, while its independent oracle runs
only the prefix before the target's last write.  The legacy internal section
name ``computation_routing`` is an adapter tag, not a claim about this task.
"""
from __future__ import annotations

from collections import defaultdict
import importlib.util
from pathlib import Path
import sys
import types

from .datasets import digest

ROLE = 'discovery_old_value_calibration_v1'
PRIMARY_STORAGE = ('absent_all_current', 'retained_other_current')
STORAGE = (*PRIMARY_STORAGE, 'equal_current')
MODES = ('current', 'previous')
SPLITS = ('train', 'development')
LIMITATION = (
    'Fresh adaptive historical-versus-current retrieval calibration on familiar '
    'literal/copy graphs, using three fixed direct-answer instructions. Previous '
    'means the target value immediately before its last assignment, not the '
    'current Python output. Old/current questions share their entire body. Equal '
    'old/current answers are controls outside the fixed reliability gate. '
    'An old numeric value can survive elsewhere or be absent from every final '
    'slot; these primary strata remain separate. Literal rereading can solve '
    'history questions, so accuracy does not establish maintained neural state '
    'or causal use. Related numeric, lexical, rotation and query views are not '
    'independent structural replication. No instruction is selected, no new '
    'interval is computed, and no causal intervention automatically follows a '
    'passing gate. Historical failures and sealed outcomes remain unchanged.'
)


def _programs():
    from . import old_value_programs
    return old_value_programs


def _clone_file(name, filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(__package__+'.'+name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _checkpoint_adapter():
    path = Path(__file__).with_name('checkpoint_suite.py')
    source = path.read_text()
    old = 'from .computation_routing_programs import '
    if source.count(old) != 4:
        raise ValueError('checkpoint adapter requires the four audited program imports')
    module = types.ModuleType(__package__+'._old_value_checkpoint_suite')
    module.__file__ = str(path)
    module.__package__ = __package__
    sys.modules[module.__name__] = module
    exec(compile(source.replace(old, 'from .old_value_programs import '), str(path), 'exec'), module.__dict__)
    return module


def _cohort(rows):
    """Source-only grouping/pair checks before native preparation or inference."""
    seen = set(); pairs = defaultdict(dict); groups = defaultdict(set); cells = defaultdict(set)
    for row in rows:
        key = row['id']
        if key in seen or row['query_mode'] not in MODES or row['old_storage'] not in STORAGE or row['split'] not in SPLITS:
            raise ValueError('unique declared old/current source factors required')
        seen.add(key); groups[row['component_id']].add(row['split'])
        pair = pairs[row['pair_id']]
        if row['query_mode'] in pair:
            raise ValueError('duplicate old/current pair member')
        pair[row['query_mode']] = row
        if row['old_storage'] in PRIMARY_STORAGE:
            cells[row['split'],row['query_mode'],row['old_storage']].add(digest([row['body'], row['target_slot']]))
    expected = {(split, mode, storage) for split in SPLITS for mode in MODES for storage in PRIMARY_STORAGE}
    if set(cells) != expected or any(len(values) < 24 for values in cells.values()):
        raise ValueError('every primary source cell requires at least24 distinct body/target inputs')
    if any(len(splits) != 1 for splits in groups.values()):
        raise ValueError('canonical graph relatives must stay split disjoint')
    for pair in pairs.values():
        if set(pair) != set(MODES): raise ValueError('complete old/current source pairs required')
        old, current = pair['previous'], pair['current']
        fields = ('body','component_id','split','old_storage','target_slot','target_update_count',
                  'last_write_lag','lexical_realization','profile_id')
        if any(old[field] != current[field] for field in fields):
            raise ValueError('old/current questions must share body, target and source strata')
        if (old['expected_answer'] == current['expected_answer']) != (old['old_storage'] == 'equal_current'):
            raise ValueError('equality control and different-value primary status differ')
    return pairs


def _point(items):
    scores = [score for _,score,_ in items]
    n = len(scores); correct = sum(bool(s['correct']) for s in scores)
    invalid = sum(not s['valid'] for s in scores); grouped = defaultdict(list)
    for row, score, _ in items: grouped[row['component_id']].append(bool(score['correct']))
    by_graph = {group:dict(n=len(values),correct=sum(values),accuracy=sum(values)/len(values))
                for group,values in sorted(grouped.items())}
    return dict(n=n,correct=correct,invalid=invalid,valid=n-invalid,
        accuracy=correct/n if n else None,invalid_rate=invalid/n if n else None,
        unique_source_n=len({row['id'] for row,_,_ in items}),
        unique_body_target_n=len({digest([row['body'],row['target_slot']]) for row,_,_ in items}),
        unique_prompt_n=len({prompt for _,_,prompt in items}),graph_groups=len(grouped),
        group_macro_accuracy=(sum(v['accuracy'] for v in by_graph.values())/len(by_graph) if by_graph else None),
        per_graph=by_graph,uncertainty='Descriptive; related views remain grouped, no confidence interval.')


def summarize(records, config):
    records = list(records); variants = _CORE._variants(); rows,_ = _CORE._inputs(config)
    row_map = {row['id']:row for row in rows}; expected = {(variant,key) for variant in variants for key in row_map}
    seen = set(); logical = []; pairs = defaultdict(dict); token_lengths = defaultdict(list)
    for case,response in records:
        key = case.get('variant'),case.get('id')
        if key not in expected or key in seen or case.get('kind') != 'computation_routing' or case.get('record') != row_map[key[1]]:
            raise ValueError('complete unique registered old/current response identities required')
        seen.add(key); _CORE.suite.validate_response(case,response)
        row = row_map[key[1]]; logical.append((key[0],row,response['score'],case['prompt_sha256']))
        pair = pairs[key[0],row['pair_id']]
        if row['query_mode'] in pair: raise ValueError('duplicate paired question response')
        pair[row['query_mode']] = (row,response['score'])
        token_lengths[key[0]].append((len(case['input_token_ids']),len(response['output_token_ids'])))
    if seen != expected: raise ValueError('complete three-instruction old/current coverage required')
    gates = defaultdict(list); controls = defaultdict(list); descriptive = defaultdict(list)
    for variant,row,score,prompt_hash in logical:
        value = (row,score,prompt_hash)
        category = (variant,row['query_mode'],row['old_storage'],row['split'])
        (gates if row['old_storage'] in PRIMARY_STORAGE else controls)[category].append(value)
        for axis in ('target_slot','target_update_count','last_write_lag','lexical_realization','profile_id','numeric_seed'):
            descriptive[(*category,axis,str(row[axis]))].append(value)
    expected_cells = {(variant,mode,storage,split) for variant in variants for mode in MODES
                      for storage in PRIMARY_STORAGE for split in SPLITS}
    if set(gates) != expected_cells: raise ValueError('complete fixed primary reliability matrix required')
    def cell(key,values):
        return dict(variant=key[0],query_mode=key[1],old_storage=key[2],split=key[3],**_point(values))
    gate_cells = [dict(cell(key,values),passed=(len(values)>=24
        and len({p for _,_,p in values})>=24 and _point(values)['accuracy']>=.9
        and _point(values)['invalid_rate']<=.05)) for key,values in sorted(gates.items())]
    instructions = {}
    for variant in variants:
        cells = [c for c in gate_cells if c['variant']==variant]
        train = all(c['passed'] for c in cells if c['split']=='train')
        dev = all(c['passed'] for c in cells if c['split']=='development')
        instructions[variant] = dict(status='passed' if train and dev else 'failed',
            training_qualified=train,development_descriptive_passed=dev,
            numeric_development_qualified=train and dev,behavioral_calibration_qualified=train and dev,cells=cells)
    contrast_values = defaultdict(list); paired_events = defaultdict(list)
    for (variant,_),pair in pairs.items():
        if set(pair) != set(MODES): raise ValueError('paired old/current question response missing')
        previous,pscore = pair['previous'];current,cscore = pair['current']
        if any(previous[k]!=current[k] for k in ('body','component_id','split','old_storage','target_slot')):
            raise ValueError('paired body/target/source identities differ')
        category = variant,previous['split'],previous['old_storage']
        contrast_values[category].append((previous['component_id'],int(pscore['correct'])-int(cscore['correct'])))
        paired_events[category].append(dict(both_correct=pscore['correct'] and cscore['correct'],
            previous_only_correct=pscore['correct'] and not cscore['correct'],
            current_only_correct=cscore['correct'] and not pscore['correct'],
            neither_correct=not pscore['correct'] and not cscore['correct'],
            previous_answered_current=pscore['valid'] and not pscore['correct'] and pscore['prediction']==current['expected_answer'],
            current_answered_previous=cscore['valid'] and not cscore['correct'] and cscore['prediction']==previous['expected_answer'],
            invalid_previous=not pscore['valid'],invalid_current=not cscore['valid']))
    contrasts = []
    for key,values in sorted(contrast_values.items()):
        grouped = defaultdict(list)
        for group,value in values:grouped[group].append(value)
        per_graph = {group:dict(n=len(v),previous_minus_current=sum(v)/len(v)) for group,v in sorted(grouped.items())}
        contrasts.append(dict(variant=key[0],split=key[1],old_storage=key[2],paired_n=len(values),graph_groups=len(grouped),
            previous_minus_current=sum(v for _,v in values)/len(values),
            group_macro_previous_minus_current=sum(v['previous_minus_current'] for v in per_graph.values())/len(per_graph),
            per_graph=per_graph,paired_outcomes={name:sum(bool(event[name]) for event in paired_events[key])
                for name in ('both_correct','previous_only_correct','current_only_correct','neither_correct',
                             'previous_answered_current','current_answered_previous','invalid_previous','invalid_current')},
            confidence_interval=None,scope='Descriptive matched body/target pairs; familiar discovery graphs.'))
    overall = _point([(r,s,p) for _,r,s,p in logical])
    return dict(status='complete_audited',complete=True,evaluation_role=ROLE,config_hash=digest(config),
        **overall,scored_unique_cases=len(records),logical_responses=len(records),logical_source_views=len(rows),
        unique_sources=len(rows),source_body_target_pairs=len(rows)//2,instructions=list(variants),
        query_modes=list(MODES),primary_storage=list(PRIMARY_STORAGE),gate_cells=gate_cells,
        equality_control_cells=[cell(k,v) for k,v in sorted(controls.items())],
        descriptive_cells=[dict(cell(k,v),axis=k[4],value=k[5]) for k,v in sorted(descriptive.items())],
        paired_contrasts=contrasts,prompt_geometry={variant:dict(n=len(lengths),
            input_min=min(x[0] for x in lengths),input_max=max(x[0] for x in lengths),
            output_min=min(x[1] for x in lengths),output_max=max(x[1] for x in lengths))
            for variant,lengths in token_lengths.items()},
        reliability_gate=dict(thresholds=THRESHOLDS,instructions=instructions,
            status='passed' if all(g['behavioral_calibration_qualified'] for g in instructions.values()) else 'failed',
            selection='All three fixed instructions and both different-value storage categories retained; equality controls excluded prospectively.',
            causal_design_review_required=True,automatic_causal_launch=False),
        new_fits=0,generated_holdouts_opened=False,new_intervals=False,limitation=LIMITATION)


def _report(result):
    lines = ['# Previous versus current value retrieval calibration','',LIMITATION,'',
        f"{result['n']:,} scored responses; {result['correct']:,} correct and {result['invalid']:,} invalid. "
        f"Confirmed warm-up requests: {result['accounting']['confirmed_warmup_requests']:,}.",'',
        'Each instruction × question mode × different-value storage category × split cell requires at least24 responses and24 unique prompts, accuracy at least90%, and invalid rate at most5%. Equality controls remain separate. All instructions stay visible; a passing gate triggers morning design review only.','',
        '| Instruction | Training qualified | DEV descriptive pass | Behavioral calibration qualified |',
        '|---|---|---|---|']
    for variant,gate in result['reliability_gate']['instructions'].items():
        lines.append(f"| {variant} | {gate['training_qualified']} | {gate['development_descriptive_passed']} | {gate['behavioral_calibration_qualified']} |")
    lines += ['', '| Instruction | Mode | Old numeric value | Split | Correct / n | Unique prompts | Invalid |',
              '|---|---|---|---|---:|---:|---:|']
    for cell in result['gate_cells']+result['equality_control_cells']:
        lines.append(f"| {cell['variant']} | {cell['query_mode']} | {cell['old_storage']} | {cell['split']} | {cell['correct']}/{cell['n']} | {cell['unique_prompt_n']} | {cell['invalid']} |")
    lines += ['', '| Instruction | Split | Old numeric value | Paired n | Previous minus current | Previous answered current | Current answered previous |',
              '|---|---|---|---:|---:|---:|---:|']
    for pair in result['paired_contrasts']:
        errors=pair['paired_outcomes']
        lines.append(f"| {pair['variant']} | {pair['split']} | {pair['old_storage']} | {pair['paired_n']} | {100*pair['previous_minus_current']:.3f} pp | {errors['previous_answered_current']} | {errors['current_answered_previous']} |")
    lines += ['', 'Current target assignment version is overwrite-count plus1; previous target assignment version equals overwrite-count. These version cells are retained through question mode and the overwrite-count strata.','', 'All per-graph, owner, overwrite-count, recency, lexical, numeric-seed and profile strata, paired question differences and exact prompt/output token geometry remain in the machine review. Old-value questions can be solved by rereading the visible literals; these results do not establish retained latent state or causal use. No confidence interval or independent-trial claim is assigned to related views.','']
    return '\n'.join(lines).replace('least24','least 24').replace('and24','and 24').replace('least90%','least 90%').replace('most5%','most 5%').replace('plus1','plus 1')


def _adapter():
    engine = _clone_file('_old_value_execution','computation_routing_run.py')
    engine.ROLE = ROLE; engine.LIMITATION = LIMITATION; engine._programs = _programs
    engine.suite = _checkpoint_adapter()
    old_config = engine._config
    def config(value):
        result=old_config(value);variants=engine._variants();tokens=value.get('max_new_tokens')
        expected={variant:engine._programs().instruction_spec(variant)['max_new_tokens'] for variant in variants}
        if (expected!={variant:16 for variant in variants} or not isinstance(tokens,dict)
                or set(tokens)!=set(variants) or any(type(n) is not int or n!=16 for n in tokens.values())):
            raise ValueError('fixed16-token instruction ceilings required')
        return result
    engine._config=config
    old_inputs = engine._inputs
    def inputs(config):
        rows,manifest = old_inputs(config); _cohort(rows); return rows,manifest
    old_prepared=engine._prepared
    def prepared(value,source):
        qa,cases=old_prepared(value,source);native_cells=defaultdict(set)
        for case in cases:
            ids=case.get('input_token_ids')
            if (type(case.get('max_new_tokens')) is not int or case['max_new_tokens']!=16
                    or case.get('stop')!=['\n\n'] or not isinstance(case.get('prompt'),str)
                    or case.get('prompt_sha256')!=digest(case['prompt']) or not isinstance(ids,list)
                    or not ids or any(type(token) is not int or token<0 for token in ids)
                    or len(ids)+16>value['context_limit']):
                raise ValueError('prepared prompt, native IDs or fixed16-token generation ceiling differs')
            row=case['record']
            if row['old_storage'] in PRIMARY_STORAGE:
                native_cells[case['variant'],row['split'],row['query_mode'],row['old_storage']].add(digest(ids))
        expected={(variant,split,mode,storage) for variant in engine._variants() for split in SPLITS
                  for mode in MODES for storage in PRIMARY_STORAGE}
        if set(native_cells)!=expected or any(len(values)<24 for values in native_cells.values()):
            raise ValueError('each primary native-token cell requires at least24 distinct prompts')
        return qa,cases
    engine._inputs=inputs;engine._prepared=prepared;engine.summarize=summarize;engine._report=_report
    return engine


_CORE = _adapter()
THRESHOLDS = _CORE.THRESHOLDS
MODELS = _CORE.MODELS
metadata = _CORE.metadata
preflight = _CORE.preflight
run = _CORE.run
audit = _CORE.audit
review = _CORE.review
_config = _CORE._config
_inputs = _CORE._inputs
_source = _CORE._source
_prepared = _CORE._prepared
_responses = _CORE._responses
_attempt_history = _CORE._attempt_history
