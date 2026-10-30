"""Run identities include dirty source contents; incompatible resumes are refused."""
from __future__ import annotations
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from contextvars import ContextVar
from functools import wraps
from datetime import datetime, timezone
from pathlib import Path
from .datasets import digest, write_json

ROOT = Path(__file__).resolve().parents[3]
ACTIVE_STAGE = ContextVar('binding_active_stage', default=None)


def guarded(function):
    """Record failures even before a stage reaches its main processing loop."""
    @wraps(function)
    def wrapped(config):
        token = ACTIVE_STAGE.set(None)
        started = time.monotonic()
        try:
            return function(config)
        except Exception as exc:
            active = ACTIVE_STAGE.get()
            if active is not None:
                out, manifest = active
                finish(out, manifest, time.monotonic() - started, 'failed', error=f'{type(exc).__name__}: {exc}')
            raise
        finally:
            ACTIVE_STAGE.reset(token)
    return wrapped


def code_identity():
    from .snapshots import hashes, verify
    if (ROOT / 'frozen_manifest.json').exists():
        return verify(ROOT)['code']
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    content = hashes(ROOT)
    return {"git_revision": rev, "source_sha256": digest(content), "source_files": content}


def _log_stage(event_type, out, manifest):
    try:
        from .experiment_log import safe_emit_event
        from .snapshots import workspace_root
        safe_emit_event(event_type,root=workspace_root(ROOT),run_dir=out,
            stage=manifest['identity']['stage'],job_id=manifest.get('slurm_job_id'),
            payload={'status':manifest['status'],'manifest':str(out/'manifest.json'),
                     'identity_hash':manifest['identity_hash'],'error':manifest.get('error')})
    except Exception as exc:
        print(f'Experiment lifecycle logging deferred: {type(exc).__name__}: {exc}',file=sys.stderr)


def begin(config, stage, reuse_complete=False):
    import torch
    import transformers
    dataset = Path(config["dataset"])
    dataset_manifest = json.loads(dataset.with_suffix(".manifest.json").read_text())
    if hashlib.sha256(dataset.read_bytes()).hexdigest() != dataset_manifest["sha256"]:
        raise ValueError("dataset hash mismatch")
    if config.get('generation') and dataset_manifest['generation_config_hash'] != digest(config['generation']):
        raise ValueError('run generation configuration does not match dataset manifest')
    identity = {"config": config, "config_hash": digest(config), "code": code_identity(),
                "dataset_manifest": dataset_manifest, "stage": stage,
                "environment": {"python": sys.version, "torch": torch.__version__,
                                "transformers": transformers.__version__, "platform": platform.platform(),
                                "backend": config.get('execution_backend', "transformers, eager attention"), "sampling": "greedy, do_sample=False"},
                "model_revision": config["model_revision"], "tokenizer_revision": config["tokenizer_revision"]}
    out = Path(config["run_dir"]) / stage
    out.mkdir(parents=True, exist_ok=True)
    path = out / "manifest.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if previous["identity"] != identity or previous['identity_hash'] != digest(identity):
            raise ValueError("resume identity differs (code/config/data/environment); use a new run directory")
        if reuse_complete and previous['status'] == 'complete':
            # Completed artifacts are read-only: no attempt, lease or timestamp change.
            return out, previous
        manifest = previous
    else:
        manifest = {"identity": identity, "identity_hash": digest(identity), "started_utc": datetime.now(timezone.utc).isoformat(),
                    "host": platform.node(), "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                    "artifact_dir": str(out.resolve()), "status": "started", "attempts": []}
    manifest['status'] = 'started'
    manifest["attempts"].append({"started_utc": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                                  "slurm_job_id": os.environ.get("SLURM_JOB_ID")})
    from .budget import reserve
    manifest["budget_lease"] = reserve(config, stage)
    manifest['budget_seconds_available'] = None
    manifest['compute_policy'] = 'No project or stage compute cap; only scheduler-enforced allocation limits apply.'
    write_json(path, manifest)
    ACTIVE_STAGE.set((out, manifest))
    _log_stage('stage_started',out,manifest)
    return out, manifest


def finish(out, manifest, seconds, status="complete", **extra):
    from .budget import release
    release(manifest.get("budget_lease"), seconds, status)
    manifest["budget_lease"] = None
    manifest.update(status=status, finished_utc=datetime.now(timezone.utc).isoformat(), **extra)
    manifest["attempts"][-1].update(wall_seconds=seconds, status=status)
    manifest["wall_seconds_total"] = sum(a.get("wall_seconds", 0) for a in manifest["attempts"])
    write_json(out / "manifest.json", manifest)
    _log_stage('stage_finished',out,manifest)
    ACTIVE_STAGE.set(None)
