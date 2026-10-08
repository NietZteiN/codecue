"""Select probe training programs without reusing held-out computations."""
from __future__ import annotations

import json


def program_key(instance):
    """Ignore identifier spelling while retaining input, operations and query."""
    return json.dumps({"xs": instance.xs, "stmts": instance.stmts, "query": instance.query}, sort_keys=True)


def disjoint_training(train, test, limit):
    if limit <= 0:
        raise ValueError("probe training limit must be positive")
    if any(x.condition != "neutral" for x in train):
        raise ValueError("probe training must contain neutral programs only")
    held_out = {program_key(x) for x in test}
    selected = [x for x in train if program_key(x) not in held_out][:limit]
    if not selected:
        raise ValueError("no disjoint probe-training programs remain")
    return selected


def assert_disjoint_metadata(train, tests):
    """Reject shared matched sets or renamed copies before loading hidden states."""
    train_sets = {x["set_id"] for x in train["instances"]}
    train_keys = {x["program_key"] for x in train["instances"] if "program_key" in x}
    overlaps = {}
    for group, test in tests.items():
        n = sum(x["set_id"] in train_sets or x.get("program_key") in train_keys
                for x in test["instances"])
        if n:
            overlaps[group] = n
    if overlaps:
        raise ValueError(f"probe training overlaps evaluation programs: {overlaps}")
