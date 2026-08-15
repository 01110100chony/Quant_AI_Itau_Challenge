from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "audit" / "rsr_001_audit.py"
SPEC = importlib.util.spec_from_file_location("rsr_001_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {MODULE_PATH}")
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def synthetic_prices(start: str, end: str) -> pd.DataFrame:
    dates = pd.bdate_range(start, end)
    steps = np.arange(len(dates), dtype=float)
    data: dict[str, np.ndarray] = {}
    market_return = 0.0004 + 0.0002 * np.sin(steps / 11.0)
    data["SPY"] = 100.0 * np.exp(np.cumsum(market_return))
    for position, ticker in enumerate(audit.UNIVERSE, 1):
        noise = 0.0001 * position * np.cos(steps / (3.0 + position))
        ticker_return = 0.0001 * position + (0.4 + position / 20.0) * market_return + noise
        data[ticker] = (90.0 + position) * np.exp(np.cumsum(ticker_return))
    return pd.DataFrame(data, index=dates)


class WindowInvariantTests(unittest.TestCase):
    def test_ols_residual_uses_exactly_previous_window(self) -> None:
        prices = synthetic_prices("2020-01-01", "2020-05-29")
        returns = audit.log_returns(prices)
        market = returns["SPY"]
        window = 20
        residuals = audit.point_in_time_residuals(returns, market, window)
        position = 35
        date = returns.index[position]
        x = market.iloc[position - window:position].to_numpy()
        y = returns["XLB"].iloc[position - window:position].to_numpy()
        design = np.column_stack([np.ones(window), x])
        alpha, beta = np.linalg.lstsq(design, y, rcond=None)[0]
        expected = returns.loc[date, "XLB"] - alpha - beta * market.loc[date]
        self.assertAlmostEqual(residuals.loc[date, "XLB"], expected, places=14)

    def test_signal_uses_t_minus_s_plus_one_through_t(self) -> None:
        residuals = pd.DataFrame(
            {ticker: np.arange(1.0, 31.0) + i for i, ticker in enumerate(audit.UNIVERSE)},
            index=pd.bdate_range("2020-01-01", periods=30),
        )
        signal = -residuals.rolling(7).sum()
        expected = -residuals["XLB"].iloc[13:20].sum()
        self.assertEqual(signal["XLB"].iloc[19], expected)


class TimingAndPersistenceTests(unittest.TestCase):
    def test_midmonth_snapshot_excludes_incomplete_next_month(self) -> None:
        prices = synthetic_prices("2018-01-01", "2020-03-10")
        panel = audit.build_panel(
            prices,
            audit.PanelConfig(estimation_window=20, signal_window=5, require_complete_target=True),
        )
        self.assertNotIn(pd.Timestamp("2020-02-28"), panel.index)
        self.assertEqual(panel.index.max(), pd.Timestamp("2020-01-31"))
        self.assertEqual(panel.iloc[-1]["target_end"], pd.Timestamp("2020-02-28"))

    def test_frozen_snapshot_eligibility_is_june_with_july_target(self) -> None:
        prices = audit.load_prices(
            REPO_ROOT / "data" / "raw" / "us_sector_etfs_plus_spy_adjusted_close.csv"
        )
        panel = audit.build_panel(prices, audit.PanelConfig())
        self.assertNotIn(pd.Timestamp("2026-07-31"), panel.index)
        self.assertEqual(panel.index.max(), pd.Timestamp("2026-06-30"))
        self.assertEqual(panel.iloc[-1]["target_end"], pd.Timestamp("2026-07-31"))

    def test_target_excludes_signal_date(self) -> None:
        prices = synthetic_prices("2018-01-01", "2020-04-10")
        panel = audit.build_panel(
            prices,
            audit.PanelConfig(estimation_window=20, signal_window=5),
        )
        row = panel.iloc[-1]
        t = panel.index[-1]
        target_end = row["target_end"]
        returns = audit.log_returns(prices)
        expected = returns.loc[t:target_end, "XLB"].iloc[1:].sum()
        self.assertAlmostEqual(row["y_XLB"], expected, places=14)

    def test_panel_persistence_columns_exist_without_long(self) -> None:
        prices = synthetic_prices("2018-01-01", "2020-04-10")
        panel = audit.build_panel(
            prices,
            audit.PanelConfig(estimation_window=20, signal_window=5),
        )
        self.assertNotIn("long", panel.columns)
        self.assertIn("spread", panel.columns)
        self.assertIn("liquido", panel.columns)
        panel.to_csv(Path(self.id().replace(".", "_") + ".csv"))
        Path(self.id().replace(".", "_") + ".csv").unlink()


class GovernanceAndStatisticsTests(unittest.TestCase):
    def test_quarantine_never_enters_corrected_oos(self) -> None:
        prices = audit.load_prices(
            REPO_ROOT / "data" / "raw" / "us_sector_etfs_plus_spy_adjusted_close.csv"
        )
        panel = audit.build_panel(prices, audit.PanelConfig())
        oos = panel.loc[audit.OOS_START:audit.OOS_SPEC_END]
        self.assertTrue((oos.index > audit.QUARANTINE_END).all())
        self.assertEqual(len(oos), 88)

    def test_placebos_are_deterministic_and_use_plus_one_estimator(self) -> None:
        x = np.arange(54.0).reshape(6, 9)
        y = x[:, ::-1]
        first = audit.permutation_placebos(x, y, n_perm=31, seed=7)
        second = audit.permutation_placebos(x, y, n_perm=31, seed=7)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["p1"], 1 / 32)
        self.assertGreaterEqual(first["p2"], 1 / 32)

    def test_corrected_blocks_preserve_frozen_boundaries(self) -> None:
        panel = pd.DataFrame({"value": np.arange(88)})
        b1, b2, b3 = audit.fixed_oos_blocks(panel)
        self.assertEqual((len(b1), len(b2), len(b3)), (30, 30, 28))
        self.assertEqual((b1.index[-1], b2.index[0], b2.index[-1], b3.index[0]), (29, 30, 59, 60))

    def test_research_path_crops_before_oos_computation(self) -> None:
        prices = synthetic_prices("2016-01-01", "2020-12-31")
        research = audit.research_panel(
            prices,
            audit.PanelConfig(estimation_window=20, signal_window=5),
        )
        self.assertLessEqual(research.index.max(), audit.RESEARCH_END)
        self.assertLessEqual(pd.Timestamp(research["target_end"].max()), audit.RESEARCH_TARGET_END)

    def test_spearman_matches_pandas_with_ties(self) -> None:
        x = np.array([[1, 1, 2, 3, 3, 4, 5, 5, 6]], dtype=float)
        y = np.array([[2, 3, 1, 4, 4, 6, 5, 5, 7]], dtype=float)
        expected = pd.Series(x[0]).rank().corr(pd.Series(y[0]).rank())
        self.assertAlmostEqual(audit.mean_spearman(x, y), expected, places=15)

    def test_drawdowns_are_reported_separately(self) -> None:
        net = pd.Series([0.10, -0.20, 0.05])
        frozen, conventional = audit.drawdowns(net)
        self.assertAlmostEqual(frozen, -0.20)
        self.assertAlmostEqual(conventional, np.exp(-0.20) - 1.0)
        self.assertNotEqual(frozen, conventional)


if __name__ == "__main__":
    unittest.main()
