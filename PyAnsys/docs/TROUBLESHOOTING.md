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

## 7. Student Edition exits under SSH

If the Windows Student Edition host starts Fluent and then the gRPC server dies immediately under SSH, treat that as a launch/EOF problem first, not a setup-script problem.

Use the local manual-launch fallback in `src/pyansys_fluent/connection.py`:

```text
- set FLUENT_LOCAL_EXE on the Windows host
- keep stdin open by launching Fluent directly instead of through a short-lived SSH shell
- verify the session with scripts/connection/check_connection.py
```

If `connect_to_fluent()` starts asking for TLS certificates or otherwise refuses the remote handoff, switch to the local manual-launch path instead of iterating on shell quoting.

When launching a Windows batch wrapper over SSH, call it explicitly:

```text
call C:\path\to\run_setup08b_smoke.cmd
```

## 8. Visualization import problems

If `ansys-fluent-visualization` imports fail, still continue with `ansys-fluent-core`, `pandas`, and `matplotlib`. Visualization can be fixed later.

## 9. Meshing not available

`ansys-meshing-prime` requires access to Ansys Prime Server / meshing capability. Treat it as a later-stage feature.

## 10. Local one-inlet parity script behaves differently than older notes

The current local hardened smoke-test path is documented separately in:

```text
docs/LOCAL_ONE_INLET_SMOKE_TEST.md
```

Use that note when the task is:

```text
- local Fluent launch
- local mesh-only setup
- one mixed steam-water inlet reconstruction
- short parity smoke test
- writing local case/data outputs
```
