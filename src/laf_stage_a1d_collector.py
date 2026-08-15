"""Bounded Tiingo EOD collector for LAF_001 Stage A1d.

The collector performs only the authorized IWM request and writes response
bytes and attempt receipts below the ignored private-data root. It never
places credentials in URLs, records, exceptions or emitted output.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROVIDER = "Tiingo EOD"
SYMBOL = "IWM"
START_DATE = "2005-05-11"
END_DATE = "2005-07-08"
ENDPOINT = "https://api.tiingo.com/tiingo/daily/IWM/prices"
TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 2


class AcquisitionError(RuntimeError):
    """Raised when the bounded private acquisition cannot be completed."""


@dataclass(frozen=True)
class AcquisitionOutcome:
    """Sanitized acquisition result; it contains no response observations."""

    retrieval_id: str
    private_dir: Path
    raw_path: Path
    receipt_path: Path
    attempt_count: int
    http_status: int
    payload_size_bytes: int
    payload_sha256: str
    acquired_at_utc: str


def request_url() -> str:
    """Return the fixed request URL containing dates but no credential."""
    query = urlencode({"startDate": START_DATE, "endDate": END_DATE})
    return f"{ENDPOINT}?{query}"


def build_request(token: str) -> Request:
    """Build the fixed request with header-only authentication."""
    if not token:
        raise AcquisitionError("TIINGO_API_TOKEN is not present")
    return Request(
        request_url(),
        headers={
            "Authorization": f"Token {token}",
            "Accept": "application/json",
            "User-Agent": "Quant-AI-Itau-LAF001-StageA1d/1.0",
        },
        method="GET",
    )


def _retrieval_id(moment: datetime) -> str:
    utc = moment.astimezone(timezone.utc)
    return utc.strftime("%Y%m%dT%H%M%S") + f"{utc.microsecond // 1000:03d}Z"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_new_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def _write_new_json(path: Path, value: dict[str, Any]) -> None:
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_new_bytes(path, encoded)


def _receipt(
    *,
    attempt: int,
    started_at: str,
    completed_at: str,
    status: int | None,
    payload: bytes,
    outcome: str,
    error_type: str | None,
) -> dict[str, Any]:
    return {
        "provider": PROVIDER,
        "symbol": SYMBOL,
        "endpoint": ENDPOINT,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "frequency": "daily",
        "authentication": "Authorization header",
        "attempt": attempt,
        "attempt_started_at_utc": started_at,
        "attempt_completed_at_utc": completed_at,
        "http_status": status,
        "payload_size_bytes": len(payload),
        "payload_sha256": _sha256(payload) if payload else None,
        "outcome": outcome,
        "error_type": error_type,
    }


def acquire_tiingo_eod(
    private_parent: Path,
    token: str,
    *,
    opener: Callable[..., Any] = urlopen,
    now: Callable[[], datetime] | None = None,
) -> AcquisitionOutcome:
    """Perform one logical acquisition with the narrowly allowed retry policy."""
    clock = now or (lambda: datetime.now(timezone.utc))
    if private_parent.exists() and any(private_parent.iterdir()):
        raise AcquisitionError(
            "Stage A1d private acquisition already exists; refusing another logical acquisition"
        )
    retrieval_id = _retrieval_id(clock())
    private_dir = private_parent / retrieval_id
    private_dir.mkdir(parents=True, exist_ok=False)

    request = build_request(token)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        started_at = clock().astimezone(timezone.utc).isoformat()
        payload = b""
        status: int | None = None
        error_type: str | None = None
        try:
            with opener(request, timeout=TIMEOUT_SECONDS) as response:
                response_status = getattr(response, "status", None)
                status = int(response_status if response_status is not None else response.getcode())
                payload = response.read()
        except HTTPError as exc:
            status = int(exc.code)
            payload = exc.read()
            error_type = type(exc).__name__
            exc.close()
        except (TimeoutError, URLError, OSError) as exc:
            error_type = type(exc).__name__

        completed_at = clock().astimezone(timezone.utc).isoformat()
        retryable = error_type is not None and status is None
        retryable = retryable or status == 429 or (
            status is not None and 500 <= status <= 599
        )
        successful_http = status is not None and 200 <= status <= 299
        outcome = (
            "SUCCESS"
            if successful_http and payload
            else "RETRYABLE_FAILURE"
            if retryable
            else "NON_RETRYABLE_FAILURE"
        )
        receipt = _receipt(
            attempt=attempt,
            started_at=started_at,
            completed_at=completed_at,
            status=status,
            payload=payload,
            outcome=outcome,
            error_type=error_type,
        )
        receipt_path = private_dir / f"attempt_{attempt}_receipt.json"
        _write_new_json(receipt_path, receipt)
        if payload and not successful_http:
            _write_new_bytes(private_dir / f"attempt_{attempt}_response.bin", payload)

        if successful_http:
            if not payload:
                raise AcquisitionError("empty successful response; content failure is not retried")
            raw_path = private_dir / "tiingo_response.json"
            _write_new_bytes(raw_path, payload)
            persisted = raw_path.read_bytes()
            if persisted != payload:
                raise AcquisitionError("private raw bytes changed while persisting")
            return AcquisitionOutcome(
                retrieval_id=retrieval_id,
                private_dir=private_dir,
                raw_path=raw_path,
                receipt_path=receipt_path,
                attempt_count=attempt,
                http_status=status,
                payload_size_bytes=len(payload),
                payload_sha256=_sha256(payload),
                acquired_at_utc=completed_at,
            )

        if retryable and attempt < MAX_ATTEMPTS:
            continue
        if retryable:
            raise AcquisitionError("bounded acquisition exhausted retry allowance")
        raise AcquisitionError("non-retryable HTTP/content failure")

    raise AcquisitionError("bounded acquisition ended without an outcome")


def validate_constants() -> None:
    """Protect the literal acquisition boundary against accidental edits."""
    if SYMBOL != "IWM" or START_DATE != "2005-05-11" or END_DATE != "2005-07-08":
        raise AcquisitionError("Stage A1d acquisition boundary changed")
    if MAX_ATTEMPTS != 2 or not math.isfinite(TIMEOUT_SECONDS):
        raise AcquisitionError("Stage A1d retry/timeout contract changed")
