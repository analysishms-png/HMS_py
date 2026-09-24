"""Folio UI (P4-b): Check-Out settle + FolioLog + amend — VB6 evidence se.

Run: python -m HMS_py.ui.folio_ui
Menu: Front Office -> 'Check-Out' / 'Folio Log' / 'Amend Departure'.
PYT-guard: sirf PYT* folio pe write allowed.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QFormLayout,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from HMS_py.core import db, folio
from HMS_py.ui import theme as _theme


def _fill(table: QTableWidget, headers: list, rows: list):
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    table.setAlternatingRowColors(True)
    text_col = QColor(_theme.palette()["text"])
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            it = QTableWidgetItem(str(val))
            it.setForeground(text_col)
            table.setItem(i, j, it)


class FolioBrowser(QWidget):
    """Check-Out + FolioLog + Amend views (VB6 Front Office leaves)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        self.lblTitle = QLabel("In-House Folios")
        top.addWidget(self.lblTitle)
        top.addStretch(1)
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.setToolTip("Reload folio list (Ctrl+F5)")
        self.btnRefresh.clicked.connect(self.reload)
        top.addWidget(self.btnRefresh)
        v.addLayout(top)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self._drill)
        self._empty_label = QLabel("No folios found.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color:{_theme.palette()['text_dim']}; font-size:13px; padding:24px;")
        v.addWidget(self.table)
        v.addWidget(self._empty_label)

        bar = QHBoxLayout()
        self.btnSettle = QPushButton("Check-Out (Settle)")
        self.btnSettle.setToolTip("Check-out selected folio (Ctrl+O)")
        self.btnSettle.clicked.connect(self._settle)
        self.btnAmend = QPushButton("Amend Departure")
        self.btnAmend.setToolTip("Amend departure date of selected folio (Ctrl+A)")
        self.btnAmend.clicked.connect(self._amend)
        self.btnLog = QPushButton("Folio Log")
        self.btnLog.setToolTip("View folio activity log (Ctrl+L)")
        self.btnLog.clicked.connect(self._log)
        self.btnPay = QPushButton("Receive Payment")
        self.btnPay.setToolTip("Receive payment against selected folio (Ctrl+R)")
        self.btnPay.clicked.connect(self._pay)
        for b in (self.btnSettle, self.btnAmend, self.btnPay, self.btnLog):
            bar.addWidget(b)
        bar.addStretch(1)
        v.addLayout(bar)

        QShortcut(QKeySequence("Ctrl+O"), self,
                  activated=self._settle)
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self._amend)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._pay)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._log)
        QShortcut(QKeySequence("Ctrl+F5"), self, activated=self.reload)
        self._view = "folios"
        self.reload()

    def _folios(self) -> list:
        # EVIDENCE: GuestFolio ke date-cols = Vdate (arrival) + DepDate;
        # ArrDate column DB me NAHI hai (ArrFrom varchar hai) - live-probed.
        return db.query(
            "SELECT FolioNo, Name, Vdate, DepDate, DocId, Vprefix "
            "FROM GuestFolio WHERE Site_Code = ? AND Vprefix = ? "
            "ORDER BY FolioNo DESC",
            (folio.SITE_CODE, folio.VPREFIX))

    def reload(self):
        self._view = "folios"
        self.lblTitle.setText("In-House Folios")
        rows = self._folios()
        def _d(v):
            return v.strftime("%Y-%m-%d") if hasattr(v, "strftime") else \
                ((v or "")[:10] if v else "")
        data = [[r.FolioNo, (r.Name or "").strip(),
                 _d(r.Vdate), _d(r.DepDate),
                 (r.DocId or "").strip()] for r in rows]
        _fill(self.table,
              ["Folio", "Guest", "Arrival", "Departure", "DocId"], data)
        self._empty_label.setVisible(len(data) == 0)
        self.table.setVisible(len(data) > 0)

    def _log(self):
        self._view = "log"
        self.lblTitle.setText("Folio Log (latest)")
        data = [[x["id"], x["docid"], x["flag"], x["user"], x["dt"], x["ae"]]
                for x in folio.log_list()]
        _fill(self.table, ["Id", "Folio DocId", "Flag", "User", "DT", "A/E"],
              data)
        self._empty_label.setVisible(len(data) == 0)
        self.table.setVisible(len(data) > 0)

    def _drill(self, row, _col):
        if self._view != "folios":
            return
        item = self.table.item(row, 0)
        if not item:
            return
        folio_no = int(item.text())
        dlg = ChargeDialog(folio_no, self)
        dlg.exec()

    def _settle(self):
        rows = self.table.selectionModel().selectedRows() \
            if self._view == "folios" else []
        if not rows:
            QMessageBox.information(self, "Check-Out",
                                    "Pehle in-house folio select karo")
            return
        item = self.table.item(rows[0].row(), 0)
        if not item:
            return
        folio_no = int(item.text())
        try:
            billno = folio.settle_folio(folio_no)
        except ValueError as e:
            QMessageBox.warning(self, "Check-Out blocked", str(e))
            return
        QMessageBox.information(
            self, "Check-Out done",
            f"Folio #{folio_no} settled.\nBill_No = {billno}")
        self.reload()

    def _pay(self):
        rows = self.table.selectionModel().selectedRows() \
            if self._view == "folios" else []
        if not rows:
            QMessageBox.information(self, "Payment",
                                    "Pehle folio select karo")
            return
        item = self.table.item(rows[0].row(), 0)
        if not item:
            return
        folio_no = int(item.text())
        dlg = PaymentDialog(folio_no, self)
        if dlg.exec():
            self.reload()

    def _amend(self):
        rows = self.table.selectionModel().selectedRows() \
            if self._view == "folios" else []
        if not rows:
            QMessageBox.information(self, "Amend",
                                    "Pehle folio select karo")
            return
        item = self.table.item(rows[0].row(), 0)
        if not item:
            return
        folio_no = int(item.text())
        r = [x for x in self._folios()
             if x.FolioNo == folio_no]
        if not r:
            return
        dlg = AmendDialog(folio_no, r[0].DepDate, self)
        if dlg.exec():
            self.reload()


class ChargeDialog(QDialog):
    """Ek folio ki charges (VB6 folio-detail drill)."""

    def __init__(self, folio_no: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Folio #{folio_no} - Charges")
        self.setModal(True)
        self.resize(640, 400)
        v = QVBoxLayout(self)
        v.addWidget(QLabel(f"Folio #{folio_no} charges "
                           f"(balance = Dr-Cr)"))
        t = QTableWidget()
        charges = folio.folio_charges(folio_no)
        bal = folio.folio_balance(folio_no)
        data = [[c["sno"], c["paycode"], c["paytype"], c["comments"],
                 f"{c['dr']:.2f}", f"{c['cr']:.2f}"] for c in charges]
        _fill(t, ["SNo", "PayCode", "Type", "Comments", "Dr", "Cr"], data)
        v.addWidget(t)
        v.addWidget(QLabel(f"Balance: {bal:.2f}"))
        btn = QPushButton("Close")
        btn.setToolTip("Close this dialog")
        btn.clicked.connect(self.accept)
        v.addWidget(btn)


class PaymentDialog(QDialog):
    """Payment receive (VB6 FrmReceivePayment/fdPaymentCharge): folio pe
    REC payment — KKCASH default, balance live update."""

    def __init__(self, folio_no: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Receive Payment - Folio #{folio_no}")
        self.setModal(True)
        self.folio_no = folio_no
        form = QFormLayout(self)
        self.lblBal = QLabel(f"Current Balance: "
                             f"{folio.folio_balance(folio_no):.2f}")
        form.addRow(self.lblBal)
        self.cmbMode = QComboBox()
        for code, ptype in folio.PAY_TYPES.items():
            self.cmbMode.addItem(f"{code} - {ptype}", code)
        form.addRow("Pay Mode:", self.cmbMode)
        self.txtAmt = QLineEdit("0.00")
        self.txtAmt.setPlaceholderText("Payment amount")
        form.addRow("Amount:", self.txtAmt)
        self.txtComments = QLineEdit("CASH RECD.")
        self.txtComments.setPlaceholderText("Remarks for this payment")
        form.addRow("Remarks:", self.txtComments)
        hb = QHBoxLayout()
        ok = QPushButton("Receive")
        ok.setToolTip("Receive this payment")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.setToolTip("Discard and close")
        cancel.clicked.connect(self.reject)
        hb.addStretch(1)
        hb.addWidget(ok)
        hb.addWidget(cancel)
        form.addRow(hb)

    def accept(self):
        try:
            amt = float(self.txtAmt.text().strip() or "0")
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Amount numeric hona chahiye")
            return
        try:
            vno = folio.receive_payment(
                self.folio_no, amt, paycode=self.cmbMode.currentData(),
                comments=self.txtComments.text().strip())
        except ValueError as e:
            QMessageBox.warning(self, "Payment blocked", str(e))
            return
        QMessageBox.information(
            self, "Payment received",
            f"REC voucher #{vno} posted on folio #{self.folio_no}")
        super().accept()


class AmendDialog(QDialog):
    """Departure date amend (VB6 GuestFolioAmend pattern)."""

    def __init__(self, folio_no: int, cur_dep, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Amend Departure - Folio #{folio_no}")
        self.setModal(True)
        self.folio_no = folio_no
        form = QFormLayout(self)
        self.dt = QDateEdit()
        self.dt.setCalendarPopup(True)
        try:
            import datetime
            d = cur_dep if isinstance(cur_dep, datetime.datetime) else \
                datetime.datetime.strptime(str(cur_dep)[:10], "%Y-%m-%d")
        except Exception:
            import datetime
            d = datetime.datetime.now()
        self.dt.setDate(d.date())
        form.addRow("New Departure:", self.dt)
        hb = QHBoxLayout()
        ok = QPushButton("Save")
        ok.setToolTip("Save amended departure date")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.setToolTip("Discard changes and close")
        cancel.clicked.connect(self.reject)
        hb.addStretch(1)
        hb.addWidget(ok)
        hb.addWidget(cancel)
        form.addRow(hb)

    def accept(self):
        try:
            folio.amend_departure(self.folio_no, self.dt.date())
        except ValueError as e:
            QMessageBox.warning(self, "Amend blocked", str(e))
            return
        super().accept()


def open_folio(parent=None):
    """Shell ke liye opener (Folio Log / Amend Departure leaves)."""
    w = FolioBrowser(parent)
    w.setWindowFlags(Qt.WindowType.Window)
    w.setWindowTitle("Folio / Check-Out - HMS_py")
    w.resize(920, 580)
    w.show()
    return w


def main():  # pragma: no cover
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    _theme.apply_theme(app)
    w = FolioBrowser()
    w.resize(900, 560)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    main()
