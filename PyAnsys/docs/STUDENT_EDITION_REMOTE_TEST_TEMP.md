# Student Edition Remote Test Availability

Temporary operational note for future agents.

## Status

A Windows PC with Ansys Student Edition is now reachable over SSH and can be used for `PyAnsys` testing when the professional-license Fluent gRPC servers are full.

Current status:
- SSH access works
- SSH key authentication works
- this machine can be used as the fallback remote execution target for Student-edition tests

## Current Remote Target

- Host IP: `10.0.0.5`
- SSH user: `shuhei.yokkaichi123@outlook.com`
- Windows host name seen in session: `HOME-DESKTOP-SH`

Current direct connect form:

```bash
ssh "shuhei.yokkaichi123@outlook.com"@10.0.0.5
```

Recommended local SSH alias on the Mac:

```sshconfig
Host windows-pyansys-student
    HostName 10.0.0.5
    User shuhei.yokkaichi123@outlook.com
    IdentityFile ~/.ssh/id_ed25519
```

Then connect with:

```bash
ssh windows-pyansys-student
```

## Windows-Side SSH Notes

- The Windows account is in the `Administrators` group.
- Because of the default Windows OpenSSH config, key auth had to be placed in:

```text
C:\ProgramData\ssh\administrators_authorized_keys
```

- User-home `authorized_keys` alone was not sufficient for this admin-backed account.

## Intended Use

Use this machine when:
- professional-license Fluent servers are occupied
- the task needs a live Windows Fluent environment
- a Student-edition smoke test is acceptable
- the goal is script-path validation, environment validation, or partial workflow testing

Do not assume Student Edition is a perfect substitute for the professional environment. Treat it as a fallback validation target.

## Important Limits

- This target is currently identified by LAN IP `10.0.0.5`
- if the machine leaves the LAN or the IP changes, reconnect details must be updated
- if remote access from anywhere is needed, add Tailscale or another VPN layer
- Student Edition may differ in licensing limits, model availability, or automation behavior

## Basic Remote Workflow

Connect:

```bash
ssh windows-pyansys-student
```

Move into the repository on Windows:

```powershell
cd "C:\Users\Shuhei Yokkaichi\path\to\P4P_knowledgeWiki"
```

Reset the repo to current remote `main` if needed:

```powershell
git fetch origin
git checkout main
git reset --hard origin/main
git clean -fd
```

Enter `PyAnsys`:

```powershell
cd PyAnsys
```

If the environment needs to be created:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-minimal.txt
```

## Guidance For Future Agents

When a task requires remote Windows execution:
1. Prefer the professional-license Fluent servers if they are available.
2. If they are not available, use this Student-edition SSH target as the fallback test path.
3. Distinguish clearly between:
   - script-structure validation
   - environment/bootstrap validation
   - live Fluent behavioral validation
4. Record any Student-edition-specific limitations discovered during testing.

## Related Notes

- [WINDOWS_SSH_SETUP_TEMP.md](./WINDOWS_SSH_SETUP_TEMP.md)
- [PyAnsys/AGENTS.md](../AGENTS.md)
