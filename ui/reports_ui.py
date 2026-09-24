"""Reports Center UI - REPORTS_TXT collection (231 VB6 reports) ka viewer.

Run: python -m HMS_py.ui.reports_ui
Menu wiring: shell registry me module-wise report leaves (Front Office,
Finance, Point Of Sale, Inventory, Night Audit). READ-ONLY — core/reports.py
sirf SELECT chalata hai; export_csv file likhta hai, DB me kuch nahi.
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QFileDialog,
                             QFormLayout, QHBoxLayout, QHeaderView, QLabel,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from HMS_py.core import reports as rp


def _cell(val) -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return it


class ReportsCenter(QDialog):
    """Date-range + report-picker + grid + CSV export (read-only)."""

    def __init__(self, parent=None, module: str | None = None,
                 report_key: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Reports Center - HMS_py")
        self.resize(900, 560)
        self._cols: list[str] = []
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Report:"))
        self.cmbReport = QComboBox()
        by_mod = rp.by_module()
        for mod in sorted(by_mod):
            for r in by_mod[mod]:
                self.cmbReport.addItem(f"[{mod}] {r['title']}", r["key"])
        top.addWidget(self.cmbReport, 1)
        root.addLayout(top)

        form = QFormLayout()
        today = datetime.date.today()
        self.dtFrom = QDateEdit()
        self.dtFrom.setCalendarPopup(True)
        self.dtFrom.setDisplayFormat("dd/MM/yyyy")
        self.dtFrom.setDate(QDate(2016, 1, 1))
        self.dtTo = QDateEdit()
        self.dtTo.setCalendarPopup(True)
        self.dtTo.setDisplayFormat("dd/MM/yyyy")
        self.dtTo.setDate(QDate(today.year, today.month, today.day))
        form.addRow("From:", self.dtFrom)
        form.addRow("To:", self.dtTo)
        root.addLayout(form)

        btns = QHBoxLayout()
        self.btnRun = QPushButton("Run Report")
        self.btnRun.setDefault(True)
        self.btnRun.setToolTip("Execute the selected report")
        self.btnRun.clicked.connect(self._run)
        self.btnCsv = QPushButton("Export CSV")
        self.btnCsv.setToolTip("Export report results to CSV file")
        self.btnCsv.clicked.connect(self._csv)
        btns.addWidget(self.btnRun)
        btns.addWidget(self.btnCsv)
        btns.addStretch(1)
        root.addLayout(btns)

        self.lblStatus = QLabel(
            "Ready (read-only — DB me koi write nahi hota)")
        root.addWidget(self.lblStatus)

        self.tbl = QTableWidget(0, 0)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        if report_key:
            i = self.cmbReport.findData(report_key)
            if i >= 0:
                self.cmbReport.setCurrentIndex(i)
        elif module:
            for i in range(self.cmbReport.count()):
                if self.cmbReport.itemText(i).startswith(f"[{module}]"):
                    self.cmbReport.setCurrentIndex(i)
                    break
        self._run()

    def _key(self) -> str:
        return self.cmbReport.currentData()

    def _run(self):
        try:
            cols, rows = rp.run(self._key(), self.dtFrom.date().toPyDate(),
                                self.dtTo.date().toPyDate())
        except Exception as e:
            QMessageBox.critical(self, "Report Error", str(e)[:300])
            return
        self._cols = cols
        self.tbl.clear()
        self.tbl.setColumnCount(len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.setRowCount(0)
        for row in rows[:2000]:
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            for c, v in enumerate(row):
                self.tbl.setItem(r, c, _cell(v))
        self.tbl.resizeColumnsToContents()
        self.lblStatus.setText(
            f"{len(rows)} rows  (grid me pehli 2000) — read-only")

    def _csv(self):
        if not self._cols:
            QMessageBox.information(self, "Export", "Pehle report chalao")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", f"{self._key()}.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            n = rp.export_csv(self._key(), self.dtFrom.date().toPyDate(),
                              self.dtTo.date().toPyDate(), path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e)[:300])
            return
        self.lblStatus.setText(f"{n} rows -> {path}")
        QMessageBox.information(self, "Export", f"{n} rows exported")


def open_reports(parent=None, module: str | None = None,
                 report_key: str | None = None):
    ReportsCenter(parent, module=module, report_key=report_key).exec()


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    open_reports()
