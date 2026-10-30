"""Discovery-only preparation of new copy/overwrite graph families.

Canonical groups use the existing generic SSA labels and all 24 slot
permutations, including versions and succession. Candidate searches are finite;
an exhausted profile fails rather than changing novelty or grouping semantics.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import random

from . import relationship_schedule_programs as prior, relationships
from .competition import alpha_skeleton
from .datasets import digest
from .interpreter import execute
from .programs import rename
from .registry import code_identity
from .relationship_capture import _publish, _safe

ROLE = "discovery_relationship_schedule_diversity_sources_v1"
NUMERIC_SEEDS = (751, 857, 967)
PROFILES = ((2, 1, 1, 0), (3, 1, 0, 0), (2, 2, 0, 0))
FAMILIES_PER_PROFILE = 20
TRAIN_FAMILIES_PER_PROFILE = 15
MAX_CANDIDATES = 50_000
MAX_BYTES = 256 * 1024**2
N_ROWS = 60 * 4 * 3 * 2 * 4
LIMITATIONS = [
    "Fresh adaptive discovery source/oracle preparation only; no model, tokenizer, activation, capture, fit or decoded outcome.",
    "Graph novelty is relative only to the two explicitly named SHA-pinned exclusion banks, not the entire project or literature.",
    "The initially considered fully updated profile 1,1,1,1 was exhausted by the old 81-parent routing universe under slot canonicalization and was not generated as new evidence.",
    "The revised profiles 2,1,1,0 / 3,1,0,0 / 2,2,0,0 were fixed before source generation; a finite search failure never changes their allocation.",
    "Four cyclic slot rotations make the version domain slot-complete; version class frequencies and joint graph/slot properties are not fully balanced.",
    "Numeric seeds, rotations, lexical forms and queries are relatives of each canonical graph, not independent topology replications.",
    "Canonical families quotient slot renamings and legal commuting execution orders while retaining actual versions, dependencies and succession.",
    "Short visible prefixes may coincide across graph splits; this is reported and does not imply that final canonical graph families overlap.",
    "Definition ages, positions, dependency depth and repeated overwrites vary together; no isolated mechanism claim follows.",
    "All actual versions, dependencies, current states and answers are oracle targets, never representation features.",
    "The old fixed 2016-case learned heads are incompatible; this publication does not qualify a new readout or scientific model family.",
]


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _profile(destinations):
    return tuple(sorted((Counter(destinations)[slot] for slot in range(4)), reverse=True))


@lru_cache(maxsize=50_000)
def _graph(destinations, parents):
    source = prior._source((1, 2, 3, 4), destinations, parents, 0)
    labels = relationships.labels_at(source, 7, prior.SLOTS)
    graph, _ = prior._canonical_graph(labels)
    return digest(graph)


def _candidate_order(seed):
    candidates = []
    for destinations in product(range(4), repeat=4):
        profile = _profile(destinations)
        if profile not in PROFILES:
            continue
        choices = [tuple(slot for slot in range(4) if slot != destination) for destination in destinations]
        for parents in product(*choices):
            candidates.append((profile, destinations, parents))
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError("declared finite graph search exceeds50,000 candidates")
    random.Random(digest([ROLE, seed, "candidate_order"])).shuffle(candidates)
    return candidates


def _select(seed, excluded):
    selected = {profile: [] for profile in PROFILES}
    seen = {profile: set() for profile in PROFILES}
    candidates = _candidate_order(seed)
    evaluated = 0
    for profile, destinations, parents in candidates:
        if len(selected[profile]) >= FAMILIES_PER_PROFILE:
            continue
        evaluated += 1
        graph = _graph(destinations, parents)
        if graph in excluded or graph in seen[profile]:
            continue
        seen[profile].add(graph)
        selected[profile].append((graph, destinations, parents))
        if all(len(value) == FAMILIES_PER_PROFILE for value in selected.values()):
            break
    counts = {"_".join(map(str, profile)): len(value) for profile, value in selected.items()}
    if any(len(value) != FAMILIES_PER_PROFILE for value in selected.values()):
        raise ValueError("finite graph search exhausted without20 new families per profile; "
                         + json.dumps(dict(available_selected=counts, candidate_count=len(candidates),
                                           candidates_evaluated=evaluated), sort_keys=True))
    return selected, dict(candidate_count=len(candidates), candidates_evaluated=evaluated,
                          excluded_canonical_graphs=len(excluded), selected_per_profile=counts)


def _config(config):
    required = {"evaluation_role", "candidate_seed", "numeric_seeds", "dataset", "review", "report", "excluded_graph_sources"}
    if (not isinstance(config, dict) or set(config) != required or config.get("evaluation_role") != ROLE):
        raise ValueError("exact discovery-only schedule diversity configuration required")
    try:
        size = len(_json_bytes(config))
    except (TypeError, ValueError) as exc:
        raise ValueError("bounded JSON source configuration required") from exc
    if size > 16 * 1024:
        raise ValueError("bounded source configuration required")
    seed = config["candidate_seed"]
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("bounded integer candidate_seed required")
    if (config["numeric_seeds"] != list(NUMERIC_SEEDS)
            or any(type(value) is not int for value in config["numeric_seeds"])):
        raise ValueError("fixed distinct numeric seeds751/857/967 required")
    paths = {}
    for name, suffix in (("dataset", ".jsonl"), ("review", ".json"), ("report", ".md")):
        if not isinstance(config[name], str):
            raise ValueError("explicit output path strings required")
        path = _safe(config[name])
        if path.suffix != suffix or path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError("regular nonsymlink output with declared suffix required")
        paths[name] = path
    paths["manifest"] = _safe(paths["dataset"].with_suffix(".manifest.json"))
    if paths["manifest"].is_symlink() or (paths["manifest"].exists() and not paths["manifest"].is_file()):
        raise ValueError("regular nonsymlink manifest required")
    exclusions = config["excluded_graph_sources"]
    if not isinstance(exclusions, list) or len(exclusions) != 2:
        raise ValueError("exactly two named pinned old source banks required")
    for expected, entry in zip(("routing_sources_v1", "schedule_sources_v1"), exclusions):
        if not isinstance(entry, dict) or set(entry) != {"name", "path", "sha256"} or entry["name"] != expected:
            raise ValueError("old routing and schedule source banks must be explicitly named in order")
        checksum = entry["sha256"]
        if (not isinstance(checksum, str) or len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum)
                or not isinstance(entry["path"], str)):
            raise ValueError("source-only SHA256 exclusion pins required")
        path = _safe(entry["path"])
        if path.suffix != ".jsonl" or path.is_symlink():
            raise ValueError("nonsymlink old source JSONL banks required")
    resolved = [path.resolve() for path in paths.values()] + [_safe(e["path"]).resolve() for e in exclusions]
    if (len(set(resolved)) != len(resolved)
            or any(a in b.parents or b in a.parents for a, b in permutations(resolved, 2))):
        raise ValueError("distinct nonoverlapping input and output files required")
    return paths


def _shape(source):
    tree = relationships._tree(source)
    assignments = tree.body[:-1]
    if len(assignments) != 8 or [stmt.targets[0].id for stmt in assignments[:4]] != list(prior.VARIABLES):
        raise ValueError("exclusion sources require four canonical roots and four copies")
    for stmt in assignments[:4]:
        value = stmt.value.operand if isinstance(stmt.value, ast.UnaryOp) and isinstance(stmt.value.op, ast.USub) else stmt.value
        if not isinstance(value, ast.Constant) or type(value.value) is not int:
            raise ValueError("exclusion source roots must be integer literals")
    destinations = []; parents = []
    for stmt in assignments[4:]:
        name = stmt.targets[0].id
        if name not in prior.SLOTS or not isinstance(stmt.value, ast.Name) or stmt.value.id not in prior.SLOTS:
            raise ValueError("exclusion sources require actual four-slot copies")
        destination, parent = prior.SLOTS[name], prior.SLOTS[stmt.value.id]
        if destination == parent:
            raise ValueError("distinct-slot copy parents required")
        destinations.append(destination); parents.append(parent)
    if not isinstance(tree.body[-1].value, ast.Name) or tree.body[-1].value.id not in prior.SLOTS:
        raise ValueError("canonical final query required")
    return tuple(destinations), tuple(parents)


def _routing_universe():
    destinations = (0, 1, 2, 3)
    return {_graph(destinations, tuple(parents)) for parents in product(
        *(tuple(slot for slot in range(4) if slot != destination) for destination in destinations))}


def _excluded(config):
    graph_union = set(); reviews = []
    routing = None
    for entry in config["excluded_graph_sources"]:
        path = _safe(entry["path"])
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("bounded regular old source bank required")
        with path.open("rb") as stream:
            payload = stream.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("pinned old source bank SHA256 differs")
        graphs = set(); count = 0
        expected_role = ("discovery_relationship_routing_v1" if entry["name"] == "routing_sources_v1"
                         else prior.ROLE)
        for line in payload.splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if (not isinstance(row, dict) or not isinstance(row.get("canonical_source"), str)
                    or row.get("evaluation_role") != expected_role or row.get("condition") != "neutral"
                    or row.get("split") not in ("train", "development")):
                raise ValueError("discovery-only prior source role and neutral TRAIN/DEV records required")
            graphs.add(_graph(*_shape(row["canonical_source"])))
            count += 1
        if not count:
            raise ValueError("nonempty old source bank required")
        if entry["name"] == "routing_sources_v1":
            routing = graphs
        graph_union.update(graphs)
        reviews.append(dict(**entry, rows=count, canonical_graph_families=len(graphs)))
    old_universe = _routing_universe()
    if not old_universe <= routing:
        raise ValueError("named old routing bank does not cover the declared81-parent routing universe")
    deviation = dict(initial_profile=[1, 1, 1, 1], initial_profile_generated=False,
        initial_profile_counted_as_new=False, fixed_order_parent_patterns=81,
        slot_permutations=24, raw_profile_candidates=1944,
        canonical_profile_families=len(old_universe), missing_from_excluded_routing_bank=0,
        new_canonical_families_available=0, replacement_profile=[2, 2, 0, 0],
        proof="Relabel each permutation's copy destinations in execution order to 0,1,2,3. Every distinct-slot parent tuple is among the old 81 patterns; the canonicalizer also quotients legal commuting orders.",
        decision_before_generation=True)
    return graph_union, reviews, deviation


def _selection(config):
    _config(config)
    excluded, reviews, deviation = _excluded(config)
    selected, search = _select(config["candidate_seed"], excluded)
    return selected, excluded, reviews, deviation, search


@lru_cache(maxsize=240)
def _template(destinations, parents):
    prototype = prior._source((1, 2, 3, 4), destinations, parents, 0)
    prefixes = [relationships.labels_at(prototype, i, prior.SLOTS) for i in range(8)]
    outputs = [relationships.labels_at(prior._source((1, 2, 3, 4), destinations, parents, query),
                                     7, prior.SLOTS, output_visible=True) for query in range(4)]
    return prefixes, outputs


def _make_rows(config, selected):
    result = []
    pool = tuple(value for value in range(-12, 13) if value)
    for profile in PROFILES:
        for index, (graph, destinations, parents) in enumerate(selected[profile]):
            component = "schedule-diversity-graph:" + graph[:24]
            split = "train" if index < TRAIN_FAMILIES_PER_PROFILE else "development"
            for seed in NUMERIC_SEEDS:
                values = tuple(random.Random(digest([ROLE, graph, seed, "numeric"])).sample(pool, 4))
                base = f"{component}:numeric{seed}"
                for rotation in range(4):
                    perm = tuple((slot + rotation) % 4 for slot in range(4))
                    rotated_dest = tuple(perm[slot] for slot in destinations)
                    rotated_parents = tuple(perm[slot] for slot in parents)
                    rotated_values = [0] * 4
                    for slot, value in enumerate(values):
                        rotated_values[perm[slot]] = value
                    prefix_labels, query_labels = _template(rotated_dest, rotated_parents)
                    initial = prior._source(rotated_values, rotated_dest, rotated_parents, 0)
                    trace = execute(initial)["execution_trace"]
                    for lexical in (0, 1):
                        stem = "item" if lexical == 0 else "cell"
                        mapping = {name: f"{stem}_{slot}" for slot, name in enumerate(prior.VARIABLES)}
                        for query in range(4):
                            canonical = prior._source(rotated_values, rotated_dest, rotated_parents, query)
                            surface = rename(canonical, mapping)
                            spans = []; offset = 0
                            for statement, line in enumerate(surface.splitlines()):
                                spans.append(dict(statement=statement, start=offset, end=offset + len(line)))
                                offset += len(line) + 1
                            result.append(dict(schema_version=1, evaluation_role=ROLE,
                                id="schedule-diversity:" + digest([seed, surface])[:24],
                                source=surface, canonical_source=canonical, split=split, condition="neutral",
                                family="diverse_copy_overwrite_schedule", control_kind="targets_prepared_only",
                                base_id=base, paired_group_id=base, component_id=component, cluster_id=component,
                                template_id=component, ssa_graph_canonical_id=component,
                                canonical_graph_sha256=graph, graph_selection_index=index,
                                profile_id="_".join(map(str, profile)), update_count_profile=list(profile),
                                destination_update_counts=[rotated_dest.count(slot) for slot in range(4)],
                                slot_rotation=rotation, numeric_seed=seed, lexical_realization=lexical,
                                rename_map=mapping, variable_slots=prior.SLOTS.copy(), source_form="literal",
                                query_slot=query, query_role=f"v{query}", query_count=1,
                                raw_template_id=f"{component}:rotation{rotation}",
                                destination_schedule=list(rotated_dest), copy_parent_slots=list(rotated_parents),
                                parent_pattern="independent_distinct_slot_choices", statement_spans=spans,
                                expected_answer=trace[-1]["values"][f"v{query}"],
                                targets=dict(prefix_relationships=deepcopy(prefix_labels),
                                    final_query_relationships=deepcopy(query_labels[query]),
                                    canonical_execution_trace=deepcopy(trace))))
    return result


def make_rows(config):
    """Construct only after SHA-pinned exclusions and all profile quotas pass."""
    selected, _, _, _, _ = _selection(config)
    return _make_rows(config, selected)


def _validate(config, rows, selected, excluded, reviews, deviation, search, independent):
    if type(independent) is not bool or not isinstance(rows, list) or rows != _make_rows(config, selected):
        raise ValueError("complete exact declared diversity source/target factorial required")
    if len(rows) != N_ROWS or len({row["id"] for row in rows}) != N_ROWS:
        raise ValueError("unique fixed5760-case discovery bank required")
    fingerprints = {name: defaultdict(set) for name in ("surface_source", "canonical_ast", "alpha_structure", "canonical_graph")}
    groups = defaultdict(set); profile_groups = defaultdict(set); versions = defaultdict(set)
    version_rows = Counter(); all_programs = set(); prefixes = defaultdict(set)
    checked_canonical = set(); checked_surface = set(); prefix_labels = {}; prefix_checks = 0
    for row in rows:
        split = row["split"]; component = row["component_id"]; graph = row["canonical_graph_sha256"]
        if graph in excluded or _graph(*_shape(row["canonical_source"])) != graph:
            raise ValueError("new source overlaps excluded canonical graph or its graph identity differs")
        groups[split].add(component); profile_groups[row["profile_id"], split].add(component)
        oracle = execute(row["canonical_source"])
        if oracle["execution_trace"] != row["targets"]["canonical_execution_trace"] or oracle["expected_answer"] != row["expected_answer"]:
            raise ValueError("actual canonical trace/answer differs")
        body = "\n".join(row["canonical_source"].splitlines()[:8])
        if body not in checked_canonical:
            prior._check_oracle_labels(row, oracle)
            checked_canonical.add(body)
            prefix_checks += 8
        elif row["targets"]["final_query_relationships"] != relationships.labels_at(
                row["canonical_source"], 7, prior.SLOTS, output_visible=True):
            raise ValueError("actual final query relationships differ")
        final = row["targets"]["prefix_relationships"][-1]
        actual_canonical, _ = prior._canonical_graph(final)
        if digest(actual_canonical) != graph:
            raise ValueError("actual generic SSA labels differ from graph family")
        surface_body = "\n".join(row["source"].splitlines()[:8])
        surface_slots = {row["rename_map"][name]: slot for name, slot in prior.SLOTS.items()}
        if surface_body not in checked_surface:
            for checkpoint, labels in enumerate(row["targets"]["prefix_relationships"]):
                if relationships.labels_at(row["source"], checkpoint, surface_slots) != labels:
                    raise ValueError("actual renamed prefix labels differ")
                prefix = "\n".join(row["canonical_source"].splitlines()[:checkpoint+1])
                key = (checkpoint, prefix)
                proof = digest(labels)
                if key in prefix_labels and prefix_labels[key] != proof:
                    raise ValueError("identical visible prefixes have inconsistent targets")
                prefix_labels[key] = proof; prefixes[checkpoint, prefix].add(split)
                prefix_checks += 1
            checked_surface.add(surface_body)
        if relationships.labels_at(row["source"], 7, surface_slots, output_visible=True) != row["targets"]["final_query_relationships"]:
            raise ValueError("actual renamed query ancestry differs")
        for node in final["version_nodes"]:
            if node["status"] == "current":
                versions[split, node["slot"], node["version"]].add(component)
                version_rows[split, node["slot"], node["version"]] += 1
        for name, key in (("surface_source", row["source"]),
                ("canonical_ast", ast.dump(ast.parse(row["canonical_source"]))),
                ("alpha_structure", alpha_skeleton(row["canonical_source"])), ("canonical_graph", graph)):
            fingerprints[name][key].add(split)
        all_programs.update((row["canonical_source"], row["source"]))
    overlaps = {name: sum(len(splits) > 1 for splits in values.values()) for name, values in fingerprints.items()}
    if (any(overlaps.values()) or len(groups["train"]) != 45 or len(groups["development"]) != 15
            or groups["train"] & groups["development"]):
        raise ValueError("graph/source/AST/alpha split leakage or group coverage differs")
    version_support = {}
    for split in ("train", "development"):
        version_support[split] = {}
        for slot in range(4):
            classes = {str(version): dict(rows=version_rows[split, slot, version],
                graph_groups=len(versions[split, slot, version])) for version in range(1, 5)}
            if any(c["graph_groups"] < (3 if split == "train" else 1) for c in classes.values()):
                raise ValueError("prospective slot-complete version class/group support not met")
            version_support[split][str(slot)] = classes
    return dict(rows=len(rows), split_rows=dict(Counter(row["split"] for row in rows)),
        canonical_graph_families=60, split_canonical_graph_units={s: len(v) for s, v in groups.items()},
        count_profiles=[list(profile) for profile in PROFILES],
        profile_split_graph_units={"_".join(map(str, p)): {s: len(profile_groups["_".join(map(str, p)), s])
            for s in ("train", "development")} for p in PROFILES},
        candidate_search=search, design_deviation=deviation, excluded_graph_sources=reviews,
        canonical_graph_overlap_with_named_banks=0, cross_split_overlap=overlaps,
        slot_rotations=4, numeric_seeds=list(NUMERIC_SEEDS), lexical_realizations=2, query_slots=list(range(4)),
        maximum_assignment_version=4, current_version_class_support=version_support,
        slot_complete_version_domain=True, fully_class_balanced=False,
        train_minimum_current_version_class_graph_groups=min(len(versions["train", slot, version])
            for slot in range(4) for version in range(1, 5)),
        prefix_label_checks=prefix_checks, distinct_canonical_bodies=len(checked_canonical),
        distinct_surface_bodies=len(checked_surface),
        cross_split_visible_prefix_overlap_by_statement={str(i): sum(len(v) > 1 for (j, _), v in prefixes.items() if j == i)
            for i in range(8)}, prefix_future_information_excluded=True,
        independent_python_programs=prior._python_validate(all_programs) if independent else 0,
        independent_python_passed=independent)


def validate_rows(config, rows, independent=False):
    selected, excluded, reviews, deviation, search = _selection(config)
    return _validate(config, rows, selected, excluded, reviews, deviation, search, independent)


def _report(config, review):
    lines = ["# Slot-complete schedule diversity source preparation", "",
        f"Prepared {review['rows']:,} source rows: 4,320 TRAIN and 1,440 DEV, in 45/15 disjoint canonical SSA graph families.", "",
        "Selected 20 NEW families for each of profiles 2,1,1,0 / 3,1,0,0 / 2,2,0,0 from 18,468 finite candidates. "
        "Each family has four cyclic slot rotations, three numeric seeds, two neutral lexical forms and four final queries. "
        "All relatives remain in one graph split. Novelty is relative only to the two named SHA-pinned exclusion banks.", "",
        "The initially proposed 1,1,1,1 profile was not generated or counted: relabeling its copy destinations to 0,1,2,3 maps every parent pattern "
        "into the old 81-parent routing universe. The replacement 2,2,0,0 profile was fixed before this source generation.", "",
        f"Actual versions reach 4. Every slot contains version classes 1..4 in TRAIN and DEV; minimum TRAIN support is {review['train_minimum_current_version_class_graph_groups']} graph families. "
        "Rotations make the domain slot-complete, not fully class-balanced. Full class/row/group inventories remain in the machine review.", "",
        f"All full-source/AST/alpha/graph cross-split overlaps and canonical-graph overlaps with the named banks are zero. "
        f"Independently checked {review['independent_python_programs']:,} ordinary-Python full traces. "
        "Visible short-prefix overlap is separately reported; identical prefixes have identical labels and no future-query labels.", "",
        "This is source/oracle preparation only. Existing frozen 2016-case heads are incompatible; no learned relationship decoding or model query was performed.", "",
        f"Dataset SHA256: `{review['dataset_sha256']}`. Review: `{config['review']}`.", "", *["- " + item for item in LIMITATIONS], ""]
    return "\n".join(lines)


def build(config):
    """Independently validate and immutably publish source/oracle preparation."""
    paths = _config(config)
    selected, excluded, reviews, deviation, search = _selection(config)
    rows = _make_rows(config, selected)
    result = _validate(config, rows, selected, excluded, reviews, deviation, search, True)
    payload = "".join(json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows).encode()
    if len(payload) > MAX_BYTES:
        raise ValueError("bounded diversity source bank exceeded")
    result.update(status="passed", evaluation_role=ROLE, config_hash=digest(config), config=config,
        dataset=str(paths["dataset"]), dataset_sha256=hashlib.sha256(payload).hexdigest(), source=code_identity(),
        model_queries=0, new_model_queries=0, new_fits=0, targets_prepared_only=True,
        learned_readout_compatible=False, model_or_tokenizer_loaded=False, activation_arrays_read=False,
        graph_decoding_performed=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    report = _report(config, result).encode()
    result["report"] = dict(path=str(paths["report"]), sha256=hashlib.sha256(report).hexdigest())
    manifest = dict(schema_version=1, status="complete", evaluation_role=ROLE, role=ROLE,
        sha256=result["dataset_sha256"], rows=len(rows), split_rows=result["split_rows"],
        generation_config_hash=digest(config), generation_config=config, source=result["source"],
        review=str(paths["review"]), independent_python_passed=True, model_queries=0, new_model_queries=0,
        targets_prepared_only=True, learned_readout_compatible=False, generated_holdouts_opened=False,
        canonical_graph_families=60, split_canonical_graph_units=result["split_canonical_graph_units"],
        maximum_assignment_version=4, count_profiles=result["count_profiles"],
        slot_complete_version_domain=True, fully_class_balanced=False,
        canonical_graph_overlap_with_named_banks=0, cross_split_overlap=result["cross_split_overlap"],
        excluded_graph_sources=reviews, design_deviation=deviation)
    outputs = [(paths["dataset"], payload), (paths["manifest"], _json_bytes(manifest)),
               (paths["review"], _json_bytes(result)), (paths["report"], report)]
    for path, data in outputs:
        if path.exists() and path.read_bytes() != data:
            raise ValueError("immutable diversity artifact already differs: " + str(path))
    for path, data in outputs:
        _publish(path, data)
    from .experiment_log import note_artifact
    note_artifact(paths["review"].resolve())
    return result
