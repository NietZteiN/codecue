#!/usr/bin/env python
"""Render every registered literal-routing contrast from a completed audit."""
import argparse
import hashlib
import json
from pathlib import Path


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_controls(config):
    """Verify analytic boundary controls independently of the scientific effect."""
    from codecue.binding.published_benchmarks import immutable
    root = Path(config['run_dir']) / 'interventions'
    audit = json.loads((root / 'audit.json').read_text())
    summary = json.loads((root / 'summary.json').read_text())
    baselines = json.loads((root / 'baselines.json').read_text())
    replays = json.loads((root / 'replays.json').read_text())
    manifest = json.loads((root / 'manifest.json').read_text())
    if (audit['status'] != 'passed' or not summary.get('answer_digit_boundary_checked')
            or not config.get('require_digit_first') or manifest['identity']['config'] != config
            or checksum(root / 'baselines.json') != audit['baseline_sha256']
            or checksum(root / 'replays.json') != audit['replay_metadata_sha256']):
        raise ValueError('digit-aligned completed audit required for control verification')
    counts = dict(final_answer_vector_copies_donor=0, final_literal_controls_preserve_recipient=0,
                  identity_shams_preserve_recipient=0)
    max_norm_error = 0.
    final_layer = max(config['layers'])
    for path, expected in audit['chunk_checksums'].items():
        if checksum(path) != expected:
            raise ValueError('audited control chunk changed')
        for row in json.loads(Path(path).read_text()):
            condition = row['condition']
            if row['layer'] == final_layer and condition == 'answer_vector':
                if row['first_token'] != baselines[row['donor']]['first_token']:
                    raise ValueError('final answer-vector positive control failed to copy donor token')
                counts['final_answer_vector_copies_donor'] += 1
            if condition == 'identity_sham' or (row['layer'] == final_layer and condition != 'answer_vector'):
                if row['first_token'] != replays[row['pair_id']]['first_token']:
                    raise ValueError('analytic zero-effect control changed recipient token')
                key = 'identity_shams_preserve_recipient' if condition == 'identity_sham' else 'final_literal_controls_preserve_recipient'
                counts[key] += 1
            if condition == 'unrelated_position' or condition.startswith('random_'):
                target = row['target_effective_norm']
                error = abs(row['actual_effective_norm'] - target) / target if target else abs(row['actual_effective_norm'])
                max_norm_error = max(max_norm_error, error)
    pairs = summary['directed_pairs']
    if counts != dict(final_answer_vector_copies_donor=pairs,
            final_literal_controls_preserve_recipient=pairs * 5,
            identity_shams_preserve_recipient=pairs * len(config['layers'])):
        raise ValueError('analytic control coverage incomplete')
    result = dict(status='passed', audit_sha256=checksum(root / 'audit.json'),
        review_source_sha256=checksum(__file__), counts=counts, max_relative_norm_error=max_norm_error,
        interpretation='Post-run analytic software checks; independent of whether literal transfers change answers.',
        generated_holdouts_opened=False)
    immutable(root / 'analytic_controls.json', (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return result


def review(config):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from codecue.binding.datasets import digest, write_json
    from codecue.binding.published_benchmarks import immutable
    from codecue.binding.value_transfer import CONDITIONS
    root = Path(config['run_dir']) / 'interventions'
    audit_path = root / 'audit.json'
    audit = json.loads(audit_path.read_text())
    manifest = json.loads((root / 'manifest.json').read_text())
    if (audit['status'] != 'passed' or manifest['status'] != 'complete'
            or manifest['identity_hash'] != digest(manifest['identity'])
            or audit['identity_hash'] != manifest['identity_hash']
            or manifest['identity']['config'] != config):
        raise ValueError('review requires a complete audit of the requested identity')
    for path, expected in audit['chunk_checksums'].items():
        if checksum(path) != expected:
            raise ValueError('audited intervention chunk changed')
    if checksum(root / 'baselines.json') != audit['baseline_sha256']:
        raise ValueError('audited baseline changed')
    layers = config['layers']
    results = audit['results']
    rows = {(r['family'], r['layer'], r['condition'], r['affected'], r['both_baselines_correct_only']): r for r in results}
    if len(rows) != len(layers) * len(CONDITIONS) * 8:
        raise ValueError('registered analysis cells incomplete or duplicated')
    destination = Path('reports/binding')
    version = config.get('analysis_version', 'v1')
    suffix = '' if version == 'v1' else '_' + version
    figure_path = destination / f'value_transfer_effects{suffix}.svg'
    labels = ['Literal', 'Unrelated\nposition', 'Answer\nvector', 'Sham', 'Random\n11', 'Random\n29', 'Random\n47']
    figure, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True, sharey=True, layout='constrained')
    for family_index, family in enumerate(('ownership', 'versions')):
        for column, affected in enumerate((True, False)):
            values = np.array([[100 * rows[family, layer, condition, affected, False]['replacement_token_rate']
                                for condition in CONDITIONS] for layer in layers])
            ax = axes[family_index, column]
            graphic = ax.imshow(values, vmin=0, vmax=100, cmap='viridis', aspect='auto')
            ax.set_title(f'{family.title()}: ' + ('changed-answer query' if affected else 'unchanged-answer control'))
            ax.set_xticks(range(len(labels)), labels)
            ax.set_yticks(range(len(layers)), [str(layer) for layer in layers])
            ax.set_ylabel('Raw block')
            for i in range(len(layers)):
                for j in range(len(labels)):
                    ax.text(j, i, f'{values[i,j]:.1f}', ha='center', va='center',
                            color='black' if values[i,j] > 55 else 'white', fontsize=9)
    figure.colorbar(graphic, ax=axes, label='Replacement-digit next-token rate (%)', shrink=0.85)
    figure.suptitle('Literal-value routing discovery: all registered cases and conditions')
    figure.savefig(figure_path)
    figure.savefig(figure_path.with_suffix('.png'), dpi=160)
    plt.close(figure)
    summary = json.loads((root / 'summary.json').read_text())
    lines = ['# Literal-value routing discovery results', '',
        f"All {audit['baseline_cases']:,} complete baseline responses and {audit['intervention_forwards']:,} intervention forwards are audited. "
        f"Baseline literal correctness is {audit['baseline_correct']}/{audit['baseline_cases']}. "
        f"All {summary['first_token_consistency_cases']} generation-prefill checks passed; "
        f"same-batch forward replays match the generation first token on {summary['generation_replay_first_token_matches']}/{summary['directed_pairs']} directed pairs. "
        'Every identity sham preserves its same-batch replay, and every random/unrelated-position control passes its effective BF16 norm check.', '',
        f'![All registered literal-routing interventions]({figure_path.name})', '',
        'The heatmaps show the replacement digit, including when it is **not** the correct answer for the unchanged-answer query. '
        'These are next-token measurements on single-digit literals, not complete-output intervention accuracy. '
        'Full answer-vector transfer is an answer-copy software positive control. '
        'All cases are included; the audited artifact separately retains the subset where both complete baseline answers were correct, '
        'plus both directions, lexical realizations and mappings.', '']
    for family in ('ownership', 'versions'):
        lines += [f'## {family.title()}', '',
            '| Block | Condition | n per query type | Replacement, changed query (%) | Replacement, unchanged query (%) | Log-odds change, changed | Log-odds change, unchanged |',
            '|---:|---|---:|---:|---:|---:|---:|']
        for layer in layers:
            for condition in CONDITIONS:
                changed = rows[family, layer, condition, True, False]
                unchanged = rows[family, layer, condition, False, False]
                lines.append(f"| {layer} | {condition} | {changed['n']}/{unchanged['n']} | "
                    f"{100*changed['replacement_token_rate']:.2f} | {100*unchanged['replacement_token_rate']:.2f} | "
                    f"{changed['logodds_change']:.3f} | {unchanged['logodds_change']:.3f} |")
        lines.append('')
    lines += ['There are two templates per family, two neutral lexical realizations and nine cyclic numeric triples. '
        'No layer was confirmed by held-out selection, and no population-level or multiplicity-adjusted inference is claimed. '
        'A successful early literal patch establishes an effect of changing that local activation in this assay; it does not isolate a binding code '
        'or explain failures on the earlier competition cohort. Computed-value transport and causal prediction of held-out errors remain untested.', '',
        f"Frozen inference identity: `{audit['identity_hash']}`. Audit: `{audit_path}`. "
        f"Reproduce with `PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/111_binding_value_transfer_review.py configs/binding/competition/value_transfer_{version}.json`. "
        'See [the pre-inference design](value_transfer_plan.md). Generated final/extrapolation outcomes remain sealed.']
    if config.get('require_digit_first'):
        lines.insert(3, 'The answer-boundary gate passed on every baseline: the measured first token is the parsed digit, including incorrect predictions. '
            'The fixed space prefix matches the formatting token observed in all previous baselines; every new input is exactly the previous input plus that token. '
            'See [the boundary correction](value_transfer_boundary_correction.md). An isolated post-block literal patch leaves other positions’ earlier states intact, '
            'so failed transfer does not establish missing value information.\n')
    report = destination / f'value_transfer_results{suffix}.md'
    immutable(report, ('\n'.join(lines) + '\n').encode())
    artifact = dict(status='complete_audited', audit=str(audit_path), audit_sha256=checksum(audit_path),
        report=str(report), figure=str(figure_path), baseline_cases=audit['baseline_cases'],
        baseline_correct=audit['baseline_correct'], intervention_forwards=audit['intervention_forwards'],
        main_results=results, limitation=audit['limitation'], generated_holdouts_opened=False)
    write_json(f'artifacts/binding/value_transfer/comparison_{version}.json', artifact)
    return {k: v for k, v in artifact.items() if k != 'main_results'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('--verify-controls', action='store_true')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    print(json.dumps(verify_controls(config) if args.verify_controls else review(config), indent=2))


if __name__ == '__main__':
    main()
