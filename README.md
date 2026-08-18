# ETAS Toolkit

A comprehensive Python library for statistical earthquake forecasting and analysis using the Epidemic-Type Aftershock Sequence (ETAS) model.

## Overview
This toolkit serves as an end-to-end forecasting pipeline to acquire, prepare, calibrate, and simulate earthquake catalogs.

## Repository Layout
- `etas/sources/`: Multi-agency downloaders (FDSN, REST, scrapers)
- `etas/catalog/`: Data model, QuakeML ingestion, projections, clean/dedup
- `etas/quality/`: Mc completeness suites and b-value estimators
- `etas/viz/`: EDA diagnostics and plotting utilities
- `etas/model/`: Conditional intensity, kernels, and likelihood
- `etas/calibrate/`: EM algorithm driver and KDE background field
- `etas/decluster/`: Stochastic declustering and triggering graphs
- `etas/simulate/`: Branching simulation and bootstrap
- `etas/evaluate/`: CSEP-style forecast evaluations
- `etas/features/`: Strictly causal spatial feature pipelines
