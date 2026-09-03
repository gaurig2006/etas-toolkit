import matplotlib.pyplot as plt
import numpy as np
from etas.catalog.model import Catalog

def plot_time_magnitude(catalog: Catalog, ax=None):
    """
    Stem-style plot of time vs magnitude.
    Cites: theme-3 (EDA).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["time", "magnitude"]).sort_values("time")
    if df.empty:
        return ax

    ax.vlines(df["time"], ymin=df["magnitude"].min(), ymax=df["magnitude"], color='b', alpha=0.5, linewidth=0.5)
    ax.scatter(df["time"], df["magnitude"], s=10, color='b', alpha=0.7)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.set_title('Time vs Magnitude')
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return ax

def plot_cumulative_events(catalog: Catalog, ax=None):
    """
    Step plot of cumulative event count over time.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["time"]).sort_values("time")
    if df.empty:
        return ax

    times = df["time"].values
    counts = np.arange(1, len(times) + 1)
    
    ax.step(times, counts, where='post', color='k')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative Number of Events')
    ax.set_title('Cumulative Event Count')
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return ax

def plot_time_mag_density(catalog: Catalog, ax=None):
    """
    Hexbin density plot of magnitude over time.
    """
    import matplotlib.dates as mdates
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    if catalog.df.empty:
        return ax
        
    df = catalog.df.dropna(subset=["time", "magnitude"])
    if df.empty:
        return ax
        
    # Convert dates to matplotlib numbers for hexbin
    dates = mdates.date2num(df["time"])
    mags = df["magnitude"]
    
    hb = ax.hexbin(dates, mags, gridsize=50, cmap='inferno', mincnt=1)
    ax.xaxis_date()
    
    # Add colorbar
    plt.colorbar(hb, ax=ax, label='Event Count')
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.set_title('Time-Magnitude Density')
    return ax

