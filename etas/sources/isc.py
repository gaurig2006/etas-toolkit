from typing import Tuple
import pandas as pd
from etas.catalog.model import Catalog
from .fdsn import FDSNClient

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    ISC client via FDSN.
    TODO: Add ISC-GEM bulk CSV downloading for long-term large-event completeness.
    """
    client = FDSNClient("ISC")
    return client.get_events(bbox, time_range, min_mag)
