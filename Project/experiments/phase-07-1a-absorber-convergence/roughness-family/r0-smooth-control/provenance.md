# R0 smooth-control provenance and run lineage

This record describes how the state used for the R0 smooth-control result was
reached. It separates the preparation history from the declared statistical
control window. The preparation history is retained for reproducibility, but
its iterations must not be silently pooled with the terminal control sample.

## Lineage at a glance

| Stage | Inlet/loading state | Numerical method | Iteration record | Role in the result |
| --- | --- | --- | --- | --- |
| 1. Unintended low-inlet hold | The initial 25% inlet setting remained active because the first driver did not write the new boundary values inside its loop | The pre-existing solver settings | Last fully persisted driver event at active `1,500`; live state saved immediately afterward | Accidental field-development history; provenance only |
| 2. Corrected ramped inlet loading | Liquid and steam were ramped together from `0.25` of target to full loading, with the actual Fluent boundaries written before each block | Steady solver; actual boundary values were read back after each 10-iteration update | Exactly `2,000` additional native steady iterations from the saved post-1,500 state | Established the full-loading field used as the parent for the numerical-control continuation |
| 3. Numerical-control continuation | Full-loading inlet state held | Pressure–velocity coupling changed to `Coupled`; steady pseudo-time method changed to `Global Time Step` with automatic pseudo-timestep selection | First `+1,000` continuation iterations, then a separate second `+1,000` continuation | First continuation is warm-up/provenance; second continuation is the declared control window |

The sequence was therefore:

```text
unintended lowest-inlet hold (active-1500 handoff)
  -> corrected 2000-iteration ramp from 25% to full inlet loading
  -> Coupled + Global Time Step at full loading
  -> +1000 warm-up/provenance
  -> +1000 declared control window
```

## Stage 1 — unintended lowest-inlet run

Before the controlled inlet ramp, the case was run at the lowest inlet setting
for approximately `1,500` iterations by accident. The handoff task provides a
more precise operational record: the last fully persisted driver event was
active iteration `1,500`, and the live Fluent state was saved immediately
afterward while idle. Fluent's `sol/iterations` variable reported only the
latest 10-iteration driver block, so the global native coordinate in the saved
pair is not inferred from that variable.

The actual boundary values at this stage remained at the initial 25% settings:
liquid `29.230000 kg/s` and steam `20.1725 kg/s`. The driver was calculating
larger intended ramp commands by active iteration `1,500` (approximately
`94.9975 kg/s` liquid and `65.5606 kg/s` steam), but the first implementation
did not call the inlet-scheduling function inside the active solve loop. The
reported ramp targets were therefore not the actual Fluent boundary state.

The saved handoff pair was:

```text
Case: C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR\P71A-R0-SMOOTH-CONTROL\paused-current-20260922T024707Z\P71A-R0-SMOOTH-CONTROL-paused-current.cas.h5
Data: C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR\P71A-R0-SMOOTH-CONTROL\paused-current-20260922T024707Z\P71A-R0-SMOOTH-CONTROL-paused-current.dat.h5
Case SHA-256: 232e72ff86c657b2d90bff56f6e9cb84336e30905e365fa89d7c699ef653bf57
Data SHA-256: ff64317d4e6e77661d7faf13d26d4c04ac3d5db2ea78eed461762a3b3531c187
```

The corresponding pause receipt is in the handoff worktree at
`/Users/shuheiyokkaichi/.codex/worktrees/efcb/P4P_knowledgeWiki/PyAnsys/output/phase71a_family_r/P71A-R0-SMOOTH-CONTROL-rerun5/pause-receipt.json`.

This stage is part of the field-development history that led to the later
state. It is not a controlled comparison, and its residuals, inventories, or
fluxes must not be combined with the stage-2 ramp or with the terminal R0
control statistics.

## Stage 2 — 2,000-iteration ramped inlet loading

The next controlled preparation stage used the v2 inlet-loading schedule from
the saved post-active-1,500 state. The corrected continuation runner operated
on the currently loaded case: it did not reload the clean parent and did not
reinitialize the field. It wrote the actual inlet boundary values before each
10-iteration solve block and read those values back after the write.

The controlled schedule was:

- both inlets started at `0.25` of their recorded base targets;
- liquid was ramped linearly to `116.92 kg/s`;
- steam was ramped linearly to `80.69 kg/s`;
- the schedule was updated every `10` native steady iterations; and
- the active horizon was exactly `2,000` additional native steady iterations.

The live readback verified that the corrected schedule was changing the actual
Fluent boundaries: after the first 10 additional iterations, liquid and steam
read back as `29.66845 kg/s` and `20.4750875 kg/s`; after 100 additional
iterations they read back as `33.6145 kg/s` and `23.198375 kg/s`. This is the
corrected ramp that produced the full-loading endpoint, rather than the earlier
calculated-only ramp targets.

The authoritative ramp record is the [v2 inlet-loading result](../../v2-inlet-loading-ramp/results.md), with its executable schedule in
the [v2 ramp setup](../../v2-inlet-loading-ramp/deffered.md) and its
checkpoint/path declaration in
the [v2 ramp run-path map](../../v2-inlet-loading-ramp/run-paths.yaml).
That result reports the full-loading endpoint after the corrected 2,000-iteration
continuation and preserves the paired terminal case/data artifact and hashes.

The resulting local full-loading pair was then handed off to the numerical
control preparation:

```text
Local case: C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.cas.h5
Local data: C:\Users\syok443\Documents\FluentRuns\Phase71A\FamilyR\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.dat.h5
Case SHA-256: 331bc57550fa0eff67bdc89a0925aa52c8c6f79a4632188e234abdd8ece28c3c
Data SHA-256: 1a8c31aac6a3a3476294a94cc9814edb76b84b49ca1fdfcb1566004bef4517083
```

The pair was copied to the Server-1 OneDrive final-artifacts location without
overwriting an existing target. The source and OneDrive hashes matched. The
transfer receipt is in the handoff worktree at
`/Users/shuheiyokkaichi/.codex/worktrees/efcb/P4P_knowledgeWiki/PyAnsys/output/phase71a_family_r/current_loaded_ramp_20260922T025211Z/onedrive-copy-receipt.json`.

This ramp was the loading history that developed liquid into the v2 domain and
produced the full-loading state subsequently used for the R0 numerical-control
continuation. It is preparation evidence, not part of the declared last-1000
control sample.

## Stage 3 — Coupled and pseudo-time numerical controls

After the full-loading state had been established, the numerical treatment was
changed for the R0 continuation. The controlled changes were:

1. pressure–velocity coupling: `SIMPLE` → `Coupled`;
2. steady pseudo-time method: → `Global Time Step`, initially with automatic
   pseudo-timestep selection.

The solver formulation remained **steady**. Pseudo-time was used only as a
numerical marching method; it does not introduce physical transient time. The
mesh, physical models, boundaries, inlet commands, absorber law,
discretization, and other recorded controls were held fixed and read back
after preparation. The planned numerical delta is documented in the
[deferred Coupled/global-pseudo-time setup](../../v2-coupled-global-pseudo-time-inlet-ramp/deffered.md);
the executed full-loading continuation is documented in
[setup.md](setup.md) and [results.md](results.md).

The executed continuation was then split into two distinct 1,000-iteration
segments:

- **First `+1,000`:** the `run3` continuation from the full-loading parent.
  This is retained as warm-up/provenance history only. It is not pooled into
  the control statistics.
- **Second `+1,000`:** the `run4` continuation from the first-continuation
  endpoint. This is the declared `R0-SMOOTH-CONTROL-LAST1000` window. Its
  expected native coordinate is `4580` through `5580`; the restarted Fluent
  transcript runs from `4586` through `5586`, and that six-row restart offset
  is retained in the evidence rather than silently corrected.

The authoritative inclusion rule is recorded in
[control-window.md](control-window.md): only the second continuation is the
R0 control for later comparisons.

## Claim boundary

The result is reproducible as a continuation from the recorded full-loading
parent through the Coupled/Global-Time-Step treatment, but it is not a clean
fresh-start experiment. The approximate accidental stage and the controlled
2,000-iteration loading ramp are lineage, while the terminal second `+1,000`
is the comparison control. The control remains discovery evidence: persistent
reverse flow and turbulent-viscosity limiting mean it must not be described as
a converged or physically validated operating state.
