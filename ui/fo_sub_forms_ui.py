"""Front Office Sub-Forms UI (VB6: FdLookUpRoomNo, FrmMergeCharge,
FdReSetlement, fdRoomChange port)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QGroupBox, QFormLayout, QHeaderView, QComboBox,
    QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from core import db, fo_ops
from core.folio import PAY_TYPES as _PAY_TYPES
from ui.theme import palette


class RoomLookupWindow(QMainWindow):
    """Room Number Lookup (VB6: FdLookUpRoomNo)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Number Lookup")
        self.resize(600, 400)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Room Number Lookup")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        search_lay = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search room number...")
        self.txt_search.textChanged.connect(self._filter)
        search_lay.addWidget(QLabel("Search:"))
        search_lay.addWidget(self.txt_search)
        layout.addLayout(search_lay)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Room No", "Category", "Status", "Guest Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_exit = QPushButton("Exit"); btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

    def _load_data(self):
        try:
            rows = db.query(
                "SELECT R.Code, RC.Name, R.RoomStat, "
                "ISNULL(GP.Name, '') as GuestName "
                "FROM RoomMast R "
                "LEFT JOIN RoomCat RC ON R.RoomCat = RC.Code "
                "LEFT JOIN RoomOcc G ON R.Code = G.RoomNo AND G.Type = 'I' "
                "LEFT JOIN GuestProf GP ON G.GuestProf = GP.Code "
                "ORDER BY R.Code")
            self._all_rows = rows
            self._populate(rows)
        except Exception:
            self._all_rows = []

    def _populate(self, rows):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate([r[0] or "", r[1] or "", r[2] or "", r[3] or ""]):
                it = QTableWidgetItem(str(v))
                it.setForeground(QColor(palette()["text"]))
                self.table.setItem(i, j, it)

    def _filter(self, text):
        text = text.strip().lower()
        if not text:
            self._populate(self._all_rows); return
        filtered = [r for r in self._all_rows if text in str(r[0] or "").lower()
                     or text in str(r[1] or "").lower() or text in str(r[3] or "").lower()]
        self._populate(filtered)


class RoomChangeWindow(QMainWindow):
    """Room Change (VB6: fdRoomChange port)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Change")
        self.resize(680, 480)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Room Change")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        find = QGroupBox("Guest locate")
        fl = QHBoxLayout(find)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Room No ya Check-in DocId")
        self.txt_search.returnPressed.connect(self._load_folio)
        self.btn_load = QPushButton("Load Folio")
        self.btn_load.setToolTip("Search the in-house folio for the room or DocId")
        self.btn_load.clicked.connect(self._load_folio)
        fl.addWidget(QLabel("Search:")); fl.addWidget(self.txt_search, 1)
        fl.addWidget(self.btn_load)
        layout.addWidget(find)

        info = QGroupBox("Current stay")
        form = QFormLayout(info)
        self.lbl_folio = QLabel("-"); self.lbl_guest = QLabel("-")
        self.lbl_oldroom = QLabel("-")
        form.addRow("Folio:", self.lbl_folio)
        form.addRow("Guest:", self.lbl_guest)
        form.addRow("Current Room:", self.lbl_oldroom)
        layout.addWidget(info)

        change = QGroupBox("New room")
        cf = QFormLayout(change)
        self.cmb_newroom = QComboBox(); self.cmb_newroom.setEditable(True)
        self.cmb_newroom.setToolTip("Free 'RO' rooms (RoomMast - open RoomOcc)")
        self._fill_free_rooms()
        self.txt_reason = QLineEdit()
        self.txt_reason.setPlaceholderText("e.g. AC fault, guest request...")
        cf.addRow("New Room:", self.cmb_newroom)
        cf.addRow("Reason:", self.txt_reason)
        layout.addWidget(change)

        btn_lay = QHBoxLayout()
        self.btn_save = QPushButton("Save Room Change")
        self.btn_save.setProperty("role", "warning")
        self.btn_save.clicked.connect(self._save)
        self.btn_exit = QPushButton("Exit"); self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_save); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)
        self._docid = ""
        self.btn_save.setEnabled(False)

    def _fill_free_rooms(self):
        self.cmb_newroom.clear()
        try:
            for room in fo_ops.free_rooms():
                self.cmb_newroom.addItem(room)
        except Exception:
            pass

    def _load_folio(self):
        q = self.txt_search.text().strip()
        if not q:
            QMessageBox.warning(self, "Input", "Room No ya DocId likho"); return
        rec = fo_ops.open_folio_by_docid(q, cn=None)
        if not rec:
            rec = fo_ops.open_folio_by_room(q, cn=None)
        if not rec:
            QMessageBox.information(self, "Not found",
                                    "Koi in-house guest nahi mila"); return
        # current open room confirm
        occ = db.query("SELECT TOP 1 RTRIM(RoomNo) FROM RoomOcc "
                       "WHERE DocId = ? AND ChkOutDate IS NULL",
                       (rec["docid"],))
        self._docid = rec["docid"]
        self.lbl_folio.setText(str(rec["folio"]))
        self.lbl_guest.setText(f"{rec['name']}  ({rec['guestprof']})")
        self.lbl_oldroom.setText(occ[0][0].strip() if occ else "-")
        self._fill_free_rooms()
        self.btn_save.setEnabled(True)

    def _save(self):
        new_room = self.cmb_newroom.currentText().strip()
        if not new_room:
            QMessageBox.warning(self, "Input", "New Room select karo"); return
        reason = self.txt_reason.text().strip()
        reply = QMessageBox.question(self, "Confirm",
            f"Guest ko {self.lbl_oldroom.text()} -> {new_room} shift karein?")
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            res = fo_ops.room_change(self._docid, new_room, reason)
            QMessageBox.information(self, "Done",
                f"Room changed to {res['new_room']}\n"
                f"Old room {res['old_room']} dirty marked.")
            self._load_folio()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MergeChargeWindow(QMainWindow):
    """Merge Charges (VB6: FrmMergeCharge)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Room Charges")
        self.resize(640, 460)
        self._build_ui()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Merge Room Charges")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QGroupBox("Rooms")
        form_lay = QFormLayout(form)
        self.txt_from_room = QLineEdit(); self.txt_from_room.setPlaceholderText("Source Room No")
        self.txt_from_room.textChanged.connect(lambda _: self._refresh())
        self.txt_to_room = QLineEdit(); self.txt_to_room.setPlaceholderText("Target Room No")
        self.txt_to_room.textChanged.connect(lambda _: self._refresh())
        self.lbl_src = QLabel("-"); self.lbl_tgt = QLabel("-")
        form_lay.addRow("From Room:", self.txt_from_room)
        form_lay.addRow("(source folio)", self.lbl_src)
        form_lay.addRow("To Room:", self.txt_to_room)
        form_lay.addRow("(target folio)", self.lbl_tgt)
        layout.addWidget(form)

        self.lbl_total = QLabel("Source folio charges: -")
        layout.addWidget(self.lbl_total)
        info = QLabel("Source room ke saare charges target room me shift ho "
                      "jayenge aur source folio target se link ho jayega.")
        info.setWordWrap(True); layout.addWidget(info)

        btn_lay = QHBoxLayout()
        self.btn_merge = QPushButton("Merge Charges")
        self.btn_merge.setProperty("role", "danger")
        self.btn_merge.setEnabled(False)
        self.btn_exit = QPushButton("Exit")
        self.btn_merge.clicked.connect(self._merge)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_merge); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _refresh(self):
        src = self.txt_from_room.text().strip()
        tgt = self.txt_to_room.text().strip()
        self.lbl_src.setText("-"); self.lbl_tgt.setText("-")
        self.lbl_total.setText("Source folio charges: -")
        self.btn_merge.setEnabled(False)
        if src:
            s = fo_ops.open_folio_by_room(src, cn=None)
            if s:
                self.lbl_src.setText(f"{s['folio']} - {s['name']}")
                try:
                    tot = fo_ops.folio_charge_total(s["docid"])
                    self.lbl_total.setText(f"Source folio charges: {tot:,.2f}")
                except Exception:
                    pass
        if tgt:
            t = fo_ops.open_folio_by_room(tgt, cn=None)
            if t:
                self.lbl_tgt.setText(f"{t['folio']} - {t['name']}")
        if src and tgt and src != tgt and self.lbl_src.text() != "-" and \
                self.lbl_tgt.text() != "-":
            self.btn_merge.setEnabled(True)

    def _merge(self):
        from_room = self.txt_from_room.text().strip()
        to_room = self.txt_to_room.text().strip()
        reply = QMessageBox.question(self, "Confirm",
            f"Merge charges from {from_room} to {to_room}?\nYeh undo nahi ho sakta!")
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            res = fo_ops.merge_charge(from_room, to_room)
            QMessageBox.information(self, "Done",
                f"{res['rows_moved']} rows merged\n"
                f"Folio {res['folio_from']} -> {res['folio_to']}")
            self.txt_from_room.clear(); self.txt_to_room.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ReSettlementWindow(QMainWindow):
    """Bill Re-Settlement (VB6: FdReSetlement)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill Re-Settlement")
        self.resize(720, 540)
        self._build_ui()
        self._docid = ""
        self._pending = []

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Bill Re-Settlement")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        find = QHBoxLayout()
        self.txt_folio = QLineEdit()
        self.txt_folio.setPlaceholderText("Folio DocId ya Room No")
        self.txt_folio.returnPressed.connect(self._load)
        self.btn_load = QPushButton("Load")
        self.btn_load.setToolTip("Load the folio's current settlement receipts")
        self.btn_load.clicked.connect(self._load)
        find.addWidget(QLabel("Folio/Room:")); find.addWidget(self.txt_folio, 1)
        find.addWidget(self.btn_load)
        layout.addLayout(find)

        self.lbl_folio = QLabel("-"); layout.addWidget(self.lbl_folio)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["DocId", "VNo", "Date", "PayType", "Amount", "Comments"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        newg = QGroupBox("New settlement")
        nl = QHBoxLayout(newg)
        self.cmb_paycode = QComboBox()
        for code, label in _PAY_TYPES.items():
            self.cmb_paycode.addItem(f"{label} ({code})", code)
        self.spn_amount = QDoubleSpinBox(); self.spn_amount.setRange(0, 1_000_000_000)
        self.spn_amount.setDecimals(2); self.spn_amount.setMinimumWidth(140)
        self.txt_comment = QLineEdit(); self.txt_comment.setPlaceholderText("BY CASH / BY UPI...")
        self.btn_add = QPushButton("Add Line")
        self.btn_add.setToolTip("Add a settlement line to the new split")
        self.btn_add.clicked.connect(self._add_line)
        nl.addWidget(QLabel("Pay:")); nl.addWidget(self.cmb_paycode)
        nl.addWidget(QLabel("Amt:")); nl.addWidget(self.spn_amount)
        nl.addWidget(QLabel("Note:")); nl.addWidget(self.txt_comment, 1)
        nl.addWidget(self.btn_add)
        layout.addWidget(newg)

        self.new_table = QTableWidget()
        self.new_table.setColumnCount(4)
        self.new_table.setHorizontalHeaderLabels(["PayCode", "Amount", "Comments", ""])
        self.new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.new_table.setMinimumHeight(120)
        layout.addWidget(self.new_table)

        btn_lay = QHBoxLayout()
        self.btn_settle = QPushButton("Re-Settle Bill")
        self.btn_settle.setProperty("role", "warning")
        self.btn_settle.setEnabled(False)
        self.btn_exit = QPushButton("Exit")
        self.btn_settle.clicked.connect(self._settle)
        self.btn_exit.clicked.connect(self.close)
        btn_lay.addWidget(self.btn_settle); btn_lay.addWidget(self.btn_exit)
        layout.addLayout(btn_lay)

    def _load(self):
        q = self.txt_folio.text().strip()
        if not q:
            QMessageBox.warning(self, "Input", "Folio DocId ya Room No likho"); return
        rec = fo_ops.open_folio_by_docid(q, cn=None)
        if not rec:
            rec = fo_ops.open_folio_by_room(q, cn=None)
        if not rec:
            QMessageBox.information(self, "Not found", "Koi folio nahi mila")
            return
        self._docid = rec["docid"]
        self.lbl_folio.setText(f"Folio {rec['folio']} - {rec['name']}")
        try:
            rows = fo_ops.list_settlements(self._docid)
        except Exception:
            rows = []
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [r["docid"], str(r["vno"]), str(r["vdate"]),
                    r["paytype"], f"{r['amount']:,.2f}", r["comments"]]
            for j, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setForeground(QColor(palette()["text"]))
                self.table.setItem(i, j, it)
        self.btn_settle.setEnabled(bool(self._pending))

    def _add_line(self):
        item = self.cmb_paycode.currentItem()
        code = item.data(Qt.ItemDataRole.UserRole) if item else "KKCASH"
        amt = self.spn_amount.value()
        if amt <= 0:
            QMessageBox.warning(self, "Input", "Amount > 0 hona chahiye"); return
        self._pending.append({"paycode": code, "amount": amt,
                              "comments": self.txt_comment.text().strip()})
        self._render_pending()
        self.spn_amount.setValue(0); self.txt_comment.clear()

    def _render_pending(self):
        self.new_table.setRowCount(len(self._pending))
        for i, row in enumerate(self._pending):
            it0 = QTableWidgetItem(row["paycode"])
            it1 = QTableWidgetItem(f"{row['amount']:,.2f}")
            it2 = QTableWidgetItem(row["comments"])
            it3 = QTableWidgetItem("remove")
            it3.setForeground(QColor("#c0392b"))
            self.new_table.setItem(i, 0, it0)
            self.new_table.setItem(i, 1, it1)
            self.new_table.setItem(i, 2, it2)
            self.new_table.setItem(i, 3, it3)
        self.btn_settle.setEnabled(bool(self._pending))

    def _settle(self):
        if not self._pending:
            QMessageBox.warning(self, "Input", "Koi nayi settlement line nahi"); return
        reply = QMessageBox.question(self, "Confirm",
            "Purana settlement reverse karke naya post karein?")
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            res = fo_ops.re_settlement(self._docid, list(self._pending))
            QMessageBox.information(self, "Done",
                f"Old receipt {res['old_receipt']} reverse "
                f"(total {res['total']:,.2f})\n"
                f"Naye receipts: {', '.join(str(v) for v in res['new_vnos'])}")
            self._pending = []; self._render_pending(); self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def open_room_lookup(parent=None):
    w = RoomLookupWindow(parent); w.show(); return w

def open_room_change(parent=None):
    w = RoomChangeWindow(parent); w.show(); return w

def open_merge_charge(parent=None):
    w = MergeChargeWindow(parent); w.show(); return w

def open_re_settlement(parent=None):
    w = ReSettlementWindow(parent); w.show(); return w