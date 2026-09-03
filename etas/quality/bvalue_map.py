import numpy as np
import pandas as pd
from etas.catalog.model import Catalog
from .bvalue import calc_bvalue
from typing import Tuple

def map_spatial_b(catalog: Catalog, grid_lon: np.ndarray, grid_lat: np.ndarray, mc_grid: np.ndarray, n_events: int = 250) -> np.ndarray:
    """
    Computes a spatial grid of b-values using the nearest N events to each grid point,
    applying the corresponding Mc value from the provided mc_grid.
    
    Cites: 05 Wiemer 2000, Eq. 1.
    
    Args:
        catalog: The earthquake Catalog.
        grid_lon: 2D array of grid longitudes (from meshgrid).
        grid_lat: 2D array of grid latitudes (from meshgrid).
        mc_grid: 2D array of Mc values computed previously.
        n_events: Number of nearest events to sample per grid node (default 250).
        
    Returns:
        A 2D numpy array of b-values corresponding to the grid shape.
    """
    df = catalog.df.dropna(subset=["longitude", "latitude", "magnitude"])
    if len(df) < n_events:
        raise ValueError(f"Catalog has only {len(df)} events, but {n_events} are required for the spatial window.")
        
    ev_lons = df["longitude"].values
    ev_lats = df["latitude"].values
    ev_mags = df["magnitude"].values
    
    rows, cols = grid_lon.shape
    b_grid = np.full((rows, cols), np.nan)
    
    mean_lat_rad = np.radians(np.mean(ev_lats))
    cos_lat = np.cos(mean_lat_rad)
    
    for i in range(rows):
        for j in range(cols):
            glon = grid_lon[i, j]
            glat = grid_lat[i, j]
            local_mc = mc_grid[i, j]
            
            if np.isnan(local_mc):
                continue
            
            # Approximate distance squared
            dlon = (ev_lons - glon) * cos_lat
            dlat = (ev_lats - glat)
            dist_sq = dlon**2 + dlat**2
            
            # Nearest N events
            nearest_idx = np.argpartition(dist_sq, n_events - 1)[:n_events]
            local_mags = ev_mags[nearest_idx]
            
            # Calculate b-value
            b_val, a_val, db = calc_bvalue(local_mags, mc=local_mc, bin_width=0.1)
            b_grid[i, j] = b_val
            
    return b_grid
