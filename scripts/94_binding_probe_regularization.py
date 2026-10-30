#!/usr/bin/env python
"""Report a fixed ridge sensitivity grid on an existing sealed-discovery cache."""
import copy
import json
import sys
from pathlib import Path
from codecue.binding.datasets import write_json
from codecue.binding.probes import fit

config=json.loads(Path(sys.argv[1]).read_text())
grid=config['probe_analysis']['regularization_grid']
if grid!=[1,100,10000]:
    raise ValueError('this sensitivity predeclares [1,100,10000]; do not silently tune the grid')
output=[]
for alpha in grid:
    effective=copy.deepcopy(config)
    effective['probe_analysis'].update(alpha=alpha,output_stage=f'probes_alpha_{alpha}')
    result=fit(effective)
    curves=json.loads(Path(result['development_curves']).read_text())
    output.append({'alpha':alpha,'artifact':result['development_curves'],'results':curves['results']})
write_json(Path(config['run_dir'])/'regularization_sensitivity.json',{
    'status':'complete','selection':'none; full predeclared development grid, no final-test evaluation',
    'alpha_grid':grid,'analyses':output,
    'interpretation':'same decoder capacity and training-only preprocessing; regularization is a measurement sensitivity, not a discovered mechanism'})
print(json.dumps({'status':'complete','alpha_grid':grid}))
