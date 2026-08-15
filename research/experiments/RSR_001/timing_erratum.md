# RSR_001 — timing erratum after the consumed OOS

Classification: `POST_OOS_TIMING_ERRATUM`

Audit base: `9660319d0da25767f1be8b1240de9653893bd2e8`

Frozen H2: `a45b3a4b272c65a80170ad3e5db0dd8bb75e3f5b`

## Error

The frozen specification defines `Y_{t+1}` as the cumulative log return from
`t` exclusive through the last trading day of the following month, inclusive.
The frozen snapshot ends on 2026-08-10. The frozen implementation treats the
last available observation of every calendar month as that month's close, so
the feature dated 2026-07-31 receives a target ending on 2026-08-10 rather than
the last trading day of August 2026.

This is a material post-freeze timing bug. It does not authorize a parameter,
sample, mechanism, or success-criterion change, and correction cannot restore a
virgin OOS because the 2019–2026 outcomes have already been observed.

## Forensic reproduction

The literal detached-H2 run reproduced the reported output and then failed at
the known persistence bug:

- feature dates: 2019-03-29 through 2026-07-31, `n=89`;
- final observed target end: 2026-08-10;
- mean IC: `-0.0475655431`;
- P1/P2: `0.8980203959` / `0.8530293941`;
- net log return: `-8.503215%` annualized;
- verdict: `NO_GO`.

The rounded values match the previously reported OOS in full. The traceback is
preserved in `audit/RSR_001/transcript.txt`.

## Specification-compliant correction

A target month is accepted only when the frozen snapshot contains an
observation in a later calendar month, providing mechanical evidence that the
target month is complete. This excludes only the feature dated 2026-07-31.

- feature dates: 2019-03-29 through 2026-06-30, `n=88`;
- final target end: 2026-07-31;
- mean IC: `-0.0530303030`;
- P1/P2: `0.9220155969` / `0.8776244751`;
- fixed blocks 1..30 / 31..60 / 61..88 IC:
  `-0.0233333333`, `-0.0422222222`, `-0.0964285714`;
- net log return: `-8.710755%` annualized;
- fixed-block net log returns:
  `-7.684785%`, `+1.268183%`, `-20.501726%` annualized;
- ScientificPass: false;
- EconomicPass: false;
- verdict: `NO_GO`.

The independent implementation agrees exactly, month by month, with all 88
common literal observations (`maximum absolute difference = 0.0`, absolute
tolerance `1e-12`). It does not import `painel`, `residuos_pit`, `matrizes`,
`placebos`, or `avaliar_criterio` from the frozen script.

## Isolated partial-row contribution

The excluded 2026-07-31 row used only 2026-08-03 through 2026-08-10:

- IC: `+0.4333333333`;
- monthly log spread: `+1.146688%`;
- monthly cost: `0.333333%`;
- monthly net log return: `+0.813355%`.

Including that incomplete positive row raised full-sample mean IC by
`0.00546476` and annualized net log return by `0.207539` percentage point.

## Decision

`VERDICT_UNCHANGED_AFTER_TIMING_ERRATUM`.

This erratum preserves the original `RSR_001 = NO_GO`. It is corrective
post-OOS evidence, not a new validation, and it does not change canonical
manifest, registry, decision, or results metadata without a separate human
decision.
