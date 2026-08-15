# PROJECT_STATUS.md

## Desafio Quant AI 2026 — Estado Atual

**Fase:** `LAF_001 v0.1-draft` — preparação documental de Stage A1
**Status:** `DRAFT`
**Última atualização:** 15/08/2026

Nenhuma tese está oficialmente promovida ou validada.

`LAF_001 — Liquidity Absorption Fragility` é a candidata DRAFT atual. A
autorização humana vigente cobre exclusivamente a preparação documental da
Stage A1 de data/timing feasibility. Nenhum dado de mercado foi adquirido,
carregado, processado ou exibido para LAF_001; a Stage A1 empírica ainda não
está autorizada.

## LAF_001 — escopo documental autorizado

- Universo fixo candidato: `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- Ativo-alvo candidato: `SPY`.
- Warm-up permitido: `2003-01-01`–`2003-12-31`.
- Research permitido: `2004-01-01`–`2016-12-31`.
- `2017-01-01` em diante: CLOSED; não adquirir, carregar, processar ou exibir.
- 2026: integralmente excluído.
- Fonte primária candidata para futura auditoria estrutural: Yahoo Finance
  Chart API.
- Raw OHLCV, Adj Close e corporate actions devem permanecer separados.
- Calendário candidato: XNYS via `exchange-calendars`.
- A decisão ocorre após o close da última sessão do mês; eventual execução
  econômica só poderia ocorrer no open da primeira sessão seguinte.
- Validation, Final OOS, Stage B, estratégia, carteira e backtest permanecem
  não autorizados.

## CM_001 — encerramento definitivo

`CM_001 — Cross-Market Information Transmission` completed its first and only authorized Research Stage B execution. The primary H2 gate failed: beta `0.014480`, one-sided HAC p `0.361406`; therefore `CorePass=false` and the frozen verdict is `NO_GO`.

Gates: `CorePass=false`, `RobustnessPass=false`, `SpecificityPass=false`, `TimingPass=true`. H1 and all secondary diagnostics remained non-rescuing. No post-result variant, optimization, strategy or backtest was run.

## Provenance

- H0 Stage A: `78d9f6edca157cfcbd8643f52a9667d3a85c5fd0`.
- Original H1: `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818`.
- Original H2: `3cebbb0c54bea8b6023eb7e716de53d98402eeb9`.
- Corrective H1c: `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.
- Corrective H2c / execution commit: `694edf0d745c044cbfa9c257c44719bc0cd9f4ea`.

Original H1/H2 were preserved and superseded only for the P2 executable before any association. The corrected P2 common sample contained 2,033 strict-future pairs.

## CM_001 samples

- Research `2010-01-01`–`2018-12-31`: executed once.
- Validation `2019-01-01`–`2022-12-31`: CLOSED, not loaded.
- Final OOS `2023-01-01`–`2025-12-31`: CLOSED, not loaded.
- 2026: excluded.

Mechanical counts remained H1 `1938`, H2 `2034`, H3 `1850`. Full results and artifacts are in [`research/experiments/CM_001/results.md`](research/experiments/CM_001/results.md).

Effective Rank, Opportunity Set and Adaptive Factor Neutralization remain closed. Residual Momentum 12–1 remains only an unvalidated fallback baseline. LAF_001 was authorized by a separate, explicit human decision; it is not a rescue or extension of CM_001.
