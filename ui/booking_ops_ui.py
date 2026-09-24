"""Booking Operations UI (VB6: Front Office -> Booking Operations).

Features:
  - Table showing all bookings (BookNo, GuestName, ArrDate, DepDate, RoomRate, Cancel, ResStatus)
  - Search by guest name, docid, or mobile
  - Double-click row to view/edit booking details
  - Buttons: New Booking, Modify, Cancel Booking, Refresh, Exit
  - Form fields: GuestName, ArrDate, DepDate, NoDays, Adult, Child, NoOfRooms, RoomRate, MobNo, Email, Remarks

Run: python -m HMS_py.ui.booking_ops_ui
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


class BookingOpsDialog(QDialog):
    """Booking Operations - list, search, new, modify, cancel bookings."""

    TABLE_COLS = ["BookNo", "GuestName", "ArrDate", "DepDate",
                  "RoomRate", "Cancel", "ResStatus"]
    TABLE_KEYS = ["bookno", "guestname", "arrdate", "depdate",
                  "roomrate", "cancel", "resstatus"]

    FORM_FIELDS = [
        ("guestname", "Guest Name"),
        ("arrdate", "Arrival Date (DD/MM/YYYY)"),
        ("depdate", "Departure Date (DD/MM/YYYY)"),
        ("nodays", "No. of Days"),
        ("adult", "Adult"),
        ("child", "Child"),
        ("noofrooms", "No. of Rooms"),
        ("roomrate", "Room Rate"),
        ("mobno", "Mobile No"),
        ("email", "Email"),
        ("remarks", "Remarks"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Booking Operations")
        self.resize(900, 600)
        self.edit_bookno = None

        from HMS_py.core import booking as _booking_mod
        self._booking = _booking_mod

        root = QVBoxLayout(self)

        # ── Search bar ──
        sbar = QHBoxLayout()
        sbar.addWidget(QLabel("Search:"))
        self.edSearch = QLineEdit()
        self.edSearch.setPlaceholderText("Guest name / DocId / Mobile...")
        sbar.addWidget(self.edSearch)
        btnSearch = QPushButton("Search")
        btnSearch.clicked.connect(self._on_search)
        sbar.addWidget(btnSearch)
        root.addLayout(sbar)

        # ── Table ──
        self.tbl = QTableWidget(0, len(self.TABLE_COLS))
        self.tbl.setHorizontalHeaderLabels(self.TABLE_COLS)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._on_modify())
        root.addWidget(self.tbl)

        # ── Form fields ──
        fwrap = QDialog(self)  # placeholder
        from PyQt6.QtWidgets import QWidget
        fwrap = QWidget()
        self.form = QFormLayout(fwrap)
        self.edits = {}
        _field_hints = {
            "guestname": "Guest full name",
            "arrdate": "DD/MM/YYYY",
            "depdate": "DD/MM/YYYY",
            "nodays": "Auto-calculated",
            "adult": "Number of adults",
            "child": "Number of children",
            "noofrooms": "Number of rooms",
            "roomrate": "Rate per room per night",
            "mobno": "Mobile number",
            "email": "guest@email.com",
            "remarks": "Optional remarks",
        }
        for key, label in self.FORM_FIELDS:
            e = QLineEdit()
            e.setFont(QFont("Segoe UI", 10))
            e.setPlaceholderText(_field_hints.get(key, ""))
            self.form.addRow(label, e)
            self.edits[key] = e
        root.addWidget(fwrap)

        # ── Buttons ──
        btns = QHBoxLayout()
        btn_font = QFont("Segoe UI", 10)
        self.btnNew = QPushButton("New Booking")
        self.btnNew.setToolTip("Start a new booking entry (Ctrl+N)")
        self.btnNew.setFont(btn_font)
        self.btnModify = QPushButton("Modify")
        self.btnModify.setToolTip("Save changes to selected booking (Ctrl+M)")
        self.btnModify.setFont(btn_font)
        self.btnCancelBooking = QPushButton("Cancel Booking")
        self.btnCancelBooking.setToolTip("Cancel the selected booking")
        self.btnCancelBooking.setFont(btn_font)
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.setToolTip("Reload booking list (F5)")
        self.btnRefresh.setFont(btn_font)
        self.btnExit = QPushButton("Exit")
        self.btnExit.setToolTip("Close this window (Esc)")
        self.btnExit.setFont(btn_font)
        for b in (self.btnNew, self.btnModify, self.btnCancelBooking,
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
        self.btnCancelBooking.clicked.connect(self._on_cancel_booking)
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

    def _selected_bookno(self):
        r = self.tbl.currentRow()
        if r < 0:
            return None
        it = self.tbl.item(r, 0)
        if it is None:
            return None
        try:
            return int(it.text())
        except (ValueError, TypeError):
            return None

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
            rows = self._booking.list_all()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Load failed:\n{ex}")
            rows = []
        self.tbl.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            for c, key in enumerate(self.TABLE_KEYS):
                self.tbl.setItem(r, c, _cell(self._cell_val(key, rec)))
        self.lblState.setText(f"Loaded {len(rows)} bookings")
        self.edit_bookno = None
        self._clear_form()
        self._set_form_enabled(False)

    def _load_search(self, term: str):
        try:
            rows = self._booking.search(term)
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
        self.edit_bookno = None
        self._clear_form()
        self._set_form_enabled(True)
        self.lblState.setText("State: Add - fill form and save via Modify/Save")
        self.edits["guestname"].setFocus()

    def _on_modify(self):
        if self.edit_bookno is not None:
            self._on_save()
            return
        bookno = self._selected_bookno()
        if bookno is None:
            QMessageBox.information(self, "Modify", "Pehle row select karo")
            return
        try:
            rec = self._booking.get(bookno)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Fetch failed:\n{ex}")
            return
        if not rec:
            QMessageBox.warning(self, "Modify", f"BookNo {bookno} nahi mila")
            return
        self.edit_bookno = bookno
        self._rec_to_form(rec)
        self._set_form_enabled(True)
        self.btnModify.setText("Save (Ctrl+S)")
        self.lblState.setText(f"State: Edit - BookNo {bookno} (Modify/Save pe click karo)")
        self.edits["guestname"].setFocus()

    def _on_save(self):
        if self.edit_bookno is None:
            return
        rec = {}
        for key, _ in self.FORM_FIELDS:
            rec[key] = self.edits[key].text().strip()
        if not rec.get("guestname"):
            QMessageBox.warning(self, "Save", "Guest name required")
            return
        try:
            self._booking.update(self.edit_bookno, rec)
            QMessageBox.information(self, "Save",
                                    f"Booking {self.edit_bookno} updated")
            self.edit_bookno = None
            self.btnModify.setText("Modify")
            self._set_form_enabled(False)
            self.reload()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Save failed:\n{ex}")

    def _on_cancel_booking(self):
        bookno = self._selected_bookno()
        if bookno is None:
            QMessageBox.information(self, "Cancel",
                                    "Pehle row select karo")
            return
        if QMessageBox.question(
                self, "Cancel Booking",
                f"Booking {bookno} cancel karein?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self._booking.cancel(bookno)
            QMessageBox.information(self, "Cancel",
                                    f"Booking {bookno} cancelled")
            self.reload()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Cancel failed:\n{ex}")


def open_booking_ops(parent=None) -> BookingOpsDialog:
    dlg = BookingOpsDialog(parent)
    dlg.exec()
    return dlg


# ── Standalone run ──
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = BookingOpsDialog()
    dlg.show()
    sys.exit(app.exec())
