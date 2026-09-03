import numpy as np
from etas.model.kernels import omori_g
from typing import Tuple

def e_step(event_times: np.ndarray, 
           event_mags: np.ndarray, 
           mc: float, 
           mu: float, 
           K: float, 
           alpha: float, 
           c: float, 
           p: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes the Expectation step (E-step) of the EM algorithm.
    
    Cites: 02 Veen & Schoenberg 2008, Eq. 4, 5.
    
    Args:
        event_times: Sorted array of event times (size N).
        event_mags: Array of event magnitudes (size N).
        mc: Magnitude of completeness.
        mu, K, alpha, c, p: Current ETAS parameters.
        
    Returns:
        Tuple of (bg_probs, rho_matrix, intensities).
        - bg_probs: Array of background probabilities (size N).
        - rho_matrix: 2D array (N x N) where rho[i, j] is the probability 
          that event j triggered event i. (Lower triangular, since t_j < t_i).
        - intensities: The total conditional intensity at each event time.
    """
    N = len(event_times)
    
    # eval_t - t_hist: dt[i, j] = t_i - t_j
    # i is the target event, j is the potential parent
    dt = event_times[:, None] - event_times[None, :]
    
    causal_mask = dt > 0
    valid_dt = np.where(causal_mask, dt, 0.0)
    
    g_matrix = omori_g(valid_dt, c, p)
    g_matrix = np.where(causal_mask, g_matrix, 0.0)
    
    # Productivity weights of parents (j)
    weights = K * np.exp(alpha * (event_mags - mc))
    
    # Triggering rates lambda_{ij}
    lambda_ij = g_matrix * weights[None, :]
    
    # Total intensity at event i
    lambda_i = mu + np.sum(lambda_ij, axis=1)
    
    # Protect against division by zero
    lambda_i_safe = np.maximum(lambda_i, 1e-12)
    
    # Background probabilities
    bg_probs = mu / lambda_i_safe
    
    # Triggering probabilities rho_{ij}
    rho_matrix = lambda_ij / lambda_i_safe[:, None]
    
    # Enforce strict invariant: bg_i + sum_j rho_ij = 1.0
    # Any small floating point drift is corrected by normalizing
    row_sums = bg_probs + np.sum(rho_matrix, axis=1)
    
    bg_probs = bg_probs / row_sums
    rho_matrix = rho_matrix / row_sums[:, None]
    
    return bg_probs, rho_matrix, lambda_i

from etas.model.spatial import spatial_kernel_powerlaw

def e_step_spatial(t_hist: np.ndarray, 
                   x_hist: np.ndarray, 
                   y_hist: np.ndarray, 
                   m_hist: np.ndarray, 
                   mc: float, 
                   mu_field: np.ndarray, 
                   K: float, 
                   alpha: float, 
                   c: float, 
                   p: float,
                   d: float,
                   q: float,
                   gamma: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes the spatial Expectation step (E-step) of the EM algorithm.
    """
    dt = t_hist[:, None] - t_hist[None, :]
    dx = x_hist[:, None] - x_hist[None, :]
    dy = y_hist[:, None] - y_hist[None, :]
    
    causal_mask = dt > 0
    valid_dt = np.where(causal_mask, dt, 0.0)
    
    g_matrix = omori_g(valid_dt, c, p)
    f_matrix = spatial_kernel_powerlaw(dx, dy, m_hist[None, :], mc, d, q, gamma)
    
    # zero out non-causal
    trigger_matrix = np.where(causal_mask, g_matrix * f_matrix, 0.0)
    
    weights = K * np.exp(alpha * (m_hist - mc))
    lambda_ij = trigger_matrix * weights[None, :]
    
    lambda_i = mu_field + np.sum(lambda_ij, axis=1)
    lambda_i_safe = np.maximum(lambda_i, 1e-12)
    
    bg_probs = mu_field / lambda_i_safe
    rho_matrix = lambda_ij / lambda_i_safe[:, None]
    
    row_sums = bg_probs + np.sum(rho_matrix, axis=1)
    bg_probs = bg_probs / row_sums
    rho_matrix = rho_matrix / row_sums[:, None]
    
    return bg_probs, rho_matrix, lambda_i
