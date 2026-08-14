# Context Map

## Quick Summary

- **Purpose:** Entrada única para carregar apenas o contexto necessário a uma tarefa de research.
- **Read when:** Após as fontes de verdade da raiz, no início de qualquer tarefa não trivial.
- **Load next:** Escolha uma única rota na tabela; siga outra referência apenas se a página escolhida exigir.
- **Authority:** Índice de navegação. Não substitui as fontes canônicas que referencia.

## Contents

- [Authority hierarchy](#authority-hierarchy)
- [Where to start](#where-to-start)
- [Directory map](#directory-map)

## Authority hierarchy

1. Instrução humana explícita mais recente.
2. [`AGENTS.md`](../AGENTS.md): regras permanentes do agente.
3. [`PROJECT_STATUS.md`](../PROJECT_STATUS.md): estado científico atual.
4. [`research/current_thesis.md`](research/current_thesis.md): specification promovida, quando existir.
5. [`research/oos_policy.md`](research/oos_policy.md): governança de validation, holdout e OOS.
6. [`Research_Log_Desafio_Quant_AI_2026.md`](../Research_Log_Desafio_Quant_AI_2026.md): histórico completo e decisões anteriores.
7. [`research/experiment_registry.md`](research/experiment_registry.md) e `research/experiments/`: identidade e artefatos de experimentos.
8. [`TASKS.md`](../TASKS.md): fila operacional.

Conflitos não são resolvidos por inferência. Reporte-os e peça decisão humana.

## Where to start

| Quero… | Abrir |
|---|---|
| Entender restrições permanentes do desafio | [`challenge/constraints.md`](challenge/constraints.md) |
| Entender critérios de avaliação conhecidos | [`challenge/evaluation.md`](challenge/evaluation.md) |
| Criar ou conduzir uma tese | [`research/protocol.md`](research/protocol.md) |
| Ver a tese/candidata atual | [`research/current_thesis.md`](research/current_thesis.md) |
| Evitar ressuscitar linha encerrada | [`research/rejected_hypotheses.md`](research/rejected_hypotheses.md) |
| Definir ou abrir validation/OOS | [`research/oos_policy.md`](research/oos_policy.md) |
| Registrar ou localizar experimento | [`research/experiment_registry.md`](research/experiment_registry.md) |
| Escrever uma nova specification | [`research/hypothesis_template.md`](research/hypothesis_template.md) |
| Trabalhar na futura linha Cross-Market | [`cross_market/specification.md`](cross_market/specification.md) |

## Directory map

```text
contexts/
├── CONTEXT_MAP.md
├── challenge/       # restrições e leitura da avaliação
├── research/        # protocolo, estado, OOS e experimentos
└── cross_market/    # specification candidata separada por responsabilidade
```
