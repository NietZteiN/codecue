"""Source-only checks for generic varied-schedule targets and sham controls."""
from copy import deepcopy

import numpy as np
import pytest

from codecue.binding import relationship_schedule_programs as programs
from codecue.binding import schedule_targets as target


@pytest.fixture(scope="module")
def rows():
    return programs.make_rows(dict(evaluation_role=programs.ROLE,
        numeric_seeds=[401, 503, 607], dataset="/tmp/schedule-targets.jsonl",
        review="/tmp/schedule-targets.json", report="/tmp/schedule-targets.md"))


@pytest.fixture(scope="module")
def repeated(rows):
    return next(row for row in rows if row["destination_schedule"] == [0, 0, 1, 0]
        and row["parent_pattern"] == "ring_successor" and row["query_slot"] == 0
        and row["lexical_realization"] == 0)


def _column(family, **facts):
    return next(c["index"] for c in target.COLUMNS if c["family"] == family
                and all(c.get(name) == value for name, value in facts.items()))


def _choice(bundle, family, index):
    head = next(h for h in target.HEADS if h["name"] == f"{family}/{index}")
    return [candidate for candidate, j in zip(head["candidates"], head["indices"])
            if bundle.mask[0, j] and bundle.y[0, j] == 1]


def test_fixed_schema_has_statement_ids_and_explicit_versions():
    assert target.N_COLUMNS == 232
    assert len(target.HEADS) == 12
    assert [c["index"] for c in target.COLUMNS] == list(range(232))
    assert len({c["name"] for c in target.COLUMNS}) == 232
    assert all("@" not in c["name"] for c in target.COLUMNS)
    assert [h["candidates"] for h in target.HEADS if h["family"] == "current_version"] == [(1, 2, 3, 4)] * 4


def test_repeated_schedule_resolves_v0_version_four(repeated):
    bundle = target.targets([repeated], 8)
    assert [m["id"] for m in bundle.descriptive["version_map_by_case"][0]] == [
        "v0@1", "v1@1", "v2@1", "v3@1", "v0@2", "v0@3", "v1@2", "v0@4"]
    assert [_choice(bundle, "current_definition", slot) for slot in range(4)] == [[7], [6], [2], [3]]
    assert [_choice(bundle, "current_version", slot) for slot in range(4)] == [[4], [2], [1], [1]]
    assert [_choice(bundle, "copy_parent", step) for step in range(4)] == [[1], [1], [2], [6]]


def test_hand_checked_edges_current_status_and_actual_output(repeated):
    bundle = target.targets([repeated], "pre_answer")
    for family, expected in (("direct", {(1, 4), (1, 5), (2, 6), (6, 7)}),
                             ("ancestor", {(1, 4), (1, 5), (2, 6), (6, 7), (2, 7)})):
        positives = {(c["source_node"], c["consumer_node"]) for c in target.COLUMNS
                     if c["family"] == family and bundle.y[0, c["index"]]}
        assert positives == expected
    for family, expected in (("current", {2, 3, 6, 7}), ("obsolete", {0, 1, 4, 5}),
                             ("output_ancestor", {2, 6, 7})):
        assert {c["source_node"] for c in target.COLUMNS if c["family"] == family
                and bundle.y[0, c["index"]]} == expected


def test_masks_keep_wrong_slot_candidates_but_hide_future(repeated):
    bundle = target.targets([repeated], 7)
    j = _column("direct", source_node=0, consumer_node=5)
    assert bundle.mask[0, j] and bundle.y[0, j] == 0
    assert bundle.mask[0, _column("current_definition", slot=0, candidate=3)]
    assert not bundle.mask[0, _column("direct", source_node=6, consumer_node=5)]
    assert not bundle.mask[0, _column("ancestor", source_node=0, consumer_node=3)]
    assert not bundle.mask[0, _column("output_ancestor", source_node=0)]
    assert not np.any(bundle.y[~bundle.mask])


def test_initial_site_never_marks_future_definitions_negative(repeated):
    bundle = target.targets([repeated], 3)
    assert bundle.site_name == "statement:3"
    for column in target.COLUMNS:
        j = column["index"]
        if column["family"] in ("direct", "ancestor", "copy_parent", "output_ancestor"):
            assert not bundle.mask[0, j]
        if column["family"] == "current_definition":
            assert bundle.mask[0, j] == (column["candidate"] < 4)
        if column["family"] == "current_version":
            assert bundle.mask[0, j] == (column["candidate"] == 1)
    assert [_choice(bundle, "current_version", slot) for slot in range(4)] == [[1]] * 4
    assert [_choice(bundle, "current_definition", slot) for slot in range(4)] == [[0], [1], [2], [3]]


def test_query_labels_are_visible_only_at_pre_answer(rows, repeated):
    twin = next(r for r in rows if r["raw_template_id"] == repeated["raw_template_id"]
        and r["numeric_seed"] == repeated["numeric_seed"] and r["lexical_realization"] == 0
        and r["query_slot"] == 3)
    for site in (3, 7):
        bundle = target.targets([repeated, twin], site)
        np.testing.assert_array_equal(bundle.y[0], bundle.y[1])
        assert bundle.descriptive["canonical_visible_prefixes"][0] == bundle.descriptive["canonical_visible_prefixes"][1]
    bundle = target.targets([repeated, twin], 8)
    ids = [c["index"] for c in target.COLUMNS if c["family"] == "output_ancestor"]
    assert not np.array_equal(bundle.y[0, ids], bundle.y[1, ids])


def test_stored_oracles_are_not_coerced_or_used(repeated):
    changed = deepcopy(repeated)
    changed["targets"] = {"obsolete_old_fixed_scaffold": "ignored"}
    changed["expected_answer"] = "not read"
    np.testing.assert_array_equal(target.targets([changed], 7).y, target.targets([repeated], 7).y)


@pytest.mark.parametrize("field,value", [
    ("component_id", "different"), ("split", "wrong"),
    ("destination_schedule", [0, 1, 2, 3]), ("copy_parent_slots", [3, 3, 3, 3]),
    ("query_slot", 2), ("lexical_realization", True),
    ("variable_slots", {"v0": 3}), ("condition", "trace"),
])
def test_source_and_group_metadata_rejected(repeated, field, value):
    row = deepcopy(repeated); row[field] = value
    with pytest.raises(ValueError):
        target.targets([row], 7)


def test_surface_source_renaming_must_match(repeated):
    row = deepcopy(repeated)
    row["source"] = row["source"].replace("item_0 = item_1", "item_0 = item_2", 1)
    with pytest.raises(ValueError, match="renaming"):
        target.targets([row], 7)


def test_case_id_must_identify_actual_source(repeated):
    row = deepcopy(repeated); row["id"] = "different-case"
    with pytest.raises(ValueError, match="case ID"):
        target.targets([row], 7)


def test_actual_future_schedule_cannot_disagree_with_metadata(repeated):
    row = deepcopy(repeated)
    lines = row["canonical_source"].splitlines(); lines[5] = "v1 = v2"
    row["canonical_source"] = "\n".join(lines)
    with pytest.raises(ValueError, match="destinations"):
        target.targets([row], 3)


@pytest.mark.parametrize("site", [True, 0, 4, 9, "3", "statement:8"])
def test_undeclared_sites_rejected(repeated, site):
    with pytest.raises(ValueError, match="sites"):
        target.targets([repeated], site)


def test_read_only_arrays_and_subset_metadata(rows):
    bundle = target.targets(rows[:8], 7)
    with pytest.raises(ValueError):
        bundle.y[0, 0] = 1
    with pytest.raises(ValueError):
        bundle.mask[0, 0] = True
    small = target.subset(bundle, [4, 1])
    assert small.case_ids == (bundle.case_ids[4], bundle.case_ids[1])
    assert small.descriptive["version_map_by_case"] == [bundle.descriptive["version_map_by_case"][i] for i in (4, 1)]
    np.testing.assert_array_equal(small.y, bundle.y[[4, 1]])
    for bad in ([], [0, 0], [-1], [8], [1.5]):
        with pytest.raises(ValueError):
            target.subset(bundle, bad)


def test_controls_tie_lexical_query_relatives_and_sites(rows, repeated):
    twins = [r for r in rows if r["raw_template_id"] == repeated["raw_template_id"]
             and r["numeric_seed"] == repeated["numeric_seed"]]
    assert len(twins) == 8
    initial = target.control_targets(twins, 3, 17)
    assert all(np.array_equal(initial.y[0], row) for row in initial.y)
    final = target.control_targets(twins, 7, 17)
    assert all(np.array_equal(final.y[0], row) for row in final.y)
    output = target.control_targets(twins, 8, 17)
    nonoutput = [c["index"] for c in target.COLUMNS if c["family"] != "output_ancestor"]
    np.testing.assert_array_equal(final.y[:, nonoutput], output.y[:, nonoutput])
    for query in range(4):
        ix = [i for i, row in enumerate(twins) if row["query_slot"] == query]
        np.testing.assert_array_equal(output.y[ix[0]], output.y[ix[1]])
    assert output.descriptive["marginals_preserved"] is False
    assert output.descriptive["lawful_joint_ssa_graph"] is False
    assert output.descriptive["real_marginals"] != output.descriptive["control_marginals"]


def test_control_is_deterministic_one_hot_masked_and_seeded(rows):
    source = rows[:16]
    a = target.control_targets(source, 7, 29)
    b = target.control_targets(source, 7, 29)
    c = target.control_targets(source, 7, 43)
    np.testing.assert_array_equal(a.y, b.y)
    assert not np.array_equal(a.y, c.y)
    assert not np.any(a.y[~a.mask])
    for head in target.HEADS:
        assert np.all(a.y[:, head["indices"]].sum(1) == 1)
    for node in range(8):
        assert np.all(a.y[:, _column("current", source_node=node)] +
                      a.y[:, _column("obsolete", source_node=node)] == 1)


@pytest.mark.parametrize("seed", [True, -1, 2**63, "17"])
def test_invalid_control_seed_rejected(repeated, seed):
    with pytest.raises(ValueError, match="seed"):
        target.control_targets([repeated], 7, seed)


def test_full_bank_support_keeps_rare_and_absent_classes(rows):
    bundle = target.targets(rows, 7)
    support = target.training_support(bundle)
    assert support["structural_groups"] == 10
    assert support["development_labels_used_for_eligibility"] is False
    assert len(support["columns"]) == 232
    assert len(support["categorical_heads"]) == 12
    heads = {head["head"]: head for head in support["categorical_heads"]}
    assert heads["copy_parent/1"]["unsupported_observed_train_classes"] == [0, 1]
    assert heads["copy_parent/2"]["unsupported_observed_train_classes"] == [0, 1]
    assert heads["copy_parent/3"]["unsupported_observed_train_classes"] == [2, 4]
    assert all(not head["development_only_classes"] for head in heads.values())
    assert all(head["evaluated_choices_removed"] is False for head in heads.values())
    assert heads["current_version/0"]["candidates"] == [1, 2, 3, 4]
    assert heads["current_version/0"]["absent_train_classes"] == [1]


def test_support_eligibility_ignores_development_outcomes(rows):
    bundle = target.targets(rows, 7)
    original = target.training_support(bundle)
    altered = np.array(bundle.y, copy=True)
    dev = np.asarray(bundle.splits) == "development"
    altered[dev] = 1-altered[dev]
    from dataclasses import replace
    changed = target.training_support(replace(bundle, y=altered))
    assert changed["eligible_boolean_indices"] == original["eligible_boolean_indices"]
    assert [h["eligible_categorical"] for h in changed["categorical_heads"]] == [
        h["eligible_categorical"] for h in original["categorical_heads"]]
    assert changed["columns"] == original["columns"]


def test_initial_support_declares_constants_and_missing(rows):
    support = target.training_support(target.targets(rows, 3))
    assert support["eligible_boolean_indices"] == []
    heads = {head["head"]: head for head in support["categorical_heads"]}
    assert heads["current_version/0"]["constant"]
    assert heads["current_version/0"]["observed_train_classes"] == [1]
    assert heads["copy_parent/0"]["missing"]
    assert not heads["current_definition/0"]["eligible_categorical"]


def test_support_requires_training_and_declared_threshold(rows):
    bundle = target.targets([r for r in rows if r["split"] == "development"][:8], 7)
    with pytest.raises(ValueError, match="TRAIN"):
        target.training_support(bundle)
    for threshold in (True, 0, -1, 3.0):
        with pytest.raises(ValueError, match="positive integer"):
            target.training_support(bundle, threshold)
