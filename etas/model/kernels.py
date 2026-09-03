import numpy as np

def omori_g(t: np.ndarray, c: float, p: float) -> np.ndarray:
    """
    Evaluates the normalized temporal Omori kernel g(t).
    
    Cites: 01 Ogata 1988, Eq. 2 (modified for pure normalization).
    Formula: g(t) = ((p-1) / c) * (1 + t/c)^(-p)
    
    Args:
        t: Array of time differences (t - t_i). Must be >= 0.
        c: Omori c parameter (time offset).
        p: Omori p parameter (decay rate, must be > 1).
        
    Returns:
        Array of g(t) values. Returns 0 where t < 0.
    """
    g = np.zeros_like(t, dtype=float)
    valid = t >= 0
    t_v = t[valid]
    g[valid] = ((p - 1.0) / c) * np.power(1.0 + t_v / c, -p)
    return g

def omori_g_log(t: np.ndarray, c: float, p: float) -> np.ndarray:
    """
    Evaluates the logarithm of the normalized temporal Omori kernel log(g(t)).
    
    Cites: 01 Ogata 1988, Eq. 2 (logarithm of the kernel).
    Formula: log(g(t)) = log((p-1)/c) - p * log(1 + t/c)
    
    Args:
        t: Array of time differences (t - t_i). Must be >= 0.
        c: Omori c parameter.
        p: Omori p parameter (must be > 1).
        
    Returns:
        Array of log(g(t)) values. Returns -inf where t < 0.
    """
    log_g = np.full_like(t, -np.inf, dtype=float)
    valid = t >= 0
    t_v = t[valid]
    log_g[valid] = np.log((p - 1.0) / c) - p * np.log1p(t_v / c)
    return log_g

def omori_g_integral(a: np.ndarray, b: np.ndarray, c: float, p: float) -> np.ndarray:
    """
    Evaluates the definite integral of g(t) from a to b.
    
    Cites: 01 Ogata 1988, Section 2 (compensator integral).
    Formula: int_a^b g(t) dt = (1 + a/c)^(1-p) - (1 + b/c)^(1-p)
    
    Args:
        a: Array or scalar of start times. Must be >= 0.
        b: Array or scalar of end times. Must be >= a.
        c: Omori c parameter.
        p: Omori p parameter (must be > 1).
        
    Returns:
        Array of integrated values.
    """
    # Ensure a and b are >= 0
    a = np.maximum(a, 0.0)
    b = np.maximum(b, 0.0)
    
    term_a = np.power(1.0 + a / c, 1.0 - p)
    term_b = np.power(1.0 + b / c, 1.0 - p)
    
    return term_a - term_b
