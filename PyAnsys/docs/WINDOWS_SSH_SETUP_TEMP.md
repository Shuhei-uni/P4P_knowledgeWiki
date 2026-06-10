# Windows SSH Setup For Remote PyAnsys Work

Assumptions:
- local machine is macOS
- remote machine is Windows
- the repository is already cloned on the Windows PC
- goal is to enable SSH access from the Mac to the Windows PC so PyAnsys can be run remotely

## Goal
Enable `sshd` on the Windows PC, confirm the firewall rule exists, then connect from the Mac with `ssh`.

## Step 1: Enable OpenSSH Server On Windows

Open `PowerShell` as Administrator on the Windows PC and run:

```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP"
```

If the firewall rule does not exist, create it:

```powershell
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

## Step 2: Confirm SSH Works On The Windows PC

Still in PowerShell on the Windows PC:

```powershell
Get-Service sshd
ssh localhost
hostname
whoami
ipconfig
```

Record:
- Windows username
- hostname
- IPv4 address

## Step 3: Connect From The Mac

On the Mac, open Terminal and run:

```bash
ssh WINDOWS_USERNAME@WINDOWS_IP
```

Example:

```bash
ssh shuhei@192.168.1.45
```

On first connect, accept the host key:

```text
yes
```

## Step 4: Verify Repo Access After Login

After SSH login, verify where you are and move into the repo.

If you land in PowerShell:

```powershell
pwd
cd "C:\Users\YOUR_WINDOWS_USER\path\to\P4P_knowledgeWiki\PyAnsys"
git status
```

If you land in a Unix-like shell:

```bash
pwd
cd /c/Users/YOUR_WINDOWS_USER/path/to/P4P_knowledgeWiki/PyAnsys
git status
```

## Step 5: Troubleshooting

From the Mac, if the connection fails:

```bash
ssh -v WINDOWS_USERNAME@WINDOWS_IP
```

Common causes:
- `sshd` service is not started
- firewall rule is missing
- wrong Windows username
- wrong IP address
- both machines are not on the same network
- port `22` is blocked by network policy

## Step 6: If The Machines Are Not On The Same LAN

Prefer `Tailscale` on both machines instead of exposing port `22` through router port forwarding.

Then connect using the Tailscale IP or machine name:

```bash
ssh WINDOWS_USERNAME@TAILSCALE_IP
```

## Step 7: Next Commands For PyAnsys

Once SSH works, the next likely commands on the Windows PC are:

```powershell
cd "C:\Users\YOUR_WINDOWS_USER\path\to\P4P_knowledgeWiki\PyAnsys"
git status
```

If Python environment setup is still needed:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-minimal.txt
```

Then PyAnsys scripts can be run directly on that Windows PC over SSH.

## Official References

- Microsoft OpenSSH install/start/firewall:
  https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
- Windows OpenSSH configuration:
  https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration
- Apple SSH usage from Terminal:
  https://support.apple.com/guide/mac-help/mchlp1066/mac
