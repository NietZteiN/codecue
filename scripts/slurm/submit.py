#!/usr/bin/env python
"""Submit one command to SLURM with the project env. Small on purpose: SLURM already does
allocation, isolation and accounting; what this adds is the env, the log path, a manifest in the
log directory (argv, git sha, submit time, job id, node) and a trap that stamps the exit code
into it, so a walltime kill is visible rather than a job silently missing from done/.

    python scripts/slurm/submit.py --name tok --partition dev -- python scripts/11_tokenizer_check.py --model llama32-3b
    python scripts/slurm/submit.py --name run --partition a30 --dependency afterok:123 -- python scripts/20_run_model.py ...
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import load_config  # noqa: E402


def workspace_root(root: Path) -> Path:
    """Keep operational logging in the workspace when submitting frozen code."""
    manifest = root / 'frozen_manifest.json'
    if manifest.exists():
        return Path(json.loads(manifest.read_text())['workspace_root']).resolve()
    return root.resolve()


def log_job(event_type: str, payload: dict, job_id: str | None = None) -> None:
    """Logging is durable when available, and never changes a scheduler result."""
    try:
        from codecue.binding.experiment_log import safe_emit_event
        safe_emit_event(event_type, root=workspace_root(ROOT), payload=payload, job_id=job_id)
    except Exception as exc:
        print(f'Experiment logging warning ({event_type}): {type(exc).__name__}: {exc}', file=sys.stderr)


TEMPLATE = """#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --partition={partition}
{gres}#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={mem}
#SBATCH --time={time}
{time_min}{begin}#SBATCH --kill-on-invalid-dep=yes
{exclude}{dependency}#SBATCH --output={log_dir}/%j_{name}.out
#SBATCH --error={log_dir}/%j_{name}.out
set -uo pipefail
source {root}/scripts/env.sh
cd {root}
MANIFEST="{log_dir}/${{SLURM_JOB_ID}}_{name}.json"
python {stamp_script} start "{manifest_src}" "$MANIFEST"
finish() {{ rc=$?; python {stamp_script} finish "$MANIFEST" "$rc"; exit $rc; }}
# a walltime kill arrives as SIGTERM; record it as 143 (the EXIT trap alone logged 0 for job 391916)
trap 'python {stamp_script} finish "$MANIFEST" 143; exit 143' TERM
trap finish EXIT
echo "# codecue job $SLURM_JOB_ID on $SLURMD_NODENAME ($SLURM_JOB_PARTITION) $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>/dev/null || echo "# no GPU"
printf '%s\\n' {argv_display}
{argv}
"""


def submit(name: str, partition: str, argv: list[str], dependency: str | None = None, time: str | None = None,
           mem: str | None = None, dry_run: bool = False, gpus: int | None = None,
           time_min: str | None = None, cpus: int | None = None, begin: str | None = None) -> str | None:
    cfg = load_config("compute.yaml")["slurm"]
    p = cfg["partitions"][partition]
    if gpus is not None and gpus < 1:
        raise ValueError('GPU count must be positive')
    if cpus is not None and (type(cpus) is not int or cpus < 1):
        raise ValueError('CPU count must be a positive integer')
    allocated_cpus = p['cpus'] if cpus is None else cpus
    gres = f'gpu:{gpus}' if gpus is not None else p.get('gres')
    flexible_min = time_min or p.get('time_min')
    log_dir = workspace_root(ROOT) / cfg["log_dir_rel"]
    log_dir.mkdir(parents=True, exist_ok=True)
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    manifest_src = log_dir / f"submit_{stamp}_{name}.json"
    argv_s = " ".join(shlex.quote(x) for x in argv)
    script = TEMPLATE.format(
        name=name, partition=partition, gres=(f"#SBATCH --gres={gres}\n" if gres else ""),
        cpus=allocated_cpus, mem=mem or p["mem"], time=time or p["time"],
        time_min=(f'#SBATCH --time-min={flexible_min}\n' if flexible_min else ''),
        begin=(f'#SBATCH --begin={begin}\n' if begin else ''),
        exclude=(f"#SBATCH --exclude={p['exclude']}\n" if p.get("exclude") else ""),
        dependency=(f"#SBATCH --dependency={dependency}\n" if dependency else ""),
        log_dir=log_dir, root=ROOT, manifest_src=manifest_src, argv=argv_s,
        stamp_script=shlex.quote(str(workspace_root(ROOT) / 'scripts/slurm/stamp.py')),
        argv_display=shlex.quote('# ' + argv_s))
    if dry_run:
        print(f"--- would submit {name} on {partition} (dep={dependency}):\n    {argv_s}")
        return None
    metadata = {"name": name, "partition": partition, "argv": argv, "git": sha,
                'gres': gres, 'cpus': allocated_cpus, 'mem': mem or p['mem'],
                'time': time or p['time'], 'time_min': flexible_min, 'begin': begin,
                'dependency': dependency, 'exclude': p.get('exclude'),
                'submitted_utc': datetime.now(timezone.utc).isoformat(),
                'submission_manifest': str(manifest_src), 'submission_script': str(log_dir / f'submit_{stamp}_{name}.sbatch')}
    manifest_src.write_text(json.dumps(metadata, indent=1))
    sfile = log_dir / f"submit_{stamp}_{name}.sbatch"
    sfile.write_text(script)
    try:
        out = subprocess.run(["sbatch", "--parsable", str(sfile)], capture_output=True, text=True)
    except OSError as exc:
        log_job('job_submission_failed', {**metadata, 'error': f'{type(exc).__name__}: {exc}'})
        raise
    if out.returncode != 0:
        log_job('job_submission_failed', {**metadata, 'exit_code': out.returncode, 'error': out.stderr.strip()})
        print(out.stderr, file=sys.stderr); raise SystemExit(out.returncode)
    jid = out.stdout.strip().split(";")[0]
    if not jid.isdigit():
        log_job('job_submission_failed', {**metadata, 'error': 'sbatch returned a nonnumeric job ID', 'stdout': out.stdout})
        raise ValueError('sbatch returned a nonnumeric job ID')
    metadata.update(job_id=jid, status='submitted')
    # The actual scheduler ID is available immediately, including queued jobs.
    temporary = manifest_src.with_suffix('.json.tmp')
    try:
        temporary.write_text(json.dumps(metadata, indent=1))
        temporary.replace(manifest_src)
    except OSError as exc:
        # sbatch already accepted the task: return its ID even if this extra
        # bookkeeping write fails, otherwise a retry could submit it twice.
        metadata['submission_manifest_update_error'] = f'{type(exc).__name__}: {exc}'
        print(f'Submission metadata warning for job {jid}: {exc}', file=sys.stderr)
    log_job('job_submitted', metadata, job_id=jid)
    print(f"submitted {name} -> job {jid} ({partition})")
    return jid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--partition", required=True)
    ap.add_argument("--dependency")
    ap.add_argument("--time")
    ap.add_argument("--mem")
    ap.add_argument('--gpus', type=int, help='Requested GPUs per node; model parallelism must match the allocation')
    ap.add_argument('--time-min', help='Allow SLURM to grant a shorter backfill allocation')
    ap.add_argument('--cpus',type=int,help='Explicit CPUs per task for this workload')
    ap.add_argument('--begin',help='Earliest SLURM start time, including relative times')
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("argv", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    argv = a.argv[1:] if a.argv and a.argv[0] == "--" else a.argv
    submit(a.name, a.partition, argv, a.dependency, a.time, a.mem, a.dry_run, a.gpus, a.time_min, a.cpus, a.begin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
