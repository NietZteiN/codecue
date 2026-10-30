#!/usr/bin/env python3
"""Add the conceptual master figure while preserving published result editions."""
import base64
import csv
import hashlib
import html as html_lib
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORTS=ROOT/'reports/binding'
STEM='variable_binding_master_v1'
CAPTION=('The proposed readout suite asks whether a checkpoint supports a structured view of all current bindings, '
         'previous assignment versions, directed dependencies and algebraic relationships. '
         'Displayed values and edges are Python ground truth, not observed probe predictions.')


def pin(path):
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def publish(path,data):
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Published edition differs; use a new version: '+str(path))
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)


def science(text):
    return text[text.index('## 1. Where we stand'):text.index('## 16. Reading guide')]


def main():
    parent=json.loads((ROOT/'artifacts/binding/master_report/20261029_v3/publication_review_v1.json').read_text())
    sources=[REPORTS/'master_research_report_v3.md',REPORTS/'master_research_report_v3.html',REPORTS/'master_figure_archive_20261029_v3.csv']
    for path in sources:
        assert pin(path) in parent['outputs']
    figure=REPORTS/f'figures/{STEM}.png';oracle_path=REPORTS/f'figures/{STEM}.json';oracle=json.loads(oracle_path.read_text())['oracle']
    assert oracle['conceptual_targets_not_model_predictions'] and oracle['python_output']=='7'
    md=sources[0].read_text();old_html=sources[1].read_text()
    formats=f'[PNG](figures/{STEM}.png) · [Editable SVG](figures/{STEM}.svg) · [Vector PDF](figures/{STEM}.pdf)'
    hero='## The idea in one figure\n\n'+f'![Master conceptual figure: code enters a language model; one hidden-state tap feeds readouts for all variable bindings, versions, dependencies and algebraic relations.](figures/{STEM}.png)\n\n*Master figure. {CAPTION}*\n\n'+formats+'\n\n'
    assert md.count('## Start here: the idea in pictures')==1
    new_md=md.replace('## Start here: the idea in pictures',hero+'## Start here: the idea in pictures',1)
    new_md=new_md.replace('master_research_report_v3.html','master_research_report_v4.html').replace('master_figure_archive_20261029_v3.csv','master_figure_archive_20261029_v4.csv')
    needle='### Additional figures from completed and historical studies'
    before,after=new_md.split(needle,1)
    before=before.rstrip()+f'\n| [figures/{STEM}.png](figures/{STEM}.png) | Master conceptual framework; oracle target values, not experimental predictions. |\n\n'
    new_md=before+needle+after
    assert science(new_md)==science(md)
    encoded=base64.b64encode(figure.read_bytes()).decode()
    fragment=('<section id="master-concept-figure"><h2 id="the-idea-in-one-figure">The idea in one figure</h2>'
        '<img alt="Program to language model to structured readout targets: all current variables, old and current versions, dependency graph and algebraic relationships." '
        'src="data:image/png;base64,'+encoded+'"><p><em>Master figure. '+html_lib.escape(CAPTION)+'</em></p><p>'
        f'<a href="figures/{STEM}.png">PNG</a> · <a href="figures/{STEM}.svg">Editable SVG</a> · <a href="figures/{STEM}.pdf">Vector PDF</a></p></section>')
    marker='<h2 id="start-here-the-idea-in-pictures">'
    assert old_html.count(marker)==1
    new_html=old_html.replace(marker,fragment+marker,1).replace('master_research_report_v3.html','master_research_report_v4.html').replace('master_figure_archive_20261029_v3.csv','master_figure_archive_20261029_v4.csv')
    nav='<nav aria-label="Contents">';assert new_html.count(nav)==1
    new_html=new_html.replace(nav,nav+'<p><a href="#master-concept-figure"><strong>The idea in one figure</strong></a></p>',1)
    index_marker='<h3 id="additional-figures-from-completed-and-historical-studies">'
    # Keep the original table and its historical figures; link the added master above it.
    new_html=new_html.replace(index_marker,f'<p>New conceptual master figure: <a href="figures/{STEM}.png">PNG</a> / <a href="figures/{STEM}.svg">SVG</a> / <a href="figures/{STEM}.pdf">PDF</a>.</p>'+index_marker,1)
    with sources[2].open() as stream:reader=csv.DictReader(stream);fields=reader.fieldnames;rows=list(reader)
    png_pin=pin(figure);rows.append(dict(figure=f'figures/{STEM}.png',context='Master conceptual framework; oracle target values, not experimental predictions.',**png_pin))
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    outputs=[REPORTS/'master_research_report_v4.md',REPORTS/'master_research_report_v4.html',REPORTS/'master_figure_archive_20261029_v4.csv']
    for path,data in zip(outputs,[new_md.encode(),new_html.encode(),stream.getvalue().encode()]):publish(path,data)
    review=dict(status='complete_audited',purpose='Add one master conceptual figure inspired by the user-supplied composition.',scientific_narrative_unchanged=True,
        new_model_queries=0,new_fits=0,prior_edition='v3',new_edition='v4',main_figures=19,all_png_figures=41,
        oracle=oracle,inputs=[pin(path) for path in sources]+[pin(oracle_path)],
        figure_formats=[pin(REPORTS/f'figures/{STEM}.{suffix}') for suffix in ['png','svg','pdf']],
        builder=pin(Path(__file__).resolve()),figure_builder=pin(ROOT/'scripts/build_binding_master_figure.py'),outputs=[pin(path) for path in outputs])
    publish(ROOT/'reproducibility/figure_updates/master_concept_publication_v1.json',(json.dumps(review,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(dict(status='complete_audited',main_figures=19,all_figures=41,scientific_results_changed=False),sort_keys=True))


if __name__=='__main__':main()
