import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QFormLayout, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from HMS_py.core import member_billing
from HMS_py.ui import theme as _theme


class MemberBillingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Member Billing")
        self.resize(900, 600)
        self.current_mode = None
        self.current_vno = None
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["vno", "MemCode", "MemName", "BillDate", "NetAmt", "Status"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_select)
        splitter.addWidget(self.table)

        # Form + buttons
        bottom = QWidget()
        bl = QVBoxLayout(bottom)

        form = QFormLayout()
        self.fld_vno = QLineEdit()
        self.fld_vno.setMaxLength(10)
        self.fld_vno.setReadOnly(True)
        self.fld_vno.setPlaceholderText("Auto-generated")
        self.fld_memcode = QLineEdit()
        self.fld_memcode.setMaxLength(10)
        self.fld_memcode.setPlaceholderText("e.g. MEM001")
        self.fld_memname = QLineEdit()
        self.fld_memname.setMaxLength(60)
        self.fld_memname.setPlaceholderText("Member name")
        self.fld_billdate = QLineEdit()
        self.fld_billdate.setMaxLength(12)
        self.fld_billdate.setPlaceholderText("YYYY-MM-DD")
        self.fld_netamt = QLineEdit()
        self.fld_netamt.setMaxLength(12)
        self.fld_netamt.setPlaceholderText("e.g. 5000")
        self.fld_remarks = QLineEdit()
        self.fld_remarks.setMaxLength(100)
        self.fld_remarks.setPlaceholderText("Optional remarks")
        form.addRow("vno:", self.fld_vno)
        form.addRow("MemCode:", self.fld_memcode)
        form.addRow("MemName:", self.fld_memname)
        form.addRow("BillDate:", self.fld_billdate)
        form.addRow("NetAmt:", self.fld_netamt)
        form.addRow("Remarks:", self.fld_remarks)
        bl.addLayout(form)

        self._fields = [self.fld_memcode, self.fld_memname, self.fld_billdate,
                        self.fld_netamt, self.fld_remarks]

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("New Bill")
        self.btn_new.setToolTip("Create a new billing record")
        self.btn_new.clicked.connect(self._on_new)
        self.btn_view = QPushButton("View Details")
        self.btn_view.setToolTip("View full bill details")
        self.btn_view.clicked.connect(self._on_view)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setToolTip("Reload data from database")
        self.btn_refresh.clicked.connect(self._refresh)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_exit.clicked.connect(self.close)
        self.btn_save = QPushButton("Save Bill")
        self.btn_save.setToolTip("Save the billing record to database")
        self.btn_save.clicked.connect(self._on_save)
        for b in (self.btn_new, self.btn_save, self.btn_view,
                  self.btn_refresh, self.btn_exit):
            btn_row.addWidget(b)
        bl.addLayout(btn_row)

        # Family section
        fam_row = QHBoxLayout()
        self.fld_famcode = QLineEdit()
        self.fld_famcode.setMaxLength(10)
        self.fld_famcode.setPlaceholderText("e.g. MEM001")
        self.fld_famname = QLineEdit()
        self.fld_famname.setMaxLength(60)
        self.fld_famname.setPlaceholderText("Family member name")
        btn_add_fam = QPushButton("Add Family")
        btn_add_fam.setToolTip("Add family member for the selected member")
        btn_add_fam.clicked.connect(self._on_add_family)
        fam_row.addWidget(QLabel("Family Code:"))
        fam_row.addWidget(self.fld_famcode)
        fam_row.addWidget(QLabel("Family Name:"))
        fam_row.addWidget(self.fld_famname)
        fam_row.addWidget(btn_add_fam)
        bl.addLayout(fam_row)

        splitter.addWidget(bottom)

    def _fields_enabled(self, enabled):
        for w in self._fields:
            w.setEnabled(enabled)

    @staticmethod
    def _dark_item(text):
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor(_theme.palette()["text"]))
        return item

    def _clear_form(self):
        self.fld_vno.clear()
        for w in self._fields:
            w.clear()

    def _refresh(self):
        try:
            rows = member_billing.list_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self.table.setRowCount(0)
        if not rows:
            return
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = ([r.get("vno", ""), r.get("memcode", ""), "",
                     str(r.get("billdate") or ""), r.get("netamount", 0),
                     r.get("u_ae", "")]
                    if isinstance(r, dict) else list(r))
            for j, val in enumerate(vals):
                self.table.setItem(i, j, self._dark_item(val))

    def _on_select(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        self.fld_vno.setText(self.table.item(row, 0).text())
        self.fld_memcode.setText(self.table.item(row, 1).text())
        self.fld_memname.setText(self.table.item(row, 2).text())
        self.fld_billdate.setText(self.table.item(row, 3).text())
        self.fld_netamt.setText(self.table.item(row, 4).text())

    def _on_new(self):
        self.current_mode = "new"
        self.current_vno = None
        self._clear_form()
        self._fields_enabled(True)
        self.fld_memcode.setFocus()

    def _on_view(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.information(self, "Info", "Select a bill first.")
            return
        row = sel[0].row()
        vno = self.table.item(row, 0).text()
        try:
            rec = member_billing.get(vno)
            if rec:
                lines = []
                for key in ("vno", "MemCode", "MemName", "BillDate", "NetAmt", "Status", "Remarks"):
                    val = rec.get(key, "") if isinstance(rec, dict) else getattr(rec, key, "")
                    lines.append(f"{key}: {val}")
                QMessageBox.information(self, "Bill Details", "\n".join(lines))
            else:
                QMessageBox.information(self, "Info", "No details found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_save(self):
        rec = {
            "memcode": self.fld_memcode.text().strip(),
            "billdate": self.fld_billdate.text().strip() or None,
            "amount": self.fld_netamt.text().strip() or 0,
            "netamount": self.fld_netamt.text().strip() or 0,
        }
        if not rec["memcode"]:
            QMessageBox.warning(self, "Warning", "MemCode required.")
            return
        try:
            if self.current_mode == "new":
                member_billing.insert(rec)
            elif self.current_mode == "edit" and self.current_vno:
                member_billing.get(self.current_vno)  # exists-check
                member_billing.delete_membill(self.current_vno)
                member_billing.insert(rec)
            self._refresh()
            self._clear_form()
            self._fields_enabled(False)
            self.current_mode = None
            QMessageBox.information(self, "Success", "Bill saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_add_family(self):
        memcode = self.fld_famcode.text().strip()
        famname = self.fld_famname.text().strip()
        if not memcode or not famname:
            QMessageBox.warning(self, "Warning", "Family code and name are required.")
            return
        rec = {"subcode": memcode, "name": famname}
        try:
            member_billing.insert_family(rec)
            QMessageBox.information(self, "Success", "Family record added.")
            self.fld_famcode.clear()
            self.fld_famname.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_member_billing(parent=None):
    dlg = MemberBillingDialog(parent)
    dlg.exec()
    return dlg
