# RSR_001 post-OOS parameter surface

`POST_OOS_EXPLORATORY — NOT VALIDATION — CANNOT RESCUE RSR_001`

Diagnostic spec SHA-256: `c5904eb5c719d105d47e4f1d71c698dcad9376ceb6358fd1aceffc7abc62bf53`

Frozen data SHA-256: `30bf7c3e6834e4eae29731be64d186d500826f9751c26fbf54c83b2856e8b177`

## Scope

All 18 frozen signal specifications and all 54 economic combinations were run.
The full table, including research, seen OOS, three fixed OOS blocks, nominal
and Holm p-values, costs, volatility, Sharpe, both drawdowns, turnover, and
secondary compounded returns, is `parameter_surface.csv`.

No row is a validation result. No row can change `RSR_001 = NO_GO`.

Research `n` varies mechanically from 200 to 213 because W/S warm-up differs;
the exact counts and the aborted first-run disclosure are recorded in
`diagnostic_execution_erratum.md`. Seen OOS remains fixed at `n=88` for every
specification.

## Complete signal surface

| W | S | Proxy | Research IC | Seen OOS IC | P1 nominal/Holm | P2 nominal/Holm | OOS blocks IC | Stability |
|---:|---:|---|---:|---:|---:|---:|---|---|
| 126 | 10 | SPY | 0.0413 | -0.0487 | 0.9038/1.0000 | 0.8346/1.0000 | -0.0733/-0.0544/-0.0161 | ALL_NONPOSITIVE |
| 126 | 10 | EQUAL_WEIGHT_9 | 0.0339 | -0.0386 | 0.8498/1.0000 | 0.7792/1.0000 | -0.0794/-0.0339/0.0000 | MIXED |
| 126 | 21 | SPY | 0.0334 | -0.0326 | 0.8064/1.0000 | 0.7532/1.0000 | 0.0367/-0.0383/-0.1006 | MIXED |
| 126 | 21 | EQUAL_WEIGHT_9 | 0.0336 | -0.0392 | 0.8534/1.0000 | 0.7942/1.0000 | 0.0322/-0.0122/-0.1446 | MIXED |
| 126 | 42 | SPY | 0.0750 | 0.0241 | 0.2647/1.0000 | 0.2615/1.0000 | 0.0500/0.0222/-0.0018 | MIXED |
| 126 | 42 | EQUAL_WEIGHT_9 | 0.0689 | 0.0216 | 0.2885/1.0000 | 0.3041/1.0000 | 0.0589/0.0161/-0.0125 | MIXED |
| 252 | 10 | SPY | 0.0405 | -0.0576 | 0.9344/1.0000 | 0.8812/1.0000 | -0.1039/-0.0589/-0.0065 | ALL_NONPOSITIVE |
| 252 | 10 | EQUAL_WEIGHT_9 | 0.0388 | -0.0455 | 0.8918/1.0000 | 0.8194/1.0000 | -0.1000/-0.0411/0.0083 | MIXED |
| 252 | 21 | SPY | 0.0611 | -0.0530 | 0.9220/1.0000 | 0.8776/1.0000 | -0.0233/-0.0422/-0.0964 | ALL_NONPOSITIVE |
| 252 | 21 | EQUAL_WEIGHT_9 | 0.0653 | -0.0509 | 0.9090/1.0000 | 0.8634/1.0000 | 0.0072/-0.0561/-0.1077 | MIXED |
| 252 | 42 | SPY | 0.0858 | 0.0095 | 0.4113/1.0000 | 0.3743/1.0000 | 0.0144/0.0094/0.0042 | ALL_POSITIVE |
| 252 | 42 | EQUAL_WEIGHT_9 | 0.0800 | 0.0117 | 0.3835/1.0000 | 0.3605/1.0000 | 0.0217/0.0156/-0.0030 | MIXED |
| 504 | 10 | SPY | 0.0253 | -0.0422 | 0.8714/1.0000 | 0.7820/1.0000 | -0.0789/-0.0356/-0.0101 | ALL_NONPOSITIVE |
| 504 | 10 | EQUAL_WEIGHT_9 | 0.0216 | -0.0633 | 0.9532/1.0000 | 0.9068/1.0000 | -0.0856/-0.0850/-0.0161 | ALL_NONPOSITIVE |
| 504 | 21 | SPY | 0.0378 | -0.0456 | 0.8898/1.0000 | 0.8414/1.0000 | -0.0100/-0.0350/-0.0952 | ALL_NONPOSITIVE |
| 504 | 21 | EQUAL_WEIGHT_9 | 0.0358 | -0.0563 | 0.9370/1.0000 | 0.8926/1.0000 | -0.0211/-0.0428/-0.1083 | ALL_NONPOSITIVE |
| 504 | 42 | SPY | 0.0674 | -0.0068 | 0.5843/1.0000 | 0.5299/1.0000 | -0.0067/0.0206/-0.0363 | MIXED |
| 504 | 42 | EQUAL_WEIGHT_9 | 0.0669 | -0.0076 | 0.5883/1.0000 | 0.5237/1.0000 | 0.0094/-0.0167/-0.0161 | MIXED |

## Family-level diagnostics

- Seen-OOS Holm P1 values below 0.10: `0` of 18.
- Seen-OOS Holm P2 values below 0.10: `0` of 18.
- Specifications with positive IC in all three OOS blocks: `1` of 18.
- Row-level W monotonicity flags marked non-monotonic: `6` of 18.
- Row-level S monotonicity flags marked non-monotonic: `9` of 18.
- Frozen primary W=252/S=21/SPY seen-OOS IC:
  `-0.053030`; P1/P2 nominal
  `0.922016` / `0.877624`.

Cost monotonicity is mechanical: increasing bps weakly decreases every net
return for a fixed position path. It is not scientific support. W/S/proxy
patterns are sensitivity descriptions after OOS consumption, not evidence for
selecting a replacement primary.

## Interpretation

Any favorable combination—including S=42—was inspected only after the OOS had
already been observed. It is hypothesis generation requiring a new prospective
or independently frozen dataset. The frozen primary and the timing-corrected
primary remain `NO_GO`.

`POST_OOS_EXPLORATORY — NOT VALIDATION — CANNOT RESCUE RSR_001`
