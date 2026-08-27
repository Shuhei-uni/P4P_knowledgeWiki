> **Retired source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** These excerpts preserve the historical blocker record; no blocker status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical blocker notes

> **Retired source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** Selected historical limitations are preserved without changing their status or interpretation.

### BLK-012 | FG-MIX-T01 Stage-3 no-patch control failed at NP-DT1
- Status: Active — NP-DT1 failed; NP-DT2 requires explicit follow-on authorization
- First observed: 2026-08-16
- Related run(s): `FG-MIX-T01-S2-START-STATES-2026-08-16`, `FG-MIX-T01-S3-NP-DT1-2026-08-17`
- Symptom: the exact unpatched C1375 steady parent was loaded and converted to transient with both pressure outlets at `1.120 MPa` gauge, no Hybrid Initialization, no Y010 patch, `2.5e-4 s` timestep, and `20` maximum iterations per timestep. The native `200`-step attempt terminated with a floating-point exception after residual blow-up, full-mesh viscosity limiting, reverse flow at both pressure outlets, and AMG divergence.
- Current interpretation: the no-patch control does not support transient-conversion viability at the existing timestep. It does not by itself identify whether timestep resolution, the inherited parent field, outlet physics, or another coupled numerical mechanism dominates. The exact transient-step/physical-time failure coordinate was not recoverable from the live monitor.
- Recovery action completed: a fresh no-patch start pair was written and reload-verified from the steady parent; no endpoint was written after the native failure. No NP-DT2 retry has been submitted.
- Evidence: NP-DT1 report (retired source, details retained in this Project packet), NP-DT1 result manifest (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step_20260817.json`; not migrated), and NP-DT1 native journal (historical machine artifact path: `../../../PyAnsys/output/fg_mix_t01_stage3_NP-DT1_200step.jou`; not migrated).
