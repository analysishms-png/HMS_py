"""Error handling (VB6 ErrorHandlingModule.bas port).

LogError -> ErrorLog.txt (project root / HMS_py), severity levels,
StandardErrorHandler wrapper. No GUI deps; safe for core+ui.
"""
from __future__ import annotations

import datetime as _dt
import os
import traceback

_SEVERITY = {10: "INFO", 20: "WARNING", 30: "ERROR", 40: "CRITICAL"}


def _log_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "ErrorLog.txt")


def log_error(exc: BaseException | str, *,
              user: str = "", form: str = "", procedure: str = "",
              severity: int = 30, extra: str = "") -> None:
    """Append one ErrorLog.txt line (VB6 LogError/StandardErrorHandler)."""
    sev = _SEVERITY.get(severity, "ERROR")
    if isinstance(exc, BaseException):
        detail = "".join(traceback.format_exception(type(exc), exc,
                                                    exc.__traceback__))
        detail = detail.strip().replace("\n", " | ")
    else:
        detail = str(exc)
    ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (f"{ts} [{sev}] user={user or '-'} form={form or '-'} "
            f"proc={procedure or '-'} :: {detail}")
    if extra:
        line += f" :: {extra}"
    try:
        with open(_log_path(), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def log_trace(context: str, msg: str) -> None:
    """Append one TRACE line to ErrorLog.txt (VB6 modLog Enter/Exit/Trace).

    Lightweight, no GUI, no retention logic — callers pass e.g.
    log_trace("modLog", "Enter NightAuditoR_Click"). Best-effort write.
    """
    ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [TRACE] {context or '-'} :: {msg}"
    try:
        with open(_log_path(), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def standard_error_handler(exc: BaseException, *,
                           user: str = "", form: str = "",
                           procedure: str = "") -> str:
    """Log + return short user-facing message (VB6 StandardErrorHandler)."""
    log_error(exc, user=user, form=form, procedure=procedure,
              severity=40 if isinstance(exc, MemoryError) else 30)
    if isinstance(exc, ValueError):
        return str(exc)
    if isinstance(exc, (ConnectionError, OSError)):
        return "Database/network unavailable. Please retry."
    return "Unexpected error. Details logged to ErrorLog.txt."


def generate_error_report(date_from=None, date_to=None) -> list[str]:
    """Date-filtered ErrorLog.txt lines (VB6 GenerateErrorReport)."""
    path = _log_path()
    if not os.path.isfile(path):
        return []
    out: list[str] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                if not line:
                    continue
                if date_from or date_to:
                    try:
                        d = _dt.datetime.strptime(line[:10], "%Y-%m-%d").date()
                    except ValueError:
                        continue
                    if date_from and d < date_from:
                        continue
                    if date_to and d > date_to:
                        continue
                out.append(line)
    except OSError:
        return []
    return out
