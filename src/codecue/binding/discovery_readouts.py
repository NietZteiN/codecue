"""Capacity-matched, neutral-training linear readouts of discovery captures."""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, sha
from .registry import code_identity

CLASSES=np.array([i for i in range(-16,17) if i],dtype=int)


def neutral_train(rows):
    return np.array([r['split']=='train' and r['condition']=='neutral' for r in rows])


def group_weights(rows,seed):
    names=sorted({r['template_id'] for r in rows})
    rng=np.random.default_rng(seed)
    values=rng.exponential(1.,len(names))+1e-6
    lookup=dict(zip(names,values))
    weights=np.array([lookup[r['template_id']] for r in rows],dtype=np.float32)
    return weights/weights.mean()


def identity_labels(identifiers,seed):
    return np.array([[int(digest([seed,slot,name])[:12],16)%len(CLASSES)
                      for slot,name in enumerate(pair)] for pair in identifiers],dtype=int)


def run(config):
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    import sklearn
    from .state_capture import audit
    if len(set(config['seeds']))<3 or config['alpha']<=0:
        raise ValueError('readouts require at least three fit-weighting seeds and fixed positive regularization')
    if sha(config['capture_config'])!=config['capture_config_sha256']:
        raise ValueError('readout capture configuration changed')
    capture=json.loads(Path(config['capture_config']).read_text())
    checked=audit(capture)
    cases=read_jsonl(capture['capture_cases'])
    stems={item['case']['id']:[item['case']['record']['rename_map'][slot].removeprefix('train_').removeprefix('dev_')
                             for slot in ('v0','saved')] for item in cases}
    folder=Path(capture['run_dir'])/'activations/chunks'
    chunks=[];rows=[]
    for path in sorted(folder.glob('*.npz')):
        with np.load(path,allow_pickle=False) as data:
            chunks.append(data['features']);rows+=json.loads(data['metadata'].tobytes())
    features=np.concatenate(chunks);del chunks
    if features.shape[0]!=checked['cases']:raise ValueError('readout capture coverage differs')
    target=np.array([r['targets'] for r in rows],dtype=int)
    if not np.isin(target,CLASSES).all():raise ValueError('capture labels exceed the registered readout domain')
    labels=np.array([[int(np.where(CLASSES==value)[0][0]) for value in pair] for pair in target])
    identifiers=[stems[r['id']] for r in rows]
    queried=config.get('readout_task','all_slots')=='queried_value'
    slot_names=['queried'] if queried else ['current','saved']
    nslots=len(slot_names)
    if queried:
        selection=np.array([0 if r['query_role']=='current' else 1 for r in rows])
        labels=labels[np.arange(len(rows)),selection][:,None]
        identifiers=[[pair[index]] for pair,index in zip(identifiers,selection)]
    output=Path(config['run_dir']);output.mkdir(parents=True,exist_ok=True)
    immutable(output/'registration.json',(json.dumps(dict(config=config,capture_identity=checked['identity_hash'],
              analysis_source=code_identity()),sort_keys=True,indent=2)+'\n').encode())
    seen=set();unique=[]
    for i,row in enumerate(rows):
        key=row['state_prefix_sha256']
        if key not in seen:unique.append(i);seen.add(key)
    summaries=[]
    sites=capture.get('sites',['pre_query_state','after_query'])
    for site in range(len(sites)):
        if queried and site==0:continue  # The queried identity is not visible before the query.
        indices=np.array(unique if site==0 else list(range(len(rows))),dtype=int)
        meta=[rows[i] for i in indices];names=[identifiers[i] for i in indices]
        y=labels[indices];train=neutral_train(meta)
        if not train.any() or any(r['split'] not in ('train','development') for r in meta):
            raise ValueError('readouts require neutral discovery training and no final outcomes')
        texts=[r['visible_prefixes'][site] for r in meta]
        vectorizer=HashingVectorizer(analyzer='char',ngram_range=(3,8),n_features=config['feature_dimensions'],
                                    alternate_sign=True,norm=None,dtype=np.float32)
        surface=vectorizer.transform(texts).toarray()
        candidates=[('surface',-1,surface)]+[('hidden',layer,features[indices,l,site]) for l,layer in enumerate(capture['layers'])]
        for backend,layer,x in candidates:
            if x.shape[1]!=config['feature_dimensions']:
                raise ValueError('surface/hidden feature dimensions must match')
            scaler=StandardScaler().fit(x[train])
            z=scaler.transform(x)
            train_rows=[r for r,keep in zip(meta,train) if keep]
            supports=[set(y[train,slot]) for slot in range(nslots)]
            known_names=[{names[i][slot] for i in np.flatnonzero(train)} for slot in range(nslots)]
            for seed in config['seeds']:
                control=identity_labels(names,seed)
                truth=np.concatenate([np.eye(len(CLASSES),dtype=np.float32)[y[train,slot]] for slot in range(nslots)]+
                                     [np.eye(len(CLASSES),dtype=np.float32)[control[train,slot]] for slot in range(nslots)],axis=1)
                weights=group_weights(train_rows,seed)
                model=Ridge(alpha=config['alpha'],fit_intercept=True,solver='cholesky').fit(z[train],truth,sample_weight=weights)
                predictions=model.predict(z).reshape(len(meta),2*nslots,len(CLASSES)).argmax(axis=2)
                artifact=output/f'{backend}_layer{layer}_site{site}_seed{seed}.npz'
                if artifact.exists():raise ValueError('readout model artifacts are immutable')
                np.savez(artifact,coef=model.coef_,intercept=model.intercept_,mean=scaler.mean_,scale=scaler.scale_,
                         classes=CLASSES,training_ids=np.array([r['id'] for r in train_rows]),
                         predictions=predictions,case_ids=np.array([r['id'] for r in meta]))
                for split,condition in [('train','neutral'),('development','neutral'),
                                        ('development','informative'),('development','misleading')]:
                    mask=np.array([r['split']==split and r['condition']==condition for r in meta])
                    if not mask.any():continue
                    values=[]
                    for slot in range(nslots):
                        in_support=mask & np.array([v in supports[slot] for v in y[:,slot]])
                        name_support=mask & np.array([pair[slot] in known_names[slot] for pair in names])
                        acc=float((predictions[mask,slot]==y[mask,slot]).mean())
                        ctrl=float((predictions[name_support,nslots+slot]==control[name_support,slot]).mean()) if name_support.any() else None
                        values.append(dict(slot=slot_names[slot],accuracy=acc,
                            trained_value_classes=len(supports[slot]),out_of_support=int((mask & ~in_support).sum()),
                            in_support_accuracy=float((predictions[in_support,slot]==y[in_support,slot]).mean()) if in_support.any() else None,
                            identifier_control_accuracy=ctrl,identifier_key_support=int(name_support.sum()),
                            selectivity_difference=acc-ctrl if ctrl is not None and name_support.sum()==mask.sum() else None))
                    summaries.append(dict(backend=backend,layer=layer,site=sites[site],seed=seed,
                        split=split,condition=condition,n=int(mask.sum()),training_rows=int(train.sum()),
                        training_structural_components=len({r['template_id'] for r in train_rows}),
                        parameter_count_per_value_or_control_readout=nslots*len(CLASSES)*(x.shape[1]+1),
                        joint_value_accuracy=float((predictions[mask,:nslots]==y[mask]).all(axis=1).mean()),slots=values))
    result=dict(status='complete',model=capture['model'],capture_identity=checked['identity_hash'],config_hash=digest(config),
                analysis_source=code_identity(),sklearn_version=sklearn.__version__,fits=summaries,
                neutral_training_only=True,generated_holdouts_opened=False,
                readout_task='queried_value_after_query_only' if queried else 'all_canonical_slots',
                seed_interpretation='Three positive template-weighting draws retain every neutral training structure and value; not independent experimental replications.',
                identifier_control='Random labels keyed by canonical slot and lexical identifier stem, with train/dev prefix removed. Unseen development stems have no reported selectivity.',
                limitation='Linear recovery is measurement-specific. Control performance, missing training classes, vocabulary shifts and surface information limit interpretation. No causal effect is claimed.')
    immutable(output/'summary.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    lines=['# Discovery linear readouts','',
           'Weighted ridge classifiers train only on neutral training cases. Three predeclared positive template-weighting seeds retain all training structures. '
           'Normalization uses neutral training data only; regularization is fixed. Hidden and surface features use the same 4,096 dimensions and output-head capacity. '
           'Pre-query twins are deduplicated. These are measurement results, not a mechanism claim.','',
           '| Features | Block | Site | Development naming | '+ ' | '.join(name+' accuracy' for name in slot_names)+' |',
           '|---|---:|---|---|'+ '|'.join('---:' for _ in slot_names)+'|']
    groups=defaultdict(list)
    for fit in summaries:
        if fit['split']=='development':groups[fit['backend'],fit['layer'],fit['site'],fit['condition']].append(fit)
    for key,group in sorted(groups.items()):
        values=[np.mean([fit['slots'][slot]['accuracy'] for fit in group]) for slot in range(nslots)]
        lines.append('| '+' | '.join(map(str,key))+' | '+' | '.join(f'{100*v:.2f}%' for v in values)+' |')
    lines+=['','Full seed-level results include identifier-control accuracy/selectivity, parameter counts, class support and joint accuracy. '
            'Identifier-stem controls have few keys; high control accuracy is not evidence of semantic binding. '
            'Character-ngram surface features are one capacity-matched comparator, not an exhaustive shortcut audit. '
            'Cross-naming failures may reflect harmless representational change. No final outcomes or language-model training were used.','']
    immutable(config['report'],'\n'.join(lines).encode())
    return result
