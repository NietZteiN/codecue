#!/usr/bin/env python
"""Plot every registered paired behavioral contrast from its audited artifact."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('config')
    cfg=json.loads(Path(parser.parse_args().config).read_text())
    source=Path(cfg['source'])
    if hashlib.sha256(source.read_bytes()).hexdigest()!=cfg['source_sha256']:
        raise ValueError('figure source checksum changed')
    result=json.loads(source.read_text())
    if result['status']!='passed' or not result['complete']:raise ValueError('audited results required')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    colors=['#1c648b','#c36a24']
    contrasts=[('three_minus_one_updates','Three versus one reassignment'),
               ('tail_after_minus_before','Dead statements after versus before'),
               ('misleading_minus_informative','Misleading versus informative names')]
    models=[('codellama34b','CodeLlama 34B'),('llama31_8b','Llama 3.1 8B')]
    limits=[]
    fig,axes=plt.subplots(2,3,figsize=(12,5.8),sharex=True,layout='constrained')
    for row,query in enumerate(('current','saved')):
        for col,(contrast,title) in enumerate(contrasts):
            ax=axes[row,col];ax.axvline(0,color='#999999',lw=.8,ls='--')
            for index,(key,label) in enumerate(models):
                matches=[r for r in result['results'][key]['paired_effects'] if r['query_role']==query and r['contrast']==contrast]
                if len(matches)!=1:raise ValueError('figure contrast coverage differs')
                effect=matches[0];value=100*effect['estimate'];interval=effect['exploratory_cluster_bootstrap_95_interval']
                if interval is None:raise ValueError('figure requires recorded structural intervals')
                lo,hi=np.array(interval)*100
                limits.extend([lo,hi])
                ax.errorbar(value,1-index,xerr=[[value-lo],[hi-value]],fmt='o',color=colors[index],capsize=4,lw=1.7,ms=6)
                ax.annotate(f'{value:+.1f}',(value,1-index),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9)
            ax.set_yticks([1,0],labels=[m[1] for m in models] if col==0 else ['', ''])
            ax.set_ylim(-.55,1.65);ax.spines[['top','right','left']].set_visible(False)
            ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.15)
            if row==0:ax.set_title(title,fontsize=10)
            if col==0:ax.set_ylabel(query.capitalize()+' binding',fontsize=11)
            if row==1:ax.set_xlabel('Paired accuracy change (percentage points)',fontsize=9)
    span=max(limits)-min(limits)
    for ax in axes.flat:ax.set_xlim(min(limits)-.08*span,max(limits)+.12*span)
    fig.suptitle('Matched arithmetic-free binding discovery',fontsize=14)
    for suffix in ('svg','png'):
        path=Path(cfg['output_prefix']+'.'+suffix);path.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(path,dpi=180)
    plt.close(fig)


if __name__=='__main__':main()
