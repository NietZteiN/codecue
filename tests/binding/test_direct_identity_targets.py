"""Source-only tests for direct global-codebook event identity targets."""
import ast
from copy import deepcopy
from dataclasses import replace
import hashlib
from itertools import product
import json
import sys

import numpy as np
import pytest

from codecue.binding import direct_identity_targets as study
from codecue.binding import diversity_targets as diversity
from codecue.binding import schedule_diversity_programs as programs
from codecue.binding import schedule_targets as original
from codecue.binding.discovery_readouts import group_weights


@pytest.fixture(scope="module")
def bank(tmp_path_factory):
    """A generated fixture, never a published bank or saved model outcome."""
    folder = tmp_path_factory.mktemp("direct-identity-source-fixture")
    routing = [dict(evaluation_role="discovery_relationship_routing_v1", condition="neutral", split="train",
        canonical_source=programs.prior._source((1,2,3,4),(0,1,2,3),parents,0))
        for parents in product(*(tuple(s for s in range(4) if s != d) for d in range(4)))]
    schedules = [dict(evaluation_role=programs.prior.ROLE, condition="neutral", split="train",
        canonical_source=programs.prior._source((1,2,3,4),dest,tuple((d+offset)%4 for d in dest),0))
        for dest in programs.prior.REPEATED_SCHEDULES for offset in programs.prior.PARENT_PATTERNS.values()]
    exclusions = []
    for name, rows in (("routing_sources_v1",routing),("schedule_sources_v1",schedules)):
        path = folder/(name+".jsonl")
        payload = "".join(json.dumps(row)+"\n" for row in rows).encode()
        path.write_bytes(payload)
        exclusions.append(dict(name=name,path=str(path),sha256=hashlib.sha256(payload).hexdigest()))
    config = dict(evaluation_role=programs.ROLE,candidate_seed=20261028,numeric_seeds=[751,857,967],
        dataset=str(folder/"sources.jsonl"),review=str(folder/"review.json"),report=str(folder/"sources.md"),
        excluded_graph_sources=exclusions)
    selected,*_ = programs._selection(config)
    rows = programs._make_rows(config,selected)
    family_map = {graph:(profile,index,dest,parents,"train" if index<15 else "development")
        for profile in programs.PROFILES for index,(graph,dest,parents) in enumerate(selected[profile])}
    return rows,family_map


@pytest.fixture(autouse=True)
def fixture_map(monkeypatch,bank):
    monkeypatch.setattr(diversity,"_family_map",lambda:bank[1])


@pytest.fixture(scope="module")
def bundles(bank):
    # Module fixtures execute before function-scoped monkeypatches.
    previous = diversity._family_map
    diversity._family_map = lambda:bank[1]
    try:
        return {site:study.targets(bank[0],site) for site in study.SITES}
    finally:
        diversity._family_map = previous


def head(name):
    return next(h for h in study.HEADS if h["name"]==name)


def choices(bundle_or_scores,name):
    values = bundle_or_scores.y if hasattr(bundle_or_scores,"y") else bundle_or_scores
    spec = head(name)
    return np.asarray(spec["candidates"])[np.argmax(values[:,spec["indices"]],axis=1)]


def ordinary_trace(row):
    """Independent statement/identifier loop; no generic SSA label routine."""
    tree = ast.parse(row["source"])
    names = {name:slot for key,slot in row["variable_slots"].items() for name in [row["rename_map"][key]]}
    versions = [0]*4
    current = {}
    truth = {kind:[] for kind in ("assignment","parent")}
    definitions = []
    for statement,assign in enumerate(tree.body[:-1]):
        owner = names[assign.targets[0].id]
        if statement>=4:
            parent_owner = names[assign.value.id]
            truth["parent"].append((parent_owner,versions[parent_owner],current[parent_owner]))
        versions[owner] += 1
        definitions.append((owner,versions[owner],statement))
        current[owner] = statement
        if statement>=4:
            truth["assignment"].append(definitions[-1])
    return truth,current


def test_schema_isolated_registered_and_codebook_roundtrip():
    assert study.N_COLUMNS==192 and len(study.HEADS)==24
    assert len(set(c["name"] for c in study.COLUMNS))==192
    assert original.N_COLUMNS==232 and len(original.HEADS)==12 and original.MAX_ROWS==2016
    assert diversity.N_COLUMNS==232 and diversity.MAX_ROWS==5760
    assert study.TargetBundle is not original.TargetBundle
    assert sys.modules[study.TargetBundle.__module__].TargetBundle is study.TargetBundle
    for owner,version in product(range(4),range(1,5)):
        assert study.decode_joint(study.encode_joint(owner,version))==(owner,version)
    assert study.HEAD_ORDER==tuple(h["name"] for h in study.HEADS)
    assert all(c["kind"]=="categorical" for c in study.COLUMNS)


@pytest.mark.parametrize("value",[-1,16,True,3.0,"3",None])
def test_global_codebook_rejects_invalid_candidates(value):
    with pytest.raises(ValueError):study.decode_joint(value)


def test_stripped_records_need_no_stored_truth_or_answer(bank):
    rows = [{key:value for key,value in r.items() if key not in ("targets","expected_answer")}
            for r in bank[0][:8]]
    bundle = study.targets(rows,7)
    assert bundle.y.shape==(8,192) and bundle.case_ids==tuple(r["id"] for r in rows)
    assert bundle.descriptive["no_per_case_oracle_map_used_to_decode_predictions"] is True
    assert "version_map_by_case" not in bundle.descriptive
    row = deepcopy(rows[0]);row["evaluation_role"]="discovery_relationship_schedule_targets_v1"
    with pytest.raises(ValueError):study.targets([row],7)


def test_site3_all_heads_future_and_all_domain_choices_retained(bundles):
    before,after = bundles[3],bundles[7]
    assert before.y.shape==(5760,192) and not before.mask.any() and not before.y.any()
    assert after.mask.all()
    # Assignment version1 is impossible, yet remains a defined evaluated choice.
    first = head("assignment_joint/4")
    assert after.mask[:,first["indices"]].all()
    assert np.sum(after.y[:,first["indices"]][::,::4])==0
    np.testing.assert_array_equal(after.y,bundles[8].y)
    np.testing.assert_array_equal(after.mask,bundles[8].mask)
    assert all(all(v==-1 for v in item["assignment"]) for item in before.descriptive["syntax_owners"])


def test_full_bank_matches_independent_ordinary_trace_and_read_time(bank,bundles):
    bundle = bundles[7]
    predicted = {name:choices(bundle,name) for name in study.HEAD_ORDER}
    obsolete_parents = 0
    for i,row in enumerate(bank[0]):
        expected,current = ordinary_trace(row)
        for kind in ("assignment","parent"):
            for step,(owner,version,statement) in enumerate(expected[kind]):
                event = step+4
                assert predicted[f"{kind}_joint/{event}"][i]==study.encode_joint(owner,version)
                assert predicted[f"{kind}_owner/{event}"][i]==owner
                assert predicted[f"{kind}_version/{event}"][i]==version
                assert bundle.descriptive["event_truth_statements"][i][kind][step]==statement
                status = "current" if current[owner]==statement else "obsolete"
                assert bundle.descriptive["event_capture_status"][i][kind][step]==status
                obsolete_parents += kind=="parent" and status=="obsolete"
    assert obsolete_parents>0  # Obsolete by capture time is still correct at its earlier consumer.


def test_complete_support_keeps_rare_and_constant_classes(bundles):
    support = study.training_support(bundles[7])
    assert support["structural_groups"]==45 and len(support["columns"])==192
    assert not support["eligible_boolean_indices"]
    inventory = {h["head"]:h for h in support["categorical_heads"]}
    assert [len(inventory[f"assignment_joint/{e}"]["observed_train_classes"]) for e in study.EVENTS]==[4,8,12,12]
    assert [len(inventory[f"parent_joint/{e}"]["observed_train_classes"]) for e in study.EVENTS]==[4,8,12,16]
    assert inventory["assignment_version/4"]["constant"]
    assert inventory["parent_version/4"]["constant"]
    rare = inventory["parent_version/7"]
    assert rare["unsupported_observed_train_classes"]==[4] and not rare["eligible_categorical"]
    assert rare["classes"][3]["train_groups"]==2 and rare["classes"][3]["development_groups"]==1
    assert rare["classes"][3]["development_rows"]==96
    assert all(not h["development_only_classes"] and not h["evaluated_choices_removed"] for h in inventory.values())
    for kind,event in product(("assignment","parent"),study.EVENTS):
        for candidate in inventory[f"{kind}_owner/{event}"]["classes"]:
            assert candidate["train_rows"]==1080 and candidate["train_groups"]==45
            assert candidate["development_rows"]==360 and candidate["development_groups"]==15
    future = study.training_support(bundles[3])
    assert all(h["missing"] and not h["eligible_categorical"] for h in future["categorical_heads"])


def test_prefix_sham_coherent_and_tied_across_queries_lexical_sites(bank):
    rows = bank[0][:8]
    before = study.control_targets(rows,3,17)
    a = study.control_targets(rows,7,17);b = study.control_targets(rows,8,17)
    assert not before.mask.any() and not before.y.any()
    np.testing.assert_array_equal(a.y,b.y)
    assert all(np.array_equal(a.y[0],row) for row in a.y)
    for kind,event in product(("assignment","parent"),study.EVENTS):
        joint = choices(a,f"{kind}_joint/{event}")
        np.testing.assert_array_equal(choices(a,f"{kind}_owner/{event}"),joint//4)
        np.testing.assert_array_equal(choices(a,f"{kind}_version/{event}"),joint%4+1)
    assert not a.descriptive["lawful_joint_ssa_graph"] and not a.descriptive["marginals_preserved"]
    assert a.descriptive["joint_components_coherent_within_event"]
    assert len(a.descriptive["real_marginals"]["train"])==192
    assert not np.array_equal(a.y,study.control_targets(rows,7,29).y)


def test_subset_slices_all_source_and_target_metadata(bundles):
    bundle = bundles[7];idx = [5759,0,201]
    cut = study.subset(bundle,idx)
    for key in ("profile_ids","syntax_owners","event_capture_status","event_truth_statements",
                "canonical_visible_prefixes","canonical_output_visible_prefixes"):
        assert cut.descriptive[key]==[bundle.descriptive[key][i] for i in idx]
    assert cut.group_ids==tuple(bundle.group_ids[i] for i in idx)
    with pytest.raises(ValueError):cut.y[0,0]=0
    with pytest.raises(ValueError):study.subset(bundle,[0,0])
    with pytest.raises(ValueError):study.subset(bundle,[])


def test_source_owner_parser_uses_no_oracle_or_labels(monkeypatch,bank):
    rows = deepcopy(bank[0][:8])
    for row in rows:
        row["targets"]="poisoned";row["expected_answer"]="poisoned"
        row["canonical_source"]="poisoned";row["destination_schedule"]="poisoned"
        row["copy_parent_slots"]="poisoned"
    monkeypatch.setattr(study.relationships,"labels_at",lambda *a,**k:pytest.fail("source parser called SSA oracle"))
    result = study.syntax_owners(rows,7)
    for row,owners in zip(rows,result):
        reverse = {name:int(key[1]) for key,name in row["rename_map"].items()}
        assigns = ast.parse(row["source"]).body[4:8]
        assert owners["assignment"]==[reverse[a.targets[0].id] for a in assigns]
        assert owners["parent"]==[reverse[a.value.id] for a in assigns]
    assert study.syntax_owners(rows,3)==[dict(assignment=[-1]*4,parent=[-1]*4)]*8


def test_weighted_source_prior_first_events_perfect_and_owner_conditionals_equal(bank,bundles):
    bundle = bundles[7];train = np.asarray([s=="train" for s in bundle.splits])
    train_rows = [r for r in bank[0] if r["split"]=="train"]
    weights = group_weights(train_rows,17)
    scores = study.syntax_owner_version_prior(bundle,train,weights)
    assert scores.shape==(5760,192) and np.isfinite(scores).all()
    for kind in ("assignment","parent"):
        np.testing.assert_array_equal(choices(scores,f"{kind}_joint/4"),choices(bundle,f"{kind}_joint/4"))
        for event in study.EVENTS:
            np.testing.assert_array_equal(choices(scores,f"{kind}_owner/{event}"),choices(bundle,f"{kind}_owner/{event}"))
            h = head(f"{kind}_version/{event}")
            expected = np.sum(weights[:,None]*bundle.y[train][:,h["indices"]],axis=0)/weights.sum()
            # Whole-graph weighting + cyclic rotations gives equal owner-conditionals.
            np.testing.assert_allclose(scores[:,h["indices"]],np.broadcast_to(expected,(5760,4)),rtol=1e-7,atol=1e-8)
            assert np.isclose(scores[:,head(f"{kind}_joint/{event}")["indices"]].sum(1),1).all()
    assert np.isnan(study.syntax_owner_version_prior(bundles[3],train,weights)).all()
    assert not scores.flags.writeable


def test_dev_versions_and_evaluation_metadata_cannot_change_prior_predictions(bundles):
    bundle = bundles[7];train = np.asarray([s=="train" for s in bundle.splits]);weights = np.ones(train.sum())
    expected = study.syntax_owner_version_prior(bundle,train,weights)
    poison = bundle.y.copy();poison[~train,:] = np.nan
    desc = dict(bundle.descriptive,event_capture_status="forbidden",event_truth_statements="forbidden")
    mutated = replace(bundle,y=poison,descriptive=desc)
    np.testing.assert_array_equal(study.syntax_owner_version_prior(mutated,train,weights),expected)
    changed_train = bundle.y.copy()
    h = head("parent_version/7");changed_train[np.flatnonzero(train)[:,None],np.asarray(h["indices"])[None,:]] = [0,0,0,1]
    changed = study.syntax_owner_version_prior(replace(bundle,y=changed_train),train,weights)
    assert not np.array_equal(changed[:,h["indices"]],expected[:,h["indices"]])


def test_weighted_prior_fallback_uses_only_train_when_an_owner_unseen(bundles):
    bundle = bundles[7]
    owners = np.asarray([r["parent"][3] for r in bundle.descriptive["syntax_owners"]])
    train = np.asarray([s=="train" for s in bundle.splits]) & (owners==0)
    weights = np.arange(1,int(train.sum())+1,dtype=float)
    scores = study.syntax_owner_version_prior(bundle,train,weights)
    h = head("parent_version/7")
    expected = np.sum(weights[:,None]*bundle.y[train][:,h["indices"]],axis=0)/weights.sum()
    np.testing.assert_allclose(scores[:,h["indices"]],np.broadcast_to(expected,(len(owners),4)))


@pytest.mark.parametrize("problem",["dev_train","float_train","wrong_weights","negative_weights","nan_weights","invalid_train_y","control"])
def test_prior_rejects_leakage_and_invalid_inputs(bundles,problem):
    bundle = bundles[7];train = np.asarray([s=="train" for s in bundle.splits]);weights = np.ones(train.sum())
    if problem=="dev_train":train=~train;weights=np.ones(train.sum())
    elif problem=="float_train":train=train.astype(float)
    elif problem=="wrong_weights":weights=weights[:-1]
    elif problem=="negative_weights":weights[0]=-1
    elif problem=="nan_weights":weights[0]=np.nan
    elif problem=="invalid_train_y":
        y=bundle.y.copy();y[0,head("parent_version/7")["indices"]]=0;bundle=replace(bundle,y=y)
    elif problem=="control":bundle=replace(bundle,descriptive=dict(bundle.descriptive,control=True))
    with pytest.raises(ValueError):study.syntax_owner_version_prior(bundle,train,weights)


@pytest.mark.parametrize("seed",[True,-1,1.0,2**63])
def test_control_seed_requires_bounded_strict_integer(bank,seed):
    with pytest.raises(ValueError):study.control_targets(bank[0][:1],7,seed)
