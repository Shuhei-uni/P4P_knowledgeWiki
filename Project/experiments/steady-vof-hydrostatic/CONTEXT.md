# Steady VOF hydrostatic verification — Andy

Status: closed after a predeclared N1 speed-guard stop; endpoint preserved and unqualified. No continuation selected. See results.md.

Authorized by Andy's “okay run it” on1 October2026, accepting the preceding zero-feed pool proposal. This is a new unnumbered verification diagnostic, not reopening closed campaigns. Only Andy server1 is owned. Preserve all endpoints. No physical transient, geometry change, drain/head sweep or relaxation tuning.

Question: with feed removed, can the current steady SIMPLE/implicit VOF model preserve the intended hydrostatic pool? Hypothesis: matched initial and external heads, with zero imposed inlet velocity, give negligible boundary flux, motion and inventory change. A failure tests this discrete setup, not global steady-solution existence or full-feed separator physics.

Keep full geometry, phases/materials/gravity, K9 vent, downstream head+0.10m, initial pool+0.10m, SIMPLE, pseudo-time inactive, all eight standard URFs0.3 and spatial schemes. Deliberately change both inlet velocity magnitudes27.118→0m/s. Freshly initialize; never continue the depleted N1000 endpoint. Preserve inlet zone types and phase fractions. Initial pressure uses the established modified-pressure formula. Turbulence seed remains k=epsilon=0.01; turbulent scalar relaxation is not itself evidence of bulk fluid motion. The test is hydrodynamic quiescence, not exact equilibrium of every turbulence scalar.

One block of at most500 solved iterations, two controller-hours including retries, fixed deadline in phase-state.yaml. N1 instrumentation interruption counts inside500; then unchanged remaining499. Early scientific guard stops are valid bounded outcomes, not permission to replay. Only equivalent-state recovery of unconsumed iterations is allowed. No automatic follow-on calculation.
