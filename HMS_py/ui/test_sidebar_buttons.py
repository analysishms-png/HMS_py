# -*- coding: utf-8 -*-
"""Quick verification: sidebar buttons work correctly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from HMS_py.ui.sidebar_buttons import build_all_buttons, get_sidebar_sources
import HMS_py.ui.sidebar_buttons as _sb
from HMS_py.ui.shell import MainWindow


def test_sidebar_buttons():
    # Test 1: build_all_buttons
    btns = build_all_buttons("SA")
    assert "ACTIONS" in btns, "Missing ACTIONS section"
    assert "MODULES" in btns, "Missing MODULES section"
    assert len(btns["ACTIONS"]) == 6, f"Expected 6 actions, got {len(btns['ACTIONS'])}"
    assert len(btns["MODULES"]) == 14, f"Expected 14 modules, got {len(btns['MODULES'])}"

    # Test 2: Verify button structure
    for b in btns["ACTIONS"]:
        assert "icon" in b, f"Missing icon in {b}"
        assert "label" in b, f"Missing label in {b}"
        assert "mod_target" in b, f"Missing mod_target in {b}"
        assert "shortcut" in b, f"Missing shortcut in {b}"

    for b in btns["MODULES"]:
        assert "icon" in b, f"Missing icon in {b}"
        assert "label" in b, f"Missing label in {b}"
        assert "mod_target" in b, f"Missing mod_target in {b}"

    # Test 3: Verify module order matches Analysis.ini key 9
    sources = get_sidebar_sources("SA")
    source_names = [s["name"] for s in sources]
    module_targets = [b["mod_target"] for b in btns["MODULES"]]
    for sname, mtarget in zip(source_names, module_targets):
        assert sname == mtarget, f"Order mismatch: {sname} != {mtarget}"

    # Test 4: Verify Dashboard is NOT in MODULES (it's in ACTIONS)
    assert "Dashboard" not in module_targets, "Dashboard should not be in MODULES"
    assert any(b["mod_target"] == "Dashboard" for b in btns["ACTIONS"]), "Dashboard must be in ACTIONS"

    # Test 5: Verify __action_* targets
    action_targets = [b["mod_target"] for b in btns["ACTIONS"]]
    assert "__action_room_status" in action_targets, "Missing __action_room_status"
    assert "__action_guest_profile" in action_targets, "Missing __action_guest_profile"
    assert "__action_folio" in action_targets, "Missing __action_folio"
    assert "__action_checkin" in action_targets, "Missing __action_checkin"
    assert "__action_checkout" in action_targets, "Missing __action_checkout"

    # Test 6: Verify _AUTO_OPEN and _DIRECT_ACTIONS from _sb
    assert "reservation" in _sb.AUTO_OPEN, "_sb.AUTO_OPEN missing reservation"
    assert "main setup" in _sb.AUTO_OPEN, "_sb.AUTO_OPEN missing main setup"
    assert "__action_checkin" in _sb.DIRECT_ACTIONS, "_sb.DIRECT_ACTIONS missing checkin"
    assert _sb.DIRECT_ACTIONS["__action_checkin"] == "Check In", "DIRECT_ACTIONS mapping wrong"

    # Test 7: shell.py class attributes
    assert hasattr(MainWindow, "_DASHBOARD_MODULES"), "MainWindow missing _DASHBOARD_MODULES"
    assert hasattr(MainWindow, "_AUTO_OPEN"), "MainWindow missing _AUTO_OPEN"
    assert hasattr(MainWindow, "_DIRECT_OPENERS"), "MainWindow missing _DIRECT_OPENERS"
    assert MainWindow._AUTO_OPEN == dict(_sb.AUTO_OPEN), "_AUTO_OPEN not from _sb"

    # Test 8: Verify _sb._build_action_buttons has action field
    action_btns = _sb._build_action_buttons()
    for ab in action_btns:
        assert "action" in ab, f"Action button missing 'action' field: {ab}"

    return True

if __name__ == "__main__":
    test_sidebar_buttons()
    print("ALL TESTS PASSED")
