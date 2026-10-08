import pytest

from codecue.probe_validation import summarize_probe


def fixture():
    train = {"layers": [0, 2], "instances": [
        {"id": str(i), "set_id": f"train{i}", "program_key": f"program{i}",
         "condition": "neutral", "values": {"v1": i % 3}} for i in range(2000)]}
    tests = {group: {"instances": [
        {"id": group, "set_id": "heldout", "program_key": "unseen", "values": {"v1": 0}}]}
        for group in ("neutral", "incongruent@v1")}
    rows = [{"position": "pre@v1", "layer": layer, "seed": seed,
             "eval": {"neutral": {"accuracy": 0.9 if layer == 0 else 0.8},
                      "incongruent@v1": {"accuracy": 0.7 if layer == 0 else 1.0, "lure_rate": 0.1, "margin_mean": 0.4}},
             "control_acc": {"neutral": 0.5, "incongruent@v1": 0.2}}
            for layer in (0, 2) for seed in (0, 1, 2)]
    data = {"role": "v1", "optimizer": "sgd", "epochs": 10000, "lr": 1e-3,
            "results": rows, "test_ids": {g: [g] for g in tests}}
    return data, train, tests


def test_layer_is_selected_by_neutral_accuracy_not_misleading_accuracy():
    result = summarize_probe(*fixture())
    assert result["layer"] == 0
    assert result["misleading_accuracy"] == pytest.approx(0.7)
    assert result["program_overlap"] == 0


def test_missing_seed_cannot_be_released():
    data, train, tests = fixture()
    data["results"].pop()
    with pytest.raises(ValueError, match="seeds"):
        summarize_probe(data, train, tests)


def test_changed_test_order_cannot_be_released():
    data, train, tests = fixture()
    data["test_ids"]["neutral"] = ["different"]
    with pytest.raises(ValueError, match="disagree"):
        summarize_probe(data, train, tests)


def test_a_renamed_copy_cannot_be_released():
    data, train, tests = fixture()
    tests["incongruent@v1"]["instances"][0]["program_key"] = "program0"
    with pytest.raises(ValueError, match="overlaps"):
        summarize_probe(data, train, tests)


def test_nonfinite_readout_cannot_be_released():
    data, train, tests = fixture()
    data["results"][0]["eval"]["incongruent@v1"]["margin_mean"] = float("nan")
    with pytest.raises(ValueError, match="non-finite"):
        summarize_probe(data, train, tests)
