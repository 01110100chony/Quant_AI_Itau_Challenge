from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "verify_research.py"
SPEC = importlib.util.spec_from_file_location("verify_research", MODULE_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import bootstrap guard
    raise RuntimeError(f"Could not load {MODULE_PATH}")
verify_research = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_research)


class SplitValidationTests(unittest.TestCase):
    def test_rejects_overlapping_research_and_validation(self) -> None:
        data = {
            "research_start": "2020-01-01",
            "research_end": "2021-12-31",
            "validation_start": "2021-12-31",
            "validation_end": "2022-12-31",
            "oos_start": "2023-01-01",
            "oos_end": "2024-01-01",
        }

        errors = verify_research._validate_split_ranges(data, Path("manifest.toml"))

        self.assertTrue(any("overlap" in error for error in errors))

    def test_accepts_ordered_non_overlapping_splits(self) -> None:
        data = {
            "research_start": "2020-01-01",
            "research_end": "2020-12-31",
            "validation_start": "2021-01-01",
            "validation_end": "2021-12-31",
            "oos_start": "2022-01-01",
            "oos_end": "2022-12-31",
        }

        errors = verify_research._validate_split_ranges(data, Path("manifest.toml"))

        self.assertEqual(errors, [])


class ContextValidationTests(unittest.TestCase):
    def test_rejects_missing_authority_field(self) -> None:
        text = """# Page

## Quick Summary

- **Purpose:** Test.
- **Read when:** Testing.
- **Load next:** None.

## Contents

- [Details](#details)

## Details

Text.
"""

        errors = verify_research._validate_context_text(text, "page.md")

        self.assertTrue(any("Authority" in error for error in errors))


class OOSValidationTests(unittest.TestCase):
    def test_opened_oos_requires_timestamp_and_approval(self) -> None:
        data = {
            "oos_opened": True,
            "oos_start": "2022-01-01",
            "oos_end": "2022-12-31",
            "oos_opened_at": "",
            "oos_approval_ref": "",
        }

        errors = verify_research._validate_oos_state(
            data,
            "OOS_OPENED",
            Path("manifest.toml"),
            {"oos_status": "OPENED"},
        )

        self.assertTrue(any("timezone-aware timestamp" in error for error in errors))
        self.assertTrue(any("oos_approval_ref" in error for error in errors))


TWO_STAGE_MANIFEST = """\
experiment_id = "XX_001"
thesis = "Two-stage design"
spec_version = "v1.0"
created_at = "2026-08-14T20:27:13-03:00"
status = "{status}"
research_start = "2001-02-28"
research_end = "2018-10-31"
validation_start = ""
validation_end = ""
oos_start = "2019-03-29"
oos_end = "2026-07-31"
oos_opened = true
oos_opened_at = "2026-08-14T21:09:04-03:00"
oos_approval_ref = "66bd72831eb803beeeefe63686ef915385f00b0c"
git_commit = "66bd72831eb803beeeefe63686ef915385f00b0c"
"""


class TwoStageDesignTests(unittest.TestCase):
    """Research -> final OOS, sem amostra de validacao intermediaria."""

    def _manifest(self, root: Path, status: str) -> Path:
        experiment = root / "XX_001"
        experiment.mkdir()
        for name in ("spec.md", "results.md", "decision.md"):
            (experiment / name).write_text("placeholder\n", encoding="utf-8")
        path = experiment / "manifest.toml"
        path.write_text(TWO_STAGE_MANIFEST.format(status=status), encoding="utf-8")
        return path

    def test_final_status_accepts_empty_validation_range(self) -> None:
        registry = {"XX_001": {"spec_version": "v1.0", "status": "FINAL",
                               "oos_status": "OPENED"}}
        with tempfile.TemporaryDirectory() as tmp:
            path = self._manifest(Path(tmp), "FINAL")

            experiment_id, errors = verify_research._validate_manifest(path, registry)

        self.assertEqual(experiment_id, "XX_001")
        self.assertEqual(errors, [])

    def test_validated_status_still_requires_validation_range(self) -> None:
        registry = {"XX_001": {"spec_version": "v1.0", "status": "VALIDATED",
                               "oos_status": "OPENED"}}
        with tempfile.TemporaryDirectory() as tmp:
            path = self._manifest(Path(tmp), "VALIDATED")

            _, errors = verify_research._validate_manifest(path, registry)

        self.assertTrue(any("validation date range" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
