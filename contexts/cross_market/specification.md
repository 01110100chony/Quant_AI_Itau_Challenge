# Cross-Market specification

## Quick Summary

- **Purpose:** Preservar a research question e a specification candidata sem preencher decisões ainda não aprovadas.
- **Read when:** Discutindo ou preparando Cross-Market Information Transmission.
- **Load next:** Leia [`timing.md`](timing.md) para barreira temporal, [`data_contract.md`](data_contract.md) para dados ou [`validation_plan.md`](validation_plan.md) para falsificação.
- **Authority:** Specification candidata `CM_001` em estado `DRAFT`; não autoriza implementação.

## Contents

- [Research question](#research-question)
- [Economic mechanism](#economic-mechanism)
- [Research variables](#research-variables)
- [Scope and samples](#scope-and-samples)
- [Decision criteria](#decision-criteria)
- [Prohibited inference](#prohibited-inference)

## Research question

> Quanto tempo uma informação leva para atravessar mercados economicamente relacionados?

Formulação de trabalho registrada:

```text
Shock_A,t → AbnormalReturn_B,t+1
```

## Economic mechanism

Mercados economicamente relacionados podem incorporar a mesma informação em momentos diferentes devido a sessões e fusos não simultâneos. A existência, direção e duração de transmissão previsível ainda não foram demonstradas.

O vínculo econômico específico entre `A` e `B`: **TBD — requires human decision**.

## Research variables

- **Feature `X_t` / shock:** TBD — requires human decision.
- **Target `Y_{t+h}` / abnormal return:** TBD — requires human decision.
- **Expected direction:** TBD — requires human decision.
- **Benchmark de abnormal return:** TBD — requires human decision.
- **Controles e placebos:** TBD — requires human decision.
- **Métrica primária e secundárias:** TBD — requires human decision.

## Scope and samples

- **Universo mínimo de feasibility:** TBD — requires human decision.
- **Frequência e horizonte:** TBD — requires human decision.
- **Research sample:** TBD — requires human decision.
- **Validation:** TBD — requires human decision.
- **Final OOS:** TBD — requires human decision.

Nenhuma das amostras foi aberta por este artefato.

## Decision criteria

- **GO:** TBD — requires human decision.
- **CONDITIONAL GO:** TBD — requires human decision.
- **NO-GO:** TBD — requires human decision.

## Prohibited inference

Não escolher pares, ativos, thresholds, janelas, benchmarks ou splits observando quais resultados parecem melhores. Não criar o notebook `02_cross_market_feasibility.ipynb` até aprovação humana da specification.
