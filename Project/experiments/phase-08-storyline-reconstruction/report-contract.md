# Phase 8 — Common run and report contract

Each selected `setup.md` must list the exact Fluent report-definition name, expression or surface/zone scope, units, sign convention, sampling cadence, and output file for every applicable row. Record `N/A` with a reason for an inapplicable measure; record `unavailable` with failed readback when Fluent cannot provide it. Neither means zero.

## Reproducibility record

Record the source historical setup revision; new mesh path, hash, cell count, zone list, and Fluent mesh check; Fluent version and machine; case/data parent hashes; initialization or continuation; physics, materials, boundaries, sources, DPM/EWF settings and readback; report-definition manifest; solver controls and run commands; start/end native coordinates; checkpoints and hashes; transcript/events; and script or TUI revision. Link to raw evidence in `PyAnsys/`.

## Common reports during every solve

Run each family at the five selected nominal inlet speeds: `20.11`, `23.46`, `26.81`, `29.48`, and `32.14 m/s`. Keep the physical inlet opening and split location fixed; vary boundary flow values. Record target and realized overall superficial speed plus the separate liquid-strip and steam-zone velocities, along with meshed face areas, densities, phase split, and mass-flow commands used to convert between them. In F3/F4, DPM allocation changes Eulerian liquid-strip velocity even when nominal overall speed is matched. These are Phase 8 design points; only the `26.81 m/s` spiral reference is explicitly stated in the cited Purnanto paper text.

| Group | Quantities | Comparison rule |
| --- | --- | --- |
| Feed | commanded and realized total, phase-1 vapor, and phase-2 liquid inlet mass flow; inlet vapor fraction/loading | Separate a command change from realized flow. |
| Outlets | phase-1, phase-2, and mixture mass flow through every named external boundary, especially `steamoutlet`; derived vapor fraction/dryness | Declare Fluent flux sign and use a common boundary grouping. |
| Sources | DPM-to-carrier mass, momentum, and energy feedback where active; all active mass-source totals; absorber command/applied removal only in the later 7.2A extension | Audit applied sources, not just settings or commands. |
| Inventory | whole-domain phase masses and volumes; lower-zone liquid inventory where the same zone exists | For steady runs compare late-window level and slope **per native iteration** as a stationarity diagnostic, not a physical storage rate. |
| Balance | phase and mixture boundary-plus-source net rates; normalized imbalance | Publish equations and signs. For a physical transient only, add finite-difference inventory storage in kg/s and a dynamic closure remainder using physical time. Steady pseudo-time iterations do not supply a physical `dM/dt`. |
| Numerical health | continuity, momentum, volume-fraction, energy if enabled, turbulence and available DPM/EWF residuals; reverse flow, viscosity limiting, AMG/FPE/nonfinite events; elapsed solve time | Residual reduction alone is insufficient. |
| Routing | liquid through `steamoutlet` as mass flow and fraction of realized liquid inlet; vapor through `steamoutlet` as mass flow and fraction of realized vapor inlet | Note when source removal makes outlet fraction incomplete. |

Write native report files at least every 10 iterations for steady runs, including first and last valid points. Capture residual/event evidence at the same or finer cadence where exposed. For transient runs, declare physical-time cadence and keep time and iteration axes distinct. Save start, declared intermediate, final valid, and first-failure checkpoints on Fluent-local disk; transfer only selected start/final pairs needed across machines.

## Mechanism-specific reports

- **DPM fraction definition:** `f_DPM = injected DPM liquid mass flow / total inlet liquid mass flow`. F3/F4 use `0.025`, `0.05`, `0.075`, `0.10`, and `0.20`. For the 1600 kJ/kg reference liquid feed of `116.92 kg/s`, these correspond to injected DPM flows of `2.923`, `5.846`, `8.769`, `11.692`, and `23.384 kg/s`, with complementary Eulerian-liquid flows of `113.997`, `111.074`, `108.151`, `105.228`, and `93.536 kg/s`. Scale both components with the selected speed point while retaining the same fraction. These reference calculations are not the final 60k boundary commands until inlet area and realized-flow readback are verified.
- **F1/F2 diagnostic DPM:** use the same seven-bin 09cV3 diameter/relative-weight distribution and the same `steaminlet` physical release face, but retain full Eulerian liquid feed and turn continuous-phase interaction off. Parcel mass weights, if required by Fluent for tracking reports, are diagnostic weights and do not enter the physical inlet-liquid ledger. Do not compare their absolute escaped mass with F3/F4 physical injected mass; compare fate fractions with tracking completeness visible.
- **DPM:** injection and fixed size distribution, injected fraction of total inlet liquid, represented mass flow, complementary Eulerian-liquid inlet flow, stochastic/coupling settings, injected/escaped/trapped/incomplete counts and mass, fate by size and boundary, tracking warnings. Show incomplete fraction beside escape fraction. Include DPM mass in whole-system accounting without double-counting feedback transferred to the carrier.
- **Native DPM source dimensions:** Fluent's `DPM Mass Source` is a per-cell mass-flow rate (`kg/s`); use a **Volume Sum** over both fluid zones for whole-domain `kg/s`, not Volume Integral. Treat the first F3 N=11,000 pilot's integral monitor as dimensionally invalid. Sum the analogous per-cell momentum-source fields when used. Inert droplets may have zero mass transfer while retaining nonzero momentum feedback.
- **EWF:** wall scope and settings, film mass and thickness (maximum and area-weighted), film velocity/direction, bulk-to-film phase accretion, DPM droplet deposition, splash mass/parcel return, stripping to DPM, other film-to-bulk transfer, film outlet flow, and conservation residual where available. Record each enabled mechanism separately and do not infer a transfer from an inventory change alone.
- **Roughness:** wall scope, `k_s` and `C_s` readback, wall-adjacent liquid fraction and vertical velocity with fixed positive direction, and lower-region delivery where supported.
- **Later 7.2A extension only — absorber:** cell-zone scope, available phase-2 mass, command and applied removal, phase-1 direct-source audit, and command error. Families 1–4 record absorber state as off and mass removal as `N/A`.

## Comparisons and figures

Use one summary row per run with parent, controlled delta, mesh hash, model flags, achieved horizon, report completeness, solver events, and interpretation. Compare matched feed conditions and declared late windows; show full trajectories when a ramp, inventory drift, or failure changes their meaning. The minimum figure set is feed/routing, inventory/storage, source-inclusive closure, numerical health, and mechanism evidence where applicable. Preserve failures as labelled incomplete trajectories.
