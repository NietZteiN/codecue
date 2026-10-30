#!/usr/bin/env python
"""Stamp job manifests and automatically publish lifecycle/results metadata.

The sbatch wrapper preserves the experiment's exit status independently of this
bookkeeping. Logging failures are reported and never replace that status.
"""
import datetime
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def workspace_root(root):
    manifest = Path(root) / 'frozen_manifest.json'
    if manifest.exists():
        return Path(json.loads(manifest.read_text())['workspace_root']).resolve()
    return Path(root).resolve()


def log_job(event_type, payload):
    try:
        root = workspace_root(ROOT)
        sys.path.insert(0, str(root / 'src'))
        from codecue.binding.experiment_log import safe_emit_event
        safe_emit_event(event_type, root=root, payload=payload, job_id=payload.get('job_id'))
    except Exception as exc:
        print(f'Experiment logging warning ({event_type}): {type(exc).__name__}: {exc}', file=sys.stderr)


def sync_job(payload):
    """Index only this job's run/report paths, including frozen entrypoints."""
    try:
        root = workspace_root(ROOT)
        sys.path.insert(0, str(root / 'src'))
        from codecue.binding.experiment_log import safe_sync_job
        safe_sync_job(root=root, payload=payload, job_id=payload.get('job_id'))
    except Exception as exc:
        print(f'Experiment result indexing warning: {type(exc).__name__}: {exc}', file=sys.stderr)


def write_manifest(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=1) + '\n')
    temporary.replace(path)


def main() -> int:
    mode = sys.argv[1]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if mode == 'start':
        src, dst = sys.argv[2], sys.argv[3]
        data = json.loads(Path(src).read_text())
        data.update(job_id=os.environ.get('SLURM_JOB_ID') or data.get('job_id'),
                    node=os.environ.get('SLURMD_NODENAME'), started_utc=now,
                    actual_partition=os.environ.get('SLURM_JOB_PARTITION'),
                    restart_count=int(os.environ.get('SLURM_RESTART_COUNT', '0')),
                    submission_manifest=data.get('submission_manifest', str(Path(src).resolve())),
                    job_manifest=str(Path(dst).resolve()), status='running')
        write_manifest(dst, data)
        log_job('job_started', data)
    elif mode == 'finish':
        dst, rc = sys.argv[2], int(sys.argv[3])
        path = Path(dst)
        if path.exists():
            data = json.loads(path.read_text())
        else:
            data = dict(job_id=os.environ.get('SLURM_JOB_ID'), name=os.environ.get('SLURM_JOB_NAME'),
                        node=os.environ.get('SLURMD_NODENAME'), job_manifest=str(path.resolve()),
                        metadata_warning='Job start manifest missing; recovered completion from scheduler environment.')
        # TERM and EXIT traps may both stamp the same completion. Keep one event
        # and the original finish timestamp, while allowing a sync retry.
        if not data.get('finished_utc') or data.get('exit_code') != rc:
            data.update(exit_code=rc, finished_utc=now, status='completed' if rc == 0 else 'failed')
            write_manifest(path, data)
            log_job('job_finished', data)
        sync_job(data)
    else:
        raise ValueError(f'unknown stamp mode: {mode}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
