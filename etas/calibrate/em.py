import numpy as np
from etas.catalog.model import Catalog
from etas.model.likelihood import log_likelihood
from .estep import e_step
from .mstep import m_step
from typing import Dict, Any, List

def fit_etas_em(catalog: Catalog, 
                mc: float, 
                t_start: float, 
                t_end: float,
                max_iter: int = 200, 
                tol: float = 1e-4,
                n_restarts: int = 3) -> Dict[str, Any]:
    """
    Fits the temporal ETAS model using the Expectation-Maximization (EM) algorithm.
    Includes multiple restarts to avoid local minima, and strict monotonicity guards.
    
    Cites: 02 Veen & Schoenberg 2008, Eq. 1.
    
    Args:
        catalog: The earthquake Catalog.
        mc: Magnitude of completeness.
        t_start: Start of observation window.
        t_end: End of observation window.
        max_iter: Maximum number of EM iterations.
        tol: Convergence tolerance for log-likelihood.
        n_restarts: Number of random parameter restarts.
        
    Returns:
        Dictionary containing best parameters, log-likelihood, and history.
    """
    df = catalog.df.dropna(subset=["time_days", "magnitude"]).sort_values("time_days")
    t_hist = df["time_days"].values
    m_hist = df["magnitude"].values
    
    best_ll = -np.inf
    best_params = None
    best_history = None
    
    # Simple priors for random restarts
    np.random.seed(42)
    
    for restart in range(n_restarts):
        # Initial guesses
        if restart == 0:
            # Standard guess
            mu, K, alpha, c, p = 0.5, 0.05, 1.0, 0.05, 1.2
        else:
            mu = np.random.uniform(0.1, 1.0)
            K = np.random.uniform(0.01, 0.2)
            alpha = np.random.uniform(0.5, 2.5)
            c = np.random.uniform(0.001, 0.1)
            p = np.random.uniform(1.05, 1.5)
            
        current_ll = log_likelihood(t_hist, m_hist, t_start, t_end, mc, mu, K, alpha, c, p)
        history = [(mu, K, alpha, c, p, current_ll)]
        
        for it in range(max_iter):
            # E-step
            bg_probs, rho_matrix, _ = e_step(t_hist, m_hist, mc, mu, K, alpha, c, p)
            
            # M-step
            mu_new, K_new, alpha_new, c_new, p_new = m_step(
                t_hist, m_hist, t_start, t_end, mc, bg_probs, rho_matrix, c, p
            )
            
            new_ll = log_likelihood(t_hist, m_hist, t_start, t_end, mc, 
                                    mu_new, K_new, alpha_new, c_new, p_new)
            
            # Monotonicity guard: LL should never decrease in exact EM
            if new_ll < current_ll - 1e-6:
                print(f"Warning: LL dropped by {current_ll - new_ll} at iter {it}. M-step failed strict monotonicity.")
                # We accept small floating point jitter, but break if it drops significantly
                if new_ll < current_ll - 1e-4:
                    break
                    
            param_diff = np.max([
                np.abs(mu_new - mu),
                np.abs(K_new - K),
                np.abs(alpha_new - alpha),
                np.abs(c_new - c),
                np.abs(p_new - p)
            ])

            improvement = new_ll - current_ll
            
            mu, K, alpha, c, p = mu_new, K_new, alpha_new, c_new, p_new
            current_ll = new_ll
            history.append((mu, K, alpha, c, p, current_ll))
            
            # Dual convergence: stop if LL improvement is tiny AND parameters barely change
            if improvement > 0 and improvement < tol and param_diff < tol:
                break
                
        if current_ll > best_ll:
            best_ll = current_ll
            best_params = {"mu": mu, "K": K, "alpha": alpha, "c": c, "p": p}
            best_history = history
            
    return {
        "params": best_params,
        "log_likelihood": best_ll,
        "history": best_history
    }
