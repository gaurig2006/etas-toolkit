"""
QuakeML parsing engine via ObsPy for universal FDSN catalog ingestion.
"""

from __future__ import annotations
import io
import warnings
import pandas as pd
from pathlib import Path
from typing import Union
from obspy import read_events
from .model import Catalog


def parse_quakeml(source: Union[str, Path, io.BytesIO, "obspy.core.event.Catalog"]) -> Catalog:
    """
    Parses QuakeML XML data into a standardized Catalog instance.
    """
    if hasattr(source, "events"):
        cat_obspy = source
    else:
        cat_obspy = read_events(str(source) if isinstance(source, Path) else source)
        
    records = []
    skipped_count = 0

    for event in cat_obspy:
        # Extract preferred origin and magnitude
        origin = event.preferred_origin() or (event.origins[0] if event.origins else None)
        mag_obj = event.preferred_magnitude() or (event.magnitudes[0] if event.magnitudes else None)

        if origin is None or mag_obj is None:
            skipped_count += 1
            continue

        event_id = str(event.resource_id).split("/")[-1].split("=")[-1]
        agency = origin.creation_info.agency_id if (origin.creation_info and origin.creation_info.agency_id) else "FDSN"
        mag_val = mag_obj.mag
        mag_type = mag_obj.magnitude_type or "M"
        depth_km = (origin.depth / 1000.0) if origin.depth is not None else float('nan')

        records.append({
            "event_id": event_id,
            "time": origin.time.datetime,
            "longitude": origin.longitude,
            "latitude": origin.latitude,
            "depth": depth_km,
            "magnitude": mag_val,
            "magnitude_type": mag_type,
            "agency": agency
        })

    if skipped_count > 0:
        warnings.warn(f"Skipped {skipped_count} events due to missing origin or magnitude.")

    df = pd.DataFrame(records)
    return Catalog(df)
