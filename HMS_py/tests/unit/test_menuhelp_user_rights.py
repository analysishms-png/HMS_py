"""Per-user Param_Str AEDP filtering tests (synthetic, no DB).

VB6 evidence: MDIForm1 user ke APNE menuHelp rows se menu banata hai —
absent caption = leaf hidden. Param_Str 'A**P'/'AE*P'/'***P' = rights.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from HMS_py.core import menu_help as mh


def _row(cap, flag, param, o1=11, o2=11, o3=0, o4=0, module="FA", code=0):
    return {"caption": cap, "param": param, "flag": flag, "module": module,
            "opt1": str(o1), "opt2": str(o2), "opt3": str(o3),
            "opt4": str(o4), "code": code}


ADMIN = [
    _row("Finance", "N", "", 11, 0, 0, 0, code=1),
    _row("Transaction", "N", "", 11, 11, 0, 0, code=2),
    _row("Voucher Entry", "E", "A**P", 11, 11, 11, 0, code=3),
    _row("Trial Balance", "R", "***P", 11, 12, 11, 0, code=4),
]


def _install(user, rows):
    mh.clear_cache()
    mh._CACHE[user] = rows
    orig = mh._load_user
    mh._load_user = lambda username: list(mh._CACHE.get((username or "").upper(), [])) \
        if username == user else orig(username)
    return orig


def test_restricted_user_rights():
    orig = _install("ADMIN", ADMIN)
    # full_access: DB probe — monkeypatch full_access ko bhi
    orig_fa = mh.full_access
    mh.full_access = lambda username="SA": username.upper() == "SA"
    try:
        # Param_Str A**P filtering
        assert mh.rights("ADMIN", "Voucher Entry") == "A**P"
        assert mh.can("ADMIN", "Voucher Entry", "A")
        assert not mh.can("ADMIN", "Voucher Entry", "E")
        assert not mh.can("ADMIN", "Voucher Entry", "D")
        assert mh.can("ADMIN", "Voucher Entry", "P")
        # report ***P: print-only
        assert mh.can("ADMIN", "Trial Balance", "P")
        assert not mh.can("ADMIN", "Trial Balance", "A")
        # absent caption => hidden for restricted user
        assert mh.has_row("ADMIN", "Ledger") is False
        assert mh.flag_for("Ledger", "ADMIN") is None
        # SA: has_row None (full access), rights default AEDP
        assert mh.has_row("SA", "Kuch Bhi") is None
        assert mh.rights("SA", "Kuch Bhi") == "AEDP"
    finally:
        mh._load_user = orig  # type: ignore
        mh.full_access = orig_fa
        mh.clear_cache()


def test_null_param_falls_back_aedp():
    rows = [_row("Null Param Leaf", "E", None)]
    orig = _install("NULLPAR", rows)
    orig_fa = mh.full_access
    mh.full_access = lambda username="SA": username.upper() == "SA"
    try:
        assert mh.rights("NULLPAR", "Null Param Leaf") == "AEDP"
        assert mh.can("NULLPAR", "Null Param Leaf", "D")
    finally:
        mh._load_user = orig  # type: ignore
        mh.full_access = orig_fa
        mh.clear_cache()


def test_menubar_restricted_only_own_rows():
    # restricted user ke rows me sirf Finance hai; EPABX mangega -> []
    orig = _install("ADMIN", ADMIN)
    orig_fa = mh.full_access
    mh.full_access = lambda username="SA": username.upper() == "SA"
    orig_um = mh._um_for_test if hasattr(mh, "_um_for_test") else None
    try:
        groups = mh.menubar_for_menuhelp("Finance", "ADMIN")
        assert groups and groups[0]["name"] == "Transaction"
        # restricted: User_Module fallback bhi nahi (leak guard)
        assert mh.menubar_for("EPABX", "ADMIN") == []
        # full-access user ko fallback milta hai (no-crash; list)
        assert isinstance(mh.menubar_for("EPABX", "SA"), list)
    finally:
        mh._load_user = orig  # type: ignore
        mh.full_access = orig_fa
        if orig_um:
            mh._um_for_test = orig_um
        mh.clear_cache()
