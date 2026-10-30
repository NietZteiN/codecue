import pytest

from codecue.binding.continuation_review import clustered_delta


def test_paired_effect_preserves_direction_and_clusters_related_questions():
    pairs = [('one_structure', True, False)] * 10 + [('another_structure', False, True)] * 5
    result = clustered_delta(pairs)
    assert result['estimate'] == pytest.approx(1/3)
    assert result['pairs'] == 15 and result['structural_components'] == 2
    assert result['exploratory_cluster_bootstrap_95_interval'] is None


def test_cluster_bootstrap_is_deterministic_and_does_not_treat_rows_as_structures():
    pairs = [(str(i), True, False) for i in range(10)]
    a = clustered_delta(pairs)
    assert a == clustered_delta(pairs)
    assert a['estimate'] == 1 and a['exploratory_cluster_bootstrap_95_interval'] == [1., 1.]
    with pytest.raises(ValueError, match='empty'):
        clustered_delta([])
