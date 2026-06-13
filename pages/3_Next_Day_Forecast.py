import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_loader import load_price_data
from src.indicators import add_moving_averages, add_rsi
from src.signals import detect_levels, detect_breakouts
from src.forecast import build_forecast, build_intraday_scenarios

st.set_page_config(page_title="Next-Day Forecast", layout="wide")
st.title("Stock Analysis AI Platform — Next-Day Forecast")
st.caption("Estimate next-day direction, expected close, projected range, and scenario paths from technical structure.")

with st.sidebar:
    st.header("Forecast Input")
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y"], index=1)
    interval = st.selectbox("Interval", ["1d"], index=0)
    swing_window = st.slider("Swing window", min_value=2, max_value=10, value=5)
    volume_multiplier = st.slider("Volume confirmation x avg", min_value=1.0, max_value=3.0, value=1.5, step=0.1)

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

forecast = build_forecast(df)
if forecast["signal"] == "insufficient_data":
    st.error("Not enough data to generate a next-day forecast.")
    st.stop()

latest_close = float(df["Close"].iloc[-1])
scenarios = build_intraday_scenarios(latest_close, forecast["predicted_close"], forecast["predicted_range"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bullish %", f"{forecast['bullish_prob']}%")
c2.metric("Neutral %", f"{forecast['neutral_prob']}%")
c3.metric("Bearish %", f"{forecast['bearish_prob']}%")
c4.metric("Predicted Close", f"{forecast['predicted_close']:.2f}", f"Signal: {forecast['signal']}")

st.markdown(f"**Predicted Range:** {forecast['predicted_range'][0]:.2f} - {forecast['predicted_range'][1]:.2f}")

fig = go.Figure()
recent = df.tail(30)
fig.add_trace(go.Scatter(x=recent["Date"], y=recent["Close"], mode="lines", name="Recent Close"))
future_x = [f"Next {t}" for t in scenarios["time"]]
fig.add_trace(go.Scatter(x=future_x, y=scenarios["base"], mode="lines+markers", name="Base Case", line=dict(color="#42a5f5", dash="dash")))
fig.add_trace(go.Scatter(x=future_x, y=scenarios["bull"], mode="lines+markers", name="Bull Case", line=dict(color="#26a69a", dash="dot")))
fig.add_trace(go.Scatter(x=future_x, y=scenarios["bear"], mode="lines+markers", name="Bear Case", line=dict(color="#ef5350", dash="dot")))
fig.update_layout(template="plotly_dark", height=600, margin=dict(l=20, r=20, t=40, b=20), title="Recent Price + Next-Day Scenario Paths")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Forecast Drivers")
    for d in forecast["drivers"]:
        st.write(f"- {d}")
    st.subheader("Scenario Table")
    st.dataframe(scenarios, use_container_width=True, hide_index=True)

with right:
    st.subheader("Interpretation")
    if forecast["signal"] == "bullish":
        st.success("Bias is bullish for the next trading day.")
    elif forecast["signal"] == "bearish":
        st.error("Bias is bearish for the next trading day.")
    else:
        st.info("Bias is neutral / range-bound for the next trading day.")
    st.write("- The forecast combines moving-average structure, RSI state, breakout/breakdown events, recent momentum, and volume context.")
    st.write("- The base case is a central path, while bull and bear cases frame a scenario range rather than a guaranteed path.")
    st.write("- Treat this page as a decision-support tool, not a certainty engine.")
