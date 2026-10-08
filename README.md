<p align="center">
  <img src="assets/logo.svg" width="160" alt="NetPriority logo">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-0077b6" alt="version 1.0.0">
  <img src="https://img.shields.io/badge/platform-Windows-0078d4" alt="platform Windows">
  <img src="https://img.shields.io/badge/language-Python-3776ab" alt="language Python">
  <img src="https://img.shields.io/badge/powered%20by-psutil-2de2c0" alt="powered by psutil">
  <img src="https://img.shields.io/badge/license-MIT-4c9a2a" alt="license MIT">
</p>

<h1 align="center">NetPriority</h1>

<p align="center"><b>Give one app the internet to itself</b></p>

A small Windows tool that gives one app the internet to itself. Pick the app that matters (a game, a download, a call), and NetPriority blocks the other apps that are currently using the network, so background updates stop eating your bandwidth.

<!-- Add one or two sentences here about why you built it. -->

**Windows only.** It uses `netsh advfirewall`, so it has to run as Administrator.

## How to use it

1. Run the app as Administrator.
2. Choose your priority app from the dropdown (it lists apps that are using the network right now).
3. Click **Enable Priority Mode**. Every other app on the list gets a firewall block rule.
4. Click **Reset All** (or just close the window) to put everything back to normal.

## Run it

```
pip install -r requirements.txt
python main.py
```

Open PowerShell or CMD with "Run as administrator" first.

To build an `.exe`:

```
pyinstaller --onefile --windowed --name NetPriority main.py
```

The result is in `dist/NetPriority.exe`. You still need to right-click it and choose "Run as administrator".

## Files

- `main.py` - starts the app and makes sure blocks are removed on exit
- `ui.py` - the window (CustomTkinter)
- `network_monitor.py` - finds apps using the network (psutil)
- `firewall_controller.py` - adds and removes the `netsh` rules
- `state_manager.py` - remembers what is blocked, so a crash can be cleaned up next launch
- `config.py` - constants and the list of protected system processes

## Safety

- Every rule is named `NetPriority_Block_<app>`, so they are easy to find and don't touch your other firewall rules.
- System processes like `svchost.exe` and `explorer.exe` are never blocked.
- If the app crashes, leftover blocks are removed the next time you start it.

## Limitations

- Only apps that are already using the network when you click Enable get blocked. Apps that start later are not.
- Cleanup by rule name reads `netsh` output in English, so it may not work on a non-English Windows.

## License

MIT
