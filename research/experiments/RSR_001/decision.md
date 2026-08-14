# RSR_001 — Decision

## Current decision

`READY_FOR_FREEZE`

A specification esta completa. Nenhum campo permanece `TBD` e o criterio de
decisao esta escrito. O experimento **ainda nao esta congelado**: o estado so
passa a `FROZEN` apos aprovacao humana registrada e commit da specification,
que e o carimbo temporal que da validade ao holdout.

Nem `GO`, nem `CONDITIONAL GO`, nem `NO-GO` foi decidido, porque o Final OOS
nao foi aberto.

    READY_FOR_FREEZE -> human approval -> commit -> FROZEN -> open OOS once

## Required human approvals

Aprovar explicitamente, e commitar, antes de qualquer abertura do OOS:

- [ ] formula exata do sinal, incluindo cardinalidade das janelas
- [ ] estimacao point-in-time, com `W_d = {d-252, ..., d-1}`
- [ ] universo dos 9 ETFs setoriais
- [ ] carteira Top 3 / Bottom 3, peso igual
- [ ] rebalanceamento mensal no ultimo pregao
- [ ] `S = 21` como primary; `S = 42` permanece exploratory e nunca sera promovido
- [ ] custo primario de 10 bps por perna; 5 e 20 bps apenas como sensibilidade
- [ ] metrica primaria Rank IC e secundaria de retorno liquido
- [ ] placebos `P1`, `P2` e `P3` conforme escritos, sem alteracao posterior
- [ ] exclusao permanente de 2018-11-30 a 2019-02-28
- [ ] intervalo do OOS limpo, 2019-03-29 a 2026-07-31
- [ ] criterio `ScientificPass` e `EconomicPass`, incluindo os tres blocos
- [ ] implementacao canonica: `scripts/rsr_001.py`

## OOS state

`Closed`. 89 meses, de 2019-03-29 a 2026-07-31, nunca observados sob nenhuma
metrica.

O periodo de 2018-11-30 a 2019-02-28 esta em quarentena permanente e nao
integra o OOS. Ver `spec.md`, secao 10.

## Predecessor

`Residual Momentum 12-1` encerrado como `NO-GO de construct` em 14/08/2026,
por identidade algebrica de OLS verificada numericamente. Ver `spec.md`,
secao 9.

## Abertura

Apos as aprovacoes acima estarem marcadas e commitadas:

    python scripts/rsr_001.py --abrir-oos

O script exige confirmacao digitada, registra `oos_opened_at` no manifesto e
grava o resultado bruto antes de qualquer interpretacao. Uma unica execucao.
