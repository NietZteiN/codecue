"""Source-controlled provenance pairs and in-memory paired prediction metrics."""
from copy import deepcopy
import ast

import pytest

from codecue.binding import relationship_contrasts as study
from codecue.binding.datasets import digest
from codecue.binding.programs import rename


def rows(base='base', group='g0', split='development', values=(2,3,3,7), lexical=(0,1), rest=(0,1,2)):
    result=[]
    for lex in lexical:
        mapping={f'v{i}':f'{"item" if lex==0 else "cell"}_{i}' for i in range(4)}
        for first in (1,2,3):
            parents=(first,*rest)
            source='\n'.join([*(f'v{i} = {v}' for i,v in enumerate(values)),
                *(f'v{i} = v{p}' for i,p in enumerate(parents)), 'v0'])
            result.append(dict(id=f'{base}:lex{lex}:parent{first}',base_id=base,
                cluster_id=group,component_id=group,template_id=group,split=split,
                lexical_realization=lex,condition='neutral',canonical_source=source,
                source=rename(source,mapping),rename_map=mapping,variable_slots={f'v{i}':i for i in range(4)},
                evaluation_role='discovery_algebraic_relationship_routing_v1',
                expected_answer=object(), execution_trace=object(), targets=object()))
    return result


def predictions(records):
    return {row['id']:tuple(int(node.value.id[1:]) for node in ast.parse(row['canonical_source']).body[4:8])
        for row in records}


def test_manifest_uses_source_only_and_keeps_lexical_pairs_in_same_numeric_base():
    records=rows(); manifest=study.build_pairs(records)
    assert manifest['pair_counts']=={'development':2}
    assert manifest['numeric_base_counts']=={'development':1}
    assert manifest['component_counts']=={'development':1}
    assert manifest['qualified_sites']==[7,8] and manifest['initialization_site_unobservable']==3
    assert manifest['source_case_ids']==[row['id'] for row in records]
    assert manifest['source_only'] and manifest['actual_output_not_executed']
    assert manifest['manifest_sha256']==digest({k:v for k,v in manifest.items() if k!='manifest_sha256'})
    assert {pair['lexical_realization'] for pair in manifest['pairs']}=={0,1}
    for pair in manifest['pairs']:
        assert pair['left_parent_truth']==[1,0,1,2]
        assert pair['right_parent_truth']==[2,0,1,2]
        assert records[pair['left_index']]['id']==pair['left_id']
        assert records[pair['right_index']]['id']==pair['right_id']


def test_distinct_values_are_not_misidentified_as_equal_state_controls():
    bank=rows()+rows('distinct','g1',values=(2,3,5,7))
    result=study.build_pairs(bank)
    assert result['pair_counts']=={'development':2}
    assert all(pair['base_id']=='base' for pair in result['pairs'])
    with pytest.raises(ValueError,match='equal-state'):study.build_pairs(rows(values=(2,3,5,7)))


@pytest.mark.parametrize('change',['missing','duplicate_parent','roots','other_parent','surface_space','mapping','base_split','role'])
def test_invalid_pairing_or_reserved_roles_rejected(change):
    bank=rows()
    if change=='missing':bank.pop()
    elif change=='duplicate_parent':bank[2]=deepcopy(bank[1]);bank[2]['id']='extra'
    elif change=='roots':
        bank[1]['canonical_source']=bank[1]['canonical_source'].replace('v3 = 7','v3 = 8')
        bank[1]['source']=rename(bank[1]['canonical_source'],bank[1]['rename_map'])
    elif change=='other_parent':
        bank[1]['canonical_source']=bank[1]['canonical_source'].replace('v1 = v0','v1 = v3')
        bank[1]['source']=rename(bank[1]['canonical_source'],bank[1]['rename_map'])
    elif change=='surface_space':bank[1]['source']=bank[1]['source'].replace(' = ','  = ')
    elif change=='mapping':
        bank[1]['rename_map']={f'v{i}':f'other_{i}' for i in range(4)}
        bank[1]['source']=rename(bank[1]['canonical_source'],bank[1]['rename_map'])
    elif change=='base_split':bank+=rows('base','g1','train')
    else:bank[0]['evaluation_role']='sealed_final_results'
    with pytest.raises(ValueError):study.build_pairs(bank)


@pytest.mark.parametrize('site',[7,8])
def test_oracle_parent_fixture_scores_both_graphs_but_is_not_model_evidence(site):
    bank=rows();manifest=study.build_pairs(bank)
    report=study.score_pairs(manifest,predictions(bank),site=site)
    assert report['status']=='posthoc_descriptive'
    assert report['lexical_pairs']==2 and report['numeric_bases']==1 and report['structural_components']==1
    assert report['pooled']['both_whole_graphs_correct']==1
    assert report['pooled']['both_first_parents_correct']==1
    assert report['pooled']['first_parent_predictions_differ']==1
    assert report['pooled']['first_parent_predictions_collapse']==0
    assert report['pooled']['first_parents_swapped']==0
    assert report['component_macro']==report['pooled']
    assert not report['confidence_intervals_computed'] and not report['independent_pair_replications']


def test_distinguishable_but_swapped_predictions_are_wrong_and_constant_predictions_collapse():
    bank=rows();manifest=study.build_pairs(bank);pred=predictions(bank)
    for pair in manifest['pairs']:
        pred[pair['left_id']],pred[pair['right_id']]=pred[pair['right_id']],pred[pair['left_id']]
    swapped=study.score_pairs(manifest,pred,site=7)['pooled']
    assert swapped['first_parent_predictions_differ']==1
    assert swapped['both_first_parents_correct']==0 and swapped['first_parents_swapped']==1
    assert swapped['whole_graph_correct_fraction']==0
    constant={case:(1,0,1,2) for case in pred}
    collapsed=study.score_pairs(manifest,constant,site=7)['pooled']
    assert collapsed['first_parent_predictions_collapse']==1
    assert collapsed['first_parent_correct_fraction']==.5
    assert collapsed['both_whole_graphs_correct']==0


def test_component_macro_does_not_turn_more_numeric_lexical_relatives_into_more_groups():
    bank=rows('a','small')+rows('b','large')+rows('c','large')+rows('d','large')
    manifest=study.build_pairs(bank);pred=predictions(bank)
    for row in bank:
        if row['component_id']=='large':pred[row['id']]=(3,0,1,2)
    report=study.score_pairs(manifest,pred,site=7)
    assert report['lexical_pairs']==8 and report['numeric_bases']==4 and report['structural_components']==2
    assert report['pooled']['both_whole_graphs_correct']==.25
    assert report['component_macro']['both_whole_graphs_correct']==.5


@pytest.mark.parametrize('problem',['missing_case','extra_case','float','bool','self_parent','site3','train_empty','manifest_tamper'])
def test_prediction_identity_domain_visibility_and_manifest_guards(problem):
    bank=rows();manifest=study.build_pairs(bank);pred=predictions(bank);kwargs=dict(site=7)
    if problem=='missing_case':pred.pop(next(iter(pred)))
    elif problem=='extra_case':pred['other']=(1,0,1,2)
    elif problem=='float':pred[next(iter(pred))]=(1.,0,1,2)
    elif problem=='bool':pred[next(iter(pred))]=(True,0,1,2)
    elif problem=='self_parent':pred[next(iter(pred))]=(0,0,1,2)
    elif problem=='site3':kwargs['site']=3
    elif problem=='train_empty':kwargs['split']='train'
    else:manifest['pairs'][0]['right_parent_truth'][0]=3
    with pytest.raises(ValueError):study.score_pairs(manifest,pred,**kwargs)
