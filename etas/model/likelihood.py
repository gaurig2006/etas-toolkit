import numpy as np
from .intensity import temporal_intensity
from .kernels import omori_g_integral

def log_likelihood(event_times: np.ndarray, 
                   event_mags: np.ndarray, 
                   t_start: float, 
                   t_end: float,
                   mc: float, 
                   mu: float, 
                   K: float, 
                   alpha: float, 
                   c: float, 
                   p: float) -> float:
    """
    Computes Ogata's incomplete log-likelihood for the temporal ETAS model over [t_start, t_end].
    
    Cites: 01 Ogata 1988, Eq. 4.
    Formula: LL = sum_{t_i in [t_start, t_end]} log(lambda(t_i)) - Lambda(t_start, t_end)
    where Lambda is the integrated conditional intensity (the compensator).
    
    Args:
        event_times: Array of all historical event times.
        event_mags: Array of all historical event magnitudes.
        t_start: Start time of the observation window.
        t_end: End time of the observation window.
        mc: Magnitude of completeness.
        mu: Background rate.
        K, alpha, c, p: ETAS parameters.
        
    Returns:
        The scalar log-likelihood value.
    """
    t_hist = np.asarray(event_times)
    m_hist = np.asarray(event_mags)
    
    # Target events falling within the window
    window_mask = (t_hist >= t_start) & (t_hist <= t_end)
    t_target = t_hist[window_mask]
    
    if len(t_target) == 0:
        # If no events in window, LL is just the negative compensator
        lambda_term = 0.0
    else:
        # 1. Event term: sum(log(lambda(t_i)))
        # Intensity must be evaluated considering ALL events prior to t_i (even those before t_start)
        lmbda = temporal_intensity(t_target, t_hist, m_hist, mc, mu, K, alpha, c, p)
        # Protect against log(0)
        lmbda = np.maximum(lmbda, 1e-12)
        lambda_term = np.sum(np.log(lmbda))
        
    # 2. Compensator term: Lambda(t_start, t_end)
    # Background compensator
    compensator = mu * (t_end - t_start)
    
    # Triggering compensator: integral of each event's kernel from max(t_start, t_i) to t_end
    # Only events before t_end can trigger inside the window
    trigger_mask = t_hist < t_end
    if np.any(trigger_mask):
        t_trig = t_hist[trigger_mask]
        m_trig = m_hist[trigger_mask]
        
        # Integration bounds relative to each event time t_i
        a = np.maximum(t_start - t_trig, 0.0)
        b = t_end - t_trig
        
        weights = K * np.exp(alpha * (m_trig - mc))
        integrals = omori_g_integral(a, b, c, p)
        
        compensator += np.sum(weights * integrals)
        
    return lambda_term - compensator
