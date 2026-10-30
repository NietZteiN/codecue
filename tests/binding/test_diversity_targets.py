"""Source-only diversity target adapter tests using temporary old-bank fixtures."""
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

import numpy as np
import pytest

from codecue.binding import diversity_targets as study
from codecue.binding import schedule_diversity_programs as programs
from codecue.binding import schedule_targets as original

_build_family_map = study._family_map


@pytest.fixture(scope="module")
def bank(tmp_path_factory):
    folder = tmp_path_factory.mktemp("diversity-target-fixture")
    old_routing = [dict(evaluation_role="discovery_relationship_routing_v1", condition="neutral", split="train",
        canonical_source=programs.prior._source((1,2,3,4),(0,1,2,3),parents,0))
        for parents in product(*(tuple(s for s in range(4) if s != d) for d in range(4)))]
    old_schedule = [dict(evaluation_role=programs.prior.ROLE, condition="neutral", split="train",
        canonical_source=programs.prior._source((1,2,3,4),dest,tuple((d+offset)%4 for d in dest),0))
        for dest in programs.prior.REPEATED_SCHEDULES for offset in programs.prior.PARENT_PATTERNS.values()]
    exclusions=[]
    for name,rows in (("routing_sources_v1",old_routing),("schedule_sources_v1",old_schedule)):
        path=folder/(name+".jsonl");payload="".join(json.dumps(r)+"\n" for r in rows).encode();path.write_bytes(payload)
        exclusions.append(dict(name=name,path=str(path),sha256=hashlib.sha256(payload).hexdigest()))
    config=dict(evaluation_role=programs.ROLE,candidate_seed=20261028,numeric_seeds=[751,857,967],
        dataset=str(folder/"sources.jsonl"),review=str(folder/"review.json"),report=str(folder/"sources.md"),
        excluded_graph_sources=exclusions)
    selected,*_=programs._selection(config)
    rows=programs._make_rows(config,selected)
    family_map={graph:(profile,index,dest,parents,"train" if index<15 else "development")
        for profile in programs.PROFILES for index,(graph,dest,parents) in enumerate(selected[profile])}
    return config,rows,family_map


@pytest.fixture(autouse=True)
def fixture_map(monkeypatch,bank):
    monkeypatch.setattr(study,"_family_map",lambda:bank[2])


@pytest.fixture(scope="module")
def full_bundles(bank):
    return {site:study.targets(bank[1],site) for site in study.SITES}


def test_private_registered_engine_preserves_old_module(bank):
    assert original.MAX_ROWS==2016 and study.MAX_ROWS==5760
    assert study.N_COLUMNS==232 and study.COLUMNS==original.COLUMNS and study.HEADS==original.HEADS
    assert study.TargetBundle is not original.TargetBundle
    assert sys.modules[study.TargetBundle.__module__].TargetBundle is study.TargetBundle
    assert original._records is not study._CORE._records
    with pytest.raises(ValueError):original.targets(bank[1][:1],7)


def test_selected_family_map_is_reconstructed_without_full_bank(monkeypatch,bank):
    _build_family_map.cache_clear()
    monkeypatch.setattr(study,"_published_recipe",lambda:bank[0])
    try:
        selected=_build_family_map()
        assert dict(selected)==bank[2] and len(selected)==60
        with pytest.raises(TypeError):selected["new"]=None
    finally:
        _build_family_map.cache_clear()


def test_stripped_capture_records_need_no_oracle_fields(bank):
    rows=[{key:value for key,value in row.items() if key not in ("targets","expected_answer")}
          for row in bank[1][:8]]
    bundle=study.targets(rows,7)
    assert bundle.y.shape==(8,232) and bundle.case_ids==tuple(r["id"] for r in rows)
    assert all(r["evaluation_role"]==programs.ROLE for r in rows)
    assert bundle.descriptive["learned_version_resolution_performed"] is False


def test_complete_bank_geometry_all_dev_families_and_class_support(bank,full_bundles):
    rows=bank[1]
    assert len(rows)==5760 and sum(r["split"]=="train" for r in rows)==4320
    assert len({r["component_id"] for r in rows if r["split"]=="development"})==15
    bundle=full_bundles[7];support=study.training_support(bundle)
    assert bundle.y.shape==(5760,232) and support["structural_groups"]==45
    for slot in range(4):
        head=next(h for h in support["categorical_heads"] if h["head"]==f"current_version/{slot}")
        assert head["observed_train_classes"]==[1,2,3,4]
        assert [c["train_groups"] for c in head["classes"]]==[45,30,30,15]
        assert [c["development_groups"] for c in head["classes"]]==[15,10,10,5]
        assert not head["development_only_classes"] and head["eligible_categorical"]


def test_site3_masking_never_exposes_future_schedule_labels(full_bundles):
    bundle=full_bundles[3]
    assert np.all(bundle.y==bundle.y[0]) and np.all(bundle.mask==bundle.mask[0])
    assert not np.any(bundle.y[~bundle.mask])
    for spec in study.COLUMNS:
        j=spec["index"]
        if spec["family"] in ("direct","ancestor","copy_parent","output_ancestor"):
            assert not bundle.mask[:,j].any()
        if spec["family"]=="current_version":
            assert bundle.mask[:,j].all()==(spec["candidate"]==1)


def test_graph_tasks_and_masks_unchanged_by_visible_query(full_bundles):
    before,after=full_bundles[7],full_bundles[8]
    indices=[c["index"] for c in study.COLUMNS if c["family"]!="output_ancestor"]
    np.testing.assert_array_equal(before.y[:,indices],after.y[:,indices])
    np.testing.assert_array_equal(before.mask[:,indices],after.mask[:,indices])
    for spec in study.COLUMNS:
        if spec["family"]=="output_ancestor":assert after.mask[:,spec["index"]].all()


def test_cyclic_high_version_moves_to_every_slot(bank):
    row=next(r for r in bank[1] if r["profile_id"]=="3_1_0_0")
    rows=[r for r in bank[1] if r["component_id"]==row["component_id"] and r["numeric_seed"]==751
          and r["lexical_realization"]==0 and r["query_slot"]==0]
    assert len(rows)==4
    bundle=study.targets(rows,7)
    for slot in range(4):
        j=next(c["index"] for c in study.COLUMNS if c["family"]=="current_version" and c["slot"]==slot and c["candidate"]==4)
        assert bundle.y[:,j].sum()==1
    assert max(m["version"] for maps in bundle.descriptive["version_map_by_case"] for m in maps)==4


def test_control_ties_lexical_queries_and_assignment_boundary(bank):
    rows=bank[1][:8]
    a=study.control_targets(rows,3,17);b=study.control_targets(rows,7,17);c=study.control_targets(rows,8,17)
    assert all(np.array_equal(a.y[0],y) for y in a.y)
    assert all(np.array_equal(b.y[0],y) for y in b.y)
    other=[s["index"] for s in study.COLUMNS if s["family"]!="output_ancestor"]
    np.testing.assert_array_equal(b.y[:,other],c.y[:,other])
    for query in range(4):np.testing.assert_array_equal(c.y[query],c.y[query+4])
    assert c.descriptive["marginals_preserved"] is False and c.descriptive["lawful_joint_ssa_graph"] is False
    assert not np.any(c.y[~c.mask])


def test_subset_preserves_target_maps_and_readonly_arrays(full_bundles):
    bundle=full_bundles[7];selected=study.subset(bundle,[0,100,5759])
    assert selected.case_ids==tuple(bundle.case_ids[i] for i in (0,100,5759))
    assert selected.descriptive["version_map_by_case"]==[bundle.descriptive["version_map_by_case"][i] for i in (0,100,5759)]
    with pytest.raises(ValueError):selected.y[0,0]=0


@pytest.mark.parametrize("field,value",[("evaluation_role","discovery_relationship_schedule_targets_v1"),
    ("split","test"),("split","development"),("graph_selection_index",True),
    ("slot_rotation",True),("slot_rotation",3),("numeric_seed",1),("query_slot",True),
    ("profile_id","1_1_1_1"),("canonical_graph_sha256","0"*64),("component_id","different"),
    ("base_id","different"),("paired_group_id","different"),("id","different"),
    ("parent_pattern","ring_successor"),("update_count_profile",[True,1,1,0]),
    ("destination_schedule",[0,1,2,3]),("copy_parent_slots",[0,0,0,0]),
    ("variable_slots",{"v0":False,"v1":1,"v2":2,"v3":3})])
def test_bad_metadata_is_rejected_without_role_coercion(bank,field,value):
    row=deepcopy(bank[1][0]);row[field]=value
    with pytest.raises(ValueError):study.targets([row],7)


def test_changed_numeric_or_surface_source_rejected(bank):
    row=deepcopy(bank[1][0]);row["canonical_source"]=row["canonical_source"].replace("=", "= 0 +",1)
    with pytest.raises(ValueError,match="program differs"):study.targets([row],3)
    row=deepcopy(bank[1][0]);row["source"]=row["source"].replace("item_0","cell_0")
    with pytest.raises(ValueError,match="program differs"):study.targets([row],3)
    with pytest.raises(ValueError,match="unique case ID"):study.targets([bank[1][0],bank[1][0]],7)


def test_pinned_json_verifies_bound_and_exact_bytes(tmp_path):
    path=tmp_path/"recipe.json";payload=b'{"source_only": true}\n';path.write_bytes(payload)
    assert study._pinned_json(path,hashlib.sha256(payload).hexdigest())=={"source_only":True}
    with pytest.raises(ValueError,match="SHA256"):study._pinned_json(path,"0"*64)
    other=tmp_path/"alias.json";other.symlink_to(path)
    with pytest.raises(ValueError,match="nonsymlink"):study._pinned_json(other,hashlib.sha256(payload).hexdigest())


def test_published_recipe_rejects_consistently_replaced_metadata(monkeypatch):
    monkeypatch.setattr(study,"_pinned_json",lambda *_: {"status":"complete","evaluation_role":"other"})
    with pytest.raises(ValueError,match="exact published"):study._published_recipe()
