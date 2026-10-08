import json

import pytest

from codecue import reporting


def test_paper_keeps_original_inputs_until_a_release_is_validated(tmp_path, monkeypatch):
    monkeypatch.setattr(reporting, "RESULTS_DIR", tmp_path)
    assert reporting.probe_directory() == "probes"


def test_validated_release_selects_disjoint_outputs(tmp_path, monkeypatch):
    (tmp_path / "summary").mkdir()
    (tmp_path / "summary/probe_release.json").write_text(json.dumps(
        {"validated": True, "root": "probes_disjoint"}))
    monkeypatch.setattr(reporting, "RESULTS_DIR", tmp_path)
    assert reporting.probe_directory() == "probes_disjoint"


def test_incomplete_release_cannot_silently_replace_paper_inputs(tmp_path, monkeypatch):
    (tmp_path / "summary").mkdir()
    (tmp_path / "summary/probe_release.json").write_text(json.dumps(
        {"validated": False, "root": "probes_disjoint"}))
    monkeypatch.setattr(reporting, "RESULTS_DIR", tmp_path)
    with pytest.raises(ValueError, match="invalid probe release"):
        reporting.probe_directory()
