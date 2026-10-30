"""Publish and certify the finite saved-score grammar review without loading arrays."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
source=json.loads((FOLDER/'execution_source_v1.json').read_text())
snapshot=Path(source['snapshot'])
sys.path.insert(0,str(snapshot/'src'))
from codecue.binding import grammar_identity_review as review
from codecue.binding import preparation,relationship_capture as bounded,snapshots
from codecue.binding import experiment_log_scheduler as scheduler

def read(path):return json.loads(Path(path).read_text())
def pin(path):
    path=Path(path)
    if not path.is_absolute():path=ROOT/path
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=bounded._sha(path))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-setup',action='store_true');args=parser.parse_args()
    frozen=snapshots.verify(snapshot)
    assert frozen['snapshot_id']==source['snapshot_id'] and frozen['code']['source_sha256']==source['code']
    pipeline=read(FOLDER/'completion_pipeline_v1.json');assert pipeline['source']==source
    for item in pipeline['helper_pins']+[pipeline['readiness_config']]:assert pin(item['path'])==item
    build=read(FOLDER/'build_review_v1.json')
    if args.check_setup:
        print(json.dumps(dict(status='passed_setup',source=source['snapshot_id'],helpers=len(pipeline['helper_pins']),expected_tests=build['expected_regression_tests'],scientific_outcomes_opened=False),sort_keys=True));return
    assert os.environ.get('SLURM_JOB_ID'),'CPU allocation required'
    if (FOLDER/'handoff_review_v1.json').exists():
        old=read(FOLDER/'handoff_review_v1.json')
        for item in old['pins']:assert pin(item['path'])==item
        print(json.dumps(dict(status='verified_existing_handoff',pins=len(old['pins'])),sort_keys=True));return
    qa=read(FOLDER/'software_validation_review_v1.json')
    assert qa['status']=='passed' and qa['source']==source
    assert qa['test_source_sha256']==build['test_source_sha256']
    assert qa['counts']==dict(tests=build['expected_regression_tests'],failures=0,errors=0,skipped=0)
    jobs=read(FOLDER/'jobs_v1.json')
    raw=subprocess.run(['sacct','-n','-X','-P','-j',','.join(jobs.values()),'--format=JobIDRaw,State,ExitCode'],capture_output=True,text=True,check=True).stdout
    states={a[0]:a[1:3] for line in raw.splitlines() if (a:=line.split('|')) and a[0]}
    assert all(states[jid]==['COMPLETED','0:0'] for jid in jobs.values()),states
    config=read(snapshot/'configs/binding/identity_grammar_review_v1.json')
    result=review.completed_result(config)
    assert result['source']['snapshot_id']==source['snapshot_id'] and result['source']['source_sha256']==source['code']
    assert result['score_banks']==60 and result['saved_score_rows_checked']==345600 and result['development_prediction_rows']==86400
    assert result['original_metrics_exact'] and all(result[k]==0 for k in ('new_fits','new_model_queries','parameters_reapplied'))
    out=ROOT/config['run_dir'];proof=read(out/'grammar_replay_review_v1.json')
    assert proof['status']=='passed' and proof['source']==result['source']
    assert proof['original_score_banks_reopened'] is False
    assert proof['all_grammar_diagnostics_recomputed'] and proof['all_original_metrics_recomputed']
    assert all(proof[k] is False for k in ('activation_arrays_opened','coefficient_arrays_opened','generated_holdouts_opened'))
    assert all(proof[k]==0 for k in ('new_fits','new_model_queries','parameters_reapplied'))
    env=dict(os.environ,PYTHONPATH=str(snapshot/'src'),OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    for _ in range(2):subprocess.run([sys.executable,str(FOLDER/'publish_grammar_v1.py')],cwd=ROOT,env=env,check=True)
    publication=read(FOLDER/'publication_review_v1.json');assert publication['status']=='passed'
    cfg=read(ROOT/pipeline['readiness_config']['path'])
    cfg.update(output=str(FOLDER/'readiness_at_completion_v1.json'),csv=str(FOLDER/'readiness_at_completion_v1.csv'),report=str(ROOT/'reports/binding/identity_grammar_readiness_v1.md'))
    ready=preparation.run(cfg)
    assert ready['counts']==dict(ready=59,needs_scientific_decision=9,deferred_optional=3),ready['counts']
    current=ROOT/'reports/binding/preparation_readiness.md';shared=False
    if current.is_file() and bounded._sha(current)==pipeline['queued_readiness_report_sha256']:
        current.write_bytes(Path(cfg['report']).read_bytes());shared=True
    logging=scheduler.ensure_enabled(ROOT,force=True)
    assert logging['enabled'] and logging['healthy'] and logging['pending_guards']>=2
    logging_path=FOLDER/'completion_logging_review_v1.json'
    if not logging_path.exists():bounded._put(logging_path,dict(status='passed',enabled=True,healthy=True,interval_minutes=logging['interval_minutes'],pending_guards=logging['pending_guards'],new_fits=0,new_model_queries=0))
    else:assert read(logging_path)['status']=='passed'
    paths=[FOLDER/n for n in ('execution_source_v1.json','build_review_v1.json','target_preflight_review_v1.json','software_validation_review_v1.json','regression_v1.xml','regression_sources_v1.zip','regression_archive_review_v1.json','jobs_v1.json','completion_pipeline_v1.json','closure_job_v1.json','publication_review_v1.json','comparison_v1.json','form_cells_v1.csv','completion_logging_review_v1.json','readiness_at_completion_v1.json','readiness_at_completion_v1.csv','prepare_submission_v1.py','queue_completion_v1.py','independent_build_review_v1.json','publisher_build_review_v1.json','run_validation_v1.py','run_analysis_v1.py','publish_grammar_v1.py','finish_review_v1.py')]
    paths += [out/n for n in ('registration.json','results_v1.json','summary.json','audit.json','completion_manifest_v1.json','grammar_replay_review_v1.json')]
    paths += [snapshot/'frozen_manifest.json',ROOT/pipeline['readiness_config']['path'],ROOT/'configs/binding/identity_grammar_review_v1.json',ROOT/config['declared_plan'],ROOT/config['report'],ROOT/'reports/binding/identity_grammar_readiness_v1.md',ROOT/'reports/binding/identity_grammar_decision_v1.md',ROOT/'reports/binding/identity_grammar_summary_v1.md',ROOT/'reports/binding/figures/identity_grammar_v1.png',ROOT/'reports/binding/figures/identity_grammar_v1.svg',ROOT/'artifacts/binding/direct_identity/20261028_v1/handoff_review_v1.json']
    receipt=read(out/'completion_manifest_v1.json')
    paths += [Path(p['path']) if Path(p['path']).is_absolute() else ROOT/p['path'] for p in receipt['artifacts'].values()]
    handoff=dict(status='complete_audited',evaluation_role='discovery_identity_grammar_completed_handoff_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,original_fit_source_snapshot='3e5471ac9dc9b948761fc429',original_capture_source_snapshot='345f75b01f5c3b33bd0ca6d8',software_validation=qa['counts'],score_banks=60,saved_score_rows_checked=345600,development_prediction_rows=86400,all_diagnostics_recomputed=True,original_score_banks_reopened_in_audit=False,byte_identical_publication=True,tracked_tasks=71,readiness_counts=ready['counts'],shared_inventory_refreshed=shared,new_model_queries=0,new_fits=0,parameters_reapplied=0,generated_holdouts_opened=False,completion_worker_array_loading=False,publication_worker_job_id=os.environ['SLURM_JOB_ID'],limitation='Adaptive decoder-assisted reconstruction using external copy/version rules. Owner-only scores can acquire versions through counting; whole8joint monotonicity follows by construction. No maintained-state, natural-decoder, causal-use or unfamiliar-program qualification.',pins=[pin(p) for p in sorted(set(paths))])
    bounded._put(FOLDER/'handoff_review_v1.json',handoff)
    for item in handoff['pins']:assert pin(item['path'])==item
    print(json.dumps(dict(status='complete_audited',pins_verified=len(handoff['pins']),readiness=ready['counts']),sort_keys=True))

if __name__=='__main__':main()
