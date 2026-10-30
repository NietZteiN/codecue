"""Reproduce the discovery/control figure from two immutable JSON results."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
ORIGINAL=ROOT/'artifacts/binding/relationship_readouts/llama31_8b_v3/results_v1.json'
FOLLOWUP=ROOT/'artifacts/binding/relationship_followup/llama31_8b_v1/results_v1.json'
a=json.loads(ORIGINAL.read_text());b=json.loads(FOLLOWUP.read_text())
blue,gray,green='#2878b5','#8b929a','#278a67'
fig,axes=plt.subplots(1,3,figsize=(14.4,4.9))
vals=[a['primary']['algebraic']['methods']['direct']['score'],a['primary']['algebraic']['methods']['categorical_value_derived']['score'],b['strong_source_control']['methods']['source_categorical_value_derived']['score']]
bars=axes[0].bar(range(3),100*np.array(vals),color=[blue,gray,green],width=.7)
axes[0].set_xticks(range(3),['Hidden\ndirect','Hidden values\n→ relations','Source values\n→ relations'])
axes[0].set_title('Algebraic relations at initialization')
axes[0].set_ylabel('Four-family macro balanced accuracy (%)')
axes[0].bar_label(bars,fmt='%.1f',padding=3)
x=np.arange(2);width=.34
for backend,color,offset,label in [('hidden',blue,-width/2,'Hidden direct'),('surface',gray,width/2,'Source direct')]:
    values=[100*np.mean([f['metrics']['development']['direct']['parent_graph']['whole_graph_accuracy'] for f in a['fits'] if f['backend']==backend and f['layer']==(24 if backend=='hidden' else -1) and f['site']==site]) for site in (7,8)]
    bars=axes[1].bar(x+offset,values,width,color=color,label=label);axes[1].bar_label(bars,fmt='%.1f',padding=3)
axes[1].set_xticks(x,['Last assignment','Final prompt']);axes[1].set_title('Complete parent graph')
axes[1].set_ylabel('Whole-graph accuracy (%)');axes[1].legend(frameon=False,loc='upper right')
for backend,color,offset,label in [('hidden',blue,-width/2,'Hidden direct'),('surface',gray,width/2,'Source direct')]:
    values=[100*np.mean([r['metrics']['component_macro']['both_first_parents_correct'] for r in b['provenance_pair_evaluations'] if r['backend']==backend and r['site']==site]) for site in (7,8)]
    bars=axes[2].bar(x+offset,values,width,color=color,label=label);axes[2].bar_label(bars,fmt='%.1f',padding=3)
axes[2].set_xticks(x,['Last assignment','Final prompt']);axes[2].set_title('Equal states, different first-copy parents')
axes[2].set_ylabel('Both first parents correct (%)')
for ax in axes:
    ax.set_ylim(0,112);ax.set_yticks([0,25,50,75,100]);ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Relationship decoding on the fixed copy-routing discovery bank',fontsize=14,y=.99)
contrast=b['strong_source_control']['comparisons']['direct_minus_source_categorical_value_derived']
lo,hi=contrast['conditional_group_bootstrap_95']
foot=(f"Layer 24; three weighting seeds; nine development components. Hidden direct − source-value algebraic contrast: {100*contrast['mean']:+.2f} pp "
      f"(conditional 95% [{100*lo:+.2f}, {100*hi:+.2f}]).\n"
      'Source-value contrast and paired controls are posthoc. Paired bars: 72 lexical pairs / 36 numeric bases; component means across seeds, no pair-level interval.\n'
      'Copy-only programs and known graph scaffold; no causal-use claim. Bars show point estimates; uncertainty belongs to the specified contrasts.')
fig.text(.02,.01,foot,ha='left',va='bottom',fontsize=8.4)
fig.tight_layout(rect=(0,.16,1,.94))
out=ROOT/'reports/binding/figures/relationship_controls_v1'
fig.savefig(out.with_suffix('.png'),dpi=180,bbox_inches='tight');fig.savefig(out.with_suffix('.svg'),bbox_inches='tight');plt.close(fig)
manifest={'evaluation_role':'posthoc_discovery_relationship_figure_v1','source_files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [ORIGINAL,FOLLOWUP,Path(__file__)]],
'figures':[{'path':str(out.with_suffix(s).relative_to(ROOT)),'sha256':hashlib.sha256(out.with_suffix(s).read_bytes()).hexdigest()} for s in ['.png','.svg']],
'new_model_queries':0,'new_fits':0,'generated_holdouts_opened':False,'points_only':True,'posthoc_controls_explicit':True}
(ROOT/'artifacts/binding/relationship_followup/figure_review_v1.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print('Saved reproducible PNG/SVG and source-pin manifest.')
