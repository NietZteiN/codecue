"""Validate cached splits and the completed probe recipe before publishing scores."""
from __future__ import annotations

import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from functools import lru_cache

from .probe_data import assert_disjoint_metadata
from .config import DATA_DIR
from .generator import read_jsonl
from .probe_data import program_key


@lru_cache(maxsize=1)
def full_test_keys():
    return {program_key(instance) for instance in read_jsonl(DATA_DIR / "L5/test_sets.jsonl")}


def summarize_probe(data, train, tests, role="v1", position="pre@v1"):
    assert_disjoint_metadata(train, tests)
    if len(train["instances"]) != 2000 or any(x.get("condition") != "neutral" for x in train["instances"]):
        raise ValueError("expected 2000 neutral training programs")
    if any("program_key" not in x for x in train["instances"]):
        raise ValueError("training metadata lacks canonical program keys")
    if data["role"] != role or data["optimizer"] != "sgd" or data["epochs"] != 10000 or data["lr"] != 1e-3:
        raise ValueError("probe recipe differs from the fixed rerun")
    if data.get("standardize"):
        raise ValueError("reruns must use the unstandardized primary recipe")
    for group, test in tests.items():
        if data["test_ids"].get(group) != [x["id"] for x in test["instances"]]:
            raise ValueError(f"probe outputs and cached evaluation rows disagree: {group}")
    by_layer = defaultdict(list)
    for row in data["results"]:
        if row["position"] == position:
            by_layer[row["layer"]].append(row)
    if set(by_layer) != set(train["layers"]):
        raise ValueError("missing decision-position layers")
    misleading = f"incongruent@{role}"
    for layer, rows in by_layer.items():
        if len(rows) != 3 or {r["seed"] for r in rows} != {0, 1, 2}:
            raise ValueError(f"incomplete probe seeds at layer {layer}")
        for row in rows:
            for group in ("neutral", misleading):
                score = row["eval"][group]["accuracy"]
                control = row["control_acc"][group]
                if not all(math.isfinite(v) and 0 <= v <= 1 for v in (score, control)):
                    raise ValueError("invalid accuracy or missing control")
            metrics = row["eval"][misleading]
            if not math.isfinite(metrics["margin_mean"]) or not math.isfinite(metrics["lure_rate"]):
                raise ValueError("non-finite misleading-name probe readout")
    best = max(by_layer, key=lambda layer: mean(r["eval"]["neutral"]["accuracy"] for r in by_layer[layer]))
    rows = by_layer[best]
    majority = Counter(x["values"][role] for x in train["instances"]).most_common(1)[0][0]
    return {"layer": best, "n_train": len(train["instances"]),
            "n_neutral": len(tests["neutral"]["instances"]),
            "n_misleading": len(tests[misleading]["instances"]),
            "neutral_accuracy": mean(r["eval"]["neutral"]["accuracy"] for r in rows),
            "misleading_accuracy": mean(r["eval"][misleading]["accuracy"] for r in rows),
            "neutral_control": mean(r["control_acc"]["neutral"] for r in rows),
            "misleading_control": mean(r["control_acc"][misleading] for r in rows),
            "misleading_lure_rate": mean(r["eval"][misleading]["lure_rate"] for r in rows),
            "training_majority_digit": majority,
            "majority_accuracy": mean(x["values"][role] == majority for x in tests[misleading]["instances"]),
            "seeds": [0, 1, 2], "program_overlap": 0}


def validate_file(path):
    path = Path(path)
    data = json.loads(path.read_text())
    if not path.with_suffix(".npz").exists():
        raise ValueError(f"missing per-instance probe outputs: {path}")
    with zipfile.ZipFile(path.with_suffix(".npz")) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"corrupt per-instance probe outputs: {path}")
    train_dir = Path(data["train_dir"])
    train = json.loads((train_dir / "meta.json").read_text())
    tests = {group: json.loads((train_dir.parent / group / "meta.json").read_text())
             for group in data["test_ids"]}
    if not all(meta.get("pre_value_boundary_checked") for meta in (train, *tests.values())):
        raise ValueError("pre-value token boundary was not checked")
    if any(x["program_key"] in full_test_keys() for x in train["instances"]):
        raise ValueError("training computation overlaps the full test corpus")
    return summarize_probe(data, train, tests)
