import os
import pandas as pd
from etas.sources.registry import get_events
from etas.viz.eda import plot_eda

# Setup proxy
os.environ["HTTP_PROXY"] = "http://127.0.0.1:3128"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:3128"

def main():
    start_time = pd.to_datetime("2010-01-01T00:00:00Z")
    end_time = pd.to_datetime("2020-12-31T23:59:59Z")
    
    print("Fetching California catalog...")
    cat_ca = get_events("california", (-125.0, -114.0, 32.0, 42.0), (start_time, end_time), 3.0)
    print(f"Loaded {len(cat_ca.df)} events.")
    
    print("Generating California EDA plot...")
    plot_eda(cat_ca, save_path="docs/figures/california_eda.png")
    
    print("Fetching Italy catalog...")
    cat_it = get_events("italy", (6.0, 19.0, 36.0, 48.0), (start_time, end_time), 3.0)
    print(f"Loaded {len(cat_it.df)} events.")
    
    print("Generating Italy EDA plot...")
    plot_eda(cat_it, save_path="docs/figures/italy_eda.png")
    
    print("Done!")

if __name__ == "__main__":
    main()
