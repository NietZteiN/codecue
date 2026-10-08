from types import SimpleNamespace

import pytest

from codecue.probe_data import assert_disjoint_metadata, disjoint_training


def example(xs, condition="neutral", name="v"):
    return SimpleNamespace(xs=xs, stmts=[{"op": "len", "args": ["xs"]}],
                           query="v1", condition=condition, names={"v1": name})


def test_renaming_does_not_hide_training_test_overlap():
    train = [example([1, 2]), example([3, 4]), example([5, 6])]
    test = [example([1, 2], "incongruent", "sum_all")]
    assert disjoint_training(train, test, 1) == train[1:2]


def test_test_set_cannot_be_used_as_the_training_pool():
    test = [example([1, 2])]
    with pytest.raises(ValueError, match="no disjoint"):
        disjoint_training(test, test, 10)


def test_non_neutral_training_is_rejected():
    with pytest.raises(ValueError, match="neutral"):
        disjoint_training([example([1, 2], "incongruent")], [example([3, 4])], 10)


@pytest.mark.parametrize("test_instance", [
    {"set_id": "train", "program_key": "other"},
    {"set_id": "renamed", "program_key": "same"},
])
def test_saved_cache_overlap_is_rejected(test_instance):
    train = {"instances": [{"set_id": "train", "program_key": "same"}]}
    with pytest.raises(ValueError, match="overlaps"):
        assert_disjoint_metadata(train, {"incongruent": {"instances": [test_instance]}})


def test_disjoint_legacy_cache_metadata_is_accepted():
    assert_disjoint_metadata({"instances": [{"set_id": "train"}]},
                             {"neutral": {"instances": [{"set_id": "test"}]}})
