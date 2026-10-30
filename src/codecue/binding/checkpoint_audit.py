"""Streaming public-checkpoint integrity and official single-turn token audit."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .datasets import digest, write_json


def file_hash(path, algorithm='sha256', git_blob=False):
    path=Path(path)
    result=hashlib.new(algorithm)
    if git_blob:
        result.update(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as stream:
        while block:=stream.read(8*1024*1024):
            result.update(block)
    return result.hexdigest()


def official_single_turn(sp, user):
    return [sp.bos_id()]+sp.encode(f'[INST] {user.strip()} [/INST]')


def audit_boundary(config):
    """Compare a minimal explicit-boundary correction with SentencePiece."""
    import sentencepiece
    from transformers import AutoTokenizer
    from .diagnostics import cases
    from .calibration import prompt
    from .datasets import read_jsonl
    from .registry import code_identity
    output=Path(config['output'])
    if output.exists():raise ValueError('boundary audit is immutable')
    root=Path(config['hub'])/('models--'+config['model'].replace('/','--'))/'snapshots'/config['revision']
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['revision'],local_files_only=True)
    tokenizer.add_bos_token=False
    sp=sentencepiece.SentencePieceProcessor(model_file=str(root/'tokenizer.model'))
    rows=cases(read_jsonl(config['dataset']))
    results=[]
    for row in rows:
        for variant in ('print_direct_v3','print_trace_long_v1'):
            original,_=prompt(tokenizer,row,variant)
            corrected=original.replace(tokenizer.bos_token+'[INST]',tokenizer.bos_token+' [INST]')
            content=original.removeprefix(tokenizer.bos_token)
            expected=[sp.bos_id()]+sp.encode(content)
            before=tokenizer(original,add_special_tokens=False)['input_ids']
            after=tokenizer(corrected,add_special_tokens=False)['input_ids']
            results.append(dict(id=row['id'],variant=variant,original_prompt=original,corrected_prompt=corrected,
                                original_ids=before,corrected_ids=after,reference_ids=expected,
                                original_matches=before==expected,corrected_matches=after==expected))
    result=dict(status='passed' if all(r['corrected_matches'] for r in results) else 'failed',
                checks=results,config_hash=digest(config),code=code_identity(),heldout_outcomes_opened=False,
                correction='Explicit space between serialized BOS and [INST]; require complete ID equality to raw SentencePiece')
    write_json(output,result)
    return {'status':result['status'],'cases':len(results),
            'original_matches':sum(r['original_matches'] for r in results),
            'corrected_matches':sum(r['corrected_matches'] for r in results)}


def audit_saved_tokens(config):
    """Verify every saved phase-two prompt against the raw official tokenizer."""
    import sentencepiece
    from .datasets import read_jsonl
    if Path(config['output']).exists():raise ValueError('saved-token audit is immutable')
    root=Path(config['hub'])/('models--'+config['model'].replace('/','--'))/'snapshots'/config['revision']
    sp=sentencepiece.SentencePieceProcessor(model_file=str(root/'tokenizer.model'))
    results=[]
    for file in config['responses']:
        path=Path(file)
        if not path.exists():raise ValueError('response file unavailable for full token audit')
        for row in read_jsonl(path):
            prompt=row['prompt']
            if not prompt.startswith('<s> [INST]'):raise ValueError('corrected reference boundary missing')
            expected=[sp.bos_id()]+sp.encode(prompt[len('<s> '):])
            results.append(dict(id=row['id'],variant=row['variant'],file=file,
                                match=expected==row['input_token_ids']))
    result=dict(status='passed' if results and all(r['match'] for r in results) else 'failed',
                n=len(results),checks=results,heldout_outcomes_opened=False,
                input_hashes={file:file_hash(file) for file in config['responses']})
    write_json(config['output'],result)
    return {k:v for k,v in result.items() if k!='checks'}


def run(config):
    from .registry import code_identity
    output=Path(config['output'])
    if output.exists():
        raise ValueError('checkpoint audit is immutable')
    started=time.monotonic()
    for key in ('metadata','official_reference'):
        if file_hash(config[key])!=config[key+'_sha256']:
            raise ValueError('checkpoint audit reference checksum mismatch')
    metadata=json.loads(Path(config['metadata']).read_text())
    if metadata['sha']!=config['revision']:
        raise ValueError('remote checkpoint metadata revision mismatch')
    root=Path(config['hub'])/('models--'+config['model'].replace('/','--'))/'snapshots'/config['revision']
    index=json.loads((root/'model.safetensors.index.json').read_text())
    names=set(index['weight_map'].values())|{'model.safetensors.index.json','config.json','generation_config.json',
                                           'tokenizer.model','tokenizer.json','tokenizer_config.json','special_tokens_map.json'}
    entries={row['rfilename']:row for row in metadata['siblings']}
    checks=[]
    for name in sorted(names):
        entry=entries[name]
        lfs=entry.get('lfs')
        expected=lfs['sha256'] if lfs else entry['blobId']
        actual=file_hash(root/name,'sha256' if lfs else 'sha1',git_blob=not lfs)
        checks.append(dict(name=name,bytes=(root/name).stat().st_size,expected=expected,actual=actual,match=actual==expected))
        print(f'checkpoint integrity {name}: {actual==expected}',flush=True)
    if not all(row['match'] for row in checks):
        result=dict(status='integrity_failed',files=checks,config_hash=digest(config),code=code_identity())
        write_json(output,result)
        return result
    import sentencepiece
    from transformers import AutoTokenizer
    from .diagnostics import cases
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['revision'],local_files_only=True)
    tokenizer.add_bos_token=False
    sp=sentencepiece.SentencePieceProcessor(model_file=str(root/'tokenizer.model'))
    token_checks=[]
    for row in cases([]):
        user='What does this Python 3 program print?\n\n```python\n'+row['source']+'\n```'
        prompt=tokenizer.apply_chat_template([{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
        hf=tokenizer(prompt,add_special_tokens=False)['input_ids']
        reference=official_single_turn(sp,user)
        token_checks.append(dict(id=row['id'],source=row['source'],prompt=prompt,hf_token_ids=hf,
                                 reference_token_ids=reference,match=hf==reference,
                                 first_mismatch=next((i for i,(a,b) in enumerate(zip(hf,reference)) if a!=b),None)))
    result=dict(status='passed' if all(row['match'] for row in token_checks) else 'tokenizer_mismatch',
                files=checks,token_checks=token_checks,model=config['model'],revision=config['revision'],
                metadata_sha256=config['metadata_sha256'],official_reference_url=config['official_reference_url'],
                official_reference_sha256=config['official_reference_sha256'],config_hash=digest(config),code=code_identity(),
                wall_seconds=time.monotonic()-started,model_weights_loaded=False,heldout_outcomes_opened=False,
                interpretation='Pinned public artifact bytes and single-turn tokenization only; no validation of model competence')
    write_json(output,result)
    return {k:v for k,v in result.items() if k not in ('files','token_checks','code')}
