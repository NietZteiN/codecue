"""Descriptive prediction-prior control for counterfactual-compatible errors."""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from .datasets import read_jsonl,write_json


def shuffled_reference(responses,records,repetitions=1000,seed=17):
    if repetitions<1:
        raise ValueError('positive reference repetitions required')
    if any(r['split'] not in ('train','development') for r in responses):
        raise ValueError('diagnostic reference cannot inspect test outcomes')
    units=defaultdict(dict)
    labels=sorted({d['label'] for r in responses for d in records[r['id']]['diagnostic_counterfactuals']})
    kinds=sorted({r['control_kind'] for r in responses})
    for row in responses:
        key=(row['control_kind'],row['condition'],row['lexical_realization'])
        if key in units[row['base_id']]:
            raise ValueError('duplicate base/condition/lexical/control response')
        units[row['base_id']][key]=row
    expected={(kind,condition,lexical) for kind in kinds
              for condition in ('neutral','informative','misleading') for lexical in (0,1)}
    if any(set(rows)!=expected for rows in units.values()):
        raise ValueError('reference requires balanced complete naming/control vectors per base')
    strata=defaultdict(list)
    for base,rows in units.items():
        row=next(iter(rows.values()))
        if any(any(r[k]!=row[k] for k in ('family','load','updates','split')) for r in rows.values()):
            raise ValueError('inconsistent factorial metadata within base')
        strata[(row['family'],row['load'],row['updates'],row['split'])].append(base)
    endpoints=[(kind,label) for kind in kinds for label in labels]
    observed=np.zeros(len(endpoints))
    null=np.zeros((repetitions,len(endpoints)))
    totals=np.array([sum(r['control_kind']==kind for r in responses) for kind,_ in endpoints])
    rng=np.random.default_rng(seed)
    permutable=set()
    for bases in strata.values():
        bases=sorted(bases)
        n=len(bases)
        if n>1:
            permutable.update(bases)
        # Each donor contributes its complete six-name vector for every task.
        # The same base permutation is shared across endpoints and control kinds.
        matrices=np.zeros((len(endpoints),n,n))
        for i,target in enumerate(bases):
            for j,donor in enumerate(bases):
                for key,row in units[target].items():
                    record=records[row['id']]
                    prediction=units[donor][key]['prediction']
                    if prediction is None or prediction==record['expected_answer']:
                        continue
                    compatible={d['label'] for d in record['diagnostic_counterfactuals'] if d['expected_answer']==prediction}
                    for endpoint,(kind,label) in enumerate(endpoints):
                        matrices[endpoint,i,j]+=float(key[0]==kind and label in compatible)
        observed+=np.einsum('eii->e',matrices)
        for repetition in range(repetitions):
            order=rng.permutation(n)
            null[repetition]+=matrices[:,np.arange(n),order].sum(axis=1)
    result=[]
    for column,(kind,label) in enumerate(endpoints):
        values=null[:,column]/totals[column]
        actual=observed[column]/totals[column]
        result.append({'control_kind':kind,'label':label,'n':int(totals[column]),
                       'observed_count':int(observed[column]),'observed_rate':float(actual),
                       'shuffled_mean_rate':float(values.mean()),
                       'shuffled_reference95':np.percentile(values,[2.5,97.5]).tolist(),
                       'observed_minus_shuffled_mean':float(actual-values.mean())})
    return {'endpoints':result,'repetitions':repetitions,'seed':seed,'bases':len(units),
            'permutable_bases':len(permutable),'singleton_strata':sum(len(x)==1 for x in strata.values()),
            'stratification':['family','load','updates','split'],
            'unit':'complete base prediction vector, retaining naming, lexical and task pairing',
            'interpretation':'descriptive within-cohort output-prior reference; not a mechanistic test, population CI or multiplicity-adjusted significance test',
            'limitations':'numeric bases can share parent templates; singleton strata cannot vary; prompt/confidence effects within a cell remain uncontrolled'}


def run(config):
    run_dir=Path(config['run_dir'])
    behavior=run_dir/'behavior'
    manifest=json.loads((behavior/'manifest.json').read_text())
    if manifest['status']!='complete':
        raise ValueError('complete discovery behavior required')
    data=Path(config['dataset'])
    if hashlib.sha256(data.read_bytes()).hexdigest()!=manifest['identity']['dataset_manifest']['sha256']:
        raise ValueError('diagnostic reference dataset differs from behavior')
    rows=read_jsonl(behavior/'responses.jsonl')
    records={r['id']:r for r in read_jsonl(data)}
    if any(records[r['id']]['split'] not in ('train','development') for r in rows):
        raise ValueError('diagnostic reference cannot inspect test outcomes')
    result=shuffled_reference(rows,records)
    result['behavior_identity_hash']=manifest['identity_hash']
    result['responses_sha256']=hashlib.sha256((behavior/'responses.jsonl').read_bytes()).hexdigest()
    result['dataset_sha256']=manifest['identity']['dataset_manifest']['sha256']
    from .registry import code_identity
    result['analysis_source_sha256']=code_identity()['source_sha256']
    out=run_dir/'diagnostic_null.json'
    if out.exists():
        raise ValueError('diagnostic reference is immutable; choose a separate analysis artifact')
    write_json(out,result)
    return {'artifact':str(out),'endpoints':result['endpoints']}
