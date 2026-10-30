import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from codecue.binding import candidate_pipeline as pipeline


def fixture(tmp_path):
    directory=tmp_path/'artifacts/binding/discovery';directory.mkdir(parents=True)
    parent=dict(model='m',model_revision='a'*40,feature_profile='confidence_access_v1',output_dir=str(directory/'old_cv'))
    candidate=dict(model='m',model_revision='a'*40,measurement_dtype='float32',run_dir=str(directory/'measure'))
    def save(name,value):
        path=directory/name;path.write_text(json.dumps(value));return str(path),hashlib.sha256(path.read_bytes()).hexdigest()
    p,ph=save('parent.json',parent);c,ch=save('candidate.json',candidate)
    spec=dict(model='m',model_revision='a'*40,protocol=pipeline.protocol(),
        source_prediction_config=p,source_prediction_config_sha256=ph,
        candidate_config=c,candidate_config_sha256=ch,output_dir=str(directory/'new_prediction'),report=str(directory/'report.md'))
    return spec,parent,candidate,save


def test_changed_analysis_plan_rejected_before_input_metadata(monkeypatch):
    spec=dict(protocol=deepcopy(pipeline.protocol()));spec['protocol']['l2_grid']=[1.]
    def opened(*args,**kwargs):raise AssertionError('input metadata opened before protocol guard')
    monkeypatch.setattr(pipeline,'_object',opened)
    with pytest.raises(ValueError,match='protocol'):pipeline.validate(spec)


def test_reserved_role_rejected_before_any_metadata(monkeypatch):
    def opened(*args,**kwargs):raise AssertionError('reserved input opened')
    monkeypatch.setattr(pipeline,'_object',opened)
    with pytest.raises(ValueError):pipeline.validate({'evaluation_role':'sealed_final','protocol':pipeline.protocol()})


@pytest.mark.parametrize('change',['checkpoint','smoke','precision','output_alias','wrong_parent','checksum'])
def test_unsafe_or_unmatched_pipeline_declarations_reject(tmp_path,change):
    spec,parent,candidate,save=fixture(tmp_path)
    if change=='checkpoint':candidate['model_revision']='b'*40
    if change=='smoke':candidate['case_limit']=8
    if change=='precision':candidate['measurement_dtype']='bfloat16'
    if change=='output_alias':spec['output_dir']=candidate['run_dir']
    if change=='wrong_parent':parent['feature_profile']='capacity_oracle_v1'
    spec['source_prediction_config'],spec['source_prediction_config_sha256']=save('parent.json',parent)
    spec['candidate_config'],spec['candidate_config_sha256']=save('candidate.json',candidate)
    if change=='checksum':spec['candidate_config_sha256']='0'*64
    with pytest.raises(ValueError):pipeline.validate(spec)


def test_incomplete_upstream_cannot_trigger_collection_or_fitting(tmp_path,monkeypatch):
    spec,parent,candidate,save=fixture(tmp_path);stage=Path(candidate['run_dir'])/'candidate_measurement';stage.mkdir(parents=True)
    for name,value in [('manifest',{'status':'started'}),('summary',{'complete':False}),('audit',{'status':'failed'})]:
        (stage/(name+'.json')).write_text(json.dumps(value))
    def collected(*args,**kwargs):raise AssertionError('incomplete measurement used as training data')
    monkeypatch.setattr(pipeline.profile,'collect',collected)
    with pytest.raises(ValueError,match='complete candidate'):pipeline.fit(spec)
    assert not (Path(spec['output_dir'])/'collection_config.json').exists()


def test_effective_configs_are_immutable(tmp_path):
    path=tmp_path/'effective.json';pipeline._json(path,{'hash':'fixed'});pipeline._json(path,{'hash':'fixed'})
    with pytest.raises(ValueError):pipeline._json(path,{'hash':'changed'})


def test_reserved_comparison_rejects_before_any_metadata(monkeypatch):
    def opened(*args,**kwargs):raise AssertionError('reserved comparison metadata opened')
    monkeypatch.setattr(pipeline,'_object',opened)
    with pytest.raises(ValueError):pipeline.compare({'evaluation_role':'sealed_final','protocol':pipeline.protocol()})


def test_changed_review_cannot_pass_completed_pipeline_receipt(tmp_path):
    spec,parent,candidate,save=fixture(tmp_path);out=Path(spec['output_dir']);out.mkdir()
    artifact=out/'review_v1.json';artifact.write_text(json.dumps({'status':'complete_exploratory','metrics':{'brier':.1}}))
    effective=out/'effective_config.json';effective.write_text(json.dumps({'review_artifact':str(artifact)}))
    from codecue.binding.datasets import digest
    checksum=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    receipt=dict(status='complete_exploratory',config_hash=digest(spec),effective_config=dict(path=str(effective),sha256=checksum(effective)),review=dict(path=str(artifact),sha256=checksum(artifact)))
    (out/'pipeline_review_v1.json').write_text(json.dumps(receipt))
    run_path,run_hash=save('pipeline.json',spec)
    artifact.write_text(json.dumps({'status':'complete_exploratory','metrics':{'brier':.9}}))
    bundle=dict(protocol=pipeline.protocol(),runs={'model':dict(config=run_path,sha256=run_hash)},output_dir=str(out/'compare'),comparison_report=str(out/'comparison.md'),decision_report=str(out/'decision.md'),baseline_comparison=str(out/'baseline.json'),figure_png=str(out/'plot.png'),figure_svg=str(out/'plot.svg'))
    with pytest.raises(ValueError,match='review identity changed'):pipeline.compare(bundle)
