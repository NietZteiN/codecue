"""Editable conceptual diagrams and a Python-ground-truth walkthrough.

These are illustrations, not measured model activations or experimental results.
"""
import ast
import io
import json
from pathlib import Path

PROGRAM = ('x = 2', 'y = x', 'x = 7', 'z = x - y')
ROOT = Path(__file__).resolve().parents[4]


def trace():
    state, previous, steps = {}, {}, [dict(line=0, state={}, previous={})]
    for index, line in enumerate(PROGRAM, 1):
        node = ast.parse(line).body[0]
        target = node.targets[0].id
        if target in state: previous[target] = state[target]
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<illustrative program>', 'exec'), {'__builtins__': {}}, state)
        steps.append(dict(line=index, state=dict(state), previous=dict(previous)))
    assert steps[-1]['state'] == dict(x=7, y=2, z=5)
    assert steps[-1]['previous'] == dict(x=2)
    assert steps[2]['state']['y'] == steps[3]['state']['y'] == 2
    return steps


def build_figures(publish):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'binding-concepts-20261029'})
    navy, blue, orange, green, purple = '#173e54', '#2c7da0', '#d47d34', '#36836a', '#7a64a4'
    def box(ax, x, y, w, h, color, edge='#d2dfe5'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.08',facecolor=color,edgecolor=edge,linewidth=1.2))
    def arrow(ax, start, end, color='#7a8b94', **kwargs):
        ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color=color,lw=1.7,**kwargs))
    def save(fig, stem):
        for ext in ('svg','png'):
            data=io.BytesIO();fig.savefig(data,format=ext,dpi=180,bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {'Software':'CodeCue conceptual illustrations'})
            publish(ROOT/f'reports/binding/figures/{stem}.{ext}',data.getvalue())
        plt.close(fig)
    steps=trace()
    fig,ax=plt.subplots(figsize=(13.4,6.0));ax.set_xlim(0,13.2);ax.set_ylim(0,6.0);ax.axis('off')
    ax.text(.1,5.68,'One name, different values over time',fontsize=21,fontweight='bold',color=navy)
    ax.text(.1,5.22,'A binding says which value belongs to a variable at a particular assignment.',fontsize=12,color='#526672')
    names=['Create x','Copy its value','Overwrite x','Use current bindings']
    for i,(line,title) in enumerate(zip(PROGRAM,names)):
        x=.12+i*3.3;box(ax,x,1.7,3.02,3.05,'#f5f8fa')
        ax.text(x+.18,4.34,f'{i+1}  {title}',fontsize=12,fontweight='bold',color=navy)
        ax.text(x+.18,3.8,line,fontfamily='DejaVu Sans Mono',fontsize=17,fontweight='bold',color=orange if i==2 else blue)
        state=steps[i+1]['state']
        for j,name in enumerate(('x','y','z')):
            value=str(state[name]) if name in state else 'not defined yet'
            ax.text(x+.2,3.05-j*.43,f'{name}  =  {value}',fontsize=12,color=orange if name=='x' and i>=2 else green if name=='y' and i>=1 else navy)
        if i<3:arrow(ax,(x+3.05,3.35),(x+3.26,3.35))
    box(ax,.13,.37,6.25,.96,'#e8f3ee');ax.text(.34,.99,'y stays 2 when x changes to 7.',fontsize=13,fontweight='bold',color=green)
    ax.text(.34,.61,'For integers, y = x copies the value; it is not a live link to x.',fontsize=10.5,color='#526672')
    box(ax,6.72,.37,6.25,.96,'#fff2e6');ax.text(6.94,.99,'Current x = 7    Previous x = 2    Output z = 5',fontsize=12,fontweight='bold',color=navy)
    ax.text(6.94,.61,'Using the old x would give 0. Swapping x and y would give −5.',fontsize=10.5,color='#526672')
    ax.text(.1,.03,'Illustration of exact Python semantics — this is not a claim about how a language model stores or computes the values.',fontsize=9,color='#677a85')
    save(fig,'concept_binding_timeline_v1')

    fig,ax=plt.subplots(figsize=(13.4,6.3));ax.set_xlim(0,13.2);ax.set_ylim(0,6.3);ax.axis('off')
    ax.text(.1,6.0,'Three different questions about the same program',fontsize=20,fontweight='bold',color=navy)
    ax.text(.1,5.55,'x = 2     y = x     x = 7     z = x - y',fontfamily='DejaVu Sans Mono',fontsize=14,color='#526672')
    for x in (.12,4.53,8.94):box(ax,x,.65,4.08,4.48,'#f5f8fa')
    ax.text(.34,4.66,'1  Binding / ownership',fontsize=13,fontweight='bold',color=navy)
    ax.text(.34,4.15,'Which value belongs to which name?',fontsize=10.5,color='#526672')
    for y,label,color in [(3.22,'x  →  7',orange),(2.46,'y  →  2',green),(1.7,'z  →  5',purple)]:
        box(ax,.58,y-.22,3.1,.58,'white');ax.text(2.13,y,label,ha='center',va='center',fontsize=19,fontweight='bold',color=color)
    ax.text(.34,.97,'Knowing the values {2, 7} alone\ndoes not tell us who owns each one.',fontsize=10,color='#526672')
    ax.text(4.75,4.66,'2  Data dependencies',fontsize=13,fontweight='bold',color=navy)
    ax.text(4.75,4.15,'Which assignment supplied a value?',fontsize=10.5,color='#526672')
    nodes=[(4.93,3.05,'x@1 = 2',green),(6.7,3.05,'y@1 = 2',green),(4.93,1.85,'x@2 = 7',orange),(6.7,1.85,'z@1 = 5',purple)]
    for x,y,label,color in nodes:
        box(ax,x,y,1.58,.63,'white');ax.text(x+.79,y+.31,label,ha='center',va='center',fontsize=11,fontweight='bold',color=color)
    arrow(ax,(6.53,3.36),(6.68,3.36),green)
    arrow(ax,(6.53,2.16),(6.68,2.16),orange)
    arrow(ax,(7.49,3.02),(7.49,2.52),green)
    ax.text(4.75,.97,'@1 and @2 name different assignments.\ny keeps the value from x’s first assignment.',fontsize=10,color='#526672')
    ax.text(9.16,4.66,'3  Algebraic relations',fontsize=13,fontweight='bold',color=navy)
    ax.text(9.16,4.15,'How do the current numbers relate?',fontsize=10.5,color='#526672')
    for y,label in [(3.3,'x > y'),(2.5,'z = x − y'),(1.7,'x = y + z')]:ax.text(10.98,y,label,ha='center',va='center',fontsize=21,color=blue)
    ax.text(9.16,.97,'A true numerical relation does not\nidentify the assignment it came from.',fontsize=10,color='#526672')
    ax.text(.1,.15,'Conceptual examples, not measured model results. Arrow direction is from the assignment supplying a value to the assignment consuming it.',fontsize=9,color='#677a85')
    save(fig,'concept_relationship_types_v1')

    fig,ax=plt.subplots(figsize=(13.4,6.4));ax.set_xlim(0,13.2);ax.set_ylim(0,6.4);ax.axis('off')
    ax.text(.1,6.07,'What would count as understanding a binding?',fontsize=20,fontweight='bold',color=navy)
    ax.text(.1,5.6,'Recovering a value, changing its use, and predicting new failures are different tests.',fontsize=12,color='#526672')
    cards=[(.12,'1  Read it out','Can a probe recover\na value or relationship?','Hidden activations\n↓\nSmall decoder\n↓\nPredicted value','Measured; findings depend\non the decoder and task.',green,'#e8f3ee'),
           (4.53,'2  Change its use','Does a selective change cause\nthe predicted answer change?','Controlled donor change\n↓\nModel computation\n↓\nPredicted selective effect','Assays run; a general selective\nbinding mechanism is unresolved.',orange,'#fff2e6'),
           (8.94,'3  Predict new failures','Does the account help on\nuntouched unfamiliar programs?','Freeze explanation + forecast\n↓\nNew program structures\n↓\nCompare with strong baselines','Discovery predictors run; final\nunfamiliar-program test not reached.',purple,'#f0ebf7')]
    for x,title,question,flow,status,color,bg in cards:
        box(ax,x,.9,4.08,4.2,'#f5f8fa');ax.text(x+.2,4.66,title,fontsize=14,fontweight='bold',color=navy)
        ax.text(x+.2,4.0,question,fontsize=10.5,color='#526672',linespacing=1.45)
        ax.text(x+2.04,2.7,flow,ha='center',va='center',fontsize=11.5,color=navy,linespacing=1.55)
        box(ax,x+.15,1.05,3.78,.74,bg);ax.text(x+.3,1.42,status,va='center',fontsize=9.5,color=color,linespacing=1.4)
    ax.text(.2,.4,'High probe accuracy alone does not establish selective causal use or generalization.',fontsize=13,fontweight='bold',color=navy)
    ax.text(.2,.06,'Study logic and current qualifications, not a diagram of a known neural mechanism. Source-based shortcuts and matched negative controls matter at every stage.',fontsize=9,color='#677a85')
    save(fig,'concept_evidence_ladder_v1')
    return dict(program=list(PROGRAM),steps=steps,illustrations_not_experiments=True)


def stepper_html():
    steps=json.dumps(trace(),separators=(',',':'))
    code=''.join(f'<div class="binding-line" data-line="{i}">{line}</div>' for i,line in enumerate(PROGRAM,1))
    return '''<section id="binding-stepper" class="binding-stepper" aria-labelledby="binding-stepper-title">
<h3 id="binding-stepper-title">Try it: step through the assignments</h3>
<p>These are exact Python values, not a simulation of a model’s hidden state. Move one assignment at a time and watch what changes.</p>
<div class="binding-columns"><pre aria-label="Example program">'''+code+'''</pre>
<div><div class="binding-values"><span>x <strong id="binding-x">—</strong></span><span>y <strong id="binding-y">—</strong></span><span>z <strong id="binding-z">—</strong></span></div>
<p id="binding-history"></p><p id="binding-explanation" aria-live="polite"></p></div></div>
<div class="binding-controls"><button type="button" id="binding-prev">← Previous</button><label>Step <input id="binding-range" aria-label="Assignment step" type="range" min="0" max="4" value="0"></label><button type="button" id="binding-next">Next →</button><button type="button" id="binding-reset">Reset</button><span id="binding-count"></span></div>
<p class="binding-note">After the overwrite: current x = 7, previous x = 2, and the copied y is still 2. Using current x gives z = 5.</p>
</section>
<script id="binding-stepper-script">
(function(){'use strict';
const steps='''+steps+''';let position=0;
const byId=id=>document.getElementById(id);
const explanation=['No assignments have run. A dash means the variable has not been defined.','x now owns the value 2.','y receives the current value of x: 2.','x changes to 7. The copy in y stays 2.','z uses current x and y: 7 − 2 = 5.'];
function render(value){position=Math.max(0,Math.min(4,Number(value)));const step=steps[position];
for(const name of ['x','y','z'])byId('binding-'+name).textContent=Object.prototype.hasOwnProperty.call(step.state,name)?String(step.state[name]):'—';
byId('binding-history').textContent=Object.prototype.hasOwnProperty.call(step.previous,'x')?'Previous x (before its last assignment): '+step.previous.x:'x has not been overwritten yet.';
byId('binding-explanation').textContent=explanation[position];byId('binding-count').textContent=position+' / 4';byId('binding-range').value=String(position);
byId('binding-prev').disabled=position===0;byId('binding-next').disabled=position===4;
document.querySelectorAll('.binding-line').forEach(line=>{line.classList.toggle('binding-active',Number(line.dataset.line)===position);line.classList.toggle('binding-done',Number(line.dataset.line)<position);});}
byId('binding-next').addEventListener('click',()=>render(position+1));byId('binding-prev').addEventListener('click',()=>render(position-1));
byId('binding-reset').addEventListener('click',()=>render(0));byId('binding-range').addEventListener('input',event=>render(event.target.value));render(0);
})();
</script>'''


CSS = '''.binding-stepper{background:#eef5f7;padding:20px;border:1px solid #cddfe6;border-radius:10px;margin:24px 0}.binding-columns{display:grid;grid-template-columns:minmax(180px,1fr) 1.3fr;gap:24px}.binding-stepper pre{margin:0;background:#fff;line-height:2}.binding-line{padding:2px 10px;border-left:4px solid transparent}.binding-active{background:#fff0da;border-color:#d47d34;font-weight:bold}.binding-done{color:#587b72}.binding-values{display:flex;gap:14px}.binding-values span{display:flex;align-items:center;gap:15px;background:white;border:1px solid #d5e3e8;border-radius:7px;padding:12px 18px;font-family:monospace}.binding-values strong{font-size:1.6em}.binding-controls{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:18px}.binding-controls label{display:flex;align-items:center;gap:8px}.binding-controls button{background:#205c78;color:#fff;border:0;padding:9px 14px;border-radius:5px;cursor:pointer;font-size:14px}.binding-controls button:disabled{opacity:.35;cursor:default}.binding-controls button:focus-visible,.binding-controls input:focus-visible{outline:3px solid #d47d34;outline-offset:3px}.binding-note{font-size:.88em;color:#526672}@media(max-width:650px){.binding-columns{grid-template-columns:1fr}.binding-values span{padding:8px 12px}}@media print{.binding-controls{display:none}}'''
