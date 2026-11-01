#!/usr/bin/env python
"""Incrementally publish probe-improvement evidence under existing array policy."""
import argparse
import csv
from datetime import datetime, timezone
import gzip
import importlib.util
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('binding_export', ROOT / 'scripts/export_binding_repository.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
ROOTS = ['artifacts/binding/arithmetic_probe_selection/20261030_v1',
         'artifacts/binding/arithmetic_probe_selection/20261030_v2',
         'artifacts/binding/arithmetic_local/20261030_v1',
         'artifacts/binding/arithmetic_state_followup/20261030_v1',
         'artifacts/binding/arithmetic_state_followup/20261030_v2',
         'artifacts/binding/arithmetic_state_diagnostics/20261031_v1',
         'artifacts/binding/arithmetic_numeric_exploration/20261031_v1',
         'artifacts/binding/arithmetic_next_runs/20261031_v1',
         'artifacts/binding/arithmetic_numeric_geometry/20261031_v1']
NUMERIC_ROOT = 'artifacts/binding/arithmetic_numeric_exploration/20261031_v1'
ROOTS += [NUMERIC_ROOT + '/' + name for name in (
    'llama8b_root_definition', 'llama8b_computed_definition',
    'codellama34b_root_definition', 'codellama34b_computed_definition',
    'source_root_definition', 'source_computed_definition')]
GEOMETRY_ROOT = 'artifacts/binding/arithmetic_numeric_geometry/20261031_v1'
ROOTS += [GEOMETRY_ROOT + '/' + name for name in (
    'llama8b_root_definition', 'llama8b_computed_definition',
    'codellama34b_root_definition', 'codellama34b_computed_definition',
    'source4096_root_definition', 'source4096_computed_definition',
    'source8192_root_definition', 'source8192_computed_definition',
    'llama8b_query_cache', 'codellama34b_query_cache')]
SEMANTIC_ROOTS = tuple(f'artifacts/binding/arithmetic_semantic_controls/20261031_v{edition}' for edition in (1, 2))
ROOTS += list(SEMANTIC_ROOTS)
ROOTS += [root + '/' + name for root in SEMANTIC_ROOTS for name in (
    'labels', 'llama8b_computed_definition', 'codellama34b_computed_definition',
    'source4096_computed_definition', 'source8192_computed_definition')]
GLOBAL_ROOT = 'artifacts/binding/arithmetic_global_state/20261031_v1'
ROOTS += [GLOBAL_ROOT] + [GLOBAL_ROOT + '/' + name for name in (
    'cache', 'llama8b_width1024', 'llama8b_width4096', 'codellama34b_width1024',
    'codellama34b_width8192', 'source_width1024', 'source_width4096', 'source_width8192')]
PAIRED_ROOT = 'artifacts/binding/arithmetic_paired/20261101_v1'
ROOTS += [PAIRED_ROOT] + [PAIRED_ROOT + '/' + name for name in (
    'sources', 'llama8b_native', 'codellama34b_native', 'llama8b_calibration', 'codellama34b_calibration')]
EXPLORATION_ROOTS = tuple(f'artifacts/binding/arithmetic_paired_exploration/20261101_v{edition}' for edition in (1, 2))
ROOTS += list(EXPLORATION_ROOTS)
ROOTS += [root + '/' + name for root in EXPLORATION_ROOTS for name in (
    'error_audit', 'audit_report', 'llama8b_continuation', 'codellama34b_continuation', 'report')]
ROOTS += ['artifacts/binding/arithmetic_capture_preparation/20261101_v1']
CONDITIONAL_ROOT = 'artifacts/binding/arithmetic_conditional/20261101_v1'
ROOTS += [CONDITIONAL_ROOT] + [CONDITIONAL_ROOT + '/' + name for name in (
    'source_source1024', 'source_source2048', 'llama8b_hidden', 'llama8b_joint', 'llama8b_shuffled_joint',
    'codellama34b_hidden', 'codellama34b_joint', 'codellama34b_shuffled_joint')]
PENALTY_ROOT = 'artifacts/binding/arithmetic_penalty_path/20261101_v1'
ROOTS += [PENALTY_ROOT] + [PENALTY_ROOT + '/' + name for name in (
    'priors', 'source_source1024', 'source_source2048', 'llama8b_hidden', 'llama8b_joint', 'llama8b_shuffled_joint',
    'codellama34b_hidden', 'codellama34b_joint', 'codellama34b_shuffled_joint')]
MUTABLE = {'manifest.json', 'progress.json', 'jobs_live_v1.json', 'status_review_v1.json'}


def archive(folder, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + '.pending')
    with temporary.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0, compresslevel=6) as zipped:
            with tarfile.open(fileobj=zipped, mode='w|') as tar:
                for path in sorted(folder.rglob('*')):
                    if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts:
                        continue
                    export.scan_secret(path)
                    info = tar.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    info.mtime = 0
                    with path.open('rb') as stream:
                        tar.addfile(info, stream)
    if target.exists() and export.sha(target) != export.sha(temporary):
        raise ValueError('existing source archive differs: ' + str(target))
    temporary.replace(target)
    return dict(path=str(target.relative_to(ROOT)), bytes=target.stat().st_size, sha256=export.sha(target))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, required=True)
    parser.add_argument('--only-root', action='append', choices=ROOTS,
        help='Publish this root and registered subroots; omitted roots retain their existing catalog entries')
    args = parser.parse_args()
    edition = args.edition
    roots = ROOTS if not args.only_root else [r for r in ROOTS if any(r == p or r.startswith(p + '/') for p in args.only_root)]
    proof_path = ROOT / f'reproducibility/arithmetic_probe_publication_20261030_v{edition}.json'
    if edition < 1 or proof_path.exists():
        raise ValueError('a new positive publication edition is required')
    source_catalog = ROOT / 'reproducibility/frozen_sources.json'
    sources = {e['snapshot_id']: e for e in json.loads(source_catalog.read_text())}
    compressed_catalog = ROOT / 'reproducibility/compressed_artifacts.csv'
    with compressed_catalog.open() as stream:
        compressed = {e['original_path']: e for e in csv.DictReader(stream)}
    local_catalog = ROOT / 'reproducibility/local_payload_inventory.csv'
    with local_catalog.open() as stream:
        local = {e['path']: e for e in csv.DictReader(stream)}
    paths, pins, source_ids, archives = set(), {}, set(), []
    for relative in roots:
        folder = ROOT / relative
        for path in sorted(folder.rglob('*')):
            if (path.name.startswith(('.', 'attempt_live_')) or '.pending.' in path.name
                    or path.name.endswith(('.pending', '.tmp'))):
                continue
            if not path.is_file() or '__pycache__' in path.parts or 'regression_sources' in path.parts or 'saved_work_prefix' in path.parts:
                continue
            name = str(path.relative_to(ROOT))
            if path.is_symlink():
                expected = Path('/scratch/juno/jvl210002/codecue/arithmetic_numeric_exploration/20261031_v1/caches')
                if relative == NUMERIC_ROOT and path.suffix in export.RAW and path.resolve().is_relative_to(expected):
                    local[name] = dict(path=name, bytes=path.stat().st_size, reason='raw array relocated to verified scratch storage; original hash-pinned path retained')
                continue
            if path.suffix in export.RAW:
                local[name] = dict(path=name, bytes=path.stat().st_size, reason='raw array/model/dependency or transient state')
                continue
            if path.name in MUTABLE or path.name.startswith('.') or path.suffix not in export.TEXT:
                continue
            export.scan_secret(path)
            # Git cannot track children of the scratch-backed directory links.
            # Publish their immutable text through the existing lossless gzip
            # catalog, whose restore command recreates original artifact paths.
            if path.suffix == '.jsonl' or relative.startswith(tuple(root + '/' for root in (NUMERIC_ROOT, GEOMETRY_ROOT, GLOBAL_ROOT, PAIRED_ROOT, CONDITIONAL_ROOT, PENALTY_ROOT, *SEMANTIC_ROOTS, *EXPLORATION_ROOTS))):
                target = ROOT / 'reproducibility/compressed' / (name + '.gz')
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('wb') as raw:
                    with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0, compresslevel=6) as stream, path.open('rb') as data:
                        while chunk := data.read(1024**2):
                            stream.write(chunk)
                entry = dict(original_path=name, stored_path=str(target.relative_to(ROOT)), encoding='gzip',
                    original_bytes=path.stat().st_size, stored_bytes=target.stat().st_size,
                    original_sha256=export.sha(path), stored_sha256=export.sha(target))
                if name in compressed and compressed[name]['original_sha256'] != entry['original_sha256']:
                    raise ValueError('previously published scientific text changed')
                with gzip.open(target, 'rb') as data:
                    import hashlib
                    hasher = hashlib.sha256()
                    for chunk in iter(lambda: data.read(1024**2), b''):
                        hasher.update(chunk)
                if hasher.hexdigest() != entry['original_sha256']:
                    raise ValueError('compressed roundtrip differs')
                compressed[name] = entry
                paths.add(entry['stored_path'])
                pins[name] = dict(sha256=entry['original_sha256'], stored_path=entry['stored_path'])
            else:
                paths.add(name)
                pins[name] = dict(sha256=export.sha(path))
            if path.name == 'source_review_v1.json':
                source_ids.add(json.loads(path.read_text())['snapshot_id'])
        mirror = folder / 'regression_sources'
        if mirror.exists():
            label = 'local' if '/arithmetic_local/' in relative else 'selection'
            if '/arithmetic_penalty_path/' in relative:
                filename = f'arithmetic_penalty_path_regression_{folder.name}.tar.gz'
            elif '/arithmetic_conditional/' in relative:
                filename = f'arithmetic_conditional_regression_{folder.name}.tar.gz'
            elif '/arithmetic_paired_exploration/' in relative:
                filename = f'arithmetic_paired_exploration_regression_{folder.name}.tar.gz'
            elif '/arithmetic_paired/' in relative:
                filename = f'arithmetic_paired_regression_{folder.name}.tar.gz'
            elif '/arithmetic_global_state/' in relative:
                filename = f'arithmetic_global_state_regression_{folder.name}.tar.gz'
            elif '/arithmetic_semantic_controls/' in relative:
                filename = f'arithmetic_semantic_controls_regression_{folder.name}.tar.gz'
            elif '/arithmetic_numeric_geometry/' in relative:
                filename = f'arithmetic_numeric_geometry_regression_{folder.name}.tar.gz'
            elif '/arithmetic_numeric_exploration/' in relative:
                filename = f'arithmetic_numeric_exploration_regression_{folder.name}.tar.gz'
            elif '/arithmetic_state_followup/' in relative:
                filename = f'arithmetic_state_regression_{folder.name}.tar.gz'
            else:
                filename = f'arithmetic_probe_regression_{label}_20261030_v1.tar.gz'
            item = archive(mirror, ROOT / 'reproducibility' / filename)
            archives.append(item)
            paths.add(item['path'])
    for identity in sorted(source_ids):
        folder = ROOT / 'artifacts/binding/sources' / identity
        item = archive(folder, ROOT / f'reproducibility/frozen_sources/{identity}.tar.gz')
        sources[identity] = dict(snapshot_id=identity, stored_path=item['path'], bytes=item['bytes'], sha256=item['sha256'])
        paths.add(item['path'])
    # Catch a newly registered scratch-backed family before issuing a stage list.
    for name in paths:
        path = ROOT / name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError('publication path traverses a symbolic link: ' + name)
    export.atomic(source_catalog, (json.dumps(sorted(sources.values(), key=lambda e: e['snapshot_id']), sort_keys=True, indent=2) + '\n').encode())
    fields = ['original_path', 'stored_path', 'encoding', 'original_bytes', 'stored_bytes', 'original_sha256', 'stored_sha256']
    export.atomic(compressed_catalog, export.csv_bytes(sorted(compressed.values(), key=lambda e: e['original_path']), fields))
    export.atomic(local_catalog, export.csv_bytes(sorted(local.values(), key=lambda e: e['path']), ['path', 'bytes', 'reason']))
    proof = dict(status='published_metadata', recorded_utc=datetime.now(timezone.utc).isoformat(),
        source_ids=sorted(source_ids), published_roots=roots, artifacts=pins, regression_archives=archives,
        policy='Raw arrays remain local; source and immutable metadata published; JSONL and scratch-backed worker text losslessly compressed. Mutable live state excluded.',
        new_model_queries=0, new_fits=0, credentials_detected=0)
    export.atomic(proof_path, (json.dumps(proof, sort_keys=True, indent=2) + '\n').encode())
    paths.update(str(p.relative_to(ROOT)) for p in [source_catalog, compressed_catalog, local_catalog, proof_path])
    export.atomic(ROOT / '.git/probe_improvement_publication_paths', b'\0'.join(p.encode() for p in sorted(paths)) + b'\0')
    print(json.dumps(dict(status='published_metadata', files=len(paths), source_ids=sorted(source_ids))))


if __name__ == '__main__':
    main()
