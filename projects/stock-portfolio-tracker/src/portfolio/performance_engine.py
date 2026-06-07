import pandas as pd
from typing import Tuple, Optional

from .performance import (
    get_equity_curve,
)
from .risk_analytics import (
    calculate_return_series,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_return_series,
)
RISK_FREE_RATE = 0.045  # Example risk-free rate (4.5%)

def _compute_simple_returns_from_equity(equity: pd.Series) -> pd.Series: 
    # specifies that the function takes a pandas Series as input and returns a pandas Series as output
    """
    Helper: convert an equity curve into simple returns series.
    Assumes equity is indexed by datetime and sorted.
    """
    equity = equity.sort_index()
    returns = equity.pct_change().dropna()
    return returns


def _compute_summary_metrics(
    returns: pd.Series,
    risk_free_rate = RISK_FREE_RATE,
    label: str = "Portfolio",
) -> dict:
    """
    Helper: compute a basic bundle of performance metrics for a return series.
    """
    metrics = {}
    if returns.empty:
        return {
            "Label": label,
            "Total Return (%)": None,
            "Volatility (%)": None,
            "Sharpe Ratio": None,
            "Max Drawdown (%)": None,
        }

    cumulative_return = (1 + returns).prod() - 1

    retn = calculate_return_series()  # Ensure we have a return series (if not already)
    vol = calculate_volatility(retn)
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate = risk_free_rate)
    equity_curve = (1 + returns).cumprod()
    mdd = calculate_max_drawdown(equity_curve)

    metrics["Label"] = label
    metrics["Total Return (%)"] = cumulative_return * 100
    metrics["Volatility (%)"] = vol
    metrics["Sharpe Ratio"] = sharpe
    metrics["Max Drawdown (%)"] = mdd

    return metrics


def get_benchmark_equity_curve(
    benchmark_symbol: str = "^GSPC",
    period: str = "1Y",
) -> Optional[pd.Series]:
    """
    Placeholder: fetch benchmark equity curve over a given period.

    Implementation options:
    - Use market_data.get_current_price + historical endpoint, or
    - Load from a stored table in your DB.

    For now, this function should be implemented by you to return a
    pandas Series indexed by date with benchmark equity or price.
    """
    # TODO: implement based on your data source.
    return None


def build_combined_performance_dashboard(
    benchmark_symbol: str = "^GSPC",
    period: str = "1Y",
    risk_free_rate = RISK_FREE_RATE,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build combined portfolio vs benchmark performance for dashboard use.
    """
    # --- 1. Get portfolio equity curve ---
    portfolio_equity = get_equity_curve()  # Series indexed by date

    if portfolio_equity is None or portfolio_equity.empty:
        return pd.DataFrame(), pd.DataFrame()

    # --- 2. Get benchmark equity curve ---
    benchmark_equity = get_benchmark_equity_curve(
        benchmark_symbol=benchmark_symbol,
        period=period,
    )

    # Align portfolio and benchmark on dates if benchmark exists
    if benchmark_equity is not None and not benchmark_equity.empty:
        # Combine and forward-fill to handle small gaps
        aligned = pd.concat(
            [portfolio_equity.rename("Portfolio"), benchmark_equity.rename("Benchmark")],
            axis=1,
        ).dropna()

        if aligned.empty:
            # If alignment removes all rows, fall back to portfolio only
            aligned = portfolio_equity.to_frame(name="Portfolio")
    else:
        aligned = portfolio_equity.to_frame(name="Portfolio")

    # --- 3. Convert equity curves to returns ---
    portfolio_returns = _compute_simple_returns_from_equity(aligned["Portfolio"])

    if "Benchmark" in aligned.columns:
        benchmark_returns = _compute_simple_returns_from_equity(aligned["Benchmark"])
        # Re-align returns
        returns_df = pd.concat(
            [portfolio_returns.rename("Portfolio"), benchmark_returns.rename("Benchmark")],
            axis=1,
        ).dropna()
    else:
        returns_df = portfolio_returns.to_frame(name="Portfolio")

    # --- 4. Build normalized cumulative performance (for chart) ---
    # Start at 1.0 and multiply through (1 + daily_return)
    cum_perf = (1 + returns_df).cumprod()

    # Optional: compute active performance (portfolio relative to benchmark)
    if "Benchmark" in cum_perf.columns:
        cum_perf["Active"] = cum_perf["Portfolio"] / cum_perf["Benchmark"] - 1.0

    combined_df = cum_perf

    # --- 5. Build performance metrics table ---
    metrics_list = []

    # Portfolio metrics
    metrics_list.append(
        _compute_summary_metrics(
            returns_df["Portfolio"], risk_free_rate=risk_free_rate, label="Portfolio"
        )
    )

    if "Benchmark" in returns_df.columns:
        metrics_list.append(
            _compute_summary_metrics(
                returns_df["Benchmark"], risk_free_rate=risk_free_rate, label="Benchmark"
            )
        )

        # Active metrics (portfolio minus benchmark)
        active_returns = returns_df["Portfolio"] - returns_df["Benchmark"]
        metrics_list.append(
            _compute_summary_metrics(
                active_returns, risk_free_rate=risk_free_rate, label="Active"
            )
        )

    metrics_df = pd.DataFrame(metrics_list)

    return combined_df, metrics_df