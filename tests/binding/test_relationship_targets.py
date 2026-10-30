"""Target visibility, lawful graph reconstruction, controls and metric semantics."""
from collections import Counter, defaultdict
from copy import deepcopy
from itertools import product
import json

import numpy as np
import pytest

from codecue.binding import relationship_targets as study
from codecue.binding.programs import rename


def row(case, values=(2, 3, 5, 7), parents=(1, 0, 1, 2), group="g0", split="train", lexical=0):
    source = "\n".join([*(f"v{i} = {value}" for i, value in enumerate(values)),
                          *(f"v{i} = v{parent}" for i, parent in enumerate(parents)), "v0"])
    mapping = {f"v{i}": f"{'dev_' if split == 'development' else ''}{'item' if lexical == 0 else 'cell'}_{i}" for i in range(4)}
    return dict(id=case, split=split, cluster_id=group, template_id=group, base_id=case.rsplit(":", 1)[0],
        canonical_source=source, source=rename(source, mapping), rename_map=mapping,
        variable_slots={f"v{i}": i for i in range(4)}, lexical_realization=lexical,
        expected_answer="DO NOT READ", raw_response="DO NOT READ")


def index(bundle, family, slots=None, **fields):
    return next(spec["index"] for spec in bundle.columns if spec["family"] == family
        and (slots is None or spec["slots"] == list(slots)) and all(spec.get(key) == value for key, value in fields.items()))


@pytest.mark.parametrize("site", range(9))
def test_all_prefix_masks_match_visibility_and_fixed_candidate_graphs(site):
    bundle = study.targets([row("one")], site)
    cp = min(site, 7)
    assert bundle.y.shape == bundle.mask.shape == (1, 364)
    assert bundle.columns == study.COLUMNS and bundle.site_name == study.SITES[site]
    assert np.all(bundle.y[~bundle.mask] == 0)
    assert bundle.numeric_mask.sum() == min(cp+1, 4)
    assert np.isnan(bundle.numeric_truth[~bundle.numeric_mask]).all()
    assert bundle.parent_mask.sum() == max(cp-3, 0)
    for spec in bundle.columns:
        valid = bundle.mask[0, spec["index"]]
        if spec["family"] in ("direct", "ancestor"):
            parent = study.NODE_INDEX[spec["source_node"]]; consumer = study.NODE_INDEX[spec["consumer_node"]]
            possible = study.POSSIBLE_DIRECT if spec["family"] == "direct" else study.POSSIBLE_ANCESTOR
            assert valid == (consumer <= cp and possible[parent, consumer])
            if valid: assert parent < consumer and consumer >= 4
        if spec["family"] == "output_ancestor": assert valid == (site == 8)
    assert bundle.descriptive["learned_version_resolution"] is False
    with pytest.raises(ValueError): bundle.y[0, 0] = 0
    with pytest.raises(ValueError): bundle.mask.setflags(write=True)


def test_numeric_current_versions_and_old_parent_referents_are_separate():
    bundle = study.targets([row("one")], 7)
    np.testing.assert_equal(bundle.numeric_truth, [[3, 3, 3, 3]])
    np.testing.assert_equal(bundle.parent_truth, [[1, 0, 1, 2]])
    direct = study.reconstruct_parent_graph(bundle, bundle.y)["direct"][0]
    assert direct[1, 4] and direct[4, 5] and direct[5, 6] and direct[6, 7]
    assert not direct[0].any()  # obsolete initial v0 never supplies a copy.
    assert bundle.y[0, index(bundle, "equal", (0, 1))] == 1


def test_canonical_surface_labels_and_all_81_parent_graphs_reconstruct_exactly():
    rows = [row(str(i), parents=parents) for i, parents in enumerate(product(*study.PARENT_CANDIDATES))]
    bundle = study.targets(rows, 7)
    reconstructed = study.reconstruct_parent_graph(bundle, bundle.y)
    assert len({array.tobytes() for array in reconstructed["direct"]}) == 81
    for family in ("direct", "ancestor"):
        for spec in bundle.columns:
            if spec["family"] == family:
                np.testing.assert_equal(bundle.y[:, spec["index"]], reconstructed[family][:,
                    study.NODE_INDEX[spec["source_node"]], study.NODE_INDEX[spec["consumer_node"]]])
    report = study.metrics(bundle, bundle.y)
    assert report["parent_graph"]["whole_graph_accuracy"] == 1
    assert report["parent_graph"]["macro_parent_accuracy"] == 1
    assert report["raw_binary_exact_graph_accuracy"] == {"direct": 1, "ancestor": 1}
    assert all(head["majority_prior"] == pytest.approx(1/3) for head in report["parent_graph"]["heads"])


def test_parent_argmax_ties_remain_raw_lowest_candidate_and_no_oracle_prediction():
    bundle = study.targets([row("one", parents=(3, 3, 3, 2))], 7)
    zeros = np.zeros_like(bundle.y)
    predicted = study.reconstruct_parent_graph(bundle, zeros)["parent_predictions"]
    np.testing.assert_equal(predicted, [[1, 0, 0, 0]])
    assert study.metrics(bundle, zeros)["parent_graph"]["whole_graph_accuracy"] == 0


def test_future_program_differences_cannot_change_early_targets():
    first = row("same", parents=(1, 0, 1, 2))
    second = row("same", parents=(3, 2, 3, 0))
    a, b = study.targets([first], 3), study.targets([second], 3)
    np.testing.assert_equal(a.y, b.y); np.testing.assert_equal(a.mask, b.mask)
    assert not any(a.mask[0, spec["index"]] for spec in a.columns if spec["family"] == "output_ancestor")


def test_initialization_prefix_hides_future_values_outside_categorical_domain():
    first = row("same", values=(2, 3, 5, 7))
    second = row("same", values=(2, 0, 17, 7))
    a, b = study.targets([first], 0), study.targets([second], 0)
    np.testing.assert_equal(a.y, b.y); np.testing.assert_equal(a.mask, b.mask)
    np.testing.assert_equal(a.numeric_truth, b.numeric_truth)
    with pytest.raises(ValueError, match="fixed nonzero"): study.targets([second], 1)


def test_primary_18_semantic_cells_and_train_only_support_rule():
    values = [(2, 3, 5, 7), (2, 3, 3, 7), (-2, 5, 3, 7), (5, -2, 3, 7)]
    rows = [row(f"{g}:{v}", values=value, group=f"g{g}") for g in range(3) for v, value in enumerate(values)]
    bundle = study.targets(rows, 3)
    fixed = study.fixed_primary_boolean_indices(bundle)
    assert Counter(bundle.columns[j]["family"] for j in fixed) == {
        "less_than": 12, "equal": 2, "sum_equals_third": 2, "difference_equals_third": 2}
    support = study.training_support(bundle, min_class_groups=2)
    assert support["eligibility_split"] == "train"
    for cell in support["columns"]:
        if cell["family"] in study.ALGEBRAIC_FAMILIES:
            assert cell["eligible_boolean"] == (cell["positive_groups"] >= 2 and cell["negative_groups"] >= 2)
    dev = study.targets([row("dev", split="development")], 3)
    with pytest.raises(ValueError, match="TRAIN-only"): study.training_support(dev, min_class_groups=1)
    with pytest.raises(ValueError, match="four visible"): study.fixed_primary_boolean_indices(study.targets(rows, 2))


def test_scalar_value_derived_relations_use_predictions_clip_and_ties_to_even():
    bundle = study.targets([row("one")], 3)
    scores = np.array(bundle.y, copy=True); scores[0, :4] = [1.5, 2.5, 100, -100]
    np.testing.assert_equal(study.value_predictions(bundle, scores), [[2, 2, 64, -64]])
    derived = study.derived_relations(bundle, scores)
    assert derived[0, index(bundle, "equal", (0, 1))] == 1
    assert derived[0, index(bundle, "difference", (2, 3))] == 128
    assert np.isnan(derived[:, [spec["index"] for spec in bundle.columns if spec["family"] == "parent"]]).all()
    assert derived[0, index(bundle, "equal", (0, 1))] != bundle.y[0, index(bundle, "equal", (0, 1))]


def test_categorical_value_baseline_is_primary_and_separate_from_scalar_predictions():
    bundle = study.targets([row("one")], 3)
    scores = np.array(bundle.y, copy=True); scores[:, :4] = 14  # scalar predictions deliberately wrong.
    np.testing.assert_equal(study.categorical_value_predictions(bundle, scores), bundle.numeric_truth)
    primary = study.derived_categorical_relations(bundle, scores)
    for spec in bundle.columns:
        if spec["family"] in study.ALGEBRAIC_FAMILIES:
            np.testing.assert_equal(primary[:, spec["index"]], bundle.y[:, spec["index"]])
    assert not bundle.descriptive["whole_pipelines_parameter_matched"]
    assert bundle.descriptive["pipeline_parameter_counts_4096"] == {
        "direct_18_boolean": 73746, "categorical_value": 524416, "scalar_value": 16388}


def test_categorical_value_class_support_and_eval_out_of_training_support():
    train = study.targets([row("train")], 3); support = study.training_support(train, min_class_groups=1)
    dev = study.targets([row("dev", values=(2, 4, 5, 7), split="development")], 3)
    report = study.metrics(dev, dev.y, training_support_info=support)
    assert all(head["accuracy"] == 1 for head in report["value_categorical"])
    assert report["value_categorical"][1]["out_of_training_support_rows"] == 1
    assert report["value_categorical"][0]["out_of_training_support_rows"] == 0


def test_family_macro_weights_families_equally_and_accepts_seed_mean_correctness():
    truth = np.array([[False]*5, [True]*5])
    families = ("equal", "less_than", "less_than", "sum_equals_third", "difference_equals_third")
    correct = np.array([[1, 0, 0, 1, 1], [1, 0, 0, 1, 1]], dtype=float)
    result = study.family_macro_balanced_accuracy(truth, correct, families)
    assert result["value"] == .75  # cell-macro would incorrectly be .6.
    assert study.family_macro_balanced_accuracy(truth, correct/3, families)["value"] == .25
    missing = study.family_macro_balanced_accuracy(truth[:1], correct[:1], families)
    assert not missing["qualified"] and missing["value"] is None and missing["missing_class_cells"] == list(range(5))
    weighted = study.family_macro_balanced_accuracy(truth, correct, families, [1, 0])
    assert not weighted["qualified"]  # same invalid class-denominator draw for every method.


def test_task_correctness_retains_per_row_per_cell_and_undefined_structural_baseline():
    bundle = study.targets([row("one"), row("two", values=(2, 3, 3, 7))], 3)
    derived = study.derived_categorical_relations(bundle, bundle.y)
    result = study.task_correctness(bundle, derived)
    assert result["algebraic_correct"].shape == result["algebraic_truth"].shape == (2, 18)
    assert result["algebraic_correct"].all()
    assert np.isnan(result["parent_correct"]).all() and np.isnan(result["whole_graph_correct"]).all()


def test_metrics_report_constants_group_denominators_and_raw_scores_not_probabilities():
    rows = [row(f"g{g}:{v}", values=value, group=f"g{g}") for g in range(2)
            for v, value in enumerate(((2, 3, 5, 7), (2, 3, 3, 7)))]
    bundle = study.targets(rows, 3)
    report = study.metrics(bundle, bundle.y, eligible_boolean_indices=study.fixed_primary_boolean_indices(bundle))
    assert report["binary_scores_are_probabilities"] is False
    assert report["constant_boolean_cells"] > 0
    assert report["algebraic_family_macro_balanced_accuracy"]["value"] is None  # no selective dropping of constant fixed cells.
    nonconstant = [cell for cell in report["binary_cells"] if not cell["constant_label"]]
    assert all(cell["balanced_accuracy"] == 1 and cell["average_precision"] == 1 for cell in nonconstant)
    assert all(len(cell["per_group"]) == 2 for cell in report["binary_cells"])
    json.dumps(report, allow_nan=False)
    compact = study.metrics(bundle, bundle.y, include_per_group=False)
    assert compact["per_group_cells_included"] is False
    assert all(cell["per_group"] == [] for cell in compact["binary_cells"])
    for full, brief in zip(report["binary_cells"], compact["binary_cells"]):
        assert {key: value for key, value in full.items() if key != "per_group"} == {
            key: value for key, value in brief.items() if key != "per_group"}


def shuffle_rows():
    rows = []
    for split in ("train", "development"):
        for group in range(3):
            for number in range(3):
                for first_parent in study.PARENT_CANDIDATES[0]:
                    for lexical in (0, 1):
                        rows.append(row(f"{split}:{group}:{number}:{first_parent}:{lexical}",
                            values=(2+number+4*group, 3, 5, 7),
                            parents=(first_parent, study.PARENT_CANDIDATES[1][group],
                                study.PARENT_CANDIDATES[2][group], study.PARENT_CANDIDATES[3][group]),
                            group=f"{split}_g{group}", split=split, lexical=lexical))
    return rows


def test_coherent_component_derangement_ties_lexical_relatives_and_all_target_columns():
    rows = shuffle_rows(); donors = study.coherent_shuffle(rows, 11)
    np.testing.assert_equal(donors, study.coherent_shuffle(rows, 11))
    assert sorted(donors) == list(range(len(rows))) and not donors.flags.writeable
    per_component = defaultdict(set); program_donors = defaultdict(set)
    for i, donor in enumerate(donors):
        assert rows[i]["split"] == rows[donor]["split"]
        assert rows[i]["cluster_id"] != rows[donor]["cluster_id"]
        assert rows[i]["lexical_realization"] == rows[donor]["lexical_realization"]
        per_component[rows[i]["cluster_id"]].add(rows[donor]["cluster_id"])
        program_donors[rows[i]["cluster_id"], rows[i]["canonical_source"]].add(rows[donor]["canonical_source"])
    assert all(len(value) == 1 for value in (*per_component.values(), *program_donors.values()))
    for site in (3, 7, 8):
        bundle = study.targets(rows, site); shuffled = study.permute_bundle(bundle, donors)
        assert shuffled.case_ids == bundle.case_ids
        assert shuffled.label_case_ids == tuple(bundle.case_ids[i] for i in donors)
        np.testing.assert_equal(shuffled.y, bundle.y[donors]); np.testing.assert_equal(shuffled.mask, bundle.mask[donors])
        np.testing.assert_equal(shuffled.numeric_truth, bundle.numeric_truth[donors])
        np.testing.assert_equal(np.sort(shuffled.y, axis=0), np.sort(bundle.y, axis=0))


@pytest.mark.parametrize("seed", [11, 29, 47])
def test_initialization_base_blocks_preserve_identical_prefix_control_labels(seed):
    rows = shuffle_rows()
    for record in rows: record.pop("base_id")  # source-prefix grouping is authoritative.
    donors = study.coherent_shuffle(rows, seed)
    bundle = study.targets(rows, 3); shuffled = study.permute_bundle(bundle, donors)
    observed = defaultdict(list)
    for i, record in enumerate(rows):
        observed[record["split"], tuple(record["canonical_source"].splitlines()[:4])].append(i)
    assert set(map(len, observed.values())) == {6}
    for indices in observed.values():
        assert len({tuple(shuffled.numeric_truth[i]) for i in indices}) == 1
        boolean = [spec["index"] for spec in bundle.columns if spec["kind"] == "boolean" and np.all(bundle.mask[:, spec["index"]])]
        assert len({tuple(shuffled.y[i, boolean]) for i in indices}) == 1
    assert bundle.descriptive["coherent_shuffle_qualified_sites"] == [3, 7, 8]


def test_inconsistent_cross_component_initialization_prefix_targets_are_rejected():
    rows = shuffle_rows()
    for record in rows:
        if record["cluster_id"].endswith("g1"):
            source = record["canonical_source"].replace("v0 = 6", "v0 = 2").replace("v0 = 7", "v0 = 3").replace("v0 = 8", "v0 = 4")
            record["canonical_source"] = source; record["source"] = rename(source, record["rename_map"])
    with pytest.raises(ValueError, match="conflicting shuffled states across components"):
        study.coherent_shuffle(rows, 11)


def test_shuffle_rejects_cross_split_groups_incomplete_lexical_units_and_bad_seed():
    rows = shuffle_rows()
    with pytest.raises(ValueError): study.coherent_shuffle(rows, True)
    with pytest.raises(ValueError, match="paired lexical"): study.coherent_shuffle(rows[:-1], 11)
    bad = deepcopy(rows); bad[-1]["cluster_id"] = bad[0]["cluster_id"]
    with pytest.raises(ValueError, match="cross"): study.coherent_shuffle(bad, 11)
    only_group = [item for item in rows if item["cluster_id"] == "train_g0"]
    with pytest.raises(ValueError, match="two groups"): study.coherent_shuffle(only_group, 11)


def test_subset_and_permutation_preserve_feature_identity_and_guard_splits():
    rows = shuffle_rows(); bundle = study.targets(rows, 7)
    train_mask = np.array([split == "train" for split in bundle.splits])
    train = study.subset(bundle, train_mask)
    assert len(train.case_ids) == 54 and set(train.splits) == {"train"}
    with pytest.raises(ValueError, match="bijective"): study.permute_bundle(bundle, [0]*len(rows))
    with pytest.raises(ValueError, match="cross splits"): study.permute_bundle(bundle, list(reversed(range(len(rows)))))


@pytest.mark.parametrize("change", ["self_copy", "extra_assignment", "root_dependency", "query", "surface", "duplicate_id"])
def test_fixed_scaffold_and_canonical_surface_validation_before_labels(change, monkeypatch):
    rows = [row("one")]
    if change == "duplicate_id": rows *= 2
    elif change == "surface": rows[0]["source"] = rows[0]["source"].replace("= 2", "= 4", 1)
    else:
        source = rows[0]["canonical_source"]
        if change == "self_copy": source = source.replace("v0 = v1", "v0 = v0")
        elif change == "extra_assignment": source = source.replace("\nv0 = v1", "\nv0 = 1\nv0 = v1")
        elif change == "root_dependency": source = source.replace("v1 = 3", "v1 = v0")
        else: source = source.rsplit("\n", 1)[0] + "\nv1"
        rows[0]["canonical_source"] = source; rows[0]["source"] = rename(source, rows[0]["rename_map"])
    monkeypatch.setattr(study.structural, "labels_at", lambda *a, **kw: pytest.fail("metadata guard failed"))
    with pytest.raises(ValueError): study.targets(rows, 7)


@pytest.mark.parametrize("site", [True, -1, 9, "after_query", 3.0])
def test_strict_site_names_and_indices(site):
    with pytest.raises(ValueError): study.targets([row("one")], site)


def test_undefined_and_nonfinite_scores_cannot_enter_primary_or_parent_metrics():
    bundle = study.targets([row("one")], 7)
    scores = np.array(bundle.y, copy=True); scores[0, index(bundle, "less_than", (0, 1))] = np.nan
    with pytest.raises(ValueError, match="finite"): study.task_correctness(bundle, scores)
    scores = np.array(bundle.y, copy=True); scores[0, index(bundle, "parent", (0, 1))] = np.nan
    with pytest.raises(ValueError, match="parent-class"): study.reconstruct_parent_graph(bundle, scores)


def test_fixed_value_domain_is_explicit_not_silent_categorical_remapping():
    with pytest.raises(ValueError, match="fixed nonzero value-class"):
        study.targets([row("one", values=(0, 3, 5, 7))], 3)
