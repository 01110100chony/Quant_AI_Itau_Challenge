# PROJECT_STATUS.md

## Desafio Quant AI 2026 — Estado Atual

**Fase:** `LAF_001 v1.0-frozen` — conteúdo Research congelado; H1-LAF pendente de registro
**Status:** `DRAFT`
**Última atualização:** 15/08/2026

Nenhuma tese está oficialmente promovida ou validada.

`LAF_001 — Liquidity Absorption Fragility` é a candidata Research atual. A
ordem humana final aprovou a specification `v1.0-frozen`, mas nenhuma
associação foi executada. O próximo marco é registrar H1-LAF em commit separado
de autorização/proveniência antes da execução Research única.

## LAF_001 — freeze Research pré-associação

- Retrieval imutável: `20260815T055848814Z`.
- Aquisição H0-A1: `01cc8408a83024663cc7cb7d434f82292072a945`.
- Resultados originais: `f549a1a8d8e4b06028100b22a450fa0e5c46473b`.
- Código corretivo H0-A1c: `176bb12b2413edb866cdcc38e86a497021cebd6c`.
- Parser corretivo: `laf-stage-a1-v1.0.1`.
- Cobertura por símbolo: 3.525/3.525 sessões XNYS, `2003-01-02`–`2016-12-30`.
- Exceções de calendário, nulls, zeros, negativos e violações OHLC: zero.
- Corporate actions: 389 dividendos e um split IWM, todos enumerados.
- Linhas OHLCV de 2017+: zero; corporate actions de 2017+: zero.
- Metadados dinâmicos de 2026 estavam no raw e no artefato original; a A1c os
  detectou e não emitiu seus valores em nenhum artefato canônico corretivo.
- Cinco hashes raw permaneceram idênticos.
- Auditoria do split: 20 sessões pré + evento + 20 pós; as três razões foram
  consistentes com continuidade local, sem constituir prova semântica.
- `VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION`.
- `SAFE_TO_RUN_LAF_STAGE_A2 = NO`; revisão humana pendente.
- Nenhum retorno geral, `PI`, `LAF`, `RV`, Corwin-Schultz, `TailLoss`, feature
  ou target havia sido calculado em A1/A1c.
- H0-A1d: `74e53946e9e2fbd07dce15e77d527fd5cd0d1f38`.
- A1d: `INCONCLUSIVE_TRANSPORT_NO_PAYLOAD`; dois receipts privados preservados,
  nenhum gate científico e nenhum retry autorizado.
- Construção Research aprovada: prior-only robust z em 252 sessões, embargo de
  split, mediana diária com ao menos 4 ETFs e média mensal das últimas 21 sessões.
- Invariância real/sintética a escalas positivas pré-split: PASS em `1e-12`.
- Independência sintética do target: PASS exato.
- Grid Research: 156 target months; 8 complete cases mecânicos, nenhum em
  2004–2010 e nenhum com estado Q80 classificável.
- Nenhuma regressão, associação ou gate Research foi observado antes de H1-LAF.

## LAF_001 — escopo e fronteiras vigentes

- Universo fixo: `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- Ativo-alvo: `SPY`.
- Warm-up permitido: `2003-01-01`–`2003-12-31`.
- Research permitido: `2004-01-01`–`2016-12-31`.
- Validation `2017-01`–`2021-12`: CLOSED.
- Final OOS `2022-01`–`2025-12`: CLOSED.
- 2026: integralmente excluído.
- Fonte Research: os cinco snapshots imutáveis Yahoo Finance Chart API já auditados.
- Raw OHLCV, Adj Close e corporate actions devem permanecer separados.
- Calendário candidato: XNYS via `exchange-calendars`.
- A decisão ocorre após o close da última sessão do mês; execução informacional
  é a primeira abertura SPY do mês seguinte.
- Modelo único: OLS completo LAF+RV e controle RV-only, HAC(3), gates prospectivos.
- Validation, Final OOS, estratégia, carteira e backtest permanecem não autorizados.

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
