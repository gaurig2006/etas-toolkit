import matplotlib.pyplot as plt
import numpy as np
from etas.catalog.model import Catalog

def plot_depth_cross_section(catalog: Catalog, azimuth: float, ax=None):
    """
    Projects hypocenters onto a 2D depth cross-section along a given azimuth.
    Cites: theme-3 (EDA).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["longitude", "latitude", "depth"])
    if df.empty:
        return ax

    # Basic projection along azimuth (in degrees)
    theta = np.radians(azimuth)
    
    # Center coordinates
    lon0, lat0 = df["longitude"].mean(), df["latitude"].mean()
    
    # Approximate km conversion (rough)
    dx = (df["longitude"] - lon0) * 111.0 * np.cos(np.radians(lat0))
    dy = (df["latitude"] - lat0) * 111.0
    
    # Distance along azimuth
    dist = dx * np.sin(theta) + dy * np.cos(theta)
    
    mag = df["magnitude"].fillna(2.0)
    sizes = 2 ** (mag - mag.min() + 1)

    ax.scatter(dist, df["depth"], s=sizes, c='k', alpha=0.5, edgecolors='none')
    
    # Invert y-axis so depth goes down
    if not ax.yaxis_inverted():
        ax.invert_yaxis()
        
    ax.set_xlabel(f'Distance along azimuth {azimuth}° (km)')
    ax.set_ylabel('Depth (km)')
    ax.set_title(f'Depth Cross-Section (Azimuth {azimuth}°)')
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return ax
