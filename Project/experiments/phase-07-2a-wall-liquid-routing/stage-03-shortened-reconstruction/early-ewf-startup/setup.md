# Stage 3 — Coupled and EWF before inlet loading

| Question / authority | Contract |
| --- | --- |
| Human question | Does starting Coupled and EWF at A, then holding low feed for 500 updates, reduce the loading spike? |
| Selected model | R3 roughness and corrected contact absorber |
| Placement | Server 1; full ownership granted on 5 October 2026 |
| Earlier Stage 3 run | Separate Server 3 branch; retain its endpoints and evidence |
| Classification | Partial repeat: same low-feed parent and ramp; current model and earlier film activation |
| Exact startup basis | Continue saved historical A fields; no bulk reinitialization or replay |
| Comparison limit | Tests a combined startup recipe; does not isolate Coupled, film, roughness or absorber effects |

| Parent / invariant | Verified record or requirement |
| --- | --- |
| Historical A | N1580, at the end of the original 25% feed hold |
| A case SHA-256 | `232e72ff86c657b2d90bff56f6e9cb84336e30905e365fa89d7c699ef653bf57` |
| A data SHA-256 | `ff64317d4e6e77661d7faf13d26d4c04ac3d5db2ea78eed461762a3b3531c187` |
| A evidence | [R0 provenance](../../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/provenance.md) |
| Model template | Preserved current Server 1 R3/contact case; retain case settings while loading A bulk data |
| Mesh | Existing 60,964-cell mesh; no remeshing |
| Bulk field proof | Compare saved prepared cell solution arrays with A data before the solve |
| R3 | Roughness height 0.5 mm; Cs 0.5; verified existing wall scope |
| Contact absorber | Bulk tau 10 µs; phase-velocity momentum removal; fraction relaxation 0.1; inherited EWF drainage and DPM escape |
| Carrier | Steady Coupled; Global Time Step; current reference controls |
| Film | E2.7 phase accretion and coupled film equations; Flow Momentum Coupling off; existing film wall `wall` |
| Film initialization | Dry film at A; do not reset bulk fields |
| Film step | Fixed 1 µs throughout hold, ramp and final hold; 10 subiterations |
| Thickness bound | Existing 1 m diagnostic cap; never use the cap as a success criterion |
| DPM | Preserve inherited one-way diagnostic injections and collector escape boundaries |

| Step | Native coordinate | Feed and action |
| --- | --- | --- |
| Retained history | N0–N1580 | Original low-feed development retained through saved A fields |
| Activate at A | N1580 | Current R3/contact model; Coupled and EWF on; film initialized once |
| Low-feed hold | N1581–N2080 | Liquid 29.23 kg/s; vapor 20.1725 kg/s; 500 updates |
| Original ramp | N2081–N4080 | 2000 updates; both inlet commands updated every 10 updates |
| Full-feed hold | N4081–N5080 | Liquid 116.92 kg/s; vapor 80.69 kg/s; 1000 updates to check persistence |
| Ramp command | Relative ramp update r | f = 0.25 + 0.75 r/2000; first block uses r = 0, then r = 10, 20, …, 1990; write full target at r = 2000 |
| Ramp evidence | Actual boundary writes and readback | Preserve each command and report-cache lag; match original command trace before claiming exact scheduling |
| Native batches | Holds and ramp | 500-update low hold; exact 10-update ramp blocks; 1000-update target hold |
| Checkpoints | Local Fluent disk | Prepared A; end of low hold; every 500 ramp updates; ramp end; final endpoint |
| Shared files | OneDrive | Verified A input and prepared/final pairs only; checkpoints remain local |
| Completion | N5080 | Paired endpoint, exact horizon, complete reports, native residuals, final reopen and analysis |

| Evidence ID | Main figure / measure | Comparison and decision use |
| --- | --- | --- |
| S3-EARLY-1 | Carrier residuals, feed and inventory against ramp progress | Original A–B ramp versus new ramp; mark activation and 500-update hold separately |
| S3-EARLY-2 | Bulk + film mass and outward phase-2 steamoutlet flux | Compare peak storage and carryover at equal feed; do not count transfer to film as removal |
| S3-EARLY-3 | Film accretion, drainage, thickness and final inner residuals | Detect a displaced film spike or poor inner solves; film ledger uses actual native time |
| Required sampling | Every carrier update | All existing native reports, all seven carrier residuals and every printed film subiteration |
| Spike measures | Raw peak, 95th percentile and final-500 level | State normalization changes; raw/normalized residual decrease alone cannot qualify the model |
| Stronger support | Smaller loading excursions with bounded combined storage and carryover | Sustained response during the full-feed hold; source tracking and film accounting also required |
| Weaker / ambiguous support | Lower carrier residuals but higher inventory, carryover or failed film inner solves | Report the tradeoff; no improvement claim from one trace |
| Recovery limits | Nonfinite fields, thickness >3 mm, film Courant >1 or film ledger error >1% | Preserve the endpoint and recover within scope |
| Film clock | Nominal 3.5 ms at fixed 1 µs | Verify actual accepted steps and saved clock; 500 low-feed updates are not steady-film qualification |
| Claim limit | Finite startup response | No steady separator, developed-film reproduction, physical validation or mesh-convergence claim |

| Owner | Link |
| --- | --- |
| Historical markers / full record | [N45606 history](../../stage-02-combined-ewf-roughness/case-history-N45606.md) |
| Executable implementation | [Early EWF runner](../../../../../PyAnsys/scripts/setup/run_phase72a_stage3_early_ewf.py) |
| Machine evidence | [Run manifest](../../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/run-manifest.json) |
