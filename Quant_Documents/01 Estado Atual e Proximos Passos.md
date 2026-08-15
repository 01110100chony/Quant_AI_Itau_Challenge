---
tags: [estado, pendencias]
atualizado: 2026-08-15
---

# Estado Atual e Próximos Passos

Volta para [[00 MOC - Desafio Quant AI 2026]].

## O que está pronto

- Cadeia de falsificação completa e documentada. Ver [[03 Cadeia de Falsificacao]].
- `RSR_001` congelado por commit `H1`, com 13 aprovações humanas registradas.
- OOS aberto **uma única vez**, veredito `NO-GO`. Ver [[04 RSR_001 - Spec e Veredito do OOS]].
- **Reauditoria estática dos artefatos congelados**, sem reexecução e sem parâmetros novos. 20 identidades aritméticas satisfeitas, conformidade spec↔código conferida linha a linha, veredito reproduzido mecanicamente. Registro em `research/experiments/RSR_001/reauditoria.md`.
- **Repositório coerente com o fato**: `manifest.toml`, `results.md`, `decision.md` e o registry passaram a declarar `FINAL` / `NO-GO`.
- **Relatório final pronto**: 5 páginas, 960×540 pt (16:9 exato), anônimo, metadados sem autoria, sem placeholders. Ver [[06 Edital e Plano do Relatorio]].
- Harness verde: `verify_research.py` OK, 6 testes.
- Branch `relatorio-final` commitada e pushada.

## O bloqueio de governança — resolvido

Era: os CSVs do OOS não foram gravados porque a execução levantou `KeyError: "['long'] not found in axis"` em `scripts/rsr_001.py:310`, depois de imprimir o veredito.

**Decisão tomada: Opção B.** Não reexecutar. Os números foram transcritos para `results.md` com a proveniência escrita de forma explícita.

A reauditoria acrescentou um agravante que não se sabia: **`reports/rsr_001_oos_terminal.txt` está vazio**, 1 byte. A devolutiva de 14/08 dizia que a saída de terminal tinha sido preservada nele. Não foi. Portanto **não existe nenhum artefato de máquina do Final OOS** — nem os dois CSVs, nem a transcrição do terminal. A única fonte dos números é prosa.

O que sustenta a transcrição: os números passam em 20 testes de consistência mútua que uma transcrição errada teria altíssima chance de reprovar — custo `= c·turnover·12`, líquido `=` bruto menos custo, Sharpe `=` líquido sobre volatilidade, médias ponderadas por bloco reproduzindo o `mean IC` nos dois lados, taxas caindo em `k/n` inteiro para `n=213` e `n=89` simultaneamente, e os quatro p-valores caindo exatamente na grade `(1+k)/5001`. Isso não prova que a execução ocorreu; sustenta que a transcrição é fiel.

> [!warning] O bug de persistência continua no código, de propósito
> Corrigir a linha só teria efeito acompanhado de reexecução, e reexecutar está vedado pela regra pré-registrada. Fica registrado como achado F4.

## O que falta, em ordem

1. **Renomear o PDF** para `[chave de envio].pdf`. A chave vem pelo canal oficial.
2. **Revisão final de eliminação**: contagem de páginas, anonimato, metadados, 16:9, nome do arquivo. Os quatro primeiros já foram verificados por script; o nome depende do item 1.
3. **Enviar até domingo 16/08**, de preferência até as 18h.

## Frente paralela

`CM_001` Cross-Market Lead-Lag segue em `DRAFT`, com campos `TBD`, sem código e sem dados. Não entra nesta entrega. O relatório sai com a história do `RSR_001`, que é o combinado.

## Riscos conhecidos

- **Comparação, não critério.** O edital não aloca nenhum ponto a desempenho, e o `NO-GO` fortalece Backtest, Análise e IA. Mas avaliadores são humanos, e contra uma equipe com rigor **e** resultado positivo, a nossa perde. Contra resultado positivo sem rigor, temos argumento.
- **Ser lido como "não terminamos".** Mitigado no relatório: veredito na página 1, funil de cinco hipóteses na 2, critério caindo por regra na 4.
- **Tentação de resgate.** As proibições pós-OOS seguem em vigor. Ver [[08 Governanca, Hashes e Uso de IA]].
