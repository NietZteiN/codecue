"""Paths from scripts/env.sh (CODECUE_* variables); defaults keep the package importable on the
login node without sourcing it."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(os.environ.get("CODECUE_ROOT", Path(__file__).resolve().parents[2]))
CONFIG_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = Path(os.environ.get("CODECUE_OUT", f"/scratch/juno/{os.environ.get('USER', 'x')}/codecue"))
RESULTS_DIR = PROJECT_ROOT / "results"


def load_config(name: str) -> dict:
    with (CONFIG_DIR / name).open() as f:
        return yaml.safe_load(f)


def model_entry(key: str) -> dict:
    models = load_config("models.yaml")["models"]
    if key not in models:
        raise KeyError(f"unknown model key {key!r}; known: {sorted(models)}")
    return {"key": key, **models[key]}
