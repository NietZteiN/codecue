#!/usr/bin/env python
"""Read-only artifact/job checks, with durable local monitoring snapshots."""
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess
from pathlib import Path

from codecue.binding import arithmetic_graph_readouts as readouts,arithmetic_prompt_control as prompts
from codecue.binding import experiment_log_scheduler as scheduler

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/binding/operations/20261030_debug_v1'


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):value.update(chunk)
    return value.hexdigest()


def atomic(path,value):
    data=json.dumps(value,sort_keys=True,indent=2)+'\n';path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name('.'+path.name+f'.{os.getpid()}.pending')
    temporary.write_text(data);temporary.replace(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('phase',choices=['deep','monitor']);parser.add_argument('--label',required=True)
    args=parser.parse_args()
    if not args.label.replace('_','').isalnum():raise ValueError('simple snapshot label required')
    if not os.environ.get('SLURM_JOB_ID'):raise ValueError('operations checks require sbatch')
    watch=json.loads((OUT/'watch_config.json').read_text())
    if sha(__file__)!=watch['checker_sha256']:raise ValueError('monitor implementation changed after submission')
    science={};pins={};attention=[]
    if args.phase=='deep':
        for name in ['llama8b','codellama34b']:
            config=ROOT/f'configs/binding/arithmetic_graph_20261029_v3/{name}_readouts.json'
            readouts.audit(json.loads(config.read_text()));science[name+'_readouts']='passed'
            config=ROOT/f'configs/binding/arithmetic_prompt_control_20261030_v1/{name}.json'
            prompts.audit(json.loads(config.read_text()));science[name+'_prompt_control']='passed'
        for relative in watch['immutable_metadata']:
            path=ROOT/relative
            if not path.resolve().is_relative_to(ROOT/'artifacts/binding'):raise ValueError('explicit binding metadata required')
            pins[relative]=sha(path)
    else:
        prior=json.loads((OUT/'deep_review_v1.json').read_text())
        if prior.get('status')!='passed':attention.append('deep artifact audit did not pass')
        pins=prior['metadata_pins']
        for relative,expected in pins.items():
            if sha(ROOT/relative)!=expected:attention.append('immutable metadata changed: '+relative)
    health=scheduler.status(ROOT)
    if not health.get('healthy'):attention.append('experiment logging is degraded: '+str(health.get('error')))
    ids=watch['watched_jobs']
    result=subprocess.run(['sacct','-X','-n','-P','-j',','.join(ids),
        '--format=JobIDRaw,JobName%80,State%32,ExitCode,Reason%100'],capture_output=True,text=True,timeout=30)
    if result.returncode:raise ValueError('scheduler accounting unavailable: '+result.stderr.strip())
    jobs={}
    for line in result.stdout.splitlines():
        fields=line.split('|')
        if len(fields)<5 or fields[0] not in ids:continue
        job,name,state,exit_code,reason=fields[:5];state=state.split()[0].rstrip('+')
        jobs[job]=dict(name=name,state=state,exit_code=exit_code,reason=reason)
        if state in {'FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','BOOT_FAIL'} or reason=='DependencyNeverSatisfied':
            attention.append(f'watched job {job}: {state}, {reason}')
        elif state=='COMPLETED' and exit_code!='0:0':
            attention.append(f'watched job {job}: nonzero completion code {exit_code}')
    if set(jobs)!=set(ids):attention.append('some watched job IDs are absent from scheduler accounting')
    review=dict(status='needs_attention' if attention else 'passed',phase=args.phase,
        evaluation_role='binding_operations_debug_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),
        slurm_job_id=os.environ['SLURM_JOB_ID'],checker_sha256=sha(__file__),
        scheduler_implementation_sha256=sha(scheduler.__file__),
        scientific_artifact_audits=science,metadata_pins=pins,logger=health,jobs=jobs,attention=attention,
        new_model_queries=0,new_fits=0)
    target=OUT/('deep_review_v1.json' if args.phase=='deep' else 'monitor_'+args.label+'_review.json')
    if target.exists():raise ValueError('monitoring snapshot already exists; preserve it')
    atomic(target,review)
    print(json.dumps(dict(status=review['status'],attention=attention,last_success_utc=health.get('last_success_utc'))))
    return int(bool(attention))


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        job=os.environ.get('SLURM_JOB_ID','manual')
        failure=dict(status='failed',recorded_utc=datetime.now(timezone.utc).isoformat(),
            slurm_job_id=job,error=f'{type(exc).__name__}: {exc}',new_model_queries=0,new_fits=0)
        atomic(OUT/f'failure_{job}_review.json',failure)
        print(json.dumps(failure));raise SystemExit(1)
