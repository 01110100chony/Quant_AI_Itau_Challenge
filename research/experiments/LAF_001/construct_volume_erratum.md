# LAF_001 — construction and Volume-semantics erratum

## Preserved history

Stage A1 and A1c remain immutable and historically accurate for their stated
scope. Stage A1c correctly recorded
`VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION` because its
local split continuity checks did not prove Yahoo's literal historical Volume
unit.

Stage A1d is also preserved at H0
`74e53946e9e2fbd07dce15e77d527fd5cd0d1f38`. Its only logical acquisition
ended after two transport failures. The two private receipts remain ignored
and untracked; no payload, price, volume, split comparison or gate was
observed.

```text
A1D_STATUS = INCONCLUSIVE_TRANSPORT_NO_PAYLOAD
A1D_SCIENTIFIC_RESULT = NONE
A1D_RETRY_AUTHORIZED = NO
```

A1d is neither a scientific PASS nor FAIL and no further Tiingo acquisition is
authorized.

## Approved construction response

The Research estimator does not require a claim about the literal global scale
of historical Volume. Within one split regime, multiplying Close and/or Volume
by a positive constant `c` adds the constant `-ln(c)` to
`x = ln(abs(r)/(Close*Volume))`. Both the rolling median and current `x` shift
by that same constant, while the rolling MAD is unchanged. Therefore the
robust z-score is invariant to the positive constant scale when its complete
normalization window belongs to one regime.

This guarantee does not apply across a mechanical scale transition. The
approved safeguard excludes the split ETF on its split session and until its
entire prior 252-session window belongs to the post-split regime. For the only
observed split, IWM `2005-06-09`, the embargo runs through `2006-06-08`; IWM may
re-enter on the following XNYS session if its other eligibility conditions hold.

Pre-association synthetic and real tests multiplied pre-split IWM Close and/or
Volume by `0.5` and `2.0`. Outside the embargo, maximum absolute differences in
both `A_d` and `LAF_t` were zero at tolerance `1e-12`.

## Remaining limitation

`Close * Volume` is described only as a provider-consistent monetary-volume
proxy. This invariant construction removes sensitivity to a positive constant
unit scale within each protected regime; it does not independently establish
Yahoo's literal historical Volume semantics, prove notional traded value, or
protect against nonconstant provider errors.
