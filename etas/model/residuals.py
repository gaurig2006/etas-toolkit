import numpy as np
import matplotlib.pyplot as plt
from .kernels import omori_g_integral

def time_residuals(event_times: np.ndarray, 
                   event_mags: np.ndarray, 
                   t_start: float,
                   mc: float, 
                   mu: float, 
                   K: float, 
                   alpha: float, 
                   c: float, 
                   p: float) -> np.ndarray:
    """
    Computes the transformed-time residuals tau_i for the ETAS model.
    
    Cites: 01 Ogata 1988, Section 4.
    Formula: tau_i = Lambda(t_start, t_i) = int_{t_start}^{t_i} lambda(s) ds
    
    Args:
        event_times: Array of historical event times.
        event_mags: Array of historical event magnitudes.
        t_start: Start of the fitting window.
        mc: Magnitude of completeness.
        mu, K, alpha, c, p: ETAS parameters.
        
    Returns:
        Array of transformed times tau_i corresponding to events strictly after t_start.
    """
    sort_idx = np.argsort(event_times)
    t_hist = np.asarray(event_times)[sort_idx]
    m_hist = np.asarray(event_mags)[sort_idx]
    
    # We only compute tau for events after t_start
    target_mask = t_hist > t_start
    t_target = t_hist[target_mask]
    
    tau = np.zeros_like(t_target, dtype=float)
    
    # Compute the compensator from t_start to each t_i
    for i, t_i in enumerate(t_target):
        # Background
        tau[i] = mu * (t_i - t_start)
        
        # Triggering from all events before t_i
        trigger_mask = t_hist < t_i
        if np.any(trigger_mask):
            t_trig = t_hist[trigger_mask]
            m_trig = m_hist[trigger_mask]
            
            a = np.maximum(t_start - t_trig, 0.0)
            b = t_i - t_trig
            
            weights = K * np.exp(alpha * (m_trig - mc))
            integrals = omori_g_integral(a, b, c, p)
            tau[i] += np.sum(weights * integrals)
            
    return tau

def plot_residual_ks(tau: np.ndarray, ax=None):
    """
    Plots the empirical cumulative distribution of transformed times against the 
    theoretical uniform distribution (Kolmogorov-Smirnov diagnostic plot).
    
    If the ETAS model fits perfectly, tau_i forms a stationary Poisson process with rate 1,
    meaning the normalized inter-event times U_i = 1 - exp(-(tau_i - tau_{i-1})) are uniformly
    distributed on [0, 1].
    
    Args:
        tau: Array of transformed times (strictly increasing).
        ax: Matplotlib axes object.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        
    if len(tau) < 2:
        ax.text(0.5, 0.5, "Not enough data", ha="center")
        return ax
        
    # Inter-event times in transformed domain
    dtau = np.diff(tau)
    
    # Transform to uniform [0,1] under exponential assumption
    U = 1.0 - np.exp(-dtau)
    U_sorted = np.sort(U)
    
    # Empirical CDF
    N = len(U_sorted)
    cdf_empirical = np.arange(1, N + 1) / N
    
    ax.plot(U_sorted, cdf_empirical, 'b-', label='Empirical')
    ax.plot([0, 1], [0, 1], 'k--', label='Theoretical (Uniform)')
    
    # Calculate KS statistic (max distance)
    ks_stat = np.max(np.abs(cdf_empirical - U_sorted))
    
    ax.set_title(f"Residual KS Plot (KS Stat: {ks_stat:.3f})")
    ax.set_xlabel("Theoretical U[0, 1]")
    ax.set_ylabel("Empirical CDF")
    ax.legend()
    ax.grid(True, alpha=0.5)
    
    return ax
