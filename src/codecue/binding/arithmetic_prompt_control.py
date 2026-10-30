"""Matched print/query-wording controls; original responses are reused, not rerun."""
from __future__ import annotations

import ast
from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

from . import arithmetic_graph_capture as capture, overnight_relationship_behavior as durable
from . import relationship_capture as base
from .datasets import digest
from .interpreter import execute as original_execute
from .model_adapter import normalize_prompt

ROLE='discovery_arithmetic_prompt_control_v1'
INSTRUCTIONS=(base.INSTRUCTION,
    'Execute the assignments in order. The last line identifies the variable to report, either directly or inside print. Return its final value as a signed integer with no other text.',
    'Track each variable through all assignments, including overwrites. Report the integer named on the last line; if it is inside print(...), report that printed value. Reply with only the signed integer.')
ARMS=tuple(f'{form}_i{i}' for i in range(3) for form in ('bare','print'))
NEW_ARMS=tuple(a for a in ARMS if a!='bare_i0')
_BASELINE=[]
_QUERY_KINDS={}


def query_kind(record):
    tree=ast.parse(record['canonical_source'])
    name=tree.body[-1].value.id
    return 'arithmetic_written' if any(n.targets[0].id==name for n in tree.body[4:8]) else 'untouched_literal'


def printed(source):
    tree=ast.parse(source)
    if not isinstance(tree.body[-1],ast.Expr) or not isinstance(tree.body[-1].value,ast.Name):
        raise ValueError('one bare queried variable required')
    body,query=source.rsplit('\n',1)
    return body+'\nprint('+query.strip()+')'


def semantic_execute(source):
    tree=ast.parse(source);last=tree.body[-1].value
    if isinstance(last,ast.Call):
        if (not isinstance(last.func,ast.Name) or last.func.id!='print' or len(last.args)!=1
                or last.keywords or not isinstance(last.args[0],ast.Name)):
            raise ValueError('only a final print(variable) wrapper is allowed')
        tree.body[-1].value=last.args[0]
        source=ast.unparse(tree)
    return original_execute(source)


def variant_record(record,arm):
    if arm not in ARMS:raise ValueError('declared prompt arm required')
    value=deepcopy(record)
    value.update(id=record['id']+':'+arm,format_pair_id=record['id'],source_form=arm)
    if arm.startswith('print'):
        value['source']=printed(record['source'])
        value['canonical_source']=printed(record['canonical_source'])
    if semantic_execute(value['canonical_source'])['expected_answer']!=original_execute(record['canonical_source'])['expected_answer']:
        raise ValueError('query wrapper changed its intended value')
    return value


spec=importlib.util.spec_from_file_location(__package__+'._prompt_behavior_engine',durable.__file__)
_CORE=importlib.util.module_from_spec(spec);spec.loader.exec_module(_CORE)
_CORE.ROLE=ROLE
_CORE.capture=capture._CORE
_CORE.execute=semantic_execute
_CORE.LIMITATION='Adaptive matched discovery on reused program families. Print syntax and wording change token context. Original outcomes and parser remain unchanged; no causal or confirmatory claim.'
_CORE.REPORT_TITLE='Arithmetic prompt/output semantics control'
_CORE.COMPARISON_LABEL='Matched DEV prompt contrasts'
_legacy_config=_CORE._config


def _config(config):
    _legacy_config(config)
    if config['generation_batch_size']!=64:
        raise ValueError('prospectively fixed generation batch64 required')


_CORE._config=_config


def protocol():
    return dict(selection='five new form/wording arms on all original numeric_draw0 cases; bare_i0 responses cached',
        arms=list(ARMS),new_arms=list(NEW_ARMS),instructions=list(INSTRUCTIONS),do_sample=False,
        max_new_tokens=12,use_cache=True,parser='full signed decimal integer with whitespace only',
        uncertainty='2000 fixed-parameter resamples of whole DEV families; relatives not independent')


def _baseline(config):
    cap=base._json(config['capture_config'],config['capture_config_sha256'])
    old_preflight,cases=capture.inputs(cap)
    originals=[c for c in cases if c['record']['numeric_draw']==0]
    folder=Path(cap['run_dir']).parent/'behavior'
    receipt=base._json(folder/'completion_manifest_v1.json')
    summary=base._json(folder/'summary.json')
    registration=base._json(folder/'registration.json')
    base._verify_source(registration['config'],receipt['source'])
    if (receipt['source']!=old_preflight['source'] or summary['source']!=receipt['source']
            or summary['model']!=cap['model'] or summary['cases']!=1152
            or registration['config']['capture_config_sha256']!=config['capture_config_sha256']):
        raise ValueError('cached baseline model/source provenance differs')
    for pin in receipt['artifacts'].values():
        if base._sha(pin['path'])!=pin['sha256']:raise ValueError('cached baseline artifact changed')
    entry=receipt['artifacts']['responses']
    if base._sha(entry['path'])!=entry['sha256']:raise ValueError('cached baseline response pin differs')
    responses=durable.read_responses(entry['path'],originals)
    if len(originals)!=1152 or len(responses)!=1152:raise ValueError('complete original baseline required')
    return cap,originals,responses,entry,receipt


def prepare(config):
    import contextlib,io
    _CORE._config(config);base._slurm();source=base._current_source(config)
    if base._sha(config['declared_plan'])!=config['declared_plan_sha256']:raise ValueError('declared prompt plan changed')
    cap,originals,responses,entry,baseline_receipt=_baseline(config)
    tokenizer=capture._CORE._tokenizer(cap)
    recipe,_=capture._CORE._config(cap)
    cases=[]
    for original in originals:
        record=original['record']
        for arm in ARMS:
            row=variant_record(record,arm)
            instruction=INSTRUCTIONS[int(arm[-1])]
            prompt=normalize_prompt(tokenizer,tokenizer.apply_chat_template(
                [{'role':'user','content':instruction+'\n\n'+row['source']}],tokenize=False,add_generation_prompt=True)+'Output:')
            tokens=tokenizer(prompt,add_special_tokens=False)['input_ids']
            if len(tokens)>recipe['context_limit']:raise ValueError('declared native context exceeded')
            if arm=='bare_i0':
                if prompt!=original['prompt'] or tokens!=original['input_token_ids']:
                    raise ValueError('cached baseline native prompt/token IDs differ')
            else:cases.append(dict(record=row,prompt=prompt,input_token_ids=tokens))
        # Independent ordinary-Python print output verifies transformed labels.
        text=printed(record['source']);buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compile(text,'<controlled-print>','exec'),{'__builtins__':{'print':print}}, {})
        if durable.parse_integer(buffer.getvalue())!=original_execute(record['canonical_source'])['expected_answer']:
            raise ValueError('ordinary Python printed output disagrees with original oracle')
    if len(cases)!=5760 or len({c['record']['id'] for c in cases})!=5760:raise ValueError('complete unique five-arm cohort required')
    folder=Path(config['run_dir']);payload=''.join(json.dumps(c,sort_keys=True)+'\n' for c in cases).encode()
    base._publish(folder/'prepared_prompt_cases.jsonl',payload)
    value=dict(status='passed',config=config,config_hash=digest(config),source=source,cases=len(cases),
        prepared_sha256=hashlib.sha256(payload).hexdigest(),baseline=entry,
        baseline_source=baseline_receipt['source'],
        baseline_receipt_sha256=base._sha(Path(cap['run_dir']).parent/'behavior/completion_manifest_v1.json'),
        max_prompt_tokens=max(len(c['input_token_ids']) for c in cases),baseline_prompt_matches=1152,
        independent_print_outputs=1152,new_model_queries=0,generated_holdouts_opened=False)
    base._put(folder/'preparation_review.json',value)
    return value


def inputs(config):
    global _BASELINE,_QUERY_KINDS
    _CORE._config(config)
    cap,originals,baseline,entry,baseline_receipt=_baseline(config)
    folder=Path(config['run_dir']);preflight=base._json(folder/'preparation_review.json')
    if preflight['config']!=config or preflight['config_hash']!=digest(config) or preflight['baseline']!=entry:
        raise ValueError('native prompt preparation identity changed')
    if (preflight['baseline_source']!=baseline_receipt['source'] or preflight['baseline_receipt_sha256']!=
            base._sha(Path(cap['run_dir']).parent/'behavior/completion_manifest_v1.json')):
        raise ValueError('cached baseline receipt changed after preparation')
    base._verify_source(config,preflight['source'])
    payload=(folder/'prepared_prompt_cases.jsonl').read_bytes()
    if hashlib.sha256(payload).hexdigest()!=preflight['prepared_sha256']:raise ValueError('prepared prompts changed')
    cases=[json.loads(s) for s in payload.splitlines()]
    expected=[variant_record(c['record'],arm) for c in originals for arm in NEW_ARMS]
    if [c['record'] for c in cases]!=expected or len(cases)!=5760:raise ValueError('prompt variant records changed')
    _BASELINE=[]
    _QUERY_KINDS={c['record']['id']:query_kind(c['record']) for c in originals}
    for response in baseline:
        row=dict(response,id=response['id']+':bare_i0',format_pair_id=response['id'],source_form='bare_i0')
        _BASELINE.append(row)
    return cap,preflight,cases


def summarize(rows,baseline=None,query_kinds=None):
    combined=list(_BASELINE if baseline is None else baseline)+list(rows)
    kinds=_QUERY_KINDS if query_kinds is None else query_kinds
    cells=defaultdict(list);pairs=defaultdict(dict)
    for row in combined:
        for key in ('all/'+row['source_form'],row['split']+'/'+row['source_form']):cells[key].append(row)
        if kinds:
            cells[row['split']+'/'+kinds[row['format_pair_id']]+'/'+row['source_form']].append(row)
        if row['split']=='development':pairs[row['format_pair_id']][row['source_form']]=row
    metrics={key:dict(rows=len(values),accuracy=float(np.mean([r['correct'] for r in values])),
        invalid_fraction=float(np.mean([r['parsed'] is None for r in values]))) for key,values in cells.items()}
    contrasts={}
    for left,right in [('print_i0','bare_i0'),('bare_i1','bare_i0'),('bare_i2','bare_i0'),
                       ('print_i1','bare_i1'),('print_i2','bare_i2')]:
        for stratum in (('all','arithmetic_written','untouched_literal') if kinds else ('all',)):
            grouped=defaultdict(list);flat=[]
            for pair_id,variants in pairs.items():
                if set(variants)!=set(ARMS):raise ValueError('all six paired arms required')
                if stratum!='all' and kinds[pair_id]!=stratum:continue
                a,b=variants[left],variants[right]
                if a['component_id']!=b['component_id'] or a['expected_answer']!=b['expected_answer']:
                    raise ValueError('matched prompt states differ')
                delta=int(a['correct'])-int(b['correct'])
                grouped[a['component_id']].append(delta);flat.append(delta)
            if grouped:
                means=np.asarray([np.mean(grouped[g]) for g in sorted(grouped)])
                draws=np.random.default_rng(117).integers(0,len(means),(2000,len(means)))
                key=('' if stratum=='all' else stratum+':')+left+'_minus_'+right
                contrasts[key]=dict(paired_rows=len(flat),families=len(means),
                    row_weighted_difference=float(np.mean(flat)),family_macro_difference=float(means.mean()),
                    conditional_family_bootstrap_95=np.quantile(means[draws].mean(axis=1),[.025,.975]).tolist())
    return dict(cells=metrics,computed_literal=contrasts)


_CORE._inputs=inputs
_CORE.protocol=protocol
_CORE.summarize=summarize


def run(config):
    source=base._current_source(config)
    proof=base._json(Path(config['run_dir']).parent/'software_review.json')
    if proof.get('status')!='passed' or proof['source']['code']!=source['source_sha256']:
        raise ValueError('matching software validation required before model work')
    return _CORE.run(config)


audit=_CORE.audit
