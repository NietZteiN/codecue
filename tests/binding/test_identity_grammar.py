from fractions import Fraction
from functools import lru_cache
from itertools import product
import inspect

import numpy as np
import pytest

from codecue.binding import identity_grammar as grammar


def value(result, prefix="score", row=0):
    numerator = result[prefix+"_numerators"][row]
    exponent = result[prefix+"_exponents"][row]
    if numerator is None:
        assert exponent is None
        return None
    return Fraction(int(numerator)) * Fraction(2)**exponent


@lru_cache(maxsize=2)
def all_paths(allow_self):
    paths = []
    for digits in product(range(16),repeat=4):
        counts = [1]*4; write = []; parent = []; code = 0
        for digit in digits:
            d,p = divmod(digit,4)
            if counts[d] == 4 or (not allow_self and d == p):
                break
            parent.append(4*p+counts[p]-1)
            counts[d] += 1
            write.append(4*d+counts[d]-1)
            code = 16*code+digit
        else:
            paths.append((tuple(write),tuple(parent),code))
    return tuple(paths)


def brute_force(write,parent,evidence,allow_self):
    # Independent enumeration and Fraction conversion, with no DP/helper calls.
    fractions = [Fraction.from_float(float(v)) for v in np.concatenate((write.ravel(),parent.ravel()))]
    denominator = max(v.denominator for v in fractions)
    integers = [int(v*denominator) for v in fractions]
    w = [integers[event*16:(event+1)*16] for event in range(4)]
    p = [integers[64+event*16:64+(event+1)*16] for event in range(4)]
    if evidence == "owner_marginal":
        w = [[sum(row[(candidate//4)*4:(candidate//4+1)*4]) for candidate in range(16)] for row in w]
        p = [[sum(row[(candidate//4)*4:(candidate//4+1)*4]) for candidate in range(16)] for row in p]
    best = None; chosen = None
    for writes,parents,code in all_paths(allow_self):
        score = sum(w[event][writes[event]]+p[event][parents[event]] for event in range(4))
        if best is None or score > best or (score == best and code < chosen[2]):
            best,chosen = score,(writes,parents,code)
    return chosen,Fraction(best,denominator)


@pytest.mark.parametrize("allow_self,count",[(True,64512),(False,20412)])
def test_complete_fixed_grammar_path_counts(allow_self,count):
    assert len(all_paths(allow_self)) == count


@pytest.mark.parametrize("evidence",grammar.EVIDENCE)
@pytest.mark.parametrize("allow_self",[True,False])
def test_exact_dp_matches_independent_bruteforce(evidence,allow_self):
    rng = np.random.default_rng(51)
    write = rng.integers(-8,9,(2,4,16)).astype(float)/8
    parent = rng.integers(-8,9,(2,4,16)).astype(float)/8
    result = grammar.decode(write,parent,evidence=evidence,allow_self=allow_self,batch_size=1)
    for row in range(2):
        expected,score = brute_force(write[row],parent[row],evidence,allow_self)
        assert tuple(result["write_ids"][row]) == expected[0]
        assert tuple(result["parent_ids"][row]) == expected[1]
        assert result["path_code"][row] == expected[2]
        assert value(result,row=row) == score
        assert value(result,"free_upper_bound",row)-score == value(result,"projection_penalty",row)


@pytest.mark.parametrize("allow_self,code",[(True,4),(False,0x1114)])
def test_all_equal_scores_choose_exact_event_interleaved_lex_path(allow_self,code):
    scores = np.zeros((1,4,16))
    result = grammar.decode(scores,scores,allow_self=allow_self)
    assert result["path_code"].tolist() == [code]
    assert value(result) == 0
    assert result["score_numerators"] == ("0",) and result["score_exponents"] == (0,)


@pytest.mark.parametrize("allow_self",[True,False])
def test_subnormal_advantage_survives_later_huge_score_cancellation(allow_self):
    write = np.zeros((1,4,16)); parent = np.zeros_like(write)
    write[0,0,5] = np.nextafter(0.,1.)
    write[0,3,:] = 1e308
    result = grammar.decode(write,parent,allow_self=allow_self)
    expected,score = brute_force(write[0],parent[0],"joint",allow_self)
    assert result["write_ids"][0,0] == 5
    assert result["path_code"][0] == expected[2]
    assert value(result) == score > Fraction.from_float(1e308)


def test_extreme_finite_values_have_exact_unbounded_objective_not_float_overflow():
    scores = np.full((1,4,16),np.finfo(float).max)
    result = grammar.decode(scores,scores,evidence="owner_marginal")
    assert result["valid"].tolist() == [True]
    assert value(result) == 32*Fraction.from_float(np.finfo(float).max)
    assert value(result,"projection_penalty") == 0


def test_owner_marginal_is_exact_sum_not_rounded_float_or_component_columns():
    write = np.zeros((1,4,16)); parent = np.zeros_like(write)
    write[0,0,4:8] = [1e308,np.nextafter(0.,1.),-1e308,0]
    assert write[0,0,4:8].sum() == 0
    result = grammar.decode(write,parent,evidence="owner_marginal")
    assert result["free_write_ids"][0,0] == 4  # Exact owner1 wins, lowest tied version1.
    assert result["write_ids"][0,0] == 5       # Grammar supplies the first write's version2.
    assert value(result) == Fraction.from_float(np.nextafter(0.,1.))


@pytest.mark.parametrize("evidence",grammar.EVIDENCE)
def test_batch_permutation_duplicates_and_input_purity(evidence):
    rng = np.random.default_rng(75)
    write = rng.normal(size=(3,4,16)); parent = rng.normal(size=(3,4,16))
    take = [2,0,1,0,2,1]; w = write[take]; p = parent[take]
    before = (w.copy(),p.copy())
    small = grammar.decode(w,p,evidence=evidence,batch_size=1)
    large = grammar.decode(w,p,evidence=evidence,batch_size=256)
    for key in small:
        if isinstance(small[key],np.ndarray):np.testing.assert_array_equal(small[key],large[key])
        else:assert small[key] == large[key]
    assert small["unique_finite_rows"] == 3
    order = [4,0,5,2,1,3]; shuffled = grammar.decode(w[order],p[order],evidence=evidence,batch_size=2)
    for key in ("write_ids","parent_ids","path_code"):
        np.testing.assert_array_equal(shuffled[key],small[key][order])
    assert shuffled["score_numerators"] == tuple(small["score_numerators"][i] for i in order)
    np.testing.assert_array_equal(w,before[0]);np.testing.assert_array_equal(p,before[1])


@pytest.mark.parametrize("evidence,multiple",[("joint",1),("owner_marginal",4)])
def test_representable_per_head_constant_shifts_preserve_paths(evidence,multiple):
    rng = np.random.default_rng(16)
    write = rng.integers(-20,21,(3,4,16)).astype(float)
    parent = rng.integers(-20,21,(3,4,16)).astype(float)
    before = grammar.decode(write,parent,evidence=evidence)
    after = grammar.decode(write+np.arange(1,5)[None,:,None],
                           parent+np.arange(5,9)[None,:,None],evidence=evidence)
    np.testing.assert_array_equal(before["path_code"],after["path_code"])
    for row in range(3):assert value(after,row=row)-value(before,row=row) == 36*multiple


def test_self_copy_reads_before_write_and_no_self_flags_it():
    owners = grammar.owners_to_identities(np.array([[0,1,2,3]]),np.array([[0,0,1,2]]))
    assert owners["write_ids"].tolist() == [[1,5,9,13]]
    assert owners["parent_ids"].tolist() == [[0,1,5,9]]
    assert grammar.validate_paths(owners["write_ids"],owners["parent_ids"])["lawful"].all()
    strict = grammar.validate_paths(owners["write_ids"],owners["parent_ids"],allow_self=False)
    assert strict["flags"]["self_copy_forbidden"].tolist() == [[True,False,False,False]]
    assert strict["first_violation"].tolist() == [0]


def test_version_cap_and_wrong_versions_follow_predicted_owner_history():
    owners = np.zeros((1,4),dtype=int)
    counted = grammar.owners_to_identities(owners,owners)
    assert not counted["valid"].any() and (counted["write_ids"] == -1).all()
    assert counted["version_cap_exceeded"].tolist() == [[False,False,False,True]]
    checked = grammar.validate_paths(np.ones((1,4),dtype=int),np.zeros((1,4),dtype=int))
    assert checked["flags"]["parent_version_mismatch"].tolist() == [[False,True,True,True]]
    assert checked["flags"]["write_version_mismatch"].tolist() == [[False,True,True,True]]
    assert checked["flags"]["version_cap_exceeded"].tolist() == [[False,False,False,True]]


def test_validator_missing_invalid_and_unknown_history_are_explicit():
    write = np.array([[1,-1,5,9],[1,99,5,9]]); parent = np.array([[4,0,4,8],[4,0,4,8]])
    checked = grammar.validate_paths(write,parent)
    assert checked["flags"]["missing_id"][0,1] and checked["flags"]["invalid_id"][1,1]
    assert checked["flags"]["unknown_owner_history"].tolist() == [[False,False,True,True]]*2
    assert not checked["complete"].any() and not checked["lawful"].any()


@pytest.mark.parametrize("evidence",grammar.EVIDENCE)
def test_exact_path_scoring_matches_decoded_score_and_free_bound(evidence):
    rng = np.random.default_rng(45)
    w = rng.normal(size=(4,4,16)); p = rng.normal(size=(4,4,16))
    decoded = grammar.decode(w,p,evidence=evidence)
    selected = grammar.score_paths(w,p,decoded["write_ids"],decoded["parent_ids"],evidence=evidence)
    free = grammar.score_paths(w,p,decoded["free_write_ids"],decoded["free_parent_ids"],evidence=evidence)
    assert selected["score_numerators"] == decoded["score_numerators"]
    assert selected["score_exponents"] == decoded["score_exponents"]
    for row in range(4):assert value(free,row=row) == value(decoded,"free_upper_bound",row)


def test_lawful_free_joint_truth_preserved_and_whole_eight_cannot_decrease():
    write_owners = np.array([[0,1,0,2],[1,0,2,3],[3,3,1,0]])
    parent_owners = (write_owners+1)%4
    truth = grammar.owners_to_identities(write_owners,parent_owners)
    rng = np.random.default_rng(80)
    w = rng.normal(size=(3,4,16)); p = rng.normal(size=(3,4,16))
    for row,event in product(range(3),range(4)):
        w[row,event,truth["write_ids"][row,event]] = 100
        p[row,event,truth["parent_ids"][row,event]] = 100
    for allow_self in (True,False):
        decoded = grammar.decode(w,p,allow_self=allow_self)
        np.testing.assert_array_equal(decoded["free_write_ids"],truth["write_ids"])
        np.testing.assert_array_equal(decoded["write_ids"],truth["write_ids"])
        np.testing.assert_array_equal(decoded["parent_ids"],truth["parent_ids"])


def test_lawful_free_joint_is_preserved_with_many_exact_class_ties():
    truth = grammar.owners_to_identities(np.array([[0,0,0,1]]),np.zeros((1,4),dtype=int))
    w = np.full((1,4,16),-1.); p = np.full_like(w,-1.)
    for event in range(4):
        w[0,event,truth["write_ids"][0,event]:] = 0
        p[0,event,truth["parent_ids"][0,event]:] = 0
    decoded = grammar.decode(w,p)
    np.testing.assert_array_equal(decoded["free_write_ids"],truth["write_ids"])
    np.testing.assert_array_equal(decoded["write_ids"],truth["write_ids"])
    np.testing.assert_array_equal(decoded["parent_ids"],truth["parent_ids"])


def test_projection_can_harm_correct_parent_subset_when_free_writes_are_wrong():
    w = np.full((1,4,16),-1000.); p = np.full_like(w,-1000.)
    for event,candidate in enumerate((5,9,13,2)):w[0,event,candidate] = 100
    w[0,0,1] = 0;w[0,3,1] = 99
    p[:,:,4] = 100;p[:,1:,5] = 99
    truth = grammar.owners_to_identities(np.array([[0,2,3,0]]),np.ones((1,4),dtype=int))
    result = grammar.decode(w,p)
    np.testing.assert_array_equal(result["free_parent_ids"],truth["parent_ids"])
    assert not np.array_equal(result["parent_ids"],truth["parent_ids"])
    assert result["parent_ids"].tolist() == [[4,5,5,5]]


def test_joint_projection_can_harm_a_correct_factorized_tuple():
    w = np.zeros((1,4,16)); p = np.zeros_like(w)
    w[0,0,:4] = 9;w[0,0,5] = 10
    w[0,1,9] = 10;w[0,2,13] = 10;w[0,3,2] = 10;w[0,3,1] = 9.9
    p[:,:,4] = 10;p[:,:,5] = 9.9
    truth = grammar.owners_to_identities(np.array([[0,2,3,0]]),np.ones((1,4),dtype=int))
    def factorized(table):
        matrix = table.reshape(1,4,4,4)
        return 4*matrix.sum(axis=3).argmax(axis=2)+matrix.sum(axis=2).argmax(axis=2)
    np.testing.assert_array_equal(factorized(w),truth["write_ids"])
    np.testing.assert_array_equal(factorized(p),truth["parent_ids"])
    projected = grammar.decode(w,p)
    assert not np.array_equal(projected["write_ids"],truth["write_ids"])
    assert not np.array_equal(projected["parent_ids"],truth["parent_ids"])


@pytest.mark.parametrize("evidence",grammar.EVIDENCE)
def test_nested_no_self_scores_and_preservation_of_already_valid_broad_solution(evidence):
    rng = np.random.default_rng(92)
    w = rng.normal(size=(16,4,16)); p = rng.normal(size=(16,4,16))
    broad = grammar.decode(w,p,evidence=evidence)
    strict = grammar.decode(w,p,evidence=evidence,allow_self=False)
    legal = grammar.validate_paths(broad["write_ids"],broad["parent_ids"],allow_self=False)["lawful"]
    for row in range(16):assert value(strict,row=row) <= value(broad,row=row)
    np.testing.assert_array_equal(strict["write_ids"][legal],broad["write_ids"][legal])
    np.testing.assert_array_equal(strict["parent_ids"][legal],broad["parent_ids"][legal])


@pytest.mark.parametrize("bad",[np.nan,np.inf,-np.inf])
def test_any_nonfinite_cell_makes_entire_case_missing_without_candidate_pruning(bad):
    w = np.zeros((2,4,16)); p = np.zeros_like(w);w[0,3,15] = bad
    decoded = grammar.decode(w,p)
    assert decoded["finite"].tolist() == decoded["valid"].tolist() == [False,True]
    assert (decoded["write_ids"][0] == -1).all() and (decoded["parent_ids"][0] == -1).all()
    assert (decoded["free_write_ids"][0] == -1).all() and decoded["path_code"][0] == -1
    assert value(decoded) is None
    assert grammar.score_paths(w,p,decoded["write_ids"],decoded["parent_ids"])["valid"].tolist() == [False,True]


@pytest.mark.parametrize("dtype",[int,bool,complex,object])
def test_score_dtype_guards_reject_lossy_or_nonfloating_inputs(dtype):
    with pytest.raises(ValueError,match="floating score tables"):
        grammar.decode(np.zeros((1,4,16),dtype=dtype),np.zeros((1,4,16)))


def test_argument_geometry_and_metadata_free_signature_guards():
    scores = np.zeros((1,4,16))
    for kwargs in ({"evidence":"profile"},{"allow_self":1},{"batch_size":0},{"batch_size":True}):
        with pytest.raises(ValueError):grammar.decode(scores,scores,**kwargs)
    with pytest.raises(ValueError):grammar.decode(scores,np.zeros((2,4,16)))
    with pytest.raises(ValueError):grammar.decode(np.zeros((1,4,15)),scores)
    with pytest.raises(ValueError):grammar.owners_to_identities(np.zeros((1,4)),np.zeros((1,4),dtype=int))
    with pytest.raises(ValueError):grammar.validate_paths(np.zeros((1,4),dtype=bool),np.zeros((1,4),dtype=int))
    assert tuple(inspect.signature(grammar.decode).parameters) == (
        "write_joint","parent_joint","evidence","allow_self","batch_size")


def test_empty_float32_and_noncontiguous_tables_are_supported():
    empty = grammar.decode(np.empty((0,4,16)),np.empty((0,4,16)))
    assert empty["write_ids"].shape == (0,4) and empty["unique_finite_rows"] == 0
    scores = np.zeros((2,4,32),dtype=np.float32)[:,:,::2]
    assert not scores.flags.c_contiguous
    assert grammar.decode(scores,scores)["valid"].all()
