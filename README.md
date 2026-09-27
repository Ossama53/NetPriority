# NetPriority

A Windows tool that lets you designate a specific application, game, or download as the "priority,"
temporarily blocking other applications from accessing the internet. This prevents large downloads
or background updates from slowing down the task that actually matters to you.

>  **Windows only.** It relies on `netsh advfirewall` and must be
> run with **Administrator** privileges; otherwise, it cannot detect all applications
> or control the firewall.

## How it works

- Displays all applications currently using the internet (via `psutil`)
- You select the "priority" application from the list
- Click "Activate Priority Mode" → Temporarily blocks other applications using
Windows Firewall rules, giving your selected application exclusive access to the internet
- Click "Reset All" or close the program → Everything automatically returns to normal

## Installation and Execution

```powershell
pip install -r requirements.txt
python main.py
```

**Must be run as Administrator**: Right-click your terminal (PowerShell
or CMD), select "Run as Administrator," and then execute the command above.

## Packaging as an .exe (Optional)

```powershell
pyinstaller --onefile --windowed --name NetPriority main.py
```

The resulting file will be located at `dist/NetPriority.exe`. Since the program requires
Administrator privileges, the user must manually select "Run as Administrator"
(or you can add a manifest later to request this automatically).

## File Structure

| File | Function |
|---|---|
| `main.py` | Entry point + safe shutdown handlers (atexit/signal) |
| `network_monitor.py` | Detects active network applications via psutil |
| `firewall_controller.py` | Adds/removes blocking rules via netsh |
| `state_manager.py` | Saves current blocking state (crash recovery) |
| `ui.py` | Graphical User Interface (CustomTkinter) |
| `config.py` | Constants and list of protected system processes |

## Important Security Notes

- All blocking rules are prefixed with `NetPriority_Block_` to make them easy to identify
and remove, ensuring they do not interfere with your other firewall rules.
- Critical system processes (`svchost.exe`, `explorer.exe`, etc.) are automatically
excluded from the block list (see `config.py` → `PROTECTED_PROCESSES`).
- If the program crashes or closes unexpectedly, it detects any lingering
blocks upon the next launch and automatically cleans them up.

## Proposed Future Enhancements

- Automatic timer (e.g., priority mode turns off after 30 minutes)
- Preset profiles ("Gaming," "Download") to block groups of applications at once
- Digital signature for the executable to reduce antivirus warnings
- Windows notifications when priority mode starts or ends
