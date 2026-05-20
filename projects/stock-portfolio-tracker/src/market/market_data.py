import yfinance as yf


def get_current_price(ticker):

    stock = yf.Ticker(ticker)

    current_price = stock.info["regularMarketPrice"]

    return current_price