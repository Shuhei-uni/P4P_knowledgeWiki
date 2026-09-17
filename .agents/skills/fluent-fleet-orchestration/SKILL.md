---
name: fluent-fleet-orchestration
description: "Discover and control the live Fluent fleet for approved scientific work: inventory exact artifacts, reconcile owned sessions, plan verified transfers and placement, make output paths explicit, and preserve important restart states through OneDrive."
---

# Fluent Fleet Orchestration

Place approved work on usable preserved sessions. Scientific artifacts, not
server aliases, are the durable identities. Use the shared
[MCP integration](../fluent-live-inspection/mcp-integration.md) contract.

## Establish authority and identity

Read the phase `CONTEXT.md` and `phase-state.yaml`; consume the existing entry
check-in, including full/restricted Fluent authority, without asking again.
Keep artifact ID, setup ID, run ID, endpoint and goal lease separate.

```yaml
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'
```

Resolve the actual endpoint; the example is not configuration. A profile is
filesystem knowledge, not proof of availability or loaded case identity.

An exclusive lease permits stopping a calculation, preserving a recovery pair,
loading another approved parent and reassigning still-running sessions. It does
not permit process shutdown/relaunch or overwriting verified durable artifacts.
Restricted leases retain their explicit limits. Preserve valuable unreplicated
state before a destructive takeover; reconcile prior job ownership first.

## Preflight each compute wave

Check every configured endpoint that can reasonably be checked. Use the MCP
process bound to that alias: `session_status`, argument-free `connect` only when
needed, `solver_status`, and scoped live discovery/readback. Determine:

- current reachability, resolved endpoint, versions and usable capabilities;
- idle/running/blocked/uncertain state and the owner of any active job;
- exact loaded identity or its uncertainty;
- local paired parents/recovery states, verified remote roots and transfer options;
- valuable state that a takeover would lose.

MCP session tools are not a remote filesystem browser or fleet scheduler. Use
reviewed host/file-transfer helpers for actual file presence, hashes, directories
and OneDrive replicas; record that capability gap and exact helper. Do not infer
file availability from a case name or alias.

Enforce one writer per Fluent session across all agents, MCP processes and direct
workers. Under an exclusive lease, a busy inherited solve is not automatically
protected, but reconcile it before stopping or replacing it. Continue jobs that
belong to the active plan. Use only an authorized, verified non-terminating stop
route; `disconnect` and `manage_fluent` are not takeover tools. If a safe stop
cannot be performed, preserve the block and use another valid lane.

## Place by exact-parent locality

Prefer a compatible usable server with the exact verified parent already local,
then a verified OneDrive replica, then a parent promotable from another server.
If the only trusted copy is inaccessible, block that placement.

Return real capacity, locality and compatibility to the designer. Parallelism
serves approved science; it does not authorize filler experiments. Repeat
preflight whenever a new wave starts or availability materially changes.

## Keep one path authority

Populate and reconcile the experiment's existing `run-paths.yaml`:

- phase/lease, setup/run, `server.ref`, separate alias/IP and profile;
- takeover/recovery facts and exact artifact identity;
- actual Fluent working directory, staging/run roots and parent/prepared/final pairs;
- autosave/checkpoint/report/monitor/transcript/export destinations;
- worker logs/manifests and completion verifier;
- OneDrive destinations and verified/local-only durability.

Use MCP to inspect inherited file-backed definitions and validate/run only the
approved path corrections. Preserve their scientific meaning. Host helpers prove
directory existence and writability. Resolve required relative paths deliberately;
loading a case does not prove a working-directory change. Reconcile actual paths
after smoke and final execution, without creating a competing durable manifest.

## Promote selected artifacts

Preserve complete matching case/data pairs for important finals, likely parents,
expensive selected checkpoints and difficult-to-reconstruct reference states.
Keep routine autosaves local. Save via the approved MCP route, then use the
reviewed transfer layer to copy and verify both files, preferably by hashes.
Record artifact ID, source setup/run, progress, origin endpoint and destinations.
A file appearing in a local OneDrive folder is not proof of completed replication.
If replication fails, keep the local pair and record `LOCAL_ONLY` durability debt.

## Handoff

Return fleet availability/ownership, useful artifacts, placement, takeover and
recovery facts, the canonical path map, required transfers, durability and exact
blockers. `implement-experiment` consumes this plan; the scientific loop retains
experiment selection. A status call does not prove a run complete, and a lost
response must be reconciled before another writer or solve is started.
