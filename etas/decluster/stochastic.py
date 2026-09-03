import numpy as np

def stochastic_decluster(bg_probs: np.ndarray, n_realizations: int = 100) -> np.ndarray:
    """
    Performs stochastic declustering by binomial sampling of background probabilities.
    
    Cites: 03 Zhuang et al. 2002.
    
    Args:
        bg_probs: Array of background probabilities for each event.
        n_realizations: Number of independent declustered catalogs to generate.
        
    Returns:
        A boolean matrix of shape (N, n_realizations) where True indicates
        the event is classified as background in that realization.
    """
    N = len(bg_probs)
    
    # Generate uniform random variables
    U = np.random.uniform(0.0, 1.0, size=(N, n_realizations))
    
    # Classify as background if U < bg_prob
    is_background = U < bg_probs[:, None]
    
    return is_background
