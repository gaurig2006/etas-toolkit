import numpy as np
import pandas as pd
from typing import Union, Tuple

def calc_bvalue(mags: Union[pd.Series, np.ndarray], mc: float, bin_width: float = 0.1) -> Tuple[float, float, float]:
    """
    Computes the b-value, a-value, and standard error (delta b) via the Aki-Utsu MLE.
    
    Cites: Appendix B (Aki-Utsu MLE); 01 Ogata 1988 (for GR scaling context).
    Formulas:
        b = log10(e) / (<M> - (Mc - bin_width/2))
        a = log10(N) + b * Mc
        db = 2.3 * b^2 * sqrt( sum((M_i - <M>)^2) / (N*(N-1)) )   (Shi & Bolt 1982)
        
    Args:
        mags: Array or Series of earthquake magnitudes.
        mc: The Magnitude of Completeness cutoff.
        bin_width: Width of the magnitude bins (default 0.1).
        
    Returns:
        Tuple of (b_value, a_value, b_std_err). Returns (np.nan, np.nan, np.nan) if not enough data.
    """
    mags = np.array(mags)
    mags_above = mags[mags >= mc]
    n = len(mags_above)
    
    if n < 2:
        return np.nan, np.nan, np.nan
        
    mean_mag = np.mean(mags_above)
    
    # Aki-Utsu MLE
    b_value = np.log10(np.e) / (mean_mag - (mc - bin_width / 2.0))
    a_value = np.log10(n) + b_value * mc
    
    # Shi & Bolt 1982 standard error
    variance_term = np.sum((mags_above - mean_mag)**2) / (n * (n - 1))
    db = 2.3 * (b_value**2) * np.sqrt(variance_term)
    
    return b_value, a_value, db
