#!/usr/bin/env python
"""Entry points for the explicitly authorized second research phase."""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('command',choices=['audit','audit-boundary','validate-boundary','build-diagnostics','run-diagnostics','program-status','audit-saved-tokens','review-diagnostics','build-counterbalanced'])
parser.add_argument('config')
args=parser.parse_args()
config=json.loads(Path(args.config).read_text())
if args.command=='audit':
    from codecue.binding.checkpoint_audit import run
    result=run(config)
elif args.command=='audit-boundary':
    from codecue.binding.checkpoint_audit import audit_boundary
    result=audit_boundary(config)
elif args.command=='validate-boundary':
    import copy
    import hashlib
    from codecue.binding.diagnostics import run
    from codecue.binding.datasets import write_json
    for name in ('checkpoint_audit','boundary_audit'):
        path=Path(config[name])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=config[name+'_sha256']:
            raise ValueError('boundary validation audit provenance changed')
    integrity=json.loads(Path(config['checkpoint_audit']).read_text())
    boundary=json.loads(Path(config['boundary_audit']).read_text())
    if not all(r['match'] for r in integrity['files']) or boundary['status']!='passed':
        raise ValueError('checkpoint and tokenizer audit must pass before inference')
    result={}
    for mode in ('native','codellama_official_boundary_v1'):
        effective=copy.deepcopy(config)
        effective.update(run_dir=str(Path(config['run_dir'])/mode),tokenization_mode=mode)
        result[mode]=run(effective)
    write_json(Path(config['run_dir'])/'comparison.json',result)
    result={mode:{key:value for key,value in data.items() if key!='responses_by_batch_size'} for mode,data in result.items()}
elif args.command=='build-diagnostics':
    from codecue.binding.program_diagnostics import build
    result=build(config)
elif args.command=='run-diagnostics':
    from codecue.binding.calibration import run
    from codecue.binding.program_diagnostics import summarize
    if config.get('tokenization_mode')!='codellama_official_boundary_v1':
        raise ValueError('phase-two diagnostics require the verified reference boundary')
    run(config)
    result=summarize(config)
elif args.command=='program-status':
    from codecue.binding.research_program import status
    result=status(config)
elif args.command=='audit-saved-tokens':
    from codecue.binding.checkpoint_audit import audit_saved_tokens
    result=audit_saved_tokens(config)
elif args.command=='review-diagnostics':
    from codecue.binding.diagnostic_review import review
    result=review(config)
elif args.command=='build-counterbalanced':
    from codecue.binding.diagnostic_review import build_counterbalanced
    result=build_counterbalanced(config)
print(json.dumps(result,indent=2))
