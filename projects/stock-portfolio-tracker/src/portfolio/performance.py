import pandas as pd
import streamlit as st
from sqlalchemy import text
from src.db.db_connection import engine


def save_portfolio_snapshot(
    total_value,
    total_cost,
    total_profit_loss
):

    total_value = float(total_value)
    total_cost = float(total_cost)
    total_profit_loss = float(total_profit_loss)

    query = text("""
        INSERT INTO portfolio_snapshots (
            total_value,
            total_cost,
            total_profit_loss
        )
        VALUES (
            :total_value,
            :total_cost,
            :total_profit_loss
        )
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_profit_loss": total_profit_loss
            }
        )


@st.cache_data(ttl=300)
def get_portfolio_history():

    query = """
    SELECT
        snapshot_date,
        total_value
    FROM portfolio_snapshots
    ORDER BY snapshot_date
    """

    return pd.read_sql(query, engine)


def get_equity_curve():
    query = """
    SELECT
        snapshot_date,
        total_value
    FROM portfolio_snapshots
    ORDER BY snapshot_date
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        # Return empty Series instead of empty DataFrame
        return pd.Series(dtype=float)

    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df = df.set_index("snapshot_date").sort_index()

    # Normalize to 100
    starting_value = df["total_value"].iloc[0]

    df["equity_curve"] = (df["total_value"] / starting_value) * 100

    # Return the equity_curve series
    return df["equity_curve"]
