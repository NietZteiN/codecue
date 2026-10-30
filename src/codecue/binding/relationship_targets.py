"""Targets and metrics for the fixed four-slot, eight-assignment discovery bank.

This module reads source/identity fields only. Oracle values, graphs, versions and
relations returned here are TARGETS, never representation features. Sites 0..7
observe that assignment prefix; site 8 observes the same final assignments and
explicitly visible output ancestry. The latter supplies no extra numeric labels.

All 364 columns have fixed identities. Undefined/future/impossible columns have
mask=False and zero placeholders in y, not negative labels. Direct-edge candidates
are the three versions current when each copy executes. Ancestor candidates are
the transitive closure of that fixed possible-edge scaffold. Parent heads use
three independent ridge outputs followed by argmax; the four choices reconstruct
one of 81 lawful full graphs. Versions/status/succession are known schedule priors,
not learned version resolution in this diagnostic.

Binary ridge scores are thresholded at >=0.5, not interpreted as probabilities.
Independent value-head outputs are clipped to [-64,64] then rounded with np.rint
(ties to even); derived relations use those predictions, never oracle values.
That scalar route is secondary. The primary value-derived comparator uses four
32-class value heads with the fixed signed nonzero domain [-16..-1,1..16], then
argmax and ordinary arithmetic. Those complete pipelines are not parameter matched.
Boolean eligibility uses TRAIN class support only. Family-macro balanced accuracy
is undefined if any fixed eligible evaluation cell lacks either class. Conditional
group bootstrap and averaging correctness over weight seeds belong to the caller.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass, replace
from itertools import permutations

import numpy as np
from sklearn.metrics import average_precision_score

from . import algebraic_relationships as algebraic, relationships as structural
from .programs import rename

SITES = tuple(f"statement:{i}" for i in range(8)) + ("pre_answer",)
NODE_IDS = tuple(f"v{i}@1" for i in range(4)) + tuple(f"v{i}@2" for i in range(4))
NODE_INDEX = {name: i for i, name in enumerate(NODE_IDS)}
ALGEBRAIC_FAMILIES = ("equal", "less_than", "sum_equals_third", "difference_equals_third")
PARENT_CANDIDATES = tuple(tuple(j for j in range(4) if j != i) for i in range(4))
COHERENT_SHUFFLE_OFFSET = 100_000
COHERENT_SHUFFLE_QUALIFIED_SITES = (3, 7, 8)
MAX_ROWS = 1944
VALUE_CLASSES = tuple(range(-16, 0)) + tuple(range(1, 17))


def _columns():
    columns = []
    def add(kind, family, slots, name, **extra):
        columns.append(dict(index=len(columns), name=name, kind=kind, family=family,
                            slots=list(slots), head=extra.pop("head", name), **extra))
    for slot in range(4): add("value", "value", [slot], f"value/v{slot}")
    for left, right in permutations(range(4), 2):
        for family in ("equal", "less_than", "difference"):
            add("difference" if family == "difference" else "boolean", family,
                [left, right], f"{family}/v{left}/v{right}")
    for first, second, third in permutations(range(4), 3):
        for family in ("sum_equals_third", "difference_equals_third"):
            add("boolean", family, [first, second, third], f"{family}/v{first}/v{second}/v{third}")
    for family in ("direct", "ancestor"):
        for parent in NODE_IDS:
            for consumer in NODE_IDS:
                add("boolean", family, [], f"{family}/{parent}/{consumer}",
                    source_node=parent, consumer_node=consumer)
    for destination, candidates in enumerate(PARENT_CANDIDATES):
        for candidate in candidates:
            add("parent", "parent", [destination, candidate], f"parent/v{destination}/v{candidate}",
                head=f"parent/v{destination}", destination=destination, candidate=candidate)
    for node in NODE_IDS:
        add("boolean", "output_ancestor", [], f"output_ancestor/{node}", source_node=node)
    # Append to preserve the original 236 target indices.
    for slot in range(4):
        for class_index, candidate in enumerate(VALUE_CLASSES):
            add("value_class", "value_categorical", [slot], f"value_categorical/v{slot}/{candidate}",
                head=f"value_categorical/v{slot}", candidate=candidate, class_index=class_index)
    return tuple(columns)


COLUMNS = _columns()
N_COLUMNS = len(COLUMNS)


def _closure(direct):
    result = np.array(direct, dtype=bool, copy=True)
    for middle in range(8):
        result |= result[..., :, middle, None] & result[..., None, middle, :]
    return result


def _parent_node(destination, candidate):
    return candidate + (4 if candidate < destination else 0)


POSSIBLE_DIRECT = np.zeros((8, 8), dtype=bool)
for _destination, _candidates in enumerate(PARENT_CANDIDATES):
    for _candidate in _candidates:
        POSSIBLE_DIRECT[_parent_node(_destination, _candidate), 4 + _destination] = True
POSSIBLE_ANCESTOR = _closure(POSSIBLE_DIRECT)
POSSIBLE_DIRECT.setflags(write=False)
POSSIBLE_ANCESTOR.setflags(write=False)


def _readonly(value, dtype=None):
    array = np.asarray(value, dtype=dtype)
    return np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)


@dataclass(frozen=True)
class TargetBundle:
    y: np.ndarray
    mask: np.ndarray
    columns: tuple[dict, ...]
    numeric_truth: np.ndarray
    numeric_mask: np.ndarray
    case_ids: tuple[str, ...]
    group_ids: tuple[str, ...]
    splits: tuple[str, ...]
    site: int
    parent_truth: np.ndarray
    parent_mask: np.ndarray
    label_case_ids: tuple[str, ...]
    descriptive: dict

    @property
    def site_name(self):
        return SITES[self.site]


def _site(site):
    if isinstance(site, str) and site in SITES: return SITES.index(site)
    if type(site) is not int or not 0 <= site <= 8:
        raise ValueError("site must be an integer 0..8 or an exact declared site name")
    return site


def _records(rows):
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("bounded nonempty source rows required")
    result = []; seen = set(); group_splits = defaultdict(set)
    for row in rows:
        if not isinstance(row, dict) or row.get("split") not in ("train", "development"):
            raise ValueError("train/development source rows required")
        case = row.get("id"); group = row.get("cluster_id", row.get("component_id", row.get("template_id")))
        if not isinstance(case, str) or not case or case in seen or not isinstance(group, str) or not group:
            raise ValueError("unique case IDs and explicit structural groups required")
        seen.add(case); group_splits[group].add(row["split"])
        tree = structural._tree(row.get("canonical_source"))
        surface = structural._tree(row.get("source"))
        slots = structural._slots(tree.body[:-1], row.get("variable_slots"))
        mapping = row.get("rename_map")
        if not isinstance(mapping, dict): raise ValueError("explicit canonical-to-surface rename map required")
        rendered = structural._tree(rename(row["canonical_source"], mapping))
        if ast.dump(rendered) != ast.dump(surface): raise ValueError("canonical/surface sources differ")
        assignments = tree.body[:-1]
        if (len(assignments) != 8 or len(slots) != 4 or set(slots.values()) != set(range(4))
                or [slots[stmt.targets[0].id] for stmt in assignments] != [0, 1, 2, 3]*2
                or not isinstance(tree.body[-1].value, ast.Name)
                or slots[tree.body[-1].value.id] != 0):
            raise ValueError("fixed four-root/four-copy/v0-query scaffold required")
        for index, stmt in enumerate(assignments):
            if index < 4:
                expr = stmt.value
                if isinstance(expr, ast.UnaryOp): expr = expr.operand
                if not isinstance(expr, ast.Constant): raise ValueError("literal root assignments required")
            elif not isinstance(stmt.value, ast.Name) or slots[stmt.value.id] == index-4:
                raise ValueError("three-way distinct-slot copy assignments required")
        result.append((row, tree, slots, {mapping[name]: slot for name, slot in slots.items()}, case, group))
    if any(len(value) != 1 for value in group_splits.values()):
        raise ValueError("structural groups cross training/development splits")
    return result


def targets(rows, site) -> TargetBundle:
    """Build fixed-width targets after validating all source metadata/scaffolds."""
    site = _site(site); checkpoint = min(site, 7); records = _records(rows)
    n = len(records); y = np.zeros((n, N_COLUMNS)); mask = np.zeros_like(y, dtype=bool)
    numeric = np.full((n, 4), np.nan); numeric_mask = np.zeros((n, 4), dtype=bool)
    parent_truth = np.full((n, 4), -1, dtype=np.int64); parent_mask = np.zeros((n, 4), dtype=bool)
    last_graph = None
    for i, (row, _, slots, surface_slots, _, _) in enumerate(records):
        graph = structural.labels_at(row["canonical_source"], checkpoint, slots, output_visible=site == 8)
        if graph != structural.labels_at(row["source"], checkpoint, surface_slots, output_visible=site == 8):
            raise ValueError("canonical/surface structural targets differ")
        numbers = algebraic.labels_at(row["canonical_source"], checkpoint, slots)
        if numbers != algebraic.labels_at(row["source"], checkpoint, surface_slots):
            raise ValueError("canonical/surface numeric targets differ")
        current = {item["slot"]: item for item in numbers["current_slots"]}
        if {item["id"] for item in graph["version_nodes"]} != set(NODE_IDS[:checkpoint+1]):
            raise ValueError("visible definition inventory differs from fixed scaffold")
        if {item["definition"] for item in current.values()} != {
                item["id"] for item in graph["version_nodes"] if item["status"] == "current"}:
            raise ValueError("numeric and structural current versions differ")
        for slot, item in current.items(): numeric[i, slot] = item["value"]; numeric_mask[i, slot] = True
        pairs = {(int(item["left"][1:]), int(item["right"][1:])): item for item in numbers["ordered_pairs"]}
        triples = {tuple(int(item[key][1:]) for key in ("first", "second", "third")): item
                   for item in numbers["ordered_triples"]}
        direct = {tuple(edge) for edge in graph["direct_def_use_edges"]}
        ancestor = {tuple(edge) for edge in graph["strict_ancestor_edges"]}
        for destination, candidates in enumerate(PARENT_CANDIDATES):
            consumer = NODE_IDS[4+destination]
            if 4+destination > checkpoint: continue
            sources = [parent for parent, child in direct if child == consumer]
            if len(sources) != 1: raise ValueError("each visible copy must have one direct parent")
            candidate = int(sources[0][1:2])
            if candidate not in candidates or sources[0] != NODE_IDS[_parent_node(destination, candidate)]:
                raise ValueError("copy parent is not the version current at consumption")
            parent_truth[i, destination] = candidate; parent_mask[i, destination] = True
        for spec in COLUMNS:
            j = spec["index"]; family = spec["family"]; selected = tuple(spec["slots"])
            if spec["kind"] == "value":
                if selected[0] in current: y[i, j] = current[selected[0]]["value"]; mask[i, j] = True
            elif family in ("equal", "less_than", "difference"):
                if selected in pairs: y[i, j] = pairs[selected][family]; mask[i, j] = True
            elif family in ("sum_equals_third", "difference_equals_third"):
                if selected in triples: y[i, j] = triples[selected][family]; mask[i, j] = True
            elif family in ("direct", "ancestor"):
                parent, consumer = spec["source_node"], spec["consumer_node"]
                possible = POSSIBLE_DIRECT if family == "direct" else POSSIBLE_ANCESTOR
                mask[i, j] = NODE_INDEX[consumer] <= checkpoint and possible[NODE_INDEX[parent], NODE_INDEX[consumer]]
                y[i, j] = (parent, consumer) in (direct if family == "direct" else ancestor)
            elif family == "parent":
                destination = spec["destination"]
                mask[i, j] = parent_mask[i, destination]
                y[i, j] = mask[i, j] and parent_truth[i, destination] == spec["candidate"]
            elif family == "output_ancestor" and site == 8:
                mask[i, j] = True; y[i, j] = spec["source_node"] in graph["output"]["structural_ancestors"]
            elif spec["kind"] == "value_class" and selected[0] in current:
                value = current[selected[0]]["value"]
                if value not in VALUE_CLASSES: raise ValueError("numeric target outside fixed nonzero value-class domain")
                mask[i, j] = True; y[i, j] = value == spec["candidate"]
        if np.any(y[i, ~mask[i]] != 0): raise ValueError("masked labels cannot expose future/invalid positives")
        last_graph = graph
    descriptive = dict(visible_definitions=list(NODE_IDS[:checkpoint+1]),
        current_definitions=[node["id"] for node in last_graph["version_nodes"] if node["status"] == "current"],
        obsolete_definitions=[node["id"] for node in last_graph["version_nodes"] if node["status"] == "obsolete"],
        succession_edges=last_graph["succession_edges"], learned_version_resolution=False,
        numeric_values_are_targets=True, scaffold_possible_full_graphs=81,
        binary_score_threshold=0.5, value_rounding="clip[-64,64] then numpy.rint ties-to-even",
        primary_value_baseline="four categorical value argmax heads", value_classes=list(VALUE_CLASSES),
        coherent_shuffle_qualified_sites=list(COHERENT_SHUFFLE_QUALIFIED_SITES),
        pipeline_parameter_counts_4096=dict(direct_18_boolean=73746, categorical_value=524416, scalar_value=16388),
        whole_pipelines_parameter_matched=False)
    return TargetBundle(_readonly(y), _readonly(mask), COLUMNS, _readonly(numeric), _readonly(numeric_mask),
        tuple(item[4] for item in records), tuple(item[5] for item in records), tuple(row["split"] for row in rows),
        site, _readonly(parent_truth), _readonly(parent_mask), tuple(item[4] for item in records), descriptive)


def _indices(indices, n, permutation=False):
    values = np.asarray(indices)
    if values.dtype.kind == "b" and not permutation and values.shape == (n,): values = np.flatnonzero(values)
    if values.ndim != 1 or values.dtype.kind not in "iu" or np.any(values >= n):
        raise ValueError("bounded one-dimensional integer row indices required")
    if np.any(values < 0): raise ValueError("negative row indices excluded")
    values = values.astype(np.int64)
    if permutation and (len(values) != n or set(values.tolist()) != set(range(n))):
        raise ValueError("whole-bank bijective donor permutation required")
    return values


def subset(bundle, indices):
    indices = _indices(indices, len(bundle.case_ids))
    if not len(indices): raise ValueError("nonempty target subset required")
    return replace(bundle, **{key: _readonly(getattr(bundle, key)[indices]) for key in
        ("y", "mask", "numeric_truth", "numeric_mask", "parent_truth", "parent_mask")},
        **{key: tuple(getattr(bundle, key)[i] for i in indices) for key in
           ("case_ids", "group_ids", "splits", "label_case_ids")})


def permute_bundle(bundle, donor_indices):
    """Permute complete labels, retaining recipient IDs/features and split identity."""
    indices = _indices(donor_indices, len(bundle.case_ids), permutation=True)
    if any(bundle.splits[i] != bundle.splits[donor] for i, donor in enumerate(indices)):
        raise ValueError("target donors cannot cross splits")
    return replace(bundle, **{key: _readonly(getattr(bundle, key)[indices]) for key in
        ("y", "mask", "numeric_truth", "numeric_mask", "parent_truth", "parent_mask")},
        label_case_ids=tuple(bundle.label_case_ids[i] for i in indices))


def coherent_shuffle(rows, seed):
    """Derange components, shuffle initialization bases, then first-parent choices.

    A base is the canonical four-initial-assignment prefix, never a required ID
    field. Its three future first-parent variants and both lexical forms travel
    together for numeric-state mapping. Within each mapped base, first-parent
    programs are permuted with lexical forms tied. This prevents contradictory
    numeric labels for identical initialization prefixes. The fixed bank has 12
    bases and 36 programs per component; equal coverage is required here.

    Base seed +100000 is used. One donor permutation applies to all target columns
    and sites, but only fitted sites 3/7/8 are control-qualified. Earlier partial
    initialization/copy-prefix consistency is not asserted. Global unweighted
    marginals are preserved; recipient-template-weighted marginals need not be.
    DEV control targets are shuffled too. Global initialization-prefix consistency
    is checked across components, not assumed from the grouping IDs.
    """
    if type(seed) is not int or not 0 <= seed < 2**63-COHERENT_SHUFFLE_OFFSET:
        raise ValueError("bounded nonnegative integer base shuffle seed required")
    records = _records(rows)
    units = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    initializations = []
    for i, (row, tree, slots, _, _, group) in enumerate(records):
        lexical = row.get("lexical_realization")
        if type(lexical) is not int or lexical not in (0, 1): raise ValueError("two lexical realizations 0/1 required")
        # Fixed root destinations are canonical slots 0,1,2,3, so their literal
        # ASTs completely identify the canonical initialization-prefix block.
        initialization = tuple(ast.dump(stmt.value) for stmt in tree.body[:4])
        initializations.append(initialization)
        parent = slots[tree.body[4].value.id]
        unit = units[row["split"], group][initialization][parent]
        if lexical in unit: raise ValueError("duplicate program/lexical source unit")
        unit[lexical] = i
    if any(set(block) != set(PARENT_CANDIDATES[0]) for groups in units.values() for block in groups.values()):
        raise ValueError("three first-parent variants per initialization block required")
    if any(set(unit) != {0, 1} for groups in units.values() for block in groups.values() for unit in block.values()):
        raise ValueError("complete paired lexical program units required")
    rng = np.random.default_rng(seed + COHERENT_SHUFFLE_OFFSET)
    donors = np.full(len(rows), -1, dtype=np.int64)
    for split in ("train", "development"):
        groups = sorted(group for actual, group in units if actual == split)
        if not groups: continue
        if len(groups) < 2: raise ValueError("component derangement needs at least two groups per split")
        sizes = {len(units[split, group]) for group in groups}
        if len(sizes) != 1: raise ValueError("equal initialization-block/program coverage across components required")
        for _ in range(1000):
            order = rng.permutation(len(groups))
            if np.all(order != np.arange(len(groups))): break
        else: raise ValueError("could not construct fixed-seed component derangement")
        for group_index, group in enumerate(groups):
            target_blocks = sorted(units[split, group]); donor_group = groups[order[group_index]]
            donor_blocks = sorted(units[split, donor_group]); block_order = rng.permutation(len(donor_blocks))
            for j, block in enumerate(target_blocks):
                donor_block = donor_blocks[block_order[j]]; parent_order = rng.permutation(3)
                for p, parent in enumerate(PARENT_CANDIDATES[0]):
                    for lexical, index in units[split, group][block][parent].items():
                        donor_parent = PARENT_CANDIDATES[0][parent_order[p]]
                        donors[index] = units[split, donor_group][donor_block][donor_parent][lexical]
    _indices(donors, len(rows), permutation=True)
    prefix_targets = {}
    for i, donor in enumerate(donors):
        key = rows[i]["split"], initializations[i]
        target = initializations[donor]
        if key in prefix_targets and prefix_targets[key] != target:
            raise ValueError("identical initialization prefixes have conflicting shuffled states across components")
        prefix_targets[key] = target
    return _readonly(donors)


def _groups(bundle, groups=None):
    groups = tuple(bundle.group_ids if groups is None else groups)
    if len(groups) != len(bundle.case_ids) or any(not isinstance(group, str) or not group for group in groups):
        raise ValueError("one explicit structural group per row required")
    return groups


def fixed_primary_boolean_indices(bundle):
    """The 18 semantic primary cells; TRAIN support must independently qualify them."""
    selected = []
    for spec in bundle.columns:
        family, slots = spec["family"], tuple(spec["slots"])
        if (family == "less_than" or family == "equal" and slots in ((1, 2), (2, 1))
                or family == "sum_equals_third" and slots in ((0, 1, 2), (1, 0, 2))
                or family == "difference_equals_third" and slots in ((2, 0, 1), (2, 1, 0))):
            selected.append(spec["index"])
    if len(selected) != 18 or not np.all(bundle.mask[:, selected]):
        raise ValueError("primary cells require all four visible slots")
    return tuple(selected)


def training_support(bundle, groups=None, min_class_groups=12):
    if any(split != "train" for split in bundle.splits): raise ValueError("eligibility is TRAIN-only")
    groups = np.asarray(_groups(bundle, groups)); unique = sorted(set(groups))
    if type(min_class_groups) is not int or not 1 <= min_class_groups <= len(unique):
        raise ValueError("valid TRAIN group-support threshold required")
    cells = []; eligible = []
    for spec in bundle.columns:
        j = spec["index"]; defined = bundle.mask[:, j]; values = bundle.y[defined, j]
        classes, counts = np.unique(values, return_counts=True)
        positive = negative = mixed = 0
        for group in unique:
            observed = set(bundle.y[defined & (groups == group), j])
            positive += 1 in observed; negative += 0 in observed; mixed += observed == {0, 1}
        qualified = (spec["family"] in ALGEBRAIC_FAMILIES and positive >= min_class_groups and negative >= min_class_groups)
        if qualified: eligible.append(j)
        cells.append(dict(index=j, name=spec["name"], kind=spec["kind"], family=spec["family"],
            defined_rows=int(defined.sum()), observed_classes=[int(value) for value in classes],
            class_counts={str(int(value)): int(count) for value, count in zip(classes, counts)},
            constant=bool(len(classes) == 1), missing=not len(classes), positive_groups=positive,
            negative_groups=negative, mixed_groups=mixed, eligible_boolean=qualified))
    heads = []
    for destination, candidates in enumerate(PARENT_CANDIDATES):
        labels = bundle.parent_truth[bundle.parent_mask[:, destination], destination]
        histogram = {str(candidate): int(np.sum(labels == candidate)) for candidate in candidates}
        heads.append(dict(destination=destination, candidates=list(candidates), class_counts=histogram,
                          defined_rows=len(labels), majority_prior=max(histogram.values())/len(labels) if len(labels) else None))
    value_heads = []
    for slot in range(4):
        labels = bundle.numeric_truth[bundle.numeric_mask[:, slot], slot]
        histogram = {str(candidate): int(np.sum(labels == candidate)) for candidate in VALUE_CLASSES}
        value_heads.append(dict(slot=slot, class_domain=list(VALUE_CLASSES),
            observed_classes=[candidate for candidate in VALUE_CLASSES if histogram[str(candidate)]],
            class_counts=histogram, defined_rows=len(labels),
            majority_prior=max(histogram.values())/len(labels) if len(labels) else None))
    return dict(eligibility_split="train", minimum_class_groups=min_class_groups,
        eligibility_rule="positive_groups>=threshold AND negative_groups>=threshold",
        structural_groups=len(unique), eligible_boolean_indices=eligible, columns=cells,
        parent_heads=heads, value_categorical_heads=value_heads)


def _scores(bundle, scores):
    scores = np.asarray(scores, dtype=np.float64)
    if scores.shape != bundle.y.shape: raise ValueError("score shape differs from fixed targets")
    return scores


def value_predictions(bundle, scores):
    values = _scores(bundle, scores)[:, :4]
    if not np.all(np.isfinite(values[bundle.numeric_mask])): raise ValueError("defined value predictions must be finite")
    return np.where(bundle.numeric_mask, np.rint(np.clip(values, -64, 64)), np.nan)


def _derived_from_values(bundle, values):
    result = np.full(bundle.y.shape, np.nan)
    for spec in bundle.columns:
        j = spec["index"]; slots = spec["slots"]; family = spec["family"]
        if spec["kind"] == "value": result[:, j] = values[:, slots[0]]
        elif family in ("equal", "less_than", "difference"):
            left, right = values[:, slots[0]], values[:, slots[1]]
            result[:, j] = left == right if family == "equal" else left < right if family == "less_than" else left-right
        elif family in ("sum_equals_third", "difference_equals_third"):
            first, second, third = (values[:, slot] for slot in slots)
            result[:, j] = first+second == third if family == "sum_equals_third" else first-second == third
        result[~bundle.mask[:, j], j] = np.nan
    return _readonly(result)


def derived_relations(bundle, scores):
    """SECONDARY scalar clip/round-derived matrix; structural/category NaNs."""
    return _derived_from_values(bundle, value_predictions(bundle, scores))


def categorical_value_predictions(bundle, scores):
    """PRIMARY value comparator: argmax of each independently fitted 32-way head."""
    scores = _scores(bundle, scores); predicted = np.full(bundle.numeric_truth.shape, np.nan)
    for slot in range(4):
        indices = [spec["index"] for spec in bundle.columns if spec["kind"] == "value_class" and spec["slots"] == [slot]]
        valid = bundle.numeric_mask[:, slot]
        if not np.all(np.isfinite(scores[:, indices][valid])):
            raise ValueError("defined categorical value scores must be finite")
        choices = np.argmax(scores[:, indices], axis=1)
        predicted[valid, slot] = np.asarray(VALUE_CLASSES)[choices[valid]]
    return _readonly(predicted)


def derived_categorical_relations(bundle, scores):
    """PRIMARY value-derived relation matrix; structural heads unavailable/NaN."""
    scores = _scores(bundle, scores)
    result = np.array(_derived_from_values(bundle, categorical_value_predictions(bundle, scores)), copy=True)
    indices = [spec["index"] for spec in bundle.columns if spec["kind"] == "value_class"]
    result[:, indices] = np.where(bundle.mask[:, indices], scores[:, indices], np.nan)
    return _readonly(result)


def reconstruct_parent_graph(bundle, scores):
    scores = _scores(bundle, scores); predicted = np.full(bundle.parent_truth.shape, -1, dtype=np.int64)
    direct = np.zeros((len(bundle.case_ids), 8, 8), dtype=bool)
    for destination, candidates in enumerate(PARENT_CANDIDATES):
        indices = [spec["index"] for spec in bundle.columns if spec["kind"] == "parent" and spec["destination"] == destination]
        valid = bundle.parent_mask[:, destination]
        if not np.all(np.isfinite(scores[np.ix_(valid, indices)])):
            raise ValueError("defined parent-class scores must be finite")
        choices = np.argmax(scores[:, indices], axis=1)
        predicted[valid, destination] = np.asarray(candidates)[choices[valid]]
        for i in np.flatnonzero(valid): direct[i, _parent_node(destination, predicted[i, destination]), 4+destination] = True
    return dict(parent_predictions=_readonly(predicted), parent_mask=bundle.parent_mask,
                direct=_readonly(direct), ancestor=_readonly(_closure(direct)))


def task_correctness(bundle, scores, eligible_boolean_indices=None):
    scores = _scores(bundle, scores)
    indices = tuple(fixed_primary_boolean_indices(bundle) if eligible_boolean_indices is None else eligible_boolean_indices)
    if not indices or any(not isinstance(j, (int, np.integer)) or isinstance(j, (bool, np.bool_)) or not 0 <= j < N_COLUMNS or
            bundle.columns[j]["family"] not in ALGEBRAIC_FAMILIES for j in indices) or len(set(indices)) != len(indices):
        raise ValueError("fixed unique algebraic boolean column indices required")
    if not np.all(bundle.mask[:, indices]) or not np.all(np.isfinite(scores[:, indices])):
        raise ValueError("all fixed evaluation cells must be defined with finite scores")
    parent_correct = np.full(bundle.parent_truth.shape, np.nan); whole_graph = np.full(len(bundle.case_ids), np.nan)
    parent_columns = [spec["index"] for spec in bundle.columns if spec["kind"] == "parent"]
    if np.all(np.isfinite(scores[:, parent_columns][bundle.mask[:, parent_columns]])):
        reconstruction = reconstruct_parent_graph(bundle, scores)
        valid = bundle.parent_mask
        parent_correct[valid] = reconstruction["parent_predictions"][valid] == bundle.parent_truth[valid]
        complete = np.all(valid, axis=1)
        whole_graph[complete] = np.all(parent_correct[complete] == 1, axis=1)
    return dict(algebraic_correct=_readonly((scores[:, indices] >= 0.5) == bundle.y[:, indices]),
        algebraic_truth=_readonly(bundle.y[:, indices].astype(bool)),
        algebraic_families=tuple(bundle.columns[j]["family"] for j in indices), algebraic_column_indices=indices,
        parent_correct=_readonly(parent_correct), whole_graph_correct=_readonly(whole_graph))


def family_macro_balanced_accuracy(truth, correctness, families, sample_weight=None):
    """Allow seed-mean correctness; retain every fixed cell or mark undefined."""
    truth = np.asarray(truth); correct = np.asarray(correctness, dtype=np.float64); families = tuple(families)
    if (truth.ndim != 2 or correct.shape != truth.shape or len(families) != truth.shape[1]
            or truth.dtype.kind != "b" or not np.all(np.isfinite(correct))
            or np.any((correct < 0) | (correct > 1)) or set(families) != set(ALGEBRAIC_FAMILIES)):
        raise ValueError("fixed four-family boolean truth and correctness matrix required")
    weights = np.ones(len(truth)) if sample_weight is None else np.asarray(sample_weight, dtype=np.float64)
    if weights.shape != (len(truth),) or not np.all(np.isfinite(weights)) or np.any(weights < 0) or not weights.sum():
        raise ValueError("finite nonnegative row weights with positive total required")
    by_family = defaultdict(list); missing = []
    for j, family in enumerate(families):
        denominators = [weights[truth[:, j] == value].sum() for value in (False, True)]
        if not all(denominators): missing.append(j); continue
        recalls = [np.sum(weights[truth[:, j] == value]*correct[truth[:, j] == value, j])/denominator
                   for value, denominator in zip((False, True), denominators)]
        by_family[family].append(float(np.mean(recalls)))
    if missing:
        return dict(qualified=False, value=None, missing_class_cells=missing, family_values=None)
    values = {family: float(np.mean(by_family[family])) for family in ALGEBRAIC_FAMILIES}
    return dict(qualified=True, value=float(np.mean(list(values.values()))), missing_class_cells=[], family_values=values)


def _binary_metrics(truth, score, weights):
    truth = np.asarray(truth, dtype=bool); prediction = score >= 0.5
    tp = weights[truth & prediction].sum(); tn = weights[~truth & ~prediction].sum()
    fp = weights[~truth & prediction].sum(); fn = weights[truth & ~prediction].sum()
    positive, negative = tp+fn, tn+fp
    precision = float(tp/(tp+fp)) if tp+fp else 0.0
    recall = float(tp/positive) if positive else None
    return dict(accuracy=float((tp+tn)/weights.sum()),
        balanced_accuracy=float((tp/positive+tn/negative)/2) if positive and negative else None,
        precision=precision, recall=recall,
        f1=float(2*tp/(2*tp+fp+fn)) if 2*tp+fp+fn else 0.0,
        average_precision=float(average_precision_score(truth, score, sample_weight=weights)) if positive else None,
        positive_rows=int(truth.sum()), negative_rows=int((~truth).sum()))


def metrics(bundle, scores, groups=None, eligible_boolean_indices=None, training_support_info=None,
            include_per_group=True):
    """JSON-ready per-cell/per-group metrics; constant cells remain separate."""
    if type(include_per_group) is not bool: raise ValueError("include_per_group must be boolean")
    scores = _scores(bundle, scores); groups = np.asarray(_groups(bundle, groups)); unique = sorted(set(groups))
    row_weights = np.asarray([1/np.sum(groups == group) for group in groups])
    binary = []; numeric = []; parents = []
    for spec in bundle.columns:
        j = spec["index"]; valid = bundle.mask[:, j]
        if not np.any(valid): continue
        if not np.all(np.isfinite(scores[valid, j])): continue  # e.g. unavailable structural heads for value-derived controls
        base = dict(index=j, name=spec["name"], family=spec["family"], defined_rows=int(valid.sum()))
        if spec["kind"] == "boolean":
            truth = bundle.y[valid, j].astype(bool); weights = row_weights[valid]
            cell = {**base, **_binary_metrics(truth, scores[valid, j], weights), "constant_label": len(np.unique(truth)) == 1}
            cell["per_group"] = [{"group": group, **_binary_metrics(bundle.y[valid & (groups == group), j].astype(bool),
                scores[valid & (groups == group), j], row_weights[valid & (groups == group)])}
                for group in unique if np.any(valid & (groups == group))] if include_per_group else []
            binary.append(cell)
        elif spec["kind"] in ("value", "difference"):
            error = scores[valid, j]-bundle.y[valid, j]
            prediction = value_predictions(bundle, scores)[valid, spec["slots"][0]] if spec["kind"] == "value" else np.rint(scores[valid, j])
            numeric.append({**base, "mae": float(np.average(abs(error), weights=row_weights[valid])),
                "rmse": float(np.sqrt(np.average(error**2, weights=row_weights[valid]))),
                "integer_prediction": "clip[-64,64] then rint" if spec["kind"] == "value" else "unclipped rint",
                "rounded_integer_accuracy": float(np.average(prediction == bundle.y[valid, j], weights=row_weights[valid]))})
    primary = None
    if eligible_boolean_indices is not None:
        correctness = task_correctness(bundle, scores, eligible_boolean_indices)
        primary = family_macro_balanced_accuracy(correctness["algebraic_truth"], correctness["algebraic_correct"],
                                                 correctness["algebraic_families"], row_weights)
    parent_columns = [spec["index"] for spec in bundle.columns if spec["kind"] == "parent"]
    parent_summary = None
    if np.any(bundle.parent_mask) and np.all(np.isfinite(scores[:, parent_columns][bundle.mask[:, parent_columns]])):
        reconstruction = reconstruct_parent_graph(bundle, scores); predicted = reconstruction["parent_predictions"]
        for destination, candidates in enumerate(PARENT_CANDIDATES):
            valid = bundle.parent_mask[:, destination]
            if not np.any(valid): continue
            truth = bundle.parent_truth[valid, destination]; prediction = predicted[valid, destination]
            classes = {str(candidate): int(np.sum(truth == candidate)) for candidate in candidates}
            recalls = [float(np.average(prediction[truth == candidate] == candidate,
                weights=row_weights[valid][truth == candidate])) for candidate in candidates if np.any(truth == candidate)]
            parents.append(dict(destination=destination, candidates=list(candidates), class_counts=classes,
                majority_prior=max(classes.values())/len(truth), accuracy=float(np.average(truth == prediction, weights=row_weights[valid])),
                balanced_accuracy=float(np.mean(recalls)) if len(recalls) == 3 else None))
        complete = np.all(bundle.parent_mask, axis=1)
        parent_summary = dict(heads=parents, macro_parent_accuracy=float(np.mean([head["accuracy"] for head in parents])),
            whole_graph_accuracy=float(np.average(np.all(predicted[complete] == bundle.parent_truth[complete], axis=1), weights=row_weights[complete])) if np.any(complete) else None,
            whole_graph_rows=int(complete.sum()), reconstruction="Four three-way parent argmax heads; fixed roots/versions, 81 possible full graphs")
    graph_exact = {}
    for family in ("direct", "ancestor"):
        indices = [spec["index"] for spec in bundle.columns if spec["family"] == family]
        valid = bundle.mask[:, indices]; defined = np.any(valid, axis=1)
        if np.any(defined) and np.all(np.isfinite(scores[:, indices][valid])):
            correct = np.all(((scores[:, indices] >= 0.5) == bundle.y[:, indices]) | ~valid, axis=1)
            graph_exact[family] = float(np.average(correct[defined], weights=row_weights[defined]))
        else: graph_exact[family] = None
    categorical = []
    category_columns = [spec["index"] for spec in bundle.columns if spec["kind"] == "value_class"]
    if np.all(np.isfinite(scores[:, category_columns][bundle.mask[:, category_columns]])):
        predicted = categorical_value_predictions(bundle, scores)
        for slot in range(4):
            valid = bundle.numeric_mask[:, slot]
            if not np.any(valid): continue
            truth = bundle.numeric_truth[valid, slot]; prediction = predicted[valid, slot]
            histogram = {str(candidate): int(np.sum(truth == candidate)) for candidate in VALUE_CLASSES}
            observed = [candidate for candidate in VALUE_CLASSES if histogram[str(candidate)]]
            train_head = next((head for head in training_support_info.get("value_categorical_heads", [])
                               if head["slot"] == slot), None) if training_support_info is not None else None
            train_classes = train_head["observed_classes"] if train_head is not None else None
            out = int(np.sum(~np.isin(truth, train_classes))) if train_classes is not None else None
            categorical.append(dict(slot=slot, defined_rows=len(truth), class_domain=list(VALUE_CLASSES),
                observed_classes=observed, class_counts=histogram, training_observed_classes=train_classes,
                out_of_training_support_rows=out,
                predicted_out_of_training_support_rows=int(np.sum(~np.isin(prediction, train_classes))) if train_classes is not None else None,
                accuracy=float(np.average(truth == prediction, weights=row_weights[valid])),
                macro_recall_observed_classes=float(np.mean([np.average(prediction[truth == candidate] == candidate,
                    weights=row_weights[valid][truth == candidate]) for candidate in observed]))))
    family_summaries = {}
    for family in sorted({cell["family"] for cell in binary}):
        cells = [cell for cell in binary if cell["family"] == family]
        nonconstant = [cell for cell in cells if not cell["constant_label"]]
        summary = dict(defined_cells=len(cells), constant_cells=len(cells)-len(nonconstant),
                       nonconstant_cells=len(nonconstant), per_group=[])
        for metric in ("balanced_accuracy", "precision", "recall", "f1", "average_precision"):
            values = [cell[metric] for cell in nonconstant if cell[metric] is not None]
            summary["nonconstant_cell_macro_"+metric] = float(np.mean(values)) if values else None
        for group in unique if include_per_group else []:
            group_cells = [point for cell in cells for point in cell["per_group"] if point["group"] == group]
            qualified = [cell for cell in group_cells if cell["positive_rows"] and cell["negative_rows"]]
            group_summary = dict(group=group, defined_cells=len(group_cells), both_class_cells=len(qualified))
            for metric in ("balanced_accuracy", "precision", "recall", "f1", "average_precision"):
                values = [cell[metric] for cell in qualified if cell[metric] is not None]
                group_summary["both_class_cell_macro_"+metric] = float(np.mean(values)) if values else None
            summary["per_group"].append(group_summary)
        family_summaries[family] = summary
    return dict(site=bundle.site_name, rows=len(bundle.case_ids), structural_groups=len(unique),
        binary_threshold=0.5, binary_scores_are_probabilities=False, binary_cells=binary, numeric_cells=numeric,
        per_group_cells_included=include_per_group,
        constant_boolean_cells=sum(cell["constant_label"] for cell in binary),
        nonconstant_boolean_cells=sum(not cell["constant_label"] for cell in binary),
        masked_columns=sum(not np.any(bundle.mask[:, j]) for j in range(N_COLUMNS)),
        algebraic_family_macro_balanced_accuracy=primary, parent_graph=parent_summary, value_categorical=categorical,
        raw_binary_exact_graph_accuracy=graph_exact, binary_family_summaries=family_summaries,
        version_resolution_learned=False,
        statistical_unit="Equal-weight structural groups; per-cell and per-group metrics, no independent-cell replication")
