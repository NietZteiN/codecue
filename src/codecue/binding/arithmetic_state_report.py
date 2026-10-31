"""Human-readable state-study reports from immutable audits/compositions."""
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

AUDIT_ROLE = 'discovery_arithmetic_local_audit_report_v1'
STATE_ROLE = 'discovery_arithmetic_state_report_v1'


def _finish(config, source, text, inputs, extra=None):
    path = Path(config['report'])
    base._publish(path, ('\n'.join(text) + '\n').encode())
    result = dict(status='complete_exploratory', evaluation_role=config['evaluation_role'], source=source,
        config_hash=digest(config), inputs=inputs, new_fits=0, new_model_queries=0, **(extra or {}))
    artifacts = dict(report=storage._pin(path), **(extra or {}).get('figure_artifacts', {}))
    return common.receipt(config, source, result, artifacts)


def audit_report(config):
    source = common.validate_role(config, AUDIT_ROLE)
    if (Path(config['run_dir']) / 'completion_manifest_v1.json').exists():
        return common.completed(config)
    models, inputs = {}, {}
    for item in config['models']:
        cfg = base._json(item['config'], item['sha256'])
        audit.audit(cfg)
        path = Path(cfg['run_dir']) / 'summary_review_v1.json'
        models[item['name']] = base._json(path)
        inputs[item['name']] = storage._pin(path)
    text = ['# Local dependency readouts: completed discovery results', '',
        'Both checkpoints completed 5,292 causal local captures and 5,508 short-arithmetic answers. All 54 post-selection readouts per checkpoint were independently reapplied from saved parameters. The audit checked capture checksums, native point identities, independent source read-time traces, grouped TRAIN selection, strict response parsing and saved dependency decisions. No audit fits or language-model calls were made.', '',
        '| Model | Backend | Selected architecture | Family-macro parent accuracy | Whole-program graph | Random-family control |',
        '|---|---|---|---:|---:|---:|']
    chart = {}
    for name, model in models.items():
        chart[name] = {}
        for backend in ('hidden_local', 'hidden_global', 'source_local'):
            real = [b for b in model['replayed_banks'] if b['backend'] == backend and b['target'] == 'real' and b['training_families'] == 216]
            controls = [b for b in model['replayed_banks'] if b['backend'] == backend and b['target'] == 'random_family' and b['training_families'] == 216]
            mean = lambda banks, metric: float(np.mean([b['development'][metric] for b in banks]))
            accuracy, whole, control = mean(real, 'family_macro_accuracy'), mean(real, 'whole_program_graph_accuracy'), mean(controls, 'family_macro_accuracy')
            chart[name][backend] = dict(accuracy=accuracy, whole=whole, control=control)
            text.append(f"| {name} | {backend} | {model['selected_methods'][backend]} | {100 * accuracy:.2f}% | {100 * whole:.2f}% | {100 * control:.2f}% |")
    text += ['', 'Whole graphs have four/eight/twelve ordered parents at depths two/four/six. All metrics above are on the new 72-family development cohort, averaged over the three weighting seeds. The answer-query backend also receives earlier candidate-definition states, so it is not a probe of one final vector alone. Every backend receives candidate boundaries and statement/side coordinates. Exact source-name/recency parsing recovers 100%; the hashed character comparator is a limited learned source baseline. Selected architectures differ, and capacity-matched counterparts are a separately declared follow-up.', '',
        'This study changes data diversity, decoder architecture, candidate constraints and token access relative to the original global study. Its gains cannot be attributed solely to localization, and they do not establish causal use or a maintained complete numeric state. These are adaptive discovery findings.', '',
        '| Model | Training structures | Local hidden parents | Source parents | Local hidden complete graph |', '|---|---:|---:|---:|---:|']
    for name, model in models.items():
        for budget in (54, 108, 216):
            local = [b for b in model['replayed_banks'] if b['backend'] == 'hidden_local' and b['target'] == 'real' and b['training_families'] == budget]
            surface = [b for b in model['replayed_banks'] if b['backend'] == 'source_local' and b['target'] == 'real' and b['training_families'] == budget]
            a = np.mean([b['development']['family_macro_accuracy'] for b in local])
            s = np.mean([b['development']['family_macro_accuracy'] for b in surface])
            g = np.mean([b['development']['whole_program_graph_accuracy'] for b in local])
            text.append(f'| {name} | {budget} | {100 * a:.2f}% | {100 * s:.2f}% | {100 * g:.2f}% |')
    text += ['', '| Model | Instruction | Cohort | Depth | Query type | Correct / cases | Invalid | Accuracy |', '|---|---:|---|---:|---|---:|---:|---:|']
    for name, model in models.items():
        for m in model['behavior']:
            if m['split'] == 'train':
                continue
            text.append(f"| {name} | I{m['instruction']} | {m['split']} | {m['depth']} | {m['query_kind']} | {m['correct']}/{m['cases']} | {m['invalid']} | {100 * m['accuracy']:.2f}% |")
    text += ['', 'Arithmetic-written answers remain unreliable and sensitive to wording. All three instructions and invalid responses are retained. Representation captures use I0 only; no cross-instruction hidden-state comparison is implied. Calibration families never enter probe fits. Next steps test current-definition lookup, role-conditioned numeric decoding and algebraic relations derived from predicted states, using the saved activations.', '']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))
    for ax, metric, title in zip(axes, ('accuracy', 'whole'), ('Individual dependency parents', 'Complete program graph')):
        for offset, backend, label, color in [(-.25, 'hidden_local', 'Local hidden', '#307aab'),
                (0, 'hidden_global', 'Answer query + candidates', '#8da0b6'), (.25, 'source_local', 'Source character probe', '#65a89b')]:
            vals = [100 * chart[name][backend][metric] for name in models]
            ax.bar(np.arange(len(models)) + offset, vals, .23, label=label, color=color)
            for x, v in zip(np.arange(len(models)) + offset, vals):
                ax.text(x, v + 2, f'{v:.1f}', ha='center', fontsize=9)
        ax.set_xticks(range(len(models)), ['Llama 8B', 'CodeLlama 34B'])
        ax.set_title(title, pad=12)
        ax.set_ylim(0, 105)
        ax.set_ylabel('Accuracy (%)')
        ax.spines[['top', 'right']].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .93), ncol=3, frameon=False, fontsize=9)
    fig.suptitle('Local dependency recovery on new discovery families', y=.99, fontsize=15)
    fig.text(.02, .025, '72 structural DEV families; three weighting seeds. Candidate scaffold supplied. Architectures selected inside TRAIN.\nExact source recency oracle: 100%. No causal-use claim; this is a different protocol from the original global study.', fontsize=9)
    fig.tight_layout(rect=[0, .12, 1, .84])
    stem = config['figure']
    figure_artifacts = {}
    for suffix in ('.png', '.svg'):
        path = Path(stem + suffix)
        fig.savefig(path, dpi=170, metadata={'Date': None} if suffix == '.svg' else None)
        figure_artifacts[suffix[1:]] = storage._pin(path)
    plt.close(fig)
    text.insert(4, '![Local dependency recovery](figures/' + Path(stem).name + '.png)\n')
    return _finish(config, source, text, inputs, dict(summary=chart, figure_artifacts=figure_artifacts))


def state_report(config):
    source = common.validate_role(config, STATE_ROLE)
    if (Path(config['run_dir']) / 'completion_manifest_v1.json').exists():
        return common.completed(config)
    inputs, results = {}, {}
    text = ['# Current bindings, numeric states and derived relationships', '',
        'Adaptive follow-up on the already inspected structural development families. Primary pipeline: variable-anchor query -> predicted current definition -> role-conditioned regression -> derived algebraic relations. Independent models are composed without new fitting. Source node/slot scaffolds remain supplied; exact execution is a 100% source ceiling.', '',
        '| Model | Route | Numeric decoder | Binding accuracy | Whole numeric state | Value MAE | Derived relation balanced accuracy |',
        '|---|---|---|---:|---:|---:|---:|']
    for item in config['models']:
        cfg = base._json(item['config'], item['sha256'])
        common.completed(cfg)
        path = Path(cfg['run_dir']) / 'results.json'
        model = base._json(path)
        inputs[item['name']] = storage._pin(path)
        grouped = defaultdict(list)
        for panel in model['pipelines']:
            grouped[(panel['route'], panel['numeric_backend'], panel['numeric_format'])].append(panel['panels']['development'])
        results[item['name']] = {}
        for (route, backend, kind), panels in sorted(grouped.items()):
            avg = lambda key: float(np.mean([p[key] for p in panels]))
            relation = [p['relations']['macro_balanced_accuracy'] for p in panels]
            score = float(np.mean([v for v in relation if v is not None])) if any(v is not None for v in relation) else None
            binding_score = avg('binding_accuracy') if 'binding_accuracy' in panels[0] else None
            binding_text = 'supplied' if route == 'oracle_route' else 'n.a.' if binding_score is None else f'{100 * binding_score:.2f}%'
            relation_text = 'undefined' if score is None else f'{100 * score:.2f}%'
            text.append(f"| {item['name']} | {route} | {backend}/{kind} | {binding_text} | {100 * avg('whole_state_accuracy'):.2f}% | {avg('family_macro_mae'):.3f} | {relation_text} |")
            results[item['name']][str((route, backend, kind))] = dict(whole_state_accuracy=avg('whole_state_accuracy'), mae=avg('family_macro_mae'), relations=score)
    text += ['', 'All declared routes, encodings, layers selected within TRAIN, control tasks and priors remain in machine-readable results. Relation cells require TRAIN support and both evaluation classes; undefined cells are retained. The oracle route supplies correct binding pointers and is not end-to-end decoding. Operand composition supplies source operators and performs external arithmetic on decoded read operands; it is not evidence that a neural computed result was decoded. Version accuracy annotates predicted definition nodes rather than independently probing version labels. Pure answer-state numeric heads use one final state; answer-query routing additionally sees earlier candidate states. Calibration scores remain separate and never train a probe.', '',
        '| Model | Numeric features/encoding | Computed-write MAE | Computed-write exact | Read-computed-operand MAE | Root exact | Prior write MAE | Shuffled write MAE |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for item in config['models']:
        cfg = base._json(item['config'], item['sha256'])
        numeric_cfg = base._json(cfg['numeric_config'], cfg['numeric_config_sha256'])
        common.completed(numeric_cfg)
        model = base._json(Path(numeric_cfg['run_dir']) / 'results.json')
        grouped = defaultdict(list)
        for bank in model['fits']:
            grouped[(bank['backend'], bank['format'])].append(bank)
        for (backend, kind), banks in sorted(grouped.items()):
            avg = lambda panel, category, metric: float(np.mean([b[panel]['per_kind'][category][metric] for b in banks]))
            text.append(f"| {item['name']} | {backend}/{kind} | {avg('development', 'computed_definition', 'family_macro_mae'):.3f} | "
                f"{100 * avg('development', 'computed_definition', 'family_macro_exact_accuracy'):.2f}% | "
                f"{avg('development', 'operand_from_computed', 'family_macro_mae'):.3f} | {100 * avg('development', 'root_definition', 'family_macro_exact_accuracy'):.2f}% | "
                f"{avg('development_prior', 'computed_definition', 'family_macro_mae'):.3f} | {avg('development_control', 'computed_definition', 'family_macro_mae'):.3f} |")
    text += ['', 'Numeric layers/alphas are selected separately per encoding from TRAIN computed-write MAE. Read and write roles have independent feature blocks even when they share a token. The numeric source comparator and conditional TRAIN priors remain explicit.', '',
        '| Model | Matched architecture | Counterpart features | Real dependency accuracy | Random-family control |',
        '|---|---|---|---:|---:|']
    for item in config['capacity_models']:
        cfg = base._json(item['config'], item['sha256'])
        common.completed(cfg)
        model = base._json(Path(cfg['run_dir']) / 'results.json')
        for backend in ('hidden_global', 'source_local'):
            real = [b for b in model['fits'] if b['backend'] == backend and b['target'] == 'real']
            controls = [b for b in model['fits'] if b['backend'] == backend and b['target'] == 'random_family']
            mean = lambda banks: float(np.mean([b['development']['family_macro_accuracy'] for b in banks]))
            text.append(f"| {item['name']} | {model['reference_method']} | {backend} | {100 * mean(real):.2f}% | {100 * mean(controls):.2f}% |")
    text += ['', 'Counterpart architecture is fixed to the original TRAIN-selected local method; this follow-up makes no additional model selection. Original primary decoder selections remain preserved. All results here are adaptive discovery, with no causal-use or untouched-confirmation claim.', '']
    return _finish(config, source, text, inputs, dict(summary=results))
