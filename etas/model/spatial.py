import numpy as np

def spatial_kernel_powerlaw(dx: np.ndarray, dy: np.ndarray, m: np.ndarray, mc: float, d: float, q: float, gamma: float) -> np.ndarray:
    """
    Evaluates the normalized, magnitude-dependent power-law spatial kernel f(r; m).
    
    Cites: 03 Zhuang et al. 2002.
    Formula: f(r; m) = (q - 1) / (pi * D^2) * (1 + r^2 / D^2)^(-q)
    where D = d * exp(gamma * (m - mc)) and r^2 = dx^2 + dy^2
    
    Args:
        dx: Array of longitude/x differences (km).
        dy: Array of latitude/y differences (km).
        m: Array of parent event magnitudes.
        mc: Magnitude of completeness.
        d: Baseline triggering distance (km).
        q: Spatial decay parameter (must be > 1).
        gamma: Magnitude scaling for distance.
        
    Returns:
        Array of spatial kernel values.
    """
    r_sq = dx**2 + dy**2
    D = d * np.exp(gamma * (m - mc))
    D_sq = D**2
    
    prefactor = (q - 1.0) / (np.pi * D_sq)
    decay = np.power(1.0 + r_sq / D_sq, -q)
    
    return prefactor * decay

def spatial_kernel_gaussian(dx: np.ndarray, dy: np.ndarray, m: np.ndarray, mc: float, d: float, gamma: float) -> np.ndarray:
    """
    Evaluates the normalized, magnitude-dependent Gaussian spatial kernel.
    Alternative to power-law for testing.
    
    Formula: f(r; m) = 1 / (2 * pi * D^2) * exp(-r^2 / (2 * D^2))
    """
    r_sq = dx**2 + dy**2
    D = d * np.exp(gamma * (m - mc))
    D_sq = D**2
    
    prefactor = 1.0 / (2.0 * np.pi * D_sq)
    decay = np.exp(-r_sq / (2.0 * D_sq))
    
    return prefactor * decay
