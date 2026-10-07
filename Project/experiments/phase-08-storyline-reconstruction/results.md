# Phase 8 — results by stage

| Stage / trial | Evidence | Limit |
| --- | --- | --- |
| 1 | [Original F0–F4 results](stage-01-60k-storyline/results.md) | 60k storyline; retained numerical and accounting limits |
| 2, low-feed/ramp | [Failed at N1422](stage-02-fine-mesh-simple/results.md) | N1000 checkpoint verified; incomplete full-speed experiment |
| 2, fresh full feed | [Absorber-OFF trial](stage-02-fine-mesh-simple/full-feed3000/results.md) | Failed at N717; diagnostic pair and all histories preserved; no developed pre-failure checkpoint |
| 2, matched absorber ON | [New 3000-iteration trial](stage-02-fine-mesh-simple/absorber3000/results.md) | Fluent shutdown before N1000; N600 reopened; 18 histories recovered |
| 2, long OFF hold | [Cortex shutdown](stage-02-fine-mesh-simple/slow-enable3000/results.md) | Last printed N350; N300 reopened; absorber activation not reached |
| 2, early activation / steps | [Failed stepped trial](stage-02-fine-mesh-simple/step-enable2200/results.md) | Floating-point failure N518; absorber ON, 25% feed; failed pair preserved |
| 2, original 08b transfer | [Verified transfer](stage-02-fine-mesh-simple/08b-native997k/results.md) | Same 997k mesh; original 08b settings; N10000 retained; no new solves |
| 2, 08b settings / new997k OFF | [2,000-update continuation](stage-02-fine-mesh-simple/08b-native997k/run2000-off/results.md) | Divergence then SIGSEGV after printedN10022; only22 additional updates; N10000 start retained |
| 2, fresh08b settings/new997k OFF | [Native10,000 run](stage-02-fine-mesh-simple/08b-native997k/fresh-tui10000-off/results.md) | FreshHybrid;10,000 updates; save paired every1,000; native server journal |
