# LAF_001 — Decision record

## Current decision

The independently executed Stage A1c corrective audit has remediated the
metadata-boundary disclosure and code-provenance defects. The original
`PASS_READY_FOR_STAGE_A2_DECISIONS` remains in Git history and in the preserved
original snapshot, but is superseded for review purposes by Stage A1c.

Stage A1c establishes historical-data feasibility only. It found zero OHLCV
rows and zero corporate actions dated 2017 or later, detected out-of-scope
dynamic metadata in the immutable raw responses, emitted none of those values
to the corrective canonical artifacts, verified all five registered raw
hashes and disclosed the incident in the corrective erratum.

The corrective runner recorded H0-A1c
`176bb12b2413edb866cdcc38e86a497021cebd6c` as its exact code commit. Raw
acquisition H0 remains `01cc8408a83024663cc7cb7d434f82292072a945`; the
original results commit remains
`f549a1a8d8e4b06028100b22a450fa0e5c46473b`.

## Split-unit decision

The event-only IWM audit contains exactly 20 XNYS sessions before the
`2005-06-09` split, the event session and 20 sessions after it. All three
pre-specified post/pre ratios are classified
`CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF`.

This local pattern does not prove what the provider's historical Volume unit
means. No provider documentation or independent source was authorized for
this correction. Therefore:

`VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION`

## Human decision required

Stage A2 remains pending every material choice in
[`stage_a2_decision_request.md`](stage_a2_decision_request.md), including a
human source decision for Volume semantics. The corrective result does not
authorize feature-side construction, target construction or any later stage.

## Prohibited stages

- Stage A2 remains prohibited until a separate explicit human order.
- Stage B remains prohibited.
- Validation and Final OOS remain CLOSED and undefined operationally.
- Strategy, portfolio and backtest remain prohibited.
- Feature, target and feature–target association remain prohibited.

## Corrective verdict

HISTORICAL_DATA_FEASIBILITY = PASS
BOUNDARY_INCIDENT_REMEDIATION = PASS
PROVENANCE_REMEDIATION = PASS
VOLUME_UNIT_SEMANTICS = UNRESOLVED
SAFE_TO_RUN_LAF_STAGE_A2 = NO
READY_FOR_HUMAN_REVIEW = YES
