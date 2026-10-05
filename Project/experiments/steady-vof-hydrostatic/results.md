# Zero-feed hydrostatic verification — guarded failure

The freshly prepared pool did not preserve hydrostatic quiescence. The predeclared maximum-speed guard stopped the calculation at N1, so this is a one-iteration guarded diagnostic outcome, not a completed500-iteration test or a long-time steady-state conclusion. No further solves are selected.

## Verified observations

Before solving, both inlet magnitudes were zero; native phase and mixture boundary flows and field velocity were zero. The initial alpha/pressure/mesh fields matched the prior fresh low-pool configuration. Settings and native evidence passed save/reopen checks. Previous valuable endpoints were verified preserved.

At N1, maximum speed was10.942883m/s, exceeding the2m/s stop threshold. Liquid mass changed4096.769804→4077.559874kg (−19.209930kg, −0.468904%). Maximum individual phase boundary gross flow was62.503668kg/s. Liquid/vapor/native-mixture net inward rates were48.794553/−0.459993/48.334560kg/s. These are steady-iteration observations: do not equate the inventory change to physical storage over a time interval.

The speed maximum lies at cell centroid(0.671834,−0.328643,0.990099)m, with liquid fraction1 before and after; pressure there changed1123683.738→1123724.807Pa. Volume-weighted RMS pressure departure is13.286926Pa and volume-weighted absolute alpha change0.00176676. Cellwise localization identifies a place to investigate; it does not identify the cause.

Face/native flux parity is1.42e−14kg/s, and phase/native-mixture parity7.11e−15kg/s. Initial/final full fields, axial sections, native history/transcript, allseven residuals and N1 gross/net callback are preserved; artifact verification passed. Terminal live receipt verified idleN1, exited controller/worker, free lock, correct zero-feed settings and paired checkpoint. The first-iteration safety stop took precedence over the instrumentation-resume branch; the remaining499 iterations were never issued as another batch. The preserved native N1 evidence has been verified directly.

## Interpretation and limits

The discrete prepared state produces strong motion without operating feed. Operating inlet momentum therefore is not necessary for this startup response. This does not show whether a later state could settle, whether a different initialization would fix it, or whether the physical separator has a steady solution. The equilibrium could be disturbed by cell/face pressure initialization, interface/body-force discretization or the outlet/boundary implementation; none is uniquely isolated here. A finite scalar turbulence seed also remains part of the setup. The documented modified-pressure convention was checked and no sign error was identified, but direct SV_P writes do not prove every auxiliary quantity is refreshed.

The throughout inventory criterion failed; final100 gates are unavailable afterN1 and must not be interpreted as measured100-iteration failures. N1 residuals cannot establish convergence. The result is unqualified. This is not a reason to tune URFs or extend the run blindly.

## Disposition

Stop and preserve the guarded test. Next useful work is a no-solve audit of pressure/body-force and boundary values around the speed maximum and drain, including comparison of cell and face initialization, before selecting any repair contrast. This does not authorize a new run. The two-hour/500-iteration budget was a ceiling, not an instruction to bypass guards. One solved iteration and55.786691 controller-seconds were spent;499 iterations are unused, with zero continuation authorized. The existing Monitor phase9 schedule was activated for the job and paused after terminal review here; no redundant cross-chat handoff is needed.

Evidence pointers: exact job/build/run receipts are in phase-state.yaml; native run directory holds analysis.json, spatial-stop-audit.json and hydrostatic-evidence.png. Terminal live receipt: ../../../PyAnsys/output/steady-vof-hydrostatic/terminal-live-receipt.json.
