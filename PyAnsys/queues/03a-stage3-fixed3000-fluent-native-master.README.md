# 03A Stage-3 fixed-3000 Fluent-native handoff

Journal: [`03a-stage3-fixed3000-fluent-native-master.jou`](./03a-stage3-fixed3000-fluent-native-master.jou)

This is a Fluent TUI journal. Once submitted, Fluent owns initialization, every
solve block, native autosave, residual output, and paired case/data writes. No
Python process is required to remain in the iteration path.

## Before submitting the journal

1. Recover server 2 to a top-level Fluent prompt. If it is still waiting inside
   a boundary-condition command, press `Ctrl+C` once and enter `q` until the
   normal top-level prompt returns. If the session does not recover, restart
   Fluent without changing or overwriting the released P0.

2. Create and verify these five Fluent-machine-local boundary-settings files:

   ```text
   C:\FluentRuns\03A-stage3\F11\F11-10pct.set
   C:\FluentRuns\03A-stage3\F11\F11-20pct.set
   C:\FluentRuns\03A-stage3\F11\F11-40pct.set
   C:\FluentRuns\03A-stage3\F11\F11-80pct.set
   C:\FluentRuns\03A-stage3\F11\F11-100pct.set
   ```

   Each file must change both `liquidinlet` and `steaminlet` velocity
   magnitudes together, while preserving turbulence intensity, hydraulic
   diameter, and every other boundary setting. The intended magnitudes are:

   | File | Both split-inlet velocities |
   |---|---:|
   | `F11-10pct.set` | 2.7118 m/s |
   | `F11-20pct.set` | 5.4236 m/s |
   | `F11-40pct.set` | 10.8472 m/s |
   | `F11-80pct.set` | 21.6944 m/s |
   | `F11-100pct.set` | 27.118 m/s |

   The journal applies these with Fluent's `file/read-settings` command. Do not
   start the master journal until all five files exist and have been read back
   successfully in a disposable verification pass.

3. Confirm that the released P0 exists at the path embedded in the journal and
   that `C:\FluentRuns\03A-stage3\F02`, `F04`, `F11`, `F06`, and `F05` are on
   local Fluent-machine storage. No output path in the journal points to the
   OneDrive P0 directory.

4. Start the journal from Fluent's TUI or File → Read → Journal. Do not wrap it
   in a Python loop or submit individual iteration commands from a client.

## Queue and iteration count

| Case | Stages | Iterations |
|---|---|---:|
| F02 | carrier-only 3000, full Mixture 3000 | 6,000 |
| F04 | carrier-only 3000, full Mixture 3000 | 6,000 |
| F11 | 10%, 20%, 40%, 80%, 100%, each 3000 | 15,000 |
| F06 | carrier-only 3000, full Mixture 3000 | 6,000 |
| F05 | full Mixture 100% 3000 | 3,000 |
| **Total** | **12 explicit solve blocks** | **36,000** |

F02, F04, and F06 enable `mp` and `drift` after the carrier-only checkpoint
without reinitializing. F11 stays full Mixture and changes only the inlet
loading between blocks. F05 starts directly in full Mixture at 100% loading.

## Floating-point-error behavior

The journal deliberately contains no rescue logic and no numerical model or
discretization changes. After each `solve/iterate 3000`, it writes a paired
case/data checkpoint and a residual-history file before issuing the next
explicit step.

That is best-effort continuation only. If Fluent reports an FPE and returns
control to the journal, the following write and next command can execute. If
the FPE terminates the current solve command, the journal, or the Fluent
process, no later TUI command can run; the latest native autosave is then the
only automatic recovery artifact. A single TUI journal cannot guarantee
“save-after-FPE and continue” after a process-level failure.

Do not use a partial/FPE state as scientific evidence of convergence. Preserve
the transcript, autosave pair, and the stage filename, and classify that stage
as interrupted or numerically failed during later review.

