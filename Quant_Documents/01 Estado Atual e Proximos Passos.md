---
tags: [estado, pendencias]
atualizado: 2026-08-14
---

# Estado Atual e Próximos Passos

Volta para [[00 MOC - Desafio Quant AI 2026]].

## O que está pronto

- Cadeia de falsificação completa e documentada. Ver [[03 Cadeia de Falsificacao]].
- `RSR_001` congelado por commit `H1`, com 13 aprovações humanas registradas.
- OOS aberto **uma única vez**, veredito `NO-GO`. Ver [[04 RSR_001 - Spec e Veredito do OOS]].
- Harness de pesquisa passando: `verify_research.py` OK, 4 testes verdes.
- PDF de 5 páginas em 16:9 montado, anônimo, metadados limpos. **Precisa ser reescrito** à luz do `NO-GO`.
- Blueprint do relatório, script de gráfico, notebook de reconciliação, script de robustez. Ver [[07 Artefatos, Scripts e Runbook]].

## Bloqueio aberto — decisão de governança

Os CSVs do OOS **não foram gravados**. A execução levantou exceção depois de imprimir o veredito:

```
KeyError: "['long'] not found in axis"
scripts/rsr_001.py:310   oos.drop(columns="long").to_csv(...)
```

Causa: a refatoração que trouxe a fórmula de custo `sum|dw|` trocou a coluna `long` por colunas de peso `w_*`, e a linha de persistência ficou com a referência antiga. O `--ensaio` não cobre esse trecho.

**Fatos:** o veredito foi observado antes da exceção, o OOS está consumido, e o registro primário é a saída de terminal.

**Duas opções, decisão do parceiro:**

- **A.** Corrigir só a linha de persistência, reexecutar apenas para gravar os artefatos, e declarar por escrito que houve segunda execução, o motivo, e que os números conferem. A execução é determinística (`seed=7`, dados e spec congelados), então não pode produzir resultado diferente.
- **B.** Não reexecutar. Adotar a saída de terminal como registro primário e transcrever os números manualmente.

Nenhuma foi executada.

## O que falta, em ordem

1. **Resolver o bloqueio acima.**
2. **Reescrever o relatório** à luz do `NO-GO`. Páginas 1, 3 e 4 mudam. Ver [[06 Edital e Plano do Relatorio]].
3. **Preencher a linha `ONDE FALHOU`** da tabela de IA. Não depende de ninguém. Sugestão pronta em [[08 Governanca, Hashes e Uso de IA]].
4. **Revisão final de eliminação**: contagem de páginas, anonimato, metadados do PDF, 16:9, nome do arquivo com a chave de envio.
5. **Enviar até domingo 16/08, de preferência até as 18h.** Não deixar para as 23h.

## Frente paralela

O parceiro estava tentando o **Cross-Market Lead-Lag** (`CM_001`) como segunda frente. Estado em 14/08: `DRAFT`, com cerca de 20 campos `TBD`, nenhum código, nenhum dado. O próprio `spec.md` diz que nenhum notebook ou acesso a dados está autorizado por aquele draft.

Se essa frente não fechar a tempo, o relatório sai com a história do `RSR_001`, que é o combinado.

## Riscos conhecidos

- **Tempo.** A reescrita do relatório é o último bloco grande.
- **Tentação de resgate.** As regras pós-OOS proíbem usar `S=42`, outra janela, outro custo ou outro critério para salvar o `NO-GO`. Ver [[08 Governanca, Hashes e Uso de IA]].
- **Dois PDFs.** Houve conversa sobre montar um segundo relatório com material do Codex. **Só um arquivo é enviado.** Fundir dois documentos no domingo é risco de estourar as 5 páginas.
