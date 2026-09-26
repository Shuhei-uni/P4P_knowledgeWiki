# Autonomous convergence investigation — G6 complete, E7 selected

G1–G6 establish no qualified case. [G6](coupled-nphase/results.md) completed the N-phase-only contrast at N5000 with all evidence and six native images verified. Relative to E5, late mean-absolute liquid/vapor/native-mixture closure errors change148.115/2.132/86.795→144.369/1.520/84.841%, inventory change19.333→18.451%, continuitymaximum2.5817→1.3259. Residual improvement did not restore conservation or stationary inventory. E6 final is preserved and was restored after native spatial exports.

The selected next contrast is [E7 weaker sink under unchanged Coupled/N-phase](coupled-nphase-weaker-sink/setup.md): tau0.02→0.10s only, original common clean N0/Hybrid physical fields, absolute5000cap. This probes source-strength sensitivity in the E6 solver context; earlier E2tau.10 used SIMPLE. It changes the removal timescale and cannot establish an implicit-source derivative or validate originaltau. Exact E6 control/source assignment parity, tau-only expressions and N0/N50 gates precede normal execution. Phase-state owns live progress.

The source/source-equation interaction remains prominent because E6 native removal averages275.962kg/s versus116.921kg/s liquidfeed while inventory grows. N-phase raw/normalized reporting is now independently verified but its rawphase sumdefects remain visible; normalization is not mass closure. An unchanged long extension has no evidence-based justification. Global pseudo time or startup remains a broader alternative. Fully coupled VF is unavailable with retained Mixture slip under v252 guidance; no drift-model change is selected.

The [Shuhei audit](shuhei-audit.md) remains unchanged: lower displayed residuals coexist with approximately20.8% reported terminal liquid error; source/startup/geometry differ and raw foreign histories are unavailable locally. [G3](../spike-diagnostic/results.md) proved deterministic replication and sampled original hotspot locations.

E4 supports algorithm sensitivity of extreme bursts, but its persistent source-inclusive error leaves source/phase coupling and startup explanations open. CFL20 reduced closure error but worsened inventory drift; E6 now tests the phase-equation treatment. The documentation does not establish an API-only implicit-expression source derivative switch; no such capability is assumed. See E5 setup for the primary source sections and transfer limits.

Competing explanations remain ranked for discriminating tests:

1. Pressure/velocity–phase–turbulence amplification near the inlet: sampled
   late original maxima are far above the collector; E4 suppresses the extreme bursts but fails closure. E5 confirms damping sensitivity without steady closure.
2. Indirect source coupling or phase/source accounting: weaker tau did not
   restore closure, and source lag is exact. A lower residual with a large
   source-inclusive budget error would keep this explanation prominent.
3. Startup/developed-parent sensitivity: Shuhei's field has a low-feed hold
   and ramp history. E3's saved N0 snapshot already has a maximum speed of
   372.622 m/s at (−0.771474, 1.709912, −0.737360) m with zero domain liquid.
   That is a Hybrid initial field, not a converged gas-flow result, and its
   maximum is distinct from the sampled late-event locations. It establishes
   that high initialization speeds precede liquid accumulation; it does not
   prove the cause of late bursts. E4 intentionally preserves this field.
4. Local mesh/gradient/transport sensitivity: still plausible; proximity to
   the inlet elevation and facet variation do not establish poor cell quality.
5. Recorder artifact: weakened by exact independent E3/original-T020 agreement
   and native-field/report parity, but not a general exclusion of all errors.

The N0 observation is from
`PyAnsys/output/p7b-s40-t020-diag-20260922T071533Z/spike-diagnostics/fields-n00000.json`.
The prior E6 selection is complete. Startup, pseudo-time or source changes remain alternatives requiring their own prospective evidence-backed contrast; these rankings are not a parallel queue.
