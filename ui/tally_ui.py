"""Tally Export UI (VB6 frmTallyExport.frm port).

Run: python -m HMS_py.ui.tally_ui
Menu: Utilities/Finance -> 'Tally Export'. READ-ONLY DB (sirf XML files
banti hain) — VB6 jaisa hi: LedgerMaster.xml (groups+ledgers) +
Ledger.xml (vouchers, date-range).
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QDateEdit, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)

from HMS_py.core import tally_export as tx
from HMS_py.ui import theme as _theme


def _dark_item(val) -> QTableWidgetItem:
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


class TallyExportDialog(QDialog):
    """VB6 FrmTallyExport: From/To dates + Start button + status label."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tally Export - HMS_py")
        self.resize(760, 420)
        root = QVBoxLayout(self)

        form = QFormLayout()
        today = datetime.date.today()
        fy_start = datetime.date(today.year, 4, 1)
        if fy_start > today:
            fy_start = datetime.date(today.year - 1, 4, 1)
        self.dtFrom = QDateEdit()
        self.dtFrom.setCalendarPopup(True)
        self.dtFrom.setDisplayFormat("dd/MM/yyyy")
        self.dtFrom.setDate(QDate(fy_start.year, fy_start.month,
                                  fy_start.day))
        self.dtTo = QDateEdit()
        self.dtTo.setCalendarPopup(True)
        self.dtTo.setDisplayFormat("dd/MM/yyyy")
        self.dtTo.setDate(QDate(today.year, today.month, today.day))
        form.addRow("From:", self.dtFrom)
        form.addRow("To:", self.dtTo)
        root.addLayout(form)

        self.btnStart = QPushButton("Start Export")
        self.btnStart.setDefault(True)
        self.btnStart.setToolTip("Export ledger data to Tally XML format")
        self.btnStart.clicked.connect(self._start)
        root.addWidget(self.btnStart)

        self.lblStatus = QLabel("Ready (read-only: DB me koi write nahi)")
        root.addWidget(self.lblStatus)

        self.tbl = QTableWidget(0, 3)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

    def _start(self):
        d_from = self.dtFrom.date().toPyDate()
        d_to = self.dtTo.date().toPyDate()
        if d_from > d_to:
            QMessageBox.warning(self, "Tally Export",
                                "From > To nahi ho sakta")
            return
        self.lblStatus.setText("Exporting... (groups/ledgers/vouchers)")
        try:
            out = tx.export_all(os.getcwd(), date_from=d_from, date_to=d_to)
        except Exception as e:
            QMessageBox.critical(self, "Tally Export failed", str(e))
            self.lblStatus.setText("Failed")
            return
        self.lblStatus.setText(
            "LedgerMaster.xml and Ledger.xml Generated Successfully")
        rows = [
            ["LedgerMaster.xml (Groups)", out["groups"], out["master_xml"]],
            ["LedgerMaster.xml (Ledgers)", out["ledgers"],
             out["master_xml"]],
            ["Ledger.xml (Vouchers)", out["vouchers"], out["voucher_xml"]],
            ["Ledger.xml (Entries)", out["entries"], out["voucher_xml"]],
        ]
        self.tbl.clear()
        self.tbl.setRowCount(len(rows))
        self.tbl.setColumnCount(3)
        self.tbl.setHorizontalHeaderLabels(["Item", "Count", "File"])
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                self.tbl.setItem(r, c, _dark_item(v))


def open_tally(parent=None):
    TallyExportDialog(parent).exec()


def main() -> int:  # pragma: no cover
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = TallyExportDialog()
    w.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
