import pandas as pd


def add_moving_averages(df: pd.DataFrame, windows=(20, 50)) -> pd.DataFrame:
    out = df.copy()
    for w in windows:
        out[f"MA{w}"] = out["Close"].rolling(w).mean()
    return out


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    out = df.copy()
    delta = out["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    out["RSI"] = 100 - (100 / (1 + rs))
    return out
