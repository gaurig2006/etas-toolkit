import argparse
import pandas as pd
from typing import Tuple
from etas.catalog.model import Catalog
from . import fdsn, comcat, isc, gcmt, afad, geonet

# Note: We'll add scrapers later as they are built.
SOURCES = {
    "usgs": comcat.get_events,
    "isc": isc.get_events,
    "gcmt": gcmt.get_events,
    "afad": afad.get_events,
    "geonet": geonet.get_events,
    # Map regions to default sources
    "california": comcat.get_events,
    "global": comcat.get_events,
    "italy": lambda bbox, tr, mag: fdsn.FDSNClient("INGV").get_events(bbox, tr, mag),
    "greece": lambda bbox, tr, mag: fdsn.FDSNClient("NOA").get_events(bbox, tr, mag),
    "new_zealand": geonet.get_events,
    "turkiye": afad.get_events,
}

def get_events(
    source: str,
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    source_lower = source.lower()
    if source_lower not in SOURCES:
        raise ValueError(f"Unknown source or region: {source}. Available: {list(SOURCES.keys())}")
    
    fetch_func = SOURCES[source_lower]
    return fetch_func(bbox, time_range, min_mag)
