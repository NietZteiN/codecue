import json
import random
from pathlib import Path
import pytest
from codecue.binding.interpreter import execute, python_oracle
from codecue.binding.programs import make_program, rename, renaming, computed_swap, skeleton, FAMILIES
from codecue.binding.datasets import generate, validate, read_jsonl
from codecue.binding.activations import labels_at
from codecue.binding.behavior import select


def test_deeper_updates_and_distance_have_explicit_semantics():
    for family in FAMILIES:
        for updates in (1,3,5,7):
            original=make_program(family,4,updates,0,random.Random(43))
            padded=make_program(family,4,updates,0,random.Random(43),distance_padding=8)
            a,b=execute(original),execute(padded)
            assert a['expected_answer']==b['expected_answer']
            assert a['execution_trace'][-1]['values']==b['execution_trace'][-1]['values']
            assert sum(p['definition'].startswith('v0@') for p in b['execution_trace'])==updates+1
            assert skeleton(original)!=skeleton(padded)
            assert python_oracle([padded])[0]['answer']==b['expected_answer']


def test_six_current_bindings_renaming_and_multiset_swap():
    for family in FAMILIES:
        source=make_program(family,6,5,1,random.Random(71),variable_count=6,distance_padding=8)
        truth=execute(source)
        assert max(p['count'] for p in truth['liveness'])==6
        for condition in ('informative','neutral','misleading'):
            for lexical in (0,1):
                mapping=renaming(family,condition,lexical,'test',6)
                assert len(set(mapping.values()))==6
                rendered=rename(source,mapping)
                assert python_oracle([rendered])[0]['answer']==truth['expected_answer']
        swapped=execute(computed_swap(source))
        a,b=truth['execution_trace'][-1]['values'],swapped['execution_trace'][-1]['values']
        assert sorted(a.values())==sorted(b.values())
        assert a['v0']==b['v1'] and a['v1']==b['v0']
        truth['variable_slots']={f'v{i}':i for i in range(6)}
        assert len(labels_at(truth,len(truth['execution_trace'])-1)['current'])==6


def test_reserved_extrapolation_is_disjoint_and_sealed(tmp_path,monkeypatch):
    # One family is enough to test cross-dataset constraints while keeping the
    # independent ordinary-Python oracle in the acceptance path.
    import codecue.binding.datasets as datasets
    monkeypatch.setattr(datasets,'FAMILIES',('parallel',))
    reference=tmp_path/'reference.jsonl'
    base=dict(algorithm_version=5,seed=7,instances_per_cell=10,templates_per_cell=10,
              answer_magnitude_bins=[[0,5],[6,10],[11,15]],counterfactual_pairs=False,arithmetic_controls=False)
    generate(base,reference)
    path=tmp_path/'extrapolation.jsonl'
    config={**base,'algorithm_version':6,'seed':17,'cohort':'combined','evaluation_role':'structural_extrapolation',
            'split_override':'test','variable_count':6,'load_levels':[6],'update_levels':[5],
            'distance_padding':8,'reference_datasets':[str(reference)],'counterfactual_pairs':True}
    manifest=generate(config,path)
    assert manifest['rows']==120 and manifest['split_rows']=={'test':120}
    assert validate(path)['status']=='passed'
    rows=read_jsonl(path)
    assert {r['evaluation_role'] for r in rows}=={'structural_extrapolation'}
    old={skeleton(r['canonical_source']) for r in read_jsonl(reference)}
    assert not old & {skeleton(r['canonical_source']) for r in rows}
    with pytest.raises(ValueError,match='test is sealed'):
        select(rows,dict(splits=['test'],control_kinds=['primary']))
    with pytest.raises(ValueError,match='reserved test'):
        generate({**config,'split_override':'train'},tmp_path/'invalid.jsonl')
