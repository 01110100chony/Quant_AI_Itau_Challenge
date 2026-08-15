# OOS policy

## Quick Summary

- **Purpose:** Governar research, validation e final OOS como recursos distintos e impedir contaminação.
- **Read when:** Definindo splits, congelando specification ou solicitando acesso a holdout/OOS.
- **Load next:** Registre freezes e abertura no artefato do experimento e no [`experiment registry`](experiment_registry.md).
- **Authority:** Política canônica de holdout/OOS; mudanças exigem decisão humana explícita.

## Contents

- [Sample roles](#sample-roles)
- [Access sequence](#access-sequence)
- [After opening](#after-opening)
- [Mechanical protection](#mechanical-protection)
- [Legacy holdout](#legacy-holdout)

## Sample roles

- **Research sample:** pode ser explorado dentro da specification registrada. Resultados informam falsificação e a decisão GO/CONDITIONAL GO/NO-GO.
- **Validation:** só pode ser aberta após specification freeze, parâmetros congelados, commit registrado e aprovação humana.
- **Final OOS:** só pode ser aberto após validation, decisão registrada, novo freeze e autorização humana explícita.

Definir datas de split é decisão metodológica material. O agente não pode inventá-las nem movê-las retroativamente.

**Desenho de duas etapas.** Um experimento pode ir de research direto ao final OOS, sem amostra de validação intermediária, desde que a ausência esteja declarada na specification e aprovada por humano **antes** do freeze. Nesse caso `validation_start` e `validation_end` ficam vazios no manifesto e o verificador não exige o intervalo para os status `OOS_OPENED` e `FINAL` — que já exigem intervalo de OOS. Os status `VALIDATION` e `VALIDATED` continuam exigindo o intervalo, porque são estados sobre a própria validação. O desenho de duas etapas gasta o único holdout numa só decisão e não deve ser escolhido por conveniência de prazo.

## Access sequence

Antes de abrir validation ou final OOS:

1. specification e critérios de decisão completos;
2. parâmetros congelados e `spec_version` registrada;
3. commit Git registrado;
4. decisão e aprovação humana documentadas;
5. manifest e registry atualizados antes do acesso;
6. execução limitada à amostra autorizada.

## After opening

Qualquer modificação material depois de observar o holdout invalida seu status como amostra limpa para a specification anterior. Resultado negativo é registrado como negativo e não autoriza parameter search, troca de datas, ativos, target, métrica ou narrativa. O agente não abre OOS por curiosidade.

## Mechanical protection

`scripts/verify_research.py` garante coerência do metadado: splits ordenados e não sobrepostos, estados válidos, freeze com versão/commit e abertura OOS acompanhada de timestamp e referência de aprovação. Isso não prova que um notebook nunca leu determinada linha de dados.

Uma barreira de acesso real só deverá ser implementada quando existirem snapshots e paths concretos para Cross-Market. A solução preferida é separar fisicamente os arquivos por sample e fornecer aos notebooks de research somente o path autorizado. Hooks ou detectores de strings não são proteção confiável e não serão usados como substitutos.

## Legacy holdout

O holdout 2018–2026 da linha Effective Rank / Opportunity Set permanece fechado. Ele não pertence automaticamente a Cross-Market e não pode ser reutilizado ou aberto sem decisão humana explícita.
