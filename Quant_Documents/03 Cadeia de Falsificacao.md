---
tags: [tese, falsificacao, nucleo]
atualizado: 2026-08-14
---

# Cadeia de Falsificação

Volta para [[00 MOC - Desafio Quant AI 2026]].

Esta é a espinha dorsal do relatório. Cinco hipóteses entraram, nenhuma sobreviveu, e cada uma foi encerrada por um número específico.

> [!important] Regra de ouro
> Cada hipótese morta precisa aparecer **com o número que a matou**. Sem os números vira narrativa bonita, e o manual de avaliação penaliza exatamente isso. Com os números, vira evidência de método.

## Degrau 1 — Effective Rank

**Pergunta:** quantas forças independentes movem o mercado?

**Métrica:** `ER = (soma dos autovalores)² / soma dos autovalores ao quadrado`, sobre a matriz de correlação.

**Como morreu:** por álgebra, não por dados. Para uma matriz de correlação com `N` ativos vale `soma(λ) = N` e `soma(λ²) = N + 2·soma_{i<j}(ρ²)`, logo:

```
ER = N / (1 + (N−1)·ρ̄²)
```

onde `ρ̄²` é a média das correlações ao quadrado. Ou seja, para `N` fixo o Effective Rank é uma transformação monotônica da correlação quadrática agregada. Não é representação independente de nada.

**Número:** `Spearman(ER, MarketMode) ≈ −0,9995` e `Spearman(ER, MeanCorr) ≈ −0,995`.

**Veredito:** `DESCARTADA`. Registry: `ER_001`, `ER_002`, `ER_003`.

## Degrau 2 — Opportunity Set

**Pergunta:** quando os ativos se movem de forma mais independente, abre mais espaço para alpha cross-sectional?

**Variável:** `D_t` = Residual RMS Correlation, a raiz da média das correlações residuais ao quadrado.

**Número:** `Spearman(Opportunity, IC) ≈ −0,044` e `Spearman(Opportunity, Spread) ≈ −0,087`. Praticamente zero, e com o sinal invertido. Os quintis não mostraram progressão monotônica.

**Veredito:** `FALSIFICADA`. Registry: `OS_001`.

## Degrau 3 — Adaptive Factor Neutralization

**Pergunta:** quanto maior a parcela dos movimentos explicada pelo fator de mercado, maior deveria ser o benefício de neutralizar esse fator antes de calcular momentum.

**Variável:** `Commonality_t` = média do `R²` das regressões contra o mercado.

**Número:** `Spearman(Commonality, ΔIC) ≈ −0,059`. Nos quintis, o de maior dominância entregou `ΔIC = −0,061`, **contrário à hipótese**.

Havia a tentação de postular um "sweet spot intermediário" olhando o gráfico. Foi explicitamente recusada como *specification search*, e isso está registrado no `Research_Log`.

**Veredito:** `FALSIFICADA`. Registry: `AFN_001`.

## Degrau 4 — o construct do Residual Momentum

Este é o mais forte da cadeia, porque atinge o próprio achado positivo do grupo.

**O que se acreditava ter:** `RMOM_{i,t} = soma de ε de t−252 até t−21`, momentum residual de doze meses pulando o mês recente, com `mean IC = 0,0496` contra `0,0003` do momentum bruto.

**Como morreu:** OLS com intercepto força os resíduos a somarem zero na janela de estimação. Como a janela de estimação era **a mesma** da formação:

```
soma de ε em W_t = 0        com |W_t| = 252
logo
soma em F_t = − soma em S_t   com |F_t| = 231 e |S_t| = 21
```

O sinal chamado de momentum de doze meses era, por identidade, **o negativo dos resíduos do mês excluído**. Reversão de curto prazo com o nome trocado.

**Verificação numérica:**

| teste | resultado |
|---|---|
| `max \| soma dos 252 resíduos \|` | `4,337e-16` |
| `max \| RMOM − (−soma dos últimos 21) \|` | `4,718e-16` |
| correlação entre os dois | `1,0000000000` |
| escala típica do sinal | `0,0226` |

O resíduo da identidade está catorze ordens de grandeza abaixo da escala do sinal.

**Reconstruído point-in-time**, com beta de `[d−252, d−1]` aplicado em `d`, o efeito desaparece: `mean IC = −0,0011`, spread `0,10% a.a.`

**Indício comportamental que já apontava para isso e ninguém viu:** o turnover era de 2 dos 3 nomes por mês. Um sinal de formação de doze meses não faz isso.

**Veredito:** `NO-GO de construct`. Registry: `RM_001`.

## Degrau 5 — Residual Short-Term Reversal

A hipótese que sobreviveu à correção do construct e foi levada ao holdout.

Ver [[04 RSR_001 - Spec e Veredito do OOS]] para a especificação completa.

**Research sample:** `mean IC +0,0611`, `p = 0,0052` na permutação, retorno líquido `+2,23% a.a.`

**Final OOS:** `mean IC −0,0476`, `p = 0,8980`, retorno líquido `−8,50% a.a.`

**Veredito:** `NO-GO` fora da amostra. Registry: `RSR_001`.

## Resumo para a página 2 do relatório

| hipótese | o que perguntamos | o número que encerrou | veredito |
|---|---|---|---|
| Effective Rank | quantas forças independentes movem o mercado? | `ER = N/(1+(N−1)ρ̄²)`, Spearman `−0,9995` | descartada |
| Opportunity Set | independência abre espaço para alpha? | `−0,044`, sinal invertido | falsificada |
| Adaptive Neutralization | dominância torna neutralizar mais útil? | `−0,059`, Q5 contrário | falsificada |
| Construct do sinal | o momentum residual é o que dizemos que é? | identidade a `4,7e-16` | refutado |
| Residual Reversal | a reversão residual sobrevive fora da amostra? | `IC −0,0476`, `p = 0,898` | NO-GO |

Cinco degraus, dois derrubados por álgebra e três por dados.
