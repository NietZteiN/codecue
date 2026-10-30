"""Publish and verify the completed direct joint-identity CPU study."""
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
from codecue.binding import direct_identity_readouts as readouts
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
    assert bounded._sha(ROOT/build['linearity_note']['path'])==build['linearity_note']['sha256']
    if args.check_setup:
        print(json.dumps(dict(status='passed_setup',source=source['snapshot_id'],helpers=len(pipeline['helper_pins']),expected_tests=build['expected_regression_tests'],scientific_outcomes_opened=False),sort_keys=True));return
    assert os.environ.get('SLURM_JOB_ID'),'CPU allocation required'
    if (FOLDER/'handoff_review_v1.json').exists():
        previous=read(FOLDER/'handoff_review_v1.json')
        for item in previous['pins']:assert pin(item['path'])==item
        print(json.dumps(dict(status='verified_existing_handoff',pins=len(previous['pins'])),sort_keys=True));return
    qa=read(FOLDER/'software_validation_review_v1.json')
    assert qa['status']=='passed' and qa['source']==source
    assert qa['counts']==dict(tests=build['expected_regression_tests'],failures=0,errors=0,skipped=0)
    jobs=read(FOLDER/'jobs_v1.json')
    raw=subprocess.run(['sacct','-n','-X','-P','-j',','.join(jobs.values()),'--format=JobIDRaw,State,ExitCode'],capture_output=True,text=True,check=True).stdout
    states={a[0]:a[1:3] for line in raw.splitlines() if (a:=line.split('|')) and a[0]}
    assert all(states[jid]==['COMPLETED','0:0'] for jid in jobs.values()),states
    models={};paths=[]
    for name in ('llama8b','codellama34b'):
        cfg=read(snapshot/'configs/binding/direct_identity_20261028_v1'/f'{name}_readouts.json')
        result=readouts.completed_result(cfg)
        assert result['fit_source']['snapshot_id']==source['snapshot_id'] and result['fit_source']['source_sha256']==source['code']
        assert result['capture_source']['snapshot_id']=='345f75b01f5c3b33bd0ca6d8'
        assert result['capture_source']['source_sha256']=='9cfa6c42fd79ddb9a4f049650ba311bb996dcb9f48afb9f9c31a2cc22254a918'
        assert result['cases']==5760 and len(result['target_columns'])==192
        assert result['fit_banks']==result['factorizations']==30 and result['parameter_replay_rows']==172800
        assert len(result['fits'])==30 and {fit['site'] for fit in result['fits']}=={7,8}
        assert all(set(fit['metrics'])==set(readouts.METHODS) for fit in result['fits'])
        out=ROOT/cfg['run_dir'];proof=read(out/'parameter_replay_review_v1.json')
        assert proof['status']=='passed' and proof['evaluation_role']==readouts.ROLE
        assert proof['fit_source']==result['fit_source'] and proof['capture_source']==result['capture_source']
        assert proof['fit_banks']==proof['factorizations']==30 and proof['parameter_replay_rows']==172800
        assert all(proof[k] is True for k in ('exact_saved_parameter_score_replays','all_real_and_control_scores_replayed','all_scientific_metrics_recomputed','train_support_and_control_marginals_recomputed'))
        assert proof['new_fits']==proof['new_model_queries']==0 and proof['generated_holdouts_opened'] is False
        receipt=read(out/'completion_manifest_v1.json');assert proof['source_artifacts']==receipt['artifacts']
        for item in receipt['artifacts'].values():
            p=Path(item['path']);p=p if p.is_absolute() else ROOT/p
            assert p.stat().st_size==item['bytes'] and bounded._sha(p)==item['sha256'];paths.append(p)
        paths += [out/'completion_manifest_v1.json',out/'parameter_replay_review_v1.json']
        models[name]=read(out/'summary.json')
    env=dict(os.environ,PYTHONPATH=str(snapshot/'src'),OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    for _ in range(2):subprocess.run([sys.executable,str(FOLDER/'publish_results_v1.py')],cwd=ROOT,env=env,check=True)
    publication=read(FOLDER/'publication_review_v1.json');assert publication['status']=='passed'
    cfg=read(ROOT/pipeline['readiness_config']['path'])
    cfg.update(output=str(FOLDER/'readiness_at_completion_v1.json'),csv=str(FOLDER/'readiness_at_completion_v1.csv'),report=str(ROOT/'reports/binding/direct_identity_readiness_v1.md'))
    ready=preparation.run(cfg);assert ready['counts']==dict(ready=58,needs_scientific_decision=9,deferred_optional=3),ready['counts']
    current=ROOT/'reports/binding/preparation_readiness.md';shared=False
    if current.is_file() and bounded._sha(current)==pipeline['queued_readiness_report_sha256']:
        current.write_bytes(Path(cfg['report']).read_bytes());shared=True
    guards=scheduler.ensure_enabled(ROOT,force=True)
    assert guards['enabled'] and guards['healthy'] and guards['pending_guards']>=2
    logging_path=FOLDER/'completion_logging_review_v1.json'
    if not logging_path.exists():
        bounded._put(logging_path,dict(status='passed',enabled=True,healthy=True,interval_minutes=guards['interval_minutes'],pending_guards=guards['pending_guards'],new_model_queries=0,new_fits=0))
    else:assert read(logging_path)['status']=='passed'
    paths += [FOLDER/n for n in ('execution_source_v1.json','build_review_v1.json','target_preflight_review_v1.json','software_validation_review_v1.json','regression_v1.xml','regression_sources_v1.zip','regression_archive_review_v1.json','jobs_v1.json','submission_review_v1.json','completion_pipeline_v1.json','closure_job_v1.json','publication_review_v1.json','comparison_v1.json','form_cells_v1.csv','completion_logging_review_v1.json','readiness_at_completion_v1.json','readiness_at_completion_v1.csv','run_validation_v1.py','run_readouts_v1.py','publish_results_v1.py','finish_suite_v1.py')]
    paths += [snapshot/'frozen_manifest.json',ROOT/pipeline['readiness_config']['path'],ROOT/'reports/binding/direct_identity_plan_v1.md',ROOT/build['linearity_note']['path'],ROOT/'reports/binding/direct_identity_findings_v1.md',ROOT/'reports/binding/direct_identity_readiness_v1.md',ROOT/'reports/binding/figures/direct_identity_v1.png',ROOT/'reports/binding/figures/direct_identity_v1.svg',ROOT/'artifacts/binding/diversity_decoding/20261028_v1/handoff_review_v1.json',ROOT/'artifacts/binding/diversity_identity_review/20261028_v1/handoff_review_v1.json']
    handoff=dict(status='complete_audited',evaluation_role='discovery_direct_identity_completed_handoff_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,capture_source_snapshot='345f75b01f5c3b33bd0ca6d8',software_validation=qa['counts'],source_rows=5760,target_columns=192,categorical_heads=24,active_sites=[7,8],initial_site3='All copy-event targets undefined; no fits.',fit_banks=60,factorizations=60,parameter_replay_rows=345600,new_model_queries=0,new_GPU_allocations=0,model_summaries=models,joint_prediction_uses_global_codebook_only=True,source_owner_prior_uses_TRAIN_versions_only=True,component_scores_are_linear_joint_marginals=True,byte_identical_publication=True,tracked_tasks=70,readiness_counts=ready['counts'],shared_inventory_refreshed=shared,completion_worker_array_loading=False,generated_holdouts_opened=False,publication_worker_job_id=os.environ['SLURM_JOB_ID'],limitations='Adaptive conditional event-identity accessibility with explicit owner syntax, constant first versions, sparse final-parent version4 support and coupled score marginals; no causal use or untouched unfamiliar-program qualification.',pins=[pin(p) for p in sorted(set(paths))])
    bounded._put(FOLDER/'handoff_review_v1.json',handoff)
    for item in handoff['pins']:assert pin(item['path'])==item
    print(json.dumps(dict(status='complete_audited',pins_verified=len(handoff['pins']),fit_banks=60,readiness=ready['counts']),sort_keys=True))


if __name__=='__main__':main()
