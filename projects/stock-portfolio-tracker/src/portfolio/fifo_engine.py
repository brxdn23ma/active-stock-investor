import pandas as pd

from src.db.db_connection import engine


def process_fifo_inventory():

    query = """
    SELECT
        ticker,
        action,
        quantity,
        price,
        trade_date
    FROM trades
    ORDER BY ticker, trade_date
    """

    df = pd.read_sql(query, engine)

    inventory = {}

    realized_map = {}

    for _, row in df.iterrows():

        ticker = row["ticker"]
        action = row["action"]
        quantity = row["quantity"]
        price = row["price"]

        if ticker not in inventory:
            inventory[ticker] = []

        if ticker not in realized_map:
            realized_map[ticker] = 0

        # ------------------------
        # BUY
        # ------------------------
        if action == "BUY":

            inventory[ticker].append({
                "quantity": quantity,
                "price": price
            })

        # ------------------------
        # SELL
        # ------------------------
        elif action == "SELL":

            remaining_to_sell = quantity

            while (
                remaining_to_sell > 0
                and inventory[ticker]
            ):

                lot = inventory[ticker][0]

                shares_sold = min(
                    remaining_to_sell,
                    lot["quantity"]
                )

                profit = (
                    price - lot["price"]
                ) * shares_sold

                realized_map[ticker] += profit

                lot["quantity"] -= shares_sold

                remaining_to_sell -= shares_sold

                if lot["quantity"] == 0:
                    inventory[ticker].pop(0)

    return {
        "inventory": inventory,
        "realized_map": realized_map
    }