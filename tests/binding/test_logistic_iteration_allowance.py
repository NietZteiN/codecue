import numpy as np
import pytest

from codecue.binding import discovery_prediction as cv
from codecue.binding import joint_confidence,stress_prediction
from codecue.binding.forecasting import fit_logistic


def test_longer_allowance_preserves_every_already_converged_parameter():
    rng=np.random.default_rng(17)
    x=rng.normal(size=(160,4))
    y=(x[:,0]-.4*x[:,1]+rng.normal(size=160)>.2).astype(int)
    original=fit_logistic(x,y,.1)
    extended=fit_logistic(x,y,.1,max_iterations=1000)
    assert original==extended and original['iterations']<100


@pytest.mark.parametrize('limit',[0,-1,True,None,1.5])
def test_iteration_allowance_requires_a_positive_integer(limit):
    with pytest.raises(ValueError,match='positive integer'):
        fit_logistic(np.array([[0.],[1.]]),np.array([0,1]),1.,max_iterations=limit)


def test_only_five_stress_tiers_receive_the_extended_allowance():
    config=stress_prediction.protocol()
    for name in joint_confidence.predictor_columns():
        assert cv.predictor_max_iterations(config,name)==100
    for _,_,_,name in stress_prediction.PAIRED_TIERS:
        assert cv.predictor_max_iterations(config,name)==1000
    assert cv.predictor_max_iterations(joint_confidence.protocol(),'B_joint_input')==100


@pytest.mark.parametrize('limit',[None,100,2000])
def test_new_stress_plan_requires_the_declared_fixed_numerical_policy(limit):
    config=stress_prediction.protocol()
    if limit is None:config.pop('new_predictor_max_iterations')
    else:config['new_predictor_max_iterations']=limit
    with pytest.raises(ValueError):cv._plan(config)


def test_default_predictor_call_retains_the_legacy_solver_signature(monkeypatch):
    calls=[]
    def solver(x,y,l2):
        calls.append((x.copy(),y.copy(),l2))
        return {'mean':[0.],'scale':[1.],'weights':[0.,1.],'converged':True}
    monkeypatch.setattr(cv,'fit_logistic',solver)
    model,prediction,fallback=cv.fit_predict_columns([[0.],[1.]],[0,1],[[.5]],.1)
    assert len(calls)==1 and not fallback and model['kind']=='logistic'
    assert np.isfinite(prediction).all()
