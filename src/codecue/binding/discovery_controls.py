"""Fixed source-capacity and oracle-access controls for discovery prediction.

The original source-only collector remains unchanged. This explicitly separate
profile adds pointwise source interactions and declared source-oracle inputs.
No language-model response is queried or read by this collector. Parent labels
and neutral-query measurements are reused only after their provenance is pinned.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
import math
from pathlib import Path

from .datasets import digest
from . import discovery_features as base
from .interpreter import execute
from .published_benchmarks import immutable, sha

ROLE='discovery_failure_prediction_controls_v1'
PROFILE='capacity_oracle_v1'
BIT_ORDER=('u','c','m','q','t')
_PRODUCTS=tuple(combinations(BIT_ORDER,2))+tuple(combinations(BIT_ORDER,3))
INTERACTION_COLUMNS=tuple('interaction_'+'_'.join(bits) for bits in _PRODUCTS)+tuple('distance_x_'+bit for bit in BIT_ORDER)
ORACLE_COLUMNS=('oracle_answer_value','oracle_answer_abs','oracle_answer_negative')
INPUT_COLUMNS=base.INPUT_COLUMNS
NEUTRAL_RAW_COLUMNS=base.NEUTRAL_RAW_COLUMNS
NEUTRAL_SCORED_COLUMNS=base.NEUTRAL_SCORED_COLUMNS


def predictor_columns():
    """Keep all capacity and information tiers explicit, with no mechanism C."""
    original=list(INPUT_COLUMNS);strong=original+list(INTERACTION_COLUMNS)
    raw=list(NEUTRAL_RAW_COLUMNS);scored=list(NEUTRAL_SCORED_COLUMNS);oracle=list(ORACLE_COLUMNS)
    return {'prior':[], 'A_input':original, 'A_interactions':strong,
        'A_interactions_neutral_raw':strong+raw,
        'A_interactions_neutral_scored':strong+raw+scored,
        'A_interactions_oracle':strong+oracle,
        'A_interactions_oracle_neutral_raw':strong+oracle+raw,
        'A_interactions_oracle_neutral_scored':strong+oracle+raw+scored}


def _features(row_or_features):
    return row_or_features['features'] if 'features' in row_or_features else row_or_features


def interaction_features(row_or_features):
    """Compute fixed source interactions without fitted statistics or truth fields."""
    features=_features(row_or_features)
    required=('updates','available_bindings','misleading','query_saved','tail_after',
              'query_last_definition_distance')
    values={name:features[name] for name in required}
    if any(not isinstance(value,(int,float)) or not math.isfinite(value) for value in values.values()):
        raise ValueError('finite source condition and distance features required')
    if (values['updates'] not in (1,3) or values['available_bindings'] not in (2,4)
            or any(values[name] not in (0,1) for name in ('misleading','query_saved','tail_after'))
            or values['query_last_definition_distance']<0):
        raise ValueError('registered source conditions and nonnegative distance required')
    bits={'u':(values['updates']-1)/2,'c':(values['available_bindings']-2)/2,
          'm':values['misleading'],'q':values['query_saved'],'t':values['tail_after']}
    result={}
    for product in _PRODUCTS:
        value=1.
        for bit in product:value*=bits[bit]
        result['interaction_'+'_'.join(product)]=value
    for bit in BIT_ORDER:result['distance_x_'+bit]=values['query_last_definition_distance']*bits[bit]
    return result


source_features=interaction_features


def oracle_features(case_or_row):
    """Execute permitted source syntax; never inspect stored model outcomes."""
    row=case_or_row['record'] if 'record' in case_or_row else case_or_row
    answer=execute(row['source'])['expected_answer']
    if type(answer) is not int:raise ValueError('integer source oracle answer required')
    return {'oracle_answer_value':answer,'oracle_answer_abs':abs(answer),
            'oracle_answer_negative':int(answer<0)}


def reconstruct_neutral_failure(row_or_features,oracle_answer_value=None):
    """Scored neutral failure adds no observation once raw response and oracle exist."""
    features=_features(row_or_features);valid=features['neutral_valid']
    if valid not in (0,1):raise ValueError('binary neutral validity required')
    if not valid:return 1
    prediction=features['neutral_prediction_value']
    answer=features['oracle_answer_value'] if oracle_answer_value is None else oracle_answer_value
    if (not isinstance(prediction,(int,float)) or not isinstance(answer,(int,float))
            or not math.isfinite(prediction) or not math.isfinite(answer)):
        raise ValueError('finite neutral prediction and source oracle required')
    return int(prediction!=answer)


def augment_rows(parent_rows,cases):
    """Append controls while preserving every parent target, label and reference."""
    rows=list(parent_rows);cases=list(cases);by_id={case['id']:case for case in cases}
    if not rows or len(by_id)!=len(cases) or len({row['id'] for row in rows})!=len(rows):
        raise ValueError('unique complete parent targets and source cases required')
    expected={case['id'] for case in cases if case['record']['family']=='versions'
              and case['record']['condition'] in ('informative','misleading')}
    if {row['id'] for row in rows}!=expected:
        raise ValueError('control rows must retain every parent version target exactly once')
    neutral={}
    for case in cases:
        record=case['record']
        if record['family']=='versions' and record['condition']=='neutral':
            key=base._pair_key(case)
            if key in neutral:raise ValueError('duplicate source neutral counterpart')
            neutral[key]=case
    original_columns=set(INPUT_COLUMNS+NEUTRAL_RAW_COLUMNS+NEUTRAL_SCORED_COLUMNS)
    result=[]
    for parent in sorted(rows,key=lambda row:row['id']):
        case=by_id[parent['id']];record=case['record'];reference=neutral.get(base._pair_key(case))
        if (reference is None or parent['reference_id']!=reference['id']
                or reference['id']==case['id'] or reference['record']['source']==record['source']
                or case.get('prompt_sha256') and case.get('prompt_sha256')==reference.get('prompt_sha256')):
            raise ValueError('distinct exact source-neutral pairing required')
        if (record['canonical_source']!=reference['record']['canonical_source']
                or record['template_id']!=reference['record']['template_id']
                or record['split']!=reference['record']['split']):
            raise ValueError('neutral source semantics or structural grouping differs')
        mapping={'template_id':'template_id','base_id':'base_id','original_split':'split',
                 'condition':'condition','query_role':'query_role','available_bindings':'available_bindings',
                 'lexical_realization':'lexical_realization'}
        if any(parent[left]!=record[right] for left,right in mapping.items()):
            raise ValueError('parent target metadata differs from source')
        old=parent['features']
        if set(old)!=original_columns:raise ValueError('parent feature column contract differs')
        inputs=base.source_features(case)
        if any(old[name]!=inputs[name] for name in INPUT_COLUMNS):
            raise ValueError('parent input features differ from permitted source')
        oracle=oracle_features(case)
        if oracle!=oracle_features(reference):raise ValueError('neutral and target source oracle differ')
        if old['neutral_failure']!=reconstruct_neutral_failure(old,oracle['oracle_answer_value']):
            raise ValueError('neutral failure differs from raw response plus source oracle')
        values=dict(old);values.update(interaction_features(old));values.update(oracle)
        result.append({**parent,'features':values})
    return result


def _parent_inputs(config):
    """Validate metadata and source declarations before opening parent features."""
    from .forecasting import _discovery_declaration, _discovery_response_path
    _discovery_declaration(config)
    parent_path=Path(config['parent_config'])
    if not config.get('parent_config_sha256') or sha(parent_path)!=config['parent_config_sha256']:
        raise ValueError('pinned parent prediction configuration checksum changed')
    parent=json.loads(parent_path.read_text())
    if not isinstance(parent,dict):raise ValueError('parent prediction configuration must be an object')
    _discovery_declaration(parent)
    for key in ('model','model_revision'):
        if key in config and config[key]!=parent.get(key):
            raise ValueError('control checkpoint differs from parent prediction configuration')
    for key in ('feature_manifest','feature_table'):_discovery_response_path(parent[key])
    manifest_path=Path(parent['feature_manifest'])
    if not parent.get('feature_manifest_sha256') or sha(manifest_path)!=parent['feature_manifest_sha256']:
        raise ValueError('pinned parent feature manifest checksum changed')
    manifest=json.loads(manifest_path.read_text())
    if not isinstance(manifest,dict):raise ValueError('parent feature manifest must be an object')
    _discovery_declaration(manifest)
    if manifest.get('status')!='passed' or manifest.get('evaluation_role')!=base.ROLE:
        raise ValueError('passed discovery parent feature manifest required')
    for key,field in (('model','source_model'),('model_revision','source_model_revision')):
        if parent.get(key)!=manifest.get(field):raise ValueError('parent feature checkpoint differs')
    source_config={'source_config':manifest['source_config'],
        'source_config_sha256':manifest['source_config_sha256'],
        'model':manifest['source_model'],'model_revision':manifest['source_model_revision']}
    _,source_manifest,cases,source_provenance=base._source_inputs(source_config)
    for key,value in source_provenance.items():
        if manifest.get(key)!=value:raise ValueError('parent feature/source provenance differs: '+key)
    return parent,manifest,source_manifest,cases,source_provenance


def collect(config):
    """Materialize immutable controls using source oracles and cached parent features."""
    from .discovery_prediction import load_features
    from .registry import code_identity
    parent,metadata,source_manifest,cases,provenance=_parent_inputs(config)
    checked,rows=load_features(parent)
    if checked!=metadata:raise ValueError('parent feature metadata changed during collection')
    controlled=augment_rows(rows,cases);path=Path(config['feature_table'])
    immutable(path,''.join(json.dumps(row,sort_keys=True)+'\n' for row in controlled).encode())
    references={row['reference_id'] for row in controlled}
    result={'status':'passed','evaluation_role':ROLE,'profile':PROFILE,'sha256':sha(path),
        'feature_table':str(path),'n':len(controlled),'groups':len({row['template_id'] for row in controlled}),
        'label_counts':{str(key):value for key,value in Counter(row['label'] for row in controlled).items()},
        'invalid_targets':sum(row['target_invalid'] for row in controlled),
        'conditions':dict(Counter(row['condition'] for row in controlled)),
        'original_split_counts':dict(Counter(row['original_split'] for row in controlled)),
        'columns':{'input':list(INPUT_COLUMNS),'interaction':list(INTERACTION_COLUMNS),
                   'oracle':list(ORACLE_COLUMNS),'neutral_raw':list(NEUTRAL_RAW_COLUMNS),
                   'neutral_scored':list(NEUTRAL_SCORED_COLUMNS)},
        'predictor_columns':predictor_columns(),'parent_config':str(config['parent_config']),
        'parent_config_sha256':sha(config['parent_config']),
        'parent_feature_manifest_sha256':sha(parent['feature_manifest']),
        'parent_feature_table_sha256':metadata['sha256'],
        'parent_source_identity_hash':source_manifest['identity_hash'],
        'config_hash':digest(config),'analysis_source':code_identity(),**provenance,
        'source_oracle_target_programs':len(controlled),
        'source_oracle_reference_programs':len(references),
        'source_oracle_evaluations':2*len(controlled),
        'source_oracle_evaluation_scope':'feature construction only; excludes source/provenance validation',
        'neutral_failure_reconstruction_exact':True,
        'target_metadata_labels_references_unchanged':True,
        'additional_query_cost':{'maximum_reference_queries_per_target':1,
            'distinct_reference_queries':len(references),
            'amortized_reference_queries_per_target':len(references)/len(controlled),
            'new_language_model_queries':0,'new_response_payload_reads':0,
            'source_oracle_access':'only explicitly oracle-labelled predictor tiers',
            'scored_only_tier_access':'neutral_failure requires reference oracle correctness'},
        'generated_holdouts_opened':False,'target_outcomes_used_as_features':False,
        'mechanism_C_fitted':False,
        'information_identity':'neutral_failure = not neutral_valid or neutral_prediction_value != oracle_answer_value',
        'limitation':'Previously consumed discovery only. Oracle-assisted tiers have stronger information access. '
            'The explicit scored feature adds no observation once raw neutral response and source oracle are given; '
            'any remaining predictive increment there is a representation/capacity effect, not new evidence.'}
    target=Path(config.get('feature_manifest',path.with_suffix('.manifest.json')))
    immutable(target,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return result
