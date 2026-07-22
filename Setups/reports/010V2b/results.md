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
