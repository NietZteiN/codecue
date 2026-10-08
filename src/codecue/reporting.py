"""The paper consumes a probe release only after its split audit passes."""
from __future__ import annotations

import json

from .config import OUT_DIR, RESULTS_DIR


def probe_directory():
    release = RESULTS_DIR / "summary" / "probe_release.json"
    if release.exists():
        data = json.loads(release.read_text())
        if data.get("validated") is True and data.get("root") == "probes_disjoint":
            return "probes_disjoint"
        raise ValueError("invalid probe release; refusing to select paper inputs")
    return "probes"


def probe_output(model, regime="trace", role="v1"):
    return OUT_DIR / probe_directory() / model / "L5" / regime / f"{role}.json"
