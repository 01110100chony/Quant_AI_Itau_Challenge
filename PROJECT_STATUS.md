# PROJECT_STATUS.md

## Desafio Quant AI 2026 — Estado Atual

**Fase:** `CM_001 v1.0.1-frozen` — Research Stage B complete
**Status:** `NO_GO`
**Última atualização:** 14/08/2026

Nenhuma tese está oficialmente promovida ou validada.

`CM_001 — Cross-Market Information Transmission` completed its first and only authorized Research Stage B execution. The primary H2 gate failed: beta `0.014480`, one-sided HAC p `0.361406`; therefore `CorePass=false` and the frozen verdict is `NO_GO`.

Gates: `CorePass=false`, `RobustnessPass=false`, `SpecificityPass=false`, `TimingPass=true`. H1 and all secondary diagnostics remained non-rescuing. No post-result variant, optimization, strategy or backtest was run.

## Provenance

- H0 Stage A: `78d9f6edca157cfcbd8643f52a9667d3a85c5fd0`.
- Original H1: `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818`.
- Original H2: `3cebbb0c54bea8b6023eb7e716de53d98402eeb9`.
- Corrective H1c: `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.
- Corrective H2c / execution commit: `694edf0d745c044cbfa9c257c44719bc0cd9f4ea`.

Original H1/H2 were preserved and superseded only for the P2 executable before any association. The corrected P2 common sample contained 2,033 strict-future pairs.

## Samples

- Research `2010-01-01`–`2018-12-31`: executed once.
- Validation `2019-01-01`–`2022-12-31`: CLOSED, not loaded.
- Final OOS `2023-01-01`–`2025-12-31`: CLOSED, not loaded.
- 2026: excluded.

Mechanical counts remained H1 `1938`, H2 `2034`, H3 `1850`. Full results and artifacts are in [`research/experiments/CM_001/results.md`](research/experiments/CM_001/results.md).

Effective Rank, Opportunity Set and Adaptive Factor Neutralization remain closed. Residual Momentum 12–1 remains only an unvalidated fallback baseline. No new research line is authorized by this result.
