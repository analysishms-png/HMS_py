"""menuHelp core: Flag/Param_Str module-wise rights (VB6 FaVoucher port)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from HMS_py.core import menu_help as mh


def test_rights_parse_aedp():
    # pure parse (no DB): can() logic on a synthetic row via monkeypatch
    mh.clear_cache()
    mh._CACHE["SYN"] = [{
        "caption": "Room Master", "param": "AEDP", "flag": "E",
        "module": "GENMas", "opt1": "", "opt2": "", "opt3": "", "opt4": "",
    }, {
        "caption": "Sale Report", "param": "***P", "flag": "R",
        "module": "POSRep", "opt1": "", "opt2": "", "opt3": "", "opt4": "",
    }, {
        "caption": "Hidden Leaf", "param": "", "flag": "V",
        "module": "X", "opt1": "", "opt2": "", "opt3": "", "opt4": "",
    }]
    # force load path to use cache for synthetic user
    orig = mh._load_user
    try:
        def fake_load(username):
            return mh._CACHE.get("SYN", [])
        mh._load_user = fake_load  # type: ignore
        assert mh.flag_for("Room Master") == "E"
        assert mh.flag_for("Sale Report") == "R"
        assert mh.flag_for("Hidden Leaf") == "V"
        assert mh.flag_for("Missing") is None
        assert mh.can("SA", "Room Master", "A")
        assert mh.can("SA", "Room Master", "P")
        assert mh.can("SA", "Sale Report", "P")
        assert not mh.can("SA", "Sale Report", "A")   # ***P report: no Add
        assert not mh.can_open("SA", "Hidden Leaf")   # Flag V
        assert mh.can_open("SA", "Room Master")
        assert mh.can_open("SA", "Sale Report")
        assert mh.can_open("SA", "Unknown Leaf")      # missing => open
        assert mh.rights("SA", "Room Master") == "AEDP"
        assert mh.rights("SA", "Missing") == "AEDP"
        assert "GENMas" in mh.modules()
        tree = mh.module_tree()
        assert tree["GENMas"][0]["caption"] == "Room Master"
    finally:
        mh._load_user = orig  # type: ignore
        mh.clear_cache()


def test_menu_help_module_api_exists():
    for name in ("entries", "flag_for", "rights", "can", "can_open",
                 "module_tree", "modules", "by_caption", "clear_cache"):
        assert hasattr(mh, name), name
        assert callable(getattr(mh, name))
