import numpy as np
from .kde import background_kde

def optimize_bandwidth_cv(event_x: np.ndarray, 
                          event_y: np.ndarray, 
                          bg_probs: np.ndarray, 
                          h_candidates: np.ndarray) -> float:
    """
    Selects the optimal KDE bandwidth using likelihood cross-validation.
    
    Cites: 04 Helmstetter et al. 2007.
    
    Args:
        event_x: Array of event X coordinates.
        event_y: Array of event Y coordinates.
        bg_probs: Array of background probabilities.
        h_candidates: Array of bandwidths to test.
        
    Returns:
        The best bandwidth parameter.
    """
    N = len(event_x)
    best_h = h_candidates[0]
    best_ll = -np.inf
    
    # We leave out one event at a time to evaluate its likelihood
    # To do this efficiently, we can compute the full KDE matrix once per h
    # and subtract the self-contribution.
    
    dx = event_x[:, None] - event_x[None, :]
    dy = event_y[:, None] - event_y[None, :]
    r_sq = dx**2 + dy**2
    
    # Fill diagonal with infinity so self-contribution is 0
    np.fill_diagonal(r_sq, np.inf)
    
    for h in h_candidates:
        h_sq = h**2
        prefactor = 1.0 / (2.0 * np.pi * h_sq)
        kernel_vals = prefactor * np.exp(-r_sq / (2.0 * h_sq))
        
        # Cross-validated mu for each event
        # mu_{-i}(x_i, y_i)
        cv_mu = np.sum(kernel_vals * bg_probs[None, :], axis=1)
        
        # Protect against log(0)
        cv_mu = np.maximum(cv_mu, 1e-12)
        
        # Log-likelihood is sum of log(mu)
        ll = np.sum(np.log(cv_mu))
        
        if ll > best_ll:
            best_ll = ll
            best_h = h
            
    return best_h
