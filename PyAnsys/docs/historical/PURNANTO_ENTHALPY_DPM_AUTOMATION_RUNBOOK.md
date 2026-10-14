# Purnanto Enthalpy and DPM Automation Runbook

## 1. Purpose

This is the consolidated operator runbook and new-task handoff for the Purnanto
enthalpy/DPM replication automation. It records:

- how the Mac connects to Fluent on the Windows workstation;
- the fixed six-case operating matrix;
- the baseline and spiral-inlet automation paths;
- the order in which carrier flow and DPM are configured and run;
- dry-run, smoke, production, monitoring, and recovery commands;
- the output and acceptance contract;
- the completed result snapshot and its evidence limits; and
- how to use this workflow as the starting point for mesh convergence.

This file is operational documentation. The setup reports and research wiki
remain the authoritative scientific records.

## 2. Current Evidence Status

Two six-condition sweeps are complete:

| Branch | Setup | Cases | Injection rows | Evidence status |
|---|---|---:|---:|---|
| Purnanto baseline / Bangma-target | `08b` | 6 | 54 | Completed, scientifically provisional |
| Spiral inlet | `08c` | 6 | 54 | Completed, scientifically provisional |

Every accepted injection row contains direct Fluent DPM fate mass, and every
per-injection escaped + trapped + incomplete mass check passed the `0.2%`
tolerance. The maximum observed discrepancies were approximately `0.0321%` for
the baseline branch and `0.0290%` for the spiral branch.

The results are not convergence proof:

- baseline final continuity residuals were approximately `0.193-0.343`;
- spiral final continuity residuals were approximately `0.145-0.229`;
- baseline incomplete DPM mass was approximately `36.06-58.01 kg/s`;
- exact geometry and mesh lineage are not fully established; and
- some inherited DPM controls were not preserved in the historical manifests.

Use the completed results for provisional comparison and workflow validation,
not as a mesh-independent validation result.

## 3. Controller Architecture

```text
Mac
  Codex
  Python 3.12
  PyFluent in PyAnsys/.venv
  sweep, monitoring, and recovery scripts

        gRPC over VPN/LAN

Windows workstation
  Ansys Fluent 2024 R2
  Fluent license
  Fluent gRPC server
  case/data inputs and production outputs
```

The Mac attaches to an existing Fluent session. It does not launch Fluent and
does not own or close the remote Fluent process:

```text
cleanup_on_exit = False
```

The processor count is selected when Fluent is launched on Windows. The sweep
script does not change it. The previous production intent was 15 processors;
verify the active Fluent session before a timing or mesh-cost comparison.

## 4. Repository and Remote Paths

### Local project

```text
/Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys
```

Run all commands in this document from that directory.

### Input tables

```text
/Users/andy/Desktop/P4P/Code/harwell_results.csv
/Users/andy/Desktop/P4P/Code/spiral_harwell_results.csv
```

The source chain is:

```text
Purnanto Figure 5 digitization
-> Code/droplet_distribution.py
-> Code/harwell_calculation.py
-> harwell_results.csv or spiral_harwell_results.csv
-> nine Fluent surface injections
```

### Windows baselines

```text
C:\Users\qtra338\Documents\baseline.cas.h5
C:\Users\qtra338\Documents\baseline_spiral_inlet.cas.h5
```

### Completed Windows outputs

```text
C:\Users\qtra338\Documents\enthalpy_sweep_verified_20260721_v2
C:\Users\qtra338\Documents\spiral_enthalpy_sweep_20260725
```

### Completed local mirrors

```text
PyAnsys/output/enthalpy_sweep_verified_20260721_v2
PyAnsys/output/spiral_enthalpy_sweep_20260725
```

Do not overwrite these evidence directories. Use a new run ID for every smoke,
continuation, mesh, or production run.

## 5. Fixed Six-Case Matrix

| Case | Condition | Liquid (kg/s) | Steam (kg/s) |
|---:|---|---:|---:|
| 1 | `1600 -25%` | 87.69 | 60.52 |
| 2 | `1440` | 132.76 | 64.85 |
| 3 | `1520` | 124.84 | 72.77 |
| 4 | `1600` | 116.92 | 80.69 |
| 5 | `1680` | 109.00 | 88.61 |
| 6 | `1760` | 101.09 | 96.52 |

The automation requires:

```text
phase-1 material = water-vapor-at-psep = steam mass flow
phase-2 material = water-liquid-at-psep = liquid mass flow
```

Phase identity is verified from material readback. Phase number alone is not
accepted as evidence.

## 6. Branch-Specific DPM Contract

### Baseline / Bangma-target branch

```text
Runner: scripts/setup/run_purnanto_enthalpy_sweep.py
Case: C:\Users\qtra338\Documents\baseline.cas.h5
CSV: Code/harwell_results.csv
Injections: injection-0 through injection-8
Particle material: water-liquid-dpm
Escaped zone observed: steam_outlet
Trapped zone observed: fluid_outlet
Harwell area: 0.4115 m2
```

### Spiral-inlet branch

```text
Runner: scripts/setup/run_purnanto_spiral_enthalpy_sweep.py
Case: C:\Users\qtra338\Documents\baseline_spiral_inlet.cas.h5
CSV: Code/spiral_harwell_results.csv
Injections: injection-5-micron through injection-1631-micron
Particle material: liquid-water
Escaped zone observed: outlet
Trapped zone observed: bottom
Harwell area: 0.724^2 = 0.524176 m2
```

For both branches:

- the injection type is `surface`;
- the release surface is `inlet`;
- all nine injection mass flows sum to the case liquid flow;
- diameter and speed come from the branch CSV;
- Normal to Face uses a positive magnitude, `abs(z_velocity_ms)`;
- the selected inlet face normal must point into the vessel;
- DPM interaction must read back disabled unless a coupled sensitivity is
  explicitly requested; and
- injections are configured and read back before carrier iterations.

## 7. Per-Case Automation Order

The production runner performs the following sequence for each selected case:

1. Load the baseline case fresh.
2. Disable inherited Fluent autosave that could overwrite unrelated files.
3. Verify the expected inlet, outlet, and nine injection objects.
4. Verify phase names, phase materials, and one-way DPM interaction.
5. Apply and read back the steam and liquid mass-flow conditions.
6. Apply and read back all nine injection definitions.
7. Hybrid-initialize the carrier field.
8. Configure residual history and disable early residual-based stopping.
9. Run the requested carrier iterations in evidenced chunks.
10. Save the pre-DPM carrier case/data pair.
11. Enable per-injection/zone DPM reporting.
12. Run a required fresh DPM update.
13. Export aggregate and per-injection extended summaries.
14. Parse escaped, trapped, and incomplete mass from the explicitly labelled
    Fluent `Final` mass-flow column.
15. Reconcile each injection's fate mass against its injected mass.
16. Read and validate injection definitions without rewriting them.
17. Save the final post-DPM case/data pair.
18. Write the per-case CSV, combined CSV, residual CSV, report text, and JSON
    manifest.

A failed phase readback, injection readback, DPM update, fresh report, escaped
mass parse, or fate-mass audit stops acceptance.

Particle-count weighting is disabled. Counts are not assumed to be mass
fractions.

## 8. Prepare and Check the Connection

### Windows workstation

Find the active IPv4 address:

```powershell
ipconfig
```

For Fluent 2024 R2, a command-line launch example is:

```powershell
cd %USERPROFILE%\Desktop
"C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe" 3ddp -sifile=server_info.txt
type server_info.txt
```

Alternatively, start the server from Fluent:

```text
File -> Applications -> Server -> Start
```

or use the Fluent TUI command:

```text
server/start-server
```

Use the workstation's actual IPv4 address from the Mac. Do not use
`127.0.0.1` or `localhost`.

### Mac `.env`

Store secrets only in `PyAnsys/.env`, which is ignored by git:

```text
FLUENT_IP=WINDOWS_IPV4
FLUENT_PORT=GRPC_PORT
FLUENT_PASSWORD=TEMPORARY_TOKEN
FLUENT_ALLOW_REMOTE_HOST=true
FLUENT_INSECURE_MODE=false
FLUENT_TCP_PREFLIGHT_TIMEOUT_SECONDS=5
```

Additional workstations use the same names with suffixes:

```text
FLUENT_IP2=...
FLUENT_PORT2=...
FLUENT_PASSWORD2=...
```

Select them with `--server-id 2`, `--server-id 3`, and so on.

### Local checks

```bash
cd /Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys
.venv/bin/python scripts/connection/local_preflight.py
.venv/bin/python scripts/connection/run_guarded.py \
  --idle-timeout-seconds 90 \
  -- \
  .venv/bin/python -u scripts/connection/check_connection.py \
    --server-id 1 \
    --connect-timeout-seconds 60 \
    --health-timeout-seconds 15
```

If TCP succeeds but the health RPC times out, the port is reachable but the
Fluent gRPC session is probably wedged. Restart the Fluent server/session before
running a sweep.

## 9. Validate Before Applying

Run unit tests and syntax checks:

```bash
.venv/bin/python -m unittest tests/test_purnanto_enthalpy_sweep.py
.venv/bin/python -m py_compile \
  scripts/setup/run_purnanto_enthalpy_sweep.py \
  scripts/setup/run_purnanto_spiral_enthalpy_sweep.py \
  scripts/setup/continue_purnanto_current_case.py
```

Dry-run both six-case plans:

```bash
.venv/bin/python scripts/setup/run_purnanto_enthalpy_sweep.py --dry-run
.venv/bin/python scripts/setup/run_purnanto_spiral_enthalpy_sweep.py --dry-run
```

Require six cases, nine bins per case, and DPM totals equal to the listed liquid
flows.

## 10. Smoke Runs

Use a unique run ID. Case 4 is the standard `1600 kJ/kg` representative case.

### Baseline carrier-only setup smoke

```bash
.venv/bin/python scripts/connection/run_guarded.py \
  --idle-timeout-seconds 600 \
  --log-file output/RUN_ID/logs/baseline_smoke.log \
  -- \
  .venv/bin/python -u scripts/setup/run_purnanto_enthalpy_sweep.py \
    --apply \
    --server-id 1 \
    --case-filter 4 \
    --iterations 1 \
    --report-interval 1 \
    --checkpoint-interval 0 \
    --no-dpm-report \
    --remote-output-dir "C:\Users\qtra338\Documents\RUN_ID" \
    --local-output-dir "output/RUN_ID"
```

### Spiral carrier-only setup smoke

```bash
.venv/bin/python scripts/connection/run_guarded.py \
  --idle-timeout-seconds 600 \
  --log-file output/RUN_ID/logs/spiral_smoke.log \
  -- \
  .venv/bin/python -u scripts/setup/run_purnanto_spiral_enthalpy_sweep.py \
    --apply \
    --server-id 1 \
    --case-filter 4 \
    --iterations 1 \
    --report-interval 1 \
    --checkpoint-interval 0 \
    --no-dpm-report \
    --remote-output-dir "C:\Users\qtra338\Documents\RUN_ID" \
    --local-output-dir "output/RUN_ID"
```

The smoke test checks connectivity, remote case access, phase mapping, inlet
mutation, nine injection readbacks, initialization, one iteration, and file
writes. It is not a physical result.

## 11. Full Production Commands

Do not reuse the completed evidence directories. Replace `RUN_ID` with a new,
stable identifier before execution.

### Baseline six-case sweep

```bash
caffeinate -dimsu .venv/bin/python scripts/connection/run_guarded.py \
  --idle-timeout-seconds 1800 \
  --log-file output/RUN_ID/logs/baseline_full.log \
  -- \
  .venv/bin/python -u scripts/setup/run_purnanto_enthalpy_sweep.py \
    --apply \
    --server-id 1 \
    --iterations 1500 \
    --iteration-mode chunked \
    --report-interval 100 \
    --checkpoint-interval 500 \
    --residual-history-points 2000 \
    --remote-output-dir "C:\Users\qtra338\Documents\RUN_ID" \
    --local-output-dir "output/RUN_ID"
```

### Spiral six-case sweep

```bash
caffeinate -dimsu .venv/bin/python scripts/connection/run_guarded.py \
  --idle-timeout-seconds 1800 \
  --log-file output/RUN_ID/logs/spiral_full.log \
  -- \
  .venv/bin/python -u scripts/setup/run_purnanto_spiral_enthalpy_sweep.py \
    --apply \
    --server-id 1 \
    --iterations 1500 \
    --iteration-mode chunked \
    --report-interval 100 \
    --checkpoint-interval 500 \
    --residual-history-points 2000 \
    --remote-output-dir "C:\Users\qtra338\Documents\RUN_ID" \
    --local-output-dir "output/RUN_ID"
```

`caffeinate` prevents idle sleep but does not make lid sleep safe. Keep the Mac
open, powered, connected to VPN/Wi-Fi, and able to reach the workstation.

## 12. Monitor Without Connecting to Fluent

Baseline:

```bash
.venv/bin/python scripts/connection/check_sweep_status.py \
  --output-dir output/RUN_ID
```

Spiral:

```bash
.venv/bin/python scripts/connection/check_spiral_sweep_status.py \
  --output-dir output/RUN_ID
```

Watch mode:

```bash
.venv/bin/python scripts/connection/check_sweep_status.py \
  --output-dir output/RUN_ID \
  --watch \
  --interval 30
```

These status scripts inspect local PID, log, manifest, and CSV evidence. They do
not consume a Fluent connection or modify the solver.

## 13. Connection Loss and Recovery

If VPN, Wi-Fi, or the Mac connection drops:

1. Do not assume the current Fluent iterate call stopped immediately.
2. Reconnect VPN and verify TCP/gRPC health.
3. Inspect the local run log, newest manifest, and remote checkpoint files.
4. Determine the completed iteration count from residual-history or manifest
   evidence, not from the GUI residual plot length or the most recent requested
   iteration count.
5. Load a matching checkpoint case and data pair.
6. Continue only the missing iterations.
7. Use a new output label; do not overwrite the recovery source.

Example: continue Case 4 from a verified 1000 iterations to 1500:

```bash
.venv/bin/python -u scripts/setup/continue_purnanto_current_case.py \
  --server-id 1 \
  --case-filter 4 \
  --resume-case "C:\Users\qtra338\Documents\RUN_ID\CHECKPOINT.cas.h5" \
  --resume-data "C:\Users\qtra338\Documents\RUN_ID\CHECKPOINT.dat.h5" \
  --additional-iterations 500 \
  --verified-starting-iterations 1000 \
  --verified-completed-iterations 1500 \
  --total-label 1500iter_recovered \
  --report-interval 25 \
  --checkpoint-interval 250 \
  --remote-output-dir "C:\Users\qtra338\Documents\RECOVERY_RUN_ID" \
  --local-output-dir "output/RECOVERY_RUN_ID"
```

The continuation script revalidates phase materials and DPM interaction. Its
post-DPM injection check is read-only before the final save.

## 14. Output Contract

Each completed case should produce:

```text
pre-DPM case/data
post-DPM case/data
case manifest JSON
residual-history CSV
raw aggregate DPM report
fresh per-injection DPM report text
case_N_CONDITION_injection_results.csv
case_N_CONDITION_case_summary.csv
```

Each sweep should produce:

```text
all_enthalpy_injection_results.csv
all_enthalpy_case_summary.csv
```

Required injection columns include:

```text
case
enthalpy_kJkg
injection_name
injection_number
diameter_m
diameter_mm
injected_mass_flow_kgs
escaped_kgs
trapped_kgs
incomplete_kgs
escaped_count
trapped_count
incomplete_count
escaped_fraction
notes
```

## 15. Acceptance Checklist

A case is technically complete only when:

- the intended baseline was loaded fresh;
- phase-1 is verified as steam and phase-2 as liquid from material readback;
- the two inlet mass flows match the selected paper condition;
- one-way DPM is verified;
- all nine injections match material, surface, diameter, flow, and velocity;
- all injections are set before carrier iteration;
- the nine injection flows sum to the case liquid flow;
- residual or manifest evidence demonstrates the requested iteration count;
- pre-DPM and post-DPM case/data pairs exist;
- a fresh DPM update and fresh per-injection reports completed;
- there are exactly nine injection rows for the case;
- `escaped_kgs` comes from the labelled `Final` mass-flow column;
- escaped, trapped, and incomplete mass are all retained;
- each injection fate total agrees with injected mass within `0.2%`; and
- the final manifest and combined CSV are readable.

Scientific acceptance additionally requires:

- residual and physical monitor stability;
- acceptable mass conservation;
- mesh-quality evidence;
- mesh-independent quantities of interest;
- a resolved interpretation of incomplete particles;
- confirmed inward face-normal orientation; and
- confirmed steam-quality convention.

The existing results meet the technical completion checklist but not all
scientific acceptance conditions.

## 16. Completed Result Snapshot

### Baseline / Bangma-target

| Case | Escaped (kg/s) | Trapped (kg/s) | Incomplete (kg/s) | Provisional quality (%) |
|---:|---:|---:|---:|---:|
| 1 | 0.1367 | 51.49 | 36.06 | 99.7746 |
| 2 | 0.213559 | 74.53 | 58.01 | 99.6718 |
| 3 | 0.196699 | 69.55 | 55.09 | 99.7304 |
| 4 | 0.1817 | 63.24 | 53.50 | 99.7753 |
| 5 | 0.1648 | 56.81 | 52.02 | 99.8144 |
| 6 | 0.1443 | 51.37 | 49.58 | 99.8507 |

### Spiral inlet

| Case | Escaped (kg/s) | Trapped (kg/s) | Incomplete (kg/s) | Provisional quality (%) |
|---:|---:|---:|---:|---:|
| 1 | 0.01941 | 85.60 | 2.068 | 99.9679 |
| 2 | 0.02088 | 129.40 | 3.307 | 99.9678 |
| 3 | 0.02416 | 121.70 | 3.120 | 99.9668 |
| 4 | 0.01655 | 113.00 | 3.907 | 99.9795 |
| 5 | 0.01896 | 103.70 | 5.235 | 99.9786 |
| 6 | 0.02667 | 94.38 | 6.680 | 99.9724 |

The project comparison convention is:

```text
steam quality (%) =
  steam inlet mass flow
  / (steam inlet mass flow + escaped liquid mass flow)
  * 100
```

This convention remains inferred. It must not be presented as the confirmed
paper definition until checked against Purnanto's calculation method and the
Fluent steam-outlet flow.

## 17. Known Gaps That a New Task Must Preserve

1. A fixed 1500 iterations is an execution protocol, not a convergence rule.
2. Baseline Case 1 lacks a mirrored standalone residual CSV, although its
   manifest preserves block-level advancement to 1500.
3. Historical baseline manifests do not preserve a direct one-way DPM
   interaction readback.
4. Historical manifests do not preserve every maximum-step, step-length,
   high-resolution-tracking, and wall-fate setting.
5. The inlet face-normal direction has not been geometrically evidenced.
6. The exact CAD/mesh lineage of both production baseline files is unresolved.
7. An older audited Purnanto case had `2,964,593` cells, while production sweep
   logs reported approximately `5.58 million` cells. Treat these as different
   or unresolved assets until a fresh audit proves identity.
8. The spiral production mesh count and quality statistics are not preserved
   in the current sweep record.
9. The GUI residual history length can be limited by `n-save`/`n-display`; it
   is not an iteration counter.
10. The GUI injection panel previously raised
    `ASSQ: invalid argument [2]: improper list`. Use programmatic readback and
    a reload audit rather than relying only on that GUI panel.

## 18. Mesh-Convergence Starting Protocol

### 18.1 Scope the first study narrowly

Choose one geometry first. Do not mix baseline and spiral meshes in one
convergence sequence. Use Case 4 (`1600 kJ/kg`) as the representative operating
condition unless the research question specifically targets another condition.

Freeze:

- geometry;
- named boundary zones;
- physical models and material properties;
- inlet/outlet conditions;
- initialization method;
- discretization and coupling;
- turbulence settings;
- DPM distribution and tracking settings;
- processor count for timing comparisons; and
- convergence and output definitions.

Only the mesh should change.

### 18.2 Audit the starting mesh

Before creating a mesh ladder, record:

- exact case/mesh filename and checksum;
- cell, node, and face counts;
- cell types and partitions;
- minimum orthogonal quality;
- maximum skewness and aspect ratio;
- negative-volume and mesh-check warnings;
- worst-cell coordinates;
- named zones and zone IDs;
- local sizing at the inlet transition, outer swirl wall, dome transition,
  steam outlet, bottom outlet, and suspected incomplete-particle ring; and
- the active Fluent and PyFluent versions.

Do not use the unresolved `2.96M` versus `5.58M` historical counts as a mesh
ladder.

### 18.3 Create at least three systematically related meshes

Use coarse, medium, and fine meshes generated from the same geometry and
meshing method. Apply a consistent refinement rule and preserve zone names.

Record the actual characteristic size for each mesh. For a constant-volume 3D
domain, a cell-count proxy may be calculated as:

```text
h proportional to N_cells^(-1/3)
```

Use the actual mesh sizes or cell-volume-based measure when available. Do not
claim Richardson extrapolation or GCI when the meshes are not systematically
related.

Purnanto reported unstructured tetrahedral meshes, approximately `5 cm`
average element size, and local sizes down to `1 cm` near selected high-gradient
boundaries. Those values are literature context, not automatic acceptance
targets for the current CAD.

### 18.4 Separate carrier convergence from DPM

The current sweep runner can skip DPM with `--no-dpm-report`, but it still uses
a fixed iteration budget and does not implement the full physical-monitor
stopping and staged restart contract needed for a rigorous mesh study.

The mesh-convergence task should create or adapt a driver with two explicit
stages:

```text
Stage A: carrier-only solve
  load one mesh-specific case
  apply the frozen Case 4 setup
  initialize
  advance in chunks
  export residual and physical monitors
  stop only after the agreed stability criteria
  save converged carrier case/data

Stage B: DPM post-processing
  load the accepted carrier case/data
  verify the complete DPM contract
  run one fresh DPM update
  export direct fate mass and incomplete-particle diagnostics
  save post-DPM case/data
```

Do not compare DPM steam quality across meshes whose carrier fields have not
reached comparable stability.

### 18.5 Quantities of interest

At minimum, compare:

- carrier continuity and phase mass imbalance;
- steam outlet mass flow;
- liquid mass reaching the steam outlet, where available;
- inlet-to-outlet pressure difference;
- one or more fixed-location or fixed-surface velocity/swirl measures;
- escaped, trapped, and incomplete DPM mass;
- steam quality under the fixed project convention;
- incomplete-particle fraction by injection diameter; and
- concentration of incomplete tracks near the cylinder-to-dome transition.

Also record wall-clock time and memory, but do not use timing as a physics
acceptance metric.

### 18.6 Mesh acceptance

Define the numerical tolerance before running. A mesh is acceptable only when:

- the medium-to-fine change in each primary quantity is below the chosen
  tolerance;
- the trend is physically and numerically interpretable;
- mass conservation and monitor stability are acceptable;
- refinement does not move bad cells into critical flow regions; and
- DPM incomplete mass is stable or its mesh dependence is explicitly reported.

If three systematically refined meshes show a monotonic trend, calculate
observed order and GCI or Richardson-style uncertainty. If not, report the work
as a mesh sensitivity study rather than formal grid convergence.

### 18.7 Required mesh-study outputs

Create one row per mesh with:

```text
mesh_id
geometry_id
mesh_file
checksum
cell_count
node_count
face_count
minimum_orthogonal_quality
maximum_skewness
maximum_aspect_ratio
carrier_iterations
continuity_residual_final
phase_mass_imbalance_kgs
pressure_drop_pa
steam_outlet_mass_flow_kgs
escaped_kgs
trapped_kgs
incomplete_kgs
steam_quality_pct
wall_clock_seconds
notes
```

Preserve each mesh's case/data, residual history, physical-monitor history, DPM
report, injection CSV, manifest, and setup readbacks in a separate output
directory.

## 19. Prompt for a New Mesh-Convergence Task

Start the new task with:

```text
Read and follow all applicable AGENTS.md files, then use:

/Users/andy/Desktop/P4P/P4P_knowledgeWiki/PyAnsys/docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md

as the primary handoff for the completed Purnanto enthalpy/DPM automation.

Goal: design and implement a mesh-convergence workflow for one separator
geometry, starting with Purnanto Case 4 (1600 kJ/kg). Do not run a full sweep
yet.

First:
1. identify the exact baseline geometry and mesh files;
2. audit cell/node/face counts, mesh quality, named zones, physics, materials,
   numerics, DPM interaction, tracking controls, and processor count;
3. resolve the historical 2.96M versus 5.58M cell-count discrepancy;
4. define coarse/medium/fine meshes that differ only by a systematic mesh rule;
5. define carrier residual, mass-balance, pressure-drop, outlet-flow, and
   velocity/swirl convergence metrics;
6. propose a carrier-only solve stage followed by DPM post-processing;
7. preserve the existing phase mapping, nine-bin injection definition,
   face-normal positive magnitude, direct Final fate-mass parsing, and 0.2%
   injection mass audit; and
8. write the plan and setup identity to the repository before launching long
   Fluent runs.

Treat the completed 1500-iteration results as provisional comparison evidence,
not as converged or mesh-independent validation.
```

## 20. Supporting Records

- [Baseline setup instance](<../../Setup report/08b-purnanto-baseline-enthalpy-dpm-sweep.md>)
- [Spiral setup instance](<../../Setup report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md>)
- [Research replication report](../../ResearchProject_wiki/wiki/technical/purnanto-enthalpy-dpm-replication.md)
- [Spiral research report](../../ResearchProject_wiki/wiki/technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md)
- [Fluent connection checklist](ON_SITE_FLUENT_PC_CHECKLIST.md)
- [Remote Fluent reference](CODEX_REMOTE_FLUENT_WORKFLOW.md)
- [Dependency-safe DPM order](../knowledge/fluent-settings/orders/dpm_order.yaml)
- [Dependency-safe solution order](../knowledge/fluent-settings/orders/solution_order.yaml)
- [Mesh evidence synthesis](../../CFD_wiki/wiki/synthesis/mesh-quality-and-resolution-patterns.md)
- [Main baseline runner](../scripts/setup/run_purnanto_enthalpy_sweep.py)
- [Spiral wrapper](../scripts/setup/run_purnanto_spiral_enthalpy_sweep.py)
- [Continuation runner](../scripts/setup/continue_purnanto_current_case.py)
- [Baseline status tool](../scripts/connection/check_sweep_status.py)
- [Spiral status tool](../scripts/connection/check_spiral_sweep_status.py)
