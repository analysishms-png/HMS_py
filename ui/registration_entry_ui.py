"""Registration Entry UI (VB6: RegistrationEntry - quick FO registration).

Uses checkin.py core for all GuestFolio + RoomOcc + FolioLog writes.
GuestFolio actual columns: DocId, FolioNo, Vtype, Vprefix, Vdate,
GuestProf, Name, City, NoDays, DepDate, BookingDocId, Site_Code,
U_Name, U_EntDt, U_AE, LogSite_Code.

PYT-guard: PYT* names only (production via VB6 EXE).
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QGroupBox, QFormLayout, QMessageBox, QDateEdit, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from HMS_py.core import db, checkin, guestprof
from HMS_py.ui import theme as _theme


class RegistrationEntryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registration Entry")
        self.setMinimumSize(900, 600)
        self.resize(900, 600)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = QLabel("Registration Entry")
        title.setStyleSheet("font-size: 16px; font-weight: 700; padding: 4px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(title)

        form = QGroupBox("Guest Registration")
        fl = QFormLayout(form)
        fl.setSpacing(10)
        fl.setContentsMargins(16, 12, 16, 12)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Guest full name (PYT* for test)")
        self.txt_guestprof = QLineEdit()
        self.txt_guestprof.setPlaceholderText("Leave blank for auto KK######")
        self.txt_city = QLineEdit("KK0002")
        self.txt_city.setPlaceholderText("City code (e.g. KK0002)")
        self.dt_arr = QDateEdit()
        self.dt_arr.setCalendarPopup(True)
        self.dt_arr.setDate(QDate.currentDate())
        self.dt_dep = QDateEdit()
        self.dt_dep.setCalendarPopup(True)
        self.dt_dep.setDate(QDate.currentDate().addDays(1))
        self.txt_room = QLineEdit()
        self.txt_room.setPlaceholderText("Leave blank for auto room assign")
        self.txt_bookdocid = QLineEdit()
        self.txt_bookdocid.setPlaceholderText("BookingDocId (optional)")
        self.txt_adult = QLineEdit("1")
        self.txt_adult.setPlaceholderText("Adult count (default 1)")
        self.txt_child = QLineEdit("0")
        self.txt_child.setPlaceholderText("Children count (default 0)")
        self.txt_ratecode = QLineEdit()
        self.txt_ratecode.setPlaceholderText("RateCode (optional)")
        self.txt_chkin = QLineEdit(datetime.datetime.now().strftime("%H:%M"))
        self.txt_chkin.setPlaceholderText("Check-In time HH:MM")

        fl.addRow("Guest Name *:", self.txt_name)
        fl.addRow("GuestProf Code:", self.txt_guestprof)
        fl.addRow("City:", self.txt_city)
        fl.addRow("Arrival:", self.dt_arr)
        fl.addRow("Departure:", self.dt_dep)
        fl.addRow("Room No:", self.txt_room)
        fl.addRow("BookingDocId:", self.txt_bookdocid)
        fl.addRow("Adult:", self.txt_adult)
        fl.addRow("Children:", self.txt_child)
        fl.addRow("RateCode:", self.txt_ratecode)
        fl.addRow("ChkInTime:", self.txt_chkin)
        root.addWidget(form)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)
        btn_lay.addStretch()
        self.btn_save = QPushButton("Save Registration")
        self.btn_save.setProperty("role", "success")
        self.btn_save.setMinimumHeight(36)
        self.btn_save.setToolTip("Create check-in record (GuestFolio + RoomOcc + FolioLog)")
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setMinimumHeight(36)
        self.btn_exit.setToolTip("Close this window")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save)
        btn_lay.addWidget(self.btn_exit)
        root.addLayout(btn_lay)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Folio", "VDate", "Name", "GuestProf", "City",
             "Days", "DepDate", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table)

    def _load_data(self):
        try:
            rows = checkin.list_checkins(top=100)
            self.table.setRowCount(len(rows))
            p = _theme.palette()
            for i, rec in enumerate(rows):
                vals = [
                    rec["folio"],
                    rec["vdate"],
                    rec["name"],
                    rec["guestprof"],
                    rec["city"],
                    rec["nodays"],
                    rec["depdate"],
                    rec["u_ae"],
                ]
                for j, v in enumerate(vals):
                    if isinstance(v, (datetime.date, datetime.datetime)):
                        v = f"{v:%Y-%m-%d}"
                    it = QTableWidgetItem("" if v is None else str(v))
                    it.setForeground(QColor(p["text"]))
                    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(i, j, it)
        except Exception:
            pass

    def _save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Input", "Guest name is required")
            return
        try:
            arr_date = self.dt_arr.date().toPyDate()
            dep_date = self.dt_dep.date().toPyDate()
            gcode = self.txt_guestprof.text().strip()
            if not gcode:
                gcode = guestprof.next_code()
                guestprof.insert({"code": gcode, "name": name,
                                  "city": self.txt_city.text().strip()})
            try:
                n_adult = int(self.txt_adult.text().strip() or "1")
                n_child = int(self.txt_child.text().strip() or "0")
            except ValueError:
                QMessageBox.warning(self, "Input",
                                    "Adult/Children integer hone chahiye")
                return
            folio = checkin.create_checkin(
                gcode, name, arr_date, dep_date,
                city=self.txt_city.text().strip(),
                roomno=self.txt_room.text().strip(),
                bookingdocid=self.txt_bookdocid.text().strip(),
                adult=n_adult, children=n_child,
                ratecode=self.txt_ratecode.text().strip(),
                chkintime=self.txt_chkin.text().strip())
            QMessageBox.information(
                self, "Saved",
                f"Check-In #{folio} created.\n"
                f"DocId: {checkin.make_docid(checkin.SITE_CODE, '2026', folio)}")
            self._load_data()
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_registration_entry(parent=None):
    w = RegistrationEntryWindow(parent)
    w.show()
    return w
