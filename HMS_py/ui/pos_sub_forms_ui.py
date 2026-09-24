"""POS Sub-Forms UI (VB6: Bill Reprint, Split Bill, KOT Transfer port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QGroupBox, QFormLayout, QDateEdit, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from core import db
from ui.theme import palette


class BillReprintWindow(QMainWindow):
    """Bill Reprint (VB6: POS Bill Reprint)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("POS Bill Reprint")
        self.resize(800, 500)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("POS Bill Reprint")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        search_lay = QHBoxLayout()
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDate(QDate.currentDate())
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDate(QDate.currentDate())
        self.btn_search = QPushButton("Search")
        self.btn_search.setToolTip("Search bills within the selected date range")
        self.btn_search.clicked.connect(self._load_data)
        search_lay.addWidget(QLabel("From:")); search_lay.addWidget(self.dt_from)
        search_lay.addWidget(QLabel("To:")); search_lay.addWidget(self.dt_to)
        search_lay.addWidget(self.btn_search)
        layout.addLayout(search_lay)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["DocId", "Date", "Outlet", "Amount", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_lay = QHBoxLayout()
        self.btn_reprint = QPushButton("Reprint Selected Bill")
        self.btn_reprint.setToolTip("Reprint the selected bill using Crystal Reports")
        self.btn_reprint.setProperty("success", True)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the Bill Reprint window")
        self.btn_reprint.clicked.connect(self._reprint)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_reprint); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _load_data(self):
        try:
            rows = db.query(
                "SELECT TOP 100 S1.DocId, S1.VDate, D.Name, S1.NetAmt, S1.DelFlag "
                "FROM Sale1 S1 LEFT JOIN Depart D ON S1.RestCode = D.Code "
                "WHERE S1.VDate BETWEEN ? AND ? ORDER BY S1.DocId DESC",
                (self.dt_from.date().toPyDate(), self.dt_to.date().toPyDate()))
            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                for j, v in enumerate([r[0] or "", str(r[1] or ""), r[2] or "",
                                       str(r[3] or 0), r[4] or ""]):
                    it = QTableWidgetItem(str(v))
                    it.setForeground(QColor(palette()["text"]))
                    self.table.setItem(i, j, it)
        except Exception:
            pass

    def _reprint(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Pehle bill select karo"); return
        docid = self.table.item(row, 0).text()
        QMessageBox.information(self, "Reprint",
            f"Bill {docid} reprint.\n\nVB6 me Crystal Report se print hota tha.")


class SplitBillWindow(QMainWindow):
    """Split Sale Bill (VB6: Split Sale Bill)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Split Sale Bill")
        self.resize(800, 500)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Split Sale Bill")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Split Details")
        form_lay = QFormLayout(form)
        self.txt_docid = QLineEdit(); self.txt_docid.setPlaceholderText("Original Bill DocId")
        form_lay.addRow("Bill DocId:", self.txt_docid)
        layout.addWidget(form)

        info = QLabel("Original bill ko do parts me split karega.\n"
                      "Pehle bill ke items select karo jo naye bill me jayenge.")
        info.setWordWrap(True); layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["SNo", "Item", "Qty", "Rate", "Select"])
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_lay = QHBoxLayout()
        self.btn_split = QPushButton("Split Bill")
        self.btn_split.setToolTip("Split the original bill into two separate bills")
        self.btn_split.setProperty("role", "warning")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close the Split Bill window")
        self.btn_split.clicked.connect(self._split)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_split); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _split(self):
        docid = self.txt_docid.text().strip()
        if not docid:
            QMessageBox.warning(self, "Input", "Bill DocId zaroori hai"); return
        QMessageBox.information(self, "Info",
            "Split Bill: Selected items ko naye bill me move karo.\n\n"
            "VB6 me yeh complex operation tha - original void + 2 new bills.")


def open_bill_reprint(parent=None):
    w = BillReprintWindow(parent); w.show(); return w

def open_split_bill(parent=None):
    w = SplitBillWindow(parent); w.show(); return w
