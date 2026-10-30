from copy import deepcopy

import pytest

from codecue.binding.backend_comparison import compare
from codecue.binding.datasets import digest


def fixture():
    identity = {
        'config': dict(model='checkpoint', model_revision='a'*40, tokenizer_revision='a'*40,
                       protocol='short_answer_prefill_v2', max_new_tokens=12, device='cpu', dtype='float32'),
        'stage': 'interface_diagnostics', 'dataset_manifest': {'sha256': 'dataset'},
        'code': {'source_files': {'src/codecue/binding/model_adapter.py': 'adapter',
                                  'src/codecue/models.py': 'generation'}}}
    manifest = dict(identity=identity, identity_hash=digest(identity), status='complete',
                    samples_completed=4, samples_planned=4)
    rows = [dict(id='literal', split='train', kind='primitive', source='v0 = 7\nv0',
                 expected_answer=7, input_token_ids=[1, 7], raw_response='7', prediction=7, correct=True),
            dict(id='subtract', split='train', kind='primitive', source='v0 = 9 - 4\nv0',
                 expected_answer=5, input_token_ids=[1, 9, 4], raw_response='-5', prediction=-5, correct=False)]
    result = dict(complete=True, protocol='short_answer_prefill_v2', heldout_outcomes_opened=False,
                  responses_by_batch_size={'1': deepcopy(rows), '4': deepcopy(rows)})
    return {'CPU': (manifest, result), 'GPU': (deepcopy(manifest), deepcopy(result))}


def test_backend_comparison_aligns_ids_and_keeps_invalid_changes_separate():
    runs = fixture()
    result = runs['GPU'][1]
    result['responses_by_batch_size']['4'].reverse()
    row = result['responses_by_batch_size']['4'][0]
    row.update(raw_response='\n\n', prediction=None, correct=False)
    compared = compare(runs)
    assert len(compared['comparisons']) == 4
    batch4 = compared['comparisons'][1]
    assert batch4['raw_matches'] == batch4['prediction_matches'] == 1
    assert batch4['shared_primitive_failures'] == ['subtract']
    assert compared['runs']['GPU']['batches']['4']['invalid'] == 1
    assert batch4['differences'][0]['right_prediction'] is None


@pytest.mark.parametrize('kind', ['tokens', 'test', 'score', 'oracle', 'duplicate', 'count', 'identity', 'source', 'protocol'])
def test_backend_comparison_rejects_incompatible_or_corrupted_inputs(kind):
    runs = fixture()
    manifest, result = runs['GPU']
    row = result['responses_by_batch_size']['4'][0]
    if kind == 'tokens':
        row['input_token_ids'] = [1, 99]
    elif kind == 'test':
        row['split'] = 'test'
    elif kind == 'score':
        row['correct'] = False
    elif kind == 'oracle':
        row['expected_answer'] = 8
        row['correct'] = False
    elif kind == 'duplicate':
        result['responses_by_batch_size']['4'].append(deepcopy(row))
    elif kind == 'count':
        manifest['samples_completed'] = 3
    elif kind == 'identity':
        manifest['identity_hash'] = 'changed'
    elif kind == 'source':
        manifest['identity']['code']['source_files']['src/codecue/models.py'] = 'changed'
        manifest['identity_hash'] = digest(manifest['identity'])
    elif kind == 'protocol':
        manifest['identity']['config']['max_new_tokens'] = 16
        manifest['identity_hash'] = digest(manifest['identity'])
    with pytest.raises(ValueError):
        compare(runs)
