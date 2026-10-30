#!/usr/bin/env python
"""Prepare new slot-complete discovery copy/overwrite graph source families."""
import argparse
import json

from codecue.binding import schedule_diversity_programs as programs
from codecue.binding.relationship_capture import _safe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args()
    path = _safe(args.config)
    if path.suffix != ".json" or path.stat().st_size > 16 * 1024:
        raise ValueError("bounded discovery source JSON configuration required")
    result = programs.build(json.loads(path.read_text()))
    keys = ("status", "evaluation_role", "rows", "split_rows", "canonical_graph_families",
            "split_canonical_graph_units", "count_profiles", "candidate_search",
            "maximum_assignment_version", "slot_complete_version_domain", "fully_class_balanced",
            "train_minimum_current_version_class_graph_groups", "independent_python_programs",
            "dataset_sha256", "learned_readout_compatible", "new_model_queries")
    print(json.dumps({key: result[key] for key in keys}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
