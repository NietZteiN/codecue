"""Audited reuse of completed CV after a publication-only runner repair."""
import ast
from copy import deepcopy
from pathlib import Path

from . import relationship_capture as base
from .datasets import digest

FUNCTIONS = {'folds', 'targets', 'support', 'metrics', 'SpectralRidge', 'predict', 'weights', 'choose'}
CONSTANTS = {'ROLE', 'ALPHAS', 'RANKS', 'SEEDS', 'TASKS'}


class PublicationOnly(ast.NodeTransformer):
    """Strip the declared cache adapter and normalize output-name repair only."""
    def visit_Assign(self, node):
        if any(isinstance(t, ast.Name) and t.id == 'cache' for t in node.targets):
            return None
        return self.generic_visit(node)

    def visit_If(self, node):
        if any((isinstance(n, ast.Name) and n.id == 'cache') or
               (isinstance(n, ast.Constant) and n.value == 'cv_reuse') for n in ast.walk(node.test)):
            return None
        return self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.value = node.value.replace('final_', 'selected_')
        return node


def recipe(path):
    tree = ast.parse(Path(path).read_text())
    parts = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in FUNCTIONS:
            parts[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in CONSTANTS:
                    parts[target.id] = ast.dump(node.value, include_attributes=False)
        if isinstance(node, ast.FunctionDef) and node.name == 'run':
            parts['run'] = ast.dump(PublicationOnly().visit(deepcopy(node)), include_attributes=False)
            for inner in ast.walk(node):
                if isinstance(inner, ast.FunctionDef) and inner.name == 'features':
                    parts['features'] = ast.dump(inner, include_attributes=False)
    if set(parts) != FUNCTIONS | CONSTANTS | {'features', 'run'}:
        raise ValueError('complete archived selection recipe required')
    return digest(parts)


def verified_cache(config, source):
    request = config['cv_reuse']
    proof = base._json(request['manifest'], request['sha256'])
    old = base._json(proof['original_config'], proof['original_config_sha256'])
    if {k: v for k, v in config.items() if k not in {'run_dir', 'cv_reuse'}} != {k: v for k, v in old.items() if k != 'run_dir'}:
        raise ValueError('only output location and declared cache reference may differ for CV reuse')
    old_source = proof['original_source']
    original_manifest = base._verify_source(old, old_source)
    current_manifest = base._verify_source(config, source)
    relative = 'src/codecue/binding/arithmetic_probe_selection.py'
    old_recipe = recipe(Path(old_source['snapshot']) / relative)
    if old_recipe != recipe(Path(source['snapshot']) / relative) or old_recipe != proof['recipe_sha256']:
        raise ValueError('selection mathematics changed; cannot reuse CV')
    for name in ('arithmetic_graph_readouts.py', 'arithmetic_graph_capture.py', 'arithmetic_graph_programs.py',
                 'overnight_relationship_capture.py', 'relationship_capture.py', 'weighted_ridge.py'):
        relative = 'src/codecue/binding/' + name
        if original_manifest['code']['source_files'][relative] != current_manifest['code']['source_files'][relative]:
            raise ValueError('upstream target/feature mathematics changed; cannot reuse CV')
    cap = base._json(old['capture_config'], old['capture_config_sha256'])
    expected = {f'cv_{rep}_fold{fold}_seed{seed}.json'
        for rep in ['hidden_layer_' + str(layer) for layer in cap['layers']] + ['source_char']
        for fold in range(3) for seed in (11, 29, 47)}
    loaded = {}
    for entry in proof['entries']:
        path = Path(entry['path'])
        if path.parent != Path(old['run_dir']) or path.name not in expected or path.name in loaded:
            raise ValueError('exact original complete CV cache inventory required')
        row = base._json(path, entry['sha256'])
        if row['source'] != old_source or row['config_hash'] != digest(old) or len(row['records']) != 9:
            raise ValueError('original CV provenance differs')
        loaded[path.name] = (row, entry)
    if set(loaded) != expected:
        raise ValueError('all 45 completed CV banks required')
    return loaded
