---
tags: [aprendizado, metodo]
atualizado: 2026-08-15
---

# Aprendizados Metodológicos

Volta para [[00 MOC - Desafio Quant AI 2026]].

O que este projeto ensinou, em ordem de importância. Serve para o relatório e para qualquer projeto quant futuro.

## 1. Reprodutibilidade não é validade

Duas implementações independentes chegaram ao mesmo `mean IC` de aproximadamente `0,05`. Isso foi comemorado como confirmação. Estava errado.

As duas reproduziram a **mesma especificação**, e a especificação media outra coisa. Reprodutibilidade verifica que o código faz o que o documento diz. Não verifica que o documento descreve o fenômeno pretendido.

> Reprodutibilidade é sobre o código. Validade de construct é sobre o significado.

## 2. Auditoria algébrica vem antes de auditoria empírica

Duas das cinco hipóteses morreram por identidade matemática, não por dados:

- `ER = N/(1+(N−1)ρ̄²)` mostrou que Effective Rank era uma reescrita da correlação
- `soma de ε = 0` na janela de estimação mostrou que o momentum 12−1 era reversão de 21 dias

Nos dois casos, semanas de trabalho empírico poderiam ter sido evitadas com uma verificação algébrica de dez minutos.

**Pergunta a fazer sempre, antes de rodar qualquer coisa:** esta métrica é algebricamente independente das que já tenho? A quantidade que estou somando tem alguma restrição imposta pelo estimador?

## 3. O comportamento da carteira denuncia o construct

O turnover era de 2 dos 3 nomes por mês, cerca de 67%. Um sinal de formação de doze meses não gira dois terços da carteira mensalmente.

O número estava visível desde o início e ninguém leu como sintoma. **Métricas operacionais são teste de sanidade do construct**, não apenas item de relatório.

## 4. OLS com intercepto zera os resíduos na janela

Consequência prática, específica e valiosa:

```
Se a janela de estimação == janela de formação, então
qualquer subsoma dos resíduos é o negativo do complemento.
```

Isso destrói silenciosamente qualquer sinal construído como soma parcial de resíduos in-sample. A correção é usar resíduos **point-in-time**: estimar em `[d−252, d−1]` e aplicar em `d`.

Checagem rápida: com resíduos in-sample, `|soma dos 252|` fica em `1e-16`. Com point-in-time, fica em `0,065`. Se der zero, tem problema.

## 5. Significância no research sample não prevê nada

`p = 0,0052` com 5.000 permutações no research. `p = 0,8980` no holdout.

O teste de permutação estava correto e bem construído. Ele mediu com precisão a significância de um padrão que não existia fora daquela amostra.

> Um p-valor pequeno na amostra em que a hipótese foi formulada mede a força do padrão observado, não a probabilidade de ele se repetir.

## 6. Custo mal calculado muda a conclusão

A primeira conta media só o giro da perna comprada e extrapolava. Subestimava pela metade.

| | errado | correto |
|---|---:|---:|
| custo | 1,63% a.a. | 3,30% a.a. |
| líquido | +3,91% | +2,23% |
| Sharpe | 0,36 | 0,21 |

A fórmula tem que estar escrita na especificação **em forma idêntica ao código**: `Cost_t = c · soma_i |w_it − w_i,t−1|`. Linguagem natural do tipo "10 bps por perna" admite três implementações diferentes.

## 7. Placebo tem que poder falhar

O `P3` original era "inverter o sinal e verificar que o IC inverte". Mas `ρ_Spearman(−x, y) = −ρ_Spearman(x, y)` por identidade. O teste devolvia o simétrico por construção e não podia falhar.

Um teste que não pode falhar não é evidência. Foi substituído pela ablação `A1`, que compara com a reversão sem residualizar e **pode** dar zero.

## 8. Congelar antes de abrir é o que dá valor ao holdout

O holdout só vale porque a especificação, o critério `GO/NO-GO` e os placebos foram commitados **antes** de qualquer número de 2019 a 2026 ser observado.

Se o critério fosse definido depois, o `NO-GO` poderia ter sido negociado. Como estava pré-registrado, o resultado foi mecânico e não houve espaço para interpretação conveniente.

## 9. Um holdout observado está queimado, mesmo que o resultado seja descartado

Quatro meses foram vistos numa rodada diagnóstica que depois foi jogada fora. Não importa: viraram quarentena permanente e o OOS limpo começou depois deles.

> Uma vez observado, não volta a ser holdout. Descartar o número não desfaz a observação.

## 10. Gates de ambiente e de artefato são parte do método

O checklist antes do freeze pegou, em sequência:

- 5 erros de conformidade no harness
- 1 divergência entre spec e código (`P3` versus `A1`)
- 1 timestamp inventado
- 1 caixa de aprovação não marcada, de 13

Nenhum era erro científico. Todos teriam entrado no commit que servia de carimbo. **O carimbo só vale se a árvore que ele carimba estiver correta.**

## 11. Determinismo é o que permite auditar

`seed = 7` fixa, dados versionados, specification congelada por hash. Isso torna a segunda execução idêntica à primeira, e é o que permite discutir com honestidade se vale reexecutar depois de um crash de persistência.

Sem determinismo, qualquer reexecução seria suspeita.

## 12. O caminho irreversível precisa de ensaio no trecho inteiro

O `--ensaio` exercitava métricas e critério, mas terminava antes do bloco de gravação, que só existia sob `--abrir-oos`. A linha `oos.drop(columns="long")` tinha ficado desatualizada numa refatoração e nunca foi executada por ninguém antes da rodada que não podia falhar.

O resultado: o veredito foi observado e os artefatos se perderam. Uma única execução autorizada na vida do experimento, e o trecho de persistência estreou nela.

> Se uma operação é irreversível, todo o caminho de código dela — inclusive escrita de arquivo — precisa ter rodado antes contra dados de mentira.

**Pergunta a fazer antes de qualquer gate:** qual linha do caminho irreversível nenhum ensaio executa?

## 13. Um registro que ninguém abriu não é um registro

Depois do crash, a saída de terminal foi declarada "preservada" em `reports/rsr_001_oos_terminal.txt`. O arquivo estava vazio. Ninguém abriu para conferir, e a afirmação circulou por uma devolutiva técnica e por duas notas antes de ser checada.

Custo: o resultado mais importante do projeto não tem artefato de máquina nenhum.

> Salvar não é verificar. Depois de gravar um registro crítico, ler de volta e conferir o tamanho.

## 14. Consistência interna resgata parte de um registro perdido

Sem os artefatos, o que sobrou foram números em prosa. Mas números reais de um experimento satisfazem identidades que números transcritos errados dificilmente satisfazem: contas de custo e líquido, médias ponderadas pelos tamanhos de bloco corretos, taxas caindo em `k/n` com `k` inteiro para dois `n` diferentes ao mesmo tempo, e p-valores caindo na grade `(1+k)/(N+1)` do estimador declarado.

Vinte verificações desse tipo passaram. Não substituem o artefato, e é importante dizer isso em voz alta — mas transformam "confie em nós" em "confira você mesmo".

## 15. O último estado do ciclo de vida é o menos testado

O `verify_research.py` exigia intervalo de validação para os status `OOS_OPENED` e `FINAL`. O `RSR_001` foi desenhado sem amostra de validação intermediária, o que estava declarado no manifesto desde a criação e aprovado antes do freeze. Consequência: **não havia status válido para o estado real do experimento** — os três caminhos possíveis davam erro.

O defeito só se manifesta no último estado, que é justamente o que nenhum experimento tinha alcançado. Os gates pré-freeze não podiam tê-lo pego: eles rodaram num estado anterior, onde a regra era satisfeita por acaso.

> Uma máquina de estados só está testada quando algum caso chegou ao estado terminal. Antes disso, os estados finais são código não exercitado.
