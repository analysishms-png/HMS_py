import sys
sys.path.insert(0, r"C:\Users\LENOVO\Desktop\serialkey\PROJECT_REPAIR - Copy\HMS_py")

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QMessageBox, QHeaderView, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from HMS_py.core import facility_billing
from HMS_py.ui import theme as _theme


class FacilityBillingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Facility Billing")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # ── table ────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["VNo", "FacilityCode", "MemberCode", "BillDate", "Amount", "Status"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        # ── form ─────────────────────────────────────────────────
        grp = QGroupBox("Bill Details")
        form = QFormLayout()
        self.txt_facility = QLineEdit()
        self.txt_member = QLineEdit()
        self.txt_date = QLineEdit()
        self.txt_amount = QLineEdit()
        self.txt_remarks = QLineEdit()
        form.addRow("FacilityCode:", self.txt_facility)
        form.addRow("MemberCode:", self.txt_member)
        form.addRow("BillDate:", self.txt_date)
        form.addRow("Amount:", self.txt_amount)
        form.addRow("Remarks:", self.txt_remarks)
        grp.setLayout(form)
        layout.addWidget(grp)

        # ── buttons ──────────────────────────────────────────────
        btn_layout = QHBoxLayout()

        btn_new = QPushButton("New Bill")
        btn_new.setToolTip("Create a new facility bill")
        btn_new.clicked.connect(self._new_bill)
        btn_layout.addWidget(btn_new)

        btn_view = QPushButton("View Details")
        btn_view.setToolTip("View full bill details")
        btn_view.clicked.connect(self._view_details)
        btn_layout.addWidget(btn_view)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setToolTip("Reload data from database")
        btn_refresh.clicked.connect(self._refresh)
        btn_layout.addWidget(btn_refresh)

        btn_exit = QPushButton("Exit")
        btn_exit.setToolTip("Close this window")
        btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(btn_exit)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._selected_vno = None
        self._refresh()

    # ── helpers ──────────────────────────────────────────────────
    def _selected_row(self):
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else None

    def _fill(self, rows):
        self.table.setRowCount(0)
        for row_data in rows or []:
            vals = ([row_data.get("vno", ""), row_data.get("facilitycode", ""),
                     row_data.get("partycode", ""),
                     str(row_data.get("vdate") or ""),
                     row_data.get("amount", 0), row_data.get("u_ae", "")]
                    if isinstance(row_data, dict) else list(row_data))
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setForeground(QColor(_theme.palette()["text"]))
                self.table.setItem(idx, c, item)

    def _on_select(self):
        row = self._selected_row()
        if row is None:
            return
        vno = self.table.item(row, 0).text()
        try:
            rec = facility_billing.get_fbill1(vno)
            if rec:
                self.txt_facility.setText(str(rec.get("facilitycode", "")))
                self.txt_member.setText(str(rec.get("partycode", "")))
                self.txt_amount.setText(str(rec.get("amount", "")))
                self._selected_vno = int(vno)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _refresh(self):
        try:
            rows = facility_billing.list_all()
            self._fill(rows)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _new_bill(self):
        if not self.txt_facility.text().strip():
            QMessageBox.warning(self, "Validation", "FacilityCode required.")
            return
        rec = {
            "facilitycode": self.txt_facility.text(),
            "partycode": self.txt_member.text(),
            "amount": self.txt_amount.text() or 0,
            "unitrate": self.txt_amount.text() or 0,
            "remark": self.txt_remarks.text(),
        }
        try:
            facility_billing.insert(rec)
            self._refresh()
            self._clear_form()
            QMessageBox.information(self, "Success", "Bill saved.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _clear_form(self):
        self.txt_facility.clear()
        self.txt_member.clear()
        self.txt_date.clear()
        self.txt_amount.clear()
        self.txt_remarks.clear()
        self._selected_vno = None

    # ── actions ──────────────────────────────────────────────────

    def _view_details(self):
        row = self._selected_row()
        if row is None:
            QMessageBox.information(self, "Info", "Select a row first.")
            return
        vno = self.table.item(row, 0).text()
        try:
            rec = facility_billing.get(int(vno))
            if rec:
                info = "\n".join(f"{k}: {v}" for k, v in rec.items())
                QMessageBox.information(self, f"Bill {vno}", info)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


def open_facility_billing(parent=None):
    dlg = FacilityBillingDialog(parent)
    dlg.exec()
    return dlg


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = open_facility_billing()
    sys.exit(app.exec())
