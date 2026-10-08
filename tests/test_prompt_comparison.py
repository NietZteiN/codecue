import numpy as np
import pytest

from codecue.prompt_comparison import paired_row, prompt_boundary, validate_predictions


def test_prompt_boundary_excludes_all_generated_tokens():
    tokenizer = lambda text, **kwargs: {"input_ids": [999] + list(text.encode())}
    prompt = "f([5, 3])\nTrace:"
    ids, boundary = prompt_boundary(tokenizer, prompt, " sum_all = 8")
    assert ids[boundary] == ord(":")
    assert len(ids) == len(prompt.encode()) + 1


def test_changed_boundary_tokenization_is_rejected():
    def tokenizer(text, **kwargs):
        return {"input_ids": [1, 2] if text.endswith(":") else [1, 3, 4]}
    with pytest.raises(ValueError, match="tokenization changes"):
        prompt_boundary(tokenizer, "Trace:", " v = 2")


def test_wrong_write_selection_comes_from_observed_generation_not_probe():
    old = {"model": "m", "regime": "trace", "id": "a", "program_key": "p",
           "condition": "incongruent@v1", "fold": 0, "layer": 4, "accuracy": 1.,
           "control_label": 3, "prefix_match": True, "stratum": "lure_write"}
    result = paired_row(old, model="m", regime="trace", id_="a", program_key="p",
                        true_value=2, predictions=[2, 2, 2], controls=[3, 3, 3],
                        prompt_layer=0, condition="incongruent@v1")
    assert result["stratum"] == "lure_write" and result["prompt_accuracy"] == 1.
    assert result["prewrite_minus_prompt"] == 0.
    with pytest.raises(ValueError, match="same computation"):
        paired_row(old, model="m", regime="trace", id_="a", program_key="other",
                   true_value=2, predictions=[2, 2, 2], controls=[3, 3, 3],
                   prompt_layer=0, condition="incongruent@v1")


@pytest.mark.parametrize("values", [np.zeros((2, 5)), np.full((3, 5), np.nan),
                                  np.full((3, 5), .3), np.full((3, 5), 10)])
def test_incomplete_or_invalid_prediction_arrays_are_rejected(values):
    with pytest.raises(ValueError, match="finite digit predictions"):
        validate_predictions(values, 5)
