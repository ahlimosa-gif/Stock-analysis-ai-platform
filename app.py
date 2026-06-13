import streamlit as st

st.set_page_config(page_title="Stock Analysis AI Platform", layout="wide")

st.title("Stock Analysis AI Platform")
st.caption("Technical charting, next-day forecast experiments, and backtest validation in one Streamlit workspace.")

st.markdown("""
## Modules

- **Overview**: price chart, moving averages, RSI, support/resistance, and breakout markers.
- **Next-Day Forecast**: next-session directional probabilities, projected close, and scenario paths.
- **Backtest / Accuracy**: rolling validation, confusion matrix, class metrics, and baseline comparison.

Use the left sidebar to open each page.
""")
