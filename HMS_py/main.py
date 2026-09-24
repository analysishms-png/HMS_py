"""HMS_py main entry point (P0 flow).

Run: python -m HMS_py.main
EXE: pyinstaller build/HMS_py.spec  ->  build/dist/HMS_py.exe

Flow (VB6 jaisa): Login ('User Information') ->
Company select ('Company Details', Site table se dynamic) ->
Main window ('{Company} { Year }', sidebar ini key 9,
menubar User_Module se, ported masters registry se).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HMS_py.ui import shell


def configure_qt_headless() -> None:
    """Use Qt offscreen mode when no display is available.

    This keeps the application usable in CI/headless environments while
    preserving normal GUI mode on a desktop Windows session.
    """
    if os.environ.get("QT_QPA_PLATFORM"):
        return
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return
    if os.environ.get("HMS_FORCE_HEADLESS") == "1":
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        return
    if os.name == "nt" and not os.environ.get("WSL_DISTRO_NAME"):
        if os.environ.get("HMS_GUI") == "1":
            return
        os.environ["QT_QPA_PLATFORM"] = "offscreen"


def main() -> int:
    configure_qt_headless()
    # Analysis.ini keys 2/3: reports/temp folders must exist (VB6 ke jaise
    # report export + Temp.Mdb wahan rehte hain). Best-effort, non-fatal.
    try:
        from HMS_py.core import db as _db
        _db.ensure_paths()
    except Exception:
        pass
    return shell.run_flow()


if __name__ == "__main__":
    raise SystemExit(main())
