---
tags: [rsr001, spec, oos, resultado]
atualizado: 2026-08-15
veredito: NO-GO
status: FINAL
---

# RSR_001 — Especificação e Veredito do OOS

Volta para [[00 MOC - Desafio Quant AI 2026]]. Contexto em [[03 Cadeia de Falsificacao]].

Artefatos canônicos no repo: `research/experiments/RSR_001/{spec,decision,results}.md` e `manifest.toml`. Implementação: `scripts/rsr_001.py`.

## A tese

**Pergunta:** choques idiossincráticos de curto prazo, depois de removido o componente comum de mercado, apresentam sobrerreação e reversão parcial no período seguinte entre ETFs setoriais?

**Mecanismo econômico:** o fator comum é observado simultaneamente por todos e é precificado rápido. Choques residuais de curto prazo carregam pressão de liquidez, desequilíbrio de posicionamento e sobrerreação, e revertem parcialmente. A aposta é em provisão de liquidez no espaço idiossincrático, não em difusão lenta de informação.

## Especificação congelada

```
W_d = {d−252, ..., d−1}     |W_d| = 252    janela de estimação, anterior a d
S_t = {t−20,  ..., t}       |S_t| = 21     janela de reversão

α̂, β̂ = OLS(r_i, r_m) sobre W_d          point-in-time
ε_{i,d} = r_{i,d} − α̂_{i,d−1} − β̂_{i,d−1}·r_{m,d}
RSR_{i,t} = − soma de ε_{i,τ} para τ em S_t
```

| item | valor |
|---|---|
| universo | XLB XLE XLF XLI XLK XLP XLU XLV XLY |
| proxy de mercado | SPY |
| retornos | log, diários |
| carteira | Long Top 3, Short Bottom 3, peso igual |
| pesos | `+1/3`, `−1/3`, `0` |
| rebalanceamento | mensal, último pregão |
| custo | `Cost_t = c · soma_i \|w_it − w_i,t−1\|`, `c = 0,0010` |
| métrica primária | Rank IC de Spearman |
| métrica secundária | retorno long-short líquido |

### Fronteiras temporais

| período | intervalo | n |
|---|---|---|
| research | 2001-02-28 a 2018-10-31 | 213 |
| **quarentena** | 2018-11-30 a 2019-02-28 | 4 |
| final OOS | 2019-03-29 a 2026-07-31 | 89 |

A quarentena existe porque métricas agregadas desse trecho foram visualizadas numa rodada diagnóstica descartada. Uma vez observado, deixa de ser holdout puro.

### Placebos e ablação

- **P1** permutação cross-sectional: embaralha os labels do sinal entre os 9 ativos dentro de cada mês.
- **P2** permutação temporal em bloco: reordena os meses do vetor cross-sectional completo, mantendo cada vetor intacto.
- **A1** ablação de residualização: compara com a mesma reversão sobre o retorno bruto. **Não é placebo e não entra no critério.**

`N = 5000`, `seed = 7`, unilaterais, `p = (1 + #{nulo ≥ obs}) / (N + 1)`.

### Critério, pré-registrado antes da abertura

```
Blocos do OOS:  B1 = meses 1..30   B2 = 31..60   B3 = 61..89

ScientificPass = (mean IC > 0) ∧ (p_P1 < 0,10) ∧ (p_P2 < 0,10)
                 ∧ (#{b: IC_b > 0} ≥ 2)

EconomicPass   = (R_net > 0) ∧ (#{b: R_net_b > 0} ≥ 2)

GO              = Scientific ∧ Economic
CONDITIONAL GO  = Scientific ∧ ¬Economic
NO-GO           = ¬Scientific
```

## Resultados

### Research sample (213 meses) — exploratório, não é validação

| métrica | valor |
|---|---:|
| mean IC | +0,0611 |
| hit rate IC > 0 | 54,5% |
| spread bruto | +5,53% a.a. |
| turnover `sum\|dw\|` | 2,751 |
| custo | 3,30% a.a. |
| **retorno líquido** | **+2,23% a.a.** |
| volatilidade | 10,81% |
| Sharpe líquido | 0,21 |
| max drawdown | −31,8% |
| `p_P1` | 0,0052 |
| `p_P2` | 0,0094 |
| `A1` delta IC | +0,0337 |

Blocos de IC: `+0,0824`, `−0,0012`, `+0,1021`.

Robustez, todas reportadas e nenhuma seleciona a spec:

| variante | mean IC | spread a.a. |
|---|---:|---:|
| `W=252, S=21` primary | 0,0611 | 5,53% |
| `W=126` | 0,0337 | 5,40% |
| `W=504` | 0,0378 | 3,51% |
| `S=10` | 0,0400 | 3,76% |
| `S=42` exploratory-only | 0,0858 | 8,14% |

### Final OOS (89 meses) — aberto uma vez em 14/08

| métrica | valor | condição |
|---|---:|---|
| mean IC | **−0,0476** | falha |
| hit rate IC > 0 | 49,4% | |
| `p_P1` | 0,8980 | falha |
| `p_P2` | 0,8530 | falha |
| IC `B1` / `B2` / `B3` | −0,0233 / −0,0422 / −0,0782 | 0 de 3, falha |
| spread bruto | −5,51% a.a. | |
| turnover | 2,494 | |
| custo | 2,99% a.a. | |
| **retorno líquido** | **−8,50% a.a.** | falha |
| volatilidade | 12,97% | |
| Sharpe líquido | −0,66 | |
| max drawdown | −75,5% | |
| líquido `B1` / `B2` / `B3` | −7,68% / +1,27% / −19,46% | 1 de 3, falha |

```
ScientificPass = False
EconomicPass   = False
VERDICT        = NO-GO
```

## O contraste, que é o ponto do relatório

| | research | OOS |
|---|---:|---:|
| mean IC | +0,0611 | −0,0476 |
| `p` da permutação | 0,0052 | 0,8980 |
| retorno líquido | +2,23% a.a. | −8,50% a.a. |

Um `p = 0,005` que vira `p = 0,898`. Os três blocos do OOS são monotonicamente piores. Não é um efeito que enfraqueceu com o tempo: é um efeito que nunca existiu, e o research sample estava medindo ruído.

## Reauditoria de 15/08 — o que os números aguentam

Reauditoria estática, sem reexecução. Registro completo em `research/experiments/RSR_001/reauditoria.md`.

> [!warning] Não existe artefato de máquina do Final OOS
> Os dois CSVs não foram gravados por causa do crash de persistência, e `reports/rsr_001_oos_terminal.txt` — apontado em 14/08 como registro preservado — **está vazio, 1 byte**. A única fonte dos números é prosa.

O que foi possível verificar sem tocar no holdout: **20 identidades aritméticas, todas satisfeitas.**

| identidade | research | OOS |
|---|:---:|:---:|
| `custo = c · turnover · 12` | OK | OK |
| `líquido = bruto − custo` | OK | OK |
| `Sharpe = líquido / volatilidade` | OK | OK |
| média ponderada dos blocos reproduz o `mean IC` | OK | OK |
| `hit rate` cai em `k/n` com `k` inteiro | OK | OK |
| `meses líquidos positivos` cai em `k/n` inteiro | OK | OK |
| `p` cai na grade `(1+k)/(N+1)`, `N = 5000` | OK | OK |

Os cortes por bloco batem: `np.array_split` de 89 dá `30/30/29`, e `(30·(−0,0233) + 30·(−0,0422) + 29·(−0,0782))/89 = −0,0476`. Os líquidos por bloco dão `−8,50%`. Os quatro p-valores caem sobre a grade: `26/5001`, `47/5001`, `4491/5001`, `4266/5001`.

Conformidade `spec.md` ↔ `scripts/rsr_001.py` conferida linha a linha: janelas, off-by-one, pesos, fórmula de custo, alinhamento do retorno futuro, cortes de bloco, `N`/`seed`/unilateralidade, quarentena e `A1` fora do gate. **Sem divergência material.**

Isso não prova que a execução ocorreu. Sustenta que a transcrição é fiel: uma transcrição errada ou inventada teria altíssima chance de falhar pelo menos uma das 20.

## Proibições pós-OOS

Registradas na specification e válidas a partir da abertura. Nada disso pode ser usado para resgatar o `NO-GO`:

- `S = 42`, mesmo tendo IC `0,0858` no research
- outra janela de estimação
- outro nível ou fórmula de custo
- outro universo, benchmark ou horizonte
- outro critério de decisão
- reinterpretação do sinal ou da direção da estratégia
