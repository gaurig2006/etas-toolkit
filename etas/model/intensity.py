import numpy as np
from .kernels import omori_g

def temporal_intensity(eval_times: np.ndarray, 
                       event_times: np.ndarray, 
                       event_mags: np.ndarray, 
                       mc: float, 
                       mu: float, 
                       K: float, 
                       alpha: float, 
                       c: float, 
                       p: float) -> np.ndarray:
    """
    Evaluates the temporal conditional intensity lambda(t) at given evaluation times.
    
    Cites: 01 Ogata 1988, Eq. 2 (pure temporal marginal).
    Formula: lambda(t) = mu + sum_{t_i < t} K * exp(alpha * (M_i - Mc)) * g(t - t_i)
    
    Args:
        eval_times: Array of times at which to evaluate the intensity (size M).
        event_times: Array of historical event times (size N). Must be sorted.
        event_mags: Array of historical event magnitudes (size N).
        mc: Magnitude of completeness cutoff.
        mu: Background rate.
        K: Baseline productivity.
        alpha: Productivity scaling.
        c: Omori c parameter.
        p: Omori p parameter.
        
    Returns:
        Array of intensity values at each eval_time (size M).
    """
    # Ensure inputs are sorted arrays for safety if not already
    sort_idx = np.argsort(event_times)
    t_hist = np.asarray(event_times)[sort_idx]
    m_hist = np.asarray(event_mags)[sort_idx]
    eval_t = np.asarray(eval_times)
    
    intensities = np.full(len(eval_t), mu, dtype=float)
    
    # Precompute productivity weights
    weights = K * np.exp(alpha * (m_hist - mc))
    
    # Vectorized computation
    # For very large catalogs, a double loop is slow in Python, but broadcasting works
    # if M and N are moderate. For enormous arrays, we might chunk or use numba later.
    for i, t in enumerate(eval_t):
        # Causal mask: only consider events strictly before t
        # (Delta t > 0 is enforced)
        valid_idx = t_hist < t
        if not np.any(valid_idx):
            continue
            
        dt = t - t_hist[valid_idx]
        g_vals = omori_g(dt, c, p)
        
        intensities[i] += np.sum(weights[valid_idx] * g_vals)
        
    return intensities
