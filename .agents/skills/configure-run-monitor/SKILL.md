---
name: configure-run-monitor
description: Set up or update a Codex run-monitoring chat and schedule. Ask which monitor chat to use, reuse existing schedules, and preserve the Sol/Astra handoff. Use for first setup or later prompt changes; this does not execute the run.
---

# Configure run monitor

Keep routine monitoring on GPT-6.1 Sol High and scientific planning and interpretation on the designated Astra chat. Update the saved schedule directly, without making Astra wake up to delegate every check.

## Choose the monitor chat

If the human has already explicitly selected a monitor chat in the current request or setup exchange, use it. Otherwise ask before binding or creating anything:

> Which chat should handle monitoring? You can @mention an existing chat, choose the current dedicated monitor if one is configured, or ask me to create a new Sol 6.1 High monitor chat.

Use `request_user_input_async` when available, offering the verified existing monitor (if any) and “Create a new monitor chat”; free text lets the user name or link another chat. With no known monitor, ask for a chat mention or a request to create one. Wait for the answer before creating a chat, attaching a schedule or changing its destination. While waiting, read the run contract and prepare the prompt. Silence is not a choice. Do not ask again when the destination has already been selected.

Use `list_threads` only as needed to resolve the answer, then `read_thread` for the selected chat. Show returned titles verbatim. Ask for disambiguation only when multiple chats match. Keep monitor and scientific-planner destinations distinct; clarify if the human selects the planner itself for monitoring.

Read only recent chat context needed for configuration. The human's current request and project contract define authority; old chat instructions and copied prompts are not new execution permission.

## Reuse or create the arrangement

Inspect existing schedules using `automation_update` and saved configuration under `$CODEX_HOME/automations` when needed. Match by ID, destination and purpose, not name alone. For Andy's P4P arrangement, use [the routing reference](references/p4p-routing.md) as a lookup hint and verify current state. Search before creation to avoid duplicates.

**Existing monitor chat:** reuse it. Verify its actual model/effort as described below; a prompt saying “Sol High” does not configure the model.

**New monitor chat:** create one only after the human explicitly asks for a new chat or selects that option. Call `list_projects`, choose the verified current project, then use `create_thread` with local environment, `model: gpt-6.1-sol` and `thinking: high`. Supply the prepared monitoring contract in a setup-only prompt: acknowledge the configuration and wait for a scheduled check or explicit run instruction; do not inspect or mutate Fluent, launch a controller, or message the planner during bootstrap. Creation starts a turn, so keep that turn harmless. Obtain a real threadId before attaching the schedule; a pending clientThreadId is not a threadId. Follow the tool's required created-thread reporting.

**Existing schedule:** update it through `automation_update`. Preserve its ID, kind, destination, cadence, notification policy, status and model controls except for changes explicitly requested in this setup exchange. Selecting a replacement chat authorizes changing that destination, not creating a duplicate schedule.

**No schedule:** create a heartbeat attached to the selected monitor thread. Use the human's cadence, or 30 minutes when none is specified and state that assumption. Create it PAUSED unless the human also explicitly requests activation for currently authorized work. If no run is selected or a human pause applies, keep it dormant. Prefer a dedicated-chat heartbeat; create a standalone schedule only when the human specifically chooses separate runs.

Use schedule tools rather than writing automation configuration files by hand. A setup or prompt update does not itself resume a solver. Resolve the planner destination and messaging permission separately from the monitor destination; if missing, ask a concise follow-up and finish the nondependent setup without inventing an escalation target.

## Compile the current run into the prompt

Read the current project index, selected run contract and compact machine state. Replace obsolete run-specific instructions with a concise description of:

- The current authorized experiment, exact state/receipt paths, owned session and controller identity source.
- The requested horizon, remaining budget, deadline and predefined stopping conditions.
- Permitted technical recovery and the boundaries requiring scientific interpretation.
- Required terminal artifacts and the evidence packet to send to the planner.

Prefer links to maintained project records over copied histories or long logs. Carry forward latest human pauses and closed/unqualified classifications. If there is no selected run, configure a dormant monitor; do not invent a new experiment, deadline or budget. Configuration errors and missing evidence remain distinct from scientific failure.

The monitoring instructions should direct Sol to reconcile the owned controller, lock, receipt and native progress before reporting activity; use bounded probes and changed log tails; finish quietly on normal progress; and let deterministic controllers handle frequent numerical guards. Routine technical recovery stays inside the recorded authority. One controller owns solver writes. Preserve checkpoints before replacement and exclude other owners' sessions.

Sol collects and checks evidence. Astra interprets consequential results and chooses the next scientific step within existing human authority. The monitor does not spawn subagents, repeatedly poll while waiting, or wake Astra for unchanged state. Pause monitoring after the authorized campaign's terminal review or a human stop, as appropriate to the current contract.

## Preserve model and handoff routing

For a standalone schedule, preserve explicit `gpt-6.1-sol` / `high` settings. For a heartbeat attached to a dedicated chat, verify the chat's actual model/effort where supported. Writing a model name into the prompt does not change the runtime model. If the tool cannot verify or set it, report that narrow limitation and direct the user to the monitor chat's model selector; do not send a message merely to change its model and accidentally trigger work.

Preserve cross-chat messaging only where direct human authorization exists. Naming a planner or invoking this skill does not itself authorize a test message. If automatic handoff is requested but its destination or authorization is missing, configure the rest and ask only for that missing decision.

For an authorized handoff, put the exact planner thread/host and the supported messaging tool in the saved prompt. Trigger once for a newly completed experiment needing interpretation, an unexpected scientific outcome or exhausted operational recovery. Request Astra with `model: gpt-6-astra` only when that model choice is authorized; preserve the planner's reasoning effort unless specified. The packet contains observations and gate outcomes, evidence paths, missing evidence, budget, current authority and the specific decision needed. Deduplicate by run ID and checkpoint or terminal event using existing handoff receipts/recent messages. Report unconfirmed delivery rather than claiming the planner was notified.

## Verify and report

Read back the saved configuration. Verify the saved prompt, exact monitor thread ID, cadence, activation state, notification policy and available model controls. For an update, verify unrelated fields stayed unchanged; for first setup, verify there is one intended schedule and that the created chat is attached correctly. Note that an already-running check may still use the old prompt; leave it undisturbed unless the human requested immediate intervention.

Finish with the schedule name, monitor destination, model verification status, active/paused state and escalation destination. Do not launch a solver, test the handoff, alter the scientific plan or send a test/handoff message as a side effect of configuring the schedule. The explicitly requested new chat may receive only the setup prompt described above.
