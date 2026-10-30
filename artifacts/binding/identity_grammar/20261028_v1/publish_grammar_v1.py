"""Deterministic metadata-only publication of source-free grammar reconstruction.

Only bounded JSON/report metadata and their pins are read. No score NPZ, model,
feature, parameter, prepared/source or response record is opened. --self-test
uses a temporary synthetic metadata cohort, never actual scientific outcomes.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
import hashlib
import io
from itertools import product
import json
import math
import os
from pathlib import Path
import tempfile

ROLE='discovery_identity_grammar_review_v1'
PUBLICATION_ROLE='discovery_identity_grammar_publication_v1'
SUITE=Path('artifacts/binding/identity_grammar/20261028_v1')
MAX_JSON=192*1024**2
INPUTS={}
MODELS={
 'llama8b':('Llama 3.1 8B',(8,16,24,31)),
 'codellama34b':('CodeLlama 34B',(12,24,36,47)),
}
METHODS=('direct','training_prior','random_prefix_control','source_owner_version_prior')
RULES=('joint_allow_self','joint_no_self','owner_marginal_allow_self','owner_marginal_no_self')
SITES=(7,8)
SEEDS=(17,29,43)
TASKS=('assignment','parent','combined_eight')
LIMITATIONS=[
 'Adaptive decoder-assisted reconstruction over the same consumed discovery cases; no maintained neural state or natural causal mechanism is established.',
 'The grammar externally computes versions from a candidate owner history. A correct source-owner sequence supplies a100%counter-grammar reference without a neural version representation.',
 'Primary broad grammar allows self-copy; no-self is a separately named global cohort prior. No actual source, query, truth or per-case profile enters decoding.',
 'Joint and owner-marginal evidence are views of the same uncalibrated ridge table. Marginal sums are not independent representations or calibrated probabilities.',
 'Constrained validity is guaranteed by construction. For lawful real truth, non-decreasing whole-eight accuracy under the same evidence and fixed ties is a mathematical property, not learned skill.',
 'Historical joint/factorized references are distinct from the per-rule exact same-evidence free objective; owner-only improvements can be external counting.',
 'Sham truth is locally coherent but can be globally unlawful. Its lawfulness fraction bounds constrained exact accuracy; constrained-sham accuracy is not difficulty-matched selectivity.',
 'Fifteen DEV graph families have96dependent relatives each; three weighting seeds are dependent variants. No new interval or population confirmation is claimed.',
 'First write version2/first parent version1 are constants, source syntax exposes owners, and final-parent version4 has only2TRAIN graph families per owner.',
 'No new fit, parameter application, model query, response or capture. Old-value recovery, failed computed gates, selective causal use and untouched forecasting remain unresolved.',
]

def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_bytes(value):
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    require(len(data) <= MAX_JSON, "Publication JSON exceeds 192MiB")
    return data


def workspace():
    for parent in Path(__file__).resolve().parents:
        frozen = parent / "frozen_manifest.json"
        if frozen.is_file():
            require(frozen.stat().st_size <= MAX_JSON, "Bounded frozen manifest required")
            candidate = Path(json.loads(frozen.read_text())["workspace_root"]).resolve()
            if (candidate / SUITE).is_dir():
                return candidate
        if (parent / "src/codecue/binding").is_dir() and (parent / SUITE).is_dir():
            return parent
    raise ValueError("Cannot resolve direct identity publication workspace")


def resolve(root, value):
    path = Path(value)
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    require(path == root or root in path.parents, "Publication paths must stay in the workspace")
    return path


def checksum(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def pin(root, path, data):
    path = resolve(root, path)
    result = dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    require(INPUTS.setdefault(result["path"], result) == result, "Input changed during publication")
    return result


def read_json(root, path, expected=None, limit=8*1024**2):
    path = resolve(root, path)
    require(path.suffix == ".json" and path.is_file() and path.stat().st_size <= limit,
            "Only bounded JSON metadata may be opened: " + str(path))
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "JSON metadata grew beyond bound")
    entry = pin(root, path, data)
    if isinstance(expected, str):
        require(entry["sha256"] == expected, "Metadata SHA256 differs")
    elif expected is not None:
        require(entry["sha256"] == expected["sha256"] and ("bytes" not in expected or entry["bytes"] == expected["bytes"])
                and resolve(root, expected["path"]) == path, "Pinned metadata differs")
    result = json.loads(data)
    require(isinstance(result, dict), "Metadata JSON object required")
    return result


def source_profile(root, source, relative):
    folder = resolve(root, source["snapshot"])
    frozen = read_json(root, folder / "frozen_manifest.json", source["frozen_manifest_sha256"])
    require(frozen["snapshot_id"] == source["snapshot_id"]
            and frozen["code"]["source_sha256"] == source["source_sha256"], "Frozen source identity differs")
    require(str(relative) in frozen["config_files"], "Required configuration was not frozen")
    return read_json(root, folder / relative, frozen["config_files"][str(relative)])


def _point(value):
    return value is None or (isinstance(value, (float, int)) and not isinstance(value, bool)
                             and math.isfinite(value) and 0 <= value <= 1)


def _mean(values):
    require(len(values) == 3, "All three declared weighting seeds required")
    return sum(values) / 3 if all(v is not None for v in values) else None


def _same_point(left, right):
    return left is None and right is None or (left is not None and right is not None
        and math.isclose(left, right, rel_tol=0, abs_tol=1e-14))


def publish(path, data):
    path = Path(path)
    require(not path.is_symlink(), "Output symlinks are forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.is_file() and path.read_bytes() == data, "Immutable publication differs: " + str(path))
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name + ".", suffix=".pending", delete=False) as stream:
            temporary = Path(stream.name); stream.write(data); stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            require(not path.is_symlink() and path.read_bytes() == data, "Concurrent publication differs")
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


FIT_SNAPSHOT='3e5471ac9dc9b948761fc429'
FIT_SHA='6a34415f2a9dfdab2acb5ceecc8fb88e19b8982d21881890c137f96082ddf1ee'
CAPTURE_SNAPSHOT='345f75b01f5c3b33bd0ca6d8'
RULE_MAP={name:('owner_marginal' if name.startswith('owner_marginal') else 'joint',name.endswith('allow_self')) for name in RULES}


def compact(point):
    return {key:point[key] for key in ('n','correct','accuracy','group_macro_accuracy')}|dict(graph_groups=len(point['per_group']))


def validate_point(point,full=False):
    require(type(point.get('n')) is int and type(point.get('correct')) is int
            and 0<=point['correct']<=point['n']<=5760,'Bounded point counts required')
    n=point['n'];groups=point.get('per_group');require(isinstance(groups,dict),'Point graph counts required')
    require(_point(point.get('accuracy')) and _point(point.get('group_macro_accuracy')),'Finite bounded point required')
    require(all(type(p.get('n')) is int and type(p.get('correct')) is int and 0<=p['correct']<=p['n'] and p['n']>0
                and _point(p.get('accuracy')) and p['accuracy'] is not None for p in groups.values()),'Per-graph point differs')
    require(sum(p['n'] for p in groups.values())==n and sum(p['correct'] for p in groups.values())==point['correct'],'Point graph totals differ')
    for p in groups.values():require(_same_point(p['accuracy'],p['correct']/p['n']),'Graph rate differs from count')
    if n:
        require(_same_point(point['accuracy'],point['correct']/n)
                and _same_point(point['group_macro_accuracy'],sum(p['accuracy'] for p in groups.values())/len(groups)),'Point row/group rates differ')
    else:require(point['accuracy'] is point['group_macro_accuracy'] is None and not groups,'Undefined point must stay null')
    if full:require(n==1440 and len(groups)==15 and all(p['n']==96 for p in groups.values())
                    and _same_point(point['accuracy'],point['group_macro_accuracy']),'Full15-by96 denominator required')


def walk_points(value):
    if isinstance(value,dict):
        if {'n','correct','accuracy','group_macro_accuracy','per_group'}<=value.keys():validate_point(value)
        for item in value.values():walk_points(item)
    elif isinstance(value,(list,tuple)):
        for item in value:walk_points(item)


def validate_metrics(metrics):
    require(set(metrics['whole'])==set(TASKS) and set(metrics['per_head'])=={f'{k}/{e}' for k in ('assignment','parent') for e in range(4,8)},'Full endpoint/head inventory required')
    for point in metrics['whole'].values():validate_point(point,True)
    require(metrics['whole']['combined_eight']['correct']<=min(metrics['whole'][k]['correct'] for k in ('assignment','parent')),'Whole-eight exceeds component task')
    for head in metrics['per_head'].values():
        validate_point(head,True);classes=head['classes'];require(set(classes)=={str(c) for c in range(16)},'All16classes required')
        require(sum(c['n'] for c in classes.values())==1440 and sum(c['correct'] for c in classes.values())==head['correct'],'Class counts differ')
        require(type(head['missing_predictions']) is int and 0<=head['missing_predictions']<=1440,'Missing decisions must remain counted')
        require(set(head['by_profile'])=={'2_1_1_0','3_1_0_0','2_2_0_0'} and sum(p['n'] for p in head['by_profile'].values())==1440,'Allprofile counts required')
        require(sum(p['n'] for p in head['by_capture_status'].values())==1440,'Status counts differ')
    require(set(metrics['by_profile'])=={'2_1_1_0','3_1_0_0','2_2_0_0'},'Three profile strata required')
    for task in TASKS:require(sum(p[task]['n'] for p in metrics['by_profile'].values())==1440 and sum(p[task]['correct'] for p in metrics['by_profile'].values())==metrics['whole'][task]['correct'],'Profile endpoint totals differ')
    for kind in ('assignment','parent'):
        require(sum(p['n'] for p in metrics['by_capture_status'][kind].values())==5760
                and sum(p['correct'] for p in metrics['by_capture_status'][kind].values())==sum(metrics['per_head'][f'{kind}/{e}']['correct'] for e in range(4,8)),'Pooled status counts differ')


def validate_exact(entry):
    exact=entry['exact_objective_checks'];require(all(exact.get(k) is True for k in ('exact_arithmetic','selected_and_free_path_scores_recomputed','projection_penalty_nonnegative')),'Exact-objective proof flags required')
    names=('score','free_upper_bound','projection_penalty');positive=0;finite=0
    require(len(exact['path_code'])==1440 and all(type(c) is int and -1<=c<=65535 for c in exact['path_code']),'Bounded exact path codes required')
    for name in names:require(len(exact[name+'_numerators'])==len(exact[name+'_exponents'])==1440,'All exact objective pairs required')
    for i in range(1440):
        pairs=[(exact[n+'_numerators'][i],exact[n+'_exponents'][i]) for n in names]
        if pairs[0]==(None,None):
            require(all(p==(None,None) for p in pairs) and exact['path_code'][i]==-1,'Missing objectives must be undefined');continue
        finite+=1;converted=[]
        for numerator,exponent in pairs:
            require(isinstance(numerator,str) and 0<len(numerator)<=2048 and type(exponent) is int and -4096<=exponent<=4096,'Bounded dyadic pair required')
            number=int(numerator);require(str(number)==numerator and (number%2!=0 or number==0 and exponent==0),'Canonical dyadic pair required');converted.append((number,exponent))
        (a,ae),(b,be),(c,ce)=converted;base=min(ae,be,ce)
        require(c>=0 and (b<<(be-base))-(a<<(ae-base))==c<<(ce-base),'Exact upper-bound minus score differs from penalty')
        positive+=c>0
    require(finite==entry['finite_cases'] and positive==exact['positive_penalty_cases'],'Exact-objective finite/penalty counts differ')


def validate_transitions(transition,reference,selected):
    for task in TASKS:
        item=transition[task]
        for name in ('corrected','harmed','both_correct','both_wrong','changed'):validate_point(item[name],True)
        require(sum(item[n]['correct'] for n in ('corrected','harmed','both_correct','both_wrong'))==1440,'Transition partition differs')
        require(item['both_correct']['correct']+item['harmed']['correct']==reference['whole'][task]['correct']
                and item['both_correct']['correct']+item['corrected']['correct']==selected['whole'][task]['correct'],'Transition margins differ')
        require(item['changed']['correct']>=item['corrected']['correct']+item['harmed']['correct'],'A correctness transition must change prediction')
        strata=item['by_free_joint_lawfulness'];require(set(strata)=={'lawful','unlawful'},'Both free-lawfulness strata required')
        for name in ('corrected','harmed','both_correct','both_wrong','changed'):
            require(sum(p[name]['n'] for p in strata.values())==1440 and sum(p[name]['correct'] for p in strata.values())==item[name]['correct'],'Transition lawfulness totals differ')


def extract_diagnostic(diagnostic,cell):
    require(diagnostic['original_metrics_exact'] is True and set(diagnostic['methods'])==set(METHODS),'Original methods and metrics must remain')
    walk_points(diagnostic);counter=diagnostic['source_owner_counter'];validate_metrics(counter)
    require(all(p['correct']==1440 for p in counter['whole'].values()),'Source-owner counter reference must be100%')
    rows=[]
    for method,item in diagnostic['methods'].items():
        require(item['truth_task']==('prefix_sham' if method=='random_prefix_control' else 'real') and set(item['rules'])==set(RULES),'Correct own-task/control scope required')
        for reference in ('free_joint','free_marginal'):validate_metrics(item[reference])
        for rule,entry in item['rules'].items():
            evidence,allow_self=RULE_MAP[rule]
            require(entry['evidence']==evidence and entry['allow_self'] is allow_self,'Rule identity differs')
            require(type(entry['finite_cases']) is int and 0<=entry['finite_cases']<=1440
                    and entry['lawful_cases']==entry['finite_cases'] and entry['missing_cases']+entry['finite_cases']==1440,'Finite/lawful/missing cases differ')
            require(entry['same_evidence_lawful_free_preserved'] is True
                    and entry['joint_historical_lawful_truth_whole8_monotonic'] is (True if evidence=='joint' else None),'Scoped theorem metadata required')
            for task in ('own_task','real_task','free_objective'):validate_metrics(entry[task])
            ceiling=entry['truth_lawfulness_ceiling'];validate_point(ceiling,True)
            require(entry['own_task']['whole']['combined_eight']['correct']<=ceiling['correct'],'Constrained own accuracy exceeds lawful-truth ceiling')
            if method!='random_prefix_control':
                require(ceiling['correct']==1440 and entry['own_task']==entry['real_task'],'Real task must remain distinct from sham cross-task')
                if entry['finite_cases']==1440:
                    require(entry['own_task']['whole']['combined_eight']['correct']>=entry['free_objective']['whole']['combined_eight']['correct'],'Same-objective real whole-eight accuracy decreased')
                    if evidence=='joint':require(entry['transitions']['free_joint']['combined_eight']['harmed']['correct']==0,'Real finite joint whole-correct path harmed')
            validate_exact(entry)
            for reference in ('free_joint','free_marginal'):validate_transitions(entry['transitions'][reference],item[reference],entry['own_task'])
            row={k:cell[k] for k in ('model','name','backend','layer','site','seed')}
            row.update(method=method,rule=rule,evidence=evidence,allow_self=allow_self,truth_task=item['truth_task'],
                own_task={s:compact(entry['own_task']['whole'][s]) for s in TASKS},real_task={s:compact(entry['real_task']['whole'][s]) for s in TASKS},
                free_joint={s:compact(item['free_joint']['whole'][s]) for s in TASKS},free_marginal={s:compact(item['free_marginal']['whole'][s]) for s in TASKS},
                free_objective={s:compact(entry['free_objective']['whole'][s]) for s in TASKS},truth_lawfulness_ceiling=compact(ceiling),
                free_joint_lawfulness={k:compact(v) for k,v in item['free_joint_lawfulness'].items()},finite_cases=entry['finite_cases'],lawful_cases=entry['lawful_cases'],missing_cases=entry['missing_cases'],
                same_evidence_lawful_free_cases=entry['same_evidence_lawful_free_cases'],positive_projection_penalty_cases=entry['exact_objective_checks']['positive_penalty_cases'],
                transitions={ref:{scope:{key:compact(entry['transitions'][ref][scope][key]) for key in ('corrected','harmed','both_correct','both_wrong','changed')} for scope in TASKS} for ref in ('free_joint','free_marginal')},
                diagnostic=cell['diagnostic'],source_owner_counter_accuracy=1.)
            rows.append(row)
        for evidence in ('joint','owner_marginal'):
            broad=item['rules'][evidence+'_allow_self'];narrow=item['rules'][evidence+'_no_self']
            require(narrow['nested_feasible_broad_preserved'] is True and 0<=narrow['nested_feasible_broad_cases']<=1440,'Nested feasible preservation proof required')
            require(narrow['real_task']['whole']['combined_eight']['correct']>=broad['real_task']['whole']['combined_eight']['correct'],'No-self harmed an exact feasible real tuple')
    return rows


def load_inputs(root):
    out=root/SUITE/'analysis';receipt=read_json(root,out/'completion_manifest_v1.json')
    require(receipt.get('status')=='complete_exploratory' and receipt.get('evaluation_role')==ROLE
            and receipt.get('score_banks')==60,'Complete60-bank grammar receipt required')
    source=receipt['source'];config=source_profile(root,source,Path('configs/binding/identity_grammar_review_v1.json'))
    require(config['evaluation_role']==ROLE and digest(config)==receipt['config_hash']
            and resolve(root,config['run_dir'])==out,'Frozen grammar config differs')
    pointer=read_json(root,root/SUITE/'execution_source_v1.json')
    require(pointer['snapshot_id']==source['snapshot_id'] and pointer['code']==source['source_sha256']
            and resolve(root,pointer['snapshot'])==resolve(root,source['snapshot']),'Execution source pointer differs')
    plan=resolve(root,config['declared_plan']);require(plan.suffix=='.md' and plan.is_file() and plan.stat().st_size<=8*1024**2,'Bounded plan required')
    require(pin(root,plan,plan.read_bytes())['sha256']==config['declared_plan_sha256'],'Plan SHA differs')
    inventory=receipt['artifacts'];require(len(inventory)==125,'Exact125-artifact grammar inventory required')
    expected={name:out/filename for name,filename in [('registration','registration.json'),('results','results_v1.json'),('summary','summary.json'),('audit','audit.json')]};expected['report']=resolve(root,config['report'])
    metadata={name:read_json(root,path,inventory[name],limit=MAX_JSON if name=='results' else 8*1024**2) for name,path in expected.items() if name!='report'}
    require(expected['report'].suffix=='.md' and expected['report'].is_file() and expected['report'].stat().st_size<=8*1024**2,'Bounded original report required')
    require(pin(root,expected['report'],expected['report'].read_bytes())==inventory['report'],'Original report changed')
    proof=read_json(root,out/'grammar_replay_review_v1.json')
    require(proof.get('status')=='passed' and proof.get('evaluation_role')==ROLE and proof.get('source_artifacts')==inventory
            and proof.get('original_score_banks_reopened') is False
            and all(proof.get(k) is True for k in ('all_grammar_diagnostics_recomputed','all_original_metrics_recomputed','all_new_dev_score_banks_reopened')),'Actual new-score grammar replay proof required')
    for doc in [receipt,proof,*metadata.values()]:
        require(doc.get('evaluation_role')==ROLE and doc.get('config_hash')==receipt['config_hash']
                and all(doc.get(k)==0 for k in ('new_fits','new_model_queries','parameters_reapplied'))
                and doc.get('generated_holdouts_opened') is False,'Identity/zero-work flags differ')
    result=metadata['results'];summary=metadata['summary'];registration=metadata['registration']
    require(result['source']==source==proof['source'] and registration['source']==source
            and registration['config']==config and registration['protocol']==result['protocol'],'Registered decoder source/protocol differs')
    for doc in (receipt,proof,result,summary):
        require((doc['score_banks'],doc['saved_score_rows_checked'],doc['development_prediction_rows'])==(60,345600,86400),'Complete fixed accounting required')
    require(metadata['audit']['status']=='passed' and result['original_metrics_exact'] is True
            and result['fit_source_snapshot']==FIT_SNAPSHOT and result['capture_source_snapshot']==CAPTURE_SNAPSHOT,'Original fit/capture or audit differs')
    protocol=result['protocol'];require(protocol['rules']=={r:dict(evidence=e,allow_self=a) for r,(e,a) in RULE_MAP.items()}
            and protocol['sites']==[7,8] and protocol['seeds']==list(SEEDS) and protocol['initial_versions']==[1]*4
            and protocol['maximum_version']==4 and protocol['profile_constraints'] is False and protocol['source_features_to_decoder'] is False,'Fixed source-free grammar recipe differs')
    upstream={}
    for item in config['readout_configs']:
        cfg=read_json(root,item['path'],item['sha256'],16*1024);folder=resolve(root,cfg['run_dir']);old=read_json(root,folder/'completion_manifest_v1.json');audit=read_json(root,folder/'parameter_replay_review_v1.json')
        require(cfg['evaluation_role']=='discovery_direct_identity_readouts_v1' and digest(cfg)==old['config_hash']
                and old['fit_source']['snapshot_id']==FIT_SNAPSHOT and old['fit_source']['source_sha256']==FIT_SHA
                and old['capture_source']['snapshot_id']==CAPTURE_SNAPSHOT
                and old['fit_banks']==old['factorizations']==30 and old['parameter_replay_rows']==172800
                and audit['status']=='passed' and audit['source_artifacts']==old['artifacts'],'Original S5 source/proof differs')
        model='llama8b' if 'llama8b' in str(item['path']) else 'codellama34b'
        require(model not in upstream,'Distinct model configs required');upstream[model]=old
    require(set(upstream)==set(MODELS),'Both models required')
    grid={(m,b,l,s,k) for m,(_,layers) in MODELS.items() for b,l in [('hidden',l) for l in layers]+[('surface',-1)] for s in SITES for k in SEEDS};seen=set();artifact_keys=set(expected);rows=[];diagnostic_pins=[]
    require(len(result['cells'])==60,'All60bank cells required')
    for cell in result['cells']:
        key=tuple(cell[k] for k in ('model','backend','layer','site','seed'));require(key in grid and key not in seen,'Duplicate or undeclared bank');seen.add(key)
        name=f"{cell['backend']}_layer{cell['layer']}_site{cell['site']}_seed{cell['seed']}";require(cell['name']==name and cell['original_metrics_exact'] is True,'Bank identity differs')
        require(cell['original_score_bank']==upstream[cell['model']]['artifacts'][name],'Original bank pin differs')
        for kind,prefix,suffix,field in [('scores','scores','.npz','score_bank'),('diagnostics','diagnostics','.json','diagnostic')]:
            artifact_key=f'{kind}_{cell["model"]}_{name}';path=out/f'{prefix}_{cell["model"]}_{name}{suffix}';entry=inventory[artifact_key]
            require(entry==cell[field] and resolve(root,entry['path'])==path and checksum(entry['sha256']) and type(entry['bytes']) is int and 0<entry['bytes']<=512*1024**2,'Pinned new bank inventory differs');artifact_keys.add(artifact_key)
        diagnostic=read_json(root,cell['diagnostic']['path'],cell['diagnostic'],limit=MAX_JSON)
        require(all(diagnostic[k]==cell[k] for k in ('model','name','backend','layer','site','seed','original_metrics_exact','original_score_bank','score_bank')) and diagnostic['source']==source
                and diagnostic['config_hash']==receipt['config_hash'] and diagnostic['evaluation_role']==ROLE,'Diagnostic source/grid identity differs')
        cells=extract_diagnostic(diagnostic,cell);rows.extend(cells);diagnostic_pins.append(cell['diagnostic'])
        for method in METHODS:
            summary_method=cell['summary_methods'][method];d=diagnostic['methods'][method]
            require(summary_method['free_joint']==d['free_joint']['whole'] and summary_method['free_marginal']==d['free_marginal']['whole'],'Saved free summary differs')
            for rule in RULES:
                for task in ('own_task','real_task'):require(summary_method['rules'][rule][task]==d['rules'][rule][task]['whole'],'Saved rule summary differs')
    require(seen==grid and set(inventory)==artifact_keys and len(rows)==960,'Complete60-bank/960-rule grid required')
    for model,backend,site,method,rule,task,scope in product(MODELS,('hidden','surface'),SITES,METHODS,RULES,('own_task','real_task'),TASKS):
        selected=[row for row in rows if row['model']==model and row['backend']==backend and row['site']==site and row['method']==method and row['rule']==rule and (backend=='surface' or row['layer']==24)]
        require({r['seed'] for r in selected}==set(SEEDS),'All3primary seeds required')
        for field in ('accuracy','group_macro_accuracy'):require(_same_point(_mean([r[task][scope][field] for r in selected]),summary['primary'][model][backend][str(site)][method][rule][task][scope][field]),'Primary summary differs')
    return dict(source=source,config=config,summary=summary,rows=rows,diagnostic_pins=diagnostic_pins,proof=proof,inventory=inventory)


def table_bytes(rows):
    fields=['model','backend','layer','site','seed','method','rule','evidence','allow_self','truth_task','finite_cases','lawful_cases','missing_cases','same_evidence_lawful_free_cases','positive_projection_penalty_cases']
    for view in ('own_task','real_task','free_joint','free_marginal','free_objective'):
        for task in TASKS:
            fields += [f'{view}_{task}_{field}' for field in ('n','correct','accuracy','group_macro_accuracy')]
    fields+=['truth_lawfulness_ceiling_n','truth_lawfulness_ceiling_correct','truth_lawfulness_ceiling_accuracy','truth_lawfulness_ceiling_group_macro_accuracy','transitions_json','diagnostic_path','diagnostic_sha256']
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:
        value={k:row[k] for k in fields if k in row}
        for view in ('own_task','real_task','free_joint','free_marginal','free_objective'):
            for task in TASKS:
                for field in ('n','correct','accuracy','group_macro_accuracy'):value[f'{view}_{task}_{field}']=row[view][task][field]
        for field in ('n','correct','accuracy','group_macro_accuracy'):value['truth_lawfulness_ceiling_'+field]=row['truth_lawfulness_ceiling'][field]
        value.update(transitions_json=json.dumps(row['transitions'],sort_keys=True,separators=(',',':')),diagnostic_path=row['diagnostic']['path'],diagnostic_sha256=row['diagnostic']['sha256']);writer.writerow(value)
    return stream.getvalue().encode()


CONTEXTS=(('hidden','direct','Hidden / direct'),('surface','direct','Prefix text / direct'),('hidden','training_prior','TRAIN prior'),('hidden','source_owner_version_prior','Syntax owner / TRAIN version'),('hidden','random_prefix_control','Sham / own truth'))


def selected(rows,model,backend,method,rule,site=7):
    found=[r for r in rows if r['model']==model and r['backend']==backend and r['method']==method and r['rule']==rule and r['site']==site and (backend=='surface' or r['layer']==24)]
    require(len(found)==3 and {r['seed'] for r in found}==set(SEEDS),'Three fixed primary cells required');return found


def mean_field(rows,view='own_task',task='combined_eight',field='accuracy'):
    return _mean([r[view][task][field] for r in rows])


def figure_bytes(data):
    import matplotlib
    matplotlib.use('Agg',force=True);matplotlib.rcParams.update({'svg.hashsalt':'identity_grammar_v1','font.family':'DejaVu Sans','font.size':9})
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(12.8,8.6),sharex=True)
    for i,model in enumerate(MODELS):
        for j,evidence in enumerate(('joint','owner_marginal')):
            ax=axes[i,j];y=list(range(5));labels=[x[2] for x in CONTEXTS]+['SOURCE owners + counters (real)']
            for suffix,label,color,marker,offset in [('allow_self','Broad grammar','#2463ad','o',-.10),('no_self','No-self cohort prior','#c45426','s',.10)]:
                rule=evidence+'_'+suffix;points=[100*mean_field(selected(data['rows'],model,b,m,rule),field='group_macro_accuracy') for b,m,_ in CONTEXTS]
                ax.plot(points,[v+offset for v in y],color=color,marker=marker,ls='none',ms=6,label=label)
                sham=selected(data['rows'],model,'hidden','random_prefix_control',rule)
                ceiling=100*_mean([r['truth_lawfulness_ceiling']['group_macro_accuracy'] for r in sham])
                ax.plot(ceiling,4+offset,marker='|',ms=14,color=color,ls='none',label='Sham lawful-truth ceiling' if suffix=='allow_self' else None)
            historical=[100*mean_field(selected(data['rows'],model,b,m,evidence+'_allow_self'),view='free_joint',field='group_macro_accuracy') for b,m,_ in CONTEXTS]
            ax.plot(historical,[v+.26 for v in y],marker='x',color='#555555',ls='none',ms=5,label='Historical free joint (own task)')
            ax.plot(100,5,marker='*',color='#338354',ms=10,ls='none',label='SOURCE owner/counter real-task reference')
            ax.set_yticks(range(6),labels);ax.set_ylim(5.5,-.5);ax.set_xlim(-2,103);ax.set_xticks([0,20,40,60,80,100]);ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
            ax.set_title(MODELS[model][0]+' · '+('joint-score evidence' if evidence=='joint' else 'owner-only marginal evidence'),fontsize=10)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.53,.045),ncol=2,frameon=False,fontsize=9)
    fig.supxlabel('DEV equal-family whole-eight exact accuracy (%) · nominated layer 24/site 7',y=.145,fontsize=11)
    fig.suptitle('Decoder-assisted reconstruction from saved identity scores',y=.985,fontsize=14)
    fig.text(.52,.012,'No confidence intervals. Sham is not a matched task. Historical free joint is not the owner-only free objective.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.20,right=.985,bottom=.21,top=.91,wspace=.67,hspace=.23)
    png,svg=io.BytesIO(),io.BytesIO();fig.savefig(png,format='png',dpi=170,metadata={'Software':'CodeCue deterministic grammar publisher'});fig.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue deterministic grammar publisher'});plt.close(fig)
    return png.getvalue(),svg.getvalue(),matplotlib.__version__


def report_bytes(data,decision=False):
    rows=data['rows'];lines=['# '+('Decision: decoder-assisted identity reconstruction' if decision else 'Saved-score grammar reconstruction summary'),'']
    if decision:
        for model in MODELS:
            broad=selected(rows,model,'hidden','direct','joint_allow_self');owner=selected(rows,model,'hidden','direct','owner_marginal_allow_self');narrow=selected(rows,model,'hidden','direct','joint_no_self')
            lines.append(f"{MODELS[model][0]} at layer 24/site 7: historical free-joint whole-eight accuracy {100*mean_field(broad,view='free_joint'):.3f}%; broad joint-score grammar {100*mean_field(broad):.3f}%; owner-only grammar {100*mean_field(owner):.3f}%; no-self joint-score grammar {100*mean_field(narrow):.3f}%. These are dependent discovery point estimates, not independent mechanism tests.")
        lines+=['','Close this bounded phase as a decoder-consistency and reconstruction diagnostic. The grammar can calculate every version from an owner history; the explicit SOURCE-owner counter reference is 100% on real labels by construction. Neither an accuracy increase nor guaranteed validity establishes maintained neural state, natural causal use or a reliable computed-program regime.','',
            'Already-lawful free optima are preserved under the same evidence and ties. For finite real-lawful cases, non-decreasing whole-eight exact accuracy is a theorem of the projection. The no-self rule adds a known cohort prior. Individual heads and four-event subsets may worsen, as can comparisons across different evidence objectives. Sham truth can be unlawful, so its own-task harms and ceiling are legitimate and are kept separate.','',
            'The next scientific decision remains recovery/use of old values and a reproducible behavioral or selective intervention contrast. This analysis adds no values, behavioral responses, intervention or untouched forecast.','']
    else:
        lines+=['Both completed grammar receipts and the actual new-score replay proof passed. The publisher read only bounded JSON/report metadata. It opened no score, activation, feature, parameter, prepared/source or response records and reran no decoder or fit.','',
            'The fixed grid retains 60 original banks, 345,600 original score case rows checked and 86,400 DEV bank-case rows. Four methods and four rules give 960 rule cells; the 1,382,400 case/method/rule evaluations are repeated views of those same cases. All layers and sites 7/8 remain in the CSV and the 60 immutable diagnostic JSONs.','',
            '| Model | Context | Historical free joint | Broad joint | No-self joint | Broad owner-only | No-self owner-only | Own-truth ceiling: broad / no-self |','|---|---|---:|---:|---:|---:|---:|---:|']
        for model in MODELS:
            for backend,method,label in CONTEXTS:
                points=[selected(rows,model,backend,method,rule) for rule in RULES];values=[100*mean_field(points[0],view='free_joint')]+[100*mean_field(p) for p in points]
                ceilings=[100*_mean([r['truth_lawfulness_ceiling']['accuracy'] for r in p]) for p in points[:2]]
                lines.append('| '+' | '.join([MODELS[model][0],label,*[f'{v:.3f}%' for v in values],f'{ceilings[0]:.3f}% / {ceilings[1]:.3f}%'])+' |')
        lines+=['','Every point averages all three fixed weighting seeds at the nominated layer 24/site 7. Whole-eight accuracy requires all four write and four parent identities correct. Each of 15 graph families contributes 96 dependent rows, so whole-endpoint row and equal-family means agree; conditional class/status denominators need not.','',
            '![Primary grammar comparisons](figures/identity_grammar_v1.svg)','',
            'The panels cross models and evidence views. Broad self-copy grammar is primary; no-self is a separately named cohort prior. The green reference uses SOURCE owners plus external counters on real labels only. Sham points score their original own truth; ceiling ticks show the fraction of that truth which is globally lawful. A low constrained-sham score is not matched selectivity evidence. Historical factorized owner+version argmax and each exact same-evidence free objective remain separate in the CSV.','',
            'The decoder receives only saved joint tables and fixed flags, never a source program, query, actual profile or true identity. Raw ridge sums are uncalibrated utilities. Owner-only evidence sums over versions in the same joint table and lets the external grammar supply versions; it is not an independent representation. Validity and real whole-eight monotonicity are construction guarantees on finite cases, not learned competence.','']
    lines+=['All source, class, profile, owner/version, current/obsolete status, lawfulness, repair/harm and exact-objective details remain in the SHA-pinned per-bank diagnostic JSONs referenced by the [comparison](../../artifacts/binding/identity_grammar/20261028_v1/comparison_v1.json). The [full grid CSV](../../artifacts/binding/identity_grammar/20261028_v1/form_cells_v1.csv) and [publication proof](../../artifacts/binding/identity_grammar/20261028_v1/publication_review_v1.json) retain the complete declared scope. The runner\'s [original findings](identity_grammar_findings_v1.md) remain unchanged.','',*['- '+t for t in LIMITATIONS],'']
    text='\n'.join(lines)
    for a,b in [('a100%counter','a 100% counter'),('have96dependent','have 96 dependent'),('version2/first','version 2/first'),('version1 are','version 1 are'),('only2TRAIN','only 2 TRAIN')]:text=text.replace(a,b)
    return text.encode()


def publication(root):
    root=Path(root).resolve();INPUTS.clear();data=load_inputs(root);script=Path(__file__).resolve()
    script_pin=dict(path=str(SUITE/script.name),sha256=hashlib.sha256(script.read_bytes()).hexdigest(),bytes=script.stat().st_size)
    png,svg,version=figure_bytes(data);png2,svg2,_=figure_bytes(data);require((png,svg)==(png2,svg2),'Figure rendering changed bytes')
    comparison=dict(status='complete_metadata_publication',evaluation_role=PUBLICATION_ROLE,source=data['source'],publisher_script=script_pin,primary_layer=24,primary_site=7,source_banks=60,source_score_rows_checked=345600,development_bank_case_rows=86400,rule_cells=960,
        rows=data['rows'],primary_summary=data['summary'],diagnostic_pins=data['diagnostic_pins'],score_inventory={k:v for k,v in data['inventory'].items() if k.startswith('scores_')},input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),
        full_diagnostic_details='Preserved transitively by the60 SHA-pinned per-bank JSONs, including all exact objective pairs; not duplicated into this master.',new_fits=0,new_model_queries=0,parameters_reapplied=0,score_arrays_opened=False,source_records_opened=False,new_intervals=False,limitations=LIMITATIONS)
    out=root/SUITE;outputs={out/'comparison_v1.json':json_bytes(comparison),out/'form_cells_v1.csv':table_bytes(data['rows']),root/'reports/binding/identity_grammar_summary_v1.md':report_bytes(data),root/'reports/binding/identity_grammar_decision_v1.md':report_bytes(data,True),root/'reports/binding/figures/identity_grammar_v1.png':png,root/'reports/binding/figures/identity_grammar_v1.svg':svg}
    review=dict(status='passed',evaluation_role=PUBLICATION_ROLE,publisher_script=script_pin,input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),output_pins=[dict(path=str(p.relative_to(root)),bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for p,v in outputs.items()],plotting_version=version,
        checks=dict(complete60bank960rule_grid=True,all125artifact_metadata_pins_verified=True,actual_new_score_replay_proof_required=True,primary_layer24_site7_three_seed_means_verified=True,sham_own_truth_ceiling_separate=True,finite_theorem_scope_preserved=True,source_counter_real_reference100=True,exact_objective_metadata_checked=True,large_diagnostics_retained_by_hash=True,source_score_arrays_never_opened=True,byte_identical_repeat_render=True),new_fits=0,new_model_queries=0,parameters_reapplied=0,new_intervals=False)
    review_bytes=json_bytes(review);require(len(review_bytes)<=8*1024**2,'Publication review must stay compact');outputs[out/'publication_review_v1.json']=review_bytes
    existed=all(p.is_file() for p in outputs)
    for p,value in outputs.items():require(not p.is_symlink() and (not p.exists() or p.read_bytes()==value),'Immutable publication differs before writing')
    for p,value in outputs.items():publish(p,value)
    return dict(status='byte_identical_reproduction' if existed else 'published',rule_cells=960,diagnostic_pins=60,publication_review=str(SUITE/'publication_review_v1.json'))


def synthetic_diagnostic():
    """Small SOURCE-only traces exercise the actual producer, never study arrays."""
    import sys
    sys.path.insert(0,str(workspace()/'src'))
    import numpy as np
    from dataclasses import replace
    from codecue.binding import grammar_identity_review as producer
    from codecue.binding import direct_identity_targets as target,relationships
    patterns=[('2_1_1_0',(0,1,2,0),(1,2,3,1)),('3_1_0_0',(0,0,0,1),(1,2,3,0)),('2_2_0_0',(0,1,0,1),(1,2,3,0))]
    n=15;y=np.zeros((n,192));control=np.zeros_like(y);mask=np.ones_like(y,dtype=bool);statuses=[];syntax=[];profiles=[]
    for i in range(n):
        profile,dest,parents=patterns[i//5]
        source='\n'.join([f'v{k} = {k+1}' for k in range(4)]+[f'v{d} = v{p}' for d,p in zip(dest,parents)]+['v0'])+'\n'
        graph=relationships.labels_at(source,7,{f'v{k}':k for k in range(4)});nodes={node['id']:node for node in graph['version_nodes']};by_statement={node['statement']:node for node in nodes.values()};edges={child:parent for parent,child in graph['direct_def_use_edges']};status={'assignment':[],'parent':[]}
        for event in range(4,8):
            written=by_statement[event];read=nodes[edges[written['id']]]
            for kind,node in (('assignment',written),('parent',read)):
                target._set_event(y,i,kind,event,node['slot'],node['version']);target._set_event(control,i,kind,event,0,1);status[kind].append(node['status'])
        statuses.append(status);syntax.append(dict(assignment=list(dest),parent=list(parents)));profiles.append(profile)
    desc=dict(control=False,profile_ids=profiles,syntax_owners=syntax,event_capture_status=statuses)
    bundle=target.TargetBundle(y,mask,target.COLUMNS,tuple(f'fixture{i}' for i in range(n)),tuple(f'graph{i}' for i in range(n)),('development',)*n,7,desc)
    sham=replace(bundle,y=control,descriptive={**desc,'control':True})
    raw,_,_=producer._evaluate_bank(bundle,sham,np.stack([y,y,control,y]).astype(np.float64))
    def scale(value,key=None):
        if isinstance(value,dict):return {k:scale(v,k) for k,v in value.items()}
        if isinstance(value,(list,tuple)):
            if key in ('score_numerators','score_exponents','free_upper_bound_numerators','free_upper_bound_exponents','projection_penalty_numerators','projection_penalty_exponents','path_code'):
                return [item for item in value for _ in range(96)]
            return [scale(v) for v in value]
        if type(value) is int:return value*96
        return value
    return scale(raw)


def synthetic_workspace(root):
    """Complete60-bank metadata cohort; binary/source records intentionally absent."""
    def write(path,value):
        data=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode();publish(path,data)
        return dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    import sys
    sys.path.insert(0,str(workspace()/'src'))
    from codecue.binding import grammar_identity_review as producer
    raw=synthetic_diagnostic();out=root/SUITE/'analysis';frozen=root/'artifacts/snapshots/grammar_fixture';plan='reports/binding/identity_grammar_plan_v1.md';plan_bytes=b'Synthetic fixed grammar plan\n';publish(root/plan,plan_bytes)
    readouts=[];upstream={}
    for model in MODELS:
        cfgpath=Path('configs/binding/direct_identity_20261028_v1')/(model+'_readouts.json');cfg=dict(evaluation_role='discovery_direct_identity_readouts_v1',run_dir=str(Path('artifacts/binding/direct_identity/20261028_v1')/model/'readouts'),primary_layer=24)
        entry=write(root/cfgpath,cfg);readouts.append(dict(path=str(cfgpath),sha256=entry['sha256']));artifacts={}
        for site,(backend,layer),seed in product(SITES,[('hidden',l) for l in MODELS[model][1]]+[('surface',-1)],SEEDS):
            name=f'{backend}_layer{layer}_site{site}_seed{seed}';artifacts[name]=dict(path=str(Path(cfg['run_dir'])/(name+'.npz')),sha256='c'*64,bytes=1234)
        old=dict(status='complete_exploratory',evaluation_role=cfg['evaluation_role'],config_hash=digest(cfg),fit_source=dict(snapshot_id=FIT_SNAPSHOT,source_sha256=FIT_SHA),capture_source=dict(snapshot_id=CAPTURE_SNAPSHOT),fit_banks=30,factorizations=30,parameter_replay_rows=172800,artifacts=artifacts)
        write(root/cfg['run_dir']/'completion_manifest_v1.json',old);write(root/cfg['run_dir']/'parameter_replay_review_v1.json',dict(status='passed',source_artifacts=artifacts))
        upstream[model]=old
    config=dict(evaluation_role=ROLE,readout_configs=readouts,declared_plan=plan,declared_plan_sha256=hashlib.sha256(plan_bytes).hexdigest(),run_dir=str(SUITE/'analysis'),report='reports/binding/identity_grammar_findings_v1.md')
    cfg_relative=Path('configs/binding/identity_grammar_review_v1.json');cfg_pin=write(frozen/cfg_relative,config)
    manifest=dict(snapshot_id='synthetic_grammar_fixture',code=dict(source_sha256='a'*64),config_files={str(cfg_relative):cfg_pin['sha256']})
    pin_manifest=write(frozen/'frozen_manifest.json',manifest);source=dict(snapshot=str(frozen),snapshot_id=manifest['snapshot_id'],source_sha256='a'*64,frozen_manifest_sha256=pin_manifest['sha256'])
    write(root/SUITE/'execution_source_v1.json',dict(snapshot=str(frozen),snapshot_id=source['snapshot_id'],code=source['source_sha256']))
    result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,protocol=producer.protocol(),fit_source_snapshot=FIT_SNAPSHOT,capture_source_snapshot=CAPTURE_SNAPSHOT,score_banks=60,saved_score_rows_checked=345600,development_rows_per_bank=1440,development_prediction_rows=86400,decoded_case_rule_method_rows=1382400,cells=[],input_pins=[],original_metrics_exact=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,activation_arrays_opened=False,coefficient_arrays_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
    artifacts={};body=json.dumps(raw,sort_keys=True,separators=(',',':')).encode()[1:]
    for model in MODELS:
        for site,(backend,layer),seed in product(SITES,[('hidden',l) for l in MODELS[model][1]]+[('surface',-1)],SEEDS):
            name=f'{backend}_layer{layer}_site{site}_seed{seed}';score=dict(path=str(SUITE/'analysis'/f'scores_{model}_{name}.npz'),sha256='d'*64,bytes=1234);original=upstream[model]['artifacts'][name]
            header=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,model=model,name=name,backend=backend,layer=layer,site=site,seed=seed,score_bank=score,original_score_bank=original,original_metrics_exact=True)
            path=out/f'diagnostics_{model}_{name}.json';payload=json.dumps(header,sort_keys=True,separators=(',',':')).encode()[:-1]+b','+body;publish(path,payload);diag=dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload))
            artifacts['scores_'+model+'_'+name]=score;artifacts['diagnostics_'+model+'_'+name]=diag
            result['cells'].append({k:header[k] for k in ('model','name','backend','layer','site','seed','score_bank','original_score_bank','original_metrics_exact')}|dict(diagnostic=diag,summary_methods=producer._cell_summary(raw)))
    summary=producer._summary(result)
    registration=dict(evaluation_role=ROLE,config_hash=digest(config),source=source,config=config,protocol=result['protocol'],new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)
    audit=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),score_banks=60,original_metrics_exact=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)
    for key,name,value in [('registration','registration.json',registration),('results','results_v1.json',result),('summary','summary.json',summary),('audit','audit.json',audit)]:artifacts[key]=write(out/name,value)
    report=b'Synthetic original runner report\n';publish(root/config['report'],report);artifacts['report']=dict(path=config['report'],sha256=hashlib.sha256(report).hexdigest(),bytes=len(report))
    common=dict(evaluation_role=ROLE,config_hash=digest(config),source=source,score_banks=60,saved_score_rows_checked=345600,development_prediction_rows=86400,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)
    write(out/'completion_manifest_v1.json',dict(common,status='complete_exploratory',artifacts=artifacts))
    write(out/'grammar_replay_review_v1.json',dict(common,status='passed',all_grammar_diagnostics_recomputed=True,all_original_metrics_recomputed=True,all_new_dev_score_banks_reopened=True,original_score_banks_reopened=False,source_artifacts=artifacts))
    return raw


def self_test():
    checks=0
    with tempfile.TemporaryDirectory(prefix='grammar-publication-synthetic-') as tmp:
        root=Path(tmp);raw=synthetic_workspace(root)
        # The actual runner generates this small source fixture; scaling changes only counts and repeated exact metadata rows.
        fake=dict(model='llama8b',name='hidden_layer24_site7_seed17',backend='hidden',layer=24,site=7,seed=17,diagnostic=dict(path='synthetic.json',sha256='f'*64,bytes=1))
        extracted=extract_diagnostic(dict(raw,original_metrics_exact=True),fake);require(len(extracted)==16,'Typed producer diagnostic schema failed');checks+=1
        require(raw['methods']['random_prefix_control']['rules']['joint_allow_self']['transitions']['free_joint']['combined_eight']['harmed']['correct']==1440,'Unlawful sham harm must be accepted');checks+=1
        for mutate in [lambda d:d['source_owner_counter']['whole']['combined_eight'].update(correct=0),lambda d:d['methods']['direct']['rules']['joint_allow_self'].update(lawful_cases=0),lambda d:d['methods']['direct']['rules']['joint_allow_self']['exact_objective_checks'].update(projection_penalty_nonnegative=False),lambda d:d['methods']['random_prefix_control']['rules']['joint_allow_self']['truth_lawfulness_ceiling'].update(correct=1440),lambda d:d['methods']['direct']['rules']['joint_allow_self']['transitions']['free_joint']['parent']['changed'].update(correct=1)]:
            bad=deepcopy(raw);mutate(bad)
            try:extract_diagnostic(dict(bad,original_metrics_exact=True),fake)
            except ValueError:checks+=1
            else:raise AssertionError('Invalid synthetic diagnostic accepted')
        first=publication(root);second=publication(root);require(first['status']=='published' and second['status']=='byte_identical_reproduction','Two complete publications must match bytes');checks+=1
        require(len(list(csv.DictReader((root/SUITE/'form_cells_v1.csv').open())))==960,'All960rule cells required');checks+=1
        require(not list(root.rglob('*.npz')) and not list(root.rglob('*.jsonl')),'No binary/source records may exist in publisher fixture');checks+=1
        require((root/'reports/binding/identity_grammar_findings_v1.md').read_bytes()==b'Synthetic original runner report\n','Original report was overwritten');checks+=1
        large=root/'large.json';publish(large,json_bytes(dict(padding='x'*(9*1024**2))))
        try:read_json(root,large)
        except ValueError:checks+=1
        else:raise AssertionError('Compact bound bypassed')
        require(len(read_json(root,large,limit=MAX_JSON)['padding'])==9*1024**2,'Rich diagnostic bound failed');checks+=1
        proof=root/SUITE/'analysis/grammar_replay_review_v1.json';value=json.loads(proof.read_text());value['all_grammar_diagnostics_recomputed']=False;proof.write_bytes(json_bytes(value))
        try:publication(root)
        except ValueError:checks+=1
        else:raise AssertionError('Incomplete grammar proof accepted')
    return dict(status='passed',synthetic_checks=checks,source_only_fixture_cases=15,actual_scientific_outcomes_opened=False,score_or_parameter_files_opened=False,temporary_workspace_removed=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args();print(json.dumps(self_test() if args.self_test else publication(workspace()),sort_keys=True))


if __name__=='__main__':main()
