import json
import os
from config import STATE_FILE_NAME, APP_NAME


def _state_dir():
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(appdata, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _state_path():
    return os.path.join(_state_dir(), STATE_FILE_NAME)


def load_state():
    path = _state_path()
    if not os.path.exists(path):
        return {"blocked_apps": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "blocked_apps" not in data:
                data["blocked_apps"] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {"blocked_apps": []}


def save_state(state):
    try:
        with open(_state_path(), "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def add_blocked_app(app_name):
    state = load_state()
    if app_name not in state["blocked_apps"]:
        state["blocked_apps"].append(app_name)
    save_state(state)


def remove_blocked_app(app_name):
    state = load_state()
    if app_name in state["blocked_apps"]:
        state["blocked_apps"].remove(app_name)
    save_state(state)


def get_blocked_apps():
    return load_state().get("blocked_apps", [])


def clear_state():
    save_state({"blocked_apps": []})


def has_leftover_blocks():
    return len(get_blocked_apps()) > 0
