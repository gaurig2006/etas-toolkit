import numpy as np
import pandas as pd
from typing import Union

def calc_mc_maxc(mags: Union[pd.Series, np.ndarray], bin_width: float = 0.1, correction: float = 0.2) -> float:
    """
    Computes the Magnitude of Completeness (Mc) using the Maximum Curvature (MAXC) method.
    
    The MAXC method estimates Mc as the magnitude bin with the highest number of events 
    in the non-cumulative frequency-magnitude distribution.
    
    Cites: 05 Wiemer 2000 (ZMAP & Mc methods)
    
    Args:
        mags: Array or Series of earthquake magnitudes.
        bin_width: Width of the magnitude bins (default 0.1).
        correction: The F-score patch to add to the MAXC estimate to combat underestimation (default +0.2).
        
    Returns:
        The estimated Mc value as a float.
    """
    if len(mags) == 0:
        return np.nan
        
    m_min = np.floor(np.min(mags) * 10) / 10
    m_max = np.ceil(np.max(mags) * 10) / 10
    
    # Create bins; add small epsilon to ensure max value is included
    bins = np.arange(m_min, m_max + bin_width * 1.5, bin_width)
    counts, edges = np.histogram(mags, bins=bins)
    
    if len(counts) == 0:
        return np.nan
        
    max_idx = np.argmax(counts)
    
    # Mc is the center of the bin with the highest count, plus the correction
    mc_raw = edges[max_idx] + (bin_width / 2.0)
    
    # We return rounded to nearest 1 decimal to avoid floating point drift
    return np.round(mc_raw + correction, 1)
