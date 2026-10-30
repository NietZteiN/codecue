"""Immutable discovery-cohort recipes and content-based overlap audits.

This module prepares generated source programs, never model responses. Generation
seeds do not establish independent structural replication. Label-like template
and base IDs are scoped to their bank; cross-bank components use actual syntax.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re

from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, sha

ROLE='discovery_replication_preparation_v1'
KINDS=('competition','live_load','arithmetic_readout')
LIMITATION=(
    'Generated discovery/calibration source preparation only; no model inference, '
    'final outcomes, training or confirmatory claim. Distinct generation seeds '
    'are not independent structural replications. Cross-bank template/base ID '
    'namespaces cannot be pooled without content checks. Alpha-skeleton sharing '
    'is expected in numeric calibration but invalidates treating rows as new '
    'independent structures. No automatic pooling, resplitting or final opening '
    'is authorized by a passed source audit.'
)


def _roles():
    from .competition import ROLE as competition
    from .live_load import ROLE as live_load
    from .arithmetic_readout import ROLE as arithmetic
    return dict(competition=competition,live_load=live_load,arithmetic_readout=arithmetic)


def _safe_declarations(value):
    if not isinstance(value,dict):return
    role=str(value.get('evaluation_role','')).lower().replace('-','_')
    if any(word in role for word in ('final','extrap','holdout','heldout','held_out','sealed','reserved')) or 'test' in role.split('_'):
        raise ValueError('replication preparation cannot open reserved or final sources')
    for key in ('split','split_override','splits'):
        if key not in value:continue
        choices=value[key] if isinstance(value[key],(list,tuple)) else [value[key]]
        if not choices or any(part not in ('train','development','calibration') for part in choices):
            raise ValueError('only discovery/calibration source splits are permitted')
    for key in ('generation','config'):_safe_declarations(value.get(key))
    for section in value.get('sections',[]):_safe_declarations(section)


def _safe_path(value):
    from .forecasting import _discovery_response_path
    path=Path(value).resolve();_discovery_response_path(path)
    parts=path.parts
    markers=(parts[len(parts)-1-list(reversed(parts)).index('binding')+1:] if 'binding' in parts
        else [part for part in parts if part.lower()=='reserved' or part.lower().startswith('reserved_')]+[path.name])
    if any(re.match(r'^reserved(?:[_\-.]|$)',part.lower()) for part in markers):
        raise ValueError('reserved paths cannot be used for replication preparation')
    return path


def _normalize(config):
    _safe_declarations(config)
    banks=config.get('banks')
    if not isinstance(banks,list) or not banks:raise ValueError('declare a nonempty discovery bank list')
    names=set();seeds=set();paths={};normalized=[];roles=_roles()
    if config.get('evaluation_role',ROLE)!=ROLE:raise ValueError('preparation evaluation role differs')
    def claim(value,label):
        path=_safe_path(value)
        if path in paths:raise ValueError(f'preparation artifact path collision: {label} and {paths[path]}')
        paths[path]=label
    for index,bank in enumerate(banks):
        if not isinstance(bank,dict):raise ValueError('each bank must be an object')
        _safe_declarations(bank)
        name=bank.get('name');kind=bank.get('kind');generation=bank.get('generation')
        if not isinstance(name,str) or not name or name in names:raise ValueError('bank names must be nonempty and unique')
        names.add(name)
        if kind not in KINDS or not isinstance(generation,dict):raise ValueError('registered kind and generation object required')
        if bank.get('evaluation_role',roles[kind])!=roles[kind]:raise ValueError('bank evaluation role differs')
        generation=dict(generation)
        if 'dataset' in generation:raise ValueError('dataset belongs to the bank recipe, not generation')
        seed=generation.get('seed')
        if type(seed) is not int or (kind,seed) in seeds:raise ValueError('distinct integer generation seeds are required within each kind')
        seeds.add((kind,seed))
        if generation.get('evaluation_role',roles[kind])!=roles[kind]:raise ValueError('generator evaluation role differs')
        dataset=Path(bank.get('dataset',''))
        if dataset.suffix!='.jsonl':raise ValueError('bank dataset must name a JSONL source artifact')
        claim(dataset,name+' dataset');claim(dataset.with_suffix('.manifest.json'),name+' manifest')
        if kind=='competition':
            count=generation.get('numeric_per_template')
            if type(count) is not int or count<1:raise ValueError('positive competition numeric_per_template required')
            generator_config={**generation,'dataset':str(dataset)};rows=1248*count
        elif kind=='live_load':
            count=generation.get('numeric_per_template');templates=generation.get('templates');noise=generation.get('noise_pairs')
            if (type(count) is not int or count<2 or count%2 or type(templates) is not int or not 1<=templates<=24
                    or type(noise) is not int or not 1<=noise<=16 or generation.get('initialize_results') is not True):
                raise ValueError('live-load prep requires complete sign pairs, valid templates/noise and initialized result slots')
            generator_config={'dataset':str(dataset),'generation':generation};rows=99*templates*count
        else:
            from .arithmetic_readout import _options
            count,_,_,_=_options(generation)
            generator_config={'dataset':str(dataset),'generation':generation};rows=48*count
        normalized.append({'name':name,'kind':kind,'seed':seed,'dataset':str(dataset),
            'manifest':str(dataset.with_suffix('.manifest.json')),'evaluation_role':roles[kind],
            'generation':generation,'generator_config':generator_config,'expected_rows':rows})
    output=Path(config['output']);report=Path(config['report'])
    manifest=Path(config.get('manifest',output.with_suffix('.manifest.json')))
    inventory=Path(config.get('inventory',output.with_name(output.stem+'_fingerprints.jsonl')))
    if output.suffix!='.json' or manifest.suffix!='.json' or report.suffix!='.md' or inventory.suffix!='.jsonl':
        raise ValueError('declare JSON review/manifest, Markdown report and JSONL fingerprint artifacts')
    for value,label in ((output,'review'),(manifest,'package manifest'),(report,'report'),(inventory,'fingerprint inventory')):claim(value,label)
    return normalized,dict(output=output,manifest=manifest,report=report,inventory=inventory)


def plan(config):
    """Validate exact recipes and counts without reading or writing source payloads."""
    banks,paths=_normalize(config)
    return {'status':'planned','evaluation_role':ROLE,'config_hash':digest(config),
        'banks':banks,'expected_rows':sum(bank['expected_rows'] for bank in banks),
        'artifacts':{key:str(path) for key,path in paths.items()},
        'writes_performed':False,'model_inference':False,'generated_holdouts_opened':False,
        'generation_commands':[{'entrypoint':'scripts/123_binding_replication_prep.py build CONFIG',
            'bank':bank['name'],'generator_kind':bank['kind'],'generator_config':bank['generator_config']} for bank in banks],
        'limitation':LIMITATION}


def fingerprints(row):
    source=row['source'];canonical=row.get('canonical_source',source)
    from .competition import alpha_skeleton
    encoded=lambda text:hashlib.sha256(text.encode()).hexdigest()
    return {'source_sha256':encoded(source),
        'canonical_ast_sha256':encoded(ast.dump(ast.parse(canonical),include_attributes=False)),
        'alpha_skeleton_sha256':encoded(alpha_skeleton(canonical))}


def _load_bank(bank):
    """Check typed source metadata before opening a generated source payload."""
    path=Path(bank['dataset']);manifest_path=Path(bank['manifest'])
    if not path.exists() or not manifest_path.exists():raise ValueError('complete immutable dataset and manifest required: '+bank['name'])
    metadata=json.loads(manifest_path.read_text());_safe_declarations(metadata)
    if metadata.get('evaluation_role')!=bank['evaluation_role']:raise ValueError('bank source role differs: '+bank['name'])
    if sha(path)!=metadata.get('sha256'):raise ValueError('bank source hash differs: '+bank['name'])
    expected=digest(bank['generator_config'] if bank['kind']=='competition' else bank['generation'])
    if metadata.get('generation_config_hash')!=expected:raise ValueError('registered source generation changed: '+bank['name'])
    rows=read_jsonl(path)
    if len(rows)!=bank['expected_rows'] or metadata.get('rows')!=len(rows):raise ValueError('bank source coverage differs: '+bank['name'])
    if bank['kind']=='competition':
        from .competition import validate_rows
        validate_rows(rows)
    elif bank['kind']=='live_load':
        from .live_load import validate_rows
        validate_rows(rows,generation=bank['generation'])
    else:
        from .arithmetic_readout import validate_rows
        validate_rows(rows,generation=bank['generation'])
    return {**bank,'rows':rows,'source_manifest':metadata,'manifest_sha256':sha(manifest_path)}


def _analyze(banks):
    inventory=[];names=set();relations=defaultdict(set);declared_templates=defaultdict(lambda:defaultdict(set))
    declared_bases=defaultdict(lambda:defaultdict(set));declared_rows=defaultdict(dict);bank_sets={};summaries=[]
    roles=_roles()
    for bank in banks:
        name=bank['name']
        if name in names:raise ValueError('bank names must be unique')
        if bank.get('kind') not in KINDS:raise ValueError('registered discovery generator kind required')
        names.add(name);rows=list(bank['rows'])
        if (not rows or any(not isinstance(row.get('id'),str) or not row['id'] for row in rows)
                or len({row['id'] for row in rows})!=len(rows)):
            raise ValueError('duplicate or missing row IDs within bank: '+name)
        sets={key:set() for key in ('row_id','source_sha256','canonical_ast_sha256','alpha_skeleton_sha256')}
        alpha_splits=defaultdict(set);alpha_canonical=defaultdict(set)
        split_sets=defaultdict(lambda:{key:set() for key in sets})
        for row in rows:
            _safe_declarations(row)
            if row.get('evaluation_role')!=roles[bank['kind']]:
                raise ValueError('unexpected source evaluation role in bank: '+name)
            if row.get('split') not in ('train','development','calibration'):
                raise ValueError('reserved or missing split in generated source audit')
            values=fingerprints(row);values.update(bank=name,id=row['id'],split=row['split'])
            inventory.append(values);sets['row_id'].add(row['id']);split_sets[row['split']]['row_id'].add(row['id'])
            declared_rows[row['id']][name]=values['source_sha256']
            for key in ('source_sha256','canonical_ast_sha256','alpha_skeleton_sha256'):
                sets[key].add(values[key]);split_sets[row['split']][key].add(values[key])
            alpha=values['alpha_skeleton_sha256'];alpha_splits[alpha].add(row['split'])
            alpha_canonical[alpha].add(values['canonical_ast_sha256'])
            for field in ('base_id','paired_group_id','counterfactual_group_id','structural_group'):
                if row.get(field) is not None:relations[name,field,str(row[field])].add(alpha)
            if row.get('template_id') is not None:declared_templates[str(row['template_id'])][name].add(alpha)
            if row.get('base_id') is not None:declared_bases[str(row['base_id'])][name].add(values['canonical_ast_sha256'])
        bank_sets[name]=(sets,alpha_splits,split_sets,alpha_canonical)
        summaries.append({'name':name,'kind':bank.get('kind'),'rows':len(rows),'split_counts':dict(Counter(r['split'] for r in rows)),
            'unique_row_ids':len(sets['row_id']),'unique_source_hashes':len(sets['source_sha256']),
            'unique_canonical_asts':len(sets['canonical_ast_sha256']),'unique_alpha_skeletons':len(sets['alpha_skeleton_sha256']),
            'repeated_source_rows':len(rows)-len(sets['source_sha256']),
            'repeated_canonical_ast_rows':len(rows)-len(sets['canonical_ast_sha256']),
            'repeated_alpha_skeleton_rows':len(rows)-len(sets['alpha_skeleton_sha256']),
            'within_bank_split_overlap':[{'left_split':left,'right_split':right,
                **{'shared_'+key:len(split_sets[left][key]&split_sets[right][key]) for key in sets}}
                for left,right in combinations(sorted(split_sets),2)],
            'alpha_skeletons_crossing_train_development':sum({'train','development'}<=splits for splits in alpha_splits.values())})
    # Nodes are CONTENT fingerprints. Reused declared labels never join banks.
    parent={row['alpha_skeleton_sha256']:row['alpha_skeleton_sha256'] for row in inventory}
    def root(value):
        while parent[value]!=value:
            parent[value]=parent[parent[value]];value=parent[value]
        return value
    for alphas in relations.values():
        first=min(alphas)
        for alpha in alphas:parent[root(alpha)]=root(first)
    content=defaultdict(set)
    for alpha in parent:content[root(alpha)].add(alpha)
    component_ids={key:digest(sorted(values)) for key,values in content.items()}
    components=defaultdict(lambda:{'banks':set(),'splits':set(),'rows':0,'alpha_skeletons':set()})
    for row in inventory:
        component=component_ids[root(row['alpha_skeleton_sha256'])];row['content_relation_component']=component
        entry=components[component];entry['banks'].add(row['bank']);entry['splits'].add(row['split']);entry['rows']+=1
        entry['alpha_skeletons'].add(row['alpha_skeleton_sha256'])
    component_rows=[{'id':key,'banks':sorted(value['banks']),'splits':sorted(value['splits']),'rows':value['rows'],
        'alpha_skeletons':len(value['alpha_skeletons']),
        'crosses_train_development':{'train','development'}<=value['splits']} for key,value in sorted(components.items())]
    pairs=[]
    for left,right in combinations(sorted(names),2):
        a,asplits,asets,acanonical=bank_sets[left];b,bsplits,bsets,bcanonical=bank_sets[right]
        common=a['alpha_skeleton_sha256']&b['alpha_skeleton_sha256']
        pairs.append({'left':left,'right':right,**{'shared_'+key:len(a[key]&b[key]) for key in a},
            'split_pairs':[{'left_split':sa,'right_split':sb,
                **{'shared_'+key:len(asets[sa][key]&bsets[sb][key]) for key in a}}
                for sa in sorted(asets) for sb in sorted(bsets)],
            'shared_skeletons_with_different_canonical_variants':sum(
                acanonical[key]!=bcanonical[key] for key in common),
            'alpha_skeletons_crossing_bank_train_development':sum(
                ('train' in asplits[key] and 'development' in bsplits[key]) or
                ('development' in asplits[key] and 'train' in bsplits[key]) for key in common),
            'shared_alpha_fingerprint_examples':sorted(common)[:8]})
    def reused(mapping,field):
        return [{'declared_'+field:key,'banks':sorted(values),
                 'content_counts_by_bank':{bank:len(hashes) for bank,hashes in sorted(values.items())}}
                for key,values in sorted(mapping.items()) if len(values)>1 and len({tuple(sorted(v)) for v in values.values()})>1]
    template_reuse=reused(declared_templates,'template_id');base_reuse=reused(declared_bases,'base_id')
    row_collisions=[{'row_id':key,'source_hashes_by_bank':dict(sorted(values.items()))}
        for key,values in sorted(declared_rows.items()) if len(set(values.values()))>1]
    summary={'status':'needs_attention' if row_collisions else 'passed','evaluation_role':ROLE,'banks':summaries,'bank_pairs':pairs,
        'content_relation_components':component_rows,
        'content_relation_component_count':len(components),
        'components_crossing_train_development':sum(row['crosses_train_development'] for row in component_rows),
        'declared_template_ids_reused_with_different_content':template_reuse,
        'declared_base_ids_reused_with_different_content':base_reuse,
        'row_ids_reused_with_different_sources':row_collisions,
        'source_preparation_opportunities':{
            'bank_pairs_with_shared_source_prompts':sum(pair['shared_source_sha256']>0 for pair in pairs),
            'bank_pairs_with_different_canonical_variants_on_shared_skeletons':sum(
                pair['shared_skeletons_with_different_canonical_variants']>0 for pair in pairs),
            'alpha_skeletons_absent_from_other_banks':{name:len(
                bank_sets[name][0]['alpha_skeleton_sha256']-set().union(*[
                    bank_sets[other][0]['alpha_skeleton_sha256'] for other in names if other!=name]))
                for name in sorted(names)},
            'requires_explicit_discovery_comparison_plan':True,'confirmatory_use_authorized':False},
        'total_rows':len(inventory),'model_inference':False,'generated_holdouts_opened':False,
        'confirmatory_eligibility':False,'automatic_pooling_allowed':False,
        'component_definition':'Union actual alpha-skeleton content with bank-scoped base/paired/counterfactual/structural relatives; never join banks by declared ID alone. This conservative full graph includes calibration relatives and is not a replacement for each original main-cohort structural split.',
        'limitation':LIMITATION}
    return summary,sorted(inventory,key=lambda row:(row['bank'],row['id']))


def audit_rows(banks):
    """Pure content audit for validated source-bank records (also useful in tests)."""
    return _analyze(banks)[0]


def _emit(config,banks,paths):
    result,inventory=_analyze(banks)
    from .registry import code_identity
    source=code_identity()
    inventory_content=''.join(json.dumps(row,sort_keys=True)+'\n' for row in inventory).encode()
    immutable(paths['inventory'],inventory_content)
    result.update(config_hash=digest(config),analysis_source=source,
        cohort_hashes={bank['name']:{'dataset':bank['dataset'],'sha256':bank['source_manifest']['sha256'],
            'manifest':bank['manifest'],'manifest_sha256':bank['manifest_sha256'],'generation_seed':bank['seed']}
            for bank in banks},fingerprint_inventory=str(paths['inventory']),fingerprint_inventory_sha256=sha(paths['inventory']),
        report=str(paths['report']))
    lines=['# Discovery replication preparation','',LIMITATION,'',
        f"Prepared/audited {result['total_rows']:,} generated source rows in {len(banks)} banks. No model outcome was collected.",'',
        '| Bank | Kind | Rows | Unique source hashes | Canonical ASTs | Alpha skeletons | Train/dev shared skeletons |',
        '|---|---|---:|---:|---:|---:|---:|']
    for bank in result['banks']:
        lines.append(f"| {bank['name']} | {bank['kind']} | {bank['rows']} | {bank['unique_source_hashes']} | {bank['unique_canonical_asts']} | {bank['unique_alpha_skeletons']} | {bank['alpha_skeletons_crossing_train_development']} |")
    lines+=['','## Cross-bank overlap','','| Left | Right | Shared row IDs | Shared source hashes | Shared canonical ASTs | Shared alpha skeletons | Cross-bank train/dev skeletons |','|---|---|---:|---:|---:|---:|---:|']
    for pair in result['bank_pairs']:
        lines.append(f"| {pair['left']} | {pair['right']} | {pair['shared_row_id']} | {pair['shared_source_sha256']} | {pair['shared_canonical_ast_sha256']} | {pair['shared_alpha_skeleton_sha256']} | {pair['alpha_skeletons_crossing_bank_train_development']} |")
    lines+=['','## Content and declared identities','',
        f"Content-based relation components: {result['content_relation_component_count']}; {result['components_crossing_train_development']} contain both training and development rows. This can be intentional numeric calibration, but it does not create independent structural validation.",'',
        f"Declared template IDs reused across banks with different content sets: {len(result['declared_template_ids_reused_with_different_content'])}. Declared base IDs reused with different canonical content: {len(result['declared_base_ids_reused_with_different_content'])}. Row IDs reused for different sources: {len(result['row_ids_reused_with_different_sources'])}.",'',
        f"Source preparation opportunities: {result['source_preparation_opportunities']['bank_pairs_with_shared_source_prompts']} bank pairs share exact source prompts; {result['source_preparation_opportunities']['bank_pairs_with_different_canonical_variants_on_shared_skeletons']} share structures with different canonical variant sets. These are potential discovery comparisons requiring an explicit plan, not new independent replications.",'',
        'The full machine-readable review retains collision identities, all pairwise counts and content components. The fingerprint JSONL indexes every row by source/canonical/alpha hashes and its content relation component. Bank-local labels are not used as cross-bank identities.','',
        'All original bank splits and artifacts are preserved. A passed preparation audit neither chooses a scientific hypothesis nor authorizes pooling, new final outcomes or a confirmatory model run.','']
    immutable(paths['report'],'\n'.join(lines).encode());result['report_sha256']=sha(paths['report'])
    immutable(paths['output'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    package={'status':'needs_attention' if result['status']!='passed' else 'validated_preparation','evaluation_role':ROLE,'rows':len(inventory),
        'sha256':sha(paths['inventory']),'config_hash':digest(config),'analysis_source':source,
        'review':str(paths['output']),'review_sha256':sha(paths['output']),
        'cohort_hashes':result['cohort_hashes'],'model_inference':False,'generated_holdouts_opened':False,
        'confirmatory_eligibility':False,'limitation':LIMITATION}
    immutable(paths['manifest'],(json.dumps(package,sort_keys=True,indent=2)+'\n').encode())
    return result


def audit(config):
    banks,paths=_normalize(config)
    return _emit(config,[_load_bank(bank) for bank in banks],paths)


def build(config):
    banks,paths=_normalize(config)
    for bank in banks:
        path=Path(bank['dataset']);sidecar=Path(bank['manifest'])
        if path.exists() or sidecar.exists():
            _load_bank(bank)  # refuse partial, untyped, changed or reserved artifacts
            continue
        if bank['kind']=='competition':
            from .competition import build as generate
        elif bank['kind']=='live_load':
            from .live_load import build as generate
        else:
            from .arithmetic_readout import build as generate
        generate(bank['generator_config'])
    return audit(config)
