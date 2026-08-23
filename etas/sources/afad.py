import urllib.request
import urllib.parse
import json
import pandas as pd
from typing import Tuple
from etas.catalog.model import Catalog

AFAD_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    Türkiye AFAD custom REST/JSON API client.
    """
    min_lon, max_lon, min_lat, max_lat = bbox
    start_time, end_time = time_range
    
    # Format times like 2020-01-01T00:00:00
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
    
    params = {
        "minlat": min_lat,
        "maxlat": max_lat,
        "minlon": min_lon,
        "maxlon": max_lon,
        "start": start_str,
        "end": end_str,
        "minmag": min_mag
    }
    
    query = urllib.parse.urlencode(params)
    url = f"{AFAD_URL}?{query}"
    
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        
    records = []
    for evt in data:
        records.append({
            "event_id": evt.get("eventID", str(evt.get("id"))),
            "time": pd.to_datetime(evt.get("date"), utc=True),
            "longitude": float(evt.get("longitude")),
            "latitude": float(evt.get("latitude")),
            "depth": float(evt.get("depth")),
            "magnitude": float(evt.get("magnitude")),
            "magnitude_type": evt.get("type", "M"),
            "agency": "AFAD"
        })
        
    df = pd.DataFrame(records)
    return Catalog(df)
