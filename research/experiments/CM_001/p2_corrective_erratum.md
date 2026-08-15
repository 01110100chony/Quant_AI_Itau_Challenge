# CM_001 — P2 corrective-freeze erratum

## Status

- Corrective authorization: `CORRECTIVE FREEZE H1c/H2c AUTHORIZED`.
- Corrected version: `v1.0.1-frozen`.
- Stage B association executions before correction: zero.
- Execution receipt before correction: absent.
- Results directory before correction: absent.
- Corrective H1c: `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.
- Corrective H2c: `694edf0d745c044cbfa9c257c44719bc0cd9f4ea`; it records H1c exactly.

## Root cause

H1 `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818` implemented the P2 lead with `shift(-1)` after constructing the H2 target-complete sample. If an eligible future information window had missing H2 target inputs, that implementation skipped its feature and selected a later eligible window. This contradicted the already-frozen P2 semantics.

H2 `3cebbb0c54bea8b6023eb7e716de53d98402eeb9` only registered H1 provenance. Both commits remain immutable and are superseded only for the P2 executable, before any Stage B association.

## Canonical correction

The corrected implementation first creates the chronological table of eligible Taiwan information windows using only window eligibility and US feature-component availability. It maps each eligible window to the immediately following eligible window and its `SemiSpecific`, before any current/future target filter. Only then does it join the current H2 sample and apply common completeness.

Therefore:

- an eligible future window with missing target remains the correct lead;
- an empty-US-window session is skipped;
- the final eligible window has no lead and drops at common-complete;
- every retained `future_window_date` is strictly later than `target_session`;
- correctly aligned and future H2 fits use exactly the same sessions.

No hypothesis, feature, target, estimator, HAC option, threshold, block, robustness, provider policy, sample boundary or primary count changed.

## Mechanical evidence

Using session dates and availability flags only:

- eligible information windows: `2137`;
- H2 current-complete sessions: `2034`;
- P2 common-complete sessions: `2033`;
- final eligible window without successor: `1`.

No beta, p-value, correlation or other feature–target association was computed for this erratum.

After H2c and all corrective gates passed, Stage B executed once on Research and returned the frozen verdict `NO_GO`. This later result does not alter the pre-empirical nature of the correction.
