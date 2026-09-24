"""HMS_py Design System - Reusable UI constants, tokens, and helper functions.

Usage:
    from ui.design import DS, make_card, make_section, styled_button
    from ui.theme import palette, status_colors

All colors reference theme tokens at runtime via theme.palette() / status_colors().
These constants provide consistent spacing, typography, and sizing across all forms.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QLineEdit, QComboBox, QDateEdit, QSpinBox,
                             QDoubleSpinBox, QTextEdit, QFrame, QLabel,
                             QPushButton, QHBoxLayout, QVBoxLayout, QWidget,
                             QTableWidget, QHeaderView, QAbstractItemView,
                             QTableWidgetItem)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont


# ---------------------------------------------------------------------------
# Spacing scale (px)
# ---------------------------------------------------------------------------
class Spacing:
    XXXS = 2
    XXS = 4
    XS = 6
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32


# ---------------------------------------------------------------------------
# Typography scale (px) - all use Segoe UI
# ---------------------------------------------------------------------------
class Font:
    FAMILY = "Segoe UI"
    XS = 10
    SM = 11
    MD = 13
    LG = 14
    XL = 16
    XXL = 18
    TITLE = 22
    REGULAR = 500
    BOLD = 700


# ---------------------------------------------------------------------------
# Widget sizing
# ---------------------------------------------------------------------------
class Size:
    INPUT_H = 36
    INPUT_H_LG = 40
    BUTTON_H = 34
    BUTTON_H_LG = 40
    BUTTON_H_SM = 28
    SIDEBAR_BTN_H = 38
    HEADER_H = 52
    ROW_H = 32
    SIDEBAR_W = 220
    BUTTON_MIN_W = 80
    DIALOG_MIN_W = 400
    RADIUS = 8
    RADIUS_SM = 6
    RADIUS_LG = 10


# ---------------------------------------------------------------------------
# Layout presets (left, top, right, bottom)
# ---------------------------------------------------------------------------
class Layout:
    CONTENT = (Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
    BUTTON_BAR = (Spacing.XL, Spacing.SM, Spacing.XL, Spacing.MD)
    CARD = (Spacing.XXL, Spacing.XL, Spacing.XXL, Spacing.XL)
    DIALOG = (Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
    SECTION = (Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
    FORM_SPACING = Spacing.MD
    BUTTON_SPACING = Spacing.SM
    GRID_H_SPACING = Spacing.MD
    GRID_V_SPACING = Spacing.SM


# ---------------------------------------------------------------------------
# Window defaults
# ---------------------------------------------------------------------------
class WindowSize:
    MAIN = (1150, 720)
    LOGIN = (440, 480)
    COMPANY = (580, 420)
    MASTER = (720, 520)
    TRANSACTION = (860, 560)
    REPORT = (900, 580)
    ROOM_STATUS = (1150, 680)
    CHECKOUT = (1100, 650)
    POS = (900, 600)


# ---------------------------------------------------------------------------
# Helper functions for building common UI patterns
# ---------------------------------------------------------------------------
def make_card(parent=None, title: str = "", content_layout=None):
    """Create a glass-card frame with optional title and content layout."""
    from PyQt6.QtWidgets import QFrame, QVBoxLayout

    frame = QFrame(parent)
    frame.setProperty("glassCard", True)
    frame.setFrameShape(QFrame.Shape.NoFrame)

    outer = QVBoxLayout(frame)
    outer.setContentsMargins(*Layout.CARD)
    outer.setSpacing(Spacing.MD)

    if title:
        lbl = QLabel(title)
        lbl.setProperty("glassTitle", True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        outer.addWidget(lbl)

    if content_layout:
        if hasattr(content_layout, "addLayout"):
            outer.addLayout(content_layout)
        else:
            outer.addWidget(content_layout)

    return frame


def make_section(title: str, content, parent=None):
    """Create a labeled section group inside a form."""
    from PyQt6.QtWidgets import QGroupBox, QVBoxLayout
    from ui.theme import palette

    p = palette()
    grp = QGroupBox(title, parent)
    grp.setStyleSheet(
        f"QGroupBox {{ font-weight: 700; font-size: {Font.MD}px; margin-top: 12px; "
        f"padding: 12px 8px 8px 8px; color: {p['text']}; }}"
        f"QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}"
    )
    inner = QVBoxLayout(grp)
    inner.setContentsMargins(*Layout.SECTION)
    inner.setSpacing(Spacing.SM)
    if content is not None:
        if hasattr(content, "addLayout"):
            inner.addLayout(content)
        else:
            inner.addWidget(content)
    return grp


def status_badge(text: str, status: str = "info") -> str:
    """Return HTML for a colored status badge inside a QLabel.
    Uses theme tokens for consistent appearance.
    """
    try:
        from ui.theme import status_colors, palette
        sc = status_colors()
        p = palette()
        color_map = {
            "success": (sc.get("success_text", "#059669"), sc.get("success_bg", "#ecfdf5")),
            "warning": (sc.get("warning_text", "#d97706"), sc.get("warning_bg", "#fffbeb")),
            "danger": (sc.get("danger_text", "#dc2626"), sc.get("danger_bg", "#fef2f2")),
            "info": (sc.get("info_text", "#0284c7"), sc.get("info_bg", "#f0f9ff")),
            "neutral": (p.get("text_dim", "#64748b"), p.get("surface", "#f8fafc")),
        }
    except ImportError:
        color_map = {
            "success": ("#059669", "#ecfdf5"),
            "warning": ("#d97706", "#fffbeb"),
            "danger": ("#dc2626", "#fef2f2"),
            "info": ("#0284c7", "#f0f9ff"),
            "neutral": ("#64748b", "#f8fafc"),
        }
    fg, bg = color_map.get(status, color_map["info"])
    return (
        f'<span style="color:{fg}; background:{bg}; padding:2px 8px; '
        f'border-radius:4px; font-size:{Font.SM}px; font-weight:600;">{text}</span>'
    )


def styled_button(text: str, role: str = "default", tooltip: str = ""):
    """Create a consistently styled QPushButton.

    role: 'primary', 'danger', 'warning', 'success', 'default'
    """

    btn = QPushButton(text)
    if role == "primary":
        btn.setProperty("accent", True)
    elif role in ("danger", "warning", "success"):
        btn.setProperty("role", role)
    btn.setMinimumHeight(Size.BUTTON_H)
    if tooltip:
        btn.setToolTip(tooltip)
    return btn


def make_button_bar(buttons: list, add_stretch: bool = True):
    """Create a standardized button toolbar.

    buttons: [(text, role, callback, tooltip), ...]
    Returns QWidget with QHBoxLayout.
    """
    from PyQt6.QtWidgets import QWidget

    bar = QWidget()
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(*Layout.BUTTON_BAR)
    lay.setSpacing(Spacing.SM)
    if add_stretch:
        lay.addStretch()

    for item in buttons:
        text = item[0]
        role = item[1] if len(item) > 1 else "default"
        cb = item[2] if len(item) > 2 else None
        tip = item[3] if len(item) > 3 else ""
        btn = styled_button(text, role, tip)
        if cb:
            btn.clicked.connect(cb)
        lay.addWidget(btn)

    return bar


def make_form_row(label_text: str, widget, required: bool = False):
    """Create a labeled form row with consistent styling.

    Returns (QLabel, widget) for use in QFormLayout.
    """
    from ui.theme import palette

    p = palette()
    text = label_text
    if required:
        text += ' <span style="color:#dc2626;">*</span>'

    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size: {Font.SM}px; font-weight: 500; color: {p['text']};")
    return lbl, widget


def add_empty_state(table, message: str = "No records found"):
    """Show an empty-state message in a QTableWidget."""
    from ui.theme import palette

    p = palette()
    table.setRowCount(1)
    table.setColumnCount(1)
    item = QTableWidgetItem(message)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setForeground(QColor(p["text_dim"]))
    table.setItem(0, 0, item)


def make_search_bar(placeholder: str = "Search...", on_search=None):
    """Create a search input bar with consistent styling."""
    from PyQt6.QtWidgets import QLineEdit
    from ui.theme import palette

    p = palette()
    search = QLineEdit()
    search.setPlaceholderText(placeholder)
    search.setMinimumHeight(Size.INPUT_H)
    search.setStyleSheet(
        f"QLineEdit {{ padding-left: 28px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QLineEdit:focus {{ border: 2px solid {p['accent']}; }}"
    )
    if on_search:
        search.textChanged.connect(on_search)
    return search


def setup_table(table, columns: list, sortable: bool = True,
                alternating: bool = True, select_rows: bool = True,
                read_only: bool = True):
    """Configure a QTableWidget with consistent styling.

    Sets headers, selection behavior, edit triggers, alternating rows,
    and sorting. Call this instead of manual per-table configuration.
    """

    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)

    if read_only:
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    if select_rows:
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    table.setAlternatingRowColors(alternating)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)
    table.setSortingEnabled(sortable)

    header = table.horizontalHeader()
    header.setStretchLastSection(True)
    for i in range(len(columns) - 1):
        header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)


def set_cell_text(table, row: int, col: int, text: str, fg: str = ""):
    """Set a table cell with theme-consistent text color."""
    from PyQt6.QtGui import QColor
    from ui.theme import palette

    p = palette()
    it = QTableWidgetItem(str(text))
    it.setForeground(QColor(fg or p["text"]))
    table.setItem(row, col, it)


# ---------------------------------------------------------------------------
# Professional UI Components (NEW)
# ---------------------------------------------------------------------------
def make_line_edit(placeholder: str = "", min_width: int = 0,
                   validator=None, tooltip: str = "") -> QLineEdit:
    """Create a consistently styled QLineEdit."""
    from PyQt6.QtWidgets import QLineEdit
    from ui.theme import palette

    p = palette()
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setMinimumHeight(Size.INPUT_H)
    le.setMinimumWidth(min_width)
    le.setStyleSheet(
        f"QLineEdit {{ padding: 8px 12px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QLineEdit:focus {{ border: 2px solid {p['accent']}; }}"
        f"QLineEdit:disabled {{ background: {p['surface']}; color: {p['text_dim']}; }}"
    )
    if validator:
        le.setValidator(validator)
    if tooltip:
        le.setToolTip(tooltip)
    return le


def make_combo_box(items: list = None, placeholder: str = "", 
                   editable: bool = False, min_width: int = 0,
                   tooltip: str = "") -> QComboBox:
    """Create a consistently styled QComboBox."""
    from PyQt6.QtWidgets import QComboBox
    from ui.theme import palette

    p = palette()
    cb = QComboBox()
    cb.setEditable(editable)
    if items:
        cb.addItems(items)
    if placeholder and editable:
        cb.setCurrentText("")
        cb.lineEdit().setPlaceholderText(placeholder)
    cb.setMinimumHeight(Size.INPUT_H)
    cb.setMinimumWidth(min_width)
    cb.setStyleSheet(
        f"QComboBox {{ padding: 8px 32px 8px 12px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QComboBox:focus {{ border: 2px solid {p['accent']}; }}"
        f"QComboBox::drop-down {{ border: none; width: 24px; }}"
        f"QComboBox QAbstractItemView {{ border: 1px solid {p['border']}; "
        f"selection-background-color: {p['accent_soft']}; "
        f"background: {p['surface_solid']}; color: {p['text']}; }}"
    )
    if tooltip:
        cb.setToolTip(tooltip)
    return cb


def make_date_edit(placeholder: str = "dd/MM/yyyy", min_width: int = 120,
                   tooltip: str = "") -> QDateEdit:
    """Create a consistently styled QDateEdit with calendar popup."""
    from PyQt6.QtWidgets import QDateEdit
    from ui.theme import palette

    p = palette()
    de = QDateEdit()
    de.setCalendarPopup(True)
    de.setDisplayFormat("dd/MM/yyyy")
    de.setDate(QDate.currentDate())
    de.setMinimumHeight(Size.INPUT_H)
    de.setMinimumWidth(min_width)
    de.setStyleSheet(
        f"QDateEdit {{ padding: 8px 12px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QDateEdit:focus {{ border: 2px solid {p['accent']}; }}"
        f"QDateEdit::drop-down {{ border: none; width: 24px; }}"
    )
    if tooltip:
        de.setToolTip(tooltip)
    return de


def make_spin_box(minimum: int = 0, maximum: int = 999999, 
                  suffix: str = "", decimals: int = 0,
                  step: int = 1, min_width: int = 80,
                  tooltip: str = "") -> QSpinBox | QDoubleSpinBox:
    """Create a consistently styled spin box (int or float)."""
    from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox
    from ui.theme import palette

    p = palette()
    if decimals > 0:
        sb = QDoubleSpinBox()
        sb.setDecimals(decimals)
    else:
        sb = QSpinBox()
    sb.setMinimum(minimum)
    sb.setMaximum(maximum)
    sb.setSingleStep(step)
    if suffix:
        sb.setSuffix(f" {suffix}")
    sb.setMinimumHeight(Size.INPUT_H)
    sb.setMinimumWidth(min_width)
    sb.setStyleSheet(
        f"QSpinBox, QDoubleSpinBox {{ padding: 8px 12px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QSpinBox:focus, QDoubleSpinBox:focus {{ border: 2px solid {p['accent']}; }}"
        f"QSpinBox::up-button, QDoubleSpinBox::up-button {{ "
        f"border: none; background: {p['surface_hover']}; width: 16px; }}"
        f"QSpinBox::down-button, QDoubleSpinBox::down-button {{ "
        f"border: none; background: {p['surface_hover']}; width: 16px; }}"
    )
    if tooltip:
        sb.setToolTip(tooltip)
    return sb


def make_text_edit(placeholder: str = "", min_height: int = 80,
                   read_only: bool = False, tooltip: str = "") -> QTextEdit:
    """Create a consistently styled QTextEdit."""
    from PyQt6.QtWidgets import QTextEdit
    from ui.theme import palette

    p = palette()
    te = QTextEdit()
    te.setPlaceholderText(placeholder)
    te.setMinimumHeight(min_height)
    te.setReadOnly(read_only)
    te.setStyleSheet(
        f"QTextEdit {{ padding: 8px 12px; border: 1px solid {p['border']}; "
        f"border-radius: {Size.RADIUS}px; font-size: {Font.MD}px; "
        f"color: {p['text']}; background: {p['glass_tint']}; }}"
        f"QTextEdit:focus {{ border: 2px solid {p['accent']}; }}"
        f"QTextEdit:read-only {{ background: {p['surface']}; color: {p['text_dim']}; }}"
    )
    if tooltip:
        te.setToolTip(tooltip)
    return te


def make_card_v2(title: str = "", content=None, parent=None, 
                 elevated: bool = False) -> QFrame:
    """Enhanced glass card with optional elevation."""
    from PyQt6.QtWidgets import QFrame, QVBoxLayout
    from ui.theme import palette

    p = palette()
    frame = QFrame(parent)
    frame.setProperty("glassCard", True)
    frame.setFrameShape(QFrame.Shape.NoFrame)
    
    if elevated:
        frame.setStyleSheet(
            f"QFrame[glassCard=\"true\"] {{ "
            f"background: {p['surface']}; border: 1px solid {p['border']}; "
            f"border-radius: {Size.RADIUS_LG}px; }}"
            f"QFrame[glassCard=\"true\"][elevated=\"true\"] {{ "
            f"background: {p['surface_hover']}; border: 1px solid {p['border_strong']}; "
            f"box-shadow: 0 4px 12px {p['shadow']}; }}"
        )
        frame.setProperty("elevated", True)
    else:
        frame.setStyleSheet(
            f"QFrame[glassCard=\"true\"] {{ "
            f"background: {p['surface']}; border: 1px solid {p['border']}; "
            f"border-radius: {Size.RADIUS_LG}px; }}"
        )

    outer = QVBoxLayout(frame)
    outer.setContentsMargins(*Layout.CARD)
    outer.setSpacing(Spacing.MD)

    if title:
        lbl = QLabel(title)
        lbl.setProperty("glassTitle", True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        outer.addWidget(lbl)

    if content:
        if hasattr(content, "addLayout"):
            outer.addLayout(content)
        else:
            outer.addWidget(content)

    return frame


def make_info_bar(message: str, type_: str = "info", 
                  dismissible: bool = True) -> QWidget:
    """Create an info/warning/error/success bar."""
    from PyQt6.QtWidgets import QWidget
    from ui.theme import palette, status_colors

    p = palette()
    sc = status_colors()
    
    color_map = {
        "success": (sc.get("success_text", "#059669"), sc.get("success_bg", "#ecfdf5"), p.get("success", "#059669")),
        "warning": (sc.get("warning_text", "#d97706"), sc.get("warning_bg", "#fffbeb"), p.get("warning", "#d97706")),
        "danger": (sc.get("danger_text", "#dc2626"), sc.get("danger_bg", "#fef2f2"), p.get("danger", "#dc2626")),
        "info": (sc.get("info_text", "#0284c7"), sc.get("info_bg", "#f0f9ff"), p.get("info", "#0284c7")),
    }
    fg, bg, icon_color = color_map.get(type_, color_map["info"])

    bar = QWidget()
    bar.setStyleSheet(f"background: {bg}; border-radius: {Size.RADIUS}px; border: 1px solid {icon_color}33;")
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
    lay.setSpacing(Spacing.SM)

    icon = QLabel("●")
    icon.setStyleSheet(f"color: {icon_color}; font-size: {Font.LG}px; font-weight: bold;")
    icon.setFixedWidth(20)
    lay.addWidget(icon)

    msg = QLabel(message)
    msg.setStyleSheet(f"color: {fg}; font-size: {Font.MD}px; font-weight: 500;")
    msg.setWordWrap(True)
    lay.addWidget(msg, stretch=1)

    if dismissible:
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {fg}; "
            f"border: none; font-size: {Font.LG}px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {icon_color}20; border-radius: {Size.RADIUS_SM}px; }}"
        )
        close_btn.clicked.connect(bar.hide)
        lay.addWidget(close_btn)

    return bar


def make_progress_indicator(steps: list, current_step: int = 0) -> QWidget:
    """Create a step progress indicator (wizard-style)."""
    from PyQt6.QtWidgets import QWidget, QFrame
    from ui.theme import palette

    p = palette()
    container = QWidget()
    lay = QHBoxLayout(container)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)

    for i, step_name in enumerate(steps):
        is_current = i == current_step
        is_completed = i < current_step
        
        step_container = QWidget()
        step_lay = QVBoxLayout(step_container)
        step_lay.setContentsMargins(0, 0, 0, 0)
        step_lay.setSpacing(Spacing.XXS)

        # Circle with number
        circle = QLabel(str(i + 1))
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setFixedSize(32, 32)
        circle.setStyleSheet(
            f"QLabel {{ font-size: {Font.SM}px; font-weight: {Font.BOLD}; "
            f"border-radius: 16px; }}"
        )
        if is_completed:
            circle.setStyleSheet(circle.styleSheet() + 
                f"background: {p['success']}; color: white;")
        elif is_current:
            accent_text = p.get('on_accent', '#ffffff')
            circle.setStyleSheet(circle.styleSheet() + 
                f"background: {p['accent']}; color: {accent_text};")
        else:
            circle.setStyleSheet(circle.styleSheet() + 
                f"background: {p['surface']}; color: {p['text_dim']}; border: 2px solid {p['border']};")
        
        step_lay.addWidget(circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label
        label = QLabel(step_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"QLabel {{ font-size: {Font.XS}px; font-weight: {Font.REGULAR if not is_current else Font.BOLD}; "
            f"color: {p['text'] if is_current or is_completed else p['text_dim']}; }}"
        )
        step_lay.addWidget(label)

        lay.addWidget(step_container)

        # Connecting line (except last)
        if i < len(steps) - 1:
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFixedHeight(2)
            line.setFixedWidth(40)
            line.setStyleSheet(
                f"QFrame {{ background: {p['success'] if is_completed else p['border']}; "
                f"border: none; }}"
            )
            lay.addWidget(line, alignment=Qt.AlignmentFlag.AlignVCenter)

    return container


# ---------------------------------------------------------------------------
# Convenience namespace (module-like object)
# ---------------------------------------------------------------------------
class _DS:
    """Design System namespace - provides consistent UI components."""
    
    # Constants
    Spacing = Spacing
    Font = Font
    Size = Size
    Layout = Layout
    WindowSize = WindowSize
    
    # Component factories (staticmethods to avoid binding issues)
    make_line_edit = staticmethod(make_line_edit)
    make_combo_box = staticmethod(make_combo_box)
    make_date_edit = staticmethod(make_date_edit)
    make_spin_box = staticmethod(make_spin_box)
    make_text_edit = staticmethod(make_text_edit)
    make_card = staticmethod(make_card)
    make_card_v2 = staticmethod(make_card_v2)
    make_section = staticmethod(make_section)
    make_info_bar = staticmethod(make_info_bar)
    make_progress_indicator = staticmethod(make_progress_indicator)
    status_badge = staticmethod(status_badge)
    styled_button = staticmethod(styled_button)
    make_button_bar = staticmethod(make_button_bar)
    make_form_row = staticmethod(make_form_row)
    make_search_bar = staticmethod(make_search_bar)
    setup_table = staticmethod(setup_table)
    set_cell_text = staticmethod(set_cell_text)


# Global instance
DS = _DS()
