import pandas as pd
from src.forecast import build_forecast

CLASSES = ["bullish", "neutral", "bearish"]


def run_backtest(df: pd.DataFrame, min_history: int = 60) -> tuple[pd.DataFrame, dict]:
    rows = []
    for i in range(min_history, len(df) - 1):
        hist = df.iloc[: i + 1].copy()
        fc = build_forecast(hist)
        if fc["signal"] == "insufficient_data":
            continue
        next_row = df.iloc[i + 1]
        current_close = float(hist["Close"].iloc[-1])
        actual_close = float(next_row["Close"])
        actual_return = (actual_close / current_close) - 1
        predicted_return = (fc["predicted_close"] / current_close) - 1
        actual_dir = "bullish" if actual_return > 0.002 else "bearish" if actual_return < -0.002 else "neutral"
        rows.append(
            {
                "date": next_row["Date"],
                "signal": fc["signal"],
                "bullish_prob": fc["bullish_prob"],
                "neutral_prob": fc["neutral_prob"],
                "bearish_prob": fc["bearish_prob"],
                "predicted_close": fc["predicted_close"],
                "actual_close": actual_close,
                "predicted_return": predicted_return,
                "actual_return": actual_return,
                "predicted_range_low": fc["predicted_range"][0],
                "predicted_range_high": fc["predicted_range"][1],
                "actual_direction": actual_dir,
                "correct_direction": fc["signal"] == actual_dir,
                "range_hit": fc["predicted_range"][0] <= actual_close <= fc["predicted_range"][1],
                "abs_error": abs(fc["predicted_close"] - actual_close),
                "ape": abs(fc["predicted_close"] - actual_close) / actual_close if actual_close else 0,
            }
        )

    bt = pd.DataFrame(rows)
    if bt.empty:
        return bt, {}

    bt["equity_curve"] = (1 + bt.apply(_strategy_return, axis=1)).cumprod()
    cm = confusion_matrix_table(bt)
    baselines = compute_baselines(bt)
    class_report = classification_report_from_cm(cm)
    metrics = {
        "samples": int(len(bt)),
        "directional_accuracy": round(bt["correct_direction"].mean() * 100, 2),
        "range_hit_rate": round(bt["range_hit"].mean() * 100, 2),
        "mae": round(bt["abs_error"].mean(), 4),
        "mape": round(bt["ape"].mean() * 100, 2),
        "strategy_return": round((bt["equity_curve"].iloc[-1] - 1) * 100, 2),
        "bias": round(bt["predicted_close"].sub(bt["actual_close"]).mean(), 4),
        "confusion_matrix": cm,
        "baselines": baselines,
        "class_report": class_report,
    }
    return bt, metrics


def _strategy_return(row) -> float:
    if row["signal"] == "bullish":
        return row["actual_return"]
    if row["signal"] == "bearish":
        return -row["actual_return"]
    return 0.0


def confusion_matrix_table(bt: pd.DataFrame) -> pd.DataFrame:
    matrix = pd.DataFrame(0, index=CLASSES, columns=CLASSES)
    for _, row in bt.iterrows():
        matrix.loc[row["actual_direction"], row["signal"]] += 1
    matrix.index.name = "Actual"
    return matrix


def compute_baselines(bt: pd.DataFrame) -> dict:
    total = len(bt)
    actual = bt["actual_direction"]
    majority_class = actual.value_counts().idxmax()
    always_bull_acc = round((actual == "bullish").mean() * 100, 2)
    always_neutral_acc = round((actual == "neutral").mean() * 100, 2)
    always_bear_acc = round((actual == "bearish").mean() * 100, 2)
    majority_acc = round(actual.value_counts().max() / total * 100, 2)
    no_change_acc = always_neutral_acc
    return {
        "majority_class": majority_class,
        "majority_class_accuracy": majority_acc,
        "always_bullish_accuracy": always_bull_acc,
        "always_neutral_accuracy": always_neutral_acc,
        "always_bearish_accuracy": always_bear_acc,
        "no_change_accuracy": no_change_acc,
    }


def classification_report_from_cm(cm: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cls in CLASSES:
        tp = float(cm.loc[cls, cls])
        fp = float(cm[cls].sum() - tp)
        fn = float(cm.loc[cls].sum() - tp)
        support = float(cm.loc[cls].sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        rows.append(
            {
                "class": cls,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "support": int(support),
            }
        )
    return pd.DataFrame(rows)
