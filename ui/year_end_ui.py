"""Year-End Processing UI (VB6: frmYearEnd.frm port).

Year-end closing workflow for HMS_py. This form is NOT a CRUD master
— it is a process/workflow dialog that:
  1. Displays the current financial year dates
  2. Shows a year-end summary (balances, counts, vouchers)
  3. Checks the DATELOCK status before any operation
  4. Executes year-end procedures: carry-forward balances, reset budget

Run: python -m HMS_py.ui.year_end_ui
Menu: Finance -> "Year End Updation" (VB6 Finance leaf)

Tables operated on (core/year_end.py):
  - SubGroupCurrBal, ACGroupCurrBal, LastVoucher, Budget, DATELOCK
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel,
                              QMessageBox, QPushButton,
                              QTableWidget, QTableWidgetItem,
                              QVBoxLayout, QWidget)

from HMS_py.core import year_end as ye
from HMS_py.core import db
from HMS_py.ui import theme as _theme

# PYT guard prefix — test records only, production data protected
PYT_PREFIX = "PYT"


def _cell(val) -> QTableWidgetItem:
    """Create a read-only QTableWidgetItem from a value."""
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


def _dark_cell(val, readonly: bool = True) -> QTableWidgetItem:
    """Create a dark-styled QTableWidgetItem."""
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    if readonly:
        it.setBackground(QColor(_theme.palette()["glass_tint"]))
    return it


class YearEndForm(QDialog):
    """Year-End Processing workflow dialog (VB6 frmYearEnd.frm).

    Displays financial year dates, summary balances, date-lock status,
    and executes year-end procedures (carry-forward + budget reset).
    """

    COLS_SUMMARY = ["FY", "SubGroups", "Total DR", "Total CR",
                    "Balance", "ACGroups", "LastVouchers"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Year-End Processing - HMS_py")
        self.resize(820, 640)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 12, 16, 12)

        # ── Title ──
        title = QLabel("Year-End Processing")
        title.setFont(__import__("PyQt6").QtGui.QFont("Arial", 13,
                               __import__("PyQt6").QtGui.QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── FY Dates section ──
        fy_grp = __import__("PyQt6").QtWidgets.QGroupBox("Financial Year")
        fy_lay = QHBoxLayout(fy_grp)
        self.lbl_fy = QLabel("Loading...")
        self.lbl_fy.setFont(__import__("PyQt6").QtGui.QFont("Arial", 11,
                                __import__("PyQt6").QtGui.QFont.Weight.Bold))
        fy_lay.addWidget(self.lbl_fy)
        fy_lay.addStretch(1)
        self.btn_refresh_fy = QPushButton("Refresh FY (F5)")
        self.btn_refresh_fy.setToolTip("Reload financial year dates")
        self.btn_refresh_fy.clicked.connect(self._refresh_fy)
        fy_lay.addWidget(self.btn_refresh_fy)
        root.addWidget(fy_grp)

        # ── Summary table ──
        sum_grp = __import__("PyQt6").QtWidgets.QGroupBox("Year-End Summary")
        sum_lay = QVBoxLayout(sum_grp)
        self.tbl_summary = QTableWidget(0, len(self.COLS_SUMMARY))
        self.tbl_summary.setHorizontalHeaderLabels(self.COLS_SUMMARY)
        self.tbl_summary.setAlternatingRowColors(True)
        self.tbl_summary.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_summary.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_summary.horizontalHeader().setStretchLastSection(True)
        sum_lay.addWidget(self.tbl_summary)
        root.addWidget(sum_grp, stretch=1)

        # ── Status / Log section ──
        log_grp = __import__("PyQt6").QtWidgets.QGroupBox("Operation Log")
        log_lay = QVBoxLayout(log_grp)
        self.lbl_log = QLabel("Ready. Select actions below.")
        self.lbl_log.setWordWrap(True)
        log_lay.addWidget(self.lbl_log)
        root.addWidget(log_grp)

        # ── Button bar ──
        btn_grp = __import__("PyQt6").QtWidgets.QGroupBox()
        btn_lay = QHBoxLayout(btn_grp)
        btn_lay.setSpacing(8)

        self.btn_check_lock = QPushButton("  Check DateLock (Ctrl+L)")
        self.btn_check_lock.setToolTip("Check if dates are locked")

        self.btn_carry_fwd = QPushButton("  Carry Forward Balances (Ctrl+C)")
        self.btn_carry_fwd.setToolTip("Carry forward balances to new FY")

        self.btn_reset_budget = QPushButton("  Reset Budget (Ctrl+B)")
        self.btn_reset_budget.setToolTip("Reset budget for new FY")

        self.btn_execute = QPushButton("  Execute Year-End (Ctrl+E)")
        self.btn_execute.setProperty("accent", True)
        self.btn_execute.setToolTip("Execute full year-end procedure")

        self.btn_summary = QPushButton("  Load Summary (Ctrl+S)")
        self.btn_summary.setToolTip("Load year-end summary")

        self.btn_close = QPushButton("  Close (Esc)")

        for b in (self.btn_check_lock, self.btn_carry_fwd,
                   self.btn_reset_budget, self.btn_execute,
                   self.btn_summary, self.btn_close):
            btn_lay.addWidget(b)
        btn_lay.addStretch()
        root.addWidget(btn_grp)

        # ── Status bar ──
        self.lbl_state = QLabel("Ready")
        self.lbl_state.setStyleSheet(
            f"font-size: 11px; color: {_theme.palette().get('text_dim', '#64748b')}; "
            f"padding: 4px 0; border-top: 1px solid {_theme.palette().get('border', '#ccc')};"
        )
        root.addWidget(self.lbl_state)

        # ── Signals ──
        self.btn_check_lock.clicked.connect(self._on_check_lock)
        self.btn_carry_fwd.clicked.connect(self._on_carry_forward)
        self.btn_reset_budget.clicked.connect(self._on_reset_budget)
        self.btn_execute.clicked.connect(self._on_execute_year_end)
        self.btn_summary.clicked.connect(self._on_load_summary)
        self.btn_close.clicked.connect(self.reject)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._on_check_lock)
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._on_carry_forward)
        QShortcut(QKeySequence("Ctrl+B"), self, activated=self._on_reset_budget)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._on_execute_year_end)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_load_summary)
        QShortcut(QKeySequence("Escape"), self, activated=self.reject)
        QShortcut(QKeySequence("F5"), self, activated=self._refresh_fy)

        # ── Initial load ──
        self._refresh_fy()

    # ── Data helpers ──────────────────────────────────────────────

    def _set_state(self, text: str, color: str = "#64748b"):
        """Update the status bar label."""
        self.lbl_state.setText(f"  {text}")
        self.lbl_state.setStyleSheet(
            f"font-size: 11px; color: {color}; padding: 4px 0; "
            f"border-top: 1px solid {_theme.palette().get('border', '#ccc')};"
        )

    def _refresh_fy(self):
        """Refresh the financial year date display."""
        try:
            fy = ye.get_fy_dates()
            self.lbl_fy.setText(
                f"Current FY: {fy['fy']}  |  "
                f"From: {fy['start']}  |  To: {fy['end']}")
        except Exception as e:
            self.lbl_fy.setText(f"Error loading FY dates: {e}")
        self._set_state("FY dates refreshed")

    def _on_load_summary(self):
        """Load and display the year-end summary (alias for button)."""
        self._load_summary()

    def _load_summary(self):
        """Load and display the year-end summary."""
        try:
            summary = ye.year_end_summary()
            fy = summary["fy"]
            self.tbl_summary.setRowCount(1)
            row = 0
            values = [
                fy["fy"],
                str(summary["subgroup_count"]),
                f"{summary['total_dr']:.2f}",
                f"{summary['total_cr']:.2f}",
                f"{summary['balance']:.2f}",
                str(summary["acgroup_count"]),
                str(len(summary["last_vouchers"])),
            ]
            for c, val in enumerate(values):
                self.tbl_summary.setItem(row, c, _cell(val))
            self.tbl_summary.selectRow(0)
            self._set_state("Summary loaded — FY: " + fy["fy"], "#059669")
        except Exception as e:
            QMessageBox.critical(self, "Year-End Summary",
                                  f"Unable to load summary: {e}")
            self._set_state("Summary load failed", "#dc2626")

    # ── Action handlers ──────────────────────────────────────────

    def _on_check_lock(self):
        """Check if the current date is locked (DATELOCK check)."""
        try:
            import datetime
            today = datetime.date.today()
            locked = ye.check_datelock(today)
            if locked:
                self.lbl_log.setText(
                    f"[LOCKED] Date {today} is currently locked. "
                    "Year-end processing cannot proceed.")
                self._set_state("Date is LOCKED — abort", "#dc2626")
                self.lbl_log.setStyleSheet(
                    f"color: #dc2626; font-weight: bold;")
            else:
                self.lbl_log.setText(
                    f"[OK] Date {today} is NOT locked. "
                    "Year-end processing can proceed.")
                self._set_state("Date is NOT locked — proceed", "#059669")
                self.lbl_log.setStyleSheet(
                    f"color: #059669; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "DateLock Check",
                                  f"Unable to check datelock: {e}")
            self._set_state("Datelock check failed", "#dc2626")

    def _on_carry_forward(self):
        """Execute balance carry-forward to new financial year."""
        fy = ye.get_fy_dates()
        new_fy_start = fy["start"].isoformat()
        try:
            reply = QMessageBox.question(
                self, "Confirm Carry Forward",
                f"Carry forward balances to new FY starting {new_fy_start}?\n\n"
                "This will update SubGroupCurrBal, ACGroupCurrBal, "
                "and LastVoucher.\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            result = ye.carry_forward_balances(new_fy_start, commit=True)
            self.lbl_log.setText(
                f"[CARRY FORWARD] Complete — "
                f"SubGroupCurrBal updated: {result['subgroup_updated']}, "
                f"ACGroupCurrBal updated: {result['acgroup_updated']}")
            self._set_state("Carry forward complete", "#059669")
        except Exception as e:
            QMessageBox.critical(self, "Carry Forward",
                                  f"Unable to carry forward balances: {e}")
            self._set_state("Carry forward failed", "#dc2626")

    def _on_reset_budget(self):
        """Reset budget for the new financial year."""
        fy = ye.get_fy_dates()
        new_fy_start = fy["start"].isoformat()
        new_fy_end = fy["end"].isoformat()
        try:
            reply = QMessageBox.question(
                self, "Confirm Budget Reset",
                f"Reset budget for FY {fy['fy']} ({new_fy_start} to {new_fy_end})?\n\n"
                "Existing budget will be deleted and re-inserted with new dates.\n\n"
                "This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            count = ye.reset_budget(new_fy_start, new_fy_end, commit=True)
            self.lbl_log.setText(
                f"[BUDGET RESET] Complete — {count} budget records reset.")
            self._set_state("Budget reset complete", "#059669")
        except Exception as e:
            QMessageBox.critical(self, "Budget Reset",
                                  f"Unable to reset budget: {e}")
            self._set_state("Budget reset failed", "#dc2626")

    def _on_execute_year_end(self):
        """Execute the full year-end procedure.

        Steps:
        1. Check DATELOCK
        2. Carry forward balances
        3. Reset budget
        """
        try:
            # Step 1: Check date lock
            import datetime
            today = datetime.date.today()
            if ye.check_datelock(today):
                QMessageBox.warning(self, "Year-End Blocked",
                                     f"Date {today} is locked. "
                                     "Cannot proceed with year-end.")
                self._set_state("Year-end blocked by datelock", "#dc2626")
                return

            fy = ye.get_fy_dates()
            new_fy_start = fy["start"].isoformat()

            # Step 2: Carry forward balances
            self.lbl_log.setText("Step 1/2: Carrying forward balances...")
            self._set_state("Executing year-end...", "#d97706")
            result = ye.carry_forward_balances(new_fy_start, commit=True)

            # Step 3: Reset budget
            self.lbl_log.setText("Step 2/2: Resetting budget...")
            count = ye.reset_budget(new_fy_start, fy["end"].isoformat(),
                                     commit=True)

            self.lbl_log.setText(
                f"[YEAR-END COMPLETE] FY {fy['fy']}\n"
                f"  SubGroupCurrBal updated: {result['subgroup_updated']}\n"
                f"  ACGroupCurrBal updated: {result['acgroup_updated']}\n"
                f"  Budget records reset: {count}")
            self._set_state("Year-end procedure complete", "#059669")
            self.lbl_log.setStyleSheet(
                f"color: #059669; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Year-End Execution",
                                  f"Year-end procedure failed: {e}")
            self._set_state("Year-end execution failed", "#dc2626")


def open_year_end(parent=None):
    """Shell opener for 'Year End Updation' leaf."""
    w = YearEndForm(parent)
    w.exec()
    return w


# ── Standalone launcher ───────────────────────────────────────
class YearEndLauncher(QWidget):
    """Standalone launcher for Year-End Processing."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Year-End Processing - HMS_py")
        self.resize(400, 200)
        lay = QVBoxLayout(self)
        btn = QPushButton("Open Year-End Processing")
        btn.clicked.connect(lambda: YearEndForm(self).exec())
        btn.setToolTip("Open the Year-End Processing form")
        lay.addWidget(btn)
        self.setLayout(lay)


def main() -> int:
    """Standalone entry point for testing."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = YearEndLauncher()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
