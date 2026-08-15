# LAF_001 — Stage A2 human decision request

Stage A1 produced the literal structural verdict
`PASS_READY_FOR_STAGE_A2_DECISIONS`. Stage A2 remains prohibited until humans
decide all items below and issue a separate execution order.

1. Is Yahoo Finance Chart API the final source or only a candidate source?
2. Is a secondary provider required, and if so, which provider?
3. What is the policy for an absent expected session?
4. What is the policy for null or zero Volume?
5. What exact adjusted-return policy may be used?
6. How must splits and distributions be treated?
7. Must all five ETFs be structurally complete, or is a lower minimum allowed?
8. Is XNYS approved for every ETF in the basket?
9. Is feature-side LAF construction authorized after these decisions are frozen?
10. What is the exact rule for a daily return equal to zero?
11. What is the exact rule when MAD equals zero?

Still outside this request: target construction, feature–target association,
Stage B, Validation, Final OOS, statistical gates, portfolio rules, cash,
costs, slippage, strategy and backtest.
