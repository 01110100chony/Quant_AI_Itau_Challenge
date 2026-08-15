---
tags: [edital, relatorio, entrega]
atualizado: 2026-08-14
---

# Edital e Plano do Relatório

Volta para [[00 MOC - Desafio Quant AI 2026]].

Fontes: `Diretrizes_Relatorio_Final_DesafioQuantAI2026.pdf` e `Criterios_Avaliacao_Desafio.pdf`, ambos na pasta do projeto.

## Regras que eliminam

- **Máximo 5 páginas.** Seis ou mais = eliminação. Capa, referências e apêndice contam.
- **Anonimato total.** Sem nomes, sem nome de equipe, sem universidade, sem logos. **"Delta Vega" não pode aparecer.** "ε / ÉPSILON" pode.
- **Metadados do PDF.** PowerPoint, Word e Canva embutem o autor no arquivo. Limpar antes de enviar.
- PDF, orientação horizontal 16:9.
- Nome do arquivo exatamente `[chave de envio].pdf`.
- Nenhum link externo, nenhum QR code. **Não citar o repositório**, que é público e expõe o usuário.
- Português como língua oficial.
- Legível em tela cheia sem zoom.
- Referência de teto: cerca de 750 palavras no documento inteiro.

## Critérios e pesos

| critério | peso | o que a banca quer |
|---|---:|---|
| Conceito da estratégia | 20% | hipótese central, ineficiência explorada, lógica econômica |
| Modelagem | 20% | estrutura quantitativa, dados, sinais, geração das decisões |
| Backtest | 15% | metodologia, consistência, **tratamento de vieses** |
| Análise dos resultados | 15% | clareza, interpretação crítica, pontos fortes e fracos |
| Uso de IA generativa | 15% | como foi usada, valor agregado, exemplos, **limitações encontradas** |
| Conclusão e próximos passos | 10% | viabilidade, limitações, melhorias |
| Apresentação do robô | 5% | coerência do nome, identidade visual, integração |

## Princípios do manual, que favorecem este projeto

> "O desempenho das equipes **não será avaliado exclusivamente com base em resultados históricos**. A banca considerará, de forma prioritária, a **qualidade do processo** de desenvolvimento da estratégia."

> "A complexidade da estratégia, por si só, não constitui fator de pontuação."

Pontos negativos explícitos: *"apresentação exclusivamente descritiva de métricas"*, *"ausência de análise crítica"*, *"omissão de fragilidades do modelo"*, e em GenAI, *"uso superficial ou meramente declaratório"*.

**Leitura estratégica:** com um `NO-GO`, o projeto perde força em Modelagem e Análise se for apresentado como derrota. Mas ganha em Backtest, Análise crítica, GenAI e Conclusão se for apresentado como o que é: um teste pré-registrado que a equipe desenhou para poder falhar, e que falhou.

## Estrutura das 5 páginas — versão a reescrever após o NO-GO

O PDF atual (`EPSILON_relatorio_final.pdf`) foi montado assumindo que o holdout confirmaria. **Páginas 1, 3 e 4 precisam de reescrita.**

### Página 1 — A pergunta e o robô
Cobre Conceito 20% e Robô 5%. Cerca de 130 palavras.

A pergunta de pesquisa em corpo grande, a identidade do ε com a equação, a explicação do nome (obrigatória, §6), e a ineficiência com seu mecanismo.

**O que muda:** o mecanismo deixa de ser subreação e passa a ser sobrerreação de curto prazo no espaço residual. E a pergunta ganha uma segunda camada: *o que sobra quando o mercado é descontado, e isso persiste ou reverte?*

### Página 2 — O funil de falsificação
Cobre Conceito 20% e GenAI 15%. Cerca de 160 palavras.

Diagrama dominante, cinco degraus, cada um com o número que o encerrou. Ver [[03 Cadeia de Falsificacao]].

**O que muda:** ganha o quinto degrau, o `NO-GO` do próprio OOS.

### Página 3 — O modelo
Cobre Modelagem 20%. Cerca de 140 palavras.

Fluxograma de cinco passos, as duas equações, a tabela de especificação congelada.

**O que muda:** as equações passam a ser as do `RSR_001` point-in-time, e a especificação ganha os hashes `H1` e `H2` como carimbo.

### Página 4 — Backtest e resultados
Cobre Backtest 15% e Análise 15%. Cerca de 170 palavras.

**O que muda, e é a maior mudança:** o gráfico passa a mostrar o research contra o OOS com o contraste brutal. `IC +0,0611` virando `−0,0476`. `p 0,005` virando `0,898`. A caixa de vieses ganha o congelamento por commit e a quarentena dos 4 meses.

### Página 5 — Conclusão e próximos passos
Cobre Conclusão 10% e GenAI 15%. Cerca de 150 palavras.

**O que muda:** a conclusão passa a ser a versão `NO-GO`, que já estava escrita no blueprint. Limitações assumidas, e o quadro de GenAI com a linha `ONDE FALHOU` preenchida.

## Texto-âncora para a conclusão NO-GO

> A residualização não sobreviveu ao holdout. Registramos o NO-GO sem reajustar parâmetros. O achado do research sample era, com alta probabilidade, ruído amostral, e essa é exatamente a resposta que o processo foi desenhado para produzir.

## Correções de texto obrigatórias no PDF atual

| atual | corrigido |
|---|---|
| "consistente ao longo de dezessete anos" | "vantagem média no research sample, com variação substancial entre subperíodos" |
| "Holdout aberto uma única vez" | manter, agora é verdade |
| "SOBREVIVEU" na tabela do funil | "SOBREVIVEU NO RESEARCH SAMPLE" e depois "NO-GO NO HOLDOUT" |
