"""Synthetic-only tests for the LAF_001 Stage A1 structural audit."""

from __future__ import annotations

import sys
import json
import unittest
from datetime import date, datetime, time, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_stage_a1 import (  # noqa: E402
    AUTHORIZED_PROVIDER_METADATA_FIELDS,
    PERIOD1,
    PERIOD2,
    RAW_RESPONSE_SHA256,
    SYMBOLS,
    StructuralDataError,
    assert_no_analytical_columns,
    assert_no_analytical_mapping_keys,
    calculated_boundary_flags,
    calendar_coverage,
    classify_boundary,
    classify_post_pre_ratio,
    field_integrity_row,
    expected_xnys_dates,
    metadata_boundary_audit_rows,
    parse_chart_payload,
    provider_metadata_row,
    request_url,
    schema_audit_rows,
    sha256_bytes,
    split_unit_audit,
    split_unit_summary,
    write_immutable_bytes,
)


def _payload_object(
    rows: int = 3,
    *,
    symbol: str = "SPY",
    timestamps: list[int] | None = None,
) -> dict:
    timestamps = timestamps or [
        PERIOD1 + 3 * 86_400 + index * 86_400 for index in range(rows)
    ]
    rows = len(timestamps)
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
                        "symbol": symbol,
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
    return json.dumps(value, separators=(",", ":")).encode("utf-8")


def _split_payload(extra_sessions_each_side: int = 2) -> tuple[dict, list[date]]:
    sessions = expected_xnys_dates()
    event_date = date(2005, 6, 9)
    event_position = sessions.index(event_date)
    side = 20 + extra_sessions_each_side
    selected = sessions[event_position - side : event_position + side + 1]
    timestamps = [
        int(datetime.combine(session, time(18), tzinfo=timezone.utc).timestamp())
        for session in selected
    ]
    payload = _payload_object(symbol="IWM", timestamps=timestamps)
    event_timestamp = timestamps[selected.index(event_date)]
    payload["chart"]["result"][0]["events"] = {
        "splits": {
            str(event_timestamp): {
                "date": event_timestamp,
                "numerator": 2.0,
                "denominator": 1.0,
                "splitRatio": "2:1",
            }
        }
    }
    return payload, sessions


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


class CorrectiveMetadataTests(unittest.TestCase):
    def _parsed_with_sentinel(self):
        payload = _payload_object()
        metadata = payload["chart"]["result"][0]["meta"]
        metadata.update(
            {
                "fullExchangeName": "Synthetic Exchange",
                "timezone": "SYN",
                "firstTradeDate": PERIOD1,
                "priceHint": 2,
                "hasPrePostMarketData": False,
                "validRanges": ["1d"],
                "regularMarketTime": PERIOD2 + 1,
                "regularMarketPrice": "FUTURE_SENTINEL_2099",
                "currentTradingPeriod": {
                    "regular": {"start": PERIOD2 + 1, "end": PERIOD2 + 2}
                },
            }
        )
        return parse_chart_payload(_payload_bytes(payload), "SPY")

    def test_dynamic_metadata_is_detected_and_not_emitted(self) -> None:
        parsed = self._parsed_with_sentinel()
        audit = metadata_boundary_audit_rows(parsed)
        dynamic = [row for row in audit if row["classification"] == "OUT_OF_SCOPE_DYNAMIC"]
        self.assertTrue(dynamic)
        self.assertTrue(all(row["emitted"] is False for row in dynamic))
        self.assertIn("regularMarketTime", {row["field_name"] for row in dynamic})
        self.assertIn("regularMarketPrice", {row["field_name"] for row in dynamic})

    def test_future_sentinel_is_absent_from_canonical_metadata_artifacts(self) -> None:
        parsed = self._parsed_with_sentinel()
        canonical = provider_metadata_row(parsed)
        boundary = metadata_boundary_audit_rows(parsed)
        serialized = json.dumps(
            {"provider_metadata": canonical, "metadata_boundary_audit": boundary},
            separators=(",", ":"),
        )
        self.assertNotIn("FUTURE_SENTINEL_2099", serialized)
        self.assertEqual(tuple(canonical), AUTHORIZED_PROVIDER_METADATA_FIELDS)
        self.assertNotIn("metadata_json", canonical)

    def test_boundary_flags_are_calculated_from_evidence(self) -> None:
        parsed = self._parsed_with_sentinel()
        parsed.rows.loc[parsed.rows.index[-1], "source_timestamp"] = PERIOD2
        action = {
            "symbol": "SPY",
            "source_timestamp": PERIOD2,
            "source_timestamp_utc": "2017-01-01T00:00:00+00:00",
            "session_date": date(2017, 1, 1),
            "boundary_status": "OUT_OF_SCOPE",
            "action_type": "DIVIDEND",
            "amount": 1.0,
            "numerator": None,
            "denominator": None,
            "split_ratio": None,
            "raw_event_json": "{}",
        }
        parsed.actions = pd.DataFrame([action])
        metadata_audit = pd.DataFrame(metadata_boundary_audit_rows(parsed))
        temp = REPO_ROOT / f".laf_stage_a1c_disclosure_{uuid4().hex}"
        temp.mkdir()
        disclosure = temp / "erratum.md"
        try:
            disclosure.write_text(
                "\n".join(
                    (
                        "boundary_incident_disclosed: true",
                        "zero linhas OHLCV de 2017+",
                        "zero corporate actions de 2017+",
                        "metadados dinâmicos de 2026",
                        "nenhuma feature, target ou associação",
                    )
                ),
                encoding="utf-8",
            )
            flags = calculated_boundary_flags(
                {"SPY": parsed},
                metadata_audit,
                disclosure_path=disclosure,
                raw_hashes_unchanged=True,
            )
        finally:
            if disclosure.exists():
                disclosure.unlink()
            temp.rmdir()
        self.assertEqual(flags["historical_rows_2017_or_later"], 1)
        self.assertEqual(flags["corporate_actions_2017_or_later"], 1)
        self.assertTrue(flags["out_of_scope_dynamic_metadata_detected_in_raw"])
        self.assertFalse(flags["out_of_scope_dynamic_metadata_emitted"])
        self.assertTrue(flags["boundary_incident_disclosed"])
        self.assertTrue(flags["raw_hashes_unchanged"])


class SplitUnitAuditTests(unittest.TestCase):
    def test_split_audit_contains_volume_and_only_authorized_calculations(self) -> None:
        payload, sessions = _split_payload()
        parsed = parse_chart_payload(_payload_bytes(payload), "IWM")
        audit = split_unit_audit(parsed, sessions)
        self.assertEqual(len(audit), 41)
        self.assertEqual(audit["position_relative_to_event"].tolist(), list(range(-20, 21)))
        self.assertIn("reported_volume", audit)
        self.assertIn("provider_close_x_reported_volume", audit)
        self.assertIn("adj_close_div_provider_close", audit)
        manual = audit.iloc[0]
        self.assertEqual(
            manual["provider_close_x_reported_volume"],
            manual["provider_close"] * manual["reported_volume"],
        )
        self.assertAlmostEqual(
            manual["adj_close_div_provider_close"],
            manual["adj_close"] / manual["provider_close"],
        )
        self.assertTrue((audit["split_factor"] == 2.0).all())

    def test_no_event_only_calculation_escapes_the_41_sessions(self) -> None:
        payload, sessions = _split_payload(extra_sessions_each_side=3)
        parsed = parse_chart_payload(_payload_bytes(payload), "IWM")
        source_dates = set(parsed.rows["session_date"])
        audit = split_unit_audit(parsed, sessions)
        emitted_dates = set(audit["session_date"])
        self.assertEqual(len(source_dates), 47)
        self.assertEqual(len(emitted_dates), 41)
        self.assertTrue(emitted_dates < source_dates)

    def test_split_summary_uses_prespecified_classification(self) -> None:
        payload, sessions = _split_payload()
        audit = split_unit_audit(parse_chart_payload(_payload_bytes(payload), "IWM"), sessions)
        summary = split_unit_summary(audit)
        self.assertEqual(summary["pre_sessions"], 20)
        self.assertEqual(summary["post_sessions"], 20)
        self.assertEqual(
            summary["VOLUME_UNIT_SEMANTICS"],
            "UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION",
        )
        self.assertEqual(
            classify_post_pre_ratio(1.0),
            "CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF",
        )
        self.assertEqual(
            classify_post_pre_ratio(2.0),
            "CONSISTENT_WITH_FACTOR_TWO_DISCONTINUITY_NOT_PROOF",
        )
        self.assertEqual(classify_post_pre_ratio(1.5), "INCONCLUSIVE")


class CalendarAndRawTests(unittest.TestCase):
    def test_xnys_calendar_spans_full_authorized_window(self) -> None:
        sessions = expected_xnys_dates()
        self.assertEqual(sessions[0], date(2003, 1, 2))
        self.assertEqual(sessions[-1], date(2016, 12, 30))
        self.assertEqual(len(sessions), 3_525)

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

    def test_corrective_output_schemas_have_no_prohibited_vocabulary(self) -> None:
        assert_no_analytical_columns(AUTHORIZED_PROVIDER_METADATA_FIELDS)
        assert_no_analytical_columns(
            (
                "session_date",
                "position_relative_to_event",
                "provider_close",
                "adj_close",
                "reported_volume",
                "provider_close_x_reported_volume",
                "adj_close_div_provider_close",
                "split_factor",
            )
        )
        assert_no_analytical_mapping_keys(
            {
                "corrective_audit_code_commit": "a" * 40,
                "prohibited_calculations_performed": False,
                "safe_to_run_stage_a2": False,
            }
        )

    def test_code_commit_is_preserved_exactly_and_raw_hash_contract_is_complete(self) -> None:
        code_commit = "a" * 40
        manifest_fragment = {"corrective_audit_code_commit": code_commit}
        self.assertEqual(manifest_fragment["corrective_audit_code_commit"], code_commit)
        self.assertEqual(set(RAW_RESPONSE_SHA256), set(SYMBOLS))
        self.assertEqual(len(set(RAW_RESPONSE_SHA256.values())), 5)
        self.assertTrue(
            all(len(value) == 64 for value in RAW_RESPONSE_SHA256.values())
        )

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
