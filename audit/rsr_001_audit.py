#!/usr/bin/env python3
"""Independent post-OOS audit implementation for frozen experiment RSR_001.

This module never imports scientific functions from ``scripts/rsr_001.py``.
Its default/research path crops prices before the OOS boundary before computing
returns, residuals, signals, or targets. OOS access is explicit in callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


UNIVERSE: tuple[str, ...] = (
    "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"
)
MARKET = "SPY"
RESEARCH_START = pd.Timestamp("2001-02-28")
RESEARCH_END = pd.Timestamp("2018-10-31")
RESEARCH_TARGET_END = pd.Timestamp("2018-11-30")
QUARANTINE_START = pd.Timestamp("2018-11-30")
QUARANTINE_END = pd.Timestamp("2019-02-28")
OOS_START = pd.Timestamp("2019-03-29")
OOS_LITERAL_END = pd.Timestamp("2026-07-31")
OOS_SPEC_END = pd.Timestamp("2026-06-30")
N_PERM = 5_000
SEED = 7


@dataclass(frozen=True)
class PanelConfig:
    """Parameters for one fully specified audit panel."""

    estimation_window: int = 252
    signal_window: int = 21
    proxy: str = "SPY"
    top_bottom: int = 3
    cost_bps: int = 10
    require_complete_target: bool = True


def load_prices(path: Path, end: pd.Timestamp | None = None) -> pd.DataFrame:
    """Load the frozen adjusted-close snapshot, optionally cropping first."""

    prices = pd.read_csv(path, index_col=0, parse_dates=True)
    prices.index = pd.DatetimeIndex(prices.index)
    prices = prices.sort_index()
    if end is not None:
        prices = prices.loc[:end].copy()
    validate_prices(prices)
    return prices


def validate_prices(prices: pd.DataFrame) -> None:
    """Reject missing, duplicate, unordered, or timezone-bearing price data."""

    required = set(UNIVERSE) | {MARKET}
    missing_columns = sorted(required - set(prices.columns))
    if missing_columns:
        raise ValueError(f"missing price columns: {missing_columns}")
    if prices.index.has_duplicates:
        raise ValueError("price index contains duplicates")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("price index is not ordered")
    if prices.index.tz is not None:
        raise ValueError("daily adjusted-close index must be timezone-naive")
    if prices[list(required)].isna().any().any():
        raise ValueError("price snapshot contains NaN values")


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate one-day log returns without backfill."""

    returns = np.log(prices / prices.shift(1)).dropna(how="any")
    if returns.index.has_duplicates or not returns.index.is_monotonic_increasing:
        raise ValueError("invalid return index")
    return returns


def proxy_returns(returns: pd.DataFrame, proxy: str) -> pd.Series:
    """Return SPY or the frozen equal-weight nine-sector proxy."""

    if proxy == "SPY":
        return returns[MARKET].rename("market")
    if proxy == "EQUAL_WEIGHT_9":
        return returns.loc[:, list(UNIVERSE)].mean(axis=1).rename("market")
    raise ValueError(f"unsupported proxy: {proxy}")


def point_in_time_residuals(
    returns: pd.DataFrame,
    market: pd.Series,
    window: int,
) -> pd.DataFrame:
    """Compute residual at d from OLS fitted on exactly [d-window, d-1]."""

    if window <= 1:
        raise ValueError("estimation window must exceed one observation")
    market_variance = market.rolling(window).var().shift(1)
    market_mean = market.rolling(window).mean().shift(1)
    residuals: dict[str, pd.Series] = {}
    for ticker in UNIVERSE:
        beta = (
            returns[ticker].rolling(window).cov(market).shift(1)
            / market_variance
        )
        alpha = returns[ticker].rolling(window).mean().shift(1) - beta * market_mean
        residuals[ticker] = returns[ticker] - alpha - beta * market
    return pd.DataFrame(residuals, index=returns.index)


def spearman_rank_correlation(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman correlation using average ranks, including ties."""

    left = pd.Series(np.asarray(x, dtype=float)).rank(method="average")
    right = pd.Series(np.asarray(y, dtype=float)).rank(method="average")
    return float(left.corr(right))


def _monthly_ends(index: pd.DatetimeIndex) -> list[pd.Timestamp]:
    frame = pd.Series(index=index, data=index)
    return [pd.Timestamp(value) for value in frame.groupby(index.to_period("M")).last()]


def target_month_is_confirmed_complete(
    signal_date: pd.Timestamp,
    snapshot_end: pd.Timestamp,
) -> bool:
    """Confirm target completion by requiring an observation in a later month."""

    target_period = signal_date.to_period("M") + 1
    return target_period < snapshot_end.to_period("M")


def build_panel(prices: pd.DataFrame, config: PanelConfig) -> pd.DataFrame:
    """Build monthly signal/target observations from the supplied snapshot."""

    returns = log_returns(prices)
    market = proxy_returns(returns, config.proxy)
    residuals = point_in_time_residuals(returns, market, config.estimation_window)
    signal = -residuals.rolling(config.signal_window).sum()
    month_ends = _monthly_ends(returns.index)
    snapshot_end = pd.Timestamp(returns.index.max())
    rows: list[dict[str, float | pd.Timestamp | bool]] = []

    for signal_date, observed_target_end in zip(month_ends, month_ends[1:]):
        if observed_target_end.to_period("M") != signal_date.to_period("M") + 1:
            continue
        complete = target_month_is_confirmed_complete(signal_date, snapshot_end)
        if config.require_complete_target and not complete:
            continue
        x = signal.loc[signal_date]
        if x.isna().any():
            continue
        future_log = returns.loc[signal_date:observed_target_end, list(UNIVERSE)].iloc[1:].sum()
        future_simple = np.expm1(future_log)
        long_names = x.nlargest(config.top_bottom).index
        short_names = x.nsmallest(config.top_bottom).index
        weights = pd.Series(0.0, index=UNIVERSE)
        weights.loc[long_names] = 1.0 / config.top_bottom
        weights.loc[short_names] = -1.0 / config.top_bottom
        row: dict[str, float | pd.Timestamp | bool] = {
            "data": signal_date,
            "target_end": observed_target_end,
            "target_complete": complete,
            "ic": spearman_rank_correlation(x, future_log),
            "spread": float(weights @ future_log),
            "simple_spread": float(weights @ future_simple),
        }
        row.update({f"w_{ticker}": float(weights[ticker]) for ticker in UNIVERSE})
        row.update({f"x_{ticker}": float(x[ticker]) for ticker in UNIVERSE})
        row.update({f"y_{ticker}": float(future_log[ticker]) for ticker in UNIVERSE})
        rows.append(row)

    panel = pd.DataFrame(rows).set_index("data").sort_index()
    weight_columns = [f"w_{ticker}" for ticker in UNIVERSE]
    panel["turnover"] = panel[weight_columns].diff().abs().sum(axis=1)
    panel.loc[panel.index[0], "turnover"] = panel.loc[panel.index[0], weight_columns].abs().sum()
    panel["custo"] = config.cost_bps / 10_000 * panel["turnover"]
    panel["liquido"] = panel["spread"] - panel["custo"]
    panel["simple_liquido"] = panel["simple_spread"] - panel["custo"]
    return panel


def research_panel(prices: pd.DataFrame, config: PanelConfig) -> pd.DataFrame:
    """Build research only after physically cropping all post-target rows."""

    cropped = prices.loc[:RESEARCH_TARGET_END].copy()
    panel = build_panel(cropped, config)
    return panel.loc[RESEARCH_START:RESEARCH_END].copy()


def extract_signal_target(panel: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Extract aligned signal and future-return matrices from an audit panel."""

    x = panel[[f"x_{ticker}" for ticker in UNIVERSE]].to_numpy(dtype=float)
    y = panel[[f"y_{ticker}" for ticker in UNIVERSE]].to_numpy(dtype=float)
    return x, y


def _normalized_row_ranks(values: np.ndarray) -> np.ndarray:
    ranks = pd.DataFrame(values).rank(axis=1, method="average").to_numpy(dtype=float)
    ranks -= ranks.mean(axis=1, keepdims=True)
    norms = np.sqrt((ranks * ranks).sum(axis=1, keepdims=True))
    return np.divide(ranks, norms, out=np.zeros_like(ranks), where=norms != 0)


def mean_spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Mean row-wise Spearman correlation with average-rank tie handling."""

    rx = _normalized_row_ranks(np.asarray(x, dtype=float))
    ry = _normalized_row_ranks(np.asarray(y, dtype=float))
    return float((rx * ry).sum(axis=1).mean())


def permutation_placebos(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = N_PERM,
    seed: int = SEED,
) -> dict[str, float]:
    """Run deterministic one-sided P1/P2 with the pre-registered estimator."""

    raw_x = np.asarray(x, dtype=float)
    raw_y = np.asarray(y, dtype=float)

    def frozen_mean_ic(left: np.ndarray, right: np.ndarray) -> float:
        # Preserve the frozen evaluation order exactly. The public script uses
        # double argsort ranks; actual RSR_001 rows have no ties. The separate
        # mean_spearman API remains the specification-level, tie-aware check.
        rank_left = np.argsort(np.argsort(left, axis=1), axis=1).astype(float)
        rank_right = np.argsort(np.argsort(right, axis=1), axis=1).astype(float)
        rank_left -= rank_left.mean(axis=1, keepdims=True)
        rank_right -= rank_right.mean(axis=1, keepdims=True)
        correlations = (rank_left * rank_right).sum(axis=1) / np.sqrt(
            (rank_left * rank_left).sum(axis=1)
            * (rank_right * rank_right).sum(axis=1)
        )
        return float(correlations.mean())

    observed = frozen_mean_ic(raw_x, raw_y)

    rng = np.random.default_rng(seed)
    p1_null = np.empty(n_perm)
    for permutation in range(n_perm):
        p1_null[permutation] = frozen_mean_ic(
            rng.permuted(raw_x, axis=1), raw_y
        )

    rng = np.random.default_rng(seed)
    p2_null = np.empty(n_perm)
    for permutation in range(n_perm):
        p2_null[permutation] = frozen_mean_ic(
            raw_x, raw_y[rng.permutation(len(raw_y))]
        )

    pvalue = lambda values: (1 + int((values >= observed).sum())) / (n_perm + 1)
    return {
        "observed": observed,
        "p1": float(pvalue(p1_null)),
        "p2": float(pvalue(p2_null)),
    }


def fixed_oos_blocks(panel: pd.DataFrame) -> tuple[pd.DataFrame, ...]:
    """Preserve frozen OOS boundaries 1..30, 31..60, and 61..N."""

    if len(panel) not in {88, 89}:
        raise ValueError(f"fixed OOS blocks require n=88 or n=89, got {len(panel)}")
    return panel.iloc[:30], panel.iloc[30:60], panel.iloc[60:]


def chronological_thirds(panel: pd.DataFrame) -> tuple[pd.DataFrame, ...]:
    """Split non-OOS samples into three deterministic contiguous thirds."""

    positions = np.array_split(np.arange(len(panel)), 3)
    return tuple(panel.iloc[position] for position in positions)


def drawdowns(net_log: pd.Series) -> tuple[float, float]:
    """Return frozen additive-log and conventional equity drawdowns."""

    cumulative_log = net_log.cumsum()
    frozen = float((cumulative_log - cumulative_log.cummax()).min())
    equity = np.exp(cumulative_log)
    conventional = float((equity / equity.cummax() - 1.0).min())
    return frozen, conventional


def metrics(panel: pd.DataFrame) -> dict[str, float | int | str]:
    """Calculate scientific and economic metrics without interpretation."""

    frozen_dd, conventional_dd = drawdowns(panel["liquido"])
    net = panel["liquido"]
    simple_net = panel["simple_liquido"]
    annualized_log = float(net.mean() * 12)
    volatility = float(net.std() * np.sqrt(12))
    return {
        "n": int(len(panel)),
        "start": panel.index.min().date().isoformat(),
        "end": panel.index.max().date().isoformat(),
        "target_end": pd.Timestamp(panel["target_end"].max()).date().isoformat(),
        "mean_ic": float(panel["ic"].mean()),
        "median_ic": float(panel["ic"].median()),
        "hit_rate_ic": float((panel["ic"] > 0).mean()),
        "spread_bruto_aa_log": float(panel["spread"].mean() * 12),
        "custo_aa": float(panel["custo"].mean() * 12),
        "liquido_aa_log": annualized_log,
        "liquido_aa_composto": float(np.expm1(annualized_log)),
        "liquido_simples_cagr": float(
            np.prod(1.0 + simple_net) ** (12.0 / len(simple_net)) - 1.0
        ),
        "volatilidade_log": volatility,
        "sharpe_log": float(annualized_log / volatility),
        "turnover": float(panel["turnover"].mean()),
        "drawdown_congelado_log": frozen_dd,
        "drawdown_convencional": conventional_dd,
    }


def evaluate_frozen_gate(
    panel: pd.DataFrame,
    placebo: dict[str, float],
) -> dict[str, object]:
    """Apply the frozen gate using explicit, non-array_split OOS blocks."""

    blocks = fixed_oos_blocks(panel)
    ic_blocks = [float(block["ic"].mean()) for block in blocks]
    net_blocks = [float(block["liquido"].mean() * 12) for block in blocks]
    scientific = bool(
        panel["ic"].mean() > 0
        and placebo["p1"] < 0.10
        and placebo["p2"] < 0.10
        and sum(value > 0 for value in ic_blocks) >= 2
    )
    economic = bool(
        panel["liquido"].mean() * 12 > 0
        and sum(value > 0 for value in net_blocks) >= 2
    )
    verdict = "GO" if scientific and economic else "CONDITIONAL_GO" if scientific else "NO_GO"
    return {
        "scientific_pass": scientific,
        "economic_pass": economic,
        "ic_blocks": ic_blocks,
        "net_blocks_aa": net_blocks,
        "verdict": verdict,
    }


def holm_adjust(pvalues: Iterable[float]) -> list[float]:
    """Return Holm family-wise adjusted p-values in original order."""

    raw = np.asarray(list(pvalues), dtype=float)
    order = np.argsort(raw)
    adjusted_sorted = np.maximum.accumulate((len(raw) - np.arange(len(raw))) * raw[order])
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def assert_panel_integrity(panel: pd.DataFrame) -> None:
    """Validate NaN, duplicates, order, timestamps, and target alignment."""

    if panel.index.has_duplicates:
        raise AssertionError("monthly panel has duplicate feature dates")
    if not panel.index.is_monotonic_increasing:
        raise AssertionError("monthly panel is not ordered")
    if panel.index.tz is not None:
        raise AssertionError("monthly feature index unexpectedly has timezone")
    numeric = panel.select_dtypes(include=[np.number])
    if numeric.isna().any().any():
        raise AssertionError("monthly panel contains NaN")
    if not (pd.DatetimeIndex(panel["target_end"]) > panel.index).all():
        raise AssertionError("target must be strictly after feature date")
    expected_target_period = panel.index.to_period("M") + 1
    actual_target_period = pd.DatetimeIndex(panel["target_end"]).to_period("M")
    if not np.array_equal(expected_target_period, actual_target_period):
        raise AssertionError("target does not belong to the next calendar month")
