# LAF_001 — Results

## Stage A1c corrective audit

The original Stage A1 result and its literal
`PASS_READY_FOR_STAGE_A2_DECISIONS` are preserved, but superseded for review by
the independent Stage A1c correction. Corrective artifacts are under
`data/processed/laf_001/stage_a1c/20260815T055848814Z/`; the original processed
snapshot was not modified.

### Block 1 — Historical boundary

The same five immutable Yahoo payloads were reused without network access.
Across `SPY`, `QQQ`, `IWM`, `DIA` and `MDY`, the correction parsed 17,625 daily
rows and 390 corporate actions inside the authorized 2003–2016 boundary.

| Calculated boundary flag | Result |
|---|---:|
| `historical_rows_2017_or_later` | 0 |
| `corporate_actions_2017_or_later` | 0 |
| `out_of_scope_dynamic_metadata_detected_in_raw` | true |
| `out_of_scope_dynamic_metadata_emitted` | false |
| `boundary_incident_disclosed` | true |
| `raw_hashes_unchanged` | true |

This explicitly distinguishes the absence of dated 2017+ historical arrays
from the presence of dynamic 2026 metadata in the raw response and original
artifact. No conclusion was extracted from those metadata values.

### Block 2 — Metadata and provenance remediation

Parser `laf-stage-a1-v1.0.1` emits only the 13 human-authorized metadata
columns. The field-name-only boundary audit contains 65 authorized emitted
field occurrences and 60 `OUT_OF_SCOPE_DYNAMIC` occurrences; zero dynamic
values were emitted.

| Provenance role | Commit |
|---|---|
| Raw acquisition H0 | `01cc8408a83024663cc7cb7d434f82292072a945` |
| Original results | `f549a1a8d8e4b06028100b22a450fa0e5c46473b` |
| Corrective audit code H0-A1c | `176bb12b2413edb866cdcc38e86a497021cebd6c` |

All five registered raw-response SHA-256 values matched independently:

| Symbol | SHA-256 |
|---|---|
| SPY | `306c43087e3a33048d29b47746250cfeaca6a0ec69532084d3e12e7cb2393153` |
| QQQ | `1d747eb4f1fc4b7f22e1cfdae40ad4932a9301324c666e101e3bebcd41a9e479` |
| IWM | `ee972d8c9d5ad737370df7f30d4954e8065316218ae08d64430f28b9f3feb0b3` |
| DIA | `30f7b0370a61be244cd0425602c7c4821dbc4ddef9d3598e267f6aaf8e6fbe53` |
| MDY | `5dba651a9fa9100ef740eaa27f4a8221b63371a8a44b22b1bf29113a46a41fc5` |

### Block 3 — Event-only IWM split-unit audit

The audit uses exactly 20 XNYS sessions before `2005-06-09`, the event session
and 20 sessions after it. `provider_close` means only provider Close; no claim
that it is a particular adjustment semantic is made.

| Mechanical quantity | Pre median | Post median | Post/pre | Classification |
|---|---:|---:|---:|---|
| `reported_volume` | 22,928,200 | 20,160,900 | 0.879306 | `CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF` |
| `provider_close_x_reported_volume` | 1,378,819,367.769623 | 1,269,132,289.122009 | 0.920449 | `CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF` |
| `adj_close_div_provider_close` | 0.755618 | 0.757345 | 1.002286 | `CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF` |

The 41-row table has positions `-20` through `+20`, no duplicate session dates,
no null cells and no authorized event-only calculation outside that window. A
manual first-row check reproduced both the multiplication and division.

Local continuity is not proof of the provider's historical Volume unit:

`VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION`

### Block 4 — Scientific meaning and stop

Stage A1c is a corrective structural feasibility audit. It did not calculate
general returns, PI, log(PI), LAF, RV, Corwin-Schultz, TailLoss, feature,
target, association, strategy or backtest. Validation and Final OOS were not
opened.

| Verification | Result |
|---|---|
| LAF synthetic suite | 27/27 passed |
| Full unit suite | 64/64 passed |
| Research harness verifier | passed |
| `git diff --check` | passed |
| Manual split-row multiplication/division | passed |
| Dynamic-field and event-only containment | passed |

HISTORICAL_DATA_FEASIBILITY = PASS
BOUNDARY_INCIDENT_REMEDIATION = PASS
PROVENANCE_REMEDIATION = PASS
VOLUME_UNIT_SEMANTICS = UNRESOLVED
SAFE_TO_RUN_LAF_STAGE_A2 = NO
READY_FOR_HUMAN_REVIEW = YES
