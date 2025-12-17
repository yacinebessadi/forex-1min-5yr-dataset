forex-1min-5yr-dataset
This project implements a production-grade data engineering pipeline to extract, clean, normalize, and validate 1-minute OHLCV Forex historical data for major FX pairs.
The goal is to deliver fully gap-checked, UTC-aligned, backtest-ready datasets suitable for quantitative research, algorithmic trading, and financial analysis—without requiring additional downstream cleaning.
The pipeline was built to meet institutional-style data quality requirements, including strict timestamp consistency, gap reporting, metadata generation, and reproducibility.
Objectives
Extract 1-minute OHLCV FX data from reliable broker/public sources
Normalize all timestamps to UTC
Enforce continuous 1-minute intervals
Detect, document, and optionally fill missing bars
Deliver ready-to-use datasets with full transparency and QA artifacts
Data Coverage
Timeframe: Rolling 5-year window
From: 2020-11-22 22:00:00 UTC
To: 2025-11-21 21:59:00 UTC
Interval: 1 minute
Trading Days: Weekdays only (Saturday/Sunday excluded)
Source: Dukascopy
Pairs Included: EURUSD, USDCHF, USDCAD, USDJPY, AUDUSD, GBPUSD (AUDUSD provided as example)
Deliverables (Per FX Pair)
Each currency pair includes:
Final 5-year 1-minute CSV (example: EURUSD)
Gap summary report (coverage, counts, missing bars)
Missing timestamps file (full list of gaps)
Metadata JSON (coverage, totals, source, notes)
Reproducible Jupyter notebook showing full extraction, cleaning, and validation pipeline

Extraction scripts (including example script for EURUSD)

Note: Only AUDUSD is uploaded here as a demonstration. The same pipeline was applied to all other major pairs.
