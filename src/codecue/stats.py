"""Paired inference with matched programs kept intact across demonstration seeds."""
from __future__ import annotations

import numpy as np


def bootstrap_ci(values, clusters, n_boot=2000, seed=0, confidence=0.95):
    """Resample matched sets, including all their seed replicates and unequal counts."""
    values = np.asarray(values, dtype=float)
    clusters = np.asarray(clusters)
    if values.ndim != 1 or clusters.ndim != 1 or not len(values) or len(values) != len(clusters):
        raise ValueError("values and clusters must be nonempty vectors of the same length")
    if not 0 < confidence < 1 or n_boot < 1:
        raise ValueError("confidence must be in (0, 1) and n_boot must be positive")
    _, inverse = np.unique(clusters, return_inverse=True)
    sums = np.bincount(inverse, weights=values)
    counts = np.bincount(inverse)
    rng = np.random.default_rng(seed)
    draws = []
    for start in range(0, n_boot, 128):
        picks = rng.integers(0, len(sums), (min(128, n_boot - start), len(sums)))
        draws.extend(sums[picks].sum(axis=1) / counts[picks].sum(axis=1))
    tail = 100 * (1 - confidence) / 2
    lo, hi = np.percentile(draws, [tail, 100 - tail])
    return float(values.mean()), float(lo), float(hi)
