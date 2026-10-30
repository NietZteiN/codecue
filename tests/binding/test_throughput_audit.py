from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from codecue.binding.datasets import digest
from codecue.binding.gpu_telemetry import gpu_selector
from codecue.binding.published_benchmarks import score
from codecue.binding.throughput import quality
from codecue.binding.throughput_audit import audit_trial


def fixture():
    task = 'cruxeval_o_direct'
    record = {'id': 'a', 'input': '2', 'output': '3'}
    row = dict(task=task, id='a', input_token_ids=[1, 2], output_token_ids=[4, 5, 6],
               raw_response='assert f(2) == 3', score=score(task, record, 'assert f(2) == 3'))
    refs = {(task, 'a'): deepcopy(row)}
    trial = dict(responses=[row], cases=1, output_tokens=3, generation_seconds=2,
                 requests_per_second=.5, output_tokens_per_second=1.5, quality=quality([row], refs),
                 prompt_token_ids_sha256=digest([[task, 'a', digest(row['input_token_ids'])]]))
    return trial, {(task, 'a'): record}, refs, {task: 10}


def test_performance_audit_recomputes_token_counts_scores_and_rates():
    trial, expected, refs, ceilings = fixture()
    assert audit_trial(trial, expected, refs, ceilings)['cases'] == 1
    trial['requests_per_second'] = 100
    with pytest.raises(ValueError, match='metrics differ'):
        audit_trial(trial, expected, refs, ceilings)


@pytest.mark.parametrize('change,reason', [
    ('prompt', 'prompt differs'), ('score', 'scoring differs'),
    ('coverage', 'coverage differs'), ('ceiling', 'ceiling exceeded'),
])
def test_audit_rejects_inference_contract_corruption(change, reason):
    trial, expected, refs, ceilings = fixture()
    if change == 'prompt':trial['responses'][0]['input_token_ids'] = [9]
    elif change == 'score':trial['responses'][0]['score']['correct'] = False
    elif change == 'coverage':trial['responses'] *= 2
    else:ceilings['cruxeval_o_direct'] = 2
    with pytest.raises(ValueError, match=reason):
        audit_trial(trial, expected, refs, ceilings)


def test_gpu_selector_uses_uuid_or_global_slurm_id_not_cuda_local_index():
    assert gpu_selector('GPU-actual', '3') == 'GPU-actual'
    assert gpu_selector('01234567-0123-0123-0123-012345678901', '3').startswith('GPU-')
    assert gpu_selector(None, '3') == '3'
    assert gpu_selector(None, None) is None


def test_gpu_worker_entrypoint_is_safe_to_import_during_python_spawn():
    path = Path(__file__).resolve().parents[2] / 'scripts/102_binding_throughput.py'
    spec = importlib.util.spec_from_file_location('worker_import_only', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.main)  # Importing must not parse pytest args or load a model.
