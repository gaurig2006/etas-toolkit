import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from etas.catalog.model import Catalog

def plot_epicenter_map(catalog: Catalog, ax=None):
    """
    Plots an epicenter map with marker size proportional to magnitude 
    and color based on depth.
    Cites: theme-3 (EDA). Uses cartopy as default.
    """
    if ax is None:
        fig = plt.figure(figsize=(8, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["longitude", "latitude"])
    if df.empty:
        return ax

    # Add map features if it's a cartopy axes
    if hasattr(ax, 'coastlines'):
        ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.5)
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.coastlines(resolution='50m')
        
        # Set extent with some padding
        padding = 1.0
        ax.set_extent([
            df["longitude"].min() - padding,
            df["longitude"].max() + padding,
            df["latitude"].min() - padding,
            df["latitude"].max() + padding
        ], crs=ccrs.PlateCarree())

    # Size proportional to magnitude (exponentially scaled for visibility)
    mag = df["magnitude"].fillna(2.0)
    sizes = 2 ** (mag - mag.min() + 1) * 2

    # Color by depth
    depths = df["depth"].fillna(0)

    # Note: transform=ccrs.PlateCarree() is required if using cartopy axes
    transform_kwargs = {'transform': ccrs.PlateCarree()} if hasattr(ax, 'coastlines') else {}

    scatter = ax.scatter(
        df["longitude"], df["latitude"], 
        s=sizes, c=depths, cmap='viridis_r', alpha=0.6, edgecolors='none',
        **transform_kwargs
    )

    cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Depth (km)')

    if not hasattr(ax, 'coastlines'):
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        # Aspect ratio for non-cartopy fallback
        ax.set_aspect(1.0 / plt.np.cos(plt.np.radians(df["latitude"].mean())))

    ax.set_title('Epicenter Map')
    
    return ax
