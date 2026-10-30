#!/usr/bin/env python
"""Input-design and tokenizer balance audit; never loads model weights."""
import json
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from codecue.binding.datasets import read_jsonl, write_json
from codecue.binding.model_adapter import prompt_for, layout

config=json.loads(Path(sys.argv[1]).read_text())
rows=[r for r in read_jsonl(config['dataset']) if r['control_kind']=='primary']
tok=AutoTokenizer.from_pretrained(config['model'],revision=config['tokenizer_revision'],local_files_only=True)
counts, groups = {}, defaultdict(list)
for row in rows:
    aligned=layout(tok,row,prompt_for(tok,row,config['protocol']))
    counts[row['id']]=aligned['token_counts']
    groups[(row['condition'],row['split'],row['lexical_realization'])].append(row)
condition_features=[]
for (condition,split,lexical),group in sorted(groups.items()):
    condition_features.append(dict(condition=condition,split=split,lexical_realization=lexical,n=len(group),
        prompt_tokens_mean=float(np.mean([counts[r['id']]['prompt'] for r in group])),
        source_tokens_mean=float(np.mean([counts[r['id']]['source'] for r in group])),
        identifier_token_lengths=dict(Counter(str(n) for r in group for ns in counts[r['id']]['identifiers'].values() for n in ns))))
paired=defaultdict(dict)
for row in rows:
    paired[(row['base_id'],row['lexical_realization'])][row['condition']]=row
pair_effects=[]
for condition in ('informative','misleading'):
    differences=[]
    for group in paired.values():
        differences.append(counts[group[condition]['id']]['prompt']-counts[group['neutral']['id']]['prompt'])
    pair_effects.append(dict(condition=condition,n=len(differences),exact_length_match_fraction=float(np.mean(np.array(differences)==0)),
                            min_delta=min(differences),max_delta=max(differences),mean_delta=float(np.mean(differences))))
cells=defaultdict(list)
for row in rows:
    if row['condition']=='neutral' and row['lexical_realization']==0:
        cells[(row['family'],row['load'],row['updates'])].append(row)
cell_features=[]
for (family,load,updates),group in sorted(cells.items()):
    feature_names=('arithmetic_operations','statements','dependency_depth','max_liveness','assignment_distance','answer_magnitude',
                   'computed_values_absent_from_literals','computed_assignments','copy_assignments','literal_assignments')
    cell_features.append(dict(family=family,load=load,updates=updates,n=len(group),
       magnitude_bins=dict(Counter(str(r['answer_magnitude_bin']) for r in group)),
       features={name:dict(mean=float(np.mean([r['features'][name] for r in group])),
                          min=min(r['features'][name] for r in group),max=max(r['features'][name] for r in group)) for name in feature_names}))
result={'status':'input_design_audited','model_experiment':False,'tokenizer_revision':config['tokenizer_revision'],
        'protocol':config['protocol'],'dataset_sha256':hashlib.sha256(Path(config['dataset']).read_bytes()).hexdigest(),
        'primary_rows':len(rows),'condition_features':condition_features,'paired_token_counts':pair_effects,'cell_features':cell_features,
        'remaining_limitations':['within-bin answer distributions are not exactly matched',
          'update manipulations change depth and arithmetic work','heldout identifier roots/subwords overlap',
          'naming cues may directly steer answers without a binding failure']}
path=Path(config['dataset']).with_suffix('.'+config['protocol']+'.design_audit.json')
write_json(path,result)
print(json.dumps({'artifact':str(path),'paired_token_counts':pair_effects,'primary_rows':len(rows)},indent=2))
