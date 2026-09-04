import matplotlib.pyplot as plt
import numpy as np
from etas.catalog.model import Catalog
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_depth_cross_section(catalog: Catalog, azimuth: float, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))
    if catalog.df.empty: return ax
    df = catalog.df.dropna(subset=['longitude', 'latitude', 'depth'])
    if df.empty: return ax
    theta = np.radians(azimuth)
    lon0, lat0 = df['longitude'].mean(), df['latitude'].mean()
    dx = (df['longitude'] - lon0) * 111.0 * np.cos(np.radians(lat0))
    dy = (df['latitude'] - lat0) * 111.0
    dist = dx * np.sin(theta) + dy * np.cos(theta)
    mag = df['magnitude'].fillna(2.0)
    sizes = 2 ** (mag - mag.min() + 1)
    ax.scatter(dist, df['depth'], s=sizes, c='k', alpha=0.5, edgecolors='none')
    if not ax.yaxis_inverted(): ax.invert_yaxis()
    ax.set_xlabel(f'Distance along azimuth {azimuth} (km)')
    ax.set_ylabel('Depth (km)')
    ax.set_title(f'Depth Cross-Section (Azimuth {azimuth})')
    ax.grid(True, linestyle='--', alpha=0.5)
    return ax

def plot_spatial_mc(grid_lon, grid_lat, mc_values, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3)
    
    mc_masked = np.ma.masked_invalid(mc_values)
    mesh = ax.pcolormesh(grid_lon, grid_lat, mc_masked, cmap='viridis', 
                         transform=ccrs.PlateCarree(), shading='auto')
    
    plt.colorbar(mesh, ax=ax, label='Magnitude of Completeness (Mc)', fraction=0.046, pad=0.04)
    ax.set_title('Spatial Distribution of Mc')
    
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    return ax

def plot_spatial_b(grid_lon, grid_lat, b_values, mask=None, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3)
    
    if mask is not None:
        b_values = np.ma.masked_where(mask, b_values)
    else:
        b_values = np.ma.masked_invalid(b_values)
        
    mesh = ax.pcolormesh(grid_lon, grid_lat, b_values, cmap='coolwarm', 
                         transform=ccrs.PlateCarree(), shading='auto')
                         
    plt.colorbar(mesh, ax=ax, label='b-value (MLE)', fraction=0.046, pad=0.04)
    ax.set_title('Spatial Distribution of b-values')
    
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    return ax
