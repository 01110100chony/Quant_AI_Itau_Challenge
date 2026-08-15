---
tags: [onboarding, briefing]
atualizado: 2026-08-14
---

# Briefing para Sessão Nova

Volta para [[00 MOC - Desafio Quant AI 2026]].

Cole isto no início de uma sessão nova, no Claude Code ou em qualquer outro assistente. Depois mande ler as notas linkadas.

---

## Contexto em 10 linhas

Estou no Desafio Quant AI 2026 do Itaú Asset, com entrega em **16/08/2026 às 23h59**: PDF de no máximo 5 páginas, 16:9, totalmente anônimo.

Somos 3 pessoas. Meu parceiro tocou a pesquisa quantitativa e montou um research harness rigoroso no repositório. Eu toquei a frente de relatório e auditoria.

O projeto testou cinco hipóteses e **todas foram encerradas**. A última, `Residual Short-Term Reversal`, foi congelada por commit, testada uma única vez fora da amostra em 14/08 e deu **`NO-GO`**: `mean IC` de `+0,0611` no research virou `−0,0476` no holdout, e o `p` da permutação foi de `0,005` para `0,898`.

O relatório deixa de ser sobre uma estratégia vencedora e passa a ser sobre a **cadeia de falsificação**. O manual de avaliação diz que a banca prioriza qualidade do processo, não desempenho histórico.

Repositório: `github.com/01110100chony/Quant_AI_Itau_Challenge`, branch `relatorio-epsilon`.
Robô: **ε / ÉPSILON**. Equipe **Delta Vega**, que jamais pode aparecer no relatório.

## Ordem de leitura

1. [[03 Cadeia de Falsificacao]] — o núcleo científico, com os números
2. [[04 RSR_001 - Spec e Veredito do OOS]] — a tese final e o resultado
3. [[06 Edital e Plano do Relatorio]] — as regras e a estrutura das 5 páginas
4. [[01 Estado Atual e Proximos Passos]] — o que falta e o bloqueio aberto
5. [[07 Artefatos, Scripts e Runbook]] — comandos e onde está cada arquivo
6. [[05 Aprendizados Metodologicos]] — se precisar do porquê das decisões
7. [[08 Governanca, Hashes e Uso de IA]] — hashes e regras do harness
8. [[02 Linha do Tempo da Pesquisa]] — se precisar reconstruir a história

No repositório, leia também, nesta ordem: `PROJECT_STATUS.md`, `Research_Log_Desafio_Quant_AI_2026.md`, `TASKS.md`, `contexts/CONTEXT_MAP.md`.

## Regras que não podem ser quebradas

> [!danger] Proibições pós-OOS
> O `NO-GO` é definitivo. **Não** tentar resgatar com `S=42`, outra janela, outro custo, outro universo, outro critério ou reinterpretação da direção do sinal. Está escrito na specification e foi aprovado por humano antes da abertura.

> [!danger] Anonimato
> "Delta Vega", nomes de pessoas, universidade, logos ou o link do repositório no PDF = eliminação. Limpar metadados do arquivo também.

> [!danger] Cinco páginas
> Seis ou mais eliminam. Capa e referências contam.

## O que falta fazer

1. Decidir sobre o bug de persistência do OOS (opções A e B em [[01 Estado Atual e Proximos Passos]])
2. Atualizar `manifest.toml` e registry para `OOS_OPENED`
3. Transcrever os números do OOS para `results.md`
4. **Reescrever as páginas 1, 3 e 4 do PDF** à luz do `NO-GO`
5. Preencher a linha `ONDE FALHOU` da tabela de IA (texto pronto em [[08 Governanca, Hashes e Uso de IA]])
6. Revisão final de eliminação e envio

## Números que você vai precisar

**Research sample**, 2001-02-28 a 2018-10-31, n=213:
`IC +0,0611` · `p1 0,0052` · `p2 0,0094` · bruto `+5,53%` · custo `3,30%` · líquido `+2,23%` · Sharpe `0,21` · DD `−31,8%` · turnover `2,751`

**Final OOS**, 2019-03-29 a 2026-07-31, n=89:
`IC −0,0476` · `p1 0,8980` · `p2 0,8530` · blocos `−0,0233 / −0,0422 / −0,0782` · bruto `−5,51%` · custo `2,99%` · líquido `−8,50%` · Sharpe `−0,66` · DD `−75,5%` · turnover `2,494`

**Quarentena**, 2018-11-30 a 2019-02-28, n=4, permanentemente fora do OOS.

**Hashes:** `H1 = 66bd72831eb803beeeefe63686ef915385f00b0c`, `H2 = a45b3a4`.
