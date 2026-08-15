"""Synthetic-only tests for the LAF_001 Stage A1 structural audit."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_stage_a1 import (  # noqa: E402
    PERIOD1,
    PERIOD2,
    StructuralDataError,
    assert_no_analytical_columns,
    calendar_coverage,
    classify_boundary,
    field_integrity_row,
    parse_chart_payload,
    request_url,
    schema_audit_rows,
    sha256_bytes,
    write_immutable_bytes,
)


def _payload_object(rows: int = 3) -> dict:
    timestamps = [PERIOD1 + 3 * 86_400 + index * 86_400 for index in range(rows)]
    opens = [100.0 + index for index in range(rows)]
    closes = [100.5 + index for index in range(rows)]
    quote = {
        "open": opens,
        "high": [max(open_, close) + 1.0 for open_, close in zip(opens, closes)],
        "low": [min(open_, close) - 1.0 for open_, close in zip(opens, closes)],
        "close": closes,
        "volume": [1_000 + index for index in range(rows)],
    }
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": "SPY",
                        "currency": "USD",
                        "exchangeName": "PCX",
                        "instrumentType": "ETF",
                        "exchangeTimezoneName": "America/New_York",
                        "gmtoffset": -18_000,
                        "dataGranularity": "1d",
                    },
                    "timestamp": timestamps,
                    "indicators": {
                        "quote": [quote],
                        "adjclose": [
                            {"adjclose": [90.0 + index for index in range(rows)]}
                        ],
                    },
                    "events": {},
                }
            ],
            "error": None,
        }
    }


def _payload_bytes(value: dict) -> bytes:
    import json

    return json.dumps(value, separators=(",", ":")).encode("utf-8")


class BoundaryAndSchemaTests(unittest.TestCase):
    def test_rejects_timestamp_in_2017_or_later(self) -> None:
        payload = _payload_object()
        payload["chart"]["result"][0]["timestamp"][-1] = PERIOD2
        with self.assertRaisesRegex(StructuralDataError, "2017 or later"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_rejects_timestamp_before_2003(self) -> None:
        payload = _payload_object()
        payload["chart"]["result"][0]["timestamp"][0] = PERIOD1 - 1
        with self.assertRaisesRegex(StructuralDataError, "before 2003"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_rejects_incompatible_array_lengths(self) -> None:
        payload = _payload_object()
        payload["chart"]["result"][0]["indicators"]["quote"][0]["open"].pop()
        with self.assertRaisesRegex(StructuralDataError, "does not match timestamp"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_rejects_duplicate_timestamps(self) -> None:
        payload = _payload_object()
        timestamps = payload["chart"]["result"][0]["timestamp"]
        timestamps[1] = timestamps[0]
        with self.assertRaisesRegex(StructuralDataError, "duplicate timestamps"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_rejects_non_monotonic_timestamps(self) -> None:
        payload = _payload_object()
        timestamps = payload["chart"]["result"][0]["timestamp"]
        timestamps[1], timestamps[2] = timestamps[2], timestamps[1]
        with self.assertRaisesRegex(StructuralDataError, "not strictly increasing"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_schema_audit_reports_presence_type_and_length(self) -> None:
        payload = _payload_object()
        rows = schema_audit_rows(payload, "SPY")
        volume = next(row for row in rows if row["field"] == "volume")
        self.assertTrue(volume["present"])
        self.assertEqual(volume["provider_type"], "array")
        self.assertEqual(volume["array_length"], 3)


class FieldIntegrityTests(unittest.TestCase):
    def _audit(self, mutate) -> dict:
        payload = _payload_object()
        mutate(payload["chart"]["result"][0]["indicators"])
        parsed = parse_chart_payload(_payload_bytes(payload), "SPY")
        return field_integrity_row(parsed)

    def test_detects_high_below_open_or_close(self) -> None:
        row = self._audit(lambda indicators: indicators["quote"][0]["high"].__setitem__(0, 99.0))
        self.assertEqual(row["high_below_open_or_close"], 1)

    def test_detects_low_above_open_or_close(self) -> None:
        row = self._audit(lambda indicators: indicators["quote"][0]["low"].__setitem__(0, 102.0))
        self.assertEqual(row["low_above_open_or_close"], 1)

    def test_detects_high_below_low(self) -> None:
        def mutate(indicators) -> None:
            indicators["quote"][0]["high"][0] = 99.0
            indicators["quote"][0]["low"][0] = 101.0

        row = self._audit(mutate)
        self.assertEqual(row["high_below_low"], 1)

    def test_classifies_null_zero_and_negative_prices(self) -> None:
        def mutate(indicators) -> None:
            indicators["quote"][0]["open"] = [None, 0.0, -1.0]

        row = self._audit(mutate)
        self.assertEqual(row["open_null"], 1)
        self.assertEqual(row["open_zero"], 1)
        self.assertEqual(row["open_negative"], 1)

    def test_classifies_null_and_zero_volume(self) -> None:
        def mutate(indicators) -> None:
            indicators["quote"][0]["volume"] = [None, 0, 1_000]

        row = self._audit(mutate)
        self.assertEqual(row["volume_null"], 1)
        self.assertEqual(row["volume_zero"], 1)


class CorporateActionAndSeparationTests(unittest.TestCase):
    def test_classifies_action_inside_and_outside_boundary(self) -> None:
        self.assertEqual(classify_boundary(PERIOD1), "IN_SCOPE")
        self.assertEqual(classify_boundary(PERIOD2 - 1), "IN_SCOPE")
        self.assertEqual(classify_boundary(PERIOD2), "OUT_OF_SCOPE")

        payload = _payload_object()
        result = payload["chart"]["result"][0]
        result["events"] = {
            "dividends": {
                str(PERIOD2): {"date": PERIOD2, "amount": 1.0}
            }
        }
        with self.assertRaisesRegex(StructuralDataError, "corporate action is outside"):
            parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_preserves_close_and_adjusted_close_separately(self) -> None:
        parsed = parse_chart_payload(_payload_bytes(_payload_object()), "SPY")
        self.assertEqual(parsed.rows.loc[0, "close"], 100.5)
        self.assertEqual(parsed.rows.loc[0, "adj_close"], 90.0)
        self.assertNotEqual(parsed.rows.loc[0, "close"], parsed.rows.loc[0, "adj_close"])

    def test_preserves_corporate_action_exact_json(self) -> None:
        payload = _payload_object()
        timestamp = payload["chart"]["result"][0]["timestamp"][1]
        payload["chart"]["result"][0]["events"] = {
            "dividends": {
                str(timestamp): {"date": timestamp, "amount": 1.25}
            }
        }
        parsed = parse_chart_payload(_payload_bytes(payload), "SPY")
        self.assertEqual(parsed.actions.loc[0, "action_type"], "DIVIDEND")
        self.assertIn('"amount":1.25', parsed.actions.loc[0, "raw_event_json"])


class CalendarAndRawTests(unittest.TestCase):
    def test_enumerates_missing_and_extra_sessions(self) -> None:
        expected = [date(2003, 1, 2), date(2003, 1, 3), date(2003, 1, 6)]
        observed = [date(2003, 1, 2), date(2003, 1, 6), date(2003, 1, 7)]
        coverage, exceptions = calendar_coverage("SPY", observed, expected)
        self.assertEqual(coverage["missing_sessions"], 1)
        self.assertEqual(coverage["extra_sessions"], 1)
        self.assertEqual(
            {(row["session_date"], row["exception_type"]) for row in exceptions},
            {(date(2003, 1, 3), "MISSING"), (date(2003, 1, 7), "EXTRA")},
        )

    def test_preserves_raw_bytes_and_verifies_sha256(self) -> None:
        payload = b'{"chart":{"result":[],"error":null}}'
        temp = REPO_ROOT / f".laf_stage_a1_test_{uuid4().hex}"
        temp.mkdir()
        path = temp / "raw.json"
        try:
            observed = write_immutable_bytes(path, payload)
            self.assertEqual(observed, sha256_bytes(payload))
            self.assertEqual(path.read_bytes(), payload)
            with self.assertRaises(FileExistsError):
                write_immutable_bytes(path, b"replacement")
        finally:
            if path.exists():
                path.unlink()
            temp.rmdir()

    def test_rejects_forbidden_analytical_output_columns(self) -> None:
        assert_no_analytical_columns(
            ["symbol", "open", "adj_close", "volume_zero", "session_date"]
        )
        for forbidden in (
            "return",
            "PI",
            "LAF",
            "RV",
            "TailLoss",
            "target",
            "future_loss",
        ):
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(StructuralDataError):
                    assert_no_analytical_columns([forbidden])

    def test_request_contract_is_literal_and_has_no_yfinance(self) -> None:
        url = request_url("SPY")
        self.assertEqual(
            url,
            "https://query1.finance.yahoo.com/v8/finance/chart/SPY?"
            "interval=1d&period1=1041379200&period2=1483228800&"
            "events=div%2Csplits%2CcapitalGains&includeAdjustedClose=true&"
            "includePrePost=false",
        )
        collector = (
            REPO_ROOT / "scripts" / "acquire_laf001_stage_a1.ps1"
        ).read_text(encoding="utf-8")
        self.assertNotIn("yf.download", collector)
        self.assertNotIn("yfinance", collector.lower())
        self.assertNotIn("auto_adjust", collector.lower())
        self.assertNotIn("repair", collector.lower())


if __name__ == "__main__":
    unittest.main()
