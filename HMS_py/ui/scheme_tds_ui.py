"""Scheme/HappyHours/TDS UI (VB6 POSMAST idx-9/10/11 + FaTDSCat port).

Run: python -m HMS_py.ui.scheme_tds_ui
Menu wiring: 'Scheme Master' (POS), 'Happy Hours' (POS, read-only viewers),
'T.D.S. Category' (Finance). BaseMasterForm CRUD pattern (list_all/get/
exists/insert/update/delete) jaisa baaki masters me hai.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)

from HMS_py.core import scheme as sch
from HMS_py.core import tdscat as tdscore  # tds.py duplicate tha — tdscat hi primary
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig


# ------------------------------------------------------------- TDS Category
def tdscat_config() -> MasterConfig:
    return MasterConfig(
        title="T.D.S. Category - HMS_py",
        columns=[("Code", "code"), ("Name", "name"),
                 ("TDS Limit", "tdslimit"), ("TDS %", "tdspercentage")],
        fields=[
            Field("code", "Code", max_len=tdscore.LIMITS["code"],
                  required=True),
            Field("name", "Category Name",
                  max_len=tdscore.LIMITS["name"], required=True),
            Field("tdslimit", "TDS Limit", default="0"),
            Field("tdspercentage", "TDS Percentage", default="0"),
        ],
        api=tdscore,
        delete_guard=make_delete_guard("PYT"),
    )


def make_delete_guard(tag: str):
    """PYT-prefixed live rows delete nahi honge (PYT-guard pattern)."""
    def guard(code: str) -> str | None:
        if str(code).upper().startswith(tag):
            return (f"{tag}-row production data hai — delete nahi hoga")
        return None
    return guard


def open_tdscat(parent=None):
    BaseMasterForm(tdscat_config(), parent).exec()


# --------------------------------------------------------------- Scheme
def scheme_config() -> MasterConfig:
    return MasterConfig(
        title="Scheme Master (POS) - HMS_py",
        columns=[("Code", "code"), ("Name", "name"), ("From", "startdate"),
                 ("To", "enddate"), ("Time", "fromtime"), ("Active", "active")],
        fields=[
            Field("code", "Scheme Code", max_len=sch.LIMITS["code"],
                  required=True),
            Field("name", "Scheme Name", max_len=sch.LIMITS["name"],
                  required=True),
            Field("startdate", "Start Date (YYYY-MM-DD)"),
            Field("enddate", "End Date (YYYY-MM-DD)"),
            Field("fromtime", "From Time (HH:MM)", max_len=sch.LIMITS["time"]),
            Field("totime", "To Time (HH:MM)", max_len=sch.LIMITS["time"]),
            Field("days", "Days (0-6)", max_len=sch.LIMITS["days"]),
            Field("active", "Active Y/N", max_len=1, default="Y"),
        ],
        api=_SchemeAPI(),
        delete_guard=make_delete_guard("PYT"),
    )


class _SchemeAPI:
    """BaseMasterForm contract par SchemeMast (get/exists single-code)."""

    def list_all(self, cn=None):
        return sch.scheme_list(cn=cn)

    def get(self, pk, cn=None):
        return sch.scheme_get(pk, cn=cn)

    def exists(self, pk, cn=None):
        return sch.scheme_get(pk, cn=cn) is not None

    def insert(self, rec, cn=None, commit=True):
        return sch.scheme_insert(rec, cn=cn, commit=commit)

    def update(self, pk, rec, cn=None, commit=True):
        return sch.scheme_update(pk, rec, cn=cn, commit=commit)

    def delete(self, pk, cn=None, commit=True):
        return sch.scheme_delete(pk, cn=cn, commit=commit)


def open_scheme(parent=None):
    BaseMasterForm(scheme_config(), parent).exec()


# ------------------------------------------------- Happy Hours (viewer)
class HappyHoursViewer(QDialog):
    """Read-only: SchemeCode se HappyHoursHead + HappyHours rows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Happy Hours - HMS_py")
        self.resize(780, 460)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            "VB6 pHappyHours/NewHappyHours port (read-only viewer).\n"
            "HappyHoursHead = scheme-level setup; HappyHours = item discounts."))
        self.tbl = QTableWidget(0, 0)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)
        btns = QHBoxLayout()
        b = QPushButton("Reload")
        b.setToolTip("Reload happy hours data")
        b.clicked.connect(self._load)
        btns.addWidget(b)
        btns.addStretch(1)
        root.addLayout(btns)
        self._load()

    def _load(self):
        heads = sch.happyhead_list()
        self.tbl.clear()
        cols = ["SchemeCode", "ItemCat", "ItemGroup", "RestCode", "AppDate",
                "From", "To", "DiscType"]
        self.tbl.setColumnCount(len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setRowCount(0)
        for h in heads:
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            vals = [h["schemecode"], h["itemcat"], h["itemgroup"],
                    h["restcode"], h["appdate"], h["fromtime"], h["totime"],
                    h["discounttype"]]
            for c, v in enumerate(vals):
                it = QTableWidgetItem("" if v is None else str(v))
                it.setFlags(it.flags() & ~Qt_ItemIsEditable())
                self.tbl.setItem(r, c, it)
        self.tbl.resizeColumnsToContents()


def Qt_ItemIsEditable():
    from PyQt6.QtCore import Qt
    return Qt.ItemFlag.ItemIsEditable


def open_happyhours(parent=None):
    HappyHoursViewer(parent).exec()


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    open_scheme()
