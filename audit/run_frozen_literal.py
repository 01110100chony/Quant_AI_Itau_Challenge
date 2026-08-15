#!/usr/bin/env python3
"""Capture the one literal H2 execution of frozen RSR_001 without overwriting it."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


H2 = "a45b3a4b272c65a80170ad3e5db0dd8bb75e3f5b"
EXPECTED_HASHES = {
    "data/raw/us_sector_etfs_plus_spy_adjusted_close.csv":
        "30bf7c3e6834e4eae29731be64d186d500826f9751c26fbf54c83b2856e8b177",
    "scripts/rsr_001.py":
        "9d9595660df5bc154354bc8cb4ddc9c37129331495bff8deaa80ea7c1098bfb3",
    "research/experiments/RSR_001/spec.md":
        "d0796279e743e8fe1030d33fbc17c07d5f1d9ae18e98f3ee0be8292ccfd05467",
    "requirements.txt":
        "d5303276ad646333897abf6e8ce84c8cbb6fa60a7b92c6547162c2cc84e1473b",
}


def sha256(path: Path) -> str:
    """Hash a file without text decoding or newline conversion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_versions() -> dict[str, str]:
    """Capture versions of every frozen direct dependency when installed."""

    packages = (
        "ipykernel", "jupyterlab", "matplotlib", "nbformat",
        "numpy", "pandas", "scipy", "yfinance",
    )
    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "NOT_INSTALLED"
    return versions


def main() -> int:
    """Validate H2 bytes, execute once, and persist transcript plus receipt."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    worktree = args.worktree.resolve()
    output = args.output.resolve()
    transcript_path = output / "transcript.txt"
    receipt_path = output / "execution_receipt.json"
    if transcript_path.exists() or receipt_path.exists():
        raise SystemExit("refusing to overwrite an existing literal execution record")

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=worktree, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if commit != H2:
        raise SystemExit(f"wrong detached commit: {commit}, expected {H2}")
    observed_hashes = {
        relative: sha256(worktree / relative) for relative in EXPECTED_HASHES
    }
    mismatches = {
        relative: {"expected": EXPECTED_HASHES[relative], "observed": observed}
        for relative, observed in observed_hashes.items()
        if observed != EXPECTED_HASHES[relative]
    }
    if mismatches:
        raise SystemExit(f"frozen byte mismatch: {json.dumps(mismatches, indent=2)}")

    started_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    command = [sys.executable, "-B", "scripts/rsr_001.py", "--abrir-oos"]
    completed = subprocess.run(
        command,
        cwd=worktree,
        input="ABRIR OOS\n",
        capture_output=True,
        text=True,
        check=False,
    )
    finished_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    transcript = (
        f"started_at={started_at.isoformat()}\n"
        f"finished_at={finished_at.isoformat()}\n"
        f"cwd={worktree}\n"
        f"commit={commit}\n"
        f"command={' '.join(command)}\n"
        f"exit_code={completed.returncode}\n"
        "\n===== STDOUT =====\n"
        f"{completed.stdout}"
        "\n===== STDERR =====\n"
        f"{completed.stderr}"
    )
    output.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(transcript, encoding="utf-8", newline="\n")
    transcript_hash = sha256(transcript_path)
    receipt = {
        "classification": "POST_OOS_FORENSIC_LITERAL_REPRODUCTION",
        "oos_was_already_consumed": True,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "command": command,
        "cwd": str(worktree),
        "git_commit": commit,
        "input_sha256": observed_hashes,
        "python": sys.version,
        "packages": package_versions(),
        "exit_code": completed.returncode,
        "expected_persistence_keyerror": completed.returncode != 0,
        "transcript": str(transcript_path),
        "transcript_sha256": transcript_hash,
        "frozen_output_files_present_after_run": {
            "reports/rsr_001_oos_bruto.csv":
                (worktree / "reports/rsr_001_oos_bruto.csv").exists(),
            "reports/rsr_001_veredito.csv":
                (worktree / "reports/rsr_001_veredito.csv").exists(),
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "exit_code": completed.returncode,
        "transcript_sha256": transcript_hash,
        "receipt": str(receipt_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

