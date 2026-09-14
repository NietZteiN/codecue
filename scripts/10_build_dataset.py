#!/usr/bin/env python
"""Build every level's probe-train (neutral only) and matched test sets. CPU, seconds.

    python scripts/10_build_dataset.py [--levels 1 2 3 4 5] [--n-test 1000] [--n-train 4000]

Writes data/L<k>/{train_neutral,test_sets}.jsonl and data/L<k>/manifest.json with a content
hash; the runner refuses a dataset whose hash does not match its manifest.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.generator import LEVELS, content_hash, sample_sets, write_jsonl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="+", type=int, default=list(LEVELS))
    ap.add_argument("--n-test", type=int, default=1000, help="matched sets per target role")
    ap.add_argument("--n-train", type=int, default=4000, help="neutral instances for probe training")
    ap.add_argument("--seed-test", type=int, default=3)
    ap.add_argument("--seed-train", type=int, default=5)
    a = ap.parse_args()
    for L in a.levels:
        d = ROOT / "data" / f"L{L}"
        test = [x for s in sample_sets(L, a.n_test, seed=a.seed_test) for x in s]
        train = [x for s in sample_sets(L, a.n_train // len({x.target for x in test if x.target}), seed=a.seed_train, tag="tr")
                 for x in s if x.condition == "neutral"]
        test_programs = {x.program for x in test}
        train = [x for x in train if x.program not in test_programs]
        n1 = write_jsonl(d / "test_sets.jsonl", test)
        n2 = write_jsonl(d / "train_neutral.jsonl", train)
        man = {"level": L, "n_test_instances": n1, "n_train": n2, "seed_test": a.seed_test, "seed_train": a.seed_train,
               "hash_test": content_hash(test), "hash_train": content_hash(train),
               "conditions": sorted({x.condition for x in test}), "targets": sorted({x.target for x in test if x.target})}
        (d / "manifest.json").write_text(json.dumps(man, indent=2))
        print(f"L{L}: {n1} test instances ({len(test)//len(man['conditions']) if man['conditions'] else 0} sets/cond), "
              f"{n2} neutral train, lures {sorted({x.lure for x in test if x.lure is not None})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
