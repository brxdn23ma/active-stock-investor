import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def get_normalized_benchmark_data():

    tickers = {
        "SPY": "S&P 500",
        "QQQ": "Nasdaq",
        "BTC-USD": "Bitcoin"
    }

    combined_df = pd.DataFrame()

    for ticker, name in tickers.items():

        try:

            data = yf.download(
                ticker,
                period="1mo",
                progress=False
            )

            if data.empty:
                continue

            prices = data["Close"]

            normalized = (
                prices / prices.iloc[0]
            ) * 100

            combined_df[name] = normalized

        except Exception as e:

            print(
                f"Error loading {ticker}: {e}"
            )

    return combined_df