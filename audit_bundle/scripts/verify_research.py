#!/usr/bin/env python3
"""Verify deterministic research-process contracts without external dependencies."""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_ROOT = REPO_ROOT / "contexts"
REGISTRY_PATH = CONTEXT_ROOT / "research" / "experiment_registry.md"
EXPERIMENT_ROOT = REPO_ROOT / "research" / "experiments"

CANONICAL_FILES = (
    "AGENTS.md",
    "PROJECT_STATUS.md",
    "TASKS.md",
    "Research_Log_Desafio_Quant_AI_2026.md",
    "AI_USE_LOG.md",
    "README.md",
    "contexts/CONTEXT_MAP.md",
    "contexts/research/protocol.md",
    "contexts/research/current_thesis.md",
    "contexts/research/rejected_hypotheses.md",
    "contexts/research/oos_policy.md",
    "contexts/research/experiment_registry.md",
    "contexts/research/hypothesis_template.md",
)

ALLOWED_STATUSES = {
    "DRAFT",
    "RESEARCH",
    "NO_GO",
    "CONDITIONAL_GO",
    "FROZEN",
    "VALIDATION",
    "VALIDATED",
    "OOS_OPENED",
    "FINAL",
}
ALLOWED_OOS_STATUSES = {"CLOSED", "OPENED"}
FROZEN_STATUSES = {"FROZEN", "VALIDATION", "VALIDATED", "OOS_OPENED", "FINAL"}
OOS_STATUSES = {"OOS_OPENED", "FINAL"}
REQUIRED_MANIFEST_FIELDS = {
    "experiment_id",
    "thesis",
    "spec_version",
    "created_at",
    "status",
    "research_start",
    "research_end",
    "validation_start",
    "validation_end",
    "oos_start",
    "oos_end",
    "oos_opened",
    "oos_opened_at",
    "oos_approval_ref",
    "git_commit",
}
REQUIRED_ARTIFACT_FILES = {"spec.md", "manifest.toml", "results.md", "decision.md"}
QUICK_SUMMARY_FIELDS = ("Purpose", "Read when", "Load next", "Authority")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REGISTRY_ID = re.compile(r"^[A-Z][A-Z0-9]*_[0-9]{3}$")
GIT_COMMIT = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _github_anchor(heading: str) -> str:
    """Return the GitHub-like anchor used by the controlled context headings."""
    normalized = re.sub(r"[^\w\s-]", "", heading.lower(), flags=re.UNICODE)
    return re.sub(r"[\s-]+", "-", normalized).strip("-")


def _validate_context_text(text: str, label: str | Path) -> list[str]:
    """Validate progressive-disclosure structure in supplied Markdown text."""
    errors: list[str] = []
    lines = text.splitlines()
    preview = lines[:80]

    try:
        quick_index = preview.index("## Quick Summary")
    except ValueError:
        return [f"{label}: missing '## Quick Summary' in first 80 lines"]
    try:
        contents_index = preview.index("## Contents")
    except ValueError:
        return [f"{label}: missing '## Contents' in first 80 lines"]

    if quick_index >= contents_index:
        errors.append(f"{label}: Quick Summary must precede Contents")

    summary = "\n".join(preview[quick_index + 1 : contents_index])
    for field in QUICK_SUMMARY_FIELDS:
        if not re.search(rf"- \*\*{re.escape(field)}:\*\*", summary):
            errors.append(f"{label}: Quick Summary missing '{field}'")

    detail_anchors = {
        _github_anchor(line.removeprefix("## "))
        for line in lines
        if line.startswith("## ")
        and line not in {"## Quick Summary", "## Contents"}
    }
    next_section = next(
        (
            index
            for index in range(contents_index + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    contents_text = "\n".join(lines[contents_index + 1 : next_section])
    contents_anchors = {
        target[1:]
        for target in MARKDOWN_LINK.findall(contents_text)
        if target.startswith("#")
    }
    if contents_anchors != detail_anchors:
        errors.append(
            f"{label}: Contents anchors {sorted(contents_anchors)} do not match "
            f"section anchors {sorted(detail_anchors)}"
        )
    return errors


def _validate_context_page(page: Path) -> list[str]:
    """Validate the progressive-disclosure contract for one context page."""
    return _validate_context_text(page.read_text(encoding="utf-8"), page)


def _validate_links(page: Path) -> list[str]:
    """Check local Markdown targets while leaving external URLs untouched."""
    errors: list[str] = []
    text = page.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path_part = target.split("#", maxsplit=1)[0]
        resolved = (page.parent / path_part).resolve()
        try:
            resolved.relative_to(REPO_ROOT.resolve())
        except ValueError:
            errors.append(f"{page}: link escapes repository: {raw_target}")
            continue
        if not resolved.exists():
            errors.append(f"{page}: broken local link: {raw_target}")
    return errors


def _read_registry(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Parse the registry's controlled Markdown table and reject duplicate IDs."""
    entries: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8 or cells[0] in {"ID", "---"}:
            continue
        experiment_id = cells[0]
        if not REGISTRY_ID.fullmatch(experiment_id):
            errors.append(f"{path}:{line_number}: invalid experiment ID '{experiment_id}'")
            continue
        if experiment_id in entries:
            errors.append(f"{path}:{line_number}: duplicate experiment ID '{experiment_id}'")
            continue
        status = cells[3]
        if status not in ALLOWED_STATUSES:
            errors.append(f"{path}:{line_number}: invalid status '{status}'")
        oos_status = cells[5]
        if oos_status not in ALLOWED_OOS_STATUSES:
            errors.append(f"{path}:{line_number}: invalid OOS status '{oos_status}'")
        entries[experiment_id] = {
            "spec_version": cells[2],
            "status": status,
            "oos_status": oos_status,
        }
    if not entries:
        errors.append(f"{path}: registry contains no experiment rows")
    return entries, errors


def _parse_optional_date(value: Any, field: str, path: Path) -> tuple[date | None, list[str]]:
    """Parse an optional ISO date from a TOML manifest."""
    if value == "" or value is None:
        return None, []
    if isinstance(value, datetime):
        return value.date(), []
    if isinstance(value, date):
        return value, []
    if not isinstance(value, str):
        return None, [f"{path}: {field} must be an ISO date or empty string"]
    try:
        return date.fromisoformat(value), []
    except ValueError:
        return None, [f"{path}: {field} is not a valid ISO date: {value!r}"]


def _parse_aware_datetime(value: Any, field: str, path: Path) -> tuple[datetime | None, list[str]]:
    """Parse a required timezone-aware ISO datetime."""
    if not value:
        return None, [f"{path}: {field} must be a timezone-aware timestamp"]
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    except ValueError:
        return None, [f"{path}: {field} is not a valid ISO timestamp: {value!r}"]
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, [f"{path}: {field} must include a timezone offset"]
    return parsed, []


def _validate_split_ranges(data: dict[str, Any], path: Path) -> list[str]:
    """Ensure complete, ordered, non-overlapping research/validation/OOS ranges."""
    errors: list[str] = []
    intervals: list[tuple[str, date, date]] = []
    for name in ("research", "validation", "oos"):
        start, start_errors = _parse_optional_date(data.get(f"{name}_start"), f"{name}_start", path)
        end, end_errors = _parse_optional_date(data.get(f"{name}_end"), f"{name}_end", path)
        errors.extend(start_errors + end_errors)
        if (start is None) != (end is None):
            errors.append(f"{path}: {name} split must define both start and end")
        elif start is not None and end is not None:
            if start > end:
                errors.append(f"{path}: {name}_start must not be after {name}_end")
            intervals.append((name, start, end))

    for (left_name, _, left_end), (right_name, right_start, _) in zip(intervals, intervals[1:]):
        if left_end >= right_start:
            errors.append(
                f"{path}: {left_name} and {right_name} splits overlap or are not ordered"
            )
    return errors


def _validate_oos_state(
    data: dict[str, Any],
    status: Any,
    path: Path,
    registry_entry: dict[str, str] | None,
) -> list[str]:
    """Validate OOS opening state, timestamp, approval, dates and registry sync."""
    errors: list[str] = []
    oos_opened = data.get("oos_opened")
    if not isinstance(oos_opened, bool):
        return [f"{path}: oos_opened must be boolean"]
    if oos_opened:
        if status not in OOS_STATUSES:
            errors.append(f"{path}: oos_opened=true requires OOS_OPENED or FINAL status")
        if not data.get("oos_start") or not data.get("oos_end"):
            errors.append(f"{path}: opened OOS requires an OOS date range")
        _, opened_errors = _parse_aware_datetime(
            data.get("oos_opened_at"), "oos_opened_at", path
        )
        errors.extend(opened_errors)
        if not data.get("oos_approval_ref"):
            errors.append(f"{path}: opened OOS requires oos_approval_ref")
        if registry_entry is not None and registry_entry["oos_status"] != "OPENED":
            errors.append(f"{path}: opened OOS must be OPENED in registry")
    else:
        if status in OOS_STATUSES:
            errors.append(f"{path}: OOS_OPENED or FINAL status requires oos_opened=true")
        if data.get("oos_opened_at") or data.get("oos_approval_ref"):
            errors.append(f"{path}: closed OOS cannot have opening metadata")
        if registry_entry is not None and registry_entry["oos_status"] != "CLOSED":
            errors.append(f"{path}: closed OOS must be CLOSED in registry")
    return errors


def _validate_manifest(
    path: Path, registry: dict[str, dict[str, str]]
) -> tuple[str | None, list[str]]:
    """Validate one machine-readable experiment manifest."""
    errors: list[str] = []
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, [f"{path}: cannot parse TOML: {exc}"]

    missing = sorted(REQUIRED_MANIFEST_FIELDS - data.keys())
    if missing:
        errors.append(f"{path}: missing manifest fields: {', '.join(missing)}")

    experiment_id = data.get("experiment_id")
    if not isinstance(experiment_id, str) or not REGISTRY_ID.fullmatch(experiment_id):
        errors.append(f"{path}: invalid experiment_id {experiment_id!r}")
        return None, errors
    if path.parent.name != experiment_id:
        errors.append(f"{path}: experiment_id must match directory name")

    status = data.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{path}: invalid status {status!r}")

    _, timestamp_errors = _parse_aware_datetime(data.get("created_at"), "created_at", path)
    errors.extend(timestamp_errors)
    errors.extend(_validate_split_ranges(data, path))

    if status in {"VALIDATION", "VALIDATED", "OOS_OPENED", "FINAL"}:
        if not data.get("validation_start") or not data.get("validation_end"):
            errors.append(f"{path}: {status} status requires a validation date range")

    registry_entry = registry.get(experiment_id)
    if registry_entry is None:
        errors.append(f"{path}: experiment is missing from registry")
    else:
        if registry_entry["status"] != status:
            errors.append(f"{path}: status does not match registry")
        if registry_entry["spec_version"] != data.get("spec_version"):
            errors.append(f"{path}: spec_version does not match registry")

    if status in FROZEN_STATUSES:
        if not data.get("spec_version"):
            errors.append(f"{path}: frozen experiment requires spec_version")
        if not GIT_COMMIT.fullmatch(str(data.get("git_commit", ""))):
            errors.append(f"{path}: frozen experiment requires a Git commit hash")

    errors.extend(_validate_oos_state(data, status, path, registry_entry))

    missing_artifacts = sorted(
        name for name in REQUIRED_ARTIFACT_FILES if not (path.parent / name).is_file()
    )
    if missing_artifacts:
        errors.append(f"{path.parent}: missing artifact files: {', '.join(missing_artifacts)}")
    return experiment_id, errors


def _validate_reference_tracking(root: Path) -> list[str]:
    """Reject tracked files under the reference-only checkout."""
    result = subprocess.run(
        ["git", "ls-files", "--", ".references"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"git ls-files failed while checking .references: {result.stderr.strip()}"]
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return [f"tracked reference-only path: {path}" for path in tracked]


def verify(root: Path = REPO_ROOT) -> tuple[list[str], dict[str, int]]:
    """Run every deterministic contract and return errors plus summary counts."""
    errors: list[str] = []
    for relative in CANONICAL_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing canonical file: {relative}")

    context_pages = sorted((root / "contexts").rglob("*.md"))
    for page in context_pages:
        errors.extend(_validate_context_page(page))
        errors.extend(_validate_links(page))

    critical_pages = [root / "AGENTS.md", root / "README.md"]
    critical_pages.extend(sorted((root / "research" / "experiments").rglob("*.md")))
    for page in critical_pages:
        if page.is_file():
            errors.extend(_validate_links(page))

    registry, registry_errors = _read_registry(root / REGISTRY_PATH.relative_to(REPO_ROOT))
    errors.extend(registry_errors)

    manifest_ids: set[str] = set()
    manifests = sorted((root / "research" / "experiments").glob("*/manifest.toml"))
    for manifest in manifests:
        experiment_id, manifest_errors = _validate_manifest(manifest, registry)
        errors.extend(manifest_errors)
        if experiment_id:
            if experiment_id in manifest_ids:
                errors.append(f"duplicate manifest experiment_id: {experiment_id}")
            manifest_ids.add(experiment_id)

    errors.extend(_validate_reference_tracking(root))
    return errors, {
        "context_pages": len(context_pages),
        "registry_entries": len(registry),
        "manifests": len(manifests),
    }


def main() -> int:
    """CLI entry point."""
    errors, counts = verify()
    if errors:
        print("[FAIL] research harness integrity errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "[OK] research harness integrity passed "
        f"({counts['context_pages']} context pages, "
        f"{counts['registry_entries']} registry entries, "
        f"{counts['manifests']} manifests)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
