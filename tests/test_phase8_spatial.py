import numpy as np
import pytest
from etas.model.spatial import spatial_kernel_powerlaw
from etas.calibrate.kde import background_kde
from etas.calibrate.bandwidth import optimize_bandwidth_cv

def test_spatial_kernel_normalization():
    # Numerically integrate the spatial kernel to ensure it integrates to 1
    # over a large enough grid
    
    mc = 3.0
    m = np.array([5.0])
    d = 2.0
    q = 1.5
    gamma = 1.0
    
    # Grid from -100 to 100 km
    x = np.linspace(-100, 100, 500)
    y = np.linspace(-100, 100, 500)
    xx, yy = np.meshgrid(x, y)
    
    # 1D arrays for the kernel
    dx = xx.ravel()
    dy = yy.ravel()
    
    f_vals = spatial_kernel_powerlaw(dx, dy, m, mc, d, q, gamma)
    
    # Cell area
    cell_area = (x[1] - x[0]) * (y[1] - y[0])
    
    integral = np.sum(f_vals) * cell_area
    
    # Should be close to 1.0. (Won't be exactly 1 due to finite bounds)
    assert integral > 0.85
    assert integral < 1.05

def test_bandwidth_cv():
    np.random.seed(42)
    # Generate 2 distinct clusters
    x1 = np.random.normal(0, 1, 50)
    y1 = np.random.normal(0, 1, 50)
    
    x2 = np.random.normal(10, 1, 50)
    y2 = np.random.normal(10, 1, 50)
    
    event_x = np.concatenate([x1, x2])
    event_y = np.concatenate([y1, y2])
    bg_probs = np.ones(100)
    
    h_candidates = np.array([0.1, 1.0, 5.0, 20.0])
    
    best_h = optimize_bandwidth_cv(event_x, event_y, bg_probs, h_candidates)
    
    # Best bandwidth should be around 1.0 (the standard deviation of the clusters)
    assert best_h == 1.0
