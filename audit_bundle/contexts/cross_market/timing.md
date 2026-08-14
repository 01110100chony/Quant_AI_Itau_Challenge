# Cross-Market timing

## Quick Summary

- **Purpose:** Isolar o contrato temporal e os riscos de alinhamento entre mercados.
- **Read when:** Definindo sessões, calendários, timezone, feature availability ou decision timestamp.
- **Load next:** Depois de decisão humana, sincronize o contrato com [`data_contract.md`](data_contract.md) e testes futuros.
- **Authority:** Requisitos temporais da candidata; horários concretos ainda não estão aprovados.

## Contents

- [Known timing requirement](#known-timing-requirement)
- [Unresolved timing fields](#unresolved-timing-fields)
- [Future mechanical invariants](#future-mechanical-invariants)

## Known timing requirement

O teste deve explorar uma barreira temporal natural entre mercados e alinhar rigorosamente timezone, sessão e feriados. A informação de `A` usada na feature precisa estar publicamente disponível antes da decisão ou abertura-alvo em `B`.

## Unresolved timing fields

- Mercado líder e timezone: **TBD — requires human decision**.
- Mercado seguidor e timezone: **TBD — requires human decision**.
- Janela exata de informação de `A`: **TBD — requires human decision**.
- Timestamp exato da decisão em `B`: **TBD — requires human decision**.
- Preço de execução candidato: **TBD — requires human decision**.
- Calendários e tratamento de DST: **TBD — requires human decision**.

## Future mechanical invariants

Quando dados e timing forem aprovados, testes reais deverão verificar:

- `feature_timestamp < decision_timestamp`;
- fim da janela de informação de `A` anterior à decisão/abertura em `B`;
- nenhum target session duplicado;
- nenhuma sessão futura de `A` mapeada para target passado em `B`;
- nenhuma observação duplicada por feriados distintos;
- timestamps timezone-aware e DST tratado explicitamente;
- boundaries de research, validation e OOS respeitados.

Esses itens são especificação futura, não testes implementados que passam sem dados.
