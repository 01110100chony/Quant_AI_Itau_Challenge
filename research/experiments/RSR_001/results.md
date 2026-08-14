# RSR_001 — Results

## Execution state

Research sample executado. **Final OOS nao aberto.**

O intervalo 2019-03-29 a 2026-07-31, com 89 meses, nunca foi observado sob
nenhuma metrica. O trecho 2018-11-30 a 2019-02-28 esta em quarentena
permanente e nao integra o OOS.

Implementacao canonica: `scripts/rsr_001.py`.

## Research sample — 2001-02-28 a 2018-10-31, n = 213

Estes numeros sao exploratorios e **nao constituem validacao**. A amostra foi
inspecionada durante a formulacao da hipotese.

### Sinal

| metrica | valor |
|---|---:|
| mean IC (Spearman) | +0,0611 |
| hit rate IC > 0 | 54,5% |

### Economia da carteira

`Long = Top 3`, `Short = Bottom 3`, peso igual, rebalanceamento mensal.

| metrica | valor |
|---|---:|
| spread bruto | +5,53% a.a. |
| turnover `soma \|dw\|` | 2,751 por mes |
| custo a 10 bps por perna | 3,30% a.a. |
| **retorno liquido** | **+2,23% a.a.** |
| volatilidade do liquido | 10,81% |
| **Sharpe liquido** | **0,21** |
| meses liquidos positivos | 52,6% |
| max drawdown do liquido | −31,8% |

### Controles

| construct | mean IC | spread bruto a.a. |
|---|---:|---:|
| Residual Short-Term Reversal | +0,0611 | 5,53% |
| Residual Momentum 12–1 PIT | −0,0011 | 0,10% |
| Raw Momentum 12–1 | +0,0174 | 1,06% |

### Placebos pre-registrados

| teste | p unilateral |
|---|---:|
| `P1` permutacao cross-sectional | 0,0052 |
| `P2` permutacao temporal em bloco | 0,0094 |

`N = 5000`, `seed = 7`, `p = (1 + #{nulo >= obs}) / (N + 1)`.

### Ablacao A1 — evidencia secundaria, fora do criterio

| sinal | mean IC |
|---|---:|
| reversao residual | +0,0611 |
| reversao sem residualizar | +0,0274 |
| `delta IC (A1)` | **+0,0337** |

Residualizar mais que dobra o IC.

### Robustez — todas reportadas, nenhuma seleciona a specification

| variante | mean IC | spread bruto a.a. |
|---|---:|---:|
| `W=252, S=21` primary | 0,0611 | 5,53% |
| `W=126` | 0,0337 | 5,40% |
| `W=504` | 0,0378 | 3,51% |
| `S=10` | 0,0400 | 3,76% |
| `S=42` exploratory-only | 0,0858 | 8,14% |

`S=42` nao sera promovido a primary sob nenhuma circunstancia, nem usado para
reinterpretar o OOS.

## Fragilidades identificadas

O beneficio nao e estavel entre subperiodos. Nos tres blocos cronologicos do
research sample o IC medio foi `+0,0824`, `−0,0012` e `+0,1021`. O bloco
central e praticamente nulo.

O retorno liquido de `+2,23% a.a.` com volatilidade de `10,81%` deixa o
resultado economico proximo do limiar. Uma execucao pior que `10 bps` por perna
zeraria o `EconomicPass`.

O universo de 9 ativos limita o poder estatistico do ranking.

## Final OOS

Nao executado. Resultado indisponivel ate a abertura autorizada.
