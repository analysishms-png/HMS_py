"""Guest History viewer (VB6-style live DB browser).

This is a real read-only viewer for guest history patterns using the live HMS
schema. It does not invent new tables; it reads from GuestFolio, RoomOcc,
GuestProf, and payment/charge references already present in the database.
"""
from __future__ import annotations

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from HMS_py.core import db
from HMS_py.ui import theme as _theme


_APP = None


def _ensure_qapp():
    global _APP
    _APP = QApplication.instance() or QApplication(["HMS_py"])
    return _APP


_ensure_qapp()


def _cell(val) -> QTableWidgetItem:
    it = QTableWidgetItem("" if val is None else str(val))
    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
    it.setForeground(QColor(_theme.palette()["text"]))
    return it


class GuestHistoryViewer(QDialog):
    COLS = ["Folio", "DocId", "Guest", "Room", "Arrival", "Departure",
            "Status", "GuestProf", "User", "Site"]

    def __init__(self, parent=None, user: str = "SA"):
        _ensure_qapp()
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Guest History - HMS_py")
        self.resize(1100, 560)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Guest History (live DB view: GuestFolio + RoomOcc)"))

        self.tbl = QTableWidget(0, len(self.COLS))
        self.tbl.setHorizontalHeaderLabels(self.COLS)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.tbl)

        btns = QHBoxLayout()
        self.btnRefresh = QPushButton("Refresh")
        self.btnRefresh.setToolTip("Reload guest history from database")
        self.btnClose = QPushButton("Close")
        self.btnClose.setToolTip("Close this window")
        self.btnRefresh.clicked.connect(self.reload)
        self.btnClose.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(self.btnRefresh); btns.addWidget(self.btnClose)
        root.addLayout(btns)

        self.reload()

    def reload(self):
        try:
            rows = db.query(
                "SELECT TOP 200 gf.FolioNo, gf.DocId, gf.Name, ro.RoomNo, "
                "gf.VDate, gf.DepDate, "
                "CASE WHEN ro.ChkOutDate IS NULL THEN 'In-House' ELSE 'Checked Out' END AS Status, "
                "gf.GuestProf, gf.U_Name, gf.Site_Code "
                "FROM GuestFolio gf LEFT JOIN RoomOcc ro ON ro.DocId = gf.DocId "
                "WHERE gf.Site_Code = ? AND gf.Vprefix = ? "
                "ORDER BY gf.FolioNo DESC",
                ("KK", "2026"),
            )
            self.tbl.setRowCount(len(rows))
            for r, rec in enumerate(rows):
                vals = [
                    rec[0], rec[1], rec[2], rec[3], rec[4], rec[5],
                    rec[6], rec[7], rec[8], rec[9],
                ]
                for c, v in enumerate(vals):
                    self.tbl.setItem(r, c, _cell(v))
        except Exception as e:
            QMessageBox.warning(self, "Guest History", f"Load error: {e}")


def open_guest_history(parent=None, user: str = "SA"):
    GuestHistoryViewer(parent, user=user).exec()


def main() -> int:
    app = QApplication(sys.argv)
    w = GuestHistoryViewer()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
