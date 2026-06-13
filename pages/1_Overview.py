import streamlit as st
import pandas as pd
from src.data_loader import load_price_data
from src.indicators import add_moving_averages, add_rsi
from src.signals import detect_levels, detect_breakouts
from src.charts import line_price_chart, candlestick_volume_chart

st.set_page_config(page_title="Overview", layout="wide")
st.title("Stock Analysis AI Platform — Overview")
st.caption("Input a ticker to load recent price data, key metrics, support/resistance, and volume-confirmed breakout signals.")

with st.sidebar:
    st.header("Market Input")
    ticker = st.text_input("Ticker", value="AAPL").upper().strip()
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    interval = st.selectbox("Interval", ["1d", "1h"], index=0)
    chart_type = st.radio("Chart Type", ["Line", "Candlestick + Volume"], index=1)
    show_rsi_panel = st.toggle("Show RSI panel", value=True)
    show_rsi_state = st.toggle("Show RSI state text", value=True)
    show_levels = st.toggle("Show support/resistance", value=True)
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
    return df

if not ticker:
    st.warning("Please enter a ticker symbol.")
    st.stop()

df = get_data(ticker, period, interval)

if df.empty:
    st.error("No data returned. Check the ticker or try another period/interval.")
    st.stop()

levels = detect_levels(df, window=swing_window) if show_levels else {"supports": [], "resistances": []}
last_support = levels["supports"][-1] if levels["supports"] else None
last_resistance = levels["resistances"][-1] if levels["resistances"] else None
df = detect_breakouts(df, resistance=last_resistance, support=last_support, volume_multiplier=volume_multiplier)

latest = df.iloc[-1]
prev_close = df["Close"].iloc[-2] if len(df) > 1 else latest["Close"]
change = latest["Close"] - prev_close
change_pct = (change / prev_close * 100) if prev_close else 0
high_20 = df["High"].tail(20).max() if "High" in df.columns else None
low_20 = df["Low"].tail(20).min() if "Low" in df.columns else None
avg_vol_20 = df["Volume"].tail(20).mean() if "Volume" in df.columns else None

c1, c2, c3, c4 = st.columns(4)
c1.metric("Last Close", f"{latest['Close']:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
c2.metric("MA20", f"{latest['MA20']:.2f}" if pd.notna(latest['MA20']) else "N/A")
c3.metric("MA50", f"{latest['MA50']:.2f}" if pd.notna(latest['MA50']) else "N/A")
c4.metric("RSI(14)", f"{latest['RSI']:.2f}" if pd.notna(latest['RSI']) else "N/A")

if chart_type == "Candlestick + Volume":
    fig = candlestick_volume_chart(df, show_rsi=show_rsi_panel, levels=levels)
else:
    fig = line_price_chart(df, show_rsi=show_rsi_panel, levels=levels)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Recent Data")
    display_cols = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume", "avg_volume", "volume_confirmed", "MA20", "MA50", "RSI", "bull_breakout", "bear_breakdown"] if c in df.columns]
    st.dataframe(df[display_cols].tail(20), use_container_width=True, hide_index=True)

with right:
    st.subheader("Quick Read")
    bias = "Bullish" if pd.notna(latest["MA20"]) and latest["Close"] >= latest["MA20"] else "Bearish"
    st.write(f"- Current bias: **{bias}**")
    st.write(f"- Latest support: **{last_support:.2f}**" if last_support is not None else "- Latest support: N/A")
    st.write(f"- Latest resistance: **{last_resistance:.2f}**" if last_resistance is not None else "- Latest resistance: N/A")
    st.write(f"- 20-period high: **{high_20:.2f}**" if high_20 is not None else "- 20-period high: N/A")
    st.write(f"- 20-period low: **{low_20:.2f}**" if low_20 is not None else "- 20-period low: N/A")
    st.write(f"- 20-period avg volume: **{avg_vol_20:,.0f}**" if avg_vol_20 is not None else "- 20-period avg volume: N/A")
    if pd.notna(latest.get("avg_volume", None)):
        st.write(f"- Volume confirmation threshold: **{volume_multiplier:.1f}x** average volume")
    if latest.get("bull_breakout", False):
        st.success("First bull breakout confirmed by volume.")
    elif latest.get("bear_breakdown", False):
        st.error("First bear breakdown confirmed by volume.")
    elif latest.get("volume_confirmed", False):
        st.info("Volume is elevated, but no first breakout/breakdown signal on the latest bar.")
    else:
        st.info("No volume-confirmed breakout/breakdown on the latest bar.")
    if show_rsi_state:
        if pd.notna(latest["RSI"]):
            if latest["RSI"] >= 70:
                st.write("- RSI state: **Overbought**")
            elif latest["RSI"] <= 30:
                st.write("- RSI state: **Oversold**")
            else:
                st.write("- RSI state: **Neutral**")
        else:
            st.write("- RSI state: N/A")
