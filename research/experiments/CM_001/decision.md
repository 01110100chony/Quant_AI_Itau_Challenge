# CM_001 — Decision

## Corrected frozen state

`NO_GO`. Human authorization preserved every `v1.0-frozen` scientific choice and authorized only the pre-empirical P2 implementation correction documented in [`p2_corrective_erratum.md`](p2_corrective_erratum.md), producing `v1.0.1-frozen`.

H1 `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818` and H2 `3cebbb0c54bea8b6023eb7e716de53d98402eeb9` remain immutable and are superseded only for the P2 executable. H1c is `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`; H2c `694edf0d745c044cbfa9c257c44719bc0cd9f4ea` records it exactly. Corrected Stage B executed once on Research and returned `NO_GO`. Validation and Final OOS remain CLOSED.

## Stage A closure

Stage A verdict is `PASS_READY_FOR_SPEC_FREEZE`. The reviewed H0 baseline commit is `78d9f6edca157cfcbd8643f52a9667d3a85c5fd0`. It contains structural evidence only and no feature–target association.

Human-approved policies:

- Yahoo immutable JSON for `XSD/QQQ/SPY`; TWSE official for Taiwan instruments, sessions and actions.
- retain 2,223 Taiwan sessions; exclude unavailable required OHLC; never impute;
- raw OHLC primary, adjusted Close audit only, never mixed raw/adjusted legs;
- leg-specific corporate-action exclusions frozen in the canonical specification;
- XNYS actual sessions and official TWSE dates/times;
- Research 2010–2018, Validation 2019–2022 CLOSED, Final OOS 2023–2025 CLOSED, 2026 excluded.

## Frozen Stage B decision rule

The exact models, HAC inference, P1/P2, blocks, secondary diagnostics and gates are in [`spec.md`](spec.md). `CorePass` depends only on primary H2. GO requires all gates; CONDITIONAL_GO requires CorePass with at least one failed support gate; NO_GO follows whenever CorePass fails. No secondary result can rescue H2.

## Research verdict

`CorePass=false`, `RobustnessPass=false`, `SpecificityPass=false`, `TimingPass=true`. Under the frozen rule, `CorePass=false` implies `NO_GO`. No secondary result was used to rescue H2. CM_001 stops here without optimization, Validation or Final OOS access.
