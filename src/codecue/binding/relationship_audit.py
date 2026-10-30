"""Value-free discovery-corpus audit for prefix-visible relationship targets.

This prepares and audits oracle target support. It never reads responses or
activations and does not fit a relationship decoder. Numeric/name relatives are
deduplicated within structural groups before graph/prior summaries.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from . import relationships
from .datasets import digest
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable
from .registry import code_identity
from .representation_sensitivity import _safe

ROLE = 'discovery_relationship_target_audit_v1'
MAX_METADATA_BYTES = 8*1024**2
MAX_DATASET_BYTES = 256*1024**2
MAX_RECORD_BYTES = 1024**2
MAX_ROWS = 50_000
ROW_KEYS = {'id', 'base_id', 'template_id', 'cluster_id', 'family', 'condition', 'lexical_realization',
    'canonical_source', 'source', 'rename_map', 'variable_slots', 'execution_trace', 'split',
    'control_kind', 'evaluation_role', 'load', 'updates', 'paired_group_id', 'counterfactual_group_id',
    'semantic_variant', 'variant', 'rewiring_variant'}
LIMITATION = (
    'Prepared structural targets only: no learned relationship decoder, activation '
    'analysis, model query or causal intervention. Each graph uses only visible '
    'assignment versions; the output expression is absent unless explicitly '
    'visible at the final checkpoint. Relations are syntactic def-use, strict '
    'ancestry and version succession, not numerical equality, functional '
    'influence or evidence that a model represents these relationships. '
    'Support/prior summaries weight structural groups equally after deduplicating '
    'graph states within each group; numeric and naming relatives are not '
    'independent replications. Fixed or one-class labels can make later decoding '
    'trivial. Graph variation alone does not qualify captures, independent '
    'generalization, an ownership mechanism or mechanism C.'
)


def _metadata(config):
    keys = {'evaluation_role', 'dataset', 'dataset_sha256', 'output', 'report'}
    if not isinstance(config, dict) or set(config) != keys or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit discovery relationship-audit configuration required')
    _discovery_declaration(config)
    for key in ('dataset', 'output', 'report'):
        if not isinstance(config[key], str) or not config[key]: raise ValueError('explicit source/output paths required')
        _discovery_response_path(config[key]); _safe(config[key])
    checksum = config['dataset_sha256']
    if (not isinstance(checksum, str) or len(checksum) != 64
            or any(character not in '0123456789abcdef' for character in checksum)):
        raise ValueError('explicit dataset SHA256 pin required')
    dataset, output, report = (Path(config[key]) for key in ('dataset', 'output', 'report'))
    if dataset.suffix != '.jsonl' or output.suffix != '.json' or report.suffix != '.md':
        raise ValueError('JSONL source, compact JSON review and Markdown report required')
    paths = [path.resolve() for path in (dataset, output, report)]
    if len(set(paths)) != 3 or output.resolve() == dataset.with_suffix('.manifest.json').resolve():
        raise ValueError('audit outputs cannot replace source metadata or each other')
    if not dataset.is_file() or dataset.stat().st_size > MAX_DATASET_BYTES:
        raise ValueError('bounded discovery source JSONL required')
    hasher = hashlib.sha256()
    with dataset.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''): hasher.update(block)
    if hasher.hexdigest() != checksum: raise ValueError('pinned relationship source checksum changed')
    return dataset


def _rows(dataset):
    rows = []
    with dataset.open('rb') as stream:
        while True:
            line = stream.readline(MAX_RECORD_BYTES+1)
            if not line: break
            if len(line) > MAX_RECORD_BYTES: raise ValueError('relationship source record exceeds byte limit')
            if not line.strip(): continue
            try: row = json.loads(line)
            except (ValueError, UnicodeError) as exc: raise ValueError('valid discovery JSONL records required') from exc
            if not isinstance(row, dict): raise ValueError('discovery source records must be objects')
            rows.append(row)
            if len(rows) > MAX_ROWS: raise ValueError('relationship source exceeds row limit')
    if not rows: raise ValueError('nonempty relationship source required')
    seen = set(); splits = defaultdict(lambda: defaultdict(set)); bases = {}
    forbidden = {'expected_answer', 'raw_response', 'correct', 'incorrect', 'prediction', 'score',
        'versioned_bindings', 'liveness', 'dependency_edges', 'transitive_dependencies', 'output_uses'}
    for row in rows:
        _discovery_declaration(row)
        if (row.get('split') not in ('train', 'development') or row.get('control_kind') != 'primary'
                or row.get('evaluation_role', ROLE) != ROLE or forbidden.intersection(row) or set(row)-ROW_KEYS):
            raise ValueError('only value-free train/development PRIMARY source records are accepted')
        for key in ('id', 'base_id', 'template_id', 'family', 'canonical_source', 'source'):
            if not isinstance(row.get(key), str) or not row[key]: raise ValueError('explicit source identity/program strings required')
        if row['id'] in seen: raise ValueError('source row identities must be unique')
        seen.add(row['id'])
        if row.get('condition') not in ('neutral', 'informative', 'misleading'):
            raise ValueError('declared discovery naming condition required')
        if type(row.get('lexical_realization', 0)) is not int or row.get('lexical_realization', 0) < 0:
            raise ValueError('nonnegative lexical realization index required')
        for key in ('base_id', 'template_id', 'cluster_id'):
            if key in row:
                if not isinstance(row[key], str) or not row[key]: raise ValueError('nonempty structural identity required')
                splits[key][row[key]].add(row['split'])
        base = (row['split'], row['template_id'], row.get('cluster_id'), row['family'])
        if row['base_id'] in bases and bases[row['base_id']] != base:
            raise ValueError('numeric/naming relatives disagree about their source base identity')
        bases[row['base_id']] = base
        trace = row.get('execution_trace')
        if (not isinstance(trace, list) or not trace
                or any(not isinstance(point, dict) or set(point) != {'statement', 'definition', 'uses'} for point in trace)):
            raise ValueError('stripped statement/definition/uses trace required; oracle values are excluded')
    if any(len(values) != 1 for kind in splits.values() for values in kind.values()):
        raise ValueError('source base/template/cluster groups cross training/development splits')
    return rows, splits


class _Rename(ast.NodeTransformer):
    def __init__(self, mapping): self.mapping = mapping
    def visit_Name(self, node):
        if node.id not in self.mapping: raise ValueError('explicit inverse rename map must cover every visible identifier')
        return ast.copy_location(ast.Name(id=self.mapping[node.id], ctx=node.ctx), node)


def _operand_uses(expression, versions, slots, statement, consumer):
    """Independent lexical AST reads, preserving repeated operand occurrences."""
    result = []
    def visit(node, path):
        if isinstance(node, ast.Name):
            version = int(versions[node.id].rsplit('@', 1)[1])
            result.append(dict(statement=statement, consumer=consumer, occurrence=len(result), operand_path=path,
                referent=f'v{slots[node.id]}@{version}', canonical_name=f'v{slots[node.id]}', slot=slots[node.id], version=version))
        elif isinstance(node, ast.BinOp):
            visit(node.left, path+['left']); visit(node.right, path+['right'])
        elif isinstance(node, ast.UnaryOp): visit(node.operand, path+['operand'])
        elif not isinstance(node, ast.Constant): raise ValueError('restricted relationship expression required')
    visit(expression, [])
    return result


def _source(row):
    canonical = relationships._tree(row['canonical_source']); surface = relationships._tree(row['source'])
    mapping = row.get('rename_map')
    if (not isinstance(mapping, dict) or not mapping or any(not isinstance(k, str) or not isinstance(v, str) for k, v in mapping.items())
            or len(set(mapping.values())) != len(mapping)):
        raise ValueError('explicit bijective canonical-to-surface rename map required')
    inverse = {value: key for key, value in mapping.items()}
    restored = _Rename(inverse).visit(deepcopy(surface))
    if len(restored.body) != len(canonical.body): raise ValueError('surface and canonical statement counts differ')
    for end in range(1, len(canonical.body)+1):
        if ast.dump(ast.Module(body=canonical.body[:end], type_ignores=[])) != ast.dump(ast.Module(body=restored.body[:end], type_ignores=[])):
            raise ValueError('inverse-renamed canonical/surface visible prefixes differ')
    names = {node.id for node in ast.walk(canonical) if isinstance(node, ast.Name)}
    if set(mapping) != names: raise ValueError('rename map must match exactly the source identifier inventory')
    supplied = row.get('variable_slots')
    if supplied is None:
        supplied = {}
        for point in canonical.body[:-1]:
            if point.targets[0].id not in supplied: supplied[point.targets[0].id] = len(supplied)
    slots = relationships._slots(canonical.body[:-1], supplied)
    if set(slots) != names: raise ValueError('canonical slot frame must match the source identifier inventory')
    if len(row['execution_trace']) != len(canonical.body)-1:
        raise ValueError('stripped trace must cover every assignment checkpoint')
    versions = {}; counts = Counter(); definitions = []; direct = set(); succession = set()
    snapshots = []; all_uses = []
    for index, statement in enumerate(canonical.body[:-1]):
        name = statement.targets[0].id
        reads = [{'name': node.id, 'definition': versions[node.id]} for node in ast.walk(statement.value) if isinstance(node, ast.Name)]
        counts[name] += 1; definition = f'{name}@{counts[name]}'
        point = row['execution_trace'][index]
        if (type(point.get('statement')) is not int or point['statement'] != index or point.get('definition') != definition
                or not isinstance(point.get('uses'), list)
                or any(not isinstance(use, dict) or set(use) != {'name', 'definition'} for use in point['uses'])
                or Counter((use['name'], use['definition']) for use in point['uses']) != Counter((use['name'], use['definition']) for use in reads)):
            raise ValueError('stripped canonical trace definition/use referents differ from visible source')
        key = f'v{slots[name]}@{counts[name]}'
        all_uses.extend(_operand_uses(statement.value, versions, slots, index, key))
        referents = {f"v{slots[use['name']]}@{use['definition'].rsplit('@', 1)[1]}" for use in reads}
        direct.update((referent, key) for referent in referents)
        if name in versions: succession.add((f"v{slots[name]}@{counts[name]-1}", key))
        versions[name] = definition
        definitions.append({'id': key, 'canonical_name': f'v{slots[name]}', 'slot': slots[name], 'version': counts[name], 'statement': index})
        current = {f"v{slots[name]}@{value.rsplit('@', 1)[1]}" for name, value in versions.items()}
        nodes = [{**node, 'status': 'current' if node['id'] in current else 'obsolete'} for node in definitions]
        snapshots.append((nodes, set(direct), set(succession), deepcopy(all_uses), None))
    final = snapshots[-1]
    snapshots[-1] = (*final[:-1], _operand_uses(canonical.body[-1].value, versions, slots, len(snapshots), 'output'))
    return canonical, slots, {mapping[name]: slot for name, slot in slots.items()}, snapshots


def _graph(graph, index, visible, expected):
    required = {'schema_version', 'checkpoint', 'output_visible', 'version_nodes', 'direct_def_use_edges',
        'strict_ancestor_edges', 'succession_edges', 'uses'}|({'output'} if visible else set())
    if (not isinstance(graph, dict) or set(graph) != required or graph.get('schema_version') != 1
            or type(graph.get('checkpoint')) is not int or graph.get('checkpoint') != index or graph.get('output_visible') is not visible):
        raise ValueError('strict visible-only relationship graph schema required')
    nodes, direct, succession, expected_uses, expected_output_uses = expected
    if sorted(graph['version_nodes'], key=lambda node: node['id']) != sorted(nodes, key=lambda node: node['id']):
        raise ValueError('topological current/obsolete version nodes differ from the visible trace')
    lookup = {node['id']: node for node in nodes}; parents = defaultdict(set)
    for start, end in direct: parents[end].add(start)
    closure = {}
    for node in sorted(nodes, key=lambda value: value['statement']):
        closure[node['id']] = parents[node['id']]|{ancestor for parent in parents[node['id']] for ancestor in closure[parent]}
    strict = {(parent, child) for child, values in closure.items() for parent in values}
    for field, expected_edges in [('direct_def_use_edges', direct), ('strict_ancestor_edges', strict), ('succession_edges', succession)]:
        edges = graph[field]
        if (not isinstance(edges, list) or any(not isinstance(edge, list) or len(edge) != 2 for edge in edges)
                or len({tuple(edge) for edge in edges}) != len(edges) or {tuple(edge) for edge in edges} != expected_edges):
            raise ValueError('prefix relationship edges/strict closure/version succession differ from trace')
    uses = graph['uses']
    if not isinstance(uses, list) or uses != expected_uses:
        raise ValueError('complete operand-path/use-occurrence records must match the visible AST')
    observed = set(); occurrences = defaultdict(set)
    for use in uses:
        if (not isinstance(use, dict) or use.get('referent') not in lookup or use.get('consumer') not in lookup
                or lookup[use['referent']]['statement'] >= lookup[use['consumer']]['statement']
                or use.get('statement') != lookup[use['consumer']]['statement']
                or any(use.get(key) != lookup[use['referent']][key] for key in ('canonical_name', 'slot', 'version'))
                or type(use.get('occurrence')) is not int or use['occurrence'] < 0
                or use['occurrence'] in occurrences[use['statement']]):
            raise ValueError('topological latest-definition use referents differ')
        occurrences[use['statement']].add(use['occurrence']); observed.add((use['referent'], use['consumer']))
    if observed != direct: raise ValueError('use referents and direct def-use graph differ')
    if visible:
        output = graph['output']
        expected_referents = {use['referent'] for use in expected_output_uses}
        if (not isinstance(output, dict) or set(output) != {'direct_uses', 'direct_referents', 'structural_ancestors', 'semantics'}
                or output.get('direct_uses') != expected_output_uses or set(output.get('direct_referents', [])) != expected_referents
                or output.get('semantics') != 'syntactic_dependencies_not_functional_influence'
                or not isinstance(output.get('direct_referents'), list) or not set(output['direct_referents']) <= set(lookup)
                or any(lookup[value]['status'] != 'current' for value in output['direct_referents'])
                or set(output.get('structural_ancestors', [])) != set(output['direct_referents'])|{
                    parent for value in output['direct_referents'] for parent in closure[value]}):
            raise ValueError('explicit final output ancestor graph differs')
    return lookup, direct, strict, succession


def audit_rows(rows):
    """Audit prevalidated value-free rows without model/activation access."""
    graph_cells = defaultdict(lambda: defaultdict(set)); pair_cells = defaultdict(lambda: defaultdict(dict))
    exact_prefix = {}; matched = {}; canonical_cache = {}; status_groups = defaultdict(set)
    catalog = {}; positioned = defaultdict(set)
    relation_groups = defaultdict(lambda: {'positive': set(), 'negative': set()})
    versions = Counter(); views = 0; assignments = 0; duplicate_prefixes = 0; final_rows = 0
    for row in rows:
        tree, slots, surface_slots, snapshots = _source(row)
        group = row.get('cluster_id', row['template_id'])
        for index in range(len(snapshots)):
            for visible in ([False, True] if index == len(snapshots)-1 else [False]):
                cache_key = (row['canonical_source'], tuple(sorted(slots.items())), index, visible)
                if cache_key not in canonical_cache:
                    canonical_cache[cache_key] = relationships.labels_at(row['canonical_source'], index, slots, output_visible=visible)
                graph = canonical_cache[cache_key]
                surface = relationships.labels_at(row['source'], index, surface_slots, output_visible=visible)
                if graph != surface: raise ValueError('canonical and inverse-renamed surface relationship labels differ')
                lookup, direct, strict, succession = _graph(graph, index, visible, snapshots[index])
                full_signature = digest(graph)
                # Assignment order/use operand positions are separate baselines,
                # not new semantic definition graphs. Keep obsolete versions.
                semantic = {key: deepcopy(graph[key]) for key in
                    ('direct_def_use_edges', 'strict_ancestor_edges', 'succession_edges')}
                semantic['version_nodes'] = [{key: node[key] for key in
                    ('id', 'canonical_name', 'slot', 'version', 'status')} for node in graph['version_nodes']]
                semantic['output_visible'] = visible
                if visible:
                    semantic['output'] = {key: deepcopy(graph['output'][key]) for key in
                        ('direct_referents', 'structural_ancestors', 'semantics')}
                signature = digest(semantic); catalog[signature] = semantic
                body = tree.body if visible else tree.body[:index+1]
                frame = tuple(sorted({node['slot'] for node in lookup.values()}))
                defined = {node.id for point in body for node in ast.walk(point) if isinstance(node, ast.Name)}
                visible_mapping = sorted((name, slots[name]) for name in defined)
                mapping_hash = digest(visible_mapping)
                prefix = digest([ast.dump(ast.Module(body=body, type_ignores=[])), visible_mapping, visible])
                if prefix in exact_prefix:
                    duplicate_prefixes += 1
                    if exact_prefix[prefix] != full_signature: raise ValueError('identical visible canonical prefix has inconsistent relationship graphs')
                exact_prefix[prefix] = full_signature
                # Counterfactual rewiring variants can share one numeric base.
                # Only naming/lexical relatives of the SAME canonical program
                # must reproduce the same graph.
                relative = (row['base_id'], digest(row['canonical_source']), tuple(sorted(slots.items())), index, visible)
                if relative in matched and matched[relative] != signature:
                    raise ValueError('matched naming/numeric source relatives have inconsistent prefix graphs')
                matched[relative] = signature
                context = (row['split'], row['family'], index+1, visible, frame, mapping_hash)
                graph_cells[context][group].add(signature)
                positioned[context].add(full_signature)
                views += 1; assignments += not visible; final_rows += visible
                current = {node['slot']: node['id'] for node in lookup.values() if node['status'] == 'current'}
                for status in ('current', 'obsolete'):
                    nodes = [node for node in lookup.values() if node['status'] == status]
                    versions[status] += len(nodes)
                    if nodes: status_groups[status].add(group)
                for category, edges in [('direct_def_use', direct), ('strict_ancestor', strict), ('version_succession', succession)]:
                    possible = {(left, right) for left in lookup for right in lookup if left != right}
                    if edges: relation_groups[category]['positive'].add(group)
                    if possible-edges: relation_groups[category]['negative'].add(group)
                for category, edges in [('direct_def_use', direct), ('strict_ancestor', strict)]:
                    for left in current:
                        for right in current:
                            pair_cells[(*context, category, left, right)][group][signature] = int((current[left], current[right]) in edges)
                if visible:
                    ancestors = set(graph['output']['structural_ancestors'])
                    if ancestors: relation_groups['output_ancestor']['positive'].add(group)
                    if set(lookup)-ancestors: relation_groups['output_ancestor']['negative'].add(group)
                    for slot, definition in current.items():
                        pair_cells[(*context, 'output_ancestor', slot, 'output')][group][signature] = int(definition in ancestors)
    variation = []
    for key, groups in sorted(graph_cells.items()):
        split, family, length, visible, frame, mapping_hash = key
        all_graphs = set().union(*groups.values())
        variation.append(dict(split=split, family=family, prefix_assignments=length, output_visible=visible,
            visible_slot_ids=list(frame), canonical_slot_mapping_sha256=mapping_hash, structural_groups=len(groups), distinct_graphs=len(all_graphs),
            distinct_position_labeled_graphs=len(positioned[key]),
            groups_with_multiple_graphs=sum(len(values) > 1 for values in groups.values()),
            group_graph_count_histogram={str(k): v for k, v in sorted(Counter(map(len, groups.values())).items())}))
    support = []
    for key, groups in sorted(pair_cells.items(), key=lambda pair: str(pair[0])):
        split, family, length, visible, frame, mapping_hash, category, left, right = key
        values = [set(observed.values()) for observed in groups.values()]
        positive = sum(1 in value for value in values); negative = sum(0 in value for value in values)
        fractions = [sum(observed.values())/len(observed) for observed in groups.values()]
        prevalence = sum(fractions)/len(fractions)
        support.append(dict(split=split, family=family, prefix_assignments=length, output_visible=visible,
            visible_slot_ids=list(frame), canonical_slot_mapping_sha256=mapping_hash, relation=category, source_slot=left, target_slot=right,
            structural_groups=len(groups), positive_groups=positive, negative_groups=negative,
            mixed_label_groups=sum(len(value) == 2 for value in values), nontrivial_label_support=positive > 0 and negative > 0,
            group_weighted_positive_fraction=prevalence, group_weighted_majority_prior=max(prevalence, 1-prevalence)))
    overlap = []
    contexts = {(family, length, visible, frame, mapping_hash) for _, family, length, visible, frame, mapping_hash in graph_cells}
    for family, length, visible, frame, mapping_hash in sorted(contexts):
        by_split = {}
        for split in ('train', 'development'):
            groups = graph_cells.get((split, family, length, visible, frame, mapping_hash), {})
            by_split[split] = set().union(*groups.values()) if groups else set()
        overlap.append(dict(family=family, prefix_assignments=length, output_visible=visible,
            visible_slot_ids=list(frame), canonical_slot_mapping_sha256=mapping_hash, train_graphs=len(by_split['train']), development_graphs=len(by_split['development']),
            shared_semantic_graphs=len(by_split['train'] & by_split['development'])))
    return dict(assignment_checkpoint_views=assignments, final_output_checkpoint_views=final_rows, graph_views=views,
        exact_canonical_prefixes=len(exact_prefix), repeated_exact_prefix_views=duplicate_prefixes,
        exact_duplicate_prefix_graphs_consistent=True, matched_condition_and_lexical_graphs_consistent=True,
        matched_condition_consistency_scope='Same base and canonical-program signature; explicit counterfactual rewiring variants may differ.',
        prefix_only_output_labels=None, output_visibility='Only separate explicit final-assignment views include output labels; hidden output is absent, not a negative label.',
        version_node_observations=dict(versions), version_status_structural_groups={k: len(v) for k, v in status_groups.items()},
        relation_structural_group_support={category: {key+'_groups': len(value) for key, value in counts.items()}
            for category, counts in sorted(relation_groups.items())},
        semantic_graph_signature='Canonical version IDs/slots/current-or-obsolete status, direct/strict/succession edges and explicit output referents/ancestors; excludes assignment positions, use operand paths, numeric literals and surface names.',
        semantic_graph_catalog=catalog, semantic_graphs=len(catalog),
        cross_split_semantic_graph_overlap_by_prefix=overlap,
        prefix_overlap_interpretation='Shared partial graphs across split-disjoint full components are reported, not rejected or counted as novel independent structures.',
        graph_variation_by_visible_prefix=variation, current_slot_pair_support=support,
        current_slot_pair_scope='Relations between currently active definitions only; historical-version nodes and all version edges remain in the semantic graph catalog.',
        nontrivial_current_slot_pair_cells=sum(cell['nontrivial_label_support'] for cell in support),
        total_current_slot_pair_cells=len(support), statistical_unit='Structural group; unique graph states within each group, never raw row/naming/numeric counts.')


def run(config):
    dataset = _metadata(config); rows, splits = _rows(dataset)
    audited = audit_rows(rows)
    groups = {row.get('cluster_id', row['template_id']) for row in rows}
    result = dict(status='prepared_targets_only', evaluation_role=ROLE, config_hash=digest(config), analysis_source=code_identity(),
        dataset=str(dataset), dataset_sha256=config['dataset_sha256'], dataset_bytes=dataset.stat().st_size,
        rows=len(rows), source_bases=len({row['base_id'] for row in rows}), structural_groups=len(groups),
        split_rows=dict(Counter(row['split'] for row in rows)),
        split_structural_groups={split: len({row.get('cluster_id', row['template_id']) for row in rows if row['split'] == split})
            for split in ('train', 'development')},
        checked_group_keys=sorted(splits), split_group_overlap={key: 0 for key in splits}, **audited,
        learned_relationship_decoder_fitted=False, training_ready_relation_matrix_exported=False,
        activation_arrays_opened=False, model_responses_opened=False, expected_answers_used_as_features=False,
        new_model_queries=0, generated_holdouts_opened=False, mechanism_C_fitted=False, limitation=LIMITATION)
    lines = ['# Prefix-visible relationship target audit', '', LIMITATION, '',
        f"{result['rows']:,} value-free PRIMARY discovery rows, {result['source_bases']:,} source bases and {result['structural_groups']} structural groups. No group crosses training/development.", '',
        f"Audited {audited['assignment_checkpoint_views']:,} assignment-prefix views plus {audited['final_output_checkpoint_views']:,} separate output-visible final views. Exact duplicate canonical prefixes and matched naming relatives have consistent graphs.", '',
        f"{audited['nontrivial_current_slot_pair_cells']:,} of {audited['total_current_slot_pair_cells']:,} current-slot relation cells have both positive and negative structural-group support. This is target variation, not measured decoding performance.", '',
        '| Split | Family | Visible assignments | Output visible | Visible slots | Groups | Distinct graphs | Groups with graph variation |',
        '|---|---|---:|---|---|---:|---:|---:|']
    for cell in audited['graph_variation_by_visible_prefix']:
        lines.append('| '+' | '.join(str(cell[key]) for key in ('split', 'family', 'prefix_assignments', 'output_visible',
            'visible_slot_ids', 'structural_groups', 'distinct_graphs', 'groups_with_multiple_graphs'))+' |')
    lines += ['', 'The JSON retains every current-slot pair, prefix length, visible slot frame, relation and structural-group class-support/prior cell. Output-ancestor targets exist only in explicit output-visible views. No relation matrix, activations or learned probe are produced.', '']
    data = {Path(config['output']): (json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n').encode(),
        Path(config['report']): '\n'.join(lines).encode()}
    if len(data[Path(config['output'])]) > MAX_METADATA_BYTES: raise ValueError('compact relationship audit exceeds metadata byte limit')
    for path, content in data.items():
        if path.exists() and path.read_bytes() != content: raise ValueError('immutable relationship audit artifact differs: '+str(path))
    for path, content in data.items(): immutable(path, content)
    return result
