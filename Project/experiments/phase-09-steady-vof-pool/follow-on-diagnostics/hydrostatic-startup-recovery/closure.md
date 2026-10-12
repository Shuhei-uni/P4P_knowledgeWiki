# Bounded closure — hydrostatic startup not preserved

## Answer

Three evidence-directed contrasts were executed under the renewed autonomous envelope. All stopped after one solved iteration at the predeclared2m/s maximum-speed guard, so none is a completed500-iteration run or a late-time convergence test. The campaign is closed unqualified at the three-unsuccessful-contrast limit. No further solve is selected; unusediteration/hour budget is not permission for a fourth contrast.

| Fresh zero-feed contrast | N1 max speed m/s | Liquid mass change | Liquid net inward kg/s |
| --- | ---: | ---: | ---: |
| Native pressure patch, PRESTO! | 30.891001 | +0.355991% | 33.937701 |
| Native pressure patch, Modified BFW | 30.891001 | +0.355991% | 33.937701 |
| Native pressure patch, Modified BFW, brine sealed | 30.938888 | +0.328854% | 0 |

The preserved earlier direct-SV_P reference had speed10.942883m/s and inventory change−0.468904% atN1. It is not counted in this new campaign. Pressure/alpha/geometry starting fields matched within declared tolerance, velocities/native boundary flow were zero and settings/save-reopen passed before each new solve.

## Supported interpretation

Native pressure patching changed startup behavior but did not cure the motion. This establishes route dependence, not the identity of an auxiliary-field defect. Changing PRESTO! to Modified BFW gave bitwise-identical exported N1 pressure/velocity/alpha fields despite verified distinct method settings; that finding is restricted to the first guarded iteration.

Sealing only brine gave the same order of motion while liquid boundary flow was zero. Brine pressure/vent forcing is therefore not necessary for the response. This weakens a simple explanation that the current failure is solely caused by the drain. The steam pressure boundary remains open and other boundaries/initialization/body-force/interface discretization remain possible. The liquid inventory change with zero liquid boundary flux is an unconverged steady numerical update, not a physical storage rate.

The speed maximum for all three new cases is at(0.766235,0.140942,0.408113)m, about0.041m above the nominal initial interface. That location directs the next audit toward local interface/pressure/body-force initialization, but is not causal proof. A field-consistent initialization check should include face/gradient state and the discrete interface, not only cell-center arrays.

## Evidence quality and limits

All three terminal jobs passed deterministic artifact verification. Saved Fluent-local pairs, native histories and seven residuals, completeN1 callbacks, gross/net phase/native mixture ledgers, fullfields and axial sections are present. Independent face/native flux parity is≤1.42e−14kg/s. Terminal live probe verified idleN1, exited worker/controller, free server1 lock and the saved sealed-brine pair. No missing100-iteration window has been relabelled as a measured failed window: only initial preservation/guard outcomes were tested. This campaign does not prove no steady solution exists, physical transient necessity, calibrated drainage or separator performance.

## Spend and next direction

Three solved iterations and171.187112 controller-seconds were used; build/API repairs issued zero solves. Three unsuccessful mechanism contrasts exhausted the decision limit, well below the3000-iteration/six-controller-hour ceiling. Monitoring is paused after this terminal review. Fluent remains on the unqualified sealed-brine diagnostic; all earlier original-boundary endpoints are preserved.

Recommend a focused discrete-interface/body-force initialization investigation before more full-feed runs. A useful next comparison would need a verified consistent native interface/pressure construction and a predeclared discriminating result; merely extending these N1 failures or trying more relaxation values is not supported here. No new phase number, fourth contrast or physical transient is selected by this closure.

Exact sources: phase-state.yaml links each run; PyAnsys/output/hydrostatic-startup-recovery/campaign-comparison.json and native-versus-modified-audit.json hold the comparison, terminal-live-proof.json holds ownership/state proof.
