import numpy as np
import pytest
from etas.model.kernels import omori_g, omori_g_integral
from etas.model.intensity import temporal_intensity
from etas.model.likelihood import log_likelihood
from etas.model.residuals import time_residuals

def test_single_aftershock_intensity():
    # 1 event at t=0, M=5.0
    t_hist = np.array([0.0])
    m_hist = np.array([5.0])
    
    mc = 3.0
    mu = 0.1
    K = 1.0
    alpha = 1.0
    c = 0.01
    p = 1.2
    
    # Evaluate at t=1.0
    # lambda(1.0) = mu + K * exp(alpha * (5 - 3)) * g(1.0)
    # g(1.0) = ((1.2-1)/0.01) * (1 + 1.0/0.01)^(-1.2)
    # = 20 * (101)^(-1.2)
    
    eval_t = np.array([1.0])
    lmbda = temporal_intensity(eval_t, t_hist, m_hist, mc, mu, K, alpha, c, p)
    
    g_1 = 20.0 * (101.0)**(-1.2)
    expected_lambda = mu + K * np.exp(alpha * 2.0) * g_1
    
    assert np.isclose(lmbda[0], expected_lambda)

def test_coincident_timestamps():
    # If eval_time exactly equals event_time, the causal mask (dt > 0) should drop it.
    t_hist = np.array([1.0])
    m_hist = np.array([4.0])
    
    eval_t = np.array([1.0]) # same time
    
    lmbda = temporal_intensity(eval_t, t_hist, m_hist, 3.0, 0.1, 1.0, 1.0, 0.01, 1.2)
    # Event at t=1.0 cannot trigger itself at exactly t=1.0. Intensity should just be mu.
    assert np.isclose(lmbda[0], 0.1)

def test_unsorted_input():
    t_hist_unsorted = np.array([5.0, 1.0])
    m_hist_unsorted = np.array([4.0, 5.0])
    
    t_hist_sorted = np.array([1.0, 5.0])
    m_hist_sorted = np.array([5.0, 4.0])
    
    eval_t = np.array([6.0])
    
    params = (3.0, 0.1, 1.0, 1.0, 0.01, 1.2)
    lmbda_u = temporal_intensity(eval_t, t_hist_unsorted, m_hist_unsorted, *params)
    lmbda_s = temporal_intensity(eval_t, t_hist_sorted, m_hist_sorted, *params)
    
    # The output must be identical regardless of input sorting
    assert np.isclose(lmbda_u[0], lmbda_s[0])

def test_residual_uniformity_diagnostic():
    # Generate a pure Poisson sequence (K=0), so tau_i = mu * t_i
    # The intervals dtau should be exponential with mean 1.
    np.random.seed(42)
    mu = 2.0
    N = 1000
    
    # Inter-event times for Poisson
    dt = np.random.exponential(1.0 / mu, N)
    t_hist = np.cumsum(dt)
    m_hist = np.full(N, 3.0)
    
    t_start = 0.0
    tau = time_residuals(t_hist, m_hist, t_start, 3.0, mu, 0.0, 1.0, 0.01, 1.2)
    
    dtau = np.diff(tau)
    mean_dtau = np.mean(dtau)
    
    # Mean of dtau should be approx 1.0
    assert np.isclose(mean_dtau, 1.0, atol=0.1)
