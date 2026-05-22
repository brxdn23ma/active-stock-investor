import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def get_benchmark_data():

    benchmarks = {
        "SPY": "S&P 500",
        "QQQ": "Nasdaq",
        "BTC-USD": "Bitcoin"
    }

    benchmark_returns = []

    for ticker, name in benchmarks.items():

        try:

            data = yf.download(
                ticker,
                period="1mo",
                progress=False
            )

            if data.empty:
                continue

            start_price = data["Close"].iloc[0]
            end_price = data["Close"].iloc[-1]

            return_pct = (
                (end_price - start_price)
                / start_price
            ) * 100

            benchmark_returns.append({
                "Benchmark": name,
                "Ticker": ticker,
                "Return (%)": round(float(return_pct), 2)
            })

        except Exception as e:

            print(
                f"Benchmark error for {ticker}: {e}"
            )

    return pd.DataFrame(benchmark_returns)