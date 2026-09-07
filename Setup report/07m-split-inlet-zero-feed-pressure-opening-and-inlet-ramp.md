# Setup 07m — Zero-Feed Brine Pressure Opening and Guarded Inlet Ramp

## Status

`Diagnostic / pressure-opening bracket accepted; 0.1% inlet hold accepted; progressive ramp stopped at the 1% continuity gate; stale zero-step 1% hold preserved and not resumed`

This branch does not establish the plant brine pressure, a downstream
resistance curve, steady separator performance, mesh independence, DPM
carryover or EWF behavior.

## Purpose

Setup 07m opens the resolved brine face from the accepted hydrostatic-rest
lineage before any carrier feed is applied. It answers two bounded questions:

1. can the relaxed liquid pool tolerate conversion of `brineoutlet` from a
   wall to a liquid-backflow pressure outlet; and
2. can the carrier inlets be introduced gradually without recreating the 07j
   drainage failure or the 07k pressure/velocity failure.

## Authoritative Source

Every pressure-opening member is sourced independently from the setup-07l
qualification checkpoint at physical step 10:

```text
C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.cas.h5

C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.dat.h5
```

The source clock is step 10 at `1.0e-5 s`. No failed 07j/07k field,
uncheckpointed live field or 07l initialized time-zero field is used.

## Fixed Physics

- Fluent 2024 R2, 16 compute ranks, double precision;
- 620,431-cell resolved-brine-outlet mesh;
- transient explicit VOF, vapor primary and liquid secondary;
- RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off;
- PISO, PRESTO, Geo-Reconstruct, implicit body-force treatment and WFGC;
- steam outlet pressure `1,120,000 Pa`;
- user-input operating density equal to vapor density and reference-pressure
  location in the vapor region;
- zero DPM injection objects, interaction off and unsteady tracking off;
- no EWF and no numerical sink.

The opening matrix holds both phases at both inlets at `0 kg/s`. The brine
pressure outlet uses liquid backflow volume fraction `1.0`.

## Diagnostic Pressure Bracket

The centre is the area-weighted closed-face pressure observed at the accepted
07l rest state:

```text
p_center = 1,122,090.400 Pa
```

The bracket half-width is one reference-feed dynamic head:

```text
U_ref = 116.92 / (881.2108765 * 0.19936247) = 0.6655268 m/s
q_ref = 0.5 * 881.2108765 * U_ref^2 = 195.1556 Pa
```

| Member | Brine gauge pressure |
|---|---:|
| low | `1,121,895.244 Pa` |
| centre | `1,122,090.400 Pa` |
| high | `1,122,285.556 Pa` |

These values are a **CFD-derived closed-face modified-pressure rest bracket
(diagnostic)**. Fluent transforms pressure inputs under gravity. The values
must not be described as measured plant pressure, validated downstream line
pressure or a manual hydrostatic correction.

## One-Step Matrix

Each of the three pressures was crossed with independent one-step tests at:

```text
dt = 1e-6, 3e-6 and 1e-5 s
```

All nine members:

- loaded the same 07l step-10 parent;
- saved a separate opened-time-zero and post-step case/data pair;
- advanced Fluent's physical-step and flow-time clocks exactly once;
- remained finite and within every pressure, velocity, VOF, Courant, residual,
  DPM and phase-flux hard gate;
- had maximum Global Courant between about `1.14e-8` and `1.14e-7`.

The first step did not yet resolve a nonzero brine mass flux. The matrix was
therefore labelled individually bounded but response-pattern unresolved, and
the inlet ramp was withheld. Residual convergence or a small Courant number
alone was not used as proof of a correct outlet response.

## Ten-Step Opening Extension

The low, centre and high opened-time-zero cases were then each advanced for
ten independent `1e-5 s` steps. Step 1, 3 and 10 case/data pairs were saved.

| Pressure | Step-10 liquid brine flow | Step-10 brine velocity | Maximum reported Global Co |
|---|---:|---:|---:|
| low | `-0.00724149 kg/s` | `0.00120518 m/s` | `2.85e-6` |
| centre | `+0.00451280 kg/s` | `0.00120755 m/s` | `3.25e-6` |
| high | `+0.01626494 kg/s` | `0.00121358 m/s` | `3.64e-6` |

Fluent's sign convention is negative outward. The response is monotonic with
pressure, the endpoints bracket a sign change, and the centre flow is only
`0.00386%` of the `116.92 kg/s` reference liquid feed. No DPM tracking or
numerical-failure signature occurred. This promoted the centre-pressure
checkpoint to a guarded inlet-startup diagnostic.

## Inlet-Startup Findings

### Direct 1% start — rejected

At `1%` feed, `dt=1e-6 s`, 20 maximum inner iterations and three physical
steps, fields remained finite and Global Courant was `3.49e-4`. The brine
liquid response was outward at `-0.873924 kg/s`, but the final continuity
residual was `2.15676`. The gate stopped the branch and saved the case/data.

### 0.1% micro-start — under-converged at first, then accepted as a hold

The clean centre-pressure checkpoint was reloaded and the input was reduced to
`0.1%` with `dt=1e-7 s`.

- 20 maximum inner iterations: final continuity `0.215680` after three steps;
- 100 maximum inner iterations: final continuity `0.0269836` after three steps.

The residual tail decreased instead of diverging, so the finite 0.1%/100-inner
checkpoint was held for ten additional physical steps without increasing
flow. Continuity then decreased monotonically:

```text
0.0152229, 0.00910674, 0.00640736, 0.00486243, 0.00389506,
0.00322901, 0.00273747, 0.00237145, 0.00209430, 0.00186867
```

Final hold metrics:

| Metric | Value |
|---|---:|
| liquid inlet | `+0.116920 kg/s` |
| vapor inlet | `+0.080690 kg/s` |
| brine liquid | `-0.0830901 kg/s` |
| steam-outlet vapor | `-0.0809126 kg/s` |
| brine vapor | `0 kg/s` |
| domain velocity | `0.00369468 m/s` |
| brine velocity | `0.00122915 m/s` |
| final Global Courant | `3.46743e-6` |
| final continuity residual | `0.00186867` |

The step-1, step-5 and step-10 case/data pairs are preserved. This is accepted
only as a bounded `0.1%` startup hold, not as production operation.

### Why the residual trace is periodic

The repeating residual shape is the expected transient inner-iteration
pattern for this run. Each physical time step starts a new set of up to 100
inner iterations. Continuity rises when the new time level and boundary flux
are applied, then falls during the inner iterations; the next physical step
repeats the cycle. Periodicity by itself is therefore neither acceptance nor
failure.

For the accepted 0.1% hold, the pattern was healthy: the maximum continuity
within each successive physical step decreased from `0.48262` to `0.045257`,
and the end-of-step continuity decreased monotonically from `0.0152229` to
`0.00186867`. Global Courant simultaneously remained nearly constant and
decreased slightly from `3.4825e-6` to `3.46743e-6`. A periodic trace would be
rejected if its peak envelope or end-of-step residual grew, if it stopped
decaying within each step, or if physical monitors became unbounded or drifted.
The rejected direct 1% start demonstrates this distinction: it was finite and
also had a repeated transient pattern, but its final continuity was `2.15676`.

## Active Continuation

The accepted 0.1% step-10 checkpoint was progressed through `0.2%`, `0.5%`
and `1%`. Each level received ten `1e-7 s` physical steps with up to 100 inner
iterations, separate readback, a checkpoint and the same hard stops. The
`0.2%` and `0.5%` blocks completed without a hard-gate failure. The `1%` block
remained finite and bounded (`Co_max=3.48732e-5`, brine liquid
`-0.877498 kg/s`, steam-outlet vapor `-0.808819 kg/s`), but its final
continuity residual was `0.0177001`, above the `0.01` promotion limit. The
controller saved the 1% case/data, classified the branch
`diagnostic / unresolved`, and withheld every queued `2%`-to-`100%` stage.

Because the 1% field failed only the residual-promotion criterion and remained
finite and physically bounded, a separate guarded follow-up was launched from
the saved 1% checkpoint. The server-1 connection stalled before any new step
was credited, so its manifest is stale and the hold remains pending. The
planned hold keeps the same 1% inlet conditions for 20 further `1e-7 s` steps
with 100 inner iterations per step; it does not increase the flow. Its purpose
is to distinguish insufficient settling from a persistent 1% residual floor.
The unused attempt record is under
`progressive_hold_1pct_dt1e-7_inner100_steps20/`.

### Fluent-server use

Server 1 is the authoritative owner of the accepted setup-07l step-10 lineage
and the sequential setup-07m ramp. On 2026-08-21, server 2 was independently
confirmed healthy and running Fluent 2024 R2, but it could not see the setup-07l
step-10 case at server 1's remote Windows path. The ramp stages are also
sequentially dependent: each accepted fraction supplies the next fraction's
checkpoint. Splitting that chain across servers would change the lineage or
require copying and verifying the complete parent case/data on server 2.
Server 2 remains suitable for an independent sensitivity branch only after
the same parent checkpoint is transferred, its checksum/readback is verified,
and its live partition count is confirmed.

An independent server-2 Mixture comparison was subsequently run from the
case already loaded on that server, not from setup-07m lineage. Six inherited
DPM injections were removed, the resolved brine pressure was set to the
`1.12209 MPa` diagnostic value, a liquid-full brine backflow condition and
`y<=0 m` liquid pool were applied, and 16 ranks were verified. The branch
stopped at 150 steady iterations when brine liquid discharge increased to
`-1372.91 kg/s` and mixture imbalance to `-1247.64 kg/s`. This is a gross
drainage failure and must not be resumed. Iterations 50 and 100 plus the
verified iteration-150 failure state are preserved separately under
`server2_mixture_carrier_extension_20260821_resume1/`.

### Why the server-2 residual curve is a real instability

Unlike the setup-07m transient sawtooth, the server-2 branch was steady. It
has no physical-time-step reset that could legitimately create a repeated
residual envelope. Continuity instead worsened from `0.31664` at iteration 50
to `0.38956` at 100 and `0.53041` at 150. The phase and flow fields worsened at
the same time:

| Iteration | Continuity | Mixture net (kg/s) | Brine liquid (kg/s) | Brine velocity (m/s) | Domain velocity (m/s) | Domain liquid VF |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | `0.31664` | `-271.38` | `-390.10` | `2.999` | `7.787` | `0.1609` |
| 100 | `0.38956` | `-79.56` | `-197.03` | `6.459` | `10.096` | `0.1948` |
| 150 | `0.53041` | `-1247.64` | `-1372.91` | `11.017` | `14.467` | `0.2336` |

The brine area is `0.19936247 m2`; therefore the nominal full-feed bulk liquid
velocity is only `116.92/(881.2109*0.19936247)=0.66553 m/s`. The reported
brine velocity grew from `4.51` to `9.71` to `16.55` times that reference.
Reversed-flow warnings persisted at both pressure outlets and the number of
cells hitting the turbulent-viscosity limiter grew substantially. These
correlated trends establish a changing, non-converged phase/pressure field,
not merely a residual-display issue.

The strongest explanation is the combination of an incompatible startup and
an under-specified outlet model. Hybrid initialization explicitly used a
constant pressure because boundary pressure information was unavailable; the
dense liquid pool was then patched into that non-hydrostatic field. The steady
Mixture solver received the full feed immediately and a fixed brine pressure
that had been inferred from a closed-face transient rest state, not calibrated
for the flowing downstream brine line. With no modeled pipe/valve resistance
or level controller, the pressure outlet can drain the pool without a physical
flow-pressure feedback. High-order steady startup numerics amplify the
response but cannot repair that missing boundary physics.

### Recommended calculation sequence

1. Do not resume the server-2 iteration-150 field. Retain it only as a gross-
   drainage diagnostic.
2. Resume the saved setup-07m 1% transient checkpoint and hold the same flow,
   `dt=1e-7 s` and 100 inner iterations for 20 further physical steps. Save at
   5, 10 and 20 steps. Promote only after two consecutive end-of-step
   continuity values are at or below `0.01` with bounded Courant, VOF, outlet
   phase flows, velocity and liquid inventory.
3. If the 1% hold does not pass, run two one-factor numerical sensitivities
   from the same checkpoint: 200 inner iterations at `dt=1e-7 s`, then 100
   inner iterations at `dt=5e-8 s`. Do not change pressure or feed in those
   comparisons.
4. Once 1% passes, replace the coarse `1->2->5->10%` jumps with a smooth common
   physical-time inlet profile or closely spaced holds such as `1.5, 2, 3,
   5%`. Keep both phase feeds proportional and stop at the first growing
   end-of-step residual envelope.
5. Before calling any full-flow result physical, obtain the downstream brine
   pressure/head and pipe or valve resistance. Prefer explicitly modeling the
   downstream pipe/loss or a justified pressure-flow resistance. The
   `1.12209 MPa` value remains a CFD-derived rest diagnostic, not a validated
   production outlet boundary.
6. Keep the production path transient VOF with PISO, bounded explicit-VOF
   Courant control, hydrostatically relaxed initialization, DPM/EWF/sink off,
   and startup-order numerics. Only after the carrier field and liquid level
   remain stable should second-order sensitivities, mesh convergence and DPM
   be attempted.

## Output Location

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
brine620k_07m_pressure_opening_campaign_v1/
```

Important children are:

- `campaign_manifest.json` and `matrix_summary.csv`;
- `matrix/<pressure_dt>/case_manifest.json`, transcript and residual history;
- `opening_extension_10steps/`;
- `inlet_ramp/` for the rejected direct 1% start;
- `micro_inlet_ramp_dt1e-7_inner100/` for the three-step micro-start;
- `micro_inlet_hold_0p1pct_inner100/` for the accepted ten-step hold;
- `progressive_micro_ramp_dt1e-7_inner100/` for the active continuation.

## Interpretation and Limitations

Accepted evidence:

- the relaxed pool tolerates opening the brine face at the diagnostic pressure;
- the zero-feed response is finite, bounded and monotonic across the bracket;
- a 0.1% proportional inlet feed can be introduced and held with continuity
  below `0.01` when adequate physical and inner iteration settling is allowed.

Unresolved:

- the actual downstream brine static pressure and liquid-level datum;
- a pipe, valve or control resistance curve;
- whether the short micro-ramp remains stable at full feed and longer time;
- time-step and inner-iteration independence at operating flow;
- long-time pool-level/storage closure;
- mesh independence, separator efficiency, steam quality, DPM and EWF.

## Official Fluent Guidance Used

- [Pressure inputs and hydrostatic head, Fluent 2024 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_bcs_sec_bound_cond.html)
- [Multiphase operating density, Fluent 2024 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_setup.html)
- [Explicit VOF time controls, Fluent 2024 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_mphase_using_steps_vof.html)
- [Multiphase solution strategy, Fluent 2024 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_solution.html)

## 22 August 2026 continuation correction

The zero-step 1% hold attempt was preserved as
`progressive_hold_1pct_dt1e-7_inner100_steps20/ramp_manifest_attempt1_stale_zero_step_connection_timeout_20260822.json`.
The original `ramp_manifest.json` remains unchanged with status `running`, but
its PID/process audit proves that it is stale. It credited no blocks,
checkpoints or physical steps and must not be resumed.

The earlier recommended 20-step 1% hold is now an optional numerical
sensitivity only. Setup 07n has superseded it as the physical mainline because
07m's pool elevation, microsecond time window and `1,122,090.400 Pa` pressure
do not establish a controlled operating level or plant-valid downstream
condition. No additional setup-07m step was run on 22 August, and the server-2
steady Mixture field remains terminal and prohibited.

The subsequent setup-07n lower-face-proxy closed-drain pilot and its first
`dt` extension did not read or resume the setup-07m 1% field. They used zero
feed, a closed brine wall and fresh pool reconstruction from the setup-07l case
only. Their clean bounded result therefore changes neither the unresolved 07m
1% hold nor the status of `1,122,090.400 Pa`; both remain diagnostic only.

The later setup-07n exact whole-cell reconstruction and closed-drain trajectory
through `0.22271 s`, plus its matched base/half/quarter-`dt` window to `0.22783 s`,
also remained independent of setup 07m: they used zero feed, a brine wall and
the steam outlet as the sole pressure anchor. Inventory, VOF, pressure and
steam-seal evidence remained bounded, while half-to-quarter average velocity,
vorticity and maximum velocity changed `1.427%`, `1.404%` and `7.491%`. This
neither validates the 07m pressure,
operating level or 1% field nor establishes time-step independence. No
setup-07m physical step has been resumed.

The subsequent fixed-`dt` setup-07n inner-iteration discriminator improved
continuity by `99.70%` but reproduced the 20-inner velocity field within
`0.000009%`. It therefore rules out loose inner convergence as the source of
the 07n timestep discrepancy without changing any setup-07m conclusion.

Zero-iteration setup-07n localization then showed that base, half and quarter
timesteps share the same interfacial maximum cell and strongly overlapping
top-velocity region. That evidence narrows 07n's numerical issue but still does
not validate setup 07m's level, pressure, 1% field or constant-level behavior.

The subsequent matched setup-07n `dt/8` branch also passed its hard gates but
did not contract the velocity-field differences. Explicit timestep halving is
therefore stopped without changing or resuming any setup-07m field.

The subsequent setup-07n solver screen also remained fully independent of
setup 07m. It cold-loaded only the checksum-bound zero-feed closed-pool
step-940 parent and completed matched implicit-VOF/PISO and explicit plain-
Coupled branches. No 07m case/data was read, no inlet flow was introduced and
no brine outlet was opened. Second-order Modified-HRIC remained `6.831%`
different from explicit in maximum velocity, while plain Coupled reproduced
PISO within `0.000063%` at `3.234x` the summed solve-step wall time. These are
accepted closed-pool solver diagnostics only. They do not validate the 07m
`1,122,090.400 Pa` pressure, 1% checkpoint, operating level or constant-level
behavior, and no setup-07m physical step has been resumed.
