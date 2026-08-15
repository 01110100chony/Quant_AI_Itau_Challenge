#!/usr/bin/env python3
"""Run the LAF_001 Stage A1c audit from one immutable raw retrieval."""

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

from laf_stage_a1 import StructuralDataError, run_corrective_audit  # noqa: E402


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
    """Validate one retrieval identifier and produce the bounded audit artifacts."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{8}T[0-9]{9}Z", args.retrieval_id):
        parser.error("retrieval-id must use yyyyMMddTHHmmssfffZ")

    raw_dir = REPO_ROOT / "data" / "raw" / "laf_001" / "research" / args.retrieval_id
    processed_dir = (
        REPO_ROOT
        / "data"
        / "processed"
        / "laf_001"
        / "stage_a1c"
        / args.retrieval_id
    )
    disclosure_path = (
        REPO_ROOT
        / "research"
        / "experiments"
        / "LAF_001"
        / "stage_a1_corrective_erratum.md"
    )
    if not raw_dir.is_dir():
        parser.error(f"raw retrieval does not exist: {raw_dir}")
    try:
        summary = run_corrective_audit(
            raw_dir,
            processed_dir,
            corrective_audit_code_commit=_head_commit(),
            disclosure_path=disclosure_path,
        )
    except StructuralDataError as exc:
        print(f"STOP_DATA_INFEASIBLE: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 2 if summary["verdict"] != "PASS_CORRECTIVE_AUDIT_READY_FOR_HUMAN_REVIEW" else 0


if __name__ == "__main__":
    raise SystemExit(main())
