#!/usr/bin/env python3
"""Produce literal and spec-compliant primary RSR_001 audit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import rsr_001_audit as audit


def json_ready(value: object) -> object:
    """Convert NumPy/Pandas scalar values into JSON-native values."""

    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_reported_literal(
    metrics: dict[str, object],
    placebo: dict[str, float],
    gate: dict[str, object],
) -> None:
    """Hard-stop unless independent rounded metrics equal the published OOS."""

    observed = {
        "mean_ic": f"{float(metrics['mean_ic']):.4f}",
        "p1": f"{placebo['p1']:.4f}",
        "p2": f"{placebo['p2']:.4f}",
        "ic_blocks": [f"{value:.4f}" for value in gate["ic_blocks"]],
        "spread_pct": f"{float(metrics['spread_bruto_aa_log']) * 100:.2f}",
        "cost_pct": f"{float(metrics['custo_aa']) * 100:.2f}",
        "net_pct": f"{float(metrics['liquido_aa_log']) * 100:.2f}",
        "vol_pct": f"{float(metrics['volatilidade_log']) * 100:.2f}",
        "sharpe": f"{float(metrics['sharpe_log']):.2f}",
        "turnover": f"{float(metrics['turnover']):.3f}",
        "net_blocks_pct": [f"{value * 100:.2f}" for value in gate["net_blocks_aa"]],
        "verdict": gate["verdict"],
    }
    expected = {
        "mean_ic": "-0.0476",
        "p1": "0.8980",
        "p2": "0.8530",
        "ic_blocks": ["-0.0233", "-0.0422", "-0.0782"],
        "spread_pct": "-5.51",
        "cost_pct": "2.99",
        "net_pct": "-8.50",
        "vol_pct": "12.97",
        "sharpe": "-0.66",
        "turnover": "2.494",
        "net_blocks_pct": ["-7.68", "1.27", "-19.46"],
        "verdict": "NO_GO",
    }
    if observed != expected:
        raise RuntimeError(
            "MISMATCH_WITH_REPORTED_OOS\n"
            + json.dumps({"expected": expected, "observed": observed}, indent=2)
        )


def panel_output(panel: pd.DataFrame) -> pd.DataFrame:
    """Return the stable monthly columns used in public audit artifacts."""

    columns = [
        "target_end", "target_complete", "ic", "spread", "simple_spread",
        "turnover", "custo", "liquido", "simple_liquido",
    ]
    columns += [f"w_{ticker}" for ticker in audit.UNIVERSE]
    columns += [f"x_{ticker}" for ticker in audit.UNIVERSE]
    columns += [f"y_{ticker}" for ticker in audit.UNIVERSE]
    return panel.loc[:, columns].copy()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(ZoneInfo("America/Sao_Paulo"))

    prices = audit.load_prices(args.data.resolve())
    literal_all = audit.build_panel(
        prices,
        audit.PanelConfig(require_complete_target=False),
    )
    corrected_all = audit.build_panel(
        prices,
        audit.PanelConfig(require_complete_target=True),
    )
    literal = literal_all.loc[audit.OOS_START:audit.OOS_LITERAL_END].copy()
    corrected = corrected_all.loc[audit.OOS_START:audit.OOS_SPEC_END].copy()
    audit.assert_panel_integrity(literal)
    audit.assert_panel_integrity(corrected)
    if len(literal) != 89 or len(corrected) != 88:
        raise RuntimeError(f"unexpected OOS sizes: literal={len(literal)}, corrected={len(corrected)}")
    if literal.index[-1] != audit.OOS_LITERAL_END:
        raise RuntimeError("literal panel does not end on 2026-07-31")
    if pd.Timestamp(literal.iloc[-1]["target_end"]) != pd.Timestamp("2026-08-10"):
        raise RuntimeError("literal partial target does not end on 2026-08-10")
    if corrected.index[-1] != audit.OOS_SPEC_END:
        raise RuntimeError("corrected panel does not end on 2026-06-30")
    if pd.Timestamp(corrected.iloc[-1]["target_end"]) != pd.Timestamp("2026-07-31"):
        raise RuntimeError("corrected final target does not end on 2026-07-31")

    common_columns = [
        "ic", "spread", "simple_spread", "turnover", "custo", "liquido",
        "simple_liquido",
    ]
    common_columns += [f"w_{ticker}" for ticker in audit.UNIVERSE]
    common_columns += [f"x_{ticker}" for ticker in audit.UNIVERSE]
    common_columns += [f"y_{ticker}" for ticker in audit.UNIVERSE]
    left = literal.loc[corrected.index, common_columns]
    right = corrected.loc[:, common_columns]
    differences = (left - right).abs()
    tolerance = 1e-12
    maximum_difference = float(differences.to_numpy().max())
    if not np.allclose(left.to_numpy(), right.to_numpy(), rtol=0.0, atol=tolerance):
        raise RuntimeError(f"independent common-month mismatch: max_abs={maximum_difference}")

    literal_x, literal_y = audit.extract_signal_target(literal)
    corrected_x, corrected_y = audit.extract_signal_target(corrected)
    literal_placebo = audit.permutation_placebos(literal_x, literal_y)
    corrected_placebo = audit.permutation_placebos(corrected_x, corrected_y)
    literal_metrics = audit.metrics(literal)
    corrected_metrics = audit.metrics(corrected)
    literal_gate = audit.evaluate_frozen_gate(literal, literal_placebo)
    corrected_gate = audit.evaluate_frozen_gate(corrected, corrected_placebo)
    validate_reported_literal(literal_metrics, literal_placebo, literal_gate)

    partial = literal.iloc[[-1]].copy()
    partial_metrics = audit.metrics(partial)
    classification = (
        "VERDICT_UNCHANGED_AFTER_TIMING_ERRATUM"
        if corrected_gate["verdict"] == literal_gate["verdict"] == "NO_GO"
        else "OOS_INVALIDATED_BY_POST_FREEZE_BUG — HUMAN_DECISION_REQUIRED"
    )
    literal_result = {
        "classification": "POST_OOS_FORENSIC_LITERAL_REPRODUCTION",
        "implementation": "independent reconstruction checked against frozen transcript",
        "config": {
            "W": 252, "S": 21, "proxy": "SPY", "top_bottom": 3,
            "cost_bps": 10, "require_complete_target": False,
        },
        "metrics": literal_metrics,
        "placebos": literal_placebo,
        "gate": literal_gate,
        "reported_rounded_values_match": True,
        "known_timing_bug": {
            "feature_date": "2026-07-31",
            "observed_target_end": "2026-08-10",
            "required_target_end": "last trading day of 2026-08",
        },
    }
    corrected_result = {
        "classification": classification,
        "oos_was_already_consumed": True,
        "config": {
            "W": 252, "S": 21, "proxy": "SPY", "top_bottom": 3,
            "cost_bps": 10, "require_complete_target": True,
        },
        "metrics": corrected_metrics,
        "placebos": corrected_placebo,
        "gate": corrected_gate,
        "common_month_comparison": {
            "n": 88,
            "absolute_tolerance": tolerance,
            "maximum_absolute_difference": maximum_difference,
            "passed": True,
        },
        "excluded_partial_row": {
            "metrics": partial_metrics,
            "row": {
                key: json_ready(value)
                for key, value in panel_output(partial).iloc[0].to_dict().items()
            },
            "effect_on_annualized_metrics": {
                "mean_ic_literal_minus_corrected":
                    float(literal_metrics["mean_ic"]) - float(corrected_metrics["mean_ic"]),
                "net_log_aa_literal_minus_corrected":
                    float(literal_metrics["liquido_aa_log"]) - float(corrected_metrics["liquido_aa_log"]),
            },
        },
    }

    literal_path = output / "frozen_literal_results.json"
    corrected_path = output / "spec_compliant_results.json"
    literal_path.write_text(
        json.dumps(json_ready(literal_result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    corrected_path.write_text(
        json.dumps(json_ready(corrected_result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    panel_output(literal).to_csv(output / "frozen_literal_monthly.csv")

    comparison = panel_output(literal).add_prefix("literal_")
    corrected_output = panel_output(corrected).add_prefix("spec_")
    comparison = comparison.join(corrected_output, how="left")
    comparison["common_row_max_abs_difference"] = np.nan
    comparison.loc[corrected.index, "common_row_max_abs_difference"] = differences.max(axis=1)
    comparison.index.name = "feature_date"
    comparison.to_csv(output / "monthly_comparison.csv")

    finished_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    run_record = {
        "classification": classification,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "command": [str(item) for item in [Path(__file__), "--data", args.data, "--output", args.output]],
        "outputs": {
            path.name: sha256(path)
            for path in (
                literal_path,
                corrected_path,
                output / "frozen_literal_monthly.csv",
                output / "monthly_comparison.csv",
            )
        },
    }
    (output / "primary_audit_run.json").write_text(
        json.dumps(run_record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "classification": classification,
        "literal": literal_result,
        "corrected": corrected_result,
    }, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
