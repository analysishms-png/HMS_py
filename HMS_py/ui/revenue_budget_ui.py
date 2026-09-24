"""Revenue Group + Budget Entry UI (VB6: RevenueGroup + BudgetEntry port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QComboBox, QMessageBox, QGroupBox, QFormLayout, QDateEdit, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from HMS_py.core import revenue_budget as rb
from HMS_py.ui.theme import palette


class RevenueBudgetWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Revenue Group & Budget Entry")
        self.resize(800, 600)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("Revenue Group Setting & Budget Entry")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        tabs = QTabWidget()

        # Revenue Group tab
        rg_widget = QWidget()
        rg_layout = QVBoxLayout(rg_widget)
        rg_form = QGroupBox("Revenue Group")
        rg_flay = QFormLayout(rg_form)
        self.txt_revcode = QLineEdit()
        self.txt_revcode.setPlaceholderText("Revenue code")
        self.txt_revname = QLineEdit()
        self.txt_revname.setPlaceholderText("Revenue name")
        self.txt_grpcode = QLineEdit()
        self.txt_grpcode.setPlaceholderText("Group code")
        rg_flay.addRow("Rev Code:", self.txt_revcode)
        rg_flay.addRow("Rev Name:", self.txt_revname)
        rg_flay.addRow("Group Code:", self.txt_grpcode)
        rg_layout.addWidget(rg_form)

        rg_btns = QHBoxLayout()
        self.btn_rg_add = QPushButton("Add")
        self.btn_rg_add.setToolTip("Add new revenue group")
        self.btn_rg_del = QPushButton("Delete")
        self.btn_rg_del.setToolTip("Delete selected revenue group")
        self.btn_rg_add.clicked.connect(self._add_rev_group)
        self.btn_rg_del.clicked.connect(self._del_rev_group)
        rg_btns.addWidget(self.btn_rg_add)
        rg_btns.addWidget(self.btn_rg_del)
        rg_layout.addLayout(rg_btns)

        self.rg_table = QTableWidget()
        self.rg_table.setColumnCount(4)
        self.rg_table.setAlternatingRowColors(True)
        self.rg_table.setHorizontalHeaderLabels(
            ["Rev Code", "Rev Name", "Group Code", "Nature"])
        rg_layout.addWidget(self.rg_table)
        tabs.addTab(rg_widget, "Revenue Group")

        # Budget tab
        bg_widget = QWidget()
        bg_layout = QVBoxLayout(bg_widget)
        bg_form = QGroupBox("Budget Entry")
        bg_flay = QFormLayout(bg_form)
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDate(QDate.currentDate())
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDate(QDate.currentDate().addYears(1))
        self.txt_bgrp = QLineEdit()
        self.txt_bgrp.setPlaceholderText("Group code")
        self.txt_bamt = QLineEdit()
        self.txt_bamt.setPlaceholderText("e.g. 500000")
        bg_flay.addRow("From Date:", self.dt_from)
        bg_flay.addRow("To Date:", self.dt_to)
        bg_flay.addRow("Group Code:", self.txt_bgrp)
        bg_flay.addRow("Amount:", self.txt_bamt)
        bg_layout.addWidget(bg_form)

        bg_btns = QHBoxLayout()
        self.btn_bg_add = QPushButton("Add")
        self.btn_bg_add.setToolTip("Add new budget entry")
        self.btn_bg_del = QPushButton("Delete")
        self.btn_bg_del.setToolTip("Delete selected budget entry")
        self.btn_bg_add.clicked.connect(self._add_budget)
        self.btn_bg_del.clicked.connect(self._del_budget)
        bg_btns.addWidget(self.btn_bg_add)
        bg_btns.addWidget(self.btn_bg_del)
        bg_layout.addLayout(bg_btns)

        self.bg_table = QTableWidget()
        self.bg_table.setColumnCount(5)
        self.bg_table.setAlternatingRowColors(True)
        self.bg_table.setHorizontalHeaderLabels(
            ["From", "To", "SrNo", "Group", "Amount"])
        bg_layout.addWidget(self.bg_table)
        tabs.addTab(bg_widget, "Budget Entry")

        layout.addWidget(tabs)

        btn_exit = QPushButton("Exit")
        btn_exit.setToolTip("Close this window")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

    def _load_data(self):
        try:
            rows = rb.revenue_group_list()
            self.rg_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate([r["rev_code"], r["rev_name"],
                                       r["group_code"], r["group_nature"]]):
                    it = QTableWidgetItem(str(v))
                    it.setForeground(QColor(palette()["text"]))
                    self.rg_table.setItem(i, j, it)
        except Exception:
            pass
        try:
            rows = rb.budget_list()
            self.bg_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate([str(r["from_date"]), str(r["to_date"]),
                                       str(r["sr_no"]), r["group_code"],
                                       str(r["amount"])]):
                    it = QTableWidgetItem(v)
                    it.setForeground(QColor(palette()["text"]))
                    self.bg_table.setItem(i, j, it)
        except Exception:
            pass

    def _add_rev_group(self):
        code = self.txt_revcode.text().strip()
        if not code:
            QMessageBox.warning(self, "Input", "Rev Code zaroori hai"); return
        try:
            rb.revenue_group_insert({
                "rev_code": code,
                "rev_name": self.txt_revname.text().strip(),
                "group_code": self.txt_grpcode.text().strip(),
            })
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _del_rev_group(self):
        row = self.rg_table.currentRow()
        if row < 0: return
        code = self.rg_table.item(row, 0).text()
        try:
            rb.revenue_group_delete(code)
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _add_budget(self):
        grp = self.txt_bgrp.text().strip()
        if not grp:
            QMessageBox.warning(self, "Input", "Group Code zaroori hai"); return
        try:
            amt = float(self.txt_bamt.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Input", "Amount invalid"); return
        try:
            rb.budget_insert({
                "from_date": self.dt_from.date().toPyDate(),
                "to_date": self.dt_to.date().toPyDate(),
                "group_code": grp, "amount": amt,
                "sr_no": self.bg_table.rowCount() + 1,
            })
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _del_budget(self):
        row = self.bg_table.currentRow()
        if row < 0: return
        try:
            from_date = self.bg_table.item(row, 0).text()
            to_date = self.bg_table.item(row, 1).text()
            sr_no = int(self.bg_table.item(row, 2).text())
            rb.budget_delete(from_date, to_date, sr_no)
            self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_revenue_budget(parent=None):
    w = RevenueBudgetWindow(parent); w.show(); return w
