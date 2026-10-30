"""The unchanged 232 target tasks on the pinned 5,760-case diversity bank.

The original target implementation lives in a separate registered namespace.
Only its source validator and row bound change; the old module, roles, labels,
masking, prefix-keyed sham tasks and TRAIN support rules remain untouched.
All source-derived identities here are targets or validation metadata, never
representation features. This adapter does not load source outcome arrays.
"""
from __future__ import annotations

import ast
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
from types import MappingProxyType

from . import schedule_diversity_programs as programs, schedule_targets as original
from .datasets import digest
from .programs import rename
from .relationship_capture import _safe

DATASET_ROLE = programs.ROLE
DATASET_SHA256 = "d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1"
MANIFEST_SHA256 = "e6a778b1bdab4dbb7666795a9baed63a4410184b4d0a9458afa8ce3ce13ee12f"
GENERATION_CONFIG_SHA256 = "e243d7128a9882762f293b120d5fae14fb1f274305471e5e7736554c2c83352d"
GENERATION_CONFIG_HASH = "feb31d690d97e98fb870199f45f6864920eaebe2cbe0acca0def3b3501543029"
MANIFEST_PATH = "artifacts/binding/schedule_diversity/20261028_v1/sources.manifest.json"
GENERATION_CONFIG_PATH = "configs/binding/relationships/schedule_diversity_generation_v1.json"
MAX_ROWS = 5760
MAX_METADATA_BYTES = 2 * 1024**2


def _pinned_json(path, checksum):
    path = _safe(path)
    if path.suffix != ".json" or path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_METADATA_BYTES:
        raise ValueError("bounded nonsymlink pinned generation JSON required")
    with path.open("rb") as stream:
        payload = stream.read(MAX_METADATA_BYTES + 1)
    if len(payload) > MAX_METADATA_BYTES or hashlib.sha256(payload).hexdigest() != checksum:
        raise ValueError("published diversity generation metadata SHA256 differs")
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError("published generation metadata object required")
    return value


def _published_recipe():
    manifest = _pinned_json(MANIFEST_PATH, MANIFEST_SHA256)
    config = _pinned_json(GENERATION_CONFIG_PATH, GENERATION_CONFIG_SHA256)
    if (manifest.get("status") != "complete" or manifest.get("evaluation_role") != DATASET_ROLE
            or manifest.get("role") != DATASET_ROLE or manifest.get("sha256") != DATASET_SHA256
            or manifest.get("rows") != MAX_ROWS or manifest.get("split_rows") != {"train":4320,"development":1440}
            or manifest.get("canonical_graph_families") != 60
            or manifest.get("split_canonical_graph_units") != {"train":45,"development":15}
            or manifest.get("generated_holdouts_opened") is not False
            or manifest.get("targets_prepared_only") is not True
            or manifest.get("learned_readout_compatible") is not False
            or manifest.get("generation_config") != config
            or manifest.get("generation_config_hash") != GENERATION_CONFIG_HASH
            or digest(config) != GENERATION_CONFIG_HASH):
        raise ValueError("exact published diversity generation recipe required")
    return config


@lru_cache(maxsize=1)
def _family_map():
    # Reconstruct only the small selected-family map, never the full source bank.
    selected, _, _, _, _ = programs._selection(_published_recipe())
    result = {}
    for profile in programs.PROFILES:
        for index, (graph, destinations, parents) in enumerate(selected[profile]):
            if graph in result:
                raise ValueError("selected graph families are not distinct")
            result[graph] = (profile, index, destinations, parents,
                             "train" if index < 15 else "development")
    if len(result) != 60:
        raise ValueError("complete60-family generation selection required")
    return MappingProxyType(result)


def _records(rows):
    """Validate complete recipe identities, including stripped capture records."""
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("bounded nonempty diversity source rows required")
    families = _family_map(); result = []; seen = set()
    for row in rows:
        if (not isinstance(row, dict) or row.get("evaluation_role") != DATASET_ROLE
                or row.get("condition") != "neutral" or row.get("variable_slots") != programs.prior.SLOTS
                or any(type(value) is not int for value in row["variable_slots"].values())
                or row.get("source_form") != "literal"):
            raise ValueError("neutral discovery diversity role and canonical four slots required")
        for field in ("update_count_profile","destination_update_counts","destination_schedule","copy_parent_slots"):
            values = row.get(field)
            if not isinstance(values,list) or len(values) != 4 or any(type(value) is not int for value in values):
                raise ValueError("strict integer profile/schedule metadata required")
        graph = row.get("canonical_graph_sha256")
        if not isinstance(graph, str) or graph not in families:
            raise ValueError("source graph is outside the pinned selected-family map")
        profile, index, destinations, parents, split = families[graph]
        component = "schedule-diversity-graph:" + graph[:24]
        if (row.get("split") != split or type(row.get("graph_selection_index")) is not int
                or row["graph_selection_index"] != index
                or row.get("profile_id") != "_".join(map(str,profile))
                or row.get("update_count_profile") != list(profile)
                or any(row.get(key) != component for key in
                       ("component_id","cluster_id","template_id","ssa_graph_canonical_id"))):
            raise ValueError("graph selection, profile or split identity differs from the published recipe")
        rotation = row.get("slot_rotation"); seed = row.get("numeric_seed")
        lexical = row.get("lexical_realization"); query = row.get("query_slot")
        if (type(rotation) is not int or rotation not in range(4)
                or type(seed) is not int or seed not in programs.NUMERIC_SEEDS
                or type(lexical) is not int or lexical not in (0,1)
                or type(query) is not int or query not in range(4)
                or row.get("query_role") != f"v{query}" or type(row.get("query_count")) is not int
                or row["query_count"] != 1):
            raise ValueError("declared cyclic rotation, numeric seed, lexical or query identity required")
        permutation = tuple((slot + rotation) % 4 for slot in range(4))
        actual_dest = tuple(permutation[slot] for slot in destinations)
        actual_parents = tuple(permutation[slot] for slot in parents)
        base = f"{component}:numeric{seed}"
        if (row.get("base_id") != base or row.get("paired_group_id") != base
                or row.get("raw_template_id") != f"{component}:rotation{rotation}"
                or row.get("destination_schedule") != list(actual_dest)
                or row.get("copy_parent_slots") != list(actual_parents)
                or row.get("destination_update_counts") != [actual_dest.count(slot) for slot in range(4)]
                or row.get("parent_pattern") != "independent_distinct_slot_choices"):
            raise ValueError("source schedule, parent or related-case identity differs from actual rotation")
        values = random.Random(digest([DATASET_ROLE,graph,seed,"numeric"])).sample(
            tuple(value for value in range(-12,13) if value),4)
        rotated_values = [0]*4
        for slot,value in enumerate(values):
            rotated_values[permutation[slot]] = value
        canonical = programs.prior._source(rotated_values,actual_dest,actual_parents,query)
        stem = "item" if lexical == 0 else "cell"
        mapping = {name:f"{stem}_{slot}" for slot,name in enumerate(programs.prior.VARIABLES)}
        surface = rename(canonical,mapping)
        if (row.get("canonical_source") != canonical or row.get("source") != surface
                or row.get("rename_map") != mapping):
            raise ValueError("actual numeric/canonical/surface program differs from the pinned recipe")
        tree = programs.relationships._tree(canonical)
        rendered = programs.relationships._tree(surface)
        if (programs._shape(canonical) != (actual_dest,actual_parents)
                or ast.dump(programs.relationships._tree(rename(canonical,mapping))) != ast.dump(rendered)
                or programs._graph(actual_dest,actual_parents) != graph):
            raise ValueError("actual renamed source or generic SSA family differs")
        case = row.get("id")
        if case != "schedule-diversity:" + digest([seed,surface])[:24] or case in seen:
            raise ValueError("unique case ID must identify the actual diversity program")
        seen.add(case)
        result.append((row,tree,{mapping[name]:slot for name,slot in programs.prior.SLOTS.items()}))
    return result


def _isolated_engine():
    name = __package__ + "._diversity_schedule_targets_engine"
    spec = importlib.util.spec_from_file_location(name,original.__file__)
    if spec is None or spec.loader is None:
        raise ValueError("original generic target implementation unavailable")
    engine = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = engine  # dataclass inspects its registered module.
    try:
        spec.loader.exec_module(engine)
    except BaseException:
        if previous is None:
            sys.modules.pop(name,None)
        else:
            sys.modules[name] = previous
        raise
    engine.MAX_ROWS = MAX_ROWS
    engine._records = _records
    return engine


_CORE = _isolated_engine()
targets = _CORE.targets
control_targets = _CORE.control_targets
subset = _CORE.subset
training_support = _CORE.training_support
TargetBundle = _CORE.TargetBundle
COLUMNS = _CORE.COLUMNS
N_COLUMNS = _CORE.N_COLUMNS
HEADS = _CORE.HEADS
SITES = _CORE.SITES
SITE_NAMES = _CORE.SITE_NAMES
NODE_IDS = _CORE.NODE_IDS
VERSION_CLASSES = _CORE.VERSION_CLASSES
CONTROL_KIND = _CORE.CONTROL_KIND
