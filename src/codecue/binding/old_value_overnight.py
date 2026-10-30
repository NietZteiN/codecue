"""Metadata-only overnight execution, integrity, logging and morning checks.

This checker never submits jobs, loads models, reads source records or decodes
numeric arrays. Gate failure is a scientific result, separate from job failure.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROLE='discovery_old_value_overnight_check_v1'
MODEL_ROLE='discovery_old_value_calibration_v1'
WORK=('regression','llama8b_preflight','codellama34b_preflight','llama8b_behavior','codellama34b_behavior')
AUX=('publication','morning')
MODELS={'meta-llama/Llama-3.1-8B-Instruct':'llama8b','codellama/CodeLlama-34b-Instruct-hf':'codellama34b'}
FAILED={'FAILED','CANCELLED','TIMEOUT','PREEMPTED','NODE_FAIL','BOOT_FAIL','OUT_OF_MEMORY','DEADLINE','REVOKED'}
ACTIVE={'RUNNING','COMPLETING'}
WAIT={'PENDING','CONFIGURING','SUSPENDED','REQUEUED','RESIZING'}
LIMIT=16*1024**2


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _sha(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):result.update(block)
    return result.hexdigest()


def _is_sha(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def _path(root,value):
    if not isinstance(value,str) or not value:raise ValueError('explicit metadata paths required')
    path=Path(value);path=path if path.is_absolute() else root/path
    resolved=path.resolve()
    if resolved!=root and root not in resolved.parents:raise ValueError('metadata path escapes workspace')
    if path.is_symlink():raise ValueError('metadata symlinks are not permitted')
    return resolved


def _read(path,limit=LIMIT):
    if path.suffix!='.json' or path.stat().st_size>limit:raise ValueError('bounded JSON metadata required')
    data=json.loads(path.read_text())
    if not isinstance(data,dict):raise ValueError('metadata object required')
    return data


def _pin(root,entry,*,hash_file=True):
    if not isinstance(entry,dict) or set(entry)!={'path','sha256','bytes'} or not _is_sha(entry['sha256']):
        raise ValueError('exact artifact pin required')
    path=_path(root,entry['path'])
    if type(entry['bytes']) is not int or entry['bytes']<0 or path.stat().st_size!=entry['bytes']:
        raise ValueError('artifact size differs: '+str(path))
    if hash_file and _sha(path)!=entry['sha256']:raise ValueError('artifact SHA differs: '+str(path))
    return path


def _config(config,root):
    fields={'evaluation_role','suite_root','model_configs','source_pointer','baseline_handoff','morning_at','report','morning_report'}
    if not isinstance(config,dict) or set(config)!=fields or config.get('evaluation_role')!=ROLE:
        raise ValueError('exact overnight checker configuration required')
    morning=datetime.fromisoformat(config['morning_at'])
    if morning.tzinfo is None:raise ValueError('timezone-aware morning required')
    inputs=config['model_configs'];baseline=config['baseline_handoff']
    if (not isinstance(inputs,list) or len(inputs)!=2 or any(not isinstance(i,dict) or set(i)!={'path','sha256'} or not _is_sha(i['sha256']) for i in inputs)
            or not isinstance(baseline,dict) or set(baseline)!={'path','sha256'} or not _is_sha(baseline['sha256'])):
        raise ValueError('two model pins and immutable baseline pin required')
    all_inputs=[_path(root,i['path']) for i in inputs]+[_path(root,baseline['path']),_path(root,config['source_pointer'])]
    outputs=[_path(root,config[k]) for k in ('suite_root','report','morning_report')]
    if len(set(all_inputs))!=len(all_inputs) or len(set(outputs))!=3 or any(p==q for p in all_inputs for q in outputs):
        raise ValueError('distinct inputs and outputs required')
    if any(p.suffix!='.md' for p in outputs[1:]):raise ValueError('Markdown reports required')
    return morning


def _source(root,config,deep):
    value=_read(_path(root,config['source_pointer']))
    if not _is_sha(value.get('code')) or not isinstance(value.get('snapshot_id'),str):raise ValueError('frozen source pointer required')
    folder=_path(root,value['snapshot']);manifest=_read(folder/'frozen_manifest.json')
    if (manifest['snapshot_id']!=value['snapshot_id'] or manifest['code']['source_sha256']!=value['code']
            or _digest(manifest['code']['source_files'])!=value['code']):
        raise ValueError('frozen source identity differs')
    if deep:
        for name,expected in {**manifest['code']['source_files'],**manifest['config_files']}.items():
            if _sha(_path(root,str(folder/name)))!=expected:raise ValueError('frozen source/config changed: '+name)
    return value


def _source_matches(actual,expected):
    return (isinstance(actual,dict) and actual.get('snapshot_id')==expected['snapshot_id']
            and actual.get('source_sha256',actual.get('code'))==expected['code'])


def _baseline(root,config,deep):
    item=config['baseline_handoff'];path=_path(root,item['path'])
    if _sha(path)!=item['sha256']:raise ValueError('immutable baseline handoff changed')
    handoff=_read(path)
    if handoff.get('status')!='complete_audited' or len(handoff.get('pins',[]))!=161:
        raise ValueError('complete 161-pin baseline required')
    hashes=0
    for pin in handoff['pins']:
        candidate=_path(root,pin['path']);hashed=deep or (candidate.suffix!='.npz' and pin['bytes']<=2*1024**2)
        _pin(root,pin,hash_file=hashed);hashes+=hashed
    return dict(status='passed',artifacts=161,hashes_checked=hashes,deep=deep,
        historical_overview_pins='Prior followup README/checklist/backlog hashes describe historical completion versions; current overviews are not frozen scientific inputs.')


def scheduler(ids,runner=None):
    runner=runner or subprocess.run;ids=sorted(set(ids));jobs={};errors=[]
    if not ids:return jobs,errors
    if any(not isinstance(v,str) or not v.isdigit() for v in ids):raise ValueError('numeric owned job IDs required')
    commands=[['sacct','-n','-X','-P','-j',','.join(ids),'--format=JobIDRaw,State%32,ExitCode,Reason%120'],
              ['squeue','-h','-j',','.join(ids),'-o','%i|%T|%r']]
    for command in commands:
        try:result=runner(command,capture_output=True,text=True,timeout=20,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:errors.append(command[0]+': '+str(exc));continue
        if result.returncode:errors.append(command[0]+': '+result.stderr.strip());continue
        for line in result.stdout.splitlines():
            values=line.strip().split('|')
            if len(values)<3 or values[0] not in ids:continue
            entry=jobs.setdefault(values[0],{});entry['state']=values[1].split()[0].rstrip('+')
            if command[0]=='sacct':entry.update(exit_code=values[2],reason=values[3] if len(values)>3 else '')
            else:entry['reason']=values[2]
    return jobs,errors


def committed_responses(path):
    """Count a bounded committed JSONL prefix; leave interrupted tails untouched."""
    if not path.exists():return dict(committed=0,trailing_partial=False,invalid_committed_line=None)
    if path.stat().st_size>512*1024**2:raise ValueError('response metadata exceeds bound')
    count=0;seen=set();partial=False;bad=None
    with path.open('rb') as stream:
        while True:
            line=stream.readline(2*1024**2+1)
            if not line:break
            if len(line)>2*1024**2:raise ValueError('response line exceeds bound')
            if not line.endswith(b'\n'):partial=True;break
            try:
                record=json.loads(line);key=tuple(record[k] for k in ('section','task','id'))
                if any(not isinstance(v,str) or not v for v in key) or key in seen:raise ValueError('response key differs')
            except (ValueError,KeyError,TypeError):bad=count+1;break
            seen.add(key);count+=1
            if count>200000:raise ValueError('response count exceeds metadata bound')
    return dict(committed=count,trailing_partial=partial,invalid_committed_line=bad)


def _model(root,cfg,source,deep):
    folder=_path(root,cfg['run_dir']);backend=folder/'checkpoint_suite';progress=committed_responses(backend/'responses.jsonl')
    native_path=_path(root,cfg['preflight_result']);native=_read(native_path) if native_path.exists() else {}
    planned=native.get('cases');preflight_path=folder/'routing_preflight_v1.json';preflight=_read(preflight_path) if preflight_path.exists() else {}
    prepared=(preflight.get('status')=='passed' and preflight.get('config_hash')==_digest(cfg)
              and _source_matches(preflight.get('source'),source) and native.get('status')=='passed'
              and native.get('config_hash')==_digest(cfg) and native.get('source_sha256')==source['code']
              and native.get('model_inference') is False and native.get('generated_holdouts_opened') is False
              and type(planned) is int and planned>0)
    result=dict(model=cfg['model'],planned=planned,progress=progress,preflight_valid=prepared,
        completed_outputs_valid=False,scientific_status='pending',reliability_gate=None)
    completion=folder/'routing_completion_v1.json'
    if not completion.exists():return result
    receipt=_read(completion)
    if (receipt.get('status')!='complete_audited' or receipt.get('evaluation_role')!=MODEL_ROLE
            or receipt.get('config_hash')!=_digest(cfg) or not _source_matches(receipt.get('source'),source)
            or receipt.get('new_fits')!=0 or receipt.get('generated_holdouts_opened') is not False
            or set(receipt.get('artifacts',{}))!={'review','report'}):raise ValueError('completed model receipt differs')
    review_path=_pin(root,receipt['artifacts']['review']);report_path=_pin(root,receipt['artifacts']['report'])
    if review_path!=_path(root,cfg['review_artifact']) or report_path!=_path(root,cfg['report']):raise ValueError('model output paths differ')
    review=_read(review_path)
    if (not prepared or review.get('status')!='complete_audited' or review.get('complete') is not True
            or review.get('evaluation_role')!=MODEL_ROLE or review.get('config_hash')!=_digest(cfg)
            or review.get('generated_holdouts_opened') is not False or review.get('new_fits')!=0
            or review.get('model')!=cfg['model'] or not _source_matches(review.get('source'),source)
            or receipt.get('scored_cases')!=planned or review.get('n')!=planned or progress['committed']!=planned
            or progress['trailing_partial'] or progress['invalid_committed_line'] is not None):raise ValueError('model committed coverage differs')
    gate=review.get('reliability_gate',{})
    if gate.get('status') not in ('passed','failed') or gate.get('automatic_causal_launch') is not False:
        raise ValueError('explicit behavioral gate and no automatic causal launch required')
    for name,item in review.get('artifacts',{}).items():
        candidate=_path(root,item['path']);_pin(root,item,hash_file=deep or candidate.suffix=='.json')
    result.update(completed_outputs_valid=True,scientific_status='gate_failed' if gate['status']=='failed' else 'calibration_passed',
        reliability_gate=gate,gate_cells=review.get('gate_cells'),paired_contrasts=review.get('paired_contrasts'),
        equality_control_cells=review.get('equality_control_cells'),accounting=review.get('accounting'))
    return result


def _logging(state,observed,now):
    interval=state.get('interval_minutes',10);last=state.get('last_success_utc');age=None
    if isinstance(last,str):
        try:age=(now-datetime.fromisoformat(last.replace('Z','+00:00'))).total_seconds()
        except (ValueError,TypeError):pass
    pending=sum(observed.get(str(item.get('job_id')),{}).get('state') in WAIT for item in state.get('jobs',[]))
    fresh=age is not None and 0<=age<=2*interval*60
    return dict(enabled=state.get('enabled') is True,pending_guards=pending,last_success_utc=last,
        last_success_age_seconds=age,fresh_within_two_intervals=fresh,interval_minutes=interval,
        guard_health=state.get('enabled') is True and pending>=2 and not state.get('last_scheduler_error') and not state.get('last_tick_error'),
        queue=[dict(job_id=str(item.get('job_id')),**observed.get(str(item.get('job_id')),{})) for item in state.get('jobs',[])])


def _write(path,value,*,immutable=False):
    payload=value.encode() if isinstance(value,str) else (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    if immutable and path.exists():
        if path.read_bytes()!=payload:raise ValueError('immutable check snapshot differs')
        return
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        temporary=Path(stream.name);stream.write(payload);stream.flush();os.fsync(stream.fileno())
    try:
        if immutable:
            try:os.link(temporary,path)
            except FileExistsError:
                if path.read_bytes()!=payload:raise ValueError('immutable concurrent snapshot differs')
        else:os.replace(temporary,path)
    finally:
        if temporary.exists():temporary.unlink()


def _report(result):
    lines=['# Old-value overnight check','',f"Checked: {result['checked_at']}. Execution: **{result['status']}**. Behavioral gate: **{result['scientific_status']}**.",'',
        '| Stage | Job | State | Reason |','|---|---:|---|---|']
    for stage in WORK+AUX:
        item=result['stages'][stage];lines.append(f"| {stage} | {item.get('job_id','')} | {item['status']} | {str(item.get('reason','')).replace('|','/')} |")
    lines+=['','| Model | Committed / planned | Gate |','|---|---:|---|']
    for name in sorted(result['models']):
        item=result['models'][name];lines.append(f"| {name} | {item.get('progress',{}).get('committed',0)} / {item.get('planned')} | {item.get('scientific_status','pending')} |")
    logging=result['logging'];lines+=['',f"Logging enabled: {logging['enabled']}; pending guards: {logging['pending_guards']}; last successful export age: {logging['last_success_age_seconds']} seconds; fresh within two intervals: {logging['fresh_within_two_intervals']}.",'',
        'Job completion and behavioral gate qualification are separate. This check never qualifies a causal mechanism or starts another experiment. Existing overview-document hashes are historical; the immutable scientific handoff is checked separately.','']
    if result['issues']:lines+=['Issues:','',*['- '+item for item in result['issues']],'']
    if result['scheduler_errors']:lines+=['Scheduler-query warnings:','',*['- '+item for item in result['scheduler_errors']],'']
    return '\n'.join(lines)


def check(config,deep=False,morning=False,*,root=None,now=None,runner=None):
    from .snapshots import workspace_root
    root=Path(root).resolve() if root is not None else workspace_root(Path(__file__).resolve().parents[3])
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('timezone-aware check time required')
    if type(deep) is not bool or type(morning) is not bool:raise ValueError('boolean check flags required')
    target=_config(config,root);out=_path(root,config['suite_root']);issues=[];models={};source=None;baseline={}
    for kind,operation in [('source',lambda:_source(root,config,deep)),('baseline',lambda:_baseline(root,config,deep))]:
        try:
            value=operation()
            if kind=='source':source=value
            else:baseline=value
        except (OSError,ValueError,KeyError,TypeError) as exc:issues.append(kind+': '+str(exc))
    for pin in config['model_configs']:
        path=_path(root,pin['path'])
        if _sha(path)!=pin['sha256']:raise ValueError('model config pin changed')
        cfg=_read(path,64*1024);name=MODELS.get(cfg.get('model'))
        protected={_path(root,cfg[k]) for k in ('dataset','prepared_cases','preflight_result','report','review_artifact','declared_plan') if isinstance(cfg.get(k),str)}
        if any(_path(root,config[k]) in protected for k in ('report','morning_report')):raise ValueError('checker reports cannot replace model inputs/outputs')
        if name is None or name in models or cfg.get('evaluation_role')!=MODEL_ROLE:raise ValueError('two distinct supported model configurations required')
        try:models[name]=_model(root,cfg,source,deep) if source else dict(error='source unavailable')
        except (OSError,ValueError,KeyError,TypeError) as exc:models[name]=dict(error=str(exc));issues.append(name+': '+str(exc))
    jobs_path=out/'jobs_v1.json';jobs=_read(jobs_path) if jobs_path.exists() else {}
    if set(jobs)-set(WORK+AUX) or any(not isinstance(j,str) or not j.isdigit() for j in jobs.values()):raise ValueError('owned stage/job mapping required')
    logging_path=root/'artifacts/binding/experiment_log/scheduler_state.json';logging_state=_read(logging_path) if logging_path.exists() else {}
    observed,errors=scheduler(list(jobs.values())+[str(j['job_id']) for j in logging_state.get('jobs',[])],runner)
    qa_path=out/'software_validation_review_v1.json';qa=_read(qa_path) if qa_path.exists() else {}
    counts=qa.get('counts',{});qa_valid=(qa.get('status')=='passed' and source is not None and _source_matches(qa.get('source'),source)
        and type(counts.get('tests')) is int and counts['tests']>0 and all(counts.get(k)==0 for k in ('failures','errors','skipped')))
    junit=out/'regression_v1.xml'
    try:
        suites=ET.parse(junit).getroot().findall('testsuite')
        actual={k:sum(int(v.attrib.get(k,0)) for v in suites) for k in ('tests','failures','errors','skipped')}
        qa_valid=qa_valid and bool(suites) and actual==counts and _sha(junit)==qa.get('junit_sha256')
    except (OSError,ValueError,ET.ParseError):qa_valid=False
    stages={}
    for key in WORK+AUX:
        jid=jobs.get(key);job=observed.get(jid,{});raw=job.get('state');item=dict(job_id=jid,raw_state=raw,reason=job.get('reason',''))
        status='waiting' if jid is None or raw in WAIT else 'running' if raw in ACTIVE else 'failed' if raw in FAILED else 'unknown'
        if raw=='COMPLETED':
            valid=True if key in AUX else qa_valid if key=='regression' else models.get(key.split('_')[0],{}).get('preflight_valid' if key.endswith('preflight') else 'completed_outputs_valid',False)
            status='completed' if job.get('exit_code') in ('0','0:0') and valid else 'failed'
            if not valid:item['reason']='scheduler success without complete matching output proof'
        item['status']=status;stages[key]=item
    work_status=[stages[k]['status'] for k in WORK];complete=all(s=='completed' for s in work_status)
    failed_stage=any(stages[k]['status']=='failed' for k in WORK+AUX)
    status='failed' if issues or failed_stage else 'complete' if complete else 'running' if 'running' in work_status else 'waiting'
    gates=[v.get('scientific_status','pending') for v in models.values()]
    scientific='gate_failed' if 'gate_failed' in gates else 'calibration_passed' if len(gates)==2 and all(g=='calibration_passed' for g in gates) else 'pending'
    result=dict(evaluation_role=ROLE,config_hash=_digest(config),checked_at=now.isoformat(),status=status,scientific_status=scientific,
        source=source,baseline=baseline,stages=stages,models=models,logging=_logging(logging_state,observed,now),issues=issues,
        scheduler_errors=errors,all_scientific_work_complete=complete,causal_qualification=False,new_model_queries=0,new_fits=0,
        source_records_opened=False,score_arrays_opened=False,model_loaded=False,morning_due=now>=target)
    result['needs_attention']=(status=='failed' or bool(errors) or not result['logging']['guard_health'] or not result['logging']['fresh_within_two_intervals'])
    for stem,report_path,due in [('completion_check_v1',out/'completion_check_v1.md',complete),('morning_review_v1',_path(root,config['morning_report']),now>=target)]:
        path=out/(stem+'.json')
        if due and not path.exists():_write(path,result,immutable=True);_write(report_path,_report(result),immutable=True)
        elif due:
            previous=_read(path)
            if previous.get('config_hash')!=result['config_hash']:raise ValueError('historical snapshot configuration differs')
            _write(report_path,_report(previous),immutable=True)
        result[stem]=str(path) if path.exists() else None
    _write(out/'check_live_v1.json',result);_write(_path(root,config['report']),_report(result))
    try:
        from .experiment_log import safe_emit_event
        safe_emit_event('artifact_written',root=root,payload={'path':str(out/'check_live_v1.json')})
    except Exception:pass
    return result
