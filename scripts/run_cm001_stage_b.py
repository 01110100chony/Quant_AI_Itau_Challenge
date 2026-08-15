"""Preflight or execute the frozen CM_001 Stage B exactly once."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import tomllib
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_b import (  # noqa: E402
    EXPECTED_COUNTS,
    HAC_MAXLAGS,
    PERMUTATIONS,
    RNG_SEED,
    RegressionResult,
    circular_shift_placebo,
    evaluate_gates,
    frozen_hac_ols,
    future_information_placebo,
    load_research_samples,
    mechanical_p2_common_count,
    monotonicity_diagnostics,
    stability_blocks,
    verify_mechanical_counts,
)


EXPERIMENT_ROOT = REPO_ROOT / "research" / "experiments" / "CM_001"
PROCESSED_ROOT = REPO_ROOT / "data" / "processed" / "cm_001"
FLAGS_PATH = PROCESSED_ROOT / "stage_a_closure_audit" / "mechanical_availability_flags.csv"
MAPPING_PATH = PROCESSED_ROOT / "stage_a_provider_audit_v2" / "session_mapping.csv"
MANIFEST_PATH = EXPERIMENT_ROOT / "manifest.toml"
OUTPUT_ROOT = EXPERIMENT_ROOT / "stage_b"
RECEIPT_PATH = EXPERIMENT_ROOT / "stage_b_execution_receipt.json"
FROZEN_VERSION = "v1.0.1-frozen"


def main() -> int:
    """Run a non-scientific preflight or the one authorized scientific execution."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(run_preflight(), indent=2, sort_keys=True))
        return 0
    execute_once()
    return 0


def run_preflight() -> dict[str, Any]:
    """Validate closed samples and registered counts without loading prices."""
    manifest = _read_manifest()
    counts = verify_mechanical_counts(FLAGS_PATH)
    p2_mechanical = mechanical_p2_common_count(MAPPING_PATH, FLAGS_PATH)
    return {
        "mode": "PREFLIGHT_ONLY_NO_FEATURE_TARGET_ASSOCIATION",
        "experiment_id": manifest["experiment_id"],
        "spec_version": manifest["spec_version"],
        "status": manifest["status"],
        "research": [manifest["research_start"], manifest["research_end"]],
        "validation": [manifest["validation_start"], manifest["validation_end"]],
        "final_oos": [manifest["oos_start"], manifest["oos_end"]],
        "oos_opened": manifest["oos_opened"],
        "mechanical_counts": counts,
        "p2_mechanical": p2_mechanical,
        "expected_counts": EXPECTED_COUNTS,
        "execution_receipt_absent": not RECEIPT_PATH.exists(),
        "results_directory_absent": not OUTPUT_ROOT.exists(),
    }


def execute_once() -> None:
    """Execute and persist the frozen Research analysis, guarded by a receipt."""
    if RECEIPT_PATH.exists() or OUTPUT_ROOT.exists():
        raise RuntimeError("Stage B has already started; automatic re-execution is forbidden")
    manifest = _read_manifest()
    _verify_frozen_manifest(manifest)
    frozen_commit = str(manifest["git_commit"])
    execution_commit = _git("rev-parse", "HEAD")
    _git("merge-base", "--is-ancestor", frozen_commit, execution_commit)
    receipt = {
        "experiment_id": "CM_001",
        "status": "RUNNING",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "frozen_scientific_commit": frozen_commit,
        "execution_commit": execution_commit,
        "research_start": "2010-01-01",
        "research_end": "2018-12-31",
        "validation_loaded": False,
        "final_oos_loaded": False,
    }
    _write_json(RECEIPT_PATH, receipt)
    try:
        counts = verify_mechanical_counts(FLAGS_PATH)
        samples = load_research_samples(PROCESSED_ROOT)
        results = _estimate(samples.primary)
        h2 = results["H2"]
        h3 = results["H3"]
        p1_h2 = circular_shift_placebo(
            samples.primary["H2"],
            target="intraday_rel",
            controls=[],
            observed_beta=h2.parameter("semi_specific")["coefficient"],
        )
        p1_h3 = circular_shift_placebo(
            samples.primary["H3"],
            target="intraday_rel",
            controls=["broad_tech", "prev_tw_rel"],
            observed_beta=h3.parameter("semi_specific")["coefficient"],
        )
        p2 = future_information_placebo(
            samples.primary["H2"], samples.eligible_window_table
        )
        blocks = stability_blocks(samples.primary["H2"])
        positive_blocks = sum(int(item["positive"]) for item in blocks)
        gates = evaluate_gates(
            h2=h2,
            h3=h3,
            p_perm_h2=p1_h2["p_perm"],
            p_perm_h3=p1_h3["p_perm"],
            positive_blocks=positive_blocks,
            timing_pass=p2["passed"],
        )
        robustness = _estimate_robustness(samples)
        diagnostics, quintiles = monotonicity_diagnostics(samples.primary["H2"])
        _persist_outputs(
            counts=counts,
            results=results,
            p1_h2=p1_h2,
            p1_h3=p1_h3,
            p2=p2,
            blocks=blocks,
            robustness=robustness,
            diagnostics=diagnostics,
            quintiles=quintiles,
            gates=gates,
            manifest=manifest,
            execution_commit=execution_commit,
        )
    except Exception as error:
        receipt.update(
            {
                "status": "FAILED_STOP_NO_AUTOMATIC_RERUN",
                "finished_at_utc": datetime.now(UTC).isoformat(),
                "error_type": type(error).__name__,
                "error": str(error),
            }
        )
        _write_json(RECEIPT_PATH, receipt)
        raise
    receipt.update(
        {
            "status": "COMPLETED",
            "finished_at_utc": datetime.now(UTC).isoformat(),
            "verdict": gates["verdict"],
        }
    )
    _write_json(RECEIPT_PATH, receipt)
    print(json.dumps({"status": "COMPLETED", "verdict": gates["verdict"]}))


def _estimate(samples: dict[str, pd.DataFrame] | Any) -> dict[str, RegressionResult]:
    return {
        "H1": frozen_hac_ols(
            samples["H1"], target="gap_rel", regressors=["semi_specific"], model="H1"
        ),
        "H2": frozen_hac_ols(
            samples["H2"],
            target="intraday_rel",
            regressors=["semi_specific"],
            model="H2",
        ),
        "H3": frozen_hac_ols(
            samples["H3"],
            target="intraday_rel",
            regressors=["semi_specific", "broad_tech", "prev_tw_rel"],
            model="H3",
        ),
    }


def _estimate_robustness(samples: Any) -> dict[str, RegressionResult]:
    robustness = samples.robustness_0050
    output = {
        "H1_0050": frozen_hac_ols(
            robustness["H1"],
            target="gap_rel_0050",
            regressors=["semi_specific"],
            model="H1_0050",
        ),
        "H2_0050": frozen_hac_ols(
            robustness["H2"],
            target="intraday_rel_0050",
            regressors=["semi_specific"],
            model="H2_0050",
        ),
        "H3_0050": frozen_hac_ols(
            robustness["H3"],
            target="intraday_rel_0050",
            regressors=["semi_specific", "broad_tech", "prev_tw_rel_0050"],
            model="H3_0050",
        ),
    }
    h2_one = samples.primary["H2"].loc[
        samples.primary["H2"]["n_us_sessions"].eq(1)
    ]
    h3_one = samples.primary["H3"].loc[
        samples.primary["H3"]["n_us_sessions"].eq(1)
    ]
    output["H2_n_us_1"] = frozen_hac_ols(
        h2_one,
        target="intraday_rel",
        regressors=["semi_specific"],
        model="H2_n_us_1",
    )
    output["H3_n_us_1"] = frozen_hac_ols(
        h3_one,
        target="intraday_rel",
        regressors=["semi_specific", "broad_tech", "prev_tw_rel"],
        model="H3_n_us_1",
    )
    return output


def _persist_outputs(**payload: Any) -> None:
    OUTPUT_ROOT.mkdir(parents=False, exist_ok=False)
    results: dict[str, RegressionResult] = payload["results"]
    p1_h2 = payload["p1_h2"]
    p1_h3 = payload["p1_h3"]
    p2 = payload["p2"]
    blocks = payload["blocks"]
    robustness: dict[str, RegressionResult] = payload["robustness"]
    quintiles: pd.DataFrame = payload["quintiles"]

    main_rows = [_result_row(name, result) for name, result in results.items()]
    robustness_rows = [
        _result_row(name, result) for name, result in robustness.items()
    ]
    pd.DataFrame(main_rows).to_csv(OUTPUT_ROOT / "main_results.csv", index=False)
    pd.DataFrame(robustness_rows).to_csv(
        OUTPUT_ROOT / "secondary_robustness.csv", index=False
    )
    block_rows = [
        {
            "block": item["block"],
            "start": item["start"],
            "end": item["end"],
            "positive": item["positive"],
            **_result_row(item["result"].model, item["result"]),
        }
        for item in blocks
    ]
    pd.DataFrame(block_rows).to_csv(OUTPUT_ROOT / "stability_blocks.csv", index=False)
    quintiles.to_csv(OUTPUT_ROOT / "quintile_diagnostics.csv", index=False)
    p2["common_sessions"].to_csv(
        OUTPUT_ROOT / "p2_common_session_mapping.csv", index=False
    )
    pd.DataFrame(
        {"beta_perm_h2": p1_h2["beta_perm"], "beta_perm_h3": p1_h3["beta_perm"]}
    ).to_csv(OUTPUT_ROOT / "placebo_distributions.csv", index=False)

    result_json = {
        "mechanical_counts": payload["counts"],
        "main": {name: result.to_dict() for name, result in results.items()},
        "P1": {"H2": _without_draws(p1_h2), "H3": _without_draws(p1_h3)},
        "P2": {
            "n_common": p2["n_common"],
            "correct": p2["correct"].to_dict(),
            "future": p2["future"].to_dict(),
            "correct_standardized_beta": p2["correct_standardized_beta"],
            "future_standardized_beta": p2["future_standardized_beta"],
            "passed": p2["passed"],
        },
        "positive_stability_blocks": sum(int(item["positive"]) for item in blocks),
        "secondary": {name: result.to_dict() for name, result in robustness.items()},
        "diagnostics": payload["diagnostics"],
        "gates": payload["gates"],
    }
    _write_json(OUTPUT_ROOT / "stage_b_results.json", result_json)
    provenance = {
        "experiment_id": "CM_001",
        "spec_version": FROZEN_VERSION,
        "frozen_scientific_commit": payload["manifest"]["git_commit"],
        "execution_commit": payload["execution_commit"],
        "retrieval_or_execution_date": date.today().isoformat(),
        "research_period": ["2010-01-01", "2018-12-31"],
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
        "placebo": {"B": PERMUTATIONS, "seed": RNG_SEED},
        "inputs": _input_provenance(),
        "versions": {
            package: importlib.metadata.version(package)
            for package in ("numpy", "pandas", "scipy", "matplotlib")
        },
        "parser": "src/cross_market_stage_b.py@frozen_scientific_commit",
    }
    _write_json(OUTPUT_ROOT / "provenance.json", provenance)
    _write_report(OUTPUT_ROOT / "report.md", result_json)
    _write_figures(results, p1_h2, quintiles)


def _result_row(label: str, result: RegressionResult) -> dict[str, Any]:
    semi = result.parameter("semi_specific")
    return {
        "model": label,
        "N": result.n,
        "beta_semi_specific": semi["coefficient"],
        "hac_se": semi["hac_standard_error"],
        "t": semi["t_statistic"],
        "p_one_sided": semi["one_sided_p_value"],
        "ci95_lower": semi["ci95_lower"],
        "ci95_upper": semi["ci95_upper"],
        "adjusted_r_squared": result.adjusted_r_squared,
        "effect_1sd_bps": result.semi_specific_effect_1sd_bps,
    }


def _without_draws(placebo: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in placebo.items() if key != "beta_perm"}


def _write_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# CM_001 frozen Stage B result",
        "",
        "Research only: 2010-01-01–2018-12-31. Validation and Final OOS remained closed.",
        "",
        "## Main models",
        "",
        "| Model | N | beta | HAC SE | t | one-sided p | 95% CI | Adj. R2 | 1 SD effect (bps) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, item in result["main"].items():
        row = _result_row(name, RegressionResult(**item))
        lines.append(
            f"| {name} | {row['N']} | {row['beta_semi_specific']:.8g} | "
            f"{row['hac_se']:.8g} | {row['t']:.4f} | {row['p_one_sided']:.6g} | "
            f"[{row['ci95_lower']:.8g}, {row['ci95_upper']:.8g}] | "
            f"{row['adjusted_r_squared']:.6g} | {row['effect_1sd_bps']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Frozen gates",
            "",
            *[f"- {key}: {value}" for key, value in result["gates"].items()],
            "",
            "H1 and secondary diagnostics were not allowed to rescue the primary H2 gate.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_figures(
    results: dict[str, RegressionResult],
    p1_h2: dict[str, Any],
    quintiles: pd.DataFrame,
) -> None:
    names = list(results)
    betas = [results[name].parameter("semi_specific")["coefficient"] for name in names]
    low = [results[name].parameter("semi_specific")["ci95_lower"] for name in names]
    high = [results[name].parameter("semi_specific")["ci95_upper"] for name in names]
    figure, axis = plt.subplots(figsize=(6, 4))
    axis.errorbar(
        names,
        betas,
        yerr=[np.subtract(betas, low), np.subtract(high, betas)],
        fmt="o",
        capsize=4,
    )
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_ylabel("SemiSpecific coefficient (log-return units)")
    figure.tight_layout()
    figure.savefig(OUTPUT_ROOT / "main_coefficients.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6, 4))
    axis.hist(p1_h2["beta_perm"], bins=40)
    axis.axvline(
        results["H2"].parameter("semi_specific")["coefficient"],
        color="red",
        label="observed H2 beta",
    )
    axis.legend()
    axis.set_xlabel("Circular-shift placebo beta")
    figure.tight_layout()
    figure.savefig(OUTPUT_ROOT / "p1_h2_placebo.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6, 4))
    axis.plot(quintiles["quintile"].astype(int), quintiles["mean_intraday_rel"], marker="o")
    axis.set_xlabel("SemiSpecific quintile")
    axis.set_ylabel("Mean IntradayRel")
    figure.tight_layout()
    figure.savefig(OUTPUT_ROOT / "quintile_means.png", dpi=160)
    plt.close(figure)


def _input_provenance() -> list[dict[str, Any]]:
    paths = [
        FLAGS_PATH,
        PROCESSED_ROOT / "stage_a_provider_audit_v2" / "session_mapping.csv",
        PROCESSED_ROOT / "stage_a_closure_audit" / "corporate_action_master.csv",
    ]
    canonical = PROCESSED_ROOT / "stage_a_provider_audit_v2" / "canonical"
    paths.extend(canonical / f"{asset}_ohlc.csv" for asset in ("XSD", "QQQ", "SPY", "0050", "TAIEX"))
    paths.append(canonical / "0052_ohlc_valid_rows.csv")
    return [
        {
            "path": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in paths
    ]


def _read_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _verify_frozen_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "experiment_id": "CM_001",
        "spec_version": FROZEN_VERSION,
        "status": "FROZEN",
        "research_start": "2010-01-01",
        "research_end": "2018-12-31",
        "validation_start": "2019-01-01",
        "validation_end": "2022-12-31",
        "oos_start": "2023-01-01",
        "oos_end": "2025-12-31",
        "oos_opened": False,
    }
    divergences = {
        key: (expected_value, manifest.get(key))
        for key, expected_value in expected.items()
        if manifest.get(key) != expected_value
    }
    if divergences or not manifest.get("git_commit"):
        raise ValueError(f"manifest is not execution-ready: {divergences}")


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


if __name__ == "__main__":
    raise SystemExit(main())
