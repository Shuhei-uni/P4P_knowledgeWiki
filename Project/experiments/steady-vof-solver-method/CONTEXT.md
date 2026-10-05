# Steady VOF solver-method diagnostic — Andy

## Status and authority
Closed unqualified after the bounded N1000 comparison; no further solves selected. See [closure](closure.md). The following records the completed test authority.
Selected under Andy's 1 October2026 instruction: “Decide what to run next and monitor”. One new bounded diagnostic, not reopening Phase7b, Phase9 or the closed K9 Coupled campaign. Existing dedicated Monitor phase9 chat remains selected; activate its existing schedule for this run. Only Andy server1 is owned; preserve all prior endpoints. No physical transient or geometry change.

## Evidence and question
Both K9/Coupled/global-pseudo fresh starts failed conservation, inventory, routing and residual gates after1000 iterations; higher initial submergence did not remove the failure. Independently reduced flux and inventory agree with native reports, eliminating a simple accounting discrepancy as explanation. The single-liquid duct benchmark passed, but it does not test multiphase coupling in separator geometry.
Question: is the failure materially sensitive to the numerical solution method when the physical model and initial fields are held fixed? Hypothesis: supported SIMPLE/pseudo-time-Off treatment may obtain substantially better mass balance than Coupled/global pseudo under identical physical conditions. This is a combined method treatment, including a fixed documented URF prescription; it cannot attribute an effect uniquely to coupling, pseudo-time or relaxation.

## Selected contrast and alternatives
PARTIAL REPEAT of the K9 low-start full-geometry VOF case: same fresh h_i=+0.10m, fixed h_d=+0.10m and K9, same full feed, materials, geometry, turbulence, gravity and spatial schemes. Change Coupled/global pseudo to SIMPLE/pseudo Off with all exposed standard under-relaxation controls fixed0.3. The value is a predeclared choice in the v252 recommended0.2–0.5 range, not a case optimum. No URF, K, head, inlet or pseudo-time sweep.
A single-fluid fullgeometry control is deferred: it changes density/momentum/hydrostatic support along with the interface and answers a less direct question. A physical transient needs separate scope. Previous Phase7b SIMPLE tests used Mixture/sinks and a closed drain and do not settle this matched VOF question.

## Evidence and bounds
Exactly1000 total solved iterations max, six controller wall-hours including retries, fixed deadline in phase-state. One fresh low start; at most a conserved-state technical recovery of unconsumed iterations, no fresh replay beyond cap. No automatic extension. Uniform0.3 URFs remain fixed even if progress is poor. Preserve finite/speed/phase/netflux/deadline guards. Native reports, all active residuals, gross/net phase and mixture boundary ledgers, inventory and N0/N1000 fields plus axial sections are required. Verify initial fields match reference exactly and save/reopen all settings before compute.

Compare last500 absolute conservation, inventory drift, routing/backflow and residual/clipping evidence to the corresponding K9 Coupled reference; show full histories. Equal iteration counts do not represent equal numerical or physical time. A smaller inventory change or lower residual alone does not support the hypothesis. Absolute qualification thresholds are retained as diagnostics, but one start never qualifies the separator. Missing evidence is repaired separately from scientific failure.

After N1000 or a safety stop, preserve and review. No remaining budget from closed campaigns carries over. This test establishes numerical-method sensitivity at most, not calibrated drain physics, a validated steady solution, dynamic stability or global nonexistence. No endpoint is promoted by this diagnostic.
