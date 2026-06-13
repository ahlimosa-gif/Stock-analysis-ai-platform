import pandas as pd


def detect_levels(df: pd.DataFrame, window: int = 5) -> dict:
    if df.empty or len(df) < window * 2 + 1:
        return {"supports": [], "resistances": []}

    supports, resistances = [], []
    lows = df["Low"].reset_index(drop=True)
    highs = df["High"].reset_index(drop=True)

    for i in range(window, len(df) - window):
        low_slice = lows.iloc[i - window:i + window + 1]
        high_slice = highs.iloc[i - window:i + window + 1]
        if lows.iloc[i] == low_slice.min():
            supports.append(float(lows.iloc[i]))
        if highs.iloc[i] == high_slice.max():
            resistances.append(float(highs.iloc[i]))

    supports = _dedupe_nearby(sorted(supports))
    resistances = _dedupe_nearby(sorted(resistances))
    return {"supports": supports[-3:], "resistances": resistances[-3:]}


def _dedupe_nearby(levels, threshold: float = 0.008):
    if not levels:
        return []
    cleaned = [levels[0]]
    for level in levels[1:]:
        if abs(level - cleaned[-1]) / cleaned[-1] > threshold:
            cleaned.append(level)
    return cleaned


def detect_breakouts(
    df: pd.DataFrame,
    resistance: float | None,
    support: float | None,
    volume_multiplier: float = 1.5,
    volume_window: int = 20,
) -> pd.DataFrame:
    out = df.copy()
    out["avg_volume"] = out["Volume"].rolling(volume_window).mean() if "Volume" in out.columns else None
    out["volume_confirmed"] = False
    out["bull_breakout"] = False
    out["bear_breakdown"] = False

    if resistance is not None:
        crossed_up = (out["Close"] > resistance) & (out["Close"].shift(1) <= resistance)
        out.loc[crossed_up, "bull_breakout"] = True

    if support is not None:
        crossed_down = (out["Close"] < support) & (out["Close"].shift(1) >= support)
        out.loc[crossed_down, "bear_breakdown"] = True

    if "Volume" in out.columns:
        out["volume_confirmed"] = out["Volume"] >= (out["avg_volume"] * volume_multiplier)
        out["bull_breakout"] = out["bull_breakout"] & out["volume_confirmed"]
        out["bear_breakdown"] = out["bear_breakdown"] & out["volume_confirmed"]

    return out
