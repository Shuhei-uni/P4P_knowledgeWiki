# Fluent server profiles

This directory stores small, non-secret descriptions of the remote filesystem layout used by each Fluent server.

The purpose is operational consistency: a run supervisor should know where active cases, run outputs, checkpoints, and final data belong on the selected Fluent machine without inventing a new directory scheme each time.

A server profile is routing and filesystem knowledge only. It must never be used as evidence of which scientific case is currently loaded.

## Profile convention

Use one YAML file per configured endpoint/profile. Because multiple operators may each have a local `server-1`, `server-2`, and so on, make the profile filename itself collision-resistant with a stable operator or endpoint namespace, for example:

```text
shuhei-server-1.yaml
shuhei-server-2.yaml
partner-server-1.yaml
partner-server-2.yaml
```

The static profile does not need to contain the server IP. Keep connection/IP resolution in the existing environment or connection configuration, especially while this repository is public.

A minimal profile may contain:

```yaml
profile_id: shuhei-server-1
server_id: server-1
connection_key: SHUHEI_FLUENT_SERVER_1
path_style: windows
working_root: 'C:\\known\\working\\root'
experiment_root: 'C:\\known\\experiment\\root'
temporary_root: 'C:\\known\\temp\\root'
notes:
  - 'Keep active Fluent run data on local storage.'
```

Keep only paths and operational notes that have been directly observed or explicitly supplied by the user. Do not guess missing roots.

Do not store passwords, server-info credentials, tokens, or other secrets here.

## Runtime server identity

A short server ID alone is not unique enough for execution records when collaborators may each have `server-1`, `server-2`, and so on.

During live fleet preflight, resolve the actual IP used for the connection and form a runtime server reference from both values:

```yaml
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'
```

Use `server.ref` as the canonical server identity in run placement, execution handoffs, and `run-paths.yaml`. Keep `server.id` and `server.ip` as separate fields as well so tooling does not need to parse the combined string.

Do not use `server_id` alone as a durable run identity. The IP is live operational metadata and should be recorded from the endpoint actually used for the run rather than guessed from the profile name.

If a public/routable IP or another endpoint value should not be committed to this public repository, keep that sensitive value out of Git and use the approved private operational record instead. Private/local endpoint details should not be exposed merely for naming convenience.

## Run use

`fluent-fleet-orchestration` should resolve the static profile plus the live endpoint into the runtime server reference before allocating work. `supervise-fluent-run` then uses that resolved placement.

If no verified profile or explicit path exists, stop before launching and obtain/inspect the correct remote path. Once a path is verified, it may be added to the profile for future runs.

Do not infer case identity, iteration state, or scientific provenance from the server reference, profile name, or directory alone.