# ETAS Toolkit 🌍📉

A comprehensive, mathematically rigorous Python library for statistical earthquake forecasting and analysis using the **Epidemic-Type Aftershock Sequence (ETAS)** model.

## 📖 What is ETAS?
Earthquakes do not happen randomly; they cluster in space and time. A large "Mainshock" triggers a cascade of "Aftershocks." The ETAS model treats earthquakes like a viral epidemic—calculating the baseline probability of random tectonic shifts (background rate) and the probability of those events triggering offspring (aftershock sequences).

This toolkit provides an **end-to-end pipeline** to download raw earthquake data, clean it, statistically calibrate the ETAS mathematical model using Machine Learning (EM Algorithm), and decluster the catalog to untangle the earthquake "family tree."

---

## 🚀 Setup and Installation
This project requires Python 3.12+ and uses Conda for strict environment management.

```bash
# Create and activate the environment
conda create -n etas -c conda-forge python=3.12
conda activate etas

# Install the toolkit
pip install -e .
```

---

## 🧩 Core Architecture & Modules

This project was built from scratch and is organized into modular pipelines:

### 1. Data Acquisition & Ingestion (`etas/sources/` & `etas/catalog/`)
* **Unified Downloader:** Automatically fetches earthquake catalogs from 8 global agencies (USGS, ISC, AFAD, GeoNet, EMSC) and custom web scrapers (INGV HORUS, Chile, Taiwan).
* **Caching Engine:** Bypasses API download limits (like the USGS 20,000 limit) via automated time-chunking and local `.parquet` caching.
* **Data Model:** Strictly typed Pandas objects that automatically handle QuakeML parsing and spatial pyproj coordinate projections.

### 2. Quality Control & Visualization (`etas/quality/` & `etas/viz/`)
* **Magnitude of Completeness ($M_c$):** Algorithms (MAXC, GFT) to detect sensor blind-spots.
* **b-value Statistics:** Aki-Utsu Maximum Likelihood Estimation (MLE) with Shi-Bolt standard error calculations.
* **Mapping:** Cartopy-powered geographical rendering of $M_c$ and $b$-value distribution heatmaps.

### 3. The ETAS Mathematical Model (`etas/model/`)
* **Fully Vectorized Math:** The temporal and spatial intensity equations (Ogata 1988) are implemented using strict NumPy broadcasting matrices, completely eliminating slow Python `for`-loops.
* **Spatial Kernels:** Supports both Power-law and Gaussian spatial magnitude-scaling kernels.

### 4. Machine Learning Calibration (`etas/calibrate/`)
* **Expectation-Maximization (EM):** Uses a multi-restart EM algorithm (Veen & Schoenberg 2008) to safely calibrate the ETAS parameters without the math failing to converge.
* **Spatial Background:** Uses a Zhuang fixed-point loop and Cross-Validated Kernel Density Estimation (KDE) to map the geographic background seismicity.

### 5. Stochastic Declustering (`etas/decluster/`)
* **Graph Genealogy:** Uses the calibrated ETAS model to calculate the exact probability matrix ($\rho_{ij}$) of one earthquake triggering another.
* **Declustering:** Automatically separates independent background earthquakes from triggered aftershocks using binomial sampling.

---

## 💻 CLI Usage Example

You can easily download and cache earthquake data using the built-in Command Line Interface:

```bash
# Download a cleaned California catalog for the year 2020 (Magnitude 3.0+)
python -m etas.sources fetch --region california --from-year 2020 --to-year 2020 --min-mag 3.0 --out my_catalog.parquet
```

---

## 📚 Documentation & Proofs
* **Mathematical Derivations:** Full mathematical proofs for the EM algorithm, $b$-value MLE, and spatial kernels are located in `docs/notes/`.
* **Project Status:** For a detailed breakdown of completion status by Phase, please read `HANDOFF.md`.
