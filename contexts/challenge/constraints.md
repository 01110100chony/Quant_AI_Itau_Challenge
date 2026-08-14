# Challenge constraints

## Quick Summary

- **Purpose:** Consolidar restrições do desafio que moldam a execução do research.
- **Read when:** Planejando dados, feasibility, backtest ou relatório.
- **Load next:** Para o processo científico, [`../research/protocol.md`](../research/protocol.md).
- **Authority:** Síntese operacional; decisões científicas continuam no Project Status e no Research Log.

## Contents

- [Research constraints](#research-constraints)
- [Implementation constraints](#implementation-constraints)
- [Reporting constraints](#reporting-constraints)

## Research constraints

- A tese deve ser economicamente clara, falsificável e defensável.
- Retorno alto não compensa desenho inválido.
- Informação de decisão deve ser point-in-time; survivorship e calendários precisam ser tratados ou explicitados como limitação.
- OOS é recurso escasso e segue a [`política canônica`](../research/oos_policy.md).
- Complexidade só se justifica por informação incremental, estabilidade ou interpretação econômica.

## Implementation constraints

- Use Python 3.11+ e dependências já justificadas.
- Preserve dados raw e separe aquisição de transformação.
- Não construa engine, optimizer, dashboard ou pipeline de produção antes de o fenômeno sobreviver.
- Qualquer estratégia implementável precisa especificar decisão, execução, frequência, custos, slippage, turnover e short/borrow quando aplicável.

## Reporting constraints

O relatório final é curto. A pesquisa deve sustentar uma pergunta memorável, regras replicáveis, interpretação crítica, uso material e verificável de GenAI e poucas evidências visuais fortes. Essa é a leitura interna consolidada no Research Log, não uma reprodução de rubric oficial.
