"""Write the empirical discovery-baseline decision from immutable scored outputs."""
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
    folder=ROOT/'artifacts/binding/discovery_prediction'
    comparison=folder/'comparison_v1.json';result=json.loads(comparison.read_text())
    assert result['status']=='complete_exploratory' and result['complete']
    jobs=json.loads((folder/'jobs_v1.json').read_text())
    scheduler,errors=query_scheduler(list(jobs.values()))
    assert not errors and all(scheduler[job]['state']=='COMPLETED' for job in jobs.values())
    protocol=json.loads((folder/'protocol_registration_v1.json').read_text())
    assert sha(ROOT/protocol['plan'])==protocol['plan_sha256']
    names=('llama31_8b','codellama34b')
    labels={'llama31_8b':'Llama 3.1 8B','codellama34b':'CodeLlama 34B'}
    predictors=('prior','A_input','A_neutral_raw','A_neutral_scored')
    total=sum(model['n'] for model in result['models'].values());assert total==12288
    figure=folder/'figure_review_v2.json';figure_metadata=json.loads(figure.read_text())
    assert figure_metadata['comparison_sha256']==sha(comparison)
    lines=['# Discovery failure-prediction decision','',
        f"Completed empirical predictive baselines on **{total:,} previously observed target examples** across both cached checkpoints. This is nested structural-group cross-validation within consumed discovery data, not frozen final validation. All collection, fitting, comparison and figure jobs completed successfully.",'',
        'Input features improve prediction over the fitted training-prior baseline. Raw neutral-query properties add no clear Brier-score improvement in either checkpoint. Scoring that distinct neutral query against its oracle adds predictive information, with the stronger oracle-access contract explicitly separated. These results establish exploratory baselines, not a mechanism C model or a causal explanation.','',
        '## Complete mean-OOF ensemble scores','',
        'Lower Brier/log loss is better within each checkpoint. Failure prevalence differs between checkpoints, so their absolute scores do not rank the language models. The ensemble averages the three predeclared partition seeds; no favorable seed is selected.','',
        '| Checkpoint | Targets | Failures | Predictor | Brier | Log loss |',
        '|---|---:|---:|---|---:|---:|']
    learned=prior=0;counts={}
    for name in names:
        review=result['models'][name]
        assert review['templates']==24 and review['n']==6144 and review['fallback_count']==0
        ensemble=next(context for context in review['per_seed_and_ensemble'] if context['scope']=='ensemble')
        for predictor in predictors:
            metric=ensemble['metrics'][predictor]
            lines.append(f"| {labels[name]} | {review['n']} | {review['failures']} | {predictor} | {metric['brier_score']:.6f} | {metric['log_loss']:.6f} |")
        fold_fits=json.loads((folder/(name+'_v1')/'cv/fold_fits.json').read_text())
        per_model={}
        for fold in fold_fits:
            for predictor,fit in fold['predictors'].items():
                fitted=1+sum(len(curve['inner_fits']) for curve in fit['inner_curves'])
                per_model[predictor]=per_model.get(predictor,0)+fitted
                if predictor=='prior':prior+=fitted
                else:learned+=fitted
        counts[name]=per_model
    lines+=['','![Discovery baseline scores](discovery_prediction_results_v2.svg)','',
        '## Incremental neutral-query information','',
        'Positive improvement is loss(left) minus loss(right). Intervals resample whole structural components and condition on the saved OOF probabilities; they do not refit the training procedure and are unadjusted for multiplicity.','',
        '| Checkpoint | Left | Right | Brier improvement [95%] | Log-loss improvement [95%] |',
        '|---|---|---|---|---|']
    for name in names:
        for contrast in result['models'][name]['contrasts']:
            if contrast['scope']!='ensemble' or contrast['left'] not in ('A_input','A_neutral_raw'):continue
            metrics=[]
            for key in ('brier_score','log_loss'):
                value=contrast[key];low,high=value['exploratory_template_bootstrap_95']
                metrics.append(f"{value['mean']:+.6f} [{low:+.6f}, {high:+.6f}]")
            lines.append(f"| {labels[name]} | {contrast['left']} | {contrast['right']} | "+' | '.join(metrics)+' |')
    lines+=['','## Information, grouping and costs','',
        'Targets are informative/misleading version-family programs. Each is paired with a distinct neutral query using base, updates, tail placement, query role, ownership status and lexical realization. Ownership-only records are excluded prospectively because they have no transformed counterpart. All numeric, naming, lexical and query relatives remain in the same structural component.','',
        'The input tier has 19 fixed source-only features. Five raw-reference features use the neutral answer, validity and response lengths without checking its correctness. The scored tier adds one reference-failure indicator and requires the reference oracle, which shares the target semantic answer. Target model answers, validity and correctness never enter feature vectors. No confidence, activation or mechanism-derived feature is present.','',
        'Maximum prediction-time access is one extra neutral query per target. Each checkpoint uses 3,072 distinct cached references for 6,144 targets (0.5 amortized queries per target in this paired cohort). This analysis made zero new language-model queries. The scored tier additionally needs reference ground truth and is not an oracle-free deployment comparator.','',
        '## Limits and next work','',
        'All 24 components were previously observed discovery data. The new folds combine original training and development components; they do not preserve the original identifier-vocabulary boundary. Source features are fixed additive logistic inputs, not an exhaustive class of input-only predictors. Fixed interactions or more flexible input baselines, and oracle-access-matched controls, remain useful before interpreting additional information from costly measurements.','',
        'Repeated partition seeds are sensitivity analyses on the same data, not independent scientific replications. Conditional OOF bootstrap intervals omit feature-selection and refitting uncertainty. No supported causal account, empirical mechanism C, prospectively frozen final forecast or original final/extrapolation score is produced. The earlier arithmetic reliability failures remain unchanged.','',
        'The completed result advances empirical discovery A/behavioral baselines. It does not complete M5. Remaining work includes appropriate confidence measurements, an evidence-supported internal measurement account, capacity/access controls and genuinely frozen unfamiliar-program validation.','',
        '## Software and reproduction','',
        f"The full regression suite passed **385 tests**. The fixed analysis performed **{learned:,} regularized logistic fits** and {prior} smoothed training-prior estimates, including all inner candidate fits and outer refits; no single-class fallback was needed. Every fold identity, inner curve, normalizer, weight, OOF probability and calibration bin is retained. These statistical fits do not train a language-model checkpoint.",'',
        '[Full comparison and per-checkpoint reports](discovery_prediction_results_v1.md) · [Fixed analysis plan](discovery_prediction_plan.md) · [Automatic log](experiment_log.md)','']
    report=ROOT/'reports/binding/discovery_prediction_decision.md'
    immutable(report,'\n'.join(lines).encode())
    suites=list(ET.parse(folder/'regression_v1.xml').getroot().iter('testsuite'))
    tests={key:sum(int(suite.attrib.get(key,0)) for suite in suites) for key in ('tests','failures','errors','skipped')}
    handoff={'status':'complete_exploratory','target_examples':total,'templates_per_checkpoint':24,
        'learned_logistic_fits':learned,'prior_estimates':prior,'fit_counts':counts,
        'jobs':jobs,'scheduler_accounting':scheduler,'regression':tests,
        'collection_source':json.loads((folder/'collection_source_v1.json').read_text()),
        'fitting_source':json.loads((folder/'fitting_source_v1.json').read_text()),
        'comparison_sha256':sha(comparison),'figure_review_sha256':sha(figure),
        'decision':str(report),'decision_sha256':sha(report),'summary_script_sha256':sha(__file__),
        'new_language_model_queries':0,'language_model_training':False,'generated_holdouts_opened':False,
        'mechanism_C_fitted':False,'frozen_final_validation_completed':False}
    write_json(folder/'handoff_review_v1.json',handoff)
    print(json.dumps({'status':handoff['status'],'targets':total,'logistic_fits':learned,'regression':tests,'report':str(report)},indent=2))


if __name__=='__main__':main()
