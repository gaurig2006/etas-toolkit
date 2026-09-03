import numpy as np
from scipy.optimize import minimize, root_scalar
from etas.model.kernels import omori_g_integral
from typing import Tuple

def m_step(event_times: np.ndarray, 
           event_mags: np.ndarray,
           t_start: float,
           t_end: float,
           mc: float,
           bg_probs: np.ndarray,
           rho_matrix: np.ndarray,
           c_current: float,
           p_current: float) -> Tuple[float, float, float, float, float]:
    """
    Computes the Maximization step (M-step) of the EM algorithm.
    
    Cites: 02 Veen & Schoenberg 2008, Section 4.
    
    Args:
        event_times: Sorted array of event times (size N).
        event_mags: Array of event magnitudes (size N).
        t_start: Start of observation window.
        t_end: End of observation window.
        mc: Magnitude of completeness.
        bg_probs: Background probabilities (size N).
        rho_matrix: Triggering probabilities (N x N).
        c_current, p_current: Current values of numerical parameters.
        
    Returns:
        Tuple of new parameters (mu, K, alpha, c, p).
    """
    T = t_end - t_start
    N = len(event_times)
    
    # Target events falling in window
    window_mask = (event_times >= t_start) & (event_times <= t_end)
    bg_window = bg_probs[window_mask]
    
    # 1. Update mu
    # \hat{\mu} = sum(bg_i) / T
    mu_new = np.sum(bg_window) / T
    
    # Pre-calculate sums for K and alpha
    # rho_matrix is strictly causal, so we can sum over all elements safely
    sum_rho = np.sum(rho_matrix)  # Total expected triggered events
    
    # We need the integrated kernels for all events that could trigger within the window
    trigger_mask = event_times < t_end
    t_trig = event_times[trigger_mask]
    m_trig = event_mags[trigger_mask]
    
    a = np.maximum(t_start - t_trig, 0.0)
    b = t_end - t_trig
    
    # Integrals using CURRENT c, p
    G_vals = omori_g_integral(a, b, c_current, p_current)
    
    # 2. Update alpha (1D root finding)
    # Equation: sum_{i>j} rho_ij (m_j - mc) - K * sum_j (m_j - mc) e^{alpha(m_j - mc)} G_j = 0
    # But K itself depends on alpha: K = sum_rho / sum_j e^{alpha(m_j - mc)} G_j
    # So we substitute K to get an equation purely in alpha:
    # sum_rho_m = sum_rho * [sum_j (m_j - mc) e^{alpha...} G_j] / [sum_j e^{alpha...} G_j]
    
    # We need sum_{i>j} rho_ij * (m_j - mc)
    dm = m_trig - mc
    # Sum of rho columns gives total offspring per parent
    rho_col_sums = np.sum(rho_matrix[:, trigger_mask], axis=0)
    
    target_sum_rho_m = np.sum(rho_col_sums * dm)
    
    def alpha_objective(alpha_val):
        E = np.exp(alpha_val * dm)
        num = np.sum(dm * E * G_vals)
        den = np.sum(E * G_vals)
        # Avoid division by zero
        if den == 0:
            return 1e9
        return target_sum_rho_m - sum_rho * (num / den)
    
    try:
        # Typical alpha values are between 0 and 3
        res = root_scalar(alpha_objective, bracket=[0.0, 5.0], method='brentq')
        alpha_new = res.root
    except ValueError:
        # Fallback if bracket fails
        alpha_new = 1.0 # arbitrary safe fallback
        
    # 3. Update K
    E_new = np.exp(alpha_new * dm)
    den_K = np.sum(E_new * G_vals)
    K_new = sum_rho / den_K if den_K > 0 else 0.0
    
    # 4. Update c, p (Numerical optimization)
    # The objective for c, p only involves the rho_ij log(g) term and the K G_j term.
    # Q_{c,p} = sum_{i, j} rho_ij log g(t_i - t_j; c, p) - K * sum_j e^{alpha(m_j - mc)} G_j(c, p)
    
    # Get all valid (i, j) pairs where rho_ij > 1e-6 for efficiency
    i_idx, j_idx = np.nonzero(rho_matrix > 1e-8)
    dt_pairs = event_times[i_idx] - event_times[j_idx]
    rho_pairs = rho_matrix[i_idx, j_idx]
    
    def cp_neg_q(params):
        c_val, p_val = params
        
        # log g(t)
        log_g = np.log((p_val - 1.0) / c_val) - p_val * np.log1p(dt_pairs / c_val)
        term1 = np.sum(rho_pairs * log_g)
        
        # Integrals
        G_j = omori_g_integral(a, b, c_val, p_val)
        term2 = K_new * np.sum(E_new * G_j)
        
        # We want to maximize Q, so we return -Q
        return -(term1 - term2)
        
    bounds = [(1e-5, 1.0), (1.001, 3.0)] # c > 0, p > 1
    init_guess = [c_current, p_current]
    
    opt_res = minimize(cp_neg_q, init_guess, bounds=bounds, method='L-BFGS-B')
    c_new, p_new = opt_res.x
    
    return mu_new, K_new, alpha_new, c_new, p_new

from etas.model.spatial import spatial_kernel_powerlaw

def m_step_spatial(t_hist: np.ndarray, 
                   x_hist: np.ndarray, 
                   y_hist: np.ndarray, 
                   m_hist: np.ndarray, 
                   t_start: float,
                   t_end: float,
                   mc: float, 
                   bg_probs: np.ndarray, 
                   rho_matrix: np.ndarray, 
                   c_current: float, 
                   p_current: float,
                   d_current: float,
                   q_current: float,
                   gamma_current: float) -> Tuple[float, float, float, float, float, float, float]:
    """
    Computes the spatial M-step.
    In the Zhuang model, mu(x,y) is updated in the KDE step (coupling loop), so we don't 
    return mu_new here.
    The integral of the spatial kernel is exactly 1 over infinite space, so K and alpha 
    updates are mathematically identical to the temporal-only case, assuming we don't 
    apply spatial boundary edge-corrections.
    d, q, gamma are optimized numerically just like c, p.
    """
    _, K_new, alpha_new, c_new, p_new = m_step(
        t_hist, m_hist, t_start, t_end, mc, bg_probs, rho_matrix, c_current, p_current
    )
    
    # Numerical optimization for spatial parameters: d, q, gamma
    i_idx, j_idx = np.nonzero(rho_matrix > 1e-8)
    dx_pairs = x_hist[i_idx] - x_hist[j_idx]
    dy_pairs = y_hist[i_idx] - y_hist[j_idx]
    m_parent = m_hist[j_idx]
    rho_pairs = rho_matrix[i_idx, j_idx]
    
    def dqg_neg_q(params):
        d_val, q_val, gamma_val = params
        f_vals = spatial_kernel_powerlaw(dx_pairs, dy_pairs, m_parent, mc, d_val, q_val, gamma_val)
        
        # log f
        # add tiny epsilon to prevent log(0)
        log_f = np.log(np.maximum(f_vals, 1e-30))
        
        # We want to maximize sum rho_ij * log(f_ij)
        return -np.sum(rho_pairs * log_f)
        
    bounds = [(1e-3, 100.0), (1.001, 5.0), (0.0, 3.0)]
    init_guess = [d_current, q_current, gamma_current]
    
    opt_res = minimize(dqg_neg_q, init_guess, bounds=bounds, method='L-BFGS-B')
    d_new, q_new, gamma_new = opt_res.x
    
    return K_new, alpha_new, c_new, p_new, d_new, q_new, gamma_new
