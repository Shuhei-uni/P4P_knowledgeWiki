# 03A Stage 2 — compact numerical-stabilisation screening report

## Report status

This is the compact Stage-2 screening report assembled from the locally persisted Fluent journals, residual histories, endpoint flux snapshots, and branch summaries.

Current status:

```text
N1: verified and reported
N3: verified and reported
N4: endpoint snapshot available; final gRPC/readback verification pending
N5: standard bootstrap and RNG return verified; +700 endpoint evidence pending
```

The report is decision-oriented. It does not treat a branch with improved residuals or improved balance as a canonical 03A parent until the altered numerical settings have been restored and the field survives the return-to-authority continuation.

## 1. What Stage 2 tested

The Stage-1 full-geometry case survived 1,000 steady iterations but did not establish a sufficiently settled canonical field. The reference endpoint had:

- continuity residual approximately `1.6043e-1`;
- strongly intermittent `k`/`epsilon` residual behaviour;
- phase-2 volume-fraction residual approximately `6.5142e-3`;
- diagnostic full-domain mass imbalance approximately `17.17%`.

Stage 2 therefore tested four independent stabilization routes from the same immutable Stage-1 iteration-1,000 parent while keeping the physical case and outlet pressures unchanged.

## 2. Branch definitions and iteration lineage

| Branch | Numerical intervention | Completed local lineage |
|---|---|---|
| N1 | (k)/(epsilon) URFs: 0.8 → 0.5 | Stage 1 +300, then +700; expected endpoint iteration 2000 |
| N3 | First-order (k) and (epsilon), momentum second-order | Stage 1 +300, then +700; expected endpoint iteration 2000 |
| N4 | First-order momentum, (k), and (epsilon) | Stage 1 +300, then requested +700; endpoint readback pending |
| N5 | Standard (k)-(epsilon) bootstrap, restore RNG (k)-(epsilon) | Stage 1 +500 standard +300 RNG return, then requested +700; expected endpoint iteration 2500 |

N5’s standard-model phase is a separate bootstrap. The required authority test is the restored RNG phase, not the standard-(k)-(epsilon) endpoint by itself.

## 3. Endpoint verification ledger

| Branch/phase | Case/data evidence | Residual evidence | Flux evidence | Current status |
|---|---|---|---|---|
| N1 +700 | Paired endpoint loaded | Ends at iteration 2000 | Available | `RUN_COMPLETED_ENDPOINT_VERIFIED` |
| N3 +700 | Paired endpoint loaded | Ends at iteration 2000 | Available | `RUN_COMPLETED_ENDPOINT_VERIFIED` |
| N4 +700 | Paired endpoint loaded for local flux snapshot | Local residual artifact ends at iteration 1300 | Available, but endpoint readback pending | `ENDPOINT_PRESENT_AFTER_NATIVE_EXCEPTION` |
| N5 standard +500 | Paired endpoint loaded | Ends at iteration 1500 | Available | `RUN_COMPLETED_ENDPOINT_VERIFIED` |
| N5 RNG +300 | Paired endpoint loaded | Ends at iteration 1800 | Available | `RUN_COMPLETED_ENDPOINT_VERIFIED` |
| N5 RNG +700 | Remote `.dat.h5` was observed, but local endpoint evidence is not persisted | Not available locally | Not available locally | Pending verification |

The N4 failure is recorded as a transport event: `RuntimeError: Stream removed (recvmsg:No route to host)`. It is not automatically classified as a Fluent numerical failure. The N4 and N5 verification gaps remain visible rather than being filled from filename or data-file presence alone.

## 4. Compact cross-branch figures

### Figure 1 — Direct Fluent scaled residual histories

![Four-branch direct scaled residual overview](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-full-scaled-residual-overview.png)

[Open the four-branch scaled-residual overview](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-full-scaled-residual-overview.png)

N1 and N3 contain complete +700 residual histories. N4’s local residual artifact stops at iteration 1300, and N5’s +700 residual artifact is not locally available; both limitations are marked directly on the figure.

### Figure 2 — Endpoint phase fluxes

![Compact phase-flux comparison](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-phase-flux-overview.png)

[Open the phase-flux overview](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-phase-flux-overview.png)

The comparison uses the last available endpoint for each branch. The N4 bar is a provisional `plus700` endpoint snapshot. The N5 bar is the restored RNG +300 endpoint, not the pending +700 endpoint.

### Figure 3 — Diagnostic mass balance

![Compact mass-balance comparison](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-mass-balance-overview.png)

[Open the mass-balance overview](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-mass-balance-overview.png)

The Stage-1 reference line is `17.17%`. The balance is a diagnostic all-discovered-pressure-outlet metric and should not be used as the sole convergence criterion.

### Liquid inventory history availability

No branch currently has a genuine temporal liquid-inventory history in the persisted Stage-2 monitor artifacts. Flux and inventory monitor sets have zero recorded points; only residual histories were captured. Consequently, no liquid-inventory plot is generated and no inventory trend is inferred.

## 5. Cross-branch result table

The values below are endpoint or final-available-phase values. The final-window residual values are medians over the last 100 recorded points in the corresponding available phase.

| Case/state | Continuity median | epsilon median | epsilon P95 | VF median | Diagnostic mass imbalance | x_out | Evidence state |
|---|---:|---:|---:|---:|---:|---:|---|
| Stage 1 | 1.5773e-1 | 3.2177e-2 | 9.3945e-1 | 8.7141e-3 | 17.17% | 0.9968 | Verified reference |
| N1 +700 | 3.2641e-1 | 1.0647e-1 | 1.9110e+0 | 1.0831e-2 | 25.16% | 0.9194 | Verified |
| N3 +700 | 4.8200e-1 | 1.4268e-1 | 2.8116e+0 | 1.4324e-2 | 15.10% | 0.9189 | Verified |
| N4 +700 snapshot | Not available | Not available | Not available | Not available | 93.61% | 0.6152 | Provisional endpoint snapshot |
| N5 standard +500 | 7.8155e-2 | 5.0056e-3 | 1.3436e-2 | 7.2313e-3 | 5.24% | 0.9668 | Verified bootstrap only |
| N5 restored RNG +300 | 4.0668e-1 | 6.5010e-2 | 1.3728e+0 | 1.5071e-2 | 37.57% | 0.8833 | Verified authority-return phase |
| N5 RNG +700 | Not available | Not available | Not available | Not available | Pending | Pending | Pending verification |

The low N5 standard-bootstrap values must not be used as the final N5 result because the standard model is not the canonical authority. The restored RNG phase is the relevant N5 qualification evidence, and it does not preserve the bootstrap improvement.

## 6. Branch decisions

| Branch | Numerical stability | Conservation | Physical behaviour | Current decision |
|---|---|---|---|---|
| N1 | Worse during +700; continuity and turbulence envelope rise | Worse: 25.16% | Materially changed phase routing; no inventory history | `REJECT` for canonical-return test |
| N3 | Worse during +700; continuity and turbulence envelope rise | Improved at endpoint: 15.10% | Materially changed phase routing; no inventory history | `STABILISES CONSERVATION BUT CHANGES THE SOLUTION` |
| N4 | Initially promising at +300; +700 residual history incomplete | Strongly worse in available endpoint snapshot: 93.61% | Severe phase-routing change | `REJECT PENDING FINAL READBACK` |
| N5 | Standard bootstrap improves; restored RNG return worsens | 5.24% during standard bootstrap, 37.57% after RNG return | Materially changed across model transition | `RNG RETURN NOT STABLE; +700 PENDING` |

No branch currently satisfies the evidence required to become a canonical 03A parent.

## 7. Return-to-authority gate

The canonical settings to be restored for N1, N3, or N4 are: Pressure URF `0.3`, Momentum URF `0.7`, `k` URF `0.8`, `epsilon` URF `0.8`, Momentum `Second Order Upwind`, `k` `Second Order Upwind`, `epsilon` `Second Order Upwind`, Volume fraction `QUICK`, and RNG `k-epsilon`.

The selected stabilization field would then need a 200–300 iteration continuation without reinitialization. At the current screening stage:

- N1 does not justify that test;
- N3 improves balance but not the numerical residual field, so it does not yet justify that test;
- N4 has a provisional endpoint snapshot that is physically disqualifying, pending final readback;
- N5 already contains the authority return, and the available RNG-return phase does not remain stable.

The current report therefore recommends **no canonical-return run yet**. That decision can change only if the pending N4/N5 readback materially changes the evidence.

## 8. Pending evidence and next report edit

The remaining reporting work is deliberately narrow:

1. reconnect to Fluent when `student` is reachable;
2. verify the N4 paired endpoint and capture its complete residual history/settings readback;
3. verify the N5 `plus700` paired endpoint and capture its residual and flux evidence;
4. update the two provisional branch records and regenerate Figures 1–3;
5. decide whether any branch deserves the canonical-return continuation.

No new iterations are authorised by this report-writing step. The pending verification is read-only.

## Branch-level records

- [N1 results](03a-08b-stage2-N1-results.md)
- [N3 results](03a-08b-stage2-N3-results.md)
- [N4 results](03a-08b-stage2-N4-results.md)
- [N5 results](03a-08b-stage2-N5-results.md)

## Analysis artifacts

- [overview JSON](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/overview/stage2-overview.json)
- [N1 summary JSON](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/N1/N1-summary.json)
- [N3 summary JSON](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/N3/N3-summary.json)
- [N4 summary JSON](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/N4/N4-summary.json)
- [N5 summary JSON](../../../../../PyAnsys/output/03a_stage2/20260817T132736Z/report/N5/N5-summary.json)
