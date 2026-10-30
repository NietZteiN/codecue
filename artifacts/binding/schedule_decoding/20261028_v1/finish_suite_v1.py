"""Review and publish completed dependent stages without opening model arrays."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
FOLDER = Path(__file__).resolve().parent
source = json.loads((FOLDER / 'execution_source_v1.json').read_text())
snapshot = Path(source['snapshot'])
sys.path.insert(0, str(snapshot / 'src'))
from codecue.binding import preparation, relationship_capture as bounded, snapshots
from codecue.binding import experiment_log_scheduler as scheduler


def read(path):
    return json.loads(Path(path).read_text())


def pin(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=bounded._sha(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-setup', action='store_true')
    options = parser.parse_args()
    frozen = snapshots.verify(snapshot)
    assert frozen['snapshot_id'] == source['snapshot_id']
    assert frozen['code']['source_sha256'] == source['code']
    pipeline = read(FOLDER / 'completion_pipeline_v1.json')
    assert pipeline['source'] == source
    for item in pipeline['helper_pins'] + [pipeline['readiness_config']]:
        assert pin(item['path']) == item, item['path']
    qa = read(FOLDER / 'software_validation_review_v1.json')
    assert qa['counts'] == dict(tests=1922, failures=0, errors=0, skipped=0)
    assert qa['source'] == source
    if options.check_setup:
        print(json.dumps(dict(status='passed_setup', source=source['snapshot_id'],
                              helpers=len(pipeline['helper_pins']),
                              scientific_outcomes_opened=False), sort_keys=True))
        return
    assert os.environ.get('SLURM_JOB_ID'), 'completion publication requires a CPU allocation'
    if (FOLDER / 'handoff_review_v1.json').exists():
        previous = read(FOLDER / 'handoff_review_v1.json')
        for item in previous['pins']:
            assert pin(item['path']) == item
        print(json.dumps(dict(status='verified_existing_handoff',
                              pins=len(previous['pins'])), sort_keys=True))
        return
    environment = dict(os.environ, PYTHONPATH=str(snapshot / 'src'),
                       OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4')
    for helper in ('independent_review_v1.py', 'publish_results_v1.py', 'publish_results_v1.py'):
        subprocess.run([sys.executable, str(FOLDER / helper)], cwd=ROOT,
                       env=environment, check=True)
    independent = read(FOLDER / 'independent_execution_review_v1.json')
    assert independent['status'] == 'passed' and independent['issues'] == []
    publication = read(FOLDER / 'publication_review_v1.json')
    assert publication['status'] == 'passed'
    cfg = read(ROOT / pipeline['readiness_config']['path'])
    assert pin(pipeline['readiness_config']['path']) == pipeline['readiness_config']
    cfg.update(output=str(FOLDER / 'readiness_at_completion_v1.json'),
               csv=str(FOLDER / 'readiness_at_completion_v1.csv'),
               report=str(ROOT / 'reports/binding/schedule_decoding_readiness_v1.md'))
    readiness = preparation.run(cfg)
    assert readiness['counts'] == dict(ready=51, needs_scientific_decision=9,
                                      deferred_optional=3), readiness['counts']
    # A newer user continuation may already have advanced the shared inventory.
    # Update it only while it is still byte-identical to this suite's queue view.
    current = ROOT / 'reports/binding/preparation_readiness.md'
    refreshed_shared_inventory = False
    if bounded._sha(current) == pipeline['queued_readiness_report_sha256']:
        current.write_bytes(Path(cfg['report']).read_bytes())
        refreshed_shared_inventory = True
    captures = {name: read(FOLDER / name / 'capture/summary.json')
                for name in ('llama8b', 'codellama34b')}
    readouts = {name: read(FOLDER / name / 'readouts/summary.json') for name in captures}
    assert all(c['cases'] == 2016 and c['generated_responses'] == 0 for c in captures.values())
    assert all(r['fit_banks'] == 45 and r['factorizations'] == 45 for r in readouts.values())
    guards = scheduler.ensure_enabled(ROOT, force=True)
    assert guards['enabled'] and guards['healthy'] and guards['pending_guards'] >= 2
    logging_review = dict(
        status='passed', evaluation_role='discovery_schedule_completion_logging_v1',
        enabled=True, healthy=True, interval_minutes=guards['interval_minutes'],
        pending_guards=guards['pending_guards'], worker_job_id=os.environ['SLURM_JOB_ID'],
        artifacts_emit_durable_index_events=True, new_model_queries=0, new_fits=0)
    if not (FOLDER / 'completion_logging_review_v1.json').exists():
        bounded._put(FOLDER / 'completion_logging_review_v1.json', logging_review)
    else:
        assert read(FOLDER / 'completion_logging_review_v1.json')['status'] == 'passed'
    paths = {FOLDER / name for name in (
        'execution_source_v1.json', 'build_review_v1.json', 'source_availability_review_v1.json',
        'target_preflight_review_v1.json', 'software_validation_review_v1.json',
        'regression_v1.xml', 'regression_sources_v1.zip', 'regression_archive_review_v1.json',
        'jobs_v1.json', 'submission_review_v1.json', 'completion_pipeline_v1.json',
        'closure_job_v1.json', 'independent_execution_review_v1.json',
        'publication_review_v1.json', 'comparison_v1.json', 'form_cells_v1.csv',
        'readiness_at_completion_v1.json', 'readiness_at_completion_v1.csv',
        'completion_logging_review_v1.json', 'publish_results_v1.py',
        'independent_review_v1.py', 'finish_suite_v1.py', 'run_stage_v1.py',
        'run_validation_v1.py', 'submit_suite_v1.py')}
    paths.add(snapshot / 'frozen_manifest.json')
    for name in captures:
        for stage in ('capture', 'readouts'):
            for filename in ('completion_manifest_v1.json', 'summary.json', 'audit.json'):
                paths.add(FOLDER / name / stage / filename)
        paths.add(FOLDER / name / 'readouts/parameter_replay_review_v1.json')
    for name in ('reports/binding/schedule_decoding_plan_v1.md',
                 'reports/binding/schedule_decoding_findings_v1.md',
                 'reports/binding/schedule_decoding_readiness_v1.md',
                 'reports/binding/figures/schedule_decoding_v1.png',
                 'reports/binding/figures/schedule_decoding_v1.svg'):
        paths.add(ROOT / name)
    handoff = dict(status='complete_audited',
        evaluation_role='discovery_schedule_completed_handoff_v1', source=source,
        recorded_utc=datetime.now(timezone.utc).isoformat(),
        software_validation=qa['counts'], independent_review='passed',
        source_rows=2016, target_columns=232, training_graph_families=10,
        development_graph_families=5, maximum_assignment_version=4,
        distinct_new_prefill_sources=4032,
        actual_prefill_cases={k: v['model_prefill_cases_attempted'] for k, v in captures.items()},
        generated_responses=0, fit_banks=90, factorizations=90,
        parameter_replay_rows=sum(v['parameter_replay_rows'] for v in readouts.values()),
        model_summaries=readouts, tracked_tasks=63, readiness_counts=readiness['counts'],
        refreshed_shared_inventory=refreshed_shared_inventory,
        original_scientific_decisions_remaining=9, optional_extensions_deferred=3,
        publication='Independent review followed by two byte-identical publications. Numerical replay was completed by each readout CPU worker.',
        publication_worker=dict(job_id=os.environ['SLURM_JOB_ID'],
                                slurm_terminal_state='Recorded by the job finish trap after this handoff is written.'),
        limitations='Adaptive discovery on five DEV graph families; no natural causal binding/version mechanism, reliability rescue, or untouched unfamiliar-program prediction established.',
        generated_holdouts_opened=False, array_loading_by_completion_worker=False,
        binary_artifacts_stream_hashed_only=True,
        new_model_queries_by_completion_worker=0, new_fits_by_completion_worker=0,
        pins=[pin(path) for path in sorted(paths)])
    bounded._put(FOLDER / 'handoff_review_v1.json', handoff)
    for item in handoff['pins']:
        assert pin(item['path']) == item
    print(json.dumps(dict(status='complete_audited', pins_verified=len(handoff['pins']),
                          actual_prefills=handoff['actual_prefill_cases'], fit_banks=90,
                          readiness=readiness['counts']), sort_keys=True))


if __name__ == '__main__':
    main()
