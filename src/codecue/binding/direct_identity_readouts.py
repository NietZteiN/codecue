"""Direct global owner@version readouts on the existing diversity captures.

An isolated schedule engine fits only the two captured final sites. The new
192-column target schema predicts joint identities and their owner/version
components directly. No source-oracle conversion is applied to predictions.
"""
from __future__ import annotations

import importlib.util
import sys

import numpy as np

from . import schedule_readouts as original

ROLE='discovery_direct_identity_readouts_v1'
SITES=(7,8)
FAMILIES=('assignment_joint','assignment_owner','assignment_version',
          'parent_joint','parent_owner','parent_version')
METHODS=('direct','training_prior','random_prefix_control','source_owner_version_prior')
SOURCE_ROWS=5760
TRAIN_ROWS=4320
DEV_ROWS=1440
TRAIN_GROUPS=45
DEV_GROUPS=15
SOURCE_SNAPSHOT='345f75b01f5c3b33bd0ca6d8'
SOURCE_SHA='9cfa6c42fd79ddb9a4f049650ba311bb996dcb9f48afb9f9c31a2cc22254a918'


def _targets():
    from . import direct_identity_targets
    return direct_identity_targets


def _capture():
    from . import diversity_capture
    return diversity_capture


def _initialization(rows):
    """Check the captured initialization site without fitting a future event."""
    initial=_targets().targets(rows,3)
    if initial.y.shape!=(len(rows),192) or initial.mask.any() or np.any(initial.y!=0):
        raise ValueError('initialization site3 must have all192event targets undefined')


def _rate(correct,valid,groups):
    groups=np.asarray(groups);valid=np.asarray(valid,dtype=bool);correct=np.asarray(correct,dtype=bool)
    per_group={g:dict(n=int((valid&(groups==g)).sum()),
                      correct=int(correct[valid&(groups==g)].sum()),
                      accuracy=float(correct[valid&(groups==g)].mean()))
               for g in sorted(set(groups[valid]))}
    return dict(n=int(valid.sum()),correct=int(correct[valid].sum()),
        accuracy=float(correct[valid].mean()) if valid.any() else None,
        group_macro_accuracy=float(np.mean([g['accuracy'] for g in per_group.values()])) if per_group else None,
        per_group=per_group)


def _decision(bundle,scores,family,event):
    columns=[column for column in bundle.columns if column['family']==family
             and column.get('event_statement')==event]
    if not columns:raise ValueError('complete six-family/four-event categorical schema required')
    columns=sorted(columns,key=lambda column:column['candidate'])
    indices=[column['index'] for column in columns];candidates=np.array([column['candidate'] for column in columns])
    truth=bundle.y[:,indices];valid=(truth.sum(axis=1)==1)&bundle.mask[:,indices].any(axis=1)
    values=np.asarray(scores)[:,indices];finite=np.isfinite(values).any(axis=1)
    predicted=np.full(len(values),-1,dtype=int)
    predicted[finite]=candidates[np.argmax(np.where(np.isfinite(values),values,-np.inf),axis=1)[finite]]
    expected=np.full(len(values),-1,dtype=int)
    expected[valid]=candidates[np.argmax(truth[valid],axis=1)]
    return expected,predicted,valid


def binding_comparisons(bundle,scores):
    """Compare joint argmax with composed owner/version marginal decisions."""
    scores=np.asarray(scores)
    if scores.shape!=bundle.y.shape:raise ValueError('binding score/target geometry differs')
    groups=np.asarray(bundle.group_ids);profiles=bundle.descriptive.get('profile_ids')
    if not isinstance(profiles,(list,tuple)) or len(profiles)!=len(scores):
        raise ValueError('aligned source profile labels required for stratified diagnostics')
    profiles=np.asarray(profiles);statuses=bundle.descriptive.get('event_capture_status')
    if not isinstance(statuses,(list,tuple)) or len(statuses)!=len(scores):
        raise ValueError('aligned target capture-status strata required')
    per_event={};kind_flags={};all_joint=[];all_factorized=[];all_valid=[]
    for kind in ('assignment','parent'):
        joint_flags=[];factorized_flags=[];valid_flags=[]
        for event in range(4,8):
            truth,joint,valid=_decision(bundle,scores,kind+'_joint',event)
            owner_truth,owner,owner_valid=_decision(bundle,scores,kind+'_owner',event)
            version_truth,version,version_valid=_decision(bundle,scores,kind+'_version',event)
            if (not np.array_equal(valid,owner_valid) or not np.array_equal(valid,version_valid)
                    or not np.array_equal(truth[valid],4*owner_truth[valid]+version_truth[valid]-1)):
                raise ValueError('joint and separate component target identities disagree')
            composed=np.where((owner>=0)&(version>=1),4*owner+version-1,-1)
            joint_correct=(joint==truth)&(joint>=0)
            factorized_correct=(composed==truth)&(composed>=0)
            event_status=np.array([row[kind][event-4] for row in statuses],dtype=object)
            by_profile={p:dict(joint=_rate(joint_correct,valid&(profiles==p),groups),
                               factorized=_rate(factorized_correct,valid&(profiles==p),groups))
                        for p in sorted(set(profiles))}
            by_status={str(status):dict(joint=_rate(joint_correct,valid&(event_status==status),groups),
                                       factorized=_rate(factorized_correct,valid&(event_status==status),groups))
                       for status in sorted(set(event_status),key=str)}
            by_class={str(candidate):dict(n=int((valid&(truth==candidate)).sum()),
                joint_correct=int(joint_correct[valid&(truth==candidate)].sum()),
                factorized_correct=int(factorized_correct[valid&(truth==candidate)].sum())) for candidate in range(16)}
            values={}
            for component in ('joint','owner','version'):
                columns=sorted((column for column in bundle.columns
                    if column['family']==kind+'_'+component and column.get('event_statement')==event),
                    key=lambda column:column['candidate'])
                values[component]=scores[:,[column['index'] for column in columns]]
            complete=valid&np.logical_and.reduce([np.isfinite(value).all(axis=1) for value in values.values()])
            joint_table=values['joint'][complete].reshape(-1,4,4)
            linearity=dict(n_complete=int(complete.sum()),
                max_abs_owner_difference=float(np.max(np.abs(values['owner'][complete]-joint_table.sum(axis=2)))) if complete.any() else None,
                max_abs_version_difference=float(np.max(np.abs(values['version'][complete]-joint_table.sum(axis=1)))) if complete.any() else None)
            per_event[f'{kind}/event{event}']=dict(joint=_rate(joint_correct,valid,groups),
                factorized=_rate(factorized_correct,valid,groups),
                separate_owner=_rate((owner>=0)&(owner==owner_truth),valid,groups),
                separate_version=_rate((version>=1)&(version==version_truth),valid,groups),
                joint_owner=_rate((joint>=0)&((joint//4)==owner_truth),valid,groups),
                joint_version=_rate((joint>=0)&((joint%4+1)==version_truth),valid,groups),
                prediction_disagreement=_rate(joint!=composed,valid,groups),
                joint_classes=by_class,by_profile=by_profile,by_capture_status=by_status,
                score_marginal_linearity=linearity)
            joint_flags.append(joint_correct);factorized_flags.append(factorized_correct);valid_flags.append(valid)
        valid=np.logical_and.reduce(valid_flags)
        joint=np.logical_and.reduce(joint_flags);factorized=np.logical_and.reduce(factorized_flags)
        kind_flags[kind]=dict(joint=_rate(joint,valid,groups),factorized=_rate(factorized,valid,groups))
        all_joint.extend(joint_flags);all_factorized.extend(factorized_flags);all_valid.extend(valid_flags)
    combined_valid=np.logical_and.reduce(all_valid)
    return dict(per_event=per_event,whole_by_kind=kind_flags,
        combined_eight=dict(joint=_rate(np.logical_and.reduce(all_joint),combined_valid,groups),
                            factorized=_rate(np.logical_and.reduce(all_factorized),combined_valid,groups)),
        codebook='joint_class=4*canonical_owner+(assignment_version-1)',
        capacity=dict(direct_joint_outputs_per_event=16,separate_owner_plus_version_outputs_per_event=8,
                      total_outputs=192,whole_pipelines_parameter_matched=False,
                      linear_ridge_relation='With identical features/weights/alpha, component scores equal joint-score marginal sums up to roundoff; argmax routes are different decisions, not independent representations.'),
        capture_status_scope='Underlying real-source event status at capture; parent real-task truth uses pre-consumer read time. Sham strata describe source context, not the status of a random sham identity.')


def _summary(result):
    primary={}
    for backend in ('hidden','surface'):
        primary[backend]={}
        fits=[fit for fit in result['fits'] if fit['site']==7 and fit['backend']==backend
              and (backend=='surface' or fit['layer']==24)]
        if len(fits)!=3 or {fit['seed'] for fit in fits}!={17,29,43}:
            raise ValueError('complete three-seed fixed primary required')
        for method in METHODS:
            family_points={}
            for family in FAMILIES:
                points=[fit['metrics'][method]['whole_categorical_families'][family] for fit in fits]
                family_points[family]=dict(accuracy=float(np.mean([p['accuracy'] for p in points])),
                    group_macro_accuracy=float(np.mean([p['group_macro_accuracy'] for p in points])),
                    n=points[0]['n'],heads=4)
            comparisons={}
            for scope in ('assignment','parent','combined_eight'):
                comparisons[scope]={}
                for route in ('joint','factorized'):
                    points=[fit['metrics'][method]['binding_comparisons'][
                        'combined_eight' if scope=='combined_eight' else 'whole_by_kind'] for fit in fits]
                    points=[point[route] if scope=='combined_eight' else point[scope][route] for point in points]
                    comparisons[scope][route]=dict(accuracy=float(np.mean([p['accuracy'] for p in points])),
                        group_macro_accuracy=float(np.mean([p['group_macro_accuracy'] for p in points])),n=points[0]['n'])
            primary[backend][method]=dict(whole_families=family_points,binding_comparisons=comparisons)
    return dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=result['config_hash'],
        cases=5760,training_rows=4320,development_rows=1440,training_groups=45,development_groups=15,
        fit_banks=30,factorizations=result['factorizations'],parameter_replay_rows=result['parameter_replay_rows'],
        primary=primary,active_sites=[7,8],capture_site_ids=[3,7,8],initial_site3='All192targets undefined; no banks or fits.',
        new_model_queries=0,generated_holdouts_opened=False,
        capacity=dict(direct_joint_outputs_per_event=16,separate_outputs_per_event=8,parameter_matched=False),
        limitation='Adaptive direct categorical decoding, not natural causal use; component ridge scores are joint-score marginals, so the comparison concerns argmax decisions rather than independent representations; rare parent/event7 version4 has only2TRAIN graph families; all classes remain evaluated.')


def _report(result):
    summary=_summary(result)
    lines=['# Direct joint owner and version decoding','',
        f"{result['model']}: 5,760 existing capture rows; 45 TRAIN and 15 DEV graph families. Thirty active score banks at sites7/8 completed exact parameter and metric replay. Initialization site3 has no defined event targets and is not fitted.",'',
        'Primary layer24/site7 points average all three fixed seeds. Joint16-class heads and owner4/version4 heads have different output capacity. Because their labels are coherent and ridge is linear with shared features, weights and alpha, component scores equal marginal sums of joint scores up to roundoff. The two argmax routes compare decisions rather than independent learned representations. All classes, slots, profiles, capture-status strata and graph denominators remain in the scientific result.','',
        '| Backend | Method | Assignment joint4 | Assignment factorized4 | Parent joint4 | Parent factorized4 | Joint all8 | Factorized all8 |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for backend in ('hidden','surface'):
        for method in METHODS:
            p=summary['primary'][backend][method]['binding_comparisons']
            points=[p[scope][route]['accuracy'] for scope in ('assignment','parent','combined_eight') for route in ('joint','factorized')]
            lines.append('| '+' | '.join([backend,method,*[f'{100*v:.3f}%' for v in points]])+' |')
    lines+=['','The source-owner comparator parses visible LHS/RHS names and combines them with weighted TRAIN conditional version priors. It does not execute DEV source or inspect DEV version targets. Prefix-sham joint labels supply their own coherent owner/version components; the task remains distinct from the real graph.','',
        'First-copy assignment version2 and first-parent version1 are constants. Last-parent version4 occurs in only two TRAIN graph families and fails the three-family support diagnostic; it is retained in every evaluation. No confidence interval, behavioral qualification, causal binding mechanism or unfamiliar-program claim follows.','']
    return '\n'.join(lines)


def _isolated_engine():
    name=__package__+'._direct_identity_readout_engine'
    spec=importlib.util.spec_from_file_location(name,original.__file__)
    if spec is None or spec.loader is None:raise ValueError('tested readout engine unavailable')
    engine=importlib.util.module_from_spec(spec);sys.modules[name]=engine;spec.loader.exec_module(engine)
    engine.ROLE=ROLE;engine.SITES=SITES;engine.CAPTURE_SITE_IDS=(3,7,8);engine.FIXED_GRID_BANKS=30
    for key in ('SOURCE_ROWS','TRAIN_ROWS','DEV_ROWS','TRAIN_GROUPS','DEV_GROUPS'):setattr(engine,key,globals()[key])
    engine._targets=_targets;engine._capture=_capture;engine.MAX_RESULT=192*1024**2
    engine.LIMITATIONS=[
        'Adaptive direct owner@version classification on consumed diversity captures; no new LM queries or learned causal mechanism.',
        'Global16-class identity codebook; separate owner/version heads use8outputs versus16for joint heads, so total capacity differs.',
        'Identical linear-ridge fitting makes component scores joint-score marginal sums up to roundoff; joint-versus-factorized argmax alone does not identify separate representations.',
        'All classes remain scored; last-parent/event7 version4 appears in only2TRAIN graph families and does not meet the three-group diagnostic.',
        'Source-owner plus TRAIN conditional-version prior is an explicit comparator; no DEV targets or source SSA execution enter its predictions.',
        'Sites7/8 alone are fitted; source initialization site3 has all192event labels undefined and no fitted bank.',
        'Fifteen DEV graph families and related variants support descriptive discovery; no new interval, behavioral gate or untouched generalization claim.']
    def protocol():
        return dict(sites=[7,8],capture_site_ids=[3,7,8],seeds=[17,29,43],alpha=100.,
            primary_train_class_group_minimum=3,binary_threshold=.5,primary_layer=24,primary_site=7,
            source_features='signed character ngrams3..8, matched hidden width',
            target_columns=192,categorical_heads=24,identity_codebook='4*owner+(version-1)',
            control='Prefix-keyed joint identity draw with coherent owner/version components; not a lawful graph or marginal-matched task.',
            additional_comparator='Parsed visible source owners plus weighted TRAIN conditional version priors.',
            component_score_relation='Joint-score marginal sums under shared linear ridge; comparison concerns argmax decisions, not independent representations.',
            source_only_site3='All192event targets undefined; zero fitted banks.',
            interval='none; all15DEV graph outcomes and all fixed layers/heads/classes retained')
    engine.protocol=protocol
    old_config=engine._config
    def config(value):
        result=old_config(value)
        if value['primary_layer']!=24:raise ValueError('fixed direct-identity primary layer24 required')
        return result
    engine._config=config
    old_metadata=engine._metadata
    def metadata(config,scheduled):
        source,checked,records=old_metadata(config,scheduled)
        if checked['source']['snapshot_id']!=SOURCE_SNAPSHOT or checked['source']['source_sha256']!=SOURCE_SHA:
            raise ValueError('originalS3 diversity capture source required')
        return source,checked,records
    engine._metadata=metadata
    old_bundles=engine._bundles
    def bundles(records):
        _initialization(records)
        return old_bundles(records)
    engine._bundles=bundles
    old_metrics=engine.metrics
    def metrics(bundle,scores,support):
        result=old_metrics(bundle,scores,support)
        result['binding_comparisons']=binding_comparisons(bundle,scores)
        return result
    engine.metrics=metrics
    engine._additional_predictions=lambda bundle,train,weights:{
        'source_owner_version_prior':_targets().syntax_owner_version_prior(bundle,train,weights)}
    engine._summary=_summary;engine._report=_report
    old_finish=engine._finish
    def finish(config,result,artifacts):
        result['primary']['tasks']=list(FAMILIES)
        return old_finish(config,result,artifacts)
    engine._finish=finish
    return engine


_CORE=_isolated_engine()
protocol=_CORE.protocol
preflight=_CORE.preflight
run=_CORE.run
audit=_CORE.audit
completed_result=_CORE.completed_result
_config=_CORE._config
_metadata=_CORE._metadata
_bundles=_CORE._bundles
