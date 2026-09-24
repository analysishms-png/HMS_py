"""POS Happy Hours UI (VB6: HappyHours / HappyHoursHead browser).

Tables: HappyHoursHead (SchemeCode, ItemCat, RestCode, FromTime, ToTime,
        DiscountType, DiscountValue, Active, EndDate)
Run: python -m HMS_py.ui.pos_happy_ui
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

from HMS_py.core.pos_happy import HappyHoursHeadAPI
from HMS_py.ui import theme as _theme


class PosHappyDialog(QDialog):
    COLS = ["Code", "Name", "FromTime", "ToTime", "Discount", "Status"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Happy Hours")
        self.resize(900, 600)
        self._selected_code = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("POS Happy Hours - Happy Hours Records"))

        self.table = QTableWidget(0, len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        grp = QGroupBox("Happy Hours Details")
        form = QFormLayout()
        self.txt_code = QLineEdit()
        self.txt_code.setPlaceholderText("Scheme code")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Item category name")
        self.txt_fromtime = QLineEdit()
        self.txt_fromtime.setPlaceholderText("Start time (e.g. 10:00)")
        self.txt_totime = QLineEdit()
        self.txt_totime.setPlaceholderText("End time (e.g. 18:00)")
        self.txt_discount = QLineEdit()
        self.txt_discount.setPlaceholderText("Discount value")
        self.txt_status = QLineEdit()
        self.txt_status.setPlaceholderText("Active / Inactive")
        self.txt_restcode = QLineEdit()
        self.txt_restcode.setPlaceholderText("Restaurant code")
        self.txt_enddate = QLineEdit()
        self.txt_enddate.setPlaceholderText("End date (YYYY-MM-DD)")
        form.addRow("Code:", self.txt_code)
        form.addRow("Name:", self.txt_name)
        form.addRow("From Time:", self.txt_fromtime)
        form.addRow("To Time:", self.txt_totime)
        form.addRow("Discount:", self.txt_discount)
        form.addRow("Status:", self.txt_status)
        form.addRow("RestCode:", self.txt_restcode)
        form.addRow("End Date:", self.txt_enddate)
        grp.setLayout(form)
        layout.addWidget(grp)

        btn_layout = QHBoxLayout()
        btn_new = QPushButton("New"); btn_new.setToolTip("Add a new happy hours entry"); btn_new.clicked.connect(self._new_entry)
        btn_edit = QPushButton("Edit"); btn_edit.setToolTip("Edit the selected happy hours entry"); btn_edit.clicked.connect(self._edit_entry)
        btn_delete = QPushButton("Delete"); btn_delete.setToolTip("Delete the selected happy hours entry"); btn_delete.clicked.connect(self._delete_entry)
        btn_refresh = QPushButton("Refresh"); btn_refresh.setToolTip("Refresh the happy hours list"); btn_refresh.clicked.connect(self._refresh)
        btn_exit = QPushButton("Exit"); btn_exit.setToolTip("Close the POS Happy Hours"); btn_exit.clicked.connect(self.close)
        for b in (btn_new, btn_edit, btn_delete, btn_refresh, btn_exit):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        for rec in rows:
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            vals = [
                rec.get("schemecode", ""),
                rec.get("itemcat", ""),
                rec.get("fromtime", ""),
                rec.get("totime", ""),
                rec.get("discountvalue", ""),
                "Active" if rec.get("active") == "Y" else "Inactive",
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
        code = self.table.item(row, 0).text()
        try:
            rec = HappyHoursHeadAPI.get(code)
            if rec:
                self.txt_code.setText(str(rec.get("schemecode", "")))
                self.txt_name.setText(str(rec.get("itemcat", "")))
                self.txt_fromtime.setText(str(rec.get("fromtime", "")))
                self.txt_totime.setText(str(rec.get("totime", "")))
                self.txt_discount.setText(str(rec.get("discountvalue", "")))
                self.txt_status.setText("Active" if rec.get("active") == "Y" else "Inactive")
                self.txt_restcode.setText(str(rec.get("restcode", "")))
                self.txt_enddate.setText(str(rec.get("enddate", "")))
                self._selected_code = code
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _refresh(self):
        try:
            rows = HappyHoursHeadAPI.list_all()
            self._fill_table(rows)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _new_entry(self):
        code = self.txt_code.text().strip()
        if not code:
            QMessageBox.information(self, "Info", "Enter Scheme Code for new entry.")
            return
        rec = {
            "schemecode": code,
            "itemcat": self.txt_name.text(),
            "restcode": self.txt_restcode.text(),
            "fromtime": self.txt_fromtime.text(),
            "totime": self.txt_totime.text(),
            "discounttype": "%",
            "discountvalue": self.txt_discount.text(),
            "active": "Y" if self.txt_status.text().strip().upper() in ("ACTIVE", "Y", "") else "N",
            "enddate": self.txt_enddate.text() or None,
        }
        try:
            HappyHoursHeadAPI.insert(rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _edit_entry(self):
        if not self._selected_code:
            QMessageBox.information(self, "Info", "Select an entry to edit.")
            return
        rec = {
            "itemcat": self.txt_name.text(),
            "restcode": self.txt_restcode.text(),
            "fromtime": self.txt_fromtime.text(),
            "totime": self.txt_totime.text(),
            "discounttype": "%",
            "discountvalue": self.txt_discount.text(),
            "active": "Y" if self.txt_status.text().strip().upper() in ("ACTIVE", "Y") else "N",
            "enddate": self.txt_enddate.text() or None,
        }
        try:
            HappyHoursHeadAPI.update(self._selected_code, rec)
            self._refresh()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _delete_entry(self):
        if not self._selected_code:
            QMessageBox.information(self, "Info", "Select an entry to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Delete happy hours entry {self._selected_code}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                HappyHoursHeadAPI.delete(self._selected_code)
                self._refresh()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))


def open_pos_happy(parent=None):
    dlg = PosHappyDialog(parent)
    dlg.exec()
    return dlg


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PosHappyDialog()
    w.show()
    raise SystemExit(app.exec())
