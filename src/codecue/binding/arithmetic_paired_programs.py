"""Paired retention/binding sources, structural closure and independent oracles.

Simple copy/literal programs are calibration-only: projecting rich families to
those controls destroys structural independence. No model input contains gold
traces, version labels, error labels or split metadata.
"""
import ast
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import permutations
import random
import re
import tokenize
import io

from . import interpreter
from . import arithmetic_graph_programs as graph
from . import arithmetic_local_programs as local
from .datasets import digest

ROLE = 'discovery_arithmetic_paired_sources_v1'
SEEDS = (20261101, 20261102, 20261103)
DELAYS = (0, 4, 12)
SLOTS = tuple(f'v{i}' for i in range(4))
MAPS = (dict(zip(SLOTS, SLOTS)), dict(zip(SLOTS, ('amber', 'birch', 'cedar', 'dune'))))
ORDERS = ((0, 1, 2, 3), (3, 2, 1, 0))
PROTOCOLS = ('output_only', 'intermediate_query', 'stepwise')
SCOPES = ('single', 'all')
INSTRUCTIONS = (
    'Execute assignments in order and report the printed result.',
    'Track assignments and overwrites, then give the result of print.',
    'Follow Python integer arithmetic and report the final printed values.',
)
PERMUTATIONS = tuple(permutations(range(4)))


def structural_keys(body, target=2):
    """Numeric/name/root-order invariant full and target-ancestry skeletons.

    Identity copies (including delays) do not manufacture new families. The
    ancestry key drops dead writes while retaining arithmetic/copy structure.
    """
    tree = ast.parse(body)
    if len(tree.body) < 5: raise ValueError('four roots and at least one write required')
    roots = tree.body[:4]
    if {n.targets[0].id for n in roots} != set(SLOTS): raise ValueError('four distinct root slots required')
    for node in roots:
        if any(isinstance(p, ast.Name) for p in ast.walk(node.value)):
            raise ValueError('root definitions must be independent literals')
        interpreter.value(node.value, {})
    nodes, parents, current = [], [], {i: i for i in range(4)}
    for node in tree.body[4:]:
        d = SLOTS.index(node.targets[0].id); rhs = node.value
        if isinstance(rhs, ast.Name):
            a = SLOTS.index(rhs.id)
            if d == a: continue
            record, uses = ('copy', d, a), [current[a]]
        elif isinstance(rhs, ast.BinOp) and isinstance(rhs.op, (ast.Add, ast.Sub)):
            a, b = SLOTS.index(rhs.left.id), SLOTS.index(rhs.right.id)
            record, uses = ('binary', d, a, b, '+' if isinstance(rhs.op, ast.Add) else '-'), [current[a], current[b]]
        else:
            interpreter.value(rhs, {})
            record, uses = ('literal', d), []
        nodes.append(record); parents.append(uses); current[d] = 3 + len(nodes)
    live = set()
    def visit(index):
        if index < 4 or index in live: return
        live.add(index)
        for parent in parents[index - 4]: visit(parent)
    visit(current[target])
    def key(chosen):
        alternatives = []
        for p in PERMUTATIONS:
            alternative = []
            for kind, d, *args in chosen:
                alternative.append((kind, p[d], *(p[a] if isinstance(a, int) else a for a in args)))
            alternatives.append(tuple(alternative))
        return digest(min(alternatives))
    return ('full:' + key(nodes), 'live:' + key([n for i, n in enumerate(nodes, 4) if i in live]))


def closure(key_sets):
    """Connected closure, including relatives that bridge earlier components."""
    parent = list(range(len(key_sets)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    seen = {}
    for i, keys in enumerate(key_sets):
        for key in keys:
            if key in seen:
                a, b = root(i), root(seen[key]); parent[max(a, b)] = min(a, b)
            else: seen[key] = i
    groups = defaultdict(list)
    for i in range(len(parent)): groups[root(i)].append(i)
    return list(groups.values())


def prefix_body(updates, roots=(1, 2, 3, 4), lexical=0, order=0, copy=False):
    mapping = MAPS[lexical]
    lines = [f'{mapping[SLOTS[i]]} = {roots[i]}' for i in ORDERS[order]]
    for d, a, b, op in updates:
        rhs = mapping[SLOTS[a]] if copy else f'{mapping[SLOTS[a]]} {op} {mapping[SLOTS[b]]}'
        lines.append(f'{mapping[SLOTS[d]]} = {rhs}')
    return lines


def compose(updates, roots, *, mutation='operand', delay=0, operator='+', binding_swap=None,
            mutation_value=7, lexical=0, order=0, calibration_kind=None):
    if delay not in DELAYS or operator not in ('+', '-') or mutation not in ('operand', 'irrelevant'):
        raise ValueError('declared paired intervention required')
    copy = calibration_kind == 'copy'
    lines = prefix_body(updates, roots, lexical, order, copy=copy)
    roles = ['root'] * 4 + ['prefix'] * len(updates)
    names = MAPS[lexical]; a, b, target, spare = [names[s] for s in SLOTS]
    expression = str(roots[2]) if calibration_kind == 'literal' else a if copy else f'{a} {operator} {b}'
    if binding_swap is None:
        lines.append(f'{target} = {expression}'); roles.append('target_write')
        destination = a if mutation == 'operand' else spare
        lines.append(f'{destination} = {mutation_value}'); roles.append('mutation')
    else:
        # Two independent RHS expressions; swapping destinations preserves the
        # entire current-value multiset and source token multiset.
        opposite = '-' if operator == '+' else '+'
        destinations = (spare, target) if binding_swap else (target, spare)
        for destination, rhs in zip(destinations, (expression, f'{a} {opposite} {b}')):
            lines.append(f'{destination} = {rhs}')
            roles.append('target_write' if destination == target else 'paired_write')
    for _ in range(delay): lines.append(f'{spare} = {spare}'); roles.append('delay')
    lines.append(f'{target} = {target}'); roles.append('later_use')
    return '\n'.join(lines), roles


def family_keys(updates, include_copy=False):
    keys = set()
    for op in ('+', '-'):
        for mutation in ('operand', 'irrelevant'):
            body, _ = compose(updates, (1, 2, 3, 4), operator=op, mutation=mutation)
            keys.update(structural_keys(body))
        for swap in (False, True):
            body, _ = compose(updates, (1, 2, 3, 4), operator=op, binding_swap=swap)
            keys.update(structural_keys(body))
    if include_copy:
        body, _ = compose(updates, (1, 2, 3, 4), calibration_kind='copy')
        keys.update(structural_keys(body))
    return keys


def all_prefix_live(updates):
    current = list(range(4)); parents = {}
    for i, (d, a, b, _) in enumerate(updates, 4):
        parents[i] = (current[a], current[b]); current[d] = i
    live = set()
    def visit(i):
        if i < 4 or i in live: return
        live.add(i)
        for j in parents[i]: visit(j)
    visit(current[0]); visit(current[1])
    return current[0] >= 4 and current[1] >= 4 and live == set(range(4, 4 + len(updates)))


def nondegenerate(updates):
    state = [tuple(int(i == j) for j in range(4)) for i in range(4)]
    for d, a, b, op in updates:
        state[d] = tuple(x + y if op == '+' else x - y for x, y in zip(state[a], state[b]))
    return all(any(x + sign * y for x, y in zip(state[0], state[1])) for sign in (1, -1)) and any(state[1])


@lru_cache(maxsize=1)
def families():
    excluded = {graph.canonical_key(updates) for _, _, updates in graph.structures()}
    excluded.update(graph.canonical_key(updates) for _, _, _, updates in local.structures())
    rng = random.Random(20261101); candidates, seen = [], set(excluded)
    for depth in (4, 6):
        bank = []
        for _ in range(100000):
            updates = []
            for j in range(depth):
                a, b = rng.sample(range(4), 2)
                d = (0 if j == depth - 2 else 1) if j >= depth - 2 else rng.randrange(4)
                updates.append((d, a, b, rng.choice(('+', '-'))))
            key = graph.canonical_key(updates)
            if key in seen or not all_prefix_live(updates) or not nondegenerate(updates) or len({u[3] for u in updates}) < 2: continue
            seen.add(key); bank.append(tuple(updates))
            if len(bank) == 96: break
        if len(bank) != 96: raise ValueError('finite live-prefix candidate search exhausted')
        candidates.extend(bank)
    key_sets = [family_keys(u) for u in candidates]
    groups = closure(key_sets)
    selected = []
    for depth in (4, 6):
        feasible = [g for g in groups if all(len(candidates[i]) == depth for i in g)]
        feasible.sort(key=lambda g: digest(sorted(set.union(*(key_sets[i] for i in g)))))
        if len(feasible) < 64: raise ValueError('structural closure cannot supply 96 TRAIN / 32 DEV components')
        for j, members in enumerate(feasible[:64]):
            keys = sorted(set.union(*(key_sets[i] for i in members)))
            selected.append(dict(id='paired-family:' + digest(keys)[:24],
                split='train' if j < 48 else 'development', depth=depth,
                updates=candidates[members[0]], closure_keys=keys, candidate_members=members))
    collapse = len(closure([family_keys(u, include_copy=True) for u in candidates]))
    evidence = dict(candidate_templates=len(candidates), arithmetic_components=len(groups),
        components_if_copy_relatives_joined=collapse, selected_components=len(selected),
        split_components=dict(Counter(f['split'] for f in selected)),
        exclusions='old arithmetic-graph and arithmetic-local prefix skeletons; not a new confirmation claim',
        calibration_policy='literal and copy controls remain outside probe fits because of ancestry collapse')
    return tuple(selected), evidence


def numeric_state(family, seed):
    for attempt in range(10000):
        rng = random.Random(digest([family['id'], seed, attempt]))
        roots = tuple(rng.randrange(-6, 7) for _ in range(4))
        body = '\n'.join(prefix_body(family['updates'], roots))
        try:
            trace = interpreter.execute(body + '\nv0', bound=96)
            state = trace['execution_trace'][-1]['values']
            if state['v1'] == 0: continue  # Functional same-bag binding contrast.
            for op in ('+', '-'):
                answer = state['v0'] + state['v1'] if op == '+' else state['v0'] - state['v1']
                if abs(answer) > 96: raise ValueError('target outside numeric domain')
        except ValueError: continue
        mutation = rng.choice([v for v in range(-12, 13) if v != state['v0']])
        return roots, mutation, attempt
    raise ValueError('finite prospective numeric state search exhausted')


def canonical_surface(body, lexical):
    inverse = {v: k for k, v in MAPS[lexical].items()}
    tree = ast.parse(body)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name): node.id = inverse[node.id]
    return ast.unparse(tree)


def token_bag(body):
    return Counter((t.type, t.string) for t in tokenize.generate_tokens(io.StringIO(body).readline)
        if t.type not in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL))


def row(family, seed, roots, mutation_value, operator, mutation, delay, lexical, order,
        binding_swap=None, calibration_kind=None):
    body, roles = compose(family['updates'], roots, mutation=mutation, delay=delay, operator=operator,
        binding_swap=binding_swap, mutation_value=mutation_value, lexical=lexical, order=order,
        calibration_kind=calibration_kind)
    target = MAPS[lexical]['v2']; bare = body + '\n' + target
    oracle = interpreter.execute(bare, bound=96)
    trace = oracle['execution_trace']; target_index = roles.index('target_write')
    before = trace[target_index - 1]['values']; truth = trace[target_index]['value']
    after = trace[-1]['values']; names = MAPS[lexical]
    effective_op = ('-' if operator == '+' else '+') if binding_swap else operator
    recomputed = after[names['v0']] if calibration_kind == 'copy' else roots[2] if calibration_kind == 'literal' else (
        after[names['v0']] + after[names['v1']] if effective_op == '+' else after[names['v0']] - after[names['v1']])
    opposite = before[names['v0']] - before[names['v1']] if effective_op == '+' else before[names['v0']] + before[names['v1']]
    keys = structural_keys(canonical_surface(body, lexical))
    condition = 'binding' if binding_swap is not None else 'retention'
    identity = [family['id'], seed, operator, mutation if condition == 'retention' else None,
        delay, lexical, order, binding_swap, calibration_kind]
    return dict(id='paired-case:' + digest(identity)[:24], evaluation_role=ROLE, condition='neutral',
        component_id=family['id'], split=family['split'], depth=family['depth'], numeric_seed=seed,
        lexical_realization=lexical, root_order=order, nominated_realization=(lexical == 0 and order == 0),
        contrast=condition, target_operator=effective_op, mutation=mutation if condition == 'retention' else 'none',
        binding_swap=binding_swap, delay=delay, calibration_kind=calibration_kind,
        same_bag_guaranteed_sites=['later_use', 'query'] if condition == 'binding' else [],
        body=body, roles=roles, target_name=target, slot_names=[names[s] for s in SLOTS],
        structural_keys=list(keys), target_statement=target_index, expected_answer=truth,
        final_values=[after[names[s]] for s in SLOTS], oracle=oracle,
        error_candidates=dict(correct=truth, stale_target=before[target], recomputed_current_operands=recomputed,
            **({'opposite_operator': opposite} if calibration_kind not in ('literal', 'copy') else {})),
        source_literal_values=sorted({interpreter.value(n, {}) for stmt in ast.parse(body).body
            for n in [stmt.value] if not any(isinstance(p, ast.Name) for p in ast.walk(n))}))


def iter_rows(selected=None):
    selected = families()[0] if selected is None else selected
    for family in selected:
        for seed in SEEDS:
            roots, mutation, _ = numeric_state(family, seed)
            for lexical in range(2):
                for order in range(2):
                    for delay in DELAYS:
                        for op in ('+', '-'):
                            for kind in ('operand', 'irrelevant'):
                                yield row(family, seed, roots, mutation, op, kind, delay, lexical, order)
                        for swap in (False, True):
                            yield row(family, seed, roots, mutation, '+', 'operand', delay, lexical, order, binding_swap=swap)


def calibration_rows():
    # These finite skeletons are deliberately outside all formal probe fits.
    for kind in ('literal', 'copy', 'arithmetic'):
        for depth in (0, 1, 2):
            updates = tuple((0, 0, 3, '+') for _ in range(depth))
            family = dict(id='paired-calibration:' + digest([kind, depth])[:24], split='calibration', depth=depth, updates=updates)
            for seed in SEEDS:
                roots, mutation, _ = numeric_state(family, seed)
                if kind == 'copy':
                    prefix = '\n'.join(prefix_body(updates, roots, copy=True))
                    current = interpreter.execute(prefix + '\nv0', bound=96)['expected_answer']
                    mutation = next(v for v in range(-12, 13) if v != current)
                for op in (('+', '-') if kind == 'arithmetic' else ('+',)):
                    for kind_mut in ('operand', 'irrelevant'):
                        for delay in DELAYS:
                            yield row(family, seed, roots, mutation, op, kind_mut, delay, 0, 0,
                                calibration_kind=kind if kind != 'arithmetic' else None)


def sites(row):
    tree = ast.parse(row['body']); lines = row['body'].splitlines(keepends=True)
    starts = []; cursor = 0
    for line in lines: starts.append(cursor); cursor += len(line)
    target = row['target_statement']; later = row['roles'].index('later_use')
    result = []
    for kind, index, newline in [('rhs_end', target, False), ('assignment_newline', target, True), ('later_use', later, False)]:
        node = tree.body[index]; stop = starts[node.end_lineno - 1] + node.end_col_offset
        if newline:
            if row['body'][stop:stop + 1] != '\n': raise ValueError('assignment newline missing')
            stop += 1
        point = row['oracle']['execution_trace'][index]
        prefix = row['body'][:stop]
        visible = {interpreter.value(n.value, {}) for n in ast.parse(prefix).body
            if isinstance(n, ast.Assign) and not any(isinstance(p, ast.Name) for p in ast.walk(n.value))}
        result.append(dict(kind=kind, statement=index, stop=stop, value=point['values'][row['target_name']],
            values=[point['values'][n] for n in row['slot_names']],
            versions=[point['versions'][n] for n in row['slot_names']],
            read_definitions=[u['definition'] for u in point['uses']], target_literal_visible=point['values'][row['target_name']] in visible,
            same_bag_control_matched=(kind in row['same_bag_guaranteed_sites'])))
    return result


def prompt_content(row, scope, protocol, instruction):
    if scope not in SCOPES or protocol not in PROTOCOLS or instruction not in range(3):
        raise ValueError('declared prompt factorial required')
    query = row['target_name'] if scope == 'single' else ', '.join(row['slot_names'])
    source = row['body'] + '\nprint(' + query + ')'
    suffix = INSTRUCTIONS[instruction]
    if protocol == 'intermediate_query':
        suffix += f" First state {row['target_name']}'s value immediately after line {row['target_statement'] + 1}."
    elif protocol == 'stepwise': suffix += ' Explain the assignments step by step before the final answer.'
    if scope == 'single': suffix += ' End with exactly Answer: followed by one signed integer.'
    else: suffix += ' End with exactly Answer: followed by a bracketed list of the four signed integers in print argument order.'
    return 'Execute this Python program.\n```python\n' + source + '\n```\n' + suffix


def parse_answer(text, scope):
    if scope not in SCOPES: raise ValueError('known query scope required')
    matches = re.findall(r'(?m)^\s*Answer:[ \t]*([^\r\n]*)', text)
    if not matches: return dict(valid=False, reason='missing_answer')
    answer = matches[-1].strip()
    pattern = r'[+-]?\d+' if scope == 'single' else r'\[[ \t]*[+-]?\d+(?:[ \t]*,[ \t]*[+-]?\d+){3}[ \t]*\]'
    if not re.fullmatch(pattern, answer): return dict(valid=False, reason='invalid_answer_shape')
    try: values = [int(v) for v in re.findall(r'[+-]?\d+', answer)]
    except ValueError: return dict(valid=False, reason='invalid_integer')
    return dict(valid=True, values=values)


def validate_one(record, independent=None):
    oracle = interpreter.execute(record['body'] + '\n' + record['target_name'], bound=96)
    if oracle != record['oracle'] or oracle['expected_answer'] != record['expected_answer']:
        raise ValueError('versioned oracle or expected value differs')
    if [oracle['execution_trace'][-1]['values'][n] for n in record['slot_names']] != record['final_values']:
        raise ValueError('four-variable oracle differs')
    if list(structural_keys(canonical_surface(record['body'], record['lexical_realization']))) != record['structural_keys']:
        raise ValueError('structural identity differs')
    if independent is not None:
        if independent['answer'] != record['expected_answer'] or independent['trace'] != [w['values'] for w in oracle['execution_trace']]:
            raise ValueError('independent Python trace differs')
    if record['contrast'] == 'retention':
        if record['mutation'] == 'operand' and record['calibration_kind'] != 'literal' and record['error_candidates']['recomputed_current_operands'] == record['expected_answer']:
            raise ValueError('operand intervention lacks functional diagnostic')
        if record['mutation'] == 'irrelevant' and record['error_candidates']['recomputed_current_operands'] != record['expected_answer']:
            raise ValueError('irrelevant intervention changed target operands')
    sites(record)
    return True
