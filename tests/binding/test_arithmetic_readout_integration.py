"""Protect the distinct discovery-data contract used by the shared GPU runner."""
import json

import pytest

from codecue.binding import arithmetic_readout, checkpoint_suite
from codecue.binding.published_benchmarks import sha


def test_shared_suite_accepts_only_registered_readout_role_and_checksum(tmp_path):
    config={'dataset':str(tmp_path/'bank.jsonl'),
            'generation':{'seed':29,'numeric_per_stratum':2,'operand_max':17}}
    arithmetic_readout.build(config)
    section={'kind':'arithmetic_readout','dataset':config['dataset'],'sha256':sha(config['dataset'])}
    rows=checkpoint_suite.generated_rows(section)
    for row in rows:
        for variant,raw in [('print_direct_v3',str(row['expected_answer'])),
                            ('print_trace_long_v1',f"Checked assignments.\nAnswer: {row['expected_answer']}")]:
            case={'kind':'arithmetic_readout','record':row,'variant':variant}
            assert checkpoint_suite.score_case(case,raw)=={
                'prediction':row['expected_answer'],'valid':True,'correct':True}
    with pytest.raises(ValueError,match='checksum'):
        checkpoint_suite.generated_rows({**section,'sha256':'0'*64})
    manifest=tmp_path/'bank.manifest.json'
    data=json.loads(manifest.read_text());data['evaluation_role']='final'
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='role'):
        checkpoint_suite.generated_rows(section)
