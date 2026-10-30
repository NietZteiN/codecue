"""Frequency-matched, grouped shuffled-label diagnostics on audited captures.

Permute complete (current, saved) target pairs across numeric base programs
within each split/template. All naming, lexical, update, tail and query
relatives inherit one mapping. This is a negative-control task, not a causal
selectivity test; matching label frequencies does not equate task complexity.
"""
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np

from .datasets import digest, write_json
from .discovery_readouts import CLASSES, group_weights, neutral_train
from .published_benchmarks import immutable, sha
from .registry import code_identity


def grouped_shuffle(rows, seed):
    """Return paired class-index labels and the complete donor-base mapping."""
    base={};groups=defaultdict(list)
    for row in rows:
        if row['split'] not in ('train','development'):
            raise ValueError('matched controls cannot open final outcomes')
        key=row['base_id'];identity=(row['split'],row['template_id'],tuple(row['targets']))
        if key in base and base[key]!=identity:
            raise ValueError('base relatives disagree on split, template or targets')
        base[key]=identity
    train_templates={v[1] for v in base.values() if v[0]=='train'}
    dev_templates={v[1] for v in base.values() if v[0]=='development'}
    if train_templates & dev_templates:raise ValueError('train/development templates overlap')
    for key,(split,template,_) in base.items():groups[split,template].append(key)
    donors={}
    for stratum,keys in sorted(groups.items()):
        keys=sorted(keys)
        if len(keys)<2:raise ValueError('shuffle stratum needs multiple numeric bases')
        rng=np.random.default_rng(int(digest([seed,list(stratum)])[:16],16))
        donors.update(zip(keys,rng.permutation(keys).tolist()))
    class_index={int(v):i for i,v in enumerate(CLASSES)}
    try:
        labels=np.array([[class_index[v] for v in base[donors[r['base_id']]][2]] for r in rows],dtype=int)
    except KeyError as exc:raise ValueError('shuffle label outside the fixed value domain') from exc
    return labels,donors


def class_labels(rows, queried=False):
    lookup={int(v):i for i,v in enumerate(CLASSES)}
    labels=np.array([[lookup[v] for v in r['targets']] for r in rows],dtype=int)
    if queried:
        slots=np.array([0 if r['query_role']=='current' else 1 for r in rows])
        labels=labels[np.arange(len(rows)),slots][:,None]
    return labels


def select_queried(labels,rows):
    slots=np.array([0 if r['query_role']=='current' else 1 for r in rows])
    return labels[np.arange(len(rows)),slots][:,None]


def histogram_audit(rows, truth, shuffled):
    """Require exact class frequencies in every analyzed split/naming cell."""
    if truth.shape!=shuffled.shape or truth.shape[0]!=len(rows):raise ValueError('label geometry differs')
    cells=[]
    for split,condition in [('train','neutral'),('development','neutral'),('development','informative'),('development','misleading')]:
        mask=np.array([r['split']==split and r['condition']==condition for r in rows])
        if not mask.any():raise ValueError('complete split/naming cells required')
        for slot in range(truth.shape[1]):
            counts=np.bincount(truth[mask,slot],minlength=len(CLASSES))
            controls=np.bincount(shuffled[mask,slot],minlength=len(CLASSES))
            if not np.array_equal(counts,controls):raise ValueError('shuffled-label frequencies differ from value labels')
            p=counts[counts>0]/counts.sum()
            cells.append(dict(split=split,condition=condition,slot=slot,n=int(mask.sum()),counts=counts.tolist(),
                              control_counts=controls.tolist(),classes=int((counts>0).sum()),entropy_bits=float(-(p*np.log2(p)).sum())))
    return cells


def validate_model(saved, registration_hash, ids, training_ids, targets, controls, width):
    nslots=targets.shape[1]
    if (str(saved['registration_hash'].item())!=registration_hash or saved['case_ids'].tolist()!=ids
            or saved['training_ids'].tolist()!=training_ids or not np.array_equal(saved['classes'],CLASSES)
            or not np.array_equal(saved['target_labels'],targets) or not np.array_equal(saved['control_labels'],controls)
            or saved['coef'].shape!=(2*nslots*len(CLASSES),width) or saved['intercept'].shape!=(2*nslots*len(CLASSES),)
            or saved['mean'].shape!=(width,) or saved['scale'].shape!=(width,)
            or saved['predictions'].shape!=(len(ids),2*nslots)):
        raise ValueError('saved matched-control model identity or geometry differs')
    if any(not np.isfinite(saved[k]).all() for k in ('coef','intercept','mean','scale')) or (saved['scale']<=0).any():
        raise ValueError('saved matched-control model has invalid parameters')


def predictions_from_saved(saved,x):
    from sklearn.preprocessing import StandardScaler
    scaler=StandardScaler();scaler.mean_=saved['mean'];scaler.scale_=saved['scale'];scaler.n_features_in_=x.shape[1]
    z=scaler.transform(x)
    scores=z@saved['coef'].T+saved['intercept']
    return scores.reshape(len(x),-1,len(CLASSES)).argmax(axis=2)


def inputs(config):
    capture_path=Path(config['capture_config'])
    if sha(capture_path)!=config['capture_config_sha256']:raise ValueError('capture configuration changed')
    capture=json.loads(capture_path.read_text());root=Path(capture['run_dir'])/'activations'
    audit_path=root/'audit.json'
    if sha(audit_path)!=config['capture_audit_sha256']:raise ValueError('pinned capture audit changed')
    checked=json.loads(audit_path.read_text());manifest=json.loads((root/'manifest.json').read_text())
    if checked['status']!='passed' or manifest['status']!='complete' or manifest['identity']['config']!=capture or checked['identity_hash']!=manifest['identity_hash'] or manifest['identity_hash']!=digest(manifest['identity']):
        raise ValueError('complete audited capture required')
    if sha(config['reference_summary'])!=config['reference_summary_sha256']:raise ValueError('reference readout summary changed')
    ref_registration=Path(config['reference_summary']).parent/'registration.json'
    if sha(ref_registration)!=config['reference_registration_sha256']:raise ValueError('reference registration changed')
    ref_config=json.loads(ref_registration.read_text())['config']
    if any(ref_config.get(k,'all_slots' if k=='readout_task' else None)!=config[k] for k in ('alpha','seeds','feature_dimensions','readout_task')):
        raise ValueError('reference probe protocol differs')
    reference=json.loads(Path(config['reference_summary']).read_text())
    if reference['capture_identity']!=checked['identity_hash']:raise ValueError('reference uses another capture bank')
    for path,checksum in config['reference_model_checksums'].items():
        if sha(path)!=checksum:raise ValueError('reference model changed')
    return capture,checked


def load_bank(config):
    from .state_capture import inputs as capture_inputs,validate_chunk
    capture,checked=inputs(config)
    manifest=json.loads((Path(capture['run_dir'])/'activations/manifest.json').read_text())
    _,cases=capture_inputs(capture,manifest['identity']['code']['source_sha256'])
    chunks=[];rows=[]
    for name,checksum in sorted(checked['chunk_checksums'].items()):
        if sha(name)!=checksum:raise ValueError('audited capture chunk changed')
        with np.load(name,allow_pickle=False) as saved:
            vectors=saved['features'];part=json.loads(saved['metadata'].tobytes())
            validate_chunk(capture,cases[len(rows):len(rows)+len(part)],vectors,part)
            chunks.append(vectors);rows+=part
    bank=np.concatenate(chunks)
    if len(rows)!=checked['cases']:raise ValueError('capture coverage differs')
    return capture,checked,bank,rows


def fit_metrics(meta,truth,controls,predictions,train,reference_predictions,slot_names):
    nslots=truth.shape[1];result=[]
    for split,condition in [('train','neutral'),('development','neutral'),('development','informative'),('development','misleading')]:
        mask=np.array([r['split']==split and r['condition']==condition for r in meta])
        values=[]
        for slot,name in enumerate(slot_names):
            counts=np.bincount(truth[train,slot],minlength=len(CLASSES));majority=int(counts.argmax())
            support=np.flatnonzero(counts);in_support=mask & np.isin(truth[:,slot],support)
            value_correct=predictions[:,slot]==truth[:,slot];control_correct=predictions[:,nslots+slot]==controls[:,slot]
            template_cells=[]
            for template in sorted({r['template_id'] for r,keep in zip(meta,mask) if keep}):
                tm=mask & np.array([r['template_id']==template for r in meta])
                template_cells.append(dict(template_id=template,n=int(tm.sum()),value_correct=int(value_correct[tm].sum()),control_correct=int(control_correct[tm].sum())))
            values.append(dict(slot=name,value_accuracy=float(value_correct[mask].mean()),control_accuracy=float(control_correct[mask].mean()),
                value_minus_control=float(value_correct[mask].mean()-control_correct[mask].mean()),majority_accuracy=float((truth[mask,slot]==majority).mean()),
                control_majority_accuracy=float((controls[mask,slot]==majority).mean()),trained_classes=len(support),out_of_support=int((mask & ~in_support).sum()),
                reference_value_prediction_matches=int((predictions[mask,slot]==reference_predictions[mask,slot]).sum()),template_cells=template_cells))
        result.append(dict(split=split,condition=condition,n=int(mask.sum()),slots=values,
            joint_value_accuracy=float((predictions[mask,:nslots]==truth[mask]).all(axis=1).mean()),
            joint_control_accuracy=float((predictions[mask,nslots:]==controls[mask]).all(axis=1).mean())))
    return result


def run(config):
    """Fit only small CPU probes; never load a language model or tokenizer."""
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits
    import sklearn
    if config['alpha']<=0 or len(set(config['seeds']))<3 or config['readout_task'] not in ('all_slots','queried_value'):
        raise ValueError('fixed positive alpha, three seeds and known task required')
    started=time.monotonic();capture,checked,bank,rows=load_bank(config)
    output=Path(config['run_dir']);output.mkdir(parents=True,exist_ok=True)
    registration=dict(config=config,capture_identity=checked['identity_hash'],analysis_source=code_identity(),
        numpy_version=np.__version__,sklearn_version=sklearn.__version__,language_model_loaded=False,
        control='Joint target-pair permutation across numeric bases within each split/template; relatives share one assignment.',
        limitation='Class-frequency and entropy matching does not match all task complexity. No causal selectivity or information-absence conclusion.')
    immutable(output/'registration.json',(json.dumps(registration,sort_keys=True,indent=2)+'\n').encode());identity=digest(registration)
    if (output/'summary.json').exists():
        summary=json.loads((output/'summary.json').read_text())
        if summary['registration_hash']!=identity:raise ValueError('completed run identity differs')
        for path,checksum in summary['fit_checksums'].items():
            if sha(path)!=checksum:raise ValueError('completed fit changed')
        return dict(status='complete_reused',fits=summary['fit_count'],summary=str(output/'summary.json'))
    queried=config['readout_task']=='queried_value';nslots=1 if queried else 2;slot_names=['queried'] if queried else ['current','saved']
    seen=set();unique=[]
    for i,r in enumerate(rows):
        if r['state_prefix_sha256'] not in seen:unique.append(i);seen.add(r['state_prefix_sha256'])
    shuffle={seed:grouped_shuffle(rows,seed) for seed in config['seeds']}
    for seed,(labels,donors) in shuffle.items():
        immutable(output/f'shuffle_seed{seed}.json',(json.dumps(dict(seed=seed,donor_bases=donors,
            unchanged_base_mappings=sum(k==v for k,v in donors.items()),total_bases=len(donors)),sort_keys=True,indent=2)+'\n').encode())
    all_fits=[];checksums={}
    with threadpool_limits(limits=config['cpu_threads']):
        for site,site_name in enumerate(capture['sites']):
            if queried and site==0:continue
            indices=np.array(unique if site==0 else range(len(rows)),dtype=int);meta=[rows[i] for i in indices]
            truth=class_labels(meta,queried);train=neutral_train(meta);training_rows=[r for r,keep in zip(meta,train) if keep]
            ids=[r['id'] for r in meta];train_ids=[r['id'] for r in training_rows]
            if not train.any():raise ValueError('no neutral training cases')
            controls={seed:(select_queried(labels[indices],meta) if queried else labels[indices]) for seed,(labels,_) in shuffle.items()}
            histograms={seed:histogram_audit(meta,truth,y) for seed,y in controls.items()}
            vectorizer=HashingVectorizer(analyzer='char',ngram_range=(3,8),n_features=config['feature_dimensions'],alternate_sign=True,norm=None,dtype=np.float32)
            surface=vectorizer.transform([r['visible_prefixes'][site] for r in meta]).toarray()
            candidates=[('surface',-1,surface)]+[('hidden',layer,bank[indices,li,site]) for li,layer in enumerate(capture['layers'])]
            for backend,layer,x in candidates:
                if x.shape[1]!=config['feature_dimensions']:raise ValueError('hidden/surface capacity differs')
                for seed in config['seeds']:
                    name=f'{backend}_layer{layer}_site{site}_seed{seed}'
                    path=output/(name+'.npz');proof=output/(name+'.json');control=controls[seed]
                    if proof.exists() and json.loads(proof.read_text())['model_sha256']!=sha(path):raise ValueError('resumed model checksum differs')
                    if not path.exists():
                        scaler=StandardScaler().fit(x[train]);z=scaler.transform(x)
                        target=np.concatenate([np.eye(len(CLASSES),dtype=np.float32)[truth[train,slot]] for slot in range(nslots)]+
                                              [np.eye(len(CLASSES),dtype=np.float32)[control[train,slot]] for slot in range(nslots)],axis=1)
                        model=Ridge(alpha=config['alpha'],fit_intercept=True,solver='cholesky').fit(z[train],target,sample_weight=group_weights(training_rows,seed))
                        predictions=model.predict(z).reshape(len(meta),2*nslots,len(CLASSES)).argmax(axis=2)
                        temp=path.with_suffix('.tmp')
                        with temp.open('wb') as stream:
                            np.savez(stream,registration_hash=np.array(identity),coef=model.coef_,intercept=model.intercept_,
                                mean=scaler.mean_,scale=scaler.scale_,classes=CLASSES,training_ids=np.array(train_ids),case_ids=np.array(ids),
                                predictions=predictions,target_labels=truth,control_labels=control)
                        temp.replace(path)
                    with np.load(path,allow_pickle=False) as saved:
                        validate_model(saved,identity,ids,train_ids,truth,control,x.shape[1])
                        predictions=saved['predictions']
                        if not np.array_equal(predictions,predictions_from_saved(saved,x)):raise ValueError('saved-weight replay differs')
                    ref=Path(config['reference_summary']).parent/(name+'.npz')
                    if str(ref) not in config['reference_model_checksums']:raise ValueError('unregistered reference fit')
                    with np.load(ref,allow_pickle=False) as reference:
                        if reference['case_ids'].tolist()!=ids or reference['training_ids'].tolist()!=train_ids:raise ValueError('reference fit case identities differ')
                        reference_predictions=reference['predictions'][:,:nslots]
                    metrics=fit_metrics(meta,truth,control,predictions,train,reference_predictions,slot_names)
                    fit=dict(backend=backend,layer=layer,site=site_name,seed=seed,training_rows=len(train_ids),
                        training_structural_components=len({r['template_id'] for r in training_rows}),
                        parameters_per_value_or_control_head=nslots*len(CLASSES)*(x.shape[1]+1),model_sha256=sha(path),
                        saved_weight_replay_cases=len(meta),label_histograms=histograms[seed],cells=metrics)
                    immutable(proof,(json.dumps(fit,sort_keys=True,indent=2)+'\n').encode());checksums[str(path)]=sha(path);checksums[str(proof)]=sha(proof);all_fits.append(fit)
                    write_json(output/'progress.json',dict(status='running',last_fit=name,completed_fits=len(all_fits)))
                    print(f'{name}: saved-weight replay and frequency checks passed',flush=True)
    result=dict(status='complete',registration_hash=identity,config_hash=digest(config),capture_identity=checked['identity_hash'],
                fit_count=len(all_fits),fits=all_fits,fit_checksums=checksums,wall_seconds=time.monotonic()-started,
                language_model_loaded=False,generated_holdouts_opened=False,analysis_source=code_identity())
    immutable(output/'summary.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete',fits=len(all_fits),summary=str(output/'summary.json'))


def metadata(config):
    """Read pinned labels and prefixes without materializing activation arrays."""
    capture,checked=inputs(config);rows=[]
    for name,checksum in sorted(checked['chunk_checksums'].items()):
        if sha(name)!=checksum:raise ValueError('capture chunk changed')
        with np.load(name,allow_pickle=False) as saved:rows+=json.loads(saved['metadata'].tobytes())
    if len(rows)!=checked['cases']:raise ValueError('metadata coverage differs')
    return capture,checked,rows


def audit(config):
    capture,checked,rows=metadata(config);output=Path(config['run_dir'])
    summary=json.loads((output/'summary.json').read_text());registration=json.loads((output/'registration.json').read_text())
    if (summary['status']!='complete' or registration['config']!=config or summary['config_hash']!=digest(config)
            or summary['registration_hash']!=digest(registration) or summary['capture_identity']!=checked['identity_hash']):
        raise ValueError('completed pinned matched-control run required')
    for path,checksum in summary['fit_checksums'].items():
        if sha(path)!=checksum:raise ValueError('audited fit checksum differs')
    queried=config['readout_task']=='queried_value';nslots=1 if queried else 2;slot_names=['queried'] if queried else ['current','saved']
    seen=set();unique=[]
    for i,r in enumerate(rows):
        if r['state_prefix_sha256'] not in seen:unique.append(i);seen.add(r['state_prefix_sha256'])
    shuffle={seed:grouped_shuffle(rows,seed) for seed in config['seeds']};all_fits=[];expected_paths=[];replay_cases=0;reference_matches=reference_total=0
    for site,site_name in enumerate(capture['sites']):
        if queried and site==0:continue
        indices=np.array(unique if site==0 else range(len(rows)),dtype=int);meta=[rows[i] for i in indices]
        truth=class_labels(meta,queried);train=neutral_train(meta);train_ids=[r['id'] for r,keep in zip(meta,train) if keep];ids=[r['id'] for r in meta]
        for backend,layer in [('surface',-1)]+[('hidden',l) for l in capture['layers']]:
            for seed in config['seeds']:
                labels,donors=shuffle[seed];control=select_queried(labels[indices],meta) if queried else labels[indices]
                shuffle_path=output/f'shuffle_seed{seed}.json';mapping=json.loads(shuffle_path.read_text())
                if mapping['donor_bases']!=donors:raise ValueError('saved shuffle mapping differs')
                name=f'{backend}_layer{layer}_site{site}_seed{seed}'
                path=output/(name+'.npz');proof=output/(name+'.json');expected_paths.extend([str(path),str(proof)])
                fit=json.loads(proof.read_text());all_fits.append(fit)
                if fit['label_histograms']!=histogram_audit(meta,truth,control) or fit['model_sha256']!=sha(path):raise ValueError('frequency audit or model proof differs')
                if (fit['backend'],fit['layer'],fit['site'],fit['seed'])!=(backend,layer,site_name,seed):raise ValueError('fit identity differs')
                if fit['saved_weight_replay_cases']!=len(meta):raise ValueError('incomplete saved-weight replay')
                with np.load(path,allow_pickle=False) as saved:
                    validate_model(saved,summary['registration_hash'],ids,train_ids,truth,control,config['feature_dimensions']);pred=saved['predictions']
                ref=Path(config['reference_summary']).parent/(name+'.npz')
                with np.load(ref,allow_pickle=False) as saved:
                    ref_pred=saved['predictions'][:,:nslots]
                    if saved['case_ids'].tolist()!=ids:raise ValueError('reference identities differ')
                if fit['cells']!=fit_metrics(meta,truth,control,pred,train,ref_pred,slot_names):raise ValueError('saved predictions do not reproduce reported metrics')
                replay_cases+=len(meta);reference_matches+=int((pred[:,:nslots]==ref_pred).sum());reference_total+=len(meta)*nslots
    if summary['fits']!=all_fits or summary['fit_count']!=len(all_fits) or set(expected_paths)!=set(summary['fit_checksums']) or {str(p) for p in output.glob('*.npz')}!={p for p in expected_paths if p.endswith('.npz')}:
        raise ValueError('full registered fit coverage differs')
    result=dict(status='passed',registration_hash=summary['registration_hash'],summary_sha256=sha(output/'summary.json'),
        fit_count=len(all_fits),saved_weight_replay_cases=replay_cases,reference_value_prediction_matches=reference_matches,
        reference_value_prediction_total=reference_total,exact_class_histograms=True,language_model_loaded=False,generated_holdouts_opened=False)
    immutable(output/'audit.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode());return result


def review(config):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output=Path(config['run_dir']);checked=json.loads((output/'audit.json').read_text());summary=json.loads((output/'summary.json').read_text())
    if checked['status']!='passed' or checked['summary_sha256']!=sha(output/'summary.json'):raise ValueError('completed matching audit required')
    existing=Path(config['review_artifact'])
    if existing.exists():
        previous=json.loads(existing.read_text())
        if previous['audit']!=checked or previous['report_sha256']!=sha(config['report']) or previous['figure_sha256']!=sha(config['figure']):
            raise ValueError('completed review artifacts changed')
        return dict(status='complete_reused',report=config['report'],review_artifact=config['review_artifact'])
    groups=defaultdict(list);entropy=set()
    for fit in summary['fits']:
        for h in fit['label_histograms']:entropy.add((h['split'],h['condition'],h['slot'],h['classes'],round(h['entropy_bits'],9)))
        for cell in fit['cells']:
            for slot in cell['slots']:
                key=(fit['backend'],fit['layer'],fit['site'],cell['split'],cell['condition'],slot['slot'])
                groups[key].append(slot)
    metrics=[dict(backend=k[0],layer=k[1],site=k[2],split=k[3],condition=k[4],slot=k[5],seeds=len(v),
                  value_accuracy=float(np.mean([r['value_accuracy'] for r in v])),control_accuracy=float(np.mean([r['control_accuracy'] for r in v])),
                  value_minus_control=float(np.mean([r['value_minus_control'] for r in v])),majority_accuracy=float(np.mean([r['majority_accuracy'] for r in v])),
                  out_of_support_per_seed=[r['out_of_support'] for r in v]) for k,v in sorted(groups.items())]
    lines=['# Frequency-matched grouped probe controls','',
           'These are post-hoc measurement controls on the already-audited discovery capture bank. Ordinary weighted ridge heads predict oracle values and shuffled labels with equal feature/head capacity and the same training preprocessing. Joint current/saved label pairs are permuted across numeric base programs within each split/template; all related variants share the mapping. No final outcomes or language-model training are used.','',
           f"All {checked['fit_count']} fits passed saved-weight replay and complete metric audits. Value and shuffled-label class histograms match exactly in every analyzed split/naming/head cell. The original value-head predictions agree on {checked['reference_value_prediction_matches']:,}/{checked['reference_value_prediction_total']:,} comparisons.",'',
           'The three fixed seeds vary both positive template fit weights and the shuffle; they are not independent model or dataset replications. Frequency matching repairs the earlier two-label-versus-32-label mismatch, but does not equate all task complexity or prove semantic selectivity. High training shuffle accuracy can reflect memorization. Failed control transfer or successful value decoding does not establish natural causal use.','',
           '| Features | Block | Site | Split | Naming | Head | Value | Shuffled | Training prior |','|---|---:|---|---|---|---|---:|---:|---:|']
    for row in metrics:
        lines.append('| '+ ' | '.join(str(row[k]) for k in ('backend','layer','site','split','condition','slot'))+f" | {row['value_accuracy']:.2%} | {row['control_accuracy']:.2%} | {row['majority_accuracy']:.2%} |")
    slots=sorted({r['slot'] for r in metrics});fig,axes=plt.subplots(1,len(slots),figsize=(7*len(slots),5),squeeze=False)
    for slot,ax in zip(slots,axes[0]):
        chosen=[r for r in metrics if r['slot']==slot and r['split']=='development' and r['condition']=='neutral' and r['backend']=='hidden']
        for site in sorted({r['site'] for r in chosen}):
            selected=sorted([r for r in chosen if r['site']==site],key=lambda r:r['layer'])
            ax.plot([r['layer'] for r in selected],[r['value_accuracy'] for r in selected],marker='o',label=site+' values')
            ax.plot([r['layer'] for r in selected],[r['control_accuracy'] for r in selected],marker='x',linestyle='--',label=site+' shuffled')
        ax.set(xlabel='Raw block',ylabel='Neutral development accuracy',ylim=(0,1),title=slot);ax.legend(fontsize=8)
    figure=Path(config['figure']);figure.parent.mkdir(parents=True,exist_ok=True);fig.tight_layout();fig.savefig(figure);fig.savefig(figure.with_suffix('.png'),dpi=150);plt.close(fig)
    lines+=['',f'![Full registered hidden curves]({figure.name})','']
    immutable(config['report'],('\n'.join(lines)).encode())
    result=dict(status='complete_audited',audit=checked,metrics=metrics,class_entropy_cells=[list(v) for v in sorted(entropy)],report=config['report'],report_sha256=sha(config['report']),figure=str(figure),figure_sha256=sha(figure),generated_holdouts_opened=False)
    immutable(config['review_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'],review_artifact=config['review_artifact'])
