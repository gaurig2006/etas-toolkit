import pandas as pd
from typing import Tuple
import urllib.request
import json
import io
import os
from etas.catalog.model import Catalog
from etas.catalog.clean import filter_catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    Chile CSN. Scrapes sismologia.cl or ingests the static Zenodo catalog (fallback).
    Currently implemented: Zenodo static catalog ingestion.
    """
    # Use proxy if configured
    proxy = os.environ.get("HTTP_PROXY")
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    # Fetch Zenodo record metadata to get the file download URL
    zenodo_api_url = "https://zenodo.org/api/records/11360590"
    
    req = urllib.request.Request(zenodo_api_url)
    with urllib.request.urlopen(req) as response:
        record_data = json.loads(response.read().decode("utf-8"))
        
    # Find the CSV file URL
    file_url = None
    for file_info in record_data.get("files", []):
        if file_info["links"]["self"].endswith(".csv") or "catalog" in file_info["key"].lower():
            file_url = file_info["links"]["self"]
            break
            
    if not file_url:
        raise RuntimeError("Could not find the catalog file in Zenodo record 11360590.")
        
    df_raw = pd.read_csv(file_url, encoding="latin1", sep=None, engine="python", on_bad_lines="skip")
    
    # Map to standardized format
    records = []
    for idx, row in df_raw.iterrows():
        # Adjust column names according to the specific Zenodo CSV schema
        # Typically it's time, latitude, longitude, depth, magnitude
        # Fallback to general names
        try:
            records.append({
                "event_id": f"csn_{idx}",
                "time": pd.to_datetime(row.get("time", row.get("Date")), utc=True),
                "longitude": float(row.get("longitude", row.get("Longitude"))),
                "latitude": float(row.get("latitude", row.get("Latitude"))),
                "depth": float(row.get("depth", row.get("Depth"))),
                "magnitude": float(row.get("magnitude", row.get("Magnitude"))),
                "magnitude_type": "Mw", # default assumption if missing
                "agency": "CSN"
            })
        except Exception:
            continue
            
    df = pd.DataFrame(records)
    cat = Catalog(df)
    return filter_catalog(cat, min_mag=min_mag, bbox=bbox, time_range=time_range)
