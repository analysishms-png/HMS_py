"""Expense Entry UI (VB6: Front Office -> Expense Entry).

VB6 RsFolioEntry.frm pattern:
  - Top: folio selection grid (active check-ins)
  - Bottom: charge lines for selected folio
  - New Expense: paycode + amount + remarks -> post to folio (AmtDr)
  - New Receipt/Payment: paycode + amount -> post (AmtCr)
  - Running balance shown
  - PYT-guard: sirf PYT* folios pe writes

Run: python -m HMS_py.ui.expense_ui
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout)

from HMS_py.core import checkout, expenseentry
from HMS_py.ui import theme as _theme


def _cell(val, fg: str = "") -> QTableWidgetItem:
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%Y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(fg))
    return it


class ExpenseEntryForm(QDialog):
    """Folio charge entry - Expense (Dr) + Receipt/Payment (Cr)."""

    FOLIO_COLS = ["FolioNo", "Guest Name", "City", "Departure", "Days"]
    CHARGE_COLS = ["VType", "VNo", "PayCode", "Amount",
                   "Dr (Charge)", "Cr (Payment)", "Remarks", "By"]

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Expense Entry - HMS_py")
        self.resize(1100, 700)

        root = QVBoxLayout(self)

        # ---- Folio list (top) ----
        root.addWidget(QLabel(
            "Active Folios (PYT* folios pe hi expense/receipt post hogi):"))
        self.tbl_folio = QTableWidget(0, len(self.FOLIO_COLS))
        self.tbl_folio.setHorizontalHeaderLabels(self.FOLIO_COLS)
        self.tbl_folio.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_folio.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_folio.setAlternatingRowColors(True)
        self.tbl_folio.setMaximumHeight(180)
        self.tbl_folio.horizontalHeader().setStretchLastSection(True)
        self.tbl_folio.cellClicked.connect(lambda *_: self._load_charges())
        root.addWidget(self.tbl_folio)

        # ---- Balance bar ----
        self.lblBal = QLabel("Folio select karo")
        f = QFont("Segoe UI", 10, QFont.Weight.Bold)
        self.lblBal.setFont(f)
        self.lblBal.setStyleSheet(
            f"padding:4px; background:{_theme.palette()['glass_tint']};"
            f"border-radius:6px;")
        root.addWidget(self.lblBal)

        # ---- Charge lines (middle) ----
        root.addWidget(QLabel("Folio Charges / Payments:"))
        self.tbl_charges = QTableWidget(0, len(self.CHARGE_COLS))
        self.tbl_charges.setHorizontalHeaderLabels(self.CHARGE_COLS)
        self.tbl_charges.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_charges.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_charges.setAlternatingRowColors(True)
        self.tbl_charges.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl_charges)

        # ---- Entry form (bottom) ----
        entry_row = QHBoxLayout()

        # Expense (Dr) section
        exp_form = QFormLayout()
        self.edPayCode = QLineEdit()
        self.edPayCode.setMaxLength(6)
        self.edPayCode.setPlaceholderText("e.g. KKRMCH")
        self.edAmount = QLineEdit("0")
        self.edAmount.setPlaceholderText("0.00")
        self.edRemarks = QLineEdit()
        self.edRemarks.setMaxLength(100)
        self.edRemarks.setPlaceholderText("Optional remarks")
        exp_form.addRow("Pay Code *", self.edPayCode)
        exp_form.addRow("Amount *", self.edAmount)
        exp_form.addRow("Remarks", self.edRemarks)

        st = _theme.status_colors()
        self.btnExpense = QPushButton("Post EXPENSE (Dr)")
        self.btnExpense.setToolTip("Post expense (debit) to the selected folio (Ctrl+E)")
        self.btnExpense.setStyleSheet(
            f"background:{st['danger']}; color:{st['on_danger']};"
            "font-weight:bold; padding:6px; border:none; border-radius:6px;")
        exp_form.addRow(self.btnExpense)
        entry_row.addLayout(exp_form)

        # Receipt (Cr) section
        rec_form = QFormLayout()
        self.edRecPayCode = QLineEdit()
        self.edRecPayCode.setMaxLength(6)
        self.edRecPayCode.setPlaceholderText("e.g. CASH")
        self.edRecAmount = QLineEdit("0")
        self.edRecAmount.setPlaceholderText("0.00")
        self.edRecRemarks = QLineEdit()
        self.edRecRemarks.setMaxLength(100)
        self.edRecRemarks.setPlaceholderText("Payment mode note")
        rec_form.addRow("Pay Code *", self.edRecPayCode)
        rec_form.addRow("Amount *", self.edRecAmount)
        rec_form.addRow("Remarks", self.edRecRemarks)

        self.btnReceipt = QPushButton("Post RECEIPT (Cr)")
        self.btnReceipt.setToolTip("Post receipt/payment (credit) to the selected folio (Ctrl+R)")
        self.btnReceipt.setStyleSheet(
            f"background:{st['success']}; color:{st['on_success']};"
            "font-weight:bold; padding:6px; border:none; border-radius:6px;")
        rec_form.addRow(self.btnReceipt)
        entry_row.addLayout(rec_form)

        root.addLayout(entry_row)

        # ---- Bottom buttons ----
        bot = QHBoxLayout()
        self.btnRefresh = QPushButton("Refresh (F5)")
        self.btnRefresh.setToolTip("Reload active folios and charges (F5)")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close the expense entry form")
        bot.addStretch()
        bot.addWidget(self.btnRefresh)
        bot.addWidget(self.btnClose)
        root.addLayout(bot)

        # ---- signals ----
        self.btnExpense.clicked.connect(self._post_expense)
        self.btnReceipt.clicked.connect(self._post_receipt)
        self.btnRefresh.clicked.connect(self.reload)
        self.btnClose.clicked.connect(self.reject)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)
        QShortcut(QKeySequence("Ctrl+E"), self,
                  activated=self._post_expense)
        QShortcut(QKeySequence("Ctrl+R"), self,
                  activated=self._post_receipt)

        self.reload()

    # ---- data ----
    def reload(self):
        rows = checkout.list_active_folios()
        self.tbl_folio.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            for c, v in enumerate([rec["folio"], rec["name"],
                                   rec["city"], rec["depdate"],
                                   rec["nodays"]]):
                self.tbl_folio.setItem(r, c, _cell(v))
        if rows:
            self.tbl_folio.selectRow(0)
            self._load_charges()

    def _selected_folio(self) -> tuple[int | None, str]:
        r = self.tbl_folio.currentRow()
        if r < 0:
            return None, ""
        it_f = self.tbl_folio.item(r, 0)
        it_n = self.tbl_folio.item(r, 1)
        folio = int(it_f.text()) if it_f and it_f.text() else None
        name = it_n.text() if it_n else ""
        return folio, name

    def _load_charges(self):
        folio, name = self._selected_folio()
        if not folio:
            return
        try:
            bal = checkout.folio_balance(folio)
            b = bal["balance"]
            self.lblBal.setText(
                f"Folio #{folio} | {name} | "
                f"Dr: ₹{bal['charges_dr']:.2f} | "
                f"Cr: ₹{bal['payments_cr']:.2f} | "
                f"Balance: ₹{b:.2f}")
            st = _theme.status_colors()
            self.lblBal.setStyleSheet(
                f"padding:4px; background:{st['danger_bg']};"
                f"color:{st['danger_text']}; font-weight:bold;"
                f"border-radius:6px;"
                if b > 0 else
                f"padding:4px; background:{st['success_bg']};"
                f"color:{st['success_text']}; font-weight:bold;"
                f"border-radius:6px;")

            charges = expenseentry.list_folio_charges(folio)
            self.tbl_charges.setRowCount(len(charges))
            for r, ch in enumerate(charges):
                for c, v in enumerate([
                    ch["vtype"], ch["vno"], ch["paycode"],
                    f"{ch['amount']:.2f}",
                    f"{ch['amt_dr']:.2f}" if ch["amt_dr"] else "—",
                    f"{ch['amt_cr']:.2f}" if ch["amt_cr"] else "—",
                    ch["remarks"], ch["u_name"],
                ]):
                    st = _theme.status_colors()
                    fg = (st["danger_text"]
                          if c == 4 and ch["amt_dr"] > 0
                          else st["success_text"]
                          if c == 5 and ch["amt_cr"] > 0
                          else _theme.palette()["text"])
                    self.tbl_charges.setItem(r, c, _cell(v, fg=fg))
        except Exception as e:
            self.lblBal.setText(f"Error: {e}")

    def _guard_pyt(self, name: str) -> bool:
        if not name.upper().startswith("PYT"):
            QMessageBox.warning(
                self, "Safety Guard",
                "Sirf PYT* test folios pe expense/receipt post karo.\n"
                "Production folios VB6 EXE se manage karo.")
            return False
        return True

    def _post_expense(self):
        folio, name = self._selected_folio()
        if not folio:
            QMessageBox.information(
                self, "Post Expense", "Pehle folio select karo")
            return
        if not self._guard_pyt(name):
            return
        paycode = self.edPayCode.text().strip()
        if not paycode:
            QMessageBox.warning(
                self, "Post Expense", "PayCode zaroori hai")
            return
        try:
            amount = float(self.edAmount.text() or 0)
        except ValueError:
            QMessageBox.warning(
                self, "Post Expense", "Amount valid number hona chahiye")
            return
        try:
            vno = expenseentry.post_expense(
                folio, paycode, amount,
                remarks=self.edRemarks.text().strip(),
                user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Post Expense", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Post Expense", f"DB error: {e}")
            return
        self.edAmount.setText("0")
        self.edRemarks.clear()
        self._load_charges()
        self.lblBal.setText(
            self.lblBal.text() + f"  | Expense VNo={vno} posted ✓")

    def _post_receipt(self):
        folio, name = self._selected_folio()
        if not folio:
            QMessageBox.information(
                self, "Post Receipt", "Pehle folio select karo")
            return
        if not self._guard_pyt(name):
            return
        paycode = self.edRecPayCode.text().strip()
        if not paycode:
            QMessageBox.warning(
                self, "Post Receipt", "PayCode zaroori hai")
            return
        try:
            amount = float(self.edRecAmount.text() or 0)
        except ValueError:
            QMessageBox.warning(
                self, "Post Receipt", "Amount valid number hona chahiye")
            return
        try:
            vno = expenseentry.post_receipt(
                folio, paycode, amount,
                remarks=self.edRecRemarks.text().strip(),
                user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Post Receipt", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Post Receipt", f"DB error: {e}")
            return
        self.edRecAmount.setText("0")
        self.edRecRemarks.clear()
        self._load_charges()
        self.lblBal.setText(
            self.lblBal.text() + f"  | Receipt VNo={vno} posted ✓")


def open_expense(parent=None, user: str = "SA"):
    ExpenseEntryForm(parent, user=user).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = ExpenseEntryForm()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
