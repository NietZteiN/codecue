import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.generator import sample_sets
from codecue.prompts import build_prompt, demos, parse_answer, parse_answer_free, value_written, parse_regime


def test_trace_prompt_writes_every_value_and_ends_at_trace():
    d = demos(3, 7, "trace")
    x = next(i for i in next(sample_sets(3, 1, seed=3)) if i.condition == "incongruent")
    p = build_prompt(x, "trace_s7", d)
    assert p.endswith("\nTrace:") and p.count("Answer:") == 3
    for dd in d:
        for r, v in dd.values.items():
            assert f"{dd.names[r]} = {v}" in p
    assert x.program in p


def test_demos_are_fixed_per_seed_and_disjoint_from_tests():
    a, b = demos(3, 7, "trace"), demos(3, 7, "trace")
    assert [i.program for i in a] == [i.program for i in b]
    assert [i.program for i in demos(3, 11, "trace")] != [i.program for i in a]
    test_programs = {i.program for s in sample_sets(3, 200, seed=3) for i in s}
    assert not {i.program for i in a} & test_programs


def test_parse_takes_last_answer_before_blank_line():
    assert parse_answer(" 7\n\ndef f(xs):") == 7
    assert parse_answer(" total = 8, v = 6\nAnswer: 6\n\ndef f") == 6
    assert parse_answer(" total = 8, v = 6\nAnswer: 6\nAnswer: 9\n\ndef f") == 9
    assert parse_answer("nothing here") is None
    assert parse_answer_free("So the result is 5.\nAnswer: 5\nextra") == 5
    assert parse_answer_free("Therefore the function returns 4.") == 4


def test_value_written_stops_at_the_next_assignment_in_a_trace():
    # the trace format lists every variable on one line; the value for `count` is 5, not the 4
    # that follows for `vv` (this exact case produced a false "wrote the lure" hit)
    assert value_written(" count = 5, zz = 1, vv = 4\nAnswer: 4", "count") == 5
    assert value_written(" count = 5, zz = 1, vv = 4\nAnswer: 4", "vv") == 4
    assert value_written(" total = 3, k = 6, m = 9\nAnswer: 9", "total") == 3


def test_value_written_takes_the_final_value_of_a_worked_expression():
    assert value_written("In this case, `xs = [2, 1, 5]`, so `count = 2 + 1 + 5 = 8`. Then\nAnswer: 8", "count") == 8
    assert value_written("so `length = 4 + 5 = 9`.", "length") == 9
    assert value_written("n_items = 0 + 4 + 5 =\n9\nAnswer: 9", "n_items") == 9  # value continued on the next line


def test_value_written_detects_only_the_named_variable():
    t = "First, total = sum([1,2,3]) = 6. Then count is 3 because count = total - 3.\nAnswer: 3"
    assert value_written(t, "total") == 6
    assert value_written(t, "count") == 3
    assert value_written("we return count\nAnswer: 3", "count") is None
    assert value_written(t, "tot") is None


def test_parse_regime():
    assert parse_regime("trace_s11") == ("trace", 11) and parse_regime("prose") == ("prose", 7)
