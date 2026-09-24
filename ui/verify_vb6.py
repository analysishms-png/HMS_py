# -*- coding: utf-8 -*-
"""Final verification: VB6 sidebar works correctly."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from HMS_py.ui.shell import MainWindow
from HMS_py.ui.sidebar_buttons import build_all_buttons, VB6_COLORS, VB6_BUTTON_STYLE, VB6_SECTION_STYLE, get_vb6_sidebar_style, build_vb6_buttons

# Verify VB6 style constants
print("=== VB6 Style ===")
print(f"VB6_COLORS: {VB6_COLORS}")
print(f"VB6_BUTTON_STYLE length: {len(VB6_BUTTON_STYLE)}")
print(f"VB6_SECTION_STYLE length: {len(VB6_SECTION_STYLE)}")
print(f"get_vb6_sidebar_style: {get_vb6_sidebar_style()}")

# Verify button data
btns = build_all_buttons("SA")
print(f"\n=== Button Data ===")
print(f"ACTIONS: {len(btns['ACTIONS'])}")
for b in btns["ACTIONS"]:
    print(f"  {b['label']:20} -> {b['mod_target']}")
print(f"MODULES: {len(btns['MODULES'])}")
for b in btns["MODULES"]:
    print(f"  {b['label']:20} -> {b['mod_target']}")

# Verify MainWindow attributes
print(f"\n=== MainWindow ===")
print(f"_DASHBOARD_MODULES: {MainWindow._DASHBOARD_MODULES}")
print(f"_AUTO_OPEN: {MainWindow._AUTO_OPEN}")
print(f"_DIRECT_OPENERS keys: {list(MainWindow._DIRECT_OPENERS.keys())}")

# Verify VB6 button style properties
style = VB6_BUTTON_STYLE
assert "#d0d0d0" in style, "VB6 button bg color missing"
assert "#000000" in style, "VB6 button text color missing"
assert "#808080" in style, "VB6 button border color missing"
assert "border-radius: 0px" in style, "VB6 button should have no rounded corners"
assert "#9dc3e6" in style, "VB6 selected button color missing"

sec_style = VB6_SECTION_STYLE
assert "#000080" in sec_style, "VB6 section header bg color missing"
assert "#ffffff" in sec_style, "VB6 section header text color missing"

print("\n=== VB6 Style Verification ===")
print("All VB6 colors correct: YES")
print("No rounded corners (border-radius: 0px): YES")
print("Blue section headers (#000080): YES")
print("Gray buttons (#d0d0d0): YES")
print("Selected blue (#9dc3e6): YES")
print("\nALL VERIFIED OK")
