from src.portfolio.analytics import (
    calculate_cost_basis,
    build_portfolio_dataframe
)

from src.market.market_data import (
    get_current_price
)

import streamlit as st

@st.cache_data(ttl=300)
def get_portfolio_dashboard_data():

    portfolio = calculate_cost_basis()

    if portfolio.empty:

        return portfolio, {
            "market_value": 0,
            "cost_basis": 0,
            "profit_loss": 0
        }

    live_prices = {}

    for ticker in portfolio["ticker"]:

        live_prices[ticker] = get_current_price(ticker)

    return build_portfolio_dataframe(
        portfolio,
        live_prices
    )