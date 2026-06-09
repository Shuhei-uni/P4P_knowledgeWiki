# Likely Issues and Quick Fixes

## 1. Connection timeout

Check:

```text
- Is Fluent open?
- Did you start the gRPC server?
- Is the port correct?
- Did the port change after restarting Fluent?
- Did Windows Firewall block the port?
- Are laptop and Fluent PC on the same network/VPN?
```

## 2. server_info.txt says 127.0.0.1

Use the Fluent PC's real IPv4 address from `ipconfig`.

## 3. Password/authentication failure

Generate/check a fresh `server_info.txt`.

## 4. PyFluent version mismatch

If your Fluent version is older, the latest PyFluent may not work. Check the Fluent version first and match PyFluent accordingly if needed.

## 5. File path problem

Laptop path and Fluent PC path are different. Use Fluent PC paths for Fluent file operations.

## 6. Codex uses launch_fluent

Correct it:

```text
Use connect_to_fluent. Fluent is running remotely and is not installed on this laptop.
```

## 7. Visualization import problems

If `ansys-fluent-visualization` imports fail, still continue with `ansys-fluent-core`, `pandas`, and `matplotlib`. Visualization can be fixed later.

## 8. Meshing not available

`ansys-meshing-prime` requires access to Ansys Prime Server / meshing capability. Treat it as a later-stage feature.

## 9. Local one-inlet parity script behaves differently than older notes

The current local hardened smoke-test path is documented separately in:

```text
docs/findings/LOCAL_ONE_INLET_SMOKE_TEST.md
```

Use that note when the task is:

```text
- local Fluent launch
- local mesh-only setup
- one mixed steam-water inlet reconstruction
- short parity smoke test
- writing local case/data outputs
```

## 10. Mesh trial harness launches Fluent and then immediately dies

Common signs:

```text
- LaunchFluentError
- Stream removed / 10054
- fluent-0-error.log or fluent-1-error.log shows Auto_Partition or segmentation fault
```

Try:

```text
- rerun with --processor-count 1
- kill stale fluent / cx2610 / ansyscl processes before relaunch
- retry the harness after a clean process reset
```

This showed up during local Student-license meshing runs and was more of a
launcher/process-stability issue than an input-mesh parsing issue.

## 11. Mesh reopens, but save fails with a license error

Common signs:

```text
- reopen succeeds
- diagnostics succeed
- write_case or write_mesh fails
- transcript says the Student license only supports less than 1048576 cells
```

Interpretation:

```text
The mesh can still be useful for diagnostics in meshing mode, but Fluent will not
let you save a result that remains over the Student limit.
```

Use:

```text
- the JSON trial report
- the Fluent transcript
- the baseline/trial comparison
```

as the main output when this happens.

## 12. `.meshdat` opens but metrics or zones are missing

Common signs:

```text
- transcript says the file was read
- warning says no nodes read
- get_cell_zones returns nothing
- report.mesh_statistics is unavailable
```

Interpretation:

```text
Treat `.meshdat` as a partial diagnostic input on this setup, not as equivalent
to `.msh`.
```

If possible, prefer the matching `.msh` for the first harness run.
