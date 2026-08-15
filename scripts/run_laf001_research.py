#!/usr/bin/env python3
"""Preflight or execute the one authorized frozen LAF_001 Research analysis."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from laf_research import (  # noqa: E402
    HAC_MAXLAGS,
    RAW_RESPONSE_SHA256,
    SPEC_VERSION,
    SYMBOLS,
    ConstructionBundle,
    LAFResearchError,
    construct_bundle,
    execute_frozen_models,
    json_default,
    load_split_table,
    load_yahoo_research,
    scale_invariance_audit,
    target_independence_audit,
    write_json,
)


EXPERIMENT_ROOT = REPO_ROOT / "research" / "experiments" / "LAF_001"
RAW_ROOT = REPO_ROOT / "data" / "raw" / "laf_001" / "research" / "20260815T055848814Z"
SPLIT_TABLE = (
    REPO_ROOT
    / "data"
    / "processed"
    / "laf_001"
    / "stage_a1c"
    / "20260815T055848814Z"
    / "corporate_actions.csv"
)
MANIFEST_PATH = EXPERIMENT_ROOT / "manifest.toml"
OUTPUT_ROOT = EXPERIMENT_ROOT / "research_result"
RECEIPT_PATH = EXPERIMENT_ROOT / "research_execution_receipt.json"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _verify_execution_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "experiment_id": "LAF_001",
        "spec_version": SPEC_VERSION,
        "status": "FROZEN",
        "warmup_start": "2003-01-01",
        "warmup_end": "2003-12-31",
        "research_start": "2004-01-01",
        "research_end": "2016-12-31",
        "validation_start": "2017-01-01",
        "validation_end": "2021-12-31",
        "oos_start": "2022-01-01",
        "oos_end": "2025-12-31",
        "oos_opened": False,
        "research_execution_authorized": True,
    }
    divergences = {
        key: (value, manifest.get(key))
        for key, value in expected.items()
        if manifest.get(key) != value
    }
    frozen_commit = str(manifest.get("git_commit", ""))
    if divergences or len(frozen_commit) != 40:
        raise LAFResearchError(f"manifest is not execution-ready: {divergences}")
    _git("merge-base", "--is-ancestor", frozen_commit, _git("rev-parse", "HEAD"))


def run_preflight() -> tuple[dict[str, Any], ConstructionBundle]:
    """Run all pre-association construction/invariance checks without fitting."""
    frames = load_yahoo_research(RAW_ROOT)
    splits = load_split_table(SPLIT_TABLE)
    invariance = scale_invariance_audit(frames, splits)
    if not invariance["pass"]:
        raise LAFResearchError("positive-scale invariance failed before target construction")
    target_independence = target_independence_audit(frames, splits)
    if not target_independence["pass"]:
        raise LAFResearchError("target independence failed before association")
    bundle = construct_bundle(frames, splits)
    summary = {
        "mode": "PREFLIGHT_ONLY_NO_ASSOCIATION",
        "spec_version": SPEC_VERSION,
        "raw_hashes_unchanged": all(
            hashlib.sha256((RAW_ROOT / f"{symbol}_response.json").read_bytes()).hexdigest()
            == RAW_RESPONSE_SHA256[symbol]
            for symbol in SYMBOLS
        ),
        "boundary_audit": bundle.boundary_audit,
        "scale_invariance": invariance,
        "target_independence": target_independence,
        "execution_receipt_absent": not RECEIPT_PATH.exists(),
        "results_directory_absent": not OUTPUT_ROOT.exists(),
    }
    return summary, bundle


def execute_once() -> None:
    """Execute the frozen Research association once and persist its literal verdict."""
    if RECEIPT_PATH.exists() or OUTPUT_ROOT.exists():
        raise LAFResearchError("Research execution already started; automatic rerun forbidden")
    manifest = _manifest()
    _verify_execution_manifest(manifest)
    preflight, bundle = run_preflight()
    execution_commit = _git("rev-parse", "HEAD")
    receipt = {
        "experiment_id": "LAF_001",
        "status": "RUNNING",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "frozen_scientific_commit": manifest["git_commit"],
        "execution_commit": execution_commit,
        "research_target_months": ["2004-01", "2016-12"],
        "validation_loaded": False,
        "final_oos_loaded": False,
    }
    write_json(RECEIPT_PATH, receipt)
    try:
        result = execute_frozen_models(bundle.research_sample)
        _persist(result, bundle, preflight, manifest, execution_commit)
    except Exception as exc:
        receipt.update(
            {
                "status": "FAILED_STOP_NO_AUTOMATIC_RERUN",
                "finished_at_utc": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        write_json(RECEIPT_PATH, receipt)
        raise
    receipt.update(
        {
            "status": "COMPLETED",
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "verdict": result["gates"]["verdict"],
        }
    )
    write_json(RECEIPT_PATH, receipt)
    print(json.dumps({"status": "COMPLETED", "verdict": result["gates"]["verdict"]}))


def _persist(
    result: dict[str, Any],
    bundle: ConstructionBundle,
    preflight: dict[str, Any],
    manifest: dict[str, Any],
    execution_commit: str,
) -> None:
    OUTPUT_ROOT.mkdir(parents=False, exist_ok=False)
    full = result["full"]
    control = result["control"]
    coefficients = []
    for model in (full, control):
        for parameter in model.parameter_names:
            values = model.parameter(parameter)
            coefficients.append(
                {
                    "model": model.model,
                    "parameter": parameter,
                    "N": model.n,
                    **values,
                    "adjusted_r_squared": model.adjusted_r_squared,
                }
            )
    pd.DataFrame(coefficients).to_csv(OUTPUT_ROOT / "coefficients.csv", index=False)
    block_rows = []
    for block in result["blocks"]:
        parameter = (
            block["result"].parameter("laf")
            if block["result"] is not None
            else {
                "coefficient": np.nan,
                "hac_standard_error": np.nan,
                "t_statistic": np.nan,
                "one_sided_p_value": np.nan,
                "ci95_lower": np.nan,
                "ci95_upper": np.nan,
            }
        )
        block_rows.append(
            {
                "block": block["block"],
                "N": block["n"],
                "estimable": block["estimable"],
                "beta_laf_positive": block["beta_laf_positive"],
                **parameter,
            }
        )
    pd.DataFrame(block_rows).to_csv(OUTPUT_ROOT / "stability_blocks.csv", index=False)
    pd.DataFrame([result["state"]]).to_csv(OUTPUT_ROOT / "state_summary.csv", index=False)
    sample_columns = [
        "feature_month",
        "target_month",
        "feature_timestamp",
        "execution_timestamp",
        "laf",
        "rv",
        "tail_loss",
        "state_prior_month_count",
        "laf_prior_q80",
        "laf_state",
        "primary_complete_case",
    ]
    bundle.research_sample.loc[:, sample_columns].to_csv(
        OUTPUT_ROOT / "monthly_research_sample.csv", index=False
    )
    result_json = {
        "full_model": full.to_dict(),
        "rv_only_model": control.to_dict(),
        "stability_blocks": [
            {
                "block": block["block"],
                "n": block["n"],
                "estimable": block["estimable"],
                "beta_laf_positive": block["beta_laf_positive"],
                "result": block["result"].to_dict() if block["result"] is not None else None,
            }
            for block in result["blocks"]
        ],
        "state": result["state"],
        "gates": result["gates"],
        "boundary_audit": bundle.boundary_audit,
    }
    write_json(OUTPUT_ROOT / "research_results.json", result_json)
    provenance = {
        "experiment_id": "LAF_001",
        "spec_version": SPEC_VERSION,
        "frozen_scientific_commit": manifest["git_commit"],
        "execution_commit": execution_commit,
        "research_target_months": ["2004-01", "2016-12"],
        "validation_loaded": False,
        "final_oos_loaded": False,
        "estimator": {
            "method": "OLS with intercept",
            "covariance": "Newey-West HAC",
            "kernel": "Bartlett",
            "maxlags": HAC_MAXLAGS,
            "small_sample_correction": True,
            "use_t": True,
        },
        "input_hashes": {
            **{f"{symbol}_raw": RAW_RESPONSE_SHA256[symbol] for symbol in SYMBOLS},
            "stage_a1c_corporate_actions": hashlib.sha256(SPLIT_TABLE.read_bytes()).hexdigest(),
        },
        "preflight": preflight,
        "versions": {
            package: importlib.metadata.version(package)
            for package in ("numpy", "pandas", "scipy", "matplotlib", "exchange-calendars")
        },
    }
    write_json(OUTPUT_ROOT / "provenance.json", provenance)
    _write_report(OUTPUT_ROOT / "report.md", result_json)
    _write_figures(result, bundle.research_sample)


def _write_report(path: Path, result: dict[str, Any]) -> None:
    full = result["full_model"]
    control = result["rv_only_model"]
    laf_index = full["parameter_names"].index("laf")
    rv_index = full["parameter_names"].index("rv")
    lines = [
        "# LAF_001 frozen Research result",
        "",
        "Research target months only: 2004-01 through 2016-12. Validation and Final OOS remained closed.",
        "",
        "## Primary model",
        "",
        f"- N: {full['n']}",
        f"- beta_LAF: {full['coefficients'][laf_index]:.10g}",
        f"- HAC SE LAF: {full['hac_standard_errors'][laf_index]:.10g}",
        f"- t LAF: {full['t_statistics'][laf_index]:.6g}",
        f"- one-sided p LAF: {full['one_sided_p_values'][laf_index]:.8g}",
        f"- beta_RV: {full['coefficients'][rv_index]:.10g}",
        f"- adjusted R2 full: {full['adjusted_r_squared']:.10g}",
        f"- adjusted R2 RV-only: {control['adjusted_r_squared']:.10g}",
        "",
        "## Frozen gates",
        "",
        *[f"- {key}: {value}" for key, value in result["gates"].items()],
        "",
        "Secondary diagnostics cannot rescue CorePass. This Research screening is not validation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_figures(result: dict[str, Any], sample: pd.DataFrame) -> None:
    full = result["full"]
    names = ["laf", "rv"]
    betas = [full.parameter(name)["coefficient"] for name in names]
    lows = [full.parameter(name)["ci95_lower"] for name in names]
    highs = [full.parameter(name)["ci95_upper"] for name in names]
    figure, axis = plt.subplots(figsize=(6, 4))
    axis.errorbar(
        names,
        betas,
        yerr=[np.subtract(betas, lows), np.subtract(highs, betas)],
        fmt="o",
        capsize=4,
    )
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_ylabel("Coefficient with 95% HAC/t interval")
    figure.tight_layout()
    figure.savefig(OUTPUT_ROOT / "coefficients_laf_rv.png", dpi=160)
    plt.close(figure)

    states = sample.loc[sample["primary_complete_case"] & sample["laf_state"].notna()].copy()
    colors = states["laf_state"].map({"HIGH": "#c43d3d", "NORMAL": "#808080"})
    figure, axis = plt.subplots(figsize=(10, 4))
    axis.bar(pd.to_datetime(states["target_month"]), states["tail_loss"], color=colors, width=24)
    axis.set_ylabel("SPY monthly TailLoss")
    axis.set_xlabel("Target month (red = prior-only high LAF state)")
    figure.tight_layout()
    figure.savefig(OUTPUT_ROOT / "tail_loss_by_laf_state.png", dpi=160)
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            summary, _ = run_preflight()
            print(json.dumps(summary, indent=2, sort_keys=True, default=json_default))
        else:
            execute_once()
    except (LAFResearchError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"STOP_LAF_RESEARCH: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
