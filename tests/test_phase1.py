import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from etas.catalog.model import Catalog
from etas.catalog.projection import project_catalog, inverse_project
from etas.catalog.clean import filter_catalog, deduplicate, get_cache_path

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "event_id": ["nc1001", "nc1002", "nc1003"],
        "time": ["2020-01-01T00:00:00Z", "2020-01-02T12:00:00Z", "2020-01-02T12:00:01Z"],
        "longitude": [-122.1, -122.2, -122.2],
        "latitude": [37.5, 37.6, 37.6],
        "depth": [10.0, 5.0, 5.1],
        "magnitude": [2.5, 4.0, 3.9],
        "magnitude_type": ["Mw", "ML", "ML"],
        "agency": ["NCEDC", "NCEDC", "NCEDC"]
    })

def test_catalog_roundtrip_csv_parquet(sample_df, tmp_path):
    cat = Catalog(sample_df)
    assert len(cat) == 3
    assert "time_days" in cat.df.columns

    # Test CSV
    csv_path = tmp_path / "test.csv"
    cat.to_csv(csv_path)
    loaded_csv = Catalog.from_csv(csv_path)
    assert len(loaded_csv) == 3
    assert np.allclose(loaded_csv.df["magnitude"], cat.df["magnitude"])

    # Test Parquet
    pq_path = tmp_path / "test.parquet"
    cat.to_parquet(pq_path)
    loaded_pq = Catalog.from_parquet(pq_path)
    assert len(loaded_pq) == 3
    assert np.allclose(loaded_pq.df["time_days"], cat.df["time_days"])

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371000 # Radius of earth in meters
    return c * r

def test_projection_submeter_accuracy(sample_df):
    cat = Catalog(sample_df)
    projected = project_catalog(cat)
    assert "x_km" in projected.df.columns
    assert "y_km" in projected.df.columns

    # Test inverse round-trip precision (< 1 meter = 1e-3 km)
    c_lon, c_lat = projected.df.attrs["center_lon"], projected.df.attrs["center_lat"]
    rec_lon, rec_lat = inverse_project(
        projected.df["x_km"].values,
        projected.df["y_km"].values,
        c_lon,
        c_lat
    )
    dist_m = haversine(rec_lon, rec_lat, cat.df["longitude"].values, cat.df["latitude"].values)
    assert np.all(dist_m < 1.0)

def test_deduplication(sample_df):
    cat = Catalog(sample_df)
    cleaned = deduplicate(cat, dt_sec=2.0, dr_km=5.0)
    # nc1003 is within 1 sec and 0 km from nc1002, so it should be dropped
    assert len(cleaned) == 2

def test_serialization_preserves_origin_after_filter(sample_df, tmp_path):
    cat = Catalog(sample_df)
    orig_time_days = cat.df["time_days"].copy()
    
    # Filter to exclude the first event
    filtered = filter_catalog(cat, min_mag=3.0)
    assert len(filtered) == 2
    
    # Check that time_days hasn't shifted
    assert np.allclose(filtered.df["time_days"].values, orig_time_days.iloc[1:].values)
    assert filtered.origin_time == cat.origin_time
    
    # Serialize and reload
    pq_path = tmp_path / "filtered.parquet"
    filtered.to_parquet(pq_path)
    loaded = Catalog.from_parquet(pq_path)
    
    # Check again
    assert np.allclose(loaded.df["time_days"].values, filtered.df["time_days"].values)
    assert loaded.origin_time == filtered.origin_time
