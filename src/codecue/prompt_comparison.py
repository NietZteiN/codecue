"""Guards for comparing prompt-end and pre-write readouts on identical programs."""
from __future__ import annotations

import numpy as np

from .probe_data import assert_disjoint_metadata


def prompt_boundary(tokenizer, prompt, continuation):
    """Return the last prompt token only when it survives continuation tokenization."""
    ids = tokenizer(prompt, add_special_tokens=True)["input_ids"]
    extended = tokenizer(prompt + continuation, add_special_tokens=True)["input_ids"]
    if not ids or extended[:len(ids)] != ids:
        raise ValueError("prompt tokenization changes at the generation boundary")
    return ids, len(ids) - 1


def validate_predictions(predictions, n):
    predictions = np.asarray(predictions)
    if (predictions.shape != (3, n) or not np.isfinite(predictions).all()
            or not np.equal(predictions, np.floor(predictions)).all()
            or not ((0 <= predictions) & (predictions < 10)).all()):
        raise ValueError("expected three seeds of finite digit predictions in row order")
    return predictions


def validate_prompt_output(data, train, tests):
    assert_disjoint_metadata(train, tests)
    if (len(train["instances"]) != 2000 or any(x["condition"] != "neutral" for x in train["instances"])
            or data["role"] != "v1" or data["optimizer"] != "sgd" or data["epochs"] != 10000
            or data["lr"] != 1e-3 or data.get("standardize")):
        raise ValueError("prompt probes differ from the original training recipe")
    if set(tests) != {"neutral", "incongruent@v1"} or set(data["test_ids"]) != set(tests):
        raise ValueError("expected the original two evaluation groups")
    for meta in (train, *tests.values()):
        if not meta.get("prompt_only") or not meta.get("prompt_boundary_checked"):
            raise ValueError("prompt cache has no verified pre-generation boundary")
        if meta["pos_labels"] != ["prompt_end"] or meta["layers"] != train["layers"]:
            raise ValueError("prompt cache positions or layers disagree")
    for group, meta in tests.items():
        if data["test_ids"][group] != [x["id"] for x in meta["instances"]]:
            raise ValueError("prompt outputs and cached evaluation order disagree")
    expected = {(layer, seed) for layer in train["layers"] for seed in (0, 1, 2)}
    seen = set()
    for row in data["results"]:
        key = row["layer"], row["seed"]
        if row["position"] != "prompt_end" or key not in expected or key in seen:
            raise ValueError("unexpected or repeated prompt probe fit")
        seen.add(key)
        for group in tests:
            for value in (row["eval"][group]["accuracy"], row["control_acc"][group]):
                if not np.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError("invalid prompt probe accuracy")
        for field in ("margin_mean", "lure_rate", "lure_mass"):
            if not np.isfinite(row["eval"]["incongruent@v1"][field]):
                raise ValueError("nonfinite prompt probe readout")
    if seen != expected:
        raise ValueError("incomplete prompt probe layers or seeds")


def paired_row(old, *, model, regime, id_, program_key, true_value, predictions,
               controls, prompt_layer, condition):
    """Use the previously audited outcome; never reclassify errors using probe outputs."""
    if (old["model"], old["regime"], old["id"], old["program_key"]) != (
            model, regime, id_, program_key):
        raise ValueError("prompt and pre-write readouts do not describe the same computation")
    if old["condition"] != condition:
        raise ValueError("readout conditions disagree")
    accuracy = float(np.mean(np.asarray(predictions) == true_value))
    return {
        "model": model, "regime": regime, "id": id_, "program_key": program_key,
        "condition": condition, "fold": old["fold"], "prompt_layer": prompt_layer,
        "prewrite_layer": old["layer"], "prompt_accuracy": accuracy,
        "prewrite_accuracy": old["accuracy"],
        "prewrite_minus_prompt": old["accuracy"] - accuracy,
        "prompt_control_accuracy": float(np.mean(np.asarray(controls) == old["control_label"])),
        **({"prefix_match": old["prefix_match"], "stratum": old["stratum"]}
           if condition != "neutral" else {}),
    }
