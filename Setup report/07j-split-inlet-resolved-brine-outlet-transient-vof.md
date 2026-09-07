# Split-Inlet Resolved Brine Outlet Transient VOF Qualification

## Purpose and current classification

Setup `07j` is the source-free successor to the failed steady Mixture branches
07h and 07i. It asks whether explicit physical time and liquid inventory can
produce bounded, phase-correct drainage through the resolved brine outlet.
Until both time-step and physical-window gates pass, every result is
`Diagnostic / unresolved`.

## Authoritative clean origin

- Mesh: `C:\Users\qtra338\Documents\Mesh study\Meshes\brine-outlet-620kcells.msh.h5`.
- SHA-256: `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`.
- Mesh: 620,431 cells, 16 partitions, minimum orthogonal quality `0.250003`, maximum aspect ratio `66.0258`.
- Settings authority: `C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set`.
- Phase materials: vapor primary `water-vapor-at-psep`, liquid secondary `water-liquid-at-psep`.
- Reference feeds: liquid `116.92 kg/s`, steam `80.69 kg/s`.
- Gravity `(0,-9.81,0) m/s2`, Energy off, RNG k-epsilon and WFGC enabled/read back.
- Fresh Hybrid Initialization followed by phase-2 liquid patch below geometry-inferred `y=0 m`.
- EWF and every sink/source UDF remain off. The imported case had global DPM
  interaction disabled, but a later forensic transcript audit proved that six
  inherited injections still tracked `6,456` one-way parcels. Setup 07j is
  therefore not strictly carrier-only evidence; setup 07l deletes the
  injections and disables unsteady tracking explicitly.

## Formulation and documentation basis

The new branch uses the pressure-based transient VOF model, explicit volume
fraction and Geo-Reconstruct. Fluent 2024 R2 documents explicit VOF as
time-dependent and Courant-limited, while Geo-Reconstruct is its most accurate
general-unstructured-mesh interface scheme. Initial startup uses first-order
implicit physical-time discretization, Sharp interface modeling, PISO
pressure-velocity coupling, fixed `1e-4 s` steps and at most 20 inner
iterations per step. These selections follow the Fluent 2024 R2
[VOF setup guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_mphase_using_steps_vof.html),
[multiphase formulation guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_setup.html),
and [VOF theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_vof_eq.html).
A later accepted branch must repeat a physical
window at `5e-5 s` and move to second-order time before any time-step-
independence claim.

Both steam and brine faces initially remain pressure outlets at `1.12 MPa`.
Steam backflow is vapor-only and brine backflow is liquid-only. This is a
controlled diagnostic bracket, not a validated downstream brine pressure.

## Guarded execution matrix

| Stage | Physical-time target | Step size | Maximum inner iterations | Decision |
|---|---:|---:|---:|---|
| preparation | `0 s` | — | — | require complete model, boundary, phase, gravity, WFGC and DPM-off readback |
| one-step smoke | `0.0001 s` | `1e-4 s` | 20/step | prove one complete time step before any block |
| startup A | `0.001 s` | `1e-4 s` | 20/step | stop on non-finite field, SIGSEGV/FPE, incomplete step or gross outlet flux |
| startup B | `0.005 s` | `1e-4 s` | 20/step | require bounded phase fractions and storage-aware phase balance |
| diagnostic window | `0.010 s` | `1e-4 s` | 20/step | decide whether extension is physically useful |
| conditional extension | `0.05-0.10 s` | `1e-4 s` | 20/step | only if preceding gates pass; save non-overwriting checkpoints |
| time-step sensitivity | matched accepted window | `5e-5 s` | 20/step | required before time-step independence can be claimed |

## Monitors and acceptance

For every checkpoint record residuals by time step/inner iteration; flow time;
all four boundary mixture/vapor/liquid mass flows; pressure drops; outlet and
domain velocity; vorticity; domain liquid volume fraction; liquid inventory;
and VOF Courant information where Fluent reports it.

Transient phase balance includes storage. For phase `q`, with Fluent boundary
flux positive into the domain,

```text
closure_q = dM_q/dt - sum(mdot_q,boundaries)
```

The raw steady imbalance is retained only for comparison; it is not the
transient conservation test. Startup is acceptable only when fields remain
finite, intended outlet directions establish without gross drainage, volume
fractions remain bounded, and storage-aware closure trends toward no more than
5% of feed. Formal carrier acceptance additionally requires no more than 1%
storage-aware closure over a statistically stable physical window, no more
than 0.5% primary-monitor drift, no more than 1% secondary/inventory drift,
and a matched `dt/2` sensitivity within 1% for primary metrics and 2% for
secondary metrics.

## Outputs

Local root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07j_transient_vof_equal_psep_v1/
```

Planned files are `preparation_manifest.json`, `preparation_transcript.trn`,
`qualification_manifest.json`, `qualification_transcript.trn`,
`residual_history.csv`, and `transient_physical_history.csv`. The qualification
manifest contains the storage-balance history, gross-gate decisions and exact
runtime-clock proof. Separate case/data pairs are written at `t0`, `0.0001`,
`0.001`, `0.005`, `0.010`, `0.050` and `0.100 s` where the guards permit them.

## Execution status — 19 August 2026

- The restarted server initially authenticated successfully as Fluent 2024 R2
  with exactly 16 solver ranks (`n0` through `n15`; `/20` is the workstation's
  hardware-core denominator, not a 20-process launch).
- Live probing established the release-specific control mapping: interface
  selector `0` is Sharp and changes the volume-fraction readback to
  `geo-reconstruct`; PISO is an allowed coupling scheme; transient controls are
  under `solution/run-calculation/transient-controls`.
- The first formal attempt reloaded the clean 620,431-cell mesh and stopped
  before initialization when the generated Settings-API `read_settings` RPC
  remained blocked for more than 11 minutes. The attempt was interrupted and
  preserved; it advanced zero physical time.
- The settings importer now prefers the project's established Fluent 2024 R2
  TUI `file/read-settings` path. The preparation driver and the new guarded
  transient controller compile, and ten focused local tests pass (process
  roster, inventory/storage closure, staged block schedule and gross-failure
  handling).
- After the blocked RPC was interrupted, the port remained open but Cortex was
  unobtainable and authentication stopped succeeding. The live process is
  therefore `unresolved / requires Fluent restart`; no retry will occur against
  that wedged process.

## Study-limiting unresolved issue

The downstream brine-system static pressure, imposed brine flow, resistance
curve and measured operating liquid level are all unavailable. Therefore an
equal-pressure result can qualify numerical behavior only. If the transient
pressure bracket drains or fills nonphysically, the next controlled option is
a strictly outward `116.92 kg/s` brine mass-flow-outlet diagnostic or a
measured downstream resistance/pressure condition; neither should be relabeled
as plant validation without supporting data.

## Execution result — 21 August 2026

Preparation ultimately passed on Fluent 2024 R2 with exactly 16 compute ranks.
The accepted time-zero pair came from the clean 620,431-cell mesh, complete
settings readback, fresh Hybrid Initialization and the `y<=0 m` liquid patch.
No production step was credited during preparation. EWF and every sink/source
remained off. Forensic correction: Fluent nevertheless tracked `6,456` parcels
from six inherited DPM injections. Interaction was off, so the parcels did not
couple momentum back to the carrier and are unlikely to explain the pressure
failure, but the earlier “no DPM tracked” statement was incorrect.

Hybrid Initialization also reported that pressure information was unavailable
at the boundaries and used constant-pressure initialization. The dense
`y<=0 m` liquid pool was patched afterward, so the first transient step did not
start from a hydrostatic liquid-pressure field. Setup 07l isolates this issue.

The equal-`1.12 MPa` pressure bracket failed its gross-drainage gate at physical
step 2 (`t=0.0002 s`). Brine liquid discharge was `-4692.8688 kg/s`, compared
with the `116.92 kg/s` liquid feed. This was not a reporting artefact: liquid
inventory changed at `-4576.4867 kg/s`, the net liquid boundary flux was
`-4575.9488 kg/s`, and their storage-aware closure residual was only
`-0.5379 kg/s` (`0.4601%` of feed). The pressure-bracket field was therefore
stopped and is not resumed.

The authoritative preserved states are the accepted time-zero pair and the
step-1 pair. A multi-step PyFluent request that returned early was separately
diagnosed; the controller now issues exactly one physical time step per RPC and
proves Fluent's time-step and flow-time clocks after every call. This evidence
does not validate separator performance or a downstream brine pressure.

Decision: the predefined strictly outward brine mass-flow diagnostic proceeds
as setup `07k`. It is a boundary sensitivity, not plant validation.
