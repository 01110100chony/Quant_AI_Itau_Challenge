"""Frozen CM_001 Stage B estimators, placebos, and Research-sample construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy import stats


RESEARCH_START = date(2010, 1, 1)
RESEARCH_END = date(2018, 12, 31)
EXPECTED_COUNTS = {"H1": 1_938, "H2": 2_034, "H3": 1_850}
HAC_MAXLAGS = 5
PERMUTATIONS = 5_000
RNG_SEED = 7
BLOCKS = (
    ("2010-2012", date(2010, 1, 1), date(2012, 12, 31)),
    ("2013-2015", date(2013, 1, 1), date(2015, 12, 31)),
    ("2016-2018", date(2016, 1, 1), date(2018, 12, 31)),
)


@dataclass(frozen=True)
class RegressionResult:
    """Frozen OLS/HAC output for one model."""

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
    semi_specific_effect_1sd_bps: float
    df_resid: int
    hac_kernel: str = "Bartlett"
    hac_maxlags: int = HAC_MAXLAGS
    small_sample_correction: bool = True
    use_t: bool = True

    def parameter(self, name: str) -> dict[str, float]:
        """Return one parameter and its frozen inference fields."""
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
        """Serialize the result without changing numerical values."""
        return asdict(self)


@dataclass(frozen=True)
class SampleBundle:
    """Frozen primary and robustness samples."""

    primary: Mapping[str, pd.DataFrame]
    robustness_0050: Mapping[str, pd.DataFrame]
    eligible_window_table: pd.DataFrame


def assert_research_dates(values: pd.Series, *, label: str) -> None:
    """Reject any date outside the frozen Research sample."""
    parsed = pd.to_datetime(values, errors="raise").dt.date
    if parsed.empty:
        return
    if parsed.min() < RESEARCH_START or parsed.max() > RESEARCH_END:
        raise ValueError(f"{label} crosses frozen Research boundaries")


def verify_mechanical_counts(flags_path: Path) -> dict[str, int]:
    """Verify the frozen counts without loading prices or computing associations."""
    flags = pd.read_csv(flags_path)
    assert_research_dates(flags["session_date"], label="mechanical flags")
    actual = {
        "H1": int(_as_bool(flags["h1_usable_under_candidate_policy"]).sum()),
        "H2": int(_as_bool(flags["h2_usable_under_candidate_policy"]).sum()),
        "H3": int(_as_bool(flags["h3_usable_under_candidate_policy"]).sum()),
    }
    if actual != EXPECTED_COUNTS:
        raise ValueError(f"mechanical count divergence: expected {EXPECTED_COUNTS}, got {actual}")
    return actual


def map_next_eligible_windows(eligible_dates: pd.Series) -> pd.DataFrame:
    """Map each eligible Taiwan window to the next eligible window by date."""
    dates = pd.to_datetime(eligible_dates, errors="raise").dt.date
    assert_research_dates(pd.Series(dates), label="eligible window dates")
    if dates.duplicated().any():
        raise ValueError("eligible window dates are not unique")
    ordered = pd.DataFrame({"target_session": dates}).sort_values(
        "target_session"
    ).reset_index(drop=True)
    ordered["future_window_date"] = ordered["target_session"].shift(-1)
    complete = ordered.dropna(subset=["future_window_date"])
    if not (complete["future_window_date"] > complete["target_session"]).all():
        raise ValueError("P2 future window is not strictly later than target")
    return ordered


def mechanical_p2_common_count(mapping_path: Path, flags_path: Path) -> dict[str, Any]:
    """Count P2 common-complete sessions without loading price values."""
    mapping = pd.read_csv(mapping_path)
    flags = pd.read_csv(flags_path)
    assert_research_dates(mapping["target_session"], label="P2 mechanical mapping")
    assert_research_dates(flags["session_date"], label="P2 mechanical flags")
    eligible = mapping.loc[mapping["mapping_status"].eq("VALID"), "target_session"]
    future_map = map_next_eligible_windows(eligible)
    h2_dates = pd.to_datetime(
        flags.loc[_as_bool(flags["h2_usable_under_candidate_policy"]), "session_date"]
    ).dt.date
    common = future_map.loc[
        future_map["target_session"].isin(h2_dates)
        & future_map["future_window_date"].notna()
    ].copy()
    return {
        "eligible_windows": len(future_map),
        "h2_current_complete": len(h2_dates),
        "p2_common_complete": len(common),
        "last_eligible_without_lead": int(future_map["future_window_date"].isna().sum()),
    }


def frozen_hac_ols(
    frame: pd.DataFrame,
    *,
    target: str,
    regressors: Sequence[str],
    model: str,
    maxlags: int = HAC_MAXLAGS,
) -> RegressionResult:
    """Estimate intercept OLS with Bartlett Newey-West HAC and t inference."""
    columns = [target, *regressors]
    clean = frame.loc[:, columns].dropna()
    if len(clean) != len(frame):
        raise ValueError(f"{model} received incomplete rows")
    if len(clean) <= len(regressors) + 1:
        raise ValueError(f"{model} has insufficient observations")
    if maxlags < 0 or maxlags >= len(clean):
        raise ValueError(f"{model} has invalid HAC maxlags={maxlags}")

    y = clean[target].to_numpy(dtype=float)
    x_raw = clean.loc[:, regressors].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(clean)), x_raw])
    names = ("intercept", *tuple(regressors))
    coefficients, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError(f"{model} design matrix is rank deficient")
    residuals = y - x @ coefficients
    bread = np.linalg.inv(x.T @ x)
    score = x * residuals[:, None]
    meat = score.T @ score
    for lag in range(1, maxlags + 1):
        weight = 1.0 - lag / (maxlags + 1.0)
        cross = score[lag:].T @ score[:-lag]
        meat += weight * (cross + cross.T)
    n, k = x.shape
    correction = n / (n - k)
    covariance = correction * bread @ meat @ bread
    standard_errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        t_statistics = coefficients / standard_errors
    df_resid = n - k
    one_sided = stats.t.sf(t_statistics, df=df_resid)
    critical = stats.t.ppf(0.975, df=df_resid)
    lower = coefficients - critical * standard_errors
    upper = coefficients + critical * standard_errors
    total = float(np.sum((y - y.mean()) ** 2))
    residual_sum = float(residuals @ residuals)
    r_squared = 1.0 - residual_sum / total if total > 0 else np.nan
    adjusted = 1.0 - (1.0 - r_squared) * (n - 1) / df_resid if total > 0 else np.nan
    semi_index = names.index("semi_specific")
    semi_effect = float(
        coefficients[semi_index]
        * clean["semi_specific"].std(ddof=1)
        * 10_000.0
    )
    return RegressionResult(
        model=model,
        n=n,
        parameter_names=names,
        coefficients=tuple(float(value) for value in coefficients),
        hac_standard_errors=tuple(float(value) for value in standard_errors),
        t_statistics=tuple(float(value) for value in t_statistics),
        one_sided_p_values=tuple(float(value) for value in one_sided),
        ci95_lower=tuple(float(value) for value in lower),
        ci95_upper=tuple(float(value) for value in upper),
        adjusted_r_squared=float(adjusted),
        semi_specific_effect_1sd_bps=semi_effect,
        df_resid=df_resid,
        hac_maxlags=maxlags,
    )


def circular_shift_placebo(
    frame: pd.DataFrame,
    *,
    target: str,
    controls: Sequence[str],
    observed_beta: float,
    permutations: int = PERMUTATIONS,
    seed: int = RNG_SEED,
) -> dict[str, Any]:
    """Run the frozen circular-shift placebo on SemiSpecific only."""
    ordered = frame.sort_values("session_date").reset_index(drop=True)
    n = len(ordered)
    offsets = np.arange(21, n - 20, dtype=int)
    if offsets.size == 0:
        raise ValueError("placebo sample is too short for the frozen offset set")
    rng = np.random.default_rng(seed)
    draws = rng.choice(offsets, size=permutations, replace=True)
    y = ordered[target].to_numpy(dtype=float)
    semi = ordered["semi_specific"].to_numpy(dtype=float)
    fixed = ordered.loc[:, controls].to_numpy(dtype=float) if controls else np.empty((n, 0))
    beta_perm = np.empty(permutations, dtype=float)
    for index, offset in enumerate(draws):
        shifted = np.roll(semi, int(offset))
        design = np.column_stack([np.ones(n), shifted, fixed])
        beta_perm[index] = np.linalg.lstsq(design, y, rcond=None)[0][1]
    count_ge = int(np.count_nonzero(beta_perm >= observed_beta))
    return {
        "B": permutations,
        "seed": seed,
        "offset_min": 21,
        "offset_max": n - 21,
        "count_beta_perm_ge_observed": count_ge,
        "p_perm": float((1 + count_ge) / (permutations + 1)),
        "beta_perm": beta_perm,
    }


def build_p2_common_sample(
    h2_frame: pd.DataFrame,
    eligible_window_table: pd.DataFrame,
) -> pd.DataFrame:
    """Build P2 only after mapping the next pre-target eligible window."""
    windows = eligible_window_table[["session_date", "semi_specific"]].copy()
    windows["session_date"] = pd.to_datetime(windows["session_date"]).dt.date
    windows = windows.dropna(subset=["semi_specific"]).sort_values("session_date")
    future_map = map_next_eligible_windows(pd.Series(windows["session_date"]))
    future_values = windows.rename(
        columns={
            "session_date": "future_window_date",
            "semi_specific": "future_semi_specific",
        }
    )
    mapped = future_map.merge(
        future_values,
        on="future_window_date",
        how="left",
        validate="many_to_one",
    )
    current = h2_frame.copy()
    current["session_date"] = pd.to_datetime(current["session_date"]).dt.date
    common = current.merge(
        mapped,
        left_on="session_date",
        right_on="target_session",
        how="inner",
        validate="one_to_one",
    )
    common = common.dropna(
        subset=[
            "intraday_rel",
            "semi_specific",
            "future_semi_specific",
            "future_window_date",
        ]
    ).copy()
    if not (common["future_window_date"] > common["session_date"]).all():
        raise ValueError("P2 common sample contains non-future information")
    return common.sort_values("session_date").reset_index(drop=True)


def future_information_placebo(
    h2_frame: pd.DataFrame,
    eligible_window_table: pd.DataFrame,
) -> dict[str, Any]:
    """Estimate correct/future H2 on the canonical common-complete sample."""
    common = build_p2_common_sample(h2_frame, eligible_window_table)
    correct = frozen_hac_ols(
        common,
        target="intraday_rel",
        regressors=["semi_specific"],
        model="P2_H2_correct_common",
    )
    future_input = common.rename(
        columns={"semi_specific": "correct_semi_specific", "future_semi_specific": "semi_specific"}
    )
    future = frozen_hac_ols(
        future_input,
        target="intraday_rel",
        regressors=["semi_specific"],
        model="P2_H2_future",
    )
    future_beta = future.parameter("semi_specific")
    target_sd = float(common["intraday_rel"].std(ddof=1))
    if target_sd == 0.0:
        raise ValueError("P2 common target has zero variance")
    correct_standardized = correct.semi_specific_effect_1sd_bps / (target_sd * 10_000.0)
    future_standardized = future.semi_specific_effect_1sd_bps / (target_sd * 10_000.0)
    passed = (
        future_beta["one_sided_p_value"] >= 0.10
        and correct_standardized > future_standardized
    )
    return {
        "n_common": len(common),
        "common_sessions": common[["session_date", "future_window_date"]].copy(),
        "correct": correct,
        "future": future,
        "correct_standardized_beta": float(correct_standardized),
        "future_standardized_beta": float(future_standardized),
        "passed": bool(passed),
    }


def stability_blocks(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Estimate frozen H2 independently in the three pre-registered blocks."""
    dated = frame.copy()
    dated["session_date"] = pd.to_datetime(dated["session_date"]).dt.date
    results: list[dict[str, Any]] = []
    for label, start, end in BLOCKS:
        block = dated.loc[dated["session_date"].between(start, end)].copy()
        result = frozen_hac_ols(
            block,
            target="intraday_rel",
            regressors=["semi_specific"],
            model=f"H2_{label}",
        )
        beta = result.parameter("semi_specific")["coefficient"]
        results.append({"block": label, "start": start, "end": end, "result": result, "positive": beta > 0})
    return results


def monotonicity_diagnostics(frame: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    """Compute frozen secondary Spearman and target means by SemiSpecific quintile."""
    clean = frame[["semi_specific", "intraday_rel"]].dropna().copy()
    statistic, p_two_sided = stats.spearmanr(clean["semi_specific"], clean["intraday_rel"])
    clean["quintile"] = pd.qcut(clean["semi_specific"], 5, labels=[1, 2, 3, 4, 5])
    quintiles = (
        clean.groupby("quintile", observed=True)["intraday_rel"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"mean": "mean_intraday_rel"})
    )
    return {
        "n": len(clean),
        "spearman_rank_ic": float(statistic),
        "p_two_sided_unadjusted": float(p_two_sided),
    }, quintiles


def evaluate_gates(
    *,
    h2: RegressionResult,
    h3: RegressionResult,
    p_perm_h2: float,
    p_perm_h3: float,
    positive_blocks: int,
    timing_pass: bool,
) -> dict[str, Any]:
    """Apply the frozen CM_001 decision gates without discretionary overrides."""
    h2_beta = h2.parameter("semi_specific")
    h3_beta = h3.parameter("semi_specific")
    core = h2_beta["coefficient"] > 0 and h2_beta["one_sided_p_value"] < 0.05
    robustness = p_perm_h2 < 0.05 and positive_blocks >= 2
    specificity = (
        h3_beta["coefficient"] > 0
        and h3_beta["one_sided_p_value"] < 0.05
        and p_perm_h3 < 0.05
    )
    timing = bool(timing_pass)
    if not core:
        verdict = "NO_GO"
    elif robustness and specificity and timing:
        verdict = "GO"
    else:
        verdict = "CONDITIONAL_GO"
    return {
        "CorePass": bool(core),
        "RobustnessPass": bool(robustness),
        "SpecificityPass": bool(specificity),
        "TimingPass": timing,
        "verdict": verdict,
    }


def load_research_samples(processed_root: Path) -> SampleBundle:
    """Build frozen primary and 0050 robustness samples from Research-only raw OHLC."""
    provider = processed_root / "stage_a_provider_audit_v2"
    closure = processed_root / "stage_a_closure_audit"
    canonical = provider / "canonical"
    mapping = pd.read_csv(provider / "session_mapping.csv")
    mapping["session_date"] = pd.to_datetime(mapping["target_session"]).dt.date
    assert_research_dates(mapping["session_date"], label="session mapping")

    assets: dict[str, pd.DataFrame] = {}
    paths = {
        "XSD": canonical / "XSD_ohlc.csv",
        "QQQ": canonical / "QQQ_ohlc.csv",
        "SPY": canonical / "SPY_ohlc.csv",
        "0052": canonical / "0052_ohlc_valid_rows.csv",
        "0050": canonical / "0050_ohlc.csv",
        "TAIEX": canonical / "TAIEX_ohlc.csv",
    }
    for asset, path in paths.items():
        frame = pd.read_csv(path)
        frame["session_date"] = pd.to_datetime(frame["session_date"]).dt.date
        assert_research_dates(frame["session_date"], label=asset)
        keep = ["session_date", "open", "close"]
        assets[asset] = frame[keep].rename(
            columns={"open": f"open_{asset}", "close": f"close_{asset}"}
        )

    return construct_samples(
        mapping,
        assets,
        actions_path=closure / "corporate_action_master.csv",
        expected_counts=EXPECTED_COUNTS,
    )


def construct_samples(
    mapping: pd.DataFrame,
    assets: Mapping[str, pd.DataFrame],
    *,
    actions_path: Path | None = None,
    actions: pd.DataFrame | None = None,
    expected_counts: Mapping[str, int] | None = None,
) -> SampleBundle:
    """Construct literal frozen features/targets and apply action exclusions.

    Passing in-memory ``actions`` supports synthetic tests. Production acquisition
    passes ``actions_path`` and enforces the registered primary sample counts.
    """
    if (actions_path is None) == (actions is None):
        raise ValueError("provide exactly one of actions_path or actions")
    required_assets = {"XSD", "QQQ", "SPY", "0052", "0050", "TAIEX"}
    missing_assets = required_assets.difference(assets)
    if missing_assets:
        raise ValueError(f"missing assets: {sorted(missing_assets)}")

    mapping = mapping.copy()
    if "session_date" not in mapping:
        mapping["session_date"] = pd.to_datetime(mapping["target_session"]).dt.date
    else:
        mapping["session_date"] = pd.to_datetime(mapping["session_date"]).dt.date
    assert_research_dates(mapping["session_date"], label="session mapping")
    prepared_assets: dict[str, pd.DataFrame] = {}
    for asset, source in assets.items():
        frame = source.copy()
        frame["session_date"] = pd.to_datetime(frame["session_date"]).dt.date
        assert_research_dates(frame["session_date"], label=asset)
        prepared_assets[asset] = frame

    us = prepared_assets["XSD"].merge(
        prepared_assets["QQQ"], on="session_date", validate="one_to_one"
    )
    us = us.merge(prepared_assets["SPY"], on="session_date", validate="one_to_one")
    us["semi_specific"] = np.log(us["close_XSD"] / us["open_XSD"]) - np.log(
        us["close_QQQ"] / us["open_QQQ"]
    )
    us["broad_tech"] = np.log(us["close_QQQ"] / us["open_QQQ"]) - np.log(
        us["close_SPY"] / us["open_SPY"]
    )
    us_lookup = us.set_index("session_date")[["semi_specific", "broad_tech"]]

    def aggregate(row: pd.Series, field: str) -> float:
        dates = [
            date.fromisoformat(value)
            for value in str(row["us_session_dates"]).split(";")
            if value and value != "nan"
        ]
        if row["mapping_status"] != "VALID" or not dates:
            return np.nan
        values = us_lookup.reindex(dates)[field]
        if values.isna().any() or len(values) != int(row["n_us_sessions"]):
            raise ValueError(f"missing {field} input for {row['session_date']}")
        return float(values.sum())

    ledger = mapping[
        ["session_date", "mapping_status", "n_us_sessions", "us_session_dates"]
    ].copy()
    ledger["semi_specific"] = ledger.apply(aggregate, axis=1, field="semi_specific")
    ledger["broad_tech"] = ledger.apply(aggregate, axis=1, field="broad_tech")
    for asset in ("0052", "0050", "TAIEX"):
        ledger = ledger.merge(
            prepared_assets[asset], on="session_date", how="left", validate="one_to_one"
        )

    for asset in ("0052", "0050", "TAIEX"):
        ledger[f"previous_close_{asset}"] = ledger[f"close_{asset}"].shift(1)
        ledger[f"previous2_close_{asset}"] = ledger[f"close_{asset}"].shift(2)
    ledger["gap_0052"] = np.log(ledger["open_0052"] / ledger["previous_close_0052"])
    ledger["gap_0050"] = np.log(ledger["open_0050"] / ledger["previous_close_0050"])
    ledger["gap_TAIEX"] = np.log(ledger["open_TAIEX"] / ledger["previous_close_TAIEX"])
    ledger["intraday_0052"] = np.log(ledger["close_0052"] / ledger["open_0052"])
    ledger["intraday_0050"] = np.log(ledger["close_0050"] / ledger["open_0050"])
    ledger["intraday_TAIEX"] = np.log(ledger["close_TAIEX"] / ledger["open_TAIEX"])
    ledger["prev_0052"] = np.log(ledger["previous_close_0052"] / ledger["previous2_close_0052"])
    ledger["prev_0050"] = np.log(ledger["previous_close_0050"] / ledger["previous2_close_0050"])
    ledger["prev_TAIEX"] = np.log(ledger["previous_close_TAIEX"] / ledger["previous2_close_TAIEX"])
    ledger["gap_rel"] = ledger["gap_0052"] - ledger["gap_TAIEX"]
    ledger["intraday_rel"] = ledger["intraday_0052"] - ledger["intraday_TAIEX"]
    ledger["prev_tw_rel"] = ledger["prev_0052"] - ledger["prev_TAIEX"]
    ledger["gap_rel_0050"] = ledger["gap_0052"] - ledger["gap_0050"]
    ledger["intraday_rel_0050"] = ledger["intraday_0052"] - ledger["intraday_0050"]
    ledger["prev_tw_rel_0050"] = ledger["prev_0052"] - ledger["prev_0050"]

    if actions_path is not None:
        actions = pd.read_csv(actions_path)
    else:
        actions = actions.copy()
    actions["event_date"] = pd.to_datetime(actions["event_date"]).dt.date
    assert_research_dates(actions["event_date"], label="corporate actions")
    event_dates = {
        asset: set(
            actions.loc[
                actions["instrument"].astype(str).str.zfill(4).eq(asset),
                "event_date",
            ]
        )
        for asset in ("0052", "0050")
    }
    next_session: dict[date, date] = {
        previous: current
        for previous, current in zip(ledger["session_date"].iloc[:-1], ledger["session_date"].iloc[1:])
    }
    primary_h1_exclusions = event_dates["0052"]
    robustness_events = event_dates["0052"] | event_dates["0050"]
    missing_successors = robustness_events.difference(next_session)
    if missing_successors:
        raise ValueError(f"corporate actions lack following session: {sorted(missing_successors)}")
    primary_h3_exclusions = {next_session[value] for value in event_dates["0052"]}
    robustness_h3_exclusions = {next_session[value] for value in robustness_events}

    eligible = ledger["mapping_status"].eq("VALID")
    primary = {
        "H1": _complete_sample(
            ledger,
            eligible & ~ledger["session_date"].isin(primary_h1_exclusions),
            ["semi_specific", "gap_rel"],
        ),
        "H2": _complete_sample(ledger, eligible, ["semi_specific", "intraday_rel"]),
        "H3": _complete_sample(
            ledger,
            eligible & ~ledger["session_date"].isin(primary_h3_exclusions),
            ["semi_specific", "broad_tech", "prev_tw_rel", "intraday_rel"],
        ),
    }
    robustness = {
        "H1": _complete_sample(
            ledger,
            eligible & ~ledger["session_date"].isin(robustness_events),
            ["semi_specific", "gap_rel_0050"],
        ),
        "H2": _complete_sample(ledger, eligible, ["semi_specific", "intraday_rel_0050"]),
        "H3": _complete_sample(
            ledger,
            eligible & ~ledger["session_date"].isin(robustness_h3_exclusions),
            ["semi_specific", "broad_tech", "prev_tw_rel_0050", "intraday_rel_0050"],
        ),
    }
    actual = {name: len(frame) for name, frame in primary.items()}
    if expected_counts is not None and actual != dict(expected_counts):
        raise ValueError(
            f"constructed count divergence: expected {dict(expected_counts)}, got {actual}"
        )
    eligible_window_table = ledger.loc[
        eligible & ledger["semi_specific"].notna() & ledger["broad_tech"].notna(),
        ["session_date", "semi_specific", "broad_tech"],
    ].copy()
    return SampleBundle(
        primary=primary,
        robustness_0050=robustness,
        eligible_window_table=eligible_window_table,
    )


def _complete_sample(frame: pd.DataFrame, mask: pd.Series, columns: Sequence[str]) -> pd.DataFrame:
    selected = frame.loc[mask, ["session_date", "n_us_sessions", *columns]].dropna().copy()
    assert_research_dates(selected["session_date"], label="constructed sample")
    return selected.sort_values("session_date").reset_index(drop=True)


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series
    return series.astype(str).str.lower().map({"true": True, "false": False}).fillna(False).astype(bool)
