"""Purchase Bill Entry (VB6: pPBill port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from HMS_py.core import purchase as purch
from HMS_py.core import ledger as led
from HMS_py.ui.theme import palette

class PurchaseBillWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Purchase Bill Entry")
        self.resize(1000, 700)
        self._all_parties = []
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        hdr = QGroupBox("Purchase Bill Header")
        hdr_lay = QFormLayout(hdr)
        self.dt_date = QDateEdit(); self.dt_date.setCalendarPopup(True)
        self.dt_date.setDate(QDate.currentDate())
        self.cbo_party = QComboBox(); self.cbo_party.setEditable(True)
        self.txt_remark = QLineEdit()
        self.txt_remark.setPlaceholderText("Enter remark/narration")
        hdr_lay.addRow("Date:", self.dt_date)
        hdr_lay.addRow("Party:", self.cbo_party)
        hdr_lay.addRow("Remark:", self.txt_remark)
        layout.addWidget(hdr)
        lines_grp = QGroupBox("Bill Lines")
        lines_lay = QVBoxLayout(lines_grp)
        self.table = QTableWidget(); self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["SNo", "Item Code", "Item Name", "Qty", "Rate", "Tax%", "Amount",
             "", "TaxStru"])
        self.table.setColumnHidden(7, True)
        self.table.setAlternatingRowColors(True)
        lines_lay.addWidget(self.table)
        btn_lay = QHBoxLayout()
        self.btn_add = QPushButton("Add Line (+)")
        self.btn_add.setToolTip("Add a new bill line")
        self.btn_del = QPushButton("Remove (-)")
        self.btn_del.setToolTip("Remove the selected bill line")
        self.btn_save = QPushButton("Save Bill")
        self.btn_save.setProperty("success", True)
        self.btn_save.setToolTip("Save the purchase bill")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the purchase bill form")
        for b in [self.btn_add, self.btn_del, self.btn_save, self.btn_exit]:
            btn_lay.addWidget(b)
        lines_lay.addLayout(btn_lay)
        layout.addWidget(lines_grp)
        self.btn_add.clicked.connect(self._add_line)
        self.btn_del.clicked.connect(self._del_line)
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)

    def _load_data(self):
        try:
            self._all_parties = led.list_all()
            for p in self._all_parties:
                self.cbo_party.addItem(p["code"] + " - " + p["name"], p["code"])
        except Exception:
            pass

    def _add_line(self):
        r = self.table.rowCount(); self.table.insertRow(r)
        for c, v in enumerate([str(r+1), "", "", "0", "0", "0", "0", "", ""]):
            it = QTableWidgetItem(v)
            it.setForeground(QColor(palette()["text"]))
            self.table.setItem(r, c, it)

    def _del_line(self):
        r = self.table.currentRow()
        if r >= 0: self.table.removeRow(r)

    def _save(self):
        party_code = self.cbo_party.currentData() or ""
        vdate = self.dt_date.date().toPyDate()
        lines = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
            if not item: continue
            try:
                qty = float(self.table.item(r, 3).text() or 0)
                rate = float(self.table.item(r, 4).text() or 0)
                tax_per = float(self.table.item(r, 5).text() or 0)
            except ValueError:
                QMessageBox.warning(self, "Error", "Row %d: Invalid" % (r+1)); return
            amount = qty * rate
            # PI-4: TaxStru slab GST when structure code given (col 8)
            tax_stru = ""
            if self.table.columnCount() > 8 and self.table.item(r, 8):
                tax_stru = self.table.item(r, 8).text().strip()
            if tax_stru:
                from HMS_py.core import taxstru as _ts
                calc = _ts.calculate(tax_stru, amount)
                tax_per = (round(calc["total_tax"] / amount * 100, 2)
                           if amount else 0)
                tax_amt = calc["total_tax"]
            else:
                tax_amt = amount * tax_per / 100
            lines.append({"item": item, "qty": qty, "rate": rate, "unit": "",
                          "amount": amount, "tax_per": tax_per,
                          "tax_amt": tax_amt, "tax_stru": tax_stru,
                          "disc_per": 0, "disc_amt": 0})
        if not lines:
            QMessageBox.warning(self, "Empty", "Koi lines nahi"); return
        if not party_code:
            QMessageBox.warning(self, "Input", "Party code zaroori hai"); return
        try:
            result = purch.purchase_bill_create(
                party_code, vdate, lines,
                remark=self.txt_remark.text().strip())
            QMessageBox.information(
                self, "Saved",
                f"Purchase Bill saved!\nDocId: {result['docid']}")
            self.table.setRowCount(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def open_purchase_bill(parent=None):
    w = PurchaseBillWindow(parent); w.show(); return w
