# Phase 7b S20 — Results

**Status: API recovered; report and export repaired; S20 running.**

The 2026-09-21 NZ retry verified the loaded N0 case, corrected the maximum-speed
report and successfully computed every screen report after reload. Current run:
`PyAnsys/output/p7b-s020-20260920T221831Z/manifest.json`.
The earlier N0 failure below remains implementation evidence, not a scientific
screen result.

**Observed:** a separate 50-iteration collector-source startup diagnostic
completed with native/expression inventory agreement, all residual rows and
no recorded Cortex segmentation fault. It ended with 0.0037996848 m³ liquid
(3.3504481 kg); effectively none had reached the lowest collector. This
source diagnostic was not counted toward the five-case screen.

The fully instrumented S20 child was freshly initialized, saved and reopened
with the exact collector cells and interface-face accounting. Its solve
request advanced zero iterations because the new maximum-speed expression
omitted the mixture phase context. The source code now supplies that context.
During recovery, the API stopped responding before the case-read command was
sent; independent health, build-info, Settings and Scheme probes timed out.
No scientific-screen iteration or physical conclusion follows from this block.

**Inferred:** the corrected source route and exact-face recorder are viable
for bounded diagnostics. A practical nonzero removal/stability claim remains
untested. The API stall's cause is unknown; no shutdown command was issued.

Four fixed sections with ten fields each have now been exported and verified
at N0. The steady solve has reached N50 with complete native scalar history and
continuous collector-flux rows; the last PC flux row matched local readback.
A matching N50 checkpoint pair is saved, and the runner is continuing to N500
then the approved N5000 horizon. This early checkpoint does not establish
steady convergence or effective liquid removal.

**Missing Info:** the full 5,000-iteration history and final
pair, and the prescribed comparative analyses. The S20 runner is active; consult its manifest for verified progress.

Evidence: [technical diagnostics](../diagnostics.md),
[execution paths](run-paths.yaml),
failed N0 build receipt (local generated artifact): `PyAnsys/output/p7b-s020-20260918T065338Z/manifest.json`,
recovery timeout (local generated artifact): `PyAnsys/output/p7b-s020-20260918T070215Z/manifest.json`.
Required scientific evidence remains fixed by [setup.md](setup.md).
