"""Synthetic and bounded real-data tests for frozen LAF_001 Research."""

from __future__ import annotations

import math
import sys
import unittest
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_research import (  # noqa: E402
    HAC_MAXLAGS,
    INVARIANCE_TOLERANCE,
    LOOKBACK,
    MAD_SCALE,
    MIN_ELIGIBLE_ETFS,
    MONTHLY_WINDOW,
    RAW_RESPONSE_SHA256,
    SPEC_VERSION,
    STATE_PRIOR_MIN,
    SYMBOLS,
    _rolling_robust_z,
    attach_expanding_state,
    construct_bundle,
    construct_daily_features,
    construct_monthly_targets,
    execute_frozen_models,
    fit_hac_ols,
    load_split_table,
    load_yahoo_research,
    scale_invariance_audit,
    split_embargo_dates,
    target_independence_audit,
)
from laf_stage_a1 import expected_xnys_dates  # noqa: E402


RAW_ROOT = REPO_ROOT / "data" / "raw" / "laf_001" / "research" / "20260815T055848814Z"
SPLIT_PATH = (
    REPO_ROOT
    / "data"
    / "processed"
    / "laf_001"
    / "stage_a1c"
    / "20260815T055848814Z"
    / "corporate_actions.csv"
)


def _synthetic_frames() -> dict[str, pd.DataFrame]:
    sessions = expected_xnys_dates()
    index = np.arange(len(sessions), dtype=float)
    frames: dict[str, pd.DataFrame] = {}
    for offset, symbol in enumerate(SYMBOLS):
        log_price = 4.5 + 0.0002 * index + 0.003 * np.sin(index / (11.0 + offset))
        adjusted = np.exp(log_price)
        close = adjusted / (0.75 + 0.01 * offset)
        open_ = close * (1.0 + 0.001 * np.cos(index / (7.0 + offset)))
        low = np.minimum(open_, close) * 0.99
        volume = 1_000_000.0 + 20_000.0 * np.sin(index / (13.0 + offset)) + index
        frames[symbol] = pd.DataFrame(
            {
                "symbol": symbol,
                "source_timestamp": np.arange(len(sessions)),
                "source_timestamp_utc": "2000-01-01T00:00:00+00:00",
                "session_date": sessions,
                "open": open_,
                "high": np.maximum(open_, close) * 1.01,
                "low": low,
                "close": close,
                "adj_close": adjusted,
                "volume": volume,
            }
        )
    return frames


def _split_table() -> pd.DataFrame:
    return pd.DataFrame(
        [{"symbol": "IWM", "session_date": date(2005, 6, 9), "action_type": "STOCK_SPLIT"}]
    )


class FrozenContractTests(unittest.TestCase):
    def test_literal_constants(self) -> None:
        self.assertEqual(SPEC_VERSION, "v1.0-frozen")
        self.assertEqual(SYMBOLS, ("SPY", "QQQ", "IWM", "DIA", "MDY"))
        self.assertEqual(LOOKBACK, 252)
        self.assertEqual(MONTHLY_WINDOW, 21)
        self.assertEqual(MIN_ELIGIBLE_ETFS, 4)
        self.assertEqual(MAD_SCALE, 1.4826)
        self.assertEqual(HAC_MAXLAGS, 3)
        self.assertEqual(STATE_PRIOR_MIN, 36)

    def test_prior_only_rolling_z_is_future_invariant(self) -> None:
        x = pd.Series(np.linspace(-3.0, 4.0, 600) + np.sin(np.arange(600)))
        _, _, baseline = _rolling_robust_z(x)
        changed = x.copy()
        changed.iloc[500:] *= 99.0
        _, _, altered = _rolling_robust_z(changed)
        pd.testing.assert_series_equal(baseline.iloc[:500], altered.iloc[:500])
        self.assertTrue(baseline.iloc[:LOOKBACK].isna().all())

    def test_zero_pi_and_zero_mad_are_missing(self) -> None:
        constant = pd.Series([1.0] * 400)
        _, mad, z = _rolling_robust_z(constant)
        self.assertEqual(mad.iloc[LOOKBACK], 0.0)
        self.assertTrue(z.isna().all())


class ConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = _synthetic_frames()
        cls.splits = _split_table()

    def test_split_embargo_ends_when_prior_window_is_post_split(self) -> None:
        sessions = expected_xnys_dates()
        embargo = split_embargo_dates(sessions, self.splits)["IWM"]
        event_position = sessions.index(date(2005, 6, 9))
        self.assertEqual(len(embargo), LOOKBACK)
        self.assertIn(sessions[event_position], embargo)
        self.assertIn(sessions[event_position + LOOKBACK - 1], embargo)
        self.assertNotIn(sessions[event_position + LOOKBACK], embargo)

    def test_daily_formula_manual_row(self) -> None:
        daily = construct_daily_features(self.frames, self.splits)
        position = LOOKBACK + 10
        spy = self.frames["SPY"]
        expected_return = math.log(
            spy.iloc[position]["adj_close"] / spy.iloc[position - 1]["adj_close"]
        )
        expected_x = math.log(
            abs(expected_return)
            / (spy.iloc[position]["close"] * spy.iloc[position]["volume"])
        )
        self.assertAlmostEqual(daily.iloc[position]["r_SPY"], expected_return, places=15)
        self.assertAlmostEqual(daily.iloc[position]["x_SPY"], expected_x, places=15)

    def test_aggregate_requires_at_least_four_eligible_etfs(self) -> None:
        daily = construct_daily_features(self.frames, self.splits)
        eligible = daily.loc[daily["eligible_etf_count"] >= 4].iloc[0]
        values = [eligible[f"z_{symbol}"] for symbol in SYMBOLS if eligible[f"eligible_{symbol}"]]
        self.assertAlmostEqual(eligible["A_d"], float(np.median(values)), places=15)

    def test_target_manual_entry_to_low(self) -> None:
        frames = {symbol: frame.copy(deep=True) for symbol, frame in self.frames.items()}
        january = pd.PeriodIndex(frames["SPY"]["session_date"], freq="M") == pd.Period("2004-01")
        positions = frames["SPY"].index[january]
        first = positions[0]
        frames["SPY"].loc[first, "open"] = frames["SPY"].loc[first, "close"]
        frames["SPY"].loc[positions, "low"] = frames["SPY"].loc[first, "close"] * 0.90
        targets = construct_monthly_targets(frames["SPY"])
        january_target = targets.loc[targets["target_month"] == "2004-01"].iloc[0]
        self.assertAlmostEqual(january_target["tail_loss"], -math.log(0.90), places=12)

    def test_target_fields_do_not_change_features(self) -> None:
        audit = target_independence_audit(self.frames, self.splits)
        self.assertTrue(audit["features_exactly_equal"])
        self.assertTrue(audit["pass"])

    def test_synthetic_positive_scale_invariance(self) -> None:
        audit = scale_invariance_audit(self.frames, self.splits)
        self.assertTrue(audit["pass"])
        self.assertLessEqual(
            max(item["max_abs_daily_difference"] for item in audit["scenarios"]),
            INVARIANCE_TOLERANCE,
        )


class StateAndInferenceTests(unittest.TestCase):
    def test_q80_excludes_current_month(self) -> None:
        sample = pd.DataFrame(
            {
                "target_month": [f"2004-{index + 1:02d}" for index in range(12)]
                + [f"{2005 + index // 12}-{index % 12 + 1:02d}" for index in range(36)],
                "laf": np.arange(48, dtype=float),
            }
        )
        state = attach_expanding_state(sample)
        expected = float(pd.Series(np.arange(36, dtype=float)).quantile(0.80))
        self.assertEqual(state.iloc[36]["laf_prior_q80"], expected)
        self.assertEqual(state.iloc[36]["state_prior_month_count"], 36)

    def test_hac_ols_point_estimate_and_options(self) -> None:
        x = np.linspace(-2.0, 2.0, 80)
        rv = np.cos(np.arange(80) / 5)
        y = 0.2 + 0.7 * x - 0.3 * rv + 0.01 * np.sin(np.arange(80))
        frame = pd.DataFrame({"tail_loss": y, "laf": x, "rv": rv})
        result = fit_hac_ols(
            frame, target="tail_loss", regressors=("laf", "rv"), model="synthetic"
        )
        expected = np.linalg.lstsq(
            np.column_stack([np.ones(80), x, rv]), y, rcond=None
        )[0]
        np.testing.assert_allclose(result.coefficients, expected, atol=1e-12)
        self.assertEqual(result.hac_maxlags, 3)
        self.assertTrue(result.small_sample_correction)
        self.assertTrue(result.use_t)

    def test_literal_no_go_cannot_be_rescued(self) -> None:
        months = pd.period_range("2004-01", periods=120, freq="M").astype(str)
        laf = np.linspace(-1, 1, 120)
        rv = np.sin(np.arange(120) / 9) + 2
        tail = 0.2 - 0.05 * laf + 0.01 * rv + 0.001 * np.cos(np.arange(120))
        sample = pd.DataFrame(
            {
                "target_month": months,
                "laf": laf,
                "rv": rv,
                "tail_loss": tail,
                "laf_state": ["HIGH" if index % 5 == 0 else "NORMAL" for index in range(120)],
                "primary_complete_case": True,
            }
        )
        result = execute_frozen_models(sample)
        self.assertFalse(result["gates"]["CorePass"])
        self.assertEqual(result["gates"]["verdict"], "NO_GO")

    def test_unestimable_stability_block_fails_without_variant(self) -> None:
        months = pd.period_range("2011-01", periods=24, freq="M").astype(str)
        laf = np.linspace(-1, 1, 24)
        rv = np.sin(np.arange(24) / 4) + 2
        tail = 0.1 + 0.02 * laf + 0.01 * rv
        sample = pd.DataFrame(
            {
                "target_month": months,
                "laf": laf,
                "rv": rv,
                "tail_loss": tail,
                "laf_state": None,
                "primary_complete_case": True,
            }
        )
        result = execute_frozen_models(sample)
        first = next(item for item in result["blocks"] if item["block"] == "2004-2010")
        self.assertFalse(first["estimable"])
        self.assertIsNone(first["result"])
        self.assertFalse(result["gates"]["StabilityPass"])
        self.assertFalse(result["gates"]["StatePass"])
        self.assertIsNone(result["state"]["high_minus_normal"])


class BoundedRealDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = load_yahoo_research(RAW_ROOT)
        cls.splits = load_split_table(SPLIT_PATH)

    def test_hashes_universe_and_closed_boundary(self) -> None:
        self.assertEqual(tuple(self.frames), SYMBOLS)
        self.assertEqual(set(RAW_RESPONSE_SHA256), set(SYMBOLS))
        self.assertTrue(
            all(max(frame["session_date"]) == date(2016, 12, 30) for frame in self.frames.values())
        )

    def test_real_scale_invariance_and_target_independence(self) -> None:
        invariance = scale_invariance_audit(self.frames, self.splits)
        self.assertTrue(invariance["pass"])
        self.assertTrue(target_independence_audit(self.frames, self.splits)["pass"])

    def test_real_bundle_has_no_closed_rows_or_duplicate_dates(self) -> None:
        bundle = construct_bundle(self.frames, self.splits)
        self.assertEqual(bundle.boundary_audit["historical_rows_2017_or_later"], 0)
        self.assertEqual(bundle.boundary_audit["daily_duplicate_dates"], 0)
        self.assertTrue(bundle.boundary_audit["feature_before_execution"])
        self.assertEqual(bundle.research_sample["target_month"].max(), "2016-12")


if __name__ == "__main__":
    unittest.main()
