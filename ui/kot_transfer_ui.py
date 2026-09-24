"""POS KOT Transfer / Table Change UI (VB6: RsTbChange, RsKOTTransfer port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QGroupBox, QFormLayout, QComboBox, QCheckBox,
    QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from core import db, pos_kot
from ui.theme import palette


def _outlets() -> list[tuple]:
    """RestCode + name (shop/outlet). Depart master + default FOM."""
    rows = db.query("SELECT RTRIM(Code), RTRIM(Name) FROM Depart "
                    "ORDER BY Code")
    return [("KKFOM", "Front Office (KKFOM)")] + [(r[0], r[1]) for r in rows]


class TableChangeWindow(QMainWindow):
    """Table Change (VB6: RsTbChange)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Table Change Entry")
        self.resize(640, 460)
        self._build_ui()
        self._load_outlets()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Table Change Entry")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Table move")
        fl = QFormLayout(form)
        self.cmb_outlet = QComboBox()
        self.cmb_outlet.currentIndexChanged.connect(self._load_tables)
        self.cmb_from = QComboBox()
        self.cmb_from.currentIndexChanged.connect(self._load_kots)
        self.txt_to = QLineEdit()
        self.txt_to.setPlaceholderText("Target Table No, e.g. T5")
        fl.addRow("Outlet:", self.cmb_outlet)
        fl.addRow("From Table:", self.cmb_from)
        fl.addRow("To Table:", self.txt_to)
        layout.addWidget(form)

        self.lbl_pending = QLabel("Pending KOTs: -")
        layout.addWidget(self.lbl_pending)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["DocId", "VNo", "Date", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("Change Table")
        self.btn_save.setProperty("role", "warning")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit = QPushButton("Exit"); self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _load_outlets(self):
        self.cmb_outlet.blockSignals(True)
        self.cmb_outlet.clear()
        try:
            for code, name in _outlets():
                self.cmb_outlet.addItem(f"{code} - {name}", code)
        except Exception:
            self.cmb_outlet.addItem("KKFOM - Front Office", "KKFOM")
        self.cmb_outlet.blockSignals(False)
        self._load_tables()

    def _load_tables(self):
        rest = self.cmb_outlet.currentData() or "KKFOM"
        self.cmb_from.blockSignals(True)
        self.cmb_from.clear()
        try:
            for t in pos_kot.pending_kot_tables(rest, cn=None):
                self.cmb_from.addItem(
                    f"Table {t['roomno']} ({t['pending']} pending)", t["roomno"])
        except Exception:
            pass
        self.cmb_from.blockSignals(False)
        self._load_kots()

    def _load_kots(self):
        rest = self.cmb_outlet.currentData() or "KKFOM"
        tbl = self.cmb_from.currentData() or ""
        self.table.setRowCount(0)
        self.lbl_pending.setText(f"Pending KOTs ({rest} / Table {tbl}): -")
        try:
            rows = pos_kot.pending_kot_list(rest, table=tbl, cn=None)
        except Exception:
            rows = []
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate([r["docid"], str(r["vno"]),
                                   str(r["vdate"]), r["vtime"]]):
                it = QTableWidgetItem(v)
                it.setForeground(QColor(palette()["text"]))
                self.table.setItem(i, j, it)
        self.lbl_pending.setText(f"Pending KOTs ({rest} / Table {tbl}): {len(rows)}")

    def _save(self):
        rest = self.cmb_outlet.currentData() or "KKFOM"
        frm = self.cmb_from.currentData() or ""
        to = self.txt_to.text().strip()
        if not frm or not to:
            QMessageBox.warning(self, "Input", "From/To table dono zaroori hain"); return
        reply = QMessageBox.question(self, "Confirm",
            f"Table {frm} ke saare pending KOTs table {to} pe shift karein?"
            f"\n\nYeh undo nahi ho sakta!")
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            n = pos_kot.table_change(rest, frm, to)
            QMessageBox.information(self, "Done", f"{n} KOT(s) shifted")
            self._load_tables(); self.txt_to.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class KOTTransferWindow(QMainWindow):
    """KOT Transfer (VB6: RsKOTTransfer)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KOT Transfer")
        self.resize(660, 480)
        self._build_ui()
        self._load_outlets()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("KOT Transfer")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("KOT move")
        fl = QFormLayout(form)
        self.cmb_outlet = QComboBox()
        self.cmb_outlet.currentIndexChanged.connect(self._load_kots)
        self.chk_room = QCheckBox("Room Service (target room se RoomCat le) ")
        self.chk_room.toggled.connect(self._load_kots)
        self.cmb_kot = QComboBox()
        self.txt_to = QLineEdit()
        self.txt_to.setPlaceholderText("Target Table/Room No")
        fl.addRow("Outlet:", self.cmb_outlet)
        fl.addRow("", self.chk_room)
        fl.addRow("KOT:", self.cmb_kot)
        fl.addRow("To Table/Room:", self.txt_to)
        layout.addWidget(form)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["DocId", "VNo", "Room", "Date", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self._pick_kot)
        layout.addWidget(self.table)

        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("Transfer KOT")
        self.btn_save.setProperty("role", "warning")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit = QPushButton("Exit"); self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _load_outlets(self):
        self.cmb_outlet.blockSignals(True)
        self.cmb_outlet.clear()
        try:
            for code, name in _outlets():
                self.cmb_outlet.addItem(f"{code} - {name}", code)
        except Exception:
            self.cmb_outlet.addItem("KKFOM - Front Office", "KKFOM")
        self.cmb_outlet.blockSignals(False)
        self._load_kots()

    def _load_kots(self):
        rest = self.cmb_outlet.currentData() or "KKFOM"
        try:
            rows = pos_kot.pending_kot_list(rest, table="", cn=None)
        except Exception:
            rows = []
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate([r["docid"], str(r["vno"]), r["roomno"],
                                   str(r["vdate"]), r["vtime"]]):
                it = QTableWidgetItem(v)
                it.setForeground(QColor(palette()["text"]))
                self.table.setItem(i, j, it)
        self.cmb_kot.blockSignals(True)
        self.cmb_kot.clear()
        for r in rows:
            label = r["docid"] if self.chk_room.isChecked() else str(r["vno"])
            self.cmb_kot.addItem(f"{label}  (room {r['roomno']}, VNo {r['vno']})",
                                 r["docid"])
        self.cmb_kot.blockSignals(False)

    def _pick_kot(self, item):
        row = item.row()
        docid = self.table.item(row, 0).text()
        self.cmb_kot.setCurrentIndex(self.cmb_kot.findData(docid))

    def _save(self):
        rest = self.cmb_outlet.currentData() or "KKFOM"
        to = self.txt_to.text().strip()
        if self.cmb_kot.currentData() is None:
            QMessageBox.warning(self, "Input", "Koi pending KOT nahi mila"); return
        kot = self.cmb_kot.currentData()
        if self.chk_room.isChecked():
            ref = kot  # Room Service reference = KOT DocId
        else:
            ref = self.cmb_kot.currentText().split("  ")[0].strip()
        if not to or not ref:
            QMessageBox.warning(self, "Input", "KOT aur target table/room zaroori hain"); return
        reply = QMessageBox.question(self, "Confirm",
            f"KOT {ref} -> {to} transfer karein?")
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            res = pos_kot.kot_transfer(rest, ref, to, room_service=self.chk_room.isChecked())
            msg = f"{res['affected']} KOT row(s) transfer"
            if res["roomcat_updated"]:
                msg += " + RoomCat synced"
            QMessageBox.information(self, "Done", msg)
            self._load_kots(); self.txt_to.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_table_change(parent=None):
    w = TableChangeWindow(parent); w.show(); return w

def open_kot_transfer(parent=None):
    w = KOTTransferWindow(parent); w.show(); return w