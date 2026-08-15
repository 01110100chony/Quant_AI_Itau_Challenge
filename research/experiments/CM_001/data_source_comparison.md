# CM_001 — Data source comparison

| Provider candidate | Coverage | OHLC quality | Corporate actions | Timezone/calendar quality | Reproducibility | Main limitation | Recommendation |
|---|---|---|---|---|---|---|---|
| Yahoo Chart API — US | 2010–2018 complete | valid OHLC | dividends/splits stream | timezone metadata; no calendar | no auth; live endpoint | unofficial and mutable history | Candidate for human approval |
| Yahoo Chart API — Taiwan | partial | 0052 zero/missing Open; 0050 scale issue | incomplete/misaligned event history | timezone metadata; no calendar | no auth; live endpoint | history not defensible as sole source | Diagnostic only; do not promote |
| TWSE public — TAIEX | 1999 onward; complete Research | official OHLC | not applicable | date only; hours separate | public monthly endpoint | no timezone in response | Recommended primary TAIEX source |
| TWSE public — 0052/0050 | 2010 onward | official raw OHLC; 0052 has 108 classified no-regular-OHLC rows | 6/11 distributions cross-checked in two official endpoints; no Research split found | date only; hours separately documented | public endpoints; immutable local snapshots | pre-2010 unavailable; redistribution terms need review | Recommended Taiwan price/action source after policy approval |
| TWSE Data E-Shop | starts 1992 | official daily OHLC product | separate products may be needed | official production metadata | subscription required | licensing/cost | Not needed after approved 2010 revision unless missing-row policy requires it |
| Fubon / issuer — 0052 | product/distribution history | not a daily exchange-OHLC source | issuer distributions | not a calendar | public pages | does not replace TWSE OHLC | Use for action cross-check |

```text
TECHNICAL RECOMMENDATION: APPROVE
HUMAN DECISION: REQUIRED
```

Recommended multi-provider candidate for human approval: Yahoo immutable JSON for `XSD/QQQ/SPY`; official TWSE monthly endpoints for `0052/TAIEX/0050`; official TWSE event endpoints for Taiwan corporate actions; official session sources for Taiwan dates/hours; and `exchange-calendars==4.13.2` `XNYS` for the US calendar. This recommendation uses only coverage, schema, provenance, timestamps, OHLC integrity, corporate-action information and reproducibility.
