"""Bounded analysis metadata stays discoverable without inspecting its contents."""
import builtins
import csv
import json
import os
from pathlib import Path

import pytest

from codecue.binding import experiment_log as log


def oversized_review(root,monkeypatch,*,name='comparison_v1.json'):
    # Keep fixture events below the cap while exercising exactly the production
    # size-bound branch, with explicit success claims that must not be inferred.
    monkeypatch.setattr(log,'MAX_METADATA_BYTES',4096)
    path=root/'artifacts/binding/discovery'/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(dict(status='complete',complete=True,
        reliability_gate=dict(status='passed'),padding='x'*5000)))
    return path


def prohibit_content_reads(monkeypatch,target):
    original_path_open=Path.open;original_builtin_open=builtins.open
    def check(path,mode):
        if isinstance(path,(str,os.PathLike)) and Path(path).absolute()==target.absolute() and 'r' in mode:
            raise AssertionError('oversized review content must not be opened, including for hashing')
    def path_open(self,mode='r',*args,**kwargs):
        check(self,mode);return original_path_open(self,mode,*args,**kwargs)
    def builtin_open(file,mode='r',*args,**kwargs):
        check(file,mode);return original_builtin_open(file,mode,*args,**kwargs)
    monkeypatch.setattr(Path,'open',path_open)
    monkeypatch.setattr(builtins,'open',builtin_open)


@pytest.mark.parametrize('ingest',['refresh','artifact_event'])
def test_oversized_review_is_linked_without_reading_hashing_or_inferred_success(tmp_path,monkeypatch,ingest):
    path=oversized_review(tmp_path,monkeypatch);size=path.stat().st_size
    prohibit_content_reads(monkeypatch,path)
    if ingest=='artifact_event':
        monkeypatch.setattr(log,'_ensure_reconciler',lambda root:None)
        log.note_artifact(path,root=tmp_path)
    first=log.refresh(tmp_path);records=log.list_records(tmp_path,kind='analysis')
    assert len(records)==1
    record=records[0]
    assert record['status']=='unknown' and record['scientific_status'] is None and record['audit_status'] is None
    assert record['metrics']=={} and record['finished_utc'] is None
    assert record['artifacts']['review']==dict(path=str(path),bytes=size)
    assert record['content_not_indexed']==dict(reason='metadata_size_limit',bytes=size,limit_bytes=4096)
    assert 'sha256' not in record['artifacts']['review'] and record['issues']==[]
    assert first['status']=='ok' and first['issues']==[] and len(first['notices'])==1
    assert first['notices'][0]['code']=='metadata_size_limit' and first['notices'][0]['path']==str(path)
    second=log.refresh(tmp_path)
    assert first['events']==second['events'] and first['notices']==second['notices']
    assert log.list_records(tmp_path,kind='analysis')==records
    with Path(first['csv']).open(newline='') as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==1 and rows[0]['status']=='unknown'
    assert json.loads(rows[0]['artifacts_json'])['review']['path']==str(path)
    assert json.loads(rows[0]['notices_json'])==record['notices']
    report=Path(first['report']).read_text()
    assert '## Indexing notices' in report and '## Indexing issues' not in report
    assert f'[{path.name}]({path})' in report and 'unknown' in report


def test_declared_oversized_review_is_linked_from_run_without_an_error_or_duplicate_notice(tmp_path,monkeypatch):
    path=oversized_review(tmp_path,monkeypatch)
    folder=tmp_path/'artifacts/binding/behavior/run';folder.mkdir(parents=True)
    (folder/'manifest.json').write_text(json.dumps(dict(status='complete',identity=dict(
        config=dict(evaluation_role='development',review_artifact=str(path)),stage='behavior'))))
    prohibit_content_reads(monkeypatch,path)
    first=log.refresh(tmp_path)
    assert first['status']=='ok' and first['issues']==[] and len(first['notices'])==1
    run=log.list_records(tmp_path,kind='run')[0]
    assert run['status']=='complete'  # Independently declared by its own manifest.
    assert run['artifacts']['review']['path']==str(path)
    assert 'review' not in run['metrics'] and len(run['notices'])==1
    assert log.refresh(tmp_path)['events']==first['events']


def test_review_growth_and_shrink_replace_the_same_record_and_clear_stale_claims(tmp_path,monkeypatch):
    path=oversized_review(tmp_path,monkeypatch)
    path.write_text(json.dumps(dict(status='complete',reliability_gate=dict(status='passed'),n=10)))
    log.refresh(tmp_path);small=log.list_records(tmp_path,kind='analysis')[0]
    assert small['status']=='complete' and small['scientific_status']=='passed'
    path.write_text(json.dumps(dict(status='complete',padding='x'*5000)))
    with monkeypatch.context() as patch:
        prohibit_content_reads(patch,path)
        grown=log.refresh(tmp_path)
    large=log.list_records(tmp_path,kind='analysis')[0]
    assert large['id']==small['id'] and large['status']=='unknown' and large['metrics']=={}
    assert large['scientific_status'] is None and grown['notices']
    path.write_text(json.dumps(dict(status='complete_exploratory',n=12,reliability_gate=dict(status='failed'))))
    recovered=log.refresh(tmp_path);current=log.list_records(tmp_path,kind='analysis')[0]
    assert current['id']==small['id'] and current['status']=='complete_exploratory'
    assert current['scientific_status']=='failed' and current['metrics']['review']['n']==12
    assert 'content_not_indexed' not in current and not current.get('notices')
    assert recovered['status']=='ok' and recovered['notices']==[] and recovered['issues']==[]
    assert log.refresh(tmp_path)['events']==recovered['events']


@pytest.mark.parametrize('protection',['path','manifest'])
def test_oversized_sealed_review_is_excluded_before_stat_or_content_reads(tmp_path,monkeypatch,protection):
    path=oversized_review(tmp_path,monkeypatch)
    if protection=='path':
        sealed=path.parent/'final';sealed.mkdir();path=path.rename(sealed/path.name)
    else:
        (path.parent/'manifest.json').write_text(json.dumps(dict(identity=dict(config=dict(evaluation_role='final')))))
    original_stat=Path.stat
    def stat(self,*args,**kwargs):
        if self==path:raise AssertionError('sealed review must not even be sized')
        return original_stat(self,*args,**kwargs)
    prohibit_content_reads(monkeypatch,path);monkeypatch.setattr(Path,'stat',stat)
    record,issues=log._analysis_record(tmp_path,path)
    assert record is None and issues==[]
    result=log.refresh(tmp_path)
    assert result['notices']==[] and result['issues']==[]
    assert not any(r['path']==str(path) for r in log.list_records(tmp_path))


@pytest.mark.parametrize('bad_content',['{"status":','[]'])
def test_size_notices_do_not_hide_malformed_small_metadata(tmp_path,monkeypatch,bad_content):
    oversized_review(tmp_path,monkeypatch)
    bad=tmp_path/'artifacts/binding/discovery/bad_review.json';bad.write_text(bad_content)
    result=log.refresh(tmp_path)
    assert result['status']=='needs_attention' and len(result['notices'])==1
    assert result['issues'] and str(bad) in result['issues'][0]


@pytest.mark.parametrize('failure',['stat','read'])
def test_permission_failures_remain_indexing_errors(tmp_path,monkeypatch,failure):
    path=oversized_review(tmp_path,monkeypatch);path.write_text('{"status":"complete"}')
    if failure=='stat':
        original=Path.stat
        def denied(self,*args,**kwargs):
            if self==path:raise PermissionError('denied fixture metadata stat')
            return original(self,*args,**kwargs)
        monkeypatch.setattr(Path,'stat',denied)
    else:
        original=Path.open
        def denied(self,mode='r',*args,**kwargs):
            if self==path and 'r' in mode:raise PermissionError('denied fixture metadata read')
            return original(self,mode,*args,**kwargs)
        monkeypatch.setattr(Path,'open',denied)
    result=log.refresh(tmp_path)
    assert result['status']=='needs_attention' and result['notices']==[]
    assert any('PermissionError' in issue and str(path) in issue for issue in result['issues'])


def test_large_non_review_metadata_still_requires_attention(tmp_path,monkeypatch):
    path=oversized_review(tmp_path,monkeypatch).rename(tmp_path/'artifacts/binding/discovery/manifest.json')
    prohibit_content_reads(monkeypatch,path)
    result=log.refresh(tmp_path)
    assert result['status']=='needs_attention' and result['notices']==[]
    assert result['issues'] and 'metadata exceeds 4096 bytes' in result['issues'][0]


def test_large_analysis_summary_is_linked_without_inferred_completion(tmp_path,monkeypatch):
    path=oversized_review(tmp_path,monkeypatch,name='summary.json')
    (path.parent/'registration.json').write_text(json.dumps(dict(status='registered',
        config=dict(evaluation_role='development'))))
    prohibit_content_reads(monkeypatch,path)
    result=log.refresh(tmp_path)
    record=next(r for r in log.list_records(tmp_path,kind='analysis') if r['path']==str(path.parent))
    assert result['status']=='ok' and result['issues']==[] and len(result['notices'])==1
    assert record['status']=='registered' and record['scientific_status'] is None
    assert 'summary' not in record['metrics']
    assert record['artifacts']['summary']==dict(path=str(path),bytes=path.stat().st_size)
    assert 'sha256' not in record['artifacts']['summary']


@pytest.mark.parametrize('ingest',['refresh','artifact_event'])
def test_bounded_completion_manifest_is_indexed_as_its_own_evidence(tmp_path,monkeypatch,ingest):
    path=tmp_path/'artifacts/binding/discovery/completion_manifest_v2.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(dict(status='complete_exploratory',evaluation_role='discovery',
        cases=9216,factorizations=45,scientific_artifacts_changed=False)))
    if ingest=='artifact_event':
        monkeypatch.setattr(log,'_ensure_reconciler',lambda root:None)
        log.note_artifact(path,root=tmp_path)
    result=log.refresh(tmp_path)
    records=log.list_records(tmp_path,kind='analysis')
    assert result['status']=='ok' and len(records)==1
    assert records[0]['path']==str(path) and records[0]['status']=='complete_exploratory'
