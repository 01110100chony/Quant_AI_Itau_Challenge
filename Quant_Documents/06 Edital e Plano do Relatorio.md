---
tags: [edital, relatorio, entrega]
atualizado: 2026-08-15
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

## As 5 páginas — o que foi entregue

Fonte em `reports/EPSILON_relatorio_fonte.html`, PDF em `reports/EPSILON_relatorio_final.pdf`.

| pág | conteúdo | critérios cobertos |
|---|---|---|
| 1 | A pergunta em corpo grande, hipótese, ineficiência, identidade do ε com a equação e a explicação do nome. Faixa preta no rodapé já entrega o veredito. | Conceito 20%, Robô 5% |
| 2 | Funil de falsificação: cinco hipóteses, a pergunta de cada uma, o número que a encerrou e o veredito. Caixa sobre o degrau 4 e a frase-síntese. | Conceito 20%, GenAI 15% |
| 3 | Fluxograma de cinco passos, as duas equações point-in-time, tabela da especificação congelada com turnover e custo. | Modelagem 20% |
| 4 | Gráfico de Rank IC por bloco cronológico com os seis valores observados, tabela do critério pré-registrado com as seis falhas, contraste research↔holdout e a caixa de vieses. | Backtest 15%, Análise 15% |
| 5 | Diagnóstico do resultado negativo, limitações, próximos passos, quadro de GenAI com a linha `ONDE FALHOU`, e a conclusão em faixa. | Conclusão 10%, GenAI 15% |

### Decisões de conteúdo que valem lembrar

- **O veredito aparece na página 1.** Um avaliador lendo rápido precisa entender que concluímos, não que ficamos sem tempo.
- **A página 4 não tem curva ilustrativa.** O gráfico usa os seis ICs por bloco realmente observados — três do research, três do holdout — com o divisor no congelamento. Nada foi desenhado "à mão".
- **Nenhum hash aparece no PDF.** O carimbo do freeze é comunicado como "commitado com 13 aprovações antes de qualquer número do holdout existir". Hash é risco desnecessário num critério que elimina.
- **A limitação de custo foi reconciliada.** A versão antiga dizia que custos não foram modelados, o que contradizia o líquido de −8,50%. Agora diz o que é verdade: custo linear a 10 bps, sem impacto de mercado nem slippage.

### Verificação de eliminação — feita por script

- 5 páginas · `960 × 540 pt` · razão `1,7778` (16:9 exato)
- metadados: só `/Producer: pypdf`. Sem autor, título, criador ou datas
- zero ocorrências de "Delta Vega", nomes, universidade, links, `github`
- zero placeholders: "substituir pela curva real", "Holdout ?" e "[preencher]" eliminados

### Contagem de palavras

Referência do edital: cerca de 750. O relatório tem **652 palavras de texto corrido** e cerca de 410 dentro de tabelas, eixos e rótulos — que é a forma que o próprio edital recomenda. Somando tudo dá ~1060, acima do PDF anterior (917), porque a página 4 ganhou duas tabelas de evidência que antes não existiam.

> [!note] Se for preciso cortar mais
> Os candidatos são a tabela de contraste research↔holdout da página 4 e o quadro de vieses. Os dois são pontuados. Cortar reduz palavra e reduz nota.

## Texto-âncora da conclusão

> ÉPSILON não encontrou alpha robusto — e o processo impediu que um resultado exploratório virasse estratégia recomendada.
