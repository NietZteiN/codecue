#!/usr/bin/env python
"""Cross-fit decision-layer selection without touching probe training or test outcomes."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import DATA_DIR, OUT_DIR, RESULTS_DIR
from codecue.generator import read_jsonl
from codecue.probe_data import program_key
from codecue.probe_validation import validate_file
from codecue.round6 import crossfit_layers, fold_for
from codecue.stats import bootstrap_ci


def interval(rows, field):
    return list(bootstrap_ci([r[field] for r in rows], [r["program_key"] for r in rows], n_boot=4000)) if rows else None


def main():
    instances = {x.id: x for x in read_jsonl(DATA_DIR / "L5/test_sets.jsonl")}
    previous = json.loads((RESULTS_DIR / "summary/round5_error_probes.json").read_text())
    audited_rows = {(r["model"], r["regime"], r["id"]): r for r in previous["records"]}
    result = {"validated": True, "method": "5-fold canonical-computation cross-fitting of neutral layer selection",
              "selection": "neutral validation accuracy, average seeds0/1/2; lowest-layer tie break",
              "interval_scope": "cluster bootstrap conditional on the fixed fold selectors",
              "models": {}, "records": []}
    for model in ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it"):
        model_rows, runs = [], {}
        for demo_seed in (7, 11, 13):
            regime = "trace" if demo_seed == 7 else f"trace_s{demo_seed}"
            source = OUT_DIR / "probes_disjoint" / model / "L5" / regime / "v1.json"
            validate_file(source)
            data = json.loads(source.read_text())
            layers = sorted({r["layer"] for r in data["results"] if r["position"] == "pre@v1"})
            neutral_ids = data["test_ids"]["neutral"]
            keys = [program_key(instances[id_]) for id_ in neutral_ids]
            y = np.array([instances[id_].values["v1"] for id_ in neutral_ids])
            with np.load(source.with_suffix(".npz")) as arrays:
                predictions = {layer: np.stack([arrays[f"pre@v1/L{layer}/s{s}/neutral/pred"] for s in (0,1,2)]) for layer in layers}
                choices = crossfit_layers(predictions, y, keys)
                rows = []
                for group in ("neutral", "incongruent@v1"):
                    for i, id_ in enumerate(data["test_ids"][group]):
                        x = instances[id_]
                        key = program_key(x)
                        fold = fold_for(key)
                        layer = choices[fold]["layer"]
                        pred = np.array([arrays[f"pre@v1/L{layer}/s{s}/{group}/pred"][i] for s in (0,1,2)])
                        if not np.isfinite(pred).all():
                            raise ValueError("nonfinite held-out predictions")
                        row = {"model": model, "regime": regime, "id": id_, "set_id": x.set_id,
                               "program_key": key, "fold": fold, "layer": layer, "condition": group,
                               "accuracy": float(np.mean(pred == x.values["v1"]))}
                        if group != "neutral":
                            old = audited_rows[model, regime, id_]
                            row.update(prefix_match=old["prefix_match"], stratum=old["stratum"],
                                       previous_accuracy=old["probe_accuracy"])
                            row["accuracy_change"] = row["accuracy"] - row["previous_accuracy"]
                        rows.append(row)
                runs[regime] = {"folds": choices, "neutral_accuracy_ci95": interval([r for r in rows if r["condition"] == "neutral"], "accuracy"),
                                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            model_rows += rows
            print(model, regime, "layers", {f:c["layer"] for f,c in choices.items()}, flush=True)
        eligible = [r for r in model_rows if r.get("prefix_match")]
        strata = {}
        for group in ("lure_write", "correct_write", "other_error"):
            rows = [r for r in eligible if r["stratum"] == group]
            strata[group] = {"n":len(rows), "n_programs":len({r["program_key"] for r in rows}),
                             "accuracy_ci95":interval(rows,"accuracy"), "change_ci95":interval(rows,"accuracy_change")}
        result["models"][model] = {"runs":runs, "pooled":strata}
        result["records"] += model_rows
    path = RESULTS_DIR / "summary/round6_crossfit_probes.json"
    temp = path.with_suffix(".tmp"); temp.write_text(json.dumps(result,indent=2)+"\n"); temp.replace(path)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
