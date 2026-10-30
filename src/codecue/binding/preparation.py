"""Metadata-only readiness inventory: never submit jobs or open outcome payloads."""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .datasets import digest,write_json

BULK_SUFFIXES={'.jsonl','.npz','.npy','.pt','.bin','.safetensors'}


def _path(root,value):
    path=Path(value)
    return path if path.is_absolute() else root/path


def _metadata(path):
    from .experiment_log import _protected_outcome
    if path.suffix!='.json' or path.stat().st_size>8*1024**2:
        raise ValueError('bounded JSON metadata required')
    if _protected_outcome(path) and not (path.name in ('manifest.json','registration.json') or path.name.endswith('.manifest.json')):
        raise ValueError('reserved outcome metadata is excluded from readiness')
    value=json.loads(path.read_text())
    if not isinstance(value,dict):raise ValueError('metadata object required')
    return value


def _check(root,spec):
    path=_path(root,spec['path']);purpose=spec.get('purpose','source')
    result={'path':str(path),'purpose':purpose,'passed':False,'issue':None}
    if not path.is_file():return dict(result,issue='missing file')
    kind=spec.get('kind','exists')
    try:
        data=None
        if kind=='json' or (spec.get('sha256') and path.suffix=='.json'):
            # Enforce bounded, permitted metadata access BEFORE checksum reads.
            data=_metadata(path)
        if spec.get('sha256'):
            from .experiment_log import _protected_outcome
            if _protected_outcome(path) and data is None:raise ValueError('reserved outcomes are excluded from readiness')
            if path.suffix in BULK_SUFFIXES:raise ValueError('readiness does not hash raw outcome/array/weight payloads')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:raise ValueError('checksum differs')
        if kind=='json':
            for key,expected in spec.get('equals',{}).items():
                value=data
                for part in key.split('.'):value=value[part]
                if value!=expected:raise ValueError('metadata field differs: '+key)
        elif kind=='tests':
            if path.suffix!='.xml' or path.stat().st_size>8*1024**2:raise ValueError('bounded JUnit metadata required')
            suites=[s for s in ET.parse(path).getroot().iter('testsuite') if not s.findall('.//testsuite')]
            rows=[{key:int(s.attrib.get(key,0)) for key in ('tests','errors','failures','skipped')} for s in suites]
            if any(any(value<0 for value in row.values()) or row['errors']+row['failures']+row['skipped']>row['tests'] for row in rows):
                raise ValueError('inconsistent JUnit counts')
            counts={key:sum(row[key] for row in rows) for key in ('tests','errors','failures','skipped')}
            counts['passed']=counts['tests']-counts['errors']-counts['failures']-counts['skipped']
            result['test_counts']=counts
            if counts['passed']<spec.get('minimum_tests',1) or counts['errors'] or counts['failures']:
                raise ValueError('required software checks have not passed')
        elif kind!='exists':raise ValueError('unknown readiness evidence kind')
        return dict(result,passed=True)
    except (OSError,ValueError,KeyError,TypeError,ET.ParseError) as exc:
        return dict(result,issue=f'{type(exc).__name__}: {exc}')


def inspect_cache(config,root):
    """Inspect pinned metadata/shard existence without importing model libraries."""
    home=_path(root,config['hf_home']);results=[]
    for item in config.get('models',[]):
        folder=home/'hub'/('models--'+item['model'].replace('/','--'))/'snapshots'/item['revision']
        issues=[];shards=[]
        if not (folder/'config.json').is_file():issues.append('model config missing')
        if not any((folder/name).is_file() for name in ('tokenizer.json','tokenizer.model')):issues.append('tokenizer asset missing')
        index=folder/'model.safetensors.index.json'
        if index.is_file():
            data=json.loads(index.read_text());shards=sorted(set(data.get('weight_map',{}).values()))
            if not shards:issues.append('weight index has no shards')
            for name in shards:
                if Path(name).name!=name:raise ValueError('weight shard must be a local filename')
                if not (folder/name).is_file():issues.append('weight shard missing: '+name)
        elif (folder/'model.safetensors').is_file():shards=['model.safetensors']
        else:issues.append('safetensors index/weights missing')
        results.append({'model':item['model'],'revision':item['revision'],'snapshot':str(folder),
            'status':'ready' if not issues else 'needs_setup','issues':issues,'weight_shards':len(shards),
            'weight_bytes':sum((folder/name).stat().st_size for name in shards if (folder/name).is_file()),
            'weights_loaded_or_hashed':False,'model_inference':False})
    return results


def _order(items):
    by_id={item['id']:item for item in items}
    if len(by_id)!=len(items):raise ValueError('duplicate readiness task identity')
    visited=set();active=set();ordered=[]
    def visit(identity):
        if identity not in by_id:raise ValueError('unknown readiness dependency: '+identity)
        if identity in active:raise ValueError('readiness dependency cycle')
        if identity in visited:return
        active.add(identity)
        for dependency in by_id[identity].get('dependencies',[]):visit(dependency)
        active.remove(identity);visited.add(identity);ordered.append(by_id[identity])
    for identity in by_id:visit(identity)
    return ordered


def inspect(config):
    from .snapshots import workspace_root
    root=Path(config.get('root') or workspace_root(Path(__file__).resolve().parents[3])).resolve()
    rows=[];states={}
    for item in _order(config['items']):
        evidence=[_check(root,spec) for spec in item.get('evidence',[])]
        missing=[entry for entry in evidence if not entry['passed']]
        dependencies=[identity for identity in item.get('dependencies',[]) if states[identity]!='ready']
        if item.get('policy')=='deferred_optional':state='deferred_optional'
        elif item.get('scientific_decision_required'):state='needs_scientific_decision'
        elif dependencies:state='blocked_dependency'
        elif missing:
            purposes={entry['purpose'] for entry in missing}
            state='needs_build' if 'source' in purposes else 'needs_validation' if 'validation' in purposes else 'needs_execution'
        else:state='ready'
        states[item['id']]=state
        rows.append({'id':item['id'],'title':item['title'],'category':item['category'],'status':state,
            'dependencies':item.get('dependencies',[]),'blocking_dependencies':dependencies,
            'scientific_prerequisite':item.get('scientific_decision_required'),
            'description':item.get('description',''),'commands':item.get('commands',[]),
            'evidence':evidence,'jobs_submitted':False})
    environment=config.get('environment',{});checks={}
    if environment.get('python'):
        # Keep the virtualenv entrypoint; resolving its symlink chooses base Python.
        python=_path(root,environment['python']).absolute();checks['python']={'path':str(python),'exists':python.is_file()}
    checks['package_versions']={}
    for package in environment.get('packages',[]):
        try:checks['package_versions'][package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:checks['package_versions'][package]=None
    if environment.get('cache'):checks['model_cache']=inspect_cache(environment['cache'],root)
    jobs={};scheduler_errors=[]
    if config.get('jobs'):
        from .experiment_status import query_scheduler
        definitions=_metadata(_path(root,config['jobs']))
        ids=[str(value) for value in definitions.values()]
        observed,scheduler_errors=query_scheduler(ids)
        jobs={name:{'job_id':str(value),**observed.get(str(value),{'state':'UNKNOWN'})}
              for name,value in definitions.items()}
    return {'status':'inventory_complete','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'config_hash':digest(config),'root':str(root),'items':rows,'counts':dict(Counter(row['status'] for row in rows)),
        'environment':checks,'jobs':jobs,'scheduler_errors':scheduler_errors,
        'jobs_submitted':False,'model_inference':False,'generated_holdouts_opened':False,
        'scope':'Readiness evidence only; software availability is separate from scientific qualification.'}


def run(config):
    result=inspect(config);write_json(config['output'],result)
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=('id','category','status','title','prerequisite'))
    writer.writeheader()
    for item in result['items']:
        writer.writerow({'id':item['id'],'category':item['category'],'status':item['status'],
            'title':item['title'],'prerequisite':item['scientific_prerequisite'] or ', '.join(item['blocking_dependencies'])})
    if config.get('csv'):
        path=Path(config['csv']);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(stream.getvalue())
    lines=['# Preparation and execution readiness','',
        'This inventory reads metadata and file existence only. It does not submit jobs, load models or open reserved outcomes. A ready implementation is not a supported scientific claim.','',
        '| Task | Category | Readiness | Prerequisite |','|---|---|---|---|']
    for item in result['items']:
        prerequisite=item['scientific_prerequisite'] or ', '.join(item['blocking_dependencies']) or '—'
        lines.append('| '+' | '.join(str(value).replace('|','\\|') for value in (item['title'],item['category'],item['status'],prerequisite))+' |')
    for item in result['items']:
        lines+=['','## '+item['title'],'',item['description']]
        if item['commands']:lines+=['']+['- `'+command+'`' for command in item['commands']]
        failed=[entry for entry in item['evidence'] if not entry['passed']]
        if failed:lines+=['']+['- '+entry['path']+': '+entry['issue'] for entry in failed]
    if result['jobs']:
        lines+=['','## Scheduler observations','','| Task | Job | State | Reason |','|---|---:|---|---|']
        for name,job in result['jobs'].items():
            lines.append('| '+' | '.join(str(value).replace('|','\\|') for value in
                (name,job['job_id'],job['state'],job.get('reason','—')))+' |')
        lines+=['']+['- '+error for error in result['scheduler_errors']]
    lines+=['','Environment/cache metadata and exact evidence are in the companion JSON. Model shards are counted by metadata; weights are never loaded or hashed by this inventory.','']
    path=Path(config['report']);path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(lines))
    return result
