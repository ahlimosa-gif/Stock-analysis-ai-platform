import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_price_data
from src.indicators import add_moving_averages, add_rsi
from src.signals import detect_levels, detect_breakouts
from src.backtest import run_backtest

st.set_page_config(page_title="Backtest / Accuracy", layout="wide")
st.title("Stock Analysis AI Platform — Backtest / Accuracy")
st.caption("Validate next-day forecast quality on historical data with rolling one-step-ahead evaluation.")

with st.sidebar:
    st.header("Backtest Input")
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Period", ["6mo", "1y", "2y"], index=2)
    interval = st.selectbox("Interval", ["1d"], index=0)
    swing_window = st.slider("Swing window", min_value=2, max_value=10, value=5)
    volume_multiplier = st.slider("Volume confirmation x avg", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
    min_history = st.slider("Minimum history bars", min_value=40, max_value=120, value=60, step=5)

@st.cache_data(ttl=900)
def get_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = load_price_data(ticker=ticker, period=period, interval=interval)
    if df.empty:
        return df
    if "Datetime" in df.columns and "Date" not in df.columns:
        df = df.rename(columns={"Datetime": "Date"})
    df = add_moving_averages(df, windows=(20, 50))
    df = add_rsi(df, period=14)
    levels = detect_levels(df, window=swing_window)
    last_support = levels["supports"][-1] if levels["supports"] else None
    last_resistance = levels["resistances"][-1] if levels["resistances"] else None
    df = detect_breakouts(df, resistance=last_resistance, support=last_support, volume_multiplier=volume_multiplier)
    return df

if not ticker:
    st.warning("Please enter a ticker symbol.")
    st.stop()

df = get_data(ticker, period, interval)
if df.empty:
    st.error("No data returned. Check the ticker or try another period.")
    st.stop()

bt, metrics = run_backtest(df, min_history=min_history)
if bt.empty:
    st.error("Not enough data to run the backtest.")
    st.stop()

baselines = metrics["baselines"]

c1, c2, c3 = st.columns(3)
c1.metric("Directional Accuracy", f"{metrics['directional_accuracy']}%")
c2.metric("Range Hit Rate", f"{metrics['range_hit_rate']}%")
c3.metric("Strategy Return", f"{metrics['strategy_return']}%")

c4, c5, c6 = st.columns(3)
c4.metric("Samples", str(metrics["samples"]))
c5.metric("MAE", f"{metrics['mae']:.2f}")
c6.metric("MAPE", f"{metrics['mape']}%")

st.subheader("Benchmarks")
b1, b2, b3 = st.columns(3)
b1.metric("Majority-Class Baseline", f"{baselines['majority_class_accuracy']}%", f"Class: {baselines['majority_class']}")
b2.metric("Always Bullish", f"{baselines['always_bullish_accuracy']}%")
b3.metric("No-Change / Neutral", f"{baselines['no_change_accuracy']}%")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=bt["date"], y=bt["equity_curve"], mode="lines", name="Equity Curve", line=dict(color="#26a69a")))
fig1.update_layout(template="plotly_dark", height=360, margin=dict(l=20, r=20, t=40, b=20), title="Forecast Strategy Equity Curve")
st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=bt["date"], y=bt["predicted_close"], mode="lines", name="Predicted Close", line=dict(color="#42a5f5")))
fig2.add_trace(go.Scatter(x=bt["date"], y=bt["actual_close"], mode="lines", name="Actual Close", line=dict(color="#ef5350")))
fig2.update_layout(template="plotly_dark", height=420, margin=dict(l=20, r=20, t=40, b=20), title="Predicted vs Actual Next-Day Close")
st.plotly_chart(fig2, use_container_width=True)

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Confusion Matrix")
    st.dataframe(metrics["confusion_matrix"], use_container_width=True)
    st.subheader("Precision / Recall / F1 by Class")
    st.dataframe(metrics["class_report"], use_container_width=True, hide_index=True)
    st.subheader("Recent Backtest Rows")
    cols = ["date", "signal", "actual_direction", "bullish_prob", "neutral_prob", "bearish_prob", "predicted_close", "actual_close", "correct_direction", "range_hit", "abs_error"]
    st.dataframe(bt[cols].tail(30), use_container_width=True, hide_index=True)

with right:
    st.subheader("Validation Notes")
    st.write("- The confusion matrix compares actual next-day direction against the forecast direction; diagonal cells are correct calls.")
    st.write("- Precision shows how often a predicted class was correct, recall shows how much of the actual class was captured, and F1 balances both. Per-class metrics are computed one-vs-rest for bullish, neutral, and bearish labels.")
    st.write("- Majority-class baseline shows the accuracy you would get by always predicting the most common realized class.")
    st.write("- Always-bullish and no-change baselines help check whether the forecast beats simple naive rules.")
    st.write("- If the model does not beat naive baselines consistently, the signal likely needs better features or calibration.")
