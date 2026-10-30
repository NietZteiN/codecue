"""Independent saved-parameter review. Never fits or loads a language model."""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np

from . import arithmetic_graph_capture as capture, arithmetic_graph_readouts as readouts
from . import relationship_capture as base
from .datasets import digest
from .weighted_ridge import from_parameters, _array_hash

ROLE = 'discovery_arithmetic_graph_postrun_review_v1'


def match_signature(original, response):
    """Numeric coincidences overlap; they do not identify a causal error type."""
    value = response['parsed']
    if value is None:
        return 'invalid'
    if value == original['expected_answer']:
        return 'correct'
    slot = original['query_slot']
    truth = original['oracle']
    current = truth['definitions'][slot]
    stale = any(w['slot'] == slot and w['statement'] < current and w['value'] == value for w in truth['writes'])
    other = any(i != slot and v == value for i, v in enumerate(truth['values']))
    return ('stale_and_other_current' if stale and other else 'stale_only' if stale
            else 'other_current_only' if other else 'neither')


def head_diagnostics(scores, truth, prior, heads, rows, training_truth):
    result = {}
    for kind in ('parent', 'definition', 'version', 'value'):
        selected = [h for h in heads if h['kind'] == kind]
        if not selected:
            continue
        prediction = readouts._decode(scores, heads, kind)
        target = readouts._decode(truth, heads, kind)
        baseline = readouts._decode(prior, heads, kind)
        cells = []
        for i, head in enumerate(selected):
            count = head['stop']-head['start']
            confusion = np.zeros((count, count), dtype=int)
            np.add.at(confusion, (target[:, i], prediction[:, i]), 1)
            cells.append(dict(slot=i, accuracy=float((prediction[:, i] == target[:, i]).mean()),
                prior_accuracy=float((baseline[:, i] == target[:, i]).mean()),
                predicted_classes=np.flatnonzero(confusion.sum(axis=0)).tolist(),
                largest_prediction_fraction=float(confusion.sum(axis=0).max()/len(rows)),
                confusion_nonzero=[[int(a),int(b),int(confusion[a,b])]
                    for a,b in zip(*np.nonzero(confusion))]))
        result[kind] = dict(individual_accuracy=float((prediction == target).mean()),
            whole_accuracy=float((prediction == target).all(axis=1).mean()),
            individual_prior_accuracy=float((baseline == target).mean()),
            whole_prior_accuracy=float((baseline == target).all(axis=1).mean()), heads=cells)
        if kind == 'value':
            train_values = readouts._decode(training_truth, heads, 'value')
            seen = np.column_stack([np.isin(target[:, i], train_values[:, i]) for i in range(4)])
            correct = prediction == target
            query = np.asarray([r['query_slot'] for r in rows])
            selected_query = np.arange(4)[None, :] == query[:, None]
            result[kind].update(queried_accuracy=float(correct[selected_query].mean()),
                unqueried_accuracy=float(correct[~selected_query].mean()),
                seen_class_cells=int(seen.sum()), unseen_class_cells=int((~seen).sum()),
                seen_class_accuracy=float(correct[seen].mean()) if seen.any() else None,
                unseen_class_accuracy=float(correct[~seen].mean()) if (~seen).any() else None)
    return result


def replay_check(predicted, saved, heads, tolerance=1e-10):
    if predicted.shape != saved.shape or not np.isfinite(predicted).all():
        raise ValueError('complete finite score replay required')
    maximum = float(np.max(np.abs(predicted-saved)))
    if not np.allclose(predicted, saved, rtol=tolerance, atol=tolerance):
        raise ValueError('saved parameter score replay exceeds declared numerical tolerance')
    if not np.array_equal(predicted[:, :48] >= .5, saved[:, :48] >= .5):
        raise ValueError('replayed binary decisions changed')
    for kind in ('parent', 'definition', 'version', 'value'):
        if any(h['kind'] == kind for h in heads) and not np.array_equal(
                readouts._decode(predicted, heads, kind), readouts._decode(saved, heads, kind)):
            raise ValueError('replayed categorical decisions changed')
    return maximum


def run(config):
    from sklearn.feature_extraction.text import HashingVectorizer
    base._slurm()
    source = base._current_source(config)
    if config.get('evaluation_role') != ROLE:
        raise ValueError('explicit postrun review role required')
    out = base._safe(config['run_dir'])
    out.mkdir(parents=True, exist_ok=True)
    if (out/'review.json').exists():
        raise ValueError('review already exists; preserve completed analysis')
    models = {}
    analysis_manifest = base._json(Path(source['snapshot'])/'frozen_manifest.json')
    for item in config['models']:
        old = base._json(item['readout_config'], item['readout_config_sha256'])
        readouts.audit(old)
        folder = Path(old['run_dir'])
        result = base._json(folder/'results.json', item['results_sha256'])
        original_manifest = base._verify_source(old, result['source'])
        for name in ('arithmetic_graph_programs.py','arithmetic_graph_readouts.py','weighted_ridge.py'):
            relative='src/codecue/binding/'+name
            if analysis_manifest['code']['source_files'][relative] != original_manifest['code']['source_files'][relative]:
                raise ValueError('target/decoder implementation differs from original scientific fit')
        cap = base._json(old['capture_config'], old['capture_config_sha256'])
        capture.completed_metadata(cap)
        preflight, cases = capture.inputs(cap)
        rows, _ = capture._CORE._dataset(cap)
        train = np.asarray([r['split'] == 'train' for r in rows])
        dev = ~train
        ids = np.asarray([r['id'] for r in rows])
        groups = np.asarray([r['component_id'] for r in rows])
        donor = readouts.donor_indices(rows)
        vectors = np.empty((len(rows), 3, cap['hidden_size']), np.float32)
        layer = cap['layers'].index(old['primary_layer'])
        manifest = base._json(Path(cap['run_dir'])/'summary.json')
        for entry in manifest['chunks']:
            start, count = entry['first'], entry['rows']
            chunk, _ = capture.load_chunk(entry, cases[start:start+count], cap)
            vectors[start:start+count] = chunk[:, :, layer]
        banks = []
        for site in range(3):
            y, binary, values, heads, differences = readouts.targets(rows, site)
            joined = np.concatenate((y[train], y[donor[train]]), axis=1)
            surface = HashingVectorizer(analyzer='char', ngram_range=(3, 8), n_features=cap['hidden_size'],
                alternate_sign=True, norm=None).transform(c['visible_prefixes'][site] for c in cases).toarray().astype(np.float32)
            for backend, x in [('hidden', vectors[:, site]), ('source', surface)]:
                originals = [b for b in result['fits'] if b['site'] == site and b['backend'] == backend]
                for bank in originals:
                    metadata = bank['ridge_metadata']
                    rng = np.random.default_rng(bank['seed'])
                    group_weights = dict(zip(sorted(set(groups[train])), rng.exponential(1., len(set(groups[train])))+.1))
                    weights = np.asarray([group_weights[g] for g in groups[train]])
                    actual_hashes = dict(features=_array_hash(x[train]), targets=_array_hash(joined), sample_weight=_array_hash(weights))
                    if actual_hashes != metadata['training_input_sha256'] or metadata['training_ids'] != ids[train].tolist():
                        raise ValueError('reconstructed training inputs differ from saved fit')
                    with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as stored:
                        model = from_parameters(metadata, {k: stored[k] for k in stored.files})
                    scores = model.predict(x)
                    real, shuffled = np.split(scores, 2, axis=1)
                    with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as stored:
                        if not np.array_equal(stored['ordered_case_ids'], ids) or not np.array_equal(stored['dev_indices'], np.flatnonzero(dev)):
                            raise ValueError('saved score row order differs')
                        if not np.array_equal(stored['truth'], y[dev]) or not np.array_equal(stored['shuffle_truth'], y[donor[dev]]):
                            raise ValueError('saved score oracle targets differ')
                        maximum = replay_check(real[dev], stored['real'], heads)
                        maximum = max(maximum, replay_check(shuffled[dev], stored['shuffled'], heads))
                        eligible = stored['eligible']
                    prior = np.broadcast_to(model.weighted_target_mean[:y.shape[1]], y.shape)
                    train_metrics = readouts.summarize(real, y, binary, values, heads, differences, eligible, train)
                    diagnostics = head_diagnostics(real[dev], y[dev], prior[dev], heads,
                        [r for r in rows if r['split'] == 'development'], y[train])
                    banks.append(dict(site=site, backend=backend, seed=bank['seed'], replay_max_abs_diff=maximum,
                        train=train_metrics, development=bank['metrics']['direct'],
                        prior=bank['metrics']['train_prior'], shuffled=bank['metrics']['coherent_shuffle'],
                        development_diagnostics=diagnostics))
                    print(f"review {item['name']} site{site} {backend} seed{bank['seed']}", flush=True)
        behavior_folder = folder.parent/'behavior'
        receipt = base._json(behavior_folder/'completion_manifest_v1.json')
        entry = receipt['artifacts']['responses']
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('completed behavior responses changed')
        source_rows = {r['id']: r for r in rows}
        signatures = defaultdict(Counter)
        for response in map(json.loads, Path(entry['path']).read_text().splitlines()):
            original = source_rows[response['id']]
            if original['split'] != 'development':
                continue
            from .overnight_relationship_behavior import parse_integer
            if parse_integer(response['raw_response']) != response['parsed'] or (response['parsed'] == original['expected_answer']) != response['correct']:
                raise ValueError('response scoring changed')
            kind = 'arithmetic_written' if original['oracle']['definitions'][original['query_slot']] >= 4 else 'untouched_literal'
            signatures[kind][match_signature(original, response)] += 1
        models[item['name']] = dict(banks=banks, behavior_match_signatures=dict(signatures),
            capture_source=preflight['source'], readout_source=result['source'], cases=len(rows),
            training_rows=int(train.sum()), development_rows=int(dev.sum()))
    review = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config),
        analysis_source=source, models=models, new_model_queries=0, new_fits=0,
        parameter_application_rows=sum(v['cases']*len(v['banks']) for v in models.values()),
        generated_holdouts_opened=False,
        limitations='Adaptive postrun diagnostics. Numeric match categories are coincidences, not causal error labels. Training scores measure interpolation. No selected layer, decoder refit, causal patch or untouched evaluation.')
    publish(config, review)
    base._put(out/'review.json', review)
    paths={'review':out/'review.json','report':Path(config['report']),
           'figure':Path(config['figure']),'vector':Path(config['figure']).with_suffix('.svg')}
    base._put(out/'completion_manifest_v1.json',dict(status='complete_exploratory',evaluation_role=ROLE,
        config_hash=digest(config),analysis_source=source,new_model_queries=0,new_fits=0,
        artifacts={k:dict(path=str(v),sha256=base._sha(v),bytes=v.stat().st_size) for k,v in paths.items()}))
    return review


def publish(config, review):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.fonttype'] = 'none'
    text=['# Morning review of the arithmetic relationship suite', '', review['limitations'], '',
          '| Model | Site | Features | TRAIN parent | DEV parent | TRAIN whole graph | DEV whole graph | DEV parent prior |',
          '|---|---|---|---:|---:|---:|---:|---:|']
    signatures=[]
    fig, axes = plt.subplots(1, len(review['models']), figsize=(11, 4.4), constrained_layout=True)
    for ax, (name, model) in zip(np.atleast_1d(axes), review['models'].items()):
        for site in (1, 2):
            for backend in ('hidden', 'source'):
                banks=[b for b in model['banks'] if b['site']==site and b['backend']==backend]
                def avg(section, key):return float(np.mean([b[section][key] for b in banks]))
                cells=[avg('train','parent_accuracy'),avg('development','parent_accuracy'),
                       avg('train','whole_parent_accuracy'),avg('development','whole_parent_accuracy'),
                       avg('prior','parent_accuracy')]
                text.append('| '+' | '.join([name, str(site), backend, *(f'{100*v:.2f}%' for v in cells)])+' |')
                if site==2 and backend=='hidden':
                    width=.34; x=np.arange(2)
                    bars=ax.bar(x-width/2,[100*cells[0],100*cells[2]],width,label='TRAIN',color='#4b82b8')
                    ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=8)
                    bars=ax.bar(x+width/2,[100*cells[1],100*cells[3]],width,label='DEV',color='#c47845')
                    ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=8)
                    ax.scatter(x,[100*cells[4],100*avg('prior','whole_parent_accuracy')],
                        marker='_',s=220,color='#555555',label='TRAIN prior on DEV',zorder=5)
        ax.set(title=name+' · answer preparation',ylabel='Accuracy (%)',ylim=(0,105))
        ax.set_xticks([0,1],['Individual parents','All eight parents']);ax.legend(frameon=False)
        signatures+=['',name+' DEV numeric match signatures: `'+json.dumps(model['behavior_match_signatures'],sort_keys=True)+'`','']
    fig.suptitle('Readouts fit training graphs but fail to transfer to held-out families')
    path=Path(config['figure']);path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=180);fig.savefig(path.with_suffix('.svg'));plt.close(fig)
    text+=signatures
    text+=['','TRAIN/DEV comparisons use the same frozen parameters. Every reconstructed training input is hash-checked against its saved fit. DEV numerical replay permits only1e-10 floating-point tolerance; categorical and binary decisions must match exactly. All sites/backends remain in the JSON, including priors, coherent shuffles, value-class coverage and queried/unqueried accuracy.','']
    base._publish(config['report'], ('\n'.join(text)+'\n').encode())
