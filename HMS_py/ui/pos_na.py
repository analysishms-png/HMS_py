"""POS + Night Audit UI (P5): KOT browser, sales reports, NA log/occupancy.

Run: python -m HMS_py.ui.pos_na
Menu wiring: Point Of Sale -> 'KOT Entry'/'POS Status' + POS Reports leaves;
Night Audit -> 'Log'/'Night Audit Log' + 'Daily Report'/'Occupancy Analysis'.
Read-only (PYT-guard: POS/NA entries VB6 EXE se aati hain - koi write nahi).
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout)

from HMS_py.core import nightaudit, pos
from HMS_py.ui import theme as _theme


def _dark_item(val) -> QTableWidgetItem:
    """Dark-mode-safe cell (P3-b proven bug)."""
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


class PosBrowser(QDialog):
    """KOT list + drill-down lines + outlet/item reports (tabs-free: 3 views)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS - KOT Browser (P5) - HMS_py")
        self.resize(1080, 600)
        root = QVBoxLayout(self)

        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(
            ["KOT No", "Date", "Outlet", "Lines", "Amount", "DocId"])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._lines())
        root.addWidget(self.tbl)

        self.lblState = QLabel(
            "State: KOT list | double-click = lines | "
            "Ctrl+O = outlet report, Ctrl+W = itemwise")
        root.addWidget(self.lblState)

        btns = QHBoxLayout()
        self.btnLines = QPushButton("Lines")
        self.btnLines.setToolTip("View KOT line items for the selected KOT")
        self.btnOutlet = QPushButton("Outlet Report")
        self.btnOutlet.setToolTip("View sales summary by outlet (Ctrl+O)")
        self.btnItem = QPushButton("Item-wise Report")
        self.btnItem.setToolTip("View item-wise sales report (Ctrl+W)")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close the POS KOT Browser")
        for b in (self.btnLines, self.btnOutlet, self.btnItem, self.btnClose):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btnLines.clicked.connect(self._lines)
        self.btnOutlet.clicked.connect(self._outlet)
        self.btnItem.clicked.connect(self._itemwise)
        self.btnClose.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Return"), self, activated=self._lines)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self._outlet)
        QShortcut(QKeySequence("Ctrl+W"), self, activated=self._itemwise)

        self._mode = "kot"
        self.reload()

    def reload(self):
        rows = pos.kot_list()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["KOT No", "Date", "Outlet", "Lines", "Amount", "DocId"])
        for r, k in enumerate(rows):
            for c, v in enumerate([k["vno"], k["vdate"], k["rest"],
                                   k["lines"], round(k["amount"], 2),
                                   k["docid"]]):
                self.tbl.setItem(r, c, _dark_item(v))
        if rows:
            self.tbl.selectRow(0)
        self._mode = "kot"
        self.setWindowTitle("POS - KOT Browser (P5) - HMS_py")

    def _selected_docid(self):
        r = self.tbl.currentRow()
        if r < 0 or self._mode != "kot":
            return None
        return self.tbl.item(r, 5).text()

    def _lines(self):
        docid = self._selected_docid()
        if not docid:
            return
        lines = pos.kot_lines(docid)
        self.tbl.setRowCount(len(lines))
        self.tbl.setHorizontalHeaderLabels(
            ["Sno", "Item Code", "Item Name", "Qty", "Unit", "Amount"])
        for r, l in enumerate(lines):
            for c, v in enumerate([l["sno"], l["item"], l["name"],
                                   l["qty"], l["unit"],
                                   round(l["amount"], 2)]):
                self.tbl.setItem(r, c, _dark_item(v))
        self._mode = "lines"
        self.setWindowTitle(f"POS - KOT Lines (P5) - HMS_py")

    def _outlet(self):
        rows = pos.sales_summary()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Outlet Code", "Outlet", "KOTs", "Amount", "", ""])
        for r, s in enumerate(rows):
            for c, v in enumerate([s["rest"], s["outlet"], s["kots"],
                                   round(s["amount"], 2), "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self._mode = "report"
        self.setWindowTitle("POS - Sales Register (P5) - HMS_py")

    def _itemwise(self):
        rows = pos.itemwise_sale()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Item Code", "Item Name", "Qty", "Amount", "", ""])
        for r, i in enumerate(rows):
            for c, v in enumerate([i["item"], i["name"], i["qty"],
                                   round(i["amount"], 2), "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self._mode = "report"
        self.setWindowTitle("POS - Item-wise Sale (P5) - HMS_py")


class NABrowser(QDialog):
    """Night Audit: log + occupancy + revenue (3 views)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Night Audit (P5) - HMS_py")
        self.resize(1000, 560)
        root = QVBoxLayout(self)

        self.tbl = QTableWidget(0, 6)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        self.lblState = QLabel(
            "State: NA Log | Ctrl+O = Occupancy, Ctrl+V = Revenue, "
            "Ctrl+M = Room Revenue")
        root.addWidget(self.lblState)

        btns = QHBoxLayout()
        self.btnLog = QPushButton("NA Log")
        self.btnLog.setToolTip("View the Night Audit log history")
        self.btnOcc = QPushButton("Occupancy")
        self.btnOcc.setToolTip("View occupancy analysis (Ctrl+O)")
        self.btnRev = QPushButton("Revenue")
        self.btnRev.setToolTip("View daily revenue summary (Ctrl+V)")
        self.btnRoom = QPushButton("Room Revenue")
        self.btnRoom.setToolTip("View room-wise revenue report (Ctrl+M)")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close the Night Audit browser")
        for b in (self.btnLog, self.btnOcc, self.btnRev, self.btnRoom,
                  self.btnClose):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btnLog.clicked.connect(self._log)
        self.btnOcc.clicked.connect(self._occ)
        self.btnRev.clicked.connect(self._rev)
        self.btnRoom.clicked.connect(self._room)
        self.btnClose.clicked.connect(self.reject)

        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._log)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self._occ)
        QShortcut(QKeySequence("Ctrl+V"), self, activated=self._rev)
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self._room)

        self._log()

    def _log(self):
        rows = nightaudit.na_log()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Id", "From", "To", "Start", "End", "User"])
        for r, n in enumerate(rows):
            for c, v in enumerate([n["id"], n["from"], n["to"],
                                   n["start"], n["end"], n["user"]]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Night Audit - Log (68 runs)")

    def _occ(self):
        rows = nightaudit.occupancy()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Date", "Check-Ins", "Occupancy %", "", "", ""])
        for r, o in enumerate(rows):
            for c, v in enumerate([o["date"], o["checkins"],
                                   o["occ_pct"], "", "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Night Audit - Occupancy Analysis")

    def _rev(self):
        rows = nightaudit.revenue_summary()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Date", "Dr (Charges)", "Cr (Payments)", "Lines", "", ""])
        for r, x in enumerate(rows):
            for c, v in enumerate([x["date"], round(x["dr"], 2),
                                   round(x["cr"], 2), x["lines"], "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Night Audit - Revenue Summary (Daily Report)")

    def _room(self):
        rows = nightaudit.room_revenue()
        self.tbl.setRowCount(len(rows))
        self.tbl.setHorizontalHeaderLabels(
            ["Date", "Room Revenue (RC)", "", "", "", ""])
        for r, x in enumerate(rows):
            for c, v in enumerate([x["date"], round(x["roomrev"], 2),
                                   "", "", "", ""]):
                self.tbl.setItem(r, c, _dark_item(v))
        self.setWindowTitle("Night Audit - Room Revenue")


def open_pos(parent=None):
    PosBrowser(parent).exec()


def open_na(parent=None):
    NABrowser(parent).exec()


def main() -> int:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = PosBrowser()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
