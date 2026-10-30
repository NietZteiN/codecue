import pytest

from codecue.binding.datasets import digest
from codecue.binding.published_benchmarks import score
from codecue.binding.published_review import descriptive, equivalent_score


def fixture():
    row = {'id': 'crux/a', 'input': '2', 'output': '5'}
    tasks = ['cruxeval_o_direct', 'cruxeval_o_cot']
    texts = ['assert f(2) == 4', '[ANSWER]\nassert f(2) == 5\n[/ANSWER]']
    results = [{'task': task, 'id': row['id'], 'record_sha256': digest(row),
                'raw_response': text, 'score': score(task, row, text),
                'stop_reason': 'eos', 'generated_tokens': 10}
               for task, text in zip(tasks, texts)]
    return [(task, row) for task in tasks], results


def test_review_pairs_protocols_and_recomputes_scores():
    planned, results = fixture()
    review = descriptive(results, planned)
    assert review['cruxeval_paired_correctness'] == dict(
        n=1, both_correct=0, direct_only_correct=0, cot_only_correct=1, both_incorrect=0)
    results[0]['score']['correct'] = True
    with pytest.raises(ValueError, match='recomputed score mismatch'):
        descriptive(results, planned)


def test_review_rejects_missing_duplicate_and_wrong_record_rows():
    planned, results = fixture()
    with pytest.raises(ValueError, match='complete unique'):
        descriptive(results[:1], planned)
    with pytest.raises(ValueError, match='coverage differs'):
        descriptive([results[0], results[0]], planned)
    results[0]['record_sha256'] = 'tampered'
    with pytest.raises(ValueError, match='record or recomputed'):
        descriptive(results, planned)


def test_format_valid_demo_copy_is_flagged_without_excluding_it():
    task = 'bbh_tracking_3'
    row = {'id': 'bbh/0', 'target': '(A)'}
    text = 'Q: A different question\nThe answer is (A).'
    result = dict(task=task, id=row['id'], record_sha256=digest(row), raw_response=text,
                  score=score(task, row, text), stop_reason='eos', generated_tokens=20)
    review = descriptive([result], [(task, row)])
    assert result['score']['correct']
    assert review['tasks'][0]['starts_new_question'] == 1
    assert review['tasks'][0]['predicted_letters'] == {'(A)': 1}


def test_parse_error_object_addresses_are_not_scientific_score_fields():
    a = dict(correct=False, valid=False,
             parse_error='ValueError: malformed node: <ast.Call object at 0x7f123>')
    b = {**a, 'parse_error': a['parse_error'].replace('0x7f123', '0x456')}
    assert equivalent_score(a, b)
    assert not equivalent_score(a, {**b, 'correct': True})
    assert not equivalent_score(a, {**b, 'parse_error': b['parse_error'].replace('Call', 'BinOp')})
