#!/usr/bin/env python
"""Run the fresh training bank only when the fixed prompt calibration passes."""
import copy
import hashlib
import json
import sys
from pathlib import Path
from codecue.binding.calibration import choose_variant,run
from codecue.binding.datasets import write_json

config=json.loads(Path(sys.argv[1]).read_text())
summary_path=Path(config['calibration']['selector_summary'])
out=Path(config['run_dir'])
out.mkdir(parents=True,exist_ok=True)
decision=out/'pipeline_decision.json'
if decision.exists():
    raise ValueError('calibration selection is immutable')
result={'status':'skipped','heldout_outcomes_opened':False,
        'rule':'At least 7/8 primitive and 2/4 training correct, all 12 parsed; direct protocol preferred if both pass'}
if not summary_path.exists():
    result['reason']='fixed-suite summary unavailable; no model run'
else:
    summary=json.loads(summary_path.read_text())
    manifest=json.loads(summary_path.with_name('manifest.json').read_text())
    result['selector_summary_sha256']=hashlib.sha256(summary_path.read_bytes()).hexdigest()
    result['selector_identity_hash']=manifest['identity_hash']
    if manifest['identity']['model_revision']!=config['model_revision']:
        raise ValueError('calibration checkpoint changed')
    selected=choose_variant(summary) if manifest['status']=='complete' else None
    if selected is None:
        result['reason']='no prompt meets the predeclared completed-suite gate; no model run'
    else:
        effective=copy.deepcopy(config)
        effective['calibration']['variants']=[selected]
        effective['calibration']['selector_summary_sha256']=result['selector_summary_sha256']
        effective['calibration']['selector_identity_hash']=result['selector_identity_hash']
        effective['run_dir']=str(out/selected)
        result.update(status='selected_training_calibration',variant=selected,effective_config=effective)
        write_json(out/'effective_config.json',effective)
write_json(decision,result)
if result['status']=='selected_training_calibration':
    result['bank_result']=run(result['effective_config'])
    write_json(out/'bank_result.json',result)
print(json.dumps(result,indent=2))
