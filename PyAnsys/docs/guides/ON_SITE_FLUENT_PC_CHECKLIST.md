# On-Site Fluent PC Checklist

Use this when you finally have access to the PC with Ansys Fluent.

## 1. Before touching PyFluent

On the Fluent PC:

```text
[ ] Confirm Fluent opens normally.
[ ] Confirm the full license works.
[ ] Confirm you can open or create a solver session.
[ ] Confirm the case file you need is available on that PC.
```

## 2. Find the Fluent PC IP address

Open PowerShell or Command Prompt on the Fluent PC:

```powershell
ipconfig
```

Find the active adapter's IPv4 address, for example:

```text
IPv4 Address . . . . . . . . . . . : 192.168.1.100
```

Write it here:

```text
Fluent PC IP = ______________________
```

Do not use:

```text
127.0.0.1
localhost
```

from the laptop.

## 3. Start Fluent gRPC server

Recommended method: command line.

Open Command Prompt on the Fluent PC and run a command like:

```powershell
"C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe" 3ddp -sifile=server_info.txt
```

Adjust `v252` to the installed Ansys version.

Examples:

```text
v242 = Ansys 2024 R2
v251 = Ansys 2025 R1
v252 = Ansys 2025 R2
```

For your current Fluent 2024 R2 install, try this first:

```powershell
cd %USERPROFILE%\Desktop
"C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe" 3ddp -sifile=server_info.txt
```

If you need a 2D solver session instead:

```powershell
"C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe" 2ddp -sifile=server_info.txt
```

If Windows says the path does not exist, search for `fluent.exe` under:

```text
C:\Program Files\ANSYS Inc\
```

Then show the server-info file:

```powershell
type server_info.txt
```

It should look something like:

```text
192.168.1.100:51344
5scj6c8l
```

Write down:

```text
IP       = ______________________
Port     = ______________________
Password = ______________________
```

Alternative GUI method:

```text
Fluent → File → Applications → Server → Start...
```

If the GUI asks for server fields, use:

```text
Session name    = separator-remote
Token           = choose a temporary password/token and keep it for .env
Port            = 50055
Port span       = 1 or 10
Job service URL = leave blank
```

Notes:

```text
- Token is the FLUENT_PASSWORD value for PyFluent.
- Port is the FLUENT_PORT value.
- If port 50055 is blocked or occupied, use another high port such as 50056.
- Job service URL is not needed for a direct Fluent gRPC connection.
```

Alternative TUI method:

```text
server/start-server
```

## 4. Check server_info.txt for localhost issue

If it says:

```text
127.0.0.1:51344
```

or:

```text
localhost:51344
```

do not use that as the host from your laptop.

Use the actual Fluent PC IP from `ipconfig`, while keeping the same port/password.

## 5. Firewall rule

If your laptop cannot connect, make a temporary inbound firewall rule on the Fluent PC:

```text
Windows Defender Firewall with Advanced Security
→ Inbound Rules
→ New Rule
→ Port
→ TCP
→ Specific local port = the gRPC port
→ Allow the connection
→ Private/Domain profile if possible
→ Name: Temporary Fluent gRPC <port>
```

Delete this rule after finishing.

## 6. Fill laptop `.env`

On your laptop project folder, edit `.env`.

Use this section when Codex/PyAnsys is running on a different computer from Fluent.
If Codex/PyAnsys is running on the same Windows computer as Fluent, `localhost` or
`127.0.0.1` can work, but the remote-laptop workflow should use the real Fluent PC
IPv4 address.

Option A: explicit IP/port/password:

```text
FLUENT_IP=192.168.1.100
FLUENT_PORT=51344
FLUENT_PASSWORD=5scj6c8l
FLUENT_ALLOW_REMOTE_HOST=true
FLUENT_INSECURE_MODE=false
```

Option B: copy `server_info.txt` to laptop and use:

```text
FLUENT_SERVER_INFO_FILE=./server_info.txt
FLUENT_ALLOW_REMOTE_HOST=true
FLUENT_INSECURE_MODE=false
```

If the copied server-info file contains `127.0.0.1`, use Option A instead.

## 7. Test connection from laptop

Run:

```bash
.venv/bin/python scripts/check_connection.py
```

Expected:

```text
Connected to Fluent.
Health ...
Fluent version ...
Done. This script did not close Fluent.
```

## 8. Inspect current Fluent session

Run:

```bash
.venv/bin/python scripts/inspect_fluent_session.py
```

This should help Codex discover what Fluent can expose.

## 9. Next step after connection

Ask Codex:

```text
Connection works. Use PyFluent to inspect the current Fluent session. List the available boundary condition names, phases/materials, enabled models, and working directory. Do not run iterations yet. Build a robust inspect_case.py script for this case.
```

## 10. Important path reminder

Fluent file operations usually use paths from the Fluent PC's perspective.

This laptop path probably will not work inside Fluent:

```text
/Users/shuhei/project/case.cas.h5
```

This Fluent PC path may work:

```text
C:\FluentRemoteWork\separator_project\case.cas.h5
```

A smooth workflow is:

```text
Fluent PC:
C:\FluentRemoteWork\separator_project\
    cases\
    exports\
    logs\

Laptop:
your Codex project folder
    scripts\
    docs\
    results\
```

For the current Fluent 2024 R2 workstation test, the Fluent-PC project folder is:

```text
C:\Users\syok443\Documents\Fluent Standalone Test 1\
```

Current known subfolders:

```text
case and data\
geom\
mesh\
```

These paths should be recorded in `.env` as:

```text
FLUENT_REMOTE_PROJECT_DIR=C:\Users\syok443\Documents\Fluent Standalone Test 1
FLUENT_REMOTE_CASE_DATA_DIR=C:\Users\syok443\Documents\Fluent Standalone Test 1\case and data
FLUENT_REMOTE_GEOM_DIR=C:\Users\syok443\Documents\Fluent Standalone Test 1\geom
FLUENT_REMOTE_MESH_DIR=C:\Users\syok443\Documents\Fluent Standalone Test 1\mesh
FLUENT_REMOTE_CASE_FILE=C:\Users\syok443\Documents\Fluent Standalone Test 1\case and data\FFF.1-2.cas.h5
FLUENT_REMOTE_DATA_FILE=C:\Users\syok443\Documents\Fluent Standalone Test 1\case and data\FFF.1-2-02541.dat.h5
FLUENT_REMOTE_GEOM_FILE=C:\Users\syok443\Documents\Fluent Standalone Test 1\geom\pureTwoPhase_OneMextensionInlet.agdb
FLUENT_REMOTE_MESH_FILE=C:\Users\syok443\Documents\Fluent Standalone Test 1\mesh\pureTwoPhase_OneMextensionInlet.mesh
```
