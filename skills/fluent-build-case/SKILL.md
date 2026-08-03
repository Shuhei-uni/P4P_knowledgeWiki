---
name: fluent-build-case
description: Build and verify an Ansys Fluent case from setup Markdown and an optional parent case. Use when Codex must apply setup changes through laptop-controlled PyFluent or TUI, reuse previously successful commands, recover from Fluent restarts, and deliver a verified `.cas.h5`.
---

# Fluent Build Case

Read the setup Markdown directly. Do not hash or compile it.

Keep the laptop agent responsible for understanding the setup, choosing
commands, checking results, and deciding what to retry. The Fluent computer
only provides the live Fluent session.

## Process

1. Read the setup Markdown, parent case, relevant repository instructions, and
   any similar completed setup.
2. Search existing setup scripts, knowledge files, and past cases for TUI/API
   commands that already worked. Use these as the strongest starting evidence.
3. Connect to Fluent, confirm health and generation, and load the parent case
   or mesh.
4. Inspect the live state before changing it.
5. Apply settings in dependency order. After any tree-changing operation,
   reacquire handles.
6. Read each important setting back. A command returning without an exception
   is not enough.
7. Save case-only checkpoints at useful verified boundaries.
8. Reload and inspect the final `.cas.h5` before accepting it.

## Retry and reconnect

If a command is rejected but Fluent remains healthy, inspect the response,
adjust the command, and retry in the same session.

If Fluent or gRPC fails:

1. keep the last verified case checkpoint;
2. allow the watchdog to restart Fluent;
3. wait for a newer healthy connection generation—this may take several
   minutes;
4. poll patiently and keep the user updated rather than giving up early;
5. reconnect and discard every handle from the old session;
6. reload the last verified case;
7. confirm the restored state, then continue.

Stop for human review only when the restored state cannot be verified or the
setup intent is genuinely unclear.

## Evidence and completion

Keep the final proven TUI/API sequence and important readbacks. A detailed log
of every failed experiment is not required.

Return the verified case path, the successful commands or script used, the
important readbacks, and any unresolved assumptions.
