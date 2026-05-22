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