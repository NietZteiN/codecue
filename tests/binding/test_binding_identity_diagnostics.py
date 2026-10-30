"""Counterexamples for oracle-assisted owner/version interpretation, no I/O."""
from copy import deepcopy
from dataclasses import replace

import numpy as np
import pytest

from codecue.binding import binding_identity_diagnostics as core
from codecue.binding import relationship_schedule_programs as programs
from codecue.binding import schedule_targets as target
from codecue.binding.datasets import digest
from codecue.binding.programs import rename


@pytest.fixture(scope="module")
def bundles():
    template=next(t for t in programs._templates() if t["destinations"]==(0,0,1,0)
                  and t["parent_pattern"]=="ring_successor")
    component=template["component_id"];mapping={f"v{i}":f"item_{i}" for i in range(4)}
    canonical=programs._source((1,2,3,4),template["destinations"],template["parents"],0)
    surface=rename(canonical,mapping);base=f"{component}:numeric11"
    row=dict(evaluation_role=programs.ROLE,condition="neutral",split=template["split"],
        id="relationship-schedule:"+digest([11,surface])[:24],component_id=component,
        cluster_id=component,template_id=component,ssa_graph_canonical_id=component,
        schedule_id=template["schedule_id"],parent_pattern=template["parent_pattern"],
        ordered_schedule_canonical_id=template["ordered_schedule_canonical_id"],
        destination_schedule=list(template["destinations"]),copy_parent_slots=list(template["parents"]),
        schedule_kind=template["schedule_kind"],raw_template_id=template["schedule_id"]+":"+template["parent_pattern"],
        numeric_seed=11,lexical_realization=0,query_slot=0,query_role="v0",query_count=1,
        source_form="literal",base_id=base,paired_group_id=base,source=surface,canonical_source=canonical,
        variable_slots=programs.SLOTS.copy(),rename_map=mapping)
    return {site:target.targets([row],site) for site in (3,7,8)}


def predictions(bundle):
    truth=np.full((len(bundle.case_ids),12),-1,dtype=np.int16)
    valid=np.zeros_like(truth,dtype=bool)
    for h,head in enumerate(target.HEADS):
        for i in range(len(truth)):
            labels=bundle.y[i,list(head["indices"])]
            if labels.sum()==1:
                valid[i,h]=True;truth[i,h]=head["candidates"][int(labels.argmax())]
    return dict(truth=truth,predicted=truth.copy(),valid=valid,correct=valid.copy(),
                margin=np.full(truth.shape,np.nan),top_score=np.ones(truth.shape))


def h(name):return core.HEAD_ORDER.index(name)


def repeated(bundle,groups):
    n=len(groups);descriptive=deepcopy(bundle.descriptive)
    descriptive["version_map_by_case"]=[deepcopy(bundle.descriptive["version_map_by_case"][0]) for _ in groups]
    return replace(bundle,y=np.repeat(bundle.y,n,axis=0),mask=np.repeat(bundle.mask,n,axis=0),
        case_ids=tuple(f"case{i}" for i in range(n)),group_ids=tuple(groups),
        splits=("development",)*n,descriptive=descriptive)


def details(result,name,index=0):return next(r for r in result["rows"] if r["head"]==name and r["case_id"]==result["rows"][index*12]["case_id"])


def test_exact_predictions_and_parent_obsolete_only_at_capture(bundles):
    bundle=bundles[7];pred=predictions(bundle)
    result=core.diagnostics(bundle,pred,include_rows=True)
    assert result["oracle_assisted"] and result["real_task_truth_only"]
    assert core.HEAD_ORDER==tuple(h["name"] for h in target.HEADS)
    for family in core.FAMILIES:
        assert result["per_family"][family]["counts"]["exact"]==4
        assert result["per_family"][family]["metric_rates"]["exact"]==1
    assert result["per_family"]["current_version"]["metric_rates"]["owner_correct"] is None
    # Statements4/5 read v1@1, which statement6 later overwrites.
    assert bundle.descriptive["version_map_by_case"][0][1]["status"]=="obsolete"
    row=details(result,"copy_parent/0")
    assert row["truth"]==1 and row["category"]=="exact"
    assert row["reference_checkpoint"]==3 and row["predicted_definition_status"]=="current"


def test_wrong_owner_same_ordinal_version_never_becomes_identity(bundles):
    pred=predictions(bundles[7])["predicted"];pred[0,h("current_definition/3")]=2
    result=core.diagnostics(bundles[7],pred,include_rows=True)
    row=details(result,"current_definition/3")
    assert row["category"]=="different_owner_current"
    assert row["metrics"]==dict(exact=False,owner_correct=False,version_number_equal=True)
    joint=result["scalar_definition_joint"]["3"]
    assert joint["scalar_correct__definition_owner_correct"]["counts"]["true__false"]==1
    assert joint["scalar_correct__definition_version_equal"]["counts"]["true__true"]==1
    assert joint["scalar_correct__scalar_definition_agree"]["counts"]["true__true"]==1


def test_same_owner_old_version_and_jointly_wrong_agreement(bundles):
    pred=predictions(bundles[7])["predicted"]
    pred[0,h("current_definition/0")]=4;pred[0,h("current_version/0")]=2
    result=core.diagnostics(bundles[7],pred,include_rows=True)
    row=details(result,"current_definition/0")
    assert row["truth_version"]==4 and row["predicted_version"]==2
    assert row["category"]=="same_owner_wrong_version" and row["predicted_definition_status"]=="obsolete"
    assert row["metrics"]==dict(exact=False,owner_correct=True,version_number_equal=False)
    assert result["scalar_definition_joint"]["0"]["scalar_correct__scalar_definition_agree"]["counts"]["false__true"]==1


@pytest.mark.parametrize("candidate,category,status",[(5,"different_owner_current","current"),
    (4,"different_owner_obsolete","obsolete")])
def test_parent_currentness_uses_predicted_owner_at_read_not_capture(bundles,candidate,category,status):
    pred=predictions(bundles[7])["predicted"];pred[0,h("copy_parent/3")]=candidate
    result=core.diagnostics(bundles[7],pred,include_rows=True)
    row=details(result,"copy_parent/3")
    assert row["reference_checkpoint"]==6 and row["truth"]==6
    assert row["category"]==category and row["predicted_definition_status"]==status
    assert bundles[7].descriptive["version_map_by_case"][0][candidate]["status"]=="obsolete"


def test_different_owner_obsolete_can_share_true_version_number(bundles):
    pred=predictions(bundles[7])["predicted"];pred[0,h("current_definition/1")]=4
    row=details(core.diagnostics(bundles[7],pred,include_rows=True),"current_definition/1")
    assert row["category"]=="different_owner_obsolete"
    assert row["truth_version"]==row["predicted_version"]==2 and not row["metrics"]["owner_correct"]


def test_missing_future_and_outside_domain_are_counted_without_repair(bundles):
    pred=predictions(bundles[7])["predicted"].astype(object)
    pred[0,h("copy_parent/0")]=4;pred[0,h("copy_parent/1")]=7
    pred[0,h("current_definition/2")]=99;pred[0,h("current_definition/3")]=None
    pred[0,h("current_version/2")]=0;pred[0,h("current_version/3")]=-1
    result=core.diagnostics(bundles[7],pred,include_rows=True)
    assert details(result,"copy_parent/0")["category"]=="invalid_future"
    assert details(result,"copy_parent/1")["category"]=="invalid_future"
    assert details(result,"current_definition/2")["category"]=="invalid_candidate"
    assert details(result,"current_definition/3")["category"]=="missing"
    assert details(result,"current_version/2")["category"]=="invalid_candidate"
    assert details(result,"current_version/3")["category"]=="missing"
    stats=result["per_family"]["current_definition"]
    assert stats["n_defined"]==4 and stats["counts"]["exact"]==2 and stats["metric_rates"]["exact"]==.5
    agree=result["scalar_definition_joint"]["3"]["scalar_correct__scalar_definition_agree"]
    assert agree["counts"]["false__undefined"]==1 and agree["rates"]["false__undefined"]==1


def test_initial_site_has_undefined_parents_and_future_versions(bundles):
    pred=predictions(bundles[3])["predicted"]
    pred[0,h("copy_parent/0")]=0;pred[0,h("current_definition/0")]=4;pred[0,h("current_version/0")]=2
    result=core.diagnostics(bundles[3],pred,include_rows=True)
    assert details(result,"current_definition/0")["category"]=="invalid_future"
    assert details(result,"current_version/0")["category"]=="invalid_future"
    parent=result["per_family"]["copy_parent"]
    assert parent["n_total"]==parent["n_undefined"]==4 and parent["n_defined"]==0
    assert parent["counts"]["undefined"]==4 and parent["metric_rates"]["exact"] is None
    assert parent["equal_graph_rates"]["exact"] is None and parent["n_graphs_defined"]==0


def test_unequal_graph_aggregation_profiles_and_pooled_head_denominators(bundles):
    bundle=repeated(bundles[7],["large","large","small"]);pred=predictions(bundle)["predicted"]
    pred[2,h("current_definition/0")]=2
    result=core.diagnostics(bundle,pred,profiles=["p1","p1","p2"])
    head=result["per_head"]["current_definition/0"]
    assert head["n_defined"]==3 and head["rates"]["exact"]==pytest.approx(2/3)
    assert head["equal_graph_rates"]["exact"]==.5
    family=result["per_family"]["current_definition"]
    assert family["n_defined"]==12 and family["counts"]["exact"]==11
    assert family["metric_rates"]["exact"]==pytest.approx(11/12)
    assert family["equal_graph_metric_rates"]["exact"]==.875
    assert result["by_profile"]["p1"]["per_head"]["current_definition/0"]["rates"]["exact"]==1
    assert result["by_profile"]["p2"]["per_head"]["current_definition/0"]["rates"]["exact"]==0


@pytest.mark.parametrize("damage",["duplicate_statement","duplicate_identity","version_jump","final_status","boolean_slot","future_node"])
def test_malformed_ssa_maps_rejected(bundles,damage):
    desc=deepcopy(bundles[7].descriptive);nodes=desc["version_map_by_case"][0]
    if damage=="duplicate_statement":nodes[4]["statement"]=3
    elif damage=="duplicate_identity":nodes[4].update(slot=1,version=1,id="v1@1")
    elif damage=="version_jump":nodes[4].update(version=3,id="v0@3")
    elif damage=="final_status":nodes[1]["status"]="current"
    elif damage=="boolean_slot":nodes[0]["slot"]=False
    else:nodes.append(dict(statement=8,slot=0,version=5,id="v0@5",status="current"))
    with pytest.raises(ValueError):core.diagnostics(replace(bundles[7],descriptive=desc),predictions(bundles[7]))


def test_obsolete_parent_truth_rejected_even_with_matching_direct_edge(bundles):
    bundle=bundles[7];y=bundle.y.copy();head=target.HEADS[h("copy_parent/3")]
    y[0,list(head["indices"])]=0;y[0,head["indices"][1]]=1
    for spec in target.COLUMNS:
        if spec["family"]=="direct" and spec["consumer_node"]==7:y[0,spec["index"]]=spec["source_node"]==1
    bad=replace(bundle,y=y)
    with pytest.raises(ValueError,match="latest definition at consumer read time"):
        core.diagnostics(bad,predictions(bad))


@pytest.mark.parametrize("family,candidate",[("current_definition",5),("current_version",3)])
def test_real_truth_must_match_source_checkpoint(bundles,family,candidate):
    bundle=bundles[7];y=bundle.y.copy();head=target.HEADS[h(family+"/0")]
    y[0,list(head["indices"])]=0;y[0,list(head["indices"])[head["candidates"].index(candidate)]]=1
    bad=replace(bundle,y=y)
    with pytest.raises(ValueError,match="source checkpoint"):core.diagnostics(bad,predictions(bad))


def test_future_mask_and_sham_truth_rejected(bundles):
    bundle=bundles[3];mask=bundle.mask.copy();head=target.HEADS[h("current_definition/0")];mask[0,head["indices"][7]]=True
    with pytest.raises(ValueError,match="static candidate"):core.diagnostics(replace(bundle,mask=mask),predictions(bundle))
    desc=deepcopy(bundle.descriptive);desc["control"]=True
    with pytest.raises(ValueError,match="real-task"):core.diagnostics(replace(bundle,descriptive=desc),predictions(bundle))


@pytest.mark.parametrize("bad",[1.0,float("nan"),True,"1"])
def test_noninteger_predictions_rejected(bundles,bad):
    pred=predictions(bundles[7])["predicted"].astype(object);pred[0,0]=bad
    with pytest.raises(ValueError,match="integer predictions"):core.diagnostics(bundles[7],pred)


@pytest.mark.parametrize("field",["truth","valid","correct","case_ids"])
def test_supplied_prediction_identity_is_cross_checked(bundles,field):
    pred=predictions(bundles[7])
    if field=="case_ids":pred[field]=["wrong-case"]
    else:pred[field][0,0]=0 if field=="truth" else False
    with pytest.raises(ValueError):core.diagnostics(bundles[7],pred)


def test_groups_may_coarsen_but_cannot_split_or_cross_discovery_splits(bundles):
    bundle=repeated(bundles[7],["g1","g1"])
    with pytest.raises(ValueError,match="graph groups"):core.diagnostics(bundle,predictions(bundle),groups=["one","two"])
    bundle=replace(bundle,splits=("train","development"))
    with pytest.raises(ValueError,match="graph groups"):core.diagnostics(bundle,predictions(bundle))
    bundle=repeated(bundles[7],["g1","g2"])
    assert core.diagnostics(bundle,predictions(bundle),groups=["coarse","coarse"])["graph_groups"]==1


def test_pure_diagnostic_does_not_read_files_arrays_or_mutate_inputs(bundles,monkeypatch):
    pred=predictions(bundles[7]);before=deepcopy(bundles[7].descriptive);y=bundles[7].y.copy();p=pred["predicted"].copy()
    def forbidden(*_,**__):raise AssertionError("diagnostic must remain pure")
    monkeypatch.setattr("builtins.open",forbidden);monkeypatch.setattr(np,"load",forbidden)
    result=core.diagnostics(bundles[7],pred)
    assert "rows" not in result and bundles[7].descriptive==before
    np.testing.assert_array_equal(bundles[7].y,y);np.testing.assert_array_equal(pred["predicted"],p)
