"""Descriptive discovery analyses; uncertainty resamples structural templates."""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from codecue.stats import bootstrap_ci
from .datasets import read_jsonl, write_json


def interval(values, clusters):
    if len(set(clusters)) < 2:
        return {'estimate': float(np.mean(values)), 'ci95': None, 'clusters': len(set(clusters)),
                'uncertainty_status': 'fewer than two independent clusters'}
    estimate, low, high = bootstrap_ci(values, clusters, n_boot=2000, seed=17)
    return {"estimate": estimate, "ci95": [low, high], "clusters": len(set(clusters))}


def summarize(rows):
    if not rows:
        raise ValueError("empty behavioral run")
    structural_templates = len({r["template_id"] for r in rows})
    rows = [{**r, "template_id": r.get("cluster_id", r["template_id"])} for r in rows]
    groups = defaultdict(list)
    for r in rows:
        groups[(r["split"], r["control_kind"], r["condition"], r["family"], r["load"], r["updates"])].append(r)
    cells = []
    for keys, cell in sorted(groups.items()):
        cells.append({**dict(zip(("split", "control_kind", "condition", "family", "load", "updates"), keys)),
                      "n": len(cell), "invalid": sum(r["prediction"] is None for r in cell),
                      "accuracy": interval([r["correct"] for r in cell], [r["template_id"] for r in cell])})
    # Each paired delta first averages lexical realizations, preserving base grouping.
    paired = defaultdict(dict)
    for r in rows:
        key = (r["base_id"], r["control_kind"])
        paired[key].setdefault(r["condition"], []).append(r)
    deltas = []
    for key, conditions in paired.items():
        if set(conditions) != {"neutral", "informative", "misleading"}:
            raise ValueError("unbalanced naming conditions in run")
        neutral = np.mean([r["correct"] for r in conditions["neutral"]])
        for condition in ("informative", "misleading"):
            first = conditions[condition][0]
            deltas.append({**{k: first[k] for k in ("template_id", "family", "load", "updates", "split", "control_kind")},
                           "condition": condition, "delta": float(np.mean([r["correct"] for r in conditions[condition]]) - neutral)})
    naming = []
    for condition in ("informative", "misleading"):
        for kind in sorted({r["control_kind"] for r in rows}):
            for split in sorted({r["split"] for r in rows}):
                selected = [r for r in deltas if r["condition"] == condition and r["control_kind"] == kind and r["split"] == split]
                if selected:
                    naming.append({"condition": condition, "control_kind": kind, "split": split,
                                   **interval([r["delta"] for r in selected], [r["template_id"] for r in selected])})
    labels = Counter(label for r in rows for label in r["classification"]["compatible_labels"])
    interactions = []
    for condition in ("informative", "misleading"):
        for kind in sorted({r["control_kind"] for r in rows}):
            for split in sorted({r["split"] for r in rows}):
                subset = [r for r in deltas if r["condition"] == condition and r["control_kind"] == kind and r["split"] == split]
                for factor, low, high in (("load", 2, 4), ("updates", 1, 3)):
                    a, b = [r for r in subset if r[factor] == low], [r for r in subset if r[factor] == high]
                    if a and b:
                        # Weighted contrast, balanced cells give +/-2 weights. Retain
                        # parent-template clusters across both load conditions.
                        n = len(a) + len(b)
                        values = [-n / len(a) * r["delta"] for r in a] + [n / len(b) * r["delta"] for r in b]
                        interactions.append({"condition": condition, "control_kind": kind, "split": split,
                                             "factor": factor, "contrast": "high minus low naming effect",
                                             **interval(values, [r["template_id"] for r in a + b])})
    parsed = [r for r in rows if r["prediction"] is not None]
    distinct = [r for r in rows if r["diagnostically_distinct_available"]]
    by_control_kind = {}
    for kind in sorted({r['control_kind'] for r in rows}):
        subset = [r for r in rows if r['control_kind'] == kind]
        by_control_kind[kind] = {'n':len(subset), 'invalid_count':sum(r['prediction'] is None for r in subset),
                                 'accuracy':interval([r['correct'] for r in subset], [r['template_id'] for r in subset])}
    return {"n": len(rows), "bases": len({r["base_id"] for r in rows}),
            "templates": structural_templates,
            "independent_template_clusters": len({r["template_id"] for r in rows}),
            "accuracy": interval([r["correct"] for r in rows], [r["template_id"] for r in rows]),
            "invalid_count": len(rows) - len(parsed),
            "parsed_accuracy": sum(r["correct"] for r in parsed) / len(parsed) if parsed else None,
            "ambiguous_error_count": sum(r["classification"]["ambiguous"] for r in rows),
            "counterfactual_consistent_error_counts_nonexclusive": dict(labels),
            "diagnostically_distinct_subset_n": len(distinct),
            "diagnostically_distinct_error_count": sum(r["classification"]["status"] == "semantic_error" and bool(r["classification"]["compatible_alternatives"])
                                                       and not r["classification"]["ambiguous"] for r in distinct),
            "cells": cells, "within_base_naming_deltas": naming, "naming_factor_interactions": interactions,
            'by_control_kind': by_control_kind,
            "inference_unit": "structural template; all numeric, lexical and counterfactual relatives clustered",
            "analysis_status": "discovery; no frozen explanatory hypothesis or confirmatory holdout result"}


def report(run_dir):
    stage = run_dir / "behavior"
    rows = read_jsonl(stage / "responses.jsonl")
    summary = summarize(rows)
    manifest = json.loads((stage / "manifest.json").read_text())
    summary['complete'] = manifest['status'] == 'complete' and len(rows) == manifest.get('samples_planned')
    from .registry import code_identity
    summary['analysis_source_sha256'] = code_identity()['source_sha256']
    summary['behavior_identity_hash'] = manifest['identity_hash']
    write_json(stage / "summary.json", summary)
    accuracy = summary["accuracy"]
    text = ["# Binding behavioral discovery report", "",
            f"Completed {len(rows)} / {manifest.get('samples_planned', '?')} planned responses across {summary['bases']} bases and {summary['templates']} structural templates.", "",
            f"Exact accuracy: {accuracy['estimate']:.3f}; template-cluster 95% bootstrap interval {accuracy['ci95']}. "
            f"Invalid outputs: {summary['invalid_count']}; ambiguous diagnostic errors: {summary['ambiguous_error_count']}.", "",
            "Intervals in small cells can be degenerate and do not provide a power analysis. "
            "Compatible error labels describe outputs and cannot identify internal causes.", "",
            "| Split | Control | Naming | Difference from neutral | 95% interval |", "|---|---|---|---:|---|"]
    for effect in summary["within_base_naming_deltas"]:
        text.append(f"| {effect['split']} | {effect['control_kind']} | {effect['condition']} | {effect['estimate']:.3f} | {effect['ci95']} |")
    device = manifest['identity']['config']['device']
    text.extend(["", f"Wall seconds: {manifest.get('wall_seconds_total')}; {device.upper()} forward/generation seconds: {manifest.get('device_seconds')}. "
                 f"Peak allocated GPU bytes: {manifest.get('gpu_peak_bytes')}. Device: {manifest.get('device_name')}.", "",
                 "See summary.json for every factorial cell, raw responses.jsonl for all attempts, and manifest.json for pinned identities.", "",
                 "No mechanistic conclusion or unfamiliar-program prediction is established by behavior alone. "
                 "Final test data are sealed unless explicitly relabelled as discovery. Select one diagnostic error on development data before a focused intervention study."])
    (stage / "report.md").write_text("\n".join(text) + "\n")
    return {"report": str(stage / "report.md"), "summary": str(stage / "summary.json"), "n": len(rows)}
