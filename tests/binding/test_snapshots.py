from pathlib import Path
import pytest
from codecue.binding.snapshots import freeze, verify


def test_snapshot_captures_source_and_configs_then_rejects_mutation(tmp_path):
    path=tmp_path/'frozen'
    created=freeze(path)
    manifest=verify(path)
    assert manifest['snapshot_id']==created['snapshot_id']
    assert (path/'src/codecue/binding/model_adapter.py').is_file()
    assert (path/'configs/binding/cpu_smoke.json').is_file()
    assert freeze(path)==created
    source=path/'src/codecue/binding/model_adapter.py'
    source.write_text(source.read_text()+'\n# modified\n')
    with pytest.raises(ValueError,match='source checksum mismatch'):
        verify(path)


def test_frozen_configuration_is_part_of_identity(tmp_path):
    path=tmp_path/'frozen'
    freeze(path)
    config=path/'configs/binding/smoke.json'
    config.write_text('{}\n')
    with pytest.raises(ValueError,match='configuration changed'):
        verify(path)


def test_older_snapshot_verifies_after_entrypoint_catalog_expands(tmp_path,monkeypatch):
    import codecue.binding.snapshots as snapshots
    path=tmp_path/'frozen'
    freeze(path)
    monkeypatch.setattr(snapshots,'SCRIPT_NAMES',(*snapshots.SCRIPT_NAMES,'99_future_entrypoint.py'))
    assert verify(path)['snapshot_id']


def test_extra_executable_source_invalidates_snapshot(tmp_path):
    path=tmp_path/'frozen'
    freeze(path)
    (path/'scripts/extra.py').write_text('print("unexpected")\n')
    with pytest.raises(ValueError,match='source checksum mismatch'):
        verify(path)


def test_frozen_report_writes_to_workspace_instead_of_source_snapshot(tmp_path):
    import json
    import subprocess
    import sys
    from codecue.binding.snapshots import workspace_root
    frozen=tmp_path/'frozen'
    workspace=tmp_path/'workspace'
    workspace.mkdir()
    freeze(frozen)
    path=frozen/'frozen_manifest.json'
    manifest=json.loads(path.read_text())
    manifest['workspace_root']=str(workspace)
    path.write_text(json.dumps(manifest))
    assert workspace_root(frozen)==workspace.resolve()
    subprocess.run([sys.executable,str(frozen/'scripts/91_binding_frozen_run.py'),str(frozen),
                    'scripts/92_binding_progress_report.py'],check=True,capture_output=True,text=True)
    assert (workspace/'reports/binding/pilot_report.md').is_file()
    assert (workspace/'artifacts/binding/phase2_evidence.json').is_file()
    assert not (frozen/'reports').exists()
