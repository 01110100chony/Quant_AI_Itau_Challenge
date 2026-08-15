# RSR_001 — Results

## Execution state

Research sample executado. **Final OOS aberto uma unica vez em 14/08/2026.**
Veredito `NO-GO`. O trecho 2018-11-30 a 2019-02-28 permanece em quarentena
permanente e nao integrou o OOS.

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

## Final OOS — 2019-03-29 a 2026-07-31, n = 89

Aberto uma unica vez, em 14/08/2026, apos os commits `H1` e `H2`, com arvore
limpa e confirmacao digitada `ABRIR OOS`.

> **Proveniencia.** Os numeros abaixo sao **transcritos da saida de terminal
> observada durante a execucao**, e nao lidos de um artefato de maquina. A
> execucao levantou `KeyError: "['long'] not found in axis"` em
> `scripts/rsr_001.py:310`, depois de imprimir todas as metricas e o veredito,
> e antes de gravar `rsr_001_oos_bruto.csv` e `rsr_001_veredito.csv`. Os dois
> CSVs **nao existem**. O arquivo `reports/rsr_001_oos_terminal.txt`, apontado
> em 14/08 como registro preservado, esta **vazio**.
>
> Nao houve reexecucao: a regra pre-registrada proibe reabrir o holdout, e a
> decisao registrada foi a Opcao B, transcrever. A consistencia mutua dos
> numeros foi verificada por vinte identidades algebricas em `reauditoria.md`,
> secao 1, todas satisfeitas. Isso sustenta a fidelidade da transcricao; nao
> substitui o artefato perdido.

### Sinal

| metrica | valor |
|---|---:|
| mean IC (Spearman) | **-0,0476** |
| hit rate IC > 0 | 49,4% |
| IC bloco `B1` (meses 1..30) | -0,0233 |
| IC bloco `B2` (meses 31..60) | -0,0422 |
| IC bloco `B3` (meses 61..89) | -0,0782 |

### Economia da carteira

| metrica | valor |
|---|---:|
| spread bruto | -5,51% a.a. |
| turnover `soma \|dw\|` | 2,494 por mes |
| custo a 10 bps | 2,99% a.a. |
| **retorno liquido** | **-8,50% a.a.** |
| volatilidade do liquido | 12,97% |
| **Sharpe liquido** | **-0,66** |
| meses liquidos positivos | 46,1% |
| max drawdown do liquido | -75,5% |
| liquido `B1` / `B2` / `B3` | -7,68% / +1,27% / -19,46% a.a. |

### Placebos pre-registrados

| teste | p unilateral |
|---|---:|
| `P1` permutacao cross-sectional | 0,8980 |
| `P2` permutacao temporal em bloco | 0,8530 |

### Criterio pre-registrado

```
mean IC > 0                 -0,0476        FALHA
p_P1 < 0,10                  0,8980        FALHA
p_P2 < 0,10                  0,8530        FALHA
IC > 0 em >= 2 de 3 blocos    0 de 3       FALHA
                                           ScientificPass = False

R_net > 0                    -8,50% a.a.   FALHA
R_net > 0 em >= 2 de 3        1 de 3       FALHA
                                           EconomicPass = False

VEREDITO -> NO-GO
```

Seis condicoes, seis falhas. Nenhuma proxima da fronteira.

### Contraste research versus OOS

| | research | OOS |
|---|---:|---:|
| mean IC | +0,0611 | -0,0476 |
| `p_P1` | 0,0052 | 0,8980 |
| retorno liquido | +2,23% a.a. | -8,50% a.a. |

O `p` de permutacao vai de 0,005 a 0,898 e os tres blocos do OOS pioram
monotonicamente. A leitura registrada e que o achado do research sample era
ruido amostral, e nao um efeito que enfraqueceu com o tempo.

### Proibicoes pos-OOS, em vigor

`S = 42`, outra janela de estimacao, outro nivel ou formula de custo, outro
universo, outro horizonte, outro criterio de decisao e reinterpretacao da
direcao do sinal. Nenhum foi invocado. O `NO-GO` e definitivo.
