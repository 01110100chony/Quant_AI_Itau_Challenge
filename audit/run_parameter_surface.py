#!/usr/bin/env python3
"""Run the frozen RSR_001 post-OOS exploratory parameter surface."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import rsr_001_audit as audit


LABEL = "POST_OOS_EXPLORATORY — NOT VALIDATION — CANNOT RESCUE RSR_001"
SPEC_HASH = "c5904eb5c719d105d47e4f1d71c698dcad9376ceb6358fd1aceffc7abc62bf53"
DATA_HASH = "30bf7c3e6834e4eae29731be64d186d500826f9751c26fbf54c83b2856e8b177"
SIGNAL_GRID = list(itertools.product((126, 252, 504), (10, 21, 42), ("SPY", "EQUAL_WEIGHT_9")))
COST_GRID = (5, 10, 20)
SAMPLES = ("research", "oos_seen", "oos_b1", "oos_b2", "oos_b3")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def with_cost(panel: pd.DataFrame, cost_bps: int) -> pd.DataFrame:
    result = panel.copy()
    result["custo"] = cost_bps / 10_000 * result["turnover"]
    result["liquido"] = result["spread"] - result["custo"]
    result["simple_liquido"] = result["simple_spread"] - result["custo"]
    return result


def monotonic_direction(values: list[float], tolerance: float = 1e-15) -> str:
    differences = np.diff(values)
    if np.all(differences >= -tolerance):
        return "NONDECREASING"
    if np.all(differences <= tolerance):
        return "NONINCREASING"
    return "NON_MONOTONIC"


def format_number(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data_path = args.data.resolve()
    spec_path = args.spec.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if sha256(spec_path) != SPEC_HASH:
        raise SystemExit("diagnostic specification changed after freeze")
    if sha256(data_path) != DATA_HASH:
        raise SystemExit("grid input is not the exact frozen CSV byte sequence")
    if len(SIGNAL_GRID) != 18 or len(SIGNAL_GRID) * len(COST_GRID) != 54:
        raise SystemExit("closed grid cardinality changed")
    started_at = datetime.now(ZoneInfo("America/Sao_Paulo"))

    prices = audit.load_prices(data_path)
    signals: list[dict[str, object]] = []
    panels: dict[tuple[int, int, str], dict[str, pd.DataFrame]] = {}
    for number, (window, signal_window, proxy) in enumerate(SIGNAL_GRID, 1):
        config = audit.PanelConfig(
            estimation_window=window,
            signal_window=signal_window,
            proxy=proxy,
            cost_bps=10,
            require_complete_target=True,
        )
        full = audit.build_panel(prices, config)
        research = full.loc[audit.RESEARCH_START:audit.RESEARCH_END].copy()
        oos = full.loc[audit.OOS_START:audit.OOS_SPEC_END].copy()
        audit.assert_panel_integrity(research)
        audit.assert_panel_integrity(oos)
        expected_research_n = {
            (126, 10): 213, (126, 21): 213, (126, 42): 213,
            (252, 10): 213, (252, 21): 213, (252, 42): 212,
            (504, 10): 202, (504, 21): 201, (504, 42): 200,
        }[(window, signal_window)]
        if len(research) != expected_research_n or len(oos) != 88:
            raise RuntimeError(
                f"sample count changed for W={window}, S={signal_window}, proxy={proxy}: "
                f"research={len(research)}, oos={len(oos)}"
            )
        b1, b2, b3 = audit.fixed_oos_blocks(oos)
        sample_panels = {
            "research": research,
            "oos_seen": oos,
            "oos_b1": b1,
            "oos_b2": b2,
            "oos_b3": b3,
        }
        panels[(window, signal_window, proxy)] = sample_panels
        signal_result: dict[str, object] = {
            "W": window,
            "S": signal_window,
            "proxy": proxy,
            "label": LABEL,
        }
        for sample_name, sample_panel in sample_panels.items():
            x, y = audit.extract_signal_target(sample_panel)
            placebo = audit.permutation_placebos(x, y)
            signal_result[f"{sample_name}_n"] = len(sample_panel)
            signal_result[f"{sample_name}_mean_ic"] = float(sample_panel["ic"].mean())
            signal_result[f"{sample_name}_median_ic"] = float(sample_panel["ic"].median())
            signal_result[f"{sample_name}_hit_rate_ic"] = float((sample_panel["ic"] > 0).mean())
            signal_result[f"{sample_name}_p1_nominal"] = placebo["p1"]
            signal_result[f"{sample_name}_p2_nominal"] = placebo["p2"]
        block_ics = [
            float(signal_result[f"oos_b{block}_mean_ic"]) for block in (1, 2, 3)
        ]
        signal_result["oos_positive_ic_blocks"] = sum(value > 0 for value in block_ics)
        signal_result["oos_ic_block_range"] = max(block_ics) - min(block_ics)
        signal_result["oos_ic_sign_stability"] = (
            "ALL_POSITIVE" if all(value > 0 for value in block_ics)
            else "ALL_NONPOSITIVE" if all(value <= 0 for value in block_ics)
            else "MIXED"
        )
        signals.append(signal_result)
        print(
            f"[{number:02d}/18] W={window} S={signal_window} proxy={proxy} complete",
            flush=True,
        )

    for sample_name in SAMPLES:
        for placebo_name in ("p1", "p2"):
            nominal_key = f"{sample_name}_{placebo_name}_nominal"
            adjusted_key = f"{sample_name}_{placebo_name}_holm"
            adjusted = audit.holm_adjust(float(row[nominal_key]) for row in signals)
            for row, value in zip(signals, adjusted):
                row[adjusted_key] = value

    lookup = {
        (int(row["W"]), int(row["S"]), str(row["proxy"])): row for row in signals
    }
    for row in signals:
        window, signal_window, proxy = int(row["W"]), int(row["S"]), str(row["proxy"])
        along_w = [
            float(lookup[(candidate, signal_window, proxy)]["oos_seen_mean_ic"])
            for candidate in (126, 252, 504)
        ]
        along_s = [
            float(lookup[(window, candidate, proxy)]["oos_seen_mean_ic"])
            for candidate in (10, 21, 42)
        ]
        row["oos_w_monotonicity"] = monotonic_direction(along_w)
        row["oos_s_monotonicity"] = monotonic_direction(along_s)

    rows: list[dict[str, object]] = []
    economic_keys = (
        "spread_bruto_aa_log", "custo_aa", "liquido_aa_log",
        "liquido_aa_composto", "liquido_simples_cagr", "volatilidade_log",
        "sharpe_log", "turnover", "drawdown_congelado_log",
        "drawdown_convencional",
    )
    for signal_result in signals:
        key = (int(signal_result["W"]), int(signal_result["S"]), str(signal_result["proxy"]))
        for cost_bps in COST_GRID:
            row = dict(signal_result)
            row["cost_bps"] = cost_bps
            for sample_name, sample_panel in panels[key].items():
                sample_metrics = audit.metrics(with_cost(sample_panel, cost_bps))
                for metric_name in economic_keys:
                    row[f"{sample_name}_{metric_name}"] = sample_metrics[metric_name]
            rows.append(row)

    surface = pd.DataFrame(rows)
    if len(surface) != 54 or surface[["W", "S", "proxy", "cost_bps"]].duplicated().any():
        raise RuntimeError("surface is incomplete or contains duplicate combinations")
    surface_path = output / "parameter_surface.csv"
    surface.to_csv(surface_path, index=False)

    signal_frame = pd.DataFrame(signals)
    primary = signal_frame.query("W == 252 and S == 21 and proxy == 'SPY'").iloc[0]
    p1_holm_rejections = int((signal_frame["oos_seen_p1_holm"] < 0.10).sum())
    p2_holm_rejections = int((signal_frame["oos_seen_p2_holm"] < 0.10).sum())
    all_positive = int((signal_frame["oos_ic_sign_stability"] == "ALL_POSITIVE").sum())
    nonmonotonic_w = int((signal_frame["oos_w_monotonicity"] == "NON_MONOTONIC").sum())
    nonmonotonic_s = int((signal_frame["oos_s_monotonicity"] == "NON_MONOTONIC").sum())

    table_lines = [
        "| W | S | Proxy | Research IC | Seen OOS IC | P1 nominal/Holm | P2 nominal/Holm | OOS blocks IC | Stability |",
        "|---:|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for row in signals:
        blocks = "/".join(
            format_number(float(row[f"oos_b{block}_mean_ic"])) for block in (1, 2, 3)
        )
        table_lines.append(
            f"| {row['W']} | {row['S']} | {row['proxy']} | "
            f"{format_number(float(row['research_mean_ic']))} | "
            f"{format_number(float(row['oos_seen_mean_ic']))} | "
            f"{format_number(float(row['oos_seen_p1_nominal']))}/"
            f"{format_number(float(row['oos_seen_p1_holm']))} | "
            f"{format_number(float(row['oos_seen_p2_nominal']))}/"
            f"{format_number(float(row['oos_seen_p2_holm']))} | "
            f"{blocks} | {row['oos_ic_sign_stability']} |"
        )

    results_text = f"""# RSR_001 post-OOS parameter surface

`{LABEL}`

Diagnostic spec SHA-256: `{SPEC_HASH}`

Frozen data SHA-256: `{DATA_HASH}`

## Scope

All 18 frozen signal specifications and all 54 economic combinations were run.
The full table, including research, seen OOS, three fixed OOS blocks, nominal
and Holm p-values, costs, volatility, Sharpe, both drawdowns, turnover, and
secondary compounded returns, is `parameter_surface.csv`.

No row is a validation result. No row can change `RSR_001 = NO_GO`.

Research `n` varies mechanically from 200 to 213 because W/S warm-up differs;
the exact counts and the aborted first-run disclosure are recorded in
`diagnostic_execution_erratum.md`. Seen OOS remains fixed at `n=88` for every
specification.

## Complete signal surface

{chr(10).join(table_lines)}

## Family-level diagnostics

- Seen-OOS Holm P1 values below 0.10: `{p1_holm_rejections}` of 18.
- Seen-OOS Holm P2 values below 0.10: `{p2_holm_rejections}` of 18.
- Specifications with positive IC in all three OOS blocks: `{all_positive}` of 18.
- Row-level W monotonicity flags marked non-monotonic: `{nonmonotonic_w}` of 18.
- Row-level S monotonicity flags marked non-monotonic: `{nonmonotonic_s}` of 18.
- Frozen primary W=252/S=21/SPY seen-OOS IC:
  `{float(primary['oos_seen_mean_ic']):+.6f}`; P1/P2 nominal
  `{float(primary['oos_seen_p1_nominal']):.6f}` / `{float(primary['oos_seen_p2_nominal']):.6f}`.

Cost monotonicity is mechanical: increasing bps weakly decreases every net
return for a fixed position path. It is not scientific support. W/S/proxy
patterns are sensitivity descriptions after OOS consumption, not evidence for
selecting a replacement primary.

## Interpretation

Any favorable combination—including S=42—was inspected only after the OOS had
already been observed. It is hypothesis generation requiring a new prospective
or independently frozen dataset. The frozen primary and the timing-corrected
primary remain `NO_GO`.

`{LABEL}`
"""
    results_path = output / "results.md"
    results_path.write_text(results_text, encoding="utf-8", newline="\n")

    finished_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    run_record = {
        "diagnostic_id": "RSR_001_POST_OOS_DIAGNOSTIC",
        "classification": "POST_OOS_EXPLORATORY",
        "label": LABEL,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "diagnostic_spec_sha256": SPEC_HASH,
        "data_sha256": DATA_HASH,
        "command": [
            str(Path(__file__)), "--data", str(args.data), "--spec", str(args.spec),
            "--output", str(args.output),
        ],
        "signal_specifications": len(signal_frame),
        "economic_combinations": len(surface),
        "outputs": {
            "parameter_surface.csv": sha256(surface_path),
            "results.md": sha256(results_path),
        },
    }
    (output / "surface_run.json").write_text(
        json.dumps(run_record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(run_record, indent=2, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
