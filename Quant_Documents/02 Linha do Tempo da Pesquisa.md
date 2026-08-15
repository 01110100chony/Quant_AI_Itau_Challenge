---
tags: [historico, timeline]
atualizado: 2026-08-14
---

# Linha do Tempo da Pesquisa

Volta para [[00 MOC - Desafio Quant AI 2026]].

## Julho — a proposta inicial

O pré-relatório foi entregue com a tese **VEGA-Δ**: momentum 12−1 nas ações mais líquidas da B3, com trava de risco pela média móvel de 200 dias do Ibovespa. Compra as 10 melhores por momentum, sai para o CDI quando o índice fecha abaixo da média.

A justificativa era subreação: o mercado reage devagar a informação nova, então quem vem subindo continua subindo. A trava resolvia o problema conhecido dos *momentum crashes*.

O pré-relatório **não valia nota**. Servia para confirmar a composição da equipe, que ficou travada em 31/07.

## Início de agosto — a virada

O parceiro pesquisou os vencedores de 2024 e 2025 (Persistence, Pharos, Coincierge, Prometheus, KernelNet, Janus IA, Maxwell) e identificou um padrão: todos têm uma **representação quantitativa interessante** que conecta um fenômeno financeiro a uma decisão de investimento.

Conclusão dele, registrada no `Research_Log`: momentum puro não tem gancho de pesquisa memorável, e a nota interna que deu para VEGA-Δ foi **4/10**, a pior da lista de candidatas.

A partir daí veio a família de teses estruturais. Ver [[03 Cadeia de Falsificacao]].

## 10 e 11/08 — as três primeiras falsificações

`Effective Rank`, `Opportunity Set` e `Adaptive Factor Neutralization` foram testadas e encerradas. Sobrou o `Residual Momentum 12−1` como subproduto exploratório, com holdout preservado e fechado.

`PROJECT_STATUS.md` de 11/08 abre com: *"Nenhuma tese está oficialmente promovida neste momento."*

## 12/08 — CM_001

Criado o artefato do `Cross-Market Lead-Lag` como próxima candidata. Ficou em `DRAFT`, com todos os campos de pesquisa em `TBD`.

## 14/08 — o dia inteiro

**Manhã e tarde.** O parceiro construiu o *research harness*: `contexts/`, política de OOS, registry de experimentos, `verify_research.py` com 406 linhas e testes automatizados. Commit `v2` às 17:50.

**Tarde.** Auditoria da frente de relatório: reimplementação independente do Residual Momentum a partir da specification escrita. Reproduziu o painel de 307 meses e o research de 214, com as mesmas datas.

**Noite.** Um parecer externo apontou que o construct estava errado por **identidade algébrica de OLS**. Verificado a 4×10⁻¹⁶. O sinal chamado de momentum 12−1 era, na verdade, reversão residual de curto prazo. Ver [[03 Cadeia de Falsificacao]].

Pivô para `RSR_001`, quatro rodadas de revisão da specification, correção da fórmula de custo, congelamento por commit `H1`, e abertura única do OOS.

**Veredito: `NO-GO`.** Ver [[04 RSR_001 - Spec e Veredito do OOS]].

## Erros cometidos no caminho, e corrigidos

Registrados porque são material de relatório e porque evitam repetição.

| erro | quem pegou | como |
|---|---|---|
| Reimplementação com beta móvel diário em vez de uma regressão por janela de formação | conferência contra o notebook original | o método do parceiro era o correto, o padrão de Blitz |
| Alarme falso de que `n=214` invadia o holdout | leitura do notebook `v0_5` | o split é 70/30 posicional e a separação era limpa |
| Rodada diagnóstica com split posicional alcançou fev/2019 | auto-detecção | 4 meses viraram quarentena permanente |
| Custo calculado só na perna comprada | parecer externo | subestimava pela metade; corrigido para `sum\|dw\|` |
| `P3` definido como inversão de sinal | implementação | era identidade trivial de Spearman, sem conteúdo; virou ablação `A1` |
| `created_at` inventado no manifesto | parecer externo (Gate B) | substituído pelo mtime real |
| Primeiro `H1` marcou 12 de 13 caixas | contagem de linhas do commit | corrigido por `--amend` |
| `spec.md` descrevia `P3` enquanto o código usava `A1` | varredura antes do freeze | divergência spec-código corrigida |
| `drop(columns="long")` na persistência | crash na abertura do OOS | bug ainda aberto, ver [[01 Estado Atual e Proximos Passos]] |
