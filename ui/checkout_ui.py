"""Check-Out UI (VB6: Front Office -> Check-Out / Reverse Check-Out).

VB6 pattern (RsFolioEntry.frm):
  - Active folios grid (FolioNo, Guest, Arrival, Departure, Balance)
  - Select folio -> show charges breakdown -> Check-Out button
  - Reverse Check-Out: reopen checked-out folio
  - Balance shown prominently (Dr - Cr from PayCharge)
  - PYT-guard: production check-outs VB6 EXE se; test-only writes

Run: python -m HMS_py.ui.checkout_ui
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QSplitter,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget, QTabWidget)

from HMS_py.core import checkout, expenseentry
from HMS_py.ui import theme as _theme


def _cell(val) -> QTableWidgetItem:
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%Y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


def _red_cell(val) -> QTableWidgetItem:
    it = _cell(val)
    it.setForeground(QColor(_theme.status_colors()["danger_text"]))
    return it


def _green_cell(val) -> QTableWidgetItem:
    it = _cell(val)
    it.setForeground(QColor(_theme.status_colors()["success_text"]))
    return it


class CheckOutBrowser(QDialog):
    """VB6 Check-Out screen:
    Top: active folio list | Bottom: folio charges detail + balance.
    Actions: Check-Out (PYT* only), Reverse Check-Out, Refresh.
    """

    FOLIO_COLS = ["FolioNo", "Guest Name", "GuestProf", "City",
                  "Departure", "Days", "Status"]
    CHARGE_COLS = ["VType", "VNo", "PayCode", "Amount",
                   "Dr (Charge)", "Cr (Payment)", "Remarks"]

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Check-Out Browser - HMS_py")
        self.resize(1100, 650)

        root = QVBoxLayout(self)

        # ---- Tab: Active / Checked-Out ----
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # Tab 1: Active folios
        tab_active = QWidget()
        lay_active = QVBoxLayout(tab_active)
        self.tbl_active = QTableWidget(0, len(self.FOLIO_COLS))
        self.tbl_active.setHorizontalHeaderLabels(self.FOLIO_COLS)
        self.tbl_active.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_active.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_active.horizontalHeader().setStretchLastSection(True)
        self.tbl_active.setAlternatingRowColors(True)
        self.tbl_active.cellClicked.connect(lambda *_: self._load_charges())
        self.tbl_active.cellDoubleClicked.connect(
            lambda *_: self._do_checkout())
        lay_active.addWidget(self.tbl_active)

        self.lblBal = QLabel("Balance: ---")
        f = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self.lblBal.setFont(f)
        lay_active.addWidget(self.lblBal)

        self.tbl_charges = QTableWidget(0, len(self.CHARGE_COLS))
        self.tbl_charges.setHorizontalHeaderLabels(self.CHARGE_COLS)
        self.tbl_charges.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_charges.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_charges.horizontalHeader().setStretchLastSection(True)
        self.tbl_charges.setMaximumHeight(200)
        self.tbl_charges.setAlternatingRowColors(True)
        lay_active.addWidget(self.tbl_charges)

        btns_active = QHBoxLayout()
        btns_active.setSpacing(8)
        self.btnCheckOut = QPushButton("Check-Out (PYT*)")
        self.btnCheckOut.setToolTip("Check-out selected folio (PYT* test only, Ctrl+O)")
        self.btnCheckOut.setProperty("role", "danger")
        self.btnCheckOut.setMinimumHeight(34)
        self.btnRefreshA = QPushButton("Refresh (F5)")
        self.btnRefreshA.setToolTip("Reload active folio list (F5)")
        self.btnRefreshA.setMinimumHeight(34)
        self.btnCloseA = QPushButton("Close")
        self.btnCloseA.setToolTip("Close this window (Esc)")
        self.btnCloseA.setMinimumHeight(34)
        for b in (self.btnCheckOut, self.btnRefreshA, self.btnCloseA):
            btns_active.addWidget(b)
        lay_active.addLayout(btns_active)
        self.tabs.addTab(tab_active, "Active Check-Ins")

        # Tab 2: Checked-Out folios (Reverse)
        tab_co = QWidget()
        lay_co = QVBoxLayout(tab_co)
        self.tbl_co = QTableWidget(0, 6)
        self.tbl_co.setHorizontalHeaderLabels(
            ["FolioNo", "Guest Name", "Departure",
             "Check-Out Date", "By User", "DocId"])
        self.tbl_co.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_co.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_co.horizontalHeader().setStretchLastSection(True)
        self.tbl_co.setAlternatingRowColors(True)
        lay_co.addWidget(self.tbl_co)

        btns_co = QHBoxLayout()
        btns_co.setSpacing(8)
        self.btnReverse = QPushButton("Reverse Check-Out (PYT*)")
        self.btnReverse.setToolTip("Reverse check-out for selected folio (PYT* only, Ctrl+R)")
        self.btnReverse.setProperty("role", "warning")
        self.btnReverse.setMinimumHeight(34)
        self.btnRefreshCO = QPushButton("Refresh (F5)")
        self.btnRefreshCO.setToolTip("Reload checked-out folio list (F5)")
        self.btnRefreshCO.setMinimumHeight(34)
        self.btnCloseCO = QPushButton("Close")
        self.btnCloseCO.setToolTip("Close this window (Esc)")
        self.btnCloseCO.setMinimumHeight(34)
        for b in (self.btnReverse, self.btnRefreshCO, self.btnCloseCO):
            btns_co.addWidget(b)
        lay_co.addLayout(btns_co)
        self.tabs.addTab(tab_co, "Checked-Out Folios")

        # ---- signal wiring ----
        self.btnCheckOut.clicked.connect(self._do_checkout)
        self.btnRefreshA.clicked.connect(self.reload_active)
        self.btnCloseA.clicked.connect(self.reject)
        self.btnReverse.clicked.connect(self._do_reverse)
        self.btnRefreshCO.clicked.connect(self.reload_checkedout)
        self.btnCloseCO.clicked.connect(self.reject)

        QShortcut(QKeySequence("F5"), self,
                  activated=lambda: (self.reload_active(),
                                     self.reload_checkedout()))
        QShortcut(QKeySequence("Ctrl+O"), self,
                  activated=self._do_checkout)
        QShortcut(QKeySequence("Ctrl+R"), self,
                  activated=self._do_reverse)

        self.reload_active()
        self.reload_checkedout()

    # ---- data loaders ----
    def reload_active(self, keep_folio: int | None = None):
        rows = checkout.list_active_folios()
        self.tbl_active.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            status = "Checked-Out" if rec.get("checkout_date") else "In-House"
            vals = [rec["folio"], rec["name"], rec["guestprof"],
                    rec["city"], rec["depdate"], rec["nodays"],
                    status]
            for c, v in enumerate(vals):
                self.tbl_active.setItem(r, c, _cell(v))
        if keep_folio:
            for r, rec in enumerate(rows):
                if rec["folio"] == keep_folio:
                    self.tbl_active.selectRow(r)
                    return
        if rows:
            self.tbl_active.selectRow(0)
            self._load_charges()

    def reload_checkedout(self):
        rows = checkout.list_checked_out()
        self.tbl_co.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            vals = [rec["folio"], rec["name"], rec["depdate"],
                    rec["checkout_date"], rec["checkout_user"], rec["docid"]]
            for c, v in enumerate(vals):
                self.tbl_co.setItem(r, c, _cell(v))
        if rows:
            self.tbl_co.selectRow(0)

    def _load_charges(self):
        folio = self._selected_active_folio()
        if not folio:
            return
        try:
            bal = checkout.folio_balance(folio)
            b = bal["balance"]
            status = "OUTSTANDING" if b > 0 else "SETTLED" if b == 0 else "OVERPAID"
            self.lblBal.setText(
                f"Folio #{folio}  |  Guest: {bal['name']}  |  "
                f"Charges: {bal['charges_dr']:>12,.2f}  |  "
                f"Payments: {bal['payments_cr']:>12,.2f}  |  "
                f"Balance: {b:>12,.2f}  [{status}]")
            st = _theme.status_colors()
            self.lblBal.setStyleSheet(
                f"color:{st['danger_text']}; font-weight:bold;" if b > 0
                else f"color:{st['success_text']}; font-weight:bold;")

            charges = expenseentry.list_folio_charges(folio)
            self.tbl_charges.setRowCount(len(charges))
            for r, ch in enumerate(charges):
                vals = [ch["vtype"], ch["vno"], ch["paycode"],
                        f"{ch['amount']:.2f}",
                        f"{ch['amt_dr']:.2f}" if ch["amt_dr"] else "",
                        f"{ch['amt_cr']:.2f}" if ch["amt_cr"] else "",
                        ch["remarks"]]
                for c, v in enumerate(vals):
                    it = (_red_cell(v) if c == 4 and ch["amt_dr"] > 0
                          else _green_cell(v) if c == 5 and ch["amt_cr"] > 0
                          else _cell(v))
                    self.tbl_charges.setItem(r, c, it)
        except Exception as e:
            self.lblBal.setText(f"Balance load error: {e}")

    # ---- selected helpers ----
    def _selected_active_folio(self) -> int | None:
        # BUG-024 fix: currentRow() -1 ho to bhi item access safe rakho +
        # non-numeric folio text pe crash guard
        r = self.tbl_active.currentRow()
        if r < 0:
            return None
        item = self.tbl_active.item(r, 0)
        if not item or not item.text().strip():
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def _selected_co_folio(self) -> int | None:
        r = self.tbl_co.currentRow()
        if r < 0:
            return None
        item = self.tbl_co.item(r, 0)
        if not item or not item.text().strip():
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    # ---- actions ----
    def _do_checkout(self):
        folio = self._selected_active_folio()
        if not folio:
            QMessageBox.information(
                self, "Check-Out", "Pehle folio select karo")
            return
        # PYT-guard check (BUG-024 fix: r >= 0 kaafi nahi - item bhi None ho
        # sakta hai jab row ka cell khali/missing ho)
        r = self.tbl_active.currentRow()
        guest = ""
        if r >= 0:
            guest_item = self.tbl_active.item(r, 1)
            guest = guest_item.text() if guest_item else ""
        if not guest.upper().startswith("PYT"):
            QMessageBox.warning(
                self, "Check-Out",
                "Safety: sirf PYT* test folios check-out ho sakte hain\n"
                "(Production check-outs VB6 EXE se karo)")
            return
        try:
            bal = checkout.folio_balance(folio)
        except Exception as e:
            QMessageBox.critical(self, "Check-Out", str(e))
            return

        msg = (f"Folio #{folio} - {bal['name']}\n\n"
               f"Charges:  ₹{bal['charges_dr']:.2f}\n"
               f"Payments: ₹{bal['payments_cr']:.2f}\n"
               f"Balance:  ₹{bal['balance']:.2f}\n\n")
        if bal["balance"] > 0:
            msg += f"⚠ Outstanding balance ₹{bal['balance']:.2f} hai!\n\n"
        msg += "Check-Out confirm karein?"

        if QMessageBox.question(
                self, "Confirm Check-Out", msg) != \
                QMessageBox.StandardButton.Yes:
            return
        try:
            checkout.do_checkout(folio, user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Check-Out", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Check-Out", f"DB error: {e}")
            return
        QMessageBox.information(
            self, "Check-Out",
            f"Folio #{folio} check-out ho gaya!")
        self.reload_active()
        self.reload_checkedout()

    def _do_reverse(self):
        folio = self._selected_co_folio()
        if not folio:
            QMessageBox.information(
                self, "Reverse", "Pehle folio select karo")
            return
        r = self.tbl_co.currentRow()
        guest = ""
        if r >= 0:
            guest_item = self.tbl_co.item(r, 1)
            guest = guest_item.text() if guest_item else ""
        if not guest.upper().startswith("PYT"):
            QMessageBox.warning(
                self, "Reverse Check-Out",
                "Safety: sirf PYT* test folios reverse ho sakte hain")
            return
        if QMessageBox.question(
                self, "Reverse Check-Out",
                f"Folio #{folio} - {guest}\nReverse check-out karein?") != \
                QMessageBox.StandardButton.Yes:
            return
        try:
            checkout.reverse_checkout(folio, user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Reverse", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Reverse", f"DB error: {e}")
            return
        QMessageBox.information(
            self, "Reverse Check-Out",
            f"Folio #{folio} reopen ho gaya (In-House)")
        self.reload_active()
        self.reload_checkedout()


def open_checkout(parent=None, user: str = "SA"):
    CheckOutBrowser(parent, user=user).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = CheckOutBrowser()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
