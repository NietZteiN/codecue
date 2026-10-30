"""Oracle-assisted interpretation of existing statement-ID predictions.

No file, score bank, model or fitting operation is available here. Source maps
supply owner/version identity; this is not a newly learned binding decoder.
Current heads use the capture checkpoint. A copy parent is interpreted at the
instant before its consumer executes, even when it becomes obsolete later.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product

import numpy as np

from . import schedule_targets as schema

HEADS = schema.HEADS
HEAD_ORDER = tuple(head["name"] for head in HEADS)
FAMILIES = ("current_definition", "current_version", "copy_parent")
CATEGORIES = ("exact", "same_owner_wrong_version", "different_owner_current",
              "different_owner_obsolete", "wrong_version", "missing",
              "invalid_candidate", "invalid_future", "undefined")
METRICS = ("exact", "owner_correct", "version_number_equal")
MAX_ROWS = 25_000
JOINTS = (
    ("scalar_correct", "definition_exact"),
    ("scalar_correct", "definition_owner_correct"),
    ("scalar_correct", "definition_version_equal"),
    ("scalar_correct", "scalar_definition_agree"),
)


def _integer(value):
    return isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_))


def _labels(values, n, name):
    if not isinstance(values, (list, tuple, np.ndarray)) or len(values) != n:
        raise ValueError(f"aligned {name} labels required")
    result = tuple(values)
    if any(not isinstance(value, str) or not value or len(value) > 256 for value in result):
        raise ValueError(f"bounded nonempty {name} labels required")
    return result


def _maps(bundle):
    n = len(bundle.case_ids)
    _labels(bundle.case_ids,n,"case IDs");_labels(bundle.group_ids,n,"graph groups")
    if (not 1 <= n <= MAX_ROWS or len(set(bundle.case_ids)) != n
            or tuple(bundle.columns) != schema.COLUMNS or bundle.site not in (3,7,8)
            or type(bundle.site) is not int or bundle.descriptive.get("control") is not False):
        raise ValueError("bounded real-task bundle with the fixed232-column schema required")
    if len(bundle.splits) != n or any(s not in ("train","development") for s in bundle.splits):
        raise ValueError("aligned discovery TRAIN/DEV splits required")
    y=np.asarray(bundle.y);mask=np.asarray(bundle.mask)
    if (y.shape != (n,232) or mask.shape != y.shape or mask.dtype != np.bool_
            or not np.isfinite(y).all() or np.any((y!=0)&(y!=1)) or np.any(y[~mask]!=0)):
        raise ValueError("finite one-hot/boolean targets and explicit future masks required")
    maps=bundle.descriptive.get("version_map_by_case")
    if not isinstance(maps,(list,tuple)) or len(maps)!=n:
        raise ValueError("aligned source-oracle visible SSA maps required")
    checkpoint=min(bundle.site,7);result=[]
    for entries in maps:
        if not isinstance(entries,(list,tuple)) or len(entries)!=checkpoint+1:
            raise ValueError("source map must contain exactly the visible assignment prefix")
        nodes={};ids=set()
        for entry in entries:
            if not isinstance(entry,dict) or any(not _integer(entry.get(k)) for k in ("statement","slot","version")):
                raise ValueError("strict integer statement/slot/version identities required")
            statement,slot,version=(int(entry[k]) for k in ("statement","slot","version"))
            if (statement in nodes or statement not in range(checkpoint+1) or slot not in range(4)
                    or version not in range(1,5) or entry.get("id")!=f"v{slot}@{version}"
                    or entry["id"] in ids or entry.get("status") not in ("current","obsolete")):
                raise ValueError("unique actual SSA statement/owner/version identities required")
            ids.add(entry["id"]);nodes[statement]=dict(statement=statement,slot=slot,version=version,
                                                       id=entry["id"],status=entry["status"])
        if set(nodes)!=set(range(checkpoint+1)) or {nodes[j]["slot"] for j in range(4)}!=set(range(4)):
            raise ValueError("complete visible four-root assignment map required")
        counts=Counter();latest={}
        for j in range(checkpoint+1):
            node=nodes[j];counts[node["slot"]]+=1;latest[node["slot"]]=j
            if node["version"]!=counts[node["slot"]]:
                raise ValueError("SSA versions must increase exactly once per owner assignment")
        for j,node in nodes.items():
            if node["status"]!=("current" if latest[node["slot"]]==j else "obsolete"):
                raise ValueError("capture-checkpoint source status disagrees with actual SSA order")
        result.append(nodes)
    return y,mask,result


def _frame(nodes, end):
    latest={}
    for j in range(end+1):
        latest[nodes[j]["slot"]]=j
    return latest


def _truth(bundle,y,mask,maps):
    n=len(maps);truth=np.full((n,12),-1,dtype=np.int64);valid=np.zeros((n,12),dtype=bool)
    checkpoint=min(bundle.site,7)
    direct={(c["source_node"],c["consumer_node"]):c["index"] for c in schema.COLUMNS if c["family"]=="direct"}
    for i,nodes in enumerate(maps):
        latest=_frame(nodes,checkpoint)
        for h,head in enumerate(HEADS):
            family=head["family"];slot_or_step=int(head["name"].split("/")[1]);indices=list(head["indices"])
            expected_mask=(np.asarray([c<=checkpoint for c in head["candidates"]]) if family=="current_definition"
                else np.asarray([checkpoint==7 or c==1 for c in head["candidates"]]) if family=="current_version"
                else np.asarray([4+slot_or_step<=checkpoint and c<4+slot_or_step for c in head["candidates"]]))
            if not np.array_equal(mask[i,indices],expected_mask):
                raise ValueError("categorical masks must preserve every visible static candidate")
            defined=bool(expected_mask.any());positives=np.flatnonzero(y[i,indices])
            if len(positives)!=(1 if defined else 0):
                raise ValueError("each defined categorical head must have exactly one true candidate")
            if not defined:
                continue
            choice=int(head["candidates"][int(positives[0])]);valid[i,h]=True;truth[i,h]=choice
            if family=="current_definition" and choice!=latest[slot_or_step]:
                raise ValueError("current-definition truth disagrees with the source checkpoint")
            if family=="current_version" and choice!=nodes[latest[slot_or_step]]["version"]:
                raise ValueError("scalar-version truth disagrees with the source checkpoint")
            if family=="copy_parent":
                consumer=4+slot_or_step;read_current=_frame(nodes,consumer-1)
                if choice>=consumer or read_current[nodes[choice]["slot"]]!=choice:
                    raise ValueError("parent truth must be its owner's latest definition at consumer read time")
                actual=[j for j in range(consumer) if y[i,direct[j,consumer]]==1]
                if actual!=[choice]:
                    raise ValueError("copy-parent truth and direct dependency target disagree")
    return truth,valid


def _predictions(value,truth,valid,case_ids):
    supplied=value if isinstance(value,dict) else None
    matrix=np.asarray(supplied.get("predicted") if supplied is not None else value,dtype=object)
    if matrix.shape!=truth.shape:
        raise ValueError("predictions must have rows×12 shape in the declared HEAD_ORDER")
    predictions=np.empty(truth.shape,dtype=np.int64)
    for index,item in np.ndenumerate(matrix):
        if item is None:
            predictions[index]=-1
        elif _integer(item) and -(2**63)<=int(item)<2**63:
            predictions[index]=int(item)
        else:
            raise ValueError("integer predictions or explicit None/-1 missing sentinel required")
    if supplied is not None:
        if "truth" in supplied and not np.array_equal(np.asarray(supplied["truth"]),truth):
            raise ValueError("supplied prediction truth differs from aligned target heads")
        if "valid" in supplied:
            actual=np.asarray(supplied["valid"])
            if actual.dtype!=np.bool_ or not np.array_equal(actual,valid):
                raise ValueError("supplied prediction validity differs from target visibility")
        if "correct" in supplied:
            actual=np.asarray(supplied["correct"])
            if actual.dtype!=np.bool_ or not np.array_equal(actual,valid&(truth==predictions)):
                raise ValueError("supplied original statement/scalar correctness differs")
        if "case_ids" in supplied and tuple(supplied["case_ids"])!=tuple(case_ids):
            raise ValueError("prediction case order differs from source maps")
    return predictions


def _stats(observations,categories=CATEGORIES):
    counts={name:0 for name in categories};metric_counts={name:0 for name in METRICS};denominators={name:0 for name in METRICS}
    defined=0;undefined=0;mappable=0;grouped=defaultdict(list)
    for row in observations:
        counts[row["category"]]+=1;grouped[row["group"]].append(row)
        if row["defined"]:defined+=1
        else:undefined+=1
        mappable+=bool(row.get("mappable",False))
        for name in METRICS:
            flag=row.get("metrics",{}).get(name)
            if flag is not None:
                denominators[name]+=1;metric_counts[name]+=bool(flag)
    def rate(c,n):return c/n if n else None
    result=dict(n_total=len(observations),n_defined=defined,n_undefined=undefined,
        n_prediction_mappable=mappable,counts=counts,
        rates={key:rate(value,defined) if key!="undefined" else None for key,value in counts.items()},
        metric_counts=metric_counts,metric_denominators=denominators,
        metric_rates={key:rate(metric_counts[key],denominators[key]) for key in METRICS})
    # One recursion level only: group rows are already inside a single group.
    groups={group:_group_stats(rows,categories) for group,rows in sorted(grouped.items())}
    result.update(per_graph=groups,n_graphs_total=len(groups),n_graphs_defined=sum(g["n_defined"]>0 for g in groups.values()),
        equal_graph_rates={key:_mean_defined([g["rates"][key] for g in groups.values()]) for key in counts},
        equal_graph_metric_rates={key:_mean_defined([g["metric_rates"][key] for g in groups.values()]) for key in METRICS})
    return result


def _mean_defined(values):
    defined=[value for value in values if value is not None]
    return sum(defined)/len(defined) if defined else None


def _group_stats(rows,categories):
    counts={key:sum(row["category"]==key for row in rows) for key in categories}
    n=sum(row["defined"] for row in rows)
    metric_denominators={key:sum(row.get("metrics",{}).get(key) is not None for row in rows) for key in METRICS}
    metric_counts={key:sum(row.get("metrics",{}).get(key) is True for row in rows) for key in METRICS}
    return dict(n_total=len(rows),n_defined=n,n_undefined=len(rows)-n,counts=counts,
        rates={key:counts[key]/n if n and key!="undefined" else None for key in counts},
        metric_counts=metric_counts,metric_denominators=metric_denominators,
        metric_rates={key:metric_counts[key]/metric_denominators[key] if metric_denominators[key] else None for key in METRICS})


def _observation(bundle,i,h,prediction,truth,defined,nodes,group,profile):
    head=HEADS[h];family=head["family"];slot_or_step=int(head["name"].split("/")[1])
    end=min(bundle.site,7) if family!="copy_parent" else 3+slot_or_step
    row=dict(case_id=bundle.case_ids[i],group=group,profile=profile,head=head["name"],family=family,
        slot=slot_or_step if family!="copy_parent" else None,copy_step=slot_or_step if family=="copy_parent" else None,
        reference_checkpoint=end,reference_frame="consumer_read_time" if family=="copy_parent" else "capture_checkpoint",
        defined=bool(defined),prediction=int(prediction),truth=int(truth) if defined else None,
        truth_owner=None,truth_version=None,predicted_owner=None,predicted_version=None,
        predicted_definition_status=None,mappable=False,metrics={name:None for name in METRICS})
    if not defined:
        row["category"]="undefined";return row
    if family=="current_version":
        row["truth_owner"]=slot_or_step;row["truth_version"]=int(truth)
        valid=prediction in (1,2,3,4)
        future=valid and min(bundle.site,7)==3 and prediction!=1
        category=("missing" if prediction==-1 else "invalid_candidate" if not valid
                  else "invalid_future" if future else "exact" if prediction==truth else "wrong_version")
        row.update(category=category,mappable=valid and not future,
            predicted_version=int(prediction) if valid and not future else None,
            metrics=dict(exact=category=="exact",owner_correct=None,version_number_equal=category=="exact"))
        return row
    target=nodes[int(truth)];row.update(truth_owner=target["slot"],truth_version=target["version"])
    if prediction==-1:category="missing"
    elif prediction not in range(8):category="invalid_candidate"
    elif prediction>end:category="invalid_future"
    else:
        predicted=nodes[int(prediction)];current=_frame(nodes,end)
        owner=predicted["slot"]==target["slot"];version=predicted["version"]==target["version"]
        status="current" if current[predicted["slot"]]==prediction else "obsolete"
        exact=owner and version
        if exact!=(prediction==truth):raise ValueError("mapped exact identity must equal original statement-class correctness")
        category=("exact" if exact else "same_owner_wrong_version" if owner else "different_owner_"+status)
        row.update(predicted_owner=predicted["slot"],predicted_version=predicted["version"],
            predicted_definition_status=status,mappable=True)
    row["category"]=category
    row["metrics"]=dict(exact=category=="exact",
        owner_correct=row["mappable"] and row["predicted_owner"]==row["truth_owner"],
        version_number_equal=row["mappable"] and row["predicted_version"]==row["truth_version"])
    return row


def diagnostics(bundle,predictions,*,groups=None,profiles=None,include_rows=False):
    """Return counts/rates over real-task truth and source-assisted identities.

    ``predictions`` is rows×12 in HEAD_ORDER, or an existing prediction-data dict
    with ``predicted`` and optional cross-checked truth/valid/correct/case_ids.
    ``None`` and -1 mean missing; floats are rejected. Groups may coarsen but
    cannot split an original graph family. Family rates pool four head decisions
    and are NOT whole-state AND accuracy. Invalid/missing defined targets count
    wrong. Unavailable scalar/definition agreement retains its own partition cell.
    """
    if type(include_rows) is not bool:raise ValueError("include_rows must be boolean")
    y,mask,maps=_maps(bundle);truth,valid=_truth(bundle,y,mask,maps)
    predicted=_predictions(predictions,truth,valid,bundle.case_ids);n=len(maps)
    groups=_labels(bundle.group_ids if groups is None else groups,n,"graph groups")
    profiles=_labels(["unspecified"]*n if profiles is None else profiles,n,"profiles")
    original_groups=defaultdict(set);splits=defaultdict(set)
    for old,new,split in zip(bundle.group_ids,groups,bundle.splits):
        original_groups[old].add(new);splits[new].add(split)
    if any(len(value)!=1 for value in (*original_groups.values(),*splits.values())):
        raise ValueError("graph groups cannot be split or cross discovery partitions")
    rows=[_observation(bundle,i,h,int(predicted[i,h]),int(truth[i,h]),bool(valid[i,h]),nodes,groups[i],profiles[i])
          for i,nodes in enumerate(maps) for h in range(12)]
    per_head={head:_stats([r for r in rows if r["head"]==head]) for head in HEAD_ORDER}
    per_family={family:_stats([r for r in rows if r["family"]==family]) for family in FAMILIES}
    by_profile={profile:dict(per_head={head:_stats([r for r in rows if r["profile"]==profile and r["head"]==head]) for head in HEAD_ORDER},
        per_family={family:_stats([r for r in rows if r["profile"]==profile and r["family"]==family]) for family in FAMILIES})
        for profile in sorted(set(profiles))}
    by_row={(i,head):rows[i*12+h] for i in range(n) for h,head in enumerate(HEAD_ORDER)}
    joint={}
    joint_categories=tuple(a+"__"+b for a,b in product(("true","false","undefined"),repeat=2))
    for slot in range(4):
        tables={}
        for left,right in JOINTS:
            observations=[]
            for i in range(n):
                definition=by_row[i,f"current_definition/{slot}"];scalar=by_row[i,f"current_version/{slot}"]
                defined=definition["defined"] and scalar["defined"]
                flags=dict(scalar_correct=scalar["metrics"]["exact"],definition_exact=definition["metrics"]["exact"],
                    definition_owner_correct=definition["metrics"]["owner_correct"],
                    definition_version_equal=definition["metrics"]["version_number_equal"],
                    scalar_definition_agree=(scalar["predicted_version"]==definition["predicted_version"])
                        if scalar["mappable"] and definition["mappable"] else None)
                label=lambda flag:"undefined" if flag is None else "true" if flag else "false"
                observations.append(dict(group=groups[i],defined=defined,category=label(flags[left])+"__"+label(flags[right])))
            tables[left+"__"+right]=_stats(observations,joint_categories)
        joint[str(slot)]=tables
    result=dict(schema_version=1,oracle_assisted=True,real_task_truth_only=True,
        interpretation="Source maps supply owner/version semantics for fixed statement-ID predictions; this is not a learned full binding decoder or causal mechanism.",
        head_order=list(HEAD_ORDER),categories=list(CATEGORIES),metrics=list(METRICS),site=bundle.site,
        row_count=n,graph_groups=len(set(groups)),profiles=sorted(set(profiles)),
        family_aggregation="Four head decisions pooled, not whole-family AND correctness; missing/invalid predictions are wrong on defined targets.",
        equality_semantics="Version-number equality can hold for different owners; exact identity requires both owner and version.",
        reference_frames=dict(current_definition="capture checkpoint",current_version="capture checkpoint",copy_parent="immediately before consumer executes"),
        agreement_semantics="Scalar/definition agreement can be jointly wrong; unavailable predictions retain undefined agreement cells.",
        per_head=per_head,per_family=per_family,by_profile=by_profile,scalar_definition_joint=joint)
    if include_rows:result["rows"]=rows
    return result
