# LAF_001 — Stage A1 structural results

## Objective and method

Stage A1 tested only whether the provider fields required by the candidate
design exist, are structurally usable inside the authorized boundary and can
be reproduced. It used one direct Yahoo Finance Chart API request per symbol
with `interval=1d`, `period1=1041379200`, exclusive
`period2=1483228800`, `events=div,splits,capitalGains`,
`includeAdjustedClose=true` and `includePrePost=false`.

No auto-adjust, repair, fill or imputation was enabled. Raw response bytes were
written before parsing and verified against SHA-256. Timestamps were converted
to session dates with the provider timezone and compared with candidate XNYS
sessions from `exchange-calendars` explicitly bounded to 2003–2016.

## Provenance

- Retrieval ID: `20260815T055848814Z`.
- Provider: Yahoo Finance Chart API.
- Parser: `laf-stage-a1-v1`.
- H0-A1: `01cc8408a83024663cc7cb7d434f82292072a945`.
- All requests succeeded on attempt 1 with HTTP 200 and a null `chart.error`.
- Raw responses, request records, receipts and retrieval manifest are under
  `data/raw/laf_001/research/20260815T055848814Z/`.
- Derived structural audits are under
  `data/processed/laf_001/stage_a1/20260815T055848814Z/`.

| Symbol | Bytes | SHA-256 |
|---|---:|---|
| SPY | 394680 | `306c43087e3a33048d29b47746250cfeaca6a0ec69532084d3e12e7cb2393153` |
| QQQ | 390234 | `1d747eb4f1fc4b7f22e1cfdae40ad4932a9301324c666e101e3bebcd41a9e479` |
| IWM | 385312 | `ee972d8c9d5ad737370df7f30d4954e8065316218ae08d64430f28b9f3feb0b3` |
| DIA | 394576 | `30f7b0370a61be244cd0425602c7c4821dbc4ddef9d3598e267f6aaf8e6fbe53` |
| MDY | 386581 | `5dba651a9fa9100ef740eaa27f4a8221b63371a8a44b22b1bf29113a46a41fc5` |

Independent file hashing matched every receipt.

## Coverage and structural integrity

| Symbol | Expected XNYS | Observed | Missing | Extra | First | Last |
|---|---:|---:|---:|---:|---|---|
| SPY | 3525 | 3525 | 0 | 0 | 2003-01-02 | 2016-12-30 |
| QQQ | 3525 | 3525 | 0 | 0 | 2003-01-02 | 2016-12-30 |
| IWM | 3525 | 3525 | 0 | 0 | 2003-01-02 | 2016-12-30 |
| DIA | 3525 | 3525 | 0 | 0 | 2003-01-02 | 2016-12-30 |
| MDY | 3525 | 3525 | 0 | 0 | 2003-01-02 | 2016-12-30 |

For every symbol, all audited counts were zero for null, zero and negative
Open/High/Low/Close/Adj Close/Volume; High below max(Open, Close); Low above
min(Open, Close); High below Low; duplicate timestamps; and timestamps outside
the authorized boundary. Timestamps were strictly increasing. Monthly OHLC
completeness was 100%, and `calendar_exceptions.csv` contains zero rows.

The provider reported USD ETFs at daily granularity in
`America/New_York`; exchange codes were PCX for SPY, IWM, DIA and MDY and NGM
for QQQ. Metadata was preserved without reinterpretation.

## Corporate actions

| Symbol | Dividends | Stock splits | Capital gains |
|---|---:|---:|---:|
| SPY | 57 | 0 | 0 |
| QQQ | 51 | 0 | 0 |
| IWM | 57 | 1 | 0 |
| DIA | 168 | 0 | 0 |
| MDY | 56 | 0 | 0 |

The single split was IWM on `2005-06-09`, provider factor 2.0. The raw Close
before the event was `61.71500015258789`, event Open
`61.66999816894531`, event Close `62.31999969482422`, and next raw Close
`62.45000076293945`; the permitted mechanical check classified the raw series
as `RAW_SERIES_ALREADY_SCALE_CONTINUOUS`. This classification does not select
an adjusted-return or distribution policy.

## Anomalies and limitations

The initial derived calendar comparison used the library's moving default
calendar window, beginning `2006-08-15`, and therefore generated a false set
of exceptions. The raw acquisition was not affected. The deterministic defect
was corrected by supplying the fixed human-approved start/end to XNYS; the
corrected 3,525-session expectation is protected by a regression test. The
invalid derivative was removed and reproduced from unchanged raw hashes.

Yahoo remains a candidate source, not a human-approved final source. Absence
of missing values in this snapshot does not choose a future missingness or
zero-volume policy. Structural availability also does not decide adjusted
returns, distributions, universe completeness, feature normalization or any
statistical gate.

## Verdict

`PASS_READY_FOR_STAGE_A2_DECISIONS`

No structural failure remains unclassified. This verdict is not evidence of
association, prediction, economic performance or thesis validity.
