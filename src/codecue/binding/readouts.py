"""Syntax-assisted distributed measurements; no semantic labels choose positions."""
from __future__ import annotations
import ast
import numpy as np
from .interpreter import parse


def latest_definition_sites(record,last_statement=None):
    statements=parse(record['canonical_source']).body[:-1]
    limit=len(statements)-1 if last_statement is None else last_statement
    if type(limit) is not int:
        raise ValueError('readout prefix must be an integer statement index')
    if not 0<=limit<len(statements):raise ValueError('readout prefix outside assignments')
    slots=record['variable_slots'];latest={}
    if (not slots or any(type(slot) is not int for slot in slots.values())
            or sorted(slots.values())!=list(range(len(slots)))):
        raise ValueError('canonical readout slots must be unique contiguous nonnegative integers')
    for index,statement in enumerate(statements[:limit+1]):
        if not isinstance(statement,ast.Assign) or not isinstance(statement.targets[0],ast.Name):
            raise ValueError('readout needs simple canonical assignments')
        name=statement.targets[0].id
        if name not in slots:raise ValueError('assignment not covered by canonical slots')
        latest[slots[name]]=index
    return {slot:f'statement:{index}' for slot,index in sorted(latest.items())}


def definition_pool(hidden,cache_row,record,layer_index,seed=17,last_statement=None):
    """Project latest-definition vectors to one hidden-width vector without labels.

    A slot-specific signed permutation makes ownership part of the measurement
    convention. The fixed projection is input-independent, untrained and lossy.
    It does not demonstrate that the model uses registers or these readout slots.
    """
    hidden=np.asarray(hidden)
    if (hidden.ndim!=3 or hidden.shape[0]!=len(cache_row['sites'])
            or len(set(cache_row['sites']))!=len(cache_row['sites']) or not hidden.shape[2]):
        raise ValueError('readout activation shape does not match cached sites')
    if type(layer_index) is not int or not 0<=layer_index<hidden.shape[1]:
        raise ValueError('readout layer index outside cached layers')
    if type(seed) is not int or seed<0:
        raise ValueError('readout projection seed must be a nonnegative integer')
    if 'id' in cache_row and 'id' in record and cache_row['id']!=record['id']:
        raise ValueError('readout record does not match activation identity')
    selected=latest_definition_sites(record,last_statement)
    width=hidden.shape[-1];result=np.zeros(width,dtype=np.float64)
    for slot,site in selected.items():
        if site not in cache_row['sites']:raise ValueError('readout definition site was not captured')
        rng=np.random.default_rng(seed+1009*slot)
        permutation=rng.permutation(width);signs=rng.integers(0,2,width)*2-1
        vector=hidden[cache_row['sites'].index(site),layer_index].astype(np.float64)
        if not np.isfinite(vector).all():raise ValueError('nonfinite activation in readout')
        result+=signs*vector[permutation]
    return result/np.sqrt(len(selected))


def definition_surface_source(record,last_statement=None):
    """Give surface controls slot/position assistance without executed values."""
    selected=latest_definition_sites(record,last_statement)
    tree=ast.parse(record['source']);lines=[]
    canonical=parse(record['canonical_source'])
    mapping=record.get('rename_map',{name:name for name in record['variable_slots']})
    if (set(mapping)!=set(record['variable_slots']) or len(set(mapping.values()))!=len(mapping)):
        raise ValueError('readout surface rename map must be a complete bijection')
    inverse={name:slot for slot,name in mapping.items()}
    class CanonicalNames(ast.NodeTransformer):
        def visit_Name(self,node):
            if node.id not in inverse:raise ValueError('surface identifier missing from readout map')
            return ast.copy_location(ast.Name(id=inverse[node.id],ctx=node.ctx),node)
    restored=CanonicalNames().visit(ast.parse(record['source']))
    if ast.dump(restored)!=ast.dump(canonical):
        raise ValueError('surface program differs from canonical readout source')
    limit=len(tree.body)-2 if last_statement is None else last_statement
    lines.extend(ast.unparse(stmt) for stmt in tree.body[:limit+1])
    for slot,site in selected.items():
        index=int(site.split(':')[1])
        lines.append(f'slot_{slot}_statement_{index}: '+ast.unparse(tree.body[index]))
    return '\n'.join(lines)
