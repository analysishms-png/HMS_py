"""Requisition Slip (VB6: pReqSlip port) + Pending M.R. browser.

VB6 pReqSlip: pending indent lines (Indent1.ClearYN='') dikhata hai aur
unke liye Stock Issue (Vtype='RQI') generate karta hai - linked indent
lines ClearYN='Y' ho jaati hain (inventory.stock_issue already karta hai).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QGroupBox, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from HMS_py.core import inventory as inv
from HMS_py.ui import theme as _theme


def _cell(val, fg: str = "", editable: bool = False) -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    if not editable:
        it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    else:
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(fg or _theme.palette()["text"]))
    return it


class RequisitionSlipWindow(QMainWindow):
    """Pending indent lines -> select -> issue stock (RQI)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Requisition Slip (Pending Indents)")
        self.resize(980, 620)
        self._build_ui()
        self.reload()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        info = QLabel(
            "Pending indent lines (ClearYN='') list. Jo lines issue karni hain "
            "unke 'Issue Qty' me number daalein (blank = skip), phir Save Issue.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{_theme.palette()['text']}; padding:4px;")
        lay.addWidget(info)

        grp = QGroupBox("Pending Requisition Lines")
        glay = QVBoxLayout(grp)
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["Indent DocId", "Sno", "Date", "Dept", "Item", "Req Qty",
             "Unit", "Godown", "Rate", "Issue Qty"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        glay.addWidget(self.table)

        btns = QHBoxLayout()
        self.btn_reload = QPushButton("Reload")
        self.btn_reload.setToolTip("Reload pending indent lines from database")
        self.btn_issue = QPushButton("Save Issue (RQI)")
        self.btn_issue.setStyleSheet(
            "QPushButton{background:#28a745;color:white;font-weight:bold;}")
        self.btn_issue.setToolTip("Generate stock issue (RQI) for lines with Issue Qty")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the requisition slip form")
        for b in (self.btn_reload, self.btn_issue, self.btn_exit):
            btns.addWidget(b)
        btns.addStretch()
        glay.addLayout(btns)
        lay.addWidget(grp)

        self.btn_reload.clicked.connect(self.reload)
        self.btn_issue.clicked.connect(self._do_issue)
        self.btn_exit.clicked.connect(self.close)

    def reload(self):
        """Pending indent lines (ClearYN='') grid me load karo."""
        self.table.setRowCount(0)
        try:
            rows = db_pending_lines()
        except Exception as e:
            QMessageBox.critical(self, "Load", f"Pending indents load fail: {e}")
            return
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            docid, sno, vdate, dept, item, qty, unit, godown, rate = row
            self.table.setItem(r, 0, _cell(docid))
            self.table.setItem(r, 1, _cell(sno))
            self.table.setItem(r, 2, _cell(vdate))
            self.table.setItem(r, 3, _cell(dept))
            self.table.setItem(r, 4, _cell(item))
            self.table.setItem(r, 5, _cell(qty))
            self.table.setItem(r, 6, _cell(unit))
            self.table.setItem(r, 7, _cell(godown))
            self.table.setItem(r, 8, _cell(rate))
            self.table.setItem(r, 9, _cell("", editable=True))

    def _do_issue(self):
        lines = []
        for r in range(self.table.rowCount()):
            issue_item = self.table.item(r, 9)
            raw = issue_item.text().strip() if issue_item else ""
            if not raw:
                continue
            try:
                qty = float(raw)
            except ValueError:
                QMessageBox.warning(
                    self, "Error",
                    f"Row {r + 1}: Issue Qty '{raw}' valid number nahi hai")
                return
            if qty <= 0:
                QMessageBox.warning(
                    self, "Error", f"Row {r + 1}: Issue Qty > 0 hona chahiye")
                return
            item_item = self.table.item(r, 4)
            item_code = item_item.text().strip() if item_item else ""
            docid_item = self.table.item(r, 0)
            sno_item = self.table.item(r, 1)
            godown_item = self.table.item(r, 7)
            rate_item = self.table.item(r, 8)
            godown = godown_item.text().strip() if godown_item else ""
            try:
                rate = float(rate_item.text() or 0) if rate_item else 0.0
            except ValueError:
                rate = 0.0
            lines.append({
                "item": item_code,
                "godown": godown,
                "qty": qty,
                "unit": self.table.item(r, 6).text() if self.table.item(r, 6) else "",
                "rate": rate,
                "amount": qty * rate,
                "indent_docid": docid_item.text() if docid_item else "",
                "indent_sno": int(sno_item.text()) if sno_item else 0,
            })
        if not lines:
            QMessageBox.warning(
                self, "Empty",
                "Koi issue qty nahi. 'Issue Qty' column me numbers daalein.")
            return
        try:
            result = inv.stock_issue(lines)
            QMessageBox.information(
                self, "Saved",
                f"Stock Issue saved!\nDocId: {result['docid']} "
                f"({len(lines)} lines, linked indents cleared)")
            self.reload()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def db_pending_lines() -> list:
    """Indent1 lines jinka ClearYN='' hai (pending requisitions).

    PI-15: also return Indent.Godown + ItemMast rate default
    (VB6 pGIss: CASE LPurRate<=0 THEN PurchRate ELSE LPurRate).
    """
    from HMS_py.core import db
    rows = db.query(
        "SELECT TOP 200 i1.DocId, i1.Sno, i1.VDate, i.Department, "
        "i1.Item, i1.Qty, i1.Unit, "
        "ISNULL(i.Godown, '') AS IndentGodown, "
        "CASE WHEN MAX(im.LPurRate) <= 0 OR MAX(im.LPurRate) IS NULL "
        "THEN ISNULL(MAX(im.PurchRate), 0) ELSE MAX(im.LPurRate) END "
        "AS ItemRate "
        "FROM Indent1 i1 "
        "INNER JOIN Indent i ON i.DocId = i1.DocId "
        "LEFT JOIN ItemMast im ON im.Code = i1.Item "
        "WHERE RTRIM(ISNULL(i1.ClearYN, '')) = '' "
        "GROUP BY i1.DocId, i1.Sno, i1.VDate, i.Department, "
        "i1.Item, i1.Qty, i1.Unit, i.Godown "
        "ORDER BY i1.DocId, i1.Sno")
    return [
        (r[0], r[1], r[2], r[3] or "", r[4], float(r[5] or 0), r[6] or "",
         r[7] or "", float(r[8] or 0))
        for r in rows
    ]


def open_requisition_slip(parent=None):
    w = RequisitionSlipWindow(parent)
    w.show()
    return w


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = RequisitionSlipWindow()
    w.show()
    sys.exit(app.exec())
