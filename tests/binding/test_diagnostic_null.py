import pytest
from codecue.binding.diagnostic_null import shuffled_reference


def fixture(constant=False):
    rows=[];records={}
    for base in range(3):
        alternative=-1 if constant else 11*(base+1)
        for condition in ('neutral','informative','misleading'):
            for lexical in (0,1):
                identifier=f'{base}:{condition}:{lexical}'
                row=dict(id=identifier,base_id=str(base),condition=condition,lexical_realization=lexical,
                         control_kind='primary',family='parallel',load=2,updates=1,split='train',prediction=alternative)
                records[identifier]={'expected_answer':100+base,'diagnostic_counterfactuals':[
                    {'label':'obsolete_assignment','expected_answer':alternative}]}
                rows.append(row)
    return rows,records


def test_prediction_prior_can_explain_compatible_errors_without_program_association():
    rows,records=fixture(constant=True)
    result=shuffled_reference(rows,records,repetitions=200)
    endpoint=result['endpoints'][0]
    assert endpoint['observed_rate']==endpoint['shuffled_mean_rate']==1
    assert endpoint['observed_minus_shuffled_mean']==0


def test_program_specific_prediction_association_exceeds_shuffled_reference():
    rows,records=fixture()
    result=shuffled_reference(rows,records,repetitions=1000)
    endpoint=result['endpoints'][0]
    assert endpoint['observed_rate']==1
    assert .28<endpoint['shuffled_mean_rate']<.38
    assert result['permutable_bases']==3


def test_reference_preserves_complete_vectors_and_rejects_test_outcomes():
    rows,records=fixture()
    with pytest.raises(ValueError,match='balanced complete'):
        shuffled_reference(rows[:-1],records)
    with pytest.raises(ValueError,match='test outcomes'):
        shuffled_reference([{**r,'split':'test'} for r in rows],records)
