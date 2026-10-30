"""Bounded temporary-source tests; no actual bank or scientific outcomes opened."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path

import pytest

from codecue.binding import relationship_schedule_programs as prior
from codecue.binding import schedule_diversity_programs as study


@pytest.fixture(scope="module")
def config(tmp_path_factory):
    folder = tmp_path_factory.mktemp("diversity-source-fixture")
    routing = []
    for parents in product(*(tuple(s for s in range(4) if s != d) for d in range(4))):
        routing.append(dict(evaluation_role="discovery_relationship_routing_v1", split="train", condition="neutral",
            canonical_source=prior._source((1, 2, 3, 4), (0, 1, 2, 3), parents, 0)))
    schedule = [dict(canonical_source=prior._source((1, 2, 3, 4), destinations,
        tuple((slot + offset) % 4 for slot in destinations), 0),
        evaluation_role=prior.ROLE, split="train", condition="neutral")
        for destinations in prior.REPEATED_SCHEDULES for offset in prior.PARENT_PATTERNS.values()]
    excluded = []
    for name, rows in (("routing_sources_v1", routing), ("schedule_sources_v1", schedule)):
        data = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode()
        path = folder / (name + ".jsonl"); path.write_bytes(data)
        excluded.append(dict(name=name, path=str(path), sha256=hashlib.sha256(data).hexdigest()))
    return dict(evaluation_role=study.ROLE, candidate_seed=202610281,
        numeric_seeds=[751, 857, 967], dataset=str(folder / "sources.jsonl"),
        review=str(folder / "review.json"), report=str(folder / "sources.md"), excluded_graph_sources=excluded)


@pytest.fixture(scope="module")
def bank(config):
    return study.make_rows(config)


@pytest.fixture(scope="module")
def checked(config, bank):
    return study.validate_rows(config, bank, independent=True)


def test_finite_candidate_space_has_declared_independent_parents(config):
    candidates = study._candidate_order(config["candidate_seed"])
    assert len(candidates) == 18468 < 50000
    assert Counter(profile for profile, _, _ in candidates) == {
        (2, 1, 1, 0): 11664, (3, 1, 0, 0): 3888, (2, 2, 0, 0): 2916}
    assert all(len(dest) == len(parents) == 4 and all(d != p for d, p in zip(dest, parents))
               for _, dest, parents in candidates)
    assert candidates == study._candidate_order(config["candidate_seed"])
    assert candidates != study._candidate_order(config["candidate_seed"] + 1)


def test_discarded_fully_updated_profile_is_exhausted_before_generation(config):
    excluded, reviews, deviation = study._excluded(config)
    assert study._routing_universe() <= excluded
    assert reviews[0]["rows"] == 81
    assert deviation["new_canonical_families_available"] == 0
    assert deviation["initial_profile_generated"] is False
    assert deviation["initial_profile_counted_as_new"] is False
    assert deviation["decision_before_generation"] is True
    assert deviation["raw_profile_candidates"] == 1944
    # Destination-order relabeling maps any permutation to the old81 choices.
    for destinations in prior.SLOT_PERMUTATIONS:
        permutation = {slot: index for index, slot in enumerate(destinations)}
        parents = tuple((slot + 1) % 4 for slot in destinations)
        relabeled = tuple(permutation[parent] for parent in parents)
        assert study._graph(destinations, parents) == study._graph((0, 1, 2, 3), relabeled)
    assert (1, 1, 1, 1) not in study.PROFILES


def test_complete_new_graph_factorial_and_named_exclusion_scope(config, bank, checked):
    assert len(bank) == len({row["id"] for row in bank}) == 5760
    assert checked["split_rows"] == {"train": 4320, "development": 1440}
    assert checked["canonical_graph_families"] == 60
    assert checked["split_canonical_graph_units"] == {"train": 45, "development": 15}
    assert checked["profile_split_graph_units"] == {
        key: {"train": 15, "development": 5} for key in ("2_1_1_0", "3_1_0_0", "2_2_0_0")}
    excluded, _, _ = study._excluded(config)
    assert not {row["canonical_graph_sha256"] for row in bank} & excluded
    assert all(value == 0 for value in checked["cross_split_overlap"].values())
    assert checked["independent_python_programs"] == 8640
    assert checked["independent_python_passed"]
    assert checked["fully_class_balanced"] is False


def test_rotated_slot_version_support_is_complete_but_not_balanced(bank, checked):
    assert checked["maximum_assignment_version"] == 4
    assert checked["train_minimum_current_version_class_graph_groups"] == 15
    support = checked["current_version_class_support"]
    for slot in range(4):
        assert {v: cell["rows"] for v, cell in support["train"][str(slot)].items()} == {
            "1": 1800, "2": 1080, "3": 1080, "4": 360}
        assert {v: cell["rows"] for v, cell in support["development"][str(slot)].items()} == {
            "1": 600, "2": 360, "3": 360, "4": 120}
        assert min(cell["graph_groups"] for cell in support["train"][str(slot)].values()) >= 3
        assert all(cell["graph_groups"] for cell in support["development"][str(slot)].values())
    groups = defaultdict(list)
    for row in bank:
        groups[row["component_id"]].append(row)
    for relatives in groups.values():
        assert len(relatives) == 96
        assert len({r["split"] for r in relatives}) == 1
        assert {r["slot_rotation"] for r in relatives} == set(range(4))
        assert {r["numeric_seed"] for r in relatives} == {751, 857, 967}
        assert {r["lexical_realization"] for r in relatives} == {0, 1}
        assert {r["query_slot"] for r in relatives} == set(range(4))
    assert any(len({(p-d) % 4 for d, p in zip(row["destination_schedule"], row["copy_parent_slots"])}) > 1
               for row in bank)


def test_actual_high_versions_query_ancestors_and_obsolete_definitions(bank):
    row = next(r for r in bank if r["profile_id"] == "3_1_0_0")
    final = row["targets"]["prefix_relationships"][-1]
    assert max(node["version"] for node in final["version_nodes"]) == 4
    assert any(node["statement"] >= 4 and node["status"] == "obsolete" for node in final["version_nodes"])
    relatives = [r for r in bank if r["raw_template_id"] == row["raw_template_id"]
        and r["numeric_seed"] == row["numeric_seed"] and r["lexical_realization"] == row["lexical_realization"]]
    assert len(relatives) == 4
    assert all(r["targets"]["prefix_relationships"] == relatives[0]["targets"]["prefix_relationships"] for r in relatives)
    assert len({tuple(r["targets"]["final_query_relationships"]["output"]["direct_referents"]) for r in relatives}) == 4
    for checkpoint, labels in enumerate(row["targets"]["prefix_relationships"]):
        assert "output" not in labels and labels["output_visible"] is False
        assert all(node["statement"] <= checkpoint for node in labels["version_nodes"])


def test_exhausted_quota_fails_without_redefinition(config, monkeypatch):
    candidates = study._candidate_order(config["candidate_seed"])
    monkeypatch.setattr(study, "_candidate_order", lambda seed: candidates[:5])
    with pytest.raises(ValueError, match="finite graph search exhausted"):
        study.make_rows(config)
    assert not Path(config["dataset"]).exists()
    assert not Path(config["review"]).exists()


@pytest.mark.parametrize("field,value", [
    ("evaluation_role", "confirmation"), ("candidate_seed", True), ("candidate_seed", -1),
    ("numeric_seeds", [1, 2, 3]), ("numeric_seeds", [751, 857, True]),
    ("excluded_graph_sources", []), ("profiles", [[1, 1, 1, 1]]),
])
def test_bad_config_rejected_before_exclusion_or_generation(config, field, value, monkeypatch):
    bad = deepcopy(config); bad[field] = value
    monkeypatch.setattr(study, "_excluded", lambda *_: pytest.fail("exclusions must not be opened"))
    with pytest.raises(ValueError):
        study.make_rows(bad)


@pytest.mark.parametrize("field", ["source", "expected_answer", "component_id", "targets", "split", "slot_rotation"])
def test_mutated_sources_targets_and_relatives_rejected(config, bank, field):
    changed = list(bank); changed[0] = deepcopy(bank[0])
    if field == "expected_answer": changed[0][field] += 1
    elif field == "targets": changed[0][field]["prefix_relationships"][5]["direct_def_use_edges"] = []
    else: changed[0][field] = "changed"
    with pytest.raises(ValueError, match="complete exact"):
        study.validate_rows(config, changed)


def test_pinned_old_bank_changes_fail_before_sources(config):
    bad = deepcopy(config); bad["excluded_graph_sources"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SHA256"):
        study.make_rows(bad)


@pytest.mark.parametrize("field,value", [("evaluation_role", "sealed_final"),
    ("evaluation_role", "discovery_relationship_schedule_targets_v1"),
    ("split", "test"), ("condition", "misleading")])
def test_prior_roles_and_splits_rejected_even_with_consistent_sha(config, tmp_path, field, value):
    bad = deepcopy(config)
    row = json.loads(Path(bad["excluded_graph_sources"][0]["path"]).read_text().splitlines()[0])
    row[field] = value
    payload = (json.dumps(row) + "\n").encode()
    path = tmp_path / "prior.jsonl"; path.write_bytes(payload)
    bad["excluded_graph_sources"][0].update(path=str(path), sha256=hashlib.sha256(payload).hexdigest())
    with pytest.raises(ValueError, match="discovery-only prior source role"):
        study.make_rows(bad)


def test_outputs_cannot_alias_named_inputs_or_sealed_paths(config):
    bad = deepcopy(config); bad["dataset"] = bad["excluded_graph_sources"][0]["path"]
    with pytest.raises(ValueError, match="nonoverlapping"):
        study.make_rows(bad)
    bad = deepcopy(config); bad["dataset"] = str(Path(bad["dataset"]).with_name("sealed_final.jsonl"))
    with pytest.raises(ValueError):
        study.make_rows(bad)


def test_immutable_publication_is_targets_only(config, checked, monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(study, "code_identity", lambda: {"source_sha256": "synthetic-source-fixture"})
    monkeypatch.setattr(experiment_log, "note_artifact", lambda *_: None)
    monkeypatch.setattr(study, "_validate", lambda *_: deepcopy(checked))
    result = study.build(config)
    assert result["new_model_queries"] == result["new_fits"] == 0
    assert result["learned_readout_compatible"] is False
    assert result["targets_prepared_only"] is True
    manifest_path = Path(config["dataset"]).with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text())
    assert manifest["sha256"] == hashlib.sha256(Path(config["dataset"]).read_bytes()).hexdigest()
    assert manifest["rows"] == 5760 and manifest["canonical_graph_families"] == 60
    assert manifest["slot_complete_version_domain"] is True and manifest["fully_class_balanced"] is False
    assert study.build(config) == result
    Path(config["report"]).write_text("changed")
    with pytest.raises(ValueError, match="immutable"):
        study.build(config)
