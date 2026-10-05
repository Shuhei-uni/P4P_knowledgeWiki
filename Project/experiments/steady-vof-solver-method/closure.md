# Closure — mixed method response, no qualified solution

The declared 1000-iteration diagnostic is complete and closed unqualified. All 1000 solves and 6239.363 controller-seconds are accounted for; terminal artifacts and idle ownership reconciliation passed. No further solver work is selected. See results.md for the evidence matrix and exact machine artifacts.

## Scientific disposition

The numerical-method package changes the trajectory substantially. Late500 mean absolute liquid and mixture imbalance decreased about60% relative to the matched Coupled run. The stronger hypothesis of a simultaneous improvement is not supported: the predeclared inventory-not-worse rule fails, routing is mixed, and absolute conservation, inventory and residual criteria still fail. This is a mixed diagnostic response, not proof that SIMPLE is uniformly better or worse.

Startup inventory change alone would not disprove eventual convergence: an arbitrary initial pool need not equal an equilibrium pool. The slower final200 depletion is therefore relevant, but does not replace a stationary, conservative acceptance window. The test does not distinguish eventual convergence from a different poorly balanced numerical state. No physical storage time can be inferred from steady iteration count. Neither endpoint is a qualified continuation parent for separator claims.

A saved-field height audit (PyAnsys/output/steady-vof-solver-method/planner-height-audit.json) confirms a materially different liquid distribution: volume-mean liquid fraction in −0.5≤y<0 m is0.2325 for SIMPLE versus0.8774 for Coupled; below−0.5 m it remains0.9764 versus0.9985. Thus the SIMPLE result retains a substantial lower liquid region; it is not evidence that the vessel has emptied completely. Horizontal bins do not establish connected-interface geometry or drainage causality.

## Recommended next scientific question — proposal, not execution authority

Before another full-feed continuation, isolate whether the full-geometry two-phase model can preserve a hydrostatically balanced pool without feed. This is a verification control, not an operating separator prediction. Keep the current SIMPLE/pseudo-off treatment and drain representation fixed; establish analytically consistent pressure/head and a fresh interface, then check spurious motion, inventory and individual boundary fluxes against predeclared absolute scales. A previous Phase9 rest diagnostic used Coupled/global pseudo and failed quiescence; it did not test this formulation. The passing single-liquid duct control did not test a two-phase hydrostatic interface in this geometry.

This would deliberately replace full feed with a zero-feed verification condition. It must have its own bounded contract, supported zero-flow boundary treatment and tolerances before execution. Its value is distinguishing failure of static pool support/initialization/boundaries from difficulties introduced by operating feed. A pass would not validate full-feed separation; a failure would focus diagnosis on the simpler balance before spending more full-feed compute. No mesh change, transient, tuning sweep, new phase number or new solve is authorized by this recommendation.
