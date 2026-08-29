import matplotlib.pyplot as plt
from etas.catalog.model import Catalog

def plot_epicenter_map(catalog: Catalog, ax=None):
    """
    Plots an epicenter map with marker size proportional to magnitude 
    and color based on depth.
    Cites: theme-3 (EDA).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["longitude", "latitude"])
    if df.empty:
        return ax

    # Size proportional to magnitude (exponentially scaled for visibility)
    mag = df["magnitude"].fillna(2.0)
    sizes = 2 ** (mag - mag.min() + 1) * 2

    # Color by depth
    depths = df["depth"].fillna(0)

    scatter = ax.scatter(
        df["longitude"], df["latitude"], 
        s=sizes, c=depths, cmap='viridis_r', alpha=0.6, edgecolors='none'
    )

    cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Depth (km)')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Epicenter Map')
    ax.grid(True, linestyle="--", alpha=0.5)
    
    # Aspect ratio for maps (approximate local projection)
    ax.set_aspect(1.0 / plt.np.cos(plt.np.radians(df["latitude"].mean())))

    return ax
