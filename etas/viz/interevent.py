import matplotlib.pyplot as plt
import numpy as np
from etas.catalog.model import Catalog

def plot_interevent_time(catalog: Catalog, ax=None):
    """
    Histogram of inter-event times vs theoretical Poisson.
    Cites: theme-3 (EDA); 01 Ogata 1988 (diagnostic plots motivation).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))

    if catalog.df.empty:
        return ax

    df = catalog.df.dropna(subset=["time"]).sort_values("time")
    if len(df) < 2:
        return ax

    dt_days = df["time"].diff().dt.total_seconds().dropna() / 86400.0
    dt_days = dt_days[dt_days > 0] # Avoid zeros
    
    if len(dt_days) == 0:
        return ax

    # Log binning
    min_dt, max_dt = dt_days.min(), dt_days.max()
    bins = np.logspace(np.log10(min_dt), np.log10(max_dt), 50)
    
    ax.hist(dt_days, bins=bins, density=True, alpha=0.6, color='b', label='Empirical')
    
    # Poisson reference line: exponential distribution for dt
    mean_rate = 1.0 / dt_days.mean()
    x = np.logspace(np.log10(min_dt), np.log10(max_dt), 100)
    y = mean_rate * np.exp(-mean_rate * x)
    ax.plot(x, y, 'r--', label='Poisson (Theoretical)')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Inter-event time (days)')
    ax.set_ylabel('Density')
    ax.set_title('Inter-event Time Distribution')
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return ax

def plot_cumulative_moment(catalog: Catalog, ax=None):
    """
    Cumulative seismic moment release over time.
    Cites: theme-3 (EDA). Formula: M0 = 10^(1.5 * Mw + 9.1).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))
        
    if catalog.df.empty:
        return ax
        
    df = catalog.df.dropna(subset=["time", "magnitude"]).sort_values("time")
    if df.empty:
        return ax
        
    times = df["time"]
    mags = df["magnitude"]
    
    # Calculate moment (N m)
    moment = 10 ** (1.5 * mags + 9.1)
    cum_moment = np.cumsum(moment)
    
    ax.step(times, cum_moment, where='post', color='r')
    ax.set_xlabel('Time')
    ax.set_ylabel('Cumulative Moment (N m)')
    ax.set_title('Cumulative Seismic Moment Release')
    ax.grid(True, linestyle="--", alpha=0.5)
    return ax

