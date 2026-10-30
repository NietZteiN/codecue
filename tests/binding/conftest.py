"""Keep fixture lifecycle events out of the real workspace experiment journal."""
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_fixture_lifecycle_logging(monkeypatch):
    from codecue.binding import registry
    from codecue.binding.snapshots import workspace_root

    original=registry._log_stage

    def log_fixture_stage(event_type,out,manifest):
        root=workspace_root(registry.ROOT).resolve()
        if Path(out).resolve().is_relative_to(root):
            return original(event_type,out,manifest)

    monkeypatch.setattr(registry,'_log_stage',log_fixture_stage)
