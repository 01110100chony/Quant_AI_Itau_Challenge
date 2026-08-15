# Research Log — Desafio Quant AI 2026
## Resumo consolidado para o grupo

**Data de consolidação:** 10/08/2026  
**Status atual:** fase de pesquisa / seleção de tese principal  
**Objetivo do documento:** registrar de forma condensada as decisões, hipóteses, testes, resultados e descartes feitos até aqui, para que todos os integrantes do grupo partam do mesmo estado de conhecimento.

---

# 1. Objetivo competitivo

O desafio não parece premiar simplesmente a estratégia com maior retorno histórico ou maior Sharpe.

A leitura dos materiais oficiais e da Masterclass indica que o foco é:

1. hipótese econômica clara;
2. transformação da hipótese em regras objetivas;
3. modelagem replicável;
4. backtest metodologicamente correto;
5. interpretação crítica dos resultados;
6. conclusões proporcionais às evidências;
7. uso concreto e justificável de GenAI;
8. comunicação extremamente eficiente no relatório final.

A restrição mais importante para nós é o relatório final curto: precisamos de uma tese que seja explicável em poucas frases e que produza 1–2 evidências visuais realmente fortes.

**Princípio de pesquisa adotado pelo grupo:**

> não buscar “o algoritmo mais impressionante”, mas uma pergunta quantitativa interessante, falsificável e economicamente defensável.

---

# 2. O que aprendemos com os projetos fortes de 2024–2025

Não encontramos os relatórios finais completos e códigos oficiais dos finalistas de 2025 publicados de forma aberta. As informações disponíveis vêm principalmente de divulgação do Itaú, equipes e ligas acadêmicas.

Ainda assim, foi possível identificar o “research hook” de vários projetos fortes:

| Projeto | Ano | Ideia central pública |
|---|---:|---|
| Persistence | 2024 | Topological Data Analysis aplicada à estrutura dos retornos / portfólio |
| Pharos | 2024 | Deep Learning + Enhanced Index Tracking |
| Coincierge | 2024 | Sentimento de notícias aplicado a moedas |
| Prometheus | 2025 | Hidden Markov Models para identificar regimes e adaptar alocação |
| KernelNet | 2025 | Rede de causalidade não linear, drivers/followers, market-neutral |
| Janus IA | 2025 | Arbitragem / convergência entre ações e ADRs/BDRs |
| Maxwell | 2025 | Entropia como métrica de risco para rebalanceamento |

## Padrão percebido

Os projetos mais fortes tendem a possuir:

Name
\text{representação quantitativa interessante}
\rightarrow
\text{fenômeno financeiro}
\rightarrow
\text{decisão de investimento}
Name

Exemplos:

- Prometheus: mercado como **estados latentes**;
- KernelNet: mercado como **rede de transmissão de informação**;
- Persistence: mercado como **estrutura topológica**;
- Janus: preços ligados por **mesma exposição econômica**.

O ponto importante não é copiar HMM, TDA ou grafos.

O que precisamos copiar é a **estrutura intelectual**:

> uma pergunta que a banca consiga lembrar depois de ler dezenas de relatórios.

---

# 3. Research Funnel utilizado

As teses candidatas foram avaliadas por:

- mecanismo econômico;
- originalidade competitiva;
- disponibilidade de dados;
- falsificabilidade;
- viabilidade do backtest;
- possibilidade de testes de robustez;
- potencial visual;
- facilidade de defesa;
- prazo de execução.

Regra usada:

> se os dados forem difíceis demais para reconstruir corretamente no prazo disponível, a ideia é eliminada mesmo que seja intelectualmente interessante.

---

# 4. Principais ideias inicialmente consideradas

## 4.1 Effective Rank / Market Dimensionality

Pergunta original:

> Quando existe espaço para stock picking?

Intuição:

- quando todas as ações se movem juntas, poucos fatores comuns dominam o mercado;
- quando os ativos se movem de forma mais independente, pode existir maior espaço para alpha cross-sectional.

Métrica inicial:

Name
ER =
\frac{(\sum_i \lambda_i)^2}
{\sum_i \lambda_i^2}
Name

onde $\lambda_i$ são os autovalores da matriz de correlação.

---

## 4.2 Model Trust / Distribution Shift

Pergunta:

> Quando um modelo deveria deixar de confiar nas próprias previsões?

Ideia:

Name
\text{distância do estado atual à distribuição de treino}
\rightarrow
\text{erro futuro do modelo}
Name

Tema muito atual em model risk / ML financeiro, porém:
- mais difícil de executar corretamente;
- risco elevado de leakage;
- existem trabalhos recentes próximos dessa formulação.

---

## 4.3 Model Disagreement

Pergunta:

> Discordância entre modelos contém informação sobre a confiabilidade de uma decisão?

Ideia:

Name
U_t =
Std(\hat y_t^{(1)},...,\hat y_t^{(M)})
Name

e testar:

Name
U_t \uparrow
\Rightarrow
Erro_{t+1}\uparrow
Name

Foi considerada mais adequada como camada de robustez do que como tese principal.

---

## 4.4 Cross-Market Lead-Lag

Pergunta:

> Quanto tempo a informação leva para atravessar mercados?

Estrutura:

Name
R_A(t)
\rightarrow
R_B(t+1)
Name

com alinhamento rigoroso de horários/sessões.

Continua entre as ideias mais fortes após o descarte do Effective Rank como tese principal.

---

## 4.5 Overnight vs. Intraday Information

Decomposição:

Name
R_{overnight}
=
\ln(Open_t/Close_{t-1})
Name

Name
R_{intraday}
=
\ln(Close_t/Open_t)
Name

Pergunta:

> choques incorporados fora do pregão possuem dinâmica diferente de choques formados durante a sessão?

Boa alternativa pela simplicidade dos dados e baixo risco metodológico.

---

# 5. Linha de pesquisa: Effective Rank / Opportunity Set

Essa foi a ideia mais explorada até agora.

Foram criadas as versões:

- `v0.1` — sanity check estrutural;
- `v0.2` — comparação ER vs. medidas simples;
- `v0.3` — residualização contra SPY;
- `v0.4` — teste Opportunity Set → Residual Momentum;
- `v0.5` — teste Adaptive Factor Neutralization.

---

# 6. v0.1 — Sanity check do Effective Rank

Universo de feasibility:

- XLB
- XLE
- XLF
- XLI
- XLK
- XLP
- XLU
- XLV
- XLY

Janela:

Name
252 \text{ pregões}
Name

Resultados principais:

Name
Corr(ER, MarketMode) \approx -0.969
Name

Name
Corr(ER, MeanCorr) \approx -0.971
Name

Os quintis apresentaram separação muito clara de estados de correlação.

Conclusão inicial:

- implementação correta;
- interpretação estrutural coerente;
- **nenhuma evidência de previsibilidade ainda**.

---

# 7. Descoberta matemática importante sobre o ER

Para uma matriz de correlação com $N$ ativos:

Name
\sum_i \lambda_i = N
Name

e:

Name
\sum_i \lambda_i^2
=
N + 2\sum_{i<j}\rho_{ij}^2
Name

portanto:

Name
ER =
\frac{N^2}
{N + 2\sum_{i<j}\rho_{ij}^2}
Name

ou:

Name
\boxed{
ER =
\frac{N}
{1+(N-1)\overline{\rho^2}}
}
Name

Consequência:

> para $N$ fixo, o participation-ratio Effective Rank é uma transformação monotônica da correlação quadrática agregada.

Isso reduziu bastante a originalidade do ER como protagonista.

Não é uma representação independente de toda a “geometria” ou topologia da matriz.

---

# 8. v0.2 — ER vs. medidas estruturais simples

Foram comparados:

- Effective Rank;
- mean correlation;
- market mode.

Resultados:

Name
Spearman(ER,MeanCorr) \approx -0.995
Name

Name
Spearman(ER,MarketMode) \approx -0.9995
Name

Ou seja:

> neste universo, as três métricas praticamente ordenam os meses da mesma forma.

Conclusão:

- abandonar a narrativa “Effective Rank Strategy”;
- promover a tese mais geral **Market Dimensionality / Opportunity Set**;
- ER passa a ser apenas uma métrica candidata.

---

# 9. v0.3 — Residualização contra SPY

Modelo:

Name
r_{i,t}
=
\alpha_i+\beta_i r_{SPY,t}+\epsilon_{i,t}
Name

Depois, a estrutura foi recalculada sobre:

Name
Corr(\epsilon_1,...,\epsilon_N)
Name

Resultados médios:

Name
ER_{raw}\approx2.28
Name

Name
ER_{resid}\approx6.24
Name

Name
MeanCorr_{raw}\approx0.605
Name

Name
MeanCorr_{resid}\approx-0.022
Name

Name
RMSCorr_{raw}\approx0.630
Name

Name
RMSCorr_{resid}\approx0.238
Name

Name
Corr(ER_{raw},ER_{resid})\approx-0.259
Name

A residualização realmente altera a representação estrutural.

Porém:

Name
Spearman(ER_{resid},RMSCorr_{resid})=-1
Name

exatamente como esperado pela identidade matemática.

Conclusão:

> ER continua sem fornecer informação independente; Residual RMS Correlation é uma representação mais simples e transparente da mesma informação.

---

# 10. Reformulação para Residual Dependence / Opportunity Set

Nova variável estrutural:

Name
D_t =
\sqrt{
\frac{2}{N(N-1)}
\sum_{i<j}
(\rho^\epsilon_{ij,t})^2
}
Name

onde:

Name
D_t = Residual\ RMS\ Correlation
Name

Interpretação:

- $D_t$ alto → dependência residual forte;
- $D_t$ baixo → movimentos relativos mais independentes.

Hipótese:

Name
D_t \downarrow
\Rightarrow
\text{melhor eficácia futura de alpha cross-sectional}
Name

---

# 11. Alpha experimental escolhido

Foi congelado:

## Residual Momentum 12–1

Name
RMOM_{i,t}
=
\sum_{\tau=t-252}^{t-21}
\epsilon_{i,\tau}
Name

Controle:

## Raw Momentum 12–1

Name
MOM_{i,t}
=
\sum_{\tau=t-252}^{t-21}
r_{i,\tau}
Name

A escolha 12–1 foi feita antes de observar os resultados condicionais para evitar parameter search.

---

# 12. Métricas de qualidade do alpha

Como o universo possui apenas 9 ETFs, evitamos inicialmente construir uma carteira arbitrária.

## Métrica primária: Rank IC

Name
IC_t =
Spearman(
Signal_{i,t},
FutureReturn_{i,t+1}
)
Name

Interpretação:

- $IC>0$: ranking contém informação;
- $IC=0$: ranking sem poder;
- $IC<0$: ranking apontou na direção errada.

## Métrica secundária: Top 3 – Bottom 3 spread

Name
Spread_t =
Return_{Top3}
-
Return_{Bottom3}
Name

---

# 13. v0.4 — Opportunity Set → Residual Momentum

Research sample:

Name
2001\text{–}2018
Name

Final OOS preservado:

Name
2018\text{–}2026
Name

e ainda **não aberto**.

## Resultado do alpha-base no research sample

Residual Momentum:

Name
MeanIC \approx 0.0496
Name

Name
MedianIC \approx 0.0917
Name

Name
HitRate(IC>0) \approx 55.6\%
Name

Raw Momentum:

Name
MeanIC \approx 0.0003
Name

Name
MedianIC \approx 0.0333
Name

Assim:

> Residual Momentum foi exploratoriamente mais informativo que Raw Momentum.

Esse foi o principal resultado positivo encontrado até agora.

---

# 14. Falha da hipótese Opportunity Set

Hipótese testada:

Name
Opportunity_t\uparrow
\Rightarrow
Quality(ResidualMomentum_{t+1})\uparrow
Name

Resultado contínuo:

Name
Spearman(Opportunity,IC)\approx-0.044
Name

Name
Spearman(Opportunity,Spread)\approx-0.087
Name

Praticamente zero e com sinal contrário.

Quintis de Opportunity Score:

| Quintil | IC médio Residual Momentum |
|---|---:|
| Q1 | +0.160 |
| Q2 | ~0 |
| Q3 | +0.040 |
| Q4 | -0.078 |
| Q5 | +0.126 |

Não existe progressão monotônica.

Conclusão:

Name
\boxed{\text{NO-GO para Opportunity Set como condicionador}}
Name

Não foi aberto o OOS.

---

# 15. v0.5 — Adaptive Factor Neutralization

Nova hipótese exploratória:

> Quanto maior a parcela dos movimentos explicada pelo fator de mercado, maior deveria ser o benefício de neutralizar esse fator antes de calcular momentum.

Definição de Market Commonality:

Name
Commonality_t
=
\frac{1}{N}\sum_iR^2_{i,t}
Name

Target:

Name
\Delta IC
=
IC^{ResidualMom}
-
IC^{RawMom}
Name

Hipótese:

Name
Commonality_t\uparrow
\Rightarrow
\Delta IC_{t+1}\uparrow
Name

---

# 16. Resultado da Adaptive Factor Neutralization

Research sample:

Name
n=214\ meses
Name

Médias:

Name
Commonality\approx0.650
Name

Name
\Delta IC_{mean}\approx+0.0493
Name

Name
\Delta IC_{median}\approx+0.0917
Name

Name
P(\Delta IC>0)\approx54.2\%
Name

Porém a relação com Commonality falhou:

Name
Pearson(Commonality,\Delta IC)\approx-0.051
Name

Name
Spearman(Commonality,\Delta IC)\approx-0.059
Name

Spread:

Name
Spearman(Commonality,\Delta Spread)\approx-0.048
Name

---

# 17. Quintis da Market Commonality

| Quintil | $\Delta IC$ médio |
|---|---:|
| Q1 | +0.023 |
| Q2 | +0.111 |
| Q3 | +0.102 |
| Q4 | +0.072 |
| Q5 | -0.061 |

O quintil de maior commonality apresenta resultado **contrário à hipótese**.

Poderíamos inventar uma hipótese pós-hoc de “sweet spot intermediário”, mas decidimos explicitamente **não fazer isso**, pois seria specification search.

---

# 18. Consistência temporal

O research sample foi separado em três blocos apenas para diagnóstico interno:

| Bloco | Período | Mean ΔIC | Spearman(Commonality, ΔIC) |
|---|---|---:|---:|
| B1 | 2001–2006 | +0.079 | +0.161 |
| B2 | 2006–2012 | -0.066 | +0.018 |
| B3 | 2012–2018 | +0.134 | -0.094 |

Conclusão:

- o benefício da residualização muda substancialmente ao longo do tempo;
- a relação Commonality → benefício da neutralização não é estável.

---

# 19. Outra redundância detectada

Market Commonality e Raw RMS Correlation são praticamente a mesma variável nesse universo:

Name
Pearson(Commonality,RawRMS)\approx0.990
Name

Name
Spearman(Commonality,RawRMS)\approx0.989
Name

Logo:

> Market Commonality também não forneceu uma nova representação estrutural significativa.

---

# 20. Status final da família Effective Rank / Opportunity Set

## Effective Rank puro

**Descartado como protagonista.**

Motivo:
- redundância matemática com correlações quadráticas;
- quase nenhuma informação incremental no universo analisado.

## Opportunity Set

**Hipótese falsificada no research sample.**

Motivo:
- dependência residual não condicionou de forma consistente o alpha futuro.

## Adaptive Factor Neutralization

**Hipótese falsificada no research sample.**

Motivo:
- Market Commonality não explicou o ganho do Residual Momentum sobre Raw Momentum.

## Residual Momentum

**Mantido como baseline/fallback promissor, mas não validado.**

Motivo:
- apresentou IC superior ao momentum bruto na amostra exploratória;
- ainda não foi testado no OOS final;
- não possui sozinho originalidade suficiente para ser nossa tese preferida.

---

# 21. Regra de governança adotada

**Não abrir o OOS 2018–2026 ainda.**

Ele continua sendo o conjunto mais valioso para validação final.

Não devemos gastá-lo em hipóteses que já falharam no research sample.

Também foi decidido:

- não testar 6–1, 9–1 etc. só porque 12–1 não gerou a história esperada;
- não inventar thresholds;
- não trocar arbitrariamente de métrica;
- não criar uma hipótese de “U-shape” ou “sweet spot” depois de observar os quintis;
- não manter ER no projeto apenas porque investimos tempo nele.

---

# 22. Principal aprendizado metodológico até agora

A sequência de pesquisa foi:

Name
EffectiveRank
Name

Name
\downarrow
Name

redundante com dependência

Name
\downarrow
Name

Opportunity Set

Name
\downarrow
Name

não condicionou alpha

Name
\downarrow
Name

Adaptive Neutralization

Name
\downarrow
Name

Commonality não explicou o ganho

Name
\downarrow
Name

Name
\boxed{
ResidualMomentum\ permanece\ como\ único\ achado\ exploratório\ promissor
}
Name

Essa sequência é útil porque mostra que o grupo está **falsificando hipóteses em vez de otimizar retrospectivamente uma narrativa**.

---

# 23. Avaliação competitiva atual

Estimativas internas qualitativas, não notas previstas da banca:

| Ideia | Potencial competitivo atual |
|---|---:|
| Momentum + MA200 | ~4/10 |
| Effective Rank puro | ~5–5.5/10 |
| Opportunity Set | ~5.5–6/10 após os testes |
| Adaptive Factor Neutralization | ~6/10 |
| Residual Momentum puro | ~6.5–7/10 |
| Cross-Market Lead-Lag | ~8.5–9/10 potencial |
| Overnight Information | ~8/10 potencial |
| Model Reliability / Distribution Shift | ~7.5–8/10 potencial |

**Conclusão atual:**

> não levar Effective Rank / Opportunity Set como tese principal para a competição.

---

# 24. Próximas teses mais promissoras

## Candidate #1 — Cross-Market Information Transmission

Pergunta:

> Quanto tempo a informação leva para atravessar mercados economicamente relacionados?

Estrutura:

Name
Shock_{A,t}
\rightarrow
AbnormalReturn_{B,t+1}
Name

Possíveis famílias:

- mercados de semicondutores em fusos diferentes;
- commodities → empresas/setores expostos;
- mercados globais com fechamento e abertura não simultâneos.

Vantagens:

- mecanismo econômico direto;
- barreira temporal natural;
- boa narrativa;
- possibilidade de event/lead-lag study;
- aproximação intelectual com KernelNet sem copiar a rede causal.

Risco principal:

- alinhamento correto de timezone e sessões;
- não criar look-ahead.

---

## Candidate #2 — Overnight Information Transmission

Pergunta:

> Choques incorporados fora do pregão persistem ou revertem de forma diferente dos choques produzidos durante o pregão?

Estrutura:

Name
R^{ON}_t
\rightarrow
R^{ID}_t
Name

ou:

Name
R^{ON}_t
\rightarrow
R^{ON}_{t+1}
Name

Vantagens:

- dados muito simples;
- excelente auditabilidade;
- baixo risco operacional;
- muito viável no prazo.

Desvantagem:

- menor originalidade que Cross-Market Lead-Lag.

---

## Candidate #3 — Model Reliability / Distribution Shift

Pergunta:

> Um modelo consegue reconhecer quando está operando fora do ambiente estatístico em que foi construído?

Estrutura:

Name
Distance(X_t,D_{train})
\rightarrow
ForecastError_{t+1}
Name

Vantagens:

- muito alinhado a 2026+ e ML/model risk;
- excelente conexão com Quant AI.

Desvantagens:

- mecanismo econômico menos direto;
- maior risco de leakage;
- literatura recente relativamente próxima.

---

# 25. Direção recomendada no momento

Próximo feasibility sugerido:

Name
\boxed{\text{Cross-Market Lead-Lag}}
Name

com um notebook separado e simples.

Objetivo:

> testar apenas se existe transmissão temporal previsível entre dois mercados/ativos economicamente relacionados.

Sem:

- ML complexo;
- otimização;
- estratégia final;
- múltiplos thresholds.

Estrutura ideal:

Name
Data
\rightarrow
TimeAlignment
\rightarrow
Shock
\rightarrow
FutureAbnormalReturn
\rightarrow
GO/NO-GO
Name

Se falhar rapidamente, migrar para **Overnight Information**.

---

# 26. Como GenAI está sendo usada no projeto

Até agora, GenAI foi usada como:

- copiloto de ideação;
- revisor metodológico;
- auditor de possíveis vieses;
- suporte de arquitetura de pesquisa;
- geração dos feasibility notebooks;
- revisão de fórmulas e identidades;
- apoio para falsificação de hipóteses;
- documentação do processo;
- controle de overfitting narrativo.

Um ponto forte para o relatório final pode ser:

> GenAI não foi utilizada como “oráculo de preço”, mas como ferramenta de pesquisa e auditoria metodológica, ajudando inclusive a identificar redundâncias matemáticas e abandonar hipóteses que não sobreviveram aos dados.

---

# 27. Princípios que não devem ser quebrados daqui para frente

1. Não usar composição atual de índice para reconstruir passado.
2. Não usar informação de $t+1$ em decisão tomada em $t$.
3. Não abrir o OOS até a especificação estar congelada.
4. Não escolher parâmetros olhando o OOS.
5. Não criar uma nova hipótese apenas para explicar um gráfico já observado.
6. Não manter complexidade que não agrega informação.
7. Não confundir correlação estrutural com capacidade preditiva.
8. Não confundir resultado exploratório com validação.
9. Não buscar “big alpha” à custa de rigor.
10. Priorizar uma tese que consiga ser explicada em uma frase.

---

# 28. Estado atual para o grupo

## O que está encerrado

- Effective Rank como protagonista;
- Opportunity Set como condicionador do Residual Momentum;
- Adaptive Factor Neutralization via Market Commonality.

## O que está preservado

- Residual Momentum 12–1 como benchmark/fallback;
- OOS final 2018–2026 ainda fechado;
- toda a infraestrutura de dados e funções construídas nos notebooks.

## O que será investigado agora

1. Cross-Market Lead-Lag;
2. Overnight Information como fallback;
3. Model Reliability como terceira opção.

---

# 29. Frase que resume nossa filosofia de research

> **Não estamos procurando um backtest que pareça vencedor; estamos procurando uma hipótese que sobreviva ao processo de tentar destruí-la.**

Esse é o critério que deve orientar as próximas decisões.

---

# 30. CM_001 — Stage A closure and v1.0 scientific freeze decision

Em 14/08/2026, antes de qualquer relação feature–target, o grupo aprovou a evidência estrutural de Stage A e congelou `CM_001 v1.0-frozen`: ativos e benchmarks originais, Research 2010–2018, Validation 2019–2022 fechada, Final OOS 2023–2025 fechado, fontes Yahoo/TWSE, raw OHLC, exclusões mecânicas de missing e corporate actions, calendários XNYS/TWSE, OLS/HAC(5), P1/P2, blocos, diagnósticos e gates literais.

O baseline Stage A revisado foi registrado em H0 `78d9f6edca157cfcbd8643f52a9667d3a85c5fd0`. H1 `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818` congelou conteúdo/código sem resultados; H2 registrou o hash H1 e autorizou a execução única de Stage B. As contagens mecânicas pré-associação são H1 1938, H2 2034, H3 1850. Validation e Final OOS permanecem fechados.

Antes da execução, foi detectado que o P2 deslocava a feature após o filtro de target H2 e poderia pular uma janela elegível com target ausente. Nenhuma associação ou receipt existia. A decisão humana preservou a semântica original — próxima janela informacional elegível antes do target — e autorizou o freeze corretivo `v1.0.1-frozen`, mantendo H0/H1/H2 imutáveis. H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6` foi registrado por H2c; o common-complete mecânico corrigido tem N `2033`.

Stage B foi então executado uma única vez em Research. H2 apresentou beta `0.014480` e p HAC unilateral `0.361406`, logo `CorePass=false`. Os gates foram `CorePass=false`, `RobustnessPass=false`, `SpecificityPass=false`, `TimingPass=true`, produzindo o veredito congelado `NO_GO`. Validation e Final OOS não foram carregados; não houve otimização ou variante pós-resultado.

---

# 31. CM_001 — encerramento definitivo

O CM_001 testou se retornos intraday específicos de semicondutores nos EUA antecipavam o desempenho relativo da tecnologia taiwanesa. O alinhamento temporal e os placebos foram auditados antes da execução, mas H2 não passou HAC nem permutação, H3 não confirmou especificidade e as robustezes não mostraram monotonicidade. O experimento foi encerrado como `NO_GO` ainda em Research; Validation e Final OOS permaneceram intocados.

---

# 32. LAF_001 — Stage A1 de viabilidade estrutural

Em 15/08/2026, após o commit pré-dados H0-A1
`01cc8408a83024663cc7cb7d434f82292072a945`, foi realizada uma única coleta
direta da Yahoo Finance Chart API para `SPY`, `QQQ`, `IWM`, `DIA` e `MDY`, com
`period1=1041379200` e `period2=1483228800` exclusivo. Os cinco payloads raw,
requests, receipts e SHA-256 foram preservados sob o retrieval
`20260815T055848814Z`.

A auditoria encontrou 3.525 sessões XNYS por símbolo entre `2003-01-02` e
`2016-12-30`, sem sessões ausentes/extras, duplicatas, timestamps não
monotônicos, nulls/zeros/negativos em OHLCV/Adj Close ou violações OHLC. Foram
enumeradas 389 distribuições e um split de IWM; o check mecânico do evento
classificou o raw como já contínuo em escala, sem escolher política de retorno
ajustado.

Uma primeira comparação derivada de calendário foi rejeitada porque a janela
padrão móvel do `exchange-calendars` começava em 2006. A correção apenas
explicitou o intervalo XNYS 2003–2016 já autorizado, adicionou regressão e
reproduziu os derivados a partir dos mesmos raw hashes, sem nova requisição.

O veredito literal da Stage A1 é
`PASS_READY_FOR_STAGE_A2_DECISIONS`. Ele prova somente disponibilidade,
cobertura e reprodutibilidade estrutural. Yahoo como fonte final, provider
secundário, políticas de missing/volume/ajustes/corporate actions, completude
da cesta, calendário, retorno zero, MAD zero e autorização de feature-side
continuam decisões humanas. Stage A2, Stage B, Validation, Final OOS, target,
associação, estratégia e backtest permanecem proibidos.

---

# 33. LAF_001 — Stage A1c corrective boundary and provenance audit

Em 15/08/2026, uma revisão independente identificou que as respostas
históricas do Yahoo continham metadados dinâmicos correntes. Esses campos foram
materializados no resultado original, inclusive em `metadata_json`, tornando a
flag `boundary_2017_or_later_loaded=false` incompleta. O incidente foi
registrado sem apagar nem reescrever o resultado original.

A autorização humana limitou a correção a: reutilizar os mesmos cinco raws,
sanitizar metadados, registrar proveniência exata e auditar mecanicamente a
unidade preço-volume em 41 sessões ao redor do split do IWM. O código/testes e
contrato foram congelados antes da reexecução em H0-A1c
`176bb12b2413edb866cdcc38e86a497021cebd6c`.

O parser `laf-stage-a1-v1.0.1` confirmou zero linhas OHLCV e zero corporate
actions de 2017+, detectou metadados dinâmicos no raw, emitiu zero valores
dinâmicos e verificou os cinco hashes originais. A proveniência separou H0 de
aquisição `01cc8408a83024663cc7cb7d434f82292072a945`, resultados originais
`f549a1a8d8e4b06028100b22a450fa0e5c46473b` e código corretivo H0-A1c.

As razões pós/pré das três quantidades mecânicas do split foram classificadas
como `CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF`. Sem documentação do provider
ou fonte independente, `VOLUME_UNIT_SEMANTICS` permanece
`UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION`.

O `PASS_READY_FOR_STAGE_A2_DECISIONS` original foi preservado e superseded para
revisão pela auditoria A1c. O corretivo encerrou com feasibility, remediação de
fronteira e proveniência em PASS, mas `SAFE_TO_RUN_LAF_STAGE_A2 = NO`. Nenhuma
feature, target, associação, estratégia ou backtest foi calculado; Validation e
Final OOS permaneceram fechados.

---

# 34. LAF_001 — freeze Research provider-invariant

Em 15/08/2026, a decisão humana final encerrou A1d como
`INCONCLUSIVE_TRANSPORT_NO_PAYLOAD`: H0-A1d
`74e53946e9e2fbd07dce15e77d527fd5cd0d1f38` e os dois receipts privados foram
preservados, nenhum payload/gate foi observado e nenhum retry adicional foi
autorizado. A1d não é PASS nem FAIL científico.

Foi aprovada a specification `v1.0-frozen` para testar se LAF agregado no
fechamento de `t` informa incrementalmente o TailLoss SPY em `t+1` além de RV.
A construção usa os cinco raws Yahoo imutáveis, retornos por Adj Close,
`Close*Volume` como proxy monetária consistente com o provider, z robusto com
252 sessões estritamente anteriores, embargo de janelas que atravessam o split
IWM, mediana diária de ao menos quatro ETFs e média única das últimas 21 sessões.

Antes de associação, mudanças positivas de escala `0.5`/`2.0` em Close e/ou
Volume pré-split deixaram `A_d` e `LAF_t` idênticos fora do embargo em tolerância
`1e-12`; mudança target-only deixou features exatamente iguais. Os cinco hashes
foram confirmados, nenhuma linha 2017+ foi carregada e Validation/Final OOS
permaneceram fechados.

A missingness literal produziu apenas 8 complete cases dos 156 target months,
zero em 2004–2010 e zero com estado Q80 classificável. Essa fragilidade foi
registrada antes de qualquer regressão e não motivou relaxamento de regra.
Bloco não estimável e contagem de estados insuficiente não podem passar os
gates congelados. H1-LAF
`cfbdff048ae8b0f7d9b8a1a804558bf59b656c1b` registrou o conteúdo científico; a
autorização metadata-only subsequente permite exatamente uma execução Research,
realizada uma vez a partir do commit
`842a87c2ca4ff7e65627f29d93726e9cae22c169`.

A amostra completa foi N `8`. No modelo completo, `beta_LAF` foi
`0.01620172883243451` (HAC SE `0.019928968505894328`, t
`0.8129737787303228`, p unilateral `0.22659457277469747`) e `beta_RV` foi
`-0.4511591592478728`. O R² ajustado completo (`-0.2816963209821848`) ficou
abaixo do RV-only (`-0.0837671317096973`). O bloco 2004–2010 permaneceu
inestimável; 2011–2016 teve beta LAF positivo. Nenhum complete case recebeu
estado Q80, logo a diferença high-minus-normal é indefinida.

Os quatro gates congelados foram falsos e o veredito literal foi `NO_GO`.
Nenhuma variante, resgate, Validation, Final OOS, estratégia ou backtest foi
executado.
