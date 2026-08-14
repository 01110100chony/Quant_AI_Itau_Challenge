# Hypothesis template

## Quick Summary

- **Purpose:** Fornecer o contrato mínimo e reutilizável para uma nova hipótese.
- **Read when:** Criando ou versionando uma specification antes de código.
- **Load next:** Registre o ID no [`experiment registry`](experiment_registry.md) e siga o [`protocol`](protocol.md).
- **Authority:** Template canônico; valores metodológicos preenchidos exigem aprovação humana quando materiais.

## Contents

- [Template](#template)
- [Completion rules](#completion-rules)

## Template

```markdown
# <Experiment ID> — <Title>

- Experiment ID:
- Spec version:
- Status:
- Created at:
- Research question:
- Economic mechanism:
- Null hypothesis:
- Alternative hypothesis:
- Expected direction:
- Feature X_t:
- Target Y_t+h:
- Information available at:
- Decision timestamp:
- Universe:
- Benchmark:
- Frequency/horizon:
- Data sources:
- Research sample:
- Validation sample:
- Final OOS:
- Primary metric:
- Secondary metrics:
- Controls:
- Placebos:
- Known confounders:
- Robustness-only tests:
- GO criteria:
- CONDITIONAL GO criteria:
- NO-GO criteria:
- Frozen parameters:
- Changes since previous specification:
- Human approvals:
- Git commit:
```

## Completion rules

- Use timestamps e timezones explícitos; “mesmo dia” não é contrato temporal.
- Escreva `TBD — requires human decision` em vez de inferir valor ausente.
- Separe métrica decisória de diagnóstico/robustness.
- Registre mudanças depois de qualquer resultado observado; não sobrescreva a specification anterior.
- Não marque `FROZEN` sem versão e commit reproduzível.
