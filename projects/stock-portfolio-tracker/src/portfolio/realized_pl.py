from src.portfolio.fifo_engine import (
    process_fifo_inventory
)


def calculate_realized_pl():

    fifo_data = process_fifo_inventory()

    realized_map = fifo_data["realized_map"]

    total_realized = sum(
        realized_map.values()
    )

    return round(total_realized, 2)