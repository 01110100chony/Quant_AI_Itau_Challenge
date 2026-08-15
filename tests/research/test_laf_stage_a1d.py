"""Synthetic-only tests for the LAF_001 Stage A1d source-unit audit."""

from __future__ import annotations

import io
import json
import shutil
import sys
import unittest
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from uuid import uuid4

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_stage_a1d_audit import (  # noqa: E402
    ALLOWED_FIELDS,
    AuditOutputs,
    SourceAuditError,
    audit_frames,
    normalize_tiingo_session_date,
    parse_tiingo_payload,
    split_convention,
)
from laf_stage_a1d_collector import (  # noqa: E402
    AcquisitionError,
    acquire_tiingo_eod,
    build_request,
    request_url,
)


@contextmanager
def _workspace_temp():
    path = REPO_ROOT / f".laf_stage_a1d_test_{uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


class _Response:
    def __init__(self, payload: bytes, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None


def _dates() -> list[date]:
    holidays = {date(2005, 5, 30), date(2005, 7, 4)}
    return [value.date() for value in pd.bdate_range("2005-05-11", "2005-07-08") if value.date() not in holidays]


def _frames(split_factor: float = 2.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = _dates()
    assert len(dates) == 41 and dates[20] == date(2005, 6, 9)
    yahoo_rows = []
    tiingo_rows = []
    for position, session in enumerate(dates, start=-20):
        yahoo_close = 100.0 + (position + 20) / 10
        yahoo_volume = 2_000.0 + 2 * (position + 20)
        before = session < date(2005, 6, 9)
        yahoo_rows.append(
            {
                "session_date": session,
                "position_relative_to_event": position,
                "provider_close": yahoo_close,
                "reported_volume": yahoo_volume,
            }
        )
        tiingo_rows.append(
            {
                "session_date": session,
                "tiingo_close": yahoo_close * (2.0 if before else 1.0),
                "tiingo_volume": yahoo_volume / (2.0 if before else 1.0),
                "tiingo_split_factor": split_factor if position == 0 else 1.0,
            }
        )
    return pd.DataFrame(yahoo_rows), pd.DataFrame(tiingo_rows)


def _audit(split_factor: float = 2.0) -> AuditOutputs:
    yahoo, tiingo = _frames(split_factor)
    return audit_frames(
        yahoo,
        tiingo,
        raw_sha256="0" * 64,
        payload_size_bytes=100,
        acquired_at_utc="2026-08-15T12:00:00+00:00",
        http_status=200,
        attempt_count=1,
        retrieval_id="20260815T120000000Z",
        h0_a1d_commit="1" * 40,
    )


class CollectorContractTests(unittest.TestCase):
    def test_token_is_header_only_and_url_is_literal(self) -> None:
        request = build_request("synthetic-secret")
        self.assertEqual(request.get_header("Authorization"), "Token synthetic-secret")
        self.assertNotIn("synthetic-secret", request.full_url)
        self.assertEqual(
            request_url(),
            "https://api.tiingo.com/tiingo/daily/IWM/prices?startDate=2005-05-11&endDate=2005-07-08",
        )

    def test_transport_failure_allows_exactly_one_retry(self) -> None:
        calls = []

        def opener(_request, **_kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise TimeoutError()
            return _Response(b"[]")

        with _workspace_temp() as temp:
            outcome = acquire_tiingo_eod(
                temp / "private", "synthetic-secret", opener=opener
            )
            self.assertEqual(outcome.attempt_count, 2)
            self.assertEqual(len(calls), 2)
            receipts = list(outcome.private_dir.glob("attempt_*_receipt.json"))
            self.assertEqual(len(receipts), 2)
            self.assertNotIn("synthetic-secret", "".join(p.read_text() for p in receipts))

    def test_non_retryable_http_stops_after_one_attempt(self) -> None:
        calls = []

        def opener(request, **_kwargs):
            calls.append(1)
            raise HTTPError(request.full_url, 400, "bad", {}, io.BytesIO(b"bad"))

        with _workspace_temp() as temp:
            with self.assertRaisesRegex(AcquisitionError, "non-retryable"):
                acquire_tiingo_eod(temp / "private", "synthetic-secret", opener=opener)
        self.assertEqual(len(calls), 1)


class ParserAndTimezoneTests(unittest.TestCase):
    def test_extracts_only_authorized_fields(self) -> None:
        payload = json.dumps(
            [
                {
                    "date": "2005-05-11T00:00:00.000Z",
                    "close": 200.0,
                    "volume": 1_000,
                    "splitFactor": 1.0,
                    "private_extra": 999_999,
                }
            ]
        ).encode()
        parsed = parse_tiingo_payload(payload)
        self.assertEqual(
            list(parsed.columns),
            ["session_date", "tiingo_close", "tiingo_volume", "tiingo_split_factor"],
        )
        self.assertEqual(ALLOWED_FIELDS, ("date", "close", "volume", "splitFactor"))

    def test_date_label_uses_valid_iso_and_authorized_boundary(self) -> None:
        self.assertEqual(
            normalize_tiingo_session_date("2005-06-09T00:00:00.000Z"),
            date(2005, 6, 9),
        )
        with self.assertRaisesRegex(SourceAuditError, "outside"):
            normalize_tiingo_session_date("2005-05-10T00:00:00.000Z")

    def test_duplicate_date_is_content_failure(self) -> None:
        row = {"date": "2005-05-11T00:00:00Z", "close": 1, "volume": 1, "splitFactor": 1}
        with self.assertRaisesRegex(SourceAuditError, "duplicate"):
            parse_tiingo_payload(json.dumps([row, row]).encode())


class FrozenGateTests(unittest.TestCase):
    def test_direct_split_convention_and_all_gates_pass(self) -> None:
        outputs = _audit(2.0)
        self.assertEqual(outputs.summary["split_factor_convention"], "DIRECT_TWO_FOR_ONE")
        self.assertTrue(outputs.summary["all_gates_pass"])
        self.assertTrue(all(item["pass"] for item in outputs.gates.values()))
        self.assertNotIn("metrics", outputs.summary)
        self.assertNotIn("price_mape_pre", json.dumps(outputs.gates))

    def test_reciprocal_split_convention_is_mechanical(self) -> None:
        outputs = _audit(0.5)
        self.assertEqual(
            outputs.summary["split_factor_convention"], "RECIPROCAL_HALF_REPORTED"
        )
        self.assertTrue(outputs.gates["SplitEventPass"]["pass"])

    def test_manual_first_pre_row_mapping(self) -> None:
        outputs = _audit()
        row = outputs.private_comparison.iloc[0]
        self.assertEqual(row["tiingo_split_close"], row["provider_close"])
        self.assertEqual(row["tiingo_split_volume"], row["reported_volume"])
        self.assertEqual(
            row["tiingo_raw_dollar_volume"], row["yahoo_dollar_volume"]
        )

    def test_invalid_event_factor_fails_split_gate_without_rescue(self) -> None:
        outputs = _audit(3.0)
        self.assertFalse(outputs.gates["SplitEventPass"]["pass"])
        self.assertEqual(outputs.summary["VOLUME_UNIT_SEMANTICS"], "UNRESOLVED")
        self.assertEqual(outputs.summary["SAFE_TO_RUN_LAF_STAGE_A2"], "NO")

    def test_multiple_non_unit_events_fail(self) -> None:
        _, tiingo = _frames()
        tiingo.loc[0, "tiingo_split_factor"] = 2.0
        convention, factor, count, passed = split_convention(tiingo)
        self.assertEqual(convention, "INVALID_EVENT_PATTERN")
        self.assertIsNone(factor)
        self.assertEqual(count, 2)
        self.assertFalse(passed)


class RepositoryContainmentTests(unittest.TestCase):
    def test_private_ignore_rule_is_exact(self) -> None:
        lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("/data/private/laf_001/", lines)


if __name__ == "__main__":
    unittest.main()
