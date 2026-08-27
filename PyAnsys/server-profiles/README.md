# Fluent server profiles

This directory stores small, non-secret descriptions of the remote filesystem layout used by each Fluent server.

The purpose is operational consistency: a run supervisor should know where active cases, run outputs, checkpoints, and final data belong on the selected Fluent machine without inventing a new directory scheme each time.

A server profile is routing and filesystem knowledge only. It must never be used as evidence of which scientific case is currently loaded.

## Profile convention

Use one YAML file per configured endpoint, for example:

```text
server-1.yaml
server-2.yaml
server-3.yaml
student.yaml
```

Keep only paths and operational notes that have been directly observed or explicitly supplied by the user. Do not guess missing roots.

A minimal profile may contain:

```yaml
server: 1
path_style: windows
working_root: 'C:\\known\\working\\root'
experiment_root: 'C:\\known\\experiment\\root'
temporary_root: 'C:\\known\\temp\\root'
notes:
  - 'Keep active Fluent run data on local storage.'
```

Do not store IP addresses, passwords, server-info credentials, tokens, or other secrets here. Connection credentials remain in the existing environment configuration.

## Run use

`supervise-fluent-run` should read the matching profile before allocating an operational run directory. If the experiment setup already gives explicit remote paths, those paths take precedence.

If no verified profile or explicit path exists, stop before launching and obtain/inspect the correct remote path. Once a path is verified, it may be added to the profile for future runs.

Do not infer case identity, iteration state, or scientific provenance from the server name or directory alone.