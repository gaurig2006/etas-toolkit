import os
import subprocess
import pytest

SOURCES_TO_TEST = [
    ("comcat", "usgs"),
    ("isc", "isc"),
    # ("gcmt", "gcmt"), # We'll skip gcmt for tiny queries since it downloads a 12MB ndk file, but wait, let's include it
    ("afad", "afad"),
    ("geonet", "geonet"),
    ("csn_chile", "chile"),
    ("ingv_horus", "ingv_horus")
]

def test_smoke_cli():
    # Setup proxy for tests
    env = os.environ.copy()
    env["HTTP_PROXY"] = "http://127.0.0.1:3128"
    env["HTTPS_PROXY"] = "http://127.0.0.1:3128"
    
    for source_name, region in SOURCES_TO_TEST:
        print(f"Testing {region}...")
        cmd = [
            "/mnt/hdd/home/gauri/conda-envs/etas/bin/python", "-m", "etas.sources", "fetch",
            "--region", region,
            "--from-year", "2020",
            "--to-year", "2020",
            "--min-mag", "6.5",
            "--out", f"smoke_{region}.parquet"
        ]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert res.returncode == 0, f"Failed for {region}: {res.stderr}"
        assert os.path.exists(f"smoke_{region}.parquet")
