import matplotlib.pyplot as plt
from pathlib import Path
from etas.catalog.model import Catalog

from .fmd import plot_fmd
from .maps import plot_epicenter_map
from .time import plot_time_magnitude, plot_cumulative_events
from .space import plot_depth_cross_section
from .interevent import plot_interevent_time

def plot_eda(catalog: Catalog, save_path: str = None):
    """
    Produces a multi-panel EDA figure for a Catalog.
    Combines FMD, Epicenter Map, Time-Mag, Depth cross-section, and Inter-event times.
    """
    fig = plt.figure(figsize=(16, 12))
    
    # 2 rows, 3 cols
    ax_map = plt.subplot(2, 3, 1)
    plot_epicenter_map(catalog, ax=ax_map)
    
    ax_fmd = plt.subplot(2, 3, 2)
    # Simple Mc heuristic (max curvature without correction for quick EDA plot)
    if not catalog.df.empty and "magnitude" in catalog.df.columns:
        mags = catalog.df["magnitude"].dropna()
        if len(mags) > 0:
            mc = np.round(mags.mode().iloc[0], 1) if not mags.mode().empty else mags.min()
            plot_fmd(catalog, ax=ax_fmd, mc=mc)
    else:
        plot_fmd(catalog, ax=ax_fmd)
        
    ax_time = plt.subplot(2, 3, 3)
    plot_time_magnitude(catalog, ax=ax_time)
    
    ax_cum = plt.subplot(2, 3, 4)
    plot_cumulative_events(catalog, ax=ax_cum)
    
    ax_space = plt.subplot(2, 3, 5)
    plot_depth_cross_section(catalog, azimuth=45, ax=ax_space)
    
    ax_inter = plt.subplot(2, 3, 6)
    plot_interevent_time(catalog, ax=ax_inter)
    
    plt.tight_layout()
    
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved EDA plot to {save_path}")
        
    return fig

# Needs numpy imported for mc heuristic inside plot_eda
import numpy as np
