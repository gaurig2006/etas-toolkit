"""
Catalog data model for ETAS forecasting.
Grounds the core tabular schema and serialization (CSV, Parquet).
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Union


REQUIRED_COLUMNS = {
    "event_id": "object",
    "time": "datetime64[ns, UTC]",
    "time_days": "float64",
    "longitude": "float64",
    "latitude": "float64",
    "depth": "float64",
    "magnitude": "float64",
    "magnitude_type": "object",
    "agency": "object"
}


class Catalog:
    """Typed container for standardized seismic event catalogs."""

    def __init__(self, df: pd.DataFrame, t0: Optional[pd.Timestamp] = None):
        self.df = self._validate_and_format(df.copy(), t0)

    @classmethod
    def _validate_and_format(cls, df: pd.DataFrame, t0: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in REQUIRED_COLUMNS.items()})

        # Ensure UTC datetime
        if not pd.api.types.is_datetime64_any_dtype(df["time"]):
            df["time"] = pd.to_datetime(df["time"], utc=True)
        elif df["time"].dt.tz is None:
            df["time"] = df["time"].dt.tz_localize("UTC")
        else:
            df["time"] = df["time"].dt.tz_convert("UTC")

        # Sort chronologically
        df = df.sort_values("time").reset_index(drop=True)

        # Compute continuous decimal days since reference origin t0
        origin_time = t0 if t0 is not None else df["time"].iloc[0]
        delta = df["time"] - origin_time
        df["time_days"] = delta.dt.total_seconds() / 86400.0

        # Type conversion
        df["event_id"] = df["event_id"].astype(str)
        df["longitude"] = df["longitude"].astype(np.float64)
        df["latitude"] = df["latitude"].astype(np.float64)
        df["depth"] = df["depth"].astype(np.float64)
        df["magnitude"] = df["magnitude"].astype(np.float64)
        df["magnitude_type"] = df["magnitude_type"].astype(str)
        df["agency"] = df["agency"].astype(str)

        # Validate coordinate limits
        if not (df["latitude"].between(-90.0, 90.0).all()):
            raise ValueError("Latitude values out of valid bounds [-90, 90]")
        if not (df["longitude"].between(-180.0, 180.0).all()):
            raise ValueError("Longitude values out of valid bounds [-180, 180]")

        return df[list(REQUIRED_COLUMNS.keys()) + [c for c in df.columns if c not in REQUIRED_COLUMNS]]

    def __len__(self) -> int:
        return len(self.df)

    def __repr__(self) -> str:
        if self.df.empty:
            return "<Catalog: 0 events>"
        t_min, t_max = self.df["time"].min(), self.df["time"].max()
        m_min, m_max = self.df["magnitude"].min(), self.df["magnitude"].max()
        return f"<Catalog: {len(self.df)} events | Range: {t_min.date()} to {t_max.date()} | M: [{m_min:.1f}, {m_max:.1f}]>"

    def to_csv(self, path: Union[str, Path]) -> None:
        self.df.to_csv(path, index=False)

    @classmethod
    def from_csv(cls, path: Union[str, Path]) -> Catalog:
        df = pd.read_csv(path)
        return cls(df)

    def to_parquet(self, path: Union[str, Path]) -> None:
        self.df.to_parquet(path, index=False)

    @classmethod
    def from_parquet(cls, path: Union[str, Path]) -> Catalog:
        df = pd.read_parquet(path)
        return cls(df)

    def copy(self) -> Catalog:
        return Catalog(self.df.copy())
