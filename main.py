import atexit
import signal
import sys

import firewall_controller
import state_manager


def cleanup_on_exit():
    leftover = state_manager.get_blocked_apps()
    if leftover:
        firewall_controller.unblock_all(leftover)
        state_manager.clear_state()

    firewall_controller.unblock_all_by_prefix()


def _signal_handler(signum, frame):
    cleanup_on_exit()
    sys.exit(0)


def main():
    if not firewall_controller.is_windows():
        print("هذا البرنامج مخصص لنظام Windows فقط.")
        sys.exit(1)

    atexit.register(cleanup_on_exit)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
        signal.signal(signal.SIGINT, _signal_handler)
    except (ValueError, AttributeError):
        pass 
    
    from ui import NetPriorityApp

    app = NetPriorityApp()
    app.mainloop()


if __name__ == "__main__":
    main()
