#!/usr/bin/env python
"""Paper numbers and appendix tables from validated independent follow-ups."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
LABEL={'olmo2-7b-it':'OLMo-2-7B','llama32-3b-it':'Llama-3.2-3B',
       'llama31-8b-it':'Llama-3.1-8B','codegemma-7b-it':'CodeGemma-7B'}


def load(name):
    path=ROOT/'results/summary'/f'round6_{name}.json'
    if not path.exists():return None
    data=json.loads(path.read_text())
    if not data.get('validated'):raise ValueError(f'unvalidated result: {path}')
    return data


def ci(value):
    return '--' if value is None else f'{100*value[0]:.1f} [{100*value[1]:.1f}, {100*value[2]:.1f}]'


def identifier(name):
    return r'\texttt{'+name.replace('_',r'\_')+'}'


def table(lines,columns,header,rows,caption,label):
    lines.extend([r'\begin{table*}[t]',r'\centering\small',r'\sbox{\roundsixbox}{\begin{tabular}{@{}'+columns+r'@{}}',
                  r'\toprule',header+r' \\',r'\midrule'])
    lines.extend(' & '.join(row)+r' \\' for row in rows)
    lines.extend([r'\bottomrule',r'\end{tabular}}',
                  r'\ifdim\wd\roundsixbox>\textwidth\resizebox{\textwidth}{!}{\usebox{\roundsixbox}}\else\usebox{\roundsixbox}\fi',
                  r'\caption{'+caption+'}',r'\label{'+label+'}',r'\end{table*}'])


def narrative_numbers():
    numbers={}
    probes=load('crossfit_probes')
    if probes:
        rates=[]
        for model,tag in (('olmo2-7b-it','olmo7'),('llama32-3b-it','llama3'),('llama31-8b-it','llama8')):
            value=probes['models'][model]['pooled']['lure_write']['accuracy_ci95']
            rates.append(value[0])
            for field,rate in zip(('accuracy','lo','hi'),value):numbers[f'crossfit-{tag}-{field}']=f'{100*rate:.1f}'
        numbers['crossfit-min']=f'{100*min(rates):.1f}'
        numbers['crossfit-max']=f'{100*max(rates):.1f}'
    replication=load('identifier_replication')
    if replication:
        numbers['r6-name-list']=', '.join(identifier(n) for n in replication['selected_names'])
        numbers['r6-name-n']=str(len(replication['selected_names']))
        numbers['r6-screen-n']=str(len(replication['gate']))
        numbers['r6-screen-passed']=str(sum(g['panel_pass'] for g in replication['gate'].values()))
        for model,tag in (('olmo2-7b-it','olmo7'),('llama32-3b-it','llama3'),('llama31-8b-it','llama8'),('codegemma-7b-it','codegemma7')):
            result=replication['models'][model]
            numbers['r6-program-n']=str(result['n_programs'])
            for fmt,short in (('trace','trace'),('trace_expr','expression')):
                for field,rate in zip(('mean','lo','hi'),result[fmt]['excess_ci95']):
                    numbers[f'r6-{tag}-{short}-{field}']=f'{100*rate:.1f}'
    return numbers


def main():
    lines=['% Generated from validated round-six summaries.',r'\newsavebox{\roundsixbox}']
    probes=load('crossfit_probes')
    if probes:
        lines.extend([r'\section{Independent probe layer selection}',r'\label{app:round6-probes}',
            'The main-text error readouts use five-fold cross-fitting. A fixed SHA256 hash assigns canonical program computations to folds, keeping renamed versions and demonstration repeats together. For each held-out fold, we select the layer with the highest neutral accuracy on the other four folds, averaging three probe seeds and breaking ties toward the lowest layer. Neither the held-out neutral labels nor its misleading writes enter that choice. Probe training remains disjoint from every evaluation computation.',
            'Each program is scored only with its held-out fold\'s layer. The generated-prefix audit from Appendix~\\ref{app:round5-errors} still applies. Table~\\ref{tab:round6-probes} reports the conditional write strata and paired changes from the earlier full-neutral selection. Intervals use 4,000 canonical-program bootstrap draws, keeping demonstration repeats together. They condition on the fixed fold selectors and do not refit layer selection inside each bootstrap. Name controls and the full layer curves remain descriptive measurements in Appendix~\\ref{app:probes}.'])
        rows=[]
        for model,data in probes['models'].items():
            for group,result in data['pooled'].items():
                rows.append([LABEL[model],{'lure_write':'name error','correct_write':'correct write','other_error':'other error'}[group],str(result['n']),str(result['n_programs']),
                             ci(result['accuracy_ci95']),ci(result['change_ci95'])])
        table(lines,'llrrll','Model & Write & Rows & Computations & Accuracy (\\%) & Change (points)',rows,
              'True-digit readouts with independent layer selection. Changes compare the same observed writes with the earlier full-neutral layer choice. A dash denotes an empty stratum. These readouts establish decodability, not causal use.','tab:round6-probes')
    replication=load('identifier_replication')
    if replication:
        lines.extend([r'\section{Independent replication with screened names}',r'\label{app:round6-identifiers}',
            'We fix \\NUM{r6-screen-n} fresh sum-family candidates before scoring them with the original candidate-continuation meaning check (Appendix~\\ref{app:gate}). The panel is the same seven models used for that gate. A name qualifies when sum is the highest-scoring continuation in at least 80\\% of the panel; ties follow the original scoring order. Two additional function-name contexts and neutral names are diagnostic and do not affect selection. Of the candidates, \\NUM{r6-screen-passed} qualify. We freeze the first \\NUM{r6-name-n} qualifying names in the fixed order: \\NUM{r6-name-list}. No trace outcomes enter selection.',
            'The replication uses \\NUM{r6-program-n} new length-computed programs. Their canonical computations are unique and absent from the original level-5 training and test corpus and all three demonstration sets. True and name-suggested values are checked by execution and retain the original value-exclusion rules. Every selected name is crossed with every program; its neutral twin differs only in the target identifier. The three affected models and the prespecified CodeGemma-7B control use the same programs and demonstration sets 7, 11 and 13 under trace and expression demonstrations.',
            'Table~\\ref{tab:round6-replication} pools names and demonstration sets, clustering all repeats of each computation in 4,000 bootstrap draws. Table~\\ref{tab:round6-replication-names} reports each identifier. The format contrast replicates on independently selected names, but names and programs differ from the original experiment, so differences in effect magnitude across the two samples are descriptive. This exploratory replication does not retroactively repair the original selection-rule deviation. Probes and patches concern the original identifiers, not these new names.'])
        rows=[[identifier(name),f"{gate['n_pass']}/{gate['n_models']}",
               'yes' if gate['panel_pass'] else 'no','yes' if name in replication['selected_names'] else 'no']
              for name,gate in replication['gate'].items()]
        table(lines,'lccc','Candidate & Sum agreement & Qualifies & Selected',rows,
              'The entire fixed candidate list, in selection order. Qualification uses the original canonical meaning prompt. Selection retains the first three qualifying candidates without consulting behavior.','tab:round6-screen')
        rows=[[LABEL[model],ci(result['trace']['excess_ci95']),ci(result['trace_expr']['excess_ci95']),
               ci(result['expression_minus_trace_ci95'])] for model,result in replication['models'].items()]
        table(lines,'llll','Model & Trace excess & Expression excess & Expression minus trace',rows,
              'Independent screened-name replication: excess name errors and paired format changes in percentage points [95\\% interval]. All selected identifiers and three demonstration sets are pooled over 200 fresh computations. A zero bootstrap interval records no observed paired name errors; it is not a population-level absence or equivalence claim.','tab:round6-replication')
        rows=[]
        for model,result in replication['models'].items():
            for name in replication['selected_names']:
                rows.append([LABEL[model],identifier(name),ci(result['trace']['by_name'][name]),ci(result['trace_expr']['by_name'][name])])
        table(lines,'llll','Model & Identifier & Trace excess & Expression excess',rows,
              'Per-identifier replication, pooling the same three demonstration sets. Effects are percentage points [95\\% canonical-program bootstrap interval]. All affected-model trace means are positive in every demonstration set; per-set estimates are retained in the saved summary.','tab:round6-replication-names')
    (ROOT/'paper/tables/round6_followups.tex').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
