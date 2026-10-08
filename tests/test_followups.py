from codecue.followups import control_demo, first_value_boundary, write_class
from codecue.prompts import demos, demo_block, value_written


class WordTokenizer:
    def __call__(self, text, **kwargs):
        return {"input_ids": list(range(len(text.split())))}


def test_control_preserves_demo_values_and_matches_length():
    tok = WordTokenizer()
    for x in demos(5, 7, "trace"):
        block = control_demo(x, "neutral_annotation", tok)
        assert len(tok(block)["input_ids"]) == len(tok(demo_block(x, "trace_expr"))["input_ids"])
        trace = block.split("Trace:", 1)[1]
        for role, name in x.names.items():
            assert value_written(trace, name) == x.values[role]
        numeric = control_demo(x, "numeric_elaboration", tok).split("Trace:", 1)[1]
        for role, name in x.names.items():
            assert value_written(numeric, name) == x.values[role]


def test_first_value_boundary_rejects_prefaces():
    generation = " sum_all = 8, ww = 9"
    boundary = first_value_boundary(generation, "sum_all")
    assert generation[boundary["marker"]] == "="
    assert generation[boundary["value_start"]] == "8"
    assert first_value_boundary("Here is the trace: sum_all = 8", "sum_all") is None
    assert first_value_boundary("sum_all = 3 + 5 = 8", "sum_all") is None
    assert write_class(None, 2, 8) == "other_error"
    assert write_class(8, 2, 8) == "lure_write"
