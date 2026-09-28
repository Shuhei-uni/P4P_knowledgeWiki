# E7 checkpoint recovery — 28 September 2026

Andy accepted the bounded phase-finish plan and instructed execution. Recover
E7 unchanged to its existing absolute N5000 horizon; do not initialize a fresh
case or change physics/source/solver controls. The accepted later source audit
and conditional single startup contrast remain separate decisions after G7.

## Reconciled evidence and replay budget

The newly reachable configured endpoint responds as Fluent 2025 R2 but has no
active cell-zone or run-calculation tree and no named expressions. There is no
live E7 field to preserve. The exclusive controller lock is free. Through the
Fluent API, the prior run's N50 and N500 case/data pairs exist; none of its N1000,
N1500, …, N4500 or final pairs exist. The last controller-issued block was
N500→1000. Recovered native scalar history reaches N680 and native residual
history N679; local flux reaches N679 and speed/diagnostic history N678.
The old process's exact final iteration is unavailable.

Use the N500 pair only after live reload verifies its counter, fields, ordered
geometry and full E7 settings against the saved N500 evidence. Preserve the
old partial records unchanged. A separately derived complete N1–500 prefix
will seed the new evidence; the old N501–680 tail is retired partial evidence,
not spliced into the recovered trajectory. Any overlapping replay can be
compared diagnostically but need not be bitwise identical after restart.

The recovery issues at most **4500 additional iterations**, with an N505
recording/snapshot/checkpoint check, then N1000 and every500 to N5000. Absolute
coordinate cap stays5000. Including the old issued block, the original attempt
could have advanced at most1000; thus the combined attempt/recovery compute
ceiling is5500 iterations (5000 retained trajectory plus at most500 retired
replayed steps). This explicit bounded replay replaces lost live state; it is
not a longer convergence continuation. No hidden solve, counter offset or
residual reset is permitted.

## Preservation and evidence requirements

- Read the N500 pair into the empty session. Compare all saved physical arrays
  and geometry, excluding uncalibrated mass-imbalance storage. Verify all eight
  residual settings, source slots/definitions, methods/controls and interval1.
- Keep the original remote report/transcript untouched. Write a unique report
  seeded with the exact N1–500 prefix and a unique transcript prefix. Rebind
  only report destination, then save a unique recovery pair and reopen/read
  back before continuation. Record any representation-only file-path change.
- Use new capture IDs and unique local-PC checkpoint names. Reuse the original
  verified N0 sections/parity and the N0/N50/N500 snapshot prefix with explicit
  provenance. Every new iteration retains scalar, exact-face flux, speed and
  eight residuals; all scheduled/event snapshots and final fields remain due.
- N505 must verify normalized/native inventory parity, raw fraction/sum capture,
  source lag, iteration parity and the paired checkpoint before normal batches.
- Report reload-dependent differences explicitly; an unexpected field/control
  difference blocks the continuation for investigation, not numerical rejection.

The E6/E7 comparison still uses N4501–5000 and inventory means N4001–4500 versus
N4501–5000, with unchanged closure/inventory/residual criteria. State clearly
that E7 includes a verified checkpoint restart at N500 while E6's continuation
history differs; do not claim an uninterrupted bitwise solver contrast.

Machine inspection and immutable recovered remote files:
`PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/`.
Only one sequential controller may own the endpoint. Fluent must remain open.

## Native report rollover repair at N505

The first controller solved N501–505 and captured all residual/flux/diagnostic records. Fluent automatically selected a new `_501.out` scalar file, including an identical N500 boundary row. Reading the originally seeded filename therefore returned only N1–500 and correctly stopped the controller. The native segment was recovered, and full N1–505 history passes with 504 zero-error source-lag pairs. An independent no-solve API check verified exact live N505 fields/settings and saved a unique paired checkpoint.

The replacement starts from unchanged live N505, with 4495 steps remaining. It combines the hash-verified immutable N1–500 prefix and the separately preserved native scalar segment only after verifying headers, continuous indices, finite values and exact equality of the repeated boundary row. Missing indices and conflicting boundary values are rejected by offline tests. No new scientific treatment or repeated solve is involved. The total recovery remains 4500 steps and the original cumulative ceiling remains5500. N505 is the additional whole-cell normalization proof; no further extra startup block is needed.

## Recorder RPC interruption at N687

The N505 continuation stopped producing local records at N686/687. Its iteration RPC and recorder callback remained waiting for over twenty minutes. The sole owned local Python controller was retired without any Fluent exit command. A fresh sequential API connection found Fluent at N687 with its pending iteration command active. An end-of-iteration interrupt plus release of the sole retired controller's pause registration (ID2) returned the endpoint to idle N687 without another iteration. The precise transport-stall cause remains unresolved; this is not evidence of numerical divergence.

A unique N687 case/data pair was saved. Recovered native scalar and all eight residual histories are continuous through N687, with 686 exact zero-error source-lag pairs. The last local flux row exactly matches both its PC file and independent live face reductions. Only the missing N687 speed row is recovered from unchanged live native speed, with scalar and full-cell snapshot parity. Both raw phase fractions and normalized-native inventory parity are retained. The new N687 full-cell snapshot is explicitly additional recovery evidence, alongside N505; no required scheduled/event sample is replaced. Original raw partial files remain unchanged.

The sole replacement resumes unchanged live N687, with **4313 iterations remaining**, checkpoints N1000 and every500 through absolute N5000. It rechecks exact preserved fields, geometry, sources, methods, controls and all native histories before solving. No reload, initialization, counter offset or further replay is used. Total recovery still adds4500 and cumulative attempted-compute ceiling remains5500. The controller now persists the exact callback/pause registration ID immediately after registration to make ownership explicit in future recovery. All physical and numerical settings remain unchanged. Evidence is under `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n505/rpc-stall-recovery/`; the new job is `resume-n687/job.yaml`.

## Host sleep and transport recovery at N1631

The N687 controller saved N1000/N1500 and recorded through N1630 before its iteration RPC failed with `Stream removed (recvmsg:Operation timed out)`. macOS records clamshell sleep at 15:54:44 NZDT on28 September (02:54:44UTC), matching the final recorder timestamp; the lid opened at15:57:18 and the error surfaced at15:57:37. This strongly supports host sleep interrupting transport. It does not establish numerical failure. The earlier N687 stall also followed a clamshell-sleep event, but that transport cause is less directly established.

The exited controller had removed registration3, while Fluent remained at a pending pause atN1631. A verified end-of-iteration interrupt followed by release of that exact owned pause returned idleN1631 without advancement. A unique local-PC pair, exact geometry/settings/sources, whole-cell raw fractions and independent normalized-native inventory proof were preserved. All native scalar and eight residual histories cover1–1631 with1630 zero-error source-lag pairs. The missing N1631 face-flux and speed records were recovered from unchanged idle state with native readback and scalar/full-cell parity. Their provenance is explicit; no raw partial file was overwritten.

The replacement is predeclared to resume **unchanged live N1631 with3369 steps remaining**: N2000 and every500 to absoluteN5000, with the same diagnostic schedule and final fields. It must independently reverify exact live fields, sources, settings and full native histories before solving. No reload, initialization, counter offset or additional replay is allowed. The extra N1631 recovery snapshot joins505/687; all originally required snapshots remain due. Total added recovery compute remains4500 and cumulative attempted ceiling5500. The new job wraps the Python controller with process-lifetime `caffeinate -i`, preventing idle sleep without changing persistent power settings. This does not prevent deliberate lid-close sleep; the host must remain awake with the lid open during client supervision.

Evidence: `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n687/transport-recovery-20260928T0305/`; selected job: `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n1631/job.yaml`. Offline positive and negative checks pass; launch and live progress belong to phase-state. N500 restart disclosure and the original late comparison windows remain unchanged.

## Network-loss recovery at N2185

The N1631 controller saved N2000 and recorded throughN2184 before a network/address error on the Mac; callback cleanup reported network unreachable. No new sleep event was found. A read-only API check failed, then Andy requested another attempt after restoring connectivity. The next check found liveN2185. Its exact owned pause4 was unregistered/released after an end-of-iteration interrupt, returning idleN2185 without advancement. The cause beyond network loss is not established; this is not numerical failure.

A unique local-PC pair and exact live geometry/settings/source proof are preserved. Native scalar/all-eight-residual histories cover1–2185 with2184 zero-error source-lag pairs. Missing face-flux and speed2185 were recovered from unchanged idle state with unique native persistence/readback, independent face reduction, scalar/full-cell parity and raw/normalized inventory evidence. Raw retired records remain immutable. Evidence: `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n1631/network-recovery-20260928T0408/`.

The sole replacement is predeclared to resume unchanged liveN2185 for **2815 remaining steps**, withN2500/every500 to absoluteN5000. Original scheduled/event snapshots and final fields remain required; extra recovery snapshot2185 joins505/687/1631. No reload/init/counteroffset/replay; total recovery additions4500 and cumulative attempted ceiling5500 remain unchanged. Exact fields/settings and native histories must pass again before compute. Process-lifetime idle-sleep protection remains; continuous network access is also required. Selected job: `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n2185/job.yaml`; phase-state owns actual launch/progress.
