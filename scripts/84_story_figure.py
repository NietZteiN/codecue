#!/usr/bin/env python
"""Main evidence as two readable questions; technical layer curves stay in the appendix.

CPU only: python scripts/84_story_figure.py
All plotted quantities come from validated, saved summaries. Panels are separate cohorts.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from codecue.config import PROJECT_ROOT

MODELS = [('olmo2-7b-it', 'OLMo-2-7B'), ('llama32-3b-it', 'Llama-3.2-3B'),
          ('llama31-8b-it', 'Llama-3.1-8B')]
GREEN, RED, BLUE = '#157A55', '#B5321F', '#2B4A9E'


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
    root = PROJECT_ROOT / 'results' / 'summary'
    probe = json.loads((root/'round6_crossfit_probes.json').read_text())
    repl = json.loads((root/'round6_identifier_replication.json').read_text())
    assert probe['validated'] and repl['validated']
    fig = plt.figure(figsize=(7.2, 3.55))
    fig.text(.02, .96, 'A wrong write can coexist with a readable correct value', fontsize=12,
             weight='bold', va='top')
    fig.text(.02, .83, '(a) Correct digit read before a wrong sum write', weight='bold')
    fig.text(.02, .755, 'Separate predictor reads internal activity.\nOriginal names; training uses other programs.', fontsize=8.5, va='top')
    fig.text(.55, .83, '(b) Include the code expression in examples', weight='bold')
    fig.text(.55, .755, 'Fresh programs; names screened before testing.', fontsize=8.5)
    ax = fig.add_axes([.18, .30, .29, .36])
    payload = {'probe': {}, 'replication': {}}
    for y, (key, label) in zip([2, 1, 0], MODELS):
        row = probe['models'][key]['pooled']['lure_write']
        mean, lo, hi = [100*x for x in row['accuracy_ci95']]
        ax.barh(y, mean, height=.52, color=GREEN, alpha=.18)
        ax.errorbar(mean, y, xerr=[[mean-lo], [hi-mean]], fmt='o', color=GREEN, capsize=3)
        ax.text(40, y, f'{mean:.1f}%', va='center', weight='bold', color=GREEN)
        payload['probe'][key] = row
    ax.set_yticks([2, 1, 0], [lab for _, lab in MODELS]); ax.tick_params(axis='y', length=0)
    ax.set_xlim(0, 103); ax.set_ylim(-.6, 2.6); ax.set_xticks([0, 50, 100])
    ax.set_xlabel('Correct predictions (%)', fontsize=9)
    ax.grid(axis='x', alpha=.15)
    fig.text(.02, .04, 'Readable information does not show that the model uses it.', fontsize=8.5)
    ax = fig.add_axes([.69, .30, .29, .36])
    rows = MODELS + [('codegemma-7b-it', 'CodeGemma-7B')]
    # Find the control's exact saved key rather than silently omit it.
    if rows[-1][0] not in repl['models']:
        rows[-1] = (next(k for k in repl['models'] if 'codegemma' in k), 'CodeGemma-7B')
    for y, (key, label) in zip([3, 2, 1, 0], rows):
        for regime, offset, color, marker, legend in [
            ('trace', .12, RED, 'o', 'Examples: v = 2'),
            ('trace_expr', -.12, BLUE, 's', 'Examples: v = len(xs) = 2')]:
            triple = repl['models'][key][regime]['excess_ci95']
            mean, lo, hi = [100*x for x in triple]
            ax.errorbar(mean, y+offset, xerr=[[mean-lo], [hi-mean]], fmt=marker,
                        color=color, capsize=2, ms=4, label=legend if y == 3 else None)
            payload['replication'].setdefault(key, {})[regime] = triple
    ax.set_yticks([3, 2, 1, 0], [lab for _, lab in rows]); ax.tick_params(axis='y', length=0, labelsize=8)
    ax.set_xlim(-4, 100); ax.set_ylim(-.6, 3.6); ax.set_xticks([0, 50, 100])
    ax.axvline(0, color='.65', lw=.8); ax.grid(axis='x', alpha=.15)
    ax.set_xlabel('Added wrong sum writes (points)', fontsize=8.5)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(.55, .115), frameon=False, fontsize=8, borderaxespad=0)
    fig.text(.02, .13, '95% intervals. Added writes = misleading-name rate minus ordinary-name rate.', fontsize=8.5)
    dest = PROJECT_ROOT/'paper'/'figures'; dest.mkdir(exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(dest/f'story_evidence.{ext}', dpi=180)
    (dest/'story_evidence_data.json').write_text(json.dumps(payload, indent=2)+'\n')
    print('wrote', dest/'story_evidence.pdf')


if __name__ == '__main__':
    main()
