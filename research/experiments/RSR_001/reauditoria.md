# RSR_001 — Reauditoria dos artefatos congelados

**Escopo.** Reauditoria estática dos artefatos congelados por `H1`. Nenhuma
execução do modelo, nenhuma leitura de dado de mercado, nenhum parâmetro novo,
nenhuma reabertura do holdout. Tudo abaixo é derivado dos números já publicados
e do código congelado, por identidade algébrica ou por leitura.

**Conclusão.** Os números do `RSR_001` são internamente consistentes e o veredito
`NO-GO` se reproduz mecanicamente a partir deles. O que **não** está íntegro é o
registro de estado: quatro artefatos ainda descrevem o OOS como fechado, e o
arquivo apontado como registro primário da execução está vazio.

---

## 1. Consistência aritmética dos números publicados

Vinte verificações, todas derivadas das identidades da `spec.md`. Cada uma usa
apenas números já divulgados; nenhuma recalcula o sinal.

| # | identidade testada | research | final OOS |
|---|---|:---:|:---:|
| 1 | `custo = c · turnover · 12`, `c = 0,0010` | OK | OK |
| 2 | `líquido = bruto − custo` | OK | OK |
| 3 | `Sharpe = líquido / volatilidade` | OK | OK |
| 4 | média ponderada dos blocos de IC reproduz o `mean IC` | OK | OK |
| 5 | `hit rate` cai em `k/n` com `k` inteiro | OK | OK |
| 6 | `meses líquidos positivos` cai em `k/n` com `k` inteiro | OK | OK |
| 7 | `p` cai na grade `(1+k)/(N+1)`, `N = 5000` | OK | OK |

Detalhamento dos casos que mais restringem:

**Blocos → média.** O corte pré-registrado é `np.array_split` em três partes.
Para `n = 89` isso dá `30 / 30 / 29`, exatamente `1..30`, `31..60`, `61..89`
como escrito na `spec.md`. A média ponderada por esses tamanhos:

```
(30·(−0,0233) + 30·(−0,0422) + 29·(−0,0782)) / 89 = −0,04756   →  −0,0476   OK
(30·(−7,68)   + 30·(+1,27)   + 29·(−19,46))  / 89 = −8,502 %   →  −8,50 %   OK
```

Para `n = 213` o corte dá `71 / 71 / 71`, e `(0,0824 − 0,0012 + 0,1021)/3 =
0,0611`, igual ao `mean IC` do research. As duas séries de blocos são,
portanto, consistentes com as médias divulgadas e com os `n` declarados.

**Taxas.** `49,4 %` de `89` só é atingível com `44/89 = 49,44 %`. `54,5 %` de
`213` só com `116/213 = 54,46 %`. O mesmo vale para os meses líquidos positivos
(`41/89` e `112/213`). Taxas escritas à mão dificilmente cairiam sobre a grade
de inteiros dos dois `n` simultaneamente.

**p-valores.** Os quatro `p` caem exatamente sobre a grade `(1+k)/5001` do
estimador pré-registrado:

| p publicado | k implícito | `(1+k)/5001` |
|---|---:|---|
| `0,0052` research `P1` | 25 | 0,005199 |
| `0,0094` research `P2` | 46 | 0,009398 |
| `0,8980` OOS `P1` | 4490 | 0,898020 |
| `0,8530` OOS `P2` | 4265 | 0,853029 |

**Cobertura temporal.** `213 + 4 + 89 = 306` meses. As três fronteiras cobrem o
painel sem buraco e sem sobreposição.

## 2. Reavaliação do critério pré-registrado

O critério da `spec.md` foi reaplicado sobre os números publicados, sem tocar em
dados:

```
mean IC > 0                 −0,0476        FALHA
p_P1 < 0,10                  0,8980        FALHA
p_P2 < 0,10                  0,8530        FALHA
IC > 0 em ≥ 2 de 3 blocos     0 de 3       FALHA
                                           ScientificPass = False

R_net > 0                    −8,50 % a.a.  FALHA
R_net > 0 em ≥ 2 de 3         1 de 3       FALHA
                                           EconomicPass = False

VEREDITO -> NO-GO
```

Seis condições, seis falhas. O veredito não depende de julgamento: ele cai fora
do critério de forma mecânica, e nenhuma das seis está perto da fronteira.

## 3. Conformidade entre `spec.md` e `scripts/rsr_001.py`

Conferência linha a linha, por leitura. Nenhuma divergência material encontrada.

| item da specification | implementação | conforme |
|---|---|:---:|
| `W_d = {d−252, …, d−1}`, anterior a `d` | `rolling(252).cov(...).shift(1)` | sim |
| `S_t = {t−20, …, t}`, `S = 21` | `rolling(21).sum()` avaliado em `t` | sim |
| sinal `RSR = −Σ ε` | `sinal = -eps.rolling(s).sum()` | sim |
| pesos `+1/3`, `−1/3`, `0` | `w[lng]=+1/3`, `w[srt]=−1/3`, resto `0` | sim |
| `Cost_t = c·Σ|w_it − w_i,t−1|`, `w_{i,−1}=0` | `diff().abs().sum(axis=1)`, 1ª linha `= Σ|w|` | sim |
| retorno futuro sem look-ahead | `ret.loc[t:t_prox].iloc[1:]`, começa em `t+1` | sim |
| blocos `1..30`, `31..60`, `61..89` | `np.array_split(arange(89), 3)` → `30/30/29` | sim |
| `N = 5000`, `seed = 7`, unilateral | `N_PERM = 5000`, `SEMENTE = 7`, `p=(1+k)/(N+1)` | sim |
| quarentena `2018-11-30`–`2019-02-28` fora de tudo | `fatiar()` descarta o trecho central | sim |
| `A1` fora do gate de GO | `avaliar_criterio` não referencia `A1` | sim |

**Nota de código, sem efeito no resultado.** Em `painel()` o nome `w` é o
parâmetro da janela de estimação e é reatribuído dentro do laço como vetor de
pesos. A chamada que consome a janela (`residuos_pit(ret, mkt, w)`) acontece
antes do laço, e o vetor é reatribuído a cada iteração, então nenhum número muda
— inclusive nas variantes de robustez `W=126` e `W=504`. É sombreamento de nome,
não bug de cálculo. Registrado por completude; não foi corrigido, porque mexer
em arquivo congelado sem necessidade é pior do que a confusão de leitura.

## 4. Achados

### F1 — o registro primário da execução do OOS não existe · **crítico**

`reports/rsr_001_oos_terminal.txt` tem **1 byte** e nenhum conteúdo. A devolutiva
de 14/08 declara que a saída de terminal foi "preservada" nesse arquivo; ela não
foi. Somado ao crash de persistência, o resultado é que **nenhum artefato de
máquina do Final OOS existe no repositório**: não há os dois CSVs e não há a
transcrição do terminal.

A única fonte dos números é prosa — a devolutiva de 14/08 e as notas do vault.

O que a Seção 1 acrescenta a isso: os números não podem ser verificados contra
uma execução, mas **passam em vinte testes de consistência mútua** que uma
transcrição errada ou inventada teria altíssima chance de reprovar. Isso não
substitui o artefato; sustenta a transcrição como fiel.

Ação tomada: transcrever os números para `results.md` marcando a proveniência de
forma explícita, sem reexecutar. É a Opção B da devolutiva. Nenhum número foi
reconstruído, arredondado de novo ou completado por inferência.

### F2 — quatro artefatos afirmam que o OOS está fechado · **alto**

Estado encontrado, todos contradizendo o fato de que o OOS foi consumido:

| artefato | dizia |
|---|---|
| `manifest.toml` | `status = "FROZEN"`, `oos_opened = false`, `oos_opened_at = ""` |
| `results.md` | "Final OOS **não aberto**" e "Não executado" |
| `decision.md` | "Nem `GO`, nem `CONDITIONAL GO`, nem `NO-GO` foi decidido" |
| `experiment_registry.md` | `FROZEN`, OOS status `CLOSED` |

Corrigidos nesta reauditoria. O `decision.md` preserva íntegras as 13 aprovações
humanas: elas são o carimbo do freeze e não são reescritas.

### F3 — o harness não consegue representar o estado terminal deste desenho · **alto**

`verify_research.py` exigia intervalo de validação para os status `OOS_OPENED` e
`FINAL`. O `RSR_001` foi desenhado sem amostra de validação intermediária — vai
de research direto ao Final OOS, o que está declarado no `manifest.toml` desde a
criação e aprovado antes do freeze.

Consequência: **não havia status válido para o estado real do experimento.**

```
FINAL       + oos_opened=true  ->  "requires a validation date range"
OOS_OPENED  + oos_opened=true  ->  "requires a validation date range"
NO_GO       + oos_opened=true  ->  "requires OOS_OPENED or FINAL status"
```

O defeito só se manifesta no último estado do ciclo de vida, que é exatamente o
estado que nenhum experimento tinha alcançado antes. Os gates pré-freeze não
podiam tê-lo pego.

Correção aplicada, mínima: a exigência de intervalo de validação passa a valer
para `VALIDATION` e `VALIDATED`, que são estados **sobre** a validação, e deixa
de valer para `OOS_OPENED` e `FINAL`, que já exigem intervalo de OOS declarado
duas linhas acima. Teste adicionado cobrindo o desenho de duas etapas. A
`oos_policy.md` passa a registrar o desenho de duas etapas como admissível
quando declarado na specification e aprovado antes do freeze.

Nenhum parâmetro científico, fronteira, critério ou número foi tocado.

### F4 — `--ensaio` não cobre o caminho de persistência · **médio**

O crash `KeyError: "['long'] not found in axis"` em `scripts/rsr_001.py:310`
está confirmado por leitura: `painel()` produz `ic`, `spread`, `w_*`,
`turnover`, `custo` e `liquido`, e nenhuma coluna `long`. A referência ficou da
refatoração que trocou a coluna `long` pelas colunas de peso ao adotar
`Cost_t = c·Σ|dw|`.

O `--ensaio` exercita `metricas` e `avaliar_criterio`, mas termina antes do
bloco de gravação, que só existe sob `--abrir-oos`. O ensaio nunca poderia ter
pego o defeito. É lacuna real do gate: o caminho irreversível tinha um trecho
que nenhum ensaio executava.

A linha **não foi corrigida** nesta reauditoria. Corrigi-la só teria efeito se
acompanhada de reexecução, e reexecutar está fora do escopo autorizado.

### F5 — proveniência do `oos_opened_at` · **baixo, resolvido**

O horário exato da abertura não foi registrado por nenhum artefato. O único
carimbo disponível é o mtime de `reports/rsr_001_oos_terminal.txt`,
`2026-08-14T21:09:04-03:00`, criado manualmente logo após o crash.

Esse valor foi adotado **com a proveniência escrita no manifesto**, pelo mesmo
método já usado no `created_at`. Não foi inventado nem arredondado: é o mtime de
um arquivo real, e o manifesto diz exatamente isso. A alternativa — escolher um
horário plausível — é o erro que os gates pré-freeze já pegaram uma vez.

## 5. O que esta reauditoria não pode afirmar

- Não prova que a execução ocorreu. Prova que os números publicados são mutuamente
  consistentes e que o veredito decorre deles.
- Não substitui os CSVs perdidos. `rsr_001_oos_bruto.csv` e
  `rsr_001_veredito.csv` continuam não existindo.
- Não reexaminou a série de preços nem o alinhamento de calendário. Isso exigiria
  execução.

## 6. Situação final

`RSR_001` encerrado como `NO-GO` fora da amostra. Estado do repositório agora
coerente com o fato. As proibições pós-OOS da `spec.md` seguem valendo: `S = 42`,
outra janela, outro custo, outro universo, outro critério e reinterpretação de
direção do sinal continuam vedados, e nenhum deles foi invocado aqui.
