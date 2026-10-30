"""Independent metadata and streaming-byte audit of completed old-value suite."""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
ROOT=Path('/work/jvl210002/migration/codecue')
FOLDER=ROOT/'artifacts/binding/old_value_overnight/20261028_v1'
REPORT=ROOT/'reports/binding/old_value_overnight_postrun_integrity_v1.md'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def read(p):return json.loads(p.read_text())
def main():
    issues=[];checked={};checks={}
    def check(condition,message):
        if not condition:issues.append(message)
    def pin(item,label):
        p=ROOT/item['path'];actual={'path':item['path'],'bytes':p.stat().st_size,'sha256':sha(p)}
        check(actual['bytes']==item['bytes'] and actual['sha256']==item['sha256'],f'{label}: pin mismatch {p}')
        prior=checked.get(item['path']);check(prior is None or prior==actual,f'inconsistent pin {p}')
        checked[item['path']]=actual
    completion=read(FOLDER/'completion_review_v1.json');pipeline=read(FOLDER/'completion_pipeline_v1.json')
    for label,items in [('completion_input',completion['input_pins']),('completion_output',completion['output_pins']),('readiness',completion['readiness']['pins']),('pipeline_helper',pipeline['helper_pins'])]:
        for item in items:pin(item,label)
    pin(pipeline['readiness_config'],'readiness config')
    snapshot=Path(completion['source']['snapshot']);frozen=read(snapshot/'frozen_manifest.json')
    for group in ['source_files','config_files']:
        entries=frozen['code'][group] if group=='source_files' else frozen[group]
        for relative,want in entries.items():
            actual=sha(snapshot/relative);check(actual==want,f'frozen {relative} changed')
    checks['frozen_snapshot']={'snapshot_id':frozen['snapshot_id'],'source_sha256':frozen['code']['source_sha256'],'source_files':len(frozen['code']['source_files']),'config_files':len(frozen['config_files'])}
    qa=read(FOLDER/'software_validation_review_v1.json');xml=ET.parse(FOLDER/'regression_v1.xml').getroot();suite=xml.find('testsuite')
    counts={k:int(suite.attrib[k]) for k in ['tests','failures','errors','skipped']}
    check(counts==qa['counts']=={'tests':2280,'failures':0,'errors':0,'skipped':0},'QA counts')
    check(sha(FOLDER/'regression_v1.xml')==qa['junit_sha256'],'QA JUnit hash')
    archive_review=read(FOLDER/'regression_archive_review_v1.json');check(sha(FOLDER/'regression_sources_v1.zip')==archive_review['archive_sha256'],'QA archive hash')
    with zipfile.ZipFile(FOLDER/'regression_sources_v1.zip') as archive:
        check(len(archive.namelist())==109,'archive source count')
        for relative,want in qa['software_file_sha256'].items():
            check(hashlib.sha256(archive.read(relative)).hexdigest()==want,f'archived QA source {relative}')
            check(sha(ROOT/relative)==want,f'current QA source {relative}')
    checks['software_validation']={'status':qa['status'],'counts':counts,'source_files':len(qa['software_file_sha256']),'archive_source_files':109}
    models={};total_scored=0;total_queries=0;total_warmups=0
    for name in ['llama8b','codellama34b']:
        folder=FOLDER/name;receipt=read(folder/'routing_completion_v1.json');attempts=read(folder/'routing_attempts_v1.json')['attempts'];audit=read(folder/'checkpoint_suite/audit.json');native=read(folder/'tokenizer_preflight.json');preflight=read(folder/'routing_preflight_v1.json');manifest=read(folder/'checkpoint_suite/manifest.json');review=read(folder/'review_v1.json')
        for parent in [receipt,preflight,review]:
            for item in parent.get('artifacts',{}).values():pin(item,f'{name} artifacts')
        check(receipt['status']=='complete_audited' and receipt['scored_cases']==audit['evaluated']==audit['planned']==manifest['evaluated']==20160,f'{name} completion cases')
        check(native['status']=='passed' and native['cases']==20160 and native['model_inference'] is False,f'{name} native preflight')
        check(native['source_sha256']==frozen['code']['source_sha256'],f'{name} source')
        check(len(attempts)==1 and attempts[0]['status']=='complete' and len(manifest['attempts'])==1,f'{name} attempts')
        warmups=sum(a['confirmed_warmup_requests'] for a in attempts);check(warmups==8 and receipt['new_model_queries']==20160+warmups,f'{name} warmup accounting')
        check(review['reliability_gate']['status']=='failed',f'{name} gates should remain failed')
        total_scored+=receipt['scored_cases'];total_queries+=receipt['new_model_queries'];total_warmups+=warmups
        models[name]={'status':receipt['status'],'scored_responses':receipt['scored_cases'],'warmups':warmups,'total_model_queries':receipt['new_model_queries'],'correct':sum(c['correct'] for c in audit['cells']),'valid':sum(c['valid'] for c in audit['cells']),'scientific_gate_status':review['reliability_gate']['status'],'native_preflight_status':native['status'],'native_model_inference':native['model_inference'],'attempts':len(attempts)}
    check(total_scored==completion['total_scored_responses']==40320 and total_warmups==16 and total_queries==40336,'aggregate accounting')
    publog=ROOT/'log/slurm/481706_oldvalue-publication.out';pubtext=publog.read_text();statuses=[]
    for line in pubtext.splitlines():
        if line.startswith('{'):statuses.append(json.loads(line).get('status'))
    check(statuses==['published','byte_identical_reproduction'],'actual two publication statuses')
    checks['publication']={'job_id':'481706','statuses':statuses,'log_sha256':sha(publog),'input_pins':len(completion['input_pins']),'output_pins':len(completion['output_pins']),'readiness_pins':len(completion['readiness']['pins']),'pipeline_helpers':len(pipeline['helper_pins'])}
    state=read(FOLDER/'monitor_state_v1.json');records=[json.loads(line) for line in (FOLDER/'monitor_checks_v1.jsonl').read_text().splitlines() if line.strip()];lastlog=ROOT/'log/slurm/481724_oldvalue-watch-b69ced9ff61d.out'
    check(state['terminal'] is True and len(records)==3,'monitor terminal and three checks')
    check(all(r['needs_attention'] is False for r in records),'monitor attention')
    check('terminal_no_successor' in lastlog.read_text(),'last monitor did not stop')
    checks['monitor']={'checks':len(records),'tick_jobs':[r['monitor_job_id'] for r in records],'intervals_seconds':[records[i]['checked_epoch']-records[i-1]['checked_epoch'] for i in range(1,len(records))],'terminal':state['terminal'],'last_job':'481724','last_job_status':'terminal_no_successor','last_job_log_sha256':sha(lastlog)}
    jobids='481692,481693,481694,481704,481705,481706,481708,481709,481718,481724'
    accounting=subprocess.run(['sacct','-n','-X','-P','-j',jobids,'--format=JobIDRaw,State%32,ExitCode,Elapsed,Start,End'],check=True,text=True,capture_output=True).stdout
    rows=[line.split('|') for line in accounting.splitlines() if line.strip()];check(len(rows)==10 and all(row[1]=='COMPLETED' and row[2]=='0:0' for row in rows),'actual completed Slurm stages')
    morning=subprocess.run(['scontrol','show','job','481707'],check=True,text=True,capture_output=True).stdout
    check('Dependency=(null)' in morning and 'JobState=PENDING' in morning and 'EligibleTime=2026-10-29T08:00:00' in morning,'independent morning schedule')
    checks['scheduler']={'completed_job_accounting':accounting,'morning_job_id':'481707','morning_start_local':'2026-10-29T08:00:00-05:00','morning_independent':True,'morning_raw_job':morning}
    logging=read(ROOT/'artifacts/binding/experiment_log/scheduler_state.json');now=datetime.now(timezone.utc);last=datetime.fromisoformat(logging['last_success_utc']);age=(now-last).total_seconds()
    queue=subprocess.run(['squeue','-u','jvl210002','-h','-o','%i|%j|%T|%R'],check=True,text=True,capture_output=True).stdout
    guards=[line for line in queue.splitlines() if '|'+logging['job_name']+'|' in line]
    check(logging['enabled'] and age<=2*logging['interval_minutes']*60 and len(guards)>=2,'current logging freshness/guards')
    checks['logging']={'enabled':logging['enabled'],'last_success_utc':logging['last_success_utc'],'last_success_age_seconds':age,'interval_minutes':logging['interval_minutes'],'fresh_within_two_intervals':age<=2*logging['interval_minutes']*60,'live_guards':guards,'last_tick_error':logging.get('last_tick_error')}
    counts=completion['readiness']['counts'];check(counts=={'deferred_optional':3,'needs_scientific_decision':9,'ready':62},'readiness counts')
    review={'evaluation_role':'discovery_old_value_postrun_integrity_v1','status':'passed' if not issues else 'needs_attention','checked_at':now.isoformat(),'source':completion['source'],'operational_status':'complete_audited','scientific_status':'gate_failed','causal_qualification':False,'new_model_queries':0,'new_fits':0,'arrays_opened':False,'response_records_parsed':False,'source_records_parsed':False,'prepared_records_parsed':False,'total_scored_responses':total_scored,'total_original_warmups':total_warmups,'total_original_model_queries':total_queries,'models':models,'readiness_counts':counts,'checks':checks,'verified_pins':list(checked.values()),'issues':issues}
    path=FOLDER/'postrun_integrity_review_v1.json';text=json.dumps(review,indent=2,sort_keys=True)+'\n';check(not path.exists() or path.read_text()==text,'audit target exists')
    if path.exists():raise RuntimeError('Review is immutable; use new version to repeat')
    path.write_text(text)
    lines=['# Old-value overnight post-run integrity check','',f"Recorded {now.astimezone(ZoneInfo('America/Chicago')).isoformat()}. Status: **{review['status']}**.",'','The two measurements and publication completed successfully. Both scientific reliability gates failed; operational completion does not qualify a causal follow-on.','',f"Verified {len(checked)} distinct metadata/data pins by streaming bytes, plus {len(frozen['code']['source_files'])} frozen source files and {len(frozen['config_files'])} frozen configs. No model calls, fitting, array loading, or response/source/prepared-record parsing occurred.",'','- Full regression: 2,280 passed, zero failures/errors/skips; all 109 archived and current test sources match.','- Both native preparations passed for 20,160 cases each without model inference.','- Scored responses: 40,320; warm-ups: 16; total original model queries: 40,336. Each model used one completed backend attempt.','- Publication job 481706 actually produced `published` and `byte_identical_reproduction` in sequence and completed with exit 0.','- Three periodic checks ran about ten minutes apart. Final cleanup tick 481724 stopped with `terminal_no_successor`; no further suite-monitor successor remains.','- Independent morning job 481707 remains queued for October 29 at 08:00 America/Chicago (UTC−05:00), with no dependency.',f"- Logging last succeeded {logging['last_success_utc']}; age at check {age:.1f} seconds, within the {2*logging['interval_minutes']}-minute threshold. {len(guards)} logger guards are queued.",'','The readiness inventory records 74 tasks: 62 ready, nine requiring scientific decisions, and three optional deferred tasks.','',f"Evidence: `{path.relative_to(ROOT)}`."]
    if issues:lines+=['','Issues:']+[f'- {issue}' for issue in issues]
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':review['status'],'pins':len(checked),'issues':issues,'review':str(path),'report':str(REPORT),'logging_age_seconds':age},sort_keys=True))
if __name__=='__main__':main()
