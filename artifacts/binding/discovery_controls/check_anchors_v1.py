"""Check real v1/v2 common baselines before interpreting the new controls."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding.datasets import read_jsonl,write_json
from codecue.binding.published_benchmarks import sha

TOLERANCE=1e-10


def compare_values(left,right):
    if isinstance(left,dict):
        assert isinstance(right,dict) and set(left)==set(right)
        return max((compare_values(left[key],right[key]) for key in left),default=0.)
    if isinstance(left,list):
        assert isinstance(right,list) and len(left)==len(right)
        return max((compare_values(a,b) for a,b in zip(left,right)),default=0.)
    if isinstance(left,(int,float)) and not isinstance(left,bool):
        assert isinstance(right,(int,float)) and abs(left-right)<=TOLERANCE
        return abs(left-right)
    assert left==right
    return 0.


def main():
    folder=ROOT/'artifacts/binding/discovery_controls'
    comparison=json.loads((folder/'comparison_v1.json').read_text())
    assert comparison['status']=='complete_exploratory' and comparison['complete']
    checks=[]
    for name in ('llama31_8b','codellama34b'):
        config=json.loads((ROOT/'configs/binding/discovery_controls'/(name+'_v1.json')).read_text())
        assert sha(ROOT/config['reproduction_parent_config'])==config['reproduction_parent_config_sha256']
        parent=json.loads((ROOT/config['reproduction_parent_config']).read_text())
        old=json.loads((ROOT/parent['review_artifact']).read_text());new=comparison['models'][name]
        for review in (old,new):
            assert review['status']=='complete_exploratory'
            for artifact in review['artifacts'].values():assert sha(ROOT/artifact['path'])==artifact['sha256']
        old_rows=read_jsonl(ROOT/parent['feature_table']);new_rows=read_jsonl(ROOT/config['feature_table'])
        old_by_id={row['id']:row for row in old_rows};new_by_id={row['id']:row for row in new_rows}
        assert len(old_rows)==len(new_rows)==6144 and set(old_by_id)==set(new_by_id)
        for identity,row in old_by_id.items():
            changed=new_by_id[identity]
            assert {k:v for k,v in row.items() if k!='features'}=={k:v for k,v in changed.items() if k!='features'}
            for column,value in row['features'].items():assert changed['features'][column]==value
        old_oof=read_jsonl(ROOT/old['artifacts']['oof_predictions']['path'])
        new_oof=read_jsonl(ROOT/new['artifacts']['oof_predictions']['path'])
        before={(row['seed'],row['id']):row for row in old_oof}
        after={(row['seed'],row['id']):row for row in new_oof}
        assert len(before)==len(old_oof)==len(after)==len(new_oof) and set(before)==set(after)
        maximum=0.
        for key,row in before.items():
            changed=after[key]
            assert {k:v for k,v in row.items() if k!='predictions'}=={k:v for k,v in changed.items() if k!='predictions'}
            for predictor in ('prior','A_input'):
                difference=abs(row['predictions'][predictor]-changed['predictions'][predictor])
                assert difference<=TOLERANCE
                maximum=max(maximum,difference)
        old_fits=json.loads((ROOT/old['artifacts']['fold_fits']['path']).read_text())
        new_fits=json.loads((ROOT/new['artifacts']['fold_fits']['path']).read_text())
        before={(row['seed'],row['outer_fold']):row for row in old_fits}
        after={(row['seed'],row['outer_fold']):row for row in new_fits}
        assert set(before)==set(after) and len(before)==18
        fit_difference=0.
        for key,row in before.items():
            changed=after[key]
            for field in ('train_groups','test_groups','inner_assignments'):assert row[field]==changed[field]
            for predictor in ('prior','A_input'):
                fit_difference=max(fit_difference,compare_values(row['predictors'][predictor],changed['predictors'][predictor]))
        checks.append({'checkpoint':name,'targets':len(old_rows),'oof_records':len(old_oof),
            'outer_folds':len(before),'anchor_predictors':['prior','A_input'],
            'maximum_probability_difference':maximum,'maximum_fit_or_curve_difference':fit_difference,
            'identities_labels_references_original_features_unchanged':True,
            'all_outer_inner_group_assignments_unchanged':True})
    result={'status':'passed','complete':True,'checks':checks,'tolerance':TOLERANCE,
        'comparison_sha256':sha(folder/'comparison_v1.json'),'check_script_sha256':sha(__file__),
        'generated_holdouts_opened':False,'new_language_model_queries':0}
    write_json(folder/'anchor_review_v1.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
