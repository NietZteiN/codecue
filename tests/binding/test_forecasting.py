import json
from pathlib import Path
import numpy as np
import pytest
from codecue.binding.forecasting import fit_logistic,predict,validate_contract,fit
from codecue.binding.datasets import digest


def test_logistic_fits_signal_and_keeps_train_normalization():
    rng=np.random.default_rng(29)
    x=rng.normal(size=(300,3))
    y=(x[:,0]-2*x[:,1]>.1).astype(float)
    model=fit_logistic(x[:200],y[:200],1.)
    assert np.mean((predict(model,x[200:])>.5)==y[200:])>.9
    assert np.allclose(model['mean'],x[:200].mean(0))
    before=list(model['mean'])
    assert np.isfinite(predict(model,x[200:]+10000)).all()
    assert before==model['mean']


def test_nested_features_and_target_outcomes_are_checked():
    contract={'A_input':['length'],'B_behavior':['length','confidence'],
              'C_measurements':['length','confidence','probe_value'],'cheap_stress_test':['stress']}
    validate_contract(contract)
    with pytest.raises(ValueError,match='nested'):
        validate_contract({**contract,'C_measurements':['length','probe_value']})
    with pytest.raises(ValueError,match='target outcomes'):
        validate_contract({**contract,'A_input':['correct']})
    with pytest.raises(ValueError,match='both training classes'):
        fit_logistic(np.ones((5,2)),np.zeros(5),1.)


def test_forecaster_refuses_test_labels_before_reading_features(tmp_path):
    dataset=tmp_path/'dataset.jsonl'; responses=tmp_path/'responses.jsonl'
    dataset.write_text(json.dumps({'id':'held','split':'test'})+'\n')
    responses.write_text(json.dumps({'id':'held','prediction':2})+'\n')
    config={'dataset':str(dataset),'forecasting':{'discovery_responses':str(responses),
        'features':{'A_input':['a'],'B_behavior':['a','b'],'C_measurements':['a','b','c'],'cheap_stress_test':['d']}}}
    with pytest.raises(ValueError,match='cannot open test'):
        fit(config)


def test_discovery_fit_and_registered_forecasts_are_immutable(tmp_path,monkeypatch):
    import hashlib
    from codecue.binding.forecasting import write_forecasts
    from codecue.binding import heldout
    rng=np.random.default_rng(2)
    features=rng.normal(size=(100,4))
    records=[]; observed=[]; table=[]
    for i,x in enumerate(features):
        split='train' if i<60 else ('development' if i<90 else 'test')
        records.append(dict(id=str(i),split=split,cluster_id=f'{split}:{i//3}',control_kind='primary',expected_answer=1))
        row=dict(id=str(i),features=dict(zip(('a','b','c','d'),x)))
        if split!='test':
            table.append(row)
            observed.append(dict(id=str(i),prediction=0 if x[0]+x[1]>.1 else 1))
    def jsonl(name,rows):
        path=tmp_path/name; path.write_text(''.join(json.dumps(r)+'\n' for r in rows)); return str(path)
    dataset=jsonl('data.jsonl',records)
    responses=jsonl('responses.jsonl',observed)
    table_path=jsonl('features.jsonl',table)
    manifest={'status':'complete','identity_hash':'test-software-identity','identity':{
        'dataset_manifest':{'sha256':hashlib.sha256(Path(dataset).read_bytes()).hexdigest()},'model_revision':'test'}}
    (tmp_path/'manifest.json').write_text(json.dumps(manifest))
    contract={'A_input':['a'],'B_behavior':['a','b'],'C_measurements':['a','b','c'],'cheap_stress_test':['a','d']}
    config=dict(dataset=dataset,run_dir=str(tmp_path/'run'),model_revision='test',forecasting={
        'features':contract,'discovery_responses':responses,'feature_table':table_path,'l2_grid':[.1,1.,10.]})
    result=fit(config)
    fitted=json.loads(Path(result['fit']).read_text())
    assert fitted['train_n']==60 and fitted['development_n']==30
    assert np.allclose(fitted['models']['A_input']['mean'],[features[:60,0].mean()])
    with pytest.raises(ValueError,match='immutable'):
        fit(config)
    frozen={'frozen_fitting_procedure':{'fit_manifest_sha256':digest(fitted)},
            'feature_information_contract':{'features':contract}}
    monkeypatch.setattr(heldout,'registration',lambda _: (frozen,'test-registration'))
    targets=[dict(id=str(i),features=dict(zip(('a','b','c','d'),x))) for i,x in enumerate(features) if i>=90]
    target_path=jsonl('target_features.jsonl',targets)
    config['forecasting'].update(fitted_model=result['fit'],target_feature_table=target_path)
    config['frozen_predictions']=str(tmp_path/'forecasts.jsonl')
    written=write_forecasts(config)
    assert written['rows']==10
    assert written['sha256']==hashlib.sha256(Path(config['frozen_predictions']).read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='immutable'):
        write_forecasts(config)
    frozen['frozen_fitting_procedure']['fit_manifest_sha256']='changed'
    with pytest.raises(ValueError,match='pin the fitted'):
        write_forecasts(config)
