"""Dashboard UI — Summary cards for main window.

Shows key hotel metrics at a glance:
- Today's Reservations, Check-ins, Check-outs
- Available / Occupied / Dirty Rooms
- Pending Payments, Today's Revenue

Data loaded from live DB on refresh. Cards are glassmorphism-styled.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGridLayout, QFrame, QSizePolicy)

from HMS_py.ui import theme as _theme


class DashboardCard(QFrame):
    """A single glassmorphism summary card."""

    def __init__(self, title: str, value: str = "0", icon: str = "",
                 accent_color: str = "", parent=None):
        super().__init__(parent)
        self.setProperty("glassCard", True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumSize(180, 100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setMaximumHeight(120)

        p = _theme.palette()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Icon + title row
        header = QHBoxLayout()
        header.setSpacing(8)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 20px; color: {accent_color or p['accent']};")
            header.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {p['text_dim']};"
            f" background: transparent; border: none;"
        )
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        # Value
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {p['text']};"
            f" background: transparent; border: none;"
        )
        self.value_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.value_lbl)

    def set_value(self, value: str):
        self.value_lbl.setText(value)


class DashboardWidget(QWidget):
    """Full dashboard with summary cards grid."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(16)

        p = _theme.palette()

        # Header
        header = QLabel("Dashboard")
        header.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {p['text']};"
            f" background: transparent; border: none;"
        )
        root.addWidget(header)

        subtitle = QLabel("Hotel overview at a glance")
        subtitle.setStyleSheet(
            f"font-size: 12px; color: {p['text_dim']};"
            f" background: transparent; border: none;"
        )
        root.addWidget(subtitle)

        # Cards grid
        grid = QGridLayout()
        grid.setSpacing(12)

        accent = p.get("accent", "#2563eb")
        success = p.get("success", "#059669")
        warning = p.get("warning", "#d97706")
        danger = p.get("danger", "#dc2626")

        # Row 1: Reservations, Check-ins, Check-outs
        self.card_reservations = DashboardCard(
            "Reservations", "0", "\U0001F4C5", accent)
        self.card_checkins = DashboardCard(
            "Check-ins Today", "0", "\u2705", success)
        self.card_checkouts = DashboardCard(
            "Check-outs Today", "0", "\U0001F3E0", warning)
        grid.addWidget(self.card_reservations, 0, 0)
        grid.addWidget(self.card_checkins, 0, 1)
        grid.addWidget(self.card_checkouts, 0, 2)

        # Row 2: Available, Occupied, Dirty
        self.card_available = DashboardCard(
            "Available Rooms", "0", "\U0001F534", success)
        self.card_occupied = DashboardCard(
            "Occupied Rooms", "0", "\U0001F7E2", accent)
        self.card_dirty = DashboardCard(
            "Dirty Rooms", "0", "\u26A0\uFE0F", danger)
        grid.addWidget(self.card_available, 1, 0)
        grid.addWidget(self.card_occupied, 1, 1)
        grid.addWidget(self.card_dirty, 1, 2)

        # Row 3: Revenue, Pending
        self.card_revenue = DashboardCard(
            "Today's Revenue", "\u20B90", "\U0001F4B0", success)
        self.card_pending = DashboardCard(
            "Pending Payments", "\u20B90", "\u23F3", danger)
        grid.addWidget(self.card_revenue, 2, 0)
        grid.addWidget(self.card_pending, 2, 1)

        root.addLayout(grid)
        root.addStretch()

        # Refresh on show
        self._load_data()

    def _load_data(self):
        """Load dashboard data from database."""
        try:
            from HMS_py.core import db

            # Reservations today (live schema: Booking, ResStatus)
            try:
                rows = db.query(
                    "SELECT COUNT(*) FROM Booking "
                    "WHERE CAST(VDate AS DATE) = CAST(GETDATE() AS DATE)")
                self.card_reservations.set_value(str(rows[0][0] if rows else 0))
            except Exception:
                self.card_reservations.set_value("N/A")

            # Check-ins today (RoomOcc: Type='I' = in-house, ChkInDate)
            try:
                rows = db.query(
                    "SELECT COUNT(*) FROM RoomOcc "
                    "WHERE CAST(ChkInDate AS DATE) = CAST(GETDATE() AS DATE) "
                    "AND Type = 'I'")
                self.card_checkins.set_value(str(rows[0][0] if rows else 0))
            except Exception:
                self.card_checkins.set_value("N/A")

            # Check-outs today (GuestFolio.DepDate = departure)
            try:
                rows = db.query(
                    "SELECT COUNT(*) FROM GuestFolio "
                    "WHERE CAST(DepDate AS DATE) = CAST(GETDATE() AS DATE)")
                self.card_checkouts.set_value(str(rows[0][0] if rows else 0))
            except Exception:
                self.card_checkouts.set_value("N/A")

            # Room status counts (RoomOcc.Type, not Status)
            try:
                rows = db.query(
                    "SELECT Type, COUNT(*) FROM RoomOcc "
                    "GROUP BY Type")
                occ_map = {}
                for r in rows:
                    occ_map[str(r[0] or "")] = r[1]
                occupied = sum(v for k, v in occ_map.items() if k == "I")
                self.card_occupied.set_value(str(occupied))
            except Exception:
                self.card_occupied.set_value("N/A")

            try:
                rows = db.query("SELECT COUNT(*) FROM RoomMast")
                total = rows[0][0] if rows else 0
                try:
                    occ = int(self.card_occupied.value_lbl.text() or 0)
                except (ValueError, TypeError):
                    occ = 0
                self.card_available.set_value(str(max(0, total - occ)))
            except Exception:
                self.card_available.set_value("N/A")

            # Dirty rooms (RoomMast.RoomStat='D')
            try:
                rows = db.query(
                    "SELECT COUNT(*) FROM RoomMast WHERE RoomStat = 'D'")
                self.card_dirty.set_value(str(rows[0][0] if rows else 0))
            except Exception:
                self.card_dirty.set_value("N/A")

            # Today's revenue (PayCharge.AmtDr - live cols)
            try:
                rows = db.query(
                    "SELECT ISNULL(SUM(AmtDr - AmtCr), 0) FROM PayCharge "
                    "WHERE Vtype NOT IN ('HPOST') "
                    "AND CAST(Vdate AS DATE) = CAST(GETDATE() AS DATE)")
                val = rows[0][0] if rows else 0
                self.card_revenue.set_value(f"₹{val:,.0f}")
            except Exception:
                self.card_revenue.set_value("N/A")

            # Pending payments (AmtDr > AmtCr)
            try:
                rows = db.query(
                    "SELECT ISNULL(SUM(AmtDr - AmtCr), 0) FROM PayCharge "
                    "WHERE AmtDr > AmtCr")
                val = rows[0][0] if rows else 0
                self.card_pending.set_value(f"₹{val:,.0f}")
            except Exception:
                self.card_pending.set_value("N/A")

        except ImportError:
            # DB module not available — show placeholder values
            pass
        except Exception:
            pass


def open_dashboard(parent=None):
    """Open dashboard as a standalone window."""
    from PyQt6.QtWidgets import QDialog, QVBoxLayout
    dlg = QDialog(parent)
    dlg.setWindowTitle("HMS Dashboard")
    dlg.resize(800, 500)
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(0, 0, 0, 0)
    dash = DashboardWidget(dlg)
    lay.addWidget(dash)
    dlg.show()
    return dlg
