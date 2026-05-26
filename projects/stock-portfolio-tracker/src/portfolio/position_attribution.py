# src/portfolio/position_attribution.py

import pandas as pd

from src.portfolio.fifo_engine import (
    process_fifo_inventory,
)


def calculate_position_attribution() -> pd.DataFrame:
    """
    Build a position-level performance attribution table from FIFO data.

    Returns
    -------
    attribution_df : pd.DataFrame
        Columns (example):
        - Ticker
        - Realized P/L
        - Unrealized P/L
        - Total P/L

    This function assumes that `process_fifo_inventory()` returns a dict
    with at least:
    - "inventory": mapping ticker -> list or dict of remaining lots
    - "realized_map": mapping ticker -> realized profit/loss
    """
    fifo_data = process_fifo_inventory()

    inventory = fifo_data.get("inventory", {})
    realized_map = fifo_data.get("realized_map", {})

    # Build a row per ticker
    rows = []

    # Use union of tickers from both realized_map and inventory keys
    tickers = set(realized_map.keys()) | set(inventory.keys())

    for ticker in tickers:
        realized_pl = realized_map.get(ticker, 0.0)

        # Compute unrealized P/L from inventory
        # This depends on how you store each lot. For now we assume each
        # lot is a dict with keys: "shares", "cost_basis", "market_value".
        lots = inventory.get(ticker, [])

        unrealized_pl = 0.0

        for lot in lots:
            # Adjust these field names to match your fifo_engine structure
            shares = lot.get("shares", 0)
            cost_basis = lot.get("cost_basis", 0.0)
            market_value = lot.get("market_value", 0.0)

            unrealized_pl += (market_value - cost_basis)

        total_pl = realized_pl + unrealized_pl

        rows.append(
            {
                "Ticker": ticker,
                "Realized P/L": realized_pl,
                "Unrealized P/L": unrealized_pl,
                "Total P/L": total_pl,
            }
        )

    if not rows:
        return pd.DataFrame()

    attribution_df = pd.DataFrame(rows)
    attribution_df = attribution_df.sort_values(by="Total P/L", ascending=False)

    return attribution_df