#!/usr/bin/env python3
"""Consolidate immutable run records into the requested execution receipt."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
LITERAL_DIR = ROOT / "audit" / "RSR_001"
SURFACE_DIR = ROOT / "audit" / "RSR_001_POST_OOS"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    receipt_path = LITERAL_DIR / "execution_receipt.json"
    receipt = load_json(receipt_path)
    primary = load_json(LITERAL_DIR / "primary_audit_run.json")
    surface = load_json(SURFACE_DIR / "surface_run.json")
    transcript_path = LITERAL_DIR / "transcript.txt"
    if sha256(transcript_path) != receipt["transcript_sha256"]:
        raise SystemExit("literal transcript changed after capture")

    required = (
        LITERAL_DIR / "preflight.md",
        LITERAL_DIR / "frozen_literal_results.json",
        LITERAL_DIR / "spec_compliant_results.json",
        LITERAL_DIR / "monthly_comparison.csv",
        LITERAL_DIR / "transcript.txt",
        SURFACE_DIR / "diagnostic_spec.md",
        SURFACE_DIR / "parameter_surface.csv",
        SURFACE_DIR / "results.md",
        ROOT / "research" / "experiments" / "RSR_001" / "timing_erratum.md",
        ROOT / "tests" / "research" / "test_rsr_001_audit.py",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"required audit artifacts missing: {missing}")
    receipt["finalized_at"] = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
    receipt["audit_runs"] = {
        "literal_frozen": {
            "started_at": receipt["started_at"],
            "finished_at": receipt["finished_at"],
            "command": receipt["command"],
            "exit_code": receipt["exit_code"],
            "result": "REPORTED_VALUES_MATCH; NO_GO; EXPECTED_PERSISTENCE_KEYERROR",
        },
        "primary_independent": primary,
        "post_oos_surface": surface,
    }
    receipt["aborted_diagnostic_attempt"] = {
        "persisted_results": False,
        "numerical_results_printed": False,
        "reason": "incorrect assertion that all W/S variants retain research n=213",
        "resolution": "mechanical warm-up counts recorded in diagnostic_execution_erratum.md",
    }
    receipt["final_classification"] = "VERDICT_UNCHANGED_AFTER_TIMING_ERRATUM"
    receipt["required_artifact_sha256"] = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in required
    }
    receipt["canonical_files_intentionally_unchanged"] = [
        "research/experiments/RSR_001/manifest.toml",
        "contexts/research/experiment_registry.md",
        "research/experiments/RSR_001/decision.md",
        "research/experiments/RSR_001/results.md",
        "AI_USE_LOG.md",
    ]
    receipt_path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "receipt": str(receipt_path),
        "transcript_sha256": receipt["transcript_sha256"],
        "artifacts": len(required),
        "classification": receipt["final_classification"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

