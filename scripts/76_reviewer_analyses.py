#!/usr/bin/env python
"""A1/A2: prefix-audited error readouts and original identifier-gate sensitivity."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.cache import cache_spans, trace_text
from codecue.config import DATA_DIR, OUT_DIR, RESULTS_DIR, model_entry
from codecue.followups import first_value_boundary, write_class
from codecue.generator import read_jsonl
from codecue.layout import assert_before_value, spans_to_tokens
from codecue.probe_validation import validate_file
from codecue.prompts import build_prompt, demos
from codecue.stats import bootstrap_ci

MODELS = ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it")


def read(path):
    return [json.loads(line) for line in path.open()]


def interval(rows, field):
    if not rows:
        return None
    return list(bootstrap_ci([r[field] for r in rows], [r["set_id"] for r in rows], n_boot=4000))


def code_errors():
    from transformers import AutoTokenizer
    instances = {x.id:x for x in read_jsonl(DATA_DIR / "L5/test_sets.jsonl")}
    result = {"validated": True, "selection": "neutral accuracy, three-seed mean",
        "prefix_rule": "exact token IDs through the pre-value marker, excluding any supplied digit",
        "models": {}, "records": []}
    for model in MODELS:
        tok = AutoTokenizer.from_pretrained(model_entry(model)["hf_id"], local_files_only=True)
        model_rows = []
        runs = {}
        for seed in (7, 11, 13):
            regime = "trace" if seed == 7 else f"trace_s{seed}"
            source = OUT_DIR / "probes_disjoint" / model / "L5" / regime / "v1.json"
            audited = validate_file(source)
            data = json.loads(source.read_text())
            ids = data["test_ids"]["incongruent@v1"]
            behaviors = {r["id"]:r for r in read(OUT_DIR / "runs" / model / "L5" / regime / "incongruent@v1/behavior.jsonl")}
            ds = demos(5, seed, "trace")
            rows = []
            with np.load(source.with_suffix(".npz")) as arrays:
                pred = np.array([arrays[f"pre@v1/L{audited['layer']}/s{s}/incongruent@v1/pred"] for s in (0,1,2)])
                margin = np.array([arrays[f"pre@v1/L{audited['layer']}/s{s}/incongruent@v1/margin"] for s in (0,1,2)])
            if pred.shape != (3,285) or margin.shape != pred.shape or not np.isfinite(margin).all():
                raise ValueError("incomplete or non-finite saved predictions")
            for i, id_ in enumerate(ids):
                x, behavior = instances[id_], behaviors[id_]
                boundary = first_value_boundary(behavior["generation"], x.names["v1"])
                matches = False
                if boundary:
                    prompt = build_prompt(x, regime, ds)
                    gold = tok(prompt + trace_text(x), return_offsets_mapping=True, add_special_tokens=True)
                    gi = spans_to_tokens(cache_spans(prompt, trace_text(x), x, "v1"), gold["offset_mapping"])["pre@v1"]
                    actual = tok(prompt + behavior["generation"], return_offsets_mapping=True, add_special_tokens=True)
                    marker = len(prompt) + boundary["marker"]
                    token = next((j for j,(a,b) in enumerate(actual["offset_mapping"]) if a <= marker < b), None)
                    if token is not None:
                        try:
                            assert_before_value(actual["offset_mapping"], token, len(prompt) + boundary["value_start"])
                            matches = actual["input_ids"][:token+1] == gold["input_ids"][:gi+1]
                        except ValueError:
                            pass
                rows.append({"model":model,"regime":regime,"id":id_,"set_id":x.set_id,
                    "prefix_match":matches, "stratum":write_class(behavior["value_written"], x.values["v1"], x.lure),
                    "probe_accuracy":float(np.mean(pred[:,i] == x.values["v1"])),
                    "margin":float(np.mean(margin[:,i])), "layer":audited["layer"]})
            eligible = [r for r in rows if r["prefix_match"]]
            runs[regime] = {"n_total":len(rows),"n_prefix_match":len(eligible),"n_excluded":len(rows)-len(eligible),
                "strata": {group:{"n":sum(r["stratum"]==group for r in eligible),
                    "accuracy_ci95":interval([r for r in eligible if r["stratum"]==group], "probe_accuracy"),
                    "margin_ci95":interval([r for r in eligible if r["stratum"]==group], "margin")}
                    for group in ("lure_write","correct_write","other_error")}}
            model_rows += rows
        eligible = [r for r in model_rows if r["prefix_match"]]
        result["models"][model] = {"runs":runs,"n_total":len(model_rows),"n_prefix_match":len(eligible),
            "pooled":{group:{"n":sum(r["stratum"]==group for r in eligible),
                "n_sets":len({r["set_id"] for r in eligible if r["stratum"]==group}),
                "accuracy_ci95":interval([r for r in eligible if r["stratum"]==group], "probe_accuracy"),
                "margin_ci95":interval([r for r in eligible if r["stratum"]==group], "margin")}
                for group in ("lure_write","correct_write","other_error")},
            "unfiltered_diagnostic":{group:interval([r for r in model_rows if r["stratum"]==group],"probe_accuracy")
                for group in ("lure_write","correct_write","other_error")}}
        result["records"] += model_rows
        print(model, "prefix coverage", len(eligible), "/", len(model_rows), flush=True)
    return result


def identifier_sensitivity():
    gate = json.loads((RESULTS_DIR / "summary/lure_gate_v2.json").read_text())
    instances = {x.id:x for x in read_jsonl(DATA_DIR / "L5/test_sets.jsonl")}
    names = ("total","sum_all","acc")
    panel_pass = {name:bool(np.mean([d[name]["pass"] for d in gate.values()]) >= .8) for name in names}
    result = {"validated":True,"cell":"L5 len-to-sum", "panel_pass":panel_pass,"models":{},
        "interpretation":"Exploratory sensitivity using the original gate; does not erase the protocol deviation."}
    for model in gate:
        values = []
        for seed in (7,11,13):
            regime = "trace" if seed==7 else f"trace_s{seed}"
            root = OUT_DIR / "runs" / model / "L5" / regime
            inc = read(root / "incongruent@v1/behavior.jsonl")
            neutral = {r["set_id"]:r for r in read(root / "neutral/behavior.jsonl")}
            for row in inc:
                x=instances[row["id"]]
                if x.stmts[0]["op"] != "len" or row["lure_name"] not in names:
                    continue
                twin=neutral[row["set_id"]]
                values.append({"set_id":row["set_id"],"seed":seed,"name":row["lure_name"],
                    "delta":int(row["value_written"]==row["lure"])-int(twin["values_written"]["v1"]==row["lure"])})
        subsets={"all":values,"panel_gate":[r for r in values if panel_pass[r["name"]]],
            "model_gate":[r for r in values if gate[model][r["name"]]["pass"]],
            **{name:[r for r in values if r["name"]==name] for name in names}}
        summary={}
        for key,rows in subsets.items():
            ci=interval(rows,"delta")
            seeds={str(s):float(np.mean([r["delta"] for r in rows if r["seed"]==s]))
                for s in (7,11,13) if any(r["seed"]==s for r in rows)}
            summary[key]={"n":len(rows),"n_sets":len({r["set_id"] for r in rows}),"excess_ci95":ci,
                "by_seed":seeds,"reliable":bool(ci and len(seeds)==3 and
                    (all(x>0 for x in seeds.values()) or all(x<0 for x in seeds.values())) and (ci[1]>0 or ci[2]<0))}
        result["models"][model]={"subsets":summary,"gate":{name:gate[model][name] for name in names}}
    return result


def main():
    summary=RESULTS_DIR / "summary"
    for name,function in (("round5_error_probes",code_errors),("round5_identifiers",identifier_sensitivity)):
        data=function(); destination=summary / f"{name}.json"
        destination.write_text(json.dumps(data,indent=2)+"\n")
        print("wrote",destination,flush=True)


if __name__ == "__main__":
    main()
