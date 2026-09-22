# Phase 7.1A — 60k Virtual Liquid Outlet (parent evidence)


> [Phase-level interpretation](interpretation.md) — concise hypothesis → experiments → evidence → decision narrative.
## Status

**Completed parent phase.** Phase 7.1A established the developed numerical state that is now used as the baseline for [Phase 7.2A](../phase-07-2a-wall-liquid-routing/index.md).

The promoted parent is the completed R0 smooth-wall continuation:

- source run: `PyAnsys/output/phase71a_r0_control_run4`;
- steady pressure-based Coupled solver;
- Coupled-compatible Global Time Step pseudo-time;
- full inlet loading;
- v2 phase-2-only throughput-controlled virtual liquid outlet;
- smooth wall, EWF off;
- terminal native report/transcript state: iteration `5586`.

The exact case/data pair and hashes are recorded in the [Phase 7.2A baseline handoff](../phase-07-2a-wall-liquid-routing/baseline-control-handoff.md).

## Why this state was promoted

The decision to move to Phase 7.2A was **not** based on every scaled residual becoming smooth or small.

The run4 endpoint was promoted because, relative to the earlier Phase 7.1A states, it gave the strongest combined behaviour in the quantities that matter most for this project:

- liquid inventory became bounded and much more stable;
- source-inclusive mass closure was the best obtained so far;
- continuity reached the lowest useful level obtained so far;
- the absorber command remained exactly matched by the applied phase-2 removal;
- the 1,000-iteration continuation completed without AMG, FPE, nonfinite, or fatal events.

At the terminal report point:

- total liquid mass: `295.8536 kg`;
- absorber command / applied removal: `116.9200 / 116.9200 kg/s`;
- command error: `4.26e-14 kg/s`;
- continuity residual: `2.7841e-3`;
- phase-2 volume-fraction residual: `5.4762e-4`;
- phase-2 liquid through `steamoutlet`: `-24.3344 kg/s`;
- phase-1 vapor through `steamoutlet`: `-80.2509 kg/s`.

This is therefore the **best-available developed parent**, not a fully converged or physically validated separator solution.

## What remains wrong

The remaining problem is now more physical than purely numerical.

The multiphase and turbulence residuals remain oscillatory, and substantial liquid still leaves through `steamoutlet`. The endpoint therefore does **not** demonstrate correct separator performance.

For this project, a jumpy residual by itself is not enough reason to reject a state if the macroscopic solution is bounded. The more important failure would be continued drift in liquid inventory, poor source-inclusive mass closure, worsening continuity, or unstable phase routing.

The Phase 7.1A endpoint passed that parent-state test well enough to stop treating residual reduction as the main question.

## Phase 7.1A decision

Phase 7.1A therefore ends with the following decision:

> Preserve the run4 developed state and move the next experiments to the unresolved liquid-routing problem.

Phase 7.2A now asks whether wall interaction can reduce liquid carryover through `steamoutlet` **without destroying** the useful behaviour established here.

The comparison priority for 7.2A is:

1. bounded total liquid inventory and late-window inventory slope;
2. source-inclusive mass closure;
3. continuity behaviour;
4. phase-resolved routing, especially liquid through `steamoutlet`;
5. residual amplitude/trend and solver-event health.

Lower residuals alone are not a positive result if inventory, closure, or phase routing becomes worse.

## Active mechanism retained from 7.1A

The v2 virtual outlet command is

\[
Q_{\rm cmd}=|\dot m_{l,in}|,
\qquad
S_l(\mathbf{x})=-Q_{\rm cmd}
\frac{\alpha_l(\mathbf{x})}
{\max(\int_{V_a}\alpha_l\,dV,10^{-6}\ {\rm m^3})}.
\]

The source acts directly on phase 2 only. Matching liquid momentum and shared
`k`/`epsilon` removal are attached. Phase 1 has no direct mass source.

This mechanism is held fixed in the initial Phase 7.2A wall-treatment screen so that changes in liquid routing can be attributed to the wall treatment rather than to a new absorber law.

## Evidence boundary

Phase 7.1A establishes a reusable numerical parent and its provenance. It does not establish:

- physical validity of the virtual outlet;
- correct real-plant brine hydraulics;
- a validated separator liquid inventory;
- negligible liquid carryover;
- mesh independence; or
- fully steady convergence of every solved equation.

Earlier turbulence, C7/C8, inlet-ramp, dynamic-ring, prepared-v2, and Family N records remain historical provenance. They are not eligible parents for the active Phase 7.2A comparison.
