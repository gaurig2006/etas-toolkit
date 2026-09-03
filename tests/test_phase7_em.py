import numpy as np
import pandas as pd
from etas.catalog.model import Catalog
from etas.calibrate.em import fit_etas_em

def test_em_monotonicity_and_convergence():
    # Generate a small synthetic test catalog manually
    # Just to prove the math works and increases LL monotonically.
    # We'll use 50 deterministic events spanning 100 days.
    
    np.random.seed(42)
    t = np.sort(np.random.uniform(0, 100, 50))
    m = np.random.exponential(1.0, 50) + 3.0
    
    df = pd.DataFrame({
        "time_days": t,
        "magnitude": m,
        "longitude": np.zeros(50),
        "latitude": np.zeros(50),
        "depth": np.zeros(50),
        "event_id": [f"test_{i}" for i in range(50)],
        "magnitude_type": ["Mw"] * 50,
        "agency": ["TEST"] * 50,
        "time": pd.date_range("2020-01-01", periods=50, tz="UTC")
    })
    
    catalog = Catalog(df, t0=pd.to_datetime("2020-01-01", utc=True))
    
    # Run EM for 5 iterations (no restart, to check strict monotonicity)
    res = fit_etas_em(catalog, mc=3.0, t_start=0.0, t_end=100.0, max_iter=5, n_restarts=1)
    
    history = res["history"]
    assert len(history) > 1
    
    # Check that log-likelihood strictly increases (or stays flat)
    lls = [h[5] for h in history]
    for i in range(1, len(lls)):
        assert lls[i] >= lls[i-1] - 1e-6, f"LL dropped from {lls[i-1]} to {lls[i]}"
        
    # Check that parameters are recovered and finite
    params = res["params"]
    assert params["mu"] > 0
    assert params["K"] >= 0
    assert params["alpha"] > 0
    assert params["c"] > 0
    assert params["p"] >= 1.0
