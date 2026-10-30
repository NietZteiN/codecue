"""Prefix-visible targets for the varied copy/overwrite schedule discovery bank.

Statement IDs 0..7 identify definitions in execution order, rather than assuming
that the last four statements overwrite slots 0,1,2,3.  The existing generic
``relationships.labels_at`` resolves every actual slot/version and dependency.
All information in this module is a TARGET, never an input representation.

The selectivity control is a prefix-keyed random task.  It ties lexical and
pre-query relatives, but does not preserve real label marginals or assert a
lawful joint SSA graph.  It is not a shuffled-program generalization test.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, replace
import hashlib
import json

import numpy as np

from . import relationship_schedule_programs as programs, relationships
from .datasets import digest
from .programs import rename

SITES = (3, 7, 8)
SITE_NAMES = {3: "statement:3", 7: "statement:7", 8: "pre_answer"}
NODE_IDS = tuple(range(8))
VERSION_CLASSES = (1, 2, 3, 4)
CONTROL_KIND = "canonical_visible_prefix_keyed_random_task_v1"
MAX_ROWS = programs.N_ROWS


def _columns():
    result = []
    def add(kind, family, name, **extra):
        result.append(dict(index=len(result), kind=kind, family=family,
                           name=name, head=extra.pop("head", name), **extra))
    for family in ("direct", "ancestor"):
        for source in NODE_IDS:
            for consumer in NODE_IDS:
                add("boolean", family, f"{family}/statement{source}/statement{consumer}",
                    source_node=source, consumer_node=consumer)
    for family in ("current", "obsolete", "output_ancestor"):
        for node in NODE_IDS:
            add("boolean", family, f"{family}/statement{node}", source_node=node)
    for family, candidates in (("current_definition", NODE_IDS),
                               ("current_version", VERSION_CLASSES),
                               ("copy_parent", NODE_IDS)):
        for slot_or_step in range(4):
            head = f"{family}/{slot_or_step}"
            for candidate in candidates:
                add("categorical", family, f"{head}/{candidate}", head=head,
                    candidate=candidate, **({"copy_step": slot_or_step,
                    "consumer_node": 4 + slot_or_step} if family == "copy_parent"
                    else {"slot": slot_or_step}))
    return tuple(result)


COLUMNS = _columns()
N_COLUMNS = len(COLUMNS)
HEADS = tuple(dict(name=head, family=next(c["family"] for c in COLUMNS if c["head"] == head),
                   indices=tuple(c["index"] for c in COLUMNS if c["head"] == head),
                   candidates=tuple(c["candidate"] for c in COLUMNS if c["head"] == head))
              for head in dict.fromkeys(c["head"] for c in COLUMNS if c["kind"] == "categorical"))


def _readonly(value, dtype=None):
    array = np.asarray(value, dtype=dtype)
    return np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)


@dataclass(frozen=True)
class TargetBundle:
    y: np.ndarray
    mask: np.ndarray
    columns: tuple[dict, ...]
    case_ids: tuple[str, ...]
    group_ids: tuple[str, ...]
    splits: tuple[str, ...]
    site: int
    descriptive: dict

    @property
    def site_name(self):
        return SITE_NAMES[self.site]


def _site(site):
    if isinstance(site, str):
        site = next((i for i, name in SITE_NAMES.items() if site == name), None)
    if type(site) is not int or site not in SITES:
        raise ValueError("schedule sites must be 3, 7, 8 or their declared exact names")
    return site


def _records(rows):
    """Validate source identities and grouping without reading stored targets."""
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("bounded nonempty schedule source rows required")
    templates = {(t["schedule_id"], t["parent_pattern"]): t for t in programs._templates()}
    result = []; seen = set(); split_fingerprints = defaultdict(set)
    for row in rows:
        if (not isinstance(row, dict) or row.get("evaluation_role") != programs.ROLE
                or row.get("condition") != "neutral" or row.get("split") not in ("train", "development")
                or row.get("variable_slots") != programs.SLOTS):
            raise ValueError("declared neutral schedule rows and canonical slots required")
        case = row.get("id"); group = row.get("component_id")
        if not isinstance(case, str) or not case or case in seen:
            raise ValueError("unique nonempty schedule case IDs required")
        seen.add(case)
        key = (row.get("schedule_id"), row.get("parent_pattern"))
        if any(not isinstance(value, str) for value in key) or key not in templates:
            raise ValueError("declared schedule and parent pattern required")
        template = templates[key]
        if (group != template["component_id"] or row["split"] != template["split"]
                or any(row.get(name) != group for name in ("cluster_id", "template_id", "ssa_graph_canonical_id"))
                or row.get("ordered_schedule_canonical_id") != template["ordered_schedule_canonical_id"]
                or row.get("destination_schedule") != list(template["destinations"])
                or row.get("copy_parent_slots") != list(template["parents"])
                or row.get("schedule_kind") != template["schedule_kind"]
                or row.get("raw_template_id") != key[0] + ":" + key[1]):
            raise ValueError("actual schedule family/split metadata differs")
        seed = row.get("numeric_seed"); lexical = row.get("lexical_realization")
        query = row.get("query_slot")
        if (type(seed) is not int or not 0 <= seed < 2**63 or type(lexical) is not int or lexical not in (0, 1)
                or type(query) is not int or query not in range(4) or row.get("query_role") != f"v{query}"
                or row.get("query_count") != 1 or row.get("source_form") != "literal"
                or row.get("base_id") != f"{group}:numeric{seed}"
                or row.get("paired_group_id") != row["base_id"]):
            raise ValueError("numeric, lexical, query and grouping metadata differs")
        tree = relationships._tree(row.get("canonical_source"))
        surface = relationships._tree(row.get("source"))
        assignments = tree.body[:-1]
        if len(assignments) != 8:
            raise ValueError("eight schedule assignments required")
        if [stmt.targets[0].id for stmt in assignments] != [*programs.VARIABLES,
                *(f"v{slot}" for slot in template["destinations"])]:
            raise ValueError("actual assignment destinations differ from schedule")
        for stmt in assignments[:4]:
            expr = stmt.value
            if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, (ast.UAdd, ast.USub)):
                expr = expr.operand
            if not isinstance(expr, ast.Constant) or type(expr.value) is not int:
                raise ValueError("four integer literal roots required")
        if ([stmt.value.id if isinstance(stmt.value, ast.Name) else None for stmt in assignments[4:]]
                != [f"v{slot}" for slot in template["parents"]]
                or not isinstance(tree.body[-1].value, ast.Name)
                or tree.body[-1].value.id != f"v{query}"):
            raise ValueError("actual copy sources or final query differ")
        stem = "item" if lexical == 0 else "cell"
        mapping = {name: f"{stem}_{i}" for i, name in enumerate(programs.VARIABLES)}
        if (row.get("rename_map") != mapping
                or ast.dump(relationships._tree(rename(row["canonical_source"], mapping))) != ast.dump(surface)):
            raise ValueError("canonical/surface lexical renaming differs")
        if case != "relationship-schedule:" + digest([seed, row["source"]])[:24]:
            raise ValueError("case ID does not identify the actual numeric/surface source")
        # Explicitly reject cross-split source/group relatives even for subsets.
        for name, fingerprint in (("group", group), ("canonical", ast.dump(tree)),
                                  ("source", ast.dump(surface))):
            split_fingerprints[name, fingerprint].add(row["split"])
        result.append((row, tree, {mapping[name]: slot for name, slot in programs.SLOTS.items()}))
    if any(len(splits) != 1 for splits in split_fingerprints.values()):
        raise ValueError("schedule source/group relatives cross TRAIN/DEV")
    return result


def _prefix_key(tree, checkpoint, output=False):
    visible = list(tree.body[:checkpoint+1])
    if output:
        visible.append(tree.body[-1])
    return ast.dump(ast.Module(body=visible, type_ignores=[]), include_attributes=False)


def targets(rows, site) -> TargetBundle:
    """Resolve actual visible SSA labels into a fixed 232-column target schema."""
    site = _site(site); checkpoint = min(site, 7); records = _records(rows)
    y = np.zeros((len(records), N_COLUMNS), dtype=np.float64)
    mask = np.zeros_like(y, dtype=bool)
    maps = []; prefixes = []; output_prefixes = []
    for i, (row, tree, surface_slots) in enumerate(records):
        graph = relationships.labels_at(row["canonical_source"], checkpoint, programs.SLOTS,
                                        output_visible=site == 8)
        if graph != relationships.labels_at(row["source"], checkpoint, surface_slots, output_visible=site == 8):
            raise ValueError("canonical/surface actual SSA labels differ")
        ordered = sorted(graph["version_nodes"], key=lambda node: node["statement"])
        if [node["statement"] for node in ordered] != list(range(checkpoint+1)):
            raise ValueError("actual prefix definition inventory differs")
        node_index = {node["id"]: node["statement"] for node in ordered}
        by_statement = {node["statement"]: node for node in ordered}
        current = {node["slot"]: node for node in ordered if node["status"] == "current"}
        direct = {(node_index[a], node_index[b]) for a, b in graph["direct_def_use_edges"]}
        ancestor = {(node_index[a], node_index[b]) for a, b in graph["strict_ancestor_edges"]}
        parents = {consumer: [source for source, child in direct if child == consumer]
                   for consumer in range(4, checkpoint+1)}
        if any(len(value) != 1 for value in parents.values()):
            raise ValueError("each visible schedule copy must have exactly one actual parent definition")
        output = ({node_index[node] for node in graph["output"]["structural_ancestors"]}
                  if site == 8 else set())
        for column in COLUMNS:
            j = column["index"]; family = column["family"]
            if family in ("direct", "ancestor"):
                source, consumer = column["source_node"], column["consumer_node"]
                valid = 4 <= consumer <= checkpoint and source < consumer
                value = (source, consumer) in (direct if family == "direct" else ancestor)
            elif family in ("current", "obsolete"):
                node = column["source_node"]; valid = node <= checkpoint
                value = valid and by_statement[node]["status"] == family
            elif family == "output_ancestor":
                valid = site == 8; value = column["source_node"] in output
            elif family == "current_definition":
                valid = column["candidate"] <= checkpoint
                value = current[column["slot"]]["statement"] == column["candidate"]
            elif family == "current_version":
                # Before any copy, versions 2..4 do not exist. At final prefixes
                # all four schema choices remain, including absent TRAIN classes.
                valid = checkpoint == 7 or column["candidate"] == 1
                value = current[column["slot"]]["version"] == column["candidate"]
            else:
                consumer = column["consumer_node"]
                valid = consumer <= checkpoint and column["candidate"] < consumer
                value = valid and parents[consumer][0] == column["candidate"]
            mask[i, j] = valid
            y[i, j] = bool(valid and value)
        maps.append([dict(statement=node["statement"], id=node["id"], slot=node["slot"],
                          version=node["version"], status=node["status"]) for node in ordered])
        prefixes.append(_prefix_key(tree, checkpoint))
        output_prefixes.append(_prefix_key(tree, checkpoint, output=site == 8))
    descriptive = dict(schema_version=1, statement_ids=list(NODE_IDS),
        targets_only=True, actual_slot_version_maps_are_targets=True,
        node_id_semantics="zero-based assignment statement, resolved to actual v@N by labels_at",
        direct_edge_semantics="source statement to copy-consumer statement",
        output_ancestor_semantics="syntactic dependencies, including the directly queried definition",
        version_resolution_is_a_target=True, learned_version_resolution_performed=False,
        version_classes=list(VERSION_CLASSES),
        version_map_by_case=maps, canonical_visible_prefixes=prefixes,
        canonical_output_visible_prefixes=output_prefixes,
        future_or_impossible_masked=True, masks_are_targets_not_features=True,
        categorical_heads=[dict(head) for head in HEADS],
        query_visible=site == 8, control=False)
    return TargetBundle(_readonly(y), _readonly(mask), COLUMNS,
        tuple(row["id"] for row, _, _ in records), tuple(row["component_id"] for row, _, _ in records),
        tuple(row["split"] for row, _, _ in records), site, descriptive)


def subset(bundle, indices):
    values = np.asarray(indices)
    if values.dtype.kind == "b" and values.shape == (len(bundle.case_ids),):
        values = np.flatnonzero(values)
    if (values.ndim != 1 or values.dtype.kind not in "iu" or not len(values)
            or np.any(values < 0) or np.any(values >= len(bundle.case_ids))
            or len(set(values.tolist())) != len(values)):
        raise ValueError("unique bounded nonempty row indices required")
    values = values.astype(np.int64)
    descriptive = dict(bundle.descriptive)
    for name in ("version_map_by_case", "canonical_visible_prefixes", "canonical_output_visible_prefixes"):
        descriptive[name] = [bundle.descriptive[name][i] for i in values]
    return replace(bundle, y=_readonly(bundle.y[values]), mask=_readonly(bundle.mask[values]),
        case_ids=tuple(bundle.case_ids[i] for i in values), group_ids=tuple(bundle.group_ids[i] for i in values),
        splits=tuple(bundle.splits[i] for i in values), descriptive=descriptive)


def _draw(seed, prefix, label, count):
    payload = json.dumps([CONTROL_KIND, seed, prefix, label], separators=(",", ":"), ensure_ascii=True).encode()
    # Rejection avoids modulo bias even for non-power-of-two parent domains.
    limit = 2**256 - 2**256 % count
    for attempt in range(16):
        value = int.from_bytes(hashlib.sha256(payload + str(attempt).encode()).digest(), "big")
        if value < limit:
            return value % count
    raise RuntimeError("bounded keyed control draw failed")


def _marginals(bundle):
    result = {}
    groups = np.asarray(bundle.group_ids)
    for split in ("train", "development"):
        split_rows = np.asarray([value == split for value in bundle.splits])
        cells = []
        for column in COLUMNS:
            j = column["index"]; valid = split_rows & bundle.mask[:, j]
            positive = valid & (bundle.y[:, j] == 1)
            negative = valid & (bundle.y[:, j] == 0)
            cells.append(dict(index=j, defined_rows=int(valid.sum()), positive_rows=int(positive.sum()),
                negative_rows=int(negative.sum()), positive_groups=len(set(groups[positive])),
                negative_groups=len(set(groups[negative]))))
        result[split] = cells
    return result


def control_targets(rows, site, seed) -> TargetBundle:
    """Build a deterministic prefix-consistent sham task, not donor targets.

    No full-source/group/split/site key enters a pre-query draw. Identical visible
    canonical prefixes therefore receive identical labels, including across
    lexical/query relatives and final-assignment/pre-answer graph tasks.
    """
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("bounded nonnegative integer control seed required")
    real = targets(rows, site); y = np.zeros_like(real.y)
    for i, prefix in enumerate(real.descriptive["canonical_visible_prefixes"]):
        for column in COLUMNS:
            j = column["index"]
            if column["kind"] != "boolean" or not real.mask[i, j]:
                continue
            family = column["family"]
            key = real.descriptive["canonical_output_visible_prefixes"][i] if family == "output_ancestor" else prefix
            label = f"current/statement{column['source_node']}" if family == "obsolete" else column["name"]
            value = _draw(seed, key, label, 2)
            y[i, j] = 1-value if family == "obsolete" else value
        for head in HEADS:
            valid = [j for j in head["indices"] if real.mask[i, j]]
            if valid:
                y[i, valid[_draw(seed, prefix, head["name"], len(valid))]] = 1
    descriptive = dict(real.descriptive)
    descriptive.update(control=True, control_kind=CONTROL_KIND, control_seed=seed,
        control_semantics="Independent keyed boolean tasks and one-hot categorical heads; current/obsolete complementary",
        canonical_prefix_ties_lexical_and_prequery_variants=True,
        query_used_only_for_output_ancestor=True, group_split_site_not_in_random_key=True,
        lawful_joint_ssa_graph=False, marginals_preserved=False,
        control_class_support_may_differ=True)
    result = replace(real, y=_readonly(y), descriptive=descriptive)
    descriptive["real_marginals"] = _marginals(real)
    descriptive["control_marginals"] = _marginals(result)
    descriptive["marginals_scope"] = dict(case_count=len(real.case_ids),
                                          population="complete input bank before any subset")
    return result


def training_support(bundle, min_class_groups=3):
    """TRAIN-only eligibility plus complete TRAIN/DEV class inventories.

    Head eligibility requires at least two observed TRAIN classes and support in
    the declared number of graph groups for every observed TRAIN class. Absent
    domain classes are explicit; they are never removed from the evaluated head.
    DEV-only classes are descriptive and do not alter TRAIN-derived eligibility.
    """
    if type(min_class_groups) is not int or min_class_groups < 1:
        raise ValueError("positive integer minimum class-group support required")
    groups = np.asarray(bundle.group_ids)
    train = np.asarray([value == "train" for value in bundle.splits])
    dev = np.asarray([value == "development" for value in bundle.splits])
    if not np.any(train):
        raise ValueError("TRAIN source rows required for support eligibility")
    cells = []; eligible = []
    for column in COLUMNS:
        j = column["index"]; valid = train & bundle.mask[:, j]
        positive = valid & (bundle.y[:, j] == 1); negative = valid & (bundle.y[:, j] == 0)
        pos_groups, neg_groups = len(set(groups[positive])), len(set(groups[negative]))
        observed = int(np.any(positive)) + int(np.any(negative))
        qualified = column["kind"] == "boolean" and min(pos_groups, neg_groups) >= min_class_groups
        if qualified:
            eligible.append(j)
        cells.append(dict(index=j, name=column["name"], family=column["family"], kind=column["kind"],
            defined_rows=int(valid.sum()), positive_rows=int(positive.sum()), negative_rows=int(negative.sum()),
            positive_groups=pos_groups, negative_groups=neg_groups, constant=observed == 1,
            missing=observed == 0, eligible_boolean=qualified))
    heads = []
    for head in HEADS:
        classes = []
        for candidate, j in zip(head["candidates"], head["indices"]):
            train_positive = train & bundle.mask[:, j] & (bundle.y[:, j] == 1)
            dev_positive = dev & bundle.mask[:, j] & (bundle.y[:, j] == 1)
            n_groups = len(set(groups[train_positive]))
            classes.append(dict(candidate=candidate, train_rows=int(train_positive.sum()),
                train_groups=n_groups, development_rows=int(dev_positive.sum()),
                development_groups=len(set(groups[dev_positive])),
                supported=n_groups >= min_class_groups, absent_train=not np.any(train_positive),
                development_only=not np.any(train_positive) and bool(np.any(dev_positive))))
        observed = [c for c in classes if c["train_rows"]]
        eligible_head = len(observed) >= 2 and all(c["supported"] for c in observed)
        heads.append(dict(head=head["name"], family=head["family"], candidates=list(head["candidates"]),
            classes=classes, observed_train_classes=[c["candidate"] for c in observed],
            absent_train_classes=[c["candidate"] for c in classes if c["absent_train"]],
            unsupported_observed_train_classes=[c["candidate"] for c in observed if not c["supported"]],
            development_only_classes=[c["candidate"] for c in classes if c["development_only"]],
            constant=len(observed) == 1, missing=not observed, eligible_categorical=eligible_head,
            all_domain_classes_supported=all(c["supported"] for c in classes),
            evaluated_choices_removed=False))
    return dict(eligibility_split="train", minimum_class_groups=min_class_groups,
        structural_groups=len(set(groups[train])),
        eligibility_rule="Boolean: both classes in >=threshold TRAIN groups; categorical: >=2 observed TRAIN classes and every observed TRAIN class in >=threshold groups",
        absent_domain_choices_retained=True, development_labels_used_for_eligibility=False,
        eligible_boolean_indices=eligible, columns=cells, categorical_heads=heads)
