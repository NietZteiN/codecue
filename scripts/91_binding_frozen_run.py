#!/usr/bin/env python
"""Verify a frozen package, then execute its module or captured entrypoint."""
import argparse
import os
from pathlib import Path
import runpy
import sys

parser=argparse.ArgumentParser()
parser.add_argument('snapshot')
parser.add_argument('entrypoint', help='module or a captured scripts/... path')
parser.add_argument('args', nargs=argparse.REMAINDER)
args=parser.parse_args()
snapshot=Path(args.snapshot).resolve()
sys.path.insert(0,str(snapshot/'src'))
from codecue.binding.snapshots import verify
manifest=verify(snapshot)
os.environ['PYTHONPATH']=str(snapshot/'src')
os.chdir(manifest['workspace_root'])
if args.entrypoint=='module':
    sys.argv=['codecue.binding',*args.args]
    runpy.run_module('codecue.binding',run_name='__main__')
else:
    if args.entrypoint not in manifest['code']['source_files'] or not args.entrypoint.startswith('scripts/'):
        raise ValueError('entrypoint must be a captured script')
    path=snapshot/args.entrypoint
    sys.argv=[str(path),*args.args]
    runpy.run_path(str(path),run_name='__main__')
