"""Train-only weighted ridge with one factorization for independent heads.

The normalizer matches the original unweighted StandardScaler. Weighted
centering happens afterwards, exactly as in Ridge(fit_intercept=True) supplied
with sample weights. No rank reduction, target coupling or weight rescaling is
introduced. All arrays are float64; fitting uses the smaller Gram system.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import numbers

import numpy as np

from .datasets import digest

ROLE = 'train_only_independent_weighted_ridge_v1'
PARAMETER_NAMES = ('mean', 'scale', 'coef', 'intercept', 'weighted_feature_mean', 'weighted_target_mean')
OBJECTIVE = 'sum_i weight_i * ||target_i - (standardized_feature_i @ coef + intercept)||_2^2 + alpha * ||coef||_F^2'
NORMALIZATION = 'sklearn.StandardScaler.fit(training_features), unweighted population mean/std; constant scale=1'


def _matrix(value, name, *, n=None):
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name+' must be a finite numeric matrix') from exc
    if (array.ndim != 2 or array.shape[1] < 1 or (n is not None and len(array) != n)
            or not np.isfinite(array).all()):
        raise ValueError(name+' must be a finite matrix with matching rows and positive width')
    return array


def _array_hash(array):
    array = np.ascontiguousarray(array, dtype='<f8')
    value = hashlib.sha256()
    value.update(json.dumps({'shape': list(array.shape), 'dtype': '<f8'}, sort_keys=True).encode())
    value.update(array.tobytes())
    return value.hexdigest()


def _frozen(array):
    array = np.ascontiguousarray(array, dtype=np.float64)
    return np.frombuffer(array.tobytes(), dtype=np.float64).reshape(array.shape)


def _ids(values, n):
    if isinstance(values, str):
        raise ValueError('training IDs must be an ordered collection of unique strings')
    try:
        identities = tuple(values)
    except TypeError as exc:
        raise ValueError('training IDs must be an ordered collection') from exc
    if (len(identities) != n or any(not isinstance(value, str) or not value.strip() for value in identities)
            or len(set(identities)) != n):
        raise ValueError('unique nonempty training IDs must match training rows exactly')
    return identities


def _train_split(split, n):
    if isinstance(split, str):
        valid = split == 'train'
    else:
        try:
            values = tuple(split)
            valid = len(values) == n and all(isinstance(value, str) and value == 'train' for value in values)
        except (TypeError, ValueError):
            valid = False
    if not valid:
        raise ValueError('weighted ridge fitting accepts training rows only, never development/final rows')


def _alpha(value):
    if isinstance(value, bool) or not isinstance(value, numbers.Real) or not np.isfinite(value) or value <= 0:
        raise ValueError('a fixed finite positive ridge alpha is required')
    return float(value)


def _policy(alpha, mode):
    return dict(estimator='independent_multioutput_weighted_ridge', fit_split='train',
        alpha=alpha, mode=mode, normalization=NORMALIZATION, objective=OBJECTIVE,
        intercept='unpenalized; weighted centering of standardized training features and targets',
        sample_weight='provided positive weights, used exactly without renormalization',
        output_coupling='none; one shared Gram factorization with independent right-hand sides',
        dtype='float64')


def _solve(centered_features, centered_targets, weights, alpha, mode):
    """Factor once; every target column is a separate ridge right-hand side."""
    from scipy.linalg import cho_factor, cho_solve
    root = np.sqrt(weights)
    design = centered_features*root[:, None]
    targets = centered_targets*root[:, None]
    if not np.isfinite(design).all() or not np.isfinite(targets).all():
        raise ValueError('weighted training matrices overflowed the finite ridge domain')
    if mode == 'dual_cholesky':
        gram = design@design.T
        gram.flat[::len(gram)+1] += alpha
        if not np.isfinite(gram).all():
            raise ValueError('weighted ridge dual Gram matrix overflowed')
        factor = cho_factor(gram, lower=True, overwrite_a=True, check_finite=False)
        return design.T@cho_solve(factor, targets, check_finite=False)
    if mode == 'primal_cholesky':
        gram = design.T@design
        gram.flat[::len(gram)+1] += alpha
        if not np.isfinite(gram).all():
            raise ValueError('weighted ridge primal Gram matrix overflowed')
        factor = cho_factor(gram, lower=True, overwrite_a=True, check_finite=False)
        return cho_solve(factor, design.T@targets, check_finite=False)
    raise ValueError('unknown weighted ridge factorization mode')


@dataclass(frozen=True)
class WeightedRidgeModel:
    mean: np.ndarray
    scale: np.ndarray
    coef: np.ndarray
    intercept: np.ndarray
    weighted_feature_mean: np.ndarray
    weighted_target_mean: np.ndarray
    train_ids: tuple[str, ...]
    _metadata_json: str

    @property
    def parameters(self):
        return {name: getattr(self, name) for name in PARAMETER_NAMES}

    @property
    def metadata(self):
        return json.loads(self._metadata_json)

    def predict(self, x):
        x = _matrix(x, 'prediction features')
        if x.shape[1] != len(self.mean):
            raise ValueError('prediction feature width differs from fitted training features')
        result = ((x-self.mean)/self.scale)@self.coef+self.intercept
        if not np.isfinite(result).all():
            raise ValueError('prediction features produce nonfinite weighted ridge outputs')
        return result


def fit(x, y, weights, train_ids, split, alpha=100.0):
    """Fit independent target columns on explicitly declared training rows only.

    Targets are finite real-valued matrices. A classification controller must
    separately declare and validate its one-hot class/head layout; this helper
    neither changes labels nor couples output columns.
    """
    from sklearn.preprocessing import StandardScaler
    x = _matrix(x, 'training features')
    if len(x) < 2:
        raise ValueError('at least two declared training rows are required')
    _train_split(split, len(x))
    identities = _ids(train_ids, len(x))
    y = _matrix(y, 'training targets', n=len(x))
    try:
        weights = np.asarray(weights, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('finite positive sample weights required') from exc
    if (weights.shape != (len(x),) or not np.isfinite(weights).all() or np.any(weights <= 0)
            or not np.isfinite(weights.sum())):
        raise ValueError('one finite positive sample weight per training row is required')
    alpha = _alpha(alpha)
    scaler = StandardScaler().fit(x)
    mean, scale = scaler.mean_, scaler.scale_
    if not np.isfinite(mean).all() or not np.isfinite(scale).all() or np.any(scale <= 0):
        raise ValueError('training normalization does not produce finite positive scales')
    z = scaler.transform(x)
    feature_mean = np.average(z, axis=0, weights=weights)
    target_mean = np.average(y, axis=0, weights=weights)
    centered_features, centered_targets = z-feature_mean, y-target_mean
    mode = 'dual_cholesky' if x.shape[1] > len(x) else 'primal_cholesky'
    try:
        coef = _solve(centered_features, centered_targets, weights, alpha, mode)
    except np.linalg.LinAlgError as exc:
        raise ValueError('training matrices are numerically unsuitable for weighted ridge Cholesky') from exc
    intercept = target_mean-feature_mean@coef
    parameters = dict(mean=mean, scale=scale, coef=coef, intercept=intercept,
        weighted_feature_mean=feature_mean, weighted_target_mean=target_mean)
    if not all(np.isfinite(value).all() for value in parameters.values()):
        raise ValueError('training matrices produce nonfinite weighted ridge parameters')
    policy = _policy(alpha, mode)
    metadata = dict(schema_version=1, evaluation_role=ROLE, fit_split='train',
        n_train=len(x), features=x.shape[1], targets=y.shape[1], alpha=alpha, mode=mode, dtype='float64',
        training_ids=list(identities), training_ids_sha256=digest(list(identities)),
        config=policy, config_hash=digest(policy),
        training_input_sha256={key: _array_hash(value) for key, value in
            [('features', x), ('targets', y), ('sample_weight', weights)]},
        parameters_sha256={key: _array_hash(value) for key, value in parameters.items()},
        sample_weight_sum=float(weights.sum()), factorizations=1, output_columns_independent=True,
        heldout_rows_used_for_fit=0, generated_holdouts_opened=False)
    return WeightedRidgeModel(**{key: _frozen(value) for key, value in parameters.items()},
        train_ids=identities, _metadata_json=json.dumps(metadata, sort_keys=True, allow_nan=False))


def from_parameters(metadata, parameters):
    """Restore a validated immutable model; every saved parameter is hash pinned."""
    if not isinstance(metadata, dict) or not isinstance(parameters, dict) or set(parameters) != set(PARAMETER_NAMES):
        raise ValueError('complete weighted ridge metadata and exact parameter whitelist required')
    if (metadata.get('schema_version') != 1 or metadata.get('evaluation_role') != ROLE
            or metadata.get('fit_split') != 'train' or metadata.get('heldout_rows_used_for_fit') != 0
            or metadata.get('generated_holdouts_opened') is not False
            or metadata.get('dtype') != 'float64'
            or metadata.get('factorizations') != 1 or metadata.get('output_columns_independent') is not True):
        raise ValueError('saved train-only weighted ridge role or fitting policy differs')
    n, d, k = (metadata.get(key) for key in ('n_train', 'features', 'targets'))
    if any(type(value) is not int for value in (n, d, k)) or n < 2 or d < 1 or k < 1:
        raise ValueError('saved weighted ridge dimensions differ')
    identities = _ids(metadata.get('training_ids'), n)
    if digest(list(identities)) != metadata.get('training_ids_sha256'):
        raise ValueError('saved weighted ridge training identity hash differs')
    alpha = _alpha(metadata.get('alpha'))
    mode = 'dual_cholesky' if d > n else 'primal_cholesky'
    policy = _policy(alpha, mode)
    if metadata.get('mode') != mode or metadata.get('config') != policy or metadata.get('config_hash') != digest(policy):
        raise ValueError('saved weighted ridge normalization/objective policy differs')
    pins = metadata.get('training_input_sha256', {})
    if (not isinstance(pins, dict) or set(pins) != {'features', 'targets', 'sample_weight'}
            or any(not isinstance(value, str) or len(value) != 64
                   or any(character not in '0123456789abcdef' for character in value) for value in pins.values())):
        raise ValueError('saved weighted ridge training input hash pins differ')
    weight_sum = metadata.get('sample_weight_sum')
    if isinstance(weight_sum, bool) or not isinstance(weight_sum, numbers.Real) or not np.isfinite(weight_sum) or weight_sum <= 0:
        raise ValueError('saved weighted ridge positive sample-weight total differs')
    if not isinstance(metadata.get('parameters_sha256'), dict) or set(metadata['parameters_sha256']) != set(PARAMETER_NAMES):
        raise ValueError('saved weighted ridge parameter hash whitelist differs')
    shapes = dict(mean=(d,), scale=(d,), coef=(d, k), intercept=(k,),
        weighted_feature_mean=(d,), weighted_target_mean=(k,))
    arrays = {}
    for name, shape in shapes.items():
        try:
            value = np.asarray(parameters[name], dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('saved weighted ridge parameters must be numeric') from exc
        if (value.shape != shape or not np.isfinite(value).all()
                or _array_hash(value) != metadata.get('parameters_sha256', {}).get(name)):
            raise ValueError('saved weighted ridge parameter shape/value/hash differs: '+name)
        arrays[name] = _frozen(value)
    if np.any(arrays['scale'] <= 0):
        raise ValueError('saved weighted ridge feature scales must be positive')
    return WeightedRidgeModel(**arrays, train_ids=identities,
        _metadata_json=json.dumps(metadata, sort_keys=True, allow_nan=False))
