import numpy as np
import pandas as pd
from typing import Dict

def compute_network_features(rho_matrix: np.ndarray) -> pd.DataFrame:
    """
    Computes triggering graph features from the rho_ij matrix.
    These features form the input to downstream neural models.
    
    Args:
        rho_matrix: N x N triggering probability matrix.
        
    Returns:
        DataFrame containing expected offspring, generation depth, etc.
    """
    N = rho_matrix.shape[0]
    
    # Expected direct offspring (out-degree)
    # Sum of rho_ij over rows (i) for a given parent column (j)
    expected_offspring = np.sum(rho_matrix, axis=0)
    
    # Expected generation depth
    # depth_i = sum_j rho_ij * (depth_j + 1)
    # Since rho is strictly lower triangular (causal), we can compute this iteratively
    expected_depth = np.zeros(N, dtype=float)
    for i in range(N):
        # Parents are j < i
        if i > 0:
            expected_depth[i] = np.sum(rho_matrix[i, :i] * (expected_depth[:i] + 1.0))
            
    # Cluster sizes (expected total descendants)
    # size_j = sum_i rho_ij * (size_i + 1)
    # We iterate backwards from the last event
    expected_cluster_size = np.zeros(N, dtype=float)
    for j in range(N - 1, -1, -1):
        if j < N - 1:
            expected_cluster_size[j] = np.sum(rho_matrix[j+1:, j] * (expected_cluster_size[j+1:] + 1.0))
            
    return pd.DataFrame({
        "expected_direct_offspring": expected_offspring,
        "expected_generation_depth": expected_depth,
        "expected_cluster_size": expected_cluster_size
    })
