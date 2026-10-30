"""Prefix visibility and version-reference invariants for relationship labels."""
import ast
import json

import pytest

from codecue.binding import relationships as rel
from codecue.binding.interpreter import execute
from codecue.binding.programs import rename


SOURCE = "x = 2\ny = x\nx = 9\nz = x + y\nz"
SLOTS = {"x": 0, "y": 1, "z": 2}


def test_versions_obsolete_bindings_and_three_distinct_edge_relations():
    result = rel.labels_at(SOURCE, 3, SLOTS)
    assert result["version_nodes"] == [
        {"id": "v0@1", "canonical_name": "v0", "slot": 0, "version": 1,
         "statement": 0, "status": "obsolete"},
        {"id": "v0@2", "canonical_name": "v0", "slot": 0, "version": 2,
         "statement": 2, "status": "current"},
        {"id": "v1@1", "canonical_name": "v1", "slot": 1, "version": 1,
         "statement": 1, "status": "current"},
        {"id": "v2@1", "canonical_name": "v2", "slot": 2, "version": 1,
         "statement": 3, "status": "current"},
    ]
    assert result["direct_def_use_edges"] == [
        ["v0@1", "v1@1"], ["v0@2", "v2@1"], ["v1@1", "v2@1"]]
    assert result["strict_ancestor_edges"] == [
        ["v0@1", "v1@1"], ["v0@1", "v2@1"], ["v0@2", "v2@1"], ["v1@1", "v2@1"]]
    assert result["succession_edges"] == [["v0@1", "v0@2"]]
    assert ["v0@1", "v0@2"] not in result["direct_def_use_edges"]
    assert all(a != b for a, b in result["strict_ancestor_edges"])
    assert result["uses"][0]["referent"] == "v0@1"
    assert "output" not in result


@pytest.mark.parametrize("checkpoint", range(4))
@pytest.mark.parametrize("visible", [False, True])
def test_explicit_semantic_slots_are_exactly_rename_invariant(checkpoint, visible):
    if visible and checkpoint != 3:
        with pytest.raises(ValueError, match="final assignment"):
            rel.labels_at(SOURCE, checkpoint, SLOTS, output_visible=True)
        return
    mapping = {"x": "misleading_name", "y": "saved", "z": "dev_item"}
    surface = rename(SOURCE, mapping)
    mapped = {mapping[name]: slot for name, slot in SLOTS.items()}
    assert rel.labels_at(SOURCE, checkpoint, SLOTS, output_visible=visible) == rel.labels_at(
        surface, checkpoint, mapped, output_visible=visible)


def test_independent_assignment_reordering_preserves_semantic_version_graph():
    a = rel.labels_at("x = 2\ny = 3\nz = x - y\nz", 2, SLOTS)
    b = rel.labels_at("y = 3\nx = 2\nz = x - y\nz", 2, SLOTS)
    for key in ("direct_def_use_edges", "strict_ancestor_edges", "succession_edges", "uses"):
        assert a[key] == b[key]
    assert [{k: v for k, v in n.items() if k != "statement"} for n in a["version_nodes"]] == [
        {k: v for k, v in n.items() if k != "statement"} for n in b["version_nodes"]]
    assert a["version_nodes"][0]["statement"] != b["version_nodes"][0]["statement"]


def test_cancellation_and_equal_values_do_not_erase_syntactic_reads():
    source = "x = 4\ny = 4\nz = x - x\nz"
    result = rel.labels_at(source, 2, SLOTS, output_visible=True)
    assert result["direct_def_use_edges"] == [["v0@1", "v2@1"]]
    assert result["output"]["structural_ancestors"] == ["v0@1", "v2@1"]
    assert [use["referent"] for use in result["uses"]] == ["v0@1", "v0@1"]
    assert [use["occurrence"] for use in result["uses"]] == [0, 1]
    assert [use["operand_path"] for use in result["uses"]] == [["left"], ["right"]]
    assert execute(source)["expected_answer"] == execute(source, {"x@1": 11})["expected_answer"]
    assert result["output"]["semantics"] == "syntactic_dependencies_not_functional_influence"


def test_operand_order_is_expression_order_not_breadth_first_ast_walk():
    source = "x = 2\ny = 3\nz = 4\nw = (x + y) - (-z + x)\nw"
    result = rel.labels_at(source, 3)
    assert [use["referent"] for use in result["uses"]] == ["v0@1", "v1@1", "v2@1", "v0@1"]
    assert [use["operand_path"] for use in result["uses"]] == [
        ["left", "left"], ["left", "right"], ["right", "left", "operand"], ["right", "right"]]


def test_self_update_reads_previous_version_before_defining_new_version():
    result = rel.labels_at("x = 1\nx = x + x\nx", 1)
    assert result["direct_def_use_edges"] == [["v0@1", "v0@2"]]
    assert result["succession_edges"] == [["v0@1", "v0@2"]]
    assert [use["referent"] for use in result["uses"]] == ["v0@1", "v0@1"]


def test_future_assignments_and_hidden_output_cannot_change_returned_labels():
    a = "x = 2\ny = x\nx = 3\nx + y"
    b = "x = 2\ny = x\nz = y * 3\nw = z - z\nw - x"
    c = "x = 2\ny = x\nx = x * 3\nx = x * 3\nx = x * 3\nx * 3"
    assert rel.labels_at(a, 1) == rel.labels_at(b, 1) == rel.labels_at(c, 1)
    fixed_a = {"x": 0, "y": 1}
    fixed_b = {"x": 0, "y": 1, "z": 2, "w": 3}
    assert rel.labels_at(a, 1, fixed_a) == rel.labels_at(b, 1, fixed_b)


def test_default_slot_order_uses_only_first_visible_definitions():
    result = rel.labels_at("later = 2\nearlier = later\nz = 4\nz", 1)
    assert [(n["canonical_name"], n["statement"]) for n in result["version_nodes"]] == [
        ("v0", 0), ("v1", 1)]
    assert len(result["version_nodes"]) == 2
    assert rel.labels_at("x = 2\nx", 0, {"future": 0, "x": 1})["version_nodes"][0]["id"] == "v1@1"


def test_output_graph_requires_explicit_visibility_and_last_assignment():
    source = "x = 2\ny = x + 1\ny - x"
    assert "output" not in rel.labels_at(source, 1)
    with pytest.raises(ValueError, match="final assignment"):
        rel.labels_at(source, 0, output_visible=True)
    result = rel.labels_at(source, 1, output_visible=True)
    assert result["output"]["direct_referents"] == ["v0@1", "v1@1"]
    assert result["output"]["structural_ancestors"] == ["v0@1", "v1@1"]
    assert [u["operand_path"] for u in result["output"]["direct_uses"]] == [["left"], ["right"]]
    assert all(u["consumer"] == "output" and u["statement"] == 2
               for u in result["output"]["direct_uses"])
    assert rel.labels_at("x = 1\n0", 0, output_visible=True)["output"]["direct_referents"] == []


def test_prefix_validation_never_executes_hidden_assignments_or_output(monkeypatch):
    original = rel.interpreter.execute
    calls = []

    def spy(source, **kwargs):
        calls.append((source, kwargs))
        return original(source, **kwargs)

    monkeypatch.setattr(rel.interpreter, "execute", spy)
    rel.labels_at("x = 2\ny = x\nz = y * 3\nz - x", 1)
    assert len(calls) == 1
    tree = ast.parse(calls[0][0])
    assert len(tree.body) == 3
    assert isinstance(tree.body[-1].value, ast.Constant) and tree.body[-1].value.value == 0
    assert calls[0][1]["substitutions"] == {"x@1": 0, "y@1": 0}
    assert "z" not in calls[0][0]


def test_labels_contain_no_values_names_answers_or_future_trace():
    a = rel.labels_at("secret_name = 2\ncopy = secret_name\ncopy", 1)
    b = rel.labels_at("secret_name = 47\ncopy = secret_name\nsecret_name - copy", 1)
    assert a == b
    serialized = json.dumps(a)
    for forbidden in ("secret_name", "copy", "value", "answer", "execution_trace", "liveness"):
        assert forbidden not in serialized


@pytest.mark.parametrize("checkpoint", [True, False, 0.0, "0", None, -1, 4])
def test_reject_invalid_checkpoint(checkpoint):
    with pytest.raises(ValueError):
        rel.labels_at(SOURCE, checkpoint)


@pytest.mark.parametrize("visible", [0, 1, "yes", None])
def test_reject_nonboolean_output_visibility(visible):
    with pytest.raises(ValueError, match="boolean"):
        rel.labels_at(SOURCE, 3, output_visible=visible)


@pytest.mark.parametrize("slots", [
    {}, {"x": 0}, {"x": 0, "y": 0, "z": 1}, {"x": -1, "y": 0, "z": 1},
    {"x": 0, "y": 2, "z": 3}, {"x": False, "y": 1, "z": 2},
    {"x": 0.0, "y": 1, "z": 2}, {"x": "0", "y": 1, "z": 2},
    {"x": 0, "y": 1, "z": 2, "_private": 3},
    {"x": 0, "y": 1, "z": 2, "for": 3},
    {"x": 0, "y": 1, "z": 2, "bad-name": 3}, ["x", "y", "z"],
])
def test_reject_invalid_canonical_maps(slots):
    with pytest.raises(ValueError):
        rel.labels_at(SOURCE, 3, slots)


@pytest.mark.parametrize("source", [
    "x = 1\ny = unknown\nx", "x = 1\n__import__('os')", "x = 1\nx / 2",
    "x = 1\nx * 4", "x = True\nx", "x = 65\nx", "x = 1\nif x: pass",
    "x = 1\ny = (", "x = 1", "x = 1\ny = 2\nz", 3,
])
def test_safe_parser_rejects_unsupported_or_invalid_future_code(source):
    with pytest.raises(ValueError):
        rel.labels_at(source, 0)


def test_structural_labels_do_not_require_values_in_original_execution_bound():
    source = "x = 64\ny = x * 3\ny"
    with pytest.raises(ValueError, match="bounds"):
        execute(source)
    assert rel.labels_at(source, 1)["direct_def_use_edges"] == [["v0@1", "v1@1"]]


def test_validator_detects_independent_oracle_disagreement(monkeypatch):
    original = rel.interpreter.execute

    def wrong(source, **kwargs):
        result = original(source, **kwargs)
        result["dependency_edges"] = []
        return result

    monkeypatch.setattr(rel.interpreter, "execute", wrong)
    with pytest.raises(ValueError, match="direct-edge mismatch"):
        rel.labels_at(SOURCE, 1)


def test_explicit_limits_bound_source_ast_and_recursive_ancestry_work(monkeypatch):
    with pytest.raises(ValueError, match="byte limit"):
        rel.labels_at("x = 1\nx" + " " * rel.MAX_SOURCE_BYTES, 0)
    monkeypatch.setattr(rel, "MAX_AST_NODES", 4)
    with pytest.raises(ValueError, match="AST limits"):
        rel.labels_at("x = 1\nx", 0)
    monkeypatch.setattr(rel, "MAX_AST_NODES", 8192)
    monkeypatch.setattr(rel, "MAX_AST_DEPTH", 2)
    with pytest.raises(ValueError, match="AST limits"):
        rel.labels_at("x = 1\ny = x + 2\ny", 1)
    monkeypatch.setattr(rel, "MAX_AST_DEPTH", 64)
    monkeypatch.setattr(rel, "MAX_ANCESTOR_VISITS", 1)
    with pytest.raises(ValueError, match="ancestry-work"):
        rel.labels_at("x = 1\ny = x\nz = y\nz", 2)


def test_dense_valid_dag_is_rejected_before_exponential_oracle_recursion(monkeypatch):
    lines = ["x = 1", "y = 1"]
    lines.extend(f"{'x' if i % 2 else 'y'} = x + y" for i in range(30))
    source = "\n".join([*lines, "x - y"])

    def forbidden(*args, **kwargs):
        pytest.fail("work guard must run before the recursive execution oracle")

    monkeypatch.setattr(rel.interpreter, "execute", forbidden)
    with pytest.raises(ValueError, match="ancestry-work"):
        rel.labels_at(source, len(lines) - 1)


def test_unseen_dense_future_does_not_change_eligible_prefix_labels():
    prefix = ["x = 1", "y = 1"]
    future = [f"{'x' if i % 2 else 'y'} = x + y" for i in range(30)]
    assert rel.labels_at("\n".join([*prefix, *future, "x - y"]), 1) == rel.labels_at(
        "\n".join([*prefix, "x"]), 1)


def test_visible_output_work_is_guarded_separately(monkeypatch):
    monkeypatch.setattr(rel, "MAX_ANCESTOR_VISITS", 1)
    source = "x = 1\ny = x\ny"
    assert "output" not in rel.labels_at(source, 1)
    with pytest.raises(ValueError, match="visible output.*ancestry-work"):
        rel.labels_at(source, 1, output_visible=True)


def test_explicit_future_slot_map_is_bounded_before_graph_validation(monkeypatch):
    slots = {"x": 0, **{f"future{i}": i for i in range(1, rel.MAX_CANONICAL_SLOTS + 1)}}

    def forbidden(*args, **kwargs):
        pytest.fail("oversized map reached graph validation")

    monkeypatch.setattr(rel.interpreter, "execute", forbidden)
    with pytest.raises(ValueError, match="slot limit"):
        rel.labels_at("x = 1\nx", 0, slots)
    with pytest.raises(ValueError, match="bounded nonnegative"):
        rel.labels_at("x = 1\nx", 0, {"x": 1 << 1000})
