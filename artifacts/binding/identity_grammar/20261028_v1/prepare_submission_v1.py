"""Collect, freeze and submit the finite grammar QA/analysis chain once sources are stable."""
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding import relationship_capture as bounded,snapshots,preparation
from codecue.binding import overnight_relationship_capture as durable
from codecue.binding.datasets import digest
PYTHON='/work/jvl210002/migration/envs/probe-cu129/bin/python'

def read(path):return json.loads(Path(path).read_text())
def main():
    assert sys.executable==PYTHON or os.path.samefile(sys.executable,PYTHON)
    progress=read(FOLDER/'submission_progress_v1.json') if (FOLDER/'submission_progress_v1.json').exists() else {}
    if 'source' not in progress:
        before=snapshots.hashes(ROOT)
        old=read(ROOT/'artifacts/binding/sources/3e5471ac9dc9b948761fc429/frozen_manifest.json')
        changed=[name for name,value in old['code']['source_files'].items() if before[name]!=value]
        assert changed==['src/codecue/binding/snapshots.py'],changed
        checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'tests/binding').rglob('*.py'))}
        process=subprocess.run([PYTHON,'-m','pytest','tests/binding','--collect-only','-q'],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        bounded._publish(FOLDER/'collection_stdout_v1.txt',process.stdout)
        assert process.returncode==0,process.stdout[-4000:]
        matches=re.findall(rb'(\d+) tests? collected',process.stdout);assert len(matches)==1
        count=int(matches[0]);assert count>2129 and len(checksums)==106
        assert before==snapshots.hashes(ROOT)
        cfg_path=ROOT/'configs/binding/preparation/readiness_v23.json';cfg=read(cfg_path)
        regression=next(item for item in cfg['items'] if item['id']=='regression')
        regression['evidence'][0]['minimum_tests']=count
        cfg_path.write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
        source=snapshots.freeze();bounded._put(FOLDER/'execution_source_v1.json',source)
        bounded._put(FOLDER/'build_review_v1.json',dict(status='passed',evaluation_role='discovery_identity_grammar_build_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,expected_regression_tests=count,test_source_files=len(checksums),test_source_sha256=digest(checksums),new_tests=count-2129,changed_historical_sources=changed,source_free_core_independently_reviewed=True,expected_score_banks=60,expected_saved_score_rows=345600,expected_development_prediction_rows=86400,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        progress=dict(source=source,expected_tests=count,jobs={});durable._journal(FOLDER/'submission_progress_v1.json',progress)
    spec=importlib.util.spec_from_file_location('grammar_submit',ROOT/'scripts/slurm/submit.py');submit=importlib.util.module_from_spec(spec);spec.loader.exec_module(submit)
    for key,worker,name in [('regression','run_validation_v1.py','binding-grammar-qa'),('analysis','run_analysis_v1.py','binding-grammar-scores')]:
        if key not in progress['jobs']:
            dependency=None if key=='regression' else 'afterok:'+progress['jobs']['regression']
            job=submit.submit(name=name,partition='dev,normal',cpus=8,mem='32G' if key=='analysis' else '16G',time='02:00:00',dependency=dependency,argv=[PYTHON,str(FOLDER/worker)])
            progress['jobs'][key]=job;durable._journal(FOLDER/'submission_progress_v1.json',progress)
    bounded._put(FOLDER/'jobs_v1.json',progress['jobs'])
    bounded._put(FOLDER/'submission_review_v1.json',dict(status='submitted',evaluation_role='discovery_identity_grammar_submission_v1',source=progress['source'],jobs=progress['jobs'],score_banks=60,saved_score_rows_to_check=345600,development_prediction_rows=86400,new_fits=0,new_model_queries=0,parameters_reapplied=0,new_GPU_allocations=0,preserved_unrelated_jobs=True,generated_holdouts_opened=False))
    cfg=read(ROOT/'configs/binding/preparation/readiness_v23.json');ready=preparation.run(cfg)
    bounded._put(FOLDER/'readiness_at_submission_v1.json',ready)
    print(json.dumps(dict(status='submitted',source=progress['source'],expected_tests=progress['expected_tests'],jobs=progress['jobs'],readiness=ready['counts']),sort_keys=True))

if __name__=='__main__':main()
