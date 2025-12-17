from datetime import datetime
import dukascopy_python
from dukascopy_python.instruments import INSTRUMENT_FX_MAJORS_EUR_USD


instrument = INSTRUMENT_FX_MAJORS_EUR_USD
interval   = dukascopy_python.INTERVAL_MIN_1
offer_side = dukascopy_python.OFFER_SIDE_BID


ranges = [
    # Partial 2020
    ("2020-11-22_2020-12-31",
     datetime(2020, 11, 22, 0, 0, 0),
     datetime(2020, 12, 31, 23, 59, 0)),

    # Full years
    ("2021-01-01_2021-12-31",
     datetime(2021, 1, 1, 0, 0, 0),
     datetime(2021, 12, 31, 23, 59, 0)),

    ("2022-01-01_2022-12-31",
     datetime(2022, 1, 1, 0, 0, 0),
     datetime(2022, 12, 31, 23, 59, 0)),

    ("2023-01-01_2023-12-31",
     datetime(2023, 1, 1, 0, 0, 0),
     datetime(2023, 12, 31, 23, 59, 0)),

    ("2024-01-01_2024-12-31",
     datetime(2024, 1, 1, 0, 0, 0),
     datetime(2024, 12, 31, 23, 59, 0)),

    # Year‑to‑date 2025
    ("2025-01-01_2025-11-22",
     datetime(2025, 1, 1, 0, 0, 0),
     datetime(2025, 11, 22, 23, 59, 0)),
]


first_done = False

for label, start, end in ranges:
    print(f"Downloading {label} ...")
    df = dukascopy_python.fetch(
        instrument,
        interval,
        offer_side,
        start,
        end,
    )

    # timestamp is the index in UTC per dukascopy-python docs
    df = df.reset_index()

    out_name = f"EURUSD_1m_raw_{label}.csv"
    df.to_csv(out_name, index=False)
    print(f"Saved {out_name} with columns: {df.columns.tolist()}")

    if not first_done:
        print(f"[DEBUG] First segment ({label}) downloaded successfully, rows: {len(df)}.")
        first_done = True
