import numpy as np
from typing import Optional

def background_kde(eval_x: np.ndarray, 
                   eval_y: np.ndarray, 
                   event_x: np.ndarray, 
                   event_y: np.ndarray, 
                   bg_probs: np.ndarray,
                   bandwidth: float,
                   adaptive: bool = False,
                   k_neighbors: int = 10) -> np.ndarray:
    """
    Computes a 2D Gaussian Kernel Density Estimate for the background rate mu(x,y).
    
    Cites: 03 Zhuang et al. 2002; 04 Helmstetter et al. 2007.
    Formula: mu(x,y) = sum_i bg_i * K_h(x - x_i, y - y_i)
    where K_h is a 2D Gaussian kernel with bandwidth h.
    
    Args:
        eval_x: X coordinates to evaluate mu at (size M).
        eval_y: Y coordinates to evaluate mu at (size M).
        event_x: Historical event X coordinates (size N).
        event_y: Historical event Y coordinates (size N).
        bg_probs: Background probability weights for each event (size N).
        bandwidth: Base bandwidth h in km.
        adaptive: If true, uses nearest-neighbor adaptive bandwidth per Helmstetter.
        k_neighbors: Number of neighbors for adaptive bandwidth.
        
    Returns:
        Array of estimated mu values at (eval_x, eval_y).
    """
    M = len(eval_x)
    N = len(event_x)
    
    mu_vals = np.zeros(M, dtype=float)
    
    # We use a vectorized approach if memory allows
    # memory footprint: M x N floats
    dx = eval_x[:, None] - event_x[None, :]
    dy = eval_y[:, None] - event_y[None, :]
    r_sq = dx**2 + dy**2
    
    if adaptive and N > k_neighbors:
        # Distance to k-th nearest neighbor for each event
        # (calculated among the events themselves, not eval points)
        event_dx = event_x[:, None] - event_x[None, :]
        event_dy = event_y[:, None] - event_y[None, :]
        event_r_sq = event_dx**2 + event_dy**2
        
        # Sort distances for each event (axis 1)
        # We want the k-th neighbor (index k since index 0 is distance 0 to self)
        sorted_r_sq = np.sort(event_r_sq, axis=1)
        h_sq = sorted_r_sq[:, k_neighbors]
        
        # Protect against 0 bandwidth if many coincident events exist
        h_sq = np.maximum(h_sq, bandwidth**2)
    else:
        h_sq = np.full(N, bandwidth**2, dtype=float)
        
    # Evaluate 2D Gaussian kernel
    # K_h = 1 / (2 * pi * h^2) * exp(-r^2 / (2 * h^2))
    prefactor = 1.0 / (2.0 * np.pi * h_sq)
    kernel_vals = prefactor[None, :] * np.exp(-r_sq / (2.0 * h_sq[None, :]))
    
    # Sum over events weighted by bg_probs
    mu_vals = np.sum(kernel_vals * bg_probs[None, :], axis=1)
    
    return mu_vals
