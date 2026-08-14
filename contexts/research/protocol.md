# Research protocol

## Quick Summary

- **Purpose:** Definir o processo obrigatório, falsification-first, para qualquer nova tese.
- **Read when:** Antes de escrever specification, código, notebook, validation, OOS ou backtest.
- **Load next:** Use [`hypothesis_template.md`](hypothesis_template.md) para especificar e [`oos_policy.md`](oos_policy.md) antes de qualquer holdout.
- **Authority:** Contrato canônico do processo de research; decisões metodológicas concretas permanecem humanas.

## Contents

- [Research lifecycle](#research-lifecycle)
- [Specification contract](#specification-contract)
- [Feasibility and falsification](#feasibility-and-falsification)
- [Freeze validation and OOS](#freeze-validation-and-oos)
- [Material changes](#material-changes)
- [Semantic and mechanical guarantees](#semantic-and-mechanical-guarantees)

## Research lifecycle

```text
Idea
  → Economic mechanism
  → Research specification
  → Feasibility
  → Falsification
  → Research result
  → GO / CONDITIONAL GO / NO-GO
  → Freeze
  → Validation
  → Freeze novamente
  → Final OOS
  → Backtest / portfolio somente depois
```

O objetivo não é salvar uma tese, mas tentar destruí-la com o menor experimento informativo possível.

## Specification contract

Antes de código, toda tese deve responder:

- Qual é o fenômeno e por que economicamente deveria existir?
- Qual é `X_t` e qual é `Y_{t+h}`?
- Quando exatamente `X_t` está disponível e quando uma decisão pode ser tomada?
- Qual é o universo, benchmark, horizonte e frequência?
- Quais são controles e confounders conhecidos?
- Quais são hipótese nula, alternativa e direção esperada?
- Qual é a métrica primária? Quais são secundárias? Quais testes são apenas robustness?
- Quais são research sample, validation e final OOS?
- Que resultado causa GO, CONDITIONAL GO e NO-GO?
- O que não poderá ser modificado depois de observar resultados?

Registre a resposta com o [`hypothesis template`](hypothesis_template.md) e atribua um Experiment ID antes da implementação.

## Feasibility and falsification

Feasibility implementa somente o mínimo para verificar se o fenômeno é mensurável. Falsification procura leakage, explicações simples concorrentes, instabilidade temporal, placebos e falhas de alinhamento. Controles, subperíodos e métricas alternativas devem ser justificados antes de seu uso como decisão; análises pós-hoc são rotuladas como exploratórias e não mudam o critério original.

## Freeze validation and OOS

GO ou CONDITIONAL GO no research sample não autoriza automaticamente validation. Primeiro congele specification, parâmetros e commit. Depois da validation, registre a decisão e congele novamente antes do final OOS. O final OOS é executado uma vez; resultado negativo não autoriza busca de parâmetros. Consulte a [`política de OOS`](oos_policy.md).

Backtest de portfolio, custos e execução só ocorre depois que a tese sobrevive ao processo anterior.

## Material changes

Mudanças em tese, mecanismo, universo, benchmark, horizonte, frequência, lookback, sinal, target, split, OOS, custo, portfolio ou critério de sucesso exigem aprovação humana anterior à implementação. Registre versionamento, motivo, evidência já observada e aprovação no artefato do experimento.

## Semantic and mechanical guarantees

Regras como “não use informação futura” e “não faça specification mining” exigem política e julgamento; ficam neste protocolo e em `AGENTS.md`. Invariantes observáveis, como `feature_timestamp < decision_timestamp`, splits não sobrepostos ou IDs únicos, pertencem a testes ou ao verificador. Hooks não devem tentar decidir semântica científica.
