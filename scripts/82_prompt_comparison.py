#!/usr/bin/env python
"""Release paired prompt-end versus pre-write readouts after all GPU fits validate."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import OUT_DIR, RESULTS_DIR
from codecue.prompt_comparison import paired_row, validate_predictions, validate_prompt_output
from codecue.probes import control_labels
from codecue.round6 import crossfit_layers, fold_for
from codecue.stats import bootstrap_ci

MODELS = ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it")
REGIMES = ("trace", "trace_s11", "trace_s13")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def interval(rows, field):
    return list(bootstrap_ci([r[field] for r in rows], [r["program_key"] for r in rows],
                             n_boot=4000)) if rows else None


def summarize(rows):
    return {"n": len(rows), "n_programs": len({r["program_key"] for r in rows}),
            **{f"{field}_ci95": interval(rows, field) for field in (
                "prompt_accuracy", "prewrite_accuracy", "prewrite_minus_prompt",
                "prompt_control_accuracy")}}


def main():
    original_path = RESULTS_DIR / "summary/round6_crossfit_probes.json"
    original = json.loads(original_path.read_text())
    if not original.get("validated"):
        raise ValueError("the reference pre-write release is not validated")
    old_rows = {(r["model"], r["regime"], r["id"]): r for r in original["records"]}
    if len(old_rows) != len(original["records"]):
        raise ValueError("duplicate pre-write observations")
    result = {"validated": False, "comparison": "final full-prompt token versus pre-value marker",
              "selection": "independent five-fold neutral-only layer selection at each position",
              "interval_scope": "paired canonical-computation bootstrap conditional on fixed selectors",
              "reference_sha256": digest(original_path), "models": {}, "records": []}
    for model in MODELS:
        rows, runs = [], {}
        for regime in REGIMES:
            source = OUT_DIR / "prompt_end_probes" / model / "L5" / regime / "v1.json"
            data = json.loads(source.read_text())
            receipt = json.loads(source.with_suffix(".receipt.json").read_text())
            reference = OUT_DIR / "probes_disjoint" / model / "L5" / regime / "v1.json"
            if (receipt["reference_probes_sha256"] != digest(reference)
                    or receipt["probes_sha256"] != digest(source)
                    or receipt["arrays_sha256"] != digest(source.with_suffix(".npz"))):
                raise ValueError("probe receipt does not match the source files")
            root = Path(data["train_dir"]).parent
            train = json.loads((root / "train_neutral/meta.json").read_text())
            tests = {g: json.loads((root / g / "meta.json").read_text()) for g in data["test_ids"]}
            validate_prompt_output(data, train, tests)
            neutral = tests["neutral"]["instances"]
            keys = [x["program_key"] for x in neutral]
            labels = [x["values"]["v1"] for x in neutral]
            with np.load(source.with_suffix(".npz")) as arrays:
                predictions = {layer: validate_predictions(np.stack([
                    arrays[f"prompt_end/L{layer}/s{s}/neutral/pred"] for s in (0, 1, 2)
                ]), len(neutral)) for layer in train["layers"]}
                choices = crossfit_layers(predictions, labels, keys)
                for group, meta in tests.items():
                    control_y = control_labels(meta, "v1")
                    group_arrays = {
                        (layer, field): validate_predictions(np.stack([
                            arrays[f"prompt_end/L{layer}/s{s}/{group}/{field}"] for s in (0, 1, 2)
                        ]), len(meta["instances"]))
                        for layer in train["layers"] for field in ("pred", "control_pred")
                    }
                    for i, x in enumerate(meta["instances"]):
                        key = x["program_key"]
                        old = {**old_rows[model, regime, x["id"]], "control_label": int(control_y[i])}
                        if old["fold"] != fold_for(key):
                            raise ValueError("the canonical fold changed between positions")
                        layer = choices[old["fold"]]["layer"]
                        rows.append(paired_row(old, model=model, regime=regime, id_=x["id"],
                                              program_key=key, true_value=x["values"]["v1"],
                                              predictions=group_arrays[layer, "pred"][:, i],
                                              controls=group_arrays[layer, "control_pred"][:, i],
                                              prompt_layer=layer, condition=group))
            runs[regime] = {"folds": choices, "source_sha256": digest(source),
                            "arrays_sha256": receipt["arrays_sha256"]}
        misleading = [r for r in rows if r["condition"] != "neutral"]
        eligible = [r for r in misleading if r["prefix_match"]]
        strata = {s: summarize([r for r in eligible if r["stratum"] == s])
                  for s in ("lure_write", "correct_write", "other_error")}
        for stratum, summary in strata.items():
            old = original["models"][model]["pooled"][stratum]
            if summary["n"] != old["n"] or summary["n_programs"] != old["n_programs"]:
                raise ValueError("the observed outcome cohort changed")
            if summary["prewrite_accuracy_ci95"] != old["accuracy_ci95"]:
                raise ValueError("the paired pre-write reference changed")
        result["models"][model] = {
            "runs": runs, "n_total": len(misleading), "n_prefix_match": len(eligible),
            "neutral": summarize([r for r in rows if r["condition"] == "neutral"]), "pooled": strata,
        }
        result["records"].extend(rows)
        print(model, "observed wrong writes", strata["lure_write"], flush=True)
    result["validated"] = True
    path = RESULTS_DIR / "summary/round7_prompt_comparison.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
