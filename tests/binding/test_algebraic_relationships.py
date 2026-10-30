"""Actual arithmetic targets must remain canonical and prefix-visible."""
import ast

import pytest

from codecue.binding import algebraic_relationships as algebra
from codecue.binding.programs import rename


SOURCE = "x = 2\ny = x\nx = 7\nz = x - y\nz"
SLOTS = {"x": 0, "y": 1, "z": 2}


def pair(result, left, right):
    return next(item for item in result["ordered_pairs"] if (item["left"], item["right"]) == (left, right))


def triple(result, first, second, third):
    return next(item for item in result["ordered_triples"]
                if (item["first"], item["second"], item["third"]) == (first, second, third))


def test_overwrite_preserves_saved_value_and_reports_only_current_versions():
    result = algebra.labels_at(SOURCE, 3, SLOTS)
    assert result["current_slots"] == [
        {"canonical_name": "v0", "slot": 0, "version": 2, "definition": "v0@2", "statement": 2, "value": 7},
        {"canonical_name": "v1", "slot": 1, "version": 1, "definition": "v1@1", "statement": 1, "value": 2},
        {"canonical_name": "v2", "slot": 2, "version": 1, "definition": "v2@1", "statement": 3, "value": 5}]
    assert pair(result, "v0", "v1")["difference"] == 5
    assert triple(result, "v0", "v1", "v2")["difference_equals_third"] is True
    assert result["target_semantics"] == "numeric_oracle_targets_not_model_features"


def test_exact_canonical_rename_invariance_at_every_checkpoint():
    mapping = {"x": "saved", "y": "misleading", "z": "item"}
    surface = rename(SOURCE, mapping)
    mapped = {mapping[name]: slot for name, slot in SLOTS.items()}
    for index in range(4):
        assert algebra.labels_at(SOURCE, index, SLOTS) == algebra.labels_at(surface, index, mapped)


def test_identical_visible_prefixes_ignore_future_values_and_output_queries():
    left = "x = 64\ny = x\nx - y"
    right = "x = 64\ny = x\nx = x * 3\nz = x * 3\nz + x"
    assert algebra.labels_at(left, 1) == algebra.labels_at(right, 1)
    # The out-of-bounds future assignment is parsed but never executed above.
    with pytest.raises(ValueError, match="bounds"):
        algebra.labels_at(right, 2)


def test_actual_execution_receives_only_prefix_and_literal_zero_sentinel(monkeypatch):
    original = algebra.interpreter.execute
    calls = []

    def spy(source, **kwargs):
        calls.append((source, kwargs))
        return original(source, **kwargs)

    monkeypatch.setattr(algebra.interpreter, "execute", spy)
    result = algebra.labels_at(SOURCE, 1)
    assert len(calls) == 1 and calls[0][1] == {"bound": 64}
    tree = ast.parse(calls[0][0])
    assert len(tree.body) == 3 and ast.dump(tree.body[-1].value) == "Constant(value=0)"
    assert all(node["value"] == 2 for node in result["current_slots"])
    assert set(result) == {"schema_version", "checkpoint", "target_semantics", "current_slots", "ordered_pairs", "ordered_triples"}


def test_primitive_pair_consistency_equal_values_order_and_antisymmetry():
    result = algebra.labels_at("x = -3\ny = 5\nz = -3\nx", 2)
    assert len(result["ordered_pairs"]) == 6
    for item in result["ordered_pairs"]:
        inverse = pair(result, item["right"], item["left"])
        assert item["difference"] == -inverse["difference"]
        assert item["equal"] == inverse["equal"] == (item["difference"] == 0)
        assert item["less_than"] == (item["difference"] < 0)
        assert int(item["equal"]) + int(item["less_than"]) + int(inverse["less_than"]) == 1
        assert type(item["difference"]) is int and type(item["equal"]) is bool
    assert pair(result, "v0", "v2")["equal"] is True


def test_ordered_distinct_triples_support_sum_and_signed_difference_tasks():
    result = algebra.labels_at("x = -2\ny = 5\nz = 3\nx", 2)
    assert len(result["ordered_triples"]) == 6
    assert triple(result, "v0", "v1", "v2")["sum_equals_third"] is True
    assert triple(result, "v1", "v0", "v2")["sum_equals_third"] is True
    assert triple(result, "v2", "v0", "v1")["difference_equals_third"] is True
    assert triple(result, "v0", "v2", "v1")["difference_equals_third"] is False
    assert all(len({item[key] for key in ("first", "second", "third")}) == 3
               for item in result["ordered_triples"])


def test_signed_difference_targets_reach_plus_and_minus_128():
    result = algebra.labels_at("x = 64\ny = -64\nx", 1)
    assert pair(result, "v0", "v1")["difference"] == 128
    assert pair(result, "v1", "v0")["difference"] == -128


def test_affine_cancellation_uses_actual_values_not_syntactic_influence():
    result = algebra.labels_at("x = 7\ny = x - x\nz = 0\ny", 2)
    assert [item["value"] for item in result["current_slots"]] == [7, 0, 0]
    assert pair(result, "v1", "v2")["equal"] is True
    assert not any("edges" in key or "ancestor" in key for key in result)


def test_unseen_explicit_slots_produce_no_nodes_pairs_or_triples():
    result = algebra.labels_at("x = 2\ny = 3\ny", 0, {"future": 0, "y": 1, "x": 2})
    assert [item["canonical_name"] for item in result["current_slots"]] == ["v2"]
    assert result["ordered_pairs"] == result["ordered_triples"] == []
    assert algebra.labels_at("x = 2\ny = 3\ny", 1)["ordered_triples"] == []


def test_visible_slot_cap_precedes_execution_and_cubic_expansion(monkeypatch):
    source = "\n".join([*(f"x{i} = {i}" for i in range(9)), "x0"])
    monkeypatch.setattr(algebra.interpreter, "execute", lambda *a, **kw: pytest.fail("slot cap failed"))
    with pytest.raises(ValueError, match="eight visible slots"):
        algebra.labels_at(source, 8)


def test_eight_visible_slots_and_large_unseen_frame_are_supported():
    source = "\n".join([*(f"x{i} = {i}" for i in range(8)), "x0"])
    slots = {f"x{i}": i for i in range(8)} | {f"future{i}": i for i in range(8, 128)}
    result = algebra.labels_at(source, 7, slots)
    assert len(result["current_slots"]) == 8
    assert len(result["ordered_pairs"]) == 56 and len(result["ordered_triples"]) == 336


@pytest.mark.parametrize("statement", [True, 0.0, "0", -1, 4])
def test_strict_checkpoint_validation(statement):
    with pytest.raises(ValueError): algebra.labels_at(SOURCE, statement)


@pytest.mark.parametrize("slots", [{}, {"x": False, "y": 1, "z": 2},
    {"x": 0, "y": 0, "z": 1}, {"x": 0, "y": 2, "z": 3}, {"x": 0, "y": 1}, []])
def test_strict_canonical_mapping_validation(slots):
    with pytest.raises(ValueError): algebra.labels_at(SOURCE, 3, slots)


@pytest.mark.parametrize("source", ["x = 64\ny = x + 1\ny", "x = -64\ny = x - 1\ny"])
def test_visible_actual_assignment_values_must_stay_in_bounds(source):
    with pytest.raises(ValueError, match="bounds"): algebra.labels_at(source, 1)


@pytest.mark.parametrize("source", ["x = unknown\nx", "x = 1\n__import__('os')", "x = 1\nx / 2"])
def test_restricted_parser_rejects_undefined_or_unsafe_code(source):
    with pytest.raises(ValueError): algebra.labels_at(source, 0)


def test_dense_prefix_work_cap_precedes_recursive_oracle_execution(monkeypatch):
    lines = ["x = 0", "y = 0"] + [f"{'x' if i % 2 else 'y'} = x + y" for i in range(30)]
    monkeypatch.setattr(algebra.interpreter, "execute", lambda *a, **kw: pytest.fail("ancestry guard failed"))
    with pytest.raises(ValueError, match="ancestry-work"):
        algebra.labels_at("\n".join([*lines, "x"]), len(lines) - 1)
