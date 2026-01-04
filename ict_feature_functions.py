import pandas as pd
import numpy as np


# creating column hour and min 
def compute_utc_time_features(df,timestamp_col="timestamp"):
    ts=pd.to_datetime(df[timestamp_col],utc=True)
    df['hour']=ts.dt.hour.astype('int')
    df['minute']=ts.dt.minute.astype('int')
    return df


# day_of_week (0=Mon … 5=friday), per trading setup
def compute_day_of_week(df, timestamp_col="timestamp"):
    # UTC day_of_week (PDF spec)
    ts = pd.to_datetime(df[timestamp_col], utc=True)
    df["day_of_week"] = ts.dt.dayofweek.astype(int)
    return df


def compute_session(df, hour_col="hour"):
    """
    session (UTC), from canonical brief:
      - Asia:   00:00–07:59
      - London: 08:00–12:59
      - New York: 13:00–16:59
      - Afterhours: otherwise
    Requires df[hour] already computed from UTC timestamp.
    """
    h = df[hour_col]

    conditions = [
        (h >= 0) & (h <= 7),    # Asia include everything up to 07:59
        (h >= 8) & (h <= 12),   # London include everything up to 12:59
        (h >= 13) & (h <= 16),  # New York include everything up to 16:59
    ]
    choices = ["Asia", "London", "NewYork"]

    df["session"] = np.select(conditions, choices, default="Afterhours")
    return df


def compute_killzone(df, hour_col="hour", minute_col="minute"):
    """
    Canonical killzone column (UTC):
    mark true when:
      - London Killzone: 07:00 up to and including 10:00
      - New York Killzone: 12:00 up to and including 14:00
    None: otherwise
    """
    h = df[hour_col]
    m = df[minute_col]
    kz = np.full(len(df), None, dtype=object)

    # London: 07:00–10:00 inclusive
    london_mask = (
        (h == 7) |                      # all 07:xx
        ((h >= 8) & (h <= 9)) |         # all 08:xx and 09:xx
        ((h == 10) & (m == 0))          # exactly 10:00
    )
    kz[london_mask] = "London_KZ"

    # New York: 12:00–14:00 inclusive
    ny_mask = (
        (h == 12) |                     # all 12:xx
        (h == 13)  |                    # all 13:xx
        ((h == 14) & (m == 0))          # exactly 14:00
    )
    kz[ny_mask] = "NewYork_KZ"

    df["killzone"] = kz
    return df


def add_timestamp_ny(df, timestamp_col="timestamp"):
    """
    Add New York time columns from a UTC ISO8601 timestamp string.
    Creates: timestamp_ny (datetime64[ns, America/New_York]),
             hour_ny, minute_ny.
    """
    ts_utc = pd.to_datetime(df[timestamp_col], utc=True)
    ts_ny = ts_utc.dt.tz_convert("America/New_York")
    df["timestamp_ny"] = ts_ny
    df["hour_ny"] = ts_ny.dt.hour
    df["minute_ny"] = ts_ny.dt.minute
    return df


def compute_session_ny(df, hour_col="hour_ny"):
    """
    NY sessions (chart setup):
      - Tokyo:  19:00–00:00
      - London: 02:00–05:00
      - NY:     07:00–10:00
      - Off:    otherwise
    """
    h = df[hour_col]

    # Treat 00:00 as still Tokyo; 00:01+ is Off unless in another session
    tokyo = ((h >= 19) | (h == 0))
    london = (h >= 2) & (h <= 5)
    ny     = (h >= 7) & (h <= 10)

    df["session_ny"] = np.where(tokyo, "Tokyo",
                         np.where(london, "London",
                         np.where(ny, "NewYork", "Off")))
    return df


def compute_killzone_ny(df, hour_col="hour_ny"):
    """
    Kill zone reversal times in NY:
      - London KZ: 03:00–03:59
      - NY KZ:     08:00–08:59
      - None:      otherwise
    """
    h = df[hour_col]
    kz = np.full(len(df), None, dtype=object)
    kz[(h == 3)] = "London_KZ"
    kz[(h == 8)] = "NY_KZ"
    df["killzone_ny"] = kz
    return df


def add_ny_day_week_flags(df):
    """
    NY-based day/week markers:
      - is_ny_day_open: each day 17:00 NY
      - is_sunday_open_ny: Sunday 17:00 NY (extended to Friday in their logic)
      - is_ny_midnight: each day 00:00 NY
    Requires timestamp_ny already present.
    """
    ts_ny = df["timestamp_ny"]

    df["is_ny_day_open"] = (
        (ts_ny.dt.hour == 17) & (ts_ny.dt.minute == 0)
    )
    
    df["is_sunday_open_ny"] = (
        (ts_ny.dt.weekday == 6) &    # Sunday
        (ts_ny.dt.hour == 17) &
        (ts_ny.dt.minute == 0)
    )

    df["is_ny_midnight"] = (
        (ts_ny.dt.hour == 0) & (ts_ny.dt.minute == 0)
    )

    return df

def compute_day_of_week_ny(df):
    # NY local day_of_week 
    ts_ny = df["timestamp_ny"]
    df["day_of_week_ny"] = ts_ny.dt.dayofweek.astype(int)
    return df




#second table
#HTF_high_lookback float Highest high over past 60 mins
def compute_high_lookback(df,high_col="high"):

    df['HTF_high_lookback']=df[high_col].rolling(window=60).max().shift(1)
    return df
 
def compute_low_lookback(df,low_col="low"):
    df['HTF_low_lookback']=df[low_col].rolling(window=60).min().shift(1)
    return df

#price_above_HTF_mid bool Close > midpoint of HTF range
def compute_price_above_HTF_mid(df,close_col="close"):
    df['HTF_midpoint']=(df['HTF_high_lookback']+df['HTF_low_lookback'])/2
    df['price_above_HTF_mid']=df[close_col]>df['HTF_midpoint']
    return df


#sweep_HTF_high bool Current high exceeds HTF_high_lookback, then closes back inside
def compute_sweep_HTF_high(df,high_col="high",close_col="close"):
    df['sweep_HTF_high']=(df[high_col]>df['HTF_high_lookback']) & (df[close_col]<df['HTF_high_lookback'])
    return df

#sweep_HTF_low bool Current low dips below HTF_low_lookback, then closes back inside
def compute_sweep_HTF_low(df,low_col="low",close_col="close"):
    df['sweep_HTF_low']=(df[low_col]<df['HTF_low_lookback']) & (df[close_col]>df['HTF_low_lookback'])
    return df   




#third table
#Swing High / Low Detection table


def compute_swing_high(df,high_col="high"):
    #true when the current high is greater then the previous of the past and the next 3 rows
    #past 3
    past3_max=df[high_col].shift(1).rolling(3,min_periods=3).max()
    #next 3
    future3_max=df[high_col].shift(-3).rolling(3,min_periods=3).max()
    df["swing_high"] = (df[high_col] > past3_max) & (df[high_col] > future3_max)
    return df


def compute_swing_low(df,low_col="low"):
    #true when the current low is less then the previous of the past and the next 3 rows
    #past 3
    past3_min=df[low_col].shift(1).rolling(3,min_periods=3).min()
    #next 3
    future3_min=df[low_col].shift(-3).rolling(3,min_periods=3).min()
    df["swing_low"] = (df[low_col] < past3_min) & (df[low_col] < future3_min)
    return df



def compute_equal_high_low(df, high_col="high", low_col="low", swing_high_col="swing_high",
                           swing_low_col="swing_low", pip_size=0.0001, tolerance_pips=2):#default pip size 
    
    tol = tolerance_pips * pip_size
    prev_swing_high = df[high_col].where(df[swing_high_col]).shift().ffill()
    prev_swing_low  = df[low_col].where(df[swing_low_col]).shift().ffill()
    df["equal_high"] = (
        df[swing_high_col]
        & prev_swing_high.notna()
        & (np.abs(df[high_col] - prev_swing_high) <= tol)
    )
    df["equal_low"] = (
        df[swing_low_col]
        & prev_swing_low.notna()
        & (np.abs(df[low_col] - prev_swing_low) <= tol)
    )
    return df




#fourth table
# Displacement & Volatility Features 
def compute_displacement_up(df, open_col="open", close_col="close", high_col="high"):
    # body_size and its prior-20 average
    body_size = (df[close_col] - df[open_col]).abs()
    avg_body_size_20 = body_size.shift(1).rolling(20, min_periods=20).mean()
    prev_high = df[high_col].shift(1)
    df["displacement_up"] = (
        (df[close_col] > prev_high) &
        avg_body_size_20.notna() &
        (body_size > avg_body_size_20)
    )
    return df

def compute_displacement_down(df, open_col="open", close_col="close", low_col="low"):
    body_size = (df[close_col] - df[open_col]).abs()
    avg_body_size_20 = body_size.shift(1).rolling(20, min_periods=20).mean()
    prev_low = df[low_col].shift(1)
    df["displacement_down"] = (
        (df[close_col] < prev_low) &
        avg_body_size_20.notna() &
        (body_size > avg_body_size_20)
    )
    return df

def compute_range_size(df, high_col="high", low_col="low"):
    df["range_size"] = df[high_col] - df[low_col]
    return df


def compute_avg_range_20(df):
    # uses prior bars only to avoid leakage
    df["avg_range_20"] = df["range_size"].shift(1).rolling(20, min_periods=20).mean()
    return df


def compute_range_expansion(df, factor=1.5):
    """
    range_expansion: True when range_size > factor × avg_range_20.
    Requires compute_range_size and compute_avg_range_20 run beforehand.
    """
    df["range_expansion"] = (
        df["avg_range_20"].notna() & (df["range_size"] > (factor * df["avg_range_20"]))
    )
    return df




#fifth table
def compute_prev_day_levels(df, timestamp_col="timestamp",
                            high_col="high", low_col="low"):
    """
    Adds:
      - prev_day_high: daily high of the prior UTC calendar day
      - prev_day_low:  daily low of the prior UTC calendar day
    """
    ts = pd.to_datetime(df[timestamp_col], utc=True)          # ensure timezone-aware UTC
    day = ts.dt.floor("D")                                    # normalize to UTC day (yyyy-mm-dd 00:00)

    # daily high/low for each UTC day
    daily = df.groupby(day).agg(
        day_high=(high_col, "max"),
        day_low=(low_col, "min"),
    )                                                      

    # previous day’s high/low (no future leakage)
    daily["prev_day_high"] = daily["day_high"].shift(1)
    daily["prev_day_low"]  = daily["day_low"].shift(1)     

    # map back so every row on day D sees day D-1’s values
    df["prev_day_high"] = day.map(daily["prev_day_high"])
    df["prev_day_low"]  = day.map(daily["prev_day_low"])

    return df

def compute_prev_week_levels(df, timestamp_col="timestamp",
                             high_col="high", low_col="low"):
    """
    Adds:
      - prev_week_high: high of the prior ISO week (Mon–Sun)
      - prev_week_low:  low  of the prior ISO week (Mon–Sun)
    """
    ts = pd.to_datetime(df[timestamp_col], utc=True)
    iso = ts.dt.isocalendar()                                 # columns: year, week, day

    week_key = pd.MultiIndex.from_arrays(
        [iso["year"], iso["week"]],
        names=["year", "week"],
    )

    # weekly high/low per ISO week
    weekly = df.groupby(week_key).agg(
        week_high=(high_col, "max"),
        week_low=(low_col, "min"),
    )                                                       

    # previous week’s high/low (shift by one ISO week)
    weekly["prev_week_high"] = weekly["week_high"].shift(1)
    weekly["prev_week_low"]  = weekly["week_low"].shift(1)  

    # map back by (year, week) so each row sees prior week’s range
    df["prev_week_high"] = week_key.map(weekly["prev_week_high"])
    df["prev_week_low"]  = week_key.map(weekly["prev_week_low"])

    return df
