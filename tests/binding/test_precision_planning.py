"""Planning checks use synthetic groups/OOF records, never sealed outcomes."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import precision_planning as planning
from codecue.binding.datasets import digest
from codecue.binding.published_benchmarks import sha


def groups():
    rng=np.random.default_rng(31)
    return [{'group_id':f'component:{level}:{index}','stratum':level,'value':float(rng.normal(0,.04))}
            for level in (2,4) for index in range(12)]


def options(**changes):
    return dict(component_counts=[24,48,240],effect_scenarios=[-.01,0.,.01],
                draws=4000,seed=117,alpha=.05,stratify=True,**changes)


def test_group_scenarios_are_deterministic_and_null_calibrated():
    config=options();result=planning.simulate(groups(),config)
    assert result==planning.simulate(list(reversed(groups())),config)
    assert result['status']=='conditional_scenarios' and result['pilot_groups']==24
    assert result['strata_counts']=={'2':12,'4':12}
    assert result['source_partition_seeds_are_replications'] is False
    assert result['model_refits']==0
    assert len(result['rows'])==9
    for count in config['component_counts']:
        rows=[row for row in result['rows'] if row['component_count']==count]
        assert all(row['components_per_stratum']==count//2 for row in rows)
        null=next(row for row in rows if row['effect_scenario']==0)
        assert abs(null['conditional_one_sided_detection_probability']-.05)<.01
        assert np.isclose(rows[0]['projection_half_width'],rows[-1]['projection_half_width'])
        assert rows[0]['conditional_one_sided_detection_probability']<null['conditional_one_sided_detection_probability']<rows[-1]['conditional_one_sided_detection_probability']


def test_projected_width_tracks_inverse_square_root_component_count():
    result=planning.simulate(groups(),options())
    widths={row['component_count']:row['projection_half_width'] for row in result['rows'] if row['effect_scenario']==0}
    assert widths[240]<widths[48]<widths[24]
    assert np.isclose(widths[240]/widths[24],np.sqrt(24/240),rtol=.15)
    # Effect-list order does not alter the shared Monte Carlo errors.
    other=planning.simulate(groups(),{**options(),'effect_scenarios':[0.,.01,-.01]})
    before={(row['component_count'],row['effect_scenario']):row for row in result['rows']}
    after={(row['component_count'],row['effect_scenario']):row for row in other['rows']}
    assert before==after


@pytest.mark.parametrize('pilot',[
    [{'group_id':'one','stratum':2,'value':.1}],
    [{'group_id':'a','stratum':2,'value':.1},{'group_id':'b','stratum':2,'value':.1}],
    [{'group_id':str(i),'stratum':2,'value':.1} for i in range(12)],
    [{'group_id':f'{level}:{i}','stratum':level,'value':float(level)} for level in (2,4) for i in range(3)],
])
def test_insufficient_or_degenerate_pilot_never_claims_certain_power(pilot):
    result=planning.simulate(pilot,options())
    assert result['status']=='ineligible_pilot' and not result['eligible']
    assert result['ineligibility_reason']
    assert len(result['rows'])==9
    assert all(row['conditional_one_sided_detection_probability'] is None
               and row['projection_half_width'] is None for row in result['rows'])


@pytest.mark.parametrize('change',[
    {'component_counts':[25]}, {'component_counts':[24,24]}, {'component_counts':[True]},
    {'effect_scenarios':[float('nan')]}, {'effect_scenarios':[0.,0.]},
    {'draws':99}, {'seed':-1}, {'alpha':.6}, {'stratify':'yes'},
])
def test_invalid_design_is_refused(change):
    with pytest.raises(ValueError):planning.simulate(groups(),{**options(),**change})
    with pytest.raises(ValueError):planning.simulate(groups()+[groups()[0]],options())


@pytest.fixture
def source(tmp_path):
    """Build two small completed discovery metadata chains, without model code."""
    contrasts=[{'left':'A_interactions','right':'A_interactions_neutral_raw'}]
    source_config=tmp_path/'comparison_config.json';comparison_path=tmp_path/'comparison.json'
    source={'runs':{},'comparison_artifact':str(comparison_path),'report':str(tmp_path/'source_report.md')}
    comparison={'status':'complete_exploratory','complete':True,'generated_holdouts_opened':False,
                'mechanism_C_fitted':False,'models':{},'review_checksums':{}}
    components=[(f'group:{load}:{index}',load) for load in (2,4) for index in range(2)]
    features=[dict(id=f'target:{i}',template_id=group,available_bindings=load,
                   original_split='train' if i%2 else 'development',label=i%2)
              for i,(group,load) in enumerate(components)]
    for name in ('first','second'):
        folder=tmp_path/name;folder.mkdir();out=folder/'cv';out.mkdir()
        table=folder/'features.jsonl';table.write_text(''.join(json.dumps(row)+'\n' for row in features))
        manifest=folder/'features.manifest.json'
        data={'status':'passed','evaluation_role':'discovery_failure_prediction_controls_v1',
            'sha256':sha(table),'n':4,'groups':4,'source_dataset_sha256':'same-discovery-source',
            'source_model':name,'source_model_revision':name+'revision',
            'generated_holdouts_opened':False,'target_outcomes_used_as_features':False}
        manifest.write_text(json.dumps(data))
        config={'feature_profile':'capacity_oracle_v1','model':name,'model_revision':name+'revision',
            'feature_table':str(table),'feature_manifest':str(manifest),'feature_manifest_sha256':sha(manifest),
            'output_dir':str(out),'review_artifact':str(folder/'review.json')}
        config_path=folder/'config.json';config_path.write_text(json.dumps(config))
        plan={'feature_profile':'capacity_oracle_v1','seeds':[17,29,43],
              'predictors':{'A_interactions':['a'],'A_interactions_neutral_raw':['a','b']},
              'comparisons':[['A_interactions','A_interactions_neutral_raw']]}
        rows=[]
        for seed in plan['seeds']:
            for i,row in enumerate(features):
                rows.append(dict(id=row['id'],template_id=row['template_id'],seed=seed,label=row['label'],
                    predictions={'A_interactions':.35+.1*(i%2),
                                 'A_interactions_neutral_raw':.15+.7*(i%2)}))
        oof=out/'oof_predictions.jsonl';oof.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        (out/'registration.json').write_text(json.dumps({'config':config,'config_hash':digest(config)}))
        review={'status':'complete_exploratory','config_hash':digest(config),
            'feature_manifest_sha256':sha(manifest),'feature_table_sha256':sha(table),
            'generated_holdouts_opened':False,'mechanism_C_fitted':False,'n':4,'templates':4,
            'analysis_plan':plan,'artifacts':{'oof_predictions':{'path':str(oof),'sha256':sha(oof)}}}
        Path(config['review_artifact']).write_text(json.dumps(review))
        source['runs'][name]={'config':str(config_path),'sha256':sha(config_path)}
        comparison['models'][name]=review
        comparison['review_checksums'][config['review_artifact']]=sha(config['review_artifact'])
    source_config.write_text(json.dumps(source));comparison['config_hash']=digest(source)
    comparison_path.write_text(json.dumps(comparison))
    return dict(source_config=str(source_config),source_config_sha256=sha(source_config),
        comparison=str(comparison_path),comparison_sha256=sha(comparison_path),
        contrasts=contrasts,metrics=['brier_score','log_loss'],
        component_counts=[4,8],effect_scenarios=[0.,.01],draws=256,seed=117,alpha=.05,stratify=True,
        output_dir=str(tmp_path/'outputs'),review_artifact=str(tmp_path/'outputs/planning_review_v1.json'),
        report=str(tmp_path/'report.md'),csv=str(tmp_path/'outputs/scenarios.csv'))


def test_collect_ensembles_partition_seeds_before_scoring_each_component(source):
    collected=planning.collect(source)
    assert len(collected['series'])==4  # two checkpoints, one contrast, two metrics
    for series in collected['series']:
        assert len(series['groups'])==4  # NOT 12 seed-by-component pseudo-replicates
        assert series['targets']==4 and series['partition_seeds']==[17,29,43]
        for row in series['groups']:
            assert row['target_examples']==1
            assert row['stratum'] in (2,4)
            assert row['value']>0


@pytest.mark.parametrize('change',['comparison_pin','source_pin','reserved_comparison','feature_role',
                                   'review_incomplete','oof_path','unregistered_contrast'])
def test_metadata_failures_are_rejected_before_any_payload_reader(source,monkeypatch,change):
    config=deepcopy(source)
    if change=='comparison_pin':config['comparison_sha256']='0'*64
    elif change=='source_pin':config['source_config_sha256']='0'*64
    elif change=='reserved_comparison':config['comparison']=str(Path(config['comparison']).with_name('final_results.json'))
    elif change=='unregistered_contrast':config['contrasts']=[{'left':'prior','right':'A_interactions'}]
    else:
        comparison=json.loads(Path(config['comparison']).read_text())
        src=json.loads(Path(config['source_config']).read_text())
        name=next(iter(src['runs']));run_path=Path(src['runs'][name]['config']);run=json.loads(run_path.read_text())
        if change=='feature_role':
            p=Path(run['feature_manifest']);meta=json.loads(p.read_text());meta['evaluation_role']='final';p.write_text(json.dumps(meta))
            run['feature_manifest_sha256']=sha(p);run_path.write_text(json.dumps(run));src['runs'][name]['sha256']=sha(run_path)
            Path(config['source_config']).write_text(json.dumps(src));config['source_config_sha256']=sha(config['source_config'])
            comparison['config_hash']=digest(src)
        else:
            review=comparison['models'][name]
            if change=='review_incomplete':review['status']='failed'
            else:review['artifacts']['oof_predictions']['path']=str(Path(run['output_dir'])/'final_responses.jsonl')
            Path(run['review_artifact']).write_text(json.dumps(review))
            comparison['review_checksums'][run['review_artifact']]=sha(run['review_artifact'])
        Path(config['comparison']).write_text(json.dumps(comparison));config['comparison_sha256']=sha(config['comparison'])
    def forbidden(_):raise AssertionError('outcome/feature payload opened before metadata rejection')
    monkeypatch.setattr(planning,'read_jsonl',forbidden)
    with pytest.raises(ValueError):planning.collect(config)


def test_run_exports_all_scenarios_immutably_without_selecting_size(source):
    result=planning.run(source)
    assert result['scenario_rows']==16 and result['series']==4
    assert result['confirmatory_sample_size_selected'] is False
    review=json.loads(Path(source['review_artifact']).read_text())
    assert review['new_model_queries']==0 and review['generated_holdouts_opened'] is False
    original={name:Path(source[name]).read_bytes() for name in ('review_artifact','report','csv')}
    assert planning.run(source)==result
    assert all(Path(source[name]).read_bytes()==value for name,value in original.items())
    with pytest.raises(ValueError):planning.run({**source,'draws':257})
