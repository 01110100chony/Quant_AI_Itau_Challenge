# LAF_001 — Stage A1 corrective erratum

`boundary_incident_disclosed: true`

## Incident

The historical Yahoo Finance Chart API responses used by Stage A1 contained
dynamic current metadata. Fields from that metadata were materialized in the
original processed result, both directly and through the aggregated
`metadata_json` field. Consequently, the original summary flag
`boundary_2017_or_later_loaded=false` was incomplete: it described the dated
historical arrays but did not disclose the separate metadata boundary.

This erratum preserves the original result and its history. It does not state
that the incident never occurred. The original
`PASS_READY_FOR_STAGE_A2_DECISIONS` is superseded by the independent Stage A1c
corrective audit for review purposes.

## Boundary distinctions

- The immutable payloads contain zero linhas OHLCV de 2017+.
- The immutable payloads contain zero corporate actions de 2017+.
- The raw responses and the original processed artifact contain metadados dinâmicos de 2026.
- Stage A1 and this correction calculated nenhuma feature, target ou associação.
- No economic conclusion was extracted from the dynamic metadata.

The first two statements concern dated historical arrays. They do not negate
the third statement about undated or current provider metadata. Stage A1c
therefore detects those fields by name, classifies them as
`OUT_OF_SCOPE_DYNAMIC`, emits no associated values and limits canonical
provider metadata to the human-authorized whitelist.

## Scope of correction

The five raw payloads remain byte-for-byte unchanged. The original processed
snapshot remains unchanged. New corrective artifacts are written only under
`data/processed/laf_001/stage_a1c/20260815T055848814Z/` with parser
`laf-stage-a1-v1.0.1` and exact corrective-code provenance.

No Stage A2 construction, general return, PI, log(PI), LAF, RV,
Corwin-Schultz, TailLoss, strategy or backtest is part of this correction.
Validation and Final OOS remain closed.
