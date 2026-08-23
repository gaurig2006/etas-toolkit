import urllib.parse
import pandas as pd
from typing import Tuple
from etas.catalog.model import Catalog
from etas.catalog.clean import filter_catalog

GEONET_URL = "https://quakesearch.geonet.org.nz/csv"

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    New Zealand GeoNet QuakeSearch CSV client.
    """
    min_lon, max_lon, min_lat, max_lat = bbox
    start_time, end_time = time_range
    
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # bbox in geonet is usually min_lon, min_lat, max_lon, max_lat
    bbox_str = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    
    params = {
        "bbox": bbox_str,
        "startdate": start_str,
        "enddate": end_str,
        "minmag": min_mag
    }
    
    query = urllib.parse.urlencode(params)
    url = f"{GEONET_URL}?{query}"
    
    df_raw = pd.read_csv(url)
    
    if df_raw.empty:
        return Catalog(pd.DataFrame())
        
    records = []
    for _, row in df_raw.iterrows():
        records.append({
            "event_id": str(row["publicid"]),
            "time": pd.to_datetime(row["origintime"], utc=True),
            "longitude": float(row["longitude"]),
            "latitude": float(row["latitude"]),
            "depth": float(row["depth"]),
            "magnitude": float(row["magnitude"]),
            "magnitude_type": str(row["magnitudetype"]),
            "agency": "GeoNet"
        })
        
    df = pd.DataFrame(records)
    return Catalog(df)
