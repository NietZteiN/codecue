"""Outcome-isolated features for an exploratory discovery failure baseline.

Input columns use the visible source AST and saved prompt length only. Extra
columns use one distinct, semantics-matched neutral query. Its correctness is
an explicitly separate oracle-scored tier; no target response enters features.
This collector never fits a mechanism predictor or opens reserved outcomes.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path

from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, sha

ROLE='discovery_failure_prediction_features_v1'
INPUT_COLUMNS=(
    'prompt_tokens','source_chars','statements','variables','assignments','copies',
    'literal_assignments','negative_literals','max_abs_literal','mean_abs_literal',
    'query_last_definition_distance','query_definition_count','query_dependency_depth',
    'available_bindings','updates','tail_after','query_saved','misleading','lexical_one',
)
NEUTRAL_RAW_COLUMNS=(
    'neutral_valid','neutral_output_tokens','neutral_response_chars',
    'neutral_prediction_value','neutral_prediction_abs',
)
NEUTRAL_SCORED_COLUMNS=('neutral_failure',)
PAIR_KEYS=('base_id','updates','tail_placement','query_role','ownership_swapped','lexical_realization')


def _signed_literal(node):
    if isinstance(node,ast.Constant) and type(node.value) is int:return node.value
    if (isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub)
            and isinstance(node.operand,ast.Constant) and type(node.operand.value) is int):
        return -node.operand.value
    return None


def source_features(case):
    """Read source syntax and declared input conditions; never interpreter truth."""
    row=case['record'];source=row['source'];tree=ast.parse(source)
    if (len(tree.body)<2 or not isinstance(tree.body[-1],ast.Expr)
            or not isinstance(tree.body[-1].value,ast.Name)):
        raise ValueError('discovery input requires assignments and a variable query')
    tokens=case['input_token_ids']
    if not isinstance(tokens,list) or any(type(value) is not int for value in tokens):
        raise ValueError('saved integer prompt token IDs required')
    depths={};last={};counts=Counter();literals=[];copies=0
    assignments=tree.body[:-1]
    for index,statement in enumerate(assignments):
        if (not isinstance(statement,ast.Assign) or len(statement.targets)!=1
                or not isinstance(statement.targets[0],ast.Name)):
            raise ValueError('only simple arithmetic-free assignments are input features')
        name=statement.targets[0].id;value=statement.value;literal=_signed_literal(value)
        if literal is not None:
            literals.append(literal);depth=1
        elif isinstance(value,ast.Name) and value.id in depths:
            copies+=1;depth=depths[value.id]+1
        else:raise ValueError('input features require literal or defined-variable copies')
        depths[name]=depth;last[name]=index;counts[name]+=1
    query=tree.body[-1].value.id
    if query not in depths:raise ValueError('queried source variable is undefined')
    if (row['available_bindings'] not in (2,4) or row['updates'] not in (1,3)
            or row['tail_placement'] not in ('before','after')
            or row['query_role'] not in ('current','saved')
            or row['condition'] not in ('neutral','informative','misleading')
            or row['lexical_realization'] not in (0,1)):
        raise ValueError('unexpected version-discovery input condition')
    values=dict(prompt_tokens=len(tokens),source_chars=len(source),statements=len(tree.body),
        variables=len(depths),assignments=len(assignments),copies=copies,
        literal_assignments=len(literals),negative_literals=sum(value<0 for value in literals),
        max_abs_literal=max(map(abs,literals),default=0),
        mean_abs_literal=sum(map(abs,literals))/len(literals) if literals else 0.,
        query_last_definition_distance=len(assignments)-1-last[query],
        query_definition_count=counts[query],query_dependency_depth=depths[query],
        available_bindings=row['available_bindings'],updates=row['updates'],
        tail_after=int(row['tail_placement']=='after'),query_saved=int(row['query_role']=='saved'),
        misleading=int(row['condition']=='misleading'),lexical_one=row['lexical_realization'])
    return {column:values[column] for column in INPUT_COLUMNS}


def _pair_key(case):
    row=case['record']
    return (case.get('section'),case.get('task') or case.get('variant'),*(row[key] for key in PAIR_KEYS))


def pair_features(cases,responses):
    """Join audited case/response pairs; target outcomes only become labels."""
    from .competition import ROLE as SOURCE_ROLE
    cases=list(cases);responses=list(responses)
    if len(cases)!=len(responses) or not cases:raise ValueError('complete discovery response coverage required')
    seen_ids=set();groups=defaultdict(dict);template_splits=defaultdict(set)
    for case,response in zip(cases,responses):
        row=case['record']
        if (case.get('kind')!='competition' or row.get('evaluation_role')!=SOURCE_ROLE
                or row.get('split') not in ('train','development')):
            raise ValueError('only competition discovery inputs and outcomes are permitted')
        if case['id']!=row['id'] or response['id']!=case['id'] or case['id'] in seen_ids:
            raise ValueError('duplicate or mismatched discovery response identities')
        seen_ids.add(case['id'])
        if row['family'] not in ('ownership','versions'):raise ValueError('unknown discovery source family')
        if row['family']!='versions':continue
        if row['condition'] not in ('neutral','informative','misleading'):
            raise ValueError('unknown naming condition')
        if row['condition'] in groups[_pair_key(case)]:raise ValueError('duplicate neutral or target pairing cell')
        groups[_pair_key(case)][row['condition']]=(case,response)
        template_splits[row['template_id']].add(row['split'])
    if not groups or any(len(splits)!=1 for splits in template_splits.values()):
        raise ValueError('missing version data or structural components cross source splits')
    output=[]
    for group in groups.values():
        if set(group)!={'neutral','informative','misleading'}:
            raise ValueError('every version input requires one distinct neutral counterpart and both target conditions')
        reference,observed=group['neutral'];ref=reference['record'];score=observed['score']
        prediction=score['prediction']
        if (type(score['valid']) is not bool or type(score['correct']) is not bool
                or score['valid']!=(prediction is not None)
                or prediction is not None and type(prediction) is not int
                or score['correct'] and not score['valid']):
            raise ValueError('neutral response score is inconsistent')
        neutral=dict(neutral_valid=int(score['valid']),neutral_output_tokens=len(observed['output_token_ids']),
            neutral_response_chars=len(observed['raw_response']),neutral_prediction_value=prediction if score['valid'] else 0,
            neutral_prediction_abs=abs(prediction) if score['valid'] else 0,
            neutral_failure=int(not score['correct']))
        for condition in ('informative','misleading'):
            target,response=group[condition];row=target['record']
            if (target['id']==reference['id'] or row['source']==ref['source']
                    or target.get('prompt_sha256') and target.get('prompt_sha256')==reference.get('prompt_sha256')
                    or row['template_id']!=ref['template_id'] or row['split']!=ref['split']
                    or row['canonical_source']!=ref['canonical_source']
                    or row['expected_answer']!=ref['expected_answer']):
                raise ValueError('neutral query must be distinct and match semantics, split and structural component')
            target_score=response['score']
            if type(target_score['correct']) is not bool or type(target_score['valid']) is not bool:
                raise ValueError('target failure labels require audited boolean scores')
            features=source_features(target);features.update(neutral)
            output.append(dict(id=target['id'],reference_id=reference['id'],template_id=row['template_id'],
                base_id=row['base_id'],original_split=row['split'],condition=condition,
                query_role=row['query_role'],available_bindings=row['available_bindings'],
                lexical_realization=row['lexical_realization'],features=features,
                label=int(not target_score['correct']),target_invalid=not target_score['valid']))
    return sorted(output,key=lambda row:row['id'])


def _source_inputs(config):
    """Verify discovery declarations/source graph before audit opens responses."""
    from .competition import ROLE as SOURCE_ROLE,assign_splits,validate_rows
    from .forecasting import _discovery_declaration,_discovery_response_path
    from .checkpoint_suite import prepared
    _discovery_declaration(config)
    source_path=Path(config['source_config'])
    if sha(source_path)!=config['source_config_sha256']:raise ValueError('pinned source configuration checksum changed')
    source=json.loads(source_path.read_text());_discovery_declaration(source)
    if any(key in config and config[key]!=source.get(key) for key in ('model','model_revision')):
        raise ValueError('collector configuration checkpoint differs from source')
    sections=source.get('sections',[])
    if (len(sections)!=1 or sections[0].get('kind')!='competition'
            or sections[0].get('variants')!=['print_direct_v3']
            or sections[0].get('dataset')!=source.get('dataset')):
        raise ValueError('one pinned direct-answer competition discovery section required')
    section=sections[0];dataset=Path(source['dataset']);stage=Path(source['run_dir'])/'checkpoint_suite'
    response_path=stage/'responses.jsonl';_discovery_response_path(response_path)
    data_manifest=json.loads(dataset.with_suffix('.manifest.json').read_text())
    _discovery_declaration(data_manifest)
    if data_manifest.get('evaluation_role')!=SOURCE_ROLE or data_manifest.get('status')!='validated':
        raise ValueError('validated competition discovery source manifest required')
    dataset_hash=sha(dataset)
    if dataset_hash!=data_manifest.get('sha256') or dataset_hash!=section.get('sha256'):
        raise ValueError('competition source dataset checksum differs')
    manifest=json.loads((stage/'manifest.json').read_text());identity=manifest.get('identity',{})
    _discovery_declaration(manifest);_discovery_declaration(identity)
    if (manifest.get('status')!='complete' or manifest.get('identity_hash')!=digest(identity)
            or identity.get('config')!=source or identity.get('model_revision')!=source.get('model_revision')
            or identity.get('tokenizer_revision')!=source.get('tokenizer_revision')
            or identity.get('dataset_manifest',{}).get('sha256')!=dataset_hash
            or identity.get('dataset_manifest',{}).get('evaluation_role')!=SOURCE_ROLE):
        raise ValueError('completed matching discovery behavior provenance required')
    audit_path=stage/'audit.json';audit=json.loads(audit_path.read_text())
    if (audit.get('status')!='passed' or not audit.get('complete')
            or audit.get('identity_hash')!=manifest['identity_hash']
            or audit.get('model')!=source.get('model') or audit.get('revision')!=source.get('model_revision')):
        raise ValueError('completed matching discovery audit required before outcomes')
    rows=read_jsonl(dataset);validate_rows(rows)
    if len(rows)!=data_manifest.get('rows'):raise ValueError('source dataset coverage differs')
    recomputed=deepcopy(rows);components=assign_splits(recomputed)
    if (components!=data_manifest.get('structural_components')
            or any(left['template_id']!=right['template_id'] or left['split']!=right['split']
                   for left,right in zip(rows,recomputed))):
        raise ValueError('source structural component graph or split assignment differs')
    source_hash=identity.get('code',{}).get('source_sha256')
    if not source_hash:raise ValueError('recorded original discovery source hash required')
    qa,cases=prepared(source,source_hash)
    by_id={row['id']:row for row in rows}
    if len(cases)!=len(rows) or len({case['id'] for case in cases})!=len(rows):
        raise ValueError('saved discovery prepared-case coverage differs')
    for case in cases:
        if (case.get('kind')!='competition' or case.get('section')!=section['name']
                or case.get('variant')!='print_direct_v3' or case.get('task')!='print_direct_v3'
                or case['id'] not in by_id or case['record']!=by_id[case['id']]):
            raise ValueError('prepared cases differ from the permitted discovery source')
    if audit.get('preflight')!=qa or audit.get('evaluated')!=len(cases):
        raise ValueError('saved discovery audit and preparation coverage differ')
    return source,manifest,cases,dict(source_config_sha256=sha(source_path),
        source_dataset_sha256=dataset_hash,source_identity_hash=manifest['identity_hash'],
        source_model=source['model'],source_model_revision=source['model_revision'],
        source_prepared_sha256=sha(source['prepared_cases']),source_audit_sha256=sha(audit_path),
        original_source_sha256=source_hash,source_responses_sha256=manifest['responses_sha256'])


def collect(config):
    """Materialize immutable features after all pre-outcome access guards pass."""
    from . import checkpoint_suite
    from .registry import code_identity
    source,manifest,cases,provenance=_source_inputs(config)
    checked=checkpoint_suite.audit(source)
    if (checked.get('status')!='passed' or not checked.get('complete')
            or checked.get('identity_hash')!=manifest['identity_hash']):
        raise ValueError('completed discovery audit identity changed')
    responses=read_jsonl(Path(source['run_dir'])/'checkpoint_suite/responses.jsonl')
    if sha(Path(source['run_dir'])/'checkpoint_suite/responses.jsonl')!=provenance['source_responses_sha256']:
        raise ValueError('discovery response checksum changed after auditing')
    if len(responses)!=len(cases):raise ValueError('complete discovery response coverage required')
    for case,response in zip(cases,responses):checkpoint_suite.validate_response(case,response)
    rows=pair_features(cases,responses);path=Path(config['feature_table'])
    immutable(path,''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows).encode())
    targets=Counter(row['condition'] for row in rows);references={row['reference_id'] for row in rows}
    result=dict(status='passed',evaluation_role=ROLE,sha256=sha(path),feature_table=str(path),
        n=len(rows),groups=len({row['template_id'] for row in rows}),
        original_split_counts=dict(Counter(row['original_split'] for row in rows)),
        conditions=dict(targets),target_conditions=['informative','misleading'],
        label_counts={str(key):value for key,value in Counter(row['label'] for row in rows).items()},
        invalid_targets=sum(row['target_invalid'] for row in rows),
        columns=dict(input=list(INPUT_COLUMNS),neutral_raw=list(NEUTRAL_RAW_COLUMNS),neutral_scored=list(NEUTRAL_SCORED_COLUMNS)),
        additional_query_cost=dict(maximum_reference_queries_per_target=1,
            distinct_reference_queries=len(references),amortized_reference_queries_per_target=len(references)/len(rows),
            reference_oracle_access='neutral_failure only; raw neutral tiers use no oracle correctness'),
        source_config=str(config['source_config']),config_hash=digest(config),
        analysis_source=code_identity(),**provenance,generated_holdouts_opened=False,
        target_outcomes_used_as_features=False,empirical_mechanism_predictor=False,
        limitation='Exploratory discovery-only feature table; all source structures were previously observed. '
                   'Neutral correctness is scored reference-oracle access, separately declared from raw query features. '
                   'Ownership sources are excluded because they have no distinct naming counterpart.')
    target=Path(config.get('feature_manifest',path.with_suffix('.manifest.json')))
    immutable(target,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return result
