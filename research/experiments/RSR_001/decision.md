# RSR_001 — Decision

## Current decision

`RESEARCH`  (equivalente a READY_FOR_FREEZE no vocabulario do harness)

A specification esta completa. Nenhum campo permanece `TBD` e o criterio de
decisao esta escrito. O experimento **ainda nao esta congelado**: o estado so
passa a `FROZEN` apos aprovacao humana registrada e commit da specification,
que e o carimbo temporal que da validade ao holdout.

Nem `GO`, nem `CONDITIONAL GO`, nem `NO-GO` foi decidido, porque o Final OOS
nao foi aberto.

    READY_FOR_FREEZE -> human approval -> commit -> FROZEN -> open OOS once

## Required human approvals

As 13 caixas abaixo correspondem, uma a uma e sem conteudo adicional, as 13
decisoes congeladas na autorizacao humana. Universo, rebalanceamento mensal,
metrica primaria e implementacao canonica nao possuem caixa propria: sao
aprovados por referencia a `spec.md` atraves dos itens 2, 6 e 12.

- [x] **1.** `Residual Momentum PIT = NO_GO` definitivo.
- [x] **2.** Construct do `RSR_001` = `Residual Short-Term Reversal`, conforme `spec.md`.
- [x] **3.** Correcao off-by-one: `W_d = {d-252,...,d-1}`, `S_t = {t-20,...,t}` com `S = 21`, e `F_t = {t-251,...,t-21}`.
- [x] **4.** `S = 21` como parametro **PRIMARY**.
- [x] **5.** `S = 42` como **EXPLORATORY ONLY**, sem promocao futura caso `S = 21` falhe.
- [x] **6.** Pesos `+1/3`, `-1/3` e `0`, com retorno long-short exatamente como na specification.
- [x] **7.** Custo primario de `10 bps`, calculado por `Cost_t = c * sum_i |w_{i,t} - w_{i,t-1}|`, com `w_{i,-1} = 0`; sensibilidades de 5 e 20 bps sao secundarias.
- [x] **8.** `P1` cross-sectional permutation placebo exatamente como pre-registrado.
- [x] **9.** `P2` temporal block permutation placebo exatamente como pre-registrado.
- [x] **10.** `P1` e `P2` unilaterais, `N_perm = 5000`, `seed = 7` e `p = (1 + #{null >= observed}) / (N + 1)`.
- [x] **11.** `A1` residualization ablation como evidencia secundaria, fora do gate de GO.
- [x] **12.** `ScientificPass`, `EconomicPass` e os vereditos `GO / CONDITIONAL_GO / NO_GO` exatamente como aprovados, incluindo a regra de positividade em pelo menos 2 de 3 blocos.
- [x] **13.** Quarentena permanente `2018-11-30` a `2019-02-28`; OOS unico `2019-03-29` a `2026-07-31`, `n = 89`, dividido previamente em meses `1..30`, `31..60` e `61..89`; nenhum parametro muda apos a abertura.

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
