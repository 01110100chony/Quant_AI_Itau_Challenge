# RSR_001 — Decision

## Current decision

`FROZEN — PENDING HUMAN APPROVAL`

A specification esta completa e congelada. Nenhum campo permanece `TBD`. O
criterio `GO / CONDITIONAL GO / NO-GO` foi pre-registrado antes de qualquer
acesso ao Final OOS.

Nem `GO`, nem `CONDITIONAL GO`, nem `NO-GO` foi decidido, porque o Final OOS
ainda nao foi aberto.

## Required human approvals

Aprovar explicitamente, e commitar, antes de qualquer abertura do OOS:

- [ ] formula exata do sinal, incluindo cardinalidade das janelas
- [ ] estimacao point-in-time, com `W_d = {d-252, ..., d-1}`
- [ ] universo dos 9 ETFs setoriais
- [ ] carteira Top 3 / Bottom 3, peso igual
- [ ] rebalanceamento mensal no ultimo pregao
- [ ] tratamento de custo a 10 bps por perna
- [ ] metrica primaria Rank IC e secundaria de retorno liquido
- [ ] exclusao permanente de 2018-11-30 a 2019-02-28
- [ ] intervalo do OOS limpo, 2019-03-29 a 2026-07-31
- [ ] criterio `GO / CONDITIONAL GO / NO-GO`
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
