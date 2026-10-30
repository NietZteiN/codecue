"""Deterministic short-answer runs with raw outputs and set-valued error labels."""
from __future__ import annotations
import json
import re
import time
from pathlib import Path
from .datasets import read_jsonl, write_json
from .registry import guarded


def parse_answer(raw):
    return int(raw.strip()) if re.fullmatch(r"[+-]?\d+", raw.strip()) else None


def classify(record, prediction):
    if prediction is None:
        return {"status": "invalid", "compatible_labels": [], "compatible_alternatives": [], "ambiguous": False}
    if prediction == record["expected_answer"]:
        return {"status": "correct", "compatible_labels": [], "compatible_alternatives": [], "ambiguous": False}
    compatible = [i for i, a in enumerate(record["diagnostic_counterfactuals"]) if a["expected_answer"] == prediction]
    labels = sorted({record["diagnostic_counterfactuals"][i]["label"] for i in compatible})
    return {"status": "semantic_error", "compatible_labels": labels,
            "compatible_alternatives": compatible, "ambiguous": len(compatible) > 1,
            "interpretation": "counterfactual-consistent output, not an identified internal cause"}


def select(rows, config, split_key="splits"):
    selected = [r for r in rows if r["split"] in config[split_key]
                and r["control_kind"] in config["control_kinds"]]
    limit = config.get("per_cell_limit")
    if limit:
        # Choose BASES per family/load/update, keeping all six naming variants.
        groups = {}
        for r in selected:
            cell = (r["family"], r["load"], r["updates"])
            groups.setdefault(cell, set()).add(r["base_id"])
        bin_counts = config.get('magnitude_bin_counts')
        if bin_counts:
            if any(type(n) is not int or n < 1 for n in bin_counts.values()) or sum(bin_counts.values()) != limit:
                raise ValueError('positive magnitude-bin counts must sum to per_cell_limit')
            base_bins = {r['base_id']: str(r['answer_magnitude_bin']) for r in selected}
            keep = set()
            for ids in groups.values():
                for bin_id, count in bin_counts.items():
                    candidates = sorted(i for i in ids if base_bins[i] == str(bin_id))
                    if len(candidates) < count:
                        raise ValueError('insufficient bases in a requested magnitude bin')
                    keep.update(candidates[:count])
        else:
            keep = set().union(*(set(sorted(ids)[:limit]) for ids in groups.values()))
        selected = [r for r in selected if r["base_id"] in keep]
    if not selected:
        raise ValueError("no samples selected")
    if any(r["split"] == "test" for r in selected) and not config.get("discovery_test_acknowledged"):
        if config.get("registration"):
            from .heldout import registration
            registration(config, require_predictions=True)
        else:
            raise ValueError("test is sealed; register confirmatory analysis or explicitly relabel as discovery")
    return selected


@guarded
def run(config):
    import torch
    from codecue.models import generate_free
    from .model_adapter import layout, load, prompt_for
    from .registry import begin, finish
    out, manifest = begin(config, "behavior")
    started = time.monotonic()
    rows = select(read_jsonl(config["dataset"]), config)
    output = out / "responses.jsonl"
    previous = read_jsonl(output) if output.exists() else []
    if len({r["id"] for r in previous}) != len(previous) or not {r["id"] for r in previous} <= {r["id"] for r in rows}:
        raise ValueError("invalid resume sample identities")
    done = {r["id"] for r in previous}
    pending = [r for r in rows if r["id"] not in done]
    device_seconds = 0.0
    try:
        if not pending:
            finish(out, manifest, time.monotonic() - started, samples_completed=len(previous), samples_planned=len(rows))
            from .analysis import summarize
            summary = summarize(previous)
            summary['complete'] = True
            return summary
        tokenizer, model = load(config)
        for start in range(0, len(pending), config["batch_size"]):
            elapsed = time.monotonic() - started
            batch = pending[start:start + config["batch_size"]]
            prompts = [prompt_for(tokenizer, r, config['protocol']) for r in batch]
            layouts = [layout(tokenizer, r, p) for r, p in zip(batch, prompts)]
            # generate_free defaults to special tokens; chat templates already carry BOS.
            # Use tokenized templates with one BOS by the tokenizer configuration below.
            torch.cuda.synchronize() if config["device"] == "cuda" else None
            begin_time = time.monotonic()
            # Existing generator uses add_special_tokens=True; disable BOS on this tokenizer
            # for its lifetime so generation and audited offsets have identical input IDs.
            if hasattr(tokenizer, "add_bos_token"):
                tokenizer.add_bos_token = False
            if any(tokenizer(p)["input_ids"] != l["input_ids"] for p, l in zip(prompts, layouts)):
                raise ValueError("generation tokenization differs from audited spans")
            generated = generate_free(tokenizer, model, prompts, config["max_new_tokens"], config["batch_size"],
                                      stop_at_blank_line=config['protocol'] == 'short_answer_prefill_v2')
            torch.cuda.synchronize() if config["device"] == "cuda" else None
            batch_seconds = time.monotonic() - begin_time
            device_seconds += batch_seconds
            with output.open("a") as f:
                for row, prompt, raw, aligned in zip(batch, prompts, generated, layouts):
                    pred = parse_answer(raw)
                    result = {"id": row["id"], "base_id": row["base_id"], "template_id": row["template_id"],
                        "cluster_id": row["cluster_id"],
                        "family": row["family"], "load": row["load"], "updates": row["updates"], "split": row["split"],
                        "condition": row["condition"], "control_kind": row["control_kind"],
                        "lexical_realization": row["lexical_realization"], "expected_answer": row["expected_answer"],
                        "prediction": pred, "correct": pred == row["expected_answer"], "raw_response": raw,
                        "response_token_count": len(tokenizer(raw, add_special_tokens=False)["input_ids"]),
                        "prompt": prompt, "token_counts": aligned["token_counts"],
                        "input_token_ids": aligned["input_ids"], "checkpoint_positions": aligned["positions"],
                        "batch_seconds": batch_seconds, "classification": classify(row, pred),
                        "name_role_alternative_answer": row["name_role_alternative_answer"],
                        "diagnostically_distinct_available": any(d["diagnostically_distinct"] for d in row["diagnostic_counterfactuals"]),
                        "features": row["features"]}
                    f.write(json.dumps(result) + "\n")
            print(f"behavior {len(done) + min(start + len(batch), len(pending))}/{len(rows)}; {elapsed:.1f}s", flush=True)
        actual = read_jsonl(output)
        complete = len(actual) == len(rows)
        finish(out, manifest, time.monotonic() - started, "complete" if complete else "budget_limited",
               device_seconds=device_seconds, samples_completed=len(actual), samples_planned=len(rows),
               gpu_peak_bytes=torch.cuda.max_memory_allocated() if config["device"] == "cuda" else None,
               device_name=torch.cuda.get_device_name() if config["device"] == "cuda" else "cpu")
        from .analysis import summarize
        summary = summarize(actual)
        summary["complete"] = complete
        write_json(out / "summary.json", summary)
        return summary
    except Exception as exc:
        finish(out, manifest, time.monotonic() - started, "failed", error=f"{type(exc).__name__}: {exc}")
        raise
