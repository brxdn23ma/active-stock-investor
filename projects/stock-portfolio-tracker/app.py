import streamlit as st
import pandas as pd

# 1. Import your interactive trading backend functions
from src.portfolio.trades import (
    buy_stock,
    sell_stock
)

# 2. Import your dashboard data loader service
from src.portfolio.services import (
    get_portfolio_dashboard_data
)

# Set up page config (Optional but recommended for layout)
st.set_page_config(layout="wide")
st.title("Stock Portfolio Tracker")

# ==========================================
# Sidebar Trading Panel
# ==========================================
st.sidebar.header("Execute Trade")

# Ensure ticker is automatically stripped and upper-cased
ticker = st.sidebar.text_input(
    "Ticker",
    value="AAPL"
).upper().strip()

action = st.sidebar.selectbox(
    "Action",
    ["BUY", "SELL"]
)

quantity = st.sidebar.number_input(
    "Quantity",
    min_value=1,
    step=1
)

price = st.sidebar.number_input(
    "Price",
    min_value=0.0,
    step=0.01
)

submit_trade = st.sidebar.button(
    "Submit Trade"
)

# If the user clicks submit, execute the backend logic and trigger a refresh
if submit_trade:
    if action == "BUY":
        buy_stock(ticker, quantity, price)
    elif action == "SELL":
        sell_stock(ticker, quantity, price)
    
    st.sidebar.success(f"{action} order executed for {ticker}")
    
    # Crucial step: forces Streamlit to rerun, pulling new data right away
    st.rerun()

# ==========================================
# Main Dashboard Display Area
# ==========================================
# Load your portfolio dashboard data
portfolio_df, summary = get_portfolio_dashboard_data()

# Dynamically calculate summaries directly from the columns if keys mismatch
if not portfolio_df.empty:
    total_value = portfolio_df["Market Value"].sum()
    total_pl = portfolio_df["Unrealized P/L"].sum()
    
    # Advanced Analytics Calculations
    portfolio_df["Weight (%)"] = (portfolio_df["Market Value"] / total_value) * 100
    # Simple risk framework: Flag positions taking up > 50% of the portfolio
    heavy_concentration = portfolio_df[portfolio_df["Weight (%)"] > 50.0]["Ticker"].tolist()
else:
    total_value = 0.0
    total_pl = 0.0

# Layout grid for summary metrics and advanced analytics
st.subheader("Executive Portfolio Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
with col2:
    # This will display negative numbers nicely as -$12,614.62
    st.metric("Total Gain/Loss", f"${total_pl:,.2f}")
with col3:
    risk_status = "⚠️ High Risk" if heavy_concentration else "✅ Diversified"
    st.metric("Risk Rating", risk_status)

st.write("---")

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
            st.warning(f"**Concentration Risk Alert:** Your position in **{', '.join(heavy_concentration)}** represents more than 50% of your total capital. Consider trimming or adding alternative assets to rebalance.")
        else:
            st.success("**Diversification Matrix:** Capital distribution looks healthy. No single asset exceeds our 50% systemic risk threshold.")
            
        # Insight 2: Performance Commentary
        top_winner = portfolio_df.sort_values(by="Unrealized P/L", ascending=False).iloc[0]
        if top_winner["Unrealized P/L"] > 0:
            st.info(f"**Alpha Driver:** **{top_winner['Ticker']}** is currently your best performing asset, contributing an unrealized gain of `${top_winner['Unrealized P/L']:,.2f}`. Monitor macro factors around this industry sector to secure gains.")
        else:
            st.info("**Market Conditions:** All active positions are currently weathering unrealized drawdowns. This is an opportune time to review cost-averaging strategy options via the sidebar panel.")
    else:
        st.write("Execute your first trade to unlock automated quantitative analysis and strategic position insights.")