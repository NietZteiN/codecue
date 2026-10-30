from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import relationship_capture as capture


class Tokenizer:
    chat_template = 'test-native-chat'

    def apply_chat_template(self, messages, **kwargs):
        assert kwargs == dict(tokenize=False, add_generation_prompt=True)
        return '<user>' + messages[0]['content'] + '</user><assistant>'

    def __call__(self, prompt, **kwargs):
        return {'input_ids': [ord(c) for c in prompt], 'offset_mapping': [(i, i + 1) for i in range(len(prompt))]}

    def decode(self, tokens, **kwargs): return ''.join(map(chr, tokens))


@pytest.fixture
def config(tmp_path):
    return dict(evaluation_role=capture.ROLE, dataset=str(tmp_path/'sources.jsonl'),
                dataset_sha256=capture.DATASET_SHA256, run_dir=str(tmp_path/'capture'), batch_size=2)


def row(identity='row', parent='v1'):
    source = 'v0 = 1\nv1 = 2\nv2 = 2\nv3 = 3\nv0 = '+parent+'\nv1 = v0\nv2 = v1\nv3 = v2\nv0'
    return dict(id=identity, base_id='base', component_id='component', cluster_id='component', template_id='component',
        split='train', condition='neutral', lexical_realization=0, source=source, canonical_source=source,
        rename_map={f'v{i}': f'v{i}' for i in range(4)}, variable_slots={f'v{i}': i for i in range(4)},
        evaluation_role='discovery_algebraic_relationship_routing_v1', family='algebraic_copy_routing',
        control_kind='primary', query_role='v0', query_count=1, targets={'numeric_stratum': 'equal_pair'})


def test_layout_preserves_exact_prefixes_and_omits_oracle_values(config):
    original = row(); original.update(expected_answer=2, execution_trace=['oracle'])
    case = capture.layout_case(Tokenizer(), original, config, 0)
    capture._case_check(case, original, config, 0)
    assert case['sites'] == list(capture.SITES) and len(case['positions']) == 9
    assert case['visible_prefixes'][0].endswith('v0 = 1')
    assert 'v1 = 2' not in case['visible_prefixes'][0]
    assert case['visible_prefixes'][-1] == case['prompt']
    assert not {'expected_answer', 'execution_trace', 'targets'} & set(case['record'])


def test_layout_permits_trailing_whitespace_but_rejects_next_code(config):
    class Extended(Tokenizer):
        def __init__(self, code): self.code = code

        def __call__(self, prompt, **kwargs):
            out = super().__call__(prompt, **kwargs)
            end = prompt.index('v0 = 1') + len('v0 = 1')
            stop = end + (2 if self.code else 1)
            out['input_ids'] = [ord(c) for c in prompt[:end-1]] + [9999] + [ord(c) for c in prompt[stop:]]
            out['offset_mapping'] = [(i, i+1) for i in range(end-1)] + [(end-1, stop)] + [(i, i+1) for i in range(stop, len(prompt))]
            self.segment = prompt[end-1:stop]
            return out

        def decode(self, tokens, **kwargs):
            return ''.join(self.segment if token == 9999 else chr(token) for token in tokens)
    assert capture.layout_case(Extended(False), row(), config, 0)['visible_prefixes'][0].endswith('1\n')
    with pytest.raises(ValueError, match='later code'): capture.layout_case(Extended(True), row(), config, 0)


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final'), ('dataset_sha256', 'a'*64),
    ('batch_size', True), ('batch_size', 0), ('layers', [8,16,24]), ('dtype', 'float32'), ('extra', 1)])
def test_bad_config_rejected_without_tokenizer_or_model(config, field, value, monkeypatch):
    config[field] = value
    monkeypatch.setattr(capture, '_tokenizer', lambda config: pytest.fail('loaded tokenizer'))
    with pytest.raises(ValueError): capture.prepare(config)


def test_slurm_and_frozen_source_guard_precede_loads(config, monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID', raising=False)
    with pytest.raises(ValueError, match='SLURM'): capture.prepare(config)
    with pytest.raises(ValueError, match='SLURM'): capture.run(config)
    monkeypatch.setenv('SLURM_JOB_ID', 'unit')
    with pytest.raises(ValueError, match='immutable source snapshot'): capture.prepare(config)


def test_prefix_tolerance_and_array_finiteness_contract(config):
    cases = [capture.layout_case(Tokenizer(), row('a'), config, 0), capture.layout_case(Tokenizer(), row('b','v2'), config, 1)]
    features = np.zeros((2,9,4,capture.HIDDEN_SIZE), dtype=np.float32)
    checks, maximum = capture.validate_chunk(features, cases)
    assert checks >= 4 and maximum == 0
    features[1,0,0,0] = 0.5*capture.ATOL
    assert capture.validate_chunk(features, cases)[1] < capture.ATOL
    features[1,0,0,0] = 2*capture.ATOL
    with pytest.raises(ValueError, match='causal prefixes'): capture.validate_chunk(features, cases)
    features[1,0,0,0] = np.nan
    with pytest.raises(ValueError, match='finiteness'): capture.validate_chunk(features, cases)
    with pytest.raises(ValueError, match='dtype'): capture.validate_chunk(np.zeros(features.shape), cases)


def test_different_padding_geometry_is_diagnostic_only(config):
    other = row('b'); other['source'] = other['source'].replace('v3 = v2', 'v3 = v2  ')
    cases = [capture.layout_case(Tokenizer(), row('a'), config, 0), capture.layout_case(Tokenizer(), other, config, 1)]
    capture._batch_geometry(cases, assign=True)
    features = np.zeros((2,9,4,capture.HIDDEN_SIZE),np.float32)
    features[1] = 1
    assert capture.validate_chunk(features,cases)[0] == 0
    assert capture._padding_diagnostics(features,cases)[0] > 0
    assert capture._padding_diagnostics(features,cases)[1] == 1


def test_forward_explicit_left_padding_positions_and_raw_layer_hooks(config,monkeypatch):
    import torch
    import codecue.patching
    other=row('b');other['source']=other['source'].replace('v3 = 3','v3 = -3')
    cases=[capture.layout_case(Tokenizer(),row('a'),config,0),capture.layout_case(Tokenizer(),other,config,1)]
    capture._batch_geometry(cases,assign=True)
    class Batch(dict):
        def __getattr__(self,key):return self[key]
        def to(self,device):return self
    class PaddedTokenizer:
        bad=False
        def __call__(self,prompts,**kwargs):
            width=max(map(len,prompts));ids=[];mask=[]
            for prompt in prompts:
                pad=width-len(prompt);ids.append([0]*pad+[ord(c) for c in prompt]);mask.append([0]*pad+[1]*len(prompt))
            if self.bad:mask[0][0]=1
            return Batch(input_ids=torch.tensor(ids),attention_mask=torch.tensor(mask))
    hooks={}
    class Block:
        def __init__(self,index):self.index=index
        def register_forward_hook(self,hook):
            hooks[self.index]=hook
            index=self.index
            class Handle:
                def remove(self):hooks.pop(index,None)
            return Handle()
    monkeypatch.setattr(codecue.patching,'decoder_layers',lambda model:[Block(i) for i in range(32)])
    class Model:
        device='cpu'
        def model(self,**kwargs):
            positions=kwargs['position_ids'];mask=kwargs['attention_mask']
            assert kwargs['use_cache'] is False
            assert torch.equal(positions,(mask.cumsum(-1)-1).clamp_min(0))
            hidden=positions.float()[...,None].expand(-1,-1,capture.HIDDEN_SIZE)
            for layer,hook in list(hooks.items()):hook(None,None,hidden+layer)
    tokenizer=PaddedTokenizer()
    features=capture._forward(tokenizer,Model(),cases)
    for i,case in enumerate(cases):
        for site,position in enumerate(case['positions']):
            assert np.array_equal(features[i,site,:,0],np.array(capture.LAYERS)+position)
    assert not hooks
    tokenizer.bad=True
    with pytest.raises(ValueError,match='left-padded'):capture._forward(tokenizer,Model(),cases)


def test_atomic_chunk_commit_cannot_replace_existing_artifact(tmp_path):
    path=tmp_path/'chunk.npz';capture._commit_chunk(path,b'complete')
    assert path.read_bytes()==b'complete' and not list(tmp_path.glob('*.pending'))
    capture._commit_chunk(path,b'complete')
    with pytest.raises(ValueError,match='differs'):capture._commit_chunk(path,b'changed')
    assert path.read_bytes()==b'complete'


def test_chunk_temporary_symlink_cannot_overwrite_its_target(tmp_path):
    path=tmp_path/'chunk.npz';target=tmp_path/'other.txt';target.write_bytes(b'preserve')
    pending=tmp_path/'.chunk.npz.pending';pending.symlink_to(target)
    with pytest.raises(FileExistsError):capture._commit_chunk(path,b'new data')
    assert target.read_bytes()==b'preserve' and pending.is_symlink() and not path.exists()


@pytest.mark.parametrize('metadata',[False,True])
def test_dangling_output_symlink_cannot_create_an_external_target(tmp_path,metadata):
    path=tmp_path/('summary.json' if metadata else 'chunk.npz');target=tmp_path/'external.txt'
    path.symlink_to(target)
    with pytest.raises(ValueError,match='symbolic links'):
        if metadata:capture._put(path,{'complete':True})
        else:capture._commit_chunk(path,b'new data')
    assert not target.exists() and path.is_symlink()


def test_chunk_reader_checks_same_bytes_checksum_metadata_inventory_and_arrays(config, tmp_path):
    cases = [capture.layout_case(Tokenizer(), row(), config, 0)]
    features = np.zeros((1,9,4,capture.HIDDEN_SIZE), dtype=np.float32)
    def entry(**arrays):
        payload = io.BytesIO(); np.savez(payload, **arrays)
        data = payload.getvalue(); path = tmp_path/'chunk.npz'; path.write_bytes(data)
        return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest())
    metadata = np.frombuffer(json.dumps(cases).encode(),dtype=np.uint8)
    saved = entry(features=features, metadata=metadata)
    assert capture.load_chunk(saved, cases)[0].shape == features.shape
    with pytest.raises(ValueError, match='checksum'): capture.load_chunk(dict(saved,sha256='a'*64), cases)
    with pytest.raises(ValueError, match='row identity'): capture.load_chunk(saved, [])
    with pytest.raises(ValueError, match='inventory'): capture.load_chunk(entry(features=features, metadata=metadata, oracle=np.ones(1)), cases)


@pytest.fixture
def fake_run(config, monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda *args, **kwargs: None)
    monkeypatch.setenv('SLURM_JOB_ID', 'unit')
    monkeypatch.setattr(capture, 'SOURCE_ROWS', 2)
    source = dict(snapshot='/unit/source',snapshot_id='unit',source_sha256='a'*64,frozen_manifest_sha256='b'*64)
    monkeypatch.setattr(capture, '_current_source', lambda config: source)
    monkeypatch.setattr(capture, '_verify_source', lambda config, source: None)
    rows = [row('a'),row('b','v2')]
    review = dict(dataset_sha256=capture.DATASET_SHA256,source_rows=2,recipe=capture._config(config)[0])
    monkeypatch.setattr(capture, '_dataset', lambda config: (rows,review))
    monkeypatch.setattr(capture, '_tokenizer', lambda config: Tokenizer())
    monkeypatch.setattr(capture, '_models', lambda config: (Tokenizer(),object()))
    class Monitor:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def summary(self):return {'samples':0,'selector_verified':False}
    monkeypatch.setattr(capture,'_monitor',Monitor)
    monkeypatch.setattr(capture,'_runtime',lambda model:{'device_name':'unit','dtype':'torch.bfloat16'})
    monkeypatch.setattr(capture, '_forward', lambda tokenizer,model,cases: np.zeros((len(cases),9,4,capture.HIDDEN_SIZE),np.float32))
    capture.prepare(config)
    return config


def test_prefill_only_run_audit_completed_receipt_and_immutable_reuse(fake_run, monkeypatch):
    config = fake_run
    result = capture.run(config)
    assert result['complete'] and result['cases'] == 2 and result['new_model_queries'] == 2
    assert result['model_prefill_cases']==2 and result['prefill_batch_calls']==1
    assert result['generation_calls']==0 and result['generated_responses']==0 and result['model_loaded'] is True
    checked = capture.audit(config)
    assert checked['status'] == 'passed'
    complete = capture.completed_metadata(config)
    assert len(complete['cases']) == 2 and len(complete['chunks']) == 1
    monkeypatch.setattr(capture, '_models', lambda config: pytest.fail('complete capture reloaded model'))
    assert capture.run(config) == result
    assert capture.audit(config) == checked


def test_failed_capture_resumes_saved_chunks_and_preserves_failure_attempt(fake_run, monkeypatch):
    config = fake_run
    original = capture._forward
    monkeypatch.setattr(capture,'_forward',lambda *args: (_ for _ in ()).throw(RuntimeError('unit failure')))
    with pytest.raises(RuntimeError,match='unit failure'):capture.run(config)
    manifest = json.loads((Path(config['run_dir'])/'manifest.json').read_text())
    assert manifest['status']=='failed' and manifest['attempts'][0]['status']=='failed'
    monkeypatch.setattr(capture,'_forward',original)
    capture.run(config);capture.audit(config)
    manifest = json.loads((Path(config['run_dir'])/'manifest.json').read_text())
    assert [attempt['status'] for attempt in manifest['attempts']]==['failed','complete']


@pytest.mark.parametrize('interruption',[RuntimeError,KeyboardInterrupt])
def test_committed_chunk_survives_process_interruption_without_more_model_calls(fake_run,monkeypatch,interruption):
    config=fake_run;write=capture.write_json
    def stop_after_commit(path,value):
        if Path(path).name=='progress.json':raise interruption('after committed chunk')
        return write(path,value)
    monkeypatch.setattr(capture,'write_json',stop_after_commit)
    with pytest.raises(interruption):capture.run(config)
    folder=Path(config['run_dir']);previous=json.loads((folder/'manifest.json').read_text())
    assert previous['chunks'][0]['sha256']==capture._sha(folder/'chunks'/'000000.npz')
    assert previous['attempts'][0]['model_loaded'] is True
    chunk=(folder/'chunks'/'000000.npz').read_bytes()
    monkeypatch.setattr(capture,'write_json',write)
    monkeypatch.setattr(capture,'_models',lambda config:pytest.fail('reloaded model for committed cases'))
    result=capture.run(config);capture.audit(config)
    assert result['new_model_queries']==2 and result['prefill_batch_calls']==1
    assert result['model_loaded'] is True and (folder/'chunks'/'000000.npz').read_bytes()==chunk
    assert result['collection_attempts'][0]['status']==('interrupted' if interruption is KeyboardInterrupt else 'failed')
    assert result['collection_attempts'][1]['prefill_cases_attempted']==0


def test_resume_rejects_shape_preserving_corruption_without_repinning_or_model_load(fake_run,monkeypatch):
    config=fake_run;write=capture.write_json
    def stop_after_commit(path,value):
        if Path(path).name=='progress.json':raise RuntimeError('after committed chunk')
        return write(path,value)
    monkeypatch.setattr(capture,'write_json',stop_after_commit)
    with pytest.raises(RuntimeError):capture.run(config)
    folder=Path(config['run_dir']);path=folder/'chunks'/'000000.npz'
    pin=json.loads((folder/'manifest.json').read_text())['chunks'][0]['sha256']
    with np.load(path,allow_pickle=False) as saved:
        features=saved['features']+1;metadata=saved['metadata']
    with path.open('wb') as stream:np.savez(stream,features=features,metadata=metadata)
    assert capture._sha(path)!=pin
    monkeypatch.setattr(capture,'write_json',write)
    monkeypatch.setattr(capture,'_models',lambda config:pytest.fail('loaded model before validating saved chunk'))
    with pytest.raises(ValueError,match='checksum differs'):capture.run(config)
    assert json.loads((folder/'manifest.json').read_text())['chunks'][0]['sha256']==pin


def test_unowned_partial_chunk_cannot_be_adopted_as_a_new_capture(fake_run,monkeypatch):
    folder=Path(fake_run['run_dir']);(folder/'chunks').mkdir()
    (folder/'chunks'/'000000.npz').write_bytes(b'unowned')
    monkeypatch.setattr(capture,'_models',lambda config:pytest.fail('loaded model before checksum inventory'))
    with pytest.raises(ValueError,match='durable checksum pin'):capture.run(fake_run)


def test_resume_recovers_summary_commit_without_rewriting_results_or_replaying_model(fake_run,monkeypatch):
    config=fake_run;write=capture.write_json;failed=False
    def stop_final_manifest(path,value):
        nonlocal failed
        if Path(path).name=='manifest.json' and value.get('status')=='complete' and not failed:
            failed=True;raise RuntimeError('final manifest unavailable')
        return write(path,value)
    monkeypatch.setattr(capture,'write_json',stop_final_manifest)
    with pytest.raises(RuntimeError,match='final manifest unavailable'):capture.run(config)
    folder=Path(config['run_dir']);summary=(folder/'summary.json').read_bytes()
    assert json.loads((folder/'manifest.json').read_text())['status']=='finalizing'
    monkeypatch.setattr(capture,'write_json',write)
    monkeypatch.setattr(capture,'_models',lambda config:pytest.fail('model reran during metadata recovery'))
    result=capture.run(config);capture.audit(config)
    assert result==json.loads(summary) and (folder/'summary.json').read_bytes()==summary
    manifest=json.loads((folder/'manifest.json').read_text())
    assert manifest['status']=='complete' and len(manifest['attempts'])==1
    assert manifest['finalization_errors']==['RuntimeError: final manifest unavailable']


def test_failed_atomic_summary_publication_leaves_no_partial_summary_and_can_resume(fake_run,monkeypatch):
    config=fake_run;link=capture.os.link
    def fail_summary(source,destination):
        if Path(destination).name=='summary.json':raise OSError('summary publication interrupted')
        return link(source,destination)
    monkeypatch.setattr(capture.os,'link',fail_summary)
    with pytest.raises(OSError,match='summary publication interrupted'):capture.run(config)
    folder=Path(config['run_dir'])
    assert not (folder/'summary.json').exists() and not list(folder.glob('.summary.json.*.pending'))
    monkeypatch.setattr(capture.os,'link',link)
    monkeypatch.setattr(capture,'_models',lambda config:pytest.fail('model reran after all chunks committed'))
    result=capture.run(config);capture.audit(config)
    assert result['new_model_queries']==2 and result['prefill_batch_calls']==1


def test_interrupted_prepared_publication_leaves_no_partial_destination_and_retry_is_exact(fake_run,monkeypatch):
    config=fake_run;folder=Path(config['run_dir']);path=folder/'prepared_cases.jsonl'
    original=path.read_bytes();path.unlink();link=capture.os.link
    def interrupt(source,destination):
        if Path(destination)==path:raise OSError('prepared publication interrupted')
        return link(source,destination)
    monkeypatch.setattr(capture.os,'link',interrupt)
    with pytest.raises(OSError,match='prepared publication interrupted'):capture.prepare(config)
    assert not path.exists() and not list(folder.glob('.prepared_cases.jsonl.*.pending'))
    monkeypatch.setattr(capture.os,'link',link)
    capture.prepare(config)
    assert path.read_bytes()==original
    assert len(capture.inputs(config)[1])==2


def test_prepared_publication_cannot_follow_dangling_output_symlink(fake_run):
    config=fake_run;folder=Path(config['run_dir']);path=folder/'prepared_cases.jsonl'
    path.unlink();external=folder/'external.txt';path.symlink_to(external)
    with pytest.raises(ValueError,match='symbolic links'):capture.prepare(config)
    assert path.is_symlink() and not external.exists()


def test_completed_reader_checks_source_guards_before_any_array_read(fake_run,monkeypatch):
    config=fake_run;capture.run(config);capture.audit(config)
    monkeypatch.setattr(capture,'_verify_source',lambda *args:(_ for _ in ()).throw(ValueError('source changed')))
    monkeypatch.setattr(capture.np,'load',lambda *args,**kwargs:pytest.fail('array opened before provenance guard'))
    with pytest.raises(ValueError,match='source changed'):capture.completed_metadata(config)


@pytest.mark.parametrize('change',['prepared','receipt_inventory','chunk_path','chunk_metadata'])
def test_completed_metadata_and_array_reader_reject_tampering_before_fits(fake_run,change):
    config = fake_run;capture.run(config);capture.audit(config)
    folder=Path(config['run_dir'])
    if change=='prepared':
        with (folder/'prepared_cases.jsonl').open('a') as f:f.write('\n')
    elif change=='receipt_inventory':
        path=folder/'completion_manifest_v1.json';value=json.loads(path.read_text());value['metadata'].pop('audit.json');path.write_text(json.dumps(value))
    elif change=='chunk_path':
        path=folder/'manifest.json';value=json.loads(path.read_text());value['chunks'][0]['path']=str(folder/'other.npz');path.write_text(json.dumps(value))
    else:
        (folder/'chunks'/'unexpected.npz').write_bytes(b'invalid')
    with pytest.raises(ValueError):capture.completed_metadata(config)
