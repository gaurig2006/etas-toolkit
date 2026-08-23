import pandas as pd
from typing import Tuple, Optional
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException
from etas.catalog.model import Catalog
from etas.catalog.quakeml import parse_quakeml
import warnings

class FDSNClient:
    def __init__(self, base_url: str):
        try:
            self.client = Client(base_url)
        except Exception:
            self.client = Client(base_url, _discover_services=False)
        self.base_url = base_url

    def get_events(
        self,
        bbox: Tuple[float, float, float, float],
        time_range: Tuple[pd.Timestamp, pd.Timestamp],
        min_mag: float
    ) -> Catalog:
        """
        Fetches events from an FDSN service. Handles the 20,000-event cap
        by splitting the request into smaller time windows if necessary.
        """
        min_lon, max_lon, min_lat, max_lat = bbox
        start_time, end_time = time_range
        
        return self._fetch_with_chunking(
            min_lon=min_lon, max_lon=max_lon,
            min_lat=min_lat, max_lat=max_lat,
            start_time=start_time, end_time=end_time,
            min_mag=min_mag
        )
        
    def _fetch_with_chunking(self, min_lon, max_lon, min_lat, max_lat, start_time, end_time, min_mag) -> Catalog:
        from obspy import UTCDateTime
        
        current_start = start_time
        catalogs = []
        
        while current_start < end_time:
            try:
                cat_obspy = self.client.get_events(
                    starttime=UTCDateTime(current_start),
                    endtime=UTCDateTime(end_time),
                    minlatitude=min_lat,
                    maxlatitude=max_lat,
                    minlongitude=min_lon,
                    maxlongitude=max_lon,
                    minmagnitude=min_mag
                )
                if len(cat_obspy) > 0:
                    catalogs.append(parse_quakeml(cat_obspy).df)
                break  # If successful, we got everything to the end_time
                
            except FDSNException as e:
                # FDSN throws exception typically with HTTP 400 or 413 for too much data
                err_msg = str(e).lower()
                if "400" in err_msg or "413" in err_msg or "limit" in err_msg or "too many" in err_msg:
                    # Time window too large, split it in half
                    current_end = current_start + (end_time - current_start) / 2
                    warnings.warn(f"FDSN limit reached, splitting time window: {current_start} to {current_end}")
                    
                    try:
                        chunk_cat = self._fetch_with_chunking(
                            min_lon, max_lon, min_lat, max_lat,
                            current_start, current_end, min_mag
                        )
                        catalogs.append(chunk_cat.df)
                        current_start = current_end
                    except RecursionError:
                        raise RuntimeError("FDSN limit reached, but time window cannot be split further.")
                else:
                    # Reraise if it's not a limit error
                    raise
            except Exception as e:
                raise

        if not catalogs:
            return Catalog(pd.DataFrame())
            
        combined_df = pd.concat(catalogs, ignore_index=True).drop_duplicates(subset=["event_id"])
        # Determine the earliest time in the original request to use as origin_time
        # Or just let Catalog infer it
        return Catalog(combined_df, t0=pd.to_datetime(start_time, utc=True))
