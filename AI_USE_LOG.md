# AI Use Log

Registre somente contribuições materiais de GenAI que sejam relevantes para auditoria ou relatório final. Cada entrada deve distinguir contribuição da IA, decisão humana e verificação independente.

## 2026-08-12 — Research harness restructuring

- **Date:** 2026-08-12
- **Tool/model:** OpenAI Codex / GPT-5
- **Task:** Reestruturar o repositório como research harness quantitativo.
- **AI contribution:** Inspeção orientada dos contratos do projeto e dos padrões do LLMQuant/quant-mind; adaptação de context routing, governança de OOS, registry, artefato de experimento e verificações determinísticas.
- **Human decision:** O usuário definiu escopo, arquitetura-alvo, limites científicos e proibição de implementar ou abrir amostras Cross-Market/OOS.
- **Verification:** Revisão das quatro fontes canônicas; `verify_research.py`; testes automatizados; revisão de Git diff.
- **Impact on project:** Organização e proteção do processo de research; nenhuma hipótese, parâmetro, amostra ou resultado financeiro foi alterado.
- **External reference:** LLMQuant/quant-mind commit `638d16a4491581f7d8e9a8b9cff7db3962c87a24`; padrões foram adaptados, sem dependência ou cópia literal não trivial.

## 2026-08-14 — Auditoria de construct do Residual Momentum

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex / GPT-5
- **Task:** Responder se o sinal `RMOM 12−1` mede o que a specification diz medir.
- **AI contribution:** Derivou a identidade de OLS com intercepto — `Σε = 0` na janela de estimação — e mostrou que, sendo a janela de estimação idêntica à de formação, `Σ_{F_t} ε = −Σ_{S_t} ε`. O sinal chamado de momentum de doze meses era o negativo dos resíduos do mês excluído.
- **Human decision:** Encerrar `RM_001` como `NO-GO de construct`, recusar qualquer reinterpretação do resultado anterior e reformular a hipótese como reversão residual de curto prazo, com resíduos point-in-time.
- **Verification:** Checagem numérica independente: `max |Σ dos 252 resíduos| = 4,337e−16`, `max |RMOM − (−Σ dos últimos 21)| = 4,718e−16`, correlação `1,0000000000`, contra escala típica de sinal de `0,0226`. Reconstrução point-in-time dá `mean IC = −0,0011`.
- **Impact on project:** Derrubou o único achado positivo do grupo, obtido por duas implementações independentes. Estabeleceu que reprodutibilidade não é validade de construct.
- **Limitation observed:** A IA havia participado da construção e da reprodução desse mesmo sinal sem apontar a identidade. Ela só a identificou quando foi explicitamente questionada sobre validade de construct. Mesmo padrão do Effective Rank, onde a redundância algébrica também só apareceu sob pergunta direta.

## 2026-08-14 — Desenho do teste pré-registrado e abertura do OOS

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex / GPT-5; Anthropic Claude
- **Task:** Desenhar placebos e critério de decisão falsificáveis para `RSR_001`, auditar a specification antes do freeze e conduzir os gates.
- **AI contribution:** Placebos `P1` e `P2`, ablação `A1`, critério `ScientificPass`/`EconomicPass` com regra de 2 de 3 blocos. Auditoria da fórmula de custo, que estava subestimada pela metade. Auditoria pré-freeze: 5 erros de conformidade do harness, 1 divergência entre spec e código (`P3` versus `A1`), 1 timestamp inventado e 1 caixa de aprovação não marcada de 13.
- **Human decision:** As 13 aprovações registradas em `research/experiments/RSR_001/decision.md`, o freeze por `H1` e a autorização de abertura única do OOS. Recusa explícita de promover `S = 42` a primary.
- **Verification:** `verify_research.py` e `pytest tests/` verdes antes da abertura; `--ensaio` exercitou o caminho do critério sobre o research sample; árvore limpa no momento da abertura.
- **Impact on project:** O `P3` original — inverter o sinal e verificar que o IC inverte — foi descartado por ser identidade (`ρ(−x, y) = −ρ(x, y)`) e portanto incapaz de falhar. Substituído por `A1`. O OOS deu `NO-GO`, e o critério pré-registrado tornou a decisão mecânica.
- **Limitation observed:** A auditoria assistida cobriu spec, conformidade e ciência, mas não cobriu o caminho de escrita de arquivos. O script quebrou na persistência (`scripts/rsr_001.py:310`) depois de imprimir o veredito, e o `--ensaio` não exercitava esse trecho. Nenhuma das revisões — humanas ou assistidas — leu o gate perguntando "qual linha do caminho irreversível nunca é executada em ensaio?".

## 2026-08-15 — Reauditoria estática dos artefatos congelados

- **Date:** 2026-08-15
- **Tool/model:** Anthropic Claude
- **Task:** Reauditar os artefatos congelados do `RSR_001` sem reexecução e sem parâmetros novos, e reconciliar o estado do repositório com o veredito.
- **AI contribution:** Vinte verificações de consistência mútua sobre os números publicados (identidades de custo, líquido, Sharpe, médias ponderadas por bloco, grade de inteiros das taxas e grade `(1+k)/(N+1)` dos p-valores); conferência linha a linha entre `spec.md` e `scripts/rsr_001.py`; identificação de que o arquivo apontado como registro primário do OOS está vazio e de que o verificador não conseguia representar o estado terminal deste desenho.
- **Human decision:** Adotar a Opção B — transcrever os números sem reexecutar —, aceitar o mtime como proveniência declarada do `oos_opened_at` e autorizar a correção mínima do verificador.
- **Verification:** `verify_research.py` e `pytest tests/` verdes após as alterações, com dois testes novos cobrindo o desenho de duas etapas. Registro completo em `research/experiments/RSR_001/reauditoria.md`.
- **Impact on project:** Quatro artefatos que ainda declaravam o OOS fechado foram corrigidos. Nenhum parâmetro, fronteira, critério ou número foi alterado.
- **Limitation observed:** A reauditoria não pode provar que a execução ocorreu, apenas que os números são mutuamente consistentes e que o veredito decorre deles. Os dois CSVs perdidos continuam inexistentes, e nenhuma verificação estática recupera um artefato que nunca foi gravado.
