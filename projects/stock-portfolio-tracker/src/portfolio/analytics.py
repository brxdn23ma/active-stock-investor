import pandas as pd
from src.db.db_connection import engine


def calculate_holdings():

    query = """
    SELECT
        ticker,

        SUM(
            CASE
                WHEN action = 'BUY' THEN quantity
                WHEN action = 'SELL' THEN -quantity
            END
        ) AS shares_owned

    FROM trades

    GROUP BY ticker
    """

    return pd.read_sql(query, engine)


def calculate_cost_basis():

    query = """
    SELECT
        ticker,

        SUM(
            CASE
                WHEN action = 'BUY'
                THEN quantity * price

                WHEN action = 'SELL'
                THEN -quantity * price
            END
        ) AS total_cost,

        SUM(
            CASE
                WHEN action = 'BUY'
                THEN quantity

                WHEN action = 'SELL'
                THEN -quantity
            END
        ) AS shares_owned

    FROM trades

    GROUP BY ticker

    HAVING
        SUM(
            CASE
                WHEN action = 'BUY' THEN quantity
                WHEN action = 'SELL' THEN -quantity
            END
        ) > 0
    """

    df = pd.read_sql(query, engine)

    df["average_cost"] = (
        df["total_cost"] / df["shares_owned"]
    )

    return df


def build_portfolio_dataframe(
    portfolio_df,
    live_prices
):

    rows = []

    total_market_value = 0
    total_cost_basis = 0
    total_profit_loss = 0

    for _, row in portfolio_df.iterrows():

        ticker = row["ticker"]

        shares = row["shares_owned"]

        average_cost = row["average_cost"]

        current_price = live_prices.get(ticker, 0)

        market_value = shares * current_price

        cost_basis = shares * average_cost

        profit_loss = market_value - cost_basis

        total_market_value += market_value
        total_cost_basis += cost_basis
        total_profit_loss += profit_loss

        rows.append({
            "Ticker": ticker,
            "Shares": shares,
            "Avg Cost": round(average_cost, 2),
            "Current Price": round(current_price, 2),
            "Market Value": round(market_value, 2),
            "Unrealized P/L": round(profit_loss, 2)
        })

    summary = {
        "market_value": total_market_value,
        "cost_basis": total_cost_basis,
        "profit_loss": total_profit_loss
    }

    return pd.DataFrame(rows), summary
