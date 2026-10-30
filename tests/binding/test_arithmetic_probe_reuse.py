from pathlib import Path

import pytest

from codecue.binding import arithmetic_probe_reuse as reuse
from codecue.binding import relationship_capture as base


def test_reuse_allows_only_adapter_and_publication_name_repair(tmp_path):
    source = Path('src/codecue/binding/arithmetic_probe_selection.py').read_text()
    before = tmp_path / 'before.py'
    after = tmp_path / 'after.py'
    before.write_text(source)
    after.write_text(source.replace("key = f'selected_{representation}_seed{seed}'", "key = f'final_{representation}_seed{seed}'"))
    assert reuse.recipe(before) == reuse.recipe(after)
    after.write_text(source.replace('fit_mask = fold_ids != fold', 'fit_mask = fold_ids == fold'))
    assert reuse.recipe(before) != reuse.recipe(after)
    after.write_text(source.replace('10000.', '1000.'))
    assert reuse.recipe(before) != reuse.recipe(after)


def test_artifact_names_do_not_weaken_reserved_outcome_protection():
    base._safe('artifacts/binding/example/selected_hidden_seed11_parameters.npz')
    with pytest.raises(ValueError):
        base._safe('artifacts/binding/example/final_hidden_seed11_parameters.npz')
