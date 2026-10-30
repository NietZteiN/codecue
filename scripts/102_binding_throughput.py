#!/usr/bin/env python
"""Profile installed GPU backends and validate the fastest completion pipeline."""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys


def configure_runtime(config):
    if config.get('cuda_home'):
        os.environ['CUDA_HOME'] = config['cuda_home']
        os.environ['PATH'] = str(Path(config['cuda_home']) / 'bin') + os.pathsep + os.environ.get('PATH', '')
    if 'flashinfer_sampler' in config:
        os.environ['VLLM_USE_FLASHINFER_SAMPLER'] = '1' if config['flashinfer_sampler'] else '0'
    if not config.get('runtime_manifest'):
        return
    path = Path(config['runtime_manifest'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != config['runtime_manifest_sha256']:
        raise ValueError('isolated runtime manifest checksum mismatch')
    runtime = json.loads(path.read_text())
    root = runtime['package_root']
    if not (Path(root) / 'vllm/__init__.py').exists():
        raise ValueError('isolated runtime is missing')
    sys.path.insert(0, root)
    os.environ['PYTHONPATH'] = root + os.pathsep + os.environ.get('PYTHONPATH', '')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('preflight', 'run', 'worker'))
    parser.add_argument('config')
    parser.add_argument('spec', nargs='?')
    parser.add_argument('output', nargs='?')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    configure_runtime(config)
    if args.command == 'preflight':
        if config.get('runtime_manifest'):
            import torch
            binary = importlib.import_module('vllm._C_stable_libtorch')
            from codecue.binding.datasets import write_json
            write_json(Path(config['preflight_result']).with_name('runtime_preflight.json'),
                       {'status': 'passed', 'vllm': importlib.metadata.version('vllm'),
                        'torch': torch.__version__, 'torch_cuda': torch.version.cuda,
                        'binary': binary.__file__})
        from codecue.binding.published_benchmarks import preflight
        result = preflight(config)
    elif args.command == 'worker':
        import codecue.binding.throughput as throughput
        if config.get('uuid_telemetry'):
            from codecue.binding.gpu_telemetry import UUIDMonitor
            throughput.Monitor = UUIDMonitor
        result = throughput.worker(config, json.loads(Path(args.spec).read_text()), Path(args.output))
    else:
        from codecue.binding.throughput import run
        result = run(config)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()  # vLLM starts CUDA engine subprocesses with Python spawn.
