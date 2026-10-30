"""Publish both completed schedule studies from pinned JSON metadata only.

No source/prepared/response JSONL, NPZ, model or activation is opened.  The
parameter inventory is checked as receipt metadata; the independent replay
receipt proves the prior numerical audit.  --self-test uses temporary synthetic
metadata and never reads the ongoing scientific runs.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import io
from itertools import product
import json
import math
import os
from pathlib import Path
import tempfile

ROLE = "discovery_diversity_readouts_v1"
PUBLICATION_ROLE = "discovery_diversity_decoding_publication_v1"
SUITE = Path("artifacts/binding/diversity_decoding/20261028_v1")
MODEL_KEYS = ("llama8b", "codellama34b")
MODELS = {
    "llama8b": ("Llama 3.1 8B", "meta-llama/Llama-3.1-8B-Instruct",
                "0e9e39f249a16976918f6564b8830bc894c89659", (8, 16, 24, 31)),
    "codellama34b": ("CodeLlama 34B", "codellama/CodeLlama-34b-Instruct-hf",
                     "d4c1c474abcacd32d2a6eda45f9811d38c83e93d", (12, 24, 36, 47)),
}
FAMILIES = ("current_definition", "current_version", "copy_parent")
LABELS = {"current_definition": "Current definitions", "current_version": "Current versions",
          "copy_parent": "Copy-parent definitions"}
METHODS = ("direct", "training_prior", "random_prefix_control")
SITES = (3, 7, 8)
SEEDS = (17, 29, 43)
DATASET_SHA = "d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1"
MAX_JSON = 192 * 1024**2
INPUTS = {}
LIMITATIONS = ['Adaptive discovery on60 canonical SSA graph families:45 TRAIN and15 DEV, each with96 dependent numeric/rotation/lexical/query relatives.', 'Graph novelty is relative to the named prior routing and schedule banks, not every project artifact or model pretraining.', 'All four final current-version classes occur in every slot, but class frequencies are unequal; domain coverage does not guarantee decoder ability.', 'The three-TRAIN-family support diagnostic is descriptive, not a behavioral reliability qualification or rescue of historical failed gates.', 'All declared heads, classes, seeds and layers remain reported; no favorable subset is selected.', 'At initialization current definitions and version1 are constants; future copy-parent targets remain undefined.', 'Parent and current-definition heads predict statement indices. Oracle conversion to natural variable@version labels is a separate assisted postmetric.', 'Explicit current-version heads do not decode the full identity of every obsolete statement or establish natural causal state tracking.', 'Canonical-prefix sham labels change class marginals/task difficulty and need not form lawful joint graphs.', 'The character baseline sees the exact visible prefix; a hidden-minus-source advantage is decoder-specific accessibility, not information absent from source.', 'Graph novelty, class support, sample size, definition age, positions and depth change together; fixed alpha has a different effective fit on the larger TRAIN set.', 'Fifteen DEV families support descriptive discovery, not population-wide causal replication. Three weighting seeds are dependent; no new intervals or bootstrap are added.', 'No generated-answer behavior is measured; sealed outcomes, failed computation gates, optional training and unfamiliar-program decisions remain unchanged.']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_bytes(value):
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    require(len(data) <= MAX_JSON, "Publication JSON exceeds192MiB")
    return data


def workspace():
    for parent in Path(__file__).resolve().parents:
        frozen = parent / "frozen_manifest.json"
        if frozen.is_file():
            require(frozen.stat().st_size <= MAX_JSON, "Bounded frozen manifest required")
            candidate = Path(json.loads(frozen.read_text())["workspace_root"]).resolve()
            if (candidate / SUITE).is_dir():
                return candidate
        if (parent / "src/codecue/binding").is_dir() and (parent / SUITE).is_dir():
            return parent
    raise ValueError("Cannot resolve schedule publication workspace")


def resolve(root, value):
    path = Path(value)
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    require(path == root or root in path.parents, "Publication paths must stay in the workspace")
    return path


def checksum(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def pin(root, path, data):
    path = resolve(root, path)
    result = dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    require(INPUTS.setdefault(result["path"], result) == result, "Input changed during publication")
    return result


def read_json(root, path, expected=None, limit=8*1024**2):
    path = resolve(root, path)
    require(path.suffix == ".json" and path.is_file() and path.stat().st_size <= limit,
            "Only bounded JSON metadata may be opened: " + str(path))
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "JSON metadata grew beyond bound")
    entry = pin(root, path, data)
    if isinstance(expected, str):
        require(entry["sha256"] == expected, "Metadata SHA256 differs")
    elif expected is not None:
        require(entry["sha256"] == expected["sha256"] and ("bytes" not in expected or entry["bytes"] == expected["bytes"])
                and resolve(root, expected["path"]) == path, "Pinned metadata differs")
    result = json.loads(data)
    require(isinstance(result, dict), "Metadata JSON object required")
    return result


def source_profile(root, source, relative):
    folder = resolve(root, source["snapshot"])
    frozen = read_json(root, folder / "frozen_manifest.json", source["frozen_manifest_sha256"])
    require(frozen["snapshot_id"] == source["snapshot_id"]
            and frozen["code"]["source_sha256"] == source["source_sha256"], "Frozen source identity differs")
    require(str(relative) in frozen["config_files"], "Required configuration was not frozen")
    return read_json(root, folder / relative, frozen["config_files"][str(relative)])


def _point(value):
    return value is None or (isinstance(value, (float, int)) and not isinstance(value, bool)
                             and math.isfinite(value) and 0 <= value <= 1)


def validate_cell(cell):
    require(type(cell.get("n")) is int and 0 <= cell["n"] <= 1440 and cell.get("heads") == 4,
            "Whole-head denominators differ")
    require(_point(cell.get("accuracy")) and _point(cell.get("group_macro_accuracy")), "Invalid accuracy")
    groups = cell.get("per_group")
    require(isinstance(groups, dict), "Per-graph outcomes required")
    if not cell["n"]:
        require(not groups and cell["accuracy"] is None and cell["group_macro_accuracy"] is None,
                "Undefined whole-head tasks must retain null points")
        return
    require(cell["n"] == 1440 and len(groups) == 15, "All 15 DEV graph families required")
    require(all(type(v.get("n")) is int and v["n"] > 0 and _point(v.get("accuracy"))
                and v["accuracy"] is not None for v in groups.values()), "Invalid per-graph cells")
    require(sum(v["n"] for v in groups.values()) == cell["n"] and all(v["n"] == 96 for v in groups.values()), "Fifteen equal96-row DEV families required")
    require(math.isclose(cell["accuracy"], cell["group_macro_accuracy"], abs_tol=1e-12), "Whole-task row and equal-family means must agree")
    require(math.isclose(cell["accuracy"], sum(v["n"] * v["accuracy"] for v in groups.values()) / cell["n"], abs_tol=1e-12)
            and math.isclose(cell["group_macro_accuracy"], sum(v["accuracy"] for v in groups.values()) / 15, abs_tol=1e-12),
            "Row/group aggregation differs from saved graph cells")


def _mean(values):
    require(len(values) == 3, "All three declared weighting seeds required")
    return sum(values) / 3 if all(v is not None for v in values) else None


def _same_point(left, right):
    return left is None and right is None or (left is not None and right is not None
        and math.isclose(left, right, rel_tol=0, abs_tol=1e-14))


def validate_version_support(result):
    """Verify genuine final-site domain coverage without qualifying performance."""
    for site in ("7", "8"):
        support = result["training_support"][site]
        require(support.get("eligibility_split") == "train" and support.get("structural_groups") == 45
                and support.get("minimum_class_groups") == 3
                and support.get("absent_domain_choices_retained") is True
                and support.get("development_labels_used_for_eligibility") is False,
                "Fixed TRAIN-only support diagnostic differs")
        heads = {head["head"]: head for head in support["categorical_heads"] if head["family"] == "current_version"}
        require(set(heads) == {f"current_version/{slot}" for slot in range(4)}, "Four current-version support heads required")
        for head in heads.values():
            require(head["candidates"] == [1, 2, 3, 4] and head["evaluated_choices_removed"] is False,
                    "All final version candidates must remain")
            classes = head["classes"]
            require([cell["candidate"] for cell in classes] == [1, 2, 3, 4]
                    and sum(cell["train_rows"] for cell in classes) == 4320
                    and sum(cell["development_rows"] for cell in classes) == 1440
                    and all(cell["train_rows"] > 0 and cell["train_groups"] >= 3
                            and cell["development_rows"] > 0 and cell["development_groups"] > 0 for cell in classes),
                    "Version1..4 support is missing from a final target slot")


def capture_accounting(root, config, expected_source):
    """Read completed capture metadata only; never inspect a feature chunk."""
    folder = resolve(root, config["run_dir"])
    receipt = read_json(root, folder / "completion_manifest_v1.json")
    require(receipt.get("status") == "complete_exploratory"
            and receipt.get("evaluation_role") == "discovery_diversity_capture_v1"
            and receipt.get("config_hash") == digest(config) and receipt.get("source") == expected_source
            and receipt.get("dataset_sha256") == DATASET_SHA and receipt.get("cases") == 5760,
            "Completed matching diversity capture receipt required")
    expected_shape = [5760, 3, 4, config["hidden_size"]]
    require(receipt.get("feature_shape") == expected_shape, "Capture feature geometry differs")
    names = {"registration.json", "preflight.json", "prepared_cases.jsonl", "manifest.json", "summary.json", "audit.json"}
    require(set(receipt.get("metadata", {})) == names, "Exact capture metadata inventory required")
    for name in names:
        require(resolve(root, receipt["metadata"][name]["path"]) == folder / name, "Capture metadata path differs")
    summary = read_json(root, folder / "summary.json", receipt["metadata"]["summary.json"])
    audit = read_json(root, folder / "audit.json", receipt["metadata"]["audit.json"])
    preflight = read_json(root, folder / "preflight.json", receipt["metadata"]["preflight.json"])
    boundary = "native" if config["hidden_size"] == 4096 else "codellama_official_boundary_v1"
    require(config["evaluation_role"] == "discovery_diversity_capture_v1"
            and preflight.get("status") == "passed" and preflight.get("cases") == 5760
            and preflight.get("config_hash") == digest(config) and preflight.get("source") == expected_source
            and preflight.get("new_model_queries") == 0
            and preflight["recipe"]["tokenization_mode"] == boundary
            and preflight["recipe"]["dtype"] == "bfloat16"
            and preflight["recipe"]["batch_size"] == config["batch_size"], "Prepared native/BF16/batch profile differs")
    require(preflight["source_review"]["source_rows"] == 5760
            and preflight["source_review"]["components"] == {"train": 45, "development": 15}
            and preflight["source_review"]["split_rows"] == {"train": 4320, "development": 1440}
            and preflight["source_review"]["dataset_manifest_sha256"] == config["dataset_manifest_sha256"],
            "Capture source cohort/manifest identity differs")
    require(summary.get("complete") is True and summary.get("cases") == 5760
            and summary.get("feature_shape") == expected_shape and summary.get("source") == expected_source
            and audit.get("status") == "passed" and audit.get("finite_float32_features") is True
            and audit.get("source_model_prefill_cases") == 5760 and audit.get("new_model_queries") == 0,
            "Completed finite capture and audit required")
    for value in (receipt, summary, audit):
        require(value.get("generated_responses") == value.get("generation_calls") == 0
                and value.get("generated_holdouts_opened") is False, "Capture unexpectedly generated responses")
    attempts = summary["collection_attempts"]
    attempted = sum(a["prefill_cases_attempted"] for a in attempts)
    calls = sum(a["prefill_batch_calls"] for a in attempts)
    require(attempts and attempts[-1]["status"] == "complete" and attempted >= 5760
            and all(0 <= a["prefill_cases_returned"] <= a["prefill_cases_attempted"] for a in attempts)
            and summary["model_prefill_cases"] == receipt["model_prefill_cases"] == 5760
            and summary["new_model_queries"] == receipt["new_model_queries"] == attempted
            and summary["prefill_batch_calls"] == receipt["prefill_batch_calls"] == calls,
            "Distinct and retry capture accounting differ")
    return dict(distinct_cases=5760, attempted_cases=attempted, retry_case_attempts=attempted - 5760,
                batch_calls=calls, generated_responses=0, generation_calls=0,
                capture_receipt=INPUTS[str((folder / "completion_manifest_v1.json").relative_to(root))],
                scope="Actual durable source-case prefill attempts; no generated-answer behavior.")


def extract_model(result, summary, model, config):
    expected = set(product(SITES, [("hidden", layer) for layer in MODELS[model][3]] + [("surface", -1)], SEEDS))
    observed = set(); rows = []
    require(result.get("model") == MODELS[model][1] and result.get("cases") == 5760
            and result.get("training_rows") == 4320 and result.get("development_rows") == 1440
            and result.get("training_groups") == 45 and result.get("development_groups") == 15,
            "Complete schedule cohort required")
    require(result.get("primary") == dict(layer=24, site=7,
        tasks=list(FAMILIES), scope="all fixed heads and classes retained; descriptive only"),
        "Prospectively nominated primary endpoint differs")
    for fit in result["fits"]:
        key = (fit["site"], (fit["backend"], fit["layer"]), fit["seed"])
        require(key in expected and key not in observed, "Duplicate or undeclared fit cell")
        observed.add(key)
        require(fit.get("name") == f"{fit['backend']}_layer{fit['layer']}_site{fit['site']}_seed{fit['seed']}"
                and fit.get("exact_parameter_score_replay") is True and fit.get("factorizations") == 1,
                "Fit identity or replay metadata differs")
        require(set(fit["metrics"]) == set(METHODS), "All direct/prior/sham methods required")
        for method in METHODS:
            metrics = fit["metrics"][method]
            require(set(metrics["whole_categorical_families"]) == set(FAMILIES), "All three fixed tasks required")
            for family in FAMILIES:
                cell = metrics["whole_categorical_families"][family]
                validate_cell(cell)
                require(cell["n"] == (0 if fit["site"] == 3 and family == "copy_parent" else 1440),
                        "Future copy-parent tasks must stay undefined at site3")
                heads = {name: value for name, value in metrics["categorical_heads"].items()
                         if value["family"] == family}
                require(set(heads) == {f"{family}/{slot}" for slot in range(4)},
                        "All four fixed heads and their class counts required")
                for head in heads.values():
                    candidates = {str(v) for v in (range(1, 5) if family == "current_version" else range(8))}
                    require(set(head["classes"]) == candidates,
                            "Every declared category choice, including absent choices, must remain")
                    require(head["n"] == cell["n"] and sum(c["n"] for c in head["classes"].values()) == cell["n"],
                            "All class denominators must be retained")
                    if family == "current_version" and fit["site"] in (7, 8) and method in ("direct", "training_prior"):
                        require(all(c["n"] > 0 for c in head["classes"].values()),
                                "Every final DEV version class must remain present in every slot")
                    require(all(type(c["n"]) is int and c["n"] >= 0 and _point(c["accuracy"])
                                and (c["accuracy"] is None) == (c["n"] == 0) for c in head["classes"].values()),
                            "Invalid or omitted categorical class cell")
                    require(type(head.get("missing_predictions")) is int and 0 <= head["missing_predictions"] <= head["n"],
                            "Missing-prediction counts required")
                    validate_cell(dict(head, heads=4))
                    require(not head["n"] or math.isclose(head["accuracy"],
                        sum(c["n"] * c["accuracy"] for c in head["classes"].values() if c["n"]) / head["n"], abs_tol=1e-12),
                        "Head accuracy differs from all class counts")
                rows.append(dict(model=model, checkpoint=MODELS[model][1], backend=fit["backend"],
                    layer=fit["layer"], site=fit["site"], seed=fit["seed"], method=method, family=family,
                    heads=cell["heads"], n=cell["n"], accuracy=cell["accuracy"],
                    group_macro_accuracy=cell["group_macro_accuracy"], graph_groups=len(cell["per_group"]),
                    per_group=cell["per_group"], categorical_heads=heads))
    require(observed == expected and len(rows) == 405, "Complete45-bank/405-task grid required")
    primary = {}
    for backend in ("hidden", "surface"):
        primary[backend] = {}
        for method in METHODS:
            primary[backend][method] = {}
            for family in FAMILIES:
                selected = [r for r in rows if r["site"] == 7 and r["backend"] == backend
                            and (backend == "surface" or r["layer"] == 24)
                            and r["method"] == method and r["family"] == family]
                point = dict(accuracy=_mean([r["accuracy"] for r in selected]),
                             group_macro_accuracy=_mean([r["group_macro_accuracy"] for r in selected]),
                             weighting_seeds=list(SEEDS), rows_per_seed=1440, graph_groups_per_seed=15)
                require(_same_point(point["accuracy"], summary["primary"][backend][method][family])
                        and _same_point(point["group_macro_accuracy"], summary["primary_group_macro"][backend][method][family]),
                        "Saved primary summary differs from the complete three-seed grid")
                primary[backend][method][family] = point
    control = result.get("control_descriptive_metadata")
    require(isinstance(control, dict) and set(control) == {str(s) for s in SITES}, "Control marginal metadata required")
    changes = {}
    for site in SITES:
        require(set(control[str(site)]) == {str(seed) for seed in SEEDS}, "All nine control descriptions required")
        changes[str(site)] = {}
        for seed in SEEDS:
            item = control[str(site)][str(seed)]
            require(item.get("control_kind") == "canonical_visible_prefix_keyed_random_task_v1"
                    and item.get("control_seed") == seed and item.get("marginals_preserved") is False
                    and item.get("lawful_joint_ssa_graph") is False,
                    "Declared prefix-sham semantics differ")
            real, sham = item["real_marginals"], item["control_marginals"]
            require(set(real) == set(sham) == {"train", "development"}, "Both split marginal inventories required")
            for split in real:
                require(len(real[split]) == len(sham[split]) == 232, "All control target marginals required")
            changes[str(site)][str(seed)] = dict(description_sha256=digest(item),
                changed_column_marginals={split: sum(a != b for a, b in zip(real[split], sham[split])) for split in real},
                marginals_preserved=False, lawful_joint_ssa_graph=False)
    validate_version_support(result)
    return dict(model=model, label=MODELS[model][0], checkpoint=MODELS[model][1],
        model_revision=MODELS[model][2], layers=list(MODELS[model][3]), primary_layer=config["primary_layer"],
        primary_site=7, cases=5760, training_rows=4320, development_rows=1440,
        training_graph_groups=45, development_graph_groups=15, primary=primary, cells=rows,
        control_marginal_differences=changes, training_support=result["training_support"])


def load_model(root, model):
    base = root / SUITE / model / "readouts"
    receipt = read_json(root, base / "completion_manifest_v1.json")
    require(receipt.get("status") == "complete_exploratory" and receipt.get("schema_version") == 1
            and receipt.get("evaluation_role") == ROLE and receipt.get("fit_banks") == 45
            and receipt.get("factorizations") == 45 and receipt.get("parameter_replay_rows") == 259200
            and receipt.get("new_model_queries") == 0 and receipt.get("generated_holdouts_opened") is False,
            "Completed matching45-bank readout receipt required")
    relative = Path("configs/binding/diversity_decoding_20261028_v1") / (model + "_readouts.json")
    config = source_profile(root, receipt["fit_source"], relative)
    require(config["evaluation_role"] == ROLE and config["primary_layer"] == 24
            and digest(config) == receipt["config_hash"] and resolve(root, config["run_dir"]) == base,
            "Prospectively frozen readout configuration differs")
    cap_relative = Path(config["capture_config"])
    capture = source_profile(root, receipt["capture_source"], cap_relative)
    capture_path = resolve(root, receipt["capture_source"]["snapshot"]) / cap_relative
    require(INPUTS[str(capture_path.relative_to(root))]["sha256"] == config["capture_config_sha256"]
            and capture["evaluation_role"] == "discovery_diversity_capture_v1"
            and capture["model"] == MODELS[model][1]
            and capture["model_revision"] == capture["tokenizer_revision"] == MODELS[model][2]
            and capture["hidden_size"] == (4096 if model == "llama8b" else 8192)
            and capture["layers"] == list(MODELS[model][3]) and capture["dataset_sha256"] == DATASET_SHA,
            "Pinned checkpoint/capture configuration differs")
    expected = {f"{backend}_layer{layer}_site{site}_seed{seed}": base / f"{backend}_layer{layer}_site{site}_seed{seed}.npz"
                for site, (backend, layer), seed in product(SITES,
                    [("hidden", layer) for layer in MODELS[model][3]] + [("surface", -1)], SEEDS)}
    expected.update(registration=base / "registration.json", results=base / "results_v1.json",
                    summary=base / "summary.json", audit=base / "audit.json", report=resolve(root, config["report"]))
    inventory = receipt.get("artifacts", {})
    require(set(inventory) == set(expected) and len(inventory) == 50, "Exact50-artifact inventory required")
    for name, path in expected.items():
        item = inventory[name]
        require(resolve(root, item["path"]) == path and checksum(item.get("sha256"))
                and type(item.get("bytes")) is int and 0 < item["bytes"] <= 512 * 1024**2,
                "Exact bounded parameter/metadata inventory required")
    metadata = {name: read_json(root, expected[name], inventory[name], limit=MAX_JSON if name == "results" else 8*1024**2)
                for name in ("registration", "results", "summary", "audit")}
    report_path = expected["report"]
    require(report_path.is_file() and report_path.suffix == ".md" and report_path.stat().st_size <= 8*1024**2,
            "Bounded completed report metadata required")
    report_entry = pin(root, report_path, report_path.read_bytes())
    require(report_entry["sha256"] == inventory["report"]["sha256"]
            and report_entry["bytes"] == inventory["report"]["bytes"], "Completed report SHA256 differs")
    replay = read_json(root, base / "parameter_replay_review_v1.json")
    require(replay.get("status") == "passed" and replay.get("evaluation_role") == ROLE
            and replay.get("config_hash") == receipt["config_hash"]
            and replay.get("fit_source") == receipt["fit_source"] and replay.get("capture_source") == receipt["capture_source"]
            and replay.get("fit_banks") == replay.get("factorizations") == 45
            and replay.get("parameter_replay_rows") == 259200 and replay.get("source_artifacts") == inventory
            and all(replay.get(k) is True for k in ("exact_saved_parameter_score_replays",
                "all_real_and_control_scores_replayed", "all_scientific_metrics_recomputed",
                "train_support_and_control_marginals_recomputed"))
            and replay.get("new_fits") == replay.get("new_model_queries") == 0
            and replay.get("generated_holdouts_opened") is False, "Independent complete numerical/metric replay audit required")
    registration, result, summary, audit = [metadata[name] for name in ("registration", "results", "summary", "audit")]
    require(registration.get("config") == config and registration.get("fit_source") == receipt["fit_source"]
            and registration.get("capture_source") == receipt["capture_source"]
            and registration.get("fixed_recipe") == result.get("protocol"), "Original registration differs")
    for name, value in metadata.items():
        require(value.get("evaluation_role") == ROLE and value.get("config_hash") == receipt["config_hash"]
                and value.get("new_model_queries") == 0 and value.get("generated_holdouts_opened") is False,
                "Discovery role/identity differs: " + name)
    require(result.get("status") == summary.get("status") == "complete_exploratory"
            and audit.get("status") == "passed" and audit.get("exact_parameter_score_replays") is True
            and result.get("fit_source") == receipt["fit_source"] and result.get("capture_source") == receipt["capture_source"]
            and result.get("dataset_sha256") == DATASET_SHA
            and result.get("fit_banks") == summary.get("fit_banks") == audit.get("fit_banks") == 45
            and result.get("factorizations") == summary.get("factorizations") == audit.get("factorizations") == 45
            and result.get("parameter_replay_rows") == summary.get("parameter_replay_rows") == audit.get("parameter_replay_rows") == 259200,
            "Completed result/summary/audit accounting differs")
    require(result["protocol"].get("sites") == list(SITES) and result["protocol"].get("seeds") == list(SEEDS)
            and result["protocol"].get("alpha") == 100.
            and result["protocol"].get("primary_train_class_group_minimum") == 3,
            "Fixed source/site/seed/readout protocol differs")
    require(registration["dataset_sha256"] == DATASET_SHA
            and {fit["name"]: resolve(root, fit["artifact"]) for fit in result["fits"]}
            == {name: path for name, path in expected.items() if path.suffix == ".npz"},
            "Scientific parameter inventory differs from completion receipt")
    accounting = capture_accounting(root, capture, receipt["capture_source"])
    value = extract_model(result, summary, model, config)
    value["capture_accounting"] = accounting
    value.update(config_hash=receipt["config_hash"], fit_source=receipt["fit_source"],
                 capture_source=receipt["capture_source"], dataset_sha256=DATASET_SHA,
                 declared_plan_sha256=config["declared_plan_sha256"],
                 capture_config_sha256=config["capture_config_sha256"],
                 parameter_inventory={name: item for name, item in inventory.items() if name.endswith(tuple(str(s) for s in SEEDS))},
                 audited_result=inventory["results"], audited_summary=inventory["summary"],
                 completion_receipt=INPUTS[str((base / "completion_manifest_v1.json").relative_to(root))],
                 numerical_replay_receipt=INPUTS[str((base / "parameter_replay_review_v1.json").relative_to(root))])
    require(len(value["parameter_inventory"]) == 45, "All45 pinned parameter banks required")
    return value


def table_bytes(models):
    fields = ["model", "checkpoint", "backend", "layer", "site", "seed", "method", "family",
              "heads", "n", "accuracy", "group_macro_accuracy", "graph_groups", "per_group_json", "categorical_heads_json"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for model in MODEL_KEYS:
        for row in models[model]["cells"]:
            value = {k: row[k] for k in fields if k in row}
            for key in ("per_group", "categorical_heads"):
                value[key + "_json"] = json.dumps(row[key], sort_keys=True, separators=(",", ":"), allow_nan=False)
            writer.writerow(value)
    return stream.getvalue().encode()


def figure_bytes(models):
    import matplotlib
    matplotlib.use("Agg", force=True)
    matplotlib.rcParams.update({"svg.hashsalt": "diversity_decoding_v1", "font.family": "DejaVu Sans", "font.size": 10})
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True)
    for i, model in enumerate(MODEL_KEYS):
        for j, family in enumerate(FAMILIES):
            ax = axes[i, j]; item = models[model]; layers = item["layers"]
            for method, label, color, marker in (("direct", "Hidden / direct", "#2463ad", "o"),
                    ("random_prefix_control", "Hidden / prefix sham", "#c45426", "s")):
                points = []
                for layer in layers:
                    cells = [r for r in item["cells"] if r["site"] == 7 and r["backend"] == "hidden"
                             and r["layer"] == layer and r["method"] == method and r["family"] == family]
                    point = _mean([r["group_macro_accuracy"] for r in cells])
                    points.append(float("nan") if point is None else 100 * point)
                ax.plot(layers, points, label=label, color=color, marker=marker, linewidth=1.8, markersize=5)
            for backend, method, label, color, style in (("surface", "direct", "Surface / direct", "#555555", "--"),
                    ("hidden", "training_prior", "TRAIN prior", "#333333", ":")):
                point = item["primary"][backend][method][family]["group_macro_accuracy"]
                if point is not None:
                    ax.axhline(100 * point, label=label, color=color, linestyle=style, linewidth=1.5)
            ax.axvline(24, color="#777777", alpha=.22, linewidth=1)
            ax.set_xticks(layers); ax.set_ylim(0, 103); ax.set_yticks([0, 20, 40, 60, 80, 100])
            ax.grid(axis="y", alpha=.2); ax.spines[["top", "right"]].set_visible(False)
            ax.set_title(item["label"] + " · " + LABELS[family], fontsize=10)
            ax.set_xlabel("Hidden layer (primary 24)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, .045))
    fig.supylabel("DEV equal-family whole-task correct (%)", x=.015, fontsize=11)
    fig.suptitle("Slot-complete overwrite decoding: all fixed layers at site 7", fontsize=14, y=.985)
    fig.text(.53, .012, "Means over three dependent weighting seeds and 15 DEV graph families; no confidence intervals. All sites remain in the CSV.", ha="center", fontsize=9)
    fig.subplots_adjust(left=.085, right=.99, bottom=.18, top=.90, wspace=.23, hspace=.38)
    png, svg = io.BytesIO(), io.BytesIO()
    fig.savefig(png, format="png", dpi=170, metadata={"Software": "CodeCue deterministic schedule publisher"})
    fig.savefig(svg, format="svg", metadata={"Date": None, "Creator": "CodeCue deterministic schedule publisher"})
    plt.close(fig)
    return png.getvalue(), svg.getvalue(), matplotlib.__version__


def report_bytes(models):
    distinct = sum(value["capture_accounting"]["distinct_cases"] for value in models.values())
    attempted = sum(value["capture_accounting"]["attempted_cases"] for value in models.values())
    lines = ["# Slot-complete overwrite relationship decoding", "",
        "Both checkpoints completed the fixed discovery grid and passed actual saved-parameter, scientific-metric and control-marginal replay audits. "
        "These are descriptive decoding results, with no behavioral reliability qualification or causal mechanism claim.", "",
        "Each model uses 5,760 source cases: 4,320 TRAIN rows in 45 canonical SSA graph families and 1,440 DEV rows in 15 families. "
        "Each family contains 96 related rotation/numeric/lexical/query cases. The three overwrite-count profiles contribute twenty families each. "
        "Novelty is relative to the two named prior graph banks, and all relatives keep their declared split.", "",
        "All four final version classes occur in every variable slot in both splits. This improves source coverage; the table below measures whether the fixed decoders recover them. "
        "It does not presume that repaired source support supplies a general version-tracking ability.", "",
        "Layer 24 at the final-assignment site 7 was nominated before capture for both checkpoints. Every table point averages all three fixed weighting seeds 17/29/43. "
        "No favorable layer, class or seed subset replaces the primary."]
    for field, title in (("accuracy", "Row-weighted DEV whole-task accuracy"), ("group_macro_accuracy", "Equal-family DEV whole-task accuracy")):
        lines += ["", title + ":", "", "| Model | Backend | Method | Current definitions | Current versions | Copy parents |", "|---|---|---|---:|---:|---:|"]
        for model, backend, method in product(MODEL_KEYS, ("hidden", "surface"), METHODS):
            points = [models[model]["primary"][backend][method][family][field] for family in FAMILIES]
            values = ["undefined" if value is None else f"{100*value:.3f}%" for value in points]
            lines.append("| " + " | ".join([models[model]["label"], backend, method, *values]) + " |")
    lines += ["", "![All fixed layers at site7](figures/diversity_decoding_v1.svg)", "",
        "The six panels retain all four hidden layers, direct and prefix-sham curves, the exact-prefix character baseline and the TRAIN prior. "
        "Points are means over the three dependent weighting seeds; no confidence interval or bootstrap is added. "
        "The nominated layer is marked at 24. [form_cells_v1.csv](../../artifacts/binding/diversity_decoding/20261028_v1/form_cells_v1.csv) "
        "retains all 810 model/site/layer/seed/backend/method/task cells, every categorical head/class and per-family count, including null future-copy tasks at site3.", "",
        "Every DEV family contributes 96 rows to a defined whole task. Row and equal-family whole-task accuracies therefore agree apart from numerical rounding; both are preserved and checked. "
        "Class-conditioned accuracies need not have equal class or family frequencies. All declared categories remain visible, including absent/impossible candidates and rare TRAIN classes. "
        "The minimum three-TRAIN-family support diagnostic is descriptive and does not rescue an earlier behavioral gate.", "",
        "At initialization current definitions and version1 are constants; copy parents are still undefined. At final sites the four current-version classes are present in every slot. "
        "The source character model can use explicit source syntax and overwrite counts; include it when assessing a hidden decoder. "
        "Current-definition and parent heads predict statement indices. Converting those predictions to full natural variable@version identities using oracle maps would be an assisted postmetric. "
        "These heads do not decode every obsolete statement's full identity.", "",
        "The canonical-prefix sham task ties identical visible prefixes but changes real/control marginals and need not form a lawful SSA graph. "
        "A direct-minus-sham or hidden-minus-character difference concerns decoder-specific accessibility and does not identify natural causal use.", "",
        "The dataset, graph families, class coverage and TRAIN sample size changed together. Fixed alpha 100 also has a different effective fit on the larger TRAIN set. "
        "Differences from the earlier study cannot isolate novelty or version coverage. Definition age, source position and dependency depth remain coupled. "
        "Fifteen DEV families and related source variants support a scoped discovery result, not a causal replication or untouched unfamiliar-program prediction.", "",
        f"Capture accounting is {distinct:,} distinct prefills and {attempted:,} actual attempted prefills, including {attempted-distinct:,} retry case attempts. "
        "No answers were generated. The 90 joint real/control banks comprise 90 factorizations and 518,400 exact parameter-replay case rows. "
        "All attempts are retained in the completed capture metadata; probe fitting is separate from language-model training.", "",
        "This publisher requires both completed scientific receipts and actual parameter-replay proofs. It reads only pinned JSON metadata and frozen profiles; "
        "parameter/capture inventories are checked without opening arrays, source records or responses. It performs no fit, parameter application, new model query or bootstrap. "
        "[comparison_v1.json](../../artifacts/binding/diversity_decoding/20261028_v1/comparison_v1.json) records the data and pins; "
        "[publication_review_v1.json](../../artifacts/binding/diversity_decoding/20261028_v1/publication_review_v1.json) pins every new output.", "",
        *["- "+text for text in LIMITATIONS], ""]
    return "\n".join(lines).encode()


def publish(path, data):
    path = Path(path)
    require(not path.is_symlink(), "Output symlinks are forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.is_file() and path.read_bytes() == data, "Immutable publication differs: " + str(path))
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name + ".", suffix=".pending", delete=False) as stream:
            temporary = Path(stream.name); stream.write(data); stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            require(not path.is_symlink() and path.read_bytes() == data, "Concurrent publication differs")
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def publication(root):
    root = Path(root).resolve(); INPUTS.clear()
    for model in MODEL_KEYS:
        base = root / SUITE / model / "readouts"
        require((base / "completion_manifest_v1.json").is_file()
                and (base / "parameter_replay_review_v1.json").is_file(),
                "Both completed model receipts and independent replay audits are required")
    models = {model: load_model(root, model) for model in MODEL_KEYS}
    pointer = read_json(root, root / SUITE / "execution_source_v1.json")
    for model in MODEL_KEYS:
        for source in (models[model]["fit_source"], models[model]["capture_source"]):
            require(pointer["snapshot_id"] == source["snapshot_id"]
                    and pointer["code"] == source["source_sha256"], "Registered source pointer differs from actual completed study")
    require(models["llama8b"]["declared_plan_sha256"] == models["codellama34b"]["declared_plan_sha256"],
            "Both models must share the frozen prospective plan")
    script = Path(__file__).resolve()
    script_pin = dict(path=str(SUITE / script.name), sha256=hashlib.sha256(script.read_bytes()).hexdigest(), bytes=script.stat().st_size)
    table = table_bytes(models)
    png, svg, version = figure_bytes(models)
    png2, svg2, _ = figure_bytes(models)
    require((png, svg) == (png2, svg2), "Repeated figure rendering is not byte-identical")
    comparison = dict(status="complete_metadata_publication", evaluation_role=PUBLICATION_ROLE,
        model_count=2, models=models, table_rows=810, primary_layer=24, primary_site=7,
        source_cases_per_model=5760, total_parameter_banks=90, parameter_banks_opened=0,
        parameter_replay_rows=518400, total_factorizations=90,
        distinct_capture_prefills=sum(v["capture_accounting"]["distinct_cases"] for v in models.values()),
        attempted_capture_prefills=sum(v["capture_accounting"]["attempted_cases"] for v in models.values()),
        inputs=sorted(INPUTS.values(), key=lambda item: item["path"]), publisher_script=script_pin,
        new_model_queries=0, new_fits=0, new_bootstraps=0, raw_activation_arrays_opened=False,
        source_or_response_records_opened=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    base = root / SUITE
    outputs = {base / "comparison_v1.json": json_bytes(comparison), base / "form_cells_v1.csv": table,
        root / "reports/binding/diversity_decoding_findings_v1.md": report_bytes(models),
        root / "reports/binding/figures/diversity_decoding_v1.png": png,
        root / "reports/binding/figures/diversity_decoding_v1.svg": svg}
    review = dict(status="passed", evaluation_role=PUBLICATION_ROLE, publisher_script=script_pin,
        input_pins=sorted(INPUTS.values(), key=lambda item: item["path"]),
        output_pins=[dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
                     for path, data in outputs.items()], plotting_version=version,
        checks=dict(both_completed_receipts_and_replay_audits_required=True,
            all90_parameter_inventory_pins_verified_as_metadata=True, no_parameter_banks_opened=True,
            all810_task_cells_and_class_counts_preserved=True, null_future_tasks_retained=True,
            primary_layer24_site7_three_seed_means_verified=True, row_and_graph_macro_tables_preserved=True, whole_task_row_graph_means_equal=True,
            all_final_slot_version_classes_present=True, capture_attempts_and_zero_generation_verified=True,
            control_marginal_metadata_pinned=True, repeated_figure_render_byte_identical=True),
        reproduction="Every invocation regenerates and byte-checks all existing outputs.",
        new_model_queries=0, new_fits=0, new_bootstraps=0, generated_holdouts_opened=False)
    review_payload = json_bytes(review)
    require(len(review_payload) <= 8*1024**2, "Compact publication review exceeds8MiB")
    outputs[base / "publication_review_v1.json"] = review_payload
    existed = all(path.is_file() for path in outputs)
    for path, data in outputs.items():
        require(not path.is_symlink() and (not path.exists() or path.read_bytes() == data),
                "Immutable publication differs before any write: " + str(path))
    for path, data in outputs.items():
        publish(path, data)
    return dict(status="byte_identical_reproduction" if existed else "published", models=2, task_cells=810,
                publication_review=str(SUITE / "publication_review_v1.json"))


def synthetic_result(model):
    """Complete metadata fixture with real cohort dimensions, no arrays."""
    groups = {f"graph{i}": dict(n=96, accuracy=.5) for i in range(15)}
    whole = dict(heads=4,n=1440,accuracy=.5,group_macro_accuracy=.5,per_group=groups)
    zero = dict(heads=4,n=0,accuracy=None,group_macro_accuracy=None,per_group={})
    result = dict(status="complete_exploratory",evaluation_role=ROLE,model=MODELS[model][1],cases=5760,
        training_rows=4320,development_rows=1440,training_groups=45,development_groups=15,
        primary=dict(layer=24,site=7,tasks=list(FAMILIES),scope="all fixed heads and classes retained; descriptive only"),
        protocol=dict(sites=list(SITES),seeds=list(SEEDS),alpha=100.,primary_train_class_group_minimum=3),
        training_support={},control_descriptive_metadata={},fits=[],fit_banks=45,factorizations=45,
        parameter_replay_rows=259200,dataset_sha256=DATASET_SHA,new_model_queries=0,generated_holdouts_opened=False)
    support = dict(eligibility_split="train",structural_groups=45,minimum_class_groups=3,
        absent_domain_choices_retained=True,development_labels_used_for_eligibility=False,categorical_heads=[])
    for slot in range(4):
        classes = [dict(candidate=c,train_rows=n,train_groups=g,development_rows=d,development_groups=h)
            for c,n,g,d,h in zip((1,2,3,4),(1800,1080,1080,360),(45,30,30,15),(600,360,360,120),(15,10,10,5))]
        support["categorical_heads"].append(dict(head=f"current_version/{slot}",family="current_version",
            candidates=[1,2,3,4],evaluated_choices_removed=False,classes=classes))
    for site in SITES:
        result["training_support"][str(site)] = deepcopy(support)
        result["control_descriptive_metadata"][str(site)] = {}
        for seed in SEEDS:
            marginal = [dict(index=i,defined_rows=5760,positive_rows=2880,negative_rows=2880,
                positive_groups=60,negative_groups=60) for i in range(232)]
            result["control_descriptive_metadata"][str(site)][str(seed)] = dict(
                control_kind="canonical_visible_prefix_keyed_random_task_v1",control_seed=seed,
                marginals_preserved=False,lawful_joint_ssa_graph=False,
                real_marginals={s:marginal for s in ("train","development")},
                control_marginals={s:[dict(c,positive_rows=2800,negative_rows=2960) for c in marginal] for s in ("train","development")})
    for site,(backend,layer),seed in product(SITES,[("hidden",layer) for layer in MODELS[model][3]]+[("surface",-1)],SEEDS):
        methods = {}
        for method in METHODS:
            heads = {}
            for family,slot in product(FAMILIES,range(4)):
                n = 0 if site==3 and family=="copy_parent" else 1440
                candidates = list(range(1,5)) if family=="current_version" else list(range(8))
                counts = dict(zip(candidates,(600,360,360,120))) if family=="current_version" and site in (7,8) else {c:(n if c==candidates[0] else 0) for c in candidates}
                heads[f"{family}/{slot}"] = dict(family=family,n=n,accuracy=.5 if n else None,
                    group_macro_accuracy=.5 if n else None,missing_predictions=0,
                    classes={str(c):dict(n=counts[c],accuracy=.5 if counts[c] else None) for c in candidates},
                    train_support=dict(constant_training_task=False),per_group=groups if n else {})
            methods[method] = dict(categorical_heads=heads,whole_categorical_families={
                f:deepcopy(zero if site==3 and f=="copy_parent" else whole) for f in FAMILIES})
        result["fits"].append(dict(name=f"{backend}_layer{layer}_site{site}_seed{seed}",backend=backend,
            layer=layer,site=site,seed=seed,factorizations=1,exact_parameter_score_replay=True,metrics=methods))
    summary = dict(status="complete_exploratory",evaluation_role=ROLE,fit_banks=45,factorizations=45,
        parameter_replay_rows=259200,new_model_queries=0,generated_holdouts_opened=False,
        primary={b:{m:{f:.5 for f in FAMILIES} for m in METHODS} for b in ("hidden","surface")},
        primary_group_macro={b:{m:{f:.5 for f in FAMILIES} for m in METHODS} for b in ("hidden","surface")})
    return result,summary


def _synthetic_workspace(root):
    snapshot = root / "artifacts/snapshots/synthetic_schedule"
    source = dict(snapshot=str(snapshot), snapshot_id="synthetic", source_sha256="a" * 64)
    configs = {}
    for model in MODEL_KEYS:
        cap_path = Path("configs/binding/diversity_decoding_20261028_v1") / (model + "_capture.json")
        cap = dict(model=MODELS[model][1], model_revision=MODELS[model][2], tokenizer_revision=MODELS[model][2],
                   layers=list(MODELS[model][3]), dataset_sha256=DATASET_SHA,
                   evaluation_role="discovery_diversity_capture_v1", hidden_size=4096 if model=="llama8b" else 8192,
                   batch_size=256 if model=="llama8b" else 128,
                   run_dir=str(SUITE/model/"capture"), dataset_manifest_sha256="e"*64)
        cap_data = json_bytes(cap); publish(snapshot / cap_path, cap_data)
        configs[str(cap_path)] = hashlib.sha256(cap_data).hexdigest()
        relative = cap_path.with_name(model + "_readouts.json")
        config = dict(evaluation_role=ROLE, primary_layer=24, capture_config=str(cap_path),
            capture_config_sha256=configs[str(cap_path)], declared_plan_sha256="b" * 64,
            run_dir=str(SUITE / model / "readouts"), report=f"reports/binding/diversity_decoding_{model}_v1.md")
        data = json_bytes(config); publish(snapshot / relative, data)
        configs[str(relative)] = hashlib.sha256(data).hexdigest()
    frozen = dict(snapshot_id="synthetic", code=dict(source_sha256="a" * 64), config_files=configs)
    data = json_bytes(frozen); publish(snapshot / "frozen_manifest.json", data)
    source["frozen_manifest_sha256"] = hashlib.sha256(data).hexdigest()
    publish(root/SUITE/"execution_source_v1.json", json_bytes(dict(snapshot=str(snapshot),snapshot_id="synthetic",code="a"*64)))
    for model in MODEL_KEYS:
        base = root / SUITE / model / "readouts"
        relative = Path("configs/binding/diversity_decoding_20261028_v1") / (model + "_readouts.json")
        config = json.loads((snapshot / relative).read_text())
        cap = json.loads((snapshot/Path(config["capture_config"])).read_text())
        capfolder = root/cap["run_dir"];shape=[5760,3,4,cap["hidden_size"]]
        common = dict(source=source,feature_shape=shape,generated_responses=0,generation_calls=0,generated_holdouts_opened=False)
        calls = math.ceil(5760/cap["batch_size"])
        capsummary = dict(common,complete=True,cases=5760,model_prefill_cases=5760,new_model_queries=5760,prefill_batch_calls=calls,
            collection_attempts=[dict(status="complete",prefill_cases_attempted=5760,prefill_cases_returned=5760,prefill_batch_calls=calls)])
        capaudit = dict(common,status="passed",finite_float32_features=True,source_model_prefill_cases=5760,new_model_queries=0)
        preflight = dict(status="passed",cases=5760,config_hash=digest(cap),source=source,new_model_queries=0,
            recipe=dict(tokenization_mode="native" if model=="llama8b" else "codellama_official_boundary_v1",dtype="bfloat16",batch_size=cap["batch_size"]),
            source_review=dict(source_rows=5760,components={"train":45,"development":15},split_rows={"train":4320,"development":1440},dataset_manifest_sha256=cap["dataset_manifest_sha256"]))
        capmeta={name:dict(path=str((capfolder/name).relative_to(root)),sha256="f"*64) for name in
            ("registration.json","preflight.json","prepared_cases.jsonl","manifest.json","summary.json","audit.json")}
        for name,value in (("preflight.json",preflight),("summary.json",capsummary),("audit.json",capaudit)):
            data=json_bytes(value);publish(capfolder/name,data);capmeta[name]["sha256"]=hashlib.sha256(data).hexdigest()
        capreceipt=dict(common,status="complete_exploratory",evaluation_role="discovery_diversity_capture_v1",config_hash=digest(cap),
            dataset_sha256=DATASET_SHA,cases=5760,model_prefill_cases=5760,new_model_queries=5760,prefill_batch_calls=calls,metadata=capmeta)
        publish(capfolder/"completion_manifest_v1.json",json_bytes(capreceipt))
        result, summary = synthetic_result(model)
        for value in (result, summary):
            value.update(config_hash=digest(config), fit_source=source, capture_source=source)
        artifacts = {}
        for fit in result["fits"]:
            path = base / (fit["name"] + ".npz")
            fit["artifact"] = str(path.relative_to(root))
            # Deliberately no NPZ file exists: publication must not open it.
            artifacts[fit["name"]] = dict(path=str(path.relative_to(root)), sha256="c" * 64, bytes=1234)
        registration = dict(evaluation_role=ROLE, config=config, config_hash=digest(config), fit_source=source,
            capture_source=source, fixed_recipe=result["protocol"], dataset_sha256=DATASET_SHA,
            new_model_queries=0, generated_holdouts_opened=False)
        audit = dict(status="passed", evaluation_role=ROLE, config_hash=digest(config), fit_banks=45,
            factorizations=45, parameter_replay_rows=259200, exact_parameter_score_replays=True,
            new_model_queries=0, generated_holdouts_opened=False)
        for name, filename, value in (("registration", "registration.json", registration),
                ("results", "results_v1.json", result), ("summary", "summary.json", summary), ("audit", "audit.json", audit)):
            data = json_bytes(value); path = base / filename; publish(path, data)
            artifacts[name] = dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        report_data = b"Synthetic completed scientific report\n"
        publish(root/config["report"],report_data)
        artifacts["report"] = dict(path=config["report"], sha256=hashlib.sha256(report_data).hexdigest(), bytes=len(report_data))
        receipt = dict(schema_version=1, status="complete_exploratory", evaluation_role=ROLE,
            config_hash=digest(config), fit_source=source, capture_source=source,
            fit_banks=45, factorizations=45, parameter_replay_rows=259200, artifacts=artifacts,
            new_model_queries=0, generated_holdouts_opened=False)
        publish(base / "completion_manifest_v1.json", json_bytes(receipt))
        replay = dict(status="passed", evaluation_role=ROLE, config_hash=digest(config), fit_source=source,
            capture_source=source, fit_banks=45, factorizations=45, parameter_replay_rows=259200,
            source_artifacts=artifacts, exact_saved_parameter_score_replays=True,
            all_real_and_control_scores_replayed=True, all_scientific_metrics_recomputed=True,
            train_support_and_control_marginals_recomputed=True, new_fits=0, new_model_queries=0,
            generated_holdouts_opened=False)
        publish(base / "parameter_replay_review_v1.json", json_bytes(replay))


def self_test():
    checks = 0
    for model in MODEL_KEYS:
        result, summary = synthetic_result(model)
        value = extract_model(result, summary, model, dict(primary_layer=24))
        require(len(value["cells"]) == 405, "Synthetic complete grid failed"); checks += 1
        for mutate in (lambda r: r["fits"].pop(),
                lambda r: r["fits"].append(deepcopy(r["fits"][0])),
                lambda r: r["fits"][0]["metrics"]["direct"]["whole_categorical_families"]["copy_parent"].update(accuracy=.5),
                lambda r: r["primary"].update(layer=36),
                lambda r: r["fits"][0]["metrics"]["direct"]["categorical_heads"]["current_definition/0"]["classes"].pop("7"),
                lambda r: r["control_descriptive_metadata"]["7"]["17"].update(marginals_preserved=True),
                lambda r: r["training_support"]["7"]["categorical_heads"][0]["classes"][2].update(development_rows=0),
                lambda r: r["training_support"]["8"]["categorical_heads"][0]["classes"][3].update(train_groups=2),
                lambda r: r["fits"][0]["metrics"]["direct"]["whole_categorical_families"]["current_definition"]["per_group"]["graph0"].update(n=95)):
            bad = deepcopy(result); mutate(bad)
            try:
                extract_model(bad, summary, model, dict(primary_layer=24))
            except ValueError:
                checks += 1
            else:
                raise AssertionError("Invalid synthetic scientific metadata was accepted")
    with tempfile.TemporaryDirectory(prefix="schedule-publisher-selftest-") as temporary:
        root = Path(temporary).resolve(); _synthetic_workspace(root)
        first = publication(root); second = publication(root)
        require(first["status"] == "published" and second["status"] == "byte_identical_reproduction", "Publication regeneration failed"); checks += 1
        table = list(csv.DictReader((root / SUITE / "form_cells_v1.csv").open()))
        require(len(table) == 810 and sum(r["site"] == "3" and r["family"] == "copy_parent" and r["accuracy"] == "" for r in table) == 90,
                "Undefined site3 tasks or complete CSV grid lost"); checks += 1
        require(not list(root.rglob("*.npz")), "Self-test must not materialize parameter arrays"); checks += 1
        large = root/"large_metadata.json"
        publish(large, json_bytes(dict(padding="x"*(9*1024**2))))
        try:
            read_json(root,large)
        except ValueError:
            checks += 1
        else:
            raise AssertionError("Large metadata bypassed the compact default bound")
        require(len(read_json(root,large,limit=MAX_JSON)["padding"])==9*1024**2
                and MAX_JSON==192*1024**2,"Separate rich192MiB input bound failed");checks += 1
        capture_folder=root/SUITE/"llama8b/capture"
        capture_receipt_path=capture_folder/"completion_manifest_v1.json"
        capture_receipt=json.loads(capture_receipt_path.read_text())
        capture_summary_path=capture_folder/"summary.json"
        capture_summary=json.loads(capture_summary_path.read_text())
        capture_summary["collection_attempts"].insert(0,dict(status="failed",prefill_cases_attempted=128,
            prefill_cases_returned=0,prefill_batch_calls=1))
        capture_summary["new_model_queries"]+=128;capture_summary["prefill_batch_calls"]+=1
        data=json_bytes(capture_summary);capture_summary_path.write_bytes(data)
        capture_receipt["metadata"]["summary.json"]["sha256"]=hashlib.sha256(data).hexdigest()
        capture_receipt["new_model_queries"]+=128;capture_receipt["prefill_batch_calls"]+=1
        capture_receipt_path.write_bytes(json_bytes(capture_receipt))
        cap_path=Path(capture_receipt["source"]["snapshot"])/"configs/binding/diversity_decoding_20261028_v1/llama8b_capture.json"
        INPUTS.clear()
        retry=capture_accounting(root,json.loads(cap_path.read_text()),capture_receipt["source"])
        require(retry["distinct_cases"]==5760 and retry["attempted_cases"]==5888
                and retry["retry_case_attempts"]==128,"Retry prefill accounting was hidden");checks+=1
        path = root / SUITE / "llama8b/readouts/parameter_replay_review_v1.json"
        value = json.loads(path.read_text()); value["all_scientific_metrics_recomputed"] = False; path.write_bytes(json_bytes(value))
        try:
            publication(root)
        except ValueError:
            checks += 1
        else:
            raise AssertionError("Incomplete metric audit was accepted")
        require((root / SUITE / "publication_review_v1.json").is_file(), "Rejected rerun removed publication")
    return dict(status="passed", synthetic_checks=checks, actual_scientific_outcomes_opened=False,
                source_or_parameter_arrays_opened=False, temporary_workspace_removed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else publication(workspace()), sort_keys=True))


if __name__ == "__main__":
    main()
