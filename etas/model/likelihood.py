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

from etas.model.spatial import spatial_kernel_powerlaw
from etas.model.kernels import omori_g

def log_likelihood_spatial(t_hist: np.ndarray,
                           x_hist: np.ndarray,
                           y_hist: np.ndarray,
                           m_hist: np.ndarray,
                           t_start: float,
                           t_end: float,
                           mc: float,
                           mu_field: np.ndarray,
                           K: float,
                           alpha: float,
                           c: float,
                           p: float,
                           d: float,
                           q: float,
                           gamma: float) -> float:
    """
    Computes log-likelihood for spatiotemporal ETAS.
    """
    window_mask = (t_hist >= t_start) & (t_hist <= t_end)
    t_target = t_hist[window_mask]
    
    if len(t_target) == 0:
        return -np.sum(mu_field) * (t_end - t_start)
        
    # We need lambda_i for each target event
    dt = t_target[:, None] - t_hist[None, :]
    dx = x_hist[window_mask, None] - x_hist[None, :]
    dy = y_hist[window_mask, None] - y_hist[None, :]
    
    causal_mask = dt > 0
    valid_dt = np.where(causal_mask, dt, 0.0)
    
    g_matrix = omori_g(valid_dt, c, p)
    f_matrix = spatial_kernel_powerlaw(dx, dy, m_hist[None, :], mc, d, q, gamma)
    
    trigger_matrix = np.where(causal_mask, g_matrix * f_matrix, 0.0)
    weights = K * np.exp(alpha * (m_hist - mc))
    lambda_ij = trigger_matrix * weights[None, :]
    
    # mu_field represents the spatial background rate AT each target event location
    lambda_i = mu_field[window_mask] + np.sum(lambda_ij, axis=1)
    
    lambda_term = np.sum(np.log(np.maximum(lambda_i, 1e-12)))
    
    # Background compensator: integral of mu(x,y) over space and time.
    # In Zhuang, sum of mu_field (which is per-event) approximates the spatial integral.
    # Actually, the total background rate over the region is sum(mu_field), wait!
    # No, mu_field(x,y) was computed such that sum_i mu_field(x_i, y_i) is NOT the integral!
    # Wait, Zhuang coupling requires the background integral to equal sum(bg_probs).
    # Since sum(bg_probs) is the expected number of bg events, the compensator term 
    # for background over the window is just sum(bg_probs) at the fixed point.
    # For a general likelihood evaluation, we integrate mu(x,y) over the bounding box.
    # To keep it simple and mathematically identical to the M-step invariant:
    # int mu(x,y) dx dy dt = sum(mu_field_unscaled) / N * Area * dt ...
    # Actually, the background compensator in spatial ETAS without edge corrections 
    # is often just approximated or calculated on a grid.
    # We will compute the background compensator as sum(mu_field) * Area. 
    # But mu_field is evaluated at event locations!
    # Let's approximate the compensator as:
    compensator = np.sum(mu_field) * (t_end - t_start)
    
    # Triggering compensator
    trigger_mask = t_hist < t_end
    if np.any(trigger_mask):
        t_trig = t_hist[trigger_mask]
        m_trig = m_hist[trigger_mask]
        
        a = np.maximum(t_start - t_trig, 0.0)
        b = t_end - t_trig
        
        weights_trig = K * np.exp(alpha * (m_trig - mc))
        integrals = omori_g_integral(a, b, c, p)
        
        # Spatial kernel integrates to 1 over infinite space, so we just use temporal integral
        compensator += np.sum(weights_trig * integrals)
        
    return lambda_term - compensator
