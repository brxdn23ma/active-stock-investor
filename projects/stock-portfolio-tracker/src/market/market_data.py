import yfinance as yf


def get_current_price(ticker):

    try:
        stock = yf.Ticker(ticker)

        # safer method
        history = stock.history(period="1d")

        if history.empty:
            return 0.0

        current_price = history["Close"].iloc[-1]

        return round(float(current_price), 2)

    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0