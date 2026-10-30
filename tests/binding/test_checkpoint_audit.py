import hashlib
import pytest
from codecue.binding.checkpoint_audit import file_hash,official_single_turn


def test_checkpoint_hash_streams_real_bytes_and_git_object_headers(tmp_path):
    path=tmp_path/'artifact';path.write_bytes(b'known checkpoint bytes\n')
    assert file_hash(path)==hashlib.sha256(path.read_bytes()).hexdigest()
    assert file_hash(path,'sha1',True)==hashlib.sha1(b'blob 23\0'+path.read_bytes()).hexdigest()
    previous=file_hash(path)
    path.write_bytes(b'changed checkpoint bytes\n')
    assert file_hash(path)!=previous


def test_official_reference_has_one_bos_and_no_eos():
    class SentencePiece:
        def bos_id(self):return 1
        def encode(self,text):
            assert text=='[INST] program [/INST]'
            return [23,45]
    assert official_single_turn(SentencePiece(),' program ')==[1,23,45]


def test_boundary_correction_is_explicit_idempotent_and_prefix_only():
    from types import SimpleNamespace
    from codecue.binding.model_adapter import normalize_prompt
    tok=SimpleNamespace(bos_token='<s>',binding_official_boundary=False)
    original='<s>[INST] source [/INST] Answer:'
    assert normalize_prompt(tok,original)==original
    tok.binding_official_boundary=True
    corrected=normalize_prompt(tok,original)
    assert corrected=='<s> [INST] source [/INST] Answer:'
    assert normalize_prompt(tok,corrected)==corrected
    with pytest.raises(ValueError,match='audited single-turn'):
        normalize_prompt(tok,'different format')
