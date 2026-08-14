# Cross-Market validation plan

## Quick Summary

- **Purpose:** Separar feasibility, falsification, validation e OOS antes de qualquer execução.
- **Read when:** Definindo critérios de decisão, controles, placebos ou plano de amostras.
- **Load next:** Consulte a [`OOS policy`](../research/oos_policy.md) antes de definir ou acessar qualquer holdout.
- **Authority:** Plano candidato; critérios e splits concretos exigem decisão humana.

## Contents

- [Feasibility](#feasibility)
- [Falsification](#falsification)
- [Decision gates](#decision-gates)
- [Validation and final OOS](#validation-and-final-oos)

## Feasibility

O feasibility mínimo deverá testar somente se uma transmissão temporal entre mercados economicamente relacionados é mensurável sob alinhamento point-in-time correto. Não inclui ML complexo, estratégia final, múltiplos thresholds, busca entre dezenas de pares ou portfolio construction.

## Falsification

Antes de implementação, ainda precisam ser aprovados:

- controle simples/contemporâneo;
- placebos de timing ou mapeamento;
- tratamento de autocorrelação e overlapping targets, se aplicável;
- subperíodos diagnósticos previamente definidos;
- sanity checks manuais de sessões e feriados;
- métrica primária distinta de robustness.

Todos: **TBD — requires human decision**.

## Decision gates

Critérios quantitativos GO, CONDITIONAL GO e NO-GO: **TBD — requires human decision**.

Um gráfico atraente, retorno alto ou significância em métrica não pré-especificada não substitui o gate aprovado.

## Validation and final OOS

Research sample, validation e final OOS: **TBD — requires human decision**. Validation somente após primeiro freeze; final OOS somente após validation, decisão e segundo freeze. Nenhuma dessas amostras foi aberta nesta tarefa.
