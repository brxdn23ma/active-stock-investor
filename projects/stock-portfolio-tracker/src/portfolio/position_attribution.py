from src.portfolio.fifo_engine import (
    process_fifo_inventory
)

fifo_data = process_fifo_inventory()

inventory = fifo_data["inventory"]

realized_map = fifo_data["realized_map"]