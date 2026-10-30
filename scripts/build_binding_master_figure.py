#!/usr/bin/env python3
"""Draw the structured-state research idea as editable SVG, PNG and PDF.

All displayed values and graph edges are independently checked program truth.
They are illustrative decoding targets, never reported model predictions.
"""
from __future__ import annotations
import argparse
import ast
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path

PROGRAM = 'a = 2\nb = 7\nsaved = a\na = b - a\nout = a + saved\nprint(out)\n'
ROOT = Path(__file__).resolve().parents[1]
STEM = 'variable_binding_master_v1'


def oracle():
    values, versions, definitions, history, edges = {}, {}, {}, [], []
    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:return node.value
        if isinstance(node, ast.Name):return values[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            left,right=evaluate(node.left),evaluate(node.right)
            return left+right if isinstance(node.op,ast.Add) else left-right
        raise ValueError('Unsupported illustrative expression')
    for statement in ast.parse(PROGRAM).body:
        if not isinstance(statement,ast.Assign):continue
        name=statement.targets[0].id
        parents=[definitions[n.id] for n in ast.walk(statement.value) if isinstance(n,ast.Name)]
        value=evaluate(statement.value)
        versions[name]=versions.get(name,0)+1
        definition=f'{name}@{versions[name]}'
        edges.extend((parent,definition) for parent in parents)
        values[name]=value;definitions[name]=definition
        history.append(dict(variable=name,version=versions[name],definition=definition,value=value))
    python_values={};output=io.StringIO()
    with redirect_stdout(output):exec(PROGRAM,{'__builtins__':{'print':print}},python_values)
    assert values==python_values==dict(a=5,b=7,saved=2,out=7)
    assert output.getvalue()=='7\n'
    assert set(edges)=={('a@1','saved@1'),('a@1','a@2'),('b@1','a@2'),('a@2','out@1'),('saved@1','out@1')}
    assert len(edges)==5
    assert values['a']<values['b'] and values['out']==values['a']+values['saved'] and values['b']==values['out']
    return dict(program=PROGRAM,current_values=values,current_versions=versions,current_definitions=definitions,
                assignment_history=history,direct_dependencies=[list(edge) for edge in sorted(edges)],
                previous_values={'a':history[0]['value']},python_output=output.getvalue().strip(),
                algebraic_relations=['a < b','out = a + saved','b = out'],
                conceptual_targets_not_model_predictions=True)


def render(output_dir,replace=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Circle
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'binding-structured-state-master-v1'})
    data=oracle();navy='#17233b';slate='#63718a';blue='#4478bf';light_blue='#edf3ff';teal='#438f87';orange='#ce802d';purple='#8460bf'
    fig=plt.figure(figsize=(19.2,11.2),facecolor='white');ax=fig.add_axes([.015,.02,.97,.96]);ax.set_xlim(0,24);ax.set_ylim(0,14.5);ax.axis('off')
    def box(x,y,w,h,fill,edge='#dce3ed',lw=1.4,radius=.18):
        patch=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={radius}',facecolor=fill,edgecolor=edge,linewidth=lw)
        ax.add_patch(patch);return patch
    def text(x,y,label,size=13,color=navy,weight='normal',**kwargs):
        return ax.text(x,y,label,fontsize=size,color=color,fontweight=weight,va='center',**kwargs)
    def arrow(start,end,color=slate,lw=2.0):
        ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color=color,lw=lw,mutation_scale=18))
    def route(points,color=slate,lw=2.0):
        ax.plot([p[0] for p in points[:-1]],[p[1] for p in points[:-1]],color=color,lw=lw,solid_capstyle='round',solid_joinstyle='round')
        arrow(points[-2],points[-1],color,lw)
    text(.65,14.03,'CONCEPTUAL OVERVIEW',10.5,teal,'bold')
    text(.65,13.37,'The idea: decode all variables and the relationships between them',25,navy,'bold')
    text(.65,12.72,'Measure current values, assignment history, data dependencies and algebraic relations from model representations.',12.5,slate)

    text(.75,11.76,'Program with updates',17,navy,'bold')
    box(.7,4.38,5.55,6.83,'#f7f9fc')
    for index,line in enumerate(PROGRAM.strip().splitlines()):
        color=orange if index==3 else purple if line.startswith('print') else navy
        text(1.1,10.48-index*.8,line,18,color,fontfamily='DejaVu Sans Mono',weight='bold' if index==3 else 'normal')
    box(1.0,4.8,4.95,.65,'#edf4fb',edge='#e4ebf5')
    text(1.2,5.12,f"Python output: {data['python_output']}",13,blue,'bold')
    text(.95,4.01,'Four variables; five assignment events.',10.5,slate)
    text(.95,3.52,'Values alone do not identify their owners.',10.5,slate)

    text(7.55,11.76,'Language model',17,navy,'bold')
    for y in (10.3,9.37,7.43,6.5):
        box(7.5,y,4.85,.72,light_blue,edge='#d3e0fa',lw=1.5)
        ax.plot([8.15,9.9,11.65],[y+.36]*3,color='#aec9f5',lw=1.1)
        ax.scatter([8.15,9.9,11.65],[y+.36]*3,s=29,color='#79a6ed',zorder=3)
    box(7.3,8.3,5.25,.91,'#cae5fa',edge='#4d87bd',lw=2.1)
    palette=['#396d9c','#4f91c2','#69b4df','#9ad1ef','#dfedf7','#70b9e4','#508dbb','#386a95']
    for i,color in enumerate(palette):box(7.62+i*.44,8.72,.34,.28,color,edge=color,lw=.3,radius=.03)
    text(9.8,8.49,'Hidden state  hₜ',12.5,'#365d87',ha='center')
    ax.add_patch(Circle((11.98,8.88),.07,color=teal,zorder=5))
    arrow((6.48,8.78),(7.15,8.78),slate,2.4)
    text(9.9,6.28,'After the full program is visible',9.8,slate,ha='center')

    route([(12.4,10.65),(12.95,10.65),(12.95,11.7),(13.65,11.7)],slate,1.9)
    box(13.78,11.22,9.48,.94,'#fafbfe',edge='#dbe2ed')
    text(14.08,11.7,'Generated answer',13,navy,'bold')
    text(18.05,11.7,'One response, scored separately',10.5,slate)
    text(22.48,11.72,'?',25,slate,'bold',ha='center')

    box(7.65,4.68,4.7,1.06,'#eef9f6',edge='#9ad8cd',lw=1.8)
    text(10,5.36,'Probe / readout suite',14,teal,'bold',ha='center')
    text(10,4.98,'Controlled heads for structured targets',9.7,teal,ha='center')
    route([(11.98,8.88),(12.68,8.88),(12.68,6.03),(10.0,6.03),(10.0,5.78)],teal,2.2)
    arrow((12.43,5.2),(13.5,5.2),teal,2.3)
    text(12.96,5.62,'targets',9.2,teal,ha='center')

    box(13.58,3.24,9.72,7.62,'#fbfdfd',edge='#b7dcd4',lw=1.6)
    text(13.9,10.48,'Structured decoding targets',16,navy,'bold')
    text(13.9,10.02,'Illustrative oracle labels shown below',10.2,slate)
    box(13.85,7.02,4.36,2.7,'#f1faf7',edge='#d0e9e2')
    text(14.1,9.34,'All current bindings',13,teal,'bold')
    for i,name in enumerate(data['current_values']):
        y=8.84-i*.44
        text(14.15,y,data['current_definitions'][name],12.5,navy,fontfamily='DejaVu Sans Mono')
        text(17.75,y,str(data['current_values'][name]),15,teal,'bold',ha='right')
    box(18.5,7.02,4.49,2.7,'#fff7ee',edge='#f0ddc8')
    text(18.75,9.34,'Current + previous versions',12.5,orange,'bold')
    text(19.5,8.63,f"a@1 = {data['previous_values']['a']}",13,blue,'bold',ha='center',fontfamily='DejaVu Sans Mono')
    text(21.83,8.63,f"a@2 = {data['current_values']['a']}",13,orange,'bold',ha='center',fontfamily='DejaVu Sans Mono')
    arrow((20.47,8.63),(20.85,8.63),orange,1.5)
    text(19.5,8.14,'previous',10.5,slate,ha='center');text(21.83,8.14,'current',10.5,slate,ha='center')
    text(18.8,7.5,'saved keeps a@1’s value',10.5,slate)

    box(13.85,3.57,4.36,3.07,'#f3f7fd',edge='#d8e3f2')
    text(14.1,6.25,'Data dependencies',13,blue,'bold')
    centers={'a@1':(14.85,5.56),'b@1':(17.2,5.56),'saved@1':(14.85,4.78),'a@2':(17.2,4.78),'out@1':(16.05,3.99)}
    # The graph is drawn from the evaluated AST, including reads before overwrite.
    for parent,child in data['direct_dependencies']:
        start,end=centers[parent],centers[child]
        arrow((start[0],start[1]-.24),(end[0],end[1]+.24),blue,1.35)
    for name,(x,y) in centers.items():
        color=orange if name=='a@2' else purple if name=='out@1' else teal if name=='saved@1' else blue
        box(x-.78,y-.24,1.56,.48,'white',edge='#ccdae9',lw=1.0,radius=.09)
        text(x,y,name,10.3,color,'bold',ha='center',fontfamily='DejaVu Sans Mono')
    box(18.5,3.57,4.49,3.07,'#f7f3fc',edge='#e2d7ef')
    text(18.75,6.25,'Algebraic relationships',12.7,purple,'bold')
    for y,label,size in [(5.57,'a < b',19),(4.84,'out = a + saved',14),(4.1,'b = out',19)]:
        text(20.75,y,label,size,purple,ha='center',fontfamily='DejaVu Sans Mono')

    box(.7,.98,22.6,1.58,'#f5f8fb',edge='#e0e7ee')
    text(1.02,2.06,'Do the right bindings and relationships remain accessible—and does the model use them?',16,navy,'bold')
    text(1.02,1.51,'Decode broadly  →  test selective causal effects  →  predict failures on unfamiliar programs',12,slate)
    text(.75,.48,'Conceptual framework. Values and edges are program ground truth, not measured probe predictions or evidence of a complete neural state store.',9.8,slate)

    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    outputs=[]
    for ext in ('png','svg','pdf'):
        stream=io.BytesIO()
        metadata={'Software':'CodeCue structured-state conceptual figure'} if ext=='png' else {'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None,'Creator':'CodeCue conceptual figure builder'}
        fig.savefig(stream,format=ext,dpi=240,bbox_inches='tight',metadata=metadata)
        path=output_dir/f'{STEM}.{ext}';payload=stream.getvalue()
        if path.exists() and path.read_bytes()!=payload and not replace:raise ValueError('Published figure differs; use a new version or a draft directory')
        path.write_bytes(payload)
        recorded_path=str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else str(path)
        outputs.append(dict(path=recorded_path,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()))
    plt.close(fig)
    manifest=output_dir/f'{STEM}.json'
    manifest.write_text(json.dumps(dict(status='complete',oracle=data,outputs=outputs,new_model_queries=0,new_fits=0),sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='complete',outputs=outputs,oracle_output=data['python_output']),sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,default=ROOT/'reports/binding/figures');parser.add_argument('--replace',action='store_true',help='Allow replacing figures in an explicitly chosen draft directory');args=parser.parse_args();render(args.output_dir,args.replace)
