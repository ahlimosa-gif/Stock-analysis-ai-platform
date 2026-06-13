import pandas as pd


def build_forecast(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 60:
        return {
            "bullish_prob": None,
            "neutral_prob": None,
            "bearish_prob": None,
            "predicted_close": None,
            "predicted_range": None,
            "signal": "insufficient_data",
            "drivers": [],
        }

    latest = df.iloc[-1]
    score = 0.0
    drivers = []

    close = float(latest["Close"])
    ma20 = float(latest["MA20"]) if pd.notna(latest.get("MA20")) else close
    ma50 = float(latest["MA50"]) if pd.notna(latest.get("MA50")) else close
    rsi = float(latest["RSI"]) if pd.notna(latest.get("RSI")) else 50.0

    if close > ma20:
        score += 1.0
        drivers.append("Close above MA20")
    else:
        score -= 1.0
        drivers.append("Close below MA20")

    if ma20 > ma50:
        score += 1.0
        drivers.append("MA20 above MA50")
    else:
        score -= 1.0
        drivers.append("MA20 below MA50")

    if 50 <= rsi <= 65:
        score += 0.7
        drivers.append("RSI in constructive zone")
    elif 65 < rsi < 75:
        score += 0.2
        drivers.append("RSI strong but nearing overbought")
    elif 35 <= rsi < 50:
        score -= 0.2
        drivers.append("RSI below momentum midpoint")
    elif rsi < 35:
        score -= 0.8
        drivers.append("RSI weak / oversold")
    else:
        score -= 0.6
        drivers.append("RSI overbought risk")

    if bool(latest.get("bull_breakout", False)):
        score += 1.2
        drivers.append("Volume-confirmed bull breakout")
    if bool(latest.get("bear_breakdown", False)):
        score -= 1.2
        drivers.append("Volume-confirmed bear breakdown")

    avg_volume = latest.get("avg_volume")
    if pd.notna(avg_volume) and avg_volume and "Volume" in df.columns:
        vol_ratio = float(latest["Volume"]) / float(avg_volume)
        if vol_ratio >= 1.5:
            score += 0.3 if close >= ma20 else -0.3
            drivers.append(f"Volume ratio {vol_ratio:.2f}x average")

    recent_returns = df["Close"].pct_change().tail(10).dropna()
    momentum = recent_returns.mean() if not recent_returns.empty else 0
    vol = recent_returns.std() if not recent_returns.empty else 0.015
    score += max(min(momentum * 100, 0.8), -0.8)
    drivers.append(f"10-bar momentum {momentum*100:.2f}%")

    bullish_prob = max(5, min(85, 50 + score * 10))
    bearish_prob = max(5, min(85, 50 - score * 10))
    neutral_prob = max(10, 100 - bullish_prob - bearish_prob)

    total = bullish_prob + bearish_prob + neutral_prob
    bullish_prob = round(bullish_prob / total * 100, 1)
    bearish_prob = round(bearish_prob / total * 100, 1)
    neutral_prob = round(neutral_prob / total * 100, 1)

    exp_move = momentum + (score / 100)
    predicted_close = round(close * (1 + exp_move), 2)
    range_width = max(vol * 1.5, 0.01)
    predicted_range = (
        round(predicted_close * (1 - range_width), 2),
        round(predicted_close * (1 + range_width), 2),
    )

    signal = "bullish" if bullish_prob > bearish_prob and bullish_prob >= 45 else "bearish" if bearish_prob > bullish_prob and bearish_prob >= 45 else "neutral"

    return {
        "bullish_prob": bullish_prob,
        "neutral_prob": neutral_prob,
        "bearish_prob": bearish_prob,
        "predicted_close": predicted_close,
        "predicted_range": predicted_range,
        "signal": signal,
        "drivers": drivers,
    }


def build_intraday_scenarios(last_close: float, predicted_close: float, predicted_range: tuple[float, float]) -> pd.DataFrame:
    times = ["09:30", "10:30", "11:30", "13:00", "14:30", "16:00"]
    low, high = predicted_range
    base = [last_close, (last_close + predicted_close) / 2, predicted_close * 0.995, predicted_close * 1.002, predicted_close * 0.998, predicted_close]
    bull = [last_close, last_close * 1.006, high * 0.992, high * 1.0, high * 1.004, high]
    bear = [last_close, last_close * 0.994, low * 1.01, low * 1.004, low * 0.998, low]
    return pd.DataFrame({"time": times, "bull": bull, "base": base, "bear": bear})
