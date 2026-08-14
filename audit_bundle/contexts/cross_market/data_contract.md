# Cross-Market data contract

## Quick Summary

- **Purpose:** Definir metadados e validações exigidos antes de adquirir ou transformar dados Cross-Market.
- **Read when:** Selecionando fonte, snapshot, símbolos, campos de preço ou calendários.
- **Load next:** Use [`timing.md`](timing.md) para sessões e [`validation_plan.md`](validation_plan.md) para checks.
- **Authority:** Contrato técnico candidato; escolhas de universo e fonte são decisões humanas pendentes.

## Contents

- [Required provenance](#required-provenance)
- [Data fields](#data-fields)
- [Acquisition constraints](#acquisition-constraints)
- [Current state](#current-state)

## Required provenance

Cada snapshot deverá registrar fonte, identificadores/símbolos, mercado/exchange, período solicitado, timestamp da coleta, timezone original, moeda, campo de preço, política de ajustes e calendário de sessões.

## Data fields

- Universo e pares: **TBD — requires human decision**.
- Fonte de dados: **TBD — requires human decision**.
- OHLC/adjusted fields necessários: **TBD — requires human decision**.
- Benchmark: **TBD — requires human decision**.
- Política de missing sessions: **TBD — requires human decision**.

Dados transformados devem preservar uma chave para o snapshot raw e a sessão original. Forward-fill só pode ocorrer com justificativa e nunca pode preencher informação ainda não disponível; backfill futuro é proibido.

## Acquisition constraints

Aquisição deve ser separada da transformação, com período fixo e cache raw não sobrescrito silenciosamente. Não usar composição atual para reconstruir universo histórico sem limitação explícita. Não baixar ativos adicionais para procurar uma relação vencedora.

## Current state

Nenhum novo dado Cross-Market foi baixado ou inspecionado nesta reestruturação. Não existe ainda snapshot autorizado nem contrato de universo aprovado.
