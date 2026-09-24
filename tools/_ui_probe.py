"""Offscreen UI probe: ek master-form opener ko offscreen kholkar modal
.exec() ko 200ms timer se close karwata hai. Exit 0 = screen opened+returned.

Usage: python HMS_py/tools/_ui_probe.py <pm|gs> <opener_name>
"""
import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

mod_name, fn_name = sys.argv[1], sys.argv[2]
app = QApplication([])


def clos():
    for w in QApplication.topLevelWidgets():
        w.close()


t = QTimer()
t.setInterval(200)
t.timeout.connect(clos)
t.start()

from HMS_py.ui import p2_masters as pm, general_setup_ui as gs  # noqa: E402

f = getattr(pm if mod_name == "pm" else gs, fn_name)
print("OPENING", fn_name, flush=True)
f(None)
print("RETURNED", fn_name, flush=True)
