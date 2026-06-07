# cd ~/_Documents/github/active-stock-investor/projects/stock-portfolio-tracker

import streamlit as st
import pandas as pd

# =========================================================
# IMPORTS: Data loading, processing, and analytics engines
# =========================================================

from src.portfolio.trades import (
    buy_stock,
    sell_stock,
    view_trades,
    reset_portfolio,
)

from src.portfolio.services import (
    get_portfolio_dashboard_data,
)

from src.portfolio.performance import (
    get_equity_curve,
    save_portfolio_snapshot,
)

from src.portfolio.realized_pl import (
    calculate_realized_pl,
)

from src.portfolio.position_attribution import (
    calculate_position_attribution,
)

from src.portfolio.performance_engine import (
    build_combined_performance_dashboard,
)

from src.portfolio.risk_analytics import (
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_return_series,
)


# ==========================================
# GLOBAL PAGE CONFIG
# ==========================================

st.set_page_config(layout="wide")
st.title("Stock Portfolio Tracker")


# ==========================================
# SIDEBAR: Trading, Data, and Analytics Controls
# ==========================================

# --- Sidebar Section 1: Trade Execution Controls ---
st.sidebar.header("💼 Portfolio Actions")
st.sidebar.subheader("Trade Execution")

ticker = st.sidebar.text_input("Ticker", value="AAPL").upper().strip()
action = st.sidebar.selectbox("Action", ["BUY", "SELL"])
quantity = st.sidebar.number_input("Quantity", min_value=1, step=1)
price = st.sidebar.number_input("Price", min_value=0.0, step=0.01)
submit_trade = st.sidebar.button("Submit Trade", use_container_width=True)

st.sidebar.divider()

# --- Sidebar Section 2: Data Management Controls ---
st.sidebar.header("⚙️ Data Controls")

save_snapshot = st.sidebar.button("Save Portfolio Snapshot", use_container_width=True)
reset_data = st.sidebar.button("Reset Portfolio", use_container_width=True)

st.sidebar.divider()

# --- Sidebar Section 3: Analytics Configuration Controls ---
st.sidebar.header("Analytics Settings")

benchmark_period = st.sidebar.selectbox(
    "Benchmark Period",
    ["1M", "3M", "6M", "YTD", "1Y", "ALL"],
    index=4,
)

risk_threshold = st.sidebar.slider(
    "Systemic Risk Threshold (%)",
    min_value=10,
    max_value=100,
    value=50,
    step=5,
)


# ==========================================
# SIDEBAR ACTION LOGIC (Trading)
# ==========================================

# 1. Handle Trade Execution
if submit_trade:
    try:
        with st.spinner("Processing trade..."):

            st.write("BUTTON TRIGGERED")

            if action == "BUY":
                buy_stock(ticker, quantity, price)

            elif action == "SELL":
                sell_stock(ticker, quantity, price)

            st.cache_data.clear()

        st.sidebar.success(f"{action} order executed for {ticker}")

    except Exception as e:
        st.exception(e)


# ==========================================
# MAIN: DATA LOADING AND CORE AGGREGATES
# ==========================================

with st.spinner("Loading portfolio dashboard data..."):
    portfolio_df, summary = get_portfolio_dashboard_data()

# TEMP DEBUGGING
st.write(view_trades())

if not portfolio_df.empty:
    total_value = portfolio_df["Market Value"].sum()
    total_pl = portfolio_df["Unrealized P/L"].sum()
else:
    total_value = 0.0
    total_pl = 0.0

# Calculate realized P/L from trade history
realized_pl = calculate_realized_pl()

# Risk / Performance aggregates (time-series based)
returns = calculate_return_series()
volatility = calculate_volatility(returns)
sharpe_ratio = calculate_sharpe_ratio(returns, risk_free_rate=0.045)
equity_curve = get_equity_curve()
max_drawdown = calculate_max_drawdown(equity_curve)

# Only compute weights and concentration if there is data
heavy_concentration = []
if not portfolio_df.empty and total_value != 0:
    portfolio_df["Weight (%)"] = (portfolio_df["Market Value"] / total_value) * 100
    heavy_concentration = portfolio_df[
        portfolio_df["Weight (%)"] > risk_threshold
    ]["Ticker"].tolist()


# ==========================================
# TABS: HIGH-LEVEL DASHBOARD STRUCTURE
# ==========================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Executive Summary",
    "2. Combined Performance",
    "3. Risk Analytics",
    "4. Attribution Analysis",
    "5. Allocation Analysis",
    "6. AI / Strategy Insights",
    "7. Trade History",
])


# ==========================================
# 1. EXECUTIVE SUMMARY (Tab 1)
# ==========================================

with tab1:
    st.subheader("1. Executive Summary")

    # Snapshot saving now uses computed aggregates
    if save_snapshot and not portfolio_df.empty:
        with st.spinner("Saving snapshot..."):
            # Use dynamically computed totals as snapshot inputs
            save_portfolio_snapshot(
                total_value,
                summary.get("cost_basis", 0.0),
                total_pl,
            )
        st.sidebar.success("Snapshot saved successfully!")

    # Handle system reset here so it is part of overall dashboard flow
    if reset_data:
        reset_portfolio()
        st.cache_data.clear()
        st.sidebar.success("Portfolio reset successfully.")
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total Gain/Loss", f"${total_pl:,.2f}")
    with col3:
        st.metric("Realized P/L", f"${realized_pl:,.2f}")
    with col4:
        risk_status = "⚠️ High Risk" if heavy_concentration else "✅ Diversified"
        st.metric("Risk Rating", risk_status)

    st.write("---")


# ==========================================
# 2. COMBINED PERFORMANCE ANALYTICS (Tab 2)
# ==========================================

with tab2:
    st.subheader("2. Combined Performance Analytics (Portfolio vs Benchmark)")

    with st.spinner("Building combined analytics engine..."):
        # TODO: wire benchmark_period into this call in a later improvement
        combined_df, metrics_df = build_combined_performance_dashboard()

    if not combined_df.empty:
        st.line_chart(combined_df)
        st.dataframe(metrics_df, use_container_width=True)
    else:
        st.info("Not enough historical data available.")

    st.write("---")


# ==========================================
# 3. RISK ANALYTICS (Tab 3)
# ==========================================

with tab3:
    st.subheader("3. Risk Analytics")

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    with risk_col1:
        st.metric("Volatility", f"{volatility:.2f}%")

    with risk_col2:
        st.metric("Sharpe Ratio", sharpe_ratio)

    with risk_col3:
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")

    st.write("---")


# ==========================================
# 4. ATTRIBUTION ANALYSIS (Tab 4)
# ==========================================

with tab4:
    st.subheader("4. Attribution Analysis (Position-Level Performance)")

    attribution_df = calculate_position_attribution()

    if not attribution_df.empty:
        st.dataframe(
            attribution_df.style.format(
                {
                    "Realized P/L": "${:,.2f}",
                    "Unrealized P/L": "${:,.2f}",
                    "Total P/L": "${:,.2f}",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info("No attribution data available.")

    st.write("---")


# ==========================================
# 5. ALLOCATION ANALYSIS (Tab 5)
# ==========================================

with tab5:
    st.subheader("5. Allocation Analysis (Positions & Weights)")

    if not portfolio_df.empty:
        display_df = portfolio_df.copy()
        st.dataframe(
            display_df.style.format(
                {
                    "Shares": "{:,.0f}",
                    "Avg Cost": "${:,.2f}",
                    "Current Price": "${:,.2f}",
                    "Market Value": "${:,.2f}",
                    "Unrealized P/L": "${:,.2f}",
                    "Weight (%)": "{:.2f}%",
                }
            ),
            use_container_width=True,
        )
    else:
        st.info(
            "No active holdings found. Use the sidebar to execute a trade and seed the database."
        )

    st.write("---")


# ==========================================
# 6. AI / STRATEGY INSIGHTS (Tab 6)
# ==========================================

with tab6:
    st.subheader("6. AI / Strategy Insights")

    if not portfolio_df.empty:
        # Insight 1: Diversification and concentration risk
        if heavy_concentration:
            st.warning(
                f"**Concentration Risk Alert:** Your position in **{', '.join(heavy_concentration)}** "
                f"represents more than {risk_threshold}% of your total capital. Consider trimming or "
                f"adding alternative assets to rebalance."
            )
        else:
            st.success(
                f"**Diversification Matrix:** Capital distribution looks healthy. "
                f"No single asset exceeds the {risk_threshold}% systemic risk threshold."
            )

        # Insight 2: Performance commentary on best performer
        top_winner = portfolio_df.sort_values(
            by="Unrealized P/L", ascending=False
        ).iloc[0]
        if top_winner["Unrealized P/L"] > 0:
            st.info(
                f"**Alpha Driver:** **{top_winner['Ticker']}** is currently your best performing asset, "
                f"contributing an unrealized gain of `${top_winner['Unrealized P/L']:,.2f}`. "
                f"Monitor macro factors around this industry sector to secure gains."
            )
        else:
            st.info(
                "**Market Conditions:** All active positions are currently facing unrealized drawdowns. "
                "This is an opportune time to review cost-averaging or risk-management strategies."
            )
    else:
        st.write(
            "Execute your first trade to unlock automated quantitative analysis and strategic position insights."
        )

    st.write("---")


# ==========================================
# 7. TRADE HISTORY (Tab 7)
# ==========================================

with tab7:
    st.subheader("7. Trade History")

    trades_df = view_trades()

    if not trades_df.empty:
        st.dataframe(trades_df, use_container_width=True)
    else:
        st.info("No trades found.")