"""Read-only experiment health checks; no tokenizer, model or budget mutation."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from .datasets import write_json

FAILED = {'FAILED', 'TIMEOUT', 'OUT_OF_MEMORY', 'NODE_FAIL', 'CANCELLED', 'PREEMPTED', 'BOOT_FAIL'}
SCHEDULER_TIMEOUT_SECONDS = 15


def read(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else None


def query_scheduler(ids, runner=None):
    runner = runner or subprocess.run
    if not ids:
        return {}, []
    if any(not str(i).isdigit() for i in ids):
        raise ValueError('scheduler job IDs must be decimal integers')
    jobs, errors = {}, []
    commands = [
        ['sacct', '-n', '-P', '-j', ','.join(ids), '--format=JobIDRaw,State%32,ExitCode,ElapsedRaw'],
        ['squeue', '-h', '-j', ','.join(ids), '-o', '%i|%T|%r'],
    ]
    for index, argv in enumerate(commands):
        try:
            result = runner(argv, capture_output=True, text=True, check=False,
                            timeout=SCHEDULER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            errors.append(f'{argv[0]}: timed out after {SCHEDULER_TIMEOUT_SECONDS}s')
            continue
        except OSError as exc:
            errors.append(f'{argv[0]}: {exc}')
            continue
        if result.returncode:
            errors.append(f'{argv[0]}: {result.stderr.strip()}')
            continue
        for line in result.stdout.splitlines():
            fields = [v.strip() for v in line.split('|')]
            if not fields or fields[0] not in ids:
                continue  # Ignore .batch/.extern and unrelated job steps.
            job = jobs.setdefault(fields[0], {})
            job['state'] = fields[1].split()[0].rstrip('+')
            if index == 0 and len(fields) >= 4:
                job.update(exit_code=fields[2], elapsed_seconds=int(fields[3]))
            elif index == 1 and len(fields) >= 3:
                job['reason'] = fields[2]
    return jobs, errors


def response_progress(path):
    path = Path(path)
    if not path.exists():
        return {'records': 0, 'incomplete_tail': False, 'malformed_lines': []}
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    count, incomplete, malformed = 0, False, []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except (ValueError, UnicodeError):
            if index == len(lines) - 1 and not line.endswith(b'\n'):
                incomplete = True  # A writer can be midway through its final append.
            else:
                malformed.append(index + 1)
        else:
            count += 1
    return {'records': count, 'incomplete_tail': incomplete, 'malformed_lines': malformed}


def inspect_stage(path):
    path = Path(path)
    manifest = read(path / 'manifest.json')
    summary = read(path / 'summary.json') or read(path / 'progress.json')  # Read before append-only responses.
    progress = response_progress(path / 'responses.jsonl')
    result = {'path': str(path), 'manifest_status': manifest['status'] if manifest else 'not_started',
              'evaluated': summary.get('evaluated', 0) if summary else 0,
              'planned': summary.get('planned') if summary else None,
              'responses': progress, 'issues': []}
    if progress['malformed_lines']:
        result['issues'].append('malformed committed response records')
    if manifest and manifest['status'] == 'complete':
        if (not summary or not summary.get('complete') or progress['incomplete_tail']
                or progress['records'] != result['evaluated'] or result['evaluated'] != result['planned']):
            result['issues'].append('completed manifest has inconsistent response coverage')
        elif (manifest.get('responses_sha256') != summary.get('responses_sha256')
              or hashlib.sha256((path / 'responses.jsonl').read_bytes()).hexdigest() != manifest.get('responses_sha256')):
            result['issues'].append('completed response checksum mismatch')
    if manifest and manifest['status'] in ('failed', 'budget_limited'):
        result['issues'].append(manifest.get('error', manifest['status']))
    if summary and not manifest:
        result['issues'].append('summary exists without a run manifest')
    return result


def inspect_throughput(path):
    """Read compact trial summaries without loading the large response artifacts."""
    path = Path(path)
    manifest, summary = read(path / 'manifest.json'), read(path / 'summary.json')
    workers = [read(p) for p in sorted(path.glob('worker_*/worker.json'))]
    trials = [t for worker in workers for t in worker.get('trials', []) if t.get('status') == 'complete']
    candidates = [t for worker in workers for t in worker.get('inline_candidates', []) if t.get('status') == 'complete']
    validation = summary.get('validation', {}) if summary else {}
    final = validation.get('trials', [])
    count = final[0].get('cases', 0) if len(final) == 1 else 0
    result = {'path': str(path), 'manifest_status': manifest['status'] if manifest else 'not_started',
              'evaluated': count, 'planned': None, 'issues': [],
              'responses': {'records': count, 'incomplete_tail': False, 'malformed_lines': []},
              'completed_profile_trials': len(trials), 'completed_validation_candidates': len(candidates),
              'best_profile_requests_per_second': max((t['requests_per_second'] for t in trials), default=None),
              'validation_requests_per_second': final[0].get('requests_per_second') if count else None}
    if manifest:
        from .published_benchmarks import plan
        result['planned'] = len(plan(manifest['identity']['config']))
        if manifest['status'] == 'complete':
            if (not summary or not summary.get('complete') or validation.get('status') != 'complete'
                    or len(final) != 1 or final[0].get('status') != 'complete' or count != result['planned']):
                result['issues'].append('completed throughput stage lacks complete full-workload validation')
        elif manifest['status'] in ('failed', 'budget_limited', 'cancelled'):
            result['issues'].append(manifest.get('error', manifest['status']))
    return result


def classify(jobs, stages, audited):
    problems = [f"job {key}: {job['state']}" for key, job in jobs.items() if job.get('state') in FAILED]
    problems += [f"job {key}: failed dependency" for key, job in jobs.items()
                 if job.get('reason') == 'DependencyNeverSatisfied']
    problems += [f"{stage['name']}: {issue}" for stage in stages for issue in stage['issues']]
    if problems:
        return 'needs_attention', problems
    if audited and stages and all(s['manifest_status'] == 'complete' for s in stages):
        return 'complete', []
    if any(j.get('state') in ('RUNNING', 'COMPLETING') for j in jobs.values()):
        return 'running', []
    if any(j.get('state') == 'PENDING' for j in jobs.values()):
        return 'queued', []
    if any(s['manifest_status'] == 'started' for s in stages):
        return 'unconfirmed_running_state', ['started artifact without a confirmed live scheduler job']
    return 'awaiting_audit' if stages and all(s['manifest_status'] == 'complete' for s in stages) else 'not_started', []


def collect(config, runner=None):
    definitions = read(config['jobs'])
    ids = {key: definitions[key] for key in config['job_keys']}
    scheduler, scheduler_errors = query_scheduler(list(ids.values()), runner)
    jobs = {key: {'job_id': value, **scheduler.get(value, {'state': 'UNKNOWN'})} for key, value in ids.items()}
    stages = [{'name': spec['name'], **(inspect_throughput(spec['path']) if spec.get('kind') == 'throughput'
                                      else inspect_stage(spec['path']))} for spec in config['stages']]
    comparison = read(config['comparison_artifact'])
    audited = bool(comparison and (comparison.get('complete') or comparison.get('status') == 'passed')
                   and Path(config['completed_report']).exists())
    status, issues = classify(jobs, stages, audited)
    ledger = read(config['budget_ledger'])
    budget = None
    if ledger:
        reserved = sum(lease['reserved_seconds'] for lease in ledger['active'].values())
        cap = ledger['cap_seconds']
        budget = {'cap_seconds': ledger['cap_seconds'], 'used_seconds': ledger['used_seconds'],
                  'reserved_seconds': reserved, 'active_jobs': len(ledger['active']),
                  'unreserved_seconds': cap - ledger['used_seconds'] - reserved if cap is not None else None}
        if budget['unreserved_seconds'] is not None and budget['unreserved_seconds'] < 0:
            status = 'needs_attention'
            issues.append('shared GPU budget exceeded or over-reserved')
    return {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'status': status,
            'jobs': jobs, 'stages': stages, 'issues': issues, 'scheduler_errors': scheduler_errors,
            'budget': budget, 'comparison_audited': audited, 'completed_report': config['completed_report'],
            'title': config.get('title', 'Serialization experiment status'),
            'refresh_command': config.get('refresh_command', 'python scripts/101_binding_experiment_status.py configs/binding/serialization/status_v1.json'),
            'plan_report': config.get('plan_report', 'serialization_plan.md'),
            'model_inference': False, 'scientific_artifacts_modified': False,
            'generated_holdouts_opened': False}


def report(result):
    lines = ['# ' + result.get('title', 'Serialization experiment status'), '',
             f"Status: **{result['status']}**. Checked at {result['recorded_utc']}. "
             'This command checks saved artifacts and SLURM; it makes no model queries.', '',
             '| Stage | Saved predictions | Planned | Manifest |', '|---|---:|---:|---|']
    for stage in result['stages']:
        lines.append(f"| {stage['name']} | {stage['responses']['records']} | {stage['planned'] if stage['planned'] is not None else 'pending'} | {stage['manifest_status']} |")
        if 'completed_profile_trials' in stage:
            lines += ['', f"Completed profiling trials: {stage['completed_profile_trials']}; full-workload candidates: "
                      f"{stage['completed_validation_candidates']}. Best profile requests/s: "
                      f"{stage['best_profile_requests_per_second']}; full validation requests/s: "
                      f"{stage['validation_requests_per_second']}.", '']
    lines += ['', '| Job | ID | State | Reason |', '|---|---:|---|---|']
    for name, job in result['jobs'].items():
        lines.append(f"| {name} | {job['job_id']} | {job['state']} | {job.get('reason', '—')} |")
    for issue in result['issues'] + result['scheduler_errors']:
        lines += ['', '- ' + issue]
    if result['budget']:
        budget = result['budget']
        lines += ['', f"GPU usage: {budget['used_seconds']/60:.2f} minutes logged, "
                  f"{budget['reserved_seconds']/60:.2f} reserved. " +
                  (f"Cap: {budget['cap_seconds']/60:.0f} minutes." if budget['cap_seconds'] is not None
                   else 'No cumulative project compute cap; reservations track active job walltime.')]
    lines += ['', 'Completed comparison report: `' + result['completed_report'] + '`. '
              'The report is ready only when the comparison audit has completed. A partial final JSONL '
              'append is reported without trimming or modifying it. No failed job, dependency or budget '
              'reservation is automatically cleared.', '',
              'Refresh with `' + result['refresh_command'] + '`. '
              'See [the fixed plan](' + result['plan_report'] + ') and the JSON status artifact for exact paths.', '']
    return '\n'.join(lines)


def run(config):
    result = collect(config)
    write_json(config['output'], result)
    path = Path(config['report'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report(result))
    return result
