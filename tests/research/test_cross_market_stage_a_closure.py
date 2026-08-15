from __future__ import annotations

import json
import sys
import unittest
from datetime import date
from pathlib import Path


import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_a_closure import (  # noqa: E402
    assert_research_dates,
    build_attrition,
    build_corporate_action_impacts,
    classify_0052_missing,
    load_corporate_action_master,
    load_missing_crosscheck,
    load_twse_stock_day,
    load_twse_taiex_presence,
)


TWSE_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "twse_official_audit_2007_2018"
CLOSURE_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "stage_a_closure_2010_2018"
MAPPING_PATH = (
    REPO_ROOT
    / "data"
    / "processed"
    / "cm_001"
    / "stage_a_provider_audit_v2"
    / "session_mapping.csv"
)
REAL_DATA_AVAILABLE = all(path.exists() for path in (TWSE_ROOT, CLOSURE_ROOT, MAPPING_PATH))


class ClosureBoundaryTests(unittest.TestCase):
    def test_rejects_post_research_date(self) -> None:
        with self.assertRaises(ValueError):
            assert_research_dates(
                [date(2018, 12, 31), date(2019, 1, 1)], label="closure test"
            )


@unittest.skipUnless(REAL_DATA_AVAILABLE, "CM_001 closure raw artifacts are not present")
class ClosureRealDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.follower = load_twse_stock_day(TWSE_ROOT.glob("0052_????????.json"), "0052")
        cls.taiex = load_twse_taiex_presence(TWSE_ROOT.glob("TAIEX_????????.json"))
        cls.missing = classify_0052_missing(cls.follower)
        cls.master, cls.action_crosscheck = load_corporate_action_master(CLOSURE_ROOT)

    def test_missing_classification_reconciles_and_uses_no_future_field(self) -> None:
        counts = self.missing["classification"].value_counts().to_dict()
        self.assertEqual(
            counts,
            {
                "NO_0052_TRADE": 102,
                "NO_REGULAR_0052_TRADE_ODD_LOT_ONLY": 6,
            },
        )
        self.assertNotIn("UNRESOLVED", counts)
        self.assertTrue((self.missing["session_date"] <= date(2018, 12, 31)).all())

    def test_second_official_missing_crosscheck_agrees(self) -> None:
        crosscheck = load_missing_crosscheck(CLOSURE_ROOT, self.missing)
        self.assertEqual(len(crosscheck), 15)
        self.assertTrue(crosscheck["crosscheck_status"].eq("official source agrees").all())

    def test_official_corporate_action_master_is_complete_and_crosschecked(self) -> None:
        counts = self.master["instrument"].value_counts().to_dict()
        self.assertEqual(counts, {"0050": 11, "0052": 6})
        self.assertTrue(self.master["confidence"].eq("CROSS_CHECKED").all())
        self.assertTrue(
            self.action_crosscheck["crosscheck_status"].eq("official source agrees").all()
        )

    def test_corporate_action_impact_maps_only_sessions(self) -> None:
        h1, h3, h2 = build_corporate_action_impacts(
            self.follower["session_date"], self.master
        )
        self.assertEqual(len(h1), 6)
        self.assertEqual(len(h3), 6)
        self.assertEqual(len(h2), 6)
        self.assertFalse(h2["automatic_exclusion"].any())

    def test_mechanical_attrition_counts_without_price_values(self) -> None:
        flags, _, _ = build_attrition(
            MAPPING_PATH, self.follower, self.taiex, self.master
        )
        self.assertEqual(len(flags), 2_223)
        self.assertEqual(int(flags["eligible_us"].sum()), 2_137)
        self.assertEqual(int(flags["h1_input_available"].sum()), 1_944)
        self.assertEqual(int(flags["h1_usable_under_candidate_policy"].sum()), 1_938)
        self.assertEqual(int(flags["h2_input_available"].sum()), 2_034)
        self.assertEqual(int(flags["h3_input_available"].sum()), 1_856)
        self.assertEqual(int(flags["h3_usable_under_candidate_policy"].sum()), 1_850)
        prohibited_value_columns = {
            "GapRel",
            "IntradayRel",
            "PrevTWRel",
            "SemiSpecific",
            "BroadTech",
        }
        self.assertTrue(prohibited_value_columns.isdisjoint(flags.columns))

    def test_closure_diagnostics_preserve_closed_samples(self) -> None:
        path = (
            REPO_ROOT
            / "data"
            / "processed"
            / "cm_001"
            / "stage_a_closure_audit"
            / "diagnostics.json"
        )
        diagnostics = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(diagnostics["validation_loaded"])
        self.assertFalse(diagnostics["final_oos_loaded"])
        self.assertFalse(diagnostics["feature_target_relationship_calculated"])
        self.assertLessEqual(date.fromisoformat(diagnostics["max_research_date"]), date(2018, 12, 31))


if __name__ == "__main__":
    unittest.main()
