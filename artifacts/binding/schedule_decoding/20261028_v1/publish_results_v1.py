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

ROLE = "discovery_schedule_readouts_v1"
PUBLICATION_ROLE = "discovery_schedule_decoding_publication_v1"
SUITE = Path("artifacts/binding/schedule_decoding/20261028_v1")
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
DATASET_SHA = "4021f720282fbd7b1344a4a92d5da02abf5269cd9b62d13eebbd5e40e2f4e287"
MAX_JSON = 64 * 1024**2
INPUTS = {}
LIMITATIONS = [
    "Adaptive discovery on 15 canonical SSA graph families: ten TRAIN and five DEV; numeric, lexical and query relatives are dependent.",
    "The three-TRAIN-group class-support diagnostic is descriptive, not a behavioral reliability gate or scientific qualification.",
    "All declared heads and classes remain evaluated, including rare, unsupported and constant tasks; no favorable layer, seed or subset is selected.",
    "At site3 current definitions and versions are initialization constants; future copy-parent targets are undefined.",
    "The DEV version head for slot1 is constant at2 and cannot demonstrate discrimination among versions.",
    "Versions3/4 occur only in restricted slots in this source bank; no general all-slot version-recovery claim follows.",
    "Parent and current-definition heads predict statement indices; converting them to natural v@N labels using oracle maps would be an oracle-assisted postmetric.",
    "Explicit current-version heads predict versions1..4, but do not decode the complete destination/version identity of every obsolete statement.",
    "Random-prefix labels form a prefix-consistent sham task; real/control class marginals and task difficulty differ, and the joint labels need not be lawful SSA graphs.",
    "The character baseline sees exactly the visible text; hidden decoding or a hidden-minus-surface difference does not establish natural causal use.",
    "Assignment schedules also change definition age, position and dependency depth; no copying, binding or selection mechanism is identified.",
    "All points average three weighting seeds; five DEV graph families support descriptive group summaries, with no new bootstrap, confidence interval or independent replication claim.",
    "Sealed final/extrapolation outcomes, historical failed gates and optional training remain unchanged.",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_bytes(value):
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    require(len(data) <= MAX_JSON, "Publication JSON exceeds64MiB")
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


def read_json(root, path, expected=None):
    path = resolve(root, path)
    require(path.suffix == ".json" and path.is_file() and path.stat().st_size <= MAX_JSON,
            "Only bounded JSON metadata may be opened: " + str(path))
    with path.open("rb") as stream:
        data = stream.read(MAX_JSON + 1)
    require(len(data) <= MAX_JSON, "JSON metadata grew beyond bound")
    entry = pin(root, path, data)
    if isinstance(expected, str):
        require(entry["sha256"] == expected, "Metadata SHA256 differs")
    elif expected is not None:
        require(entry["sha256"] == expected["sha256"] and entry["bytes"] == expected["bytes"]
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
    require(type(cell.get("n")) is int and 0 <= cell["n"] <= 696 and cell.get("heads") == 4,
            "Whole-head denominators differ")
    require(_point(cell.get("accuracy")) and _point(cell.get("group_macro_accuracy")), "Invalid accuracy")
    groups = cell.get("per_group")
    require(isinstance(groups, dict), "Per-graph outcomes required")
    if not cell["n"]:
        require(not groups and cell["accuracy"] is None and cell["group_macro_accuracy"] is None,
                "Undefined whole-head tasks must retain null points")
        return
    require(cell["n"] == 696 and len(groups) == 5, "All five DEV graph families required")
    require(all(type(v.get("n")) is int and v["n"] > 0 and _point(v.get("accuracy"))
                and v["accuracy"] is not None for v in groups.values()), "Invalid per-graph cells")
    require(sum(v["n"] for v in groups.values()) == cell["n"], "Graph cell denominators differ")
    require(math.isclose(cell["accuracy"], sum(v["n"] * v["accuracy"] for v in groups.values()) / cell["n"], abs_tol=1e-12)
            and math.isclose(cell["group_macro_accuracy"], sum(v["accuracy"] for v in groups.values()) / 5, abs_tol=1e-12),
            "Row/group aggregation differs from saved graph cells")


def _mean(values):
    require(len(values) == 3, "All three declared weighting seeds required")
    return sum(values) / 3 if all(v is not None for v in values) else None


def _same_point(left, right):
    return left is None and right is None or (left is not None and right is not None
        and math.isclose(left, right, rel_tol=0, abs_tol=1e-14))


def extract_model(result, summary, model, config):
    expected = set(product(SITES, [("hidden", layer) for layer in MODELS[model][3]] + [("surface", -1)], SEEDS))
    observed = set(); rows = []
    require(result.get("model") == MODELS[model][1] and result.get("cases") == 2016
            and result.get("training_rows") == 1320 and result.get("development_rows") == 696
            and result.get("training_groups") == 10 and result.get("development_groups") == 5,
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
                require(cell["n"] == (0 if fit["site"] == 3 and family == "copy_parent" else 696),
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
                             weighting_seeds=list(SEEDS), rows_per_seed=696, graph_groups_per_seed=5)
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
    return dict(model=model, label=MODELS[model][0], checkpoint=MODELS[model][1],
        model_revision=MODELS[model][2], layers=list(MODELS[model][3]), primary_layer=config["primary_layer"],
        primary_site=7, cases=2016, training_rows=1320, development_rows=696,
        training_graph_groups=10, development_graph_groups=5, primary=primary, cells=rows,
        control_marginal_differences=changes, training_support=result["training_support"])


def load_model(root, model):
    base = root / SUITE / model / "readouts"
    receipt = read_json(root, base / "completion_manifest_v1.json")
    require(receipt.get("status") == "complete_exploratory" and receipt.get("schema_version") == 1
            and receipt.get("evaluation_role") == ROLE and receipt.get("fit_banks") == 45
            and receipt.get("factorizations") == 45 and receipt.get("parameter_replay_rows") == 90720
            and receipt.get("new_model_queries") == 0 and receipt.get("generated_holdouts_opened") is False,
            "Completed matching45-bank readout receipt required")
    relative = Path("configs/binding/schedule_decoding_20261028_v1") / (model + "_readouts.json")
    config = source_profile(root, receipt["fit_source"], relative)
    require(config["evaluation_role"] == ROLE and config["primary_layer"] == 24
            and digest(config) == receipt["config_hash"] and resolve(root, config["run_dir"]) == base,
            "Prospectively frozen readout configuration differs")
    cap_relative = Path(config["capture_config"])
    capture = source_profile(root, receipt["capture_source"], cap_relative)
    capture_path = resolve(root, receipt["capture_source"]["snapshot"]) / cap_relative
    require(INPUTS[str(capture_path.relative_to(root))]["sha256"] == config["capture_config_sha256"]
            and capture["model"] == MODELS[model][1]
            and capture["model_revision"] == capture["tokenizer_revision"] == MODELS[model][2]
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
    metadata = {name: read_json(root, expected[name], inventory[name])
                for name in ("registration", "results", "summary", "audit")}
    replay = read_json(root, base / "parameter_replay_review_v1.json")
    require(replay.get("status") == "passed" and replay.get("evaluation_role") == ROLE
            and replay.get("config_hash") == receipt["config_hash"]
            and replay.get("fit_source") == receipt["fit_source"] and replay.get("capture_source") == receipt["capture_source"]
            and replay.get("fit_banks") == replay.get("factorizations") == 45
            and replay.get("parameter_replay_rows") == 90720 and replay.get("source_artifacts") == inventory
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
            and result.get("parameter_replay_rows") == summary.get("parameter_replay_rows") == audit.get("parameter_replay_rows") == 90720,
            "Completed result/summary/audit accounting differs")
    require(result["protocol"].get("sites") == list(SITES) and result["protocol"].get("seeds") == list(SEEDS)
            and result["protocol"].get("alpha") == 100.
            and result["protocol"].get("primary_train_class_group_minimum") == 3,
            "Fixed source/site/seed/readout protocol differs")
    require(registration["dataset_sha256"] == DATASET_SHA
            and {fit["name"]: resolve(root, fit["artifact"]) for fit in result["fits"]}
            == {name: path for name, path in expected.items() if path.suffix == ".npz"},
            "Scientific parameter inventory differs from completion receipt")
    value = extract_model(result, summary, model, config)
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
    matplotlib.rcParams.update({"svg.hashsalt": "schedule_decoding_v1", "font.family": "DejaVu Sans", "font.size": 10})
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
            ax.set_xlabel("Hidden layer (primary24)")
            if j == 0:
                ax.set_ylabel("DEV graph-macro whole-task correct (%)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, .045))
    fig.suptitle("Varied schedules: all fixed layers at the final-assignment site7", fontsize=14, y=.99)
    fig.text(.5, .012, "Means over three weighting seeds and five DEV graph families; no confidence intervals. All sites remain in the CSV.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .12, 1, .95), w_pad=2, h_pad=2)
    png, svg = io.BytesIO(), io.BytesIO()
    fig.savefig(png, format="png", dpi=170, metadata={"Software": "CodeCue deterministic schedule publisher"})
    fig.savefig(svg, format="svg", metadata={"Date": None, "Creator": "CodeCue deterministic schedule publisher"})
    plt.close(fig)
    return png.getvalue(), svg.getvalue(), matplotlib.__version__


def report_bytes(models):
    lines = ["# Varied-schedule definition and relationship decoding", "",
        "Both checkpoints completed the fixed discovery grid and passed independent saved-parameter, scientific-metric and control-marginal replay audits. "
        "This is descriptive decoding, without a behavioral reliability qualification or causal mechanism claim.", "",
        "Each model uses 2,016 source rows: 1,320 TRAIN rows in ten canonical SSA graph families and 696 DEV rows in five families. "
        "The 84 schedule/parent templates include 28 destination schedules and actual assignment versions through 4. "
        "All numeric, lexical, query and equivalent-graph relatives retain their original split. There are 45 joint direct/control parameter banks per model.", "",
        "The primary endpoint was nominated before capture: layer24, final-assignment site7, for both checkpoints. "
        "The following two tables average all three fixed weighting seeds17/29/43. No layer, seed or supported-class subset is selected."]
    for field, title in (("accuracy", "Row-weighted DEV whole-task accuracy"),
                         ("group_macro_accuracy", "Equal-graph DEV whole-task accuracy")):
        lines += ["", title + ":", "", "| Model | Backend | Method | Current definitions | Current versions | Copy parents |",
                  "|---|---|---|---:|---:|---:|"]
        for model, backend, method in product(MODEL_KEYS, ("hidden", "surface"), METHODS):
            points = [models[model]["primary"][backend][method][family][field] for family in FAMILIES]
            values = ["undefined" if point is None else f"{100 * point:.3f}%" for point in points]
            lines.append("| " + " | ".join([models[model]["label"], backend, method, *values]) + " |")
    lines += ["", "![All fixed layers at site7](figures/schedule_decoding_v1.svg)", "",
        "The six panels show site7 only: all four hidden layers, direct and prefix-sham curves, with surface-direct and TRAIN-prior references. "
        "Each point is the mean of three weighting-seed graph-macro accuracies. No intervals or independent-replication claim are assigned to these dependent relatives. "
        "[form_cells_v1.csv](../../artifacts/binding/schedule_decoding/20261028_v1/form_cells_v1.csv) retains all810 model/site/layer/seed/backend/method/task cells, "
        "including all class counts, per-graph outcomes and null copy-parent tasks at site3.", "",
        "At site3 current definitions and version1 are initialization priors; future copies are undefined. At the final site, DEV slot1 has constant version2, "
        "so its accuracy cannot establish version discrimination. The three-TRAIN-group class-support diagnostic is prospective to this discovery study and is not a relaxed historical gate. "
        "Rare parent classes, absent choices and every defined DEV outcome remain reported.", "",
        "Definition and parent heads predict statement indices0..7. Mapping a predicted statement to a natural variable@version label using source-derived oracle maps would be an oracle-assisted postmetric; "
        "explicit current-version heads separately predict versions1..4. These measurements do not decode every obsolete statement's variable/version identity.", "",
        "The source character baseline uses the exact visible prefix. Prefix-sham labels are tied across identical canonical visible prefixes and pre-query lexical/query twins. "
        "They do not preserve class marginals or necessarily define a lawful joint graph. All nine per-model control marginal descriptions are pinned in the original scientific result; "
        "the comparison records their digests and changed-column counts. A direct-minus-sham or hidden-minus-source difference is task-specific descriptive selectivity, not evidence of natural causal use.", "",
        "The publisher reads only completed JSON receipts, SHA-pinned scientific metadata and frozen profiles. It checks the45-bank parameter inventory by metadata without opening NPZs, "
        "raw captures, source/response records, models or tokenizers. No fit, replay, new bootstrap or LM query occurs during publication. "
        "[comparison_v1.json](../../artifacts/binding/schedule_decoding/20261028_v1/comparison_v1.json) records all values and input pins; "
        "[publication_review_v1.json](../../artifacts/binding/schedule_decoding/20261028_v1/publication_review_v1.json) pins every output.", "",
        *["- " + text for text in LIMITATIONS], ""]
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
        source_cases_per_model=2016, total_parameter_banks=90, parameter_banks_opened=0,
        inputs=sorted(INPUTS.values(), key=lambda item: item["path"]), publisher_script=script_pin,
        new_model_queries=0, new_fits=0, new_bootstraps=0, raw_activation_arrays_opened=False,
        source_or_response_records_opened=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    base = root / SUITE
    outputs = {base / "comparison_v1.json": json_bytes(comparison), base / "form_cells_v1.csv": table,
        root / "reports/binding/schedule_decoding_findings_v1.md": report_bytes(models),
        root / "reports/binding/figures/schedule_decoding_v1.png": png,
        root / "reports/binding/figures/schedule_decoding_v1.svg": svg}
    review = dict(status="passed", evaluation_role=PUBLICATION_ROLE, publisher_script=script_pin,
        input_pins=sorted(INPUTS.values(), key=lambda item: item["path"]),
        output_pins=[dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
                     for path, data in outputs.items()], plotting_version=version,
        checks=dict(both_completed_receipts_and_replay_audits_required=True,
            all90_parameter_inventory_pins_verified_as_metadata=True, no_parameter_banks_opened=True,
            all810_task_cells_and_class_counts_preserved=True, null_future_tasks_retained=True,
            primary_layer24_site7_three_seed_means_verified=True, row_and_graph_macro_tables_preserved=True,
            control_marginal_metadata_pinned=True, repeated_figure_render_byte_identical=True),
        reproduction="Every invocation regenerates and byte-checks all existing outputs.",
        new_model_queries=0, new_fits=0, new_bootstraps=0, generated_holdouts_opened=False)
    outputs[base / "publication_review_v1.json"] = json_bytes(review)
    existed = all(path.is_file() for path in outputs)
    for path, data in outputs.items():
        require(not path.is_symlink() and (not path.exists() or path.read_bytes() == data),
                "Immutable publication differs before any write: " + str(path))
    for path, data in outputs.items():
        publish(path, data)
    return dict(status="byte_identical_reproduction" if existed else "published", models=2, task_cells=810,
                publication_review=str(SUITE / "publication_review_v1.json"))


def synthetic_result(model):
    """Minimal complete JSON-only scientific grid for publication contract tests."""
    groups = {f"graph{i}": dict(n=n, accuracy=.5) for i, n in enumerate((120, 120, 144, 144, 168))}
    whole = dict(heads=4, n=696, accuracy=.5, group_macro_accuracy=.5, per_group=groups)
    zero = dict(heads=4, n=0, accuracy=None, group_macro_accuracy=None, per_group={})
    result = dict(status="complete_exploratory", evaluation_role=ROLE, model=MODELS[model][1], cases=2016,
        training_rows=1320, development_rows=696, training_groups=10, development_groups=5,
        primary=dict(layer=24, site=7, tasks=list(FAMILIES), scope="all fixed heads and classes retained; descriptive only"),
        protocol=dict(sites=list(SITES), seeds=list(SEEDS), alpha=100., primary_train_class_group_minimum=3),
        training_support={}, control_descriptive_metadata={}, fits=[], fit_banks=45, factorizations=45,
        parameter_replay_rows=90720, dataset_sha256=DATASET_SHA, new_model_queries=0, generated_holdouts_opened=False)
    for site, (backend, layer), seed in product(SITES,
            [("hidden", layer) for layer in MODELS[model][3]] + [("surface", -1)], SEEDS):
        metrics = {}
        for method in METHODS:
            heads = {}
            for family, slot in product(FAMILIES, range(4)):
                n = 0 if site == 3 and family == "copy_parent" else 696
                candidates = list(range(1, 5)) if family == "current_version" else list(range(8))
                heads[f"{family}/{slot}"] = dict(family=family, n=n, accuracy=.5 if n else None,
                    group_macro_accuracy=.5 if n else None, missing_predictions=0,
                    classes={str(c): dict(n=n if c == candidates[0] else 0,
                                         accuracy=.5 if n and c == candidates[0] else None) for c in candidates},
                    train_support=dict(constant_training_task=True), per_group=groups if n else {})
            metrics[method] = dict(categorical_heads=heads,
                whole_categorical_families={f: deepcopy(zero if site == 3 and f == "copy_parent" else whole) for f in FAMILIES})
        result["fits"].append(dict(name=f"{backend}_layer{layer}_site{site}_seed{seed}", backend=backend,
            layer=layer, site=site, seed=seed, factorizations=1, exact_parameter_score_replay=True, metrics=metrics))
    for site in SITES:
        result["control_descriptive_metadata"][str(site)] = {}
        for seed in SEEDS:
            marginal = [dict(index=i, defined_rows=2016, positive_rows=1008, negative_rows=1008,
                             positive_groups=15, negative_groups=15) for i in range(232)]
            result["control_descriptive_metadata"][str(site)][str(seed)] = dict(
                control_kind="canonical_visible_prefix_keyed_random_task_v1", control_seed=seed,
                marginals_preserved=False, lawful_joint_ssa_graph=False,
                real_marginals={s: marginal for s in ("train", "development")},
                control_marginals={s: [dict(c, positive_rows=1000, negative_rows=1016) for c in marginal]
                                   for s in ("train", "development")})
    summary = dict(status="complete_exploratory", evaluation_role=ROLE, fit_banks=45, factorizations=45,
        parameter_replay_rows=90720, new_model_queries=0, generated_holdouts_opened=False,
        primary={b: {m: {f: .5 for f in FAMILIES} for m in METHODS} for b in ("hidden", "surface")},
        primary_group_macro={b: {m: {f: .5 for f in FAMILIES} for m in METHODS} for b in ("hidden", "surface")})
    return result, summary


def _synthetic_workspace(root):
    snapshot = root / "artifacts/snapshots/synthetic_schedule"
    source = dict(snapshot=str(snapshot), snapshot_id="synthetic", source_sha256="a" * 64)
    configs = {}
    for model in MODEL_KEYS:
        cap_path = Path("configs/binding/schedule_decoding_20261028_v1") / (model + "_capture.json")
        cap = dict(model=MODELS[model][1], model_revision=MODELS[model][2], tokenizer_revision=MODELS[model][2],
                   layers=list(MODELS[model][3]), dataset_sha256=DATASET_SHA)
        cap_data = json_bytes(cap); publish(snapshot / cap_path, cap_data)
        configs[str(cap_path)] = hashlib.sha256(cap_data).hexdigest()
        relative = cap_path.with_name(model + "_readouts.json")
        config = dict(evaluation_role=ROLE, primary_layer=24, capture_config=str(cap_path),
            capture_config_sha256=configs[str(cap_path)], declared_plan_sha256="b" * 64,
            run_dir=str(SUITE / model / "readouts"), report=f"reports/binding/schedule_decoding_{model}_v1.md")
        data = json_bytes(config); publish(snapshot / relative, data)
        configs[str(relative)] = hashlib.sha256(data).hexdigest()
    frozen = dict(snapshot_id="synthetic", code=dict(source_sha256="a" * 64), config_files=configs)
    data = json_bytes(frozen); publish(snapshot / "frozen_manifest.json", data)
    source["frozen_manifest_sha256"] = hashlib.sha256(data).hexdigest()
    for model in MODEL_KEYS:
        base = root / SUITE / model / "readouts"
        relative = Path("configs/binding/schedule_decoding_20261028_v1") / (model + "_readouts.json")
        config = json.loads((snapshot / relative).read_text())
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
            factorizations=45, parameter_replay_rows=90720, exact_parameter_score_replays=True,
            new_model_queries=0, generated_holdouts_opened=False)
        for name, filename, value in (("registration", "registration.json", registration),
                ("results", "results_v1.json", result), ("summary", "summary.json", summary), ("audit", "audit.json", audit)):
            data = json_bytes(value); path = base / filename; publish(path, data)
            artifacts[name] = dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        artifacts["report"] = dict(path=config["report"], sha256="d" * 64, bytes=123)
        receipt = dict(schema_version=1, status="complete_exploratory", evaluation_role=ROLE,
            config_hash=digest(config), fit_source=source, capture_source=source,
            fit_banks=45, factorizations=45, parameter_replay_rows=90720, artifacts=artifacts,
            new_model_queries=0, generated_holdouts_opened=False)
        publish(base / "completion_manifest_v1.json", json_bytes(receipt))
        replay = dict(status="passed", evaluation_role=ROLE, config_hash=digest(config), fit_source=source,
            capture_source=source, fit_banks=45, factorizations=45, parameter_replay_rows=90720,
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
                lambda r: r["control_descriptive_metadata"]["7"]["17"].update(marginals_preserved=True)):
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
