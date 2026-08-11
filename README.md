# Desafio Quant AI 2026

Repositório de pesquisa quantitativa para o Desafio Quant AI 2026. O projeto está na fase de seleção e falsificação da tese principal; nenhum resultado exploratório deve ser interpretado como alpha validado.

## Estado atual

- Effective Rank, Opportunity Set e Adaptive Factor Neutralization estão encerrados como tese principal.
- Residual Momentum 12–1 está preservado apenas como baseline exploratório.
- O holdout 2018–2026 da linha anterior permanece fechado.
- Cross-Market Lead-Lag é o próximo feasibility candidato, condicionado à aprovação da specification.

Consulte, nesta ordem, `PROJECT_STATUS.md`, `Research_Log_Desafio_Quant_AI_2026.md` e `TASKS.md` antes de iniciar trabalho não trivial.

## Estrutura

```text
.
├── data/
│   ├── raw/          # snapshots de origem; não sobrescrever silenciosamente
│   └── processed/    # dados derivados e reproduzíveis
├── notebooks/        # specification, feasibility e interpretação
├── src/              # lógica reutilizável após estabilização
├── tests/            # testes de dados, tempo e ausência de look-ahead
├── config/           # parâmetros aprovados e não secretos
├── reports/          # tabelas, figuras e entregáveis derivados
└── Quant_Documents/  # material auxiliar e histórico do projeto
```

As pastas possuem documentação própria. Módulos vazios não são criados apenas para preencher a estrutura.

## Ambiente

Requer Python 3.11 ou superior. As versões auditadas das dependências diretas estão em `requirements.txt`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Execute notebooks a partir de `notebooks/`, preservando os caminhos relativos existentes. Downloads devem ser separados de transformações, ter período fixo e não substituir snapshots raw sem registro explícito.

## Governança científica

- Features usam somente informação disponível no timestamp da decisão.
- OOS só pode ser aberto depois do freeze da specification.
- Resultados negativos são registrados sem ajuste retrospectivo de parâmetros.
- Mudanças de universo, sinal, target, horizonte, benchmark, split ou critério de sucesso exigem aprovação humana.
