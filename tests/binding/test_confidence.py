"""Software-only checks: no pretrained tokenizer, model, or target outcomes."""
from copy import deepcopy
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from codecue.binding import confidence
from codecue.binding.competition import ROLE as SOURCE_ROLE
from codecue.binding.datasets import digest, read_jsonl
from codecue.binding.published_benchmarks import sha


class OracleBomb(dict):
    """A source record whose answer/outcome fields must never be consulted."""
    forbidden = {'expected_answer', 'execution_trace', 'prediction', 'correct',
                 'raw_response', 'score', 'target_label'}

    def __getitem__(self, key):
        if key in self.forbidden:
            raise AssertionError('confidence opened an oracle/outcome field: ' + key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in self.forbidden:
            raise AssertionError('confidence opened an oracle/outcome field: ' + key)
        return super().get(key, default)


def source_case(index, ids, *, condition='informative', family='versions'):
    record = OracleBomb(id=f'case-{index}', base_id=f'base-{index}', template_id='template',
        split='train' if index % 2 else 'development', condition=condition,
        lexical_realization='descriptive', available_bindings=2, updates=1,
        tail_placement='after', query_role='current', evaluation_role=SOURCE_ROLE,
        family=family, expected_answer=object(), execution_trace=object(), raw_response=object())
    prompt = f'exact prompt {index}\n'
    return dict(id=record['id'], kind='competition', record=record, prompt=prompt,
                prompt_sha256=digest(prompt), input_token_ids=ids)


class Batch(dict):
    def __getattr__(self, name):
        return self[name]

    def to(self, device):
        return Batch({key: value.to(device) for key, value in self.items()})


class FakeTokenizer:
    def __init__(self, cases):
        self.lookup = {item['prompt']: item['input_token_ids'] for item in cases}
        self.seen = []

    def __call__(self, prompts, *, add_special_tokens, padding, max_length, return_tensors):
        assert add_special_tokens is False and padding == 'max_length' and return_tensors == 'pt'
        self.seen.extend(prompts)
        ids = [self.lookup[prompt] for prompt in prompts]
        assert all(len(item) <= max_length for item in ids)
        return Batch(input_ids=torch.tensor([[0] * (max_length-len(item)) + item for item in ids]),
            attention_mask=torch.tensor([[0] * (max_length-len(item)) + [1] * len(item) for item in ids]))


class FakeModel:
    device = torch.device('cpu')

    def __init__(self, fail_at=None):
        self.calls = []
        self.backend = None
        self.fail_at = fail_at

    def set_attn_implementation(self, backend):
        self.backend = backend

    def generate(self, *args, **kwargs):
        raise AssertionError('confidence must never generate')

    def __call__(self, *, input_ids, attention_mask, position_ids, use_cache, logits_to_keep):
        assert not torch.is_grad_enabled() and use_cache is False and logits_to_keep == 1
        self.calls.append(input_ids.clone())
        if len(self.calls) == self.fail_at:
            raise RuntimeError('fake interrupted model call')
        rows = []
        for ids, mask, positions in zip(input_ids, attention_mask, position_ids):
            active = mask.bool()
            assert positions[active].tolist() == list(range(int(mask.sum())))
            assert torch.all(positions[~active] == 1)
            value = float(ids[active].sum()) / 10
            rows.append([value, -value, 0., .5])
        return SimpleNamespace(logits=torch.tensor(rows)[:, None, :])


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    from codecue.binding import discovery_features, experiment_log

    monkeypatch.setattr(experiment_log, 'note_artifact', lambda *args, **kwargs: None)
    monkeypatch.setattr(confidence, 'code_identity', lambda: {'source_sha256': 'software-v1'})
    source = dict(model='fake/checkpoint', model_revision='a'*40, tokenizer_revision='b'*40,
        dtype='float32', protocol='short_answer_chat_v1', tokenization_mode='native',
        eos_token_ids=[3], dataset=str(tmp_path/'source-bank.jsonl'), device='cpu')
    source_path = tmp_path/'source-config.json'
    source_path.write_text(json.dumps(source, sort_keys=True))
    config = dict(source, source_config=str(source_path), source_config_sha256=sha(source_path),
        prepared_cases=str(tmp_path/'prepared.jsonl'), preflight_result=str(tmp_path/'preparation.json'),
        run_dir=str(tmp_path/'run'), batch_size=1, attention_backend='sdpa')
    cases = [source_case(1, [1]), source_case(2, [1, 2, 3]), source_case(3, [2, 3]),
             source_case(4, [4], condition='neutral'), source_case(5, [5], family='ownership')]
    calls = []

    def source_inputs(checked):
        calls.append(checked)
        return source, {'identity_hash': 'original-completed-identity'}, cases, {'source': 'metadata-only'}

    monkeypatch.setattr(discovery_features, '_source_inputs', source_inputs)
    confidence.prepare(config)
    return SimpleNamespace(config=config, source=source, source_cases=cases, source_calls=calls)


def fake_registry(monkeypatch):
    """Exercise collector retries without importing HF or a real GPU ledger."""
    from codecue.binding import registry

    def begin(config, stage, reuse_complete=False):
        out = Path(config['run_dir'])/stage
        out.mkdir(parents=True, exist_ok=True)
        identity = dict(config=config, code={'source_sha256': 'software-v1'}, stage=stage)
        path = out/'manifest.json'
        if path.exists():
            manifest = json.loads(path.read_text())
            if manifest['identity'] != identity or manifest['identity_hash'] != digest(identity):
                raise ValueError('fake registry identity differs')
            if reuse_complete and manifest['status'] == 'complete':
                return out, manifest
        else:
            manifest = dict(identity=identity, identity_hash=digest(identity), attempts=[])
        manifest['status'] = 'started'
        manifest['attempts'].append({'number': len(manifest['attempts']) + 1})
        path.write_text(json.dumps(manifest))
        registry.ACTIVE_STAGE.set((out, manifest))
        return out, manifest

    def finish(out, manifest, seconds, status='complete', **extra):
        manifest.update(status=status, **extra)
        (out/'manifest.json').write_text(json.dumps(manifest))
        registry.ACTIVE_STAGE.set(None)

    monkeypatch.setattr(registry, 'begin', begin)
    monkeypatch.setattr(registry, 'finish', finish)


def fake_loader(monkeypatch, cases, model=None):
    from codecue.binding import model_adapter
    tokenizer = FakeTokenizer(cases)
    model = model or FakeModel()
    calls = []

    def load(config):
        calls.append(config)
        return tokenizer, model

    monkeypatch.setattr(model_adapter, 'load', load)
    return tokenizer, model, calls


def test_statistics_uniform_extreme_and_shift_invariant():
    rows = confidence.next_token_statistics(torch.zeros(2, 4, dtype=torch.bfloat16), [1, 3])
    assert rows[0] == rows[1]
    assert set(rows[0]) == set(confidence.STATISTICS)
    assert rows[0]['entropy_nats'] == pytest.approx(math.log(4))
    assert rows[0]['maximum_next_token_probability'] == .25
    assert rows[0]['top_two_logit_margin'] == 0
    assert rows[0]['eos_probability_mass'] == .5
    assert rows[0]['vocabulary_size'] == 4
    extreme = confidence.next_token_statistics(torch.tensor([[3e38, -3e38, 0.]]), [1])[0]
    assert extreme['entropy_nats'] == 0 and extreme['maximum_next_token_probability'] == 1
    assert extreme['top_two_logit_margin'] == pytest.approx(3e38)
    assert extreme['eos_probability_mass'] == 0
    logits = torch.tensor([[1., -.5, 2., 0.]])
    original = confidence.next_token_statistics(logits, [0])[0]
    shifted = confidence.next_token_statistics(logits+40, [0])[0]
    assert shifted == pytest.approx(original, abs=1e-6)
    assert confidence.next_token_statistics(logits, [])[0]['eos_probability_mass'] == 0


@pytest.mark.parametrize('logits,eos', [
    (torch.tensor([1., 2.]), []), (torch.zeros(1, 1), []), (torch.zeros(0, 2), []),
    (torch.tensor([[0., float('nan')]]), []), (torch.tensor([[0., float('inf')]]), []),
    (torch.zeros(1, 3), [1, 1]), (torch.zeros(1, 3), [3]), (torch.zeros(1, 3), [True]),
])
def test_statistics_reject_invalid_shape_nonfinite_or_eos(logits, eos):
    with pytest.raises(ValueError):
        confidence.next_token_statistics(logits, eos)


def test_preparation_is_label_free_immutable_and_exact(prepared):
    config = prepared.config
    metadata, cases = confidence.inputs(config)
    assert len(cases) == 3 and metadata['padded_width'] == 3
    assert metadata['target_outcomes_read'] is False and metadata['generated_tokens'] == 0
    assert metadata['source_sha256'] == 'software-v1'
    assert metadata['upstream_identity'] == 'original-completed-identity'
    assert [case['id'] for case in cases] == ['case-1', 'case-2', 'case-3']
    assert all(not OracleBomb.forbidden.intersection(case) for case in cases)
    assert all(case['prompt'].endswith('\n') for case in cases)
    assert cases[1]['input_token_ids'] == [1, 2, 3]
    before = Path(config['preflight_result']).read_bytes()
    confidence.prepare(config)
    assert Path(config['preflight_result']).read_bytes() == before
    Path(config['prepared_cases']).write_text('{}\n')
    with pytest.raises(ValueError, match='already differs'):
        confidence.prepare(config)


def test_hash_only_smoke_selection_does_not_use_record_order_or_oracles():
    cases = [source_case(i, [i]) for i in range(1, 20)]
    config = {'case_limit': 5, 'selection_seed': 117}
    chosen = confidence.select_cases(cases, config)
    assert chosen == confidence.select_cases(list(reversed(cases)), config)
    assert len(chosen) == 5
    assert chosen == sorted(chosen, key=lambda item: item['id'])
    with pytest.raises(ValueError, match='exceeds'):
        confidence.select_cases(cases, {'case_limit': 20})


@pytest.mark.parametrize('alter', ['role', 'split', 'case-id', 'prompt', 'input-id'])
def test_selection_rejects_bad_source_contract_before_model_use(alter):
    case = source_case(1, [1])
    if alter == 'role': case['record']['evaluation_role'] = 'final'
    elif alter == 'split': case['record']['split'] = 'test'
    elif alter == 'case-id': case['id'] = 'different'
    elif alter == 'prompt': case['prompt'] += 'rewrite'
    else: case['input_token_ids'] = [True]
    with pytest.raises(ValueError):
        confidence.select_cases([case], {})


@pytest.mark.parametrize('field,value', [
    ('evaluation_role', 'heldout'), ('model_revision', 'c'*40),
    ('source_config_sha256', 'wrong'), ('attention_backend', 'flash_attention_2'),
    ('batch_size', 0), ('case_limit', False), ('eos_token_ids', [3, 3]),
    ('run_dir', 'artifacts/binding/final/confidence'),
])
def test_source_guards_precede_any_source_input_open(prepared, field, value):
    before = len(prepared.source_calls)
    bad = dict(prepared.config, **{field: value})
    with pytest.raises(ValueError):
        confidence.prepare(bad)
    assert len(prepared.source_calls) == before


def test_exact_token_replay_left_padding_and_no_generation(prepared):
    _, cases = confidence.inputs(prepared.config)
    tokenizer, model = FakeTokenizer(cases), FakeModel()
    batch_rows = confidence.measure_batch(tokenizer, model, cases, 3, [3])
    individually = [confidence.measure_batch(tokenizer, model, [case], len(case['input_token_ids']), [3])[0]
                    for case in cases]
    assert batch_rows == individually
    assert tokenizer.seen[:3] == [case['prompt'] for case in cases]
    assert model.calls[0].tolist() == [[0, 0, 1], [1, 2, 3], [0, 2, 3]]
    assert all(not OracleBomb.forbidden.intersection(row) for row in batch_rows)
    tokenizer.lookup[cases[0]['prompt']] = [2]
    with pytest.raises(ValueError, match='tokenization differs'):
        confidence.measure_batch(tokenizer, model, cases, 3, [3])


def test_model_must_return_one_final_position_distribution(prepared):
    _, cases = confidence.inputs(prepared.config)

    class WrongShape:
        device = 'cpu'
        def __call__(self, **kwargs):
            return SimpleNamespace(logits=torch.zeros(len(cases), 3, 4))

    with pytest.raises(ValueError, match='final-position distribution'):
        confidence.measure_batch(FakeTokenizer(cases), WrongShape(), cases, 3, [3])


@pytest.mark.parametrize('field,value', [('model_revision', 'c'*40), ('source_config_sha256', 'wrong'),
    ('source_sha256', 'software-other'), ('prepared_cases_sha256', 'wrong'), ('cases', 2)])
def test_inputs_reject_preparation_identity_tampering(prepared, field, value):
    path = Path(prepared.config['preflight_result'])
    metadata = json.loads(path.read_text())
    metadata[field] = value
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError):
        confidence.inputs(prepared.config)


def test_run_resume_chunk_provenance_coverage_and_completed_reuse(prepared, monkeypatch):
    fake_registry(monkeypatch)
    config = prepared.config
    _, cases = confidence.inputs(config)
    _, first, _ = fake_loader(monkeypatch, cases, FakeModel(fail_at=2))
    with pytest.raises(RuntimeError, match='interrupted'):
        confidence.run(config)
    out = Path(config['run_dir'])/'confidence'
    first_chunk = (out/'chunks/00000000.json').read_bytes()
    assert not (out/'chunks/00000001.json').exists()
    assert json.loads((out/'manifest.json').read_text())['status'] == 'failed'
    assert len(first.calls) == 2
    _, resumed, load_calls = fake_loader(monkeypatch, cases)
    summary = confidence.run(config)
    assert resumed.backend == 'sdpa' and len(load_calls) == 1 and len(resumed.calls) == 2
    assert (out/'chunks/00000000.json').read_bytes() == first_chunk
    assert summary['evaluated'] == summary['planned'] == 3
    assert summary['resumed_cases'] == 1 and summary['measured_this_attempt'] == 2
    assert summary['generated_tokens'] == 0 and summary['target_outcomes_read'] is False
    rows = read_jsonl(out/'confidence.jsonl')
    assert [row['id'] for row in rows] == [case['id'] for case in cases]
    assert all(set(row) == confidence.ROW_FIELDS for row in rows)
    assert confidence.audit(config)['status'] == 'passed'

    from codecue.binding import model_adapter
    monkeypatch.setattr(model_adapter, 'load', lambda config: pytest.fail('complete run loaded checkpoint'))
    before = {path: path.read_bytes() for path in out.rglob('*') if path.is_file()}
    assert confidence.run(config) == summary
    assert all(path.read_bytes() == content for path, content in before.items())


def test_declared_sdpa_backend_cannot_silently_stay_eager(prepared, monkeypatch):
    fake_registry(monkeypatch)
    _, cases = confidence.inputs(prepared.config)

    class CannotSelectBackend:
        device = 'cpu'
        def generate(self, *args, **kwargs):
            pytest.fail('confidence generated')
        def __call__(self, **kwargs):
            pytest.fail('incorrect backend reached inference')

    fake_loader(monkeypatch, cases, CannotSelectBackend())
    with pytest.raises(ValueError, match='registered attention backend'):
        confidence.run(prepared.config)
    assert not list((Path(prepared.config['run_dir'])/'confidence/chunks').glob('*.json'))


@pytest.mark.parametrize('field,value', [
    ('measurement', 'other'), ('evaluation_role', 'final'), ('model', 'other/model'),
    ('model_revision', 'z'*40), ('evaluated', 2), ('target_prefill_evaluations', 2),
    ('generated_tokens', 1), ('target_outcomes_read', True), ('statistics', ['argmax_token_id']),
    ('confidence_sha256', 'wrong'), ('attention_backend', 'eager'), ('resumed_cases', -1),
])
def test_audit_rejects_scalar_summary_or_provenance_tampering(prepared, monkeypatch, field, value):
    fake_registry(monkeypatch)
    _, cases = confidence.inputs(prepared.config)
    fake_loader(monkeypatch, cases)
    confidence.run(prepared.config)
    path = Path(prepared.config['run_dir'])/'confidence/summary.json'
    summary = json.loads(path.read_text())
    summary[field] = value
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match='summary/hash/access'):
        confidence.audit(prepared.config)


def test_chunk_resume_rejects_noncontiguous_or_changed_input_identity(prepared, tmp_path):
    qa, cases = confidence.inputs(prepared.config)
    out = tmp_path/'chunks-check'
    out.mkdir()
    folder = out/'chunks'
    folder.mkdir()
    row = confidence.measure_batch(FakeTokenizer(cases), FakeModel(), cases[1:2], 3, [3])
    path = folder/'00000001.json'
    chunk = dict(config_hash=digest(prepared.config), prepared_cases_sha256=qa['prepared_cases_sha256'],
                 measurement=confidence.MEASUREMENT, start=1, rows=row)
    path.write_text(json.dumps(chunk))
    with pytest.raises(ValueError, match='contiguous'):
        confidence._chunks(prepared.config, qa, cases, out)
    path.rename(folder/'00000000.json')
    with pytest.raises(ValueError, match='input identity'):
        confidence._chunks(prepared.config, qa, cases, out)


def test_audit_rejects_wrong_runtime_backend_and_reserved_path(prepared, monkeypatch):
    fake_registry(monkeypatch)
    _, cases = confidence.inputs(prepared.config)
    fake_loader(monkeypatch, cases)
    confidence.run(prepared.config)
    path = Path(prepared.config['run_dir'])/'confidence/runtime.json'
    runtime = json.loads(path.read_text())
    runtime['attention_backend'] = 'eager'
    path.write_text(json.dumps(runtime))
    with pytest.raises(ValueError, match='runtime provenance'):
        confidence.audit(prepared.config)
    with pytest.raises(ValueError, match='reserved outcome paths'):
        confidence.audit(dict(prepared.config, run_dir='artifacts/binding/final/confidence'))


def test_row_schema_rejects_oracle_export_nonfinite_and_wrong_exact_prompt(prepared):
    _, cases = confidence.inputs(prepared.config)
    rows = confidence.measure_batch(FakeTokenizer(cases), FakeModel(), cases, 3, [3])
    for field, value in [('raw_response', '1'), ('entropy_nats', float('nan')),
                         ('maximum_next_token_probability', 1.01), ('prompt_sha256', 'wrong')]:
        bad = deepcopy(rows)
        bad[0][field] = value
        with pytest.raises(ValueError):
            confidence.validate_rows(cases, bad)
    with pytest.raises(ValueError, match='coverage'):
        confidence.validate_rows(cases, rows[:-1])


def test_duplicate_worker_is_rejected_before_registry_begin(tmp_path):
    out = tmp_path/'locked-run'
    with confidence._run_lock(out):
        with pytest.raises(RuntimeError, match='already owns'):
            with confidence._run_lock(out):
                pytest.fail('second worker acquired the run lock')
