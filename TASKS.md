# TASKS.md

## Archived — CM_001 v1.0.1-frozen provenance and Stage B

- [x] Close Stage A structurally with `PASS_READY_FOR_SPEC_FREEZE`.
- [x] Record reviewed Stage A baseline H0 `78d9f6e`.
- [x] Human-approve provider, missing, raw-price, corporate-action, calendar and sample policies.
- [x] Human-approve exact models, HAC inference, P1/P2, stability, secondary diagnostics and gates.
- [x] Reconcile pre-association counts H1 `1938`, H2 `2034`, H3 `1850`.
- [x] Create H1 scientific freeze commit `cc686c7` with synthetic tests and no feature–target result.
- [x] Record exact H1 and authorize Stage B in H2 metadata.
- [x] Create corrective P2 H1c and record it in H2c for `v1.0.1-frozen`, without association execution.
- [x] Execute corrected frozen Research Stage B exactly once; literal verdict `NO_GO`.
- [x] Verify and persist Stage B results in a separate commit; stop without optimization.

## Invariantes vigentes — amostras fechadas de CM_001

- Validation `2019-01-01`–`2022-12-31` permanece CLOSED e não pode ser carregada.
- Final OOS `2023-01-01`–`2025-12-31` permanece CLOSED e não pode ser carregado.
- 2026 permanece integralmente excluído.
- Nenhum acesso a holdout pode ser solicitado sem decisão humana posterior e separada.

## Invariantes vigentes — encerramento de CM_001

- Ativos, amostras, janelas, target e controles congelados não podem ser alterados.
- Nenhuma variante nova ou parameter search pode ser executada após os resultados.
- H1 e resultados secundários não podem resgatar a H2 primária.
- Nenhum backtest, estratégia, portfolio, custo ou inferência de execução pode ser
  derivado para resgatar CM_001.
- Linhas de pesquisa encerradas não podem ser revividas sem decisão humana explícita.
