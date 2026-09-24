"""Front Office Modern Dashboard (Analysis HMS / Front Office PMS).

Features:
- Live KPI Summary Cards (Arrivals, Departures, In-House, Available, Occupied, Vacant, Dirty, Pending Payments)
- Quick Action Panel (+ New Reservation, Check-In, Check-Out, Guest Search, Room Status, Folio, Room Rack)
- Today's Arrivals & Today's Departures professional data tables with actions (View, Check-In, Check-Out)
- Interactive Room Rack Visual Grid (Filterable by All, Available, Occupied, Dirty, Maintenance)
- Room details popup with guest, stay, folio, and housekeeping status actions
- Direct live DB queries with robust fallback ("Database unavailable" if offline)
"""
from __future__ import annotations

import datetime
import os
import sys

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QSizePolicy, QDialog, QMessageBox, QTabWidget
)

from HMS_py.ui import theme as _theme


class StatCard(QFrame):
    """Modern PMS KPI Metric Card."""

    clicked = pyqtSignal(str)

    def __init__(self, key: str, title: str, value: str = "0", subtext: str = "",
                 icon: str = "", accent_color: str = "", parent=None):
        super().__init__(parent)
        self.key = key
        self.setProperty("glassCard", True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(96)
        self.setMaximumHeight(115)

        p = _theme.palette()
        self._accent = accent_color or p.get("accent", "#4f46e5")
        
        self.setStyleSheet(f"""
            QFrame[glassCard="true"] {{
                background: {p.get("surface", "rgba(255,255,255,0.7)")};
                border: 1px solid {p.get("border", "rgba(148,163,184,0.3)")};
                border-left: 4px solid {self._accent};
                border-radius: 10px;
            }}
            QFrame[glassCard="true"]:hover {{
                background: {p.get("surface_hover", "rgba(255,255,255,0.9)")};
                border-color: {self._accent};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(6)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 16px; color: {self._accent}; background: transparent; border: none;")
            header.addWidget(icon_lbl)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {p.get('text_dim', '#64748b')}; background: transparent; border: none;")
        header.addWidget(self.title_lbl)
        header.addStretch()

        layout.addLayout(header)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {p.get('text', '#1e293b')}; background: transparent; border: none;")
        layout.addWidget(self.val_lbl)

        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setStyleSheet(f"font-size: 10px; color: {p.get('text_dim', '#64748b')}; background: transparent; border: none;")
        layout.addWidget(self.sub_lbl)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(ev)

    def set_data(self, value: str, subtext: str = ""):
        self.val_lbl.setText(value)
        if subtext:
            self.sub_lbl.setText(subtext)


class RoomRackItem(QFrame):
    """Single room tile in the visual room rack."""

    clicked = pyqtSignal(dict)

    def __init__(self, room_data: dict, parent=None):
        super().__init__(parent)
        self.room_data = room_data
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(110, 85)

        status = room_data.get("status", "Vacant")
        p = _theme.palette()

        # Status colors
        if status == "Occupied":
            bg_color = "rgba(239, 68, 68, 0.15)"
            border_color = "#ef4444"
            badge_bg = "#ef4444"
            badge_fg = "#ffffff"
        elif status == "Dirty":
            bg_color = "rgba(245, 158, 11, 0.15)"
            border_color = "#f59e0b"
            badge_bg = "#f59e0b"
            badge_fg = "#ffffff"
        elif status in ("Maintenance", "Blocked"):
            bg_color = "rgba(107, 114, 128, 0.15)"
            border_color = "#6b7280"
            badge_bg = "#6b7280"
            badge_fg = "#ffffff"
        else: # Vacant / Available
            bg_color = "rgba(16, 185, 129, 0.15)"
            border_color = "#10b981"
            badge_bg = "#10b981"
            badge_fg = "#ffffff"

        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-width: 2.5px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(2)

        top_row = QHBoxLayout()
        r_num = QLabel(str(room_data.get("roomno", "")))
        r_num.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {p.get('text', '#111')}; background: transparent; border: none;")
        top_row.addWidget(r_num)
        top_row.addStretch()

        badge = QLabel(status[:3].upper())
        badge.setStyleSheet(f"background: {badge_bg}; color: {badge_fg}; font-size: 8px; font-weight: bold; padding: 2px 4px; border-radius: 4px; border: none;")
        top_row.addWidget(badge)
        lay.addLayout(top_row)

        rtype = QLabel(f"{room_data.get('cat', '')} | {room_data.get('type', '')}")
        rtype.setStyleSheet(f"font-size: 9px; color: {p.get('text_dim', '#555')}; background: transparent; border: none;")
        lay.addWidget(rtype)

        guest = QLabel(room_data.get("guest") or "(Vacant)")
        guest.setStyleSheet(f"font-size: 9px; font-weight: 500; color: {p.get('text', '#222')}; background: transparent; border: none;")
        guest.setWordWrap(False)
        lay.addWidget(guest)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.room_data)
        super().mousePressEvent(ev)


class FrontOfficeDashboard(QWidget):
    """Complete Front Office Modern Workspace."""

    # Navigation requests to parent window
    openModule = pyqtSignal(str)

    def __init__(self, parent=None, user: str = "SA"):
        super().__init__(parent)
        self.user = user
        self._rack_filter = "All"
        self._rack_data = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        p = _theme.palette()
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(14)

        # ------------------ TOP BAR: Title, Live Date, and Refresh ------------------
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        icon_lbl = QLabel("🏨")
        icon_lbl.setStyleSheet("font-size: 26px; background: transparent;")
        top_bar.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.lbl_title = QLabel("Front Office Operations")
        self.lbl_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {p.get('text', '#111')}; background: transparent;")
        title_box.addWidget(self.lbl_title)

        now = datetime.datetime.now()
        self.lbl_date = QLabel(f"Today — {now.strftime('%A, %d %B %Y')}")
        self.lbl_date.setStyleSheet(f"font-size: 12px; color: {p.get('text_dim', '#64748b')}; background: transparent;")
        title_box.addWidget(self.lbl_date)
        top_bar.addLayout(title_box)

        top_bar.addStretch()

        self.btn_refresh = QPushButton("⟳ Refresh Live Data")
        self.btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_refresh.setFixedHeight(34)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: {p.get('surface_solid', '#fff')};
                border: 1px solid {p.get('border', '#ccc')};
                border-radius: 8px;
                padding: 0 14px;
                font-weight: 600;
                font-size: 11px;
                color: {p.get('text', '#333')};
            }}
            QPushButton:hover {{
                background: {p.get('accent_soft', 'rgba(79,70,229,0.1)')};
                border-color: {p.get('accent', '#4f46e5')};
            }}
        """)
        self.btn_refresh.clicked.connect(self.refresh)
        top_bar.addWidget(self.btn_refresh)
        root.addLayout(top_bar)

        # ------------------ QUICK ACTIONS BAR ------------------
        qa_frame = QFrame()
        qa_frame.setStyleSheet(f"""
            QFrame {{
                background: {p.get('surface', 'rgba(255,255,255,0.5)')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.25)')};
                border-radius: 10px;
                padding: 4px;
            }}
        """)
        qa_lay = QHBoxLayout(qa_frame)
        qa_lay.setContentsMargins(8, 6, 8, 6)
        qa_lay.setSpacing(8)

        actions = [
            ("+ New Reservation", "Reservation", "Ctrl+N", p.get("accent", "#4f46e5")),
            ("Check-In", "Check In", "Ctrl+I", p.get("success", "#10b981")),
            ("Check-Out", "Check Out", "Ctrl+O", p.get("warning", "#f59e0b")),
            ("Guest Search", "Guest Profile", "Ctrl+G", p.get("text", "#334155")),
            ("Room Status", "Room Status", "Ctrl+R", p.get("info", "#0284c7")),
            ("Folio / Billing", "Folio Log", "Ctrl+Shift+F", p.get("text", "#334155")),
            ("🗂 Visual Room Rack", "_TOGGLE_RACK_", "F8", p.get("accent", "#6366f1")),
        ]

        for label, mod_key, shortcut, col in actions:
            btn = QPushButton(label)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(32)
            btn.setToolTip(f"{label} ({shortcut})")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {p.get('surface_solid', '#ffffff')};
                    border: 1px solid {p.get('border', '#cbd5e1')};
                    border-radius: 6px;
                    padding: 0 12px;
                    font-size: 11px;
                    font-weight: 600;
                    color: {p.get('text', '#1e293b')};
                }}
                QPushButton:hover {{
                    background: {col};
                    color: #ffffff;
                    border-color: {col};
                }}
            """)
            if mod_key == "_TOGGLE_RACK_":
                btn.clicked.connect(self._toggle_view_mode)
                self.btn_rack_toggle = btn
            else:
                btn.clicked.connect(lambda _, k=mod_key: self.openModule.emit(k))
            qa_lay.addWidget(btn)

        qa_lay.addStretch()
        root.addWidget(qa_frame)

        # ------------------ KPI METRIC CARDS GRID (8 Cards) ------------------
        cards_grid = QGridLayout()
        cards_grid.setSpacing(10)

        c_accent = p.get("accent", "#4f46e5")
        c_succ = p.get("success", "#10b981")
        c_warn = p.get("warning", "#f59e0b")
        c_dang = p.get("danger", "#ef4444")
        c_info = p.get("info", "#0284c7")

        self.cards = {
            "arr": StatCard("arr", "Today's Arrivals", "0", "Scheduled today", "📥", c_succ),
            "dep": StatCard("dep", "Today's Departures", "0", "Scheduled checkout", "📤", c_warn),
            "inhouse": StatCard("inhouse", "In-House Guests", "0", "Current stays", "👥", c_accent),
            "avail": StatCard("avail", "Available Rooms", "0", "Ready for check-in", "🔑", c_succ),
            "occ": StatCard("occ", "Occupied Rooms", "0", "Rooms in use", "🛌", c_dang),
            "vac": StatCard("vac", "Vacant Rooms", "0", "Unoccupied", "🏷", c_info),
            "dirty": StatCard("dirty", "Dirty Rooms", "0", "Awaiting housekeeping", "🧹", c_warn),
            "pending": StatCard("pending", "Pending Payments", "₹0", "Unsettled balance", "💳", c_dang),
        }

        row1 = ["arr", "dep", "inhouse", "avail"]
        row2 = ["occ", "vac", "dirty", "pending"]

        for col, k in enumerate(row1):
            cards_grid.addWidget(self.cards[k], 0, col)
            self.cards[k].clicked.connect(self._on_card_click)

        for col, k in enumerate(row2):
            cards_grid.addWidget(self.cards[k], 1, col)
            self.cards[k].clicked.connect(self._on_card_click)

        root.addLayout(cards_grid)

        # ------------------ CONTENT VIEW AREA (Dual Tables OR Room Rack) ------------------
        self.stack_widget = QWidget()
        self.stack_lay = QVBoxLayout(self.stack_widget)
        self.stack_lay.setContentsMargins(0, 0, 0, 0)
        self.stack_lay.setSpacing(0)

        # View 1: Dashboard Tables (Arrivals + Departures) & Room Status Strip
        self.view_tables = QWidget()
        self._build_tables_view(self.view_tables)
        self.stack_lay.addWidget(self.view_tables)

        # View 2: Room Rack Interactive Grid
        self.view_rack = QWidget()
        self._build_rack_view(self.view_rack)
        self.view_rack.setVisible(False)
        self.stack_lay.addWidget(self.view_rack)

        root.addWidget(self.stack_widget, stretch=1)

    def _build_tables_view(self, parent_widget: QWidget):
        p = _theme.palette()
        lay = QVBoxLayout(parent_widget)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(10)

        # Room Status Summary Indicator Strip
        strip_frame = QFrame()
        strip_frame.setStyleSheet(f"""
            QFrame {{
                background: {p.get('surface', 'rgba(255,255,255,0.6)')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.3)')};
                border-radius: 8px;
                padding: 6px 14px;
            }}
        """)
        strip_lay = QHBoxLayout(strip_frame)
        strip_lay.setContentsMargins(6, 4, 6, 4)
        strip_lay.setSpacing(16)

        self.lbl_occ_gauge = QLabel("Occupancy: 0%")
        self.lbl_occ_gauge.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {p.get('text', '#111')};")
        strip_lay.addWidget(self.lbl_occ_gauge)

        self.lbl_rack_counts = QLabel("Available: 0  |  Occupied: 0  |  Dirty: 0  |  Maintenance: 0")
        self.lbl_rack_counts.setStyleSheet(f"font-size: 11px; color: {p.get('text_dim', '#64748b')};")
        strip_lay.addWidget(self.lbl_rack_counts)
        strip_lay.addStretch()

        btn_show_rack = QPushButton("Open Visual Room Rack →")
        btn_show_rack.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_show_rack.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {p.get('accent', '#4f46e5')};
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        btn_show_rack.clicked.connect(self._toggle_view_mode)
        strip_lay.addWidget(btn_show_rack)

        lay.addWidget(strip_frame)

        # Dual Tables (Arrivals | Departures)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(12)

        # Left Column: Today's Arrivals
        arr_box = QFrame()
        arr_box.setStyleSheet(f"""
            QFrame {{
                background: {p.get('surface', 'rgba(255,255,255,0.7)')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.3)')};
                border-radius: 10px;
            }}
        """)
        arr_lay = QVBoxLayout(arr_box)
        arr_lay.setContentsMargins(12, 10, 12, 10)
        arr_lay.setSpacing(8)

        arr_head = QHBoxLayout()
        arr_title = QLabel("Today's Arrivals")
        arr_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {p.get('text', '#111')}; background: transparent; border: none;")
        arr_head.addWidget(arr_title)
        arr_head.addStretch()
        self.lbl_arr_count = QLabel("0 records")
        self.lbl_arr_count.setStyleSheet(f"font-size: 11px; color: {p.get('text_dim', '#777')}; background: transparent; border: none;")
        arr_head.addWidget(self.lbl_arr_count)
        arr_lay.addLayout(arr_head)

        self.tbl_arr = QTableWidget(0, 5)
        self.tbl_arr.setHorizontalHeaderLabels(["Booking #", "Guest Name", "Arrival", "Departure", "Action"])
        self.tbl_arr.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_arr.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_arr.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_arr.setAlternatingRowColors(True)
        self.tbl_arr.setStyleSheet(f"""
            QTableWidget {{
                background: {p.get('surface_solid', '#ffffff')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.2)')};
                border-radius: 6px;
                gridline-color: {p.get('border', 'rgba(148,163,184,0.15)')};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {p.get('header_grad_top', '#f1f5f9')};
                color: {p.get('text', '#1e293b')};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
                border: none;
                border-bottom: 2px solid {p.get('accent', '#4f46e5')};
            }}
        """)
        arr_lay.addWidget(self.tbl_arr)
        split_layout.addWidget(arr_box, stretch=1)

        # Right Column: Today's Departures
        dep_box = QFrame()
        dep_box.setStyleSheet(f"""
            QFrame {{
                background: {p.get('surface', 'rgba(255,255,255,0.7)')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.3)')};
                border-radius: 10px;
            }}
        """)
        dep_lay = QVBoxLayout(dep_box)
        dep_lay.setContentsMargins(12, 10, 12, 10)
        dep_lay.setSpacing(8)

        dep_head = QHBoxLayout()
        dep_title = QLabel("Today's Departures")
        dep_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {p.get('text', '#111')}; background: transparent; border: none;")
        dep_head.addWidget(dep_title)
        dep_head.addStretch()
        self.lbl_dep_count = QLabel("0 records")
        self.lbl_dep_count.setStyleSheet(f"font-size: 11px; color: {p.get('text_dim', '#777')}; background: transparent; border: none;")
        dep_head.addWidget(self.lbl_dep_count)
        dep_lay.addLayout(dep_head)

        self.tbl_dep = QTableWidget(0, 5)
        self.tbl_dep.setHorizontalHeaderLabels(["Folio #", "Guest Name", "Room", "Dep Date", "Action"])
        self.tbl_dep.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_dep.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_dep.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_dep.setAlternatingRowColors(True)
        self.tbl_dep.setStyleSheet(f"""
            QTableWidget {{
                background: {p.get('surface_solid', '#ffffff')};
                border: 1px solid {p.get('border', 'rgba(148,163,184,0.2)')};
                border-radius: 6px;
                gridline-color: {p.get('border', 'rgba(148,163,184,0.15)')};
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {p.get('header_grad_top', '#f1f5f9')};
                color: {p.get('text', '#1e293b')};
                font-weight: bold;
                font-size: 11px;
                padding: 4px;
                border: none;
                border-bottom: 2px solid {p.get('warning', '#f59e0b')};
            }}
        """)
        dep_lay.addWidget(self.tbl_dep)
        split_layout.addWidget(dep_box, stretch=1)

        lay.addLayout(split_layout)

    def _build_rack_view(self, parent_widget: QWidget):
        p = _theme.palette()
        lay = QVBoxLayout(parent_widget)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        # Filters Row
        top_filter = QHBoxLayout()
        top_filter.setSpacing(8)

        lbl = QLabel("Filter Rooms:")
        lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {p.get('text', '#333')};")
        top_filter.addWidget(lbl)

        self.rack_filter_btns = {}
        for flt in ["All", "Available", "Occupied", "Dirty", "Maintenance"]:
            b = QPushButton(flt)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setFixedHeight(28)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {p.get('surface_solid', '#fff')};
                    border: 1px solid {p.get('border', '#ccc')};
                    border-radius: 14px;
                    padding: 0 12px;
                    font-size: 10px;
                    font-weight: 600;
                    color: {p.get('text', '#333')};
                }}
                QPushButton:hover {{
                    border-color: {p.get('accent', '#4f46e5')};
                }}
            """)
            b.clicked.connect(lambda _, f=flt: self._set_rack_filter(f))
            self.rack_filter_btns[flt] = b
            top_filter.addWidget(b)

        top_filter.addStretch()

        btn_back = QPushButton("← Back to Dashboard")
        btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {p.get('border', '#ccc')};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
                color: {p.get('text', '#333')};
            }}
            QPushButton:hover {{
                background: {p.get('accent_soft', 'rgba(79,70,229,0.1)')};
            }}
        """)
        btn_back.clicked.connect(self._toggle_view_mode)
        top_filter.addWidget(btn_back)
        lay.addLayout(top_filter)

        # Scroll Area for Room Tiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.rack_grid_widget = QWidget()
        self.rack_grid_layout = QGridLayout(self.rack_grid_widget)
        self.rack_grid_layout.setSpacing(8)
        self.rack_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.rack_grid_widget)
        lay.addWidget(scroll)

    def _toggle_view_mode(self):
        show_rack = not self.view_rack.isVisible()
        self.view_tables.setVisible(not show_rack)
        self.view_rack.setVisible(show_rack)
        if hasattr(self, "btn_rack_toggle"):
            self.btn_rack_toggle.setText("📊 Dual Tables" if show_rack else "🗂 Visual Room Rack")
        if show_rack:
            self._render_room_rack()

    def _set_rack_filter(self, flt: str):
        self._rack_filter = flt
        p = _theme.palette()
        for name, btn in self.rack_filter_btns.items():
            if name == flt:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {p.get('accent', '#4f46e5')};
                        color: #ffffff;
                        border: 1px solid {p.get('accent', '#4f46e5')};
                        border-radius: 14px;
                        padding: 0 12px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {p.get('surface_solid', '#fff')};
                        border: 1px solid {p.get('border', '#ccc')};
                        border-radius: 14px;
                        padding: 0 12px;
                        font-size: 10px;
                        font-weight: 600;
                        color: {p.get('text', '#333')};
                    }}
                """)
        self._render_room_rack()

    def _on_card_click(self, key: str):
        if key in ("arr", "dep"):
            self.openModule.emit("Reservation")
        elif key in ("inhouse", "pending"):
            self.openModule.emit("Folio Log")
        elif key in ("avail", "occ", "vac", "dirty"):
            if not self.view_rack.isVisible():
                self._toggle_view_mode()
            flt_map = {"avail": "Available", "occ": "Occupied", "vac": "Available", "dirty": "Dirty"}
            self._set_rack_filter(flt_map.get(key, "All"))

    def refresh(self):
        """Query live database and refresh cards, tables, and rack."""
        try:
            from HMS_py.core import db, roomstatus, reservation, checkin, checkout

            # 1. Room Status / Rack Live Data
            try:
                self._rack_data = roomstatus.room_rack()

                total_rooms = len([r for r in self._rack_data if r.get("type") == "RO"]) or len(self._rack_data)
                occ_rooms = len([r for r in self._rack_data if r.get("status") == "Occupied"])
                dirty_rooms = len([r for r in self._rack_data if r.get("status") == "Dirty"])
                vac_rooms = len([r for r in self._rack_data if r.get("status") == "Vacant"])
                avail_rooms = max(0, total_rooms - occ_rooms)
                maint_rooms = len([r for r in self._rack_data if r.get("status") in ("Maintenance", "Blocked")])

                self.cards["occ"].set_data(str(occ_rooms), f"{occ_rooms}/{total_rooms} rooms")
                self.cards["dirty"].set_data(str(dirty_rooms), "Housekeeping req.")
                self.cards["vac"].set_data(str(vac_rooms), "Clean & vacant")
                self.cards["avail"].set_data(str(avail_rooms), "Ready to assign")

                pct = (occ_rooms / total_rooms * 100) if total_rooms else 0
                self.lbl_occ_gauge.setText(f"Occupancy: {pct:.1f}% ({occ_rooms}/{total_rooms})")
                self.lbl_rack_counts.setText(
                    f"Available: {avail_rooms}  |  Occupied: {occ_rooms}  |  Dirty: {dirty_rooms}  |  Maintenance: {maint_rooms}"
                )
            except Exception:
                for k in ("occ", "dirty", "vac", "avail"):
                    self.cards[k].set_data("Database unavailable", "Offline")

            # 2. In-House Guests & Today's Departures
            try:
                active_fol = checkout.list_active_folios()
                self.cards["inhouse"].set_data(str(len(active_fol)), "Active in-house folios")

                today = datetime.date.today()
                deps_today = [f for f in active_fol if f.get("depdate") == today or (f.get("depdate") and f.get("depdate") <= today)]
                self.cards["dep"].set_data(str(len(deps_today)), "Departures scheduled")
                self.lbl_dep_count.setText(f"{len(deps_today)} records")

                # Populate Departures Table
                self.tbl_dep.setRowCount(len(deps_today))
                p = _theme.palette()
                for r, item in enumerate(deps_today):
                    self.tbl_dep.setItem(r, 0, QTableWidgetItem(str(item.get("folio", ""))))
                    self.tbl_dep.setItem(r, 1, QTableWidgetItem(str(item.get("name", ""))))
                    self.tbl_dep.setItem(r, 2, QTableWidgetItem(str(item.get("roomno", ""))))
                    dep_str = item.get("depdate").strftime("%d/%b/%Y") if isinstance(item.get("depdate"), datetime.date) else str(item.get("depdate") or "")
                    self.tbl_dep.setItem(r, 3, QTableWidgetItem(dep_str))

                    btn_co = QPushButton("Check-Out")
                    btn_co.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    btn_co.setStyleSheet(f"""
                        QPushButton {{
                            background: {p.get('warning', '#f59e0b')};
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 2px 6px;
                        }}
                    """)
                    btn_co.clicked.connect(lambda _, fol=item.get("folio"): self.openModule.emit("Check Out"))
                    self.tbl_dep.setCellWidget(r, 4, btn_co)

            except Exception:
                self.cards["inhouse"].set_data("Database unavailable", "Offline")
                self.cards["dep"].set_data("Database unavailable", "Offline")
                self.tbl_dep.setRowCount(0)

            # 3. Reservations & Arrivals
            try:
                res_rows = reservation.list_reservations()
                today = datetime.date.today()
                
                arr_today = []
                for row in res_rows:
                    arr_val = row[3]
                    arr_date = arr_val.date() if isinstance(arr_val, datetime.datetime) else arr_val
                    if row[8] == 'N' and (arr_date == today or (isinstance(arr_date, datetime.date) and arr_date <= today)):
                        arr_today.append(row)

                self.cards["arr"].set_data(str(len(arr_today)), "Arrivals scheduled")
                self.lbl_arr_count.setText(f"{len(arr_today)} records")

                # Populate Arrivals Table
                self.tbl_arr.setRowCount(len(arr_today))
                p = _theme.palette()
                for r, item in enumerate(arr_today):
                    self.tbl_arr.setItem(r, 0, QTableWidgetItem(str(item[0])))  # BookNo
                    self.tbl_arr.setItem(r, 1, QTableWidgetItem(str(item[2])))  # GuestName
                    arr_s = item[3].strftime("%d/%b/%Y") if isinstance(item[3], (datetime.date, datetime.datetime)) else str(item[3])
                    dep_s = item[4].strftime("%d/%b/%Y") if isinstance(item[4], (datetime.date, datetime.datetime)) else str(item[4])
                    self.tbl_arr.setItem(r, 2, QTableWidgetItem(arr_s))
                    self.tbl_arr.setItem(r, 3, QTableWidgetItem(dep_s))

                    btn_ci = QPushButton("Check-In")
                    btn_ci.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    btn_ci.setStyleSheet(f"""
                        QPushButton {{
                            background: {p.get('success', '#10b981')};
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 10px;
                            font-weight: bold;
                            padding: 2px 6px;
                        }}
                    """)
                    btn_ci.clicked.connect(lambda _, bno=item[0]: self.openModule.emit("Check In"))
                    self.tbl_arr.setCellWidget(r, 4, btn_ci)

            except Exception:
                self.cards["arr"].set_data("Database unavailable", "Offline")
                self.tbl_arr.setRowCount(0)

            # 4. Pending Payments
            try:
                q_pend = db.query("SELECT ISNULL(SUM(AmtDr - AmtCr), 0) FROM PayCharge WHERE AmtDr > AmtCr")
                val_pend = q_pend[0][0] if q_pend else 0
                self.cards["pending"].set_data(f"₹{val_pend:,.0f}", "Outstanding ledger")
            except Exception:
                self.cards["pending"].set_data("Database unavailable", "Offline")

        except Exception:
            for c in self.cards.values():
                c.set_data("Database unavailable", "Offline")

        if self.view_rack.isVisible():
            self._render_room_rack()

    def _render_room_rack(self):
        """Render room tiles according to active filter."""
        # Clear existing
        while self.rack_grid_layout.count():
            item = self.rack_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = []
        for r in self._rack_data:
            st = r.get("status", "Vacant")
            if self._rack_filter == "All":
                filtered.append(r)
            elif self._rack_filter == "Available" and st == "Vacant":
                filtered.append(r)
            elif self._rack_filter == "Occupied" and st == "Occupied":
                filtered.append(r)
            elif self._rack_filter == "Dirty" and st == "Dirty":
                filtered.append(r)
            elif self._rack_filter == "Maintenance" and st in ("Maintenance", "Blocked"):
                filtered.append(r)

        row = 0
        col = 0
        cols_per_row = 8  # responsive room rack grid

        for room in filtered:
            tile = RoomRackItem(room, self.rack_grid_widget)
            tile.clicked.connect(self._show_room_dialog)
            self.rack_grid_layout.addWidget(tile, row, col)
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1

    def _show_room_dialog(self, room: dict):
        """Dialog to show room information and allow quick housekeeping / check-in actions."""
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Room {room.get('roomno')} Details")
        dlg.setFixedSize(380, 320)
        p = _theme.palette()

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(10)

        title = QLabel(f"Room {room.get('roomno')} ({room.get('name')})")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {p.get('text', '#111')};")
        lay.addWidget(title)

        info_box = QFrame()
        info_box.setStyleSheet(f"background: {p.get('surface_solid', '#fff')}; border: 1px solid {p.get('border', '#ccc')}; border-radius: 8px; padding: 10px;")
        inf_lay = QVBoxLayout(info_box)
        inf_lay.setSpacing(6)

        st = room.get("status", "Vacant")
        inf_lay.addWidget(QLabel(f"<b>Status:</b> {st}"))
        inf_lay.addWidget(QLabel(f"<b>Category:</b> {room.get('cat', 'Standard')}"))
        inf_lay.addWidget(QLabel(f"<b>Maid Station:</b> {room.get('maid', 'General')}"))
        if room.get("guest"):
            inf_lay.addWidget(QLabel(f"<b>In-House Guest:</b> {room.get('guest')}"))
            inf_lay.addWidget(QLabel(f"<b>Folio #:</b> {room.get('folio')}"))
            if room.get("chk_in"):
                inf_lay.addWidget(QLabel(f"<b>Check-In Date:</b> {room.get('chk_in')}"))
            if room.get("dep"):
                inf_lay.addWidget(QLabel(f"<b>Departure Date:</b> {room.get('dep')}"))
        lay.addWidget(info_box)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        if st == "Dirty":
            btn_clean = QPushButton("Mark Clean")
            btn_clean.setStyleSheet("background: #10b981; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
            btn_clean.clicked.connect(lambda: self._set_room_status(room.get('roomno'), "", dlg))
            btn_row.addWidget(btn_clean)
        elif st == "Vacant":
            btn_dirty = QPushButton("Mark Dirty")
            btn_dirty.setStyleSheet("background: #f59e0b; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
            btn_dirty.clicked.connect(lambda: self._set_room_status(room.get('roomno'), "D", dlg))
            btn_row.addWidget(btn_dirty)
            btn_checkin = QPushButton("Check-In")
            btn_checkin.setStyleSheet("background: #4f46e5; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
            btn_checkin.clicked.connect(lambda: (dlg.accept(), self.openModule.emit("Check In")))
            btn_row.addWidget(btn_checkin)
        elif st == "Occupied":
            btn_folio = QPushButton("View Folio")
            btn_folio.setStyleSheet("background: #4f46e5; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
            btn_folio.clicked.connect(lambda: (dlg.accept(), self.openModule.emit("Check Out")))
            btn_row.addWidget(btn_folio)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dlg.reject)
        btn_row.addWidget(btn_close)

        lay.addLayout(btn_row)
        dlg.exec()

    def _set_room_status(self, room_no: str, new_stat: str, dlg: QDialog):
        try:
            from HMS_py.core import roomstatus
            roomstatus.mark_room_status(room_no, new_stat, user=self.user)
            dlg.accept()
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Room Status", f"Error updating room status: {e}")
