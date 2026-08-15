# RSR_001 — Decision

## Current decision

`NO-GO`  (status do harness: `FINAL`)

O Final OOS foi aberto uma unica vez em 14/08/2026 e o criterio pre-registrado
falhou nas seis condicoes. `ScientificPass = False` e `EconomicPass = False`,
o que da `NO-GO` de forma mecanica, sem margem de interpretacao.

Numeros e proveniencia em `results.md`. Reauditoria estatica dos artefatos
congelados em `reauditoria.md`.

    RESEARCH -> human approval -> commit H1 -> FROZEN -> open OOS once -> FINAL
                                                                          NO-GO

A decisao encerra o construct. `RSR_001` nao e recomendado para capital, e as
proibicoes pos-OOS da `spec.md` seguem em vigor: nenhum parametro, fronteira,
custo, universo ou criterio pode ser reajustado a partir daqui.

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

`Opened`, e **consumido**. 89 meses, de 2019-03-29 a 2026-07-31, observados uma
unica vez em 14/08/2026. Nao existe segunda abertura possivel para esta
specification.

O periodo de 2018-11-30 a 2019-02-28 permanece em quarentena permanente e nao
integrou o OOS. Ver `spec.md`, secao 10.

## Predecessor

`Residual Momentum 12-1` encerrado como `NO-GO de construct` em 14/08/2026,
por identidade algebrica de OLS verificada numericamente. Ver `spec.md`,
secao 9.

## Abertura — executada

    python scripts/rsr_001.py --abrir-oos

Executado em 14/08/2026, apos as 13 aprovacoes acima estarem marcadas e
commitadas em `H1`, com confirmacao digitada `ABRIR OOS` e `git status --short`
vazio no momento da abertura. Execucao unica.

A gravacao dos artefatos falhou depois de o veredito ter sido impresso, e os
CSVs nao existem. A decisao registrada foi nao reexecutar. Numeros transcritos
em `results.md`, analise da falha em `reauditoria.md`, achados F1 e F4.
