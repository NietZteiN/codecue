"""Train-only preparation helpers for alignment and complete-target probes.

These in-memory estimators do not load activations or checkpoints. Callers must
provide explicitly identified training rows. Heldout transforms reuse the fitted
centers, scales and weights without fitting or selecting any hyperparameter.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np

from .datasets import digest, write_json

ROLE = 'train_only_probe_sensitivity_preparation_v1'
LIMITATION = (
    'Preparation utilities only: no study activation bank or model is loaded. '
    'Fit guards rely on explicitly supplied training rows and identifiers. '
    'Alignment and ridge parameters are fixed before heldout transformation. '
    'Reduced-rank ridge requires one fixed complete target matrix; missing-label '
    'or per-output masked reduced-rank regression is not implemented. '
    'Synthetic selfchecks do not constitute a new scientific result.'
)


def _json_object(value, name, *, nonempty=False):
    if not isinstance(value, dict) or (nonempty and not value):
        raise ValueError(name+' must be an explicit JSON object'+(' with source provenance' if nonempty else ''))
    try:
        return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError(name+' must contain finite JSON metadata') from exc


def _fit_metadata(split, config, provenance):
    if split != 'train':
        raise ValueError("fitting requires explicit split='train'")
    config = _json_object({} if config is None else config, 'config')
    if 'split' in config and config['split'] != 'train':
        raise ValueError('configuration split conflicts with train-only fitting')
    return config, _json_object(provenance, 'provenance', nonempty=True)


def _matrix(value, name, *, n=None, width=None, min_rows=1):
    if np.ma.isMaskedArray(value):
        raise ValueError(name+' must be a complete unmasked matrix')
    try:
        raw = np.asarray(value)
        if raw.dtype.kind not in 'fiu':
            raise ValueError(name+' must be a real numeric matrix')
        matrix = np.array(raw, dtype=np.float64, copy=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name+' must be a finite real numeric matrix') from exc
    if (matrix.ndim != 2 or matrix.shape[0] < min_rows or matrix.shape[1] < 1
            or not np.isfinite(matrix).all()):
        raise ValueError(name+' must be a nonempty finite two-dimensional matrix')
    if n is not None and matrix.shape[0] != n:
        raise ValueError(name+' row count differs from paired training rows')
    if width is not None and matrix.shape[1] != width:
        raise ValueError(name+' feature width differs from the fitted transform')
    return matrix


def _ids(value, n, name):
    if isinstance(value, (str, bytes)):
        raise ValueError(name+' must be a sequence of unique nonempty string identifiers')
    try:
        identities = tuple(value)
    except TypeError as exc:
        raise ValueError(name+' must identify every training row') from exc
    if (len(identities) != n or any(not isinstance(identity, str) or not identity for identity in identities)
            or len(set(identities)) != n):
        raise ValueError(name+' must identify every row exactly once with unique nonempty strings')
    return identities


def _array_hash(value):
    array = np.ascontiguousarray(value, dtype='<f8')
    hasher = hashlib.sha256()
    hasher.update(json.dumps(list(array.shape)).encode())
    hasher.update(array.tobytes())
    return hasher.hexdigest()


def _frozen(value):
    # A bytes-backed array cannot be made writable again with setflags().
    array = np.ascontiguousarray(value, dtype=np.float64)
    return np.frombuffer(array.tobytes(), dtype=np.float64).reshape(array.shape)


@dataclass(frozen=True)
class Alignment:
    source_mean: np.ndarray
    target_mean: np.ndarray
    rotation: np.ndarray
    training_ids: tuple[str, ...]
    _metadata_json: str

    @property
    def metadata(self):
        return json.loads(self._metadata_json)

    def transform(self, x, *, ids=None):
        matrix = _matrix(x, 'transform inputs', width=self.rotation.shape[0])
        if ids is not None:
            _ids(ids, len(matrix), 'transform ids')
        return (matrix - self.source_mean) @ self.rotation + self.target_mean


def fit_alignment(source, target, *, source_ids, target_ids, split,
                  provenance, config=None):
    """Fit X -> Y orthogonal Procrustes on paired, train-centered anchors.

    Source/target rows must already be in identical identifier order. Reflections
    are allowed: the constraint is R.T @ R = I, not determinant(R) = +1.
    Rank-deficient anchors still define an optimum, which need not be unique.
    """
    user_config, provenance = _fit_metadata(split, config, provenance)
    x = _matrix(source, 'source anchors', min_rows=2)
    y = _matrix(target, 'target anchors', n=len(x), width=x.shape[1], min_rows=2)
    identities = _ids(source_ids, len(x), 'source ids')
    if _ids(target_ids, len(y), 'target ids') != identities:
        raise ValueError('source and target training ids must match in row order')
    x_mean, y_mean = x.mean(axis=0), y.mean(axis=0)
    xc, yc = x-x_mean, y-y_mean
    u, singular, vt = np.linalg.svd(xc.T @ yc, full_matrices=False)
    rotation = u @ vt
    effective = {'estimator': 'orthogonal_procrustes', 'fit_split': 'train',
        'centering': 'paired training means', 'reflections_allowed': True,
        'user_config': user_config}
    metadata = {'schema_version': 1, 'evaluation_role': ROLE, 'fit_split': 'train',
        'training_ids': list(identities), 'training_ids_sha256': digest(list(identities)),
        'n_train': len(x), 'features': x.shape[1], 'config': effective,
        'config_hash': digest(effective), 'provenance': provenance,
        'training_input_sha256': {'source': _array_hash(x), 'target': _array_hash(y)},
        'parameters_sha256': {'source_mean': _array_hash(x_mean),
            'target_mean': _array_hash(y_mean), 'rotation': _array_hash(rotation)},
        'anchor_cross_rank': int(np.linalg.matrix_rank(xc.T @ yc)),
        'anchor_cross_singular_values': singular.tolist(),
        'train_squared_error': float(np.sum((xc @ rotation-yc)**2)),
        'heldout_rows_used_for_fit': 0, 'limitation': LIMITATION}
    return Alignment(_frozen(x_mean), _frozen(y_mean), _frozen(rotation), identities,
                     json.dumps(metadata, sort_keys=True, allow_nan=False))


def transform_alignment(model, x, *, ids=None):
    if not isinstance(model, Alignment):
        raise ValueError('a fitted train-only Alignment is required')
    return model.transform(x, ids=ids)


@dataclass(frozen=True)
class ReducedRankRidge:
    x_mean: np.ndarray
    x_scale: np.ndarray
    y_mean: np.ndarray
    weights: np.ndarray
    training_ids: tuple[str, ...]
    _metadata_json: str

    @property
    def metadata(self):
        return json.loads(self._metadata_json)

    def predict(self, x, *, ids=None):
        matrix = _matrix(x, 'prediction inputs', width=self.weights.shape[0])
        if ids is not None:
            _ids(ids, len(matrix), 'prediction ids')
        return ((matrix-self.x_mean)/self.x_scale) @ self.weights+self.y_mean


def _ridge_options(alpha, rank):
    if (isinstance(alpha, bool) or not isinstance(alpha, (int, float))
            or not np.isfinite(alpha) or alpha <= 0):
        raise ValueError('ridge alpha must be finite and positive')
    if type(rank) is not int or rank < 1:
        raise ValueError('reduced rank must be a positive integer')
    return float(alpha), rank


def fit_reduced_rank_ridge(x, y, *, train_ids, split, alpha, rank,
                           provenance, config=None, target_ids=None,
                           target_mask=None):
    """Minimize ||Yc-ZW||_F² + alpha ||W||_F² subject to rank(W) <= rank.

    Z uses training-only population means/stds (constant features have scale 1).
    With G=Z.T@Z+alpha I,
    L=chol(G), C=L^-1 Z.T Yc. The best rank-r approximation C_r yields
    W=L^-T C_r. Truncating ordinary ridge W itself solves a different problem.
    """
    user_config, provenance = _fit_metadata(split, config, provenance)
    alpha, rank = _ridge_options(alpha, rank)
    if target_mask is not None:
        raise ValueError('complete-target reduced-rank ridge does not support target masks')
    x = _matrix(x, 'training features', min_rows=2)
    y = _matrix(y, 'training targets', n=len(x), min_rows=2)
    if rank > min(x.shape[1], y.shape[1]):
        raise ValueError('rank exceeds the fixed feature/target matrix dimensions')
    identities = _ids(train_ids, len(x), 'train ids')
    if target_ids is not None and _ids(target_ids, len(y), 'target ids') != identities:
        raise ValueError('target ids must match training feature ids in row order')
    x_mean, x_scale, y_mean = x.mean(axis=0), x.std(axis=0), y.mean(axis=0)
    x_scale = np.where(x_scale == 0, 1., x_scale)
    z, yc = (x-x_mean)/x_scale, y-y_mean
    gram = z.T @ z+alpha*np.eye(z.shape[1])
    try:
        lower = np.linalg.cholesky(gram)
        c = np.linalg.solve(lower, z.T @ yc)
        u, singular, vt = np.linalg.svd(c, full_matrices=False)
        reduced = (u[:, :rank]*singular[:rank]) @ vt[:rank]
        weights = np.linalg.solve(lower.T, reduced)
    except np.linalg.LinAlgError as exc:
        raise ValueError('training matrices are numerically unsuitable for reduced-rank ridge') from exc
    if not all(np.isfinite(value).all() for value in (x_mean, x_scale, y_mean, weights)):
        raise ValueError('training matrices produce nonfinite fitted parameters')
    objective = np.sum((yc-z @ weights)**2)+alpha*np.sum(weights**2)
    effective = {'estimator': 'complete_target_reduced_rank_ridge', 'fit_split': 'train',
        'alpha': alpha, 'rank': rank, 'x_normalization': 'training population mean/std; constant scale=1',
        'y_centering': 'training mean', 'target_matrix': 'fixed complete unmasked',
        'objective': '||Yc-ZW||_F^2 + alpha*||W||_F^2 with rank(W)<=rank',
        'user_config': user_config}
    metadata = {'schema_version': 1, 'evaluation_role': ROLE, 'fit_split': 'train',
        'training_ids': list(identities), 'training_ids_sha256': digest(list(identities)),
        'n_train': len(x), 'features': x.shape[1], 'targets': y.shape[1], 'config': effective,
        'config_hash': digest(effective), 'provenance': provenance,
        'training_input_sha256': {'features': _array_hash(x), 'targets': _array_hash(y)},
        'parameters_sha256': {'x_mean': _array_hash(x_mean), 'x_scale': _array_hash(x_scale),
            'y_mean': _array_hash(y_mean), 'weights': _array_hash(weights)},
        'whitened_cross_singular_values': singular.tolist(),
        'fitted_weight_rank': int(np.linalg.matrix_rank(weights)),
        'train_penalized_objective': float(objective), 'heldout_rows_used_for_fit': 0,
        'missing_targets_supported': False, 'limitation': LIMITATION}
    return ReducedRankRidge(_frozen(x_mean), _frozen(x_scale), _frozen(y_mean),
        _frozen(weights), identities, json.dumps(metadata, sort_keys=True, allow_nan=False))


def predict_reduced_rank_ridge(model, x, *, ids=None):
    if not isinstance(model, ReducedRankRidge):
        raise ValueError('a fitted train-only ReducedRankRidge is required')
    return model.predict(x, ids=ids)


def preflight(config):
    """Validate metadata and write a logged review without opening any data bank."""
    config = _json_object(config, 'preflight config')
    allowed = {'evaluation_role', 'split', 'alignment', 'reduced_rank_ridge',
               'output_review', 'provenance'}
    if set(config)-allowed:
        raise ValueError('preflight accepts metadata only; unknown keys: '+','.join(sorted(set(config)-allowed)))
    if config.get('evaluation_role') != ROLE:
        raise ValueError('explicit train-only probe preparation role required')
    _fit_metadata(config.get('split'), None, config.get('provenance'))
    alignment = config.get('alignment', {})
    ridge = config.get('reduced_rank_ridge', {})
    if (not isinstance(alignment, dict) or set(alignment)-{'enabled', 'center'}
            or alignment.get('enabled', True) is not True or alignment.get('center', True) is not True):
        raise ValueError('alignment requires train centering and a fixed orthogonal transform')
    if not isinstance(ridge, dict) or set(ridge)-{'alpha', 'rank', 'complete_targets'}:
        raise ValueError('declare fixed complete-target ridge alpha and rank')
    _ridge_options(ridge.get('alpha'), ridge.get('rank'))
    if ridge.get('complete_targets', True) is not True:
        raise ValueError('missing-target reduced-rank ridge is unsupported')
    output = config.get('output_review')
    if not isinstance(output, str) or not output.strip():
        raise ValueError('declare output_review metadata path')
    review = {'schema_version': 1, 'status': 'passed_preparation_preflight',
        'evaluation_role': ROLE, 'config': config, 'config_hash': digest(config),
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'study_fits_performed': 0, 'activation_payloads_opened': 0, 'new_model_queries': 0,
        'generated_holdouts_opened': False, 'limitation': LIMITATION}
    write_json(output, review)
    return review


def selfcheck(output_review):
    """Check synthetic rotation recovery and the rank-constrained ridge optimum."""
    rng = np.random.default_rng(125)
    x = rng.normal(size=(32, 4))
    q, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    y = x @ q+np.array([1., -2., 3., .5])
    ids = [f'synthetic_train:{index}' for index in range(len(x))]
    provenance = {'kind': 'synthetic_selfcheck', 'seed': 125, 'real_activation_bank': False}
    aligned = fit_alignment(x, y, source_ids=ids, target_ids=ids,
        split='train', provenance=provenance)
    targets = rng.normal(size=(32, 3))
    ridge = fit_reduced_rank_ridge(x, targets, train_ids=ids,
        split='train', alpha=1., rank=2, provenance=provenance)
    rotation_error = float(np.max(np.abs(aligned.transform(x)-y)))
    actual_rank = int(np.linalg.matrix_rank(ridge.weights))
    optimum = float(np.sum((targets-targets.mean(axis=0))**2)
        -np.sum(np.array(ridge.metadata['whitened_cross_singular_values'][:2])**2))
    objective_error = abs(ridge.metadata['train_penalized_objective']-optimum)
    if rotation_error > 1e-10 or actual_rank > 2 or objective_error > 1e-10:
        raise ValueError('synthetic preparation selfcheck failed')
    review = {'schema_version': 1, 'status': 'passed_synthetic_selfcheck',
        'evaluation_role': ROLE, 'synthetic_seed': 125, 'rotation_max_absolute_error': rotation_error,
        'ridge_weight_rank': actual_rank, 'ridge_optimal_objective_absolute_error': objective_error,
        'alignment': aligned.metadata, 'ridge': ridge.metadata,
        'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'study_fits_performed': 0, 'activation_payloads_opened': 0,
        'new_model_queries': 0, 'generated_holdouts_opened': False, 'limitation': LIMITATION}
    write_json(output_review, review)
    return review
