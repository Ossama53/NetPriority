import subprocess
import sys
from config import FIREWALL_RULE_PREFIX


def is_windows():
    return sys.platform.startswith("win")


def is_admin():
    if not is_windows():
        return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _run_netsh(args):
    try:
        result = subprocess.run(
            ["netsh"] + args,
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if is_windows() else 0,
        )
        return result.returncode == 0, (result.stdout + result.stderr)
    except Exception as e:
        return False, str(e)


def _rule_name(app_name, direction):
    safe_name = app_name.replace(" ", "_")
    return f"{FIREWALL_RULE_PREFIX}{safe_name}_{direction}"


def block_app(app_name, exe_path):
    if not exe_path:
        return False

    ok_out, _ = _run_netsh([
        "advfirewall", "firewall", "add", "rule",
        f'name={_rule_name(app_name, "out")}',
        "dir=out", f'program={exe_path}', "action=block", "enable=yes",
    ])
    ok_in, _ = _run_netsh([
        "advfirewall", "firewall", "add", "rule",
        f'name={_rule_name(app_name, "in")}',
        "dir=in", f'program={exe_path}', "action=block", "enable=yes",
    ])
    return ok_out and ok_in


def unblock_app(app_name):
    _run_netsh(["advfirewall", "firewall", "delete", "rule",
                f'name={_rule_name(app_name, "out")}'])
    _run_netsh(["advfirewall", "firewall", "delete", "rule",
                f'name={_rule_name(app_name, "in")}'])
    return True


def unblock_all(app_names):
    for name in app_names:
        unblock_app(name)


def unblock_all_by_prefix():
    ok, output = _run_netsh(["advfirewall", "firewall", "show", "rule",
                              "name=all"])
    if not ok:
        return []

    removed = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Rule Name:"):
            rule_name = line.split(":", 1)[1].strip()
            if rule_name.startswith(FIREWALL_RULE_PREFIX):
                _run_netsh(["advfirewall", "firewall", "delete", "rule",
                            f"name={rule_name}"])
                removed.append(rule_name)
    return removed
