import json
from pathlib import Path

import pytest

from codecue.binding import discovery_prediction as prediction
from codecue.binding.datasets import digest
from codecue.binding.published_benchmarks import sha


def fixture(tmp_path):
    root=tmp_path/'artifacts/binding/discovery';root.mkdir(parents=True)
    summary=root/'summary.json';summary.write_text(json.dumps({'status':'complete_exploratory','metrics':{'brier':.1}}))
    manifest=root/'features.manifest.json';manifest.write_text('{}')
    path=root/'review.json';config=dict(review_artifact=str(path),feature_manifest=str(manifest))
    review=dict(status='complete_exploratory',metrics={'brier':.1},config_hash=digest(config),feature_table_sha256='f'*64,
        feature_manifest_sha256=sha(manifest),artifacts={'summary':{'path':str(summary),'sha256':sha(summary)}})
    path.write_text(json.dumps(review));return config,{'sha256':'f'*64},review,path


def test_review_metrics_must_match_the_saved_summary_even_when_artifacts_match(tmp_path):
    cfg,manifest,review,path=fixture(tmp_path)
    assert prediction._reuse(cfg,manifest)['metrics']['brier']==.1
    review['metrics']['brier']=.9;path.write_text(json.dumps(review))
    with pytest.raises(ValueError,match='metrics differ'):prediction._reuse(cfg,manifest)


def test_protected_review_is_rejected_before_opening(tmp_path,monkeypatch):
    path=tmp_path/'artifacts/binding/final/summary.json';path.parent.mkdir(parents=True);path.write_text('{}')
    original=Path.read_text
    def guarded(p,*args,**kwargs):
        if p==path:raise AssertionError('reserved review opened')
        return original(p,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',guarded)
    with pytest.raises(ValueError):prediction._reuse({'review_artifact':str(path)}, {})


def test_protected_artifact_is_rejected_before_checksum_read(tmp_path,monkeypatch):
    cfg,manifest,review,path=fixture(tmp_path)
    protected=tmp_path/'artifacts/binding/final/responses.jsonl';protected.parent.mkdir(parents=True);protected.write_text('payload')
    review['artifacts']={'responses':{'path':str(protected),'sha256':sha(protected)}};path.write_text(json.dumps(review))
    original=prediction.sha
    def guarded(p):
        if Path(p)==protected:raise AssertionError('reserved artifact hashed')
        return original(p)
    monkeypatch.setattr(prediction,'sha',guarded)
    with pytest.raises(ValueError):prediction._reuse(cfg,manifest)
