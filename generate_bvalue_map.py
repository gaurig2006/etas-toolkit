import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from etas.sources.registry import get_events
from etas.quality.mc_map import map_spatial_mc
from etas.quality.bvalue_map import map_spatial_b
from etas.viz.space import plot_spatial_b

# Setup proxy
os.environ["HTTP_PROXY"] = "http://127.0.0.1:3128"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:3128"

def main():
    start_time = pd.to_datetime("2010-01-01T00:00:00Z")
    end_time = pd.to_datetime("2020-12-31T23:59:59Z")
    
    print("Fetching California catalog from cache (or downloading if missing)...")
    # Using California bbox
    cat_ca = get_events("california", (-125.0, -114.0, 32.0, 42.0), (start_time, end_time), 3.0)
    print(f"Loaded {len(cat_ca.df)} events.")
    
    # Define a grid over California
    lon_min, lon_max = -125.0, -114.0
    lat_min, lat_max = 32.0, 42.0
    
    # 0.25 degree resolution
    grid_lon_1d = np.arange(lon_min, lon_max, 0.25)
    grid_lat_1d = np.arange(lat_min, lat_max, 0.25)
    
    grid_lon, grid_lat = np.meshgrid(grid_lon_1d, grid_lat_1d)
    
    print("Computing spatial Mc grid (MAXC + 0.2) as prerequisite...")
    mc_values = map_spatial_mc(cat_ca, grid_lon, grid_lat, n_events=250)
    
    print("Computing spatial b-value grid...")
    b_values = map_spatial_b(cat_ca, grid_lon, grid_lat, mc_values, n_events=250)
    
    print("Plotting b-value map...")
    ax = plot_spatial_b(grid_lon, grid_lat, b_values)
    
    save_path = "docs/figures/california_bvalue_map.png"
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    fig = ax.figure
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {save_path}")

if __name__ == "__main__":
    main()
