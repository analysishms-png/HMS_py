"""Guest Lookup UI (VB6: GuestLookUp - uses GuestProf table)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QGroupBox, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from HMS_py.core import db
from HMS_py.ui.theme import palette


class GuestLookupWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guest Lookup")
        self.resize(900, 500)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Guest Lookup")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        search_lay = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search by name, phone, or company...")
        self.txt_search.textChanged.connect(self._filter)
        search_lay.addWidget(QLabel("Search:"))
        search_lay.addWidget(self.txt_search)
        layout.addLayout(search_lay)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Name", "Phone", "Address", "City"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_exit = QPushButton("Exit"); btn_exit.clicked.connect(self.close)
        btn_exit.setToolTip("Close this window")
        layout.addWidget(btn_exit)

    def _load_data(self):
        try:
            self._all_rows = db.query(
                "SELECT Code, Name, ISNULL(Phone,''), "
                "ISNULL(Add1,''), ISNULL(City,'') FROM GuestProf ORDER BY Name")
            self._populate(self._all_rows)
        except Exception:
            self._all_rows = []

    def _populate(self, rows):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j in range(5):
                it = QTableWidgetItem(str(r[j] or ""))
                it.setForeground(QColor(palette()["text"]))
                self.table.setItem(i, j, it)

    def _filter(self, text):
        text = text.strip().lower()
        if not text:
            self._populate(self._all_rows); return
        filtered = [r for r in self._all_rows if any(
            text in str(v or "").lower() for v in r)]
        self._populate(filtered)


def open_guest_lookup(parent=None):
    w = GuestLookupWindow(parent); w.show(); return w
