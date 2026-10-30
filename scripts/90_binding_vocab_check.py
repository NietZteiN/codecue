#!/usr/bin/env python
"""Screen semantically interpretable candidate names in all identifier contexts."""
import json
from transformers import AutoTokenizer
names='positive_chain negative_chain added_branch removed_branch plus_chain minus_chain added_chain removed_chain current_value saved_value updated_value prior_value third_branch last_branch positive_total negative_total added_total removed_total plus_total minus_total added_sum removed_sum new_value old_value live_value copy_value stored_value latest_value first_value earlier_value left_chain right_chain left_value right_value left_total right_total upper_total lower_total extra_left extra_right left_branch right_branch main_value prior_state old_state new_state current_state saved_state active_value backup_value last_value previous_value first_total second_total third_total fourth_total sum_left sum_right left_sum right_sum plus_value minus_value item_0 cell_0'.split()
tok=AutoTokenizer.from_pretrained('codellama/CodeLlama-7b-Instruct-hf',revision='22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed',local_files_only=True)
results=[]
for name in names:
    lengths=[]
    for prefix in ('','dev_','held_'):
        word=prefix+name
        per_context=[]
        for left,right in (('\n',' = 1'),('',' = 1'),('x = ',' + 1'),('x + ',')'),('(',' - 1'),('x + (',' + x)')):
            text=left+word+right
            offsets=tok(text,return_offsets_mapping=True,add_special_tokens=False)['offset_mapping']
            per_context.append(sum(a<len(left)+len(word) and b>len(left) for a,b in offsets))
        lengths.append(per_context)
    results.append({'name':name,'lengths':lengths})
neutral=next(r['lengths'] for r in results if r['name']=='item_0')
for result in results:
    result['matches_neutral_in_every_context']=result['lengths']==neutral
    print(json.dumps(result))
