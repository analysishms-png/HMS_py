"""Reservation browser v2 (P3-b) - full CRUD, VB6 RsBookingEntry pattern.

Run: python -m HMS_py.ui.reservation_browser
Menu: Reservation -> Operations -> 'Reservation/Cancellation'.
CRUD: New (PYT* draft), Edit (fields), Cancel (VB6 flow: Cancel='Y' +
CancelDate + CancelUName - physical delete nahi). Sab live Booking table
par; delete-guard PYT-only (production data VB6 EXE se hi).
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QDateEdit, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor

from HMS_py.core import reservation
from HMS_py.ui import theme as _theme


class ReservationBrowser(QDialog):
    COLS = [("BookNo", 0), ("VDate", 1), ("GuestName", 2), ("Arrival", 3),
            ("Departure", 4), ("Rooms", 5), ("Rate", 6), ("Status", 7),
            ("Cancel", 8), ("User", 9), ("AE", 10)]

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Reservation Master (P3-b) - HMS_py")
        self.resize(1080, 600)

        root = QVBoxLayout(self)
        self.tbl = QTableWidget(0, len(self.COLS))
        self.tbl.setHorizontalHeaderLabels([c[0] for c in self.COLS])
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.setAlternatingRowColors(True)
        self._empty_label = QLabel("No reservations found. Click 'New' to create one.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color:{_theme.palette()['text_dim']}; font-size:13px; padding:24px;")
        root.addWidget(self.tbl)
        root.addWidget(self._empty_label)
        self.tbl.cellDoubleClicked.connect(lambda *_: self._edit())

        self.lblState = QLabel(
            "State: Idle | New=PYT* draft, Edit=fields, "
            "Cancel=VB6 flow (Cancel='Y')")
        root.addWidget(self.lblState)

        btns = QHBoxLayout()
        self.btnNew = QPushButton("New")
        self.btnNew.setToolTip("Create new reservation draft (Ctrl+N)")
        self.btnEdit = QPushButton("Edit")
        self.btnEdit.setToolTip("Edit selected reservation (Ctrl+E)")
        self.btnCancel = QPushButton("Cancel Booking")
        self.btnCancel.setToolTip("Cancel selected booking (Ctrl+Del)")
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.setToolTip("Reload reservation list (F5)")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close this window (Esc)")
        for b in (self.btnNew, self.btnEdit, self.btnCancel,
                  self.btnRefresh, self.btnClose):
            btns.addWidget(b)
        root.addLayout(btns)

        self.btnNew.clicked.connect(self._new)
        self.btnEdit.clicked.connect(self._edit)
        self.btnCancel.clicked.connect(self._cancel)
        self.btnRefresh.clicked.connect(lambda: self.reload())
        self.btnClose.clicked.connect(self.reject)

        # Keyboard (P3-b E2E fix): dialog UIA me buttons expose nahi hote,
        # VB6 &-accelerator pattern: Ctrl+N = New, Ctrl+E = Edit,
        # Ctrl+Del = Cancel booking, F5 = Refresh
        from PyQt6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._new)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self._edit)
        QShortcut(QKeySequence("Ctrl+Del"), self, activated=self._cancel)
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.reload())

        self.reload()

    def reload(self, keep_bookno: int | None = None):
        """Reload grid; keep_bookno do to wahi row wapas select hogi
        (reload selection reset bug: Edit->Cancel flow me galat row
        target ho sakti thi - PYT-guard ne pakda tha)."""
        rows = reservation.list_reservations()
        self.tbl.setRowCount(len(rows))
        self._empty_label.setVisible(len(rows) == 0)
        self.tbl.setVisible(len(rows) > 0)
        for r, row in enumerate(rows):
            # list query returns (FIXED - Cancel now fetched explicitly):
            # BookNo(0),VDate(1),GuestName(2),ArrDate(3),DepDate(4),
            # NoofRooms(5),RoomRate(6),ResStatus(7),Cancel(8),U_Name(9),U_AE(10)
            vals = [row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7],                           # ResStatus
                    "Y" if str(row[8] or "").upper() == "Y" else "",  # Cancel
                    row[9], row[10]]                  # U_Name, U_AE
            for c, (h, i) in enumerate(self.COLS):
                v = vals[c]
                if isinstance(v, (datetime.date, datetime.datetime)):
                    v = f"{v:%d/%b/%Y}"
                it = QTableWidgetItem("" if v is None else str(v))
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Dark-mode fix (live-caught): palette text white hota hai,
                # white background par invisible - VB6 DataGrid jaisa
                # hamesha-dark text force karo
                it.setForeground(QColor(_theme.palette()["text"]))
                self.tbl.setItem(r, c, it)
        if keep_bookno is not None:
            for r, row in enumerate(rows):
                # BUG-022 fix: non-numeric BookNo pe crash nahi - skip
                try:
                    if int(row[0]) == keep_bookno:
                        self.tbl.selectRow(r)
                        break
                except (TypeError, ValueError):
                    continue
        elif rows:
            self.tbl.selectRow(0)

    # ---------- helpers ----------
    def _selected_bookno(self):
        """Selected BookNo (BUG-022: None/empty/non-numeric cell pe crash guard)."""
        r = self.tbl.currentRow()
        if r < 0:
            return None
        item = self.tbl.item(r, 0)
        if not item or not item.text().strip():
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def _require_pyt(self, bookno: int):
        """Safety: write-ops sirf PYT* guests par (production VB6 se)
        + M3: cancelled booking pe edit/cancel block (VB6 FGrid rule,
        RsBookingEntry.frm:1959 - Cancel='Y' check)."""
        row = reservation.get(bookno)
        if not row:
            raise ValueError(f"Booking {bookno} nahi mila")
        if str(row.get("Cancel") or "").upper() == "Y":
            raise ValueError(
                f"Booking {bookno} CANCELLED hai - edit/cancel blocked "
                "(VB6 rule: Cancel='Y' pe koi write nahi)")
        if not str(row["GuestName"]).upper().startswith("PYT"):
            raise ValueError(
                "Safety: sirf PYT* test-bookings edit/cancel ho sakti hain "
                "(production data VB6 EXE se)")
        return row

    # ---------- CRUD ----------
    def _new(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("New Reservation (PYT test-data)")
        dlg.setModal(True)
        form = QFormLayout()
        ed_guest = QLineEdit("PYT Guest")
        ed_guest.setMaxLength(100)
        ed_guest.setPlaceholderText("Guest full name (must start with PYT*)")
        de_arr = QDateEdit(QDate.currentDate()); de_arr.setCalendarPopup(True)
        de_dep = QDateEdit(QDate.currentDate().addDays(1))
        de_dep.setCalendarPopup(True)
        ed_adult = QLineEdit("1"); ed_adult.setPlaceholderText("Number of adults")
        ed_rooms = QLineEdit("1"); ed_rooms.setPlaceholderText("Number of rooms")
        ed_rate = QLineEdit("0"); ed_rate.setPlaceholderText("Room rate per night")
        form.addRow("Guest Name (PYT*)", ed_guest)
        form.addRow("Arrival", de_arr)
        form.addRow("Departure", de_dep)
        form.addRow("Adults", ed_adult)
        form.addRow("Rooms", ed_rooms)
        form.addRow("Rate", ed_rate)
        lay = QVBoxLayout(dlg)
        lay.addLayout(form)
        brow = QHBoxLayout()
        ok = QPushButton("Save"); ok.setToolTip("Save new reservation")
        cancel = QPushButton("Cancel"); cancel.setToolTip("Discard and close")
        brow.addStretch(); brow.addWidget(ok); brow.addWidget(cancel)
        lay.addLayout(brow)
        ok.clicked.connect(dlg.accept); cancel.clicked.connect(dlg.reject)
        ok.setDefault(True)   # VB6 pattern: Enter = Save
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            bookno = reservation.insert_draft(
                ed_guest.text(), de_arr.date().toPyDate(),
                de_dep.date().toPyDate(), adults=int(ed_adult.text() or 1),
                rooms=int(ed_rooms.text() or 1),
                rate=float(ed_rate.text() or 0), user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "New", str(e)); return
        except Exception as e:
            QMessageBox.critical(self, "New", f"DB error: {e}"); return
        self.lblState.setText(f"State: Idle | Booking #{bookno} add ho gaya")
        self.reload(keep_bookno=bookno)

    def _edit(self):
        bookno = self._selected_bookno()
        if bookno is None:
            QMessageBox.information(self, "Edit", "Pehle row select karo")
            return
        try:
            row = self._require_pyt(bookno)
        except ValueError as e:
            QMessageBox.warning(self, "Edit", str(e)); return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Edit Booking #{bookno}")
        dlg.setModal(True)
        form = QFormLayout()
        ed_guest = QLineEdit(row["GuestName"]); ed_guest.setMaxLength(100)
        ed_guest.setPlaceholderText("Guest full name")
        arr = row["ArrDate"]; dep = row["DepDate"]
        # BUG FIX: QDate() does NOT accept datetime.date directly.
        # Must pass year, month, day individually.
        if hasattr(arr, 'year'):
            qarr = QDate(arr.year, arr.month, arr.day)
        else:
            qarr = QDate.currentDate()
        if hasattr(dep, 'year'):
            qdep = QDate(dep.year, dep.month, dep.day)
        else:
            qdep = QDate.currentDate().addDays(1)
        de_arr = QDateEdit(qarr); de_arr.setCalendarPopup(True)
        de_dep = QDateEdit(qdep); de_dep.setCalendarPopup(True)
        ed_adult = QLineEdit(str(row["Adult"]))
        ed_adult.setPlaceholderText("Number of adults")
        ed_rooms = QLineEdit(str(row["NoofRooms"]))
        ed_rooms.setPlaceholderText("Number of rooms")
        ed_rate = QLineEdit(str(row["RoomRate"]))
        ed_rate.setPlaceholderText("Room rate per night")
        form.addRow("Guest Name", ed_guest)
        form.addRow("Arrival", de_arr)
        form.addRow("Departure", de_dep)
        form.addRow("Adults", ed_adult)
        form.addRow("Rooms", ed_rooms)
        form.addRow("Rate", ed_rate)
        lay = QVBoxLayout(dlg); lay.addLayout(form)
        brow = QHBoxLayout()
        ok = QPushButton("Save"); ok.setToolTip("Save changes to reservation")
        cancel = QPushButton("Cancel"); cancel.setToolTip("Discard changes and close")
        brow.addStretch(); brow.addWidget(ok); brow.addWidget(cancel)
        lay.addLayout(brow)
        ok.clicked.connect(dlg.accept); cancel.clicked.connect(dlg.reject)
        ok.setDefault(True)   # VB6 pattern: Enter = Save
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            reservation.update(
                bookno, ed_guest.text(), de_arr.date().toPyDate(),
                de_dep.date().toPyDate(), adults=int(ed_adult.text() or 1),
                rooms=int(ed_rooms.text() or 1),
                rate=float(ed_rate.text() or 0), user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Edit", str(e)); return
        except Exception as e:
            QMessageBox.critical(self, "Edit", f"DB error: {e}"); return
        self.lblState.setText(f"State: Idle | #{bookno} updated")
        self.reload(keep_bookno=bookno)

    def _cancel(self):
        bookno = self._selected_bookno()
        if bookno is None:
            QMessageBox.information(self, "Cancel", "Pehle row select karo")
            return
        try:
            self._require_pyt(bookno)
        except ValueError as e:
            QMessageBox.warning(self, "Cancel", str(e)); return
        if QMessageBox.question(
                self, "Cancel Booking",
                f"#{bookno} cancel karein? (VB6 flow: Cancel='Y', "
                "record rahega)") != QMessageBox.StandardButton.Yes:
            return
        try:
            reservation.cancel(bookno, user=self.user)
        except ValueError as e:
            QMessageBox.warning(self, "Cancel", str(e)); return
        except Exception as e:
            QMessageBox.critical(self, "Cancel", f"DB error: {e}"); return
        self.lblState.setText(f"State: Idle | #{bookno} cancelled")
        self.reload(keep_bookno=bookno)


def main() -> int:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    d = ReservationBrowser()
    d.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
