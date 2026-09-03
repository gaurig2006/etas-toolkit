import numpy as np
import pandas as pd
from typing import Union

def calc_mc_gft(mags: Union[pd.Series, np.ndarray], bin_width: float = 0.1, target_r: float = 90.0) -> float:
    """
    Computes the Magnitude of Completeness (Mc) using the Goodness-of-Fit Test (GFT).
    
    The algorithm tests progressively higher cutoff magnitudes. The true Mc is defined 
    as the lowest magnitude bin where R >= target_r (typically 90% or 95%).
    
    Cites: 05 Wiemer 2000, Eq. 1.
    Formula: R = 100 - (sum(|B_i - S_i|) / sum(B_i)) * 100
    
    Args:
        mags: Array or Series of earthquake magnitudes.
        bin_width: Width of the magnitude bins (default 0.1).
        target_r: The target goodness-of-fit percentage (default 90.0).
        
    Returns:
        The estimated Mc value as a float.
    """
    if len(mags) == 0:
        return np.nan
        
    mags = np.array(mags)
    m_min = np.floor(np.min(mags) * 10) / 10
    m_max = np.ceil(np.max(mags) * 10) / 10
    
    # We will test candidate Mc values from m_min up to m_max - 1.0 (need some data to fit)
    candidate_mcs = np.arange(m_min, max(m_min, m_max - 1.0), bin_width)
    
    best_mc = np.nan
    
    for mc in candidate_mcs:
        mc = np.round(mc, 1)
        mags_above = mags[mags >= mc]
        
        # Need enough events to do a fit
        if len(mags_above) < 20:
            continue
            
        mean_mag = np.mean(mags_above)
        
        # Aki-Utsu MLE for b-value (Appendix B formula)
        # b = log10(e) / (mean_m - (Mc - dm/2))
        b_value = np.log10(np.e) / (mean_mag - (mc - bin_width / 2.0))
        a_value = np.log10(len(mags_above)) + b_value * mc
        
        # Create bins starting from current mc
        bins = np.arange(mc, m_max + bin_width * 1.5, bin_width)
        
        # Observed non-cumulative frequency (B_i)
        obs_counts, edges = np.histogram(mags_above, bins=bins)
        centers = edges[:-1] + bin_width / 2.0
        
        # Synthetic non-cumulative frequency (S_i)
        # N(m) = 10^(a - b*m) is cumulative. We need incremental.
        # Incremental roughly: S_i = 10^(a - b*(m-dm/2)) - 10^(a - b*(m+dm/2))
        synth_counts = 10**(a_value - b_value * (centers - bin_width/2.0)) - 10**(a_value - b_value * (centers + bin_width/2.0))
        
        # Goodness of fit
        sum_B = np.sum(obs_counts)
        if sum_B == 0:
            continue
            
        sum_diff = np.sum(np.abs(obs_counts - synth_counts))
        R = 100.0 - (sum_diff / sum_B) * 100.0
        
        if R >= target_r:
            best_mc = mc
            break
            
    # If target not reached, fallback to returning the mc that achieved the highest R, or NaN
    # For now, return best_mc (will be NaN if never reached target_r)
    return best_mc
