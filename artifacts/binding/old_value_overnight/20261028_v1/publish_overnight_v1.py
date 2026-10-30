"""Publish audited old/current calibration from bounded metadata only.

Source/prepared/response records and numeric arrays are never deserialized.
Their declared pins may be stream-hashed. Incomplete execution gets a separate
snapshot; failed scientific gates remain completed, publishable observations.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

SUITE=Path('artifacts/binding/old_value_overnight/20261028_v1')
CHECK_CONFIG=Path('configs/binding/old_value_overnight_20261028_v1/check.json')
ROLE='discovery_old_value_calibration_v1'
PUB_ROLE='discovery_old_value_overnight_publication_v1'
WORK=('regression','llama8b_preflight','codellama34b_preflight','llama8b_behavior','codellama34b_behavior')
MODELS={'meta-llama/Llama-3.1-8B-Instruct':'llama8b','codellama/CodeLlama-34b-Instruct-hf':'codellama34b'}
VARIANTS=('old_value_output_v1','old_value_execute_v1','old_value_history_v1')
MODES=('current','previous');STORAGE=('absent_all_current','retained_other_current');SPLITS=('train','development')
THRESHOLDS=dict(minimum_cell_n=24,minimum_accuracy=.9,maximum_invalid_rate=.05)
MAX_JSON=32*1024**2
INPUTS={}


def require(ok,message):
    if not ok:raise ValueError(message)


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def json_bytes(value):
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    require(len(data)<=MAX_JSON,'Publication metadata exceeds32MiB');return data


def resolve(root,value):
    path=Path(value);path=path if path.is_absolute() else root/path
    require(not path.is_symlink(),'Metadata symlinks are forbidden')
    path=path.resolve();require(path==root or root in path.parents,'Publication path escapes workspace');return path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024**2),b''):h.update(block)
    return h.hexdigest()


def pin(root,path):
    p=resolve(root,path);return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))


def verify_pin(root,item):
    require(isinstance(item,dict) and set(item)=={'path','bytes','sha256'},'Exact artifact pin required')
    actual=pin(root,item['path']);require(actual['bytes']==item['bytes'] and actual['sha256']==item['sha256'],'Artifact SHA/size differs: '+item['path'])
    return resolve(root,item['path'])


def read(root,path,expected=None,limit=MAX_JSON):
    p=resolve(root,path);require(p.suffix=='.json' and p.is_file() and p.stat().st_size<=limit,'Bounded JSON metadata required: '+str(path))
    data=p.read_bytes();entry=dict(path=str(p.relative_to(root)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    if isinstance(expected,str):require(entry['sha256']==expected,'Metadata SHA differs')
    elif expected is not None:require(entry==dict(expected,path=str(resolve(root,expected['path']).relative_to(root))),'Pinned metadata differs')
    require(INPUTS.setdefault(entry['path'],entry)==entry,'Input changed during publication')
    value=json.loads(data);require(isinstance(value,dict),'Metadata object required');return value


def publish(path,data,immutable=True):
    path=Path(path);require(not path.is_symlink(),'Output symlinks forbidden');path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and immutable:
        require(path.read_bytes()==data,'Immutable publication differs: '+str(path));return
    temporary=path.with_name('.'+path.name+'.pending')
    require(not temporary.is_symlink(),'Temporary output symlink forbidden')
    temporary.write_bytes(data);temporary.replace(path)


def source_matches(value,pointer,manifest_sha=None):
    return isinstance(value,dict) and value.get('snapshot_id')==pointer['snapshot_id'] and value.get('source_sha256',value.get('code'))==pointer['code'] and (manifest_sha is None or value.get('frozen_manifest_sha256')==manifest_sha)


def setup(root):
    pointer=read(root,SUITE/'execution_source_v1.json');folder=resolve(root,pointer['snapshot'])
    manifest=read(root,folder/'frozen_manifest.json');manifest_sha=sha(folder/'frozen_manifest.json')
    require(manifest['snapshot_id']==pointer['snapshot_id'] and manifest['code']['source_sha256']==pointer['code'] and digest(manifest['code']['source_files'])==pointer['code'],'Frozen source identity differs')
    for name,expected in {**manifest['code']['source_files'],**manifest['config_files']}.items():
        require(sha(resolve(root,str(folder/name)))==expected,'Frozen source/config SHA differs: '+name)
    require(str(CHECK_CONFIG) in manifest['config_files'],'Checker configuration was not frozen')
    checker=read(root,folder/CHECK_CONFIG,manifest['config_files'][str(CHECK_CONFIG)])
    require(checker['evaluation_role']=='discovery_old_value_overnight_check_v1' and resolve(root,checker['suite_root'])==root/SUITE,'Checker recipe differs')
    pipeline=read(root,SUITE/'completion_pipeline_v1.json')
    require(pipeline['source']==pointer,'Completion pipeline source differs')
    for entry in pipeline['helper_pins']:verify_pin(root,entry)
    readiness_path=verify_pin(root,pipeline['readiness_config'])
    require(str(readiness_path.relative_to(root)) in manifest['config_files'] and manifest['config_files'][str(readiness_path.relative_to(root))]==pipeline['readiness_config']['sha256'],'Readiness configuration was not frozen')
    jobs=read(root,SUITE/'jobs_v1.json');require(not set(jobs)-set(WORK+('publication','morning')) and all(isinstance(v,str) and v.isdigit() for v in jobs.values()),'Declared numeric owned jobs required')
    configs={}
    for item in checker['model_configs']:
        relative=str(resolve(root,item['path']).relative_to(root));require(manifest['config_files'].get(relative)==item['sha256'],'Model config freeze differs')
        cfg=read(root,folder/relative,item['sha256']);require(read(root,item['path'],item['sha256'])==cfg,'Current model config differs from frozen copy');name=MODELS.get(cfg.get('model'))
        require(name and name not in configs and cfg.get('evaluation_role')==ROLE,'Two distinct supported model roles required');configs[name]=cfg
    require(set(configs)=={'llama8b','codellama34b'},'Both models required')
    qa=read(root,SUITE/'software_validation_review_v1.json') if (root/SUITE/'software_validation_review_v1.json').exists() else None
    if qa:
        counts=qa.get('counts',{});require(qa.get('status')=='passed' and source_matches(qa.get('source'),pointer) and type(counts.get('tests')) is int and counts['tests']>0 and all(counts.get(k)==0 for k in ('failures','errors','skipped')),'Full software QA proof differs')
        junit=root/SUITE/'regression_v1.xml';require(sha(junit)==qa['junit_sha256'],'JUnit SHA differs')
        suites=ET.parse(junit).getroot().findall('testsuite');require({k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}==counts,'JUnit counts differ')
    return dict(pointer=pointer,manifest_sha=manifest_sha,checker=checker,pipeline=pipeline,jobs=jobs,configs=configs,qa=qa)


def scheduler(jobs):
    ids=sorted(set(jobs.values()));result=subprocess.run(['sacct','-n','-X','-P','-j',','.join(ids),'--format=JobIDRaw,State%32,ExitCode'],capture_output=True,text=True,check=True,timeout=30)
    return {v[0]:dict(state=v[1].split()[0].rstrip('+'),exit_code=v[2]) for line in result.stdout.splitlines() if len(v:=line.split('|'))>=3 and v[0] in ids}


def point(value):
    n=value.get('n');correct=value.get('correct');invalid=value.get('invalid')
    require(type(n) is int and n>0 and type(correct) is int and 0<=correct<=n and type(invalid) is int and 0<=invalid<=n,'Point counts differ')
    require(value.get('valid')==n-invalid and math.isclose(value['accuracy'],correct/n,abs_tol=1e-14,rel_tol=0) and math.isclose(value['invalid_rate'],invalid/n,abs_tol=1e-14,rel_tol=0),'Point rates differ')
    groups=value.get('per_graph',{});require(groups and value.get('graph_groups')==len(groups) and sum(v['n'] for v in groups.values())==n and sum(v['correct'] for v in groups.values())==correct,'Point graph totals differ')
    require(correct<=n-invalid and all(type(v['n']) is int and v['n']>0 and type(v['correct']) is int and 0<=v['correct']<=v['n'] and math.isclose(v['accuracy'],v['correct']/v['n'],rel_tol=0,abs_tol=1e-14) for v in groups.values()),'Graph point counts/rates differ')
    require(math.isclose(value['group_macro_accuracy'],sum(v['accuracy'] for v in groups.values())/len(groups),abs_tol=1e-14,rel_tol=0),'Point graph mean differs')


def validate_review(review,cfg,pointer,manifest_sha):
    require(review.get('status')=='complete_audited' and review.get('complete') is True and review.get('evaluation_role')==ROLE and review.get('config_hash')==digest(cfg) and source_matches(review.get('source'),pointer,manifest_sha),'Audited model source/role differs')
    require(review.get('model')==cfg['model'] and review.get('model_revision')==cfg['model_revision'] and review.get('n')==review.get('scored_unique_cases')==review.get('generated_responses')==20160,'Complete20160-case model review required')
    require(review.get('new_fits')==0 and review.get('generated_holdouts_opened') is False and review.get('new_intervals') is False,'No-fit/heldout/interval contract differs')
    require(review.get('instructions')==list(VARIANTS) and review.get('unique_sources')==6720 and review.get('source_body_target_pairs')==3360,'Complete source/instruction factorial required')
    for key in ('dataset_sha256','dataset_manifest_sha256','declared_plan_sha256'):require(review.get(key)==cfg[key],'Pinned assay input differs')
    point(review);require(review.get('graph_groups')==60,'All60graph families required');gate=review['reliability_gate'];require(gate.get('thresholds')==THRESHOLDS and set(gate.get('instructions',{}))==set(VARIANTS) and gate.get('automatic_causal_launch') is False and gate.get('causal_design_review_required') is True,'Fixed behavioral gate and morning review required')
    cells=review['gate_cells'];expected={(v,m,s,p) for v in VARIANTS for m in MODES for s in STORAGE for p in SPLITS};seen=set()
    for cell in cells:
        key=tuple(cell[k] for k in ('variant','query_mode','old_storage','split'));require(key in expected and key not in seen,'Duplicate or undeclared primary cell');seen.add(key);point(cell)
        passed=cell['n']>=24 and cell['unique_prompt_n']>=24 and cell['accuracy']>=.9 and cell['invalid_rate']<=.05
        require(cell['passed'] is passed,'Cell gate does not match fixed thresholds')
    require(seen==expected and len(cells)==24,'All24primary cells required')
    controls=review['equality_control_cells'];expected_controls={(v,m,'equal_current',p) for v in VARIANTS for m in MODES for p in SPLITS}
    require({tuple(c[k] for k in ('variant','query_mode','old_storage','split')) for c in controls}==expected_controls and len(controls)==12,'All12equality cells required')
    for cell in controls:point(cell)
    for variant in VARIANTS:
        observed=[c for c in cells if c['variant']==variant];entry=gate['instructions'][variant]
        train=all(c['passed'] for c in observed if c['split']=='train');dev=all(c['passed'] for c in observed if c['split']=='development')
        require(entry['cells']==observed and entry.get('training_qualified') is train and entry.get('development_descriptive_passed') is dev and entry.get('behavioral_calibration_qualified') is (train and dev) and entry.get('numeric_development_qualified') is (train and dev) and entry['status']==('passed' if train and dev else 'failed'),'Instruction qualification differs')
        require(sum(c['n'] for c in cells+controls if c['variant']==variant)==6720,'Instruction source counts differ')
    require(gate['status']==('passed' if all(e['behavioral_calibration_qualified'] for e in gate['instructions'].values()) else 'failed'),'Overall gate differs')
    require(sum(c['n'] for c in cells+controls)==20160 and sum(c['correct'] for c in cells+controls)==review['correct'] and sum(c['invalid'] for c in cells+controls)==review['invalid'],'Cell totals differ')
    axes=('target_slot','target_update_count','last_write_lag','lexical_realization','profile_id','numeric_seed')
    require({c['axis'] for c in review['descriptive_cells']}==set(axes),'Every declared descriptive axis required')
    for axis in axes:
        axis_cells=[c for c in review['descriptive_cells'] if c['axis']==axis]
        for cell in axis_cells:point(cell)
        require(sum(c['n'] for c in axis_cells)==20160 and sum(c['correct'] for c in axis_cells)==review['correct'] and sum(c['invalid'] for c in axis_cells)==review['invalid'],'Descriptive axis totals differ')
    require({c['value'] for c in review['descriptive_cells'] if c['axis']=='numeric_seed'}=={'1151','1297','1459'},'All3numeric seeds required')
    pair_keys=set()
    for pair in review['paired_contrasts']:
        pair_key=tuple(pair[k] for k in ('variant','split','old_storage'));require(pair_key not in pair_keys,'Duplicate paired contrast');pair_keys.add(pair_key)
        outcomes=pair['paired_outcomes'];require(sum(outcomes[k] for k in ('both_correct','previous_only_correct','current_only_correct','neither_correct'))==pair['paired_n'],'Paired outcome partition differs')
        require(outcomes['previous_answered_current']<=outcomes['current_only_correct']+outcomes['neither_correct'] and outcomes['current_answered_previous']<=outcomes['previous_only_correct']+outcomes['neither_correct'],'Intrusion counts differ')
        require(pair.get('confidence_interval') is None,'No new interval is allowed')
        require(math.isclose(pair['previous_minus_current'],(outcomes['previous_only_correct']-outcomes['current_only_correct'])/pair['paired_n'],rel_tol=0,abs_tol=1e-14),'Paired difference differs from outcomes')
        groups=pair['per_graph'];require(groups and pair['graph_groups']==len(groups) and sum(v['n'] for v in groups.values())==pair['paired_n'] and math.isclose(pair['group_macro_previous_minus_current'],sum(v['previous_minus_current'] for v in groups.values())/len(groups),rel_tol=0,abs_tol=1e-14),'Paired graph counts/means differ')
    require(pair_keys=={(v,p,s) for v in VARIANTS for p in SPLITS for s in (*STORAGE,'equal_current')},'Every paired storage contrast required')


def model_metadata(root,name,cfg,data):
    dataset=resolve(root,cfg['dataset']);require(sha(dataset)==cfg['dataset_sha256'],'Assay source bytes differ')
    manifest=read(root,dataset.with_suffix('.manifest.json'),cfg['dataset_manifest_sha256'])
    require(manifest.get('status')=='complete' and manifest.get('evaluation_role')=='discovery_old_value_sources_v1' and manifest.get('sha256')==cfg['dataset_sha256'] and manifest.get('rows')==6720 and manifest.get('independent_python_passed') is True and manifest.get('generated_holdouts_opened') is False,'Independent discovery source manifest differs')
    folder=resolve(root,cfg['run_dir']);stage=folder/'checkpoint_suite';receipt=read(root,folder/'routing_completion_v1.json')
    require(receipt.get('status')=='complete_audited' and receipt.get('evaluation_role')==ROLE and receipt.get('config_hash')==digest(cfg) and source_matches(receipt.get('source'),data['pointer'],data['manifest_sha']) and receipt.get('scored_cases')==20160 and receipt.get('new_fits')==0 and receipt.get('generated_holdouts_opened') is False,'Complete matching model receipt required')
    require(set(receipt['artifacts'])=={'review','report'},'Exact model output receipt required')
    for item in receipt['artifacts'].values():verify_pin(root,item)
    require(resolve(root,receipt['artifacts']['review']['path'])==resolve(root,cfg['review_artifact']) and resolve(root,receipt['artifacts']['report']['path'])==resolve(root,cfg['report']),'Model report/review paths differ')
    review=read(root,cfg['review_artifact'],receipt['artifacts']['review']);validate_review(review,cfg,data['pointer'],data['manifest_sha'])
    paths=dict(backend_audit=stage/'audit.json',responses=stage/'responses.jsonl',backend_manifest=stage/'manifest.json',preparation=folder/'routing_preflight_v1.json',attempts=folder/'routing_attempts_v1.json')
    require(set(review['artifacts'])==set(paths),'Exact backend audit/provenance pins required')
    for key,path in paths.items():
        require(resolve(root,review['artifacts'][key]['path'])==path,'Backend artifact path differs');verify_pin(root,review['artifacts'][key])
    prep=read(root,paths['preparation'],review['artifacts']['preparation']);native=read(root,cfg['preflight_result'])
    require(prep.get('status')=='passed' and prep.get('evaluation_role')==ROLE and prep.get('config_hash')==digest(cfg) and source_matches(prep.get('source'),data['pointer'],data['manifest_sha']),'Native preparation registration differs')
    require(set(prep['artifacts'])=={'prepared_cases','preflight_result'},'Exact native preparation pins required')
    for key,item in prep['artifacts'].items():require(resolve(root,item['path'])==resolve(root,cfg[key]),'Native artifact path differs');verify_pin(root,item)
    require(native.get('status')=='passed' and native.get('config_hash')==digest(cfg) and native.get('source_sha256')==data['pointer']['code'] and native.get('cases')==20160 and native.get('model_inference') is False and native.get('generated_holdouts_opened') is False,'Complete native20160-case proof required')
    backend=read(root,paths['backend_manifest'],review['artifacts']['backend_manifest']);audit=read(root,paths['backend_audit'],review['artifacts']['backend_audit']);summary=read(root,stage/'summary.json');runtime=read(root,stage/'runtime.json')
    require(backend.get('status')=='complete' and backend['identity']['config']==cfg and backend['identity']['code']['source_sha256']==data['pointer']['code'] and backend['identity_hash']==digest(backend['identity']) and backend.get('evaluated')==backend.get('planned')==20160 and backend.get('responses_sha256')==review['artifacts']['responses']['sha256'],'Complete backend source/coverage differs')
    require(audit.get('status')=='passed' and audit.get('identity_hash')==backend['identity_hash'] and audit.get('preflight')==native and audit.get('runtime')==runtime,'Actual backend audit required')
    for document in (audit,summary):require(document.get('complete') is True and document.get('evaluated')==document.get('planned')==20160 and document.get('generated_holdouts_opened') is False,'Backend complete coverage differs')
    require(summary['responses_sha256']==review['artifacts']['responses']['sha256'] and all(audit.get(k)==summary.get(k) for k in ('cells','timings','gpu','interpretation')),'Backend summary/audit differs')
    history=read(root,paths['attempts'],review['artifacts']['attempts']);require(history.get('config_hash')==digest(cfg) and history.get('source')==review['source'] and history.get('attempts'),'Invocation history differs')
    confirmed=uncertain=pending=failed=0;previous=0
    for attempt in history['attempts']:
        prefix=attempt.get('saved_response_prefix');require(attempt.get('status') in ('complete','failed','interrupted') and type(prefix) is int and previous<=prefix<=20160 and attempt.get('pending_scored_cases')==20160-prefix and attempt.get('warmup_request_ceiling')==8,'Completed ordered invocation accounting required');previous=prefix;pending+=20160-prefix
        if attempt['status']=='complete':require(attempt.get('confirmed_warmup_requests')==8,'Successful warm-up count differs');confirmed+=8
        else:require('confirmed_warmup_requests' not in attempt,'Failed warm-up is uncertain');uncertain+=8;failed+=1
    accounting=review['accounting'];expected=dict(scored_responses=20160,confirmed_warmup_requests=confirmed,uncertain_failed_invocation_warmup_ceiling=uncertain,failed_backend_invocations=failed,scored_model_queries_exact=20160 if failed==0 else None,scored_model_queries_lower_bound=20160,scored_model_queries_upper_bound=pending)
    require(all(accounting.get(k)==v for k,v in expected.items()),'Scored/warm-up/retry accounting differs')
    queries=dict(new_model_queries=20160+confirmed if failed==0 else None,new_model_queries_lower_bound=20160+confirmed,new_model_queries_upper_bound=pending+confirmed+uncertain)
    require(all(review.get(k)==v==receipt.get(k) for k,v in queries.items()),'Exact/bounded model-query counts differ')
    timings=summary['timings'];seconds=sum(t['generation_seconds'] for t in timings);cases=sum(t['cases'] for t in timings);tokens=sum(t['output_tokens'] for t in timings)
    require(0<=cases<=20160 and seconds>=0 and (cases==0 or seconds>0),'Consistent committed generation timing metadata required')
    return dict(receipt=receipt,review=review,backend_audit=review['artifacts']['backend_audit'],backend_summary=pin(root,stage/'summary.json'),backend_runtime=pin(root,stage/'runtime.json'),
        throughput=dict(timed_cases=cases,generation_seconds=seconds,requests_per_generation_second=cases/seconds if seconds else None,output_tokens=tokens,output_tokens_per_generation_second=tokens/seconds if seconds else None,scope='Saved invocation timing blocks; loading/warm-up separate and prior retry timings may not be present.'),gpu=summary['gpu'],runtime=runtime)


def report_bytes(models,source):
    lines=['# Historical/current overnight findings','',
        'Execution and artifact audits completed for both checkpoints. Behavioral gate failure remains a result; it does not turn successful execution into a passed scientific claim. No causal intervention is authorized by these measurements.','',
        'Each model answered all20,160 registered instruction/source cases:6,720questions,3,360body/target pairs and1,440bodies on60preserved graph families. Three fixed instructions, both modes and all storage strata remain visible. Numeric, lexical and rotation relatives are dependent discovery views.','',
        '| Model | Instruction | Mode | Old numeric value | Split | Correct / n | Unique prompts | Invalid | Gate |',
        '|---|---|---|---|---|---:|---:|---:|---|']
    for name,model in sorted(models.items()):
        review=model['review']
        for cell in review['gate_cells']+review['equality_control_cells']:
            gate=str(cell['passed']) if 'passed' in cell else 'Excluded equality control'
            lines.append('| '+' | '.join([name,cell['variant'],cell['query_mode'],cell['old_storage'],cell['split'],f"{cell['correct']}/{cell['n']}",str(cell['unique_prompt_n']),str(cell['invalid']),gate])+' |')
    lines+=['','Fixed primary thresholds are at least24responses and24unique prompts, accuracy at least90%, and invalid rate at most5% in every registered primary instruction/mode/storage/split cell. Native-token uniqueness was checked before inference. Equal old/current answers remain controls outside the gate. All instructions remain reported.','',
        '| Model | Instruction | Split | Old numeric value | Pairs | Previous minus current | Graph mean difference | Previous answered current | Current answered previous |',
        '|---|---|---|---|---:|---:|---:|---:|---:|']
    for name,model in sorted(models.items()):
        for pair in model['review']['paired_contrasts']:
            events=pair['paired_outcomes'];lines.append('| '+' | '.join([name,pair['variant'],pair['split'],pair['old_storage'],str(pair['paired_n']),f"{100*pair['previous_minus_current']:.3f} pp",f"{100*pair['group_macro_previous_minus_current']:.3f} pp",str(events['previous_answered_current']),str(events['current_answered_previous'])])+' |')
    lines+=['','| Model | Overall gate | Scored responses | Confirmed warm-ups | Failed/interrupted invocations | Query lower / upper bounds | Timed requests / s | Output tokens / s |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for name,model in sorted(models.items()):
        r=model['review'];a=r['accounting'];t=model['throughput']
        requests=f"{t['requests_per_generation_second']:.3f}" if t['requests_per_generation_second'] is not None else 'Unavailable'
        output=f"{t['output_tokens_per_generation_second']:.3f}" if t['output_tokens_per_generation_second'] is not None else 'Unavailable'
        lines.append(f"| {name} | {r['reliability_gate']['status']} | {r['n']} | {a['confirmed_warmup_requests']} | {a['failed_backend_invocations']} | {r['new_model_queries_lower_bound']} / {r['new_model_queries_upper_bound']} | {requests} | {output} |")
    lines+=['','Timing covers saved generation blocks, with load/warm-up seconds and GPU memory/utilization telemetry preserved separately in comparison_v1.json. Failed invocation work can be uncertain; exact counts are reported only when justified. All errors, graph means, owner/update/lag/lexical/numeric-seed/profile cells and paired outcome partitions remain in each pinned model review.','',
        'Previous-value truth comes from the prefix before the target\'s last write, while every prompt shows the complete body. Literal rereading can solve this task. Accuracy therefore leaves maintained neural state, causal use and unfamiliar-program generalization unresolved. No new interval, model fitting, optional training or final-outcome scoring is introduced.','',
        'Review all prospective cells in the morning before selecting a subsequent design. The suite does not pick the best instruction or launch causal work after a passing gate.','',
        '[Machine comparison](../../artifacts/binding/old_value_overnight/20261028_v1/comparison_v1.json) · [completion proof](../../artifacts/binding/old_value_overnight/20261028_v1/completion_review_v1.json)','']
    text='\n'.join(lines)
    for a,b in [('all20,160','all 20,160'),(':6,720questions,3,360body/target pairs and1,440bodies on60preserved',': 6,720 questions, 3,360 body/target pairs and 1,440 bodies on 60 preserved'),('least24responses and24unique','least 24 responses and 24 unique'),('least90%','least 90%'),('most5%','most 5%')]:text=text.replace(a,b)
    return text.encode()


def incomplete(root,data,stages,issues):
    models={}
    for name,cfg in data['configs'].items():
        path=resolve(root,cfg['run_dir'])/'checkpoint_suite'/'progress.json'
        value=read(root,path) if path.exists() else {}
        models[name]=dict(reported_evaluated=value.get('evaluated',0),planned=value.get('planned',20160),scope='Backend progress metadata only; response records are not recounted by this publisher.')
    snapshot=dict(status='incomplete_action_required',evaluation_role=PUB_ROLE,recorded_utc=datetime.now(timezone.utc).isoformat(),source=data['pointer'],stages=stages,models=models,issues=issues,source_records_opened=False,response_records_opened=False,arrays_opened=False,new_model_queries=0,new_fits=0,causal_qualification=False)
    out=root/SUITE;publish(out/'publication_incomplete_v1.json',json_bytes(snapshot),immutable=False)
    text='# Overnight publication is incomplete\n\nAt least one required stage or output proof is missing or failed. This is not a completed measurement.\n\n'+ '\n'.join('- '+v for v in issues)+'\n\nCheck the live/morning checker for committed-response counts and scheduler reasons. No final comparison or complete review is fabricated.\n'
    publish(root/'reports/binding/old_value_overnight_incomplete_v1.md',text.encode(),immutable=False)
    return dict(status='incomplete_action_required',issues=issues,models=models)


def logging_snapshot(root,value=None):
    path=root/SUITE/'completion_logging_review_v1.json'
    if path.exists():return read(root,path)
    if value is None:
        from codecue.binding import experiment_log_scheduler as scheduler_module
        tick=scheduler_module.tick(root,force=True)
        health=tick.get('scheduler') or scheduler_module.ensure_enabled(root,force=True)
        state=json.loads((root/'artifacts/binding/experiment_log/scheduler_state.json').read_text())
        now=datetime.now(timezone.utc);last=state.get('last_success_utc');age=None
        if isinstance(last,str):
            try:age=(now-datetime.fromisoformat(last.replace('Z','+00:00'))).total_seconds()
            except (ValueError,TypeError):pass
        interval=state.get('interval_minutes',10)
        value=dict(recorded_utc=now.isoformat(),tick_status=tick.get('status'),tick_error=tick.get('error'),enabled=health.get('enabled') is True,guard_health=health.get('healthy') is True,pending_guards=health.get('pending_guards'),last_success_utc=last,last_success_age_seconds=age,interval_minutes=interval,fresh_within_two_intervals=age is not None and 0<=age<=2*interval*60)
    value=dict(value,status='passed' if value.get('enabled') and value.get('guard_health') and value.get('fresh_within_two_intervals') else 'needs_attention')
    publish(path,json_bytes(value));return value


def refresh_readiness(root,data,callback=None):
    folder=root/SUITE;out=folder/'readiness_at_completion_v1.json';csv=folder/'readiness_at_completion_v1.csv';report=root/'reports/binding/old_value_overnight_readiness_v1.md';marker=folder/'readiness_completion_review_v1.json'
    if marker.exists():
        value=read(root,marker)
        for item in value['pins']:verify_pin(root,item)
        return value
    cfg=read(root,data['pipeline']['readiness_config']['path'],data['pipeline']['readiness_config'])
    cfg.update(root=str(root),output=str(out),csv=str(csv),report=str(report))
    if callback is None:
        from codecue.binding import preparation
        result=preparation.run(cfg)
    else:result=callback(cfg)
    require(result['counts']==dict(ready=62,needs_scientific_decision=9,deferred_optional=3),'All completed tasks must produce62/9/3 readiness')
    shared=root/'reports/binding/preparation_readiness.md';refreshed=False
    if shared.exists() and sha(shared)==data['pipeline']['queued_readiness_report_sha256']:
        publish(shared,report.read_bytes(),immutable=False);refreshed=True
    value=dict(status='passed',counts=result['counts'],tracked_tasks=74,shared_inventory_refreshed=refreshed,pins=[pin(root,p) for p in (out,csv,report)])
    publish(marker,json_bytes(value));return value


def publication(root,observed=None,logging_value=None,readiness_callback=None):
    root=Path(root).resolve();INPUTS.clear();data=setup(root);observed=scheduler(data['jobs']) if observed is None else observed
    stages={name:dict(job_id=data['jobs'].get(name),**observed.get(data['jobs'].get(name),{})) for name in WORK}
    issues=[name+': '+str(item.get('state','not submitted/unknown'))+' '+str(item.get('exit_code','')) for name,item in stages.items() if item.get('state')!='COMPLETED' or item.get('exit_code') not in ('0','0:0')]
    if data['qa'] is None:issues.append('Complete software validation proof is missing')
    models={}
    for name,cfg in sorted(data['configs'].items()):
        if not (resolve(root,cfg['run_dir'])/'routing_completion_v1.json').exists():issues.append(name+': model completion receipt is missing');continue
        try:models[name]=model_metadata(root,name,cfg,data)
        except (OSError,ValueError,KeyError,TypeError) as exc:issues.append(name+': '+str(exc))
    if issues:return incomplete(root,data,stages,issues)
    comparison=dict(status='complete_audited',evaluation_role=PUB_ROLE,source=data['pointer'],stages=stages,models=models,
        total_scored_responses=40320,source_questions=6720,instructions=list(VARIANTS),gate_cells_per_model=24,
        scientific_status='calibration_passed' if all(m['review']['reliability_gate']['status']=='passed' for m in models.values()) else 'gate_failed',
        source_records_opened=False,prepared_records_opened=False,response_records_opened=False,arrays_opened=False,new_model_queries=0,new_fits=0,causal_qualification=False,
        input_pins=sorted(INPUTS.values(),key=lambda p:p['path']))
    outputs={root/SUITE/'comparison_v1.json':json_bytes(comparison),root/'reports/binding/old_value_overnight_findings_v1.md':report_bytes(models,data['pointer'])}
    complete=root/SUITE/'completion_review_v1.json'
    if complete.exists():
        previous=read(root,complete)
        for item in previous['output_pins']+previous['readiness']['pins']:verify_pin(root,item)
        require(previous['source']==data['pointer'] and previous['scientific_status']==comparison['scientific_status'],'Existing completion identity differs')
        for path,payload in outputs.items():require(path.read_bytes()==payload,'Byte-identical publication reproduction failed')
        return dict(status='byte_identical_reproduction',scientific_status=comparison['scientific_status'],models=2)
    for path,payload in outputs.items():publish(path,payload)
    logging=logging_snapshot(root,logging_value);ready=refresh_readiness(root,data,readiness_callback)
    script=root/SUITE/'publish_overnight_v1.py'
    review=dict(status='complete_audited',evaluation_role=PUB_ROLE,source=data['pointer'],scientific_status=comparison['scientific_status'],stages=stages,
        total_scored_responses=40320,model_gate_status={name:m['review']['reliability_gate']['status'] for name,m in models.items()},
        byte_identical_publication_required=True,all_actual_backend_audits_verified=True,source_records_opened=False,prepared_records_opened=False,response_records_opened=False,arrays_opened=False,
        new_model_queries=0,new_fits=0,causal_qualification=False,logging=logging,readiness=ready,publisher_sha256=sha(script),
        input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),output_pins=[pin(root,path) for path in outputs]+[pin(root,root/SUITE/'completion_logging_review_v1.json'),pin(root,root/SUITE/'readiness_completion_review_v1.json')])
    publish(complete,json_bytes(review));return dict(status='published',scientific_status=comparison['scientific_status'],models=2,readiness=ready['counts'])


def _fixture_point(n,correct,split):
    count=45 if split=='train' else 15;groups={}
    for index in range(count):
        amount=n//count+(index<n%count)
        if amount:groups[f'{split}-g{index}']=dict(n=amount,correct=amount if correct else 0,accuracy=1. if correct else 0.)
    return dict(n=n,correct=n if correct else 0,invalid=0,valid=n,accuracy=1. if correct else 0.,invalid_rate=0.,unique_prompt_n=n,unique_source_n=n,unique_body_target_n=n,graph_groups=len(groups),group_macro_accuracy=1. if correct else 0.,per_graph=groups)


def _fixture_review(cfg,source,fail):
    counts={('train','absent_all_current'):1248,('train','retained_other_current'):576,('train','equal_current'):696,('development','absent_all_current'):360,('development','retained_other_current'):240,('development','equal_current'):240}
    gates=[];controls=[]
    for variant in sorted(VARIANTS):
        for mode in MODES:
            for storage in (*STORAGE,'equal_current'):
                for split in sorted(SPLITS):
                    correct=not(fail and variant==VARIANTS[0] and mode=='previous' and storage in STORAGE)
                    cell=dict(variant=variant,query_mode=mode,old_storage=storage,split=split,**_fixture_point(counts[split,storage],correct,split))
                    if storage in STORAGE:cell['passed']=correct;gates.append(cell)
                    else:controls.append(cell)
    instructions={}
    for variant in VARIANTS:
        cells=[c for c in gates if c['variant']==variant];train=all(c['passed'] for c in cells if c['split']=='train');dev=all(c['passed'] for c in cells if c['split']=='development')
        instructions[variant]=dict(status='passed' if train and dev else 'failed',training_qualified=train,development_descriptive_passed=dev,numeric_development_qualified=train and dev,behavioral_calibration_qualified=train and dev,cells=cells)
    groups={}
    for cell in gates+controls:
        for name,item in cell['per_graph'].items():
            entry=groups.setdefault(name,dict(n=0,correct=0));entry['n']+=item['n'];entry['correct']+=item['correct']
    for item in groups.values():item['accuracy']=item['correct']/item['n']
    correct=sum(c['correct'] for c in gates+controls)
    review=dict(status='complete_audited',complete=True,evaluation_role=ROLE,config_hash=digest(cfg),source=source,model=cfg['model'],model_revision=cfg['model_revision'],
        n=20160,correct=correct,invalid=0,valid=20160,accuracy=correct/20160,invalid_rate=0.,graph_groups=60,per_graph=groups,group_macro_accuracy=sum(v['accuracy'] for v in groups.values())/60,
        scored_unique_cases=20160,generated_responses=20160,unique_sources=6720,source_body_target_pairs=3360,instructions=list(VARIANTS),new_fits=0,generated_holdouts_opened=False,new_intervals=False,
        gate_cells=gates,equality_control_cells=controls,reliability_gate=dict(thresholds=THRESHOLDS,instructions=instructions,status='failed' if fail else 'passed',automatic_causal_launch=False,causal_design_review_required=True),
        dataset_sha256=cfg['dataset_sha256'],dataset_manifest_sha256=cfg['dataset_manifest_sha256'],declared_plan_sha256=cfg['declared_plan_sha256'])
    axes=dict(target_slot=('0','1','2','3'),target_update_count=('1','2','3'),last_write_lag=('0','1','2','3'),lexical_realization=('0','1'),profile_id=('2_1_1_0','3_1_0_0','2_2_0_0'),numeric_seed=('1151','1297','1459'))
    review['descriptive_cells']=[]
    for cell in gates+controls:
        for axis,values in axes.items():
            for value in values:
                review['descriptive_cells'].append(dict({k:cell[k] for k in ('variant','query_mode','old_storage','split')},axis=axis,value=value,**_fixture_point(cell['n']//len(values),cell['correct']>0,cell['split'])))
    pairs=[]
    for variant in VARIANTS:
        for split in SPLITS:
            for storage in (*STORAGE,'equal_current'):
                n=counts[split,storage];bad=fail and variant==VARIANTS[0] and storage in STORAGE
                graph=_fixture_point(n,not bad,split)['per_graph'];delta=-1. if bad else 0.
                pairs.append(dict(variant=variant,split=split,old_storage=storage,paired_n=n,previous_minus_current=delta,group_macro_previous_minus_current=delta,graph_groups=len(graph),per_graph={k:dict(n=v['n'],previous_minus_current=delta) for k,v in graph.items()},confidence_interval=None,
                    paired_outcomes=dict(both_correct=0 if bad else n,previous_only_correct=0,current_only_correct=n if bad else 0,neither_correct=0,previous_answered_current=n if bad else 0,current_answered_previous=0,invalid_previous=0,invalid_current=0)))
    review['paired_contrasts']=pairs;return review


def _fixture(root):
    out=root/SUITE;out.mkdir(parents=True);folder=root/'artifacts/binding/sources'/('f'*24);folder.mkdir(parents=True)
    def write(path,value):
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(json_bytes(value) if isinstance(value,dict) else value);return p
    write(Path('src/fake.py'),b'pass\n');source_files={'src/fake.py':sha(root/'src/fake.py')};code=digest(source_files)
    write(SUITE/'publish_overnight_v1.py',Path(__file__).read_bytes())
    write(SUITE/'sources.jsonl',b'');dataset_sha=sha(out/'sources.jsonl')
    dataset_manifest=dict(status='complete',evaluation_role='discovery_old_value_sources_v1',sha256=dataset_sha,rows=6720,independent_python_passed=True,generated_holdouts_opened=False)
    write(SUITE/'sources.manifest.json',dataset_manifest)
    plan=write(Path('reports/binding/old_value_overnight_plan_v1.md'),b'Synthetic prospective plan\n')
    configs={};config_pins=[]
    for model,name in MODELS.items():
        run=SUITE/name
        cfg=dict(evaluation_role=ROLE,model=model,model_revision='r'*40,dataset=str(SUITE/'sources.jsonl'),dataset_sha256=dataset_sha,dataset_manifest_sha256=sha(out/'sources.manifest.json'),
            declared_plan=str(plan.relative_to(root)),declared_plan_sha256=sha(plan),run_dir=str(run),review_artifact=str(run/'review_v1.json'),report=f'reports/binding/old_value_{name}_v1.md',prepared_cases=str(run/'prepared_cases.jsonl'),preflight_result=str(run/'tokenizer_preflight.json'))
        p=write(Path('configs/binding/old_value_overnight_20261028_v1')/(name+'.json'),cfg);configs[name]=cfg;config_pins.append(dict(path=str(p.relative_to(root)),sha256=sha(p)))
    checker=dict(evaluation_role='discovery_old_value_overnight_check_v1',suite_root=str(SUITE),model_configs=config_pins)
    write(CHECK_CONFIG,checker);readiness_path=Path('configs/binding/preparation/readiness_v24.json');write(readiness_path,dict(items=[]))
    files=[CHECK_CONFIG,readiness_path,*[Path(p['path']) for p in config_pins]]
    config_files={str(p):sha(root/p) for p in files}
    for p in files:write(folder.relative_to(root)/p,(root/p).read_bytes())
    write(folder.relative_to(root)/'src/fake.py',b'pass\n')
    manifest=dict(snapshot_id='f'*24,code=dict(source_sha256=code,source_files=source_files),config_files=config_files,workspace_root=str(root))
    frozen=write(folder.relative_to(root)/'frozen_manifest.json',manifest)
    pointer=dict(snapshot=str(folder.relative_to(root)),snapshot_id='f'*24,code=code);write(SUITE/'execution_source_v1.json',pointer)
    source=dict(snapshot=str(folder.relative_to(root)),snapshot_id='f'*24,source_sha256=code,frozen_manifest_sha256=sha(frozen))
    queued=write(Path('reports/binding/preparation_readiness.md'),b'Synthetic queued inventory\n')
    pipeline=dict(source=pointer,helper_pins=[pin(root,out/'publish_overnight_v1.py')],readiness_config=pin(root,readiness_path),queued_readiness_report_sha256=sha(queued));write(SUITE/'completion_pipeline_v1.json',pipeline)
    jobs={name:str(1000+i) for i,name in enumerate(WORK)};write(SUITE/'jobs_v1.json',jobs)
    junit=write(SUITE/'regression_v1.xml',b'<testsuites><testsuite tests="1" failures="0" errors="0" skipped="0" /></testsuites>')
    write(SUITE/'software_validation_review_v1.json',dict(status='passed',source=pointer,counts=dict(tests=1,failures=0,errors=0,skipped=0),junit_sha256=sha(junit)))
    for name,cfg in configs.items():
        run=Path(cfg['run_dir']);stage=run/'checkpoint_suite';write(Path(cfg['prepared_cases']),b'');write(stage/'responses.jsonl',b'')
        native=dict(status='passed',config_hash=digest(cfg),source_sha256=code,cases=20160,model_inference=False,generated_holdouts_opened=False,prepared_cases_sha256=sha(root/cfg['prepared_cases']));write(Path(cfg['preflight_result']),native)
        prep=dict(status='passed',evaluation_role=ROLE,config_hash=digest(cfg),source=source,artifacts={k:pin(root,cfg[k]) for k in ('prepared_cases','preflight_result')});write(run/'routing_preflight_v1.json',prep)
        identity=dict(config=cfg,code=dict(source_sha256=code));backend=dict(status='complete',identity=identity,identity_hash=digest(identity),evaluated=20160,planned=20160,responses_sha256=sha(root/stage/'responses.jsonl'));write(stage/'manifest.json',backend)
        summary=dict(complete=True,evaluated=20160,planned=20160,cells=[],interpretation='Synthetic metadata fixture',generated_holdouts_opened=False,responses_sha256=sha(root/stage/'responses.jsonl'),timings=[dict(cases=20160,generation_seconds=120.,output_tokens=20160)],gpu=dict(samples=1,peak_memory_used_MiB=1024));write(stage/'summary.json',summary)
        runtime=dict(device_name='Synthetic device',load_warmup_seconds=1.,engine={},preflight=native,versions={});write(stage/'runtime.json',runtime)
        audit=dict(status='passed',identity_hash=backend['identity_hash'],preflight=native,runtime=runtime,**summary);write(stage/'audit.json',audit)
        attempts=dict(config_hash=digest(cfg),source=source,attempts=[dict(status='complete',saved_response_prefix=0,pending_scored_cases=20160,warmup_request_ceiling=8,confirmed_warmup_requests=8,slurm_job_id=jobs[name+'_behavior'])]);write(run/'routing_attempts_v1.json',attempts)
        review=_fixture_review(cfg,source,fail=name=='llama8b');review.update(accounting=dict(scored_responses=20160,confirmed_warmup_requests=8,uncertain_failed_invocation_warmup_ceiling=0,failed_backend_invocations=0,scored_model_queries_exact=20160,scored_model_queries_lower_bound=20160,scored_model_queries_upper_bound=20160),new_model_queries=20168,new_model_queries_lower_bound=20168,new_model_queries_upper_bound=20168,
            artifacts={k:pin(root,path) for k,path in dict(backend_audit=stage/'audit.json',responses=stage/'responses.jsonl',backend_manifest=stage/'manifest.json',preparation=run/'routing_preflight_v1.json',attempts=run/'routing_attempts_v1.json').items()})
        write(Path(cfg['report']),b'Synthetic model report\n');write(Path(cfg['review_artifact']),review)
        receipt=dict(status='complete_audited',evaluation_role=ROLE,config_hash=digest(cfg),source=source,scored_cases=20160,new_fits=0,generated_holdouts_opened=False,new_model_queries=20168,new_model_queries_lower_bound=20168,new_model_queries_upper_bound=20168,artifacts={k:pin(root,cfg[k]) for k in ('report','review_artifact')})
        receipt['artifacts']['review']=receipt['artifacts'].pop('review_artifact');write(run/'routing_completion_v1.json',receipt)
    return dict(configs=configs,jobs=jobs,observed={job:dict(state='COMPLETED',exit_code='0:0') for job in jobs.values()},source=source)


def self_test():
    checks=0
    with tempfile.TemporaryDirectory(prefix='old_value_publication_') as tmp:
        root=Path(tmp);fixture=_fixture(root);data=setup(root);checks+=1
        logging=dict(recorded_utc='2026-10-29T00:00:00+00:00',enabled=True,guard_health=True,pending_guards=2,last_success_utc='2026-10-29T00:00:00+00:00',last_success_age_seconds=0.,interval_minutes=10,fresh_within_two_intervals=True)
        def ready(cfg):
            value=dict(status='inventory_complete',counts=dict(ready=62,needs_scientific_decision=9,deferred_optional=3))
            publish(cfg['output'],json_bytes(value));publish(cfg['csv'],b'id,status\nfixture,ready\n');publish(cfg['report'],b'Synthetic completed inventory\n');return value
        observed=deepcopy(fixture['observed']);observed[fixture['jobs']['llama8b_behavior']]['state']='FAILED'
        incomplete_result=publication(root,observed,logging,ready);require(incomplete_result['status']=='incomplete_action_required' and not (root/SUITE/'comparison_v1.json').exists(),'Failed execution must not fabricate completion');checks+=1
        model=model_metadata(root,'llama8b',fixture['configs']['llama8b'],data)
        require(model['review']['reliability_gate']['status']=='failed','Failed behavioral gate must remain explicit');checks+=1
        for mutate in [lambda d:d['gate_cells'].pop(),lambda d:d['instructions'].pop(),lambda d:d['reliability_gate'].update(status='passed'),lambda d:d['paired_contrasts'][0]['paired_outcomes'].update(both_correct=999999),lambda d:d['descriptive_cells'].pop()]:
            bad=deepcopy(model['review']);mutate(bad)
            try:validate_review(bad,fixture['configs']['llama8b'],data['pointer'],data['manifest_sha'])
            except (ValueError,KeyError):checks+=1
            else:raise AssertionError('Malformed synthetic review accepted')
        first=publication(root,fixture['observed'],logging,ready);second=publication(root,fixture['observed'],logging,ready)
        require(first['status']=='published' and second['status']=='byte_identical_reproduction','Complete publication must reproduce identical bytes');checks+=1
        comparison=json.loads((root/SUITE/'comparison_v1.json').read_text());require(comparison['scientific_status']=='gate_failed' and comparison['status']=='complete_audited' and comparison['causal_qualification'] is False,'Execution success must stay distinct from gate failure');checks+=1
        complete=json.loads((root/SUITE/'completion_review_v1.json').read_text());require(complete['readiness']['counts']['ready']==62 and complete['logging']['fresh_within_two_intervals'],'Readiness and freshness snapshots required');checks+=1
        require((root/'reports/binding/preparation_readiness.md').read_bytes()==b'Synthetic completed inventory\n','Shared inventory predecessor hash guard failed');checks+=1
        require(not list(root.rglob('*.npz')) and all(p.stat().st_size==0 for p in root.rglob('*.jsonl')),'Self-test must contain no source/prepared/response records or arrays');checks+=1
        # A committed prefix can cover the cohort before finalization; a retry
        # may therefore finish with no generation timing blocks of its own.
        metadata=deepcopy(model);metadata['throughput'].update(timed_cases=0,generation_seconds=0.,requests_per_generation_second=None,output_tokens=0,output_tokens_per_generation_second=None)
        require(b'Unavailable' in report_bytes({'llama8b':metadata},data['pointer']),'Missing retry timing must remain unavailable');checks+=1
    return dict(status='passed',synthetic_checks=checks,actual_scientific_outcomes_opened=False,source_or_response_records_opened=False,arrays_opened=False,model_loaded=False,jobs_submitted=False)


def workspace():return Path(__file__).resolve().parents[4]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');parser.add_argument('--check-setup',action='store_true');args=parser.parse_args()
    if args.self_test:result=self_test()
    else:
        root=workspace();pointer=json.loads((root/SUITE/'execution_source_v1.json').read_text());sys.path.insert(0,str(resolve(root,pointer['snapshot'])/'src'))
        if args.check_setup:
            data=setup(root);result=dict(status='passed_setup',source=data['pointer']['snapshot_id'],models=len(data['configs']),scientific_outcomes_opened=False)
        else:result=publication(root)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
