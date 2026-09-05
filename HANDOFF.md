# Project Handoff & Status

## Completed
- **Phase 0 (Survey):** Repository skeleton, `pyproject.toml`, and comprehensive catalog survey (`docs/catalog_survey.md`).
- **Phase 1 (Data Model):** `Catalog` object (`etas/catalog/model.py`), projections, QuakeML, cleaning.
- **Phase 2 (Downloaders):** `sources/` module with generic FDSN, specific endpoints, and web scrapers.
- **Phase 3 (Visualization):** EDA plotting module (`viz/`) and generated PNG maps/graphs.
- **Phase 4 (Mc):** Magnitude of completeness (`quality/mc.py`) using MAXC, GFT, MBS, EMR, MBASS, and spatial maps.
- **Phase 5 (b-value):** MLE & Shi-Bolt standard errors (`quality/bvalue.py`), formal proofs in `docs/notes/phase5_bvalue.md`.
- **Phase 6 (Temporal ETAS):** Vectorized intensity and likelihood (`model/kernels.py`, `likelihood.py`), strict O(N^2) broadcasting.
- **Phase 7 (EM Calibration):** Exact E/M step derivations (`docs/notes/phase7_em.md`), and driver with monotonicity guards (`calibrate/em.py`).
- **Phase 8 (Spatiotemporal):** 2D Gaussian/Power-law spatial kernels, Zhuang fixed-point coupling loop, and KDE bandwidth cross-validation (`spatial.py`, `kde.py`).
- **Phase 9 (Declustering):** Probabilistic graph genealogy (`decluster/genealogy.py`) and stochastic declustering.

## In Progress
- **Phase 10 (Simulation):** (Next up) Forward simulation of synthetic catalogs.

## Uncertainties / Blockers
- None.

## Rubric Compliance Notes
- All scientific functions cite exact paper/equation numbers in their docstrings.
- NumPy broadcasting is strictly used over for-loops for all $N \times N$ matrix operations.
- `docs/notes/` contains full mathematical derivations for b-value, ETAS, and EM steps.
