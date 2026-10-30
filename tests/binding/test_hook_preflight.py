import pytest

from codecue.binding.hook_preflight import select_cases, state_position
from codecue.binding.calibration import printed_source


def test_replay_selection_keeps_all_ownership_and_lexical_relatives():
    cases = [dict(kind='competition', record=dict(base_id=f'{available}:{base}', family='ownership',
                 available_bindings=available, lexical=lexical, swap=swap, query=query))
             for available in (2, 4) for base in range(3) for lexical in range(2)
             for swap in range(2) for query in range(2)]
    selected = select_cases(cases, 1)
    assert len(selected) == 16 and len({r['record']['base_id'] for r in selected}) == 2
    with pytest.raises(ValueError, match='insufficient'):
        select_cases(cases, 4)


def test_state_position_rejects_tokens_crossing_into_the_future_query():
    source = 'v0 = 2\nv1 = 3\nv0'
    prompt = 'User:\n' + printed_source(source) + '\nOutput:'
    case = dict(prompt=prompt, input_token_ids=list(range(len(prompt))), record=dict(source=source))
    class Tokenizer:
        def __call__(self, text, **kwargs):
            return dict(input_ids=list(range(len(text))), offset_mapping=[(i, i+1) for i in range(len(text))])
    position = state_position(Tokenizer(), case)
    assert prompt[position] == '3' and position < prompt.index('print(')
    class Leaky(Tokenizer):
        def __call__(self, text, **kwargs):
            result = super().__call__(text, **kwargs)
            result['offset_mapping'][position] = (position, position+5)
            return result
    with pytest.raises(ValueError, match='crosses the future query'):
        state_position(Leaky(), case)
