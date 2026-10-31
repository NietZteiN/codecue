"""Content-addressed source snapshots for long queued or running experiments."""
from __future__ import annotations
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from .datasets import digest, write_json

SCRIPT_NAMES = ('87_binding_preflight.py', '88_binding_pipeline.py', '89_binding_design_audit.py',
                '90_binding_vocab_check.py', '91_binding_frozen_run.py', '92_binding_progress_report.py',
                '93_binding_calibration_pipeline.py','94_binding_probe_regularization.py','95_binding_difficulty_ladder.py',
                '96_binding_program.py','97_binding_published_benchmarks.py','98_binding_published_review.py',
                '99_binding_serialization.py','100_binding_serialization_dispatch.py',
                '101_binding_experiment_status.py','102_binding_throughput.py',
                '103_binding_throughput_audit.py','104_binding_checkpoint_suite.py','105_binding_competition.py',
                '106_binding_hook_preflight.py','107_binding_state_capture.py','108_binding_discovery_readouts.py',
                '109_binding_discovery_figure.py','110_binding_value_transfer.py',
                '111_binding_value_transfer_review.py','112_binding_routing_extension.py',
                '113_binding_timing_and_copy.py','114_binding_mechanism_followup.py','115_binding_matched_probe_controls.py','116_binding_live_load.py',
                '117_binding_experiment_log.py','118_binding_log_scheduler.py','119_binding_arithmetic_readout.py',
                '120_binding_discovery_prediction.py','121_binding_confidence.py','122_binding_precision.py',
                '123_binding_replication_prep.py','124_binding_readiness.py',
                '125_binding_probe_sensitivities.py','126_binding_candidate_confidence.py',
                '127_binding_registration_readiness.py','128_binding_confidence_prediction.py',
                '129_binding_candidate_measurement.py','130_binding_confidence_review.py',
                '131_binding_candidate_prediction.py','132_binding_candidate_pipeline.py',
                '133_binding_joint_confidence.py','134_binding_representation_sensitivity.py',
                '135_binding_stress_measurement.py','136_binding_stress_prediction.py',
                '137_binding_query_selectivity.py','138_binding_query_selectivity_review.py',
                '139_binding_relationship_audit.py','140_binding_relationship_programs.py',
                '141_binding_algebraic_programs.py','142_binding_algebraic_relationship_audit.py',
                '143_binding_relationship_capture.py','144_binding_relationship_readouts.py',
                '145_binding_relationship_pipeline.py', '147_binding_relationship_followup.py',
                '148_binding_overnight_relationship_programs.py','149_binding_overnight_relationship_capture.py',
                '150_binding_overnight_relationship_readouts.py','151_binding_overnight_relationship_behavior.py',
                '152_binding_overnight_relationship_suite.py',
                '153_binding_overnight_relationship_behavior_link.py',
                '154_binding_computation_routing.py','155_binding_relationship_schedule_programs.py',
                '156_binding_schedule_capture.py','157_binding_schedule_readouts.py',
                '158_binding_schedule_score_review.py','159_binding_schedule_diversity_programs.py',
                '160_binding_diversity_capture.py','161_binding_diversity_readouts.py',
                '162_binding_diversity_identity_review.py',
                '163_binding_direct_identity_readouts.py',
                '164_binding_grammar_identity_review.py',
                '165_binding_old_value.py',
                '166_binding_old_value_overnight.py',
                '167_binding_arithmetic_graph_capture.py',
                '168_binding_arithmetic_graph_readouts.py',
                '169_binding_arithmetic_graph_behavior.py',
                '170_binding_arithmetic_graph_suite.py',
                '171_binding_arithmetic_graph_setup.py',
                '172_binding_arithmetic_graph_review.py',
                '173_binding_arithmetic_prompt_behavior.py',
                '174_binding_arithmetic_prompt_suite.py',
                '176_binding_arithmetic_probe_selection.py',
                '177_binding_arithmetic_local_capture.py',
                '178_binding_arithmetic_local_probes.py',
                '179_binding_arithmetic_local_behavior.py',
                '180_binding_arithmetic_local_suite.py',
                '181_binding_probe_improvement_setup.py',
                '185_binding_state_followup.py',
                '186_binding_state_suite.py',
                '187_binding_state_setup.py',
                '190_binding_state_diagnostics.py',
                '192_binding_numeric_exploration.py',
                '193_binding_numeric_exploration_suite.py',
                '194_binding_numeric_exploration_setup.py',
                '200_binding_numeric_geometry.py',
                '201_binding_numeric_geometry_suite.py',
                '202_binding_numeric_geometry_setup.py')


def source_files(root):
    root = Path(root)
    files = list((root / 'src/codecue').rglob('*.py'))
    files += [root / 'scripts' / name for name in SCRIPT_NAMES]
    files += [root / 'scripts/env.sh', root / 'scripts/slurm/submit.py', root / 'scripts/slurm/stamp.py']
    return sorted(files)


def hashes(root):
    root = Path(root)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files(root)}


def verify(root):
    root = Path(root)
    manifest = json.loads((root / 'frozen_manifest.json').read_text())
    # A newer working tree may capture more entrypoints than an older snapshot.
    # Verify what the isolated snapshot actually contains, not today's catalog.
    captured = list((root/'src/codecue').rglob('*.py')) + list((root/'scripts').rglob('*.py'))
    captured += [root/'scripts/env.sh']
    try:
        actual = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(captured)}
    except FileNotFoundError as exc:
        raise ValueError('frozen source checksum mismatch') from exc
    if actual != manifest['code']['source_files'] or digest(actual) != manifest['code']['source_sha256']:
        raise ValueError('frozen source checksum mismatch')
    for name, expected in manifest['config_files'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'frozen configuration changed: {name}')
    return manifest


def workspace_root(source_root):
    """Separate immutable experiment code from writable workspace artifacts."""
    source_root=Path(source_root).resolve()
    if (source_root/'frozen_manifest.json').exists():
        return Path(verify(source_root)['workspace_root']).resolve()
    return source_root


def freeze(output=None):
    from .registry import ROOT, code_identity
    identity = code_identity()
    configs = sorted((ROOT / 'configs').rglob('*.json')) + sorted((ROOT / 'configs').glob('*.yaml'))
    config_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in configs}
    snapshot_id = digest({'code': identity, 'configs': config_hashes})[:24]
    target = Path(output) if output else ROOT / 'artifacts/binding/sources' / snapshot_id
    if target.exists():
        previous = verify(target)
        if previous['code'] != identity or previous['config_files'] != config_hashes:
            raise ValueError('snapshot directory belongs to another source/config identity')
        return {'snapshot': str(target.resolve()), 'snapshot_id': snapshot_id, 'code': identity['source_sha256']}
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + '.staging')
    if staging.exists():
        raise ValueError('unfinished snapshot staging directory; inspect before retrying')
    for path in source_files(ROOT) + configs:
        relative = path.relative_to(ROOT)
        (staging / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, staging / relative)
    write_json(staging / 'frozen_manifest.json', {
        'snapshot_id': snapshot_id, 'code': identity, 'config_files': config_hashes,
        'workspace_root': str(ROOT.resolve()), 'created_utc': datetime.now(timezone.utc).isoformat(),
        'purpose': 'immutable experiment source and configurations; model weights/data remain content-verified upstream artifacts'})
    verify(staging)
    staging.rename(target)
    return {'snapshot': str(target.resolve()), 'snapshot_id': snapshot_id, 'code': identity['source_sha256']}
