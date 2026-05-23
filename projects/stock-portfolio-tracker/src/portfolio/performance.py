import pandas as pd
from sqlalchemy import text
from src.db.db_connection import engine


def save_portfolio_snapshot(
    total_value,
    total_cost,
    total_profit_loss
):

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

    with engine.connect() as conn:

        conn.execute(
            query,
            {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_profit_loss": total_profit_loss
            }
        )

        conn.commit()

import streamlit as st

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
        return df

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"]
    )

    # Normalize to 100
    starting_value = df["total_value"].iloc[0]

    df["equity_curve"] = (
        df["total_value"] / starting_value
    ) * 100

    return df
