# P71A-T2-RNG-PRODUCTION-LIMITER results

## Status

**BLOCKED_AUTONOMOUS — bounded discovery stopped at active 250.**

The child was staged from the exact `P7-E5-CZ-ABSORB-COLD-RAMP11692` active-1000
case/data pair on `student`. The full parent readback passed. The only declared
delta was RNG production limiter off to on; Fluent read back the toggle as
`true` and materialized its default `clip_factor=10.0`. The verification path
was repaired to treat that option-dependent default as part of the declared
toggle while keeping every other scientific branch strict.

The prepared pair was saved and reopened successfully. The attached discovery
completed the 50-iteration smoke block and reached the required active-250
checkpoint, which was saved. During the next block, residuals escalated, Fluent
reported repeated AMG divergence and floating-point exceptions, and the active-
500 pair was not proven. The live Fluent process was stopped after the local
runner became blocked waiting for the busy solver. No qualification route was
entered and no claim is made about the failed branch beyond this numerical
observation.

## Evidence pointers

- Blocked delta-proof attempt: `attempts/20260911T1054-blocked-production-limiter-delta-proof/run-manifest.json`
- Active-250/FPE attempt: `attempts/20260911T110613Z-active250-fpe/run-manifest.json`
- Partial native paths: `run-paths.yaml`
- Partial attached transcript: `transcript.txt`
- Remote checkpoint pair: the `active250.cas.h5` / `active250.dat.h5` paths recorded in the blocked manifest

## Bounded observations

| Evidence | Observation | Claim limit |
|---|---|---|
| Parent identity | Exact active-1000 parent pair and hashes were verified before mutation | Parent provenance is proven for this attempt |
| Closure readback | Production limiter enabled; Fluent exposed `clip_factor=10.0` as an automatic companion default | The declared delta was implemented; this is not a comparison of alternative limiter factors |
| Smoke block | 50 active iterations completed and pair saved | Smoke behaviour only |
| Active-250 block | Pair saved at active 250; diagnostics included AMG divergence and floating-point/fatal messages | The branch is numerically unstable over this bounded interval; active-500 completion is unproven |
| Frozen physics/setup | No initialization, patch, reset, remesh, resplit, outlet, transient model, or hypothesis route was introduced | No broader physical interpretation is authorized |

## Gate disposition

This item is `BLOCKED_AUTONOMOUS` rather than `COMPLETE_VERIFIED` because its
required 500-iteration discovery horizon and terminal readback were not
completed. The remaining turbulence-family queue stays ordered; it must resume
only after the same `student` server is restarted and a fresh exact-parent
readback is proven. This blocker does not authorize a hypothesis route.
