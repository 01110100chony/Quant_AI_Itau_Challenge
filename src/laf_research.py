"""Frozen LAF_001 Research construction, inference, and falsification gates.

This module is intentionally limited to the human-approved 2003 warm-up and
2004-2016 Research target months. It contains no acquisition, Validation,
Final OOS, portfolio, or backtest logic.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

import exchange_calendars as xcals
import numpy as np
import pandas as pd
from scipy import stats

from laf_stage_a1 import (
    PERIOD2,
    RAW_RESPONSE_SHA256,
    SYMBOLS,
    StructuralDataError,
    expected_xnys_dates,
    parse_chart_payload,
)


SPEC_VERSION = "v1.0-frozen"
WARMUP_START = date(2003, 1, 1)
RESEARCH_END = date(2016, 12, 31)
TARGET_MONTH_START = "2004-01"
TARGET_MONTH_END = "2016-12"
VALIDATION_START = date(2017, 1, 1)
LOOKBACK = 252
MONTHLY_WINDOW = 21
MIN_ELIGIBLE_ETFS = 4
MAD_SCALE = 1.4826
HAC_MAXLAGS = 3
STATE_PRIOR_MIN = 36
STATE_QUANTILE = 0.80
STATE_HIGH_MIN = 8
STATE_NORMAL_MIN = 24
INVARIANCE_TOLERANCE = 1e-12
PRIMARY_REGRESSORS = ("laf", "rv")
CONTROL_REGRESSORS = ("rv",)
STABILITY_BLOCKS = (
    ("2004-2010", 2004, 2010),
    ("2011-2016", 2011, 2016),
)


class LAFResearchError(ValueError):
    """Raised when a frozen LAF Research invariant is violated."""


@dataclass(frozen=True)
class RegressionResult:
    """OLS coefficients with frozen Bartlett HAC/t inference."""

    model: str
    n: int
    parameter_names: tuple[str, ...]
    coefficients: tuple[float, ...]
    hac_standard_errors: tuple[float, ...]
    t_statistics: tuple[float, ...]
    one_sided_p_values: tuple[float, ...]
    ci95_lower: tuple[float, ...]
    ci95_upper: tuple[float, ...]
    adjusted_r_squared: float
    df_resid: int
    hac_kernel: str = "Bartlett"
    hac_maxlags: int = HAC_MAXLAGS
    small_sample_correction: bool = True
    use_t: bool = True

    def parameter(self, name: str) -> dict[str, float]:
        """Return the inference fields for one named parameter."""
        index = self.parameter_names.index(name)
        return {
            "coefficient": self.coefficients[index],
            "hac_standard_error": self.hac_standard_errors[index],
            "t_statistic": self.t_statistics[index],
            "one_sided_p_value": self.one_sided_p_values[index],
            "ci95_lower": self.ci95_lower[index],
            "ci95_upper": self.ci95_upper[index],
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize without changing numerical values."""
        return asdict(self)


@dataclass(frozen=True)
class ConstructionBundle:
    """Frozen daily/monthly features, targets, and complete Research sample."""

    daily: pd.DataFrame
    monthly_features: pd.DataFrame
    monthly_targets: pd.DataFrame
    research_sample: pd.DataFrame
    boundary_audit: dict[str, Any]


def sha256_file(path: Path) -> str:
    """Return SHA-256 for one immutable input file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yahoo_research(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Load and hash-check exactly five Yahoo raws bounded before 2017."""
    frames: dict[str, pd.DataFrame] = {}
    for symbol in SYMBOLS:
        path = raw_dir / f"{symbol}_response.json"
        observed = sha256_file(path)
        if observed != RAW_RESPONSE_SHA256[symbol]:
            raise LAFResearchError(f"raw hash mismatch for {symbol}")
        try:
            parsed = parse_chart_payload(path.read_bytes(), symbol)
        except StructuralDataError as exc:
            raise LAFResearchError(str(exc)) from exc
        frame = parsed.rows.copy()
        if (frame["source_timestamp"] >= PERIOD2).any():
            raise LAFResearchError(f"{symbol} contains an OHLCV row from 2017+")
        if not parsed.actions.empty and (
            parsed.actions["source_timestamp"] >= PERIOD2
        ).any():
            raise LAFResearchError(f"{symbol} contains a corporate action from 2017+")
        frames[symbol] = frame
    if tuple(frames) != SYMBOLS:
        raise LAFResearchError("Yahoo universe differs from the frozen five ETFs")
    return frames


def load_split_table(path: Path) -> pd.DataFrame:
    """Load only symbol/date/type from the already-audited A1c action table."""
    frame = pd.read_csv(path, usecols=["symbol", "session_date", "action_type"])
    frame["session_date"] = pd.to_datetime(frame["session_date"], errors="raise").dt.date
    splits = frame.loc[frame["action_type"] == "STOCK_SPLIT"].copy()
    expected = [("IWM", date(2005, 6, 9))]
    observed = list(splits.loc[:, ["symbol", "session_date"]].itertuples(index=False, name=None))
    if observed != expected:
        raise LAFResearchError(f"audited split table changed: {observed}")
    return splits.reset_index(drop=True)


def validate_daily_inputs(frames: Mapping[str, pd.DataFrame]) -> list[date]:
    """Validate calendar, duplicates, ordering, fields, and the closed boundary."""
    if tuple(frames) != SYMBOLS:
        raise LAFResearchError("input universe/order differs from frozen universe")
    expected_dates = expected_xnys_dates()
    for symbol, source in frames.items():
        frame = source.sort_values("session_date", kind="stable")
        if frame["session_date"].duplicated().any():
            raise LAFResearchError(f"{symbol} has duplicate session dates")
        if frame["session_date"].tolist() != expected_dates:
            raise LAFResearchError(f"{symbol} differs from the fixed XNYS calendar")
        if max(frame["session_date"]) >= VALIDATION_START:
            raise LAFResearchError(f"{symbol} loaded a closed 2017+ session")
        required = ["open", "low", "close", "adj_close", "volume"]
        numeric = frame.loc[:, required].apply(pd.to_numeric, errors="raise")
        if numeric.isna().any().any():
            raise LAFResearchError(f"{symbol} has null canonical inputs")
        if (~np.isfinite(numeric.to_numpy(dtype=float))).any() or (numeric <= 0).any().any():
            raise LAFResearchError(f"{symbol} has nonpositive/nonfinite canonical inputs")
    return expected_dates


def _rolling_robust_z(x: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    prior = x.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK)
    median = prior.median()
    mad = prior.apply(
        lambda values: float(np.median(np.abs(values - np.median(values)))), raw=True
    )
    valid = x.notna() & median.notna() & mad.notna() & (mad > 0)
    z = pd.Series(np.nan, index=x.index, dtype=float)
    z.loc[valid] = (x.loc[valid] - median.loc[valid]) / (MAD_SCALE * mad.loc[valid])
    return median, mad, z


def split_embargo_dates(
    sessions: Sequence[date], splits: pd.DataFrame
) -> dict[str, set[date]]:
    """Return split day plus sessions whose prior 252-window crosses regimes."""
    session_list = list(sessions)
    output = {symbol: set() for symbol in SYMBOLS}
    for row in splits.itertuples(index=False):
        split_date = row.session_date
        try:
            position = session_list.index(split_date)
        except ValueError as exc:
            raise LAFResearchError("split date is absent from common XNYS sessions") from exc
        end = min(position + LOOKBACK, len(session_list))
        output[row.symbol].update(session_list[position:end])
    return output


def construct_daily_features(
    frames: Mapping[str, pd.DataFrame], splits: pd.DataFrame
) -> pd.DataFrame:
    """Construct point-in-time daily z scores and the median five-ETF aggregate."""
    sessions = validate_daily_inputs(frames)
    embargo = split_embargo_dates(sessions, splits)
    output = pd.DataFrame({"session_date": sessions})
    for symbol in SYMBOLS:
        frame = frames[symbol].sort_values("session_date", kind="stable").reset_index(drop=True)
        adjusted = frame["adj_close"].astype(float)
        returns = np.log(adjusted / adjusted.shift(1))
        monetary_volume_proxy = frame["close"].astype(float) * frame["volume"].astype(float)
        pi = returns.abs() / monetary_volume_proxy
        valid_pi = (pi > 0) & (monetary_volume_proxy > 0) & np.isfinite(pi)
        x = pd.Series(np.nan, index=frame.index, dtype=float)
        x.loc[valid_pi] = np.log(pi.loc[valid_pi])
        rolling_median, rolling_mad, z = _rolling_robust_z(x)
        eligible = z.notna() & ~frame["session_date"].isin(embargo[symbol])
        output[f"r_{symbol}"] = returns
        output[f"x_{symbol}"] = x
        output[f"median_{symbol}"] = rolling_median
        output[f"mad_{symbol}"] = rolling_mad
        output[f"z_{symbol}"] = z
        output[f"eligible_{symbol}"] = eligible

    z_values = output.loc[:, [f"z_{symbol}" for symbol in SYMBOLS]].copy()
    for symbol in SYMBOLS:
        z_values.loc[~output[f"eligible_{symbol}"], f"z_{symbol}"] = np.nan
    output["eligible_etf_count"] = z_values.notna().sum(axis=1)
    output["A_d"] = z_values.median(axis=1, skipna=True)
    output.loc[output["eligible_etf_count"] < MIN_ELIGIBLE_ETFS, "A_d"] = np.nan
    return output


def construct_monthly_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Construct the unique 21-common-session LAF and contemporaneous SPY RV."""
    calendar = xcals.get_calendar("XNYS", start=WARMUP_START, end=RESEARCH_END)
    daily = daily.copy()
    daily["session_month"] = pd.PeriodIndex(daily["session_date"], freq="M")
    rows: list[dict[str, Any]] = []
    for target_month in pd.period_range(TARGET_MONTH_START, TARGET_MONTH_END, freq="M"):
        feature_month = target_month - 1
        window = daily.loc[daily["session_month"] == feature_month].tail(MONTHLY_WINDOW)
        row: dict[str, Any] = {
            "feature_month": str(feature_month),
            "target_month": str(target_month),
            "feature_window_session_count": len(window),
            "feature_window_complete": False,
            "feature_window_start": None,
            "feature_window_end": None,
            "feature_timestamp": None,
            "execution_timestamp": None,
            "laf": np.nan,
            "rv": np.nan,
        }
        if len(window) == MONTHLY_WINDOW:
            first_date = window.iloc[0]["session_date"]
            last_date = window.iloc[-1]["session_date"]
            target_sessions = daily.loc[daily["session_month"] == target_month, "session_date"]
            if target_sessions.empty:
                raise LAFResearchError(f"target month {target_month} has no Research sessions")
            execution_date = target_sessions.iloc[0]
            feature_close = calendar.session_close(pd.Timestamp(last_date))
            execution_open = calendar.session_open(pd.Timestamp(execution_date))
            if not feature_close < execution_open:
                raise LAFResearchError("feature timestamp is not strictly before execution")
            values_complete = window["A_d"].notna().all() and window["r_SPY"].notna().all()
            row.update(
                {
                    "feature_window_complete": bool(values_complete),
                    "feature_window_start": first_date,
                    "feature_window_end": last_date,
                    "feature_timestamp": feature_close,
                    "execution_timestamp": execution_open,
                }
            )
            if values_complete:
                row["laf"] = float(window["A_d"].mean())
                row["rv"] = float(np.sqrt(np.square(window["r_SPY"]).sum()))
        rows.append(row)
    return pd.DataFrame(rows)


def construct_monthly_targets(spy: pd.DataFrame) -> pd.DataFrame:
    """Construct SPY first-open to adjusted-low monthly TailLoss in Research only."""
    frame = spy.sort_values("session_date", kind="stable").copy()
    if max(frame["session_date"]) >= VALIDATION_START:
        raise LAFResearchError("target constructor received a closed 2017+ row")
    factor = frame["adj_close"].astype(float) / frame["close"].astype(float)
    frame["adj_open"] = frame["open"].astype(float) * factor
    frame["adj_low"] = frame["low"].astype(float) * factor
    frame["target_month"] = pd.PeriodIndex(frame["session_date"], freq="M")
    rows: list[dict[str, Any]] = []
    for target_month in pd.period_range(TARGET_MONTH_START, TARGET_MONTH_END, freq="M"):
        month = frame.loc[frame["target_month"] == target_month]
        if month.empty:
            raise LAFResearchError(f"target month {target_month} has no SPY rows")
        entry = float(month.iloc[0]["adj_open"])
        log_low_to_entry = np.log(month["adj_low"].astype(float) / entry)
        tail_loss = max(0.0, -float(log_low_to_entry.min()))
        rows.append(
            {
                "target_month": str(target_month),
                "target_first_session": month.iloc[0]["session_date"],
                "target_last_session": month.iloc[-1]["session_date"],
                "target_session_count": len(month),
                "tail_loss": tail_loss,
            }
        )
    return pd.DataFrame(rows)


def attach_expanding_state(sample: pd.DataFrame) -> pd.DataFrame:
    """Classify LAF high states with an expanding prior-only Q80 threshold."""
    output = sample.sort_values("target_month", kind="stable").reset_index(drop=True).copy()
    thresholds: list[float] = []
    states: list[str | None] = []
    prior_counts: list[int] = []
    for index, row in output.iterrows():
        prior = output.loc[: index - 1, "laf"].dropna() if index else pd.Series(dtype=float)
        prior_counts.append(len(prior))
        if len(prior) < STATE_PRIOR_MIN or pd.isna(row["laf"]):
            thresholds.append(np.nan)
            states.append(None)
            continue
        threshold = float(prior.quantile(STATE_QUANTILE))
        thresholds.append(threshold)
        states.append("HIGH" if float(row["laf"]) > threshold else "NORMAL")
    output["state_prior_month_count"] = prior_counts
    output["laf_prior_q80"] = thresholds
    output["laf_state"] = states
    return output


def construct_bundle(
    frames: Mapping[str, pd.DataFrame], splits: pd.DataFrame
) -> ConstructionBundle:
    """Build frozen Research features and targets without fitting an association."""
    daily = construct_daily_features(frames, splits)
    monthly_features = construct_monthly_features(daily)
    monthly_targets = construct_monthly_targets(frames["SPY"])
    sample = monthly_features.merge(
        monthly_targets, on="target_month", how="inner", validate="one_to_one"
    )
    sample = attach_expanding_state(sample)
    complete = sample.loc[:, ["laf", "rv", "tail_loss"]].notna().all(axis=1)
    sample["primary_complete_case"] = complete
    if len(sample) != 156:
        raise LAFResearchError("Research target-month grid must contain 156 months")
    if sample["target_month"].max() != TARGET_MONTH_END:
        raise LAFResearchError("Research target grid does not end at 2016-12")
    boundary = {
        "symbols": list(SYMBOLS),
        "daily_rows_per_symbol": {symbol: len(frames[symbol]) for symbol in SYMBOLS},
        "max_session_date": max(daily["session_date"]).isoformat(),
        "historical_rows_2017_or_later": sum(
            int((frame["session_date"] >= VALIDATION_START).sum()) for frame in frames.values()
        ),
        "target_months": len(sample),
        "primary_complete_cases": int(complete.sum()),
        "laf_available_months": int(sample["laf"].notna().sum()),
        "rv_available_months": int(sample["rv"].notna().sum()),
        "target_available_months": int(sample["tail_loss"].notna().sum()),
        "complete_cases_2004_2010": int(
            (complete & sample["target_month"].str[:4].astype(int).between(2004, 2010)).sum()
        ),
        "complete_cases_2011_2016": int(
            (complete & sample["target_month"].str[:4].astype(int).between(2011, 2016)).sum()
        ),
        "state_classified_complete_cases": int(
            (complete & sample["laf_state"].notna()).sum()
        ),
        "daily_duplicate_dates": int(daily["session_date"].duplicated().sum()),
        "feature_before_execution": bool(
            monthly_features.dropna(subset=["feature_timestamp", "execution_timestamp"])
            .apply(lambda row: row["feature_timestamp"] < row["execution_timestamp"], axis=1)
            .all()
        ),
        "validation_loaded": False,
        "final_oos_loaded": False,
    }
    if boundary["historical_rows_2017_or_later"] != 0:
        raise LAFResearchError("closed rows reached the construction bundle")
    return ConstructionBundle(daily, monthly_features, monthly_targets, sample, boundary)


def _scaled_pre_split_frames(
    frames: Mapping[str, pd.DataFrame], *, close_scale: float, volume_scale: float
) -> dict[str, pd.DataFrame]:
    if close_scale <= 0 or volume_scale <= 0:
        raise LAFResearchError("scale factors must be positive")
    copied = {symbol: frame.copy(deep=True) for symbol, frame in frames.items()}
    mask = copied["IWM"]["session_date"] < date(2005, 6, 9)
    copied["IWM"].loc[mask, "close"] *= close_scale
    copied["IWM"].loc[mask, "volume"] *= volume_scale
    return copied


def scale_invariance_audit(
    frames: Mapping[str, pd.DataFrame], splits: pd.DataFrame
) -> dict[str, Any]:
    """Falsify LAF sensitivity to positive pre-split Close/Volume scale changes."""
    baseline_daily = construct_daily_features(frames, splits)
    baseline_monthly = construct_monthly_features(baseline_daily)
    sessions = baseline_daily["session_date"].tolist()
    embargo = split_embargo_dates(sessions, splits)["IWM"]
    outside_daily = ~baseline_daily["session_date"].isin(embargo)
    embargo_start = min(embargo)
    embargo_end = max(embargo)
    outside_monthly = (
        (baseline_monthly["feature_window_end"] < embargo_start)
        | (baseline_monthly["feature_window_start"] > embargo_end)
    ).fillna(False)
    scenarios = (
        (0.5, 1.0),
        (2.0, 1.0),
        (1.0, 0.5),
        (1.0, 2.0),
        (0.5, 2.0),
        (2.0, 0.5),
    )
    results: list[dict[str, Any]] = []
    for close_scale, volume_scale in scenarios:
        scaled = _scaled_pre_split_frames(
            frames, close_scale=close_scale, volume_scale=volume_scale
        )
        changed_daily = construct_daily_features(scaled, splits)
        changed_monthly = construct_monthly_features(changed_daily)
        daily_diff = (
            baseline_daily.loc[outside_daily, "A_d"]
            - changed_daily.loc[outside_daily, "A_d"]
        ).abs()
        monthly_diff = (
            baseline_monthly.loc[outside_monthly, "laf"]
            - changed_monthly.loc[outside_monthly, "laf"]
        ).abs()
        max_daily = float(daily_diff.dropna().max()) if daily_diff.notna().any() else 0.0
        max_monthly = (
            float(monthly_diff.dropna().max()) if monthly_diff.notna().any() else 0.0
        )
        results.append(
            {
                "close_scale": close_scale,
                "volume_scale": volume_scale,
                "max_abs_daily_difference": max_daily,
                "max_abs_monthly_difference": max_monthly,
                "pass": max_daily <= INVARIANCE_TOLERANCE
                and max_monthly <= INVARIANCE_TOLERANCE,
            }
        )
    passed = all(item["pass"] for item in results)
    return {
        "tolerance": INVARIANCE_TOLERANCE,
        "embargo_start": embargo_start.isoformat(),
        "embargo_end": embargo_end.isoformat(),
        "outside_embargo_daily_rows": int(outside_daily.sum()),
        "outside_embargo_months": int(outside_monthly.sum()),
        "scenarios": results,
        "pass": passed,
    }


def target_independence_audit(
    frames: Mapping[str, pd.DataFrame], splits: pd.DataFrame
) -> dict[str, Any]:
    """Alter target-only SPY fields and require bitwise-identical features."""
    baseline = construct_daily_features(frames, splits)
    changed = {symbol: frame.copy(deep=True) for symbol, frame in frames.items()}
    changed["SPY"]["low"] = changed["SPY"]["low"].astype(float) * 0.5
    changed_daily = construct_daily_features(changed, splits)
    feature_columns = [
        column
        for column in baseline.columns
        if column == "A_d" or column.startswith(("r_", "x_", "median_", "mad_", "z_", "eligible_"))
    ]
    identical = baseline.loc[:, feature_columns].equals(changed_daily.loc[:, feature_columns])
    return {"altered_fields": ["SPY.low"], "features_exactly_equal": identical, "pass": identical}


def fit_hac_ols(
    frame: pd.DataFrame,
    *,
    target: str,
    regressors: Sequence[str],
    model: str,
    maxlags: int = HAC_MAXLAGS,
) -> RegressionResult:
    """Fit the frozen intercept OLS with Bartlett HAC(3), correction, and t inference."""
    columns = [target, *regressors]
    clean = frame.loc[:, columns].dropna()
    if len(clean) != len(frame):
        raise LAFResearchError(f"{model} received incomplete rows")
    if len(clean) <= len(regressors) + 1 or maxlags < 0 or maxlags >= len(clean):
        raise LAFResearchError(f"{model} has insufficient rows or invalid maxlags")
    y = clean[target].to_numpy(dtype=float)
    x_raw = clean.loc[:, regressors].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(clean)), x_raw])
    names = ("intercept", *tuple(regressors))
    coefficients, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise LAFResearchError(f"{model} design matrix is rank deficient")
    residuals = y - x @ coefficients
    bread = np.linalg.inv(x.T @ x)
    score = x * residuals[:, None]
    meat = score.T @ score
    for lag in range(1, maxlags + 1):
        weight = 1.0 - lag / (maxlags + 1.0)
        cross = score[lag:].T @ score[:-lag]
        meat += weight * (cross + cross.T)
    n, k = x.shape
    covariance = (n / (n - k)) * bread @ meat @ bread
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_statistics = coefficients / standard_errors
    df_resid = n - k
    one_sided = stats.t.sf(t_statistics, df=df_resid)
    critical = stats.t.ppf(0.975, df=df_resid)
    total = float(np.sum((y - y.mean()) ** 2))
    residual_sum = float(residuals @ residuals)
    r_squared = 1.0 - residual_sum / total if total > 0 else np.nan
    adjusted = 1.0 - (1.0 - r_squared) * (n - 1) / df_resid if total > 0 else np.nan
    return RegressionResult(
        model=model,
        n=n,
        parameter_names=names,
        coefficients=tuple(float(value) for value in coefficients),
        hac_standard_errors=tuple(float(value) for value in standard_errors),
        t_statistics=tuple(float(value) for value in t_statistics),
        one_sided_p_values=tuple(float(value) for value in one_sided),
        ci95_lower=tuple(float(value) for value in coefficients - critical * standard_errors),
        ci95_upper=tuple(float(value) for value in coefficients + critical * standard_errors),
        adjusted_r_squared=float(adjusted),
        df_resid=df_resid,
        hac_maxlags=maxlags,
    )


def execute_frozen_models(sample: pd.DataFrame) -> dict[str, Any]:
    """Execute only the frozen primary/control models, blocks, state test, and gates."""
    complete = sample.loc[sample["primary_complete_case"]].copy()
    full = fit_hac_ols(
        complete,
        target="tail_loss",
        regressors=PRIMARY_REGRESSORS,
        model="FULL_LAF_RV",
    )
    control = fit_hac_ols(
        complete,
        target="tail_loss",
        regressors=CONTROL_REGRESSORS,
        model="RV_ONLY",
    )
    blocks: list[dict[str, Any]] = []
    for label, first_year, last_year in STABILITY_BLOCKS:
        years = complete["target_month"].str[:4].astype(int)
        block_sample = complete.loc[years.between(first_year, last_year)]
        if len(block_sample) <= len(PRIMARY_REGRESSORS) + 1:
            blocks.append(
                {
                    "block": label,
                    "n": len(block_sample),
                    "estimable": False,
                    "result": None,
                    "beta_laf_positive": False,
                }
            )
            continue
        result = fit_hac_ols(
            block_sample,
            target="tail_loss",
            regressors=PRIMARY_REGRESSORS,
            model=f"FULL_{label}",
        )
        blocks.append(
            {
                "block": label,
                "n": len(block_sample),
                "estimable": True,
                "result": result,
                "beta_laf_positive": result.parameter("laf")["coefficient"] > 0,
            }
        )

    state_sample = complete.dropna(subset=["laf_state"]).copy()
    high = state_sample.loc[state_sample["laf_state"] == "HIGH", "tail_loss"]
    normal = state_sample.loc[state_sample["laf_state"] == "NORMAL", "tail_loss"]
    high_mean = float(high.mean()) if len(high) else None
    normal_mean = float(normal.mean()) if len(normal) else None
    state = {
        "high_count": len(high),
        "normal_count": len(normal),
        "high_mean_tail_loss": high_mean,
        "normal_mean_tail_loss": normal_mean,
        "high_minus_normal": (
            high_mean - normal_mean
            if high_mean is not None and normal_mean is not None
            else None
        ),
    }
    laf = full.parameter("laf")
    core_pass = laf["coefficient"] > 0 and laf["one_sided_p_value"] < 0.10
    incremental_pass = full.adjusted_r_squared > control.adjusted_r_squared
    stability_pass = all(item["beta_laf_positive"] for item in blocks)
    state_pass = (
        state["high_count"] >= STATE_HIGH_MIN
        and state["normal_count"] >= STATE_NORMAL_MIN
        and high_mean is not None
        and normal_mean is not None
        and state["high_mean_tail_loss"] > state["normal_mean_tail_loss"]
    )
    if core_pass and incremental_pass and stability_pass and state_pass:
        verdict = "GO"
    elif core_pass and incremental_pass and (stability_pass != state_pass):
        verdict = "CONDITIONAL_GO"
    else:
        verdict = "NO_GO"
    gates = {
        "CorePass": core_pass,
        "IncrementalPass": incremental_pass,
        "StabilityPass": stability_pass,
        "StatePass": state_pass,
        "verdict": verdict,
    }
    return {
        "full": full,
        "control": control,
        "blocks": blocks,
        "state": state,
        "gates": gates,
        "complete_sample": complete,
    }


def json_default(value: Any) -> Any:
    """Serialize dates, timestamps, NumPy scalars, and regression results."""
    if isinstance(value, RegressionResult):
        return value.to_dict()
    if isinstance(value, (date, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def write_json(path: Path, value: Any) -> None:
    """Write deterministic UTF-8 JSON."""
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=json_default) + "\n",
        encoding="utf-8",
    )
