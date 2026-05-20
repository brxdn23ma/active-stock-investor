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

    insert_query = text("""
        INSERT INTO trades (ticker, action, quantity, price)
        VALUES (:ticker, :action, :quantity, :price)
    """)

    with engine.connect() as conn:
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