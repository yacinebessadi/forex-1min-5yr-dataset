import enrich_fx
import pandas as pd

def enrich_new_candles(df_new: pd.DataFrame, pair: str) -> pd.DataFrame:
    """
    Enrich a DataFrame of new 1‑minute candles for a single pair
    using the same ICT feature pipeline as the historical dataset.

    Expects columns: timestamp, open, high, low, close, volume, missing_bar.
    Returns df_new with all ICT features added.
    """
    return enrich_fx.enrich_dataframe_for_pair(df_new.copy(), pair)
