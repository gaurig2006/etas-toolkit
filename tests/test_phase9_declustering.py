import numpy as np
import pytest
from etas.decluster.stochastic import stochastic_decluster
from etas.decluster.graph import compute_network_features

def test_stochastic_declustering_rate():
    # Simulate bg probabilities
    np.random.seed(42)
    N = 1000
    # Average background probability is 0.4
    bg_probs = np.random.uniform(0.2, 0.6, N)
    
    expected_bg_count = np.sum(bg_probs)
    
    # 100 realizations
    realizations = stochastic_decluster(bg_probs, n_realizations=100)
    
    # Check stable rate across realizations (within stochastic tolerance 5-10%)
    actual_bg_counts = np.sum(realizations, axis=0)
    mean_actual = np.mean(actual_bg_counts)
    
    # Should be close to expected
    assert np.isclose(mean_actual, expected_bg_count, rtol=0.05)

def test_triggering_graph_features():
    # Synthetic rho matrix for 3 events:
    # Event 0 is background.
    # Event 1 triggered by Event 0 (rho=0.8).
    # Event 2 triggered by Event 1 (rho=0.9).
    
    N = 3
    rho = np.zeros((N, N))
    rho[1, 0] = 0.8
    rho[2, 1] = 0.9
    
    features = compute_network_features(rho)
    
    # Expected offspring
    assert features["expected_direct_offspring"].iloc[0] == 0.8
    assert features["expected_direct_offspring"].iloc[1] == 0.9
    assert features["expected_direct_offspring"].iloc[2] == 0.0
    
    # Expected generation depth
    assert features["expected_generation_depth"].iloc[0] == 0.0
    assert features["expected_generation_depth"].iloc[1] == 0.8 * (0.0 + 1.0) # 0.8
    assert features["expected_generation_depth"].iloc[2] == 0.9 * (0.8 + 1.0) # 1.62
    
    # Expected cluster size
    assert features["expected_cluster_size"].iloc[2] == 0.0
    assert features["expected_cluster_size"].iloc[1] == 0.9 * (0.0 + 1.0) # 0.9
    assert features["expected_cluster_size"].iloc[0] == 0.8 * (0.9 + 1.0) # 1.52
