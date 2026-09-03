import numpy as np
from typing import Tuple, Dict, Any
from .estep import e_step_spatial
from .mstep import m_step_spatial
from .kde import background_kde
from etas.model.likelihood import log_likelihood_spatial

def zhuang_coupling_loop(t_hist: np.ndarray,
                         x_hist: np.ndarray,
                         y_hist: np.ndarray,
                         m_hist: np.ndarray,
                         mc: float,
                         t_start: float,
                         t_end: float,
                         bandwidth: float,
                         initial_params: Dict[str, float],
                         max_iter: int = 50,
                         tol: float = 1e-4) -> Dict[str, Any]:
    """
    Executes the Zhuang iterative fixed-point loop, coupling the EM calibration 
    of ETAS parameters with the KDE estimation of the spatial background field mu(x,y).
    
    Cites: 03 Zhuang et al. 2002.
    
    Args:
        t_hist, x_hist, y_hist, m_hist: Event data arrays.
        mc: Magnitude of completeness.
        t_start, t_end: Time window.
        bandwidth: KDE bandwidth.
        initial_params: Starting dictionary for {K, alpha, c, p, d, q, gamma}.
        
    Returns:
        Dict with converged parameters, spatial field mu_i, and history.
    """
    # Unpack initial
    K = initial_params.get("K", 0.05)
    alpha = initial_params.get("alpha", 1.0)
    c = initial_params.get("c", 0.05)
    p = initial_params.get("p", 1.2)
    d = initial_params.get("d", 1.0)
    q = initial_params.get("q", 1.5)
    gamma = initial_params.get("gamma", 1.0)
    
    N = len(t_hist)
    
    # 1. Initialize: start with uniform mu
    mu_scalar = N / ((t_end - t_start) * 1.0) # Dummy area 1.0
    mu_field = np.full(N, mu_scalar, dtype=float)
    
    current_ll = -np.inf
    history = []
    
    for it in range(max_iter):
        # 2. E-step (Spatial)
        # Note: we need an e_step_spatial that accepts a mu_field array!
        bg_probs, rho_matrix, _ = e_step_spatial(
            t_hist, x_hist, y_hist, m_hist, mc, mu_field, K, alpha, c, p, d, q, gamma
        )
        
        # 3. KDE Step
        # Re-estimate mu(x_i, y_i) using the new bg_probs
        mu_field_unscaled = background_kde(
            x_hist, y_hist, x_hist, y_hist, bg_probs, bandwidth
        )
        # Scale to rate per day
        mu_field = mu_field_unscaled / (t_end - t_start)
        
        # 4. M-step (Spatial)
        K_new, alpha_new, c_new, p_new, d_new, q_new, gamma_new = m_step_spatial(
            t_hist, x_hist, y_hist, m_hist, t_start, t_end, mc, bg_probs, rho_matrix, 
            c, p, d, q, gamma
        )
        
        # 5. Evaluate Convergence
        new_ll = log_likelihood_spatial(
            t_hist, x_hist, y_hist, m_hist, t_start, t_end, mc, 
            mu_field, K_new, alpha_new, c_new, p_new, d_new, q_new, gamma_new
        )
        
        improvement = new_ll - current_ll
        history.append({
            "ll": new_ll, "K": K_new, "alpha": alpha_new, 
            "c": c_new, "p": p_new, "d": d_new, "q": q_new, "gamma": gamma_new
        })
        
        if improvement > 0 and improvement < tol:
            break
            
        K, alpha, c, p, d, q, gamma = K_new, alpha_new, c_new, p_new, d_new, q_new, gamma_new
        current_ll = new_ll
        
    return {
        "params": {"K": K, "alpha": alpha, "c": c, "p": p, "d": d, "q": q, "gamma": gamma},
        "mu_field": mu_field,
        "bg_probs": bg_probs,
        "log_likelihood": current_ll,
        "history": history
    }
