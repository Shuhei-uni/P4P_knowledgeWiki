# New-chat prompt — brine-outlet CFD modelling

Copy the text below into the new Codex chat.

---

I need you to continue the resolved brine-outlet modelling for my geothermal
steam-water separator CFD project. Treat the repository as the source of truth
and work autonomously through inspection, safe implementation, execution,
analysis and documentation. Do not ask for confirmation for ordinary bounded
diagnostic steps, but do not resume a prohibited field or overwrite evidence.

Repository:

`/Users/andy/Desktop/P4P/P4P_knowledgeWiki`

First read completely:

1. `AGENTS.md`
2. `PyAnsys/AGENTS.md`
3. `ResearchProject_wiki/AGENTS.md`
4. `CFD_wiki/AGENTS.md`
5. `ResearchProject_wiki/wiki/progress/brine-outlet-modelling-handoff-2026-08-21.md`
6. `Setup report/order-dictionary.md`
7. `Setup report/07l-split-inlet-hydrostatic-rest-isolation.md`
8. `Setup report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md`
9. the current status, experiments, blockers and validation pages referenced by
   the handoff;
10. the setup-07l and setup-07m machine-readable manifests, transcripts and
    scripts listed in the handoff.

Current authoritative state:

- Setup 07l step 10 is the sole accepted clean parent.
- Setup 07m accepted the zero-feed pressure bracket and the 0.1% inlet hold.
- The progressive ramp completed 0.2% and 0.5%. The saved 1% checkpoint stayed
  finite and bounded but stopped because final continuity was 0.0177001, above
  the 0.01 promotion gate.
- The attempted 20-step 1% hold timed out during connection before any new
  physical step. Its `running` manifest is stale and must be preserved under a
  non-overwriting attempt record.
- No controller was active at handoff.
- The server-2 steady Mixture branch failed gross drainage at iteration 150
  and must never be resumed or used as a parent.
- DPM must have zero injection objects and remain off. EWF and every numerical
  sink remain off.
- The brine pressure 1,122,090.400 Pa is a CFD-derived modified-pressure rest
  diagnostic, not a validated plant boundary.

Before connecting, audit the exact controller PIDs, stale manifests and local
processes. Never start a second writer. Use bounded raw TCP preflight first.
Then authenticate one owner with `cleanup_on_exit=False`, verify Fluent 2024 R2,
exactly 16 solver ranks, connected-client state, and existence/readability of
the remote 1% case/data checkpoint. Read every changed Fluent setting back.
Do not expose `.env` credentials in chat or files.

Immediate calculation:

1. Preserve the stale zero-step 1% hold attempt and use a new non-overwriting
   output label.
2. Cold-load the saved setup-07m 1% checkpoint.
3. Keep inlet fraction 0.01, liquid 1.1692 kg/s, vapor 0.8069 kg/s,
   dt=1e-7 s and 100 inner iterations per physical step.
4. Hold for 20 additional physical steps. Save separate case/data at
   additional steps 5, 10 and 20, plus transcript, residual history, physical
   monitors and a machine-readable manifest.
5. Promote only after two consecutive end-of-step continuity values <=0.01
   and all Courant, VOF, pressure, velocity, phase-routing, inventory,
   storage-closure, clock and DPM gates pass.
6. If the 1% hold fails, run one-factor sensitivities from the same checkpoint:
   first 200 inner iterations at dt=1e-7 s, then 100 inner iterations at
   dt=5e-8 s. Do not change flow or pressure in those comparisons.
7. If 1% passes, continue with smaller common inlet fractions such as 1.5%,
   2%, 3% and 5%, saving and gating every level. Stop at the first failed
   residual envelope or physical monitor gate.

Use server 1 for the authoritative sequential lineage unless an identical
parent case/data pair is transferred to server 2 and verified by checksum and
complete Fluent readback. Server 2 may run an independent sensitivity in
parallel only when that does not alter or compete with the setup-07m chain.

Do not claim full-flow operation, level control, plant-valid brine pressure,
mesh independence, separator efficiency, DPM carryover or EWF performance.
The missing downstream pressure/head, pipe/valve resistance and operating
liquid-level data remain the main physical blocker.

Keep working while safe useful actions remain. Update the setup-07m report,
experiments, current status, blockers, validation, order dictionary and
repository log with actual evidence. Clearly classify every result as accepted
diagnostic, diagnostic/unresolved or terminal diagnostic.

Start by reporting:

- the authoritative parent case/data and why it is safe;
- whether any controller or writer is actually active;
- health/rank/file availability for each configured server;
- the exact non-overwriting 1% hold output name;
- any discrepancy that would invalidate the continuation.

Then execute the safe continuation without waiting for further confirmation.

---

