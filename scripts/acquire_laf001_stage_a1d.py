#!/usr/bin/env python3
"""Acquire the single authorized private Tiingo response for LAF_001 A1d."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_stage_a1d_collector import (  # noqa: E402
    AcquisitionError,
    acquire_tiingo_eod,
    validate_constants,
)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _preflight() -> str:
    if _git("branch", "--show-current") != "research/laf-001":
        raise AcquisitionError("collector requires branch research/laf-001")
    if _git("status", "--porcelain"):
        raise AcquisitionError("collector requires a clean worktree after H0-A1d")
    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "--no-index",
            "data/private/laf_001/stage_a1d/probe.txt",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if ignored.returncode != 0:
        raise AcquisitionError("private Stage A1d path is not ignored")
    if _git("ls-files", "--", "data/private"):
        raise AcquisitionError("a file below data/private is tracked")
    return _git("rev-parse", "HEAD")


def main() -> int:
    """Run the clean-tree preflight and one logical bounded acquisition."""
    token = os.environ.get("TIINGO_API_TOKEN")
    if not token:
        print("STOP_PRECONDITION: TIINGO_API_TOKEN is not present", file=sys.stderr)
        return 2
    try:
        validate_constants()
        h0_a1d_commit = _preflight()
        outcome = acquire_tiingo_eod(
            REPO_ROOT / "data" / "private" / "laf_001" / "stage_a1d",
            token,
        )
    except (AcquisitionError, subprocess.CalledProcessError) as exc:
        print(f"STOP_ACQUISITION: {exc}", file=sys.stderr)
        return 2
    sanitized = {
        "retrieval_id": outcome.retrieval_id,
        "h0_a1d_commit": h0_a1d_commit,
        "attempt_count": outcome.attempt_count,
        "http_status": outcome.http_status,
        "payload_size_bytes": outcome.payload_size_bytes,
        "payload_sha256": outcome.payload_sha256,
    }
    print(json.dumps(sanitized, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
