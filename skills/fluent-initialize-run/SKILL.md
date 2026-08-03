---
name: fluent-initialize-run
description: Verify initialization for an existing Fluent case and run or resume the calculation safely. Use when Codex must discover a working initialization sequence, replay it through the narrow run worker, wait through Fluent restarts, reconnect, verify checkpoints, and continue without reinitializing resumed data.
---

# Fluent Initialize and Run

Start from a verified `.cas.h5`. Read the setup Markdown directly and do not
change the physical setup in this skill.

## Process

1. Search similar cases and previous successful TUI commands for a known
   initialization sequence.
2. Connect to Fluent, load the case, and inspect the initialization options.
3. Try the most likely sequence, then verify the initialized state through
   readback, a small data save, or another suitable check.
4. If necessary, reload the original case and refine the sequence until a clean
   replay works.
5. Give the verified ordered TUI commands to the narrow Fluent-PC run worker.
6. Run to the requested iteration target. If the stopping condition requires
   dynamic judgment that the worker does not support, keep the laptop agent
   supervising it.
7. Verify the final case/data pair before handing it to analysis.

Resume requests must load the chosen case/data pair and must never initialize.

## Retry and reconnect

If an initialization command fails while Fluent remains healthy, inspect the
response, revise the sequence, reload the source case, and try again.

If Fluent or gRPC fails:

1. wait for the watchdog to publish a newer healthy generation; startup may
   take several minutes;
2. poll patiently and keep the user updated;
3. reconnect and discard stale handles;
4. reload the verified source case during initialization discovery, or the
   agent-selected checkpoint during run recovery;
5. verify the restored state;
6. continue from that verified point.

Never resume automatically just because checkpoint files exist. The laptop
agent must inspect and accept the pair first.

## Evidence and completion

Keep the verified initialization command sequence, run receipt, final
case/data paths, completed iteration or stopping evidence, and the most useful
recovery checkpoint. Do not require a full failure log.
