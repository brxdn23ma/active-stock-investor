import pandas as pd
import numpy as np

from src.portfolio.performance import (
    get_equity_curve
)

def calculate_return_series():
    """
    Calculate daily portfolio returns from the equity curve.

    Returns
    -------
    pandas.Series
        Daily percentage returns.
    """

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

def calculate_sharpe_ratio(
    returns,
    risk_free_rate=0.045
):
    """
    Calculate annualized Sharpe Ratio.
    """

    if returns is None or len(returns) == 0:
        return 0.0

    if returns.std() == 0:
        return 0.0

    daily_rf = risk_free_rate / 252

    excess_returns = returns - daily_rf

    sharpe = (
        excess_returns.mean()
        / excess_returns.std()
    ) * np.sqrt(252)

    return round(sharpe, 2)

def calculate_max_drawdown(equity_curve):
    
    if equity_curve.empty:
        return 0.0

    running_max = equity_curve.cummax()

    drawdowns = (
        equity_curve - running_max
    ) / running_max

    return drawdowns.min() * 100