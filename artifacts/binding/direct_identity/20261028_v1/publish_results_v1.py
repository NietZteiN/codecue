"""Publish both completed direct-identity studies from pinned JSON metadata only.

No source/prepared/response JSONL, NPZ, model or activation is opened.  The
parameter inventory is checked as receipt metadata; the independent replay
receipt proves the prior numerical audit.  --self-test uses temporary synthetic
metadata and never reads the ongoing scientific runs.
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

ROLE = "discovery_direct_identity_readouts_v1"
PUBLICATION_ROLE = "discovery_direct_identity_publication_v1"
SUITE = Path("artifacts/binding/direct_identity/20261028_v1")
MODEL_KEYS = ("llama8b", "codellama34b")
MODELS = {
    "llama8b": ("Llama 3.1 8B", "meta-llama/Llama-3.1-8B-Instruct",
                "0e9e39f249a16976918f6564b8830bc894c89659", (8, 16, 24, 31)),
    "codellama34b": ("CodeLlama 34B", "codellama/CodeLlama-34b-Instruct-hf",
                     "d4c1c474abcacd32d2a6eda45f9811d38c83e93d", (12, 24, 36, 47)),
}
FAMILIES = ("assignment_joint", "assignment_owner", "assignment_version", "parent_joint", "parent_owner", "parent_version")
LABELS = {"assignment_joint": "Write identity", "parent_joint": "Read-time parent identity"}
METHODS = ("direct", "training_prior", "random_prefix_control", "source_owner_version_prior")
SITES = (7, 8)
CAPTURE_SNAPSHOT = "345f75b01f5c3b33bd0ca6d8"
CAPTURE_SHA = "9cfa6c42fd79ddb9a4f049650ba311bb996dcb9f48afb9f9c31a2cc22254a918"
SEEDS = (17, 29, 43)
DATASET_SHA = "d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1"
MAX_JSON = 192 * 1024**2
INPUTS = {}
LIMITATIONS = [
    "Adaptive direct categorical decoding on consumed discovery structures; no independent replication or new interval.",
    "Global 16-class predictions use no per-case source/SSA map. Source oracles supply supervised targets and evaluation strata only.",
    "Owners are visible in SOURCE left/right variable names. The stronger syntax-owner plus weighted TRAIN version-prior comparator has explicit source access.",
    "The first write version is always 2 and first parent version always 1; these are sanity controls, not version-tracking evidence.",
    "Joint heads have 16 nominal outputs versus 8 component outputs. With identical linear-ridge X/weights/alpha/masks, component scores are marginal sums of the joint score table; these are not independent representations or a clean capacity test.",
    "Final-parent version 4 has only two TRAIN graph families per owner and one DEV family; the three-family support diagnostic fails and these classes remain scored.",
    "Prefix-sham joint/component labels are coherent within an event, but change class marginals and constant-version difficulty and need not form lawful multi-event graphs.",
    "Character features see the exact visible prefix; the full source determines all labels. A hidden advantage is specific to the tested decoders.",
    "Fifteen DEV families have 96 dependent relatives each; weighting seeds are dependent estimator variants. All fixed layers, heads and classes remain reported.",
    "Current/obsolete strata refer to underlying source definitions at capture. Parent identity truth uses pre-consumer read time, even if obsolete later.",
    "Site 3 has no visible copy targets and no fitted bank. Only sites 7/8 supply 60 actual banks across both checkpoints.",
    "No new model capture or generated-answer behavior is measured; failed gates, sealed outcomes, optional training and causal/predictive decisions remain unchanged.",
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


def validate_cell(cell):
    require(type(cell.get("n")) is int and 0 <= cell["n"] <= 1440 and cell.get("heads") == 4,
            "Whole-head denominators differ")
    require(_point(cell.get("accuracy")) and _point(cell.get("group_macro_accuracy")), "Invalid accuracy")
    groups = cell.get("per_group")
    require(isinstance(groups, dict), "Per-graph outcomes required")
    if not cell["n"]:
        require(not groups and cell["accuracy"] is None and cell["group_macro_accuracy"] is None,
                "Undefined whole-head tasks must retain null points")
        return
    require(cell["n"] == 1440 and len(groups) == 15, "All 15 DEV graph families required")
    require(all(type(v.get("n")) is int and v["n"] > 0 and _point(v.get("accuracy"))
                and v["accuracy"] is not None for v in groups.values()), "Invalid per-graph cells")
    require(sum(v["n"] for v in groups.values()) == cell["n"] and all(v["n"] == 96 for v in groups.values()), "Fifteen equal96-row DEV families required")
    require(math.isclose(cell["accuracy"], cell["group_macro_accuracy"], abs_tol=1e-12), "Whole-task row and equal-family means must agree")
    require(math.isclose(cell["accuracy"], sum(v["n"] * v["accuracy"] for v in groups.values()) / cell["n"], abs_tol=1e-12)
            and math.isclose(cell["group_macro_accuracy"], sum(v["accuracy"] for v in groups.values()) / 15, abs_tol=1e-12),
            "Row/group aggregation differs from saved graph cells")


def _mean(values):
    require(len(values) == 3, "All three declared weighting seeds required")
    return sum(values) / 3 if all(v is not None for v in values) else None


def _same_point(left, right):
    return left is None and right is None or (left is not None and right is not None
        and math.isclose(left, right, rel_tol=0, abs_tol=1e-14))


def validate_version_support(result):
    """Keep all domains, constants and the source-declared sparse parent class."""
    for site in ('7','8'):
        support=result['training_support'][site]
        require(support.get('eligibility_split')=='train' and support.get('structural_groups')==45
                and support.get('minimum_class_groups')==3 and support.get('absent_domain_choices_retained') is True
                and support.get('development_labels_used_for_eligibility') is False,'TRAIN support access differs')
        heads={h['head']:h for h in support['categorical_heads']}
        require(set(heads)=={f'{f}/{e}' for f in FAMILIES for e in range(4,8)},'All24support heads required')
        for name,head in heads.items():
            family,event=name.split('/');event=int(event)
            domain=list(range(16)) if family.endswith('_joint') else list(range(4)) if family.endswith('_owner') else [1,2,3,4]
            require(head['candidates']==domain and head.get('evaluated_choices_removed') is False,'Full class domains must remain')
            cells=head['classes'];require([c['candidate'] for c in cells]==domain,'Every support class required')
            require(sum(c['train_rows'] for c in cells)==4320 and sum(c['development_rows'] for c in cells)==1440,'Support counts differ')
            require(all(c['train_rows'] or not c['development_rows'] for c in cells),'Unexpected DEV-only identity class')
            if family=='parent_joint' and event==7:
                rare=[c for c in cells if c['candidate']%4==3]
                require(len(rare)==4 and all(c['train_groups']==2 and c['train_rows']==48 and c['development_groups']==1 and c['development_rows']==24 for c in rare),
                        'Sparse parent version4 classes must retain exact2TRAIN/1DEV support')
                require(head.get('eligible_categorical') is False and head.get('all_domain_classes_supported') is False,'Sparse source-target support must not pass')
            if family=='parent_version' and event==7:
                rare=next(c for c in cells if c['candidate']==4)
                require(rare['train_groups']==2 and rare['train_rows']==192 and rare['development_groups']==1 and rare['development_rows']==96,'Sparse scalar parent version4 missing')
            if event==4 and family.endswith('_version'):
                choice=2 if family.startswith('assignment') else 1
                require(all((c['train_rows']==4320 and c['development_rows']==1440) if c['candidate']==choice else c['train_rows']==c['development_rows']==0 for c in cells),
                        'First-event constant version sanity control differs')


def validate_binding(value):
    require(set(value['per_event'])=={f'{k}/event{e}' for k in ('assignment','parent') for e in range(4,8)},'All8event comparisons required')
    require(value['capacity']['direct_joint_outputs_per_event']==16
            and value['capacity']['separate_owner_plus_version_outputs_per_event']==8
            and value['capacity']['whole_pipelines_parameter_matched'] is False,'Joint/component capacity qualification missing')
    def rate(point,expected=None):
        n=point['n'];require(type(n) is int and 0<=n<=1440 and (expected is None or n==expected),'Comparison denominator differs')
        require(_point(point['accuracy']) and _point(point['group_macro_accuracy']),'Comparison rate differs')
        groups=point['per_group'];require(sum(g['n'] for g in groups.values())==n,'Comparison group counts differ')
        require(all(g['n']>0 and _point(g['accuracy']) and g['accuracy'] is not None for g in groups.values()),'Invalid comparison group')
        if n:
            require(_same_point(point['accuracy'],sum(g['n']*g['accuracy'] for g in groups.values())/n)
                    and _same_point(point['group_macro_accuracy'],sum(g['accuracy'] for g in groups.values())/len(groups)),'Comparison aggregation differs')
        else:require(point['accuracy'] is point['group_macro_accuracy'] is None and not groups,'Undefined comparison must stay null')
    for event in value['per_event'].values():
        if 'score_marginal_linearity' in event:
            linearity=event['score_marginal_linearity']
            require(linearity.get('n_complete')==1440 and all(isinstance(linearity.get(k),(int,float)) and not isinstance(linearity[k],bool) and math.isfinite(linearity[k]) and linearity[k]>=0 for k in ('max_abs_owner_difference','max_abs_version_difference')), 'Finite complete-row linearity diagnostics required')
        for field in ('joint','factorized','separate_owner','separate_version','joint_owner','joint_version','prediction_disagreement'):rate(event[field],1440)
        require(set(event['joint_classes'])=={str(i) for i in range(16)} and sum(c['n'] for c in event['joint_classes'].values())==1440,'All16joint comparison classes required')
        require(set(event['by_profile'])=={'2_1_1_0','3_1_0_0','2_2_0_0'},'All3profile strata required')
        for strata in (event['by_profile'],event['by_capture_status']):
            require(sum(p['joint']['n'] for p in strata.values())==1440,'Conditional strata denominator differs')
            for point in strata.values():
                for route in ('joint','factorized'):rate(point[route])
    for scope in value['whole_by_kind'].values():
        for route in ('joint','factorized'):rate(scope[route],1440)
    for route in ('joint','factorized'):
        rate(value['combined_eight'][route],1440)
        require(value['combined_eight'][route]['accuracy']<=min(p[route]['accuracy'] for p in value['whole_by_kind'].values())+1e-14,'Combined identity cannot exceed each four-event task')


def capture_accounting(root, config, expected_source):
    """Read completed capture metadata only; never inspect a feature chunk."""
    folder = resolve(root, config["run_dir"])
    receipt = read_json(root, folder / "completion_manifest_v1.json")
    require(receipt.get("status") == "complete_exploratory"
            and receipt.get("evaluation_role") == "discovery_diversity_capture_v1"
            and receipt.get("config_hash") == digest(config) and receipt.get("source") == expected_source
            and receipt.get("dataset_sha256") == DATASET_SHA and receipt.get("cases") == 5760,
            "Completed matching diversity capture receipt required")
    expected_shape = [5760, 3, 4, config["hidden_size"]]
    require(receipt.get("feature_shape") == expected_shape, "Capture feature geometry differs")
    names = {"registration.json", "preflight.json", "prepared_cases.jsonl", "manifest.json", "summary.json", "audit.json"}
    require(set(receipt.get("metadata", {})) == names, "Exact capture metadata inventory required")
    for name in names:
        require(resolve(root, receipt["metadata"][name]["path"]) == folder / name, "Capture metadata path differs")
    summary = read_json(root, folder / "summary.json", receipt["metadata"]["summary.json"])
    audit = read_json(root, folder / "audit.json", receipt["metadata"]["audit.json"])
    preflight = read_json(root, folder / "preflight.json", receipt["metadata"]["preflight.json"])
    boundary = "native" if config["hidden_size"] == 4096 else "codellama_official_boundary_v1"
    require(config["evaluation_role"] == "discovery_diversity_capture_v1"
            and preflight.get("status") == "passed" and preflight.get("cases") == 5760
            and preflight.get("config_hash") == digest(config) and preflight.get("source") == expected_source
            and preflight.get("new_model_queries") == 0
            and preflight["recipe"]["tokenization_mode"] == boundary
            and preflight["recipe"]["dtype"] == "bfloat16"
            and preflight["recipe"]["batch_size"] == config["batch_size"], "Prepared native/BF16/batch profile differs")
    require(preflight["source_review"]["source_rows"] == 5760
            and preflight["source_review"]["components"] == {"train": 45, "development": 15}
            and preflight["source_review"]["split_rows"] == {"train": 4320, "development": 1440}
            and preflight["source_review"]["dataset_manifest_sha256"] == config["dataset_manifest_sha256"],
            "Capture source cohort/manifest identity differs")
    require(summary.get("complete") is True and summary.get("cases") == 5760
            and summary.get("feature_shape") == expected_shape and summary.get("source") == expected_source
            and audit.get("status") == "passed" and audit.get("finite_float32_features") is True
            and audit.get("source_model_prefill_cases") == 5760 and audit.get("new_model_queries") == 0,
            "Completed finite capture and audit required")
    for value in (receipt, summary, audit):
        require(value.get("generated_responses") == value.get("generation_calls") == 0
                and value.get("generated_holdouts_opened") is False, "Capture unexpectedly generated responses")
    attempts = summary["collection_attempts"]
    attempted = sum(a["prefill_cases_attempted"] for a in attempts)
    calls = sum(a["prefill_batch_calls"] for a in attempts)
    require(attempts and attempts[-1]["status"] == "complete" and attempted >= 5760
            and all(0 <= a["prefill_cases_returned"] <= a["prefill_cases_attempted"] for a in attempts)
            and summary["model_prefill_cases"] == receipt["model_prefill_cases"] == 5760
            and summary["new_model_queries"] == receipt["new_model_queries"] == attempted
            and summary["prefill_batch_calls"] == receipt["prefill_batch_calls"] == calls,
            "Distinct and retry capture accounting differ")
    return dict(distinct_cases=5760, attempted_cases=attempted, retry_case_attempts=attempted - 5760,
                batch_calls=calls, generated_responses=0, generation_calls=0,
                capture_receipt=INPUTS[str((folder / "completion_manifest_v1.json").relative_to(root))],
                scope="Actual durable source-case prefill attempts; no generated-answer behavior.")


def extract_model(result,summary,model,config):
    require(result.get('protocol',{}).get('identity_codebook')=='4*owner+(version-1)' and result['protocol'].get('target_columns')==192 and result['protocol'].get('categorical_heads')==24, 'Fixed192-column global-codebook recipe required')
    expected=set(product(SITES,[('hidden',l) for l in MODELS[model][3]]+[('surface',-1)],SEEDS));observed=set();rows=[];supplement=[]
    require(result.get('model')==MODELS[model][1] and (result.get('cases'),result.get('training_rows'),result.get('development_rows'),result.get('training_groups'),result.get('development_groups'))==(5760,4320,1440,45,15),'Complete source cohort required')
    p=result.get('primary',{});require(p.get('layer')==24 and p.get('site')==7 and p.get('tasks')==list(FAMILIES),'Fixed primary tasks differ')
    require(summary.get('active_sites')==[7,8] and summary.get('capture_site_ids')==[3,7,8]
            and 'undefined' in summary.get('initial_site3','').lower(),'Captured site3 must be explicitly undefined and unfitted')
    for fit in result['fits']:
        key=(fit['site'],(fit['backend'],fit['layer']),fit['seed']);require(key in expected and key not in observed,'Duplicate/undeclared fit');observed.add(key)
        require(fit['name']==f"{fit['backend']}_layer{fit['layer']}_site{fit['site']}_seed{fit['seed']}" and fit.get('exact_parameter_score_replay') is True and fit.get('factorizations')==1,'Fit/replay identity differs')
        require(set(fit['metrics'])==set(METHODS),'All4comparator methods required')
        for method in METHODS:
            metrics=fit['metrics'][method];whole=metrics['whole_categorical_families'];require(set(whole)==set(FAMILIES),'All6families required')
            validate_binding(metrics['binding_comparisons'])
            comparisons=metrics['binding_comparisons']
            for kind,event in product(('assignment','parent'),range(4,8)):
                comparison=comparisons['per_event'][f'{kind}/event{event}']
                joint_head=metrics['categorical_heads'][f'{kind}_joint/{event}']
                require(_same_point(comparison['joint']['accuracy'],joint_head['accuracy']), 'Joint comparison differs from categorical head')
                for component in ('owner','version'):
                    head=metrics['categorical_heads'][f'{kind}_{component}/{event}']
                    require(_same_point(comparison['separate_'+component]['accuracy'],head['accuracy']), 'Component comparison differs from categorical head')
                require(set(joint_head['classes'])==set(comparison['joint_classes']), 'All joint comparison classes must remain')
                for candidate,cell in comparison['joint_classes'].items():
                    headcell=joint_head['classes'][candidate]
                    require(cell['n']==headcell['n'] and cell['joint_correct']==(round(headcell['n']*headcell['accuracy']) if headcell['n'] else 0),'Supplementary joint class counts differ')
                for strata in ('by_profile','by_capture_status'):
                    for route in ('joint','factorized'):
                        require(sum(point[route]['correct'] for point in comparison[strata].values())==comparison[route]['correct'],'Stratified correct counts differ')
                require(comparison['factorized']['accuracy']<=min(comparison['separate_owner']['accuracy'],comparison['separate_version']['accuracy'])+1e-14,'Composed identity exceeds component correctness')
                require(comparison['joint']['accuracy']<=min(comparison['joint_owner']['accuracy'],comparison['joint_version']['accuracy'])+1e-14,'Joint identity exceeds its own component correctness')
            for kind in ('assignment','parent'):
                require(_same_point(comparisons['whole_by_kind'][kind]['joint']['accuracy'],whole[kind+'_joint']['accuracy']), 'Whole comparison differs from four-event joint task')
            if method=='source_owner_version_prior':
                require(all(c['prediction_disagreement']['correct']==0 for c in comparisons['per_event'].values()), 'SOURCE-owner prior joint and factorized decisions must agree')
                for scope in list(comparisons['whole_by_kind'].values())+[comparisons['combined_eight']]:
                    require(scope['joint']['correct']==scope['factorized']['correct'] and _same_point(scope['joint']['accuracy'],scope['factorized']['accuracy']), 'Source-prior composed correctness differs')
            supplement.append(dict(name=fit['name'],backend=fit['backend'],layer=fit['layer'],site=fit['site'],seed=fit['seed'],method=method,binding_comparisons=metrics['binding_comparisons'],additional_metrics={k:v for k,v in metrics.items() if k not in ('binding_comparisons','categorical_heads','whole_categorical_families','boolean_families','boolean_cells')}))
            for family in FAMILIES:
                cell=whole[family];validate_cell(cell);require(cell['n']==1440,'Every active target must remain evaluated')
                heads={n:h for n,h in metrics['categorical_heads'].items() if h['family']==family}
                require(set(heads)=={f'{family}/{e}' for e in range(4,8)},'All4event heads required')
                domain={str(c) for c in (range(16) if family.endswith('_joint') else range(4) if family.endswith('_owner') else range(1,5))}
                for name,head in heads.items():
                    require(set(head['classes'])==domain and sum(c['n'] for c in head['classes'].values())==1440 and head['n']==1440,'Complete class counts required')
                    require(all(type(c['n']) is int and c['n']>=0 and _point(c['accuracy']) and (c['accuracy'] is None)==(c['n']==0) for c in head['classes'].values()),'Absent classes must remain null')
                    validate_cell(dict(head,heads=4))
                    require(_same_point(head['accuracy'],sum(c['n']*c['accuracy'] for c in head['classes'].values() if c['n'])/1440),'Head accuracy differs from classes')
                    require(type(head.get('missing_predictions')) is int and 0<=head['missing_predictions']<=1440,'Missing decisions must count')
                    if method=='source_owner_version_prior' and name in ('assignment_joint/4','parent_joint/4'):require(_same_point(head['accuracy'],1.),'Syntax-owner constant-version sanity baseline must be perfect')
                rows.append(dict(model=model,checkpoint=MODELS[model][1],backend=fit['backend'],layer=fit['layer'],site=fit['site'],seed=fit['seed'],method=method,family=family,heads=4,n=1440,accuracy=cell['accuracy'],group_macro_accuracy=cell['group_macro_accuracy'],graph_groups=15,per_group=cell['per_group'],categorical_heads=heads))
    require(observed==expected and len(rows)==720,'Complete30-bank/720cell model required')
    primary={}
    for backend in ('hidden','surface'):
        primary[backend]={}
        for method in METHODS:
            primary[backend][method]={}
            for family in FAMILIES:
                selected=[x for x in rows if x['site']==7 and x['backend']==backend and (backend=='surface' or x['layer']==24) and x['method']==method and x['family']==family]
                require({c['seed'] for c in selected}==set(SEEDS),'All3primary seeds required')
                point=dict(accuracy=_mean([c['accuracy'] for c in selected]),group_macro_accuracy=_mean([c['group_macro_accuracy'] for c in selected]),n_per_seed=1440,heads=4,seeds=list(SEEDS))
                for field in ('accuracy','group_macro_accuracy'):require(_same_point(point[field],summary['primary'][backend][method]['whole_families'][family][field]),'Primary family mean differs')
                primary[backend][method][family]=point
            for scope in ('assignment','parent','combined_eight'):
                for route in ('joint','factorized'):
                    selected=[s['binding_comparisons'] for s in supplement if s['site']==7 and s['backend']==backend and (backend=='surface' or s['layer']==24) and s['method']==method]
                    points=[s['combined_eight'][route] if scope=='combined_eight' else s['whole_by_kind'][scope][route] for s in selected]
                    for field in ('accuracy','group_macro_accuracy'):require(_same_point(_mean([s[field] for s in points]),summary['primary'][backend][method]['binding_comparisons'][scope][route][field]),'Primary joint/factorized summary differs')
    control=result['control_descriptive_metadata'];require(set(control)=={'7','8'},'Two active-site control inventories required');changes={}
    for site in SITES:
        changes[str(site)]={}
        require(set(control[str(site)])=={str(s) for s in SEEDS},'All3control seeds required')
        for seed in SEEDS:
            c=control[str(site)][str(seed)]
            require(c.get('control_kind')=='canonical_prefix_coherent_event_joint_identity_sham_v1' and c.get('control_seed')==seed and c.get('marginals_preserved') is False and c.get('lawful_joint_ssa_graph') is False,'Coherent but non-lawful sham declaration differs')
            real,sham=c['real_marginals'],c['control_marginals'];require(set(real)==set(sham)=={'train','development'},'Both split marginals required')
            require(all(len(real[s])==len(sham[s])==192 for s in real),'All192marginals required')
            changes[str(site)][str(seed)]=dict(description_sha256=digest(c),changed_column_marginals={s:sum(a!=b for a,b in zip(real[s],sham[s])) for s in real},marginals_preserved=False,lawful_joint_ssa_graph=False)
    validate_version_support(result)
    return dict(model=model,label=MODELS[model][0],checkpoint=MODELS[model][1],model_revision=MODELS[model][2],layers=list(MODELS[model][3]),primary_layer=24,primary_site=7,cases=5760,training_rows=4320,development_rows=1440,training_graph_groups=45,development_graph_groups=15,primary=primary,cells=rows,supplementary=supplement,primary_binding_comparisons={b:{m:summary['primary'][b][m]['binding_comparisons'] for m in METHODS} for b in ('hidden','surface')},control_marginal_differences=changes,training_support=result['training_support'],initial_site3=summary['initial_site3'])


def load_model(root, model):
    base = root / SUITE / model / "readouts"
    receipt = read_json(root, base / "completion_manifest_v1.json")
    require(receipt.get("status") == "complete_exploratory" and receipt.get("schema_version") == 1
            and receipt.get("evaluation_role") == ROLE and receipt.get("fit_banks") == 30
            and receipt.get("factorizations") == 30 and receipt.get("parameter_replay_rows") == 172800
            and receipt.get("new_model_queries") == 0 and receipt.get("generated_holdouts_opened") is False,
            "Completed matching30-bank readout receipt required")
    relative = Path("configs/binding/direct_identity_20261028_v1") / (model + "_readouts.json")
    config = source_profile(root, receipt["fit_source"], relative)
    require(config["evaluation_role"] == ROLE and config["primary_layer"] == 24
            and digest(config) == receipt["config_hash"] and resolve(root, config["run_dir"]) == base,
            "Prospectively frozen readout configuration differs")
    cap_relative = Path(config["capture_config"])
    capture = source_profile(root, receipt["capture_source"], cap_relative)
    capture_path = resolve(root, receipt["capture_source"]["snapshot"]) / cap_relative
    require(INPUTS[str(capture_path.relative_to(root))]["sha256"] == config["capture_config_sha256"]
            and capture["evaluation_role"] == "discovery_diversity_capture_v1"
            and capture["model"] == MODELS[model][1]
            and capture["model_revision"] == capture["tokenizer_revision"] == MODELS[model][2]
            and capture["hidden_size"] == (4096 if model == "llama8b" else 8192)
            and capture["layers"] == list(MODELS[model][3]) and capture["dataset_sha256"] == DATASET_SHA,
            "Pinned checkpoint/capture configuration differs")
    expected = {f"{backend}_layer{layer}_site{site}_seed{seed}": base / f"{backend}_layer{layer}_site{site}_seed{seed}.npz"
                for site, (backend, layer), seed in product(SITES,
                    [("hidden", layer) for layer in MODELS[model][3]] + [("surface", -1)], SEEDS)}
    expected.update(registration=base / "registration.json", results=base / "results_v1.json",
                    summary=base / "summary.json", audit=base / "audit.json", report=resolve(root, config["report"]))
    inventory = receipt.get("artifacts", {})
    require(set(inventory) == set(expected) and len(inventory) == 35, "Exact35-artifact inventory required")
    for name, path in expected.items():
        item = inventory[name]
        require(resolve(root, item["path"]) == path and checksum(item.get("sha256"))
                and type(item.get("bytes")) is int and 0 < item["bytes"] <= 512 * 1024**2,
                "Exact bounded parameter/metadata inventory required")
    metadata = {name: read_json(root, expected[name], inventory[name], limit=MAX_JSON if name == "results" else 8*1024**2)
                for name in ("registration", "results", "summary", "audit")}
    report_path = expected["report"]
    require(report_path.is_file() and report_path.suffix == ".md" and report_path.stat().st_size <= 8*1024**2,
            "Bounded completed report metadata required")
    report_entry = pin(root, report_path, report_path.read_bytes())
    require(report_entry["sha256"] == inventory["report"]["sha256"]
            and report_entry["bytes"] == inventory["report"]["bytes"], "Completed report SHA256 differs")
    replay = read_json(root, base / "parameter_replay_review_v1.json")
    require(replay.get("status") == "passed" and replay.get("evaluation_role") == ROLE
            and replay.get("config_hash") == receipt["config_hash"]
            and replay.get("fit_source") == receipt["fit_source"] and replay.get("capture_source") == receipt["capture_source"]
            and replay.get("fit_banks") == replay.get("factorizations") == 30
            and replay.get("parameter_replay_rows") == 172800 and replay.get("source_artifacts") == inventory
            and all(replay.get(k) is True for k in ("exact_saved_parameter_score_replays",
                "all_real_and_control_scores_replayed", "all_scientific_metrics_recomputed",
                "train_support_and_control_marginals_recomputed"))
            and replay.get("new_fits") == replay.get("new_model_queries") == 0
            and replay.get("generated_holdouts_opened") is False, "Independent complete numerical/metric replay audit required")
    registration, result, summary, audit = [metadata[name] for name in ("registration", "results", "summary", "audit")]
    require(registration.get("config") == config and registration.get("fit_source") == receipt["fit_source"]
            and registration.get("capture_source") == receipt["capture_source"]
            and registration.get("fixed_recipe") == result.get("protocol"), "Original registration differs")
    for name, value in metadata.items():
        require(value.get("evaluation_role") == ROLE and value.get("config_hash") == receipt["config_hash"]
                and value.get("new_model_queries") == 0 and value.get("generated_holdouts_opened") is False,
                "Discovery role/identity differs: " + name)
    require(result.get("status") == summary.get("status") == "complete_exploratory"
            and audit.get("status") == "passed" and audit.get("exact_parameter_score_replays") is True
            and result.get("fit_source") == receipt["fit_source"] and result.get("capture_source") == receipt["capture_source"]
            and result.get("dataset_sha256") == DATASET_SHA
            and result.get("fit_banks") == summary.get("fit_banks") == audit.get("fit_banks") == 30
            and result.get("factorizations") == summary.get("factorizations") == audit.get("factorizations") == 30
            and result.get("parameter_replay_rows") == summary.get("parameter_replay_rows") == audit.get("parameter_replay_rows") == 172800,
            "Completed result/summary/audit accounting differs")
    require(result["protocol"].get("sites") == list(SITES) and result["protocol"].get("seeds") == list(SEEDS)
            and result["protocol"].get("alpha") == 100.
            and result["protocol"].get("primary_train_class_group_minimum") == 3
            and result["protocol"].get("capture_site_ids") == [3,7,8]
            and result["protocol"].get("target_columns") == 192
            and result["protocol"].get("categorical_heads") == 24
            and result["protocol"].get("identity_codebook") == '4*owner+(version-1)',
            "Fixed source/site/seed/readout protocol differs")
    require(registration["dataset_sha256"] == DATASET_SHA
            and {fit["name"]: resolve(root, fit["artifact"]) for fit in result["fits"]}
            == {name: path for name, path in expected.items() if path.suffix == ".npz"},
            "Scientific parameter inventory differs from completion receipt")
    require(receipt["capture_source"]["snapshot_id"] == CAPTURE_SNAPSHOT
            and receipt["capture_source"]["source_sha256"] == CAPTURE_SHA,
            "Original immutable S3 capture source is required")
    plan = resolve(root, config["declared_plan"])
    require(plan.suffix == ".md" and plan.is_file() and plan.stat().st_size <= 8*1024**2,
            "Bounded declared plan required")
    require(pin(root,plan,plan.read_bytes())["sha256"] == config["declared_plan_sha256"], "Declared plan SHA differs")
    accounting = capture_accounting(root, capture, receipt["capture_source"])
    value = extract_model(result, summary, model, config)
    value["capture_accounting"] = accounting
    value.update(config_hash=receipt["config_hash"], fit_source=receipt["fit_source"],
                 capture_source=receipt["capture_source"], dataset_sha256=DATASET_SHA,
                 declared_plan_sha256=config["declared_plan_sha256"],
                 capture_config_sha256=config["capture_config_sha256"],
                 parameter_inventory={name: item for name, item in inventory.items() if name.endswith(tuple(str(s) for s in SEEDS))},
                 audited_result=inventory["results"], audited_summary=inventory["summary"],
                 completion_receipt=INPUTS[str((base / "completion_manifest_v1.json").relative_to(root))],
                 numerical_replay_receipt=INPUTS[str((base / "parameter_replay_review_v1.json").relative_to(root))])
    require(len(value["parameter_inventory"]) == 30, "All30 pinned parameter banks required")
    return value


def table_bytes(models):
    fields = ["model", "checkpoint", "backend", "layer", "site", "seed", "method", "family",
              "heads", "n", "accuracy", "group_macro_accuracy", "graph_groups", "per_group_json", "categorical_heads_json"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for model in MODEL_KEYS:
        for row in models[model]["cells"]:
            value = {k: row[k] for k in fields if k in row}
            for key in ("per_group", "categorical_heads"):
                value[key + "_json"] = json.dumps(row[key], sort_keys=True, separators=(",", ":"), allow_nan=False)
            writer.writerow(value)
    return stream.getvalue().encode()


def figure_bytes(models):
    import matplotlib
    matplotlib.use('Agg',force=True)
    matplotlib.rcParams.update({'svg.hashsalt':'direct_identity_v1','font.family':'DejaVu Sans','font.size':10})
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(11.8,7.5),sharey=True)
    for i,model in enumerate(MODEL_KEYS):
        item=models[model];layers=item['layers']
        for j,family in enumerate(('assignment_joint','parent_joint')):
            ax=axes[i,j]
            for method,label,color,marker in [('direct','Hidden / direct','#2463ad','o'),('random_prefix_control','Hidden / prefix sham','#c45426','s')]:
                ys=[100*_mean([r['group_macro_accuracy'] for r in item['cells'] if r['site']==7 and r['backend']=='hidden' and r['layer']==layer and r['method']==method and r['family']==family]) for layer in layers]
                ax.plot(layers,ys,label=label,color=color,marker=marker,lw=1.8,ms=5)
            for backend,method,label,color,style in [('surface','direct','Prefix text','#555555','--'),('hidden','training_prior','TRAIN prior','#333333',':'),('hidden','source_owner_version_prior','SOURCE owner + TRAIN version prior','#338354','-.')]:
                ax.axhline(100*item['primary'][backend][method][family]['group_macro_accuracy'],label=label,color=color,linestyle=style,lw=1.6)
            ax.axvline(24,color='#777777',alpha=.25,lw=1);ax.set_xticks(layers);ax.set_ylim(0,103);ax.set_yticks([0,20,40,60,80,100]);ax.grid(axis='y',alpha=.2)
            ax.spines[['top','right']].set_visible(False);ax.set_xlabel('Hidden layer (nominated 24)');ax.set_title(item['label']+' · '+LABELS[family],fontsize=10)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.53,.045),fontsize=9)
    fig.supylabel('DEV equal-family whole-four-event identity correct (%)',x=.015,fontsize=11)
    fig.suptitle('Direct owner/version identity decoding · site 7',y=.985,fontsize=14)
    fig.text(.53,.012,'Joint vs factorized: argmax of score table vs its marginal sums; 15 DEV families; three seeds; no CI.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.095,right=.99,bottom=.21,top=.90,wspace=.20,hspace=.38)
    png,svg=io.BytesIO(),io.BytesIO();fig.savefig(png,format='png',dpi=170,metadata={'Software':'CodeCue deterministic direct identity publisher'});fig.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue deterministic direct identity publisher'});plt.close(fig)
    return png.getvalue(),svg.getvalue(),matplotlib.__version__


def report_bytes(models):
    lines=['# Direct owner and version identity decoding','',
        'Both checkpoints completed all fixed CPU readouts and passed saved-parameter, scientific-metric and control-marginal replay audits. Joint predictions decode using the global owner/version codebook, without a per-program source map after prediction. These are adaptive accessibility measurements, not a causal binding mechanism.','',
        'The unchanged captures contain 5,760 source cases per model: 4,320 TRAIN rows in 45 families and 1,440 DEV rows in 15 families, each with 96 dependent relatives. No new model query, tokenizer load, response or capture was needed. Site 3 precedes every copy and has no defined event target; only sites 7/8 were fitted. Sixty actual banks and 345,600 parameter-row replays are retained.','',
        'The fixed primary is layer 24/site 7, averaging weighting seeds 17/29/43. Each whole task requires all four copy-event identities correct. The table retains row and equal-family estimates; equal family sizes make them agree, and both are checked.','',
        '| Model | Features/method | Write joint: row / equal-family | Parent joint: row / equal-family | All-eight joint | All-eight factorized |','|---|---|---:|---:|---:|---:|']
    def pct(p):return f'{100*p:.3f}%'
    for model in MODEL_KEYS:
        for backend in ('hidden','surface'):
            for method in METHODS:
                p=models[model]['primary'][backend][method];extra=models[model]['primary_binding_comparisons'][backend][method]['combined_eight']
                cells=[models[model]['label'],backend+' / '+method]
                cells += [' / '.join(pct(p[f][k]) for k in ('accuracy','group_macro_accuracy')) for f in ('assignment_joint','parent_joint')]
                cells += [pct(extra[r]['accuracy']) for r in ('joint','factorized')];lines.append('| '+' | '.join(cells)+' |')
    lines+=['','![All fixed layers](figures/direct_identity_v1.svg)','',
        'The four panels show all four hidden layers for direct and coherent prefix-sham tasks, exact-prefix character features, the TRAIN label prior and the stronger syntax-owner plus TRAIN conditional-version prior. The nominated layer is marked at 24. No interval or favorable layer selection is introduced.','',
        'The syntax-owner comparator parses SOURCE left/right names through the supplied slot convention and estimates version probabilities using weighted TRAIN labels only. It never obtains DEV versions from SSA or target fields. Explicit source syntax already exposes owner identities. Its first-write (version 2) and first-parent (version 1) joint heads are perfect sanity controls; high scores there do not demonstrate tracking.','',
        'Direct joint heads have 16 nominal outputs per event, versus 8 component outputs. Because all columns use identical linear-ridge features, weights, alpha and masks, owner/version scores are row/column sums of the joint score table, up to floating-point tolerance. Joint versus factorized argmax compares a table decision with decisions from those marginal sums; it does not compare independent representations or provide a clean capacity test. These ridge scores are not calibrated probabilities. The supplementary JSON preserves combined-eight, factorized, scalar linearity, per-event/class/profile/group and underlying-source capture-status diagnostics for all methods, wherever provided by the audited runner. Parent labels refer to the definition read before the consumer, even when obsolete at capture; status strata describe the underlying real source context, not a lawful random sham identity.','',
        'All 192 columns, 24 heads and declared classes remain evaluated. Observed write joint domains contain 4/8/12/12 classes across the four events, and parent domains contain 4/8/12/16. Last-parent version 4 has only two TRAIN graph families per owner and one DEV family (96 DEV rows total). It fails the unchanged three-family support diagnostic and is retained without a qualification claim.','',
        'The [CSV](../../artifacts/binding/direct_identity/20261028_v1/form_cells_v1.csv) retains all 1,440 feature/site/layer/seed/method/task cells and their full categorical class/group counts. [Comparison JSON](../../artifacts/binding/direct_identity/20261028_v1/comparison_v1.json) retains supplementary comparisons and source/support metadata. The [publication review](../../artifacts/binding/direct_identity/20261028_v1/publication_review_v1.json) pins inputs and outputs.','',
        *['- '+item for item in LIMITATIONS],'']
    return '\n'.join(lines).encode()


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


def publication(root):
    root = Path(root).resolve(); INPUTS.clear()
    for model in MODEL_KEYS:
        base = root / SUITE / model / "readouts"
        require((base / "completion_manifest_v1.json").is_file()
                and (base / "parameter_replay_review_v1.json").is_file(),
                "Both completed model receipts and independent replay audits are required")
    models = {model: load_model(root, model) for model in MODEL_KEYS}
    pointer = read_json(root, root / SUITE / "execution_source_v1.json")
    for model in MODEL_KEYS:
        for source in (models[model]["fit_source"],):
            require(pointer["snapshot_id"] == source["snapshot_id"]
                    and pointer["code"] == source["source_sha256"]
                    and resolve(root,pointer["snapshot"]) == resolve(root,source["snapshot"]), "Registered source pointer differs from actual completed study")
    require(models["llama8b"]["declared_plan_sha256"] == models["codellama34b"]["declared_plan_sha256"],
            "Both models must share the frozen prospective plan")
    script = Path(__file__).resolve()
    script_pin = dict(path=str(SUITE / script.name), sha256=hashlib.sha256(script.read_bytes()).hexdigest(), bytes=script.stat().st_size)
    table = table_bytes(models)
    png, svg, version = figure_bytes(models)
    png2, svg2, _ = figure_bytes(models)
    require((png, svg) == (png2, svg2), "Repeated figure rendering is not byte-identical")
    comparison = dict(status="complete_metadata_publication", evaluation_role=PUBLICATION_ROLE,
        model_count=2, models=models, table_rows=1440, primary_layer=24, primary_site=7,
        source_cases_per_model=5760, total_parameter_banks=60, parameter_banks_opened=0, component_score_linearity="Identical linear ridge design implies owner/version score columns equal sums of joint score columns; argmax decisions may differ.",
        parameter_replay_rows=345600, total_factorizations=60,
        distinct_capture_prefills=sum(v["capture_accounting"]["distinct_cases"] for v in models.values()),
        attempted_capture_prefills=sum(v["capture_accounting"]["attempted_cases"] for v in models.values()),
        inputs=sorted(INPUTS.values(), key=lambda item: item["path"]), publisher_script=script_pin,
        new_model_queries=0, new_fits=0, new_bootstraps=0, raw_activation_arrays_opened=False,
        source_or_response_records_opened=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    base = root / SUITE
    outputs = {base / "comparison_v1.json": json_bytes(comparison), base / "form_cells_v1.csv": table,
        root / "reports/binding/direct_identity_findings_v1.md": report_bytes(models),
        root / "reports/binding/figures/direct_identity_v1.png": png,
        root / "reports/binding/figures/direct_identity_v1.svg": svg}
    review = dict(status="passed", evaluation_role=PUBLICATION_ROLE, publisher_script=script_pin,
        input_pins=sorted(INPUTS.values(), key=lambda item: item["path"]),
        output_pins=[dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
                     for path, data in outputs.items()], plotting_version=version,
        checks=dict(both_completed_receipts_and_replay_audits_required=True,
            all60_parameter_inventory_pins_verified_as_metadata=True, no_parameter_banks_opened=True,
            all1440_task_cells_and_class_counts_preserved=True, site3_explicitly_undefined_without_fitting=True,
            primary_layer24_site7_three_seed_means_verified=True, row_and_graph_macro_tables_preserved=True, whole_task_row_graph_means_equal=True,
            rare_parent_version4_support_retained=True, source_owner_prior_joint_factorized_agreement_verified=True, linearity_qualification_retained=True, capture_attempts_and_zero_generation_verified=True,
            control_marginal_metadata_pinned=True, repeated_figure_render_byte_identical=True),
        reproduction="Every invocation regenerates and byte-checks all existing outputs.",
        new_model_queries=0, new_fits=0, new_bootstraps=0, generated_holdouts_opened=False)
    review_payload = json_bytes(review)
    require(len(review_payload) <= 8*1024**2, "Compact publication review exceeds8MiB")
    outputs[base / "publication_review_v1.json"] = review_payload
    existed = all(path.is_file() for path in outputs)
    for path, data in outputs.items():
        require(not path.is_symlink() and (not path.exists() or path.read_bytes() == data),
                "Immutable publication differs before any write: " + str(path))
    for path, data in outputs.items():
        publish(path, data)
    return dict(status="byte_identical_reproduction" if existed else "published", models=2, task_cells=1440,
                publication_review=str(SUITE / "publication_review_v1.json"))


def synthetic_result(model):
    """Full-size JSON-only schema fixture; no feature/parameter files exist."""
    def counts(family,event,n):
        kind=family.split('_')[0];versions=([2],[2,3],[2,3,4],[2,3,4])[event-4] if kind=='assignment' else ([1],[1,2],[1,2,3],[1,2,3,4])[event-4]
        joint={i:0 for i in range(16)}
        if kind=='parent' and event==7:
            rare=48 if n==4320 else 24
            for i in range(16):joint[i]=rare if i%4==3 else (n-4*rare)//12
        else:
            for owner,version in product(range(4),versions):joint[owner*4+version-1]=n//(4*len(versions))
        if family.endswith('_joint'):return joint
        if family.endswith('_owner'):return {o:sum(v for k,v in joint.items() if k//4==o) for o in range(4)}
        return {v:sum(c for k,c in joint.items() if k%4+1==v) for v in (1,2,3,4)}
    def rate(value=.5,groups=None):
        groups=list(range(15)) if groups is None else groups;per={f'graph{i}':dict(n=96,correct=int(96*value),accuracy=value) for i in groups};n=96*len(groups)
        return dict(n=n,correct=int(n*value),accuracy=value,group_macro_accuracy=value,per_group=per)
    support=dict(eligibility_split='train',structural_groups=45,minimum_class_groups=3,absent_domain_choices_retained=True,development_labels_used_for_eligibility=False,categorical_heads=[],columns=[],eligible_boolean_indices=[],eligibility_rule='Boolean: both classes in >=threshold TRAIN groups; categorical: >=2 observed TRAIN classes and every observed TRAIN class in >=threshold groups')
    for f,e in product(FAMILIES,range(4,8)):
        tr=counts(f,e,4320);dv=counts(f,e,1440);classes=[]
        for c,n in tr.items():
            rare=f in ('parent_joint','parent_version') and e==7 and (c%4==3 if f.endswith('_joint') else c==4)
            groups=(2 if rare else 45) if n else 0
            classes.append(dict(candidate=c,train_rows=n,train_groups=groups,development_rows=dv[c],development_groups=(1 if rare else 15) if dv[c] else 0,supported=groups>=3,absent_train=not n,development_only=not n and bool(dv[c])))
            support['columns'].append(dict(index=len(support['columns']),name=f'{f}/{e}/{c}',family=f,kind='categorical',defined_rows=4320,positive_rows=n,negative_rows=4320-n,positive_groups=groups,negative_groups=45 if n<4320 else 0,constant=n in (0,4320),missing=False,eligible_boolean=False))
        observed=[c for c in classes if c['train_rows']]
        support['categorical_heads'].append(dict(head=f'{f}/{e}',family=f,candidates=list(tr),evaluated_choices_removed=False,classes=classes,observed_train_classes=[c['candidate'] for c in observed],absent_train_classes=[c['candidate'] for c in classes if c['absent_train']],unsupported_observed_train_classes=[c['candidate'] for c in observed if not c['supported']],development_only_classes=[c['candidate'] for c in classes if c['development_only']],constant=len(observed)==1,missing=not observed,eligible_categorical=len(observed)>=2 and all(c['supported'] for c in observed),all_domain_classes_supported=all(c['supported'] for c in classes)))
    result=dict(status='complete_exploratory',evaluation_role=ROLE,model=MODELS[model][1],cases=5760,training_rows=4320,development_rows=1440,training_groups=45,development_groups=15,primary=dict(layer=24,site=7,tasks=list(FAMILIES)),protocol=dict(sites=[7,8],capture_site_ids=[3,7,8],seeds=list(SEEDS),alpha=100.,primary_train_class_group_minimum=3,target_columns=192,categorical_heads=24,identity_codebook='4*owner+(version-1)'),training_support={str(s):deepcopy(support) for s in SITES},control_descriptive_metadata={},fits=[],fit_banks=30,factorizations=30,parameter_replay_rows=172800,dataset_sha256=DATASET_SHA,new_model_queries=0,generated_holdouts_opened=False)
    for site in SITES:
        result['control_descriptive_metadata'][str(site)]={}
        for seed in SEEDS:
            real={};sham={}
            for split,n in [('train',4320),('development',1440)]:
                real[split]=[];sham[split]=[]
                for f,e in product(FAMILIES,range(4,8)):
                    cs=counts(f,e,n)
                    for c,positive in cs.items():
                        real[split].append(dict(index=len(real[split]),defined_rows=n,positive_rows=positive,negative_rows=n-positive))
                        p=n//len(cs);sham[split].append(dict(index=len(sham[split]),defined_rows=n,positive_rows=p,negative_rows=n-p))
            result['control_descriptive_metadata'][str(site)][str(seed)]=dict(control_kind='canonical_prefix_coherent_event_joint_identity_sham_v1',control_seed=seed,marginals_preserved=False,lawful_joint_ssa_graph=False,real_marginals=real,control_marginals=sham)
    for site,(backend,layer),seed in product(SITES,[('hidden',l) for l in MODELS[model][3]]+[('surface',-1)],SEEDS):
        ms={}
        for method in METHODS:
            heads={};whole={}
            for f,e in product(FAMILIES,range(4,8)):
                acc=1. if method=='source_owner_version_prior' and (e==4 or f.endswith('_owner')) else .5
                cs=counts(f,e,1440)
                heads[f'{f}/{e}']=dict(family=f,n=1440,accuracy=acc,group_macro_accuracy=acc,missing_predictions=0,classes={str(c):dict(n=n,accuracy=acc if n else None) for c,n in cs.items()},per_group=rate(acc)['per_group'])
            for f in FAMILIES:
                value=1. if method=='source_owner_version_prior' and f.endswith('_owner') else .5
                whole[f]=dict(rate(value),heads=4)
            comparisons=dict(per_event={},whole_by_kind={k:{r:rate() for r in ('joint','factorized')} for k in ('assignment','parent')},combined_eight={r:rate() for r in ('joint','factorized')},capacity=dict(direct_joint_outputs_per_event=16,separate_owner_plus_version_outputs_per_event=8,whole_pipelines_parameter_matched=False),capture_status_scope='Underlying REAL source event capture status; sham identity need not be lawful.',codebook='4*owner+version-1')
            for k,e in product(('assignment','parent'),range(4,8)):
                acc=1. if method=='source_owner_version_prior' and e==4 else .5;cs=counts(k+'_joint',e,1440)
                point={field:rate(acc) for field in ('joint','factorized','separate_owner','separate_version','joint_owner','joint_version','prediction_disagreement')}
                point['prediction_disagreement']=rate(0.)
                point['separate_owner']=rate(heads[f'{k}_owner/{e}']['accuracy'])
                point['separate_version']=rate(heads[f'{k}_version/{e}']['accuracy'])
                point['joint_owner']=rate(1. if method=='source_owner_version_prior' else acc)
                point.update(joint_classes={str(c):dict(n=n,joint_correct=int(n*acc),factorized_correct=int(n*acc)) for c,n in cs.items()},by_profile={p:{r:rate(acc,range(i*5,i*5+5)) for r in ('joint','factorized')} for i,p in enumerate(('2_1_1_0','2_2_0_0','3_1_0_0'))},by_capture_status={'current':{r:rate(acc) for r in ('joint','factorized')}})
                comparisons['per_event'][f'{k}/event{e}']=point
            ms[method]=dict(categorical_heads=heads,whole_categorical_families=whole,binding_comparisons=comparisons)
        result['fits'].append(dict(name=f'{backend}_layer{layer}_site{site}_seed{seed}',backend=backend,layer=layer,site=site,seed=seed,factorizations=1,exact_parameter_score_replay=True,metrics=ms))
    summary=dict(status='complete_exploratory',evaluation_role=ROLE,fit_banks=30,factorizations=30,parameter_replay_rows=172800,new_model_queries=0,generated_holdouts_opened=False,active_sites=[7,8],capture_site_ids=[3,7,8],initial_site3='All192targets undefined; no banks or fits.',primary={})
    for b in ('hidden','surface'):
        summary['primary'][b]={}
        fit=next(f for f in result['fits'] if f['backend']==b and f['site']==7 and (b=='surface' or f['layer']==24))
        for method in METHODS:
            whole=fit['metrics'][method]['whole_categorical_families'];comparisons=fit['metrics'][method]['binding_comparisons']
            summary['primary'][b][method]=dict(whole_families={f:{k:whole[f][k] for k in ('accuracy','group_macro_accuracy','n','heads')} for f in FAMILIES},binding_comparisons={scope:{route:{k:comparisons['combined_eight'][route][k] if scope=='combined_eight' else comparisons['whole_by_kind'][scope][route][k] for k in ('accuracy','group_macro_accuracy','n')} for route in ('joint','factorized')} for scope in ('assignment','parent','combined_eight')})
    return result,summary


def _synthetic_workspace(root):
    def write(path,value):
        payload=json_bytes(value);publish(path,payload);return dict(path=str(path.relative_to(root)),bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
    snapshots={};configs={}
    plan='reports/binding/direct_identity_plan_v1.md';plan_data=b'Synthetic declared plan\n';publish(root/plan,plan_data)
    plan_sha=hashlib.sha256(plan_data).hexdigest()
    for kind,snapshot_id,code in [('capture',CAPTURE_SNAPSHOT,CAPTURE_SHA),('fit','synthetic_direct_fit','a'*64)]:
        folder=root/'artifacts/snapshots'/kind;frozen_configs={};cfgs={}
        for model in MODEL_KEYS:
            cap_path=Path('configs/binding/diversity_decoding_20261028_v1')/(model+'_capture.json')
            cap=dict(model=MODELS[model][1],model_revision=MODELS[model][2],tokenizer_revision=MODELS[model][2],layers=list(MODELS[model][3]),dataset_sha256=DATASET_SHA,evaluation_role='discovery_diversity_capture_v1',hidden_size=4096 if model=='llama8b' else 8192,batch_size=256 if model=='llama8b' else 128,run_dir=str(Path('artifacts/binding/diversity_decoding/20261028_v1')/model/'capture'),dataset_manifest_sha256='e'*64)
            cfgs[model]=cap;frozen_configs[str(cap_path)]=write(folder/cap_path,cap)['sha256']
            if kind=='fit':
                relative=Path('configs/binding/direct_identity_20261028_v1')/(model+'_readouts.json')
                cfg=dict(evaluation_role=ROLE,primary_layer=24,capture_config=str(cap_path),capture_config_sha256=frozen_configs[str(cap_path)],declared_plan=plan,declared_plan_sha256=plan_sha,run_dir=str(SUITE/model/'readouts'),report=f'reports/binding/direct_identity_{model}_v1.md')
                configs[model]=cfg;frozen_configs[str(relative)]=write(folder/relative,cfg)['sha256']
        frozen=dict(snapshot_id=snapshot_id,code=dict(source_sha256=code),config_files=frozen_configs)
        p=write(folder/'frozen_manifest.json',frozen)
        snapshots[kind]=dict(snapshot=str(folder),snapshot_id=snapshot_id,source_sha256=code,frozen_manifest_sha256=p['sha256'])
    write(root/SUITE/'execution_source_v1.json',dict(snapshot=snapshots['fit']['snapshot'],snapshot_id=snapshots['fit']['snapshot_id'],code=snapshots['fit']['source_sha256']))
    for model in MODEL_KEYS:
        config=configs[model];cap=json.loads((Path(snapshots['capture']['snapshot'])/config['capture_config']).read_text());capfolder=root/cap['run_dir'];shape=[5760,3,4,cap['hidden_size']];calls=math.ceil(5760/cap['batch_size']);source=snapshots['capture']
        common=dict(source=source,feature_shape=shape,generated_responses=0,generation_calls=0,generated_holdouts_opened=False)
        capsummary=dict(common,complete=True,cases=5760,model_prefill_cases=5760,new_model_queries=5760,prefill_batch_calls=calls,collection_attempts=[dict(status='complete',prefill_cases_attempted=5760,prefill_cases_returned=5760,prefill_batch_calls=calls)])
        audit=dict(common,status='passed',finite_float32_features=True,source_model_prefill_cases=5760,new_model_queries=0)
        preflight=dict(status='passed',cases=5760,config_hash=digest(cap),source=source,new_model_queries=0,recipe=dict(tokenization_mode='native' if model=='llama8b' else 'codellama_official_boundary_v1',dtype='bfloat16',batch_size=cap['batch_size']),source_review=dict(source_rows=5760,components={'train':45,'development':15},split_rows={'train':4320,'development':1440},dataset_manifest_sha256=cap['dataset_manifest_sha256']))
        metadata={n:dict(path=str((capfolder/n).relative_to(root)),sha256='f'*64) for n in ('registration.json','preflight.json','prepared_cases.jsonl','manifest.json','summary.json','audit.json')}
        for name,value in [('summary.json',capsummary),('preflight.json',preflight),('audit.json',audit)]:metadata[name]=write(capfolder/name,value)
        write(capfolder/'completion_manifest_v1.json',dict(common,status='complete_exploratory',evaluation_role='discovery_diversity_capture_v1',config_hash=digest(cap),dataset_sha256=DATASET_SHA,cases=5760,model_prefill_cases=5760,new_model_queries=5760,prefill_batch_calls=calls,metadata=metadata))
        result,summary=synthetic_result(model);source=snapshots['fit'];base=root/config['run_dir'];artifacts={}
        for value in (result,summary):value.update(config_hash=digest(config),fit_source=source,capture_source=snapshots['capture'])
        for fit in result['fits']:
            path=base/(fit['name']+'.npz');fit['artifact']=str(path.relative_to(root));artifacts[fit['name']]=dict(path=fit['artifact'],sha256='c'*64,bytes=1234)
        registration=dict(evaluation_role=ROLE,config=config,config_hash=digest(config),fit_source=source,capture_source=snapshots['capture'],fixed_recipe=result['protocol'],dataset_sha256=DATASET_SHA,new_model_queries=0,generated_holdouts_opened=False)
        audit=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),fit_banks=30,factorizations=30,parameter_replay_rows=172800,exact_parameter_score_replays=True,new_model_queries=0,generated_holdouts_opened=False)
        for name,filename,value in [('registration','registration.json',registration),('results','results_v1.json',result),('summary','summary.json',summary),('audit','audit.json',audit)]:artifacts[name]=write(base/filename,value)
        report_data=b'Synthetic completed scientific report\n';publish(root/config['report'],report_data);artifacts['report']=dict(path=config['report'],bytes=len(report_data),sha256=hashlib.sha256(report_data).hexdigest())
        receipt=dict(schema_version=1,status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),fit_source=source,capture_source=snapshots['capture'],fit_banks=30,factorizations=30,parameter_replay_rows=172800,artifacts=artifacts,new_model_queries=0,generated_holdouts_opened=False);write(base/'completion_manifest_v1.json',receipt)
        proof=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),fit_source=source,capture_source=snapshots['capture'],fit_banks=30,factorizations=30,parameter_replay_rows=172800,source_artifacts=artifacts,exact_saved_parameter_score_replays=True,all_real_and_control_scores_replayed=True,all_scientific_metrics_recomputed=True,train_support_and_control_marginals_recomputed=True,new_fits=0,new_model_queries=0,generated_holdouts_opened=False);write(base/'parameter_replay_review_v1.json',proof)


def actual_support_contract_test():
    """Exercise the actual producer type on small synthetic labels, not study rows."""
    import sys
    sys.path.insert(0,str(workspace()/'src'))
    import numpy as np
    from codecue.binding import direct_identity_targets as target
    n=16;y=np.zeros((n,192));mask=np.ones_like(y,dtype=bool)
    for i in range(n):
        group=i//4;owner=i%4
        for head in target.HEADS:
            kind,component=head['family'].rsplit('_',1);event=head['event_statement']
            version=(2 if kind=='assignment' else 4 if event==7 and group in (0,1,3) else 1)
            candidate=4*owner+version-1 if component=='joint' else owner if component=='owner' else version
            y[i,head['indices'][head['candidates'].index(candidate)]]=1
    bundle=target.TargetBundle(y,mask,target.COLUMNS,tuple(f'synthetic{i}' for i in range(n)),tuple(f'g{i//4}' for i in range(n)),tuple('train' if i<12 else 'development' for i in range(n)),7,{'control':False})
    actual=target.training_support(bundle,min_class_groups=3)
    prototype=synthetic_result('llama8b')[0]['training_support']['7']
    require(set(actual)==set(prototype),'Synthetic source-support top-level schema differs from actual producer')
    require(set(actual['columns'][0])==set(prototype['columns'][0]),'Source-support column schema differs')
    for actual_head,synthetic_head in zip(actual['categorical_heads'],prototype['categorical_heads']):
        require(actual_head['head']==synthetic_head['head'] and set(actual_head)==set(synthetic_head),'Source-support categorical-head schema differs')
        require(all(set(c)==set(synthetic_head['classes'][0]) for c in actual_head['classes']),'Source-support class schema differs')
    rare=next(h for h in actual['categorical_heads'] if h['head']=='parent_joint/7')
    require(rare['eligible_categorical'] is False and rare['all_domain_classes_supported'] is False
            and 'all_observed_train_classes_supported' not in rare
            and all(next(c for c in rare['classes'] if c['candidate']==candidate)['train_groups']==2 for candidate in (3,7,11,15)),
            'Actual typed sparse-head producer contract differs')
    validate_version_support({'training_support':{'7':prototype,'8':deepcopy(prototype)}})
    return True


def self_test():
    require(actual_support_contract_test(), 'Actual typed support contract failed')
    checks=1
    for model in MODEL_KEYS:
        result,summary=synthetic_result(model);value=extract_model(result,summary,model,dict(primary_layer=24));require(len(value['cells'])==720,'Full synthetic model grid lost');checks+=1
        mutations=[lambda r:r['fits'].pop(),lambda r:r['fits'].append(deepcopy(r['fits'][0])),lambda r:r['primary'].update(layer=36),lambda r:r['fits'][0]['metrics']['direct']['categorical_heads']['assignment_joint/4']['classes'].pop('15'),lambda r:r['fits'][0]['metrics']['source_owner_version_prior']['categorical_heads']['parent_joint/4'].update(accuracy=.5),lambda r:r['training_support']['7']['categorical_heads'][-1]['classes'][-1].update(train_groups=3),lambda r:r['control_descriptive_metadata']['7']['17'].update(marginals_preserved=True),lambda r:r['fits'][0]['metrics']['direct']['whole_categorical_families']['parent_joint']['per_group']['graph0'].update(n=95),lambda r:r['fits'][0]['metrics']['direct']['binding_comparisons']['capacity'].update(whole_pipelines_parameter_matched=True),
            lambda r:r['fits'][0]['metrics']['source_owner_version_prior']['binding_comparisons']['per_event']['parent/event7']['prediction_disagreement'].update(correct=1),
            lambda r:r['protocol'].update(identity_codebook='per-case-oracle-map'),
            lambda r:r['fits'][0]['metrics']['direct']['binding_comparisons']['per_event']['assignment/event4'].update(score_marginal_linearity=dict(n_complete=0,max_abs_owner_difference=0.,max_abs_version_difference=0.))]
        for mutate in mutations:
            bad=deepcopy(result);mutate(bad)
            try:extract_model(bad,summary,model,dict(primary_layer=24))
            except ValueError:checks+=1
            else:raise AssertionError('Bad synthetic metadata accepted')
    with tempfile.TemporaryDirectory(prefix='direct-identity-publication-') as tmp:
        root=Path(tmp);_synthetic_workspace(root);first=publication(root);second=publication(root)
        require(first['status']=='published' and second['status']=='byte_identical_reproduction','Byte-identical publication failed');checks+=1
        table=list(csv.DictReader((root/SUITE/'form_cells_v1.csv').open()));require(len(table)==1440 and {r['site'] for r in table}=={'7','8'},'1440active CSV cells required');checks+=1
        require(not list(root.rglob('*.npz')) and not list(root.rglob('*.jsonl')),'Publisher fixture must have no arrays/source records');checks+=1
        comparison=json.loads((root/SUITE/'comparison_v1.json').read_text());require(comparison['models']['llama8b']['fit_source']!=comparison['models']['llama8b']['capture_source'],'New fit and old capture provenance conflated');checks+=1
        require(len(comparison['models']['llama8b']['supplementary'])==120,'Full4method×30bank supplementary metrics required');checks+=1
        large=root/'large.json';publish(large,json_bytes(dict(padding='x'*(9*1024**2))))
        try:read_json(root,large)
        except ValueError:checks+=1
        else:raise AssertionError('Compact JSON bound bypassed')
        require(len(read_json(root,large,limit=MAX_JSON)['padding'])==9*1024**2 and MAX_JSON==192*1024**2,'Rich bound failed');checks+=1
        path=root/SUITE/'llama8b/readouts/parameter_replay_review_v1.json';proof=json.loads(path.read_text());proof['all_scientific_metrics_recomputed']=False;path.write_bytes(json_bytes(proof))
        try:publication(root)
        except ValueError:checks+=1
        else:raise AssertionError('Failed audit accepted')
    return dict(status='passed',synthetic_checks=checks,actual_scientific_outcomes_opened=False,source_or_parameter_arrays_opened=False,temporary_workspace_removed=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    print(json.dumps(self_test() if args.self_test else publication(workspace()),sort_keys=True))


if __name__=='__main__':main()
