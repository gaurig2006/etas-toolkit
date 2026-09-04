import os
import urllib.request
import zipfile
import pandas as pd
from typing import Tuple
from pathlib import Path
from etas.catalog.model import Catalog
from etas.catalog.clean import filter_catalog, CACHE_DIR

HORUS_URL = "https://horus.bo.ingv.it/DataFolder/HORUS_Ita_Catalog.zip"

def get_events(
    bbox: Tuple[float, float, float, float],
    time_range: Tuple[pd.Timestamp, pd.Timestamp],
    min_mag: float
) -> Catalog:
    """
    INGV HORUS bulk file scraper.
    Downloads the large zip file once, caches it, and extracts the catalog.
    """
    # Use proxy if configured
    proxy = os.environ.get("HTTP_PROXY")
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = CACHE_DIR / "HORUS_Ita_Catalog.zip"
    txt_path = CACHE_DIR / "HORUS_Ita_Catalog.txt"

    if not txt_path.exists():
        if not zip_path.exists():
            print(f"Downloading HORUS bulk catalog from {HORUS_URL}...")
            urllib.request.urlretrieve(HORUS_URL, zip_path)
            
        print("Extracting HORUS catalog...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract("HORUS_Ita_Catalog.txt", path=CACHE_DIR)
            
    # Parse the file. HORUS is usually tab-delimited or pipe-delimited text.
    # Assuming tab-delimited with standard columns: Time, Lat, Lon, Depth, Mag
    try:
        df_raw = pd.read_csv(txt_path, sep=r'\s+', low_memory=False)
        
        # We need to map to our internal format
        # If columns are e.g. year, month, day, hr, min, sec, lat, lon, dep, mw
        # We try to infer or just map standard HORUS columns
        # Typical HORUS columns: #Year Month Day Hour Minute Second Lat Lon Depth Mw
        
        if "Year" in df_raw.columns:
            # Construct datetime
            df_raw.rename(columns={"Mo": "Month", "Da": "Day", "Ho": "Hour", "Mi": "Minute", "Se": "Second"}, inplace=True)
            df_raw["time"] = pd.to_datetime(df_raw[["Year", "Month", "Day", "Hour", "Minute", "Second"]])
            df_raw = df_raw.rename(columns={"Lat": "latitude", "Lon": "longitude", "Depth": "depth", "Mw": "magnitude"})
            df_raw["magnitude_type"] = "Mw"
        else:
            # fallback if columns differ
            pass
            
        df_raw["agency"] = "INGV-HORUS"
        df_raw["event_id"] = ["horus_" + str(i) for i in range(len(df_raw))]
        
        # Ensure we only have the required columns
        # This will fail if columns don't match, which is fine for a stub/first pass
        
        cat = Catalog(df_raw)
        return filter_catalog(cat, min_mag=min_mag, bbox=bbox, time_range=time_range)
        
    except Exception as e:
        raise RuntimeError(f"Error parsing HORUS catalog: {e}")
