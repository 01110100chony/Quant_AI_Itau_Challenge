"""Independent source-unit audit for the authorized LAF_001 Stage A1d sample."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import pandas as pd


PROVIDER = "Tiingo EOD"
SYMBOL = "IWM"
START_DATE = date(2005, 5, 11)
END_DATE = date(2005, 7, 8)
EVENT_DATE = date(2005, 6, 9)
ENDPOINT = "https://api.tiingo.com/tiingo/daily/IWM/prices"
PROVIDER_TIMEZONE = "America/New_York"
ALLOWED_FIELDS = ("date", "close", "volume", "splitFactor")
EXPECTED_ROWS = 41
PRE_ROWS = 20
POST_ROWS = 20


class SourceAuditError(ValueError):
    """Raised when private input violates the frozen Stage A1d contract."""


@dataclass(frozen=True)
class AuditOutputs:
    """Sanitized outputs plus the private comparison and private metrics."""

    manifest: dict[str, Any]
    gates: dict[str, Any]
    summary: dict[str, Any]
    private_comparison: pd.DataFrame
    private_metrics: dict[str, Any]


def _numeric(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SourceAuditError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise SourceAuditError(f"{label} must be finite and positive")
    return number


def normalize_tiingo_session_date(value: Any) -> date:
    """Interpret the provider value as a date label under New York semantics."""
    if not isinstance(value, str) or len(value) < 10:
        raise SourceAuditError("Tiingo date must be an ISO date string")
    try:
        label = date.fromisoformat(value[:10])
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceAuditError("Tiingo date is not valid ISO-8601") from exc
    if parsed.tzinfo is None:
        raise SourceAuditError("Tiingo date must include timezone information")
    # Constructing the historical local label through ZoneInfo rejects any use
    # of a fixed EDT/gmtoffset convention. The timestamp is not availability.
    datetime.combine(label, time(12), tzinfo=ZoneInfo(PROVIDER_TIMEZONE)).utcoffset()
    if not START_DATE <= label <= END_DATE:
        raise SourceAuditError("Tiingo date is outside the authorized boundary")
    return label


def parse_tiingo_payload(payload: bytes) -> pd.DataFrame:
    """Extract only the four authorized fields from a private Tiingo response."""
    try:
        decoded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceAuditError("Tiingo response is not valid UTF-8 JSON") from exc
    if not isinstance(decoded, list):
        raise SourceAuditError("Tiingo response root must be an array")

    rows: list[dict[str, Any]] = []
    for position, item in enumerate(decoded):
        if not isinstance(item, Mapping):
            raise SourceAuditError("each Tiingo response row must be an object")
        missing = [field for field in ALLOWED_FIELDS if field not in item]
        if missing:
            raise SourceAuditError(f"Tiingo row {position} misses an authorized field")
        rows.append(
            {
                "session_date": normalize_tiingo_session_date(item["date"]),
                "tiingo_close": _numeric(item["close"], "Tiingo close"),
                "tiingo_volume": _numeric(item["volume"], "Tiingo volume"),
                "tiingo_split_factor": _numeric(
                    item["splitFactor"], "Tiingo splitFactor"
                ),
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SourceAuditError("Tiingo response contains no rows")
    if frame["session_date"].duplicated().any():
        raise SourceAuditError("Tiingo response contains duplicate session dates")
    return frame.sort_values("session_date", kind="stable").reset_index(drop=True)


def load_yahoo_a1c(path: Path) -> pd.DataFrame:
    """Load only the authorized Yahoo columns from the fixed Stage A1c file."""
    frame = pd.read_csv(path)
    required = {
        "session_date",
        "position_relative_to_event",
        "provider_close",
        "reported_volume",
    }
    if not required.issubset(frame.columns):
        raise SourceAuditError("Stage A1c split audit misses required columns")
    selected = frame.loc[:, sorted(required)].copy()
    selected["session_date"] = pd.to_datetime(
        selected["session_date"], errors="raise"
    ).dt.date
    if len(selected) != EXPECTED_ROWS or selected["session_date"].duplicated().any():
        raise SourceAuditError("Stage A1c split audit must contain 41 unique dates")
    positions = selected["position_relative_to_event"].astype(int).tolist()
    if positions != list(range(-PRE_ROWS, POST_ROWS + 1)):
        raise SourceAuditError("Stage A1c relative positions must be -20 through +20")
    if selected.iloc[0]["session_date"] != START_DATE:
        raise SourceAuditError("Stage A1c first date changed")
    if selected.iloc[-1]["session_date"] != END_DATE:
        raise SourceAuditError("Stage A1c last date changed")
    event = selected.loc[selected["position_relative_to_event"] == 0]
    if len(event) != 1 or event.iloc[0]["session_date"] != EVENT_DATE:
        raise SourceAuditError("Stage A1c event date changed")
    for field in ("provider_close", "reported_volume"):
        selected[field] = pd.to_numeric(selected[field], errors="raise")
        if (~selected[field].map(lambda value: math.isfinite(float(value)) and value > 0)).any():
            raise SourceAuditError(f"Stage A1c {field} must be finite and positive")
    return selected


def split_convention(frame: pd.DataFrame) -> tuple[str, float | None, int, bool]:
    """Apply the pre-registered direct/reciprocal split-factor normalization."""
    non_unit = frame.loc[~frame["tiingo_split_factor"].map(lambda x: math.isclose(x, 1.0))]
    event_count = len(non_unit)
    if event_count != 1 or non_unit.iloc[0]["session_date"] != EVENT_DATE:
        return "INVALID_EVENT_PATTERN", None, event_count, False
    observed = float(non_unit.iloc[0]["tiingo_split_factor"])
    if math.isclose(observed, 2.0, rel_tol=0.0, abs_tol=1e-12):
        return "DIRECT_TWO_FOR_ONE", 2.0, event_count, True
    if math.isclose(observed, 0.5, rel_tol=0.0, abs_tol=1e-12):
        return "RECIPROCAL_HALF_REPORTED", 2.0, event_count, True
    return "INVALID_NON_UNIT_FACTOR", None, event_count, False


def _mape(reference: pd.Series, comparison: pd.Series) -> float:
    return float(((reference - comparison).abs() / comparison.abs()).mean())


def audit_frames(
    yahoo: pd.DataFrame,
    tiingo: pd.DataFrame,
    *,
    raw_sha256: str,
    payload_size_bytes: int,
    acquired_at_utc: str,
    http_status: int,
    attempt_count: int,
    retrieval_id: str,
    h0_a1d_commit: str,
) -> AuditOutputs:
    """Calculate only the frozen source-unit comparisons and aggregate gates."""
    yahoo_dates = set(yahoo["session_date"])
    tiingo_dates = set(tiingo["session_date"])
    missing_dates = yahoo_dates - tiingo_dates
    extra_dates = tiingo_dates - yahoo_dates
    duplicate_count = int(tiingo["session_date"].duplicated().sum())
    coverage_pass = (
        len(tiingo) == EXPECTED_ROWS
        and not missing_dates
        and not extra_dates
        and duplicate_count == 0
    )
    convention, economic_factor, event_count, split_event_pass = split_convention(tiingo)
    if not coverage_pass:
        raise SourceAuditError("CoveragePass failed; response content is not accepted")

    comparison = yahoo.merge(tiingo, on="session_date", how="inner", validate="one_to_one")
    comparison["split_mapping_factor"] = comparison["session_date"].map(
        lambda value: 2.0 if value < EVENT_DATE else 1.0
    )
    comparison["tiingo_split_close"] = (
        comparison["tiingo_close"] / comparison["split_mapping_factor"]
    )
    comparison["tiingo_split_volume"] = (
        comparison["tiingo_volume"] * comparison["split_mapping_factor"]
    )
    comparison["tiingo_raw_dollar_volume"] = (
        comparison["tiingo_close"] * comparison["tiingo_volume"]
    )
    comparison["yahoo_dollar_volume"] = (
        comparison["provider_close"] * comparison["reported_volume"]
    )

    pre = comparison.loc[comparison["position_relative_to_event"] < 0]
    event_post = comparison.loc[comparison["position_relative_to_event"] >= 0]
    post = comparison.loc[comparison["position_relative_to_event"] > 0]
    if len(pre) != PRE_ROWS or len(event_post) != POST_ROWS + 1 or len(post) != POST_ROWS:
        raise SourceAuditError("private comparison windows are not 20/event/20")

    metrics = {
        "price_mape_pre": _mape(pre["provider_close"], pre["tiingo_split_close"]),
        "price_mape_event_post": _mape(
            event_post["provider_close"], event_post["tiingo_close"]
        ),
        "volume_mape_pre": _mape(
            pre["reported_volume"], pre["tiingo_split_volume"]
        ),
        "volume_mape_event_post": _mape(
            event_post["reported_volume"], event_post["tiingo_volume"]
        ),
        "dollar_volume_mape_pre": _mape(
            pre["yahoo_dollar_volume"], pre["tiingo_raw_dollar_volume"]
        ),
        "dollar_volume_mape_post": _mape(
            post["yahoo_dollar_volume"], post["tiingo_raw_dollar_volume"]
        ),
        "median_yahoo_to_tiingo_raw_volume_pre": float(
            (pre["reported_volume"] / pre["tiingo_volume"]).median()
        ),
        "median_yahoo_to_tiingo_split_volume_pre": float(
            (pre["reported_volume"] / pre["tiingo_split_volume"]).median()
        ),
        "median_yahoo_to_tiingo_raw_volume_post": float(
            (post["reported_volume"] / post["tiingo_volume"]).median()
        ),
    }
    pre_volume_within_10 = int(
        (
            (pre["reported_volume"] - pre["tiingo_split_volume"]).abs()
            / pre["tiingo_split_volume"]
            <= 0.10
        ).sum()
    )
    post_volume_within_10 = int(
        (
            (post["reported_volume"] - post["tiingo_volume"]).abs()
            / post["tiingo_volume"]
            <= 0.10
        ).sum()
    )
    pre_dollar_ratio = pre["yahoo_dollar_volume"] / pre["tiingo_raw_dollar_volume"]
    post_dollar_ratio = post["yahoo_dollar_volume"] / post["tiingo_raw_dollar_volume"]
    pre_dollar_within = int(pre_dollar_ratio.between(0.90, 1.10, inclusive="both").sum())
    post_dollar_within = int(post_dollar_ratio.between(0.90, 1.10, inclusive="both").sum())

    price_pass = (
        metrics["price_mape_pre"] <= 0.02
        and metrics["price_mape_event_post"] <= 0.02
    )
    volume_pass = (
        metrics["volume_mape_pre"] <= 0.05
        and metrics["volume_mape_event_post"] <= 0.05
        and 1.80 <= metrics["median_yahoo_to_tiingo_raw_volume_pre"] <= 2.20
        and 0.95 <= metrics["median_yahoo_to_tiingo_split_volume_pre"] <= 1.05
        and 0.95 <= metrics["median_yahoo_to_tiingo_raw_volume_post"] <= 1.05
        and pre_volume_within_10 >= 18
        and post_volume_within_10 >= 18
    )
    dollar_pass = (
        metrics["dollar_volume_mape_pre"] <= 0.05
        and metrics["dollar_volume_mape_post"] <= 0.05
        and pre_dollar_within >= 18
        and post_dollar_within >= 18
    )
    gates = {
        "CoveragePass": {
            "pass": coverage_pass,
            "thresholds": {"expected_dates": 41, "missing": 0, "extra": 0, "duplicates": 0},
            "counts": {
                "observed_dates": len(tiingo),
                "missing": len(missing_dates),
                "extra": len(extra_dates),
                "duplicates": duplicate_count,
            },
        },
        "SplitEventPass": {
            "pass": split_event_pass,
            "thresholds": {"non_unit_event_count": 1, "event_date": "2005-06-09", "economic_factor": 2},
            "counts": {"non_unit_event_count": event_count},
        },
        "PriceUnitPass": {
            "pass": price_pass,
            "thresholds": {"mape_pre_max": 0.02, "mape_event_post_max": 0.02},
        },
        "VolumeUnitPass": {
            "pass": volume_pass,
            "thresholds": {
                "mape_pre_max": 0.05,
                "mape_event_post_max": 0.05,
                "median_raw_pre_min": 1.80,
                "median_raw_pre_max": 2.20,
                "median_split_pre_min": 0.95,
                "median_split_pre_max": 1.05,
                "median_raw_post_min": 0.95,
                "median_raw_post_max": 1.05,
                "sessions_within_relative_error_10pct_min": 18,
            },
            "counts": {
                "pre_sessions_within_relative_error_10pct": pre_volume_within_10,
                "post_sessions_within_relative_error_10pct": post_volume_within_10,
            },
        },
        "DollarVolumePass": {
            "pass": dollar_pass,
            "thresholds": {
                "mape_pre_max": 0.05,
                "mape_post_max": 0.05,
                "sessions_ratio_0_90_to_1_10_min": 18,
            },
            "counts": {
                "pre_sessions_ratio_0_90_to_1_10": pre_dollar_within,
                "post_sessions_ratio_0_90_to_1_10": post_dollar_within,
            },
        },
    }
    all_pass = all(bool(value["pass"]) for value in gates.values())
    if all_pass:
        classifications = {
            "YAHOO_PRICE_UNIT": "SPLIT_ADJUSTED_BASIS_CONFIRMED_FOR_IWM_2005_SAMPLE",
            "YAHOO_VOLUME_UNIT": "RECIPROCALLY_SPLIT_ADJUSTED_BASIS_CONFIRMED_FOR_IWM_2005_SAMPLE",
            "YAHOO_CLOSE_X_VOLUME": "CONSISTENT_WITH_AS_TRADED_DOLLAR_VOLUME_FOR_OBSERVED_SPLIT_SAMPLE",
            "VOLUME_UNIT_SEMANTICS": "RESOLVED_FOR_ALL_OBSERVED_SPLITS_IN_RESEARCH_DATA",
            "SAFE_TO_RUN_LAF_STAGE_A2": "NO",
            "READY_FOR_HUMAN_STAGE_A2_FREEZE_DECISION": "YES",
        }
    else:
        classifications = {
            "YAHOO_PRICE_UNIT": "NOT_CONFIRMED_GATE_FAILURE",
            "YAHOO_VOLUME_UNIT": "NOT_CONFIRMED_GATE_FAILURE",
            "YAHOO_CLOSE_X_VOLUME": "NOT_CONFIRMED_GATE_FAILURE",
            "VOLUME_UNIT_SEMANTICS": "UNRESOLVED",
            "SAFE_TO_RUN_LAF_STAGE_A2": "NO",
            "READY_FOR_HUMAN_STAGE_A2_FREEZE_DECISION": "NO",
        }
    manifest = {
        "experiment_id": "LAF_001",
        "stage": "A1d",
        "retrieval_id": retrieval_id,
        "provider": PROVIDER,
        "provider_role": "sample audit; not primary source",
        "symbol": SYMBOL,
        "endpoint": ENDPOINT,
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "frequency": "daily",
        "timezone": PROVIDER_TIMEZONE,
        "acquired_at_utc": acquired_at_utc,
        "http_status": http_status,
        "payload_size_bytes": payload_size_bytes,
        "raw_private_sha256": raw_sha256,
        "field_names_used": list(ALLOWED_FIELDS),
        "all_other_fields": "PRIVATE_NOT_USED_NOT_EMITTED",
        "attempt_count": attempt_count,
        "h0_a1d_commit": h0_a1d_commit,
        "row_count": len(tiingo),
        "private_raw_in_git": False,
    }
    summary = {
        "experiment_id": "LAF_001",
        "stage": "A1d",
        "retrieval_id": retrieval_id,
        "split_factor_convention": convention,
        "economic_factor_normalized": economic_factor == 2.0,
        "all_gates_pass": all_pass,
        "gate_pass": {name: bool(value["pass"]) for name, value in gates.items()},
        **classifications,
    }
    private_metrics = {
        "metric_definition": "MAPE denominator is Tiingo in the compared unit; ratios are Yahoo/Tiingo",
        "split_factor_convention": convention,
        "economic_factor": economic_factor,
        "metrics": metrics,
        "counts": {
            "pre_volume_within_10pct": pre_volume_within_10,
            "post_volume_within_10pct": post_volume_within_10,
            "pre_dollar_ratio_within": pre_dollar_within,
            "post_dollar_ratio_within": post_dollar_within,
        },
    }
    return AuditOutputs(manifest, gates, summary, comparison, private_metrics)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_source_unit_audit(
    *,
    raw_path: Path,
    receipt_path: Path,
    yahoo_path: Path,
    private_dir: Path,
    processed_dir: Path,
    retrieval_id: str,
    h0_a1d_commit: str,
) -> dict[str, Any]:
    """Audit one private retrieval and emit only aggregate versionable outputs."""
    raw = raw_path.read_bytes()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    raw_sha256 = hashlib.sha256(raw).hexdigest()
    if receipt.get("payload_sha256") != raw_sha256 or receipt.get("payload_size_bytes") != len(raw):
        raise SourceAuditError("private receipt does not match raw bytes")
    tiingo = parse_tiingo_payload(raw)
    yahoo = load_yahoo_a1c(yahoo_path)
    outputs = audit_frames(
        yahoo,
        tiingo,
        raw_sha256=raw_sha256,
        payload_size_bytes=len(raw),
        acquired_at_utc=str(receipt["attempt_completed_at_utc"]),
        http_status=int(receipt["http_status"]),
        attempt_count=int(receipt["attempt"]),
        retrieval_id=retrieval_id,
        h0_a1d_commit=h0_a1d_commit,
    )
    outputs.private_comparison.to_csv(private_dir / "source_unit_comparison.csv", index=False)
    _write_json(private_dir / "source_unit_metrics.json", outputs.private_metrics)

    if processed_dir.exists():
        raise SourceAuditError("Stage A1d processed destination already exists")
    temporary = processed_dir.with_name(processed_dir.name + ".tmp")
    if temporary.exists():
        raise SourceAuditError("Stage A1d temporary destination already exists")
    temporary.mkdir(parents=True)
    try:
        _write_json(temporary / "source_audit_manifest.json", outputs.manifest)
        _write_json(temporary / "source_audit_gates.json", outputs.gates)
        _write_json(temporary / "source_audit_summary.json", outputs.summary)
        temporary.replace(processed_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return outputs.summary
