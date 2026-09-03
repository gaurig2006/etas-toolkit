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
    
    # Fully vectorized computation using broadcasting (M x N matrix)
    # This exactly matches the requirement "vectorized temporal conditional intensity"
    # eval_t is shape (M, 1), t_hist is shape (1, N)
    dt_matrix = eval_t[:, None] - t_hist[None, :]
    
    # Causal mask: only consider events strictly before t (Delta t > 0)
    causal_mask = dt_matrix > 0
    
    # We apply the mask to dt to avoid negative values in the kernel
    # np.where is safe: shape is (M, N)
    valid_dt = np.where(causal_mask, dt_matrix, 0.0)
    
    # Evaluate Omori kernel g(t) for all valid Delta t
    g_matrix = omori_g(valid_dt, c, p)
    
    # Zero out non-causal entries
    g_matrix = np.where(causal_mask, g_matrix, 0.0)
    
    # Sum over historical events (axis 1) weighted by productivity
    # weights is shape (N,)
    intensities += np.sum(g_matrix * weights[None, :], axis=1)
    
    return intensities
