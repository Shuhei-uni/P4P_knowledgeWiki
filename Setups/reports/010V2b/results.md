# Diagnostic Results Report — Setup 010V2b

## Setup link and run identity

- Setup definition: [010V2b — EWF Edge-Separation Sensitivity](../../active/010V2b-ewf-edge-separation.md)
- Parent setup: [010V2 — EWF deposition and film-inventory control](../../active/010V2-ewf-deposition-film-inventory.md)
- Fluent server and version: server `1`, `Ansys Fluent 2025 R2`
- Analysis date: `2026-07-22`
- Case/data state: analysis used the already-loaded session. The read-only workflow did not expose the case/data filenames.
- Evidence class: `partial diagnostic`; this is not a completed edge-separation result.

## 1. Analysis applicability and live audit

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual/flux checks | Not available | No carrier monitor or flux extraction was produced in this analysis run. |
| EWF audit | Completed with adapter limitation | `wall` is the only detected film wall; `bottom` is not a film wall. The Fluent 2025 R2 Settings API did not expose the top-level EWF branch. |
| EWF final-state snapshot | Incomplete | The snapshot client returned without its required report, raw-results, flux, and bookkeeping bundle. |
| DPM fate analysis | Incomplete | All six live injections were discovered; only the `5.63 µm` track completed before the client stopped without partial or final artifacts. |
| EWF edge separation | API readback-limited; operator confirmed On | `wall` reports `allow_film_boundary_separation = true`; the unavailable top-level EWF branch prevents adapter confirmation of the global setting and its parameters. |
| Splash / stripping | Not available | No valid top-level EWF mechanism readback was available; they are not reported as zero. |

The audit confirms that `wall` uses the `stanton-rutland` impingement model and has `allow_film_boundary_separation = true`. `bottom` remains a non-film `trap` wall. Global DPM interaction with the continuous phase is `Off`, unsteady particle tracking is `Off`, and maximum DPM steps is `10000`, matching the branch's required DPM corrections.

Six original liquid-DPM injections were present at `steaminlet`: `5.63`, `28.14`, `56.27`, `112.54`, `168.81`, and `348.88 µm`, with respective represented flows of `0.0380130`, `0.1560534`, `0.1940664`, `0.3901335`, `0.3901335`, and `4.6776003 kg/s`. No automatically created edge-separation injection was discovered by the live DPM audit.

## 2. DPM Particle Tracks Summary — partial evidence

Fluent completed the Particle Tracks Summary completion gate for the original `water-liquid-at-psep-5um` injection before the diagnostic client ended while beginning the `28.14 µm` injection. The console printed the required `number tracked` line and a Mass Transfer Summary, but the runner did not create its required transcript, per-injection raw file, or CSV/JSON bundle. The row below is therefore retained as partial console evidence only.

| Diameter (µm) | Injection | Net flow (kg/s) | Tracked | Escaped | Trapped | Incomplete | Final absorbed | Closure status |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| `5.63` | `water-liquid-at-psep-5um` | `3.801e-02` | 2170 | 2168 | 1 | 1 | not printed | Counts close exactly; mass closure cannot be certified from rounded console-only values. |

For that first injection, Fluent printed terminal mass-flow rows of `3.798e-02 kg/s` escaped, `1.752e-05 kg/s` trapped, and `1.752e-05 kg/s` incomplete. No absorbed or splash event row was printed. These omissions are `Not available`, not zero. No fate, mass-transfer, separation, or splash conclusion is made for the remaining five injections.

## 3. EWF final-state results

No final-state EWF quantity is reported. The snapshot client connected to server `1` but returned before producing any of its expected output set. Consequently, film Courant number, film inventory, thickness, DPM-to-film source, film outflow, film velocity, and Film Separated Mass are all `Not available` for this checkpoint.

The attempted snapshot must not be used to infer zero film, zero film outflow, or zero separated mass. A single successfully captured final snapshot would still be `bookkeeping-only`; it would not establish a time-integrated EWF closure.

## 4. Interpretation, limitations, and next action

**Measured:** the live audit confirms one film wall (`wall`), permitted boundary separation at that wall, the six original DPM injections, and global DPM interaction `Off`. One original 5.63 µm DPM track is escape-dominant by count (`2168/2170` escaped).

**Derived:** none beyond the count statement above. The rounded console mass-flow values are insufficient to claim a closed DPM mass balance.

**Unresolved:** the live readback parameters for global EWF edge separation; whether film reached an intended geometric edge; film inventory/outflow/separated mass; the identity and represented mass of generated separation parcels; all five remaining injection summaries; carrier residuals and phase-flux balance. The Fluent 2025 R2 EWF settings-adapter gap and both missing diagnostic bundles are recorded limitations.

**Needs follow-up.** Keep `010V2b` active and diagnostic. Before interpreting edge separation, repair or adapt the 2025 R2 diagnostic runner so it persists snapshot and DPM partial/final artifacts, then capture a full six-injection sweep and EWF histories over a defined interval.

## Machine-readable evidence

- [EWF/DPM live audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-audit-20260722/model_audit.json)
- [Audit run manifest](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-audit-20260722/run_manifest.json)
- [Audit raw results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-audit-20260722/raw_results.json)
- [Audit bookkeeping payload](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-audit-20260722/bookkeeping.json)

The attempted `010V2b-snapshot-20260722` and `010V2b-dpm-20260722` bundles were not produced; no link is supplied for nonexistent artifacts.

## 5. Retry evidence — 2026-07-22

The operator confirmed in Fluent that **Edge Separation is On** for this `010V2b` session. The Fluent 2025 R2 Settings API adapter still cannot expose the top-level EWF branch, so this is retained as operator-confirmed configuration evidence rather than a second API readback. The repeat audit independently confirms that `wall` remains the only film wall and reports `allow_film_boundary_separation = true` on that wall.

### Retry snapshot result

The final-state EWF snapshot was retried on server `1` with a fresh branch-specific `ewfdiag-010v2b-retry` prefix. It again connected to Fluent but exited before its audit phase, before creating a local output directory, and before attempting report-definition creation. No Python exception, Fluent error, or local crash artifact was emitted. This rules out reuse of an earlier diagnostic report name as the immediate cause, but does not identify the underlying client/process or gRPC-session failure.

Accordingly, Film Courant number, film mass and thickness, Film DPM Mass Source, film outflow, film velocity, and Film Separated Mass remain `Not available`. The absence of a snapshot payload must not be interpreted as zero film or zero separation.

### Carrier flux and residual retry

The independent carrier checks completed successfully against the already-loaded session.

| Quantity | Value | Interpretation limit |
|---|---:|---|
| Liquid-inlet phase flow | `111.074 kg/s` | phase-specific Fluent flux |
| Vapor-inlet phase flow | `80.690 kg/s` | phase-specific Fluent flux |
| Steam-outlet liquid-phase flow | `0 kg/s` | scoped outlet value only |
| Steam-outlet vapor-phase flow | `81.420448 kg/s` | scoped outlet value only |
| Derived phase efficiency | `1.000` | not full separator validation |
| Derived steam-outlet dryness | `1.000` | not full separator validation |
| Derived mixture imbalance | `110.343552 kg/s` (`57.54%` of inlet mixture flow) | mixture mass-flow report unavailable; prevents a conservation claim |

The residual export contains seven curves and `998` points over monitor iterations `2`–`1498`. At the final point, continuity is `1.917e-3`, `k` is `5.306e-3`, epsilon is `7.746e-3`, and liquid volume fraction (`vf-phase-2`) is `1.342e-3`. The residual decline is useful numerical-state evidence, but the large phase-derived mass imbalance means the carrier field is not accepted here as converged or mass-balanced.

### Retry evidence files

- [Retry EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-retry-audit-20260722/model_audit.json)
- [Retry audit run manifest](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-retry-audit-20260722/run_manifest.json)
- [Carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2b-retry-20260722-flux-check.json)
- [Residual check](../../../PyAnsys/output/post_simulation_analysis/010V2b-retry-20260722-residual-check.json)
- [Residual-history plot](../../../PyAnsys/output/post_simulation_analysis/010V2b-retry-20260722-residual-check.png)

## 6. Completed Fluent-console checkpoint — `010V2-b-1498`

The following evidence was supplied as a Fluent console transcript after the earlier server-1 automation attempt. It is retained as a separate checkpoint because the transcript does not include a server/session identifier. The repeated blocks in the supplied transcript were internally consistent; values below are transcribed once.

### Run identity and mesh

| Item | Value |
|---|---:|
| Fluent version | `ANSYS Fluent 2025 R2.03` |
| Case file | `010V2-b-1498.cas.h5` |
| Data file | `010V2-b-1498.dat.h5` |
| Cell type | tetrahedral |
| Cells / faces / nodes | `7,601,261` / `15,293,724` / `1,309,312` |
| Cell zones / face zones | `1` / `6` |
| Original mesh partitions | `18` |
| Compute nodes used | `1` |
| Licensed parallel capacity | `4-way` |

The case was loaded from an 18-partition mesh onto one compute node. The transcript does not identify the Fluent server ID, so this checkpoint is not attributed to server 1 or any other server.

### Analysis applicability

| Analysis | Status | Evidence / limitation |
|---|---|---|
| Carrier boundary mass flow | Completed | Mixture and phase-specific boundary table supplied. |
| Carrier residual history | Not included in supplied transcript | No residual curve values were provided in this checkpoint. |
| DPM fate analysis | Completed | All six diameter classes have counts, terminal zones, and mass-flow rows. |
| EWF final-state snapshot | Completed with field omissions | Film mass, thickness, CFL, velocity components, outflow, and film boundary flow were reported. |
| EWF history / closure | Deferred | A single final-state checkpoint is bookkeeping-only. |
| Edge separation | Active by reported DPM outcome | `120` separated particles were reported for the `348 µm` class. |
| Splash / stripping | Not reported | No splash or stripping result is supplied; omitted mechanisms are not treated as zero. |

### EWF final-state results

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Maximum film Courant number | facet maximum | `0.0032316204` | — | final-state numerical diagnostic |
| Total film mass | sum | `0.056390628` | kg | current inventory |
| Maximum film thickness | facet maximum | `0.00012282519` (`122.825 µm`) | m | local maximum |
| Area-weighted film thickness | area-weighted average | `9.5518384e-7` (`0.955184 µm`) | m | distributed average |
| Film outflow mass | sum | `0` | kg | reported final-state value |
| Average film X velocity | area-weighted average | `0.050916318` | m/s | component |
| Average film Y velocity | area-weighted average | `0.00065094323` | m/s | component |
| Average film Z velocity | area-weighted average | `0.014724906` | m/s | component |
| Average velocity-vector magnitude | derived from components | `0.0530068` | m/s | derived, not a Fluent magnitude reduction |

The maximum film thickness is highly localized relative to the `0.955184 µm` area-weighted average. Film mass flow was `0 kg/s` at `liquidinlet`, `steaminlet`, and `steamoutlet`, with net `0 kg/s`. These final values do not establish an interval-based EWF mass closure.

`Film DPM Mass Source`, average film-velocity magnitude, and maximum film-velocity magnitude were not reported because the requested identifiers were invalid for Fluent 2025 R2. The transcript identifies the valid internal names as `film-dpm-mass-src` and `film-velocity-mag`. Repeated `phase cannot be edited` warnings left the reports computed under the existing `mixture` phase.

### DPM fate counts

| Diameter (µm) | Tracked | Escaped | Escaped % | Absorbed | Absorbed % | Trapped | Trapped % | Incomplete | Separated |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `5` | 2170 | 2168 | `99.91%` | 0 | `0.00%` | 1 | `0.05%` | 1 | 0 |
| `28` | 2170 | 2163 | `99.68%` | 6 | `0.28%` | 1 | `0.05%` | 0 | 0 |
| `56` | 2170 | 2017 | `92.95%` | 148 | `6.82%` | 5 | `0.23%` | 0 | 0 |
| `112` | 2170 | 1512 | `69.68%` | 643 | `29.63%` | 15 | `0.69%` | 0 | 0 |
| `168` | 2170 | 1039 | `47.88%` | 1106 | `50.97%` | 25 | `1.15%` | 0 | 0 |
| `348` | 2290 | 542 | `23.67%` | 1705 | `74.45%` | 43 | `1.88%` | 0 | 120 |

Escaped particles were reported at `steamoutlet`; trapped particles were reported at `bottom`. For the `348 µm` class, the supplied transcript reports `2290` tracked and separately reports `120` separated, while the displayed fate categories sum to `2410`. This count inconsistency is preserved as unresolved; separated events/parcels must not be added to terminal fates without a clarified Fluent definition.

### DPM mass-flow results

| Diameter (µm) | Total flow (kg/s) | Escaped flow (kg/s) | Absorbed flow (kg/s) | Trapped flow (kg/s) | Incomplete flow (kg/s) |
|---:|---:|---:|---:|---:|---:|
| `5` | `0.03801` | `0.03798` | `0` | `1.752e-5` | `1.752e-5` |
| `28` | `0.1561` | `0.1555` | `0.0004315` | `0.00007191` | `0` |
| `56` | `0.1941` | `0.1804` | `0.01324` | `0.0004472` | `0` |
| `112` | `0.3901` | `0.2718` | `0.1156` | `0.002697` | `0` |
| `168` | `0.3901` | `0.1868` | `0.1988` | `0.004495` | `0` |
| `348` | `4.685` | `0.9849` | `3.610` | `0.09053` | `0` |

All values are `kg/s`; percentages in the supplied transcript were calculated from rounded Fluent values. Escape dominates the fine classes, while wall-film absorption becomes the dominant reported mass fate from `168 µm` upward. Average elapsed times were also reported: escaped particles increased from `1.414 s` at `5 µm` to `1.716 s` at `348 µm`, while absorbed particles ranged from `1.606 s` at `28 µm` to `0.1902 s` at `168 µm` (no absorbed value was printed for `5 µm`).

### Continuous-phase boundary flow

| Phase | Liquid inlet (kg/s) | Steam inlet (kg/s) | Steam outlet (kg/s) | Net (kg/s) |
|---|---:|---:|---:|---:|
| Mixture | `+111.074` | `+80.690` | `-81.420448` | `+110.34355` |
| Phase 1 | `0` | `+80.690` | `-81.420448` | `-0.73044835` |
| Phase 2 | `+111.074` | `0` | `0` | `+111.074` |

The large positive mixture net is dominated by phase-2 liquid inflow with no phase-2 outlet flow in the supplied report. This indicates accumulation, incomplete convergence, or a phase/boundary reporting issue and prevents a global mass-conservation claim.

### Interpretation and conclusion

**Measured:** the supplied checkpoint reports a `0.056390628 kg` film inventory, `122.825 µm` local maximum thickness, `0.955184 µm` area-weighted thickness, zero reported film boundary flow, complete DPM tables for six diameters, and `120` reported separated particles for `348 µm`.

**Derived:** reported wall-film absorption increases with diameter, reaching `3.610 kg/s` (`77.05%` of the rounded `348 µm` injection flow). The film is spatially localized because the maximum thickness is much larger than its area average.

**Unresolved:** time-integrated EWF closure, Film DPM Mass Source, Fluent magnitude reductions, residual history for this exact checkpoint, the `348 µm` separated-count inconsistency, and the mixture mass imbalance. No claim is made that separated particles are an additional terminal mass sink.

**Needs follow-up.** Keep `010V2b` diagnostic. Correct the Fluent 2025 R2 field identifiers, capture report histories before a rerun, clarify the separated-particle count definition, and resolve the large carrier-phase imbalance before using the result for separator-performance or EWF-conservation claims.

## 7. Requested 5000-iteration checkpoint — server 3 connection attempt (2026-07-23)

The operator identified the already-loaded Fluent state as having completed `5000` iterations and requested the same post-simulation analysis against **server `3` only**. This is a requested checkpoint label, not a live readback: the local PyFluent client could not establish a TCP connection to the configured server-3 endpoint before it reached Fluent.

### Commands attempted

| Analysis | Run label | Result |
|---|---|---|
| Connection preflight | — | Failed before authentication or session attachment. |
| EWF/DPM audit | `010V2b-5000-audit-20260723` | Failed at the same TCP preflight; no audit bundle was created. |
| EWF final-state snapshot | `010V2b-5000-snapshot-20260723` | Failed at the same TCP preflight; no report definition or result was created. |
| Full DPM sweep, diameter ascending | `010V2b-5000-dpm-20260723` | Failed at the same TCP preflight; no particle tracking or transcript was created. |

All commands used `--server-id 3`. The configured address was `10.104.145.174:64162`; PyFluent raised `InvalidIpPort: Provide a valid 'ip' and 'port'.` Its underlying local socket test reports this error when the configured IP/port cannot be opened. The address and port fields themselves were present and parseable, so this records a reachability failure, not evidence of an invalid Fluent case or analysis setting.

### Analysis applicability at this checkpoint

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual/flux checks | Not available | Server 3 was not reached, so no 5000-iteration carrier values could be read. |
| DPM fate analysis | Not available | The DPM runner stopped before it could discover injections or submit a track command. |
| EWF audit/snapshot | Not available | The snapshot runner stopped before it could inspect the loaded wall-film state or create its namespaced reports. |
| EWF history/closure | Deferred | No live checkpoint or history payload was available. |
| Edge separation comparison to `010V2-b-1498` | Deferred | No new measured count, separated mass, film inventory, or flux was obtained. |

**Measured:** the three server-3 diagnostic commands were launched and each failed before Fluent access. No state-changing command reached the loaded case/data session.

**Derived:** none. The `010V2-b-1498` results in the preceding section remain the last completed quantitative checkpoint; they must not be presented as 5000-iteration values.

**Unresolved:** 5000-iteration carrier residuals and phase fluxes; EWF film mass, thickness, CFL, source/outflow, and separated mass; all DPM fates and mass closures; and the requested change from the 1498-iteration checkpoint.

**Next action:** refresh or expose the active Fluent gRPC address/port for server `3`, then rerun this same audit → snapshot → complete DPM sweep sequence. If the terminal connected to Fluent can supply its console output or fresh server-info details, attach/paste them so this report can be completed without reusing another server.

## 8. Completed 5000-iteration checkpoint — server 3 (2026-07-23)

This supersedes the unavailable-data status in section 7. The operator identified the loaded state as the `5000`-iteration checkpoint; the exported residual monitor ends at index `4999` (the monitor's stored indexing). All analysis commands used **server `3` only** and the already-loaded case/data pair. Fluent reported `Ansys Fluent 2025 R2`; case/data filenames were not exposed by the read-only workflow.

Execution was sequential: audit → final-state EWF snapshot → full diameter-ascending DPM sweep → carrier flux → residual export. Each completed command was observed for `360 s` after launch/completion, with its expected output files checked at one-minute intervals before the next command started.

### Analysis applicability

| Analysis | Status | Evidence / limitation |
|---|---|---|
| Carrier flux and residual checks | Completed | Phase flux and seven residual curves captured; mixture mass-flow report remains unavailable. |
| DPM fate analysis | Completed | All six discovered injections met the transcript completion gate and have raw per-injection reports. |
| EWF audit and final-state snapshot | Completed with adapter limitations | `wall` is the active film wall and permits film-boundary separation; DPM source and velocity-magnitude field aliases were rejected by the 2025 R2 adapter. |
| EWF history / closure | Deferred | One final state supports bookkeeping only, not a time-integrated closure. |
| Edge separation | Active by runtime evidence | The `348.88 µm` raw DPM transcript reports `171` separated events/particles. Its represented separated mass was not captured. |
| Splash / stripping | Not available / not applicable | No splash count was printed; stripping is not enabled by this branch and is not reported as zero. |

### Carrier field and numerical state

| Quantity | 1498 checkpoint | 5000 checkpoint | Interpretation |
|---|---:|---:|---|
| Liquid inlet flow | `111.074 kg/s` | `111.074 kg/s` | phase-2 inlet flow |
| Steam-outlet vapor flow | `81.420448 kg/s` | `81.417704 kg/s` | phase-1 outlet flow |
| Phase-derived mixture imbalance | `110.343552 kg/s` (`57.54%`) | `110.346296 kg/s` (`57.54%`) | effectively unchanged; prevents a global conservation claim |
| Final continuity residual | `1.917e-3` | `7.405e-3` | `3.86×` higher |
| Final `k` residual | `5.306e-3` | `6.318e-2` | `11.91×` higher |
| Final epsilon residual | `7.746e-3` | `1.592e-1` | `20.56×` higher |
| Final liquid-volume-fraction residual | `1.342e-3` | `1.398e-3` | `1.04×` higher |

The residual export contains `999` points over indices `256`–`4999`. The residual state has worsened relative to the 1498 checkpoint, while the large phase-derived flow imbalance persists. These fields are therefore numerical-state diagnostics, not evidence of carrier convergence or separator validation.

### EWF final-state comparison

| Quantity | 1498 checkpoint | 5000 checkpoint | Change / limit |
|---|---:|---:|---|
| Maximum film Courant number | `0.00323162` | `0.0109636` | `3.39×` higher; still a final-state numerical diagnostic |
| Total film mass | `0.0563906 kg` | `0.2054263 kg` | `+0.149036 kg` (`3.64×`) current inventory |
| Maximum film thickness | `122.825 µm` | `450.151 µm` | `3.67×` higher local maximum |
| Area-weighted film thickness | `0.955184 µm` | `3.479654 µm` | `3.64×` higher distributed average |
| Film outflow mass | `0 kg` | `0 kg` | Fluent-reported final-state quantity, not a rate or interval balance |
| Boundary film mass flow | `0 kg/s` at all three boundaries | `0 kg/s` at all three boundaries | `liquidinlet`, `steaminlet`, `steamoutlet`; not a closure |
| Area-average film velocity components | `x=0.05092`, `y=0.000651`, `z=0.01472 m/s` | `x=0.14821`, `y=-0.001623`, `z=0.05674 m/s` | components only; magnitude report was unavailable |

The snapshot did not obtain `Film DPM Mass Source`, velocity-magnitude reductions, or `Film Separated Mass`. The live allowed-value list identifies the valid Fluent 2025 R2 aliases as `film-dpm-mass-src` and `film-velocity-mag`; the current runner still requested unsupported aliases. In addition, its global EWF adapter marked the optional separation field inactive despite the wall-level readback and the raw DPM separation event. Consequently, no separated mass is inferred from the event count, and the snapshot remains `bookkeeping-only`.

### DPM Particle Tracks Summary — complete sweep

All terminal mass-flow rows close within Fluent's printed precision (absolute relative residual at most `2.16e-4`). `Absorbed` is a terminal fate; the EWF absorbed-event count is retained separately. The `171` separated value below is a secondary event/parcel diagnostic from the raw `348.88 µm` transcript, not an additional terminal mass sink.

| Diameter (µm) | Net flow (kg/s) | Tracked | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Separated events | Closure relative residual |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `5.63` | `0.03801` | 2170 | 2163 | 0 | 7 | not printed | not printed | not printed | `-6.84e-5` |
| `28.14` | `0.15610` | 2170 | 2151 | 5 | 4 | 10 | 10 | not printed | `2.15e-4` |
| `56.27` | `0.19410` | 2170 | 1930 | 48 | 1 | 191 | 191 | not printed | `1.94e-4` |
| `112.54` | `0.39010` | 2170 | 1295 | 66 | 0 | 809 | 809 | not printed | `7.69e-5` |
| `168.81` | `0.39010` | 2170 | 854 | 43 | 0 | 1273 | 1273 | not printed | `-7.95e-5` |
| `348.88` | `4.70200` | 2341 | 236 | 79 | 2 | 2024 | 2024 | 171 | `8.44e-5` |

Escaped terminal particles exit at `steamoutlet`; trapped particles are at `bottom`. At `348.88 µm`, the new terminal counts sum exactly to the tracked count (`236 + 79 + 2 + 2024 = 2341`), while separation remains separately reported. The dominant `348.88 µm` mass-flow fates are `4.264 kg/s` absorbed, `0.2952 kg/s` escaped, `0.1424 kg/s` trapped, and `3.211e-6 kg/s` incomplete, against `4.702 kg/s` net injection.

Relative to the 1498 checkpoint, escape counts fell and absorbed/trapped counts rose across the coarse classes. The `348 µm` result changed from `542` escaped / `1705` absorbed / `43` trapped / `120` separated to `236` escaped / `2024` absorbed / `79` trapped / `171` separated. Its absorbed flow rose from `3.610` to `4.264 kg/s`, while escaped flow fell from `0.9849` to `0.2952 kg/s`. This supports increased wall-film interception at this later checkpoint, but not a separated-particle mass balance.

### Interpretation and next action

**Measured:** the 5000-iteration checkpoint has a substantially larger film inventory and thickness, a complete six-injection DPM sweep, and `171` raw-transcript separation events for the largest diameter. Coarse DPM parcels are more absorption-dominant than at the 1498 checkpoint.

**Derived:** film inventory, maximum thickness, and area-average thickness are each approximately `3.64×` their 1498 values. The DPM terminal flow closures are within output precision; separated events are deliberately excluded from those closures.

**Unresolved:** time-integrated EWF conservation; generated separation-parcel mass and eventual fate; Film DPM Mass Source; velocity magnitudes; confirmed global splash/edge/stripping API readback; and carrier convergence/mass balance. The elevated residuals and persistent `57.54%` phase-derived imbalance keep this result diagnostic.

**Next action:** repair the Fluent 2025 R2 report-field aliases, then create EWF history files before continuing the solve so the next checkpoint can distinguish film storage, DPM source, outflow, and separated mass over a defined interval. Do not use this checkpoint for separator-performance validation until the carrier balance is resolved.

### Machine-readable evidence — 5000 checkpoint

- [Server-3 EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-audit-20260723-r2/model_audit.json)
- [EWF final reports](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-snapshot-20260723-r2/final_reports.csv), [film-boundary fluxes](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-snapshot-20260723-r2/film_flux.csv), and [snapshot raw results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-snapshot-20260723-r2/raw_results.json)
- [DPM injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-dpm-20260723-r2/dpm_injection_summary.csv), [zone/mass-flow summary](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-dpm-20260723-r2/dpm_zone_summary.csv), and [complete DPM transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-dpm-20260723-r2/dpm_particle_track_transcript.txt)
- [348.88 µm raw DPM report](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-dpm-20260723-r2/dpm_raw/03-water-liquid-at-psep-348um.txt)
- [Carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2b-5000-20260723-flux-check.json), [residual check](../../../PyAnsys/output/post_simulation_analysis/010V2b-5000-20260723-residual-check.json), and [residual plot](../../../PyAnsys/output/post_simulation_analysis/010V2b-5000-20260723-residual-check.png)

## 9. Fresh requested 5,000-iteration capture — operator-reported iteration 4,999 (2026-07-27)

The operator identified the already-loaded server-3 state as iteration `4999`, requested as the 5,000-iteration checkpoint. All successful live commands used **server `3` only**. Fluent reports `Ansys Fluent 2024 R2`, whereas the prior completed 5,000-checkpoint section records 2025 R2. Case/data filenames remain unavailable, so the two records are not a version-controlled identity comparison.

### Analysis applicability and evidence

| Analysis | Status | Evidence / limitation |
|---|---|---|
| EWF/DPM audit | Completed | `wall` is the confirmed film wall; six original liquid-DPM injections were discovered. |
| EWF final-state snapshot | Completed with adapter limitations | Film inventory, thickness, CFL, components, flux, and bookkeeping payload exist. DPM-source and velocity-magnitude aliases remain unsupported. |
| DPM fate analysis | Completed | All six injections passed the transcript completion gate; each has a raw report and final CSV/JSON output. |
| Edge separation | Runtime evidence for largest class | The `348.88 µm` raw DPM transcript reports `171` separated events/particles. No represented separated mass was captured. |
| Carrier flux and residual history | Not available | The server-3 extractor client returned after connecting but did not write either expected artifact during more than 320 seconds of supervision. No earlier carrier/residual values are substituted. |
| EWF history / closure | Deferred | One final state supports bookkeeping only, not time-integrated closure. |

**Raw evidence:** [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-server3-20260727-4999-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-server3-20260727-4999-snapshot/), and [completed six-injection DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-server3-20260727-4999-dpm/). The audit confirms global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`. The 2024 R2 Settings API does not expose the top-level EWF branch or a readable wall separation flag; this is an adapter limitation, not proof that edge separation is disabled.

### DPM Particle Tracks Summary

All flow values are terminal fate flows in kg/s. `Incomplete` remains in the raw diagnostic record but is not elevated into the simplified-geometry acceptance criterion; observed `steamoutlet` escape is the report-facing DPM metric. Separation is a secondary event/parcel diagnostic and is not added as an extra terminal mass sink.

| Diameter (µm) | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Separated events | Closure relative residual |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | 0.038010 | 0.037890 | 0 | 1.226e-4 | not printed | not printed | not printed | -6.84e-5 |
| 28.14 | 0.156100 | 0.154700 | 3.596e-4 | 2.877e-4 | 7.191e-4 | 10 | not printed | 2.15e-4 |
| 56.27 | 0.194100 | 0.172600 | 4.293e-3 | 8.943e-5 | 1.708e-2 | 191 | not printed | 1.94e-4 |
| 112.54 | 0.390100 | 0.232800 | 1.187e-2 | 0 | 0.145400 | 809 | not printed | 7.69e-5 |
| 168.81 | 0.390100 | 0.153500 | 7.731e-3 | 0 | 0.228900 | 1273 | not printed | -7.95e-5 |
| 348.88 | 4.702000 | 0.295200 | 0.142400 | 3.211e-6 | 4.264000 | 2024 | 171 | 8.44e-5 |

Escaped terminal particles exit at `steamoutlet`, while trapped particles terminate at `bottom`. The largest printed relative flow-closure residual is `2.15e-4`, consistent with report precision. At 348.88 µm, the terminal fate counts sum to the tracked count (`236 + 79 + 2 + 2024 = 2341`); the 171 separation events are retained separately.

### EWF final-state snapshot

Confirmed scope is `wall` only. This is a one-checkpoint result and not an interval mass balance.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 1.0963624e-2 | dimensionless | final-state numerical diagnostic only |
| Film Mass | sum, `wall` | 2.0542629e-1 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 4.5015113e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 3.479654e-6 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 0 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | selected boundaries / net | 0 | kg/s | `liquidinlet`, `steaminlet`, and `steamoutlet` all read -0.0 kg/s |
| Film velocity components | area-weighted, `wall` | x 1.4820767e-1; y -1.623268e-3; z 5.6735414e-2 | m/s | direct component measurements |
| Film velocity magnitude | derived from measured components | 1.5870430e-1 | m/s | not an independently extracted Fluent magnitude |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | runner requested an unsupported alias; Fluent advertises `film-dpm-mass-src` |
| Film Separated Mass | sum, `wall` | unavailable | kg | 171 DPM events exist, but no represented film-mass quantity was extracted |

**Bookkeeping status: bookkeeping-only.** Missing terms are initial inventory, time-integrated DPM-to-film source, film inflow/outflow, represented separation mass, and an explicit residual over a defined interval. Do not combine the 0.20542629 kg inventory directly with the kg/s boundary-flux read.

### Interpretation

- **Measured:** complete DPM fate evidence exists for all six injections, and the 348.88 µm transcript reports 171 separation events. The largest class is absorption-dominant by terminal flow, while smaller classes remain escape-dominant.
- **Derived:** terminal flow rows close within printed precision; the component-derived film speed is 0.15870430 m/s.
- **Unresolved:** carrier fluxes/residuals for this fresh capture, represented separation mass and ultimate generated-parcel fate, Film DPM Mass Source, time-integrated EWF closure, and root-level EWF/separation readback. None is reported as zero.

**Conclusion — diagnostic only.** The requested 4,999-iteration capture supplies fresh EWF and DPM evidence but not a carrier-state update. It supports observed separation events for the largest injection, not an edge-separation mass balance or separator-performance claim. At printed precision, its EWF and DPM values reproduce the earlier completed 5,000-checkpoint record; the Fluent-version difference and unavailable case/data identity prevent treating that agreement as proof of identical solver state.
