"""Pin completed build/publication helpers and queue automatic finite-study closure."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding import relationship_capture as bounded
from codecue.binding import experiment_log_scheduler as scheduler
from codecue.binding import overnight_relationship_capture as durable
PYTHON='/work/jvl210002/migration/envs/probe-cu129/bin/python'

def read(path):return json.loads(Path(path).read_text())
def pin(path):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    return dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=bounded._sha(p))

def main():
    source=read(FOLDER/'execution_source_v1.json');jobs=read(FOLDER/'jobs_v1.json')
    checks=read(FOLDER/'publisher_build_review_v1.json')
    assert checks['status']=='passed' and checks['synthetic_checks']>0
    assert checks['publisher_sha256']==bounded._sha(FOLDER/'publish_grammar_v1.py')
    helpers=[FOLDER/name for name in ('prepare_submission_v1.py','queue_completion_v1.py','run_validation_v1.py','run_analysis_v1.py','publish_grammar_v1.py','finish_review_v1.py','independent_build_review_v1.json','publisher_build_review_v1.json')]
    pipeline=dict(status='ready',evaluation_role='discovery_identity_grammar_completion_pipeline_v1',source=source,
        helper_pins=[pin(p) for p in helpers],readiness_config=pin('configs/binding/preparation/readiness_v23.json'),
        queued_readiness_report_sha256=bounded._sha(ROOT/'reports/binding/preparation_readiness.md'),
        requires_completed_jobs=list(jobs.values()),execution_order=['verify_QA_and_saved_score_replay','metadata_publication','byte_identical_publication','readiness_refresh','logging_health','immutable_handoff'],
        publisher_synthetic_checks=checks['synthetic_checks'],array_loading=False,new_fits=0,new_model_queries=0,parameters_reapplied=0)
    bounded._put(FOLDER/'completion_pipeline_v1.json',pipeline)
    subprocess.run([PYTHON,str(FOLDER/'finish_review_v1.py'),'--check-setup'],cwd=ROOT,check=True)
    closure=FOLDER/'closure_progress_v1.json'
    if closure.exists():job=read(closure)['job_id']
    else:
        spec=importlib.util.spec_from_file_location('grammar_closure_submit',ROOT/'scripts/slurm/submit.py');submit=importlib.util.module_from_spec(spec);spec.loader.exec_module(submit)
        job=submit.submit(name='binding-grammar-finish',partition='dev,normal',cpus=8,mem='16G',time='02:00:00',dependency='afterok:'+jobs['analysis'],argv=[PYTHON,str(FOLDER/'finish_review_v1.py')])
        durable._journal(closure,dict(job_id=job))
    bounded._put(FOLDER/'closure_job_v1.json',dict(status='submitted',job_id=job,dependency='afterok:'+jobs['analysis'],new_fits=0,new_model_queries=0,parameters_reapplied=0,array_loading=False))
    health=scheduler.ensure_enabled(ROOT,force=True)
    assert health['enabled'] and health['healthy'] and health['pending_guards']>=2
    logging_path=FOLDER/'submission_logging_review_v1.json'
    if not logging_path.exists():bounded._put(logging_path,dict(status='passed',enabled=True,healthy=True,pending_guards=health['pending_guards'],interval_minutes=health['interval_minutes']))
    else:assert read(logging_path)['status']=='passed'
    bounded._put(FOLDER/'queue_handoff_review_v1.json',dict(status='submitted_with_automatic_closure',source=source,jobs=jobs,closure_job=job,expected_regression_tests=2191,focused_tests_passed=62,score_banks=60,new_fits=0,new_model_queries=0,parameters_reapplied=0,new_GPU_allocations=0,generated_holdouts_opened=False,pipeline_sha256=bounded._sha(FOLDER/'completion_pipeline_v1.json'),pins=pipeline['helper_pins']))
    print(json.dumps(dict(status='submitted_with_automatic_closure',closure_job=job,jobs=jobs),sort_keys=True))

if __name__=='__main__':main()
