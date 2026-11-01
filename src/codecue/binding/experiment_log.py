"""Automatic local experiment journal and rebuildable metadata index.

Immutable, uniquely named JSON events are the durable source of truth. SQLite,
CSV and Markdown are derived views. Index writes are serialized with a POSIX
lock and use rollback journaling (not SQLite WAL on the shared filesystem).
Only metadata is inspected: prediction JSONL, activation arrays and sealed
final/extrapolation outcomes are never opened by the logger.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import subprocess
import sys
import uuid

VERSION = 1
SKIP_DIRS = {'sources', 'experiment_log', 'literature', '__pycache__', '.git'}
SEALED_PARTS = {'test', 'tests', 'final', 'holdout', 'holdouts', 'sealed', 'extrapolation', 'extrapolations', 'reserved'}
MAX_METADATA_BYTES = 8 * 1024 * 1024
BULK_KEYS = {'source_files', 'input_token_ids', 'output_token_ids', 'predictions', 'execution_trace',
             'versioned_bindings', 'dependency_edges', 'transitive_dependencies', 'checkpoint_counterfactuals',
             'coef', 'coefficients', 'weights', 'intercept', 'mean', 'scale', 'case_ids', 'training_ids',
             'cases', 'fits', 'paired_flips', 'paired_answer_patterns', 'chunk_checksums', 'fit_checksums'}
CSV_FIELDS = ('id','kind','status','path','stage','model','model_revision','config_hash','source_hash','dataset_hash',
              'job_id','started_utc','finished_utc','wall_seconds','audit_status','scientific_status',
              'metrics_json','artifacts_json','issues_json','notices_json')


def _now():
    return datetime.now(timezone.utc).isoformat()


def workspace_root(root=None):
    if root is not None:
        return Path(root).resolve()
    candidate=Path(__file__).resolve().parents[3]
    frozen=candidate/'frozen_manifest.json'
    if frozen.exists():
        return Path(json.loads(frozen.read_text())['workspace_root']).resolve()
    return candidate


def _paths(root):
    root=workspace_root(root);base=root/'artifacts/binding/experiment_log'
    return root,base,base/'events',base/'index.sqlite3'


def _json(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),default=str)


def _digest(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _atomic(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():temporary.unlink()


def _spool(root,event):
    _,_,folder,_=_paths(root);folder.mkdir(parents=True,exist_ok=True)
    path=folder/(event['event_id']+'.json')
    _atomic(path,_json(event)+'\n')
    return path


def _event(event_type,run_dir=None,stage=None,payload=None,job_id=None):
    return dict(schema_version=VERSION,event_id=uuid.uuid4().hex,occurred_utc=_now(),event_type=event_type,
                run_dir=str(Path(run_dir).resolve()) if run_dir is not None else None,stage=stage,
                job_id=str(job_id) if job_id is not None else None,payload=payload or {})


@contextmanager
def _index(root, *, blocking=True):
    _,base,_,database=_paths(root);base.mkdir(parents=True,exist_ok=True)
    with (base/'index.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        conn=sqlite3.connect(database,timeout=30)
        try:
            conn.execute('PRAGMA journal_mode=DELETE')
            conn.execute('PRAGMA synchronous=FULL')
            conn.execute('CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY,kind TEXT,status TEXT,path TEXT,fingerprint TEXT,data_json TEXT NOT NULL)')
            conn.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY,event_type TEXT,occurred_utc TEXT,data_json TEXT NOT NULL)')
            yield conn
            conn.commit()
        except Exception:
            conn.rollback();raise
        finally:
            conn.close();fcntl.flock(lock,fcntl.LOCK_UN)


def _get(conn,key):
    row=conn.execute('SELECT data_json FROM records WHERE id=?',(key,)).fetchone()
    return json.loads(row[0]) if row else None


def _insert_event(conn,event):
    conn.execute('INSERT OR IGNORE INTO events VALUES (?,?,?,?)',
                 (event['event_id'],event['event_type'],event['occurred_utc'],_json(event)))


def _store(conn,root,record,*,snapshot=True):
    record=dict(record);record.pop('updated_utc',None)
    if record.get('kind')=='job':
        for (encoded,) in conn.execute("SELECT data_json FROM records WHERE kind='job'").fetchall():
            other=json.loads(encoded)
            matches=(record.get('submission_identity') and record.get('submission_identity')==other.get('submission_identity')) or (record.get('submission_signature') and record.get('submission_signature')==other.get('submission_signature'))
            if not matches or other['id']==record['id']:continue
            if record.get('job_id') and not other.get('job_id'):conn.execute('DELETE FROM records WHERE id=?',(other['id'],))
            elif not record.get('job_id') and other.get('job_id'):return False
    fingerprint=_digest(record)
    previous=conn.execute('SELECT fingerprint FROM records WHERE id=?',(record['id'],)).fetchone()
    if previous and previous[0]==fingerprint:return False
    record['updated_utc']=_now()
    conn.execute('INSERT OR REPLACE INTO records VALUES (?,?,?,?,?,?)',
                 (record['id'],record['kind'],record['status'],record.get('path',''),fingerprint,_json(record)))
    if snapshot:
        event=_event('record_snapshot',run_dir=record.get('path'),stage=record.get('stage'),
                     job_id=record.get('job_id'),payload={'record':record})
        _spool(root,event);_insert_event(conn,event)
    return True


def _compact(value,depth=0):
    if value is None or isinstance(value,(str,int,float,bool)):
        return value if not isinstance(value,str) or len(value)<2000 else value[:2000]+'…'
    if depth>=5:return {'omitted_type':type(value).__name__,'count':len(value) if hasattr(value,'__len__') else None}
    if isinstance(value,dict):
        result={}
        for key,item in value.items():
            if key in BULK_KEYS and isinstance(item,(list,dict)):
                result[key+'_count']=len(item);continue
            result[key]=_compact(item,depth+1)
            if len(result)>=100:result['_more_keys_omitted']=True;break
        return result
    if isinstance(value,(list,tuple)):
        if len(value)>24:return {'count':len(value),'items_omitted':True}
        return [_compact(item,depth+1) for item in value]
    return str(value)


def _resolve(root,path):
    path=Path(path)
    return (path if path.is_absolute() else root/path).resolve()


def _path_sealed(path):
    path=Path(path);parts=path.parts
    # Workspace parents can themselves be named test_* (including pytest roots).
    # Only project artifact components carry an evaluation-role meaning.
    if 'binding' in parts:parts=parts[len(parts)-1-list(reversed(parts)).index('binding')+1:]
    elif path.is_absolute():parts=(path.name,)
    return any(part.lower() in SEALED_PARTS or re.search(r'(^|[_-])(test|final|heldout|held_out|holdout|sealed|extrap|extrapolation|reserved)([_ .-]|$)',part.lower()) for part in parts)


def _sealed(config):
    role=str(config.get('evaluation_role','')).lower()
    generation=config.get('generation') or {}
    return (role in ('test','heldout','held_out') or any(word in role for word in ('extrapolation','final','holdout','heldout','held_out','sealed')) or config.get('split') in ('test','final','holdout','heldout','held_out')
            or generation.get('split_override') in ('test','final','holdout')
            or str(generation.get('evaluation_role','')).lower() in ('test','heldout','held_out')
            or any(word in str(generation.get('evaluation_role','')).lower() for word in ('extrapolation','final','holdout','heldout','held_out','sealed'))
            or any(_sealed(section) for section in config.get('sections',[]) if isinstance(section,dict)))


def _protected_outcome(path):
    path=Path(path)
    if _path_sealed(path):return True
    for parent in path.parents:
        for filename in ('manifest.json','registration.json'):
            target=parent/filename
            if not target.exists() or target==path:continue
            metadata=_read(target,[],allow_sealed_metadata=True)
            if metadata is None:return True
            config=(metadata.get('identity') or metadata).get('config') or {}
            if _sealed(config) or _sealed((metadata.get('identity') or metadata).get('dataset_manifest') or {}) or _path_sealed(config.get('dataset','')):return True
        if parent.name=='binding' or parent.parent==parent:break
    return False


def _read(path,issues,*,allow_sealed_metadata=False):
    path=Path(path)
    if not path.exists():return None
    if not allow_sealed_metadata and _protected_outcome(path):return None
    if path.suffix!='.json':return None
    try:
        if path.stat().st_size>MAX_METADATA_BYTES:
            issues.append(f'{path}: metadata exceeds {MAX_METADATA_BYTES} bytes; linked without reading');return None
        result=json.loads(path.read_text())
        if not isinstance(result,dict):issues.append(f'{path}: expected metadata object');return None
        return result
    except (OSError,ValueError,UnicodeError) as exc:
        issues.append(f'{path}: {type(exc).__name__}: {exc}');return None


def _artifact(path):
    path=Path(path)
    result={'path':str(path)}
    if path.exists() and path.is_file():
        result['bytes']=path.stat().st_size
        # Metadata hashes only. Never hash/open raw outcomes or activation banks.
        if path.suffix=='.json' and path.stat().st_size<=MAX_METADATA_BYTES and not _protected_outcome(path):
            result['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _base(kind,path,status):
    path=str(Path(path).resolve())
    return dict(id=kind+':'+_digest(path)[:24],kind=kind,status=status,path=path,stage=None,model=None,
        model_revision=None,config_hash=None,source_hash=None,dataset_hash=None,job_id=None,
        started_utc=None,finished_utc=None,wall_seconds=None,audit_status=None,scientific_status=None,
        metrics={},artifacts={},issues=[])


def _gate_status(metrics):
    for source in ('review','summary','audit'):
        value=metrics.get(source) or {}
        for key in ('reliability_gate','baseline_gate','gate'):
            gate=value.get(key)
            if isinstance(gate,dict) and gate.get('status'):return gate['status']
    return None


def _oversized_review_record(path,issues):
    """Link permitted rich reviews without reading their metadata payload."""
    path=Path(path)
    if path.suffix!='.json' or _protected_outcome(path):return None
    try:size=path.stat().st_size
    except FileNotFoundError:return None
    except OSError as exc:
        issues.append(f'{path}: {type(exc).__name__}: {exc}');return None
    if size<=MAX_METADATA_BYTES:return None
    # Rich comparisons may duplicate per-model reviews. Enforcing the bound is
    # expected; neither completion nor a scientific result can be inferred.
    record=_base('analysis',path,'unknown')
    record.update(stage='review',content_not_indexed=dict(reason='metadata_size_limit',
        bytes=size,limit_bytes=MAX_METADATA_BYTES))
    record['artifacts']['review']={'path':str(path),'bytes':size}
    record['notices']=[dict(path=str(path),code='metadata_size_limit',bytes=size,
        limit_bytes=MAX_METADATA_BYTES,message='Metadata linked without reading or hashing; execution and scientific status are unknown.')]
    return record


def _metadata_record(root,folder,kind):
    issues=[];filename='manifest.json' if kind=='run' else 'registration.json'
    path=folder/filename;manifest=_read(path,issues,allow_sealed_metadata=True)
    if manifest is None:return None,issues
    identity=manifest.get('identity',{}) if kind=='run' else manifest
    config=identity.get('config') or {};sealed=_sealed(config) or _sealed(identity.get('dataset_manifest') or {}) or _path_sealed(folder) or _path_sealed(config.get('dataset',''))
    record=_base(kind,folder,'sealed' if sealed else manifest.get('status','registered'))
    record.update(stage=identity.get('stage',folder.name if kind=='run' else 'analysis'),model=config.get('model'),
        model_revision=config.get('model_revision'),config_hash=identity.get('config_hash') or _digest(config),
        source_hash=(identity.get('code') or manifest.get('analysis_source') or {}).get('source_sha256'),
        dataset_hash=(identity.get('dataset_manifest') or {}).get('sha256'),
        job_id=manifest.get('slurm_job_id'),started_utc=manifest.get('started_utc'),finished_utc=manifest.get('finished_utc'),
        wall_seconds=manifest.get('wall_seconds_total'),manifest_status=manifest.get('status'),sealed=sealed,
        attempts=_compact(manifest.get('attempts',[])),error=None if sealed else manifest.get('error'))
    if kind=='run' and manifest.get('identity_hash'):record['id']='run:'+manifest['identity_hash']
    record['artifacts']['manifest' if kind=='run' else 'registration']={'path':str(path)}
    if not record['model'] and config.get('capture_config'):
        capture=_read(_resolve(root,config['capture_config']),issues,allow_sealed_metadata=True) or {}
        record['model']=capture.get('model');record['model_revision']=capture.get('model_revision')
    for key in ('dataset','config_path','report','figure','review_artifact'):
        if config.get(key):record['artifacts'][key]={'path':str(_resolve(root,config[key]))}
    if not sealed:
        candidates={'summary':folder/'summary.json','audit':folder/'audit.json','runtime':folder/'runtime.json'}
        if config.get('review_artifact'):candidates['review']=_resolve(root,config['review_artifact'])
        for key,target in candidates.items():
            if key in ('review','summary'):
                errors=[];linked=_oversized_review_record(target,errors)
                if linked and linked.get('content_not_indexed'):
                    record['artifacts'][key]=linked['artifacts']['review']
                    record.setdefault('notices',[]).extend(linked['notices'])
                    continue
                if errors:
                    issues.extend(errors);continue
            value=_read(target,issues)
            if target.exists():record['artifacts'][key]=_artifact(target)
            if value is not None:record['metrics'][key]=_compact(value)
        if kind=='analysis' and record['metrics'].get('summary'):
            record['status']=record['metrics']['summary'].get('status','complete')
        if not record['model']:record['model']=(record['metrics'].get('summary') or {}).get('model')
        if not record['model_revision']:record['model_revision']=(record['metrics'].get('summary') or {}).get('revision')
        record['audit_status']=(record['metrics'].get('audit') or {}).get('status')
        record['scientific_status']=_gate_status(record['metrics'])
    record['issues']=issues
    return record,issues


def _analysis_record(root,path):
    path=Path(path);issues=[]
    if _protected_outcome(path):return None,issues
    linked=_oversized_review_record(path,issues)
    if linked or issues:return linked,issues
    data=_read(path,issues)
    if not data or not any(key in data for key in ('status','complete','results','models','aggregate','overall','correction','reason')):return None,issues
    record=_base('analysis',path,data.get('status','superseded' if 'superseded' in path.name else 'complete' if data.get('complete') else 'recorded'))
    source=data.get('analysis_source') or data.get('source') or {}
    source=source if isinstance(source,dict) else {}
    record.update(model=data.get('model'),source_hash=source.get('source_sha256'),
                  config_hash=data.get('config_hash'),stage='review',metrics={'review':_compact(data)},issues=issues)
    record['artifacts']['review']=_artifact(path)
    for key in ('report','figure'):
        if isinstance(data.get(key),str):record['artifacts'][key]={'path':str(_resolve(root,data[key]))}
    record['scientific_status']=_gate_status(record['metrics']);return record,issues


def _dataset_record(root,path):
    issues=[];data=_read(path,issues,allow_sealed_metadata=True)
    if not data or not data.get('sha256'):return None,issues
    sealed=_path_sealed(path) or _sealed(data) or _sealed(data.get('generation') or {})
    record=_base('dataset',path,'sealed' if sealed else 'recorded')
    record.update(dataset_hash=data['sha256'],config_hash=data.get('generation_config_hash'),sealed=sealed,
                  metrics={} if sealed else {'summary':_compact(data)},issues=issues)
    record['artifacts']['manifest']={'path':str(path)}
    return record,issues


def _is_review(name):
    return (name.endswith('.json') and not name.startswith('submit_')
            and (any(word in name for word in ('review','comparison','_results','correction','superseded','entropy_audit'))
                 or name in ('v1_status.json','completion_manifest_v1.json','completion_manifest_v2.json','results.json')))


def _sync_folder(conn,root,folder,*,snapshot=True):
    folder=Path(folder).resolve();issues=[]
    if 'sources' in folder.parts or _path_sealed(folder):return issues
    candidates=[folder]+[p for p in folder.iterdir() if p.is_dir() and p.name not in SKIP_DIRS and not _path_sealed(p)] if folder.is_dir() else []
    for candidate in candidates:
        if (candidate/'manifest.json').exists():record,errors=_metadata_record(root,candidate,'run')
        elif (candidate/'registration.json').exists():record,errors=_metadata_record(root,candidate,'analysis')
        else:continue
        issues+=errors
        if record:_store(conn,root,record,snapshot=snapshot)
    return issues


def _job_record(root,metadata,path=None,existing=None):
    job_id=str(metadata.get('job_id') or '')
    submission=metadata.get('submission_manifest') or (str(path) if path and Path(path).name.startswith('submit_') else None)
    submission=str(_resolve(root,submission)) if submission else None
    signature=_digest([metadata.get('argv'),metadata.get('submitted_utc')]) if metadata.get('argv') and metadata.get('submitted_utc') else None
    key='job:'+job_id if job_id else 'submission:'+_digest(submission or signature or str(path or metadata))[:24]
    record=dict(existing or _base('job',path or root/'log/slurm','submitted'));record['id']=key
    record['artifacts']=dict(record.get('artifacts') or {})
    new_attempt=existing and int(metadata.get('restart_count',0) or 0)>int(existing.get('restart_count',0) or 0)
    if new_attempt:
        record.update(finished_utc=None,exit_code=None,started_utc=None,status='submitted')
        for key in ('scheduler_status','scheduler_exit_code','scheduler_elapsed_seconds'):record.pop(key,None)
    code=metadata.get('exit_code')
    if code is None and existing and existing.get('finished_utc') and not new_attempt:code=existing.get('exit_code')
    status=metadata.get('status')
    if code is not None:status='complete' if str(code) in ('0','0:0') else 'failed'
    elif metadata.get('started_utc'):status='running'
    if not job_id and existing and existing.get('status') in ('failed','submission_failed'):status=existing['status']
    if metadata.get('status')=='submission_failed':status='submission_failed'
    terminal={'complete','completed','failed','submission_failed','cancelled','timeout','out_of_memory','node_fail','boot_fail','preempted'}
    if existing and not new_attempt:
        old_status=existing.get('status')
        if old_status in terminal and not metadata.get('finished_utc'):status=old_status
        elif old_status=='running' and not metadata.get('started_utc') and not metadata.get('finished_utc') and code is None:status='running'
    record.update(status=status or record.get('status','submitted'),job_id=job_id or None,
        name=metadata.get('name',record.get('name')),argv=metadata.get('argv',record.get('argv',[])),
        partition=metadata.get('partition',record.get('partition')),dependency=metadata.get('dependency',record.get('dependency')),
        submitted_utc=metadata.get('submitted_utc',record.get('submitted_utc')),submission_identity=submission or record.get('submission_identity'),submission_signature=signature or record.get('submission_signature'),error=metadata.get('error',record.get('error')),
        started_utc=metadata.get('started_utc',record.get('started_utc')),
        finished_utc=metadata.get('finished_utc',record.get('finished_utc')),exit_code=code if code is not None else record.get('exit_code'),
        node=metadata.get('node',record.get('node')),restart_count=int(metadata.get('restart_count',record.get('restart_count',0)) or 0),
        resources=dict(record.get('resources') or {},**{k:metadata[k] for k in ('cpus','mem','gres','time','time_min') if k in metadata}))
    artifacts=record['artifacts']
    # Submission metadata and runtime stamps are distinct artifacts. In
    # particular, scanning a submit_*.json must never replace the runtime link.
    old_runtime=(artifacts.get('job_manifest') or {}).get('path')
    if old_runtime and Path(old_runtime).name.startswith('submit_'):
        artifacts.setdefault('submission_manifest',artifacts.pop('job_manifest'))
        old_runtime=None
    runtime=metadata.get('job_manifest')
    if not runtime and path and not Path(path).name.startswith('submit_') and Path(path).parent==root/'log/slurm':runtime=path
    if runtime:artifacts['job_manifest']={'path':str(_resolve(root,runtime))}
    if submission:artifacts['submission_manifest']={'path':submission}
    canonical=(artifacts.get('job_manifest') or {}).get('path') or (artifacts.get('submission_manifest') or {}).get('path')
    if canonical:record['path']=canonical
    elif path:record['path']=str(_resolve(root,path))
    return record


def _apply(conn,root,event,*,snapshot=True):
    if event['event_type']=='record_snapshot':
        record=event.get('payload',{}).get('record')
        if record:_store(conn,root,record,snapshot=False)
        return
    payload=event.get('payload') or {};job_id=event.get('job_id') or payload.get('job_id')
    if event['event_type'].startswith('job_'):
        previous=_get(conn,'job:'+str(job_id)) if job_id else None
        if previous and previous.get('last_event_utc','')>event['occurred_utc']:return
        metadata=dict(payload,job_id=job_id)
        if event['event_type']=='job_submitted':metadata.setdefault('submitted_utc',event['occurred_utc']);metadata['status']='submitted'
        elif event['event_type']=='job_started':metadata.setdefault('started_utc',event['occurred_utc']);metadata['status']='running'
        elif event['event_type']=='job_finished':metadata.setdefault('finished_utc',event['occurred_utc'])
        elif event['event_type']=='job_submission_failed':metadata['status']='submission_failed'
        if previous and event['event_type'] in ('job_submitted','job_started') and (previous.get('finished_utc') or previous.get('scheduler_status') in ('CANCELLED','FAILED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','COMPLETED')) and int(metadata.get('restart_count',0) or 0)<=int(previous.get('restart_count',0) or 0):metadata['status']=previous['status']
        elif previous and event['event_type']=='job_submitted' and previous.get('started_utc'):metadata['status']=previous['status']
        record=_job_record(root,metadata,existing=previous);record['last_event_utc']=event['occurred_utc'];_store(conn,root,record,snapshot=snapshot)
    for record in event.get('observations',[]):_store(conn,root,record,snapshot=snapshot)
    if event.get('run_dir') and not event.get('observations'):_sync_folder(conn,root,event['run_dir'],snapshot=snapshot)
    if event['event_type']=='artifact_written' and payload.get('path'):
        path=_resolve(root,payload['path']);_sync_folder(conn,root,path.parent,snapshot=snapshot)
        record=None
        if path.name.endswith('.manifest.json'):record,_=_dataset_record(root,path)
        elif _is_review(path.name):record,_=_analysis_record(root,path)
        if record:_store(conn,root,record,snapshot=snapshot)


def _records(conn):
    return [json.loads(row[0]) for row in conn.execute('SELECT data_json FROM records ORDER BY kind,path,id')]


def _exports(conn,root,issues=None):
    root,base,_,database=_paths(root);records=_records(conn);counts=Counter(r['kind'] for r in records)
    # A run may also link the same standalone review. Export one notice per
    # path/code pair while retaining each record's own indexing provenance.
    notices=list({(notice['path'],notice['code']):notice
                  for record in records for notice in record.get('notices',[])}.values())
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=CSV_FIELDS);writer.writeheader()
    for record in records:
        row={key:record.get(key) for key in CSV_FIELDS if not key.endswith('_json')}
        row.update(metrics_json=_json(record.get('metrics',{})),artifacts_json=_json(record.get('artifacts',{})),issues_json=_json(record.get('issues',[])),notices_json=_json(record.get('notices',[])))
        writer.writerow(row)
    _atomic(base/'experiments.csv',stream.getvalue())
    summary=dict(status='needs_attention' if issues else 'ok',records=len(records),events=conn.execute('SELECT count(*) FROM events').fetchone()[0],
        counts=dict(counts),issues=issues or [],notices=notices,report=str(root/'reports/binding/experiment_log.md'),csv=str(base/'experiments.csv'),database=str(database),updated_utc=_now())
    _atomic(base/'index_summary.json',_json(summary)+'\n')
    status_counts=Counter(r['status'] for r in records if r['kind'] in ('run','analysis'))
    lines=['# Automatic experiment log','',f"Updated {summary['updated_utc']}. {len(records)} indexed records: "+', '.join(f'{n} {k}' for k,n in sorted(counts.items()))+'.','',
        'Execution status, audit status and scientific reliability are separate. A completed/audited experiment can have a failed reliability gate. Full results remain in their original artifacts. This index reads metadata only; sealed final/extrapolation outcomes and raw prediction/activation payloads are excluded.','',
        '[Complete CSV](../../artifacts/binding/experiment_log/experiments.csv) · [Index summary](../../artifacts/binding/experiment_log/index_summary.json)','',
        '| Kind | Execution | Stage | Model | Audit | Scientific gate | Artifact |','|---|---|---|---|---|---|---|']
    experiments=[r for r in records if r['kind']!='job']
    for r in sorted(experiments,key=lambda r:r.get('updated_utc',''),reverse=True)[:200]:
        label=Path(r['path']).name;target=r['path'];report=(r.get('artifacts',{}).get('report') or {}).get('path')
        link=f'[{label}]({report or target})'
        values=(r['kind'],r['status'],r.get('stage') or '—',r.get('model') or '—',r.get('audit_status') or '—',r.get('scientific_status') or '—',link)
        lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in values)+' |')
    lines+=['','## Jobs','','| Job | Name | Status | Exit | Partition |','|---|---|---|---|---|']
    jobs=[r for r in records if r['kind']=='job']
    for r in sorted(jobs,key=lambda r:r.get('submitted_utc') or r.get('started_utc') or '',reverse=True)[:100]:
        lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in (r.get('job_id') or 'unassigned',r.get('name') or '—',r['status'],r.get('exit_code','—'),r.get('partition') or '—'))+' |')
    if issues:lines+=['','## Indexing issues','']+['- '+str(i).replace('\n',' ') for i in issues[:40]]
    if notices:
        lines+=['','## Indexing notices','']
        for notice in notices[:40]:
            target=notice['path'];message=notice['message']
            lines.append(f'- [{Path(target).name}]({target}): {message} ({notice["bytes"]:,} bytes; metadata limit {notice["limit_bytes"]:,} bytes).')
    lines+=['','Refresh/reconcile: `python scripts/117_binding_experiment_log.py refresh --scheduler`. Every lifecycle/result write and SLURM completion updates the log automatically; the persistent CPU reconciler also catches external cancellations.','']
    _atomic(root/'reports/binding/experiment_log.md','\n'.join(lines));return summary


def emit_event(event_type,*,root=None,run_dir=None,stage=None,payload=None,job_id=None):
    root=workspace_root(root);event=_event(event_type,run_dir,stage,payload,job_id)
    observations=[]
    if run_dir:
        folder=_resolve(root,run_dir)
        kind='run' if (folder/'manifest.json').exists() else 'analysis' if (folder/'registration.json').exists() else None
        if kind:
            observed,_=_metadata_record(root,folder,kind)
            if observed:observations.append(observed)
    if event_type=='artifact_written' and payload and payload.get('path'):
        path=_resolve(root,payload['path']);folder=path.parent
        if (folder/'manifest.json').exists():observed,_=_metadata_record(root,folder,'run')
        elif (folder/'registration.json').exists():observed,_=_metadata_record(root,folder,'analysis')
        elif path.name.endswith('.manifest.json'):observed,_=_dataset_record(root,path)
        elif _is_review(path.name):observed,_=_analysis_record(root,path)
        else:observed=None
        if observed:observations.append(observed)
    if observations:event['observations']=observations
    _spool(root,event)
    try:
        # The durable event already exists. A reconciler can replay it without
        # making a running experiment wait behind a full-index refresh.
        with _index(root, blocking=False) as conn:
            _insert_event(conn,event);_apply(conn,root,event);_exports(conn,root)
    except Exception as exc:
        print(f'Experiment log index deferred; durable event {event["event_id"]} retained: {type(exc).__name__}: {exc}',file=sys.stderr)
    _ensure_reconciler(root)
    return event


def _ensure_reconciler(root):
    try:
        from .experiment_log_scheduler import ensure_enabled
        ensure_enabled(root)
    except Exception as exc:
        print(f'Experiment reconciliation scheduling deferred: {type(exc).__name__}: {exc}',file=sys.stderr)


def safe_emit_event(*args,**kwargs):
    try:return emit_event(*args,**kwargs)
    except Exception as exc:
        print(f'Experiment logging failed: {type(exc).__name__}: {exc}',file=sys.stderr);return None


def note_artifact(path,*,root=None):
    path=Path(path)
    if not (path.name in ('manifest.json','registration.json','summary.json','audit.json') or path.name.endswith('.manifest.json') or _is_review(path.name)):return
    root=workspace_root(root);path=_resolve(root,path)
    if root/'artifacts/binding' not in path.parents or 'experiment_log' in path.parts or 'sources' in path.parts:return
    safe_emit_event('artifact_written',root=root,payload={'path':str(path)})


def list_records(root=None,*,kind=None):
    with _index(workspace_root(root)) as conn:
        if kind is None:return _records(conn)
        return [json.loads(r[0]) for r in conn.execute('SELECT data_json FROM records WHERE kind=? ORDER BY path,id',(kind,))]


def _walk_metadata(root):
    base=root/'artifacts/binding'
    if not base.exists():return
    for folder,dirs,files in os.walk(base):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS and d.lower() not in SEALED_PARTS]
        path=Path(folder)
        protected=False
        for meta in ('manifest.json','registration.json'):
            if meta in files:
                metadata=_read(path/meta,[],allow_sealed_metadata=True) or {}
                config=(metadata.get('identity') or metadata).get('config') or {}
                if _sealed(config) or _sealed((metadata.get('identity') or metadata).get('dataset_manifest') or {}) or _path_sealed(config.get('dataset','')):
                    yield path/meta;protected=True
        if protected:
            dirs[:]=[];continue
        for name in files:
            if name in ('manifest.json','registration.json') or name.endswith('.manifest.json') or _is_review(name):yield path/name


def _jobs_from_maps(conn,root):
    base=root/'artifacts/binding'
    if not base.exists():return
    for folder,dirs,files in os.walk(base):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS and d.lower() not in SEALED_PARTS]
        for name in files:
            if not ('jobs' in name and name.endswith('.json')):continue
            path=Path(folder)/name;errors=[];data=_read(path,errors)
            if not data:continue
            def visit(value,label=''):
                if isinstance(value,dict):
                    for k,v in value.items():yield from visit(v,label+'/'+k)
                elif isinstance(value,str) and value.isdecimal():yield label,value
            for label,job_id in visit(data):
                previous=_get(conn,'job:'+job_id)
                if previous:continue
                record=_job_record(root,dict(job_id=job_id,name=label.lstrip('/'),status='unknown'),path)
                record['artifacts']['job_map']={'path':str(path)};_store(conn,root,record)


def _scan_jobs(conn,root,issues):
    folder=root/'log/slurm'
    if not folder.exists():return
    entries=[]
    for path in sorted(folder.glob('*.json')):
        data=_read(path,issues)
        if data and isinstance(data.get('argv'),list):entries.append((path,data))
    signatures={_digest([d['argv'],d['submitted_utc']]):str(d['job_id']) for _,d in entries if d.get('job_id') and d.get('argv') and d.get('submitted_utc')}
    submissions={str(_resolve(root,d['submission_manifest'])):str(d['job_id']) for _,d in entries if d.get('job_id') and d.get('submission_manifest')}
    groups={}
    for path,data in entries:
        if not data.get('job_id'):
            identity=data.get('submission_manifest') or (str(path) if path.name.startswith('submit_') else None)
            job_id=submissions.get(str(_resolve(root,identity))) if identity else None
            if not job_id and data.get('argv') and data.get('submitted_utc'):job_id=signatures.get(_digest([data['argv'],data['submitted_utc']]))
            if job_id:data=dict(data,job_id=job_id)
            elif not data.get('status'):data=dict(data,status='unknown')
        identity=_job_record(root,data,path)['id']
        groups.setdefault(identity,[]).append((path,data))
    # Merge each job's files before storing. Otherwise every refresh would
    # generate snapshots while alternating submission and runtime metadata.
    for identity,items in groups.items():
        previous=_get(conn,identity);record=previous
        for path,data in sorted(items,key=lambda item:(not item[0].name.startswith('submit_'),int(item[1].get('restart_count',0) or 0),str(item[0]))):
            record=_job_record(root,data,path,record)
        if previous and previous.get('scheduler_status') and record.get('scheduler_status'):
            for key in ('status','scheduler_status','scheduler_exit_code','scheduler_elapsed_seconds'):record[key]=previous.get(key)
        _store(conn,root,record)


def _reconcile(conn,root,issues):
    ids=[r['job_id'] for r in _records(conn) if r['kind']=='job' and r.get('job_id') and str(r['job_id']).isdecimal()]
    for start in range(0,len(ids),200):
        chunk=ids[start:start+200]
        try:
            result=subprocess.run(['sacct','-n','-P','-X','-j',','.join(chunk),'--format=JobIDRaw,State%32,ExitCode,ElapsedRaw,SubmitLine%2048'],capture_output=True,text=True,timeout=30,check=False)
            if result.returncode:issues.append('sacct: '+result.stderr.strip());continue
            for line in result.stdout.splitlines():
                parts=[p.strip() for p in line.split('|')]
                if len(parts)<4 or parts[0] not in chunk:continue
                record=_get(conn,'job:'+parts[0]);state=parts[1].split()[0].rstrip('+')
                # Old submissions did not persist their scheduler ID. Accounting
                # retains the exact sbatch path even for canceled-before-start jobs.
                if len(parts)>4:
                    for argument in shlex.split(parts[4]):
                        target=_resolve(root,argument).with_suffix('.json')
                        if target.parent!=root/'log/slurm' or not target.name.startswith('submit_'):continue
                        metadata=_read(target,issues)
                        if metadata:record=_job_record(root,dict(metadata,job_id=parts[0]),target,record)
                status={'COMPLETED':'complete','RUNNING':'running','COMPLETING':'running','PENDING':'submitted','CANCELLED':'cancelled'}.get(state,state.lower())
                record.update(status=status,scheduler_status=state,scheduler_exit_code=parts[2],scheduler_elapsed_seconds=int(parts[3] or 0));_store(conn,root,record)
        except (OSError,subprocess.TimeoutExpired,ValueError) as exc:issues.append(f'scheduler reconciliation: {exc}')


def refresh(root=None,*,reconcile_scheduler=False):
    root=workspace_root(root);issues=[]
    with _index(root) as conn:
        _,_,events,_=_paths(root)
        pending=[]
        for path in events.glob('*.json'):
            event=_read(path,issues,allow_sealed_metadata=True)
            if not event:continue
            if not all(k in event for k in ('event_id','event_type','occurred_utc')):
                issues.append(f'{path}: invalid event schema');continue
            if not conn.execute('SELECT 1 FROM events WHERE event_id=?',(event['event_id'],)).fetchone():pending.append(event)
        for event in sorted(pending,key=lambda e:(e['occurred_utc'],e['event_id'])):
            _insert_event(conn,event);_apply(conn,root,event,snapshot=False)
        for path in _walk_metadata(root):
            if path.name=='manifest.json':record,errors=_metadata_record(root,path.parent,'run')
            elif path.name=='registration.json':record,errors=_metadata_record(root,path.parent,'analysis')
            elif path.name.endswith('.manifest.json'):record,errors=_dataset_record(root,path)
            else:record,errors=_analysis_record(root,path)
            issues+=errors
            if record:_store(conn,root,record)
        _jobs_from_maps(conn,root);_scan_jobs(conn,root,issues)
        if reconcile_scheduler:_reconcile(conn,root,issues)
        return _exports(conn,root,issues)


def safe_sync_job(root=None,*,payload=None,job_id=None):
    root=workspace_root(root);payload=payload or {}
    try:
        # Finished-job manifests and spooled lifecycle events remain available
        # to refresh(); indexing must not keep the allocation alive for a lock.
        with _index(root, blocking=False) as conn:
            for argument in payload.get('argv',[]):
                if not isinstance(argument,str) or not argument.endswith('.json'):continue
                path=_resolve(root,argument)
                if 'configs' not in path.parts:continue
                issues=[];config=_read(path,issues,allow_sealed_metadata=True)
                if not config:continue
                if config.get('run_dir') and not _sealed(config):_sync_folder(conn,root,_resolve(root,config['run_dir']))
                for key in ('review_artifact','comparison_artifact','artifact'):
                    if config.get(key) and not _sealed(config):
                        target=_resolve(root,config[key]);record,_=_analysis_record(root,target)
                        if record:
                            if config.get('report'):record['artifacts']['report']={'path':str(_resolve(root,config['report']))}
                            _store(conn,root,record)
                if config.get('dataset'):
                    manifest=_resolve(root,config['dataset']).with_suffix('.manifest.json')
                    record,_=_dataset_record(root,manifest)
                    if record:_store(conn,root,record)
            _exports(conn,root)
    except Exception as exc:print(f'Experiment job-result sync deferred: {type(exc).__name__}: {exc}',file=sys.stderr)
    _ensure_reconciler(root)
