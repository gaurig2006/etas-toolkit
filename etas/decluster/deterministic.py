import numpy as np

def gardner_knopoff_windows(magnitudes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes deterministic time and space windows for declustering per Gardner & Knopoff (1974).
    
    Args:
        magnitudes: Array of event magnitudes.
        
    Returns:
        Tuple of (time_window_days, distance_window_km).
    """
    # Gardner and Knopoff (1974) empirical formulas
    # Time window (days)
    t_win = np.power(10.0, 0.5409 * magnitudes - 0.547)
    # Adjust for M < 6.5 vs M > 6.5 per some conventions, but standard is:
    t_win = np.where(magnitudes >= 6.5, np.power(10.0, 0.032 * magnitudes + 2.7389), t_win)
    
    # Distance window (km)
    d_win = np.power(10.0, 0.1238 * magnitudes + 0.983)
    
    return t_win, d_win

def gardner_knopoff_decluster(t: np.ndarray, x: np.ndarray, y: np.ndarray, m: np.ndarray) -> np.ndarray:
    """
    Performs deterministic Gardner-Knopoff declustering.
    Returns a boolean array where True = background (mainshock), False = aftershock.
    """
    N = len(t)
    is_mainshock = np.ones(N, dtype=bool)
    
    t_win, d_win = gardner_knopoff_windows(m)
    
    # Sort events by magnitude (descending) to find largest mainshocks first
    mag_order = np.argsort(-m)
    
    for idx in mag_order:
        if not is_mainshock[idx]:
            continue
            
        # Target event is a mainshock. Find all subsequent events within its window.
        t_target = t[idx]
        x_target = x[idx]
        y_target = y[idx]
        
        # Events after target
        future_mask = t > t_target
        
        # Within time window
        time_mask = (t - t_target) <= t_win[idx]
        
        # Within distance window
        dist_sq = (x - x_target)**2 + (y - y_target)**2
        dist_mask = dist_sq <= (d_win[idx]**2)
        
        # Mark as aftershocks
        aftershock_mask = future_mask & time_mask & dist_mask
        is_mainshock[aftershock_mask] = False
        
    return is_mainshock
