from typing import Tuple
import pandas as pd
import json
import urllib.request
import urllib.parse
import ssl
from etas.catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    USGS ComCat client via GeoJSON. 
    """
    min_lon, max_lon, min_lat, max_lat = bbox
    start_time, end_time = time_range
    
    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": min_mag,
        "minlongitude": min_lon,
        "maxlongitude": max_lon,
        "minlatitude": min_lat,
        "maxlatitude": max_lat,
        "limit": 20000
    }
    
    query = urllib.parse.urlencode(params)
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?{query}"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode("utf-8"))
        
    records = []
    for feature in data.get("features", []):
        props = feature["properties"]
        geom = feature["geometry"]
        
        records.append({
            "event_id": feature["id"],
            "time": pd.to_datetime(props["time"], unit="ms", utc=True),
            "longitude": geom["coordinates"][0],
            "latitude": geom["coordinates"][1],
            "depth": geom["coordinates"][2],
            "magnitude": props["mag"],
            "magnitude_type": props["magType"],
            "agency": "USGS"
        })
        
    df = pd.DataFrame(records)
    return Catalog(df)
