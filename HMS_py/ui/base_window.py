"""Modern Base Window class for all HMS forms.

Provides consistent layout, header, status bar, and styling for all windows.
All UI forms should inherit from ModernWindow for consistent look.

Usage:
    class MyForm(ModernWindow):
        def __init__(self, parent=None):
            super().__init__(parent, title="My Form", size=(900, 600))
            # Add content to self.content_area (QVBoxLayout)
"""
from __future__ import annotations
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStatusBar, QSizePolicy, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from HMS_py.ui import theme as _theme


class ModernWindow(QMainWindow):
    """Modern base window with consistent layout and styling."""

    def __init__(self, parent=None, title: str = "HMS",
                 size: tuple = (900, 600), icon: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(*size)
        self.setMinimumSize(600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header bar
        self.header = self._create_header(title)
        main_layout.addWidget(self.header)

        # Content area (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content_widget = QWidget()
        self.content_area = QVBoxLayout(self.content_widget)
        self.content_area.setContentsMargins(20, 16, 20, 16)
        self.content_area.setSpacing(12)
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, 1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        # Button bar (optional)
        self.button_bar = QHBoxLayout()
        self.button_bar.setContentsMargins(20, 8, 20, 12)
        self.button_bar.setSpacing(8)
        main_layout.addLayout(self.button_bar)

    def _create_header(self, title: str) -> QFrame:
        header = QFrame()
        header.setFixedHeight(56)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        # Title
        lbl = QLabel(title)
        lbl.setProperty("header", True)
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(lbl)

        layout.addStretch()

        return header

    def add_button(self, text: str, callback=None, style: str = "",
                   tooltip: str = "") -> QPushButton:
        """Add a button to the bottom button bar."""
        btn = QPushButton(text)
        if style:
            btn.setProperty(style, True)
        if tooltip:
            btn.setToolTip(tooltip)
        if callback:
            btn.clicked.connect(callback)
        self.button_bar.addWidget(btn)
        return btn

    def add_stretch(self):
        """Add stretch to button bar."""
        self.button_bar.addStretch()

    def set_status(self, msg: str):
        """Set status bar message."""
        self.status.showMessage(msg)

    def add_section(self, title: str) -> QGroupBox:
        """Add a titled section group to the content area."""
        from PyQt6.QtWidgets import QGroupBox
        grp = QGroupBox(title)
        grp_lay = QFormLayout(grp)
        grp_lay.setContentsMargins(16, 20, 16, 12)
        grp_lay.setSpacing(8)
        self.content_area.addWidget(grp)
        return grp

    def add_table(self, headers: list, data: list = None) -> 'QTableWidget':
        """Add a styled table to the content area."""
        from PyQt6.QtWidgets import QTableWidget
        from PyQt6.QtGui import QColor
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSortingEnabled(True)

        if data:
            table.setRowCount(len(data))
            text_col = QColor(_theme.palette()["text"])  # BUG FIX: #e0e0e0 light me invisible
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val or ""))
                    item.setForeground(text_col)
                    table.setItem(i, j, item)

        self.content_area.addWidget(table)
        return table


class GroupBox(QGroupBox):
    """Glass GroupBox — colors theme tokens se (user-defined)."""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        t = _theme.palette()
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                background: {t['glass_tint']};
                border: 1px solid {t['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding: 16px 12px 12px 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: {t['accent']};
                font-weight: bold;
            }}
        """)
