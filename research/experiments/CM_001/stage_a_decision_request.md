# CM_001 — Stage A decision request

Stage A has the technical verdict `PASS_READY_FOR_SPEC_FREEZE`. This does not approve or freeze the candidates below. Before any Stage B freeze, researchers must decide:

| Decision | Candidate | Structural evidence | Codex recommendation |
|---|---|---|---|
| Multi-provider | Yahoo immutable JSON for `XSD/QQQ/SPY`; official TWSE for `0052/TAIEX/0050` | US coverage complete/XNYS-aligned; Taiwan official OHLC and actions cross-checked | APPROVE |
| `0052` `"--"` | retain ledger; exclude when required OHLC is absent; never impute | 102 no-trade plus 6 odd-lot-only/no-regular-trade; 15/15 official sample cross-check; zero unresolved | APPROVE |
| Primary price basis | raw OHLC; adjusted close only for audit/reference | no adjusted Open; no raw-Open/adjusted-Close mix; Yahoo Taiwan scale hazard | APPROVE |
| Corporate actions | exclude confirmed H1/PrevTWRel crossings; do not automatically exclude H2 | 6 `0052` distributions confirmed by two official endpoints; affected sessions mapped; no Research split | APPROVE |
| Calendar/timezone | XNYS actual sessions; official TWSE dates plus 09:00–13:30 `Asia/Taipei` | US venues coincide; 15 XTAI omissions retained; one XTAI extra excluded; no material hour exception | APPROVE |
| Research sample | `2010-01-01`–`2018-12-31` | no post-2018 market data persisted or processed in closure artifacts | APPROVE |

Full evidence is in [`stage_a_final_data_policy_evidence.md`](stage_a_final_data_policy_evidence.md), with the missing, corporate-action and attrition audits beside it. Estimator, inference, HAC/Newey-West, placebos and GO/CONDITIONAL GO/NO-GO criteria remain untouched and TBD. `CM_001` remains `DRAFT`; Stage B, Validation and Final OOS remain closed.
