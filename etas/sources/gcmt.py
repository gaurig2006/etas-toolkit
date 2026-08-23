import io
import urllib.request
from typing import Tuple
import pandas as pd
from obspy import read_events
from etas.catalog.model import Catalog
from etas.catalog.quakeml import parse_quakeml

# Note: GCMT maintains a single large NDK for 1976-2020 and monthly files after.
GCMT_URL = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/jan76_dec20.ndk"

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    Global CMT client. Downloads .ndk and parses via ObsPy.
    Currently only fetches the historical catalog (1976-2020).
    """
    # Download the NDK
    req = urllib.request.Request(GCMT_URL)
    with urllib.request.urlopen(req) as response:
        ndk_data = response.read()

    # Parse with ObsPy
    cat_obspy = read_events(io.BytesIO(ndk_data), format="NDK")
    
    # Use our parse_quakeml to convert obspy Catalog to our Catalog
    catalog = parse_quakeml(cat_obspy)
    
    # Filter by bbox, time, and min_mag
    from etas.catalog.clean import filter_catalog
    return filter_catalog(catalog, min_mag=min_mag, bbox=bbox, time_range=time_range)
