# Diagnostic execution erratum — research warm-up counts

Classification: `POST_OOS_EXPLORATORY_EXECUTION_ERRATUM`

The frozen diagnostic specification correctly fixes the specification-compliant
seen OOS at `n=88`, but incorrectly states that every robustness variant has
`n=213` in research. That is impossible with the frozen snapshot because longer
estimation/signal windows have additional warm-up loss.

The first surface attempt stopped on this count assertion after completing
in-memory calculations for 10 of 18 signal specifications. No numerical result
was printed or persisted. The diagnostic specification, grid, OOS sample,
timing, universe, proxies, costs, and thresholds remain unchanged. The original
specification file and its SHA-256 are preserved.

The mechanical counts, audited before restarting, are:

| W | S | Research n | First research feature | Seen OOS n |
|---:|---:|---:|---|---:|
| 126 | 10 | 213 | 2001-02-28 | 88 |
| 126 | 21 | 213 | 2001-02-28 | 88 |
| 126 | 42 | 213 | 2001-02-28 | 88 |
| 252 | 10 | 213 | 2001-02-28 | 88 |
| 252 | 21 | 213 | 2001-02-28 | 88 |
| 252 | 42 | 212 | 2001-03-30 | 88 |
| 504 | 10 | 202 | 2002-01-31 | 88 |
| 504 | 21 | 201 | 2002-02-28 | 88 |
| 504 | 42 | 200 | 2002-03-28 | 88 |

Each proxy has the same count for a given W/S pair. Research metrics use every
mechanically available observation inside the frozen research calendar
boundary; the output reports `n` for every row. Holm comparison in research is
therefore descriptive across unequal warm-up samples. Seen-OOS and its three
blocks remain exactly comparable at 88 / 30 / 30 / 28 observations.

This erratum does not select a parameter and cannot rescue `RSR_001`.

