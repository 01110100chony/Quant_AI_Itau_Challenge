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

## 2026-08-14 — CM_001 pre-Stage A specification synchronization

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Documentation/specification synchronization before data feasibility.
- **AI contribution:** Applied human-approved definitions for targets, empty-window handling and Stage A/Stage B governance across the research harness.
- **Human decision:** Definitions were supplied explicitly by the researchers; no model selected the universe, targets, controls, samples or gates.
- **Verification:** Canonical-document review; `verify_research.py`; existing automated tests; `git diff --check`; Git diff review.
- **Impact on project:** Removed ambiguities before any market data/result inspection. No data, research sample, validation, final OOS, notebook or empirical result was opened.

## 2026-08-14 — CM_001 Stage A acquisition recovery and provider audit

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Recover and audit the CM_001 acquisition/provider layer and complete Data & Timing Feasibility only.
- **AI contribution:** Diagnosed the locale-induced CSV parsing failure; separated immutable HTTP raw responses, schema gates, parsing, OHLC validation and canonical Stage A artifacts; audited Yahoo/TWSE sources, calendars, mappings and corporate-action provenance; added synthetic and real invariants.
- **Human decision:** Researchers explicitly revised Research start from `2007-01-01` to `2010-01-01` based only on pre-result data availability/integrity. Assets, hypotheses, targets, Validation/OOS and Stage B restrictions were unchanged.
- **Verification:** Raw-array audits before DataFrame construction; official-source cross-checks; project unit tests; `verify_research.py`; `git diff --check`; Git diff review.
- **Impact on project:** Removed false empty-window diagnostics caused by parsing, produced a structural `DECISION_REQUIRED` Stage A verdict and preserved Validation/OOS closure. No feature–target or economic result was calculated.

## 2026-08-14 — CM_001 Stage A closure audit

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Resolve the remaining `0052` no-OHLC, corporate-action, attrition, raw/adjusted and calendar-policy evidence for Stage A closure.
- **AI contribution:** Acquired bounded official TWSE evidence; classified all 108 no-OHLC sessions from same-day trading fields; cross-checked a pre-specified date sample and the corporate-action master; mapped mechanically affected legs; quantified input attrition; audited raw/adjusted separation and US/Taiwan calendars; generated reproducible reports and tests.
- **Human decision:** The user fixed the universe, hypotheses, targets, sample and prohibited any feature–target analysis; the resulting policy recommendations remain non-binding pending an explicit human freeze decision.
- **Verification:** Official-source endpoint cross-checks; structural invariants and manual cases; full unit-test runner; `verify_research.py`; `git diff --check`; Git diff review.
- **Impact on project:** Produced `PASS_READY_FOR_SPEC_FREEZE` as a data/timing closure verdict while preserving `CM_001 = DRAFT`, Stage B unauthorized and Validation/Final OOS closed. No return, target, feature value or feature–target relationship was calculated.

## 2026-08-14 — CM_001 scientific freeze implementation

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Materialize the human-approved `v1.0-frozen` specification and deterministic Stage B implementation before any association execution.
- **AI contribution:** Synchronized the literal data/timing/model/falsification/gate decisions; implemented Research-boundary guards, OLS/HAC(5), fixed placebos, diagnostics, one-time execution receipt and synthetic tests.
- **Human decision:** Researchers explicitly selected every material scientific field, final sample boundary and decision threshold, and authorized the H0/H1/H2/result commit sequence.
- **Verification:** Synthetic-only Stage B unit tests; mechanical-count preflight without prices; full unit suite; `verify_research.py`; `git diff --check`; explicit staged-path review.
- **Impact on project:** Prepared a reproducible scientific freeze at H1 `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818` without inspecting any feature–target association before H1/H2. Validation and Final OOS remained closed.

## 2026-08-14 — CM_001 P2 corrective freeze

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Align the frozen P2 executable with the already-approved next-eligible-window semantics.
- **AI contribution:** Detected that the original executable shifted after H2 target filtering; stopped before execution; implemented pre-target eligible-window mapping, mechanical common-N audit and six synthetic edge-case tests.
- **Human decision:** Researchers rejected “next H2-complete session,” preserved P2 semantics unchanged and explicitly authorized `v1.0.1-frozen` H1c/H2c.
- **Verification:** Synthetic fixtures, full unit suite, mechanical preflight, harness verifier, boundary checks and scoped Git diff.
- **Impact on project:** Corrected a pre-empirical implementation mismatch at H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6` without inspecting any feature–target relationship. H0/H1/H2 lineage, all scientific choices and closed holdouts were preserved.

## 2026-08-14 — CM_001 frozen Stage B execution

- **Date:** 2026-08-14
- **Tool/model:** OpenAI Codex
- **Task:** Execute the corrected frozen CM_001 Research tests exactly once and apply literal gates.
- **AI contribution:** Ran the registered OLS/HAC models, P1/P2, fixed blocks and secondary diagnostics; persisted machine-readable results, provenance, receipt, tables and figures; applied gates without discretionary override.
- **Human decision:** Researchers pre-specified all models, samples, diagnostics and gates and explicitly authorized the one-time Research execution after H1c/H2c.
- **Verification:** Receipt and hashes; strict-future P2 mapping audit; counts; full unit suite; harness verifier; boundary assertions; Git diff review.
- **Impact on project:** `CorePass=false` produced the frozen verdict `NO_GO`. No optimization, Validation, Final OOS, strategy or backtest followed.

## 2026-08-15 — CM closure synchronization and LAF_001 Stage A1 draft

- **Date:** 2026-08-15
- **Tool/model:** OpenAI Codex
- **Task:** Synchronize the definitive CM_001 closure and register the minimum documentary DRAFT for LAF_001 Stage A1 preparation.
- **AI contribution:** Reconciled stale CM labels; created the self-contained LAF_001 DRAFT specification, manifest, empty result/decision records and future Stage A1 audit plan; preserved unresolved material choices as explicit `TBD` fields.
- **Human decision:** Researchers explicitly authorized LAF_001 documentary preparation and fixed the candidate universe, target asset, warm-up, Research boundary, closed period, candidate source, field separation, calendar and decision/execution timing. They explicitly prohibited market-data acquisition, calculations, feature–target association, holdout definition/opening, strategy and backtest.
- **Verification:** Virtualenv harness verifier; full unit suite; `git diff --check`; scoped diff and path audits for data, CM results and AGENTS.md.
- **Impact on project:** LAF_001 is registered as `v0.1-draft` with sample inspected `NONE`. No market data or empirical result was created, and no thesis was promoted or frozen.

## 2026-08-15 — LAF_001 Stage A1 structural data feasibility

- **Date:** 2026-08-15
- **Tool/model:** OpenAI Codex
- **Task:** Implement and execute the explicitly bounded LAF_001 Stage A1 structural acquisition and data/timing audit.
- **AI contribution:** Implemented the direct Yahoo Chart API collector, immutable raw receipts/hashes, strict boundary/parser gates, XNYS coverage, OHLCV/schema/timestamp/corporate-action audits and synthetic tests; detected and corrected a deterministic `exchange-calendars` default-window defect before accepting coverage results.
- **Human decision:** Researchers fixed the symbols, period, endpoint contract, candidate calendar, allowed outputs and hard stops, and prohibited returns/features/targets, associations, holdouts, strategy and backtest. Source/policy/Stage A2 choices remain human decisions.
- **Verification:** Five independent raw SHA-256 checks; synthetic boundary and integrity cases; full unit suite; research harness verifier; calendar regression; artifact and Git diff review.
- **Impact on project:** Stage A1 recorded `PASS_READY_FOR_STAGE_A2_DECISIONS` from structural evidence only. No raw request was repeated, no provider value was repaired, no date from 2017 onward was observed, and no return, LAF, target or predictive result was calculated.
- **Corrective note:** “No date from 2017 onward” referred only to dated
  historical rows/actions. Dynamic 2026 metadata was present and materialized;
  the following Stage A1c entry records its disclosure and remediation.

## 2026-08-15 — LAF_001 Stage A1c corrective audit

- **Date:** 2026-08-15
- **Tool/model:** OpenAI Codex
- **Task:** Remediate the Stage A1 metadata-boundary incident, make audit-code provenance exact and execute the limited IWM event-only unit audit.
- **AI contribution:** Implemented the metadata whitelist and field-name-only boundary audit; separated acquisition, original-result and corrective-code commits; added synthetic boundary/sentinel/window tests; regenerated corrective artifacts from unchanged raws; mechanically summarized the 41 authorized split sessions; synchronized the erratum and research records.
- **Human decision:** Researchers explicitly limited the correction, fixed the metadata whitelist, provenance roles, split date/window/calculations/classifications, prohibited all Stage A2/feature/target/strategy work and required exactly two local commits without push.
- **Verification:** Five independent SHA-256 checks; 27 LAF synthetic tests; full unit suite; manual split-row calculations; CSV/JSON schema and boundary audits; research harness verifier; `git diff --check`; scoped Git review.
- **Impact on project:** The original result remains preserved but is superseded for review by Stage A1c. Boundary and provenance remediation passed; Volume-unit semantics remains unresolved; Stage A2, Validation, Final OOS, strategy and backtest remain closed.

## 2026-08-15 — LAF_001 provider-invariant Research freeze

- **Date:** 2026-08-15
- **Tool/model:** OpenAI Codex
- **Task:** Materialize the human-approved LAF_001 Research specification and falsification checks before association.
- **AI contribution:** Implemented point-in-time robust normalization, split-regime embargo, unique LAF/RV aggregation, adjusted TailLoss, HAC(3) estimator, prospective gates, one-shot execution guard and real/synthetic invariance/target-independence tests; surfaced severe mechanical attrition before regression.
- **Human decision:** Researchers fixed every material field, sample, timestamp, formula, missingness rule, split protection, model, threshold and verdict, closed Tiingo/A1d without a scientific result and prohibited variants, holdouts, portfolio and backtest.
- **Verification:** Five immutable Yahoo hashes; XNYS boundary; scale factors `0.5` and `2.0`; target-only mutation; synthetic manual cases; LAF/full tests; harness verifier; Git diff review.
- **Impact on project:** Prepared `v1.0-frozen` without observing a feature-target association. Only 8 complete Research months remain under the literal rules; no rule was relaxed, and Validation/Final OOS remain closed.

## 2026-08-15 — LAF_001 frozen Research execution

- **Date:** 2026-08-15
- **Tool/model:** OpenAI Codex
- **Task:** Execute the human-authorized frozen LAF_001 Research association exactly once and apply its literal prospective gates.
- **AI contribution:** Ran the registered full and RV-only OLS/HAC(3) models, fixed stability blocks and expanding prior-only Q80 state diagnostic; persisted the receipt, provenance, tables and the informative coefficient figure; synchronized the literal result without a variant.
- **Human decision:** Researchers fixed all inputs, formulas, sample boundaries, controls, inference, gates and verdict logic; explicitly authorized the one execution while keeping Validation and Final OOS closed.
- **Verification:** H1/auth commits, immutable hashes, one-shot receipt, scale invariance, target independence, no-2017 boundary, tests, harness verifier and scoped Git review.
- **Impact on project:** All four gates failed and the frozen verdict is `NO_GO`. No optimization, holdout, strategy, portfolio or backtest followed.
