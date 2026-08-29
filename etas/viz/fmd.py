import numpy as np
import matplotlib.pyplot as plt
from etas.catalog.model import Catalog

def plot_fmd(catalog: Catalog, ax=None, mc=None, b_value=None, a_value=None):
    """
    Plots the cumulative and incremental Frequency-Magnitude Distribution (FMD).
    Cites: theme-3 (EDA).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    if catalog.df.empty:
        return ax

    mags = catalog.df["magnitude"].dropna().values
    if len(mags) == 0:
        return ax

    # Use 0.1 magnitude bins
    m_min = np.floor(mags.min() * 10) / 10
    m_max = np.ceil(mags.max() * 10) / 10
    bins = np.arange(m_min, m_max + 0.2, 0.1)
    
    # Incremental (non-cumulative histogram)
    counts, edges = np.histogram(mags, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    
    # Cumulative (reverse cumulative sum)
    cum_counts = np.cumsum(counts[::-1])[::-1]
    
    # Filter zeros for log plot
    valid = counts > 0
    valid_cum = cum_counts > 0

    ax.plot(centers[valid], counts[valid], 'o', color='gray', label='Incremental', alpha=0.5)
    ax.plot(centers[valid_cum], cum_counts[valid_cum], 's', color='black', label='Cumulative')

    # Plot fitted line if provided
    if b_value is not None and a_value is not None and mc is not None:
        ax.axvline(mc, color='red', linestyle='--', label=f'Mc = {mc}')
        
        # log10 N(>=m) = a - b * m
        fit_mags = np.linspace(mc, m_max, 50)
        fit_logN = a_value - b_value * fit_mags
        fit_N = 10**fit_logN
        
        ax.plot(fit_mags, fit_N, 'r-', label=f'b={b_value:.2f}, a={a_value:.2f}')

    ax.set_yscale('log')
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Number of Earthquakes')
    ax.set_title('Frequency-Magnitude Distribution')
    ax.legend()
    ax.grid(True, which="both", ls="--", alpha=0.5)
    
    return ax
