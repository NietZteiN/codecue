from codecue.binding.diagnostics import cases
from codecue.binding.interpreter import python_oracle


def test_interface_diagnostics_use_fixed_ground_truth_and_training_only():
    rows=[dict(id=s,split=s,control_kind='primary',condition='neutral',lexical_realization=0,
               source='v0 = 3\nv0',expected_answer=3) for s in ('train','development','test')]
    selected=cases(rows)
    assert len(selected)==9 and all(r['split']=='train' for r in selected)
    assert selected[-1]['id']=='train'
    oracle=python_oracle([r['source'] for r in selected])
    assert [r['expected_answer'] for r in selected]==[r['answer'] for r in oracle]
