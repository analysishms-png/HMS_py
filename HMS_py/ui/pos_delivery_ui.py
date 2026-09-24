"""POS Delivery Management UI (VB6: AssignDelivery browser).

Tables: AssignDelivery (DocId, VNo, DeliBoy, Ddate, BillAmt, Remark)
Run: python -m HMS_py.ui.pos_delivery_ui
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

from HMS_py.core.pos_delivery import AssignDelAPI
from HMS_py.ui import theme as _theme


class PosDeliveryDialog(QDialog):
    COLS = ["VNo", "DocId", "DeliveryBoy", "Status", "DeliveryDate"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Delivery Management")
        self.resize(900, 600)
        self._selected_docid = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("POS Delivery Management - AssignDelivery Records"))

        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        grp = QGroupBox("Delivery Details")
        form = QFormLayout()
        self.txt_docid = QLineEdit()
        self.txt_docid.setPlaceholderText("Document ID")
        self.txt_vno = QLineEdit()
        self.txt_vno.setPlaceholderText("Voucher number")
        self.txt_deliboy = QLineEdit()
        self.txt_deliboy.setPlaceholderText("Delivery boy name")
        self.txt_status = QLineEdit()
        self.txt_status.setPlaceholderText("Pending / Delivered")
        self.txt_ddate = QLineEdit()
        self.txt_ddate.setPlaceholderText("Delivery date")
        self.txt_billamt = QLineEdit()
        self.txt_billamt.setPlaceholderText("Bill amount")
        self.txt_remark = QLineEdit()
        self.txt_remark.setPlaceholderText("Remarks")
        form.addRow("DocId:", self.txt_docid)
        form.addRow("VNo:", self.txt_vno)
        form.addRow("Delivery Boy:", self.txt_deliboy)
        form.addRow("Status:", self.txt_status)
        form.addRow("Delivery Date:", self.txt_ddate)
        form.addRow("Bill Amt:", self.txt_billamt)
        form.addRow("Remarks:", self.txt_remark)
        grp.setLayout(form)
        layout.addWidget(grp)

        btn_layout = QHBoxLayout()
        btn_new = QPushButton("New Assignment"); btn_new.setToolTip("Create a new delivery assignment"); btn_new.clicked.connect(self._new_assignment)
        btn_delivered = QPushButton("Mark Delivered"); btn_delivered.setToolTip("Mark the selected delivery as delivered"); btn_delivered.clicked.connect(self._mark_delivered)
        btn_refresh = QPushButton("Refresh"); btn_refresh.setToolTip("Refresh the delivery list"); btn_refresh.clicked.connect(self._refresh)
        btn_exit = QPushButton("Exit"); btn_exit.setToolTip("Close the POS Delivery Management"); btn_exit.clicked.connect(self.close)
        for b in (btn_new, btn_delivered, btn_refresh, btn_exit):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        for rec in rows:
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            vals = [
                rec.get("vno", ""),
                rec.get("docid", ""),
                rec.get("deliboy", ""),
                "Delivered" if rec.get("ddate") else "Pending",
                str(rec.get("ddate", "")),
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
        docid = self.table.item(row, 1).text()
        try:
            rec = AssignDelAPI.get(docid)
            if rec:
                self.txt_docid.setText(str(rec.get("docid", "")))
                self.txt_vno.setText(str(rec.get("vno", "")))
                self.txt_deliboy.setText(str(rec.get("deliboy", "")))
                self.txt_status.setText("Delivered" if rec.get("ddate") else "Pending")
                self.txt_ddate.setText(str(rec.get("ddate", "")))
                self.txt_billamt.setText(str(rec.get("billamt", "")))
                self.txt_remark.setText(str(rec.get("remark", "")))
                self._selected_docid = docid
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _refresh(self):
        try:
            rows = AssignDelAPI.list_all()
            self._fill_table(rows)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _new_assignment(self):
        docid = self.txt_docid.text().strip()
        if not docid:
            QMessageBox.information(self, "Info", "Enter DocId for new assignment.")
            return
        rec = {
            "docid": docid,
            "vtype": "DEL",
            "vno": self.txt_vno.text(),
            "deliboy": self.txt_deliboy.text(),
            "billamt": self.txt_billamt.text(),
            "remark": self.txt_remark.text(),
        }
        try:
            AssignDelAPI.insert(rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _mark_delivered(self):
        if not self._selected_docid:
            QMessageBox.information(self, "Info", "Select a delivery to mark delivered.")
            return
        from datetime import date
        rec = {
            "deliboy": self.txt_deliboy.text(),
            "billamt": self.txt_billamt.text(),
            "remark": self.txt_remark.text(),
            "ddate": str(date.today()),
        }
        try:
            AssignDelAPI.update(self._selected_docid, rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


def open_pos_delivery(parent=None):
    dlg = PosDeliveryDialog(parent)
    dlg.exec()
    return dlg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PosDeliveryDialog()
    w.show()
    raise SystemExit(app.exec())
