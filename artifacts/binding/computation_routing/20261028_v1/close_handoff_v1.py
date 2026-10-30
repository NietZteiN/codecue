"""Close completed discovery work using audited metadata; no model execution."""
import hashlib
import json
from pathlib import Path

from codecue.binding import overnight_relationship_capture as capture

ROOT = Path(__file__).resolve().parents[4]
FOLDER = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def pin(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    assert path.is_file() and not path.is_symlink(), path
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=checksum.hexdigest())


comparison = read(FOLDER / 'comparison_v1.json')
assert comparison['scored_unique_responses'] == 40200
assert comparison['logical_responses'] == 41472
assert comparison['scientific_confirmed_warmup_requests'] == 16
assert comparison['scientific_model_requests_exact'] == 40216
assert comparison['prospective_instruction_gates'] == 6
assert comparison['qualified_instruction_gates'] == 0
validation = read(FOLDER / 'software_validation_review_v1.json')
assert validation['counts'] == dict(tests=1843, failures=0, errors=0, skipped=0)
assert read(FOLDER / 'independent_execution_review_v1.json')['status'] == 'passed'
source_review = read(FOLDER / 'source_handoff_review_v1.json')
assert source_review['physical_sources'] == 6700
assert source_review['logical_memberships'] == 6912
assert source_review['required_gate_cell_unique_source_minimum'] == 30
schedule = read(FOLDER / 'schedule_preparation_review_v1.json')
assert schedule['status'] == 'passed' and schedule['targets_prepared_only']
assert schedule['learned_readout_compatible'] is False
assert schedule['counts']['rows'] == 2016
assert schedule['counts']['maximum_assignment_version'] == 4
readiness = read(FOLDER / 'readiness_at_completion_v1.json')
assert readiness['counts'] == dict(ready=48, needs_scientific_decision=9,
                                deferred_optional=3)
resource = read(FOLDER / 'resource_review_v1.json')
assert len(resource['jobs']) == 8 and resource['gpu_allocation_seconds'] == 845
assert all(v['state'] == 'COMPLETED' and v['exit_code'] == '0:0'
           for v in resource['jobs'].values())
publication_stdout = ROOT / 'log/slurm/481109_computation-routing-publication.out'
assert 'byte_identical_reproduction' in publication_stdout.read_text()

log_path = FOLDER / 'log_tick_completion_stdout_v1.txt'
log = read(log_path)
assert log['status'] == 'complete' and log['result']['status'] == 'ok'
assert log['result']['issues'] == []
scheduler = log['scheduler']
assert scheduler['enabled'] and scheduler['healthy']
assert scheduler['interval_minutes'] == 10 and scheduler['pending_guards'] >= 2
assert not scheduler['error'] and not scheduler['scheduler_error']
capture._put(FOLDER / 'logging_review_v1.json', dict(
    evaluation_role='computation_routing_automatic_logging_review_v1',
    status='passed', recorded_utc=log['result']['updated_utc'],
    reconciliation=pin(log_path), counts=log['result']['counts'],
    indexed_records=log['result']['records'], events=log['result']['events'],
    issues=[], bounded_metadata_notices=log['result']['notices'],
    enabled=True, healthy=True, interval_minutes=10,
    pending_successor_guards=scheduler['pending_guards'],
    guard_jobs=scheduler['workers'], new_model_queries=0, new_fits=0,
    generated_holdouts_opened=False))

paths = set()
for pattern in ('*_review_v1.json', '*_source_v1.json', '*jobs_v1.json',
                '*_job_v1.json', '*stdout_v*.txt'):
    paths.update(FOLDER.glob(pattern))
paths.update(FOLDER / name for name in (
    'sources.jsonl', 'sources.manifest.json', 'regression_v1.xml',
    'regression_sources_v1.zip', 'readiness_at_completion_v1.json',
    'comparison_v1.json', 'form_cells_v1.csv', 'contrasts_v1.csv',
    'publish_results_v1.py', 'run_publication_v1.py', 'run_validation_v1.py',
    'close_handoff_v1.py'))
paths.add(publication_stdout)
paths.add(ROOT / 'log/slurm/481109_computation-routing-publication.json')
for name in ('generation_source_v1.json', 'execution_source_v1.json',
             'schedule_generation_source_v1.json'):
    source = read(FOLDER / name)
    assert source['code'] == validation['source_sha256']
    paths.add(Path(source['snapshot']) / 'frozen_manifest.json')
for name in ('llama8b', 'codellama34b'):
    folder = FOLDER / name
    for filename in ('routing_completion_v1.json', 'review_v1.json',
                     'routing_preflight_v1.json', 'tokenizer_preflight.json',
                     'routing_attempts_v1.json'):
        paths.add(folder / filename)
    for filename in ('audit.json', 'manifest.json', 'runtime.json', 'summary.json'):
        paths.add(folder / 'checkpoint_suite' / filename)
publication = read(FOLDER / 'publication_review_v1.json')
for item in publication['input_pins'] + publication['output_pins']:
    current = pin(item['path'])
    assert current['sha256'] == item['sha256'] and current['bytes'] == item['bytes']
    paths.add(ROOT / item['path'])
paths.update(ROOT / name for name in (
    'artifacts/binding/relationships/schedule_sources_v1.jsonl',
    'artifacts/binding/relationships/schedule_sources_v1.manifest.json',
    'artifacts/binding/relationships/schedule_source_review_v1.json',
    'configs/binding/computation_routing_20261028_v1/generation.json',
    'configs/binding/computation_routing_20261028_v1/llama8b.json',
    'configs/binding/computation_routing_20261028_v1/codellama34b.json',
    'configs/binding/relationships/schedule_generation_v1.json',
    'configs/binding/relationships/schedule_generation_v2.json',
    'configs/binding/preparation/readiness_v14.json',
    'reports/binding/computation_routing_plan_v1.md',
    'reports/binding/computation_routing_decision_v1.md',
    'reports/binding/computation_routing_status_v1.md',
    'reports/binding/relationship_schedule_preparation_v1.md',
    'artifacts/binding/overnight_relationships/20261028_completion_v1/handoff_review_v1.json'))

handoff = dict(
    evaluation_role='discovery_computation_routing_completed_handoff_v1',
    status='complete_audited', scope='adaptive discovery; completed negative qualification',
    recorded_utc=log['result']['updated_utc'],
    source=read(FOLDER / 'execution_source_v1.json'),
    software_validation=validation['counts'],
    scientific_work=dict(scored_physical_responses=40200, logical_responses=41472,
                         confirmed_warmup_requests=16, total_model_requests=40216,
                         new_fits=0, hidden_state_captures=0,
                         prospective_instruction_gates=6, qualified_instruction_gates=0),
    computation_sources=dict(unique_sources=6700, logical_memberships=6912,
                             root_order_clusters=24, train_clusters=12, dev_clusters=12,
                             minimum_required_gate_unique_support=30,
                             shared_descriptive_literal_controls=68),
    schedule_sources=dict(rows=2016, canonical_ssa_graph_families=15,
                          train_graph_families=10, dev_graph_families=5,
                          maximum_assignment_version=4, targets_prepared_only=True,
                          learned_readout_compatible=False,
                          prior_exact_source_overlap=0, prior_canonical_ast_overlap=0,
                          prior_alpha_structure_overlap=3),
    models={name: dict(status=model['status'],
                       scored_unique_cases=model['scored_unique_cases'],
                       physical_counts=model['physical_counts'],
                       prospective_gates=model['prospective_gates'],
                       resources=model['resources'])
            for name, model in comparison['models'].items()},
    resource_accounting=dict(jobs=resource['jobs'], gpu_allocation_seconds=845,
                             allocated_cpu_seconds=resource['allocated_cpu_seconds'],
                             scope=resource['scope'], unrelated_jobs_canceled=False),
    setup_history=['Initial schedule overlap configuration was rejected before source publication; corrected v2 is frozen. No model work was repeated.',
                   'A publication dependency submission failed after completed dependency records aged out; verified zero exit codes before resubmission. No scientific rerun.',
                   'Pending 34B backfill minimum changed from 30 to 15 minutes; maximum remained 48 hours. Completed in 464 seconds without retry.'],
    tracked_tasks=60, readiness_counts=readiness['counts'],
    scientific_decisions_remaining=9, optional_extensions_deferred=3,
    automatic_logging=dict(enabled=True, healthy=True, interval_minutes=10,
                           issues=[], pending_successor_guards=2),
    publication_reproduction='CPU worker ran publisher twice; second invocation reproduced all outputs byte for byte.',
    limitations=comparison['limitations'] + [
        'Full-root and full-leaf share the same program body and answer but differ in query identifier, variable age, role cues and recency; this is not causal copy isolation.',
        'The 24 root orders contain related topologies; the 72 order-depth units are not independent program families.',
        'Varied schedule targets alone do not establish learned version recovery. Existing fixed-schedule heads require a generic replacement.',
        'All six gates failed; software completion does not establish scientific reliability. Original causal and unfamiliar-program claims remain open.'],
    generated_holdouts_opened=False, activation_arrays_opened_for_handoff=False,
    new_model_queries_for_handoff=0, new_fits_for_handoff=0,
    mutable_paths_not_pinned=['README.md', 'reports/binding/implementation_checklist.md',
                             'reports/binding/preparation_readiness.md',
                             'reports/binding/experiment_log.md',
                             str((FOLDER / 'readiness_live_v1.json').relative_to(ROOT)),
                             'artifacts/binding/experiment_log/index.sqlite3'],
    pins=[pin(path) for path in sorted(paths)])
capture._put(FOLDER / 'handoff_review_v1.json', handoff)
for item in handoff['pins']:
    assert pin(item['path']) == item, item['path']
print(json.dumps(dict(status='complete_audited', pins_verified=len(handoff['pins']),
                      tests=1843, scored_responses=40200, gates_qualified=0,
                      logging_healthy=True), sort_keys=True))
