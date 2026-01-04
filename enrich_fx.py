import pandas as pd
from pathlib import Path
import ict_feature_functions as ict_fct
import json 

# Base folder where EURUSD.csv, GBPUSD.csv ... are located
BASE_RAW_DIR = Path(r"C:\Users\bessa\Documents\forexdata\FX_Dukascopy_5y\FX_ICT_Enriched")

PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDCHF", "USDCAD", "USDJPY"]
#for third table define pairs with their pip size to compute in line 47
PIP_SIZE_BY_PAIR = {
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "AUDUSD": 0.0001,
    "USDCHF": 0.0001,
    "USDCAD": 0.0001,
    "USDJPY": 0.01,
}

def enrich_dataframe_for_pair(df: pd.DataFrame, pair: str) -> pd.DataFrame:
    """Run the full ICT enrichment pipeline on one DataFrame."""

    pip_size = PIP_SIZE_BY_PAIR[pair]

    # 1) UTC + base time features
    df = ict_fct.compute_utc_time_features(df) #hour and minute
    df = ict_fct.compute_day_of_week(df) #utc day of the week starting from monday 0 to friday 4
    df = ict_fct.compute_session(df) #sessions based on utc time
    df = ict_fct.compute_killzone(df)#killzones 

    #New York session / NY time features
    df = ict_fct.add_timestamp_ny(df) 
    df = ict_fct.compute_session_ny(df)
    df = ict_fct.compute_killzone_ny(df)
    df = ict_fct.add_ny_day_week_flags(df)
    df = ict_fct.compute_day_of_week_ny(df)

    # 2) HTF structure (60m lookbacks etc.)
    df = ict_fct.compute_high_lookback(df)
    df = ict_fct.compute_low_lookback(df)
    df = ict_fct.compute_price_above_HTF_mid(df)
    df = ict_fct.compute_sweep_HTF_high(df)
    df = ict_fct.compute_sweep_HTF_low(df)

    # 3) Liquidity & swings
    df = ict_fct.compute_swing_high(df)
    df = ict_fct.compute_swing_low(df)
    df = ict_fct.compute_equal_high_low(df, pip_size=pip_size)  # <<< pip_size per pair this is because of USDJPY which has 0.01 

    # 4) Displacement & volatility
    df = ict_fct.compute_displacement_up(df)
    df = ict_fct.compute_displacement_down(df)
    df = ict_fct.compute_range_size(df)
    df = ict_fct.compute_avg_range_20(df)
    df = ict_fct.compute_range_expansion(df)

    # 5) Previous day/week levels
    df = ict_fct.compute_prev_day_levels(df)
    df = ict_fct.compute_prev_week_levels(df)

    return df


def enrich_pair(pair: str):
    """Read <PAIR>.csv, enrich it, write FX_Dukascopy_5y_raw/<PAIR>/enriched.csv."""
    input_csv = BASE_RAW_DIR / f"{pair}.csv"
    if not input_csv.exists():
        print(f" Missing {input_csv}") # just in case pairs files are missing 
        return

    print(f"Processing {pair} from {input_csv}")
    df = pd.read_csv(input_csv)

    df_enriched = enrich_dataframe_for_pair(df, pair)

    # Output directory: FX_Dukascopy_5y_raw/<PAIR>/
    out_dir = BASE_RAW_DIR / pair 
    out_dir.mkdir(parents=True, exist_ok=True)  # make a dir for each pair as requested 

    out_path = out_dir / "enriched.csv"
    df_enriched.to_csv(out_path, index=False)
    print(f"   → Saved enriched data to {out_path}")
    #missing_bars.txt
    write_missing_bars_txt(df_enriched, out_dir / "missing_bars.txt")
    print(f"   → Saved enriched data and missing_bars.txt to {out_dir}")


    #gap summary
    write_gap_summary_txt(df_enriched, pair, out_dir / "gap_summary.txt")
    print(f"   → Saved gap_summary.txt to {out_dir}")

    #metadata.json
    write_metadata_json(df_enriched, pair, out_dir / "metadata.json")
    print(f"   → Saved metadata.json to {out_dir}")



# write missing_bars.txt
def write_missing_bars_txt(df: pd.DataFrame, out_path: Path):
    """
    Write timestamps where missing_bar == True to missing_bars.txt
    in ISO8601 UTC format.
    """
    if "missing_bar" not in df.columns:
        print("missing_bar column not found; skipping missing_bars.txt")
        return # just in case you have new data and you did not do as project one by cleaning the missing bars
    
    ts = pd.to_datetime(df["timestamp"], utc=True)
    missing_ts = ts[df["missing_bar"] == True]

    (
        pd.Series(missing_ts)
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        .to_csv(out_path, index=False, header=False)
    )

# gap summary  gap_summary.txt
def write_gap_summary_txt(df: pd.DataFrame, pair: str, out_path: Path):
    """
    gap_summary.txt using full data (already no weekends in our data removed from project one):
      - coverage (earliest / latest UTC timestamp)
      - total 1m bars
      - real vs filled bars via missing_bar
    """
    ts = pd.to_datetime(df["timestamp"], utc=True)
    start = ts.min()
    end = ts.max()

    total_rows = len(df)
    if "missing_bar" in df.columns:
        filled_bars = int(df["missing_bar"].sum())
        real_bars = int(total_rows - filled_bars)
    else:
        filled_bars = 0
        real_bars = total_rows

    lines = []
    lines.append(f"{pair} 1-minute Dukascopy (UTC)\n\n")
    lines.append("Coverage:\n")
    lines.append(f"- From: {start.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
    lines.append(f"- To  : {end.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n")

    lines.append("Counts:\n")
    lines.append(f"- Total rows in file: {total_rows}\n")
    lines.append(f"- Real bars: {real_bars}\n")
    lines.append(f"- Filled bars (missing_bar == True): {filled_bars}\n\n")

    lines.append("Notes:\n")
    lines.append("- Weekends already excluded from this dataset.\n")
    lines.append("- Missing weekday minutes forward-filled and flagged via missing_bar.\n")

    out_path.write_text("".join(lines), encoding="utf-8")




def write_metadata_json(df: pd.DataFrame, pair: str, out_path: Path):
    """
    metadata.json, same schema as project 1, but taken from the enriched DataFrame.
    """
    ts = pd.to_datetime(df["timestamp"], utc=True)
    start = ts.min()
    end = ts.max()
    total_rows = len(df)
    missing_bars = int(df["missing_bar"].sum()) if "missing_bar" in df.columns else 0

    meta = {
        "pair": pair,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": end.isoformat().replace("+00:00", "Z"),
        "total_rows": total_rows,
        "missing_bars": missing_bars,
        "source": "Dukascopy",
        "note": (
            "Rolling 5-year weekday-only data (Sat/Sun excluded); "
            "missing weekday minutes forward-filled and flagged via missing_bar."
        ),
    }

    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")





def main():
    for pair in PAIRS:
        enrich_pair(pair)

if __name__ == "__main__":
    main()