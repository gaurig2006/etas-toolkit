import numpy as np
import pandas as pd
from etas.catalog.model import Catalog
from .mc_maxc import calc_mc_maxc
from typing import Tuple

def map_spatial_mc(catalog: Catalog, grid_lon: np.ndarray, grid_lat: np.ndarray, n_events: int = 250) -> np.ndarray:
    """
    Computes a spatial grid of Mc values using the nearest N events to each grid point.
    
    Iterates over a defined spatial grid, grabs the nearest N=250 events for each point, 
    and calculates Mc using the fast MAXC + 0.2 method.
    
    Cites: 05 Wiemer 2000, Eq. 1.
    
    Args:
        catalog: The earthquake Catalog.
        grid_lon: 2D array of grid longitudes (from meshgrid).
        grid_lat: 2D array of grid latitudes (from meshgrid).
        n_events: Number of nearest events to sample per grid node (default 250).
        
    Returns:
        A 2D numpy array of Mc values corresponding to the grid shape.
    """
    df = catalog.df.dropna(subset=["longitude", "latitude", "magnitude"])
    if len(df) < n_events:
        raise ValueError(f"Catalog has only {len(df)} events, but {n_events} are required for the spatial window.")
        
    ev_lons = df["longitude"].values
    ev_lats = df["latitude"].values
    ev_mags = df["magnitude"].values
    
    rows, cols = grid_lon.shape
    mc_grid = np.full((rows, cols), np.nan)
    
    # In a real heavy-duty package we might use a BallTree/KDTree with Haversine metric.
    # For a simple EDA map, we can compute rough distance if the region isn't too huge.
    # We will use simple euclidean distance in degrees (approximate) for speed, 
    # but scale longitude by cos(latitude).
    
    mean_lat_rad = np.radians(np.mean(ev_lats))
    cos_lat = np.cos(mean_lat_rad)
    
    for i in range(rows):
        for j in range(cols):
            glon = grid_lon[i, j]
            glat = grid_lat[i, j]
            
            # Approximate distance squared
            dlon = (ev_lons - glon) * cos_lat
            dlat = (ev_lats - glat)
            dist_sq = dlon**2 + dlat**2
            
            # Find indices of nearest N events
            # Using argpartition is faster than full sort
            nearest_idx = np.argpartition(dist_sq, n_events - 1)[:n_events]
            
            local_mags = ev_mags[nearest_idx]
            
            # Compute MAXC + 0.2
            mc_grid[i, j] = calc_mc_maxc(local_mags, bin_width=0.1, correction=0.2)
            
    return mc_grid
