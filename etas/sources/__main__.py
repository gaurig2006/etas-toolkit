import argparse
import pandas as pd
from etas.sources.registry import get_events
from etas.catalog.clean import read_cache, write_cache

def main():
    parser = argparse.ArgumentParser(description="Fetch earthquake catalogs.")
    parser.add_argument("action", choices=["fetch"], help="Action to perform")
    parser.add_argument("--region", required=True, help="Region or source name (e.g. california, italy, usgs)")
    parser.add_argument("--from-year", dest="from_yr", required=True, type=int, help="Start year")
    parser.add_argument("--to-year", dest="to_yr", required=True, type=int, help="End year")
    parser.add_argument("--min-mag", required=True, type=float, help="Minimum magnitude")
    parser.add_argument("--bbox", type=str, help="Bounding box min_lon,max_lon,min_lat,max_lat")
    parser.add_argument("--out", type=str, default="catalog.parquet", help="Output file path (CSV or Parquet)")
    
    args = parser.parse_args()
    
    if args.action == "fetch":
        start_time = pd.to_datetime(f"{args.from_yr}-01-01T00:00:00Z")
        end_time = pd.to_datetime(f"{args.to_yr}-12-31T23:59:59Z")
        
        if args.bbox:
            bbox = tuple(map(float, args.bbox.split(",")))
        else:
            bbox = (-180.0, 180.0, -90.0, 90.0)
            
        print(f"Fetching catalog for {args.region} from {args.from_yr} to {args.to_yr}, M>={args.min_mag}...")
        
        # Check cache first
        cache_key = f"{args.region}_{args.from_yr}_{args.to_yr}_{args.min_mag}_{bbox}"
        catalog = read_cache(cache_key)
        
        if catalog is not None:
            print("Loaded from cache.")
        else:
            catalog = get_events(args.region, bbox, (start_time, end_time), args.min_mag)
            write_cache(catalog, cache_key)
            print("Downloaded and cached.")
        
        print(f"Fetched {len(catalog)} events.")
        if args.out.endswith(".csv"):
            catalog.to_csv(args.out)
        else:
            catalog.to_parquet(args.out)
        print(f"Saved to {args.out}")

if __name__ == "__main__":
    main()
