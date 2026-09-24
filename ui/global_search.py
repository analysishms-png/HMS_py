"""Global Command / Search Dialog for Analysis HMS.

Searches across:
- Guests (GuestProf)
- Reservations (Booking)
- In-House & Checked-Out Folios (GuestFolio)
- Rooms (RoomMast)

Keyboard-first: arrow keys to navigate results, Enter to open, Esc to dismiss.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QFrame
)

from HMS_py.ui import theme as _theme


class GlobalSearchDialog(QDialog):
    """Command Search popup across all PMS entities."""

    itemSelected = pyqtSignal(str, str)  # (entity_type, entity_id)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Search")
        self.setFixedSize(650, 480)
        self.setModal(True)

        p = _theme.palette()

        self.setStyleSheet(f"""
            QDialog {{
                background: {p.get('surface_solid', '#ffffff')};
                border: 1px solid {p.get('border', '#cbd5e1')};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Header Search Input
        search_box = QFrame()
        search_box.setStyleSheet(f"""
            QFrame {{
                background: {p.get('surface', 'rgba(255,255,255,0.8)')};
                border: 2px solid {p.get('accent', '#4f46e5')};
                border-radius: 8px;
                padding: 2px 8px;
            }}
        """)
        s_lay = QHBoxLayout(search_box)
        s_lay.setContentsMargins(4, 2, 4, 2)
        s_lay.setSpacing(6)

        ico = QLabel("🔍")
        ico.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        s_lay.addWidget(ico)

        self.txtSearch = QLineEdit()
        self.txtSearch.setPlaceholderText("Search guest name, reservation #, folio #, phone, room...")
        self.txtSearch.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 13px;
                color: {p.get('text', '#111')};
            }}
        """)
        self.txtSearch.textChanged.connect(self._do_search)
        s_lay.addWidget(self.txtSearch)

        layout.addWidget(search_box)

        # Results Table
        self.tblResults = QTableWidget(0, 4)
        self.tblResults.setHorizontalHeaderLabels(["Type", "ID / Code", "Name / Details", "Status / Date"])
        self.tblResults.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tblResults.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tblResults.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tblResults.setAlternatingRowColors(True)
        self.tblResults.setStyleSheet(f"""
            QTableWidget {{
                background: {p.get('surface_solid', '#ffffff')};
                border: 1px solid {p.get('border', '#cbd5e1')};
                border-radius: 8px;
                gridline-color: {p.get('border', 'rgba(148,163,184,0.15)')};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {p.get('header_grad_top', '#f1f5f9')};
                color: {p.get('text', '#1e293b')};
                font-weight: bold;
                border: none;
                border-bottom: 2px solid {p.get('accent', '#4f46e5')};
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background: {p.get('accent', '#4f46e5')};
                color: #ffffff;
            }}
        """)
        self.tblResults.cellDoubleClicked.connect(self._on_select)
        layout.addWidget(self.tblResults)

        # Bottom Hint & Close
        bot = QHBoxLayout()
        hint = QLabel("💡 Press Enter or double-click to view | Esc to close")
        hint.setStyleSheet(f"font-size: 11px; color: {p.get('text_dim', '#64748b')};")
        bot.addWidget(hint)
        bot.addStretch()

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        bot.addWidget(btn_close)
        layout.addLayout(bot)

        # Default initial focus
        self.txtSearch.setFocus()

    def _do_search(self, query: str):
        query = query.strip()
        if len(query) < 2:
            self.tblResults.setRowCount(0)
            return

        from HMS_py.core import db
        pattern = f"%{query}%"
        results = []

        try:
            # 1. Guests (live cols: MobileNo, PhoneNo)
            q_guests = db.query(
                "SELECT TOP 10 Code, Name, MobileNo, City FROM GuestProf "
                "WHERE Name LIKE ? OR Code LIKE ? OR MobileNo LIKE ? OR PhoneNo LIKE ?",
                (pattern, pattern, pattern, pattern)
            )
            for r in q_guests:
                results.append(("Guest", r[0], f"{r[1]} ({r[3] or ''})", f"📱 {r[2] or 'No mobile'}"))

            # 2. Folios (GuestFolio has no Status col)
            q_folios = db.query(
                "SELECT TOP 10 FolioNo, Name, Vdate, DepDate FROM GuestFolio "
                "WHERE Name LIKE ? OR CAST(FolioNo AS VARCHAR) LIKE ?",
                (pattern, pattern)
            )
            for r in q_folios:
                st = "Departed" if r[3] else "In-House"
                dt_str = r[2].strftime("%d/%b/%Y") if hasattr(r[2], "strftime") else str(r[2])
                results.append(("Folio", str(r[0]), str(r[1]), f"{st} ({dt_str})"))

            # 3. Reservations (Booking.ResStatus, not Status)
            q_res = db.query(
                "SELECT TOP 10 BookNo, GuestName, VDate, ResStatus FROM Booking "
                "WHERE GuestName LIKE ? OR CAST(BookNo AS VARCHAR) LIKE ?",
                (pattern, pattern)
            )
            for r in q_res:
                dt_str = r[2].strftime("%d/%b/%Y") if hasattr(r[2], "strftime") else str(r[2])
                results.append(("Reservation", str(r[0]), str(r[1]), f"{r[3]} ({dt_str})"))

            # 4. Rooms
            q_rooms = db.query(
                "SELECT TOP 5 Code, Name, RoomCat, RoomStat FROM RoomMast "
                "WHERE Code LIKE ? OR Name LIKE ?",
                (pattern, pattern)
            )
            for r in q_rooms:
                st = "Dirty" if (r[3] or "").strip() == "D" else "Clean/Vacant"
                results.append(("Room", str(r[0]), f"{r[1]} ({r[2] or ''})", st))

        except Exception:
            pass

        self.tblResults.setRowCount(len(results))
        for i, (typ, id_code, name, info) in enumerate(results):
            self.tblResults.setItem(i, 0, QTableWidgetItem(typ))
            self.tblResults.setItem(i, 1, QTableWidgetItem(str(id_code)))
            self.tblResults.setItem(i, 2, QTableWidgetItem(str(name)))
            self.tblResults.setItem(i, 3, QTableWidgetItem(str(info)))

    def _on_select(self, row: int, col: int = 0):
        if row < 0 or row >= self.tblResults.rowCount():
            return
        entity_type = self.tblResults.item(row, 0).text()
        entity_id = self.tblResults.item(row, 1).text()
        self.itemSelected.emit(entity_type, entity_id)
        self.accept()

    def keyPressEvent(self, ev):
        if ev.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            curr = self.tblResults.currentRow()
            if curr >= 0:
                self._on_select(curr)
                return
        elif ev.key() == Qt.Key.Key_Down:
            if not self.tblResults.hasFocus():
                self.tblResults.setFocus()
                if self.tblResults.rowCount() > 0:
                    self.tblResults.selectRow(0)
                return
        super().keyPressEvent(ev)
