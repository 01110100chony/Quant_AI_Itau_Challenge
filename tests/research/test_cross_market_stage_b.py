from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_b import (  # noqa: E402
    assert_research_dates,
    build_p2_common_sample,
    circular_shift_placebo,
    construct_samples,
    evaluate_gates,
    frozen_hac_ols,
    future_information_placebo,
)


class StageBSyntheticTests(unittest.TestCase):
    def test_research_boundary_rejects_validation_date(self) -> None:
        with self.assertRaises(ValueError):
            assert_research_dates(
                pd.Series([date(2018, 12, 31), date(2019, 1, 1)]),
                label="synthetic",
            )

    def test_hac_ols_matches_ols_point_estimate_and_frozen_options(self) -> None:
        rng = np.random.default_rng(123)
        x = rng.normal(size=120)
        y = 0.01 + 0.7 * x + rng.normal(scale=0.25, size=120)
        frame = pd.DataFrame({"semi_specific": x, "intraday_rel": y})
        result = frozen_hac_ols(
            frame,
            target="intraday_rel",
            regressors=["semi_specific"],
            model="synthetic_h2",
        )
        expected = np.linalg.lstsq(
            np.column_stack([np.ones(len(x)), x]), y, rcond=None
        )[0]
        np.testing.assert_allclose(result.coefficients, expected)
        self.assertEqual(result.n, 120)
        self.assertEqual(result.hac_kernel, "Bartlett")
        self.assertEqual(result.hac_maxlags, 5)
        self.assertTrue(result.small_sample_correction)
        self.assertTrue(result.use_t)

    def test_circular_placebo_is_seeded_and_uses_frozen_offset_support(self) -> None:
        rng = np.random.default_rng(11)
        frame = pd.DataFrame(
            {
                "session_date": pd.date_range("2010-01-01", periods=80),
                "semi_specific": rng.normal(size=80),
                "intraday_rel": rng.normal(size=80),
            }
        )
        first = circular_shift_placebo(
            frame,
            target="intraday_rel",
            controls=[],
            observed_beta=0.01,
            permutations=50,
            seed=7,
        )
        second = circular_shift_placebo(
            frame,
            target="intraday_rel",
            controls=[],
            observed_beta=0.01,
            permutations=50,
            seed=7,
        )
        np.testing.assert_array_equal(first["beta_perm"], second["beta_perm"])
        self.assertEqual(first["offset_min"], 21)
        self.assertEqual(first["offset_max"], 59)
        self.assertEqual(first["p_perm"], second["p_perm"])

    def test_future_placebo_uses_common_complete_sample(self) -> None:
        rng = np.random.default_rng(4)
        semi = rng.normal(size=100)
        frame = pd.DataFrame(
            {
                "session_date": pd.date_range("2010-01-01", periods=100),
                "semi_specific": semi,
                "intraday_rel": 0.4 * semi + rng.normal(scale=0.2, size=100),
            }
        )
        result = future_information_placebo(
            frame, frame[["session_date", "semi_specific"]]
        )
        self.assertEqual(result["n_common"], 99)
        self.assertEqual(result["correct"].n, result["future"].n)
        self.assertGreater(
            result["correct_standardized_beta"],
            result["future_standardized_beta"],
        )

    def test_p2_target_future_absent_uses_its_feature_not_later_target(self) -> None:
        windows, h2 = self._p2_fixture(target_dates=["2010-01-04", "2010-01-06"])
        common = build_p2_common_sample(h2, windows)
        self.assertEqual(common.loc[0, "future_window_date"], date(2010, 1, 5))
        self.assertEqual(common.loc[0, "future_semi_specific"], 2.0)

    def test_p2_empty_us_window_is_skipped(self) -> None:
        windows, h2 = self._p2_fixture(
            eligible_dates=["2010-01-04", "2010-01-06"],
            target_dates=["2010-01-04", "2010-01-05", "2010-01-06"],
        )
        common = build_p2_common_sample(h2, windows)
        first = common.loc[common["session_date"].eq(date(2010, 1, 4))].iloc[0]
        self.assertEqual(first["future_window_date"], date(2010, 1, 6))

    def test_p2_last_eligible_window_has_no_lead_and_drops_at_common_complete(self) -> None:
        windows, h2 = self._p2_fixture()
        common = build_p2_common_sample(h2, windows)
        self.assertNotIn(date(2010, 1, 6), set(common["session_date"]))
        self.assertEqual(len(common), 2)

    def test_p2_future_dates_are_strictly_later(self) -> None:
        windows, h2 = self._p2_fixture()
        common = build_p2_common_sample(h2, windows)
        self.assertTrue((common["future_window_date"] > common["session_date"]).all())

    def test_p2_correct_and_future_models_use_identical_sessions(self) -> None:
        rng = np.random.default_rng(81)
        frame = pd.DataFrame(
            {
                "session_date": pd.date_range("2010-01-04", periods=60),
                "semi_specific": rng.normal(size=60),
                "intraday_rel": rng.normal(size=60),
            }
        )
        result = future_information_placebo(
            frame, frame[["session_date", "semi_specific"]]
        )
        self.assertEqual(result["correct"].n, result["future"].n)
        self.assertEqual(result["correct"].n, len(result["common_sessions"]))

    def test_p2_future_window_identity_is_independent_of_future_target(self) -> None:
        windows, complete_h2 = self._p2_fixture()
        missing_future_target = complete_h2.loc[
            ~complete_h2["session_date"].eq(date(2010, 1, 5))
        ]
        before = build_p2_common_sample(complete_h2, windows)
        after = build_p2_common_sample(missing_future_target, windows)
        before_a = before.loc[before["session_date"].eq(date(2010, 1, 4))].iloc[0]
        after_a = after.loc[after["session_date"].eq(date(2010, 1, 4))].iloc[0]
        self.assertEqual(before_a["future_window_date"], after_a["future_window_date"])
        self.assertEqual(before_a["future_semi_specific"], after_a["future_semi_specific"])

    def test_literal_sample_formulas_and_corporate_action_policy(self) -> None:
        sessions = pd.bdate_range("2010-01-04", periods=12)
        session_dates = sessions.date
        mapping = pd.DataFrame(
            {
                "target_session": sessions.strftime("%Y-%m-%d"),
                "mapping_status": "VALID",
                "n_us_sessions": 1,
                "us_session_dates": sessions.strftime("%Y-%m-%d"),
            }
        )

        def asset(name: str, open_base: float, close_step: float) -> pd.DataFrame:
            opens = open_base + np.arange(len(sessions), dtype=float)
            closes = opens * (1.0 + close_step)
            return pd.DataFrame(
                {
                    "session_date": session_dates,
                    f"open_{name}": opens,
                    f"close_{name}": closes,
                }
            )

        assets = {
            "XSD": asset("XSD", 40.0, 0.020),
            "QQQ": asset("QQQ", 50.0, 0.010),
            "SPY": asset("SPY", 60.0, 0.005),
            "0052": asset("0052", 30.0, 0.015),
            "0050": asset("0050", 35.0, 0.012),
            "TAIEX": asset("TAIEX", 7_000.0, 0.008),
        }
        event_0052 = session_dates[5]
        event_0050 = session_dates[7]
        actions = pd.DataFrame(
            {
                "instrument": ["0052", "0050"],
                "event_date": [event_0052, event_0050],
            }
        )
        bundle = construct_samples(mapping, assets, actions=actions)
        self.assertNotIn(event_0052, set(bundle.primary["H1"]["session_date"]))
        self.assertIn(event_0052, set(bundle.primary["H2"]["session_date"]))
        self.assertNotIn(session_dates[6], set(bundle.primary["H3"]["session_date"]))
        self.assertNotIn(event_0050, set(bundle.robustness_0050["H1"]["session_date"]))
        h2_row = bundle.primary["H2"].loc[
            bundle.primary["H2"]["session_date"].eq(session_dates[4])
        ].iloc[0]
        expected_semi = np.log(1.020) - np.log(1.010)
        expected_target = np.log(1.015) - np.log(1.008)
        self.assertAlmostEqual(h2_row["semi_specific"], expected_semi)
        self.assertAlmostEqual(h2_row["intraday_rel"], expected_target)

    def test_frozen_gate_logic_does_not_allow_secondary_rescue(self) -> None:
        x = np.linspace(-1.0, 1.0, 100)
        frame = pd.DataFrame(
            {"semi_specific": x, "intraday_rel": -0.5 * x + 0.01 * np.sin(x)}
        )
        negative_h2 = frozen_hac_ols(
            frame,
            target="intraday_rel",
            regressors=["semi_specific"],
            model="negative_h2",
        )
        gates = evaluate_gates(
            h2=negative_h2,
            h3=negative_h2,
            p_perm_h2=0.001,
            p_perm_h3=0.001,
            positive_blocks=3,
            timing_pass=True,
        )
        self.assertFalse(gates["CorePass"])
        self.assertEqual(gates["verdict"], "NO_GO")

    @staticmethod
    def _p2_fixture(
        *,
        eligible_dates: list[str] | None = None,
        target_dates: list[str] | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        all_dates = ["2010-01-04", "2010-01-05", "2010-01-06"]
        eligible_dates = eligible_dates or all_dates
        target_dates = target_dates or all_dates
        feature_lookup = {
            date(2010, 1, 4): 1.0,
            date(2010, 1, 5): 2.0,
            date(2010, 1, 6): 3.0,
        }
        windows = pd.DataFrame(
            {
                "session_date": pd.to_datetime(eligible_dates),
                "semi_specific": [
                    feature_lookup[value]
                    for value in pd.to_datetime(eligible_dates).date
                ],
            }
        )
        h2_dates = pd.to_datetime(target_dates)
        h2 = pd.DataFrame(
            {
                "session_date": h2_dates,
                "semi_specific": [feature_lookup[value] for value in h2_dates.date],
                "intraday_rel": np.arange(1, len(h2_dates) + 1, dtype=float),
            }
        )
        return windows, h2


if __name__ == "__main__":
    unittest.main()
