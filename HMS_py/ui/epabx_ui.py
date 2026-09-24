"""EPABX Masters UI (VB6: Main Setup -> EPABX).
Tables: TelCallType, TelCallCode, TelExt"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)
from HMS_py.core.epabx_masters import CallTypeAPI, CallCodeAPI, TelExtAPI
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig, make_delete_guard


def calltype_config() -> MasterConfig:
    return MasterConfig(
        title="Call Type Master (EPABX) - HMS_py",
        columns=[("Code","code"),("CallType","calltype"),("Short","shortname")],
        fields=[
            Field("code","Type Code", max_len=6, required=True),
            Field("calltype","Call Type Name", max_len=30, required=True),
            Field("shortname","Short Name", max_len=6),
            Field("accode","A/C Code", max_len=10),
            Field("taxstru","Tax Structure", max_len=6),
        ],
        api=CallTypeAPI,
        delete_guard=make_delete_guard("PYT"),
    )


def callcode_config() -> MasterConfig:
    return MasterConfig(
        title="Call Code Master (EPABX) - HMS_py",
        columns=[("STD","stdcode"),("Type","calltypecode"),
                 ("Description","description"),("Pulse","pulseinsec")],
        fields=[
            Field("stdcode","STD Code", max_len=6, required=True),
            Field("calltypecode","Call Type Code", max_len=6, required=True),
            Field("description","Description", max_len=50),
            Field("pulseinsec","Pulse In Sec", default="0"),
        ],
        api=CallCodeAPI,
        delete_guard=make_delete_guard("PYT"),
    )


def ext_config() -> MasterConfig:
    return MasterConfig(
        title="Extension Master (EPABX) - HMS_py",
        columns=[("Code","code"),("Description","description"),
                 ("Extension","extension"),("Type","type"),("Room","roomno")],
        fields=[
            Field("code","Extension Code", max_len=6, required=True),
            Field("description","Description", max_len=50),
            Field("extension","Extension No", max_len=10),
            Field("type","Type", max_len=10),
            Field("roomno","Room No", max_len=6),
            Field("shopno","Shop No", max_len=6),
            Field("depcode","Department Code", max_len=6),
            Field("pulserate","Pulse Rate", default="0"),
        ],
        api=TelExtAPI,
        delete_guard=make_delete_guard("PYT"),
    )


def _open(cfg_fn, parent=None):
    BaseMasterForm(cfg_fn(), parent).exec()

def open_calltype(parent=None):  _open(calltype_config, parent)
def open_callcode(parent=None):  _open(callcode_config, parent)
def open_extension(parent=None): _open(ext_config, parent)


class EPABXLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMS_py - EPABX Masters")
        self.resize(340, 200)
        c = QWidget(); lay = QVBoxLayout(c)
        for lbl, fn in [("Call Type Master", open_calltype),
                        ("Call Code Master", open_callcode),
                        ("Extension Master", open_extension)]:
            b = QPushButton(lbl); b.clicked.connect(fn); lay.addWidget(b)
        self.setCentralWidget(c)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = EPABXLauncher(); w.show()
    raise SystemExit(app.exec())
