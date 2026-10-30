"""Periodic reconciliation discovers completed standalone readout results."""
import json

import pytest

from codecue.binding import experiment_log as log


@pytest.mark.parametrize('filename', ['results.json', 'completion_manifest_v1.json'])
def test_periodic_scan_finds_results_without_a_registration(tmp_path, filename):
    folder = tmp_path/'artifacts/binding/arithmetic_graph/readouts'
    folder.mkdir(parents=True)
    path = folder/filename
    path.write_text(json.dumps(dict(status='complete_exploratory', model='fixture-model',
        config_hash='b'*64, source=dict(source_sha256='a'*64), cases=4608,
        contrasts=[dict(metric='whole_parent_accuracy', hidden=.5, source=.6)])))
    log.refresh(tmp_path)
    records = log.list_records(tmp_path, kind='analysis')
    assert len(records) == 1
    assert records[0]['status'] == 'complete_exploratory'
    assert records[0]['source_hash'] == 'a'*64
    assert records[0]['config_hash'] == 'b'*64
    assert records[0]['metrics']['review']['cases'] == 4608
    assert records[0]['artifacts']['review']['path'] == str(path)


def test_new_result_names_do_not_open_sealed_outputs(tmp_path, monkeypatch):
    folder = tmp_path/'artifacts/binding/sealed/readouts'
    folder.mkdir(parents=True)
    protected = {folder/'results.json', folder/'completion_manifest_v1.json'}
    for path in protected:
        path.write_text('{"status":"complete","private_outcomes":true}')
    original = log._read
    def read(path, *args, **kwargs):
        assert path not in protected, 'sealed result opened by periodic discovery'
        return original(path, *args, **kwargs)
    monkeypatch.setattr(log, '_read', read)
    log.refresh(tmp_path)
    assert log.list_records(tmp_path, kind='analysis') == []


def test_textual_source_is_not_misread_as_a_code_identity(tmp_path):
    folder = tmp_path/'artifacts/binding/discovery'
    folder.mkdir(parents=True)
    (folder/'results.json').write_text(json.dumps(dict(status='complete', source='v0 = 7')))
    log.refresh(tmp_path)
    records = log.list_records(tmp_path, kind='analysis')
    assert len(records) == 1
    assert records[0]['source_hash'] is None
