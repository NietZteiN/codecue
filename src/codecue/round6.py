"""Fixed, outcome-independent selections for the second reviewer follow-up round."""
from __future__ import annotations

import hashlib
import math

import numpy as np


def fold_for(key: str, n_folds: int = 5) -> int:
    return int.from_bytes(hashlib.sha256(f"round6:{key}".encode()).digest()[:8], "big") % n_folds


def crossfit_layers(predictions, labels, keys):
    """Layer choices for each fold use only other folds' neutral labels."""
    labels = np.asarray(labels)
    folds = np.array([fold_for(key) for key in keys])
    choices = {}
    for fold in range(5):
        validation = folds != fold
        if not validation.any() or not (folds == fold).any():
            raise ValueError("cross-fitting requires nonempty validation and test folds")
        scores = {}
        for layer, pred in predictions.items():
            pred = np.asarray(pred)
            if pred.shape != (3, len(labels)) or not np.isfinite(pred).all():
                raise ValueError("invalid neutral prediction arrays")
            scores[layer] = float(np.mean(pred[:, validation] == labels[validation]))
        layer = max(sorted(scores), key=scores.get)
        choices[fold] = {"layer": layer, "validation_accuracy": scores[layer],
                         "n_validation": int(validation.sum()), "n_test": int((~validation).sum())}
    return choices


def select_identifiers(gates, panel, candidates, threshold=.8, limit=3):
    if set(gates) != set(panel):
        raise ValueError("meaning gate must contain exactly the fixed model panel")
    minimum = math.ceil(threshold * len(panel))
    scores = {}
    for name in candidates:
        passed = [model for model in panel if gates[model]["canonical"][name]["argmax"] == "sum"]
        scores[name] = {"n_pass": len(passed), "n_models": len(panel),
                        "pass_models": passed, "panel_pass": len(passed) >= minimum}
    return [name for name in candidates if scores[name]["panel_pass"]][:limit], scores
