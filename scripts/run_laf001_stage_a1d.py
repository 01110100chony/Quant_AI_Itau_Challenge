#!/usr/bin/env python3
"""Run the private comparison and emit aggregate LAF_001 A1d artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_stage_a1d_audit import SourceAuditError, run_source_unit_audit  # noqa: E402


def _head_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main() -> int:
    """Audit one private retrieval without printing private observations."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{8}T[0-9]{9}Z", args.retrieval_id):
        parser.error("retrieval-id must use yyyyMMddTHHmmssfffZ")

    private_dir = (
        REPO_ROOT
        / "data"
        / "private"
        / "laf_001"
        / "stage_a1d"
        / args.retrieval_id
    )
    receipts = sorted(private_dir.glob("attempt_*_receipt.json"))
    successful = []
    for path in receipts:
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("outcome") == "SUCCESS":
            successful.append(path)
    if len(successful) != 1:
        parser.error("private retrieval must contain exactly one successful receipt")

    try:
        summary = run_source_unit_audit(
            raw_path=private_dir / "tiingo_response.json",
            receipt_path=successful[0],
            yahoo_path=(
                REPO_ROOT
                / "data"
                / "processed"
                / "laf_001"
                / "stage_a1c"
                / "20260815T055848814Z"
                / "split_unit_audit.csv"
            ),
            private_dir=private_dir,
            processed_dir=(
                REPO_ROOT
                / "data"
                / "processed"
                / "laf_001"
                / "stage_a1d"
                / args.retrieval_id
            ),
            retrieval_id=args.retrieval_id,
            h0_a1d_commit=_head_commit(),
        )
    except (OSError, ValueError, SourceAuditError, subprocess.CalledProcessError) as exc:
        print(f"STOP_CONTENT_AUDIT: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
