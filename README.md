# Desafio Quant AI 2026 — Research Harness

Repositório de pesquisa quantitativa falsification-first para o Desafio Quant AI 2026. O harness organiza contratos, specifications, proveniência e verificações do processo; ele não substitui julgamento metodológico humano nem mede performance de estratégias.

## Estado atual

- Nenhuma tese está oficialmente promovida.
- Effective Rank, Opportunity Set e Adaptive Factor Neutralization estão encerrados.
- Residual Momentum 12–1 é apenas baseline/fallback exploratório.
- O holdout 2018–2026 da linha anterior permanece fechado.
- `CM_001 — Cross-Market Information Transmission` foi encerrado como
  `v1.0.1-frozen / NO_GO` no Research; seus holdouts permanecem fechados.

O estado canônico está em [`PROJECT_STATUS.md`](PROJECT_STATUS.md). Comece qualquer pesquisa pelo [`Context Map`](contexts/CONTEXT_MAP.md).

## Rotas principais

| Necessidade | Fonte canônica |
|---|---|
| Estado científico atual | [`PROJECT_STATUS.md`](PROJECT_STATUS.md) |
| Histórico e decisões anteriores | [`Research_Log_Desafio_Quant_AI_2026.md`](Research_Log_Desafio_Quant_AI_2026.md) |
| Contexto mínimo para uma tarefa | [`contexts/CONTEXT_MAP.md`](contexts/CONTEXT_MAP.md) |
| Protocolo de research | [`contexts/research/protocol.md`](contexts/research/protocol.md) |
| Governança de OOS | [`contexts/research/oos_policy.md`](contexts/research/oos_policy.md) |
| Registry de experimentos | [`contexts/research/experiment_registry.md`](contexts/research/experiment_registry.md) |
| Uso material de GenAI | [`AI_USE_LOG.md`](AI_USE_LOG.md) |

## Estrutura

```text
.
├── contexts/              # contratos científicos com disclosure progressivo
├── research/experiments/  # artefatos autocontidos por experimento
├── notebooks/             # specification, feasibility e interpretação
├── src/                   # lógica reutilizável após estabilização
├── tests/research/        # garantias mecânicas do processo
├── scripts/               # verificação determinística e offline
├── data/                  # snapshots raw e derivados reproduzíveis
├── config/                # parâmetros aprovados/congelados
└── reports/               # artefatos derivados
```

Pastas e módulos só são criados quando têm responsabilidade real. O checkout `.references/quant-mind/` é referência externa, está ignorado e nunca é dependência do projeto.

## Ambiente e verificação

Requer Python 3.11 ou superior. As versões auditadas das dependências dos notebooks estão em `requirements.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/verify_research.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

O verificador testa integridade do processo e metadados, não retorno, Sharpe ou validade econômica.
