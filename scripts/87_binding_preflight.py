#!/usr/bin/env python
"""CPU tokenizer and hook validation. Random tiny model is a software test only."""
import json
import sys
import tempfile
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, LlamaConfig, LlamaForCausalLM
from codecue.binding.datasets import read_jsonl, write_json
from codecue.binding.model_adapter import prompt_for, layout, score_answers,configure_tokenizer
from codecue.binding.interventions import residual_patch
from codecue.binding.probes import fit_ridge, predict, metrics
from codecue.patching import decoder_layers

config = json.loads(Path(sys.argv[1]).read_text())
tok = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
configure_tokenizer(tok,config)
tok.pad_token = tok.eos_token
tok.padding_side = 'left'
rows = read_jsonl(config['dataset'])
# Token offsets of all naming variants and program structures; semantic test labels stay sealed.
for row in rows:
    prompt = prompt_for(tok, row, config['protocol'])
    result = layout(tok, row, prompt)
    assert all(0 <= p < len(result['input_ids']) for p in result['positions'].values())
torch.manual_seed(17)
model = LlamaForCausalLM(LlamaConfig(vocab_size=len(tok), hidden_size=16, intermediate_size=32,
    num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2,
    attn_implementation='eager')).eval()
prompt = prompt_for(tok, rows[0], config['protocol'])
aligned = layout(tok, rows[0], prompt)
ids = torch.tensor([aligned['input_ids']])
from codecue.binding.generation_reference import greedy_reference
from codecue.models import generate_free
reference = greedy_reference(tok, model, aligned['input_ids'], 3)
cached = generate_free(tok, model, [prompt], 3, 1)
assert reference['raw_response'] == cached[0], 'uncached reference differs on tiny random model'
pos = aligned['positions']['source_final']
block = decoder_layers(model)[0]
captured = []
handle = block.register_forward_hook(lambda m,a,o: captured.append((o[0] if isinstance(o, tuple) else o)[0,pos].detach().clone()))
with torch.inference_mode():
    original = model(input_ids=ids, use_cache=False).logits
handle.remove()
with torch.inference_mode(), residual_patch(block, pos, captured[0]):
    same = model(input_ids=ids, use_cache=False).logits
assert torch.equal(original, same), 'self patch changes logits'
assert not block._forward_hooks, 'hook leaked'
# Patching beyond a cached one-token generation step must be skipped safely.
with residual_patch(block, pos, captured[0]), torch.inference_mode():
    model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=2,
                   do_sample=False, pad_token_id=tok.eos_token_id)
assert not block._forward_hooks
scores = score_answers(tok, model, prompt, [-12, 0, 7, 64])
assert len(scores['scores']) == 4
assert all(np.isfinite(s['log_likelihood_sum']) for s in scores['scores'])
rng = np.random.default_rng(4)
x = rng.normal(size=(100, 8))
y = np.rint(x @ rng.normal(size=(8,4)))
fitted = fit_ridge(x[:80], y[:80], alpha=0.01)
pred = predict(fitted, x[80:])
assert metrics(pred,y[80:])['slot_exact_accuracy'] > 0.7
from codecue.binding import model_adapter
from codecue.binding.behavior import run as run_behavior
from codecue.binding.activations import extract
from codecue.binding.probes import fit
from codecue.binding.interventions import run as run_assay
original_loader = model_adapter.load
try:
    model_adapter.load = lambda cfg: (tok, model)
    with tempfile.TemporaryDirectory(prefix='codecue-binding-software-') as temporary:
        test_config = {**config, 'device': 'cpu', 'dtype': 'float32', 'layers': [0, 1],
                       'run_dir': temporary, 'control_kinds': ['primary'], 'per_cell_limit': 4,
                       'max_new_tokens': 2, 'max_gpu_seconds': 3600, 'software_test_only': True,
                       'intervention': {'split': 'development', 'layers': [0], 'per_cell_limit': 1,
                                        'quantity_queries':['v0','v1','v2','v3']}}
        behavior_check = run_behavior(test_config)
        extraction_check = extract(test_config)
        test_config['probe_analysis']={'readouts':['last_assignment','source_final','definition_pool']}
        probe_check = fit(test_config)
        assay_check = run_assay(test_config)
        assert behavior_check['complete'] and extraction_check['complete']
        assert probe_check['results'] == 162
        assay_summary=json.loads(Path(assay_check['summary']).read_text())
        assert assay_summary['complete']
        # Only completion flags persist. All random-network responses, activations,
        # probes and assay scores are temporary software fixtures, not experiments.
finally:
    model_adapter.load = original_loader
report = {'status': 'passed', 'software_test_only': True, 'model_experiment': False,
          'tokenizer_revision': config['tokenizer_revision'], 'aligned_programs': len(rows),
          'protocol':config['protocol'],
          'self_patch_bitwise_equal': True, 'hook_cleanup': True, 'cached_generation_safe': True,
          'complete_candidate_scores': scores, 'ridge_recovery': metrics(pred,y[80:]),
          'temporary_random_network_workflows': ['behavior', 'extraction', 'probes', 'intervention_assay']}
write_json(Path(config['dataset']).with_suffix('.'+config['protocol']+'.preflight.json'), report)
print(json.dumps(report,indent=2))
