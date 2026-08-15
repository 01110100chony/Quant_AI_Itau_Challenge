from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
import json

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_a import (  # noqa: E402
    assert_research_dates,
    audit_yahoo_chart_response,
    build_tw_components,
    build_us_components,
    calendar_schedule,
    distribution_us_sessions,
    map_taiwan_windows,
    mapping_integrity,
    load_provider_response,
    load_raw_ohlc,
    parse_twse_stock_samples,
    parse_twse_taiex_responses,
    parse_yahoo_chart_response,
    schedule_from_twse_sessions,
    validate_parsed_ohlc,
)


def _schedule(rows: list[tuple[str, str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "session_date": [date.fromisoformat(row[0]) for row in rows],
            "session_open_utc": pd.to_datetime([row[1] for row in rows], utc=True),
            "session_close_utc": pd.to_datetime([row[2] for row in rows], utc=True),
            "session_duration_minutes": [390.0] * len(rows),
            "early_close": [False] * len(rows),
        }
    )


def _raw(dates: list[str], opens: list[float], closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "session_date": [date.fromisoformat(value) for value in dates],
            "open": opens,
            "close": closes,
            "adj_close": closes,
        }
    )


class ResearchBoundaryTests(unittest.TestCase):
    def test_rejects_validation_date(self) -> None:
        with self.assertRaises(ValueError):
            assert_research_dates(pd.Series([date(2018, 12, 31), date(2019, 1, 2)]), label="test")


class AcquisitionGateTests(unittest.TestCase):
    def test_rejects_misaligned_provider_arrays_before_dataframe(self) -> None:
        timestamps = list(range(1_300_000_000, 1_300_000_101))
        quote = {field: [1.0] * len(timestamps) for field in ("open", "high", "low", "close", "volume")}
        quote["open"] = quote["open"][:-1]
        payload = {
            "chart": {
                "result": [{
                    "meta": {"exchangeTimezoneName": "America/New_York", "dataGranularity": "1d"},
                    "timestamp": timestamps,
                    "indicators": {"quote": [quote], "adjclose": [{"adjclose": [1.0] * len(timestamps)}]},
                }],
                "error": None,
            }
        }
        request = {
            "asset": "XSD",
            "provider_symbol": "XSD",
            "http_status": 200,
            "interval": "1d",
            "expected_timezone": "America/New_York",
        }
        audit = audit_yahoo_chart_response(payload, request)
        self.assertEqual(audit["schema_status"], "INVALID")
        self.assertTrue(any("len(quote.open)" in issue for issue in audit["issues"]))

    def test_rejects_mostly_null_close_response(self) -> None:
        timestamps = list(range(1_300_000_000, 1_300_000_101))
        quote = {field: [1.0] * len(timestamps) for field in ("open", "high", "low", "close", "volume")}
        quote["close"] = [None] * 100 + [1.0]
        payload = {
            "chart": {
                "result": [{
                    "meta": {"exchangeTimezoneName": "America/New_York", "dataGranularity": "1d"},
                    "timestamp": timestamps,
                    "indicators": {"quote": [quote], "adjclose": [{"adjclose": [1.0] * len(timestamps)}]},
                }],
                "error": None,
            }
        }
        request = {
            "asset": "XSD",
            "provider_symbol": "XSD",
            "http_status": 200,
            "interval": "1d",
            "expected_timezone": "America/New_York",
        }
        audit = audit_yahoo_chart_response(payload, request)
        self.assertEqual(audit["snapshot_status"], "INVALID")
        self.assertTrue(any("below acquisition gate" in issue for issue in audit["issues"]))


class CalendarTests(unittest.TestCase):
    def test_calendar_timestamps_are_aware_and_dst_changes_utc_open(self) -> None:
        schedule = calendar_schedule("XNYS")
        self.assertIsNotNone(schedule["session_open_utc"].dt.tz)
        before = schedule.loc[schedule["session_date"] == date(2018, 3, 9), "session_open_utc"].iloc[0]
        after = schedule.loc[schedule["session_date"] == date(2018, 3, 12), "session_open_utc"].iloc[0]
        self.assertEqual(before.hour, 14)
        self.assertEqual(after.hour, 13)


class ComponentTests(unittest.TestCase):
    def test_manual_log_return_components(self) -> None:
        us_schedule = _schedule([("2018-01-02", "2018-01-02T14:30:00Z", "2018-01-02T21:00:00Z")])
        raw = {
            "XSD": _raw(["2018-01-02"], [100.0], [110.0]),
            "QQQ": _raw(["2018-01-02"], [100.0], [105.0]),
            "SPY": _raw(["2018-01-02"], [100.0], [102.0]),
        }
        components = build_us_components(us_schedule, raw)
        self.assertAlmostEqual(components.loc[0, "semi_specific"], np.log(1.10) - np.log(1.05))
        self.assertAlmostEqual(components.loc[0, "broad_tech"], np.log(1.05) - np.log(1.02))

    def test_manual_taiwan_target_components(self) -> None:
        tw_schedule = _schedule(
            [
                ("2018-01-02", "2018-01-02T01:00:00Z", "2018-01-02T05:30:00Z"),
                ("2018-01-03", "2018-01-03T01:00:00Z", "2018-01-03T05:30:00Z"),
            ]
        )
        raw = {
            "0052": _raw(["2018-01-02", "2018-01-03"], [50.0, 52.0], [51.0, 53.0]),
            "TAIEX": _raw(["2018-01-02", "2018-01-03"], [100.0, 103.0], [102.0, 104.0]),
            "0050": _raw(["2018-01-02", "2018-01-03"], [75.0, 76.0], [75.5, 76.5]),
        }
        components = build_tw_components(tw_schedule, raw)
        self.assertAlmostEqual(components.loc[1, "gap_0052"], np.log(52.0 / 51.0))
        self.assertAlmostEqual(components.loc[1, "intraday_TAIEX"], np.log(104.0 / 103.0))


class MappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tw = _schedule(
            [
                ("2018-01-02", "2018-01-02T01:00:00Z", "2018-01-02T05:30:00Z"),
                ("2018-01-05", "2018-01-05T01:00:00Z", "2018-01-05T05:30:00Z"),
                ("2018-01-06", "2018-01-06T01:00:00Z", "2018-01-06T05:30:00Z"),
            ]
        )
        us_schedule = _schedule(
            [
                ("2018-01-02", "2018-01-02T14:30:00Z", "2018-01-02T21:00:00Z"),
                ("2018-01-03", "2018-01-03T14:30:00Z", "2018-01-03T21:00:00Z"),
            ]
        )
        raw = {
            "XSD": _raw(["2018-01-02", "2018-01-03"], [100.0] * 2, [101.0, 102.0]),
            "QQQ": _raw(["2018-01-02", "2018-01-03"], [100.0] * 2, [100.5, 101.0]),
            "SPY": _raw(["2018-01-02", "2018-01-03"], [100.0] * 2, [100.2, 100.4]),
        }
        self.us = build_us_components(us_schedule, raw)

    def test_multiple_sessions_sum_and_empty_window(self) -> None:
        mapping = map_taiwan_windows(self.tw, self.us)
        self.assertEqual(mapping.loc[1, "n_us_sessions"], 2)
        expected = self.us.loc[self.us["session_date"].isin([date(2018, 1, 2), date(2018, 1, 3)]), "semi_specific"].sum()
        self.assertAlmostEqual(mapping.loc[1, "semi_specific_sum"], expected)
        self.assertEqual(mapping.loc[2, "n_us_sessions"], 0)
        self.assertTrue(np.isnan(mapping.loc[2, "semi_specific_sum"]))
        self.assertEqual(distribution_us_sessions(mapping), {"0": 2, "1": 0, "2": 1, "3+": 0})

    def test_mapping_is_strict_unique_and_future_invariant(self) -> None:
        mapping = map_taiwan_windows(self.tw, self.us)
        integrity = mapping_integrity(mapping)
        self.assertEqual(integrity["duplicated_taiwan_targets"], 0)
        self.assertEqual(integrity["timestamp_violations"], 0)
        self.assertEqual(integrity["ambiguous_mappings"], 0)

        future = self.us.iloc[[-1]].copy()
        future["session_date"] = date(2018, 1, 8)
        future["session_open_utc"] = pd.Timestamp("2018-01-08T14:30:00Z")
        future["session_close_utc"] = pd.Timestamp("2018-01-08T21:00:00Z")
        extended = pd.concat([self.us, future], ignore_index=True)
        remapped = map_taiwan_windows(self.tw, extended)
        pd.testing.assert_series_equal(mapping["n_us_sessions"], remapped["n_us_sessions"])
        pd.testing.assert_series_equal(mapping["semi_specific_sum"], remapped["semi_specific_sum"])


YAHOO_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "yahoo_chart_2007_2018_v2"
TWSE_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "twse_official_audit_2007_2018"
REAL_DATA_AVAILABLE = (YAHOO_ROOT / "XSD_response.json").exists() and (
    TWSE_ROOT / "TAIEX_20181201.json"
).exists()


@unittest.skipUnless(REAL_DATA_AVAILABLE, "CM_001 Stage A raw snapshots are not present")
class RealDataInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.yahoo = {}
        timezones = {
            "XSD": "America/New_York",
            "QQQ": "America/New_York",
            "SPY": "America/New_York",
            "0052": "Asia/Taipei",
            "TAIEX": "Asia/Taipei",
            "0050": "Asia/Taipei",
        }
        for asset, timezone in timezones.items():
            request = json.loads(
                (YAHOO_ROOT / f"{asset}_request.json").read_text(encoding="utf-8-sig")
            )
            payload = load_provider_response(YAHOO_ROOT / f"{asset}_response.json")
            audit = audit_yahoo_chart_response(payload, request)
            frame, _ = parse_yahoo_chart_response(payload, audit, timezone)
            cls.yahoo[asset] = frame.loc[frame["session_date"] >= date(2010, 1, 1)].copy()
        cls.taiex = parse_twse_taiex_responses(list(TWSE_ROOT.glob("TAIEX_????????.json")))
        cls.taiex = cls.taiex.loc[cls.taiex["session_date"] >= date(2010, 1, 1)].copy()
        cls.tw_schedule = schedule_from_twse_sessions(cls.taiex)
        cls.us_schedule = calendar_schedule("XNYS")
        cls.us = build_us_components(cls.us_schedule, cls.yahoo)
        cls.mapping = map_taiwan_windows(cls.tw_schedule, cls.us)

    def test_raw_response_arrays_are_aligned_before_dataframe(self) -> None:
        for asset in self.yahoo:
            request = json.loads(
                (YAHOO_ROOT / f"{asset}_request.json").read_text(encoding="utf-8-sig")
            )
            audit = audit_yahoo_chart_response(
                load_provider_response(YAHOO_ROOT / f"{asset}_response.json"), request
            )
            self.assertEqual(audit["schema_status"], "VALID")
            self.assertEqual(audit["timestamp_unit"], "seconds")
            self.assertTrue(
                all(
                    stats["array_length"] == audit["timestamp_count"]
                    for stats in audit["fields"].values()
                )
            )

    def test_legacy_locale_csv_is_rejected_instead_of_silently_coerced(self) -> None:
        legacy = REPO_ROOT / "data" / "raw" / "cm_001" / "yahoo_chart_2007_2018" / "XSD_ohlc.csv"
        with self.assertRaisesRegex(ValueError, "parser would create"):
            load_raw_ohlc(legacy, "America/New_York")

    def test_official_twse_research_ohlc_and_boundary(self) -> None:
        self.assertEqual(self.taiex["session_date"].min(), date(2010, 1, 4))
        self.assertLess(self.taiex["session_date"].max(), date(2019, 1, 1))
        integrity = validate_parsed_ohlc(self.taiex)
        self.assertEqual(integrity["missing_open"], 0)
        self.assertEqual(integrity["missing_close"], 0)
        self.assertEqual(integrity["impossible_ohlc"], 0)
        follower, _ = parse_twse_stock_samples(
            list(TWSE_ROOT.glob("0052_????????.json")), "0052"
        )
        self.assertTrue((follower["session_date"] < date(2019, 1, 1)).all())
        self.assertGreater(int(follower["open"].isna().sum()), 0)

    def test_real_mapping_is_aware_unique_and_strict(self) -> None:
        self.assertIsNotNone(self.tw_schedule["session_open_utc"].dt.tz)
        integrity = mapping_integrity(self.mapping)
        self.assertEqual(integrity["duplicated_taiwan_targets"], 0)
        self.assertEqual(integrity["timestamp_violations"], 0)
        self.assertEqual(integrity["ambiguous_mappings"], 0)
        self.assertFalse(self.mapping["mapping_status"].eq("DATA_MISSING").any())

    def test_real_mapping_has_empty_multiple_and_early_close_cases(self) -> None:
        self.assertTrue(self.mapping["mapping_status"].eq("EMPTY_US_WINDOW").any())
        self.assertTrue(self.mapping["n_us_sessions"].ge(2).any())
        self.assertTrue(self.mapping["us_early_close_sessions"].gt(0).any())

    def test_real_mapping_is_future_invariant(self) -> None:
        cutoff = date(2017, 12, 31)
        past_tw = self.tw_schedule.loc[self.tw_schedule["session_date"] <= cutoff].copy()
        past_us = self.us.loc[self.us["session_date"] <= cutoff].copy()
        past_mapping = map_taiwan_windows(past_tw, past_us)
        full_past = self.mapping.loc[self.mapping["target_session"] <= cutoff].reset_index(drop=True)
        pd.testing.assert_series_equal(
            past_mapping["n_us_sessions"].reset_index(drop=True),
            full_past["n_us_sessions"],
        )
        pd.testing.assert_series_equal(
            past_mapping["us_session_dates"].reset_index(drop=True),
            full_past["us_session_dates"],
        )


if __name__ == "__main__":
    unittest.main()
