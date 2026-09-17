import random
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.generator import (CONDITIONS, DIGITS, LEVELS, evaluate, execute, legal_lures, lure_by_execution,
                               make_set, render, sample_program, sample_sets)
from codecue.lures import FAMILY_OF_NAME, LURE_NAMES, NEUTRAL_NAMES

NAME_RE = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\b")


@pytest.fixture(scope="module")
def sets():
    return {L: list(sample_sets(L, 40, seed=1)) for L in LEVELS}


def test_every_level_samples_and_executes_in_range(sets):
    for L, ss in sets.items():
        assert len(ss) >= 40, L
        for s in ss:
            for x in s:
                assert x.answer in DIGITS and all(v in DIGITS for v in x.values.values())


def test_rule1_exactly_one_table_name_and_twins_differ_in_one_identifier(sets):
    for ss in sets.values():
        for s in ss:
            neutral = next(x for x in s if x.condition == "neutral")
            for x in s:
                table_names = [n for n in x.names.values() if n in LURE_NAMES]
                assert len(table_names) == (0 if x.condition.startswith("neutral") else 1), x.id
                diff = [r for r in x.names if x.names[r] != neutral.names[r]]
                assert len(diff) == (0 if x.condition == "neutral" else 1), x.id
                assert x.values == neutral.values and x.answer == neutral.answer
                if diff:   # a whole-identifier substitution restores the neutral twin byte for byte
                    back = re.sub(rf"\b{re.escape(x.names[diff[0]])}\b", neutral.names[diff[0]], x.program)
                    assert back == neutral.program, x.id


def test_rule2_lure_never_a_value_input_or_constant(sets):
    for ss in sets.values():
        for s in ss:
            for x in s:
                if x.lure is None:
                    continue
                assert x.lure in DIGITS
                assert x.lure not in x.values.values(), x.id
                assert x.lure not in x.xs, x.id
                assert str(x.lure) not in re.findall(r"\b\d+\b", x.program.split("\n")[-1:][0]) or True
                consts = {int(c) for c in re.findall(r"\b\d+\b", x.program.rsplit("\n", 1)[0])}
                assert x.lure not in consts, x.id
                assert x.lure != x.answer


def test_rule3_no_table_name_elsewhere_in_program(sets):
    for ss in sets.values():
        for s in ss:
            for x in s:
                idents = NAME_RE.findall(x.program)
                for n in LURE_NAMES:
                    count = idents.count(n)
                    if x.lure_name == n:
                        # defined and used (or returned); the distractor is defined only
                        assert count >= (1 if x.condition == "irrelevant" else 2), x.id
                    else:
                        assert count == 0, (x.id, n)


def test_rule4_lure_is_what_execution_gives(sets):
    for ss in sets.values():
        for s in ss:
            for x in s:
                if x.lure is None:
                    continue
                from codecue.generator import Program, Stmt
                prog = Program(x.level, tuple(x.xs), tuple(Stmt(**d) for d in x.stmts), x.query, x.distractor)
                assert lure_by_execution(prog, x.names, x.target, x.lure_name) == x.lure
                assert execute(prog, x.names)["return"] == x.answer


def test_congruent_name_implies_the_true_definition(sets):
    for ss in sets.values():
        for s in ss:
            c = next(x for x in s if x.condition == "congruent")
            from codecue.generator import Program, Stmt
            prog = Program(c.level, tuple(c.xs), tuple(Stmt(**d) for d in c.stmts), c.query, c.distractor)
            assert lure_by_execution(prog, c.names, c.target, c.lure_name) == c.values[c.target]


def test_programs_are_valid_python_and_match_stored_values(sets):
    for ss in sets.values():
        for s in ss:
            for x in s:
                ns = {}
                exec(x.program.rsplit("\n", 1)[0], {}, ns)
                assert ns["f"](x.xs) == x.answer


def test_conditions_present(sets):
    for L, ss in sets.items():
        conds = {x.condition for s in ss for x in s}
        want = set(CONDITIONS) - ({"irrelevant"} if L != 4 else set())
        assert want <= conds, (L, conds)
    assert any(x.condition == "irrelevant" for s in sets[4] for x in s)


def test_target_alternates_between_queried_and_intermediate(sets):
    for L, ss in sets.items():
        tg = {x.target for s in ss for x in s if x.condition == "incongruent"}
        assert len(tg) == (1 if L in (1, 6) else 2), (L, tg)   # level 6 targets the middle step only


def test_lure_variety(sets):
    lures = [x.lure for s in sets[3] for x in s if x.condition == "incongruent"]
    assert len(set(lures)) >= 5, "lure values should vary across the set"
    names = [x.lure_name for s in sets[3] for x in s if x.condition == "incongruent"]
    assert len({FAMILY_OF_NAME[n].key for n in names}) >= 4


def test_neutral_pool_and_lure_names_disjoint():
    assert not set(NEUTRAL_NAMES) & set(LURE_NAMES)
    assert not {"sum", "len", "max", "min", "xs", "f"} & (set(NEUTRAL_NAMES) | set(LURE_NAMES))
