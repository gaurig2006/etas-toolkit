import pandas as pd
from typing import Tuple
from etas.catalog.model import Catalog

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    raise NotImplementedError("Scraper not yet implemented.")
