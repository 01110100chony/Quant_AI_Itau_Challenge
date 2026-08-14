# RSR_001 — Residual Short-Term Reversal in Sector ETFs

## Identity

- **Experiment ID:** RSR_001
- **Spec version:** v1.0
- **Status:** `FROZEN — PENDING HUMAN APPROVAL`
- **Created at:** 2026-08-14
- **Predecessor:** construct do `Residual Momentum 12–1` encerrado como `NO-GO`. Ver secao 9.
- **Canonical context:** este arquivo.

## Research specification

- **Research question:** Choques idiossincraticos de curto prazo, apos removido o componente comum de mercado, apresentam sobrerreacao e reversao parcial no periodo seguinte entre ETFs setoriais?

- **Economic mechanism:** o componente comum de mercado e observado simultaneamente por todos os participantes e tende a ser incorporado rapidamente. Choques residuais de curto prazo, ao contrario, podem carregar pressao de liquidez, desequilibrio temporario de posicionamento e sobrerreacao. Se isso ocorrer, movimentos residuais extremos em janela curta devem reverter parcialmente no periodo seguinte. A aposta e em provisao de liquidez no espaco idiossincratico, nao em difusao lenta de informacao.

- **Null hypothesis:** `H0` o ranking cross-sectional de RSR nao carrega informacao sobre o retorno do mes seguinte. `E[IC] = 0`.

- **Alternative hypothesis:** `H1` `E[IC] > 0`, isto e, ativos com resíduo acumulado mais negativo nos ultimos 21 pregoes superam ativos com resíduo acumulado mais positivo.

- **Expected direction:** positiva por construcao do sinal, que ja embute a inversao.

- **Feature `X_t`:**

  Janelas, com cardinalidade explicita:
  `W_d = {d-252, ..., d-1}`, `|W_d| = 252` — janela de estimacao, estritamente anterior a `d`
  `S_t = {t-20, ..., t}`, `|S_t| = 21` — janela de reversao

  Estimacao point-in-time, OLS com intercepto:
  `alpha_hat[i,d-1], beta_hat[i,d-1] = OLS(r[i,s], r[m,s])` para `s` em `W_d`

  Residuo:
  `eps[i,d] = r[i,d] - alpha_hat[i,d-1] - beta_hat[i,d-1] * r[m,d]`

  Sinal:
  `RSR[i,t] = - soma de eps[i,tau] para tau em S_t`

  A janela de estimacao e estritamente anterior ao dia do residuo. A identidade de OLS que invalidou o construct anterior nao se aplica aqui: a soma dos residuos point-in-time em qualquer janela nao e zero por construcao. Verificado: media de `|soma de 252 residuos|` igual a 0,0650, contra 1e-16 no construct in-sample.

- **Target `Y_{t+1}`:** retorno log acumulado de `t` exclusive ate o ultimo pregao do mes seguinte, inclusive.

- **Information available at:** todo insumo do sinal em `t` usa apenas dados ate `t` inclusive. O beta usado no residuo de `d` usa apenas ate `d-1`.

- **Decision timestamp:** ultimo pregao de cada mes, no fechamento.

- **Universe:** XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY. Fixo, publico e sem alteracao ao longo do periodo.

- **Benchmark:** carteira equal-weight dos 9 ETFs. Controle de sinal: Raw Momentum 12–1.

- **Frequency/horizon:** rebalanceamento mensal, horizonte de um mes.

- **Data sources:** `data/raw/us_sector_etfs_plus_spy_adjusted_close.csv`, precos ajustados, snapshot versionado no repositorio.

- **Research sample:** 2001-02-28 a 2018-10-31, `n = 213` meses. Ja explorado.

- **Contaminated diagnostic period:** 2018-11-30 a 2019-02-28, `n = 4` meses. Metricas agregadas deste trecho foram visualizadas durante uma rodada diagnostica descartada. **Excluido permanentemente do OOS.** Ver secao 10.

- **Final OOS:** 2019-03-29 a 2026-07-31, `n = 89` meses. **Fechado.** Nunca observado sob nenhuma metrica.

- **Primary metric:** Rank IC de Spearman, cross-sectional, media sobre os meses.

- **Secondary metrics:** retorno long-short liquido de custo, Sharpe, max drawdown, turnover, estabilidade por subperiodo.

- **Portfolio:**
  `Long = Top 3 por RSR`, `Short = Bottom 3 por RSR`, peso igual
  `R_LS[t] = media(R[i,t+1] para i em Long) - media(R[i,t+1] para i em Short)`
  `R_net[t] = R_LS[t] - Cost[t]`

- **Costs:** 10 bps por perna, ida e volta, aplicados ao turnover realizado. No research sample o turnover foi de 2,03 nomes de 3 por mes, equivalente a 1,63% a.a.

- **Controls:** Raw Momentum 12–1 e Residual Momentum 12–1 point-in-time, ambos reportados no mesmo painel.

- **Placebos:** permutacao do sinal entre ativos dentro de cada mes, preservando datas e retornos futuros, 5.000 sorteios.

- **Known confounders:** universo pequeno com 9 ativos, o que limita o poder do ranking; custos de execucao nao observados; ausencia de limite de liquidez; sobreposicao setorial entre ETFs.

- **Robustness-only tests:** janela de estimacao de 126 e 504 pregoes; proxy de mercado alternativa igual a media equal-weight dos 9 ETFs; janela de reversao de 10 e 42 pregoes. **Todas reportadas, nenhuma seleciona a especificacao.**

- **Frozen parameters:** `W = 252`, `S = 21`, `Top/Bottom = 3`, rebalanceamento mensal, custo de 10 bps por perna, metrica primaria Rank IC.

## Criterio de decisao, pre-registrado

Avaliado **uma unica vez** no Final OOS, apos aprovacao humana:

- `GO` se `mean IC > 0` **e** `retorno long-short liquido de custo > 0`
- `CONDITIONAL GO` se `mean IC > 0` **e** `retorno liquido <= 0`. Interpretacao: existe informacao no ranking, mas ela nao e economicamente explorável apos custos nesta implementacao.
- `NO-GO` se `mean IC <= 0`

Nenhum parametro sera reajustado apos a abertura. Um resultado `NO-GO` sera reportado como `NO-GO`.

## Evidencia no research sample

Somente para registro. **Nao constitui validacao.**

| construct | mean IC | spread bruto a.a. | Sharpe |
|---|---:|---:|---:|
| Residual Short-Term Reversal | +0,0611 | 5,53% | 0,51 |
| Residual Momentum 12–1 PIT | −0,0011 | 0,10% | 0,01 |
| Raw Momentum 12–1 | +0,0174 | 1,06% | 0,08 |

Spread liquido de custo: **+3,91% a.a.**, vol 10,81%, Sharpe liquido 0,36, meses positivos 54,9%, max drawdown do spread −23,6%.

Permutacao com 5.000 sorteios: `IC observado +0,0611`, `desvio do nulo 0,0240`, `p = 0,0050`, `z = 2,55`.

## Secao 9 — Encerramento do construct anterior

`Residual Momentum 12–1` como especificado ate 14/08/2026 esta encerrado como **NO-GO de construct**.

Motivo: alpha e beta eram estimados por OLS com intercepto na mesma janela usada para formar o sinal. Isso implica `soma de eps em W_t = 0`, e portanto `soma em F_t = - soma em S_t`, com `|F_t| = 231` e `|S_t| = 21`. Verificado numericamente: diferenca maxima de `4,718e-16` e correlacao de `1,0000000000`.

Consequencia: o sinal declarado como momentum de formacao longa era, por identidade algebrica, reversao de curto prazo com sinal invertido. Reconstruido point-in-time, o efeito desaparece: `mean IC = -0,0011`.

Indicio comportamental que apontava na mesma direcao antes da auditoria: o turnover de 2,03 nomes de 3 por mes e incompativel com um sinal de formacao de doze meses.

## Secao 10 — Registro do periodo contaminado

Em 14/08/2026, uma rodada diagnostica intermediaria utilizou split posicional 70/30 sobre um painel encurtado pelo aquecimento do construct point-in-time. A fracao de research alcancou 2019-02-28, ultrapassando a fronteira de 2018-10-31.

Metricas agregadas incluindo 2018-11 a 2019-02 foram visualizadas. A rodada foi descartada e todos os numeros foram recalculados com corte por data explicita, mas o trecho observado nao pode mais ser tratado como OOS puro.

Decisao: `2018-11-30` a `2019-02-28` fica permanentemente fora do Final OOS. O OOS limpo passa a iniciar em `2019-03-29`, com 89 meses.

## Aprovacoes

- **Human approvals:** pendente. Esta specification nao esta aprovada e o Final OOS nao esta autorizado.
- **Git commit:** a registrar no momento do commit de congelamento.

## Autorizacao

Nenhum acesso ao Final OOS esta autorizado por esta specification enquanto o campo de aprovacao humana permanecer pendente.
