#!/usr/bin/env python3
"""Publish compact binding-study evidence and restore its lossless archives.

Original scientific files are never rewritten by export. Raw array payloads,
installed dependencies and live logging state stay local and are inventoried.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TEXT = {'.json','.jsonl','.csv','.xml','.txt','.md','.py','.sh','.log'}
RAW = {'.npz','.npy','.pt','.pth','.safetensors','.bin','.whl','.so','.sqlite3','.lock'}
SECRET = [re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
          re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'),
          re.compile(rb'hf_[A-Za-z0-9]{30,}'),
          re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()


def atomic(path,payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        temp=Path(stream.name);stream.write(payload);stream.flush();os.fsync(stream.fileno())
    temp.replace(path)


def csv_bytes(rows,fields):
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    return stream.getvalue().encode()


def safe_target(root,relative):
    value=PurePosixPath(relative)
    if value.is_absolute() or '..' in value.parts or not value.parts or value.parts[:2]!=('artifacts','binding'):
        raise ValueError('Restore path must remain under artifacts/binding')
    path=root.joinpath(*value.parts)
    for part in (path,*path.parents):
        if part==root:break
        if part.is_symlink():raise ValueError('Restore must not follow symbolic links')
    return path


def scan_secret(path):
    previous=b''
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):
            value=previous+chunk
            if any(pattern.search(value) for pattern in SECRET):
                raise ValueError('Potential credential in publication input: '+str(path))
            previous=value[-256:]


def restore_bytes(path,data,expected):
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Restored checksum differs')
    if path.exists():
        if sha(path)!=expected:raise ValueError('Refusing to overwrite a different existing file')
        return 'already_present'
    atomic(path,data);return 'restored'


def export(root,workers=4):
    destination=root/'reproducibility';destination.mkdir(exist_ok=True)
    direct=[];compressed=[];local=[];source_folders=[]
    for folder,dirs,files in os.walk(root/'artifacts/binding'):
        here=Path(folder)
        for name in list(dirs):
            path=here/name
            if name in ('__pycache__','.git','literature','experiment_log','vllm-cu129-0.26.0'):
                local.append(dict(path=str(path.relative_to(root)),bytes='',reason='local dependency/cache/live state'));dirs.remove(name)
            elif path==root/'artifacts/binding/sources':
                source_folders=sorted(p for p in path.iterdir() if p.is_dir() and not p.name.endswith('.staging'));dirs.remove(name)
        for name in sorted(files):
            path=here/name;relative=str(path.relative_to(root));size=path.stat().st_size
            if path.is_symlink():local.append(dict(path=relative,bytes=size,reason='symbolic link'));continue
            if path.suffix in RAW or name.startswith('.') or name.endswith(('.tmp','.pending','.lock')):
                local.append(dict(path=relative,bytes=size,reason='raw array/model/dependency or transient state'));continue
            # Source and metadata are publishable; reserved outcome payloads stay sealed.
            if any(part.lower() in {'heldout','holdout','sealed','final','reserved'} for part in path.relative_to(root/'artifacts/binding').parts[:-1]):
                local.append(dict(path=relative,bytes=size,reason='reserved evaluation directory'));continue
            if path.suffix=='.jsonl' or (path.suffix in TEXT and size>8*1024**2):compressed.append(path)
            elif size>=100*1024**2:local.append(dict(path=relative,bytes=size,reason='large binary payload'))
            else:direct.append(path)
    def compress(path):
        scan_secret(path)
        target=destination/'compressed'/Path(str(path.relative_to(root))+'.gz');target.parent.mkdir(parents=True,exist_ok=True)
        before=(path.stat().st_size,path.stat().st_mtime_ns);digest=hashlib.sha256()
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as raw:
            temporary=Path(raw.name)
            with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=6) as output,path.open('rb') as source:
                for chunk in iter(lambda:source.read(1024**2),b''):digest.update(chunk);output.write(chunk)
        if before!=(path.stat().st_size,path.stat().st_mtime_ns):
            temporary.unlink();raise ValueError('Publication source changed during compression: '+str(path))
        temporary.replace(target)
        if target.stat().st_size>=100*1024**2:raise ValueError('Compressed artifact still exceeds GitHub file limit: '+str(target))
        return dict(original_path=str(path.relative_to(root)),stored_path=str(target.relative_to(root)),encoding='gzip',original_bytes=before[0],stored_bytes=target.stat().st_size,original_sha256=digest.hexdigest(),stored_sha256=sha(target))
    entries=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for index,row in enumerate(pool.map(compress,sorted(compressed)),1):
            entries.append(row)
            if index%25==0:print(json.dumps(dict(compressed=index,total=len(compressed))),flush=True)
    snapshot_entries=[]
    for index,folder in enumerate(source_folders,1):
        target=destination/'frozen_sources'/f'{folder.name}.tar.gz';target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as raw:
            temporary=Path(raw.name)
            with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=6) as zipped,tarfile.open(fileobj=zipped,mode='w|') as archive:
                for path in sorted(folder.rglob('*')):
                    if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts:continue
                    scan_secret(path)
                    info=archive.gettarinfo(str(path),arcname=str(path.relative_to(root)))
                    info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                    with path.open('rb') as stream:archive.addfile(info,stream)
        temporary.replace(target)
        if target.stat().st_size>=100*1024**2:raise ValueError('Source archive exceeds GitHub file limit')
        snapshot_entries.append(dict(snapshot_id=folder.name,stored_path=str(target.relative_to(root)),bytes=target.stat().st_size,sha256=sha(target)))
        if index%10==0:print(json.dumps(dict(source_snapshots=index,total=len(source_folders))),flush=True)
    for path in direct:
        if path.suffix in TEXT:scan_secret(path)
    atomic(destination/'compressed_artifacts.csv',csv_bytes(sorted(entries,key=lambda x:x['original_path']),['original_path','stored_path','encoding','original_bytes','stored_bytes','original_sha256','stored_sha256']))
    atomic(destination/'local_payload_inventory.csv',csv_bytes(sorted(local,key=lambda x:x['path']),['path','bytes','reason']))
    atomic(destination/'frozen_sources.json',(json.dumps(snapshot_entries,sort_keys=True,indent=2)+'\n').encode())
    snapshots=destination/'experiment_log_snapshot';snapshots.mkdir(exist_ok=True)
    for name in ('experiments.csv','index_summary.json'):
        source=root/'artifacts/binding/experiment_log'/name
        if source.exists():atomic(snapshots/name,source.read_bytes())
    report=dict(status='complete',direct_artifact_files=len(direct),compressed_artifacts=len(entries),original_compressed_bytes=sum(x['original_bytes'] for x in entries),stored_compressed_bytes=sum(x['stored_bytes'] for x in entries),frozen_source_snapshots=len(snapshot_entries),stored_source_bytes=sum(x['bytes'] for x in snapshot_entries),local_only_items=len(local),local_only_file_bytes=sum(x['bytes'] for x in local if isinstance(x['bytes'],int)),credentials_detected=0,new_model_queries=0,new_fits=0)
    atomic(destination/'export_review.json',(json.dumps(report,sort_keys=True,indent=2)+'\n').encode())
    git_paths=[str(p.relative_to(root)) for p in direct]+[str(p.relative_to(root)) for p in destination.rglob('*') if p.is_file()]
    atomic(root/'.git/binding_publication_paths',b'\0'.join(p.encode() for p in sorted(git_paths))+b'\0')
    print(json.dumps(report,sort_keys=True),flush=True)


def restore(root,match=None):
    catalogue=root/'reproducibility/compressed_artifacts.csv';counts={'restored':0,'already_present':0}
    with catalogue.open() as stream:
        for row in csv.DictReader(stream):
            if match and match not in row['original_path']:continue
            target=safe_target(root,row['original_path']);source=root/row['stored_path']
            if not source.resolve().is_relative_to(root/'reproducibility') or source.is_symlink():raise ValueError('Invalid stored artifact path')
            if sha(source)!=row['stored_sha256']:raise ValueError('Stored checksum differs')
            # Stream large restored JSONL files without loading them into memory.
            if target.exists():
                if sha(target)!=row['original_sha256']:raise ValueError('Refusing to overwrite a different existing file')
                counts['already_present']+=1;continue
            target.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as output:
                temp=Path(output.name);digest=hashlib.sha256();size=0
                with gzip.open(source,'rb') as data:
                    for chunk in iter(lambda:data.read(1024**2),b''):
                        size+=len(chunk)
                        if size>int(row['original_bytes']):
                            temp.unlink();raise ValueError('Restored file exceeds its declared size')
                        digest.update(chunk);output.write(chunk)
            if size!=int(row['original_bytes']) or digest.hexdigest()!=row['original_sha256']:
                temp.unlink();raise ValueError('Restored checksum differs')
            temp.replace(target);counts['restored']+=1
    print(json.dumps(counts,sort_keys=True))


def restore_sources(root,match=None):
    counts={'restored':0,'already_present':0}
    for row in json.loads((root/'reproducibility/frozen_sources.json').read_text()):
        if match and match not in row['snapshot_id']:continue
        source=root/row['stored_path']
        if sha(source)!=row['sha256']:raise ValueError('Source archive checksum differs')
        with tarfile.open(source,'r:gz') as archive:
            for member in archive:
                if not member.isfile() or member.size>128*1024**2:raise ValueError('Only bounded regular source files may be restored')
                target=safe_target(root,member.name)
                if not str(target.relative_to(root)).startswith('artifacts/binding/sources/'+row['snapshot_id']+'/'):raise ValueError('Wrong source snapshot path')
                data=archive.extractfile(member).read();counts[restore_bytes(target,data,hashlib.sha256(data).hexdigest())]+=1
    print(json.dumps(counts,sort_keys=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['export','restore','restore-sources']);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--match');parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();root=args.root.resolve()
    if args.command=='export':export(root,args.workers)
    elif args.command=='restore':restore(root,args.match)
    else:restore_sources(root,args.match)


if __name__=='__main__':main()
