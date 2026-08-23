"""
Catalog cleaning, spatial/temporal filtering, de-duplication, and local caching.
"""

from __future__ import annotations
import os
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from .model import Catalog


CACHE_DIR = Path(os.path.expanduser("~/.etas_cache"))


def get_cache_path(key: str) -> Path:
    """Returns the parquet path for a deterministic SHA256 query cache key."""
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.parquet"


def read_cache(key: str) -> Optional[Catalog]:
    path = get_cache_path(key)
    if path.exists():
        return Catalog.from_parquet(path)
    return None


def write_cache(catalog: Catalog, key: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    catalog.to_parquet(get_cache_path(key))


def filter_catalog(
    catalog: Catalog,
    min_mag: Optional[float] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    time_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None
) -> Catalog:
    """
    Applies bounding box (min_lon, max_lon, min_lat, max_lat), magnitude, and temporal filters.
    """
    df = catalog.df.copy()

    if min_mag is not None:
        df = df[df["magnitude"] >= min_mag]

    if bbox is not None:
        min_lon, max_lon, min_lat, max_lat = bbox
        df = df[
            (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon) &
            (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)
        ]

    if time_range is not None:
        t_start, t_end = time_range
        t_start = pd.to_datetime(t_start, utc=True)
        t_end = pd.to_datetime(t_end, utc=True)
        df = df[(df["time"] >= t_start) & (df["time"] <= t_end)]

    return Catalog(df, t0=catalog.origin_time)


def deduplicate(catalog: Catalog, dt_sec: float = 2.0, dr_km: float = 5.0) -> Catalog:
    """
    Removes duplicate event recordings within time window dt_sec and spatial radius dr_km.
    """
    df = catalog.df.copy()
    if len(df) <= 1:
        return catalog.copy()

    # Time-based candidate filter
    df = df.sort_values("time").reset_index(drop=True)
    keep = np.ones(len(df), dtype=bool)

    times = df["time"].values
    lons = df["longitude"].values
    lats = df["latitude"].values

    for i in range(len(df) - 1):
        if not keep[i]:
            continue
        # Approximate distance in km: 111.19 km per degree
        j = i + 1
        while j < len(df):
            if not keep[j]:
                j += 1
                continue
            dt = (times[j] - times[i]) / np.timedelta64(1, 's')
            if dt > dt_sec:
                break
            d_lat = (lats[j] - lats[i]) * 111.19
            d_lon = (lons[j] - lons[i]) * 111.19 * np.cos(np.radians(lats[i]))
            dist = np.sqrt(d_lat**2 + d_lon**2)
            if dist <= dr_km:
                keep[j] = False  # Mark secondary event as duplicate
            j += 1

    return Catalog(df[keep], t0=catalog.origin_time)

def convert_ml_to_mw(ml: float) -> float:
    """Stub function to convert Local Magnitude (ML) to Moment Magnitude (Mw)."""
    pass

def convert_md_to_mw(md: float) -> float:
    """Stub function to convert Duration Magnitude (Md) to Moment Magnitude (Mw)."""
    pass

def convert_mb_to_mw(mb: float) -> float:
    """Stub function to convert Body-Wave Magnitude (mb) to Moment Magnitude (Mw)."""
    pass
