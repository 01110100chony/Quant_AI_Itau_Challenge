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
