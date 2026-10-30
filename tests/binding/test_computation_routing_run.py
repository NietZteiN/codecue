from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest

from codecue.binding import computation_routing_run as study
from codecue.binding.datasets import digest


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


@pytest.fixture
def assay(tmp_path, monkeypatch):
    variants = ('plain', 'python', 'explicit')
    forms = ('literal', 'small', 'cancellation')
    questions = ('arithmetic_only', 'roots_only', 'full_root', 'full_leaf')
    programs = SimpleNamespace(ROLE=study.ROLE, INSTRUCTIONS=dict.fromkeys(variants), FORMS=forms, QUESTIONS=questions,
        validate_rows=lambda rows: rows, analysis_rows=lambda rows: [{**row, **member, 'source_id': row['id'],
        'capture_id': row['id']} for row in rows for member in row['logical_memberships']])
    monkeypatch.setattr(study, '_programs', lambda: programs)
    source = dict(snapshot='fake-frozen-source', snapshot_id='f'*24,
                  source_sha256='a'*64, frozen_manifest_sha256='b'*64)
    monkeypatch.setattr(study.base, '_current_source', lambda cfg: source)
    monkeypatch.setattr(study.base, '_verify_source', lambda cfg, saved: saved == source or (_ for _ in ()).throw(ValueError('source changed')))
    monkeypatch.setenv('SLURM_JOB_ID', '12345')
    monkeypatch.setattr(study.suite, 'configure_runtime', lambda cfg: None)
    rows = []
    for split in ('train', 'development'):
        for numeric in range(96):
            sign = -1 if (numeric//2)%2 else 1
            value = sign*(numeric+1)
            for form in forms:
                for question in questions:
                    base = split+str(numeric)
                    body = f'x = {value}\ny = x # {split} {form}'
                    program_source = body+'\n'+('y' if question=='full_leaf' else 'x')
                    if question not in ('full_root','full_leaf'):program_source += ' # '+question
                    row = dict(id=base+'/'+form+'/'+question, base_id=base, paired_group_id=base,
                        root_order_cluster=split+str(numeric//8), source=program_source,
                        expected_answer=value, form=form, question=question, operator='add' if numeric%2 else 'sub',
                        answer_sign=sign, queried_root_slot=numeric%4, topology='none' if question in ('arithmetic_only','roots_only') else 'depth1',
                        chain_depth=0 if question in ('arithmetic_only','roots_only') else 1,
                        split=split, evaluation_role=study.ROLE)
                    row['logical_memberships'] = [{k:v for k,v in row.items() if k!='source'}]
                    rows.append(row)
    dataset = tmp_path/'dataset.jsonl'
    dataset.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    manifest = dict(rows=len(rows), sha256=study.base._sha(dataset), evaluation_role=study.ROLE,
                    status='complete', independent_python_passed=True, generated_holdouts_opened=False)
    put(dataset.with_suffix('.manifest.json'), manifest)
    plan = tmp_path/'plan.md'; plan.write_text('Prospective fixed discovery protocol.\n')
    runtime = tmp_path/'runtime.json'; put(runtime, {})
    out = tmp_path/'run'
    cfg = dict(evaluation_role=study.ROLE, dataset=str(dataset), dataset_sha256=study.base._sha(dataset),
        dataset_manifest_sha256=study.base._sha(dataset.with_suffix('.manifest.json')),
        declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan),
        model='meta-llama/Llama-3.1-8B-Instruct', model_revision=study.MODELS['meta-llama/Llama-3.1-8B-Instruct'],
        tokenizer_revision=study.MODELS['meta-llama/Llama-3.1-8B-Instruct'], device='cuda', dtype='bfloat16',
        context_limit=4096, sections=[dict(name='computation_routing', kind='computation_routing',
        dataset=str(dataset), sha256=study.base._sha(dataset), variants=list(variants))],
        run_dir=str(out), report=str(tmp_path/'report.md'), review_artifact=str(out/'review_v1.json'),
        prepared_cases=str(out/'prepared.jsonl'), preflight_result=str(out/'preflight.json'),
        runtime_manifest=str(runtime), runtime_manifest_sha256=study.base._sha(runtime),
        cuda_home='/usr/local/cuda-12.9', engine={}, request_chunk_size=1024, eos_token_ids=[128009],
        reliability_gate=study.THRESHOLDS, bootstrap_replicates=2000, bootstrap_seed=913)

    def score(case, raw):
        pred = int(raw) if re.fullmatch(r'\s*[+-]?\d+\s*', raw, flags=re.ASCII) else None
        return dict(prediction=pred, valid=pred is not None, correct=pred == case['record']['expected_answer'])
    monkeypatch.setattr(study.suite, 'score_case', score)

    def prep(config):
        cases = []
        for variant in variants:
            for row in rows:
                prompt = variant+' '+row['source']
                cases.append(dict(section='computation_routing', kind='computation_routing', task=variant,
                    variant=variant, id=row['id'], record=row, prompt=prompt, prompt_sha256=digest(prompt),
                    input_token_ids=[1, 2], max_new_tokens=16, stop=['\n\n']))
        p = Path(config['prepared_cases']); p.parent.mkdir(parents=True, exist_ok=True)
        payload = ''.join(json.dumps(case, sort_keys=True)+'\n' for case in cases).encode()
        study.base._publish(p, payload)
        qa = dict(status='passed', config_hash=digest(config), source_sha256=source['source_sha256'],
            cases=len(cases), prepared_cases_sha256=study.base._sha(p), model_inference=False,
            generated_holdouts_opened=False)
        put(config['preflight_result'], qa)
        return qa
    monkeypatch.setattr(study.suite, 'preflight', prep)

    def response(case, raw=None):
        raw = str(case['record']['expected_answer']) if raw is None else raw
        r = {k: case[k] for k in ('section', 'task', 'id', 'input_token_ids', 'prompt_sha256')}
        r.update(record_sha256=digest(case['record']), raw_response=raw, output_token_ids=[9],
                 finish_reason='stop', score=score(case, raw))
        return r

    calls = []
    def backend(config):
        calls.append('run')
        _, cases = study.suite.prepared(config, source['source_sha256'])
        stage = Path(config['run_dir'])/'checkpoint_suite'; stage.mkdir(parents=True, exist_ok=True)
        existing = study._responses(config, cases)
        with (stage/'responses.jsonl').open('a') as stream:
            for case in cases[len(existing):]:stream.write(json.dumps(response(case))+'\n')
        observed = study._responses(config, cases)
        identity = dict(config=config, code=dict(source_sha256=source['source_sha256']))
        put(stage/'manifest.json', dict(status='complete', identity=identity, identity_hash=digest(identity),
            responses_sha256=study.base._sha(stage/'responses.jsonl'), attempts=[dict(slurm_job_id='12345', status='complete')]))
        summary = study.suite.summarize(observed, len(cases)); summary.update(gpu={}, timings=[])
        put(stage/'summary.json', summary); put(stage/'runtime.json', {})
        return summary
    monkeypatch.setattr(study.suite, 'run', backend)
    return SimpleNamespace(config=cfg, source=source, rows=rows, prep=prep, response=response,
                           backend=backend, calls=calls, variants=variants, forms=forms)


@pytest.mark.parametrize('change', ['plan', 'dataset', 'manifest', 'runtime'])
def test_metadata_refuses_changed_source_pins_before_tokenizer_access(assay, change):
    cfg = assay.config
    path = {'plan': cfg['declared_plan'], 'dataset': cfg['dataset'],
        'manifest': str(Path(cfg['dataset']).with_suffix('.manifest.json')),
        'runtime': cfg['runtime_manifest']}[change]
    Path(path).write_text(Path(path).read_text()+' ')
    with pytest.raises(ValueError, match='changed|checksum'):
        study.preflight(cfg)
    assert not Path(cfg['prepared_cases']).exists()


@pytest.mark.parametrize('change', ['role', 'thresholds', 'instructions', 'revision', 'source_collision', 'reserved_collision'])
def test_config_rejects_role_gate_variant_model_and_output_substitution(assay, change):
    cfg = deepcopy(assay.config)
    if change == 'role':cfg['evaluation_role'] = 'final_test'
    elif change == 'thresholds':cfg['reliability_gate']['minimum_accuracy'] = .1
    elif change == 'instructions':cfg['sections'][0]['variants'].pop()
    elif change == 'revision':cfg['model_revision'] = '0'*40
    elif change == 'source_collision':cfg['report'] = cfg['declared_plan']
    else:cfg['review_artifact'] = str(Path(cfg['run_dir'])/'routing_completion_v1.json')
    with pytest.raises(ValueError):study.metadata(cfg)


def test_preparation_is_sbatch_only_and_exact_completed_reuse_does_not_call_tokenizer(assay, monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID')
    with pytest.raises(ValueError, match='SLURM'):study.preflight(assay.config)
    monkeypatch.setenv('SLURM_JOB_ID', '12345')
    first = study.preflight(assay.config)
    monkeypatch.setattr(study.suite, 'preflight', lambda cfg: (_ for _ in ()).throw(AssertionError('tokenizer rerun')))
    assert study.preflight(assay.config) == first


def test_partial_preparation_reuses_identity_and_checks_immutable_prepared_bytes(assay, monkeypatch):
    original = assay.prep
    def interrupted(cfg):
        original(cfg)
        raise RuntimeError('after prepared publication')
    monkeypatch.setattr(study.suite, 'preflight', interrupted)
    with pytest.raises(RuntimeError):study.preflight(assay.config)
    monkeypatch.setattr(study.suite, 'preflight', original)
    assert study.preflight(assay.config)['status'] == 'passed'


def test_interrupted_prepared_file_write_is_preserved_and_rebuilt(assay, monkeypatch):
    def interrupted(cfg):
        Path(cfg['prepared_cases']).write_bytes(b'{"partial":')
        raise RuntimeError('during prepared file publication')
    monkeypatch.setattr(study.suite, 'preflight', interrupted)
    with pytest.raises(RuntimeError):study.preflight(assay.config)
    monkeypatch.setattr(study.suite, 'preflight', assay.prep)
    assert study.preflight(assay.config)['status'] == 'passed'
    backups = list(Path(assay.config['run_dir']).glob('prepared.jsonl.uncommitted_*.bin'))
    assert len(backups) == 1 and backups[0].read_bytes() == b'{"partial":'


def test_unregistered_preparation_and_replaced_prepared_bytes_are_refused(assay):
    cfg = assay.config
    p = Path(cfg['prepared_cases']); p.parent.mkdir(parents=True); p.write_text('unknown')
    with pytest.raises(ValueError, match='unregistered'):study.preflight(cfg)
    p.unlink(); study.preflight(cfg)
    p.write_text(p.read_text()+' ')
    with pytest.raises(ValueError, match='changed'):study.run(cfg)
    assert not assay.calls


def test_complete_mocked_run_audit_reuse_counts_warmup_separately(assay):
    cfg = assay.config; study.preflight(cfg)
    result = study.run(cfg)
    assert result['n'] == len(assay.rows)*3
    assert result['accounting']['confirmed_warmup_requests'] == 8
    assert result['accounting']['scored_model_queries_exact'] == result['n']
    assert result['new_model_queries'] == result['n']+8
    assert result['accounting']['uncertain_failed_invocation_warmup_ceiling'] == 0
    assert result['reliability_gate']['status'] == 'passed'
    assert result['generated_holdouts_opened'] is False and result['new_fits'] == 0
    assert study.audit(cfg) == result
    assert study.run(cfg) == result
    assert assay.calls == ['run']


def test_committed_corruption_is_not_repaired_but_uncommitted_tail_is_preserved(assay):
    cfg = assay.config; study.preflight(cfg)
    _, cases = study._prepared(cfg, assay.source)
    p = Path(cfg['run_dir'])/'checkpoint_suite'/'responses.jsonl'; p.parent.mkdir()
    first = json.dumps(assay.response(cases[0])).encode()+b'\n'
    p.write_bytes(first+b'{"interrupted":')
    assert len(study._responses(cfg, cases, repair=True)) == 1
    assert p.read_bytes() == first
    assert len(list(p.parent.glob('responses_interrupted_*.bin'))) == 1
    p.write_bytes(first+b'{bad}\n')
    with pytest.raises(ValueError, match='committed'):study._responses(cfg, cases, repair=True)
    assert p.read_bytes().endswith(b'{bad}\n')


def test_response_resumption_rejects_wrong_record_prompt_score_and_extra_cases(assay):
    cfg = assay.config; study.preflight(cfg)
    _, cases = study._prepared(cfg, assay.source)
    p = Path(cfg['run_dir'])/'checkpoint_suite'/'responses.jsonl'; p.parent.mkdir()
    for change in ('record_sha256', 'input_token_ids', 'score'):
        row = assay.response(cases[0]); row[change] = {'correct': False} if change == 'score' else 'wrong'
        p.write_text(json.dumps(row)+'\n')
        with pytest.raises(ValueError):study._responses(cfg, cases)
    p.write_text(''.join(json.dumps(assay.response(case))+'\n' for case in cases+[cases[0]]))
    with pytest.raises(ValueError, match='extra'):study._responses(cfg, cases)


def test_partial_finalization_recovers_without_new_backend_invocation(assay, monkeypatch):
    cfg = assay.config; study.preflight(cfg)
    original = study.base._put
    def interrupted(path, value):
        if Path(path) == Path(cfg['review_artifact']):raise RuntimeError('after report')
        return original(path, value)
    monkeypatch.setattr(study.base, '_put', interrupted)
    with pytest.raises(RuntimeError, match='after report'):study.run(cfg)
    monkeypatch.setattr(study.base, '_put', original)
    result = study.run(cfg)
    assert assay.calls == ['run'] and result['accounting']['confirmed_warmup_requests'] == 8
    assert len(study._json(Path(cfg['run_dir'])/'routing_attempts_v1.json')['attempts']) == 1


def test_completed_stage_without_wrapper_history_is_not_adopted(assay):
    cfg = assay.config; study.preflight(cfg); assay.backend(cfg)
    with pytest.raises(ValueError, match='no registered'):study.run(cfg)


def test_saved_response_prefix_without_backend_source_identity_is_not_adopted(assay):
    cfg = assay.config; study.preflight(cfg)
    _, cases = study._prepared(cfg, assay.source)
    p = Path(cfg['run_dir'])/'checkpoint_suite'/'responses.jsonl'; p.parent.mkdir()
    p.write_text(json.dumps(assay.response(cases[0]))+'\n')
    with pytest.raises(ValueError, match='no backend source identity'):study.run(cfg)
    assert not assay.calls


def test_missing_form_or_instruction_cannot_disappear_from_review(assay):
    cfg = assay.config; study.preflight(cfg)
    _, cases = study._prepared(cfg, assay.source)
    for subset in (cases[:-1], [c for c in cases if c['variant'] != assay.variants[0]]):
        with pytest.raises(ValueError, match='complete'):study.summarize([(c, assay.response(c)) for c in subset], cfg)


def test_failed_instruction_does_not_select_alternative_or_hide_invalid_answers(assay):
    cfg = assay.config; study.preflight(cfg)
    _, cases = study._prepared(cfg, assay.source)
    records = [(c, assay.response(c, 'Answer: 7') if c['variant'] == assay.variants[0] else assay.response(c)) for c in cases]
    result = study.summarize(records, cfg)
    gates = result['reliability_gate']['instructions']
    assert gates[assay.variants[0]]['status'] == 'failed'
    assert all(gates[v]['status'] == 'passed' for v in assay.variants[1:])
    assert result['reliability_gate']['status'] == 'failed'
    assert result['invalid'] == len(assay.rows)
    assert len(result['gate_cells']) == len(assay.forms)*3*4*2*2*2
    assert all('wilson_95' not in c for c in result['gate_cells'])


def test_failed_backend_prefix_resumes_with_explicit_query_uncertainty(assay, monkeypatch):
    cfg = assay.config; study.preflight(cfg)
    def failed(config):
        _, cases = study._prepared(config, assay.source)
        stage = Path(config['run_dir'])/'checkpoint_suite'; stage.mkdir()
        identity = dict(config=config, code=dict(source_sha256=assay.source['source_sha256']))
        put(stage/'manifest.json', dict(status='failed', identity=identity, identity_hash=digest(identity)))
        (stage/'responses.jsonl').write_text(''.join(json.dumps(assay.response(c))+'\n' for c in cases[:5]))
        raise RuntimeError('interrupted generation')
    monkeypatch.setattr(study.suite, 'run', failed)
    with pytest.raises(RuntimeError):study.run(cfg)
    monkeypatch.setattr(study.suite, 'run', assay.backend)
    result = study.run(cfg)
    cost = result['accounting']
    assert cost['scored_model_queries_exact'] is None
    assert cost['scored_model_queries_lower_bound'] == result['n']
    assert cost['scored_model_queries_upper_bound'] == 2*result['n']-5
    assert cost['confirmed_warmup_requests'] == 8
    assert cost['uncertain_failed_invocation_warmup_ceiling'] == 8
    assert result['new_model_queries'] is None
    assert result['new_model_queries_lower_bound'] == result['n']+8
    assert result['new_model_queries_upper_bound'] == 2*result['n']-5+16


def test_backend_complete_before_wrapper_journal_commit_recovers_without_generation(assay, monkeypatch):
    cfg = assay.config; study.preflight(cfg)
    original = study.durable._journal
    calls = []
    def interrupted(path, value):
        calls.append(1)
        if len(calls) == 2:raise KeyboardInterrupt('after backend completion')
        original(path, value)
    monkeypatch.setattr(study.durable, '_journal', interrupted)
    with pytest.raises(KeyboardInterrupt):study.run(cfg)
    monkeypatch.setattr(study.durable, '_journal', original)
    result = study.run(cfg)
    assert assay.calls == ['run']
    assert result['accounting']['confirmed_warmup_requests'] == 8


def test_real_source_factorial_maps_unique_scores_to_all_views_and_root_cluster_pairs(assay, monkeypatch):
    """Exercise the actual builder/analysis interface without tokenizer or inference."""
    from codecue.binding import computation_routing_programs as programs
    monkeypatch.setattr(study, '_programs', lambda: programs)
    rows = programs.make_rows(dict(evaluation_role=programs.ROLE, numeric_seeds=[401, 503, 607]))
    cfg = assay.config
    data = Path(cfg['dataset']); data.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    cfg['dataset_sha256'] = study.base._sha(data)
    manifest = data.with_suffix('.manifest.json')
    put(manifest, dict(status='complete', independent_python_passed=True, evaluation_role=programs.ROLE,
        sha256=cfg['dataset_sha256'], rows=len(rows), generated_holdouts_opened=False))
    cfg['dataset_manifest_sha256'] = study.base._sha(manifest)
    cfg['sections'][0].update(sha256=cfg['dataset_sha256'], variants=list(programs.INSTRUCTIONS))
    records = []
    for variant in programs.INSTRUCTIONS:
        for row in rows:
            case = dict(kind='computation_routing', section='computation_routing', task=variant,
                variant=variant, id=row['id'], record=row, input_token_ids=[1, 2],
                prompt_sha256=digest(variant+row['source']), max_new_tokens=16)
            records.append((case, assay.response(case)))
    result = study.summarize(records, cfg)
    assert result['n'] == 20100 and result['unique_sources'] == 6700
    assert result['logical_source_views'] == 6912 and result['logical_responses'] == 20736
    assert len(result['gate_cells']) == 288 and len(result['cells']) == 2304
    assert len(result['contrasts']) == 324 and sum(c['primary'] for c in result['contrasts']) == 108
    assert all(c['paired_groups'] == 12 and c['inference_scope'] == 'primary numeric development'
               for c in result['contrasts'] if c['primary'])
    assert result['source_reuse']['cross_split_literal_isolated_controls'] == 68
    assert result['reliability_gate']['status'] == 'passed'
    assert all(c['mean'] == 0 for c in result['contrasts'])
