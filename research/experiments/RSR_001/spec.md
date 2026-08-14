# RSR_001 — Residual Short-Term Reversal in Sector ETFs

## Identity

- **Experiment ID:** RSR_001
- **Spec version:** v1.0
- **Status:** `READY_FOR_FREEZE`

  O estado so passa a `FROZEN` apos aprovacao humana registrada e commit da
  specification. `READY_FOR_FREEZE` significa que nenhum campo esta `TBD` e que
  o criterio de decisao esta escrito, mas que a specification ainda nao foi
  carimbada temporalmente por um commit.
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

- **Costs:** formula exata, identica a implementada em `scripts/rsr_001.py`.

  Pesos, com `k = 3`:
  `w[i,t] = +1/k` se `i` em `Long_t`; `-1/k` se `i` em `Short_t`; `0` caso contrario.

  Custo:
  `Cost_t = c * soma_i |w[i,t] - w[i,t-1]|`, com `c = 0.0010` e `w[i,-1] = 0`

  Retorno liquido:
  `R_net[t] = R_LS[t] - Cost_t`, onde `R_LS[t] = soma_i w[i,t] * R[i,t+1]`

  No research sample: `soma_i |dw| = 2,751` por mes, equivalente a `3,30% a.a.`
  de custo.

  Nota de correcao: uma versao anterior deste documento estimava o custo apenas
  pelo giro da perna comprada, chegando a `1,63% a.a.`. Aquela conta subestimava
  o custo pela metade. O numero valido e `3,30% a.a.`

- **Controls:** Raw Momentum 12–1 e Residual Momentum 12–1 point-in-time, ambos reportados no mesmo painel.

- **Placebos:** definidos integralmente antes da abertura. Nenhum placebo pode ser adicionado, removido ou alterado apos observar o resultado do OOS.

  `P1 — permutacao cross-sectional.` Embaralha o sinal entre os 9 ativos dentro de cada mes, preservando datas e retornos futuros. 5.000 sorteios, semente 7. Destroi a associacao entre ativo e sinal, preservando a estrutura temporal.

  `P2 — embaralhamento temporal.` Mantem o sinal de cada ativo e embaralha os meses dos retornos futuros. 5.000 sorteios, semente 7. Destroi a associacao temporal, preservando a estrutura cross-sectional.

  `P3 — inversao de sinal.` Avalia `+soma(eps)` no lugar de `-soma(eps)`, isto e, a direcao de momentum residual em vez de reversao. Serve como verificacao de direcionalidade: se o efeito for real, esta variante deve apresentar IC de sinal oposto.

  Criterio: `P1` e `P2` sao considerados nao invalidantes quando o IC observado fica acima do percentil 90 de ambas as distribuicoes nulas, equivalente a `p < 0,10` unilateral em cada uma.

- **Sensibilidade de custo:** `10 bps por perna` e o custo primario e esta congelado. Sensibilidades a `5 bps` e `20 bps` podem ser reportadas como secundarias, e nenhuma delas altera o criterio de decisao.

- **Known confounders:** universo pequeno com 9 ativos, o que limita o poder do ranking; custos de execucao nao observados; ausencia de limite de liquidez; sobreposicao setorial entre ETFs.

- **Robustness-only tests:** janela de estimacao de 126 e 504 pregoes; proxy de mercado alternativa igual a media equal-weight dos 9 ETFs; janela de reversao de 10 e 42 pregoes. **Todas reportadas, nenhuma seleciona a especificacao.**

  Registro explicito sobre `S = 42`: no research sample esta variante entregou `IC = 0,0858` e `spread = 8,14% a.a.`, acima da base. Ela foi identificada **depois** de observar o research sample e por isso permanece classificada como `exploratory robustness / future research`. **Nao sera promovida a primary.** Caso `S = 21` resulte em `NO-GO` no OOS e `S = 42` apresente resultado favoravel, o OOS **nao** sera reinterpretado promovendo `S = 42`. A monotonicidade em `S` fica registrada como questao aberta para trabalho futuro, com a ressalva economica de que em 42 pregoes o fenomeno deixa de ser reversao de curto prazo e exigiria outro mecanismo economico.

- **Frozen parameters:** `W = 252`, `S = 21`, `Top/Bottom = 3`, rebalanceamento mensal, custo de 10 bps por perna, metrica primaria Rank IC.

## Criterio de decisao, pre-registrado

Avaliado **uma unica vez** no Final OOS, apos aprovacao humana e commit.

O criterio separa confirmacao cientifica de utilidade economica. Um retorno
liquido marginalmente positivo, sem confirmacao estatistica, nao caracteriza
`GO`.

### Blocos cronologicos

O OOS de 89 meses e dividido em tres blocos contiguos e de tamanho aproximado,
definidos **por posicao e antes da abertura**:

`B1 = meses 1 a 30` · `B2 = meses 31 a 60` · `B3 = meses 61 a 89`

### ScientificPass

Todas as condicoes abaixo:

1. `mean IC no OOS > 0`
2. `p < 0,10` unilateral no placebo `P1`, permutacao cross-sectional
3. `p < 0,10` unilateral no placebo `P2`, embaralhamento temporal
4. `mean IC > 0` em pelo menos **2 dos 3** blocos cronologicos

### EconomicPass

Ambas as condicoes abaixo:

1. `retorno long-short liquido de custo no OOS > 0`, a `10 bps` por perna
2. `retorno liquido > 0` em pelo menos **2 dos 3** blocos cronologicos

### Veredito

| resultado | condicao | interpretacao |
|---|---|---|
| `GO` | `ScientificPass` e `EconomicPass` | fenomeno replicado e economicamente utilizavel apos custos |
| `CONDITIONAL GO` | `ScientificPass` e nao `EconomicPass` | fenomeno replicado, mas nao convertido em estrategia liquida |
| `NO-GO` | nao `ScientificPass` | previsibilidade residual nao confirmada fora da amostra |

Nenhum parametro, custo, placebo ou limiar sera reajustado apos a abertura. Um
resultado `NO-GO` sera reportado como `NO-GO`.

## Evidencia no research sample

Somente para registro. **Nao constitui validacao.**

| construct | mean IC | spread bruto a.a. | Sharpe |
|---|---:|---:|---:|
| Residual Short-Term Reversal | +0,0611 | 5,53% | 0,51 |
| Residual Momentum 12–1 PIT | −0,0011 | 0,10% | 0,01 |
| Raw Momentum 12–1 | +0,0174 | 1,06% | 0,08 |

Metricas economicas com a formula de custo correta:

| metrica | valor |
|---|---:|
| spread bruto | +5,53% a.a. |
| turnover `soma \|dw\|` | 2,751 por mes |
| custo a 10 bps | 3,30% a.a. |
| **retorno liquido** | **+2,23% a.a.** |
| volatilidade do liquido | 10,81% |
| **Sharpe liquido** | **0,21** |
| meses liquidos positivos | 52,6% |
| max drawdown do liquido | −31,8% |

Placebos, 5.000 sorteios, semente 7, unilaterais:
`p_P1 = 0,0052` · `p_P2 = 0,0094`

Ablacao `A1`: IC residual `+0,0611` contra IC sem residualizar `+0,0274`,
`delta = +0,0337`.

**Leitura honesta.** Apos custos calculados corretamente, o Sharpe cai de 0,21 e
o drawdown chega a −31,8%. A evidencia estatistica de previsibilidade
cross-sectional e razoavel, mas a conversao em estrategia liquida e fraca. O
fenomeno e mais interessante cientificamente do que explorável economicamente
nesta implementacao.

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
