"""Direct event identity targets and explicit source-syntax prior controls.

Joint predictions decode through a global 16-class codebook, never a per-case
SSA map. Generic SSA labels supply supervised truth and evaluation strata only.
The owner parser reads SOURCE identifiers without tracing versions; its stronger
syntactic access is kept separate from hidden/text probe inputs.
"""
from __future__ import annotations

import ast
from dataclasses import replace
import importlib.util
import sys

import numpy as np

from . import diversity_targets as diversity, schedule_targets as generic, relationships

ROLE = "discovery_direct_event_identity_targets_v1"
DATASET_ROLE = diversity.DATASET_ROLE
DATASET_SHA256 = diversity.DATASET_SHA256
MAX_ROWS = 5760
EVENTS = (4, 5, 6, 7)
OWNERS = (0, 1, 2, 3)
VERSION_CLASSES = (1, 2, 3, 4)
JOINT_CLASSES = tuple(range(16))
FAMILIES = ("assignment_joint", "assignment_owner", "assignment_version",
            "parent_joint", "parent_owner", "parent_version")
CONTROL_KIND = "canonical_prefix_coherent_event_joint_identity_sham_v1"


def _integer(value):
    return isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))


def encode_joint(owner, version):
    if not _integer(owner) or not _integer(version) or owner not in OWNERS or version not in VERSION_CLASSES:
        raise ValueError("joint identity requires owner0..3 and version1..4")
    return 4*int(owner)+int(version)-1


def decode_joint(candidate):
    """Decode solely through the fixed codebook; no bundle/source argument."""
    if not _integer(candidate) or candidate not in JOINT_CLASSES:
        raise ValueError("joint candidate must be an integer0..15")
    return int(candidate)//4, int(candidate)%4+1


def _schema():
    columns=[];heads=[]
    for family in FAMILIES:
        kind=family.rsplit("_",1)[1]
        candidates=JOINT_CLASSES if kind=="joint" else OWNERS if kind=="owner" else VERSION_CLASSES
        for event in EVENTS:
            name=f"{family}/{event}";indices=[]
            for class_index,candidate in enumerate(candidates):
                column=dict(index=len(columns),name=f"{name}/{candidate}",kind="categorical",
                    family=family,head=name,candidate=candidate,class_index=class_index,
                    event_statement=event,event_index=event-4)
                if kind=="joint":column.update(owner=candidate//4,version=candidate%4+1)
                indices.append(len(columns));columns.append(column)
            heads.append(dict(name=name,family=family,candidates=tuple(candidates),indices=tuple(indices),
                              event_statement=event,event_index=event-4))
    return tuple(columns),tuple(heads)


COLUMNS,HEADS = _schema()
N_COLUMNS = len(COLUMNS)
HEAD_ORDER = tuple(head["name"] for head in HEADS)
_HEAD = {head["name"]:head for head in HEADS}


def _isolated_schema_helpers():
    name=__package__+"._direct_identity_schema_helpers"
    spec=importlib.util.spec_from_file_location(name,generic.__file__)
    if spec is None or spec.loader is None:raise ValueError("generic schema helpers unavailable")
    engine=importlib.util.module_from_spec(spec);previous=sys.modules.get(name);sys.modules[name]=engine
    try:spec.loader.exec_module(engine)
    except BaseException:
        if previous is None:sys.modules.pop(name,None)
        else:sys.modules[name]=previous
        raise
    engine.COLUMNS=COLUMNS;engine.HEADS=HEADS;engine.N_COLUMNS=N_COLUMNS;engine.MAX_ROWS=MAX_ROWS
    return engine


_CORE = _isolated_schema_helpers()
TargetBundle = _CORE.TargetBundle
SITES = _CORE.SITES
SITE_NAMES = _CORE.SITE_NAMES
_readonly = _CORE._readonly


def syntax_owners(rows, site):
    """Parse visible copy LHS/RHS names through supplied slots, with no SSA.

    Input source identities are validated separately by targets(). This parser
    neither evaluates arithmetic nor counts assignments/versions, reads target
    fields, or calls the relationship oracle. A future event returns -1.
    """
    site=_CORE._site(site);checkpoint=min(site,7)
    if not isinstance(rows,(list,tuple)) or not 1<=len(rows)<=MAX_ROWS:
        raise ValueError("bounded nonempty source records required")
    result=[]
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("source"),str):
            raise ValueError("actual SOURCE text required by owner parser")
        slots=row.get("variable_slots");mapping=row.get("rename_map")
        if (slots!={f"v{i}":i for i in OWNERS} or not isinstance(mapping,dict)
                or set(mapping)!=set(slots) or len(set(mapping.values()))!=4
                or any(type(v) is not int for v in slots.values())):
            raise ValueError("bijective source-name/canonical-slot convention required")
        reverse={mapping[name]:slot for name,slot in slots.items()}
        tree=ast.parse(row["source"])
        if len(tree.body)!=9:raise ValueError("eight assignments plus query required")
        owners=dict(assignment=[-1]*4,parent=[-1]*4)
        for event in EVENTS:
            if event>checkpoint:continue
            statement=tree.body[event]
            if (not isinstance(statement,ast.Assign) or len(statement.targets)!=1
                    or not isinstance(statement.targets[0],ast.Name) or not isinstance(statement.value,ast.Name)
                    or statement.targets[0].id not in reverse or statement.value.id not in reverse):
                raise ValueError("visible copies must contain known SOURCE left/right variable names")
            owners["assignment"][event-4]=reverse[statement.targets[0].id]
            owners["parent"][event-4]=reverse[statement.value.id]
        result.append(owners)
    return result


def _set_event(y,row,kind,event,owner,version):
    for component,candidate in (("joint",encode_joint(owner,version)),("owner",owner),("version",version)):
        head=_HEAD[f"{kind}_{component}/{event}"]
        y[row,head["indices"][head["candidates"].index(candidate)]]=1


def targets(rows,site):
    """Build 192 labels after strict published-diversity record validation."""
    site=_CORE._site(site);checkpoint=min(site,7);records=diversity._records(rows)
    n=len(records);y=np.zeros((n,N_COLUMNS));mask=np.zeros_like(y,dtype=bool)
    parsed=syntax_owners(rows,site);prefixes=[];outputs=[];statuses=[];truth_statements=[]
    for i,(row,tree,surface_slots) in enumerate(records):
        graph=relationships.labels_at(row["canonical_source"],checkpoint,{f"v{k}":k for k in OWNERS})
        if graph!=relationships.labels_at(row["source"],checkpoint,surface_slots):
            raise ValueError("actual canonical/surface SSA labels differ")
        nodes={node["id"]:node for node in graph["version_nodes"]}
        by_statement={node["statement"]:node for node in nodes.values()}
        direct={child:parent for parent,child in graph["direct_def_use_edges"]}
        status=dict(assignment=[None]*4,parent=[None]*4)
        statement_ids=dict(assignment=[-1]*4,parent=[-1]*4)
        for event in EVENTS:
            if event>checkpoint:continue
            assignment=by_statement[event]
            if assignment["id"] not in direct:raise ValueError("each visible copy needs one actual read-time parent")
            parent=nodes[direct[assignment["id"]]]
            current_at_read={}
            for j in range(event):current_at_read[by_statement[j]["slot"]]=j
            if parent["statement"]!=current_at_read[parent["slot"]]:
                raise ValueError("parent identity must refer to its current definition at consumer read time")
            for kind,node in (("assignment",assignment),("parent",parent)):
                if node["slot"]!=parsed[i][kind][event-4]:
                    raise ValueError("SOURCE-only owner parser and supervised oracle disagree")
                _set_event(y,i,kind,event,node["slot"],node["version"])
                status[kind][event-4]=node["status"];statement_ids[kind][event-4]=node["statement"]
            for head in HEADS:
                if head["event_statement"]==event:mask[i,list(head["indices"])]=True
        statuses.append(status);truth_statements.append(statement_ids)
        prefixes.append(_CORE._prefix_key(tree,checkpoint))
        outputs.append(_CORE._prefix_key(tree,checkpoint,output=site==8))
    descriptive=dict(schema_version=1,target_role=ROLE,control=False,targets_only=True,
        prediction_codebook="4*owner_slot+(version-1); decode globally without any per-case source map",
        owner_classes=list(OWNERS),version_classes=list(VERSION_CLASSES),joint_classes=list(JOINT_CLASSES),
        categorical_heads=[dict(head) for head in HEADS],all_declared_choices_retained=True,
        visible_events_retain_absent_and_impossible_candidates=True,future_events_undefined=True,
        profile_ids=[row["profile_id"] for row,_,_ in records],syntax_owners=parsed,
        syntax_owners_are_source_only_baseline_inputs=True,
        event_capture_status=statuses,event_truth_statements=truth_statements,
        event_status_and_statement_fields_are_evaluation_targets_only=True,
        canonical_visible_prefixes=prefixes,canonical_output_visible_prefixes=outputs,
        no_per_case_oracle_map_used_to_decode_predictions=True,
        source_owner_version_prior="Parsed SOURCE owner plus weighted TRAIN P(version|event,owner); unconditional TRAIN fallback if owner unseen")
    return TargetBundle(_readonly(y),_readonly(mask),COLUMNS,
        tuple(r["id"] for r,_,_ in records),tuple(r["component_id"] for r,_,_ in records),
        tuple(r["split"] for r,_,_ in records),site,descriptive)


def subset(bundle,indices):
    values=np.asarray(indices)
    if values.dtype.kind=="b" and values.shape==(len(bundle.case_ids),):values=np.flatnonzero(values)
    if (values.ndim!=1 or values.dtype.kind not in "iu" or not len(values)
            or np.any(values<0) or np.any(values>=len(bundle.case_ids)) or len(set(values.tolist()))!=len(values)):
        raise ValueError("unique bounded nonempty row indices required")
    values=values.astype(np.int64);desc=dict(bundle.descriptive)
    for key in ("profile_ids","syntax_owners","event_capture_status","event_truth_statements",
                "canonical_visible_prefixes","canonical_output_visible_prefixes"):
        desc[key]=[bundle.descriptive[key][i] for i in values]
    return replace(bundle,y=_readonly(bundle.y[values]),mask=_readonly(bundle.mask[values]),
        case_ids=tuple(bundle.case_ids[i] for i in values),group_ids=tuple(bundle.group_ids[i] for i in values),
        splits=tuple(bundle.splits[i] for i in values),descriptive=desc)


def training_support(bundle,min_class_groups=3):
    """Retain every class; eligibility depends only on observed TRAIN support."""
    return _CORE.training_support(bundle,min_class_groups)


def control_targets(rows,site,seed):
    """Draw one prefix-keyed joint class per event, then derive its components."""
    if type(seed) is not int or not 0<=seed<2**63:raise ValueError("bounded nonnegative control seed required")
    real=targets(rows,site);y=np.zeros_like(real.y)
    for i,prefix in enumerate(real.descriptive["canonical_visible_prefixes"]):
        if real.site==3:continue
        for kind in ("assignment","parent"):
            for event in EVENTS:
                candidate=_CORE._draw(seed,prefix,f"{CONTROL_KIND}/{kind}/{event}",16)
                owner,version=decode_joint(candidate);_set_event(y,i,kind,event,owner,version)
    desc=dict(real.descriptive)
    desc.update(control=True,control_kind=CONTROL_KIND,control_seed=seed,
        joint_components_coherent_within_event=True,lawful_joint_ssa_graph=False,marginals_preserved=False,
        canonical_prefix_ties_lexical_and_prequery_variants=True,query_not_used_in_control_draw=True,
        group_split_site_not_in_random_key=True,control_class_support_may_differ=True,
        control_semantics="One keyed16-class joint identity per event; owner/version follow the fixed codebook; unrelated events need not form lawful SSA")
    result=replace(real,y=_readonly(y),descriptive=desc)
    desc["real_marginals"]=_CORE._marginals(real);desc["control_marginals"]=_CORE._marginals(result)
    desc["marginals_scope"]=dict(case_count=len(real.case_ids),population="complete input bank before any subset")
    return result


def syntax_owner_version_prior(bundle,train,weights):
    """Return SOURCE-owner + weighted TRAIN conditional-version prior scores.

    DEV labels and source SSA/evaluation-status metadata are never inspected.
    This is a stronger source-syntax comparator, not a hidden-state model.
    The return uses global joint/owner/version choices, including all zeros for
    impossible classes. Site3 remains entirely NaN because every head is future.
    """
    n=len(bundle.case_ids);train=np.asarray(train);weights=np.asarray(weights,dtype=np.float64)
    if (bundle.descriptive.get("control") is not False or tuple(bundle.columns)!=COLUMNS
            or train.shape!=(n,) or train.dtype!=np.bool_ or not train.any()
            or weights.shape!=(int(train.sum()),) or not np.isfinite(weights).all() or np.any(weights<=0)
            or np.asarray(bundle.y).shape!=(n,N_COLUMNS) or np.asarray(bundle.mask).shape!=(n,N_COLUMNS)):
        raise ValueError("real bundle, aligned TRAIN mask and positive TRAIN-only weights required")
    if any(bundle.splits[i]!="train" for i in np.flatnonzero(train)):
        raise ValueError("version priors cannot use DEV rows as TRAIN")
    owners=bundle.descriptive.get("syntax_owners")
    if not isinstance(owners,(list,tuple)) or len(owners)!=n:
        raise ValueError("separately parsed SOURCE owner metadata required")
    scores=np.full((n,N_COLUMNS),np.nan)
    if bundle.site==3:return _readonly(scores)
    if bundle.site not in (7,8):raise ValueError("declared direct-identity site required")
    train_indices=np.flatnonzero(train)
    for kind in ("assignment","parent"):
        for event in EVENTS:
            event_owners=[]
            for item in owners:
                values=item.get(kind) if isinstance(item,dict) else None
                if not isinstance(values,(list,tuple)) or len(values)!=4 or any(not _integer(v) or v not in OWNERS for v in values):
                    raise ValueError("visible SOURCE owner slots must be integers0..3")
                event_owners.append(int(values[event-4]))
            event_owners=np.asarray(event_owners,dtype=np.int64)
            version_head=_HEAD[f"{kind}_version/{event}"];indices=list(version_head["indices"])
            # Advanced indexing reads only TRAIN labels; DEV y can be replaced
            # without affecting any baseline prediction.
            labels=np.asarray(bundle.y)[train_indices][:,indices]
            mask=np.asarray(bundle.mask)[train_indices][:,indices]
            if (not mask.all() or not np.isfinite(labels).all() or np.any((labels!=0)&(labels!=1))
                    or not np.all(labels.sum(1)==1)):
                raise ValueError("defined one-hot TRAIN version labels required")
            unconditional=np.sum(weights[:,None]*labels,axis=0)/weights.sum()
            probabilities=[]
            for owner in OWNERS:
                selected=event_owners[train_indices]==owner
                probabilities.append(np.sum(weights[selected,None]*labels[selected],axis=0)/weights[selected].sum()
                                     if selected.any() else unconditional)
            owner_head=_HEAD[f"{kind}_owner/{event}"];joint_head=_HEAD[f"{kind}_joint/{event}"]
            for i,owner in enumerate(event_owners):
                scores[i,list(owner_head["indices"])]=np.eye(4)[owner]
                scores[i,indices]=probabilities[owner]
                joint=np.zeros(16);joint[owner*4:owner*4+4]=probabilities[owner]
                scores[i,list(joint_head["indices"])]=joint
    return _readonly(scores)
