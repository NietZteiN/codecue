import json
from pathlib import Path

import pytest

from codecue.binding import preparation


def config(tmp_path,items):
    return {'root':str(tmp_path),'items':items,'output':str(tmp_path/'readiness_review.json'),
        'report':str(tmp_path/'readiness.md'),'csv':str(tmp_path/'readiness.csv')}


def test_default_inventory_root_uses_workspace_of_frozen_source(tmp_path,monkeypatch):
    from codecue.binding import snapshots
    monkeypatch.setattr(snapshots,'workspace_root',lambda source:tmp_path)
    (tmp_path/'ready.py').write_text('pass\n')
    result=preparation.inspect({'items':[{'id':'a','title':'A','category':'code',
        'evidence':[{'path':'ready.py'}]}]})
    assert result['root']==str(tmp_path)
    assert result['items'][0]['status']=='ready'


def test_inventory_distinguishes_build_execution_validation_and_scientific_readiness(tmp_path):
    (tmp_path/'source.py').write_text('pass\n')
    cfg=config(tmp_path,[
        {'id':'software','title':'Software','category':'code','evidence':[{'path':'source.py'}]},
        {'id':'data','title':'Data','category':'dataset','dependencies':['software'],
         'evidence':[{'path':'missing.json','purpose':'result'}]},
        {'id':'validation','title':'Checks','category':'tests','evidence':[{'path':'checks.xml','kind':'tests','purpose':'validation'}]},
        {'id':'dependent','title':'Dependent','category':'analysis','dependencies':['data']},
        {'id':'mechanism','title':'Mechanism','category':'science','scientific_decision_required':'Select a supported account'},
        {'id':'optional','title':'Training','category':'extension','policy':'deferred_optional'},
    ])
    result=preparation.run(cfg);states={item['id']:item['status'] for item in result['items']}
    assert states=={'software':'ready','data':'needs_execution','validation':'needs_validation',
        'dependent':'blocked_dependency','mechanism':'needs_scientific_decision','optional':'deferred_optional'}
    assert result['jobs_submitted'] is result['model_inference'] is result['generated_holdouts_opened'] is False
    assert json.loads((tmp_path/'readiness_review.json').read_text())==result
    assert 'needs_scientific_decision' in (tmp_path/'readiness.md').read_text()


@pytest.mark.parametrize('items',[
    [{'id':'a','dependencies':['missing']}],
    [{'id':'a','dependencies':['b']},{'id':'b','dependencies':['a']}],
    [{'id':'a'},{'id':'a'}],
])
def test_bad_dependency_graph_is_refused_before_any_execution(tmp_path,items):
    with pytest.raises(ValueError):preparation.inspect(config(tmp_path,items))


def test_tests_and_metadata_have_to_match_evidence(tmp_path):
    (tmp_path/'good.xml').write_text('<testsuites><testsuite tests="7" failures="0" errors="0" skipped="0"/></testsuites>')
    (tmp_path/'bad.xml').write_text('<testsuites><testsuite tests="7" failures="1"/></testsuites>')
    (tmp_path/'manifest.json').write_text(json.dumps({'status':'passed','n':12}))
    for name,expected in [('good.xml',True),('bad.xml',False)]:
        assert preparation._check(tmp_path,{'path':name,'kind':'tests'})['passed'] is expected
    assert preparation._check(tmp_path,{'path':'manifest.json','kind':'json','equals':{'status':'passed','n':12}})['passed']
    assert not preparation._check(tmp_path,{'path':'manifest.json','kind':'json','equals':{'n':13}})['passed']


def test_readiness_never_opens_raw_payloads_and_refuses_reserved_outcome_metadata(tmp_path,monkeypatch):
    raw=tmp_path/'responses.jsonl';raw.write_text('payload should not be opened')
    reserved=tmp_path/'artifacts/binding/final/summary.json';reserved.parent.mkdir(parents=True);reserved.write_text('{}')
    original_read_bytes=Path.read_bytes;original_read_text=Path.read_text
    def guarded_bytes(path,*args,**kwargs):
        if path==raw:raise AssertionError('raw payload opened')
        return original_read_bytes(path,*args,**kwargs)
    def guarded_text(path,*args,**kwargs):
        if path in (raw,reserved):raise AssertionError('reserved payload opened')
        return original_read_text(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_bytes',guarded_bytes);monkeypatch.setattr(Path,'read_text',guarded_text)
    assert preparation._check(tmp_path,{'path':str(raw)})['passed']
    assert not preparation._check(tmp_path,{'path':str(raw),'sha256':'0'*64})['passed']
    assert not preparation._check(tmp_path,{'path':str(reserved),'kind':'json'})['passed']


def test_cache_inventory_checks_metadata_and_shards_without_loading_weights(tmp_path,monkeypatch):
    snapshot=tmp_path/'hub/models--org--model/snapshots/revision';snapshot.mkdir(parents=True)
    for name in ('config.json','tokenizer.json'):(snapshot/name).write_text('{}')
    (snapshot/'model.safetensors.index.json').write_text(json.dumps({'weight_map':{'layer':'part.safetensors'}}))
    (snapshot/'part.safetensors').write_bytes(b'not actual weights')
    original=Path.read_bytes
    def no_weights(path,*args,**kwargs):
        if path.suffix=='.safetensors':raise AssertionError('weights opened')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_bytes',no_weights)
    results=preparation.inspect_cache({'hf_home':str(tmp_path),'models':[{'model':'org/model','revision':'revision'}]},tmp_path)
    assert results[0]['status']=='ready' and results[0]['weight_shards']==1 and results[0]['weights_loaded_or_hashed'] is False


@pytest.mark.parametrize('counts',[
    'tests="100" failures="0" errors="0" skipped="100"',
    'tests="-1" failures="0" errors="0" skipped="0"',
    'tests="1" failures="0" errors="0" skipped="2"',
    'tests="2" failures="-1" errors="0" skipped="0"',
])
def test_skipped_or_inconsistent_junit_counts_do_not_satisfy_validation(tmp_path,counts):
    path=tmp_path/'tests.xml';path.write_text('<testsuite '+counts+'/>')
    assert not preparation._check(tmp_path,{'path':str(path),'kind':'tests','minimum_tests':1})['passed']


def test_reserved_or_oversized_json_is_not_read_for_checksum(tmp_path,monkeypatch):
    protected=tmp_path/'artifacts/binding/final/summary.json';protected.parent.mkdir(parents=True);protected.write_text('{}')
    large=tmp_path/'oversized.json';large.write_bytes(b' '*((8*1024**2)+1))
    original_bytes=Path.read_bytes;original_text=Path.read_text
    def no_bytes(path,*args,**kwargs):
        if path in (protected,large):raise AssertionError('forbidden checksum read')
        return original_bytes(path,*args,**kwargs)
    def no_text(path,*args,**kwargs):
        if path in (protected,large):raise AssertionError('forbidden metadata read')
        return original_text(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_bytes',no_bytes);monkeypatch.setattr(Path,'read_text',no_text)
    for path in (protected,large):
        for kind in ('exists','json'):
            assert not preparation._check(tmp_path,{'path':str(path),'kind':kind,'sha256':'a'*64})['passed']


def test_scheduler_observations_include_failures_and_unknown_without_submission(tmp_path,monkeypatch):
    from codecue.binding import experiment_status
    path=tmp_path/'jobs.json';path.write_text(json.dumps({'failed':'123','unknown':'124'}))
    calls=[]
    def query(ids):
        calls.append(ids)
        return {'123':{'state':'FAILED','exit_code':'1:0'}},['squeue unavailable']
    monkeypatch.setattr(experiment_status,'query_scheduler',query)
    result=preparation.inspect({'root':str(tmp_path),'items':[],'jobs':str(path)})
    assert calls==[['123','124']]
    assert result['jobs']['failed']['state']=='FAILED'
    assert result['jobs']['unknown']['state']=='UNKNOWN'
    assert result['scheduler_errors']==['squeue unavailable']
    assert result['jobs_submitted'] is False
