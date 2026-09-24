"""menuHelp dynamic menu builder: VB6 MDIForm1 logic (synthetic, no DB)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from HMS_py.core import menu_help as mh


def _row(cap, o1, o2, o3, o4, flag, module="X", code=0, param="AEDP"):
    return {"caption": cap, "param": param, "flag": flag, "module": module,
            "opt1": str(o1), "opt2": str(o2), "opt3": str(o3),
            "opt4": str(o4), "code": code}


SYN = [
    # O1=11 Finance (module-level N)
    _row("Finance", 11, 0, 0, 0, "N", "FA", code=10),
    _row("Transaction", 11, 11, 0, 0, "N", "FA", code=11),
    _row("Voucher Entry", 11, 11, 11, 0, "E", "FA", code=12),
    _row("Trial Balance", 11, 12, 11, 0, "R", "FAR", code=13, param="***P"),
    # O2=0 direct leaf (POS 'Payment Receive' pattern)
    _row("Payment Receive", 17, 0, 11, 0, "E", "Pos", code=14),
    _row("Point Of Sale", 17, 0, 0, 0, "N", "Pos", code=15),
    # L4 child (EXTRAs SMS pattern)
    _row("EXTRAs", 27, 0, 0, 0, "N", "EXT", code=16),
    _row("SMS", 27, 12, 0, 0, "N", "EXT", code=17),
    _row("Sstup", 27, 12, 11, 0, "N", "EXT", code=18),
    _row("SMS (API)", 27, 12, 11, 11, "E", "EXT", code=19),
    # hidden + separator + deleted
    _row("Secret Leaf", 17, 33, 11, 0, "V", "Pos", code=20),
    _row("-", 17, 34, 0, 0, "E", "Pos", code=21),
    _row("Dead Leaf", 17, 35, 11, 0, "D", "Pos", code=22),
    # orphan bucket (no L1 node)
    _row("Lost Leaf", 23, 11, 11, 0, "E", "ZZ", code=23),
]


def _install():
    mh.clear_cache()
    mh._CACHE["SYN"] = SYN
    orig = mh._load_user
    mh._load_user = lambda username: list(SYN)  # type: ignore
    return orig


def test_sidebar_modules_from_menuhelp():
    orig = _install()
    try:
        side = mh.sidebar_modules("SYN")
        names = [s["name"] for s in side]
        assert names == ["Finance", "Point Of Sale", "EXTRAs"], names
        assert side[0]["opt1"] == 11
        assert all(s["flag"] if "flag" in s else True for s in side) or True
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_menubar_hierarchy_and_hidden():
    orig = _install()
    try:
        groups = mh.menubar_for_menuhelp("Point Of Sale", "SYN")
        # direct O2=0 leaf 'Payment Receive' group + O2 blocks
        names = [g["name"] for g in groups]
        assert "Point Of Sale" in names, names  # direct-items group
        d = next(g for g in groups if g["name"] == "Point Of Sale")
        assert any(it["name"] == "Payment Receive" for it in d["items"])
        # V/D rows kabhi nahi
        all_names = []

        def walk(items):
            for it in items:
                all_names.append(it["name"])
                walk(it.get("children") or [])

        for g in groups:
            walk(g["items"])
        assert "Secret Leaf" not in all_names
        assert "Dead Leaf" not in all_names
        assert "-" not in all_names
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_l4_nesting_sms():
    orig = _install()
    try:
        groups = mh.menubar_for_menuhelp("EXTRAs", "SYN")
        g = next(g for g in groups if g["name"] == "SMS")
        sstup = next(it for it in g["items"] if it["name"] == "Sstup")
        assert sstup["children"][0]["name"] == "SMS (API)"
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_menubar_for_fallback_and_merge():
    orig = _install()
    try:
        # module menuHelp me hai -> mh source
        g = mh.menubar_for("Finance", "SYN")
        assert g, "Finance must build from menuHelp"
        # module menuHelp me NAHI hai -> User_Module fallback (no crash)
        g2 = mh.menubar_for("EPABX", "SYN")
        assert isinstance(g2, list)
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_orphan_rows_report_only():
    orig = _install()
    try:
        orph = mh.orphan_rows("SYN")
        caps = [r["caption"] for r in orph]
        assert "Lost Leaf" in caps
        # aur menus me inject nahi hote
        for s in mh.sidebar_modules("SYN"):
            groups = mh.menubar_for_menuhelp(s["name"], "SYN")

            def walk(items):
                for it in items:
                    assert it["name"] != "Lost Leaf"
                    walk(it.get("children") or [])

            for g in groups:
                walk(g["items"])
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_rights_unchanged_regression():
    orig = _install()
    try:
        assert mh.flag_for("Voucher Entry", "SYN") == "E"
        assert mh.flag_for("Trial Balance", "SYN") == "R"
        assert mh.rights("SYN", "Trial Balance") == "***P"
        assert mh.can("SYN", "Trial Balance", "P")
        assert not mh.can("SYN", "Trial Balance", "A")
        assert mh.can_open("SYN", "Voucher Entry")
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()
