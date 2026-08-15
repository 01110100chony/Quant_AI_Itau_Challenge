"""Corrective structural data and timing audit for LAF_001 Stage A1c.

This module deliberately contains no return, feature, target, predictive or
portfolio calculation. It parses immutable Yahoo Chart API payloads and emits
only provenance, schema, field, timestamp, calendar, corporate-action and the
explicitly authorized 41-session split-unit audits inside the human-approved
2003-2016 boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd


EXPERIMENT_ID = "LAF_001"
PROVIDER = "Yahoo Finance Chart API"
PARSER_VERSION = "laf-stage-a1-v1.0.1"
RAW_ACQUISITION_H0_COMMIT = "01cc8408a83024663cc7cb7d434f82292072a945"
ORIGINAL_RESULTS_COMMIT = "f549a1a8d8e4b06028100b22a450fa0e5c46473b"
SYMBOLS = ("SPY", "QQQ", "IWM", "DIA", "MDY")
RAW_RESPONSE_SHA256 = {
    "SPY": "306c43087e3a33048d29b47746250cfeaca6a0ec69532084d3e12e7cb2393153",
    "QQQ": "1d747eb4f1fc4b7f22e1cfdae40ad4932a9301324c666e101e3bebcd41a9e479",
    "IWM": "ee972d8c9d5ad737370df7f30d4954e8065316218ae08d64430f28b9f3feb0b3",
    "DIA": "30f7b0370a61be244cd0425602c7c4821dbc4ddef9d3598e267f6aaf8e6fbe53",
    "MDY": "5dba651a9fa9100ef740eaa27f4a8221b63371a8a44b22b1bf29113a46a41fc5",
}
PERIOD1 = 1_041_379_200
PERIOD2 = 1_483_228_800
START_UTC = datetime(2003, 1, 1, tzinfo=timezone.utc)
END_UTC_EXCLUSIVE = datetime(2017, 1, 1, tzinfo=timezone.utc)
START_DATE = date(2003, 1, 1)
END_DATE = date(2016, 12, 31)
ENDPOINT = "https://query1.finance.yahoo.com/v8/finance/chart"
REQUEST_PARAMETERS: tuple[tuple[str, str], ...] = (
    ("interval", "1d"),
    ("period1", str(PERIOD1)),
    ("period2", str(PERIOD2)),
    ("events", "div,splits,capitalGains"),
    ("includeAdjustedClose", "true"),
    ("includePrePost", "false"),
)
PRICE_FIELDS = ("open", "high", "low", "close", "adj_close")
QUOTE_FIELDS = ("open", "high", "low", "close", "volume")
FORBIDDEN_ANALYTICAL_TOKENS = {
    "association",
    "feature",
    "return",
    "returns",
    "pi",
    "laf",
    "rv",
    "tailloss",
    "target",
    "futureloss",
}
AUTHORIZED_PROVIDER_METADATA_FIELDS = (
    "symbol",
    "currency",
    "exchangeName",
    "fullExchangeName",
    "instrumentType",
    "exchangeTimezoneName",
    "timezone",
    "gmtoffset",
    "dataGranularity",
    "firstTradeDate",
    "priceHint",
    "hasPrePostMarketData",
    "validRanges",
)
SPLIT_SYMBOL = "IWM"
SPLIT_EVENT_DATE = date(2005, 6, 9)
SPLIT_WINDOW_SESSIONS_EACH_SIDE = 20


class StructuralDataError(ValueError):
    """Raised when a payload violates a non-repairable Stage A1 contract."""


@dataclass
class ParsedSymbol:
    """Provider fields preserved for one symbol without analytical transforms."""

    symbol: str
    metadata: dict[str, Any]
    rows: pd.DataFrame
    actions: pd.DataFrame


def request_url(symbol: str) -> str:
    """Return the literal authorized Yahoo Chart API URL for one symbol."""
    if symbol not in SYMBOLS:
        raise StructuralDataError(f"unauthorized symbol: {symbol}")
    query = (
        "interval=1d&period1=1041379200&period2=1483228800&"
        "events=div%2Csplits%2CcapitalGains&includeAdjustedClose=true&"
        "includePrePost=false"
    )
    return f"{ENDPOINT}/{symbol}?{query}"


def sha256_bytes(payload: bytes) -> str:
    """Return the lowercase SHA-256 digest of exact bytes."""
    return hashlib.sha256(payload).hexdigest()


def write_immutable_bytes(path: Path, payload: bytes) -> str:
    """Create a byte-for-byte artifact once and return its SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    persisted = path.read_bytes()
    if persisted != payload:
        raise StructuralDataError(f"raw payload changed while persisting {path}")
    return sha256_bytes(persisted)


def verify_raw_payload(path: Path, expected_sha256: str) -> bytes:
    """Read immutable raw bytes and reject any hash mismatch."""
    payload = path.read_bytes()
    observed = sha256_bytes(payload)
    if observed != expected_sha256:
        raise StructuralDataError(
            f"SHA-256 mismatch for {path}: expected {expected_sha256}, observed {observed}"
        )
    return payload


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def decode_payload(payload: bytes) -> dict[str, Any]:
    """Decode a JSON object without changing the preserved raw payload."""
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StructuralDataError(f"payload is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise StructuralDataError("payload root must be an object")
    return decoded


def schema_audit_rows(payload: Mapping[str, Any], symbol: str) -> list[dict[str, Any]]:
    """Describe presence, type and array length of required provider fields."""
    rows: list[dict[str, Any]] = []

    def add(location: str, field: str, container: Any) -> Any:
        present = isinstance(container, Mapping) and field in container
        value = container.get(field) if present else None
        rows.append(
            {
                "symbol": symbol,
                "location": location,
                "field": field,
                "present": bool(present),
                "provider_type": _type_name(value) if present else "missing",
                "array_length": len(value) if isinstance(value, list) else None,
            }
        )
        return value

    chart = add("root", "chart", payload)
    result_container = add("chart", "result", chart)
    add("chart", "error", chart)
    result = (
        result_container[0]
        if isinstance(result_container, list)
        and len(result_container) == 1
        and isinstance(result_container[0], dict)
        else None
    )
    add("chart.result[0]", "meta", result)
    add("chart.result[0]", "timestamp", result)
    indicators = add("chart.result[0]", "indicators", result)
    quote_container = add("indicators", "quote", indicators)
    adj_container = add("indicators", "adjclose", indicators)
    quote = (
        quote_container[0]
        if isinstance(quote_container, list)
        and len(quote_container) == 1
        and isinstance(quote_container[0], dict)
        else None
    )
    adj = (
        adj_container[0]
        if isinstance(adj_container, list)
        and len(adj_container) == 1
        and isinstance(adj_container[0], dict)
        else None
    )
    for field in QUOTE_FIELDS:
        add("indicators.quote[0]", field, quote)
    add("indicators.adjclose[0]", "adjclose", adj)
    events = add("chart.result[0]", "events", result)
    for field in ("dividends", "splits", "capitalGains"):
        add("events", field, events)
    return rows


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise StructuralDataError(f"{label} must be an object")
    return value


def _require_single_object_array(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], Mapping):
        raise StructuralDataError(f"{label} must contain exactly one object")
    return value[0]


def _require_numeric_array(value: Any, label: str, expected_length: int) -> list[Any]:
    if not isinstance(value, list):
        raise StructuralDataError(f"{label} must be an array")
    if len(value) != expected_length:
        raise StructuralDataError(
            f"{label} length {len(value)} does not match timestamp length {expected_length}"
        )
    for index, item in enumerate(value):
        if item is not None and (isinstance(item, bool) or not isinstance(item, (int, float))):
            raise StructuralDataError(f"{label}[{index}] must be numeric or null")
    return value


def assert_timestamp_boundary(timestamps: Sequence[int], label: str) -> None:
    """Reject every timestamp outside 2003-01-01 through 2016-12-31 UTC."""
    for timestamp in timestamps:
        if timestamp < PERIOD1:
            raise StructuralDataError(f"{label} contains timestamp before 2003: {timestamp}")
        if timestamp >= PERIOD2:
            raise StructuralDataError(f"{label} contains timestamp in 2017 or later: {timestamp}")


def classify_boundary(timestamp: int) -> str:
    """Classify a provider timestamp against the authorized inclusive/exclusive bounds."""
    return "IN_SCOPE" if PERIOD1 <= timestamp < PERIOD2 else "OUT_OF_SCOPE"


def _session_date(timestamp: int, provider_timezone: str) -> date:
    try:
        zone = ZoneInfo(provider_timezone)
    except Exception as exc:  # pragma: no cover - platform zone database failure
        raise StructuralDataError(f"invalid provider timezone: {provider_timezone}") from exc
    return datetime.fromtimestamp(timestamp, timezone.utc).astimezone(zone).date()


def _parse_actions(
    events: Any,
    *,
    symbol: str,
    provider_timezone: str,
) -> pd.DataFrame:
    columns = [
        "symbol",
        "source_timestamp",
        "source_timestamp_utc",
        "session_date",
        "boundary_status",
        "action_type",
        "amount",
        "numerator",
        "denominator",
        "split_ratio",
        "raw_event_json",
    ]
    if events is None:
        return pd.DataFrame(columns=columns)
    event_map = _require_mapping(events, "chart.result[0].events")
    rows: list[dict[str, Any]] = []
    for provider_key, action_type in (
        ("dividends", "DIVIDEND"),
        ("splits", "STOCK_SPLIT"),
        ("capitalGains", "CAPITAL_GAIN"),
    ):
        container = event_map.get(provider_key)
        if container is None:
            continue
        container = _require_mapping(container, f"events.{provider_key}")
        for key, raw_event in container.items():
            raw_event = _require_mapping(raw_event, f"events.{provider_key}.{key}")
            raw_timestamp = raw_event.get("date", key)
            try:
                timestamp = int(raw_timestamp)
            except (TypeError, ValueError) as exc:
                raise StructuralDataError(
                    f"events.{provider_key}.{key} has invalid timestamp"
                ) from exc
            boundary_status = classify_boundary(timestamp)
            if boundary_status != "IN_SCOPE":
                raise StructuralDataError(
                    f"{symbol} corporate action is outside the authorized boundary: {timestamp}"
                )
            rows.append(
                {
                    "symbol": symbol,
                    "source_timestamp": timestamp,
                    "source_timestamp_utc": datetime.fromtimestamp(
                        timestamp, timezone.utc
                    ).isoformat(),
                    "session_date": _session_date(timestamp, provider_timezone),
                    "boundary_status": boundary_status,
                    "action_type": action_type,
                    "amount": raw_event.get("amount"),
                    "numerator": raw_event.get("numerator"),
                    "denominator": raw_event.get("denominator"),
                    "split_ratio": raw_event.get("splitRatio"),
                    "raw_event_json": json.dumps(
                        dict(raw_event), ensure_ascii=False, separators=(",", ":")
                    ),
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["source_timestamp", "action_type"], ignore_index=True
    )


def parse_chart_payload(payload: bytes, expected_symbol: str) -> ParsedSymbol:
    """Parse and strictly bound one immutable Yahoo Chart API payload."""
    root = decode_payload(payload)
    chart = _require_mapping(root.get("chart"), "chart")
    if chart.get("error") is not None:
        raise StructuralDataError(
            f"{expected_symbol} chart.error is non-null: {chart.get('error')!r}"
        )
    result = _require_single_object_array(chart.get("result"), "chart.result")
    metadata = dict(_require_mapping(result.get("meta"), "chart.result[0].meta"))
    provider_symbol = metadata.get("symbol")
    if provider_symbol not in (None, expected_symbol):
        raise StructuralDataError(
            f"provider symbol {provider_symbol!r} does not match {expected_symbol}"
        )
    if metadata.get("dataGranularity") != "1d":
        raise StructuralDataError("provider dataGranularity is not 1d")
    provider_timezone = metadata.get("exchangeTimezoneName")
    if not isinstance(provider_timezone, str) or not provider_timezone:
        raise StructuralDataError("provider exchangeTimezoneName is missing")

    timestamps_raw = result.get("timestamp")
    if not isinstance(timestamps_raw, list) or not timestamps_raw:
        raise StructuralDataError("chart.result[0].timestamp must be a non-empty array")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in timestamps_raw):
        raise StructuralDataError("every timestamp must be an integer")
    timestamps = [int(item) for item in timestamps_raw]
    assert_timestamp_boundary(timestamps, expected_symbol)
    if len(set(timestamps)) != len(timestamps):
        raise StructuralDataError(f"{expected_symbol} contains duplicate timestamps")
    if any(left >= right for left, right in zip(timestamps, timestamps[1:])):
        raise StructuralDataError(f"{expected_symbol} timestamps are not strictly increasing")

    indicators = _require_mapping(result.get("indicators"), "chart.result[0].indicators")
    quote = _require_single_object_array(indicators.get("quote"), "indicators.quote")
    adjusted = _require_single_object_array(
        indicators.get("adjclose"), "indicators.adjclose"
    )
    arrays = {
        field: _require_numeric_array(
            quote.get(field), f"indicators.quote[0].{field}", len(timestamps)
        )
        for field in QUOTE_FIELDS
    }
    arrays["adj_close"] = _require_numeric_array(
        adjusted.get("adjclose"),
        "indicators.adjclose[0].adjclose",
        len(timestamps),
    )

    rows = pd.DataFrame(
        {
            "symbol": expected_symbol,
            "source_timestamp": timestamps,
            "source_timestamp_utc": [
                datetime.fromtimestamp(value, timezone.utc).isoformat()
                for value in timestamps
            ],
            "session_date": [
                _session_date(value, provider_timezone) for value in timestamps
            ],
            "open": arrays["open"],
            "high": arrays["high"],
            "low": arrays["low"],
            "close": arrays["close"],
            "adj_close": arrays["adj_close"],
            "volume": arrays["volume"],
        }
    )
    actions = _parse_actions(
        result.get("events"),
        symbol=expected_symbol,
        provider_timezone=provider_timezone,
    )
    return ParsedSymbol(expected_symbol, metadata, rows, actions)


def field_integrity_row(parsed: ParsedSymbol) -> dict[str, Any]:
    """Count missing/invalid raw fields without repairing provider values."""
    frame = parsed.rows
    row: dict[str, Any] = {"symbol": parsed.symbol, "observed_rows": len(frame)}
    for field in (*PRICE_FIELDS, "volume"):
        series = frame[field]
        row[f"{field}_null"] = int(series.isna().sum())
        row[f"{field}_zero"] = int((series == 0).fillna(False).sum())
        row[f"{field}_negative"] = int((series < 0).fillna(False).sum())

    comparable_high = frame[["open", "high", "close"]].dropna()
    comparable_low = frame[["open", "low", "close"]].dropna()
    comparable_range = frame[["high", "low"]].dropna()
    row["high_below_open_or_close"] = int(
        (
            comparable_high["high"]
            < comparable_high[["open", "close"]].max(axis=1)
        ).sum()
    )
    row["low_above_open_or_close"] = int(
        (
            comparable_low["low"]
            > comparable_low[["open", "close"]].min(axis=1)
        ).sum()
    )
    row["high_below_low"] = int(
        (comparable_range["high"] < comparable_range["low"]).sum()
    )
    return row


def timestamp_audit_row(parsed: ParsedSymbol) -> dict[str, Any]:
    """Summarize source timestamp ordering and timezone conversion."""
    frame = parsed.rows
    timestamps = frame["source_timestamp"]
    return {
        "symbol": parsed.symbol,
        "observed_rows": len(frame),
        "duplicate_timestamps": int(timestamps.duplicated().sum()),
        "strictly_increasing": bool(timestamps.is_monotonic_increasing),
        "provider_timezone": parsed.metadata.get("exchangeTimezoneName"),
        "provider_gmtoffset": parsed.metadata.get("gmtoffset"),
        "session_date_conversion": "provider_exchange_timezone",
        "first_timestamp": int(timestamps.iloc[0]),
        "first_timestamp_utc": frame["source_timestamp_utc"].iloc[0],
        "first_session_date": frame["session_date"].iloc[0],
        "last_timestamp": int(timestamps.iloc[-1]),
        "last_timestamp_utc": frame["source_timestamp_utc"].iloc[-1],
        "last_session_date": frame["session_date"].iloc[-1],
        "timestamps_before_2003": int((timestamps < PERIOD1).sum()),
        "timestamps_2017_or_later": int((timestamps >= PERIOD2).sum()),
    }


def expected_xnys_dates() -> list[date]:
    """Return the candidate XNYS sessions inside the authorized boundary."""
    calendar = xcals.get_calendar("XNYS", start=START_DATE, end=END_DATE)
    schedule = calendar.schedule.loc[str(START_DATE) : str(END_DATE)]
    return list(schedule.index.date)


def calendar_coverage(
    symbol: str,
    observed_dates: Iterable[date],
    expected_dates: Iterable[date],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Compare observed dates with a supplied calendar without imputing rows."""
    observed_list = list(observed_dates)
    observed = set(observed_list)
    expected = set(expected_dates)
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    coverage = {
        "symbol": symbol,
        "expected_sessions": len(expected),
        "observed_rows": len(observed_list),
        "observed_unique_sessions": len(observed),
        "missing_sessions": len(missing),
        "extra_sessions": len(extra),
        "first_observed_session": min(observed) if observed else None,
        "last_observed_session": max(observed) if observed else None,
        "history_reaches_2003": bool(observed and min(observed).year == 2003),
    }
    exceptions = [
        {"symbol": symbol, "session_date": value, "exception_type": "MISSING"}
        for value in missing
    ] + [
        {"symbol": symbol, "session_date": value, "exception_type": "EXTRA"}
        for value in extra
    ]
    return coverage, exceptions


def monthly_completeness(
    parsed: ParsedSymbol, expected_dates: Sequence[date]
) -> list[dict[str, Any]]:
    """Count structural completeness by calendar month without filling gaps."""
    expected_frame = pd.DataFrame({"session_date": list(expected_dates)})
    expected_frame["month"] = pd.to_datetime(expected_frame["session_date"]).dt.to_period("M")
    observed = parsed.rows.copy()
    observed["month"] = pd.to_datetime(observed["session_date"]).dt.to_period("M")
    output: list[dict[str, Any]] = []
    for month, expected_group in expected_frame.groupby("month", sort=True):
        group = observed.loc[observed["month"] == month]
        missing_ohlc = group[list(QUOTE_FIELDS[:4])].isna().any(axis=1)
        output.append(
            {
                "symbol": parsed.symbol,
                "month": str(month),
                "expected_sessions": len(expected_group),
                "observed_sessions": len(group),
                "complete_ohlc_sessions": int((~missing_ohlc).sum()),
                "missing_ohlc_sessions": int(missing_ohlc.sum()),
                "volume_null_sessions": int(group["volume"].isna().sum()),
                "volume_zero_sessions": int((group["volume"] == 0).fillna(False).sum()),
            }
        )
    return output


def provider_metadata_row(parsed: ParsedSymbol) -> dict[str, Any]:
    """Return only the explicitly authorized provider metadata whitelist."""
    meta = parsed.metadata
    row = {
        "symbol": parsed.symbol,
        "currency": meta.get("currency"),
        "exchangeName": meta.get("exchangeName"),
        "fullExchangeName": meta.get("fullExchangeName"),
        "instrumentType": meta.get("instrumentType"),
        "exchangeTimezoneName": meta.get("exchangeTimezoneName"),
        "timezone": meta.get("timezone"),
        "gmtoffset": meta.get("gmtoffset"),
        "dataGranularity": meta.get("dataGranularity"),
        "firstTradeDate": meta.get("firstTradeDate"),
        "priceHint": meta.get("priceHint"),
        "hasPrePostMarketData": meta.get("hasPrePostMarketData"),
        "validRanges": (
            json.dumps(meta.get("validRanges"), ensure_ascii=False, separators=(",", ":"))
            if isinstance(meta.get("validRanges"), (list, dict))
            else meta.get("validRanges")
        ),
    }
    if tuple(row) != AUTHORIZED_PROVIDER_METADATA_FIELDS:
        raise StructuralDataError("canonical provider metadata schema drifted")
    return row


def metadata_boundary_audit_rows(parsed: ParsedSymbol) -> list[dict[str, Any]]:
    """Inventory metadata field names and suppress every non-whitelisted value."""
    rows: list[dict[str, Any]] = []
    authorized = set(AUTHORIZED_PROVIDER_METADATA_FIELDS)
    raw_fields = set(parsed.metadata)
    raw_fields.add("symbol")
    for field_name in sorted(raw_fields):
        emitted = field_name in authorized
        rows.append(
            {
                "symbol": parsed.symbol,
                "field_name": field_name,
                "classification": (
                    "AUTHORIZED_STATIC" if emitted else "OUT_OF_SCOPE_DYNAMIC"
                ),
                "emitted": emitted,
                "remediation_action": (
                    "EMITTED_CANONICAL"
                    if emitted
                    else "EXCLUDED_FROM_CANONICAL_ARTIFACTS"
                ),
            }
        )
    return rows


def _safe_ratio(numerator: Any, denominator: Any) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    if pd.isna(numerator) or pd.isna(denominator):
        return None
    return float(numerator) / float(denominator)


def split_unit_audit(
    parsed: ParsedSymbol,
    expected_dates: Sequence[date],
    *,
    event_date: date = SPLIT_EVENT_DATE,
) -> pd.DataFrame:
    """Calculate the authorized mechanical unit checks on exactly 41 sessions."""
    if parsed.symbol != SPLIT_SYMBOL:
        raise StructuralDataError("split unit audit is authorized only for IWM")
    expected = list(expected_dates)
    try:
        event_position = expected.index(event_date)
    except ValueError as exc:
        raise StructuralDataError("IWM split event is not an expected XNYS session") from exc
    side = SPLIT_WINDOW_SESSIONS_EACH_SIDE
    expected_window = expected[event_position - side : event_position + side + 1]
    if len(expected_window) != 2 * side + 1:
        raise StructuralDataError("insufficient XNYS sessions around the IWM split")

    split_actions = parsed.actions.loc[
        (parsed.actions["action_type"] == "STOCK_SPLIT")
        & (parsed.actions["session_date"] == event_date)
    ]
    if len(split_actions) != 1:
        raise StructuralDataError("expected exactly one IWM split on 2005-06-09")
    action = split_actions.iloc[0]
    split_factor = _safe_ratio(action["numerator"], action["denominator"])
    if split_factor is None:
        raise StructuralDataError("IWM split factor is unavailable")

    indexed = parsed.rows.set_index("session_date")
    if not indexed.index.is_unique:
        raise StructuralDataError("IWM split unit audit has duplicate session dates")
    missing = [session for session in expected_window if session not in indexed.index]
    if missing:
        raise StructuralDataError(
            f"IWM split unit audit is missing {len(missing)} required XNYS sessions"
        )
    window = indexed.loc[expected_window].reset_index()
    positions = list(range(-side, side + 1))
    output = pd.DataFrame(
        {
            "session_date": window["session_date"],
            "position_relative_to_event": positions,
            "provider_close": window["close"],
            "adj_close": window["adj_close"],
            "reported_volume": window["volume"],
            "provider_close_x_reported_volume": window["close"] * window["volume"],
            "adj_close_div_provider_close": window["adj_close"] / window["close"],
            "split_factor": split_factor,
        }
    )
    if len(output) != 41 or output["session_date"].tolist() != expected_window:
        raise StructuralDataError("split unit audit escaped its 41-session boundary")
    return output


def classify_post_pre_ratio(value: float | None) -> str:
    """Apply the pre-specified mechanical continuity classification."""
    if value is None or pd.isna(value):
        return "INCONCLUSIVE"
    if 0.75 <= value <= 1.33:
        return "CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF"
    if 1.60 <= value <= 2.40:
        return "CONSISTENT_WITH_FACTOR_TWO_DISCONTINUITY_NOT_PROOF"
    return "INCONCLUSIVE"


def split_unit_summary(audit: pd.DataFrame) -> dict[str, Any]:
    """Summarize pre/post medians without asserting provider unit semantics."""
    if len(audit) != 41 or set(audit["position_relative_to_event"]) != set(range(-20, 21)):
        raise StructuralDataError("split unit summary requires exactly positions -20 through 20")
    metrics: dict[str, dict[str, Any]] = {}
    for field in (
        "reported_volume",
        "provider_close_x_reported_volume",
        "adj_close_div_provider_close",
    ):
        pre_median = float(
            audit.loc[audit["position_relative_to_event"] < 0, field].median()
        )
        post_median = float(
            audit.loc[audit["position_relative_to_event"] > 0, field].median()
        )
        ratio = _safe_ratio(post_median, pre_median)
        metrics[field] = {
            "pre_median": pre_median,
            "post_median": post_median,
            "post_pre_ratio": ratio,
            "classification": classify_post_pre_ratio(ratio),
        }
    return {
        "symbol": SPLIT_SYMBOL,
        "event_date": SPLIT_EVENT_DATE.isoformat(),
        "pre_sessions": 20,
        "event_sessions": 1,
        "post_sessions": 20,
        "metrics": metrics,
        "VOLUME_UNIT_SEMANTICS": "UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION",
    }


def assert_no_analytical_columns(columns: Iterable[str]) -> None:
    """Reject analytical feature/target vocabulary from Stage A1 table schemas."""
    violations: list[str] = []
    for column in columns:
        normalized = re.sub(r"[^a-z0-9]+", "_", str(column).lower()).strip("_")
        tokens = set(normalized.split("_"))
        collapsed = normalized.replace("_", "")
        if tokens & FORBIDDEN_ANALYTICAL_TOKENS or collapsed in FORBIDDEN_ANALYTICAL_TOKENS:
            violations.append(str(column))
    if violations:
        raise StructuralDataError(
            f"Stage A1 output contains forbidden analytical columns: {violations}"
        )


def assert_no_analytical_mapping_keys(value: Any) -> None:
    """Recursively reject prohibited analytical vocabulary from JSON keys."""
    if isinstance(value, Mapping):
        assert_no_analytical_columns(value.keys())
        for child in value.values():
            assert_no_analytical_mapping_keys(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_analytical_mapping_keys(child)


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    assert_no_analytical_columns(frame.columns)
    frame.to_csv(path, index=False, lineterminator="\n", encoding="utf-8")


def _write_json(value: Any, path: Path) -> None:
    assert_no_analytical_mapping_keys(value)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def _load_receipt_and_payload(
    raw_dir: Path,
    symbol: str,
    expected_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    receipt_path = raw_dir / f"{symbol}_receipt.json"
    if not receipt_path.is_file():
        raise StructuralDataError(f"missing receipt: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    payload_name = receipt.get("raw_payload_file")
    expected_sha = receipt.get("payload_sha256")
    if not isinstance(payload_name, str) or not isinstance(expected_sha, str):
        raise StructuralDataError(f"{symbol} receipt has no canonical raw payload/hash")
    if expected_sha != expected_sha256:
        raise StructuralDataError(
            f"{symbol} receipt hash differs from the independently registered hash"
        )
    payload = verify_raw_payload(raw_dir / payload_name, expected_sha256)
    receipt["payload_sha256_verified"] = True
    return receipt, payload


def _empty_frame(columns: Sequence[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=list(columns))


def boundary_incident_disclosed(path: Path) -> bool:
    """Calculate disclosure status from the corrective erratum contract marker."""
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    required_markers = (
        "boundary_incident_disclosed: true",
        "zero linhas OHLCV de 2017+",
        "zero corporate actions de 2017+",
        "metadados dinâmicos de 2026",
        "nenhuma feature, target ou associação",
    )
    return all(marker in text for marker in required_markers)


def calculated_boundary_flags(
    parsed_by_symbol: Mapping[str, ParsedSymbol],
    metadata_audit: pd.DataFrame,
    *,
    disclosure_path: Path,
    raw_hashes_unchanged: bool,
) -> dict[str, Any]:
    """Calculate every corrective boundary flag from parsed/audited evidence."""
    historical_rows_2017_or_later = sum(
        int((parsed.rows["source_timestamp"] >= PERIOD2).sum())
        for parsed in parsed_by_symbol.values()
    )
    corporate_actions_2017_or_later = sum(
        int((parsed.actions["source_timestamp"] >= PERIOD2).sum())
        for parsed in parsed_by_symbol.values()
        if not parsed.actions.empty
    )
    if metadata_audit.empty:
        dynamic_detected = False
        dynamic_emitted = False
    else:
        dynamic = metadata_audit["classification"] == "OUT_OF_SCOPE_DYNAMIC"
        dynamic_detected = bool(dynamic.any())
        dynamic_emitted = bool((dynamic & metadata_audit["emitted"].astype(bool)).any())
    return {
        "historical_rows_2017_or_later": int(historical_rows_2017_or_later),
        "corporate_actions_2017_or_later": int(corporate_actions_2017_or_later),
        "out_of_scope_dynamic_metadata_detected_in_raw": dynamic_detected,
        "out_of_scope_dynamic_metadata_emitted": dynamic_emitted,
        "boundary_incident_disclosed": boundary_incident_disclosed(disclosure_path),
        "raw_hashes_unchanged": bool(raw_hashes_unchanged),
    }


def run_corrective_audit(
    raw_dir: Path,
    processed_dir: Path,
    *,
    corrective_audit_code_commit: str,
    disclosure_path: Path,
    expected_raw_hashes: Mapping[str, str] = RAW_RESPONSE_SHA256,
) -> dict[str, Any]:
    """Run the bounded Stage A1c audit and write one immutable corrective set."""
    if not re.fullmatch(r"[0-9a-f]{40}", corrective_audit_code_commit):
        raise StructuralDataError("corrective audit code commit must be a full Git hash")
    if set(expected_raw_hashes) != set(SYMBOLS):
        raise StructuralDataError("registered raw hash map must cover exactly five symbols")
    if processed_dir.exists():
        raise StructuralDataError(f"processed snapshot already exists: {processed_dir}")
    temp_dir = processed_dir.parent / f".{processed_dir.name}.tmp"
    if temp_dir.exists():
        raise StructuralDataError(f"temporary output already exists: {temp_dir}")
    temp_dir.mkdir(parents=True)

    schema_rows: list[dict[str, Any]] = []
    raw_records: list[dict[str, Any]] = []
    parsed_by_symbol: dict[str, ParsedSymbol] = {}
    structural_errors: list[dict[str, str]] = []
    try:
        for symbol in SYMBOLS:
            try:
                receipt, payload = _load_receipt_and_payload(
                    raw_dir, symbol, expected_raw_hashes[symbol]
                )
                raw_records.append(
                    {
                        "symbol": symbol,
                        "raw_payload_file": receipt["raw_payload_file"],
                        "payload_sha256": expected_raw_hashes[symbol],
                        "payload_size_bytes": len(payload),
                        "payload_sha256_verified": True,
                    }
                )
                root = decode_payload(payload)
                schema_rows.extend(schema_audit_rows(root, symbol))
                parsed = parse_chart_payload(payload, symbol)
                parsed_by_symbol[symbol] = parsed
            except (OSError, KeyError, json.JSONDecodeError, StructuralDataError) as exc:
                structural_errors.append({"symbol": symbol, "error": str(exc)})

        expected_dates = expected_xnys_dates()
        integrity_rows: list[dict[str, Any]] = []
        timestamp_rows: list[dict[str, Any]] = []
        coverage_rows: list[dict[str, Any]] = []
        exception_rows: list[dict[str, Any]] = []
        monthly_rows: list[dict[str, Any]] = []
        action_frames: list[pd.DataFrame] = []
        metadata_rows: list[dict[str, Any]] = []
        metadata_boundary_rows: list[dict[str, Any]] = []

        for symbol in SYMBOLS:
            parsed = parsed_by_symbol.get(symbol)
            if parsed is None:
                continue
            integrity_rows.append(field_integrity_row(parsed))
            timestamp_rows.append(timestamp_audit_row(parsed))
            coverage, exceptions = calendar_coverage(
                symbol, parsed.rows["session_date"], expected_dates
            )
            coverage_rows.append(coverage)
            exception_rows.extend(exceptions)
            monthly_rows.extend(monthly_completeness(parsed, expected_dates))
            action_frames.append(parsed.actions)
            metadata_rows.append(provider_metadata_row(parsed))
            metadata_boundary_rows.extend(metadata_boundary_audit_rows(parsed))

        schema_frame = pd.DataFrame(schema_rows)
        integrity_frame = pd.DataFrame(integrity_rows)
        timestamp_frame = pd.DataFrame(timestamp_rows)
        coverage_frame = pd.DataFrame(coverage_rows)
        exception_frame = pd.DataFrame(
            exception_rows, columns=["symbol", "session_date", "exception_type"]
        )
        monthly_frame = pd.DataFrame(monthly_rows)
        action_frame = (
            pd.concat(action_frames, ignore_index=True)
            if action_frames
            else _empty_frame(
                [
                    "symbol",
                    "source_timestamp",
                    "source_timestamp_utc",
                    "session_date",
                    "boundary_status",
                    "action_type",
                    "amount",
                    "numerator",
                    "denominator",
                    "split_ratio",
                    "raw_event_json",
                ]
            )
        )
        metadata_frame = pd.DataFrame(
            metadata_rows, columns=AUTHORIZED_PROVIDER_METADATA_FIELDS
        )
        metadata_boundary_frame = pd.DataFrame(
            metadata_boundary_rows,
            columns=(
                "symbol",
                "field_name",
                "classification",
                "emitted",
                "remediation_action",
            ),
        )

        split_frame = _empty_frame(
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
        split_summary_payload: dict[str, Any] = {
            "symbol": SPLIT_SYMBOL,
            "event_date": SPLIT_EVENT_DATE.isoformat(),
            "pre_sessions": 0,
            "event_sessions": 0,
            "post_sessions": 0,
            "metrics": {},
            "VOLUME_UNIT_SEMANTICS": "UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION",
        }

        hard_stop_reasons = [entry["error"] for entry in structural_errors]
        decision_reasons: list[str] = []
        if not integrity_frame.empty:
            for row in integrity_rows:
                if row["volume_null"] == row["observed_rows"]:
                    hard_stop_reasons.append(
                        f"{row['symbol']} has structurally absent Volume"
                    )
                if any(row[f"{field}_negative"] for field in PRICE_FIELDS):
                    hard_stop_reasons.append(f"{row['symbol']} has negative price fields")
                if any(row[f"{field}_zero"] for field in PRICE_FIELDS):
                    hard_stop_reasons.append(f"{row['symbol']} has zero price fields")
                if (
                    any(row[f"{field}_null"] for field in PRICE_FIELDS)
                    or row["volume_null"]
                    or row["volume_zero"]
                    or row["volume_negative"]
                    or row["high_below_open_or_close"]
                    or row["low_above_open_or_close"]
                    or row["high_below_low"]
                ):
                    decision_reasons.append(
                        f"{row['symbol']} has enumerated field-integrity exceptions"
                    )
        for row in coverage_rows:
            if not row["history_reaches_2003"]:
                hard_stop_reasons.append(f"{row['symbol']} history does not reach 2003")
            if row["missing_sessions"] or row["extra_sessions"]:
                decision_reasons.append(
                    f"{row['symbol']} has enumerated XNYS calendar exceptions"
                )
        parsed_iwm = parsed_by_symbol.get(SPLIT_SYMBOL)
        if parsed_iwm is None:
            hard_stop_reasons.append("IWM unavailable for the authorized split unit audit")
        else:
            try:
                split_frame = split_unit_audit(parsed_iwm, expected_dates)
                split_summary_payload = split_unit_summary(split_frame)
            except StructuralDataError as exc:
                hard_stop_reasons.append(str(exc))

        raw_hashes_unchanged = (
            len(raw_records) == len(SYMBOLS)
            and all(record["payload_sha256_verified"] for record in raw_records)
            and {record["symbol"]: record["payload_sha256"] for record in raw_records}
            == dict(expected_raw_hashes)
        )
        boundary_flags = calculated_boundary_flags(
            parsed_by_symbol,
            metadata_boundary_frame,
            disclosure_path=disclosure_path,
            raw_hashes_unchanged=raw_hashes_unchanged,
        )
        if boundary_flags["historical_rows_2017_or_later"]:
            hard_stop_reasons.append("historical rows from 2017 or later were materialized")
        if boundary_flags["corporate_actions_2017_or_later"]:
            hard_stop_reasons.append("corporate actions from 2017 or later were materialized")
        if boundary_flags["out_of_scope_dynamic_metadata_emitted"]:
            hard_stop_reasons.append("out-of-scope dynamic metadata was emitted")
        if not boundary_flags["boundary_incident_disclosed"]:
            hard_stop_reasons.append("boundary incident erratum is incomplete")
        if not boundary_flags["raw_hashes_unchanged"]:
            hard_stop_reasons.append("one or more registered raw hashes changed")

        if hard_stop_reasons:
            verdict = "STOP_DATA_INFEASIBLE"
        elif decision_reasons:
            verdict = "DECISION_REQUIRED"
        else:
            verdict = "PASS_CORRECTIVE_AUDIT_READY_FOR_HUMAN_REVIEW"

        retrieval_id = raw_dir.name
        corrective_manifest = {
            "experiment_id": EXPERIMENT_ID,
            "retrieval_id": retrieval_id,
            "provider": PROVIDER,
            "parser_version": PARSER_VERSION,
            "raw_acquisition_h0_commit": RAW_ACQUISITION_H0_COMMIT,
            "original_results_commit": ORIGINAL_RESULTS_COMMIT,
            "corrective_audit_code_commit": corrective_audit_code_commit,
            "request_contract": {
                "symbols": list(SYMBOLS),
                "endpoint": ENDPOINT,
                "parameters": dict(REQUEST_PARAMETERS),
                "period1_utc": START_UTC.isoformat(),
                "period2_utc_exclusive": END_UTC_EXCLUSIVE.isoformat(),
            },
            "raw_payloads": raw_records,
            "structural_errors": structural_errors,
        }
        summary = {
            "experiment_id": EXPERIMENT_ID,
            "retrieval_id": retrieval_id,
            "parser_version": PARSER_VERSION,
            "corrective_audit_code_commit": corrective_audit_code_commit,
            "verdict": verdict,
            "symbols_required": len(SYMBOLS),
            "symbols_parsed": len(parsed_by_symbol),
            "expected_xnys_sessions": len(expected_dates),
            "observed_rows_total": int(
                sum(len(item.rows) for item in parsed_by_symbol.values())
            ),
            "calendar_exception_count": len(exception_rows),
            "corporate_action_count": int(len(action_frame)),
            "hard_stop_reasons": sorted(set(hard_stop_reasons)),
            "decision_reasons": sorted(set(decision_reasons)),
            "prohibited_calculations_performed": False,
            "safe_to_run_stage_a2": False,
            **boundary_flags,
        }

        _write_json(corrective_manifest, temp_dir / "corrective_audit_manifest.json")
        _write_csv(schema_frame, temp_dir / "provider_schema_audit.csv")
        _write_csv(integrity_frame, temp_dir / "field_integrity_audit.csv")
        _write_csv(timestamp_frame, temp_dir / "timestamp_audit.csv")
        _write_csv(coverage_frame, temp_dir / "calendar_coverage_by_symbol.csv")
        _write_csv(exception_frame, temp_dir / "calendar_exceptions.csv")
        _write_csv(monthly_frame, temp_dir / "monthly_completeness.csv")
        _write_csv(action_frame, temp_dir / "corporate_actions.csv")
        _write_csv(metadata_frame, temp_dir / "provider_metadata.csv")
        _write_csv(
            metadata_boundary_frame,
            temp_dir / "metadata_boundary_audit.csv",
        )
        _write_csv(split_frame, temp_dir / "split_unit_audit.csv")
        _write_json(split_summary_payload, temp_dir / "split_unit_summary.json")
        _write_json(summary, temp_dir / "stage_a1c_summary.json")
        processed_dir.parent.mkdir(parents=True, exist_ok=True)
        temp_dir.rename(processed_dir)
        return summary
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise
