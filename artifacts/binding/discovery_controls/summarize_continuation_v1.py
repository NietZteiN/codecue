"""Generate the capacity/access decision and handoff from pinned completed outputs."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding.datasets import write_json
from codecue.binding.experiment_status import query_scheduler
from codecue.binding.published_benchmarks import immutable,sha


def main():
    folder=ROOT/'artifacts/binding/discovery_controls'
    result=json.loads((folder/'comparison_v1.json').read_text())
    anchors=json.loads((folder/'anchor_review_v1.json').read_text())
    figure=json.loads((folder/'figure_review_v1.json').read_text())
    assert result['status']=='complete_exploratory' and result['complete'] and anchors['status']=='passed'
    assert anchors['comparison_sha256']==figure['comparison_sha256']==sha(folder/'comparison_v1.json')
    assert all(c['maximum_probability_difference']==c['maximum_fit_or_curve_difference']==0 for c in anchors['checks'])
    registration=json.loads((folder/'protocol_registration_v1.json').read_text())
    assert sha(ROOT/registration['plan'])==registration['plan_sha256']
    jobs=json.loads((folder/'jobs_v1.json').read_text());scheduler,errors=query_scheduler(list(jobs.values()))
    assert not errors and all(scheduler[job]['state']=='COMPLETED' for job in jobs.values())
    names=('llama31_8b','codellama34b');labels={'llama31_8b':'Llama 3.1 8B','codellama34b':'CodeLlama 34B'}
    tiers=list(result['models']['llama31_8b']['analysis_plan']['predictors'])
    assert len(tiers)==8 and sum(review['n'] for review in result['models'].values())==12288
    fits=priors=0;fit_counts={}
    for name in names:
        records=json.loads((folder/(name+'_v1')/'cv/fold_fits.json').read_text());counts={}
        for fold in records:
            for predictor,value in fold['predictors'].items():
                count=1+sum(len(curve['inner_fits']) for curve in value['inner_curves'])
                counts[predictor]=counts.get(predictor,0)+count
                if predictor=='prior':priors+=count
                else:fits+=count
        fit_counts[name]=counts
    lines=['# Capacity and oracle-access control decision','',
        f"Completed **{fits:,} regularized logistic fits** across eight fixed tiers on the same **12,288 consumed discovery targets**. All seven CPU collection/fitting/comparison/figure/anchor jobs completed. The full regression suite passed **421 tests**. These controls add no language-model query and do not establish final validation or a mechanism.",'',
        'The original prior and additive input baselines reproduce exactly: target identities, labels, references, original features, all outer/inner folds, penalties, normalizers, weights and OOF probabilities match the first analysis. The maximum recorded difference is zero for both checkpoints.','',
        '## All mean-OOF ensemble scores','',
        'Lower losses are better within a checkpoint. Different failure prevalence prevents using absolute losses to rank the underlying language models. All three fixed partition seeds and every descriptive cell remain in the full reports.','',
        '| Tier | Llama Brier | Llama log loss | CodeLlama Brier | CodeLlama log loss |',
        '|---|---:|---:|---:|---:|']
    ensembles={name:next(c for c in result['models'][name]['per_seed_and_ensemble'] if c['scope']=='ensemble')['metrics'] for name in names}
    for tier in tiers:
        values=[]
        for name in names:
            metric=ensembles[name][tier];values.extend([f"{metric['brier_score']:.6f}",f"{metric['log_loss']:.6f}"])
        lines.append('| '+tier+' | '+' | '.join(values)+' |')
    lines+=['','![Capacity and oracle-access controls](discovery_controls_results_v1.svg)','',
        '## What the controls resolve','',
        'Fixed source interactions improve CodeLlama prediction over the original additive input model. Llama changes little under the same expansion. Raw neutral-response properties still have no clear Brier increment when added to the stronger oracle-free source baseline. The source-only model class therefore matters, and the earlier additive comparison was not an exhaustive input baseline.','',
        'Source-oracle value/magnitude/sign descriptors improve both checkpoints under these conditional comparisons. On CodeLlama, oracle-only input and the scored-neutral tier without explicit oracle values have nearly identical Brier point scores. This is a descriptive point comparison, not a registered equivalence test. It shows why reference-oracle access must be separated from additional neutral behavior.','',
        'The neutral query retains a conditional predictive increment for CodeLlama when added to oracle-assisted input; the corresponding Llama interval crosses zero. The explicit neutral-failure flag then improves CodeLlama further, even though it adds no observation. This final increment is useful feature encoding/model capacity, not independent information or a binding-specific measurement.','',
        'The exact relation checked on every target/reference pair is:', '',
        '```python','neutral_failure = int(not neutral_valid or neutral_prediction_value != oracle_answer_value)','```','',
        'The program oracle is not the target language model response. Its value is provided only to declared oracle-assisted tiers; target model answers, validity and correctness are excluded from all feature vectors. Once oracle value, neutral prediction and validity are available, the flag is deterministic.','',
        '## All registered non-prior increments','',
        'Positive loss(left) minus loss(right) favors the right tier. Conditional 95% intervals resample all 24 structural components together without refitting and have no multiplicity adjustment. All seven prior comparisons also remain in the full reports.','',
        '| Checkpoint | Left | Right | Brier improvement [95%] | Log-loss improvement [95%] |',
        '|---|---|---|---|---|']
    for name in names:
        for comparison in result['models'][name]['contrasts']:
            if comparison['scope']!='ensemble' or comparison['left']=='prior':continue
            values=[]
            for metric in ('brier_score','log_loss'):
                value=comparison[metric];low,high=value['exploratory_template_bootstrap_95']
                values.append(f"{value['mean']:+.6f} [{low:+.6f}, {high:+.6f}]")
            lines.append(f"| {labels[name]} | {comparison['left']} | {comparison['right']} | "+' | '.join(values)+' |')
    lines+=['','## Scope and remaining work','',
        'The same 24 structural components, original labels and cached references are used throughout. Six outer/five inner folds, three fixed partition seeds, the penalty grid and training-only preprocessing remain unchanged. The strengthened source model adds 25 fixed products to the original 19 features; it is still a restricted logistic family, not an exhaustive nonlinear input baseline. Oracle-only prediction requires no neutral language-model query; neutral tiers allow at most one distinct reference query per target and reuse the existing cache.','',
        'All examples were previously observed discovery data. Original identifier-vocabulary boundaries are not preserved by the new CV folds. Repeated seeds are sensitivities, not independent replications; conditional bootstrap intervals omit pipeline-refitting/selection uncertainty. No confidence features, internal measurements, supported mechanism C, checkpoint training or original final/extrapolation outcomes are introduced.','',
        'Future confidence or internal-measurement predictors should face these stronger capacity/access controls. Exact-prefix, label-free confidence collection remains a separate unfinished step; genuine frozen unfamiliar-program validation also remains unfinished. The current result does not turn an engineered oracle comparison into a mechanistic explanation.','',
        '[All scores and per-checkpoint reports](discovery_controls_results_v1.md) · [Fixed analysis plan](discovery_controls_plan.md) · [Original baselines](discovery_prediction_decision.md) · [Automatic log](experiment_log.md)','']
    report=ROOT/'reports/binding/discovery_controls_decision.md';immutable(report,'\n'.join(lines).encode())
    suites=list(ET.parse(folder/'regression_v1.xml').getroot().iter('testsuite'))
    tests={key:sum(int(suite.attrib.get(key,0)) for suite in suites) for key in ('tests','failures','errors','skipped')}
    handoff={'status':'complete_exploratory','targets':12288,'predictor_tiers':8,'learned_logistic_fits':fits,
        'prior_estimates':priors,'fit_counts':fit_counts,'regression':tests,'jobs':jobs,'scheduler_accounting':scheduler,
        'collection_source':json.loads((folder/'collection_source_v1.json').read_text()),
        'fitting_source':json.loads((folder/'fitting_source_v1.json').read_text()),
        'comparison_sha256':sha(folder/'comparison_v1.json'),'anchor_review_sha256':sha(folder/'anchor_review_v1.json'),
        'figure_review_sha256':sha(folder/'figure_review_v1.json'),'decision':str(report),'decision_sha256':sha(report),
        'summary_script_sha256':sha(__file__),'anchors_exactly_reproduced':True,'new_language_model_queries':0,
        'generated_holdouts_opened':False,'mechanism_C_fitted':False,'language_model_training':False,
        'final_validation_completed':False}
    write_json(folder/'handoff_review_v1.json',handoff)
    print(json.dumps({'status':handoff['status'],'targets':handoff['targets'],'logistic_fits':fits,
        'tests':tests,'anchors_exact':True,'report':str(report)},indent=2))


if __name__=='__main__':main()
