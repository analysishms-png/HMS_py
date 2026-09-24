"""General Setup UI (VB6: Main Setup -> General Setup + FO misc masters).

Forms ported (DB-verified tables):
  - RoomFeature: Room amenity/feature tags
  - GodownMast:  Inventory locations (shown in Utility section too)
  - Voucher_Type: Browse-only (config table - no user edits)
  - Enviro: System environment settings viewer (single-row, read-only browse)

Tables NOT ported (don't exist in this DB):
  - Parameter/HMSParam - use _coming_soon
  - Revenue Group Setting - use _coming_soon
  - Printing Parameters / Printing Setup - use _coming_soon
  - Revenue Wise Budget Entry - use _coming_soon

Run: python -m HMS_py.ui.general_setup_ui
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)
from HMS_py.core.general_setup import RoomFeatAPI, GodownAPI, VouchCatAPI, voucher_type_list
from HMS_py.ui.base_master import BaseMasterForm, Field, MasterConfig, make_delete_guard
from HMS_py.ui import theme as _theme


# ── Room Feature Master ───────────────────────────────────────
def roomfeat_config() -> MasterConfig:
    return MasterConfig(
        title="Room Features Master - HMS_py",
        columns=[("Code","code"),("Name","name")],
        fields=[
            Field("code","Feature Code", max_len=6, required=True),
            Field("name","Feature Name", max_len=30, required=True),
        ],
        api=RoomFeatAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── Godown / Location Master ──────────────────────────────────
def godown_config() -> MasterConfig:
    return MasterConfig(
        title="Godown / Location Master (Inventory) - HMS_py",
        columns=[("Code","code"),("Name","name"),("Short","short"),
                 ("Dept","dept"),("Sys","sysyn")],
        fields=[
            Field("code","Godown Code", max_len=6, required=True),
            Field("name","Godown Name", max_len=30, required=True),
            Field("short","Short Name", max_len=6),
            Field("dept","Department Code", max_len=6),
            Field("sysyn","System Y/N", max_len=1, default="N"),
        ],
        api=GodownAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── Voucher Type Browser (read-only) ─────────────────────────
def _vcell(val) -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


class VoucherTypeBrowser(QDialog):
    """Read-only Voucher_Type config browser
    (VB6: General Setup -> Voucher Environment)."""
    COLS = ["V_Type","Category","Description","Method","StartNo","ShortName"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voucher Type Browser (Read-Only) - HMS_py")
        self.resize(860, 480)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            "Voucher Type configuration (read-only — VB6 se set hoti hai)"))
        self.tbl = QTableWidget(0, len(self.COLS))
        self.tbl.setHorizontalHeaderLabels(self.COLS)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)
        btns = QHBoxLayout()
        btnR = QPushButton("Refresh (F5)")
        btnR.setToolTip("Reload voucher types from database")
        btnC = QPushButton("Close")
        btnC.setToolTip("Close this window")
        btnR.clicked.connect(self.reload)
        btnC.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(btnR); btns.addWidget(btnC)
        root.addLayout(btns)
        QShortcut(QKeySequence("F5"), self, activated=self.reload)
        self.reload()

    def reload(self):
        rows = voucher_type_list()
        self.tbl.setRowCount(len(rows))
        for r, rec in enumerate(rows):
            for c, k in enumerate(["vtype","category","desc",
                                    "method","startno","short"]):
                self.tbl.setItem(r, c, _vcell(rec.get(k, "")))
        if rows: self.tbl.selectRow(0)


# ── Enviro / System Settings viewer ──────────────────────────
class EnviroViewer(QDialog):
    """Single-row system environment settings viewer
    (VB6: General Setup -> Parameter / FA Environment)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Environment Settings (Read-Only) - HMS_py")
        self.resize(720, 480)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            "System Enviro settings (read-only — VB6 se configure hoti hain)"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Setting", "Value"])
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)
        btns = QHBoxLayout()
        btnR = QPushButton("Refresh"); btnR.setToolTip("Reload settings from database")
        btnC = QPushButton("Close"); btnC.setToolTip("Close this window")
        btnR.clicked.connect(self.reload); btnC.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(btnR); btns.addWidget(btnC)
        root.addLayout(btns)
        self.reload()

    def reload(self):
        from HMS_py.core import db
        cn = db.connect()
        try:
            cur = cn.cursor()
            cur.execute("SELECT TOP 1 * FROM Enviro")
            if cur.description:
                cols = [d[0] for d in cur.description]
                row = cur.fetchone()
                data = list(zip(cols, row)) if row else []
                self.tbl.setRowCount(len(data))
                for r, (k, v) in enumerate(data):
                    self.tbl.setItem(r, 0, _vcell(k))
                    self.tbl.setItem(r, 1, _vcell(v))
        except Exception as e:
            QMessageBox.warning(self, "Enviro", f"Load error: {e}")
        finally:
            cn.close()


# ── GuestParam viewer ─────────────────────────────────────────
class GuestParamViewer(QDialog):
    """GuestParam table viewer (VB6: Guest Parameters Setting)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guest Parameters (Read-Only) - HMS_py")
        self.resize(720, 400)
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Guest Parameters (read-only viewer)"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)
        btns = QHBoxLayout()
        btnC = QPushButton("Close"); btnC.clicked.connect(self.reject)
        btnC.setToolTip("Close this window")
        btns.addStretch(); btns.addWidget(btnC)
        root.addLayout(btns)
        self.reload()

    def reload(self):
        from HMS_py.core import db
        cn = db.connect()
        try:
            cur = cn.cursor()
            cur.execute("SELECT TOP 1 * FROM GuestParam")
            if cur.description:
                cols = [d[0] for d in cur.description]
                row = cur.fetchone()
                data = list(zip(cols, row)) if row else []
                self.tbl.setRowCount(len(data))
                for r, (k, v) in enumerate(data):
                    self.tbl.setItem(r, 0, _vcell(k))
                    self.tbl.setItem(r, 1, _vcell(v))
        except Exception as e:
            QMessageBox.warning(self, "GuestParam", f"Load error: {e}")
        finally:
            cn.close()


class PrintingSettingsViewer(QDialog):
    """VB6-style printing/report/temp configuration viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Printing Setup / Parameters - HMS_py")
        self.resize(820, 520)
        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            "Reports path, temporary folder, printer, and key Enviro print flags"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Setting", "Value"])
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)
        btns = QHBoxLayout()
        btnR = QPushButton("Refresh")
        btnR.setToolTip("Reload printing settings from database")
        btnC = QPushButton("Close")
        btnC.setToolTip("Close this window")
        btnR.clicked.connect(self.reload)
        btnC.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(btnR); btns.addWidget(btnC)
        root.addLayout(btns)
        self.reload()

    def reload(self):
        try:
            from HMS_py.core.general_setup import printing_settings_snapshot
            from HMS_py.core import db
            data = printing_settings_snapshot()
            rows = [
                ("Reports Path", data.get("reports")),
                ("Temp Folder", data.get("temp")),
                ("Printer", data.get("printer")),
                ("Site", data.get("site")),
                ("Company", data.get("company")),
            ]
            for key, value in sorted(data.get("enviro", {}).items()):
                rows.append((key, value))
            self.tbl.setRowCount(len(rows))
            for r, (k, v) in enumerate(rows):
                self.tbl.setItem(r, 0, _vcell(k))
                self.tbl.setItem(r, 1, _vcell(v))
        except Exception as e:
            QMessageBox.warning(self, "Printing Settings", f"Load error: {e}")


# ── open helpers ──────────────────────────────────────────────
def _open(cfg_fn, parent=None):
    BaseMasterForm(cfg_fn(), parent).exec()

def open_roomfeature(parent=None):     _open(roomfeat_config, parent)
def open_godown(parent=None):          _open(godown_config, parent)
def open_vouchertype(parent=None):     VoucherTypeBrowser(parent).exec()
def open_enviro(parent=None):          EnviroViewer(parent).exec()
def open_guestparam(parent=None):      GuestParamViewer(parent).exec()
def open_printing(parent=None):        PrintingSettingsViewer(parent).exec()
def open_vouchcat(parent=None):        _open(vouchcat_config, parent)


# ── Voucher Category Master ────────────────────────────────────
def vouchcat_config() -> MasterConfig:
    return MasterConfig(
        title="Voucher Category Master - HMS_py",
        columns=[("Code","code"),("Name","name"),("Nature","natur"),
                 ("CashBank","cashbank"),("Type","type")],
        fields=[
            Field("code","Voucher Code", max_len=6, required=True),
            Field("name","Voucher Name", max_len=30, required=True),
            Field("natur","Nature", max_len=10),
            Field("cashbank","Cash/Bank Y/N", max_len=1, default="N"),
            Field("type","Type", max_len=10),
            Field("cform","C-Form Y/N", max_len=1, default="N"),
            Field("tender","Tender Y/N", max_len=1, default="N"),
            Field("posdaybook","POS Day Book Y/N", max_len=1, default="N"),
            Field("guestac","Guest A/C Y/N", max_len=1, default="N"),
            Field("acpost","A/C Post Y/N", max_len=1, default="N"),
            Field("roundoff","Round Off", default="0"),
            Field("inwords","In Words Y/N", max_len=1, default="N"),
            Field("inwords2","In Words2 Y/N", max_len=1, default="N"),
        ],
        api=VouchCatAPI,
        delete_guard=make_delete_guard("PYT"),
    )


# ── Standalone launcher ───────────────────────────────────────
class GeneralSetupLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMS_py - General Setup Masters")
        self.resize(360, 320)
        c = QWidget(); lay = QVBoxLayout(c)
        for lbl, fn in (
            ("Room Features Master",          open_roomfeature),
            ("Godown / Location Master",       open_godown),
            ("Voucher Type Browser",           open_vouchertype),
            ("Voucher Category Master",        open_vouchcat),
            ("System Environment (Enviro)",    open_enviro),
            ("Guest Parameters",               open_guestparam),
            ("Printing Setup / Parameters",    open_printing),
        ):
            b = QPushButton(lbl); b.clicked.connect(fn); b.setToolTip(f"Open {lbl}"); lay.addWidget(b)
        self.setCentralWidget(c)


def main() -> int:
    app = QApplication(sys.argv)
    w = GeneralSetupLauncher(); w.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
