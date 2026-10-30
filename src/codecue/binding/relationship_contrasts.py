"""Post-hoc matched provenance controls from source and in-memory predictions.

The existing copy-routing bank contains programs with identical numeric states
at every checkpoint but different first-copy parents. This module prepares those
pairs and scores already decoded parent choices. It opens no files, loads no
model or saved arrays, and fits nothing. Oracle states validate the pairing only;
they must never become readout features. Sites 7/8 observe the whole graph. At
site 3 the differing first copy is future information and is not scoreable here.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from numbers import Integral

from .datasets import digest
from .forecasting import _discovery_declaration
from .interpreter import execute
from .relationship_targets import _records

ROLE = 'posthoc_discovery_relationship_provenance_contrasts_v1'
SITES = (7, 8)
METRICS = (
    'first_parent_correct_fraction', 'both_first_parents_correct',
    'first_parent_predictions_differ', 'first_parent_predictions_collapse',
    'first_parents_swapped', 'whole_graph_correct_fraction',
    'both_whole_graphs_correct', 'whole_graph_predictions_differ',
    'whole_graph_predictions_collapse',
)
LIMITATIONS = (
    'Post-hoc descriptive discovery controls, not an independent replication or '
    'a new preregistered primary. The paired programs have equal numeric states '
    'and differ in one visible first-copy source. Their surface text therefore '
    'differs: success can reflect access to that copy source under the known '
    'fixed scaffold. Distinct predictions alone do not establish correct graph '
    'recovery. Lexical/numeric relatives, weighting seeds and paired rows are '
    'not independent replications; structural components are uncertainty units. '
    'These scores do not establish a dedicated relation code, general version '
    'resolution, natural causal use or arithmetic execution.'
)


def _parents(tree, slots):
    return tuple(slots[statement.value.id] for statement in tree.body[4:8])


def _states(tree, slots):
    # Execute assignments only. The actual output expression is not evaluated.
    prefix = ast.Module(body=[*tree.body[:-1], ast.Expr(value=ast.Constant(value=0))], type_ignores=[])
    trace = execute(ast.unparse(ast.fix_missing_locations(prefix)))['execution_trace']
    names = {slot: name for name, slot in slots.items()}
    return tuple(tuple(point['values'].get(names[slot]) for slot in range(4)) for point in trace)


def _surface_context(source):
    """Retain exact bytes outside the one permissible copy-source identifier."""
    expr = ast.parse(source).body[4].value
    lines = source.encode('utf-8').splitlines(keepends=True)
    start = sum(map(len, lines[:expr.lineno-1])) + expr.col_offset
    end = sum(map(len, lines[:expr.end_lineno-1])) + expr.end_col_offset
    data = source.encode('utf-8')
    return digest([data[:start].decode('utf-8'), data[end:].decode('utf-8')])


def build_pairs(records):
    """Validate the complete three-parent groups and return equal-state pairs.

    ``records`` uses the same source-only fields as the capture's case records.
    Response, expected-answer, stratum and stored oracle fields are never read.
    Pair orientation is fixed: left first-parent v1, right first-parent v2.
    """
    if isinstance(records, (list, tuple)):
        for row in records: _discovery_declaration(row)
    parsed = _records(records)
    groups = defaultdict(dict); bases = {}; identities = []
    for index, (row, tree, slots, _, case, component) in enumerate(parsed):
        base = row.get('base_id'); lexical = row.get('lexical_realization')
        if (not isinstance(base, str) or not base or type(lexical) is not int or lexical not in (0, 1)
                or row.get('condition') != 'neutral' or row.get('template_id') != component
                or row.get('component_id', component) != component):
            raise ValueError('explicit neutral component/base/lexical identities required')
        identity = (row['split'], component)
        if base in bases and bases[base] != identity:
            raise ValueError('numeric base crosses structural components or splits')
        bases[base] = identity
        parents = _parents(tree, slots)
        key = (*identity, base, lexical)
        if parents[0] in groups[key]: raise ValueError('duplicate first-parent variant in matched group')
        # Remove precisely the first-copy read to verify the rest of the AST.
        canonical = ast.parse(row['canonical_source'])
        canonical.body[4].value = ast.Constant(value=0)
        signature = ast.dump(canonical)
        groups[key][parents[0]] = dict(index=index, case_id=case, parents=parents,
            states=_states(tree, slots), signature=signature, rename_map=row['rename_map'],
            surface_context=_surface_context(row['source']))
        identities.append(dict(case_id=case, split=row['split'], component=component,
            base_id=base, lexical_realization=lexical, source=row['source'],
            canonical_source=row['canonical_source'], rename_map=row['rename_map'], variable_slots=row['variable_slots']))
    pairs = []
    for key, variants in sorted(groups.items()):
        if set(variants) != {1, 2, 3}: raise ValueError('complete three-parent matched source groups required')
        left, right = variants[1], variants[2]
        if (len({variant['signature'] for variant in variants.values()}) != 1
                or len({variant['surface_context'] for variant in variants.values()}) != 1
                or any(variant['rename_map'] != left['rename_map'] for variant in variants.values())
                or any(variant['parents'][1:] != left['parents'][1:] for variant in variants.values())):
            raise ValueError('matched programs may differ only in the first-copy read')
        # Require the complete shared initialization state, including v1==v2.
        if left['states'][3] != right['states'][3]: raise ValueError('matched source roots differ')
        if left['states'][3][1] != left['states'][3][2]: continue
        if left['states'] != right['states']: raise ValueError('provenance pair numeric states differ')
        split, component, base, lexical = key
        pairs.append(dict(pair_id=digest([ROLE, left['case_id'], right['case_id']])[:24],
            left_index=left['index'], right_index=right['index'], left_id=left['case_id'], right_id=right['case_id'],
            split=split, component=component, base_id=base, lexical_realization=lexical,
            left_parent_truth=list(left['parents']), right_parent_truth=list(right['parents'])))
    if not pairs: raise ValueError('at least one equal-state provenance pair required')
    result = dict(evaluation_role=ROLE, schema_version=1, source_case_ids=[row['id'] for row in records],
        source_identity_sha256=digest(identities), qualified_sites=list(SITES),
        initialization_site_unobservable=3, pairs=pairs,
        pair_counts=dict(Counter(pair['split'] for pair in pairs)),
        numeric_base_counts={split:len({pair['base_id'] for pair in pairs if pair['split']==split})
            for split in sorted({pair['split'] for pair in pairs})},
        component_counts={split:len({pair['component'] for pair in pairs if pair['split']==split})
            for split in sorted({pair['split'] for pair in pairs})},
        source_only=True, actual_output_not_executed=True, new_model_queries=0,
        generated_holdouts_opened=False, limitation=LIMITATIONS)
    result['manifest_sha256'] = digest(result)
    return result


def _manifest(manifest):
    if (not isinstance(manifest, dict) or manifest.get('evaluation_role') != ROLE
            or manifest.get('schema_version') != 1 or manifest.get('qualified_sites') != list(SITES)
            or manifest.get('manifest_sha256') != digest({k:v for k,v in manifest.items() if k!='manifest_sha256'})):
        raise ValueError('complete matching provenance-pair manifest required')
    ids = manifest.get('source_case_ids')
    if (not isinstance(ids, list) or not ids or any(not isinstance(case,str) or not case for case in ids)
            or len(ids) != len(set(ids))):
        raise ValueError('unique ordered provenance source case IDs required')
    return ids


def score_pairs(manifest, parent_predictions, *, site, split='development'):
    """Score already decoded canonical parent slots, without fitting or I/O.

    ``parent_predictions`` must map every manifest case ID exactly once to four
    integer parent slots, as returned by ``reconstruct_parent_graph``. Metrics
    retain per-pair rows and component summaries for later seed averaging and
    grouped uncertainty; this helper itself computes no confidence intervals.
    """
    ids = _manifest(manifest)
    if type(site) is not int or site not in SITES:
        raise ValueError('only sites 7/8 observe the whole matched parent graph; site 3 is unobservable')
    if split not in ('train','development'): raise ValueError('train/development split required')
    if not isinstance(parent_predictions, dict) or set(parent_predictions) != set(ids):
        raise ValueError('exact manifest case-ID prediction mapping required')
    predicted = {}
    for case in ids:
        values = parent_predictions[case]
        try: values = tuple(values)
        except TypeError as exc: raise ValueError('four canonical parent slots required') from exc
        if (len(values)!=4 or any(isinstance(value,bool) or not isinstance(value,Integral)
                or value not in range(4) or value==destination for destination,value in enumerate(values))):
            raise ValueError('four lawful integer canonical parent slots required')
        predicted[case] = tuple(int(value) for value in values)
    rows = []
    for pair in manifest['pairs']:
        if pair['split'] != split: continue
        left,right = predicted[pair['left_id']],predicted[pair['right_id']]
        ltruth,rtruth = tuple(pair['left_parent_truth']),tuple(pair['right_parent_truth'])
        row = {key:pair[key] for key in ('pair_id','left_id','right_id','component','base_id','lexical_realization')}
        row.update(first_parent_correct_fraction=((left[0]==ltruth[0])+(right[0]==rtruth[0]))/2,
            both_first_parents_correct=int(left[0]==ltruth[0] and right[0]==rtruth[0]),
            first_parent_predictions_differ=int(left[0]!=right[0]), first_parent_predictions_collapse=int(left[0]==right[0]),
            first_parents_swapped=int(left[0]==rtruth[0] and right[0]==ltruth[0]),
            whole_graph_correct_fraction=((left==ltruth)+(right==rtruth))/2,
            both_whole_graphs_correct=int(left==ltruth and right==rtruth),
            whole_graph_predictions_differ=int(left!=right), whole_graph_predictions_collapse=int(left==right))
        rows.append(row)
    if not rows: raise ValueError('requested split has no provenance pairs')
    def means(selected): return {key:sum(row[key] for row in selected)/len(selected) for key in METRICS}
    components = {}
    for component in sorted({row['component'] for row in rows}):
        selected = [row for row in rows if row['component']==component]
        components[component] = dict(lexical_pairs=len(selected), numeric_bases=len({row['base_id'] for row in selected}), metrics=means(selected))
    return dict(evaluation_role=ROLE, status='posthoc_descriptive', site=site, split=split,
        manifest_sha256=manifest['manifest_sha256'], lexical_pairs=len(rows),
        numeric_bases=len({row['base_id'] for row in rows}), structural_components=len(components),
        pooled=means(rows), component_macro={key:sum(value['metrics'][key] for value in components.values())/len(components) for key in METRICS},
        per_component=components, pair_rows=rows, confidence_intervals_computed=False,
        independent_pair_replications=False, new_model_queries=0, generated_holdouts_opened=False, limitation=LIMITATIONS)
