import numpy as np

from codecue.binding.discovery_readouts import neutral_train, group_weights, identity_labels


def test_training_mask_excludes_non_neutral_and_development_rows():
    rows=[dict(split=s,condition=c) for s,c in [('train','neutral'),('train','misleading'),
                                              ('development','neutral'),('development','informative')]]
    assert neutral_train(rows).tolist()==[True,False,False,False]


def test_weighting_seeds_retain_complete_structural_groups():
    rows=[dict(template_id=str(i)) for i in range(4) for _ in range(3)]
    a=group_weights(rows,11);b=group_weights(rows,29)
    assert (a>0).all() and np.isclose(a.mean(),1)
    assert all(len(set(a[i:i+3]))==1 for i in range(0,12,3))
    assert np.array_equal(a,group_weights(rows,11)) and not np.allclose(a,b)


def test_identifier_control_labels_are_keyed_by_identity_not_values_or_answers():
    names=[['item_c','item_b'],['item_c','item_b'],['cell_c','cell_b']]
    labels=identity_labels(names,11)
    assert labels.shape==(3,2) and np.array_equal(labels[0],labels[1])
    assert (labels>=0).all() and (labels<32).all()


def test_queried_readout_uses_only_question_visible_sites_and_one_value_head(tmp_path,monkeypatch):
    import json
    import codecue.binding.discovery_readouts as module
    import codecue.binding.state_capture as capture_module
    from codecue.binding.datasets import write_json
    from codecue.binding.published_benchmarks import sha
    folder=tmp_path/'capture/activations/chunks';folder.mkdir(parents=True)
    rows=[];cases=[]
    for index,(split,condition) in enumerate([('train','neutral'),('development','neutral'),('development','informative')]):
        for query in ('current','saved'):
            row=dict(id=f'{index}:{query}',targets=[2,3],split=split,condition=condition,
                     template_id=str(index),query_role=query,state_prefix_sha256=str(index),visible_prefixes=['state','asked value'])
            rows.append(row);cases.append(dict(case=dict(id=row['id'],record=dict(rename_map={'v0':'train_item_c','saved':'train_item_b'}))))
    np.savez(folder/'000000.npz',features=np.ones((6,1,2,4),dtype=np.float32),
             metadata=np.frombuffer(json.dumps(rows).encode(),dtype=np.uint8))
    prepared=tmp_path/'cases.jsonl';prepared.write_text(''.join(json.dumps(c)+'\n' for c in cases))
    capfile=tmp_path/'capture.json';write_json(capfile,dict(run_dir=str(tmp_path/'capture'),capture_cases=str(prepared),layers=[8],model='fixture'))
    monkeypatch.setattr(capture_module,'audit',lambda _:dict(cases=6,identity_hash='fixture'))
    monkeypatch.setattr(module,'code_identity',lambda:dict(source_sha256='fixture'))
    result=module.run(dict(capture_config=str(capfile),capture_config_sha256=sha(capfile),seeds=[11,29,47],alpha=100.,
                           feature_dimensions=4,readout_task='queried_value',run_dir=str(tmp_path/'fits'),report=str(tmp_path/'report.md')))
    assert result['fits'] and all(f['site']=='after_query' for f in result['fits'])
    assert all(len(f['slots'])==1 and f['slots'][0]['slot']=='queried' for f in result['fits'])
    assert all(f['parameter_count_per_value_or_control_readout']==32*5 for f in result['fits'])
