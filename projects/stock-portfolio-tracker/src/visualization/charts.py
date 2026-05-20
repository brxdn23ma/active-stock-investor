import matplotlib.pyplot as plt

from src.portfolio.analytics import (
    calculate_holdings
)

from src.market.market_data import (
    get_current_price
)


def plot_portfolio_allocation():

    holdings = calculate_holdings()

    labels = []
    values = []

    for _, row in holdings.iterrows():

        ticker = row["ticker"]

        shares = row["shares_owned"]

        current_price = get_current_price(ticker)

        market_value = shares * current_price

        labels.append(ticker)

        values.append(market_value)

    plt.figure(figsize=(8, 8))

    plt.pie(
        values,
        labels=labels,
        autopct='%1.1f%%'
    )

    plt.title("Portfolio Allocation")

    plt.show()


from src.portfolio.trades import (
    calculate_cost_basis
)

def plot_profit_loss():

    portfolio = calculate_cost_basis()

    tickers = []

    profits = []

    for _, row in portfolio.iterrows():

        ticker = row["ticker"]

        shares = row["shares_owned"]

        average_cost = row["average_cost"]

        current_price = get_current_price(ticker)

        market_value = shares * current_price

        total_cost = shares * average_cost

        profit_loss = market_value - total_cost

        tickers.append(ticker)

        profits.append(profit_loss)

    plt.figure(figsize=(8, 5))

    plt.bar(tickers, profits)

    plt.title("Unrealized Profit / Loss")

    plt.xlabel("Ticker")

    plt.ylabel("Profit / Loss ($)")

    plt.show()