#!/usr/bin/env python
"""Cache the final prompt token and fit probes with the original disjoint splits.

GPU job only. The original states, predictions and observed generations remain intact.
Each model is loaded once to extract the three demonstration sets, then released before
the full-batch probe fits. Outputs have their own directory and resume by validated stage.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import DATA_DIR, OUT_DIR, model_entry
from codecue.generator import read_jsonl
from codecue.probe_data import assert_disjoint_metadata, program_key
from codecue.probe_validation import validate_file
from codecue.prompt_comparison import prompt_boundary, validate_prompt_output
from codecue.prompts import build_prompt, demos, parse_regime

MODELS = ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it")
REGIMES = ("trace", "trace_s11", "trace_s13")
GROUPS = ("train_neutral", "neutral", "incongruent@v1")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inputs(model):
    lookup = {x.id: x for filename in ("train_neutral.jsonl", "test_sets.jsonl")
              for x in read_jsonl(DATA_DIR / "L5" / filename)}
    runs = {}
    for regime in REGIMES:
        source = OUT_DIR / "probes_disjoint" / model / "L5" / regime / "v1.json"
        validate_file(source)
        original = json.loads(source.read_text())
        original_root = Path(original["train_dir"]).parent
        groups = {}
        for group in GROUPS:
            path = original_root / group / "meta.json"
            meta = json.loads(path.read_text())
            instances = [lookup[row["id"]] for row in meta["instances"]]
            for x, row in zip(instances, meta["instances"]):
                if (program_key(x), x.names, x.values) != (row["program_key"], row["names"], row["values"]):
                    raise ValueError("source data differ from the original cached computation")
            groups[group] = (instances, meta, digest(path))
        assert_disjoint_metadata(groups["train_neutral"][1],
                                 {g: groups[g][1] for g in GROUPS[1:]})
        if len(groups["train_neutral"][0]) != 2000:
            raise ValueError("expected the original 2000-row training split")
        held_out = {program_key(x) for seed in (7, 11, 13) for x in demos(5, seed, "trace")}
        if any(program_key(x) in held_out for x in groups["train_neutral"][0]):
            raise ValueError("training computation overlaps a worked example")
        runs[regime] = (source, groups)
    return runs


def cache_prompt(tok, model, instances, reference, source_hash, regime, out_dir, batch_size):
    import torch
    from codecue.cache import trace_text

    base, seed = parse_regime(regime)
    ds = demos(5, seed, base)
    prompts = [build_prompt(x, regime, ds) for x in instances]
    sequences = []
    for prompt, x in zip(prompts, instances):
        ids, boundary = prompt_boundary(tok, prompt, trace_text(x))
        if not prompt.endswith("\nTrace:") or boundary != len(ids) - 1:
            raise ValueError("expected the final token of the full Trace: prompt")
        sequences.append(ids)
    fingerprint = hashlib.sha256(json.dumps({
        "version": 1, "reference_meta_sha256": source_hash, "regime": regime,
        "hf_id": model.config._name_or_path, "position": "prompt_end",
        "token_ids": sequences,
    }, sort_keys=True).encode()).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path, hidden_path = out_dir / "meta.json", out_dir / "hidden.npy"
    expected = (len(instances), 1, len(reference["layers"]), reference["hidden_dim"])
    if meta_path.exists() and hidden_path.exists():
        meta = json.loads(meta_path.read_text())
        if (meta.get("data_fingerprint") != fingerprint or not meta.get("prompt_boundary_checked")
                or np.load(hidden_path, mmap_mode="r").shape != expected):
            raise ValueError("existing prompt cache does not match these inputs")
        print("reuse", out_dir, flush=True)
        return
    temporary = out_dir / "hidden.tmp.npy"
    hidden = np.lib.format.open_memmap(temporary, mode="w+", dtype=np.float16, shape=expected)
    for start in range(0, len(sequences), batch_size):
        chunk = sequences[start:start + batch_size]
        width = max(map(len, chunk))
        ids = torch.full((len(chunk), width), tok.pad_token_id, dtype=torch.long, device=model.device)
        mask = torch.zeros_like(ids)
        for i, seq in enumerate(chunk):
            ids[i, :len(seq)] = torch.tensor(seq, device=model.device)
            mask[i, :len(seq)] = 1
        with torch.no_grad():
            states = model(input_ids=ids, attention_mask=mask, output_hidden_states=True).hidden_states
            for i, seq in enumerate(chunk):
                state = torch.stack([
                    states[layer][i, len(seq) - 1] for layer in reference["layers"]
                ]).to(torch.float16).cpu().numpy()
                if not np.isfinite(state).all():
                    raise ValueError("nonfinite prompt-end hidden state")
                hidden[start + i, 0] = state
        del states, ids, mask
        if start % (batch_size * 20) == 0:
            print(regime, out_dir.name, start + len(chunk), "/", len(sequences), flush=True)
    hidden.flush()
    del hidden
    temporary.replace(hidden_path)
    meta = {**reference, "pos_labels": ["prompt_end"], "data_fingerprint": fingerprint,
            "prompt_boundary_checked": True, "prompt_only": True,
            "reference_meta_sha256": source_hash,
            "model_revision": getattr(model.config, "_commit_hash", None)}
    meta.pop("pre_value_boundary_checked", None)
    temporary_meta = meta_path.with_suffix(".tmp")
    temporary_meta.write_text(json.dumps(meta, allow_nan=False) + "\n")
    temporary_meta.replace(meta_path)
    print("cached", out_dir, flush=True)


def run(model_key, batch_size):
    import torch
    from codecue.models import load_model
    from codecue.probes import train_and_eval

    runs = inputs(model_key)
    tok, model = load_model(model_entry(model_key)["hf_id"])
    root = OUT_DIR / "prompt_end_caches" / model_key / "L5"
    for regime, (_, groups) in runs.items():
        for group, (instances, reference, source_hash) in groups.items():
            cache_prompt(tok, model, instances, reference, source_hash, regime,
                         root / regime / group, batch_size)
    del model, tok
    gc.collect()
    torch.cuda.empty_cache()
    for regime, (source, _) in runs.items():
        output = OUT_DIR / "prompt_end_probes" / model_key / "L5" / regime / "v1.json"
        if output.exists() and output.with_suffix(".npz").exists():
            print("reuse fitted probes", output, flush=True)
        else:
            train_and_eval(root / regime / "train_neutral",
                           {g: root / regime / g for g in GROUPS[1:]}, "v1", output,
                           positions=["prompt_end"], save_control_predictions=True)
        data = json.loads(output.read_text())
        metadata = {g: json.loads((root / regime / g / "meta.json").read_text()) for g in GROUPS}
        validate_prompt_output(data, metadata["train_neutral"], {g: metadata[g] for g in GROUPS[1:]})
        receipt = {"model": model_key, "regime": regime, "position": "prompt_end",
                   "reference_probes_sha256": digest(source),
                   "probes_sha256": digest(output), "arrays_sha256": digest(output.with_suffix(".npz"))}
        output.with_suffix(".receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("completed prompt-end probes", model_key, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", choices=MODELS, required=True)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.batch_size < 1:
        ap.error("batch size must be positive")
    if args.dry_run:
        for key in args.models:
            runs = inputs(key)
            print(key, {regime: {g: len(v[0]) for g, v in groups.items()}
                        for regime, (_, groups) in runs.items()})
        return
    for key in args.models:
        run(key, args.batch_size)


if __name__ == "__main__":
    main()
