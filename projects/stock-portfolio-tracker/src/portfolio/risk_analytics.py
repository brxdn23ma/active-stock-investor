import pandas as pd
import numpy as np

from src.portfolio.performance import (
    get_equity_curve
)


def calculate_return_series():

    equity_curve = get_equity_curve()

    if equity_curve.empty:
        return pd.Series(dtype=float)

    returns = (
        equity_curve
        .pct_change()
        .dropna()
    )

    return returns

returns = calculate_return_series()

def calculate_volatility(returns):
    if returns.empty:
        return 0

    volatility = (
        returns.std()
        * np.sqrt(252)
        * 100
    )

    return round(volatility, 2)

def calculate_sharpe_ratio():

    returns = calculate_return_series()

    if returns.empty:
        return 0

    sharpe_ratio = (
        returns.mean()
        / returns.std()
        * np.sqrt(252)
    )

    return round(sharpe_ratio, 2)

def calculate_max_drawdown():  # largest peak-to-trough decline

    curve = get_equity_curve()

    if curve.empty:
        return 0

    rolling_max = curve.cummax()

    drawdown = (
        curve - rolling_max
    ) / rolling_max

    max_drawdown = (
        drawdown.min()
        * 100
    )

    return round(max_drawdown, 2)