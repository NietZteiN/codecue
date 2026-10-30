"""Verify metadata publication and log the completed source-assisted score review."""
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
from codecue.binding import diversity_identity_review as review
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
    assert qa['counts']==dict(tests=build['expected_regression_tests'],failures=0,errors=0,skipped=0)
    jobs=read(FOLDER/'jobs_v1.json')
    raw=subprocess.run(['sacct','-n','-X','-P','-j',','.join(jobs.values()),'--format=JobIDRaw,State,ExitCode'],capture_output=True,text=True,check=True).stdout
    states={a[0]:a[1:3] for line in raw.splitlines() if (a:=line.split('|')) and a[0]}
    assert all(states[jid]==['COMPLETED','0:0'] for jid in jobs.values()),states
    config=read(snapshot/'configs/binding/diversity_identity_review_v1.json')
    result=review.completed_result(config)
    assert result['source']==review._source(config,scheduled=False) and result['original_metrics_exact']
    assert result['source']['snapshot_id']==source['snapshot_id']
    assert result['source']['source_sha256']==source['code']
    assert result['source']['frozen_manifest_sha256']==bounded._sha(snapshot/'frozen_manifest.json')
    assert result['score_banks']==90 and result['saved_score_rows_checked']==518400 and result['development_prediction_rows']==129600
    assert all(result[k]==0 for k in ('new_fits','new_model_queries','parameters_reapplied'))
    proof=read(ROOT/config['run_dir']/'prediction_replay_review_v1.json')
    assert proof['status']=='passed' and proof['source']==result['source'] and proof['score_banks']==90 and proof['prediction_rows']==129600
    assert proof['all_oracle_assisted_diagnostics_recomputed'] and proof['sham_original_task_kept_separate']
    assert proof['original_score_banks_reopened'] is False
    assert all(proof[k] is False for k in ('activation_arrays_opened','coefficient_arrays_opened','generated_holdouts_opened'))
    assert all(proof[k]==0 for k in ('new_fits','new_model_queries','parameters_reapplied'))
    report=ROOT/config['report'];first=review._report(result).encode();second=review._report(result).encode()
    assert first==second==report.read_bytes()
    assert review._same(read(ROOT/config['run_dir']/'summary.json'),review._summary(result))
    reproduction=dict(status='passed',evaluation_role='discovery_diversity_identity_metadata_publication_v1',report_sha256=bounded._sha(report),byte_identical_reproduction=True,source_oracle_assisted=True,array_loading=False,new_fits=0,new_model_queries=0,parameters_reapplied=0)
    bounded._put(FOLDER/'publication_review_v1.json',reproduction)
    cfg=read(ROOT/pipeline['readiness_config']['path'])
    cfg.update(output=str(FOLDER/'readiness_at_completion_v1.json'),csv=str(FOLDER/'readiness_at_completion_v1.csv'),report=str(ROOT/'reports/binding/diversity_identity_review_readiness_v1.md'))
    ready=preparation.run(cfg)
    assert ready['counts']==dict(ready=57,needs_scientific_decision=9,deferred_optional=3),ready['counts']
    current=ROOT/'reports/binding/preparation_readiness.md'
    shared=False
    if current.is_file() and bounded._sha(current) in pipeline['shared_inventory_predecessor_sha256']:
        current.write_bytes(Path(cfg['report']).read_bytes());shared=True
    logging=scheduler.ensure_enabled(ROOT,force=True)
    assert logging['enabled'] and logging['healthy'] and logging['pending_guards']>=2
    logging_path=FOLDER/'completion_logging_review_v1.json'
    if not logging_path.exists():
        bounded._put(logging_path,dict(status='passed',enabled=True,healthy=True,interval_minutes=logging['interval_minutes'],pending_guards=logging['pending_guards'],new_fits=0,new_model_queries=0))
    else:
        previous_logging=read(logging_path)
        assert previous_logging['status']=='passed' and previous_logging['enabled'] and previous_logging['healthy']
    paths=[FOLDER/name for name in ('execution_source_v1.json','build_review_v1.json','identity_source_preflight_review_v1.json','software_validation_review_v1.json','regression_v1.xml','regression_sources_v1.zip','regression_archive_review_v1.json','jobs_v1.json','completion_pipeline_v1.json','closure_job_v1.json','publication_review_v1.json','completion_logging_review_v1.json','readiness_at_completion_v1.json','readiness_at_completion_v1.csv','run_validation_v1.py','run_source_preflight_v1.py','run_analysis_v1.py','finish_review_v1.py')]
    out=ROOT/config['run_dir']
    paths += [out/name for name in ('registration.json','results_v1.json','summary.json','audit.json','completion_manifest_v1.json','prediction_replay_review_v1.json')]
    paths += [snapshot/'frozen_manifest.json',ROOT/pipeline['readiness_config']['path'],ROOT/'configs/binding/diversity_identity_review_v1.json',ROOT/config['declared_plan'],report,ROOT/'reports/binding/diversity_identity_review_readiness_v1.md',ROOT/'artifacts/binding/diversity_decoding/20261028_v1/handoff_review_v1.json']
    receipt=read(out/'completion_manifest_v1.json')
    # Stream hashes bind saved prediction binaries without loading their arrays.
    paths += [Path(item['path']) if Path(item['path']).is_absolute() else ROOT/item['path'] for item in receipt['artifacts'].values()]
    handoff=dict(status='complete_audited',evaluation_role='discovery_diversity_identity_completed_handoff_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,original_capture_source_snapshot='345f75b01f5c3b33bd0ca6d8',software_validation=qa['counts'],score_banks=90,saved_score_rows_checked=518400,development_prediction_rows=129600,source_oracle_assisted=True,all_diagnostics_recomputed=True,sham_original_task_kept_separate=True,byte_identical_report_reproduction=True,tracked_tasks=69,readiness_counts=ready['counts'],shared_inventory_refreshed=shared,new_model_queries=0,new_fits=0,parameters_reapplied=0,generated_holdouts_opened=False,completion_worker_array_loading=False,publication_worker_job_id=os.environ['SLURM_JOB_ID'],limitation='Adaptive source-oracle-assisted error taxonomy over existing discovery scores; no independent learned full binding identity, causal mechanism, new behavioral qualification or untouched prediction.',pins=[pin(p) for p in sorted(set(paths))])
    bounded._put(FOLDER/'handoff_review_v1.json',handoff)
    for item in handoff['pins']:assert pin(item['path'])==item
    print(json.dumps(dict(status='complete_audited',pins_verified=len(handoff['pins']),readiness=ready['counts']),sort_keys=True))


if __name__=='__main__':main()
