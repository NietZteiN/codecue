import json
import hashlib
from collections import defaultdict
import pytest
from codecue.binding.datasets import read_jsonl,digest,write_json
from codecue.binding.diagnostic_review import paired_counts,distractor_overlap,build_counterbalanced,load_records
from codecue.binding.program_diagnostics import without_trailing_distractor,build


def outcome(expected,prediction):
    return dict(expected_answer=expected,prediction=prediction,correct=prediction==expected)


def test_pairing_preserves_discordance_and_invalid_outputs_without_independent_sample_claims():
    left={'a':outcome(7,7),'b':outcome(8,None),'c':outcome(9,9),'d':outcome(10,11)}
    right={'d':outcome(10,11),'c':outcome(9,8),'b':outcome(8,8),'a':outcome(7,7)}
    result=paired_counts(left,right)
    assert result['n']==4 and set(result['counts'].values())=={1}
    assert result['left_invalid']==1 and result['right_invalid']==0
    assert result['accuracy_difference_left_minus_right']==0
    with pytest.raises(ValueError,match='complete matching'):
        paired_counts(left,{k:v for k,v in right.items() if k!='a'})
    right['a']['expected_answer']=100
    with pytest.raises(ValueError,match='different expected'):
        paired_counts(left,right)


def test_distractor_audit_detects_missing_within_magnitude_overlap():
    rows=[dict(expected_answer=sign*magnitude,query_followed_by_distractor=bool(magnitude%2))
          for magnitude in (1,2,3,4) for sign in (-1,1)]
    result=distractor_overlap(rows)
    assert result['confounded'] and result['magnitudes_without_both_levels']==[1,2,3,4]
    balanced=[dict(expected_answer=r['expected_answer'],query_followed_by_distractor=flag)
              for r in rows for flag in (False,True)]
    assert not distractor_overlap(balanced)['confounded']


def test_counterbalanced_candidates_are_fresh_paired_and_independently_validated(tmp_path):
    excluded=tmp_path/'excluded.jsonl'
    old_source='v0 = 0\nv1 = 2\ndistractor = v1\nv0'
    excluded.write_text(json.dumps({'source':old_source})+'\n')
    config={'base':dict(dataset=str(tmp_path/'base.jsonl'),diagnostic_kind='arithmetic_free',seed=2026102506,
                        unique_distractor_prefixes=True,exclude_datasets=[str(excluded)]),
            'output':str(tmp_path/'counterbalanced.jsonl')}
    result=build_counterbalanced(config)
    rows=read_jsonl(config['output']);groups=defaultdict(list)
    assert result['rows']==result['independent_python_programs']==768
    assert result['model_inference_performed'] is False
    assert {r['evaluation_role'] for r in rows}=={'counterbalanced_followup_only'}
    assert not distractor_overlap(rows)['confounded']
    for row in rows:
        assert without_trailing_distractor(row['source'])!=without_trailing_distractor(old_source)
        groups[row['paired_group_id']].append(row)
    assert len(groups)==384
    for group in groups.values():
        assert len(group)==2 and {r['query_followed_by_distractor'] for r in group}=={False,True}
        assert len({r['split'] for r in group})==len({r['expected_answer'] for r in group})==1
        assert len({without_trailing_distractor(r['source']) for r in group})==1
    with pytest.raises(ValueError,match='immutable'):build_counterbalanced(config)


def test_review_refuses_coherent_response_edits_after_the_saved_decision(tmp_path):
    config=dict(dataset=str(tmp_path/'dataset.jsonl'),diagnostic_kind='arithmetic_forms',seed=2026102507,
                calibration={'variants':['print_direct_v3','print_trace_long_v1']},model='software_only',
                model_revision='a'*40,tokenizer_revision='a'*40,dtype='float32',tokenization_mode='software_only')
    dataset_manifest=build(config);rows=read_jsonl(config['dataset']);records=[]
    for variant in config['calibration']['variants']:
        for row in rows:
            text=str(row['expected_answer']) if variant=='print_direct_v3' else f"Answer: {row['expected_answer']}"
            records.append(dict(row,variant=variant,raw_response=text,prediction=row['expected_answer'],correct=True,invalid=False))
    directory=tmp_path/'run';directory.mkdir();response=directory/'responses.jsonl'
    response.write_text(''.join(json.dumps(r)+'\n' for r in records))
    identity={'config':config,'dataset_manifest':dataset_manifest};identity_hash=digest(identity)
    write_json(directory/'manifest.json',dict(identity=identity,identity_hash=identity_hash,status='complete',
                                            samples_completed=len(records),samples_planned=len(records)))
    write_json(directory/'diagnostic_decision.json',dict(complete=True,identity_hash=identity_hash,
               responses_sha256=hashlib.sha256(response.read_bytes()).hexdigest()))
    assert len(load_records(directory)[0])==384
    records[0].update(raw_response='123',prediction=123,correct=False)
    response.write_text(''.join(json.dumps(r)+'\n' for r in records))
    with pytest.raises(ValueError,match='immutable decision'):load_records(directory)
