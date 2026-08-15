---
tags: [governanca, hashes, genai]
atualizado: 2026-08-14
---

# Governança, Hashes e Uso de IA

Volta para [[00 MOC - Desafio Quant AI 2026]].

## Hashes do freeze

```
H1  66bd72831eb803beeeefe63686ef915385f00b0c
    scientific freeze. 13 aprovações humanas em decision.md.
    Fri Aug 14 21:00:44 2026 -0300

H2  a45b3a4
    metadata. status = "FROZEN", git_commit aponta para H1.
    Também atualizou o registry de RESEARCH para FROZEN.
```

O `H1` é o carimbo temporal que dá validade ao holdout. Tudo que estava na árvore no momento do `H1` é a especificação congelada.

## Fluxo de estados do harness

```
DRAFT -> RESEARCH -> FROZEN -> OOS_OPENED -> FINAL
                        ^          ^
                        H1+H2      abertura única
```

Vocabulário permitido, definido em `contexts/research/experiment_registry.md` e validado por `verify_research.py`:

`DRAFT`, `RESEARCH`, `NO_GO`, `CONDITIONAL_GO`, `FROZEN`, `VALIDATION`, `VALIDATED`, `OOS_OPENED`, `FINAL`.

> [!warning] `READY_FOR_FREEZE` não existe
> Foi sugerido num parecer, mas não pertence ao enum. Usa-se `RESEARCH` como estado pré-freeze, com a equivalência documentada.

## Regras que o verificador impõe

- status do manifesto deve **bater com o registry**
- status `FROZEN` ou superior exige `git_commit` com hash válido de 7 a 40 hex
- `oos_opened = true` exige status `OOS_OPENED` ou `FINAL`, mais `oos_opened_at` com fuso e `oos_approval_ref`
- `oos_opened = false` **proíbe** ter metadados de abertura
- `created_at` exige offset de fuso
- todo experimento precisa de `spec.md`, `manifest.toml`, `results.md` e `decision.md`

## Registry — 8 entradas

| ID | tese | status |
|---|---|---|
| `ER_001` | Effective Rank sanity check | NO_GO |
| `ER_002` | ER versus medidas simples | NO_GO |
| `ER_003` | ER residualizado | NO_GO |
| `OS_001` | Opportunity Set → Residual Momentum | NO_GO |
| `AFN_001` | Adaptive Factor Neutralization | NO_GO |
| `RM_001` | Residual Momentum, construct in-sample | NO_GO |
| `CM_001` | Cross-Market Information Transmission | DRAFT |
| `RSR_001` | Residual Short-Term Reversal | FROZEN → a atualizar para OOS_OPENED |

## Pendente após a abertura do OOS

O manifesto e o registry ainda **não** refletem que o OOS foi aberto. Falta:

```toml
status = "OOS_OPENED"
oos_opened = true
oos_opened_at = "2026-08-14T21:XX:XX-03:00"
oos_approval_ref = "66bd72831eb803beeeefe63686ef915385f00b0c"
```

E no registry, `oos_status` de `CLOSED` para `OPENED` e status para `OOS_OPENED`.

Isso depende da decisão sobre o bug de persistência. Ver [[01 Estado Atual e Proximos Passos]].

---

# Uso de IA generativa

Vale 15% da nota. O manual penaliza uso *"superficial ou meramente declaratório"* e avalia explicitamente as **limitações encontradas**.

## Como a IA foi usada, com impacto concreto

| etapa | o que foi pedido | impacto |
|---|---|---|
| Estruturação do repositório | reorganizar como research harness | `contexts/`, política de OOS, registry, `verify_research.py`, testes. Feito com Codex / GPT-5 |
| Auditoria algébrica | existe redundância entre Effective Rank e correlação? | **derrubou a tese principal**: `ER = N/(1+(N−1)ρ̄²)` |
| Auditoria de construct | o sinal 12−1 mede o que dizemos? | **derrubou o achado positivo**: identidade de OLS a `4,7e-16` |
| Auditoria de viés | revisar leitura dos quintis | apontou que postular um "sweet spot" após ver o gráfico seria specification search |
| Reimplementação independente | reconstruir o sinal só a partir da spec | reproduziu painel de 307 meses e research de 214 |
| Desenho de testes | placebos e critério de decisão | `P1`, `P2`, `A1`, `ScientificPass` e `EconomicPass` |
| Auditoria de custo | a fórmula está correta? | **corrigiu subestimação pela metade**, de 1,63% para 3,30% a.a. |
| Gates pré-freeze | conferir antes do carimbo | 5 erros de conformidade, 1 divergência spec-código, 1 timestamp inventado, 1 caixa não marcada |

## A linha `ONDE FALHOU` — obrigatória no relatório

Texto sugerido, verificável nas seções 4.1 e 7 do `Research_Log`:

> A IA ajudou a construir o Effective Rank como tese central e, depois, o Residual Momentum como achado positivo. Nos dois casos ela só identificou o problema algébrico quando foi explicitamente questionada sobre redundância e sobre validade de construct. Duas vezes o mesmo tipo de falha, e as duas só apareceram porque alguém pediu auditoria. A IA não avisou espontaneamente em nenhuma delas.

## Enquadramento aprovado para a seção de GenAI

> Duas implementações independentes reproduziram aproximadamente o mesmo resultado, mas uma auditoria algébrica mostrou que reprodutibilidade não garante validade do construct. A equipe descartou a interpretação original antes da abertura do holdout e formulou uma nova hipótese de reversão residual de curto prazo.

## Registro no AI_USE_LOG

O repo tem `AI_USE_LOG.md` com formato próprio, criado pelo parceiro. Cada entrada distingue contribuição da IA, decisão humana e verificação independente. Entradas de 12/08 e 14/08 já existem; falta a do resultado do OOS.
