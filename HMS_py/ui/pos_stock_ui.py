"""POS Stock Management UI (VB6: Stock transaction browser).

Tables: Stock (DocId, Sno, Vtype, Vdate, Item, QtyIss, QtyRec, Rate, Amount)
Run: python -m HMS_py.ui.pos_stock_ui
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLabel, QLineEdit, QMessageBox, QHeaderView,
                              QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from HMS_py.core.pos_stock import StockAPI
from HMS_py.ui import theme as _theme


class PosStockDialog(QDialog):
    COLS = ["DocId", "VDate", "Vtype", "ItemCode", "Qty", "Rate", "Amount"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Stock Management")
        self.resize(900, 600)
        self._selected_docid = None
        self._selected_sno = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("POS Stock Management - Stock Records"))

        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        grp = QGroupBox("Stock Details")
        form = QFormLayout()
        self.txt_docid = QLineEdit()
        self.txt_docid.setPlaceholderText("Document ID")
        self.txt_vdate = QLineEdit()
        self.txt_vdate.setPlaceholderText("Voucher date")
        self.txt_vtype = QLineEdit()
        self.txt_vtype.setPlaceholderText("Voucher type (e.g. STK)")
        self.txt_item = QLineEdit()
        self.txt_item.setPlaceholderText("Item code")
        self.txt_qty = QLineEdit()
        self.txt_qty.setPlaceholderText("Quantity issued")
        self.txt_rate = QLineEdit()
        self.txt_rate.setPlaceholderText("Rate per unit")
        self.txt_amount = QLineEdit()
        self.txt_amount.setPlaceholderText("Total amount")
        form.addRow("DocId:", self.txt_docid)
        form.addRow("VDate:", self.txt_vdate)
        form.addRow("Vtype:", self.txt_vtype)
        form.addRow("Item Code:", self.txt_item)
        form.addRow("Qty:", self.txt_qty)
        form.addRow("Rate:", self.txt_rate)
        form.addRow("Amount:", self.txt_amount)
        grp.setLayout(form)
        layout.addWidget(grp)

        btn_layout = QHBoxLayout()
        btn_new = QPushButton("New Stock Entry"); btn_new.setToolTip("Create a new stock entry"); btn_new.clicked.connect(self._new_stock)
        btn_refresh = QPushButton("Refresh"); btn_refresh.setToolTip("Refresh the stock list"); btn_refresh.clicked.connect(self._refresh)
        btn_exit = QPushButton("Exit"); btn_exit.setToolTip("Close the POS Stock Management"); btn_exit.clicked.connect(self.close)
        for b in (btn_new, btn_refresh, btn_exit):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        for rec in rows:
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            vals = [
                rec.get("docid", ""),
                str(rec.get("vdate", "")),
                rec.get("vtype", ""),
                rec.get("item", ""),
                rec.get("qtyiss", ""),
                rec.get("rate", ""),
                rec.get("amount", ""),
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v) if v is not None else "")
                item.setForeground(QColor(_theme.palette()["text"]))
                self.table.setItem(idx, c, item)

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        docid = self.table.item(row, 0).text()
        try:
            stock_rows = StockAPI.list_by_doc(docid)
            if stock_rows:
                rec = stock_rows[0]
                self.txt_docid.setText(str(rec.get("docid", "")))
                self.txt_vdate.setText(str(rec.get("vdate", "")))
                self.txt_vtype.setText(str(rec.get("vtype", "")))
                self.txt_item.setText(str(rec.get("item", "")))
                self.txt_qty.setText(str(rec.get("qtyiss", "")))
                self.txt_rate.setText(str(rec.get("rate", "")))
                self.txt_amount.setText(str(rec.get("amount", "")))
                self._selected_docid = docid
                self._selected_sno = rec.get("sno")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _refresh(self):
        try:
            rows = StockAPI.list_all()
            self._fill_table(rows)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _new_stock(self):
        docid = self.txt_docid.text().strip()
        if not docid:
            QMessageBox.information(self, "Info", "Enter DocId for new stock entry.")
            return
        rec = {
            "docid": docid,
            "vtype": self.txt_vtype.text() or "STK",
            "vdate": self.txt_vdate.text(),
            "item": self.txt_item.text(),
            "qtyiss": self.txt_qty.text(),
            "rate": self.txt_rate.text(),
            "amount": self.txt_amount.text(),
        }
        try:
            StockAPI.insert(rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


def open_pos_stock(parent=None):
    dlg = PosStockDialog(parent)
    dlg.exec()
    return dlg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PosStockDialog()
    w.show()
    raise SystemExit(app.exec())
