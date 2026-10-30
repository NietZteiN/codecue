import sys
from types import SimpleNamespace

from codecue.binding import checkpoint_suite as suite


def test_generated_only_suite_does_not_require_public_benchmark_manifest(tmp_path, monkeypatch):
    class Tokenizer:
        def __call__(self, text, **kwargs):return {'input_ids': [100]}
        def apply_chat_template(self, messages, **kwargs):return '\n'.join(m['content'] for m in messages)
    monkeypatch.setitem(sys.modules, 'transformers', SimpleNamespace(AutoTokenizer=SimpleNamespace(
        from_pretrained=lambda *a, **k: Tokenizer())))
    import codecue.binding.model_adapter as adapter
    monkeypatch.setattr(adapter, 'configure_tokenizer', lambda *a: None)
    monkeypatch.setattr(suite, 'code_identity', lambda: {'source_sha256': 'fixture'})
    monkeypatch.setattr(suite, 'generated_rows', lambda _: [dict(id='generated', source='v0 = 2\nv0', expected_answer=2)])
    def must_not_load_assets(_):raise AssertionError('generated data is not a public release')
    monkeypatch.setattr(suite, 'assets', must_not_load_assets)
    cfg = dict(model='fixture', tokenizer_revision='a' * 40, context_limit=4096,
               sections=[dict(kind='diagnostic', name='generated', variants=['print_direct_v3'])],
               prepared_cases=str(tmp_path / 'cases.jsonl'), preflight_result=str(tmp_path / 'qa.json'))
    result = suite.preflight(cfg)
    assert result['status'] == 'passed' and result['cases'] == 1
