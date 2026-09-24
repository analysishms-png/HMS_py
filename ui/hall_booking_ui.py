"""Hall Booking Operations UI (VB6: Banquet -> Hall Booking Operations).

Features:
  - Table showing HallBook records (DocId, VNo, PartyName, Func_Name, Vdate, Advance, NetAmount, BookingStatus)
  - Buttons: New Hall Booking, Modify, Cancel, Refresh, Exit
  - Form fields: PartyName, Func_Name, Vdate, FrBookDate, ToBookDate, NoOfPerson, HallRent, Advance, Remarks
  - Search by party name or docid

Run: python -m HMS_py.ui.hall_booking_ui
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QShortcut, QKeySequence
from HMS_py.ui import theme as _theme
from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)


def _cell(val, fg: str = "") -> QTableWidgetItem:
    if isinstance(val, (datetime.date, datetime.datetime)):
        val = f"{val:%d/%b/%Y}"
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(fg))
    return it


class HallBookingDialog(QDialog):
    """Hall Booking Operations - list, search, new, modify, cancel hall bookings."""

    TABLE_COLS = ["DocId", "VNo", "PartyName", "Func_Name",
                  "BookingDate", "Advance", "NetAmount", "BookingStatus"]
    TABLE_KEYS = ["docid", "vno", "partyname", "func_name",
                  "vdate", "advance", "netamount", "bookingstatus"]

    FORM_FIELDS = [
        ("partyname", "Party Name"),
        ("func_name", "Function Name"),
        ("vdate", "Booking Date (DD/MM/YYYY)"),
        ("frbookdate", "From Date (DD/MM/YYYY)"),
        ("tobookdate", "To Date (DD/MM/YYYY)"),
        ("hallrent", "Hall Rent / Rate"),
        ("advance", "Advance"),
        ("remarks", "Remarks"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hall Booking Operations")
        self.resize(900, 600)
        self.edit_vno = None
        self.edit_vprefix = None

        from HMS_py.core import hall_booking as _hb_mod
        self._hb = _hb_mod

        root = QVBoxLayout(self)

        # ── Search bar ──
        sbar = QHBoxLayout()
        sbar.addWidget(QLabel("Search:"))
        self.edSearch = QLineEdit()
        self.edSearch.setPlaceholderText("Party name / DocId...")
        sbar.addWidget(self.edSearch)
        btnSearch = QPushButton("Search")
        btnSearch.setToolTip("Search by party name or doc ID")
        btnSearch.clicked.connect(self._on_search)
        sbar.addWidget(btnSearch)
        root.addLayout(sbar)

        # ── Table ──
        self.tbl = QTableWidget(0, len(self.TABLE_COLS))
        self.tbl.setHorizontalHeaderLabels(self.TABLE_COLS)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_modify())
        root.addWidget(self.tbl)

        # ── Form fields ──
        from PyQt6.QtWidgets import QWidget
        fwrap = QWidget()
        self.form = QFormLayout(fwrap)
        self.edits = {}
        for key, label in self.FORM_FIELDS:
            e = QLineEdit()
            e.setFont(QFont("Segoe UI", 10))
            e.setPlaceholderText(label)
            self.form.addRow(label, e)
            self.edits[key] = e
        root.addWidget(fwrap)

        # ── Buttons ──
        btns = QHBoxLayout()
        btn_font = QFont("Segoe UI", 10)
        self.btnNew = QPushButton("New Hall Booking")
        self.btnNew.setFont(btn_font)
        self.btnNew.setToolTip("Create a new hall booking (Ctrl+N)")
        self.btnModify = QPushButton("Modify")
        self.btnModify.setFont(btn_font)
        self.btnModify.setToolTip("Edit or save selected booking (Ctrl+M)")
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setFont(btn_font)
        self.btnCancel.setToolTip("Cancel selected hall booking")
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.setFont(btn_font)
        self.btnRefresh.setToolTip("Reload data from database (F5)")
        self.btnExit = QPushButton("Exit")
        self.btnExit.setFont(btn_font)
        self.btnExit.setToolTip("Close this window")
        for b in (self.btnNew, self.btnModify, self.btnCancel,
                  self.btnRefresh, self.btnExit):
            btns.addWidget(b)
        root.addLayout(btns)

        # ── State label ──
        self.lblState = QLabel("Ready")
        self.lblState.setFont(QFont("Segoe UI", 9))
        root.addWidget(self.lblState)

        # ── Connections ──
        self.btnNew.clicked.connect(self._on_new)
        self.btnModify.clicked.connect(self._on_modify)
        self.btnCancel.clicked.connect(self._on_cancel)
        self.btnRefresh.clicked.connect(self.reload)
        self.btnExit.clicked.connect(self.reject)

        # ── Keyboard shortcuts ──
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._on_new)
        QShortcut(QKeySequence("Ctrl+M"), self, activated=self._on_modify)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self._on_search)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)
        QShortcut(QKeySequence("Escape"), self, activated=self.reject)

        self.reload()

    # ────────────────────────── helpers ──────────────────────────
    def _cell_val(self, key, rec):
        val = rec.get(key, "")
        if isinstance(val, (datetime.date, datetime.datetime)):
            return f"{val:%d/%b/%Y}"
        return "" if val is None else str(val)

    def _selected_vno(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        it_vno = self.tbl.item(r, 1)
        if it_vno is None:
            return None
        try:
            return int(it_vno.text())
        except (ValueError, TypeError):
            return None

    def _selected_docid(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        it = self.tbl.item(r, 0)
        return it.text() if it else None

    def _clear_form(self):
        for e in self.edits.values():
            e.clear()

    def _form_to_rec(self) -> dict:
        rec = {}
        for key in self.edits:
            rec[key] = self.edits[key].text().strip()
        return rec

    def _rec_to_form(self, rec: dict):
        for key, _ in self.FORM_FIELDS:
            val = rec.get(key, "")
            if isinstance(val, (datetime.date, datetime.datetime)):
                val = f"{val:%d/%b/%Y}"
            self.edits[key].setText("" if val is None else str(val))

    def _set_form_enabled(self, enabled: bool):
        for e in self.edits.values():
            e.setEnabled(enabled)

    # ────────────────────────── data ──────────────────────────
    def reload(self):
        try:
            rows = self._hb.list_all_hallbook()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Load failed:\n{ex}")
            rows = []
        self.tbl.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            for c, key in enumerate(self.TABLE_KEYS):
                self.tbl.setItem(r, c, _cell(self._cell_val(key, rec)))
        self.lblState.setText(f"Loaded {len(rows)} hall bookings")
        self.edit_vno = None
        self.edit_vprefix = None
        self._clear_form()
        self._set_form_enabled(False)

    def _load_search(self, term: str):
        try:
            rows = self._hb.search_hallbook(term)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Search failed:\n{ex}")
            rows = []
        self.tbl.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            for c, key in enumerate(self.TABLE_KEYS):
                self.tbl.setItem(r, c, _cell(self._cell_val(key, rec)))
        self.lblState.setText(f"Search: {len(rows)} results for '{term}'")

    # ────────────────────────── handlers ──────────────────────────
    def _on_search(self):
        term = self.edSearch.text().strip()
        if term:
            self._load_search(term)
        else:
            self.reload()

    def _on_new(self):
        self.edit_vno = None
        self.edit_vprefix = None
        self._clear_form()
        self._set_form_enabled(True)
        self.lblState.setText("State: New - fill form then Modify to save")
        self.edits["partyname"].setFocus()

    def _on_modify(self):
        if self.edit_vno is not None:
            # Save mode
            try:
                rec = self._form_to_rec()
                if not rec.get("partyname", "").strip():
                    QMessageBox.warning(self, "Modify",
                                        "Party Name zaroori hai")
                    return
                if self.edit_vprefix is None:
                    from datetime import date
                    self.edit_vprefix = str(date.today().year)
                    self._hb.insert_hallbook(rec)
                    QMessageBox.information(self, "Save",
                                            "Hall booking saved")
                else:
                    self._hb.update_hallbook(self.edit_vno, rec,
                                             vprefix=self.edit_vprefix)
                    QMessageBox.information(self, "Save",
                                            "Hall booking updated")
                self.edit_vno = None
                self.edit_vprefix = None
                self._set_form_enabled(False)
                self.reload()
            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Save failed:\n{ex}")
        else:
            # Edit mode - load from selected row
            vno = self._selected_vno()
            if vno is None:
                QMessageBox.information(self, "Modify",
                                        "Pehle row select karo")
                return
            try:
                # Try to get vprefix from docid if available
                rec = self._hb.get_hallbook(vno)
            except Exception as ex:
                QMessageBox.critical(self, "Error", f"Fetch failed:\n{ex}")
                return
            if not rec:
                QMessageBox.warning(self, "Modify",
                                    f"VNo {vno} nahi mila")
                return
            self.edit_vno = vno
            self.edit_vprefix = rec.get("vprefix", None)
            self._rec_to_form(rec)
            self._set_form_enabled(True)
            self.lblState.setText(f"State: Edit - VNo {vno}")
            self.edits["partyname"].setFocus()

    def _on_cancel(self):
        vno = self._selected_vno()
        if vno is None:
            QMessageBox.information(self, "Cancel",
                                    "Pehle row select karo")
            return
        if QMessageBox.question(
                self, "Cancel Hall Booking",
                f"Hall booking VNo {vno} cancel karein?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self._hb.delete_hallbook(vno)
            QMessageBox.information(self, "Cancel",
                                    f"Hall booking VNo {vno} cancelled")
            self.reload()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Cancel failed:\n{ex}")


def open_hall_booking(parent=None) -> HallBookingDialog:
    dlg = HallBookingDialog(parent)
    dlg.exec()
    return dlg


# ── Standalone run ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = HallBookingDialog()
    dlg.show()
    sys.exit(app.exec())
