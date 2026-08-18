"""
Planar coordinate projection engine for ETAS spatial kernels.
Converts between geographic coordinates (lon, lat) and local Cartesian kilometers.
"""

from __future__ import annotations
import numpy as np
import pyproj
from typing import Tuple, Optional
from .model import Catalog


def get_local_projector(center_lon: float, center_lat: float) -> pyproj.Proj:
    """
    Builds forward Transverse Mercator projection centered on the catalog.
    """
    proj_str = f"+proj=tmerc +lat_0={center_lat} +lon_0={center_lon} +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +units=km +no_defs"
    return pyproj.Proj(proj_str)


def project_catalog(catalog: Catalog, center_lon: Optional[float] = None, center_lat: Optional[float] = None) -> Catalog:
    """
    Computes Cartesian x_km and y_km for all events in the catalog.
    """
    df = catalog.df.copy()
    if df.empty:
        df["x_km"] = np.array([], dtype=np.float64)
        df["y_km"] = np.array([], dtype=np.float64)
        return Catalog(df)

    c_lon = center_lon if center_lon is not None else float(df["longitude"].median())
    c_lat = center_lat if center_lat is not None else float(df["latitude"].median())

    proj = get_local_projector(c_lon, c_lat)
    x_km, y_km = proj(df["longitude"].values, df["latitude"].values)

    df["x_km"] = x_km
    df["y_km"] = y_km
    df.attrs["center_lon"] = c_lon
    df.attrs["center_lat"] = c_lat

    cat = catalog.copy()
    cat.df = df
    return cat


def inverse_project(x_km: np.ndarray, y_km: np.ndarray, center_lon: float, center_lat: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Transforms Cartesian offsets in km back into geographic longitude and latitude.
    """
    proj = get_local_projector(center_lon, center_lat)
    lon, lat = proj(x_km, y_km, inverse=True)
    return lon, lat
