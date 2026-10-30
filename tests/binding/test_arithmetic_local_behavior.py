from codecue.binding import arithmetic_local_behavior as behavior
from codecue.binding import arithmetic_local_suite as local
from codecue.binding import overnight_relationship_suite as original


def test_calibration_keeps_all_wordings_invalids_and_family_weighting():
    records = []
    for instruction in range(3):
        for group, n, correct in [('a', 3, True), ('b', 1, False)]:
            for _ in range(n):
                records.append(dict(instruction=instruction, split='development', depth=2,
                    query_kind='arithmetic_written', component_id=group, correct=correct, parsed=1 if correct else None))
    rows = behavior.summarize(records)
    assert len(rows) == 3
    assert [r['instruction'] for r in rows] == [0, 1, 2]
    assert all(r['accuracy'] == .75 and r['family_macro_accuracy'] == .5 and r['invalid'] == 1 for r in rows)


def test_local_suite_does_not_change_legacy_monitor_or_script_allowlist():
    assert local._CORE is not original
    assert local._CORE.ROLE == local.ROLE != original.ROLE
    assert 'scripts/177_binding_arithmetic_local_capture.py' in local._CORE.SCRIPTS
    assert 'scripts/177_binding_arithmetic_local_capture.py' not in original.SCRIPTS


def test_completed_capture_releases_cpu_work_without_waiting_for_other_gpu_jobs(monkeypatch):
    monkeypatch.setattr(local, '_legacy_reconcile', lambda *args: [])
    config = dict(nodes=[dict(key='probes', phase='cpu', dependencies=['capture'])])
    state = dict(status=dict(capture=dict(state='complete'), other_gpu=dict(state='running'), probes=dict(state='planned')))
    assert local.reconcile(config, state, {}) == ['probes']
    state['status']['capture']['state'] = 'failed'
    assert local.reconcile(config, state, {}) == []
