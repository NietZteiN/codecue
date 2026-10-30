"""Immutable JSONL datasets, grouped structural splits, and independent validation."""
from __future__ import annotations

import ast
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from .interpreter import execute, python_oracle, substituted_source
from .programs import CONDITIONS, FAMILIES, computed_swap, features, make_program, rename, renaming, skeleton

SCHEMA_VERSION = 1


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_jsonl(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")
    tmp.replace(path)
    try:
        from .experiment_log import note_artifact
        note_artifact(path.resolve())
    except Exception as exc:
        import sys
        print(f'Experiment metadata logging deferred: {type(exc).__name__}: {exc}',file=sys.stderr)


def diagnostics(source, trace):
    """Predefined assignment-result substitutions, plus distinguishable arithmetic errors."""
    current = trace["execution_trace"][-1]
    alternatives = []
    # Target the final definition of each output-relevant variable; propagate normally.
    relevant = {u["name"] for u in trace["output_uses"]}
    for name in sorted(relevant):
        version = current["versions"][name]
        for old, v in trace["versioned_bindings"].items():
            if old.startswith(name + "@") and old != version:
                alternatives.append(("obsolete_assignment", version, v, old))
        for other in sorted(relevant - {name}):
            alternatives.append(("competing_variable", version, current["values"][other], current["versions"][other]))
    out = []
    for label, definition, replacement, donor in alternatives:
        try:
            cf = execute(source, {definition: replacement})
        except ValueError:
            continue
        out.append({"label": label, "definition": definition, "replacement": replacement, "donor": donor,
                    "expected_answer": cf["expected_answer"],
                    "expected_downstream_state": cf["execution_trace"][-1]["values"],
                    "functional_effect": cf["expected_answer"] != trace["expected_answer"],
                    "substitution_semantics": "replace assignment result and recompute descendants"})
    # Local computation alternative: replace final subtraction with addition.
    tree = ast.parse(source)
    arithmetic_changed = False
    for node in ast.walk(tree.body[-1]):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
            node.op = ast.Add()
            arithmetic_changed = True
            break
    if arithmetic_changed:
        alternate = execute(ast.unparse(tree))
        out.append({"label": "arithmetic_add_for_subtract", "expected_answer": alternate["expected_answer"],
                    "functional_effect": alternate["expected_answer"] != trace["expected_answer"],
                    "alternative_source": ast.unparse(tree)})
    by_answer = defaultdict(list)
    for i, item in enumerate(out):
        by_answer[item["expected_answer"]].append(i)
    for item in out:
        matches = by_answer[item["expected_answer"]]
        item["compatible_alternatives"] = matches
        item["diagnostically_distinct"] = len(matches) == 1 and item["functional_effect"]
    return out


def generate(config, output):
    algorithm = config.get('algorithm_version')
    if algorithm not in (5, 6):
        raise ValueError('generation requires explicit algorithm_version=5 or 6')
    extrapolation = algorithm == 6
    if extrapolation and (config.get('evaluation_role') != 'structural_extrapolation' or config.get('split_override') != 'test'):
        raise ValueError('version 6 structural extrapolations must be reserved test data')
    if not extrapolation and any(k in config for k in ('variable_count','load_levels','update_levels','distance_padding','split_override')):
        raise ValueError('structural changes require algorithm version 6 and an explicit extrapolation role')
    width = config.get('variable_count', 4)
    padding = config.get('distance_padding', 0)
    references = {}
    reference_skeletons = set()
    for reference in config.get('reference_datasets', []):
        reference = Path(reference)
        ref_manifest = json.loads(reference.with_suffix('.manifest.json').read_text())
        if hashlib.sha256(reference.read_bytes()).hexdigest() != ref_manifest['sha256']:
            raise ValueError('reference dataset content hash mismatch')
        references[str(reference)] = ref_manifest['sha256']
        reference_skeletons.update(skeleton(r['canonical_source']) for r in read_jsonl(reference))
    if extrapolation and not references:
        raise ValueError('structural extrapolations require reference datasets for overlap checks')
    bins = config["answer_magnitude_bins"]
    if len(bins) != 3 or any(len(b) != 2 or b[0] < 0 or b[0] > b[1] for b in bins):
        raise ValueError("specify three valid magnitude bins")
    output = Path(output)
    if output.exists():
        manifest = json.loads(output.with_suffix(".manifest.json").read_text())
        if manifest["generation_config_hash"] != digest(config):
            raise ValueError("existing dataset config mismatch; choose a new path")
        validate(output)
        return manifest
    seed = config["seed"]
    n = config["instances_per_cell"]
    templates = config.get("templates_per_cell", 10)
    if templates != 10 or n < 10 or n % 10:
        raise ValueError("ten structural templates per cell, equal numeric replications; instances_per_cell must be a multiple of ten")
    rng = random.Random(seed)
    records, attempts, rejected, seen = [], 0, 0, set()
    cell_attempts, cell_rejections = Counter(), Counter()
    for family in FAMILIES:
        for load in config.get('load_levels', (2, 4)):
            for updates in config.get('update_levels', (1, 3)):
                # Assignment of templates to partitions fixed independently of outcomes.
                template_order = list(range(templates))
                random.Random(f"{seed}:{family}:{updates}").shuffle(template_order)
                split_of = {t: "train" if i < 6 else "development" if i < 8 else "test"
                            for i, t in enumerate(template_order)}
                for instance in range(n):
                    cell_key = f"{family}:load{load}:updates{updates}"
                    template = instance % templates
                    split = config.get('split_override', split_of[template])
                    for _ in range(10000):
                        attempts += 1
                        cell_attempts[cell_key] += 1
                        source = make_program(family, load, updates, template, rng,
                                              variable_count=width, distance_padding=padding)
                        if skeleton(source) in reference_skeletons:
                            raise ValueError('extrapolation skeleton overlaps reference; redesign the stressor')
                        try:
                            trace = execute(source)
                            f = features(source, trace)
                            if f["computed_values_absent_from_literals"] < 1 or digest(source) in seen:
                                raise ValueError("duplicate or no computed value absent from literals")
                            bin_index = (instance // templates) % 3
                            low, high = bins[bin_index]
                            if not low <= abs(trace["expected_answer"]) <= high:
                                raise ValueError("answer-magnitude stratification")
                        except ValueError:
                            rejected += 1
                            cell_rejections[cell_key] += 1
                            continue
                        seen.add(digest(source))
                        break
                    else:
                        raise RuntimeError("generation rejection budget exhausted")
                    template_id = digest(skeleton(source))[:20]
                    cluster_id = digest([family, updates, template])[:20]
                    base_id = digest([seed, family, load, updates, source])[:24]
                    if extrapolation:
                        cluster_id = digest(['extrapolation', config['cohort'], width, padding, family, updates, template])[:20]
                        base_id = digest(['extrapolation', config['cohort'], seed, family, load, updates, source])[:24]
                    relatives = [("primary", source)]
                    if config.get("counterfactual_pairs", True):
                        relatives.append(("binding_swap", computed_swap(source)))
                    if config.get("arithmetic_controls", True):
                        control_query = "((v0 + 1) - (1 + 0)) + 0" + (' + 0 + 0' if load == 6 else '')
                        relatives.append(("arithmetic_control", "\n".join(source.splitlines()[:-1] + [control_query])))
                    for kind, canonical in relatives:
                        truth = execute(canonical)
                        cf = diagnostics(canonical, truth)
                        semantic_features = features(canonical, truth)
                        if skeleton(canonical) in reference_skeletons:
                            raise ValueError('counterfactual/control skeleton overlaps reference')
                        for condition in CONDITIONS:
                            for lexical in (0, 1):
                                mapping = renaming(family, condition, lexical, split, width)
                                if family == "snapshot" and kind == "binding_swap" and condition != "neutral":
                                    mapping["v0"], mapping["v1"] = mapping["v1"], mapping["v0"]
                                rendered = rename(canonical, mapping)
                                rendered_trace = execute(rendered)
                                inv = {v: k for k, v in mapping.items()}
                                # Labels use canonical slots, spans use the actual rendering.
                                tree = ast.parse(rendered)
                                spans = [{"statement": i, "start": sum(len(s) + 1 for s in rendered.splitlines()[:i]),
                                          "end": sum(len(s) + 1 for s in rendered.splitlines()[:i]) + len(rendered.splitlines()[i])}
                                         for i, _ in enumerate(tree.body)]
                                cue_source = rename(canonical, {f"v{i}": f"v{i ^ 1}" for i in range(width)}).splitlines()
                                # Query-only ownership permutation: explicit cheap name-role alternative.
                                cue_source = canonical.splitlines()[:-1] + [cue_source[-1]]
                                role_answer = execute("\n".join(cue_source))["expected_answer"]
                                records.append({"schema_version": SCHEMA_VERSION,
                                    "id": f"{base_id}:{kind}:{condition}:{lexical}", "base_id": base_id,
                                    "template_id": template_id, "family": family, "paired_group_id": base_id,
                                    "cluster_id": cluster_id,
                                    "counterfactual_group_id": base_id, "split": split, "seed": seed,
                                    "source": rendered, "canonical_source": canonical, "rename_map": mapping,
                                    "condition": condition, "lexical_realization": lexical, "control_kind": kind,
                                    "load": load, "updates": updates, "token_counts": None,
                                    "statement_spans": spans, "variable_slots": {f"v{i}": i for i in range(width)},
                                    **truth, "diagnostic_counterfactuals": cf,
                                    "name_role_alternative_answer": role_answer,
                                    "features": semantic_features, "answer_magnitude_bin": bin_index,
                                    "canonical_ast_hash": digest(ast.dump(ast.parse(canonical))),
                                    "canonical_skeleton": skeleton(source),
                                    "generation_config_hash": digest(config)})
                                if extrapolation:
                                    records[-1].update(evaluation_role='structural_extrapolation',
                                                       extrapolation_cohort=config['cohort'],
                                                       distance_padding=padding, variable_count=width)
                                assert rendered_trace["expected_answer"] == truth["expected_answer"]
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".tmp")
    with temp.open("w") as f:
        for row in records:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    temp.replace(output)
    manifest = {"schema_version": SCHEMA_VERSION, "generation_config": config,
                "generation_config_hash": digest(config), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "rows": len(records), "base_instances": len({r["base_id"] for r in records}),
                "structural_templates": len({r["template_id"] for r in records}),
                "independent_template_clusters": len({r["cluster_id"] for r in records}),
                "split_rows": dict(Counter(r["split"] for r in records)),
                "split_templates": {s: len({r["template_id"] for r in records if r["split"] == s})
                                    for s in ("train", "development", "test")},
                "attempts": attempts, "rejected": rejected, "rejection_rate": rejected / attempts,
                "cell_attempts": dict(cell_attempts), "cell_rejections": dict(cell_rejections),
                "primary_answer_magnitude_bins": dict(Counter(str(r["answer_magnitude_bin"]) for r in records
                    if r["condition"] == "neutral" and r["lexical_realization"] == 0 and r["control_kind"] == "primary")),
                "value_distribution": dict(Counter(str(v) for r in records if r["condition"] == "neutral"
                                           and r["lexical_realization"] == 0 and r["control_kind"] == "primary"
                                           for p in r["execution_trace"] for v in [p["value"]])),
                "token_counts": "filled by the selected tokenizer at model-run time"}
    if extrapolation:
        manifest.update(evaluation_role='structural_extrapolation', cohort=config['cohort'],
                        reference_datasets=references, reference_skeleton_overlap=0)
    write_json(output.with_suffix(".manifest.json"), manifest)
    return manifest


def validate(path):
    rows = read_jsonl(path)
    manifest = json.loads(Path(path).with_suffix(".manifest.json").read_text())
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("dataset content hash mismatch")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("duplicate sample IDs")
    canonical_owners = defaultdict(set)
    for row in rows:
        canonical_owners[row['canonical_ast_hash']].add(row['base_id'])
    if any(len(owners)>1 for owners in canonical_owners.values()):
        raise ValueError('canonical numeric AST duplicated across bases')
    if manifest.get('evaluation_role') == 'structural_extrapolation':
        if {r['split'] for r in rows} != {'test'}:
            raise ValueError('structural extrapolation data must remain test-only')
        actual_skeletons = {skeleton(r['canonical_source']) for r in rows}
        for path, expected_hash in manifest['reference_datasets'].items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected_hash:
                raise ValueError('reference dataset changed')
            if actual_skeletons & {skeleton(r['canonical_source']) for r in read_jsonl(path)}:
                raise ValueError('structural extrapolation overlaps a reference skeleton')
    for key in ("base_id", "template_id", "cluster_id", "paired_group_id", "counterfactual_group_id", "canonical_skeleton"):
        groups = defaultdict(set)
        for r in rows:
            groups[r[key]].add(r["split"])
        if any(len(s) > 1 for s in groups.values()):
            raise ValueError(f"split leakage by {key}")
    actual_skeletons = defaultdict(set)
    for r in rows:
        actual_skeletons[skeleton(r["canonical_source"])].add(r["split"])
    if any(len(s) > 1 for s in actual_skeletons.values()):
        raise ValueError("split leakage by actual counterfactual/control skeleton")
    variants, sources, checks, matched, vocab = defaultdict(list), {}, {}, {}, defaultdict(set)
    for r in rows:
        oracle = execute(r["canonical_source"])
        for field in ("expected_answer", "execution_trace", "versioned_bindings", "dependency_edges", "liveness"):
            if r[field] != oracle[field]:
                raise ValueError(f"incorrect {field}: {r['id']}")
        if rename(r["source"], {v: k for k, v in r["rename_map"].items()}) != ast.unparse(ast.parse(r["canonical_source"])):
            raise ValueError("renaming not AST equivalent")
        vocab[r["split"]].update(r["rename_map"].values())
        variants[(r["base_id"], r["control_kind"])].append(r)
        sources[r["source"]] = execute(r["source"])
        matched.setdefault(r["base_id"], {})[r["control_kind"]] = oracle
        checks[r["canonical_source"]] = r
    for group in variants.values():
        if len(group) != 6 or len({(r["condition"], r["lexical_realization"]) for r in group}) != 6:
            raise ValueError("incomplete naming factorial")
    for a in vocab:
        for b in vocab:
            if a != b and vocab[a] & vocab[b]:
                raise ValueError("identifier vocabulary leakage")
    cf_count, no_effect, ambiguous = 0, 0, 0
    cf_sources = {}
    for source, r in checks.items():
        for cf in r["diagnostic_counterfactuals"]:
            changed = cf.get("alternative_source") or substituted_source(source, cf["definition"], cf["replacement"])
            result = execute(changed)
            if result["expected_answer"] != cf["expected_answer"]:
                raise ValueError("incorrect counterfactual output")
            if "expected_downstream_state" in cf and result["execution_trace"][-1]["values"] != cf["expected_downstream_state"]:
                raise ValueError("incorrect counterfactual downstream state")
            cf_sources[changed] = result
            cf_count += 1
            no_effect += not cf["functional_effect"]
            ambiguous += len(cf["compatible_alternatives"]) > 1
    sources.update(cf_sources)
    items = list(sources.items())
    for start in range(0, len(items), 128):
        batch = items[start:start + 128]
        independent = python_oracle([s for s, _ in batch])
        for (source, expected), actual in zip(batch, independent):
            if actual["answer"] != expected["expected_answer"] or actual["trace"] != [p["values"] for p in expected["execution_trace"]]:
                raise ValueError("Python/interpreter disagreement")
    for group in matched.values():
        if "binding_swap" in group:
            a = group["primary"]["execution_trace"][-1]["values"]
            b = group["binding_swap"]["execution_trace"][-1]["values"]
            if sorted(a.values()) != sorted(b.values()) or (a["v0"], a["v1"]) != (b["v1"], b["v0"]):
                raise ValueError("swap does not preserve the value multiset")
    return {"status": "passed", "rows": len(rows), "independent_python_programs": len(sources),
            "counterfactuals_checked": cf_count, "nonfunctional_substitutions": no_effect,
            "ambiguous_alternatives": ambiguous, "grouped_split_leakage": False,
            "identifier_vocab_overlap": False, "dataset_sha256": manifest["sha256"]}
