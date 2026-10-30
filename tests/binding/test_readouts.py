import numpy as np
import pytest
from codecue.binding.readouts import latest_definition_sites,definition_pool,definition_surface_source
from codecue.binding.probes import fit_ridge,predict


def fixture():
    source='v0 = 2\nv1 = 7\nv0 = v0 + 3\nv0 - v1'
    return dict(canonical_source=source,source=source,variable_slots={'v0':0,'v1':1})


def test_distributed_readout_uses_only_latest_visible_syntactic_definitions():
    record=fixture();cache={'sites':['statement:0','statement:1','statement:2','source_final']}
    assert latest_definition_sites(record,1)=={0:'statement:0',1:'statement:1'}
    assert latest_definition_sites(record)=={0:'statement:2',1:'statement:1'}
    hidden=np.arange(4*2*32).reshape(4,2,32).astype(float)
    early=definition_pool(hidden,cache,record,0,last_statement=1)
    hidden[2:]+=1e6
    assert np.array_equal(early,definition_pool(hidden,cache,record,0,last_statement=1))
    final=definition_pool(hidden,cache,record,0)
    hidden[0]+=1e6
    assert np.array_equal(final,definition_pool(hidden,cache,record,0))
    assert 'v0 = v0 + 3' not in definition_surface_source(record,1)
    assert 'slot_0_statement_2' in definition_surface_source(record)


def test_fixed_width_readout_can_recover_distributed_synthetic_channels():
    record=fixture();cache={'sites':['statement:0','statement:1','statement:2','source_final']}
    rng=np.random.default_rng(17);labels=rng.integers(-12,13,(140,2));features=[]
    for values in labels:
        hidden=np.zeros((4,1,64));hidden[2,0,0]=values[0];hidden[1,0,1]=values[1]
        features.append(definition_pool(hidden,cache,record,0))
    features=np.array(features)
    assert features.shape==(140,64)
    fitted=fit_ridge(features[:100],labels[:100],alpha=1e-5)
    assert np.array_equal(predict(fitted,features[100:]),labels[100:])


@pytest.mark.parametrize('error', ['duplicate_slots','float_slot','future_layer','negative_layer','identity','nan','duplicate_sites'])
def test_readout_rejects_ambiguous_ownership_and_incompatible_cache(error):
    record=fixture();record['id']='program'
    cache={'id':'program','sites':['statement:0','statement:1','statement:2','source_final']}
    hidden=np.ones((4,2,16));layer=0
    if error=='duplicate_slots':record['variable_slots']['v1']=0
    elif error=='float_slot':record['variable_slots']['v0']=0.0
    elif error=='future_layer':layer=2
    elif error=='negative_layer':layer=-1
    elif error=='identity':cache['id']='other'
    elif error=='nan':hidden[2,0,0]=np.nan
    elif error=='duplicate_sites':cache['sites'][0]='statement:1'
    with pytest.raises(ValueError):definition_pool(hidden,cache,record,layer)


def test_surface_assistance_checks_renaming_without_consulting_oracle_labels():
    record=fixture()
    record.update(source='left = 2\nright = 7\nleft = left + 3\nleft - right',rename_map={'v0':'left','v1':'right'})
    assert 'slot_0_statement_2: left = left + 3' in definition_surface_source(record)
    record['source']=record['source'].replace('left + 3','left + 9')
    with pytest.raises(ValueError,match='differs from canonical'):
        definition_surface_source(record)
