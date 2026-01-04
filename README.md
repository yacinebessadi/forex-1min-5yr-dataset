Forex Data Engineering: Raw Extraction to Quantitative Enrichment

This project establishes a production-grade pipeline to transform raw 1-minute Forex data into a high-fidelity, ML-ready format for quantitative analysis (NEX System). The workflow operates in two phases:

Phase 1: Canonical Cleaning: Extracts 5 years of raw OHLCV data, normalizes timestamps to strict UTC, and ensures time-series continuity by detecting and filling missing bars.

Phase 2: ICT-Aware Enrichment: Applies a deterministic ETL process to engineer complex financial features—such as Liquidity Sweeps, Swing Points, and Session Killzones—using high-performance Pandas vectorization.

Key Technical Highlights:

Timezone Intelligence: Automates dynamic mapping between UTC and New York trading sessions, accounting for DST.

Leakage Prevention: Implements strict lookback windows to ensure data integrity for backtesting.

Scalability: Modular architecture supports both massive historical batch processing and real-time daily data streams.
