from sqlalchemy import text
from src.db.db_connection import engine
import pandas as pd


def buy_stock(ticker, quantity, price):

    insert_query = text("""
        INSERT INTO trades (ticker, action, quantity, price)
        VALUES (:ticker, :action, :quantity, :price)
    """)

    with engine.connect() as conn:
        conn.execute(
            insert_query,
            {
                "ticker": ticker,
                "action": "BUY",
                "quantity": quantity,
                "price": price
            }
        )
        conn.commit()

    print(f"Bought {quantity} shares of {ticker}")


def sell_stock(ticker, quantity, price):

    holdings_query = text("""
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN action = 'BUY' THEN quantity
                        WHEN action = 'SELL' THEN -quantity
                    END
                ),
                0
            ) AS shares_owned
        FROM trades
        WHERE ticker = :ticker
    """)

    with engine.connect() as conn:

        result = conn.execute(
            holdings_query,
            {"ticker": ticker}
        ).fetchone()

        shares_owned = result[0]

        if quantity > shares_owned:
            raise ValueError(
                f"Cannot sell {quantity} shares of {ticker}. "
                f"Only {shares_owned} shares owned."
            )

        insert_query = text("""
            INSERT INTO trades (ticker, action, quantity, price)
            VALUES (:ticker, :action, :quantity, :price)
        """)

        conn.execute(
            insert_query,
            {
                "ticker": ticker,
                "action": "SELL",
                "quantity": quantity,
                "price": price
            }
        )

        conn.commit()

    print(f"Sold {quantity} shares of {ticker}")


def view_trades():

    query = """
    SELECT *
    FROM trades
    ORDER BY trade_date DESC
    """

    df = pd.read_sql(query, engine)

    return df


def reset_portfolio():

    delete_query = text("""
        DELETE FROM trades
    """)

    with engine.connect() as conn:
        conn.execute(delete_query)
        conn.commit()

    print("Portfolio reset complete.")