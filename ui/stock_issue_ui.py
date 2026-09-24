"""Stock Issue Entry (VB6: pGIss/pReqSlip port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from HMS_py.core import inventory as inv
from ui.theme import palette

class StockIssueWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stock Issue (Requisition)")
        self.resize(900, 600)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        hdr = QGroupBox("Issue Header")
        hdr_lay = QFormLayout(hdr)
        self.dt_date = QDateEdit(); self.dt_date.setCalendarPopup(True)
        self.dt_date.setDate(QDate.currentDate())
        self.txt_godown = QLineEdit(); self.txt_godown.setPlaceholderText("Godown code")
        self.txt_remark = QLineEdit()
        self.txt_remark.setPlaceholderText("Enter remark")
        hdr_lay.addRow("Date:", self.dt_date)
        hdr_lay.addRow("Godown:", self.txt_godown)
        hdr_lay.addRow("Remark:", self.txt_remark)
        layout.addWidget(hdr)
        lines_grp = QGroupBox("Issue Lines")
        lines_lay = QVBoxLayout(lines_grp)
        self.table = QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["SNo", "Item Code", "Qty", "Rate", "Amount"])
        self.table.setAlternatingRowColors(True)
        lines_lay.addWidget(self.table)
        btn_lay = QHBoxLayout()
        self.btn_add = QPushButton("Add Line (+)")
        self.btn_add.setToolTip("Add a new issue line")
        self.btn_del = QPushButton("Remove (-)")
        self.btn_del.setToolTip("Remove the selected issue line")
        self.btn_save = QPushButton("Save Issue")
        self.btn_save.setProperty("success", True)
        self.btn_save.setToolTip("Save the stock issue")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the stock issue form")
        for b in [self.btn_add, self.btn_del, self.btn_save, self.btn_exit]:
            btn_lay.addWidget(b)
        lines_lay.addLayout(btn_lay)
        layout.addWidget(lines_grp)
        self.btn_add.clicked.connect(self._add_line)
        self.btn_del.clicked.connect(self._del_line)
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)

    def _add_line(self):
        r = self.table.rowCount(); self.table.insertRow(r)
        for c, v in enumerate([str(r+1), "", "0", "0", "0"]):
            it = QTableWidgetItem(v)
            it.setForeground(QColor(palette()["text"]))
            self.table.setItem(r, c, it)

    def _del_line(self):
        r = self.table.currentRow()
        if r >= 0: self.table.removeRow(r)

    def _save(self):
        godown = self.txt_godown.text().strip()
        vdate = self.dt_date.date().toPyDate()
        lines = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
            if not item: continue
            try:
                qty = float(self.table.item(r, 2).text() or 0)
                rate = float(self.table.item(r, 3).text() or 0)
            except ValueError:
                QMessageBox.warning(self, "Error", "Row %d: Invalid" % (r+1)); return
            lines.append({"item": item, "godown": godown, "qty": qty,
                          "unit": "", "rate": rate, "amount": qty * rate})
        if not lines:
            QMessageBox.warning(self, "Empty", "Koi lines nahi"); return
        try:
            result = inv.stock_issue(lines, vdate=vdate)
            QMessageBox.information(self, "Saved", "Stock Issue saved!\nDocId: %s" % result["docid"])
            self.table.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def open_stock_issue(parent=None):
    w = StockIssueWindow(parent); w.show(); return w
