import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from HMS_py.core import ledger as _ledger_mod


class _LedgerMasterBridge:
    """fa_ledger_ops ke stale calls ko asli ledger-master (SubGroup,
    HMS_py/core/ledger.py) par route karta hai. Keys UI-shaped
    (AcCode/AcName/...) <-> core (code/name/...) translate hoti hain."""

    @staticmethod
    def list_ledger(cn=None):
        rows = _ledger_mod.list_all(cn=cn, top=500)
        return [{"AcCode": r["code"], "AcName": r["name"],
                 "GroupCode": r["group"], "OpBalance": "",
                 "DrCr": "", "Address": r["add1"]} for r in rows]

    @staticmethod
    def get_ledger(code, cn=None):
        r = _ledger_mod.get(code, cn=cn)
        if not r:
            return None
        return {"AcCode": r["code"], "AcName": r["name"],
                "GroupCode": r["group"], "OpBalance": "",
                "DrCr": "", "Address": r["add1"]}

    @staticmethod
    def insert_ledger(rec, cn=None, commit=True):
        return _ledger_mod.insert({
            "code": rec.get("AcCode", ""),
            "name": rec.get("AcName", ""),
            "group": rec.get("GroupCode", ""),
            "add1": rec.get("Address", "")}, cn=cn, commit=commit)

    @staticmethod
    def update_ledger(code, rec, cn=None, commit=True):
        return _ledger_mod.update(code, {
            "name": rec.get("AcName", ""),
            "group": rec.get("GroupCode", ""),
            "add1": rec.get("Address", "")}, cn=cn, commit=commit)


fa_ledger_ops = _LedgerMasterBridge()
from HMS_py.ui import theme as _theme


class FaLedgerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Finance Ledger Operations")
        self.resize(900, 600)
        self.current_code = None
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search by AcCode or AcName...")
        self.txt_search.textChanged.connect(self._filter)
        search_layout.addWidget(self.txt_search)
        layout.addLayout(search_layout)

        form_group = QGroupBox("Account Details")
        form_layout = QFormLayout(form_group)

        self.txt_ac_code = QLineEdit()
        self.txt_ac_code.setPlaceholderText("Enter account code")
        self.txt_ac_name = QLineEdit()
        self.txt_ac_name.setPlaceholderText("Enter account name")
        self.txt_group_code = QLineEdit()
        self.txt_group_code.setPlaceholderText("Enter group code")
        self.txt_op_balance = QLineEdit()
        self.txt_op_balance.setPlaceholderText("Opening balance")
        self.txt_dr_cr = QComboBox()
        self.txt_dr_cr.addItems(["Dr", "Cr"])
        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("Enter address")

        form_layout.addRow("AcCode:", self.txt_ac_code)
        form_layout.addRow("AcName:", self.txt_ac_name)
        form_layout.addRow("GroupCode:", self.txt_group_code)
        form_layout.addRow("OpBalance:", self.txt_op_balance)
        form_layout.addRow("Dr/Cr:", self.txt_dr_cr)
        form_layout.addRow("Address:", self.txt_address)
        layout.addWidget(form_group)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("New Account")
        self.btn_new.setToolTip("Create a new ledger account")
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setToolTip("Update the selected account details")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setToolTip("Reload all ledger accounts from database")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")

        for b in [self.btn_new, self.btn_edit, self.btn_refresh, self.btn_exit]:
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["AcCode", "AcName", "GroupCode", "OpBalance", "DrCr"])
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table)

        self.btn_new.clicked.connect(self._new)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_refresh.clicked.connect(self._load_data)
        self.btn_exit.clicked.connect(self.close)

    def _load_data(self):
        try:
            self._all_rows = fa_ledger_ops.list_ledger()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self._populate_table(self._all_rows)

    def _populate_table(self, rows):
        self.table.setRowCount(len(rows) if rows else 0)
        if not rows:
            return
        for i, rec in enumerate(rows):
            vals = [rec.get("AcCode", ""), rec.get("AcName", ""), rec.get("GroupCode", ""),
                    rec.get("OpBalance", ""), rec.get("DrCr", "")]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setForeground(QColor(_theme.palette()["text"]))
                self.table.setItem(i, j, item)

    def _filter(self, text):
        text = text.strip().lower()
        if not text:
            self._populate_table(self._all_rows)
            return
        filtered = [r for r in self._all_rows if text in str(r.get("AcCode", "")).lower() or text in str(r.get("AcName", "")).lower()]
        self._populate_table(filtered)

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        code = self.table.item(row, 0).text()
        try:
            rec = fa_ledger_ops.get_ledger(code)
        except Exception:
            return
        if rec:
            self.current_code = code
            self.txt_ac_code.setText(str(rec.get("AcCode", "")))
            self.txt_ac_name.setText(str(rec.get("AcName", "")))
            self.txt_group_code.setText(str(rec.get("GroupCode", "")))
            self.txt_op_balance.setText(str(rec.get("OpBalance", "")))
            idx = self.txt_dr_cr.findText(str(rec.get("DrCr", "Dr")))
            if idx >= 0:
                self.txt_dr_cr.setCurrentIndex(idx)
            self.txt_address.setText(str(rec.get("Address", "")))

    def _collect(self):
        return {
            "AcCode": self.txt_ac_code.text().strip(),
            "AcName": self.txt_ac_name.text().strip(),
            "GroupCode": self.txt_group_code.text().strip(),
            "OpBalance": self.txt_op_balance.text().strip(),
            "DrCr": self.txt_dr_cr.currentText(),
            "Address": self.txt_address.text().strip(),
        }

    def _new(self):
        rec = self._collect()
        if not rec["AcCode"]:
            QMessageBox.warning(self, "Validation", "AcCode is required.")
            return
        try:
            fa_ledger_ops.insert_ledger(rec)
            self._load_data()
            QMessageBox.information(self, "Success", "Account created.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _edit(self):
        if not self.current_code:
            QMessageBox.warning(self, "Validation", "Select an account first.")
            return
        rec = self._collect()
        try:
            fa_ledger_ops.update_ledger(self.current_code, rec)
            self._load_data()
            QMessageBox.information(self, "Success", "Account updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_fa_ledger(parent=None):
    win = FaLedgerWindow(parent)
    win.show()
    return win


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FaLedgerWindow()
    win.show()
    sys.exit(app.exec())
