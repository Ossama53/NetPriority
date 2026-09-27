APP_NAME = "NetPriority"

FIREWALL_RULE_PREFIX = "NetPriority_Block_"

STATE_FILE_NAME = "netpriority_state.json"
PROTECTED_PROCESSES = {
    "system",
    "system idle process",
    "svchost.exe",
    "wininit.exe",
    "winlogon.exe",
    "services.exe",
    "lsass.exe",
    "csrss.exe",
    "smss.exe",
    "explorer.exe",
    "dwm.exe",
    "fontdrvhost.exe",
    "registry",
    "memory compression",
    "python.exe",
    "pythonw.exe",
    "netpriority.exe",
}

MAX_BLOCK_AGE_SECONDS = 60 * 60 * 6 
