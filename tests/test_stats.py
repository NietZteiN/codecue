import numpy as np
import pytest

from codecue.stats import bootstrap_ci


def test_repeated_seed_observations_do_not_become_independent_programs():
    values = np.repeat([0.0, 1.0], 100)
    clusters = np.repeat(["a", "b"], 100)
    assert bootstrap_ci(values, clusters) == (0.5, 0.0, 1.0)


def test_unequal_cluster_sizes_keep_the_observation_weighted_estimate():
    assert bootstrap_ci([0.0] + [1.0] * 9, ["a"] + ["b"] * 9) == (0.9, 0.0, 1.0)


def test_equivalence_interval_is_nested_inside_effect_interval():
    values = np.arange(30, dtype=float) / 30
    clusters = np.arange(30)
    p90, lo90, hi90 = bootstrap_ci(values, clusters, confidence=0.90)
    p95, lo95, hi95 = bootstrap_ci(values, clusters, confidence=0.95)
    assert p90 == p95
    assert lo95 < lo90 < hi90 < hi95


@pytest.mark.parametrize("values,clusters,confidence", [([], [], .95), ([1], [], .95), ([1], [0], 1)])
def test_invalid_inputs_fail(values, clusters, confidence):
    with pytest.raises(ValueError):
        bootstrap_ci(values, clusters, confidence=confidence)
