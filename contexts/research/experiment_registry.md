# Experiment registry

## Quick Summary

- **Purpose:** Localizar experimentos, versões, amostras inspecionadas, estado do OOS e decisão.
- **Read when:** Antes de criar ID, executar amostra ou interpretar resultado existente.
- **Load next:** Abra o artefato indicado ou o Research Log para registros legados.
- **Authority:** Índice canônico de identidade/estado; resultados detalhados pertencem ao artefato e ao Research Log.

## Contents

- [Allowed statuses](#allowed-statuses)
- [Registry](#registry)
- [Legacy artifact policy](#legacy-artifact-policy)

## Allowed statuses

`DRAFT`, `RESEARCH`, `NO_GO`, `CONDITIONAL_GO`, `FROZEN`, `VALIDATION`, `VALIDATED`, `OOS_OPENED`, `FINAL`.

O status descreve estágio, não qualidade econômica. `VALIDATED` não significa OOS final aprovado.

## Registry

| ID | Thesis | Spec version | Status | Sample inspected | OOS status | Decision | Commit / artifact |
|---|---|---|---|---|---|---|---|
| ER_001 | Effective Rank sanity check | v0.1 | NO_GO | Research sample legado | CLOSED | Sanity check estrutural; ER não promovido | [`notebook`](../../notebooks/01_er_feasibility_v0_1.ipynb) |
| ER_002 | ER versus medidas simples | v0.2 | NO_GO | Research sample legado | CLOSED | ER redundante como protagonista | [`notebook`](../../notebooks/01_er_feasibility_v0_2.ipynb) |
| ER_003 | ER residualizado | v0.3 | NO_GO | Research sample legado | CLOSED | Residualização muda estrutura, mas ER segue redundante | [`notebook`](../../notebooks/01_er_feasibility_v0_3.ipynb) |
| OS_001 | Opportunity Set → Residual Momentum | v0.4 | NO_GO | 2001–2018 research | CLOSED | Hipótese falsificada no research sample | [`notebook`](../../notebooks/01_er_feasibility_v0_4.ipynb) |
| AFN_001 | Adaptive Factor Neutralization | v0.5.1 | NO_GO | 2001–2018 research | CLOSED | Hipótese falsificada no research sample | [`notebook corrigido`](../../notebooks/01_er_feasibility_v0_5_1.ipynb) |
| CM_001 | Cross-Market Information Transmission | v1.0.1-frozen | NO_GO | 2010–2018 Research Stage B once | CLOSED | CorePass false; frozen verdict NO_GO; holdouts not opened | [`results`](../../research/experiments/CM_001/results.md) |
| LAF_001 | Liquidity Absorption Fragility | v0.1-draft | DRAFT | Stage A1/A1c structural 2003–2016 | CLOSED | A1c remedia fronteira/proveniência; Volume semântico unresolved; Stage A2 NO | [`results`](../../research/experiments/LAF_001/results.md) |

## Legacy artifact policy

Os experimentos anteriores ao harness permanecem auditáveis pelo Research Log e notebooks originais. Seus commits originais não foram registrados; não serão reconstruídos retroativamente. Artefatos autocontidos completos são obrigatórios a partir de `CM_001` e devem ser criados antes da execução relevante.
