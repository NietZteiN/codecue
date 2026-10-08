import numpy as np
import pytest

from codecue.round6 import crossfit_layers, fold_for, select_identifiers


def test_test_fold_labels_do_not_change_its_selected_layer():
    keys = [f"program-{i}" for i in range(100)]
    labels = np.zeros(100, dtype=int)
    predictions = {2: np.zeros((3,100)), 4:np.ones((3,100))}
    first = crossfit_layers(predictions, labels, keys)
    labels[[fold_for(k) == 0 for k in keys]] = 1
    second = crossfit_layers(predictions, labels, keys)
    assert first[0] == second[0]


def test_renamed_computations_stay_in_the_same_fold():
    from copy import deepcopy
    from codecue.generator import sample_sets
    from codecue.probe_data import program_key
    original = next(iter(sample_sets(5, 1, 61003)))[0]
    renamed = deepcopy(original)
    renamed.names['v1'] = 'sum_of_values'
    assert fold_for(program_key(original)) == fold_for(program_key(renamed))


def test_panel_gate_requires_six_of_seven_and_keeps_fixed_candidate_order():
    panel = [f'm{i}' for i in range(7)]
    gates = {m:{'canonical':{'a':{'argmax':'sum' if i<5 else 'len'},
                             'b':{'argmax':'sum' if i<6 else 'len'},
                             'c':{'argmax':'sum'}}} for i,m in enumerate(panel)}
    selected, scores = select_identifiers(gates,panel,['a','b','c'],limit=1)
    assert selected == ['b']
    assert not scores['a']['panel_pass'] and scores['b']['panel_pass']
    with pytest.raises(ValueError,match='fixed model panel'):
        select_identifiers({k:v for k,v in gates.items() if k!='m6'},panel,['a'])


def test_fresh_replication_roundtrip_preserves_sample_and_matching(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    from codecue.generator import read_jsonl
    from codecue.probe_data import program_key
    from codecue.prompts import demos
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('screened_replication', root/'scripts/79_screened_replication.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fresh = module.fresh_programs()
    assert fresh == json.loads(json.dumps(fresh))
    excluded = {program_key(x) for p in (module.DATA_DIR/'L5').glob('*.jsonl') for x in read_jsonl(p)}
    excluded |= {program_key(x) for seed in (7,11,13) for x in demos(5,seed,'trace')}
    keys = {x['program_key'] for x in fresh}
    assert len(keys) == 200 and not keys & excluded
    module.BASE = tmp_path
    (tmp_path/'fresh_programs.json').write_text(json.dumps({'programs':fresh}))
    rows = module.instances(['sum_of_values'])
    for neutral, misleading in zip(rows[::2], rows[1::2]):
        assert program_key(neutral) == program_key(misleading)
        assert neutral.values == misleading.values and neutral.answer == misleading.answer
        assert sum(neutral.names[r] != misleading.names[r] for r in neutral.names) == 1
