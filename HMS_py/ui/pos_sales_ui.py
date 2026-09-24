"""POS Sales Register UI (VB6: RSSaleBill / POS Bill browser).

Tables: Sale1 (header) - DocId, VDate, RestCode, CustName, NetAmt, DelFlag
Run: python -m HMS_py.ui.pos_sales_ui
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

from HMS_py.core.pos_sales import Sale1API, SaleBillAPI
from HMS_py.ui import theme as _theme


class PosSalesDialog(QDialog):
    COLS = ["DocId", "VDate", "RestCode", "GuestName", "NetAmt", "Status"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Sales Register")
        self.resize(900, 600)
        self._selected_docid = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("POS Sales Register - Sale1 Records"))

        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        grp = QGroupBox("Sale Details")
        form = QFormLayout()
        self.txt_docid = QLineEdit(); self.txt_docid.setReadOnly(True)
        self.txt_docid.setPlaceholderText("Document ID")
        self.txt_vdate = QLineEdit()
        self.txt_vdate.setPlaceholderText("Voucher date")
        self.txt_restcode = QLineEdit()
        self.txt_restcode.setPlaceholderText("Restaurant code")
        self.txt_custname = QLineEdit()
        self.txt_custname.setPlaceholderText("Customer name")
        self.txt_netamt = QLineEdit()
        self.txt_netamt.setPlaceholderText("Net amount")
        self.txt_status = QLineEdit()
        self.txt_status.setPlaceholderText("Active / Voided")
        form.addRow("DocId:", self.txt_docid)
        form.addRow("VDate:", self.txt_vdate)
        form.addRow("RestCode:", self.txt_restcode)
        form.addRow("Guest Name:", self.txt_custname)
        form.addRow("Net Amt:", self.txt_netamt)
        form.addRow("Status:", self.txt_status)
        grp.setLayout(form)
        layout.addWidget(grp)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_new = QPushButton("New Sale")
        btn_new.setToolTip("Create a new sale entry")
        btn_new.setProperty("accent", True)
        btn_new.setMinimumHeight(34)
        btn_new.clicked.connect(self._new_sale)
        btn_void = QPushButton("Void")
        btn_void.setToolTip("Void the selected sale")
        btn_void.setProperty("role", "danger")
        btn_void.setMinimumHeight(34)
        btn_void.clicked.connect(self._void_sale)
        btn_print = QPushButton("Print")
        btn_print.setToolTip("Print the selected sale bill")
        btn_print.setMinimumHeight(34)
        btn_print.clicked.connect(self._print_sale)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setToolTip("Refresh the sales list")
        btn_refresh.setMinimumHeight(34)
        btn_refresh.clicked.connect(self._refresh)
        btn_exit = QPushButton("Exit")
        btn_exit.setToolTip("Close the POS Sales Register")
        btn_exit.setMinimumHeight(34)
        btn_exit.clicked.connect(self.close)
        for b in (btn_new, btn_void, btn_print, btn_refresh, btn_exit):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        if not rows:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No sales records found.")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, len(self.COLS))
            return
        for rec in rows:
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            vals = [
                rec.get("docid", ""),
                str(rec.get("vdate", "")),
                rec.get("restcode", ""),
                rec.get("custname", ""),
                rec.get("netamt", ""),
                "Voided" if rec.get("delflag") == "Y" else "Active",
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
            rec = Sale1API.get(docid)
            if rec:
                self.txt_docid.setText(str(rec.get("docid", "")))
                self.txt_vdate.setText(str(rec.get("vdate", "")))
                self.txt_restcode.setText(str(rec.get("restcode", "")))
                self.txt_custname.setText(str(rec.get("custname", "")))
                self.txt_netamt.setText(str(rec.get("netamt", "")))
                self.txt_status.setText("Voided" if rec.get("delflag") == "Y" else "Active")
                self._selected_docid = docid
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _refresh(self):
        try:
            rows = Sale1API.list_all()
            self._fill_table(rows)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _new_sale(self):
        docid = self.txt_docid.text().strip()
        if not docid:
            QMessageBox.information(self, "Info", "Enter DocId for new sale.")
            return
        try:
            netamt = float(self.txt_netamt.text() or 0)
        except ValueError:
            netamt = 0.0
        rec = {
            "docid": docid,
            "vtype": "SAL",
            "vdate": self.txt_vdate.text(),
            "restcode": self.txt_restcode.text(),
            "custname": self.txt_custname.text(),
            "total": netamt,
            "taxable": netamt,
            "tax": 0.0,
            "netamt": netamt,
        }
        try:
            # PI-2: full-save (Sale1 only for bare header entry;
            # sale2/suntran/paycharge/stock/kot optional)
            SaleBillAPI.full_save(rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _void_sale(self):
        if not self._selected_docid:
            QMessageBox.information(self, "Info", "Select a sale to void.")
            return
        reply = QMessageBox.question(self, "Confirm Void",
                                     f"Void sale {self._selected_docid}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Sale1API.delete(self._selected_docid)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _print_sale(self):
        if not self._selected_docid:
            QMessageBox.information(self, "Info", "Select a sale to print.")
            return
        QMessageBox.information(self, "Print", f"Print sale {self._selected_docid} - coming soon.")


def open_pos_sales(parent=None):
    dlg = PosSalesDialog(parent)
    dlg.exec()
    return dlg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PosSalesDialog()
    w.show()
    raise SystemExit(app.exec())
