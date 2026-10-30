"""Small nested failure forecasters, fitted on discovery and frozen before test.

Feature collection is deliberately external: the supported mechanism and query
budgets must be specified before representation/intervention features are used.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from .datasets import digest, read_jsonl, write_json
from .heldout import probability_scores

PREDICTORS = ('A_input','B_behavior','C_measurements','cheap_stress_test')
FORBIDDEN = {'correct','incorrect','target_label','expected_answer','prediction','raw_response'}


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x,-40,40)))


def fit_logistic(x, y, l2, *, max_iterations=100):
    if type(max_iterations) is not int or max_iterations < 1:
        raise ValueError('max_iterations must be a positive integer')
    x,y = np.asarray(x,dtype=float),np.asarray(y,dtype=float)
    if x.ndim != 2 or y.shape != (len(x),) or not len(x) or not np.isfinite(x).all() or not np.isin(y,[0,1]).all():
        raise ValueError('invalid training features or binary labels')
    if l2 <= 0 or len(np.unique(y)) < 2:
        raise ValueError('positive regularization and both training classes are required')
    mean,scale = x.mean(0), x.std(0).clip(1e-8)
    z = np.column_stack((np.ones(len(x)), (x-mean)/scale))
    beta = np.zeros(z.shape[1])
    beta[0] = np.log((y.sum()+.5)/(len(y)-y.sum()+.5))
    penalty = np.diag([0.] + [float(l2)]*x.shape[1])
    def objective(b):
        logits=z@b
        return float(np.sum(np.logaddexp(0,logits)-y*logits)+.5*b@penalty@b)
    converged = False
    for iteration in range(max_iterations):
        p = sigmoid(z@beta)
        gradient = z.T@(p-y)+penalty@beta
        hessian = z.T@((p*(1-p))[:,None]*z)+penalty
        step = np.linalg.solve(hessian,gradient)
        old = objective(beta)
        rate = 1.
        while rate > 1e-8 and objective(beta-rate*step) > old:
            rate *= .5
        beta -= rate*step
        if np.max(np.abs(rate*step)) < 1e-8:
            converged = True
            break
    if not converged:
        raise ValueError('logistic fit did not converge; inspect discovery data')
    return {'mean':mean.tolist(),'scale':scale.tolist(),'weights':beta.tolist(),
            'l2':float(l2),'iterations':iteration+1,'converged':True}


def predict(model,x):
    x = np.asarray(x,dtype=float)
    if x.ndim != 2 or x.shape[1] != len(model['mean']) or not np.isfinite(x).all():
        raise ValueError('prediction features do not match fitted dimensions')
    z=np.column_stack((np.ones(len(x)),(x-np.array(model['mean']))/np.array(model['scale'])))
    return sigmoid(z@np.array(model['weights']))


def validate_contract(contract):
    if set(contract) != set(PREDICTORS):
        raise ValueError('specify feature lists for all four registered predictors')
    for name,columns in contract.items():
        if not isinstance(columns,list) or not columns or len(set(columns)) != len(columns) or any(c in FORBIDDEN for c in columns):
            raise ValueError('feature lists must be unique, nonempty and exclude target outcomes')
    if not set(contract['A_input']) < set(contract['B_behavior']) < set(contract['C_measurements']):
        raise ValueError('A, B and C must be strictly nested feature sets')


def matrix(rows,columns):
    try:
        result=np.array([[r['features'][name] for name in columns] for r in rows],dtype=float)
    except (KeyError,TypeError,ValueError) as exc:
        raise ValueError('missing or nonnumeric declared feature') from exc
    if result.ndim != 2 or not np.isfinite(result).all():
        raise ValueError('declared features must be finite')
    return result


def _discovery_declaration(metadata):
    """Reject explicit reserved roles without requiring new legacy fields."""
    if not isinstance(metadata,dict):
        return
    role=str(metadata.get('evaluation_role','')).lower().replace('-','_')
    if (any(word in role for word in ('extrap','final','heldout','held_out','holdout','sealed'))
            or 'test' in role.split('_')):
        raise ValueError('forecaster fitting cannot open test or reserved outcomes')
    for key in ('split','split_override','splits'):
        if key not in metadata:
            continue
        splits=metadata[key] if isinstance(metadata[key],(list,tuple)) else [metadata[key]]
        if not splits or any(split not in ('train','development') for split in splits):
            raise ValueError('forecaster fitting cannot open test or non-discovery outcomes')
    for key in ('generation','config','dataset_manifest'):
        _discovery_declaration(metadata.get(key))
    for section in metadata.get('sections',[]):
        _discovery_declaration(section)


def _discovery_response_path(path):
    """Protect obvious reserved paths while allowing pytest test_* parents."""
    path=Path(path).resolve();parts=path.parts
    if 'binding' in parts:
        parts=parts[len(parts)-1-list(reversed(parts)).index('binding')+1:]
        markers=parts
    else:
        reserved={'test','final','heldout','held_out','holdout','sealed','extrap','extrapolation'}
        markers=[part for part in parts[:-1] if part.lower().replace('-','_') in reserved
                 or part.lower().startswith(('extrap_','extrapolation_','final_','heldout_','holdout_','sealed_'))]
        markers.append(path.name)
    if any(re.match(r'^(test|final|heldout|held_out|holdout|sealed|extrap(?:olation)?)(?:[_\-.]|$)',
                    part.lower()) for part in markers):
        raise ValueError('forecaster fitting cannot open test or reserved outcome paths')


def _discovery_inputs(config,study):
    """Check declarations and completed provenance before opening outcomes.

    Legacy mixed source datasets remain supported: their programs are not model
    outcomes. A legacy manifest without a split declaration cannot attest every
    response ID in advance, so fit also checks every observed ID after parsing.
    """
    _discovery_declaration(config)
    _discovery_response_path(study['discovery_responses'])
    dataset=Path(config['dataset']);sidecar=dataset.with_suffix('.manifest.json')
    dataset_manifest=json.loads(sidecar.read_text()) if sidecar.exists() else None
    if dataset_manifest is not None and not isinstance(dataset_manifest,dict):
        raise ValueError('discovery source dataset manifest must be an object')
    _discovery_declaration(dataset_manifest)
    rows=read_jsonl(dataset)
    records={row['id']:row for row in rows}
    if not rows or len(records)!=len(rows):
        raise ValueError('source dataset must contain unique discovery identities')
    discovery=[row for row in rows if row['split'] in ('train','development')]
    if not discovery:
        raise ValueError('forecaster fitting cannot open test outcomes; discovery source rows required')
    for row in discovery:
        _discovery_declaration(row)
    behavior_manifest=json.loads(Path(study['discovery_responses']).with_name('manifest.json').read_text())
    if not isinstance(behavior_manifest,dict) or behavior_manifest.get('status')!='complete':
        raise ValueError('complete discovery behavior is required for fitting')
    identity=behavior_manifest.get('identity')
    if (not isinstance(identity,dict) or not isinstance(behavior_manifest.get('identity_hash'),str)
            or not behavior_manifest['identity_hash']):
        raise ValueError('discovery behavior provenance is missing')
    _discovery_declaration(behavior_manifest)
    _discovery_declaration(identity)
    dataset_hash=hashlib.sha256(dataset.read_bytes()).hexdigest()
    if (not isinstance(identity.get('dataset_manifest'),dict)
            or identity['dataset_manifest'].get('sha256')!=dataset_hash
            or not config.get('model_revision')
            or identity.get('model_revision')!=config.get('model_revision')):
        raise ValueError('discovery behavior dataset or checkpoint mismatch')
    behavior_config=identity.get('config',{})
    if not isinstance(behavior_config,dict) or any(
            key in behavior_config and key in config and behavior_config[key]!=config[key]
            for key in ('model','model_revision')):
        raise ValueError('discovery behavior configuration checkpoint mismatch')
    if dataset_manifest is not None and dataset_manifest.get('sha256')!=dataset_hash:
        raise ValueError('discovery source dataset manifest hash mismatch')
    return records,behavior_manifest,dataset_hash


def fit(config):
    """Select regularization on development; never refit on dev or read test labels."""
    study=config['forecasting']
    contract=study['features']
    validate_contract(contract)
    records,behavior_manifest,dataset_hash=_discovery_inputs(config,study)
    raw=read_jsonl(study['discovery_responses'])
    if len({r['id'] for r in raw}) != len(raw):
        raise ValueError('duplicate discovery response IDs')
    if any(r['id'] not in records or records[r['id']]['split'] not in ('train','development') for r in raw):
        raise ValueError('forecaster fitting cannot open test outcomes')
    outcomes=[r for r in raw if records[r['id']]['control_kind']=='primary']
    features=read_jsonl(study['feature_table'])
    feature_by_id={r['id']:r for r in features}
    if len(feature_by_id) != len(features) or set(feature_by_id) != {r['id'] for r in outcomes}:
        raise ValueError('feature table must cover discovery primary responses exactly once')
    ids=sorted(feature_by_id)
    rows=[feature_by_id[i] for i in ids]
    observed={r['id']:r for r in outcomes}
    y=np.array([observed[i]['prediction'] != records[i]['expected_answer'] for i in ids],dtype=float)
    train=np.array([records[i]['split']=='train' for i in ids])
    dev=~train
    if not train.any() or not dev.any():
        raise ValueError('both train and development are required')
    clusters={split:{records[i]['cluster_id'] for i in ids if records[i]['split']==split}
              for split in ('train','development')}
    if clusters['train'] & clusters['development']:
        raise ValueError('parent-template leakage in forecaster split')
    grid=study['l2_grid']
    if not grid or len(set(grid)) != len(grid) or any(a<=0 for a in grid):
        raise ValueError('predeclare a positive regularization grid')
    result={'status':'discovery_fitted_not_registered','features':contract,'l2_grid':grid,
            'train_n':int(train.sum()),'development_n':int(dev.sum()),
            'selection':'minimum development Brier; tie uses first declared l2; no development refit',
            'source_dataset_sha256':dataset_hash,'model_revision':config['model_revision'],
            'behavior_identity_hash':behavior_manifest['identity_hash'],
            'feature_table_sha256':hashlib.sha256(Path(study['feature_table']).read_bytes()).hexdigest(),
            'responses_sha256':hashlib.sha256(Path(study['discovery_responses']).read_bytes()).hexdigest(),
            'models':{},'development_curves':{},'selected_development_probabilities':{}}
    from .registry import code_identity
    result['code_source_sha256']=code_identity()['source_sha256']
    from .analysis import interval
    for name in PREDICTORS:
        x=matrix(rows,contract[name])
        candidates=[]
        for alpha in grid:
            model=fit_logistic(x[train],y[train],alpha)
            probabilities=predict(model,x[dev])
            scores=probability_scores(probabilities,y[dev])
            candidates.append((scores['brier_score'],model,probabilities,scores))
        best=min(enumerate(candidates),key=lambda pair:(pair[1][0],pair[0]))[1]
        result['models'][name]=best[1]
        result['development_curves'][name]=[{'l2':c[1]['l2'],**c[3]} for c in candidates]
        result['selected_development_probabilities'][name]=best[2].tolist()
        result.setdefault('selected_development_intervals',{})[name]=interval(
            (best[2]-y[dev])**2,[records[i]['cluster_id'] for i,keep in zip(ids,dev) if keep])
    result['development_ids']=[i for i,keep in zip(ids,dev) if keep]
    result['interpretation']='development selection scores are optimistic; final scoring requires frozen registration and forecasts'
    out=Path(config['run_dir'])/'forecasters'
    out.mkdir(parents=True,exist_ok=True)
    path=out/'fit.json'
    if path.exists():
        raise ValueError('forecaster fit is immutable; choose a new run directory')
    write_json(path,result)
    return {'fit':str(path),'sha256':digest(result)}


def write_forecasts(config):
    """Registration binds the fitted model and feature contract before inference."""
    from .heldout import registration
    frozen,registration_hash=registration(config)
    fitted=json.loads(Path(config['forecasting']['fitted_model']).read_text())
    procedure=frozen['frozen_fitting_procedure']
    if not isinstance(procedure,dict) or procedure.get('fit_manifest_sha256') != digest(fitted):
        raise ValueError('registration must pin the fitted forecaster manifest')
    if fitted['model_revision'] != config['model_revision']:
        raise ValueError('fitted forecaster checkpoint differs from target checkpoint')
    contract=frozen['feature_information_contract']
    if not isinstance(contract,dict) or contract.get('features') != fitted['features']:
        raise ValueError('registered feature contract differs from fitted models')
    validate_contract(fitted['features'])
    expected={r['id'] for r in read_jsonl(config['dataset']) if r['split']=='test' and r['control_kind']=='primary'}
    rows=read_jsonl(config['forecasting']['target_feature_table'])
    if len({r['id'] for r in rows}) != len(rows) or {r['id'] for r in rows} != expected:
        raise ValueError('unlabelled feature table must cover all primary heldout IDs exactly once')
    rows=sorted(rows,key=lambda r:r['id'])
    forecasts=[{'id':r['id']} for r in rows]
    for name in PREDICTORS:
        probabilities=predict(fitted['models'][name],matrix(rows,fitted['features'][name]))
        for row,p in zip(forecasts,probabilities):
            row[name]=float(p)
    output=Path(config['frozen_predictions'])
    if output.exists():
        raise ValueError('frozen forecasts are immutable')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:
        stream.write(''.join(json.dumps(r,sort_keys=True)+'\n' for r in forecasts))
    output_hash=hashlib.sha256(output.read_bytes()).hexdigest()
    from datetime import datetime,timezone
    write_json(output.with_suffix('.manifest.json'),{
        'registered_analysis_sha256':registration_hash,'fit_manifest_sha256':digest(fitted),
        'target_features_sha256':hashlib.sha256(Path(config['forecasting']['target_feature_table']).read_bytes()).hexdigest(),
        'forecasts_sha256':output_hash,'rows':len(forecasts),'created_utc':datetime.now(timezone.utc).isoformat(),
        'target_outcomes_read':False})
    return {'forecasts':str(output),'rows':len(forecasts),
            'sha256':output_hash,
            'next':'pin this hash as frozen_predictions_sha256 before opening model outcomes'}
