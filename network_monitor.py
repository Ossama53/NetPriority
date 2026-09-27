import psutil
from config import PROTECTED_PROCESSES


class AppInfo:
    def __init__(self, name, exe_path):
        self.name = name
        self.exe_path = exe_path
        self.pids = set()
        self.connection_count = 0
        self.is_protected = name.lower() in PROTECTED_PROCESSES

    def add_pid(self, pid, conn_count):
        self.pids.add(pid)
        self.connection_count += conn_count

    def to_dict(self):
        return {
            "name": self.name,
            "exe_path": self.exe_path,
            "pids": sorted(self.pids),
            "connection_count": self.connection_count,
            "is_protected": self.is_protected,
        }


def get_active_apps():
    apps = {}

    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return {}
    pid_conn_count = {}
    for conn in connections:
        if conn.pid is None:
            continue
        pid_conn_count[conn.pid] = pid_conn_count.get(conn.pid, 0) + 1

    for pid, count in pid_conn_count.items():
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                exe_path = proc.exe()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                exe_path = None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if name not in apps:
            apps[name] = AppInfo(name, exe_path)
        elif apps[name].exe_path is None and exe_path:
            apps[name].exe_path = exe_path

        apps[name].add_pid(pid, count)

    return apps


def get_playable_apps(apps):
    return {
        name: info
        for name, info in apps.items()
        if not info.is_protected and info.exe_path
    }
