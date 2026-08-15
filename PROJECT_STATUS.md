# PROJECT_STATUS.md

## Desafio Quant AI 2026 — Estado Atual

**Fase:** encerrada. Cadeia de falsificação completa, relatório final montado.
**Última atualização:** 15/08/2026

## Tese principal

Nenhuma. As cinco hipóteses testadas foram encerradas, e a última foi encerrada
fora da amostra.

## Cadeia de falsificação

| # | hipótese | como morreu | veredito |
|---|---|---|---|
| 1 | Effective Rank | identidade `ER = N/(1+(N−1)ρ̄²)`; Spearman com Market Mode `−0,9995` | descartada |
| 2 | Opportunity Set | `Spearman(Opportunity, IC) = −0,044`, nulo e com sinal invertido | falsificada |
| 3 | Adaptive Factor Neutralization | `Spearman(Commonality, ΔIC) = −0,059`; quintil de maior dominância contrário | falsificada |
| 4 | Residual Momentum 12−1, construct | identidade de OLS a `4,7e−16`: o sinal era reversão de 21 dias | `NO-GO` de construct |
| 5 | Residual Short-Term Reversal | Final OOS: `mean IC −0,0476`, `p_P1 0,8980`, líquido `−8,50% a.a.` | `NO-GO` fora da amostra |

Duas derrubadas por álgebra, três por dados.

## RSR_001 — estado terminal

`FINAL`, veredito `NO-GO`. OOS de 89 meses aberto uma única vez em 14/08/2026,
após freeze por `H1` com 13 aprovações humanas registradas.

- Especificação e critério: `research/experiments/RSR_001/spec.md`
- Números e proveniência: `research/experiments/RSR_001/results.md`
- Decisão: `research/experiments/RSR_001/decision.md`
- Reauditoria estática dos artefatos congelados: `research/experiments/RSR_001/reauditoria.md`

Proibições pós-OOS em vigor: `S = 42`, outra janela, outro custo, outro
universo, outro critério e reinterpretação da direção do sinal.

## Pendência conhecida, registrada e não resolvida

Os artefatos de máquina do Final OOS não existem. A execução quebrou na
gravação (`scripts/rsr_001.py:310`) depois de imprimir o veredito, e o arquivo
apontado como registro de terminal está vazio. Os números foram transcritos com
proveniência declarada, sem reexecução, e sua consistência mútua foi verificada
por vinte identidades algébricas. Ver `reauditoria.md`, achados F1 e F4.

Corrigir a linha de persistência só faria sentido junto de uma reexecução, que
está vedada pela regra pré-registrada.

## Holdout

Consumido para esta specification. Não existe segunda abertura possível.

O holdout 2018–2026 da linha Effective Rank / Opportunity Set permanece fechado
e não pertence automaticamente a nenhuma tese futura.

## Continuidade

`CM_001` Cross-Market Information Transmission segue em `DRAFT`, com campos
`TBD`, sem código e sem dados. Nenhuma execução autorizada por aquele draft.

Se a linha for retomada, congelar antes de qualquer código: par ou cluster de
mercados, horário de informação disponível, definição de shock, target futuro,
benchmark de abnormal return, período, controles e critério `GO/NO-GO`.
