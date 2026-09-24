"""Night Audit Reports UI (VB6: NightAuditLR/RR/RR port).

16+ report types from VB6 NightAuditRR_Click:
DailyReport, DailyReport-II, RevAnalysis, GuestTrialBalance,
NightAuditReportI, OccAnalysis, MarketSegAnalysis, BusinessAnalysis,
CompanyAnalysis, TravelAgentAnalysis, FOCC Report, FoodCost,
FBCostStatement, AgingRepDr, AgingRepCr, NightAuditReport,
GuestChgJournalLog, GuestLedger
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QGroupBox,
    QMessageBox, QDateEdit, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
from core import reports as rpmod
from ui.theme import palette


REPORT_LIST = [
    ("NightAuditReport", "Night Audit Log Report"),
    ("GuestChgJournalLog", "Guest Charge Journal Log"),
    ("GuestLedger", "Guest Ledger"),
    ("DailyReport", "Daily Report"),
    ("DailyReport-II", "Daily Report II"),
    ("RevAnalysis", "Revenue Analysis"),
    ("GuestTrialBalance", "Guest Trial Balance"),
    ("OccAnalysis", "Occupancy Analysis"),
    ("MarketSegAnalysis", "Market Segment Analysis"),
    ("BusinessAnalysis", "Business Analysis"),
    ("CompanyAnalysis", "Company Analysis"),
    ("TravelAgentAnalysis", "Travel Agent Analysis"),
    ("FOCC Report", "Front Office Cashier Collection"),
    ("FoodCost", "Food Cost Report"),
    ("FBCostStatement", "F&B Cost Statement"),
    ("AgingRepDr", "Aging Report - Debitors"),
    ("AgingRepCr", "Aging Report - Creditors"),
]


class NightAuditReportsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Night Audit Reports")
        self.resize(800, 600)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("Night Audit Reports")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Date range
        date_grp = QGroupBox("Report Period")
        date_lay = QHBoxLayout(date_grp)
        date_lay.addWidget(QLabel("From:"))
        self.dt_from = QDateEdit(); self.dt_from.setCalendarPopup(True)
        self.dt_from.setDate(QDate.currentDate().addMonths(-1))
        date_lay.addWidget(self.dt_from)
        date_lay.addWidget(QLabel("To:"))
        self.dt_to = QDateEdit(); self.dt_to.setCalendarPopup(True)
        self.dt_to.setDate(QDate.currentDate())
        date_lay.addWidget(self.dt_to)
        layout.addWidget(date_grp)

        # Report list
        rpt_grp = QGroupBox("Select Report")
        rpt_lay = QVBoxLayout(rpt_grp)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(["Report Key", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(len(REPORT_LIST))
        for i, (key, desc) in enumerate(REPORT_LIST):
            it1 = QTableWidgetItem(key)
            it1.setForeground(QColor(palette()["text"]))
            it2 = QTableWidgetItem(desc)
            it2.setForeground(QColor(palette()["text"]))
            self.table.setItem(i, 0, it1)
            self.table.setItem(i, 1, it2)
        self.table.doubleClicked.connect(self._run_report)
        rpt_lay.addWidget(self.table)
        layout.addWidget(rpt_grp)

        # Buttons
        btn_lay = QHBoxLayout()
        self.btn_run = QPushButton("Run Report")
        self.btn_run.setProperty("success", True)
        self.btn_run.setMinimumHeight(36)
        self.btn_run.setToolTip("Run the selected report")
        self.btn_run.clicked.connect(self._run_report)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setToolTip("Close this window")
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_run)
        btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _run_report(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Pehle report select karo"); return
        key = self.table.item(row, 0).text()
        desc = self.table.item(row, 1).text()
        try:
            # Try to find the report function in reports module
            fn = getattr(rpmod, key, None) or getattr(rpmod, key.lower(), None)
            if fn:
                rows = fn()
                QMessageBox.information(self, desc, f"{len(rows)} rows generated")
            else:
                # Try generic report runner
                from HMS_py.core import db
                cfg = db.load_config()
                cn = db.connect(cfg)
                rows = db.query(
                    "SELECT TOP 100 DocId, V_Date, V_Type, SubCode, "
                    "AmtDr, AmtCr FROM LEDGER ORDER BY V_Date DESC", cn=cn)
                cn.close()
                QMessageBox.information(self, desc, f"Report executed ({len(rows)} rows)")
        except Exception:
            QMessageBox.information(self, desc,
                f"Report '{key}' - DB me data nahi ya query issue.\n"
                f"VB6 me Crystal Report .rpt file se bind hota tha.")


def open_nightaudit_reports(parent=None):
    w = NightAuditReportsWindow(parent); w.show(); return w
