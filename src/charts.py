import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _add_level_lines(fig, levels, row=1, col=1):
    for s in levels.get("supports", []):
        fig.add_hline(y=s, line_dash="dot", line_color="#26a69a", opacity=0.6, row=row, col=col)
    for r in levels.get("resistances", []):
        fig.add_hline(y=r, line_dash="dot", line_color="#ef5350", opacity=0.6, row=row, col=col)


def _add_breakout_markers(fig, df, row=1, col=1):
    bull = df[df.get("bull_breakout", False)]
    bear = df[df.get("bear_breakdown", False)]
    if not bull.empty:
        fig.add_trace(
            go.Scatter(
                x=bull["Date"],
                y=bull["Close"],
                mode="markers",
                name="Bull Breakout",
                marker=dict(symbol="triangle-up", size=11, color="#00e676"),
            ),
            row=row,
            col=col,
        )
    if not bear.empty:
        fig.add_trace(
            go.Scatter(
                x=bear["Date"],
                y=bear["Close"],
                mode="markers",
                name="Bear Breakdown",
                marker=dict(symbol="triangle-down", size=11, color="#ff5252"),
            ),
            row=row,
            col=col,
        )


def line_price_chart(df, show_rsi=False, levels=None):
    levels = levels or {"supports": [], "resistances": []}
    if show_rsi:
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25],
            subplot_titles=("Price", "RSI"),
        )
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines", name="Close"), row=1, col=1)
        for colname in [c for c in df.columns if c.startswith("MA")]:
            fig.add_trace(go.Scatter(x=df["Date"], y=df[colname], mode="lines", name=colname), row=1, col=1)
        _add_level_lines(fig, levels, row=1, col=1)
        _add_breakout_markers(fig, df, row=1, col=1)
        if "RSI" in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI(14)", line=dict(color="#f5a623")), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=2, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        fig.update_layout(template="plotly_dark", height=700, margin=dict(l=20, r=20, t=50, b=20))
        return fig

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines", name="Close"))
    for colname in [c for c in df.columns if c.startswith("MA")]:
        fig.add_trace(go.Scatter(x=df["Date"], y=df[colname], mode="lines", name=colname))
    for s in levels.get("supports", []):
        fig.add_hline(y=s, line_dash="dot", line_color="#26a69a", opacity=0.6)
    for r in levels.get("resistances", []):
        fig.add_hline(y=r, line_dash="dot", line_color="#ef5350", opacity=0.6)
    _add_breakout_markers(fig, df)
    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def candlestick_volume_chart(df, show_rsi=False, levels=None):
    levels = levels or {"supports": [], "resistances": []}
    if show_rsi:
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=("Price", "Volume", "RSI"),
        )
    else:
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25],
            subplot_titles=("Price", "Volume"),
        )

    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1,
        col=1,
    )

    for colname in [c for c in df.columns if c.startswith("MA")]:
        fig.add_trace(go.Scatter(x=df["Date"], y=df[colname], mode="lines", name=colname), row=1, col=1)
    _add_level_lines(fig, levels, row=1, col=1)
    _add_breakout_markers(fig, df, row=1, col=1)

    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["Open"], df["Close"])]
    fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color=colors, opacity=0.8), row=2, col=1)

    if show_rsi and "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], mode="lines", name="RSI(14)", line=dict(color="#f5a623")), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=3, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=850 if show_rsi else 700,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig
