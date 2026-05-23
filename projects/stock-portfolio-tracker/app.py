import streamlit as st
import pandas as pd

# Import data loading and processing functions
from src.portfolio.trades import (
    buy_stock,
    sell_stock,
    view_trades,
    reset_portfolio
)

from src.portfolio.services import (
    get_portfolio_dashboard_data
)

from src.portfolio.performance import (
    save_portfolio_snapshot
)

from src.portfolio.performance import (
    get_portfolio_history
)

from src.portfolio.benchmark import (
    get_benchmark_data
)

from src.portfolio.performance_comparison import (
    get_normalized_benchmark_data
)

from src.portfolio.performance import (
    get_equity_curve
)

from src.portfolio.realized_pl import (
    calculate_realized_pl
)

from src.portfolio.position_attribution import (
    calculate_position_attribution
)

# Set up page config (Optional but recommended for layout)
st.set_page_config(layout="wide")
st.title("Stock Portfolio Tracker")

# ==========================================
# Sidebar Trading Panel
# ==========================================

# --- SECTION 1: Portfolio Actions ---
st.sidebar.header("💼 Portfolio Actions")
st.sidebar.subheader("Trade Execution")

ticker = st.sidebar.text_input("Ticker", value="AAPL").upper().strip()
action = st.sidebar.selectbox("Action", ["BUY", "SELL"])
quantity = st.sidebar.number_input("Quantity", min_value=1, step=1)
price = st.sidebar.number_input("Price", min_value=0.0, step=0.01)
submit_trade = st.sidebar.button("Submit Trade", use_container_width=True)

# Add a divider line
st.sidebar.divider()

# --- SECTION 2: Data Controls ---
st.sidebar.header("⚙️ Data Controls")

save_snapshot = st.sidebar.button("Save Portfolio Snapshot", use_container_width=True)
reset_data = st.sidebar.button("Reset Portfolio", use_container_width=True)

# Add another divider line
st.sidebar.divider()

# --- SECTION 3: Analytics Settings ---
st.sidebar.header("Analytics Settings")

# Placeholder UI components for your future logic adjustments
benchmark_period = st.sidebar.selectbox(
    "Benchmark Period", 
    ["1M", "3M", "6M", "YTD", "1Y", "ALL"], 
    index=4
)

risk_threshold = st.sidebar.slider(
    "Systemic Risk Threshold (%)", 
    min_value=10, 
    max_value=100, 
    value=50, 
    step=5
)

# --- Action Logic Controllers ---

# 1. Handle Trade Execution
if submit_trade:
    try:
        with st.sidebar.spinner("Processing trade..."):
            if action == "BUY":
                buy_stock(ticker, quantity, price)
            elif action == "SELL":
                sell_stock(ticker, quantity, price)
            st.cache_data.clear() 
        st.sidebar.success(f"{action} order executed for {ticker}")
        st.rerun()
    except Exception as e:
        st.sidebar.error(str(e))

# 2. Handle Snapshot Saving
if save_snapshot:
    with st.sidebar.spinner("Saving snapshot..."):
        save_portfolio_snapshot(total_value, summary["cost_basis"], total_pl)
    st.sidebar.success("Snapshot saved successfully!")

# 3. Handle System Reset
if reset_data:
    reset_portfolio()
    st.cache_data.clear()
    st.sidebar.success("Portfolio reset successfully.")
    st.rerun()

# --- Save Portfolio Snapshot Button ---
save_snapshot = st.sidebar.button(
    "Save Portfolio Snapshot"
)

# ==========================================
# Main Dashboard Display Area
# ==========================================
# Use a spinner for the main dashboard data loading process
with st.spinner("Loading portfolio dashboard data..."):
    portfolio_df, summary = get_portfolio_dashboard_data()

# Calculate portfolio return based on summary data...
portfolio_return = 0
if summary["cost_basis"] > 0:
    portfolio_return = ((summary["market_value"] - summary["cost_basis"]) / summary["cost_basis"]) * 100

    
# Load your portfolio dashboard data
portfolio_df, summary = get_portfolio_dashboard_data()

#Calculate portfolio return based on summary data, with a check to avoid division by zero
portfolio_return = 0

if summary["cost_basis"] > 0:

    portfolio_return = (
        (
            summary["market_value"]
            - summary["cost_basis"]
        )
        / summary["cost_basis"]
    ) * 100

# Dynamically calculate summaries directly from the columns if keys mismatch
if not portfolio_df.empty:
    total_value = portfolio_df["Market Value"].sum()
    total_pl = portfolio_df["Unrealized P/L"].sum()
    
    # Advanced Analytics Calculations
    portfolio_df["Weight (%)"] = (portfolio_df["Market Value"] / total_value) * 100
    # Simple risk framework: Flag positions taking up > risk_threshold% of the portfolio
    heavy_concentration = portfolio_df[portfolio_df["Weight (%)"] > risk_threshold]["Ticker"].tolist()
else:
    total_value = 0.0
    total_pl = 0.0

# Calculate realized P/L from trade history
realized_pl = calculate_realized_pl()


# Layout grid for summary metrics and advanced analytics
st.subheader("Executive Portfolio Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
with col2:
    # This will display negative numbers nicely as -$12,614.62
    st.metric("Total Gain/Loss", f"${total_pl:,.2f}")
with col3:
    st.metric("Realized P/L", f"${realized_pl:,.2f}")
with col4:
    risk_status = (
        "⚠️ High Risk"
        if heavy_concentration
        else "✅ Diversified"
    )
    st.metric(
        "Risk Rating",
        risk_status
    )

st.write("---")

# --- Portfolio Performance Chart ---
st.subheader("Portfolio Performance")

# Show a spinner while pulling historical records
with st.spinner("Compiling historical performance chart..."):
    history_df = get_portfolio_history()

if not history_df.empty:
    history_df["snapshot_date"] = pd.to_datetime(history_df["snapshot_date"])
    history_df = history_df.set_index("snapshot_date")
    st.line_chart(history_df["total_value"])

history_df = get_portfolio_history()

if not history_df.empty:

    history_df["snapshot_date"] = pd.to_datetime(
        history_df["snapshot_date"]
    )

    history_df = history_df.set_index(
        "snapshot_date"
    )

    st.line_chart(history_df["total_value"])

st.write("---")

# --- Benchmark Comparison ---
st.subheader("Benchmark Comparison")

# Show a spinner for external benchmark data fetch
with st.spinner("Fetching market benchmarks..."):
    benchmark_df = get_benchmark_data()

portfolio_row = pd.DataFrame([{
    "Benchmark": "Your Portfolio",
    "Ticker": "CUSTOM",
    "Return (%)": round(portfolio_return, 2)
}])

st.write("---")

st.subheader("Portfolio vs Market Benchmarks")

# Show a spinner for the normalized time-series chart data
with st.spinner("Normalizing performance trends..."):
    comparison_chart_df = get_normalized_benchmark_data()

if not comparison_chart_df.empty:
    st.line_chart(comparison_chart_df)

portfolio_row = pd.DataFrame([
    {
        "Benchmark": "Your Portfolio",
        "Ticker": "CUSTOM",
        "Return (%)": round(portfolio_return, 2)
    }
])

comparison_df = pd.concat(
    [portfolio_row, benchmark_df],
    ignore_index=True
)

st.dataframe(
    comparison_df,
    use_container_width=True
)

st.write("---")

# --- Position Attribution ---
st.subheader(
    "Performance Attribution"
)

attribution_df = (
    calculate_position_attribution()
)

if not attribution_df.empty:

    st.dataframe(
        attribution_df.style.format({
            "Realized P/L": "${:,.2f}",
            "Unrealized P/L": "${:,.2f}",
            "Total P/L": "${:,.2f}"
        }),
        use_container_width=True
    )

else:

    st.info(
        "No attribution data available."
    )

# --- Portfolio Equity Curve ---
st.subheader("Portfolio Equity Curve")

equity_df = get_equity_curve()

if not equity_df.empty:

    equity_df = equity_df.set_index(
        "snapshot_date"
    )

    st.line_chart(
        equity_df["equity_curve"]
    )

else:

    st.info(
        "Save portfolio snapshots to build equity curve history."
    )


# --- Interactive Analytics Table ---
st.subheader("Allocation & Positions Analysis")
if not portfolio_df.empty:
    # Re-ordering and displaying columns with analytical weights
    display_df = portfolio_df.copy()
    st.dataframe(display_df.style.format({
        "Shares": "{:,.0f}",
        "Avg Cost": "${:,.2f}",
        "Current Price": "${:,.2f}",
        "Market Value": "${:,.2f}",
        "Unrealized P/L": "${:,.2f}",
        "Weight (%)": "{:.2f}%"
    }), use_container_width=True)
else:
    st.info("No active holdings found. Use the sidebar to execute a trade and seed the database.")

st.write("---")

# --- Automated Research & Commentary Insights Section ---
st.subheader("Automated Portfolio Strategy Insights")

with st.container():
    if not portfolio_df.empty:
        # Insight 1: Diversification Check
        if heavy_concentration:
            st.warning(f"**Concentration Risk Alert:** Your position in **{', '.join(heavy_concentration)}** represents more than {risk_threshold}% of your total capital. Consider trimming or adding alternative assets to rebalance.")
        else:
            st.success(f"**Diversification Matrix:** Capital distribution looks healthy. No single asset exceeds our {risk_threshold}% systemic risk threshold.")
            
        # Insight 2: Performance Commentary
        top_winner = portfolio_df.sort_values(by="Unrealized P/L", ascending=False).iloc[0]
        if top_winner["Unrealized P/L"] > 0:
            st.info(f"**Alpha Driver:** **{top_winner['Ticker']}** is currently your best performing asset, contributing an unrealized gain of `${top_winner['Unrealized P/L']:,.2f}`. Monitor macro factors around this industry sector to secure gains.")
        else:
            st.info("**Market Conditions:** All active positions are currently weathering unrealized drawdowns. This is an opportune time to review cost-averaging strategy options via the sidebar panel.")
    else:
        st.write("Execute your first trade to unlock automated quantitative analysis and strategic position insights.")


# --- Trade History ---
st.subheader("Trade History")

trades_df = view_trades()

if not trades_df.empty:

    st.dataframe(
        trades_df,
        use_container_width=True
    )

else:
    st.info("No trades found.")