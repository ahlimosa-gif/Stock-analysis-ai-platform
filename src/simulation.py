import pandas as pd
import numpy as np


def intraday_paths(last_close: float) -> pd.DataFrame:
    times = ["09:30", "10:30", "11:30", "13:00", "14:30", "16:00"]
    bull = np.array([1.00, 1.01, 1.015, 1.018, 1.022, 1.025]) * last_close
    base = np.array([1.00, 1.004, 1.002, 1.006, 1.008, 1.01]) * last_close
    bear = np.array([1.00, 0.992, 0.989, 0.993, 0.995, 0.997]) * last_close
    return pd.DataFrame({"time": times, "bull": bull, "base": base, "bear": bear})
