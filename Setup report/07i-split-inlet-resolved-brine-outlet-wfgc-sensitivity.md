# Split-Inlet Resolved Brine Outlet WFGC Sensitivity

## Purpose and status

Setup `07i` is a one-factor numerical sensitivity following the setup-07h
floating-point failure. It tests Fluent's mesh-specific recommendation to use
Warped-Face Gradient Correction (WFGC) on the 620,431-cell polyhedral
brine-outlet mesh. It is not the final full-brine formulation and cannot
validate the equal-pressure steady boundary model.

- Study ID: `split_inlet_resolved_brine_outlet_20260813`.
- Run label: `brine620k_07i_pool_y0_equal_psep_wfgc_v1`.
- Parent: `07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md`.
- Terminal classification: `Diagnostic / catastrophic numerical failure`.
- DPM, EWF and numerical sink: off/absent.

## Execution status and evidence correction (2026-08-19 NZST)

Attempt 8 reached Fluent and completed the clean preparation sequence: the
620,431-cell mesh was loaded, authoritative settings were imported, WFGC read
back `enable=true, mode=fast`, DPM/EWF/sink remained off, the `y<=0 m` liquid
pool was patched after fresh Hybrid Initialization, and a separate initialized
case/data pair was saved.

The original process-count interpretation was wrong. Fluent's connectivity
table lists nodes `n0` through `n15`, which proves exactly 16 solver processes.
The `Core` value `16/20` means core 16 on a 20-hardware-core machine; `/20`
is not a process count. The Fluent title bar independently reads
`16-processes`. Attempt 8 is therefore a valid controlled 16-process WFGC
diagnostic.

The qualification then failed catastrophically during the first requested
25-iteration block. The transcript records continuity increasing from
`3.2024` at raw iteration 16 to `6.9888e14` at raw iteration 20. The supplied
GUI photograph records raw iteration 21, `Node 4 ... Received signal SIGSEGV`,
`connection reset`, and Fluent server shutdown. Zero complete blocks were
credited, no divergent checkpoint was written, and the initialized state is
not approved for resumption or an identical retry. WFGC did not stabilize the
steady equal-pressure initialized-pool formulation.

The runtime gate now parses node IDs from Fluent's documented parallel
connectivity report through the Settings API and separately records the
hardware-core denominator. It requires exactly nodes `n0..n15` before any
remote mutation. All 29 local tests pass. A read-only check on 2026-08-19
verified the restarted Fluent 2024 R2 session is healthy and again reports 16
solver processes on 20 hardware cores; no case is loaded and no controller is
active.

## Authoritative clean origin

- Mesh: `C:\Users\qtra338\Documents\Mesh study\Meshes\brine-outlet-620kcells.msh.h5`.
- Mesh SHA-256: `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`.
- Settings: `C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set`.
- Fluent 2024 R2, exactly 16 live compute nodes and 16 mesh partitions, fresh
  Hybrid Initialization.
- Initial pool: phase-2 `mp=1` in the read-back hexahedral register spanning
  `(-2.1,-1.5,-1.5)` to `(1.1,0,1.1) m`.

## Controlled difference from setup 07h

Immediately after settings import and before boundary readback or
initialization, execute Fluent's documented fast-mode WFGC command and require
the settings API to return `enable=True`:

```text
/solve/set/warped-face-gradient-correction/enable yes yes
```

No other geometry, material, model, boundary, initialization, convergence or
solver setting is intentionally changed. Fixed carrier setup remains steady
pressure-based Mixture, vapor primary/liquid secondary, RNG k-epsilon,
gravity `(0,-9.81,0) m/s2`, Energy off, SIMPLE/PRESTO, liquid/steam inlets
`116.92/80.69 kg/s`, steam/brine pressure outlets both `1.12 MPa`, and
minimum-phase-averaged operating density.

## Guarded execution and acceptance

1. Save and cold-reload a separate initialized case/data pair.
2. Require WFGC `enable=True` after cold reload.
3. Run 25 then 225 iterations; preserve iterations 25 and 250 separately.
4. At and after iteration 250, stop if brine liquid outflow exceeds three
   times liquid feed, mixture imbalance exceeds 100%, or liquid imbalance
   exceeds 200%. This prevents a repeat of setup 07h's finite-but-nonphysical
   iteration-250 state.
5. If the gross gate passes, continue in 250-iteration blocks. At iteration
   1000 require correct outlet directions, brine vapor carryunder no more than
   25% of vapor feed and steam liquid carryover no more than 10% of liquid
   feed before extending to 3000.
6. Final acceptance retains setup 07h's closure and stability gates: each
   phase/mixture imbalance no more than 0.5%, primary final-window drift no
   more than 0.5%, secondary velocity/vorticity/inventory drift no more than
   1%, correct directions and bounded residuals.

## Outputs

Local root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07i_pool_y0_equal_psep_wfgc_v1/
```

It contains preparation, supervisor and qualification manifests; transcripts;
settings/WFGC readbacks; residual and physical-monitor histories; and
non-overwriting initialized/25/250/500/1000/2000/3000 case-data pairs where
the guarded run reaches those points.

## Limitation and next decision

Setup 07i failed before the first complete block, so it provides no converged
flow metrics. It does establish that WFGC alone cannot rescue this steady
equal-pressure pool branch. Do not repeat or resume it. Move to setup `07j`:
transient sharp-interface VOF with explicit liquid inventory and a physically
defensible brine mass-flow, pressure or downstream-resistance boundary. Mesh
convergence, DPM and EWF remain closed until a conserved carrier solution is
demonstrated.
