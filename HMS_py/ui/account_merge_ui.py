"""Account Merging UI (VB6: AccountMerg port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QGroupBox, QFormLayout, QMessageBox,
    QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from HMS_py.core import account_merge
from HMS_py.core import ledger as led


class AccountMergeWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Account Merging")
        self.resize(700, 500)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Merge Duplicate Ledger Accounts")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Merge Details")
        form_lay = QFormLayout(form)
        self.txt_old = QLineEdit()
        self.txt_old.setPlaceholderText("Old SubCode (to merge FROM)")
        self.txt_new = QLineEdit()
        self.txt_new.setPlaceholderText("New SubCode (to merge INTO)")
        form_lay.addRow("Old Code:", self.txt_old)
        form_lay.addRow("New Code:", self.txt_new)
        layout.addWidget(form)

        btn_lay = QHBoxLayout()
        self.btn_preview = QPushButton("Preview")
        self.btn_preview.setToolTip("Preview which records will be merged")
        self.btn_preview.clicked.connect(self._preview)
        self.btn_merge = QPushButton("MERGE")
        self.btn_merge.setToolTip("Merge old account into new account (irreversible!)")
        self.btn_merge.setStyleSheet(
            "QPushButton{background:#dc3545;color:white;font-weight:bold;padding:8px;}")
        self.btn_merge.clicked.connect(self._merge)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_preview)
        btn_lay.addWidget(self.btn_merge)
        btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

        prev_grp = QGroupBox("Preview Results")
        prev_lay = QVBoxLayout(prev_grp)
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(2)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setHorizontalHeaderLabels(["Table", "Records to Merge"])
        prev_lay.addWidget(self.preview_table)
        layout.addWidget(prev_grp)

    def _preview(self):
        old = self.txt_old.text().strip()
        new = self.txt_new.text().strip()
        if not old or not new:
            QMessageBox.warning(self, "Input", "Dono codes zaroori hain")
            return
        try:
            result = account_merge.preview_merge(old, new)
            counts = result.get("counts", {})
            self.preview_table.setRowCount(len(counts))
            for i, (tbl, cnt) in enumerate(counts.items()):
                self.preview_table.setItem(i, 0, QTableWidgetItem(tbl))
                self.preview_table.setItem(i, 1, QTableWidgetItem(str(cnt)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _merge(self):
        old = self.txt_old.text().strip()
        new = self.txt_new.text().strip()
        if not old or not new:
            QMessageBox.warning(self, "Input", "Dono codes zaroori hain")
            return
        reply = QMessageBox.question(
            self, "Confirm",
            f"Merge {old} -> {new}?\nYeh undo nahi ho sakta!")
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            result = account_merge.merge_accounts(old, new)
            QMessageBox.information(
                self, "Merged",
                f"Records updated: {result['records_updated']}\n"
                f"{result['merged']} -> {result['into']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_account_merge(parent=None):
    w = AccountMergeWindow(parent); w.show(); return w
