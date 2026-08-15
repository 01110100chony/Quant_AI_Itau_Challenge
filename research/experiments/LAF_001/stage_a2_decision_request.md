# LAF_001 — Stage A2 human decision request

> **Superseded on 2026-08-15:** the final human Research order resolved these
> construction/model decisions through `v1.0-frozen`. This historical request
> is preserved; it no longer blocks the single authorized Research execution.
> Validation, Final OOS, strategy and portfolio remain closed.

Stage A1 produced the literal structural verdict
`PASS_READY_FOR_STAGE_A2_DECISIONS`, now preserved but superseded for review by
the independent Stage A1c corrective audit. Stage A1c passed boundary and
provenance remediation, but recorded
`VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION` and
`SAFE_TO_RUN_LAF_STAGE_A2 = NO`.

Stage A2 remains prohibited until humans decide all items below and issue a
separate execution order. Stage A1c does not supply that order.

1. Is Yahoo Finance Chart API the final source or only a candidate source?
2. Is a secondary provider required, and if so, which provider?
3. What is the policy for an absent expected session?
4. What is the policy for null or zero Volume?
5. What provider documentation or independent source, if any, is approved to
   decide historical Volume-unit semantics?
6. What exact adjusted-return policy may be used?
7. How must splits and distributions be treated?
8. Must all five ETFs be structurally complete, or is a lower minimum allowed?
9. Is XNYS approved for every ETF in the basket?
10. Is feature-side LAF construction authorized after these decisions are frozen?
11. What is the exact rule for a daily return equal to zero?
12. What is the exact rule when MAD equals zero?

Still outside this request: target construction, feature–target association,
Stage B, Validation, Final OOS, statistical gates, portfolio rules, cash,
costs, slippage, strategy and backtest.
