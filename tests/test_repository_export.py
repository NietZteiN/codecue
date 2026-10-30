import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tarfile

import pytest

spec=importlib.util.spec_from_file_location('repository_export',Path(__file__).resolve().parents[1]/'scripts/export_binding_repository.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


@pytest.mark.parametrize('name',['../outside','/tmp/outside','artifacts/binding/../../../outside','src/codecue/file.py','artifacts/other/file'])
def test_restore_rejects_paths_outside_artifact_namespace(tmp_path,name):
    with pytest.raises(ValueError):module.safe_target(tmp_path,name)


def test_restore_rejects_symbolic_link_parents(tmp_path):
    base=tmp_path/'artifacts/binding';base.mkdir(parents=True)
    outside=tmp_path/'outside';outside.mkdir();(base/'alias').symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='symbolic'):module.safe_target(tmp_path,'artifacts/binding/alias/file.json')


def test_export_restore_roundtrip_preserves_original_and_local_arrays(tmp_path):
    original=tmp_path/'artifacts/binding/study';original.mkdir(parents=True)
    payload=b'{"case":"illustration","value":7}\n'*150
    source=original/'responses.jsonl';source.write_bytes(payload)
    (original/'review.json').write_text('{"status":"complete"}\n')
    (original/'raw.npz').write_bytes(b'opaque local array; do not open')
    snap=tmp_path/'artifacts/binding/sources'/('a'*24);(snap/'src').mkdir(parents=True)
    (snap/'src/example.py').write_text('value = 7\n')
    module.export(tmp_path,workers=1)
    assert source.read_bytes()==payload
    report=json.loads((tmp_path/'reproducibility/export_review.json').read_text())
    assert report['compressed_artifacts']==1 and report['frozen_source_snapshots']==1
    assert 'raw.npz' in (tmp_path/'reproducibility/local_payload_inventory.csv').read_text()
    clone=tmp_path/'clone';clone.mkdir();shutil.copytree(tmp_path/'reproducibility',clone/'reproducibility')
    module.restore(clone);module.restore_sources(clone)
    assert (clone/'artifacts/binding/study/responses.jsonl').read_bytes()==payload
    assert (clone/'artifacts/binding/sources'/('a'*24)/'src/example.py').read_text()=='value = 7\n'
    module.restore(clone);module.restore_sources(clone)
    (clone/'artifacts/binding/study/responses.jsonl').write_text('local modification')
    with pytest.raises(ValueError,match='overwrite'):module.restore(clone)
    assert (clone/'artifacts/binding/study/responses.jsonl').read_text()=='local modification'


def make_catalog(root,expected_sha=None,declared_size=None):
    folder=root/'reproducibility';folder.mkdir()
    data=b'{"value":7}\n';archive=folder/'data.gz'
    with gzip.open(archive,'wb') as stream:stream.write(data)
    row=dict(original_path='artifacts/binding/study/data.jsonl',stored_path='reproducibility/data.gz',encoding='gzip',original_bytes=len(data) if declared_size is None else declared_size,stored_bytes=archive.stat().st_size,original_sha256=expected_sha or hashlib.sha256(data).hexdigest(),stored_sha256=module.sha(archive))
    (folder/'compressed_artifacts.csv').write_bytes(module.csv_bytes([row],list(row)))
    return archive


def test_corrupt_stored_archive_is_rejected_before_restore(tmp_path):
    archive=make_catalog(tmp_path);archive.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='Stored checksum'):module.restore(tmp_path)
    assert not (tmp_path/'artifacts').exists()


def test_uncompressed_checksum_mismatch_never_publishes_target(tmp_path):
    make_catalog(tmp_path,expected_sha='0'*64)
    with pytest.raises(ValueError,match='Restored checksum'):module.restore(tmp_path)
    assert not (tmp_path/'artifacts/binding/study/data.jsonl').exists()


def test_uncompressed_data_cannot_exceed_declared_size(tmp_path):
    make_catalog(tmp_path,declared_size=1)
    with pytest.raises(ValueError,match='declared size'):module.restore(tmp_path)
    assert not (tmp_path/'artifacts/binding/study/data.jsonl').exists()


@pytest.mark.parametrize('kind',['symlink','hardlink','traversal'])
def test_source_archive_rejects_links_and_traversal(tmp_path,kind):
    folder=tmp_path/'reproducibility';folder.mkdir();archive=folder/'source.tar.gz';sid='a'*24
    with tarfile.open(archive,'w:gz') as stream:
        entry=tarfile.TarInfo('../outside' if kind=='traversal' else f'artifacts/binding/sources/{sid}/unsafe')
        if kind!='traversal':entry.type=tarfile.SYMTYPE if kind=='symlink' else tarfile.LNKTYPE;entry.linkname='/tmp/outside'
        stream.addfile(entry,io.BytesIO(b''))
    (folder/'frozen_sources.json').write_text(json.dumps([dict(snapshot_id=sid,stored_path='reproducibility/source.tar.gz',sha256=module.sha(archive))]))
    with pytest.raises(ValueError):module.restore_sources(tmp_path)
    assert not (tmp_path/'outside').exists()


def test_credential_detection_never_echoes_credential(tmp_path):
    secret='ghp_'+'X'*36;path=tmp_path/'sample.json';path.write_text(secret)
    with pytest.raises(ValueError) as exc:module.scan_secret(path)
    assert secret not in str(exc.value)
