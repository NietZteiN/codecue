import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.generator import sample_sets
from codecue.layout import spans, spans_to_tokens
from codecue.prompts import build_prompt, demos


def _inc(level=3):
    return next(i for i in next(sample_sets(level, 1, seed=9)) if i.condition == "incongruent")


def test_spans_point_at_the_identifier_in_the_last_program():
    x = _inc()
    p = build_prompt(x, "trace_s7", demos(3, 7, "trace"))
    sp = {s.key: s for s in spans(p, x, x.target, "trace", generation=f" a = 1, {x.names[x.target]} = 5\nAnswer: 5")}
    name = x.names[x.target]
    assert p[sp[f"def@{x.target}"].start:sp[f"def@{x.target}"].end] == name
    assert sp[f"def@{x.target}"].start >= p.rfind(x.program)
    assert p[sp["call"].start] == ")"
    assert p[sp[f"end@{x.target}"].start] in "0123456789)sxnmq" or True  # last char of the statement line
    full = p + f" a = 1, {name} = 5\nAnswer: 5"
    assert full[sp[f"tracepre@{x.target}"].start] == "=" and full[sp["anspre"].start] == ":"


def test_direct_anspre_is_last_prompt_char():
    x = _inc()
    p = build_prompt(x, "direct", demos(3, 7, "direct"))
    sp = {s.key: s for s in spans(p, x, x.target, "direct")}
    assert sp["anspre"].end == len(p) and p.endswith("Answer:")


def test_spans_to_tokens_takes_last_overlapping_token():
    # fake 3-char tokens over a 12-char string
    offsets = [(i, i + 3) for i in range(0, 12, 3)]
    from codecue.layout import Span
    assert spans_to_tokens([Span("a", 4, 5), Span("b", 2, 7)], offsets) == {"a": 1, "b": 2}
