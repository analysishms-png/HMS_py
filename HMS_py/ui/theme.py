"""HMS_py Theme Engine — Light Frost Glass (glassmorphism).

Design tokens -> dynamic QSS. User apne colors Appearance dialog se
set kar sakta hai; sab QSettings ("HMS_py", "appearance") me save hota hai.

Research basis (uxpilot.ai glassmorphism guide):
  - blur + semi-transparent tint (10-30%) + subtle border
  - dark text on pale tint (light mode glass), light text on dark tint
  - glass ko background depth chahiye (aurora blobs) warna effect flat lagta hai
"""
from __future__ import annotations

import json

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

# ============================================================ tokens
# Default preset: "Ocean Frost" (light frost glass)
DEFAULTS: dict[str, str] = {
    # VB6 Classic (MDI Teal) — default now to match VB6 FODER/MDIForm1.frm exactly
    "mode": "light",
    "accent": "#000080",  # VB6 navy &H800000? Actually navy
    "accent_hover": "#0000a0",
    "accent_soft": "rgba(0, 0, 128, 0.12)",
    "bg": "#d4d0c8",  # VB6 button face gray (MainSetup bg)
    "surface": "#ffffff",
    "surface_solid": "#ffffff",
    "surface_hover": "#ffffff",
    "border": "#808080",
    "border_strong": "#404040",
    "text": "#000000",
    "text_dim": "#404040",
    "glass_tint": "#ffffff",
    "header_grad_top": "#d4d0c8",
    "header_grad_bottom": "#d4d0c8",
    "sidebar_tint": "#ffffff",
    "shadow": "rgba(0,0,0,0.25)",
    "success": "#008000",
    "warning": "#800000",
    "danger": "#c00000",
    "info": "#000080",
    "blob1": "#d4d0c8", "blob2": "#d4d0c8", "blob3": "#d4d0c8", "blob4": "#d4d0c8",
    "radius": "0",  # VB6 sharp corners, bevel
    "glass_opacity": "0.95",
    "bg_style": "solid",
    "bg_image_path": "",
    "sidebar_top": "#2b8c9d",
    "sidebar_bottom": "#0d4f60",
    "sidebar_text": "#ffffff",
    "sidebar_border": "#0a3d4a",
    "mdi_bg": "#aaffff",
    "vb_gray": "#d4d0c8",
    "vb_mint": "#c2e0ce",
    "vb_pale_yellow": "#ffffc0",
    "vb_pink": "#ffc0ff",
    "vb_navy": "#000080",
    "vb_maroon": "#800000",
}

# ============================================================ presets
PRESETS: dict[str, dict[str, str]] = {
    "Ocean Frost (default)": {
        "mode": "light",
        "accent": "#2563eb", "accent_hover": "#1d4ed8",
        "bg": "#eef3fb", "surface_solid": "#ffffff",
        "text": "#1e293b", "text_dim": "#64748b",
        "header_grad_top": "#dbeafe", "header_grad_bottom": "#eff6ff",
        "blob1": "#93c5fd", "blob2": "#c4b5fd", "blob3": "#99f6e4",
        "blob4": "#fbcfe8", "glass_opacity": "0.62",
    },
    "Midnight Glass": {
        "mode": "dark",
        "accent": "#8b5cf6", "accent_hover": "#7c3aed",
        "bg": "#141425", "surface_solid": "#1e1e32",
        "text": "#e7e9f5", "text_dim": "#9ca3c4",
        "header_grad_top": "#241f47", "header_grad_bottom": "#191632",
        "blob1": "#4c1d95", "blob2": "#1e3a8a", "blob3": "#0f766e",
        "blob4": "#831843", "glass_opacity": "0.45",
    },
    "Emerald Breeze": {
        "mode": "light",
        "accent": "#059669", "accent_hover": "#047857",
        "bg": "#ecfdf5", "surface_solid": "#ffffff",
        "text": "#064e3b", "text_dim": "#4b7c6f",
        "header_grad_top": "#d1fae5", "header_grad_bottom": "#f0fdfa",
        "blob1": "#6ee7b7", "blob2": "#a7f3d0", "blob3": "#99f6e4",
        "blob4": "#fde68a", "glass_opacity": "0.60",
    },
    "Sunset Amber": {
        "mode": "light",
        "accent": "#ea580c", "accent_hover": "#c2410c",
        "bg": "#fff7ed", "surface_solid": "#ffffff",
        "text": "#431407", "text_dim": "#9a5b3d",
        "header_grad_top": "#ffedd5", "header_grad_bottom": "#fffbeb",
        "blob1": "#fdba74", "blob2": "#fca5a5", "blob3": "#fde68a",
        "blob4": "#f9a8d4", "glass_opacity": "0.60",
    },
    "Rose Quartz": {
        "mode": "light",
        "accent": "#e11d48", "accent_hover": "#be123c",
        "bg": "#fdf2f8", "surface_solid": "#ffffff",
        "text": "#4c0519", "text_dim": "#9d5c75",
        "header_grad_top": "#fce7f3", "header_grad_bottom": "#fff1f2",
        "blob1": "#f9a8d4", "blob2": "#c4b5fd", "blob3": "#bae6fd",
        "blob4": "#fed7aa", "glass_opacity": "0.60",
    },
    "Graphite Pro": {
        "mode": "dark",
        "accent": "#38bdf8", "accent_hover": "#0ea5e9",
        "bg": "#0f172a", "surface_solid": "#1e293b",
        "text": "#e2e8f0", "text_dim": "#94a3b8",
        "header_grad_top": "#1e293b", "header_grad_bottom": "#0f172a",
        "blob1": "#0e7490", "blob2": "#334155", "blob3": "#155e75",
        "blob4": "#1e40af", "glass_opacity": "0.50",
    },
    "VB6 Classic (MDI Teal)": {
        "mode": "light",
        # VB6 dialog palette exact (MDIForm1 & Pict* colors)
        "accent": "#000080", "accent_hover": "#0000a0",  # VB6 navy
        "bg": "#d4d0c8",  # VB6 button face gray (classic)
        "surface_solid": "#ffffff",
        "surface": "rgba(255, 255, 255, 0.95)",
        "surface_hover": "#ffffff",
        "text": "#000000", "text_dim": "#404040",
        "header_grad_top": "#d4d0c8", "header_grad_bottom": "#d4d0c8",
        "border": "#808080", "border_strong": "#404040",
        "glass_tint": "#ffffff", "sidebar_tint": "#ffffff",
        "shadow": "rgba(0,0,0,0.25)",
        "success": "#008000", "warning": "#800000", "danger": "#c00000", "info": "#000080",
        "blob1": "#d4d0c8", "blob2": "#d4d0c8", "blob3": "#d4d0c8", "blob4": "#d4d0c8",
        "glass_opacity": "0.95", "radius": "0",
        "bg_style": "solid",
        # MDI teal sidebar still
        "sidebar_top": "#2b8c9d", "sidebar_bottom": "#0d4f60",
        "sidebar_text": "#ffffff", "sidebar_border": "#0a3d4a",
        "mdi_bg": "#aaffff", "vb_gray": "#d4d0c8", "vb_mint": "#c2e0ce",
        "vb_pale_yellow": "#ffffc0", "vb_pink": "#ffc0ff",
        "vb_navy": "#000080", "vb_maroon": "#800000",
    },
}

SETTINGS_KEY = "HMS_py/appearance"
_active: dict[str, str] = dict(DEFAULTS)


# ============================================================ helpers
def _is_dark(hex_color: str) -> bool:
    """Hex '#rrggbb' -> luminance check (glass text contrast ke liye)."""
    h = (hex_color or "").lstrip("#")
    if len(h) != 6:
        return False
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return False
    return (0.299 * r + 0.587 * g + 0.114 * b) < 128


def _tint_from(bg: str, mode: str) -> str:
    """Background se glass tint nikalo (light: white-ish, dark: bg tint)."""
    if mode == "dark":
        return _rgba(bg, 0.42)
    return "rgba(255, 255, 255, 0.55)"


def _rgba(color: str, alpha: float) -> str:
    """Hex color -> 'rgba(r, g, b, a)' string."""
    h = (color or "#000000").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return color
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return color
    return f"rgba({r}, {g}, {b}, {alpha})"


def _opacity_to_alpha(opacity_str) -> float:
    try:
        return max(0.0, min(1.0, float(opacity_str)))
    except (TypeError, ValueError):
        return 0.62


def _resolve(tokens: dict[str, str]) -> dict[str, str]:
    """User token overrides -> complete token set (derived values bharo)."""
    t = dict(DEFAULTS)
    mode = tokens.get("mode", t["mode"])
    t["mode"] = mode

    for k in ("accent", "accent_hover", "bg", "surface_solid", "text",
              "text_dim", "blob1", "blob2", "blob3", "blob4",
              "header_grad_top", "header_grad_bottom", "bg_style", "bg_image_path",
              "sidebar_top", "sidebar_bottom", "sidebar_text", "sidebar_border"):
        v = tokens.get(k)
        if v:
            t[k] = v

    try:
        op = max(0.10, min(0.92, float(tokens.get("glass_opacity",
                                                  t["glass_opacity"]))))
        t["glass_opacity"] = f"{op:.2f}"
    except (TypeError, ValueError):
        pass
    try:
        t["radius"] = str(max(0, min(18, int(tokens.get("radius",
                                                        t["radius"])))))
    except (TypeError, ValueError):
        pass

    alpha = _opacity_to_alpha(t["glass_opacity"])
    if mode == "dark":
        t["surface"] = _rgba(t["surface_solid"], alpha * 0.80)
        t["surface_hover"] = _rgba(t["surface_solid"], alpha * 0.95)
        t["border"] = "rgba(148, 163, 184, 0.22)"
        t["border_strong"] = "rgba(148, 163, 184, 0.40)"
        t["glass_tint"] = _rgba(t["surface_solid"], alpha * 0.55)
        t["sidebar_tint"] = _rgba(t["surface_solid"], alpha * 0.45)
        t["shadow"] = "rgba(0, 0, 0, 0.45)"
        t["success"] = "#34d399"
        t["warning"] = "#fbbf24"
        t["danger"] = "#f87171"
        t["info"] = "#38bdf8"
        t["accent_soft"] = _rgba(t["accent"], 0.25)
    else:
        t["surface"] = _rgba(t["surface_solid"], alpha)
        t["surface_hover"] = _rgba(t["surface_solid"],
                                   min(1.0, alpha + 0.20))
        t["border"] = "rgba(148, 163, 184, 0.35)"
        t["border_strong"] = "rgba(100, 116, 139, 0.50)"
        t["glass_tint"] = _rgba(t["surface_solid"], alpha)
        t["sidebar_tint"] = _rgba(t["surface_solid"], alpha * 0.75)
        t["shadow"] = "rgba(15, 23, 42, 0.18)"
        # VB6 parity: light mode bhi DEFAULTS ke classic hues rakhe
        # (#008000 green, #800000 maroon, #c00000 red, #000080 navy) —
        # pehle yahan hardcoded tailwind hues override kar dete the, isliye
        # VB6 Classic default runtime pe apply hi nahi hota tha.
        t["success"] = DEFAULTS["success"]
        t["warning"] = DEFAULTS["warning"]
        t["danger"] = DEFAULTS["danger"]
        t["info"] = DEFAULTS["info"]
        t["accent_soft"] = _rgba(t["accent"], 0.12)

    t["radius"] = t["radius"]
    # Sidebar derived colors: hover = top-stop se lighter, checked =
    # bottom-stop se darker, on_sidebar_text = contrast-safe label.
    t["sidebar_hover"] = _mix(t["sidebar_top"], "#ffffff", 0.18)
    t["sidebar_checked"] = _mix(t["sidebar_bottom"], "#000000", 0.30)
    t["on_sidebar_text"] = ("#0f172a" if not _is_dark(t["sidebar_bottom"])
                            else "#ffffff")
    # WCAG fix: light accent pe white text 2:1 tak gir jaata hai —
    # accent luminance se button/selection text color derive karo.
    t["on_accent"] = ("#0f172a" if not _is_dark(t["accent"])
                      else "#ffffff")
    t.update(_resolve_status(tokens, t["mode"]))
    return t


def _glass_qss(t: dict[str, str]) -> str:
    """Token set -> full application stylesheet (light frost glass)."""
    R = int(t.get("radius", 10))
    return f"""
/* ═══════════ HMS Light Frost Glass ═══════════ */
* {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: {t['text']};
    outline: none;
}}
/* NOTE: universal transparent rule pehle, phir window bg —
   equal specificity me last rule jeetta hai (BUG FIX: warna
   QDialog/QMainWindow transparent ho ke black render hota hai). */
QWidget {{ background-color: transparent; color: {t['text']}; }}
QStackedWidget {{ background: transparent; }}
QMainWindow, QDialog {{
    background-color: {t['bg']};
    color: {t['text']};
}}

/* ── Menus ── */
QMenuBar {{
    background: {t['glass_tint']};
    color: {t['text']};
    border-bottom: 1px solid {t['border']};
    padding: 2px;
}}
QMenuBar::item {{
    background: transparent; padding: 6px 12px; border-radius: 6px;
}}
QMenuBar::item:selected {{ background: {t['accent_soft']}; }}
QMenu {{
    background: {t['surface_hover']};
    border: 1px solid {t['border']};
    border-radius: {R}px; padding: 6px;
}}
QMenu::item {{ padding: 8px 24px; border-radius: 6px; }}
QMenu::item:selected {{ background: {t['accent']}; color: {t['on_accent']}; }}
QMenu::item:disabled {{ color: {t['text_dim']}; }}
QMenu::separator {{ height: 1px; background: {t['border']}; margin: 4px 8px; }}

/* ── Buttons ── */
QPushButton {{
    background: {t['surface_hover']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: {R}px;
    padding: 8px 20px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {t['glass_tint']};
    border-color: {t['accent']};
}}
QPushButton:pressed {{ background: {t['accent_soft']}; }}
QPushButton:disabled {{
    background: transparent; color: {t['text_dim']};
    border-color: {t['border']};
}}
QPushButton[accent="true"] {{
    background: {t['accent']}; color: {t['on_accent']}; border: none;
    font-weight: 700; padding: 8px 20px; min-height: 20px;
}}
QPushButton[accent="true"]:hover {{ background: {t['accent_hover']}; }}
QPushButton[accent="true"]:pressed {{ background: {t.get('accent_pressed', t['accent_hover'])}; }}
QPushButton[success="true"] {{
    background: {t['success']}; color: #ffffff; border: none;
    font-weight: 600; padding: 6px 16px; min-height: 20px;
}}
QPushButton[success="true"]:hover {{ opacity: 0.9; }}
QPushButton[danger="true"] {{
    background: {t['danger']}; color: #ffffff; border: none;
    font-weight: 600; padding: 6px 16px; min-height: 20px;
}}
QPushButton[danger="true"]:hover {{ opacity: 0.9; }}
QPushButton[role="danger"] {{
    background: {t['danger']}; color: #ffffff; border: none;
    font-weight: 600; padding: 6px 16px; border-radius: {R}px; min-height: 20px;
}}
QPushButton[role="danger"]:hover {{ opacity: 0.9; }}
QPushButton[role="warning"] {{
    background: {t['warning']}; color: #ffffff; border: none;
    font-weight: 600; padding: 6px 16px; border-radius: {R}px; min-height: 20px;
}}
QPushButton[role="warning"]:hover {{ opacity: 0.9; }}
QPushButton[role="success"] {{
    background: {t['success']}; color: #ffffff; border: none;
    font-weight: 600; padding: 6px 16px; border-radius: {R}px; min-height: 20px;
}}
QPushButton[role="success"]:hover {{ opacity: 0.9; }}

/* ── Inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background: {t['glass_tint']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: {R}px;
    padding: 8px 12px;
    selection-background-color: {t['accent']};
    selection-color: {t['on_accent']};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1.5px solid {t['accent']};
    background: {t['surface_hover']};
}}
QLineEdit:read-only {{
    background: {t['accent_soft']}; color: {t['text_dim']};
}}
QComboBox {{
    background: {t['glass_tint']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: {R}px; padding: 8px 12px; min-width: 120px;
}}
QComboBox:hover {{ border-color: {t['accent']}; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow {{
    image: none; border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {t['text_dim']}; margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {t['surface_hover']}; color: {t['text']};
    border: 1px solid {t['border']}; border-radius: {R}px;
    selection-background-color: {t['accent']};
    selection-color: {t['on_accent']};
    padding: 4px;
}}

/* ── Tables ── */
QTableWidget, QTableView {{
    background: {t['glass_tint']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: {R}px;
    gridline-color: {t['border']};
    selection-background-color: {t['accent']};
    selection-color: {t['on_accent']};
    alternate-background-color: {t['accent_soft']};
    font-size: 12px;
}}
QTableWidget::item, QTableView::item {{ padding: 6px 8px; }}
QTableWidget::item:selected, QTableView::item:selected {{
    background: {t['accent']}; color: {t['on_accent']};
}}
QHeaderView::section {{
    background: {t['header_grad_top']};
    color: {t['text']};
    border: none;
    border-bottom: 2px solid {t['accent']};
    padding: 8px;
    font-weight: bold; font-size: 12px;
}}
QTableCornerButton::section {{ background: {t['header_grad_top']}; }}

/* ── Group / Tabs ── */
QGroupBox {{
    background: {t['glass_tint']};
    border: 1px solid {t['border']};
    border-radius: {R + 2}px;
    margin-top: 12px;
    padding: 16px 12px 12px 12px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 4px 12px; color: {t['accent']}; font-weight: bold;
}}
QTabWidget::pane {{
    background: {t['glass_tint']};
    border: 1px solid {t['border']}; border-radius: {R}px; padding: 4px;
}}
QTabBar::tab {{
    background: transparent; color: {t['text_dim']};
    border: 1px solid {t['border']}; border-bottom: none;
    border-top-left-radius: {R}px; border-top-right-radius: {R}px;
    padding: 10px 20px; margin-right: 2px; font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {t['glass_tint']}; color: {t['accent']};
    border-bottom: 2px solid {t['accent']};
}}
QTabBar::tab:hover {{ color: {t['text']}; }}

/* ── Scroll / Status / Tool ── */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: {t['border_strong']}; border-radius: 5px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {t['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{
    background: {t['border_strong']}; border-radius: 5px; min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: {t['accent']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QStatusBar {{
    background: {t['glass_tint']};
    color: {t['text_dim']};
    border-top: 1px solid {t['border']};
    font-size: 12px; padding: 4px 12px; min-height: 24px;
}}
QToolBar {{
    background: {t['glass_tint']};
    border-bottom: 1px solid {t['border']}; spacing: 6px; padding: 4px;
}}
QSplitter::handle {{ background: {t['border']}; }}
QSplitter::handle:horizontal {{ width: 2px; }}
QSplitter::handle:vertical {{ height: 2px; }}

/* ── Check / Radio / Progress ── */
QCheckBox, QRadioButton {{ spacing: 8px; color: {t['text']}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px; height: 18px;
    border: 2px solid {t['border_strong']};
    background: {t['glass_tint']};
}}
QCheckBox::indicator {{ border-radius: 5px; }}
QRadioButton::indicator {{ border-radius: 10px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {t['accent']}; border-color: {t['accent']};
}}
QProgressBar {{
    background: {t['glass_tint']};
    border: 1px solid {t['border']}; border-radius: 6px;
    text-align: center; color: {t['text']}; height: 20px;
}}
QProgressBar::chunk {{ background: {t['accent']}; border-radius: 5px; }}

/* ── Tooltip ── */
QToolTip {{
    background: {t['surface_solid']}; color: {t['text']};
    border: 1px solid {t['accent']}; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
}}

/* ── Sidebar ── */
QFrame[sidebar="true"] {{
    background: {t['sidebar_tint']};
    border-right: 1px solid {t['border']};
}}
QPushButton[sidebar-btn="true"] {{
    background: transparent; color: {t['text_dim']};
    border: none; border-radius: {R}px;
    padding: 10px 16px; text-align: left;
    font-size: 13px; font-weight: 500;
}}
QPushButton[sidebar-btn="true"]:hover {{
    background: {t['accent_soft']}; color: {t['text']};
    border-left: 3px solid {t['accent']}; padding-left: 13px;
}}
QPushButton[sidebar-btn="true"]:checked {{
    background: {t['accent']}; color: {t['on_accent']};
    font-weight: bold; border-left: 3px solid {t['accent']};
    padding-left: 13px;
}}
QPushButton[sidebar-btn="true"]:checked:hover {{
    background: {t['accent_hover']}; color: {t['on_accent']};
}}

/* ── Glass card / header (custom widgets) ── */
QFrame[glassCard="true"] {{
    background: {t['glass_tint']};
    border: 1px solid {t['border']};
    border-radius: {R + 2}px;
}}
QLabel[glassTitle="true"] {{
    background: transparent; color: {t['text']};
    font-size: 18px; font-weight: bold; padding: 4px;
}}
QLabel[glassSub="true"] {{
    background: transparent; color: {t['text_dim']}; font-size: 13px;
}}

/* ── Theme toggle ── */
QPushButton#themeToggle {{
    background: {t['glass_tint']}; color: {t['text_dim']};
    border: 1px solid {t['border']}; border-radius: 16px;
    font-size: 11px; font-weight: bold;
}}
QPushButton#themeToggle:hover {{
    border-color: {t['accent']}; color: {t['text']};
}}
QPushButton#themeToggle:checked {{
    background: {t['accent']}; color: {t['on_accent']};
}}
/* ── VB6 Classic bevel override (radius==0 → VB6 outset/inset) ── */
QPushButton[vb6="true"] {{
    background: #ffffc0; color: #000000;
    border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff;
    padding: 4px 18px; font-family: 'Arial'; font-weight: bold; border-radius: 0px;
}}
QPushButton[vb6="true"]:pressed {{ border-style: inset; }}
QLineEdit[vb6="true"] {{
    background: #ffffff; color: #000000;
    border: 2px inset; border-color: #808080 #ffffff #ffffff #808080;
    padding: 3px 6px; border-radius: 0px;
}}
QTableWidget[vb6="true"] {{
    background: #ffffff; gridline-color: #808080; border: 2px inset;
    border-color: #808080 #ffffff #ffffff #808080; border-radius: 0px;
}}
QHeaderView[vb6="true"]::section {{
    background: #d4d0c8; border: 1px outset; border-color: #ffffff #808080 #808080 #ffffff;
    padding: 3px; border-radius: 0px;
}}
{chr(10) + "/* VB6 mode: bevel buttons (R==0) */" + chr(10) + "QPushButton { border: 2px outset; border-color: #ffffff #808080 #808080 #ffffff; border-radius: 0px; }" + chr(10) + "QPushButton:pressed { border-style: inset; }" if R==0 else ""} 
"""


# ============================================================ palette
def palette() -> dict[str, str]:
    """Active token set (copy). Derived keys (sidebar_hover/checked,
    on_sidebar_text, on_accent, status colors) guaranteed — agar
    apply_theme abhi tak na chala ho to abhi resolve karo."""
    global _active
    if "sidebar_hover" not in _active or "on_accent" not in _active:
        _active = _resolve(_active)
    return dict(_active)


def accent() -> str:
    return _active["accent"]


# ============================================================ status palette
# Semantic status colors — room status, expense Dr/Cr, KOT state jaise
# jagah use hote hain. Hardcoded pastels ki jagah mode-adaptive: light
# presets me pale tint + dark text, dark presets me glassy tint + light text.
# Base status hues: mode defaults (user Appearance dialog se override kare).
_STATUS_BASE_LIGHT = {
    # VB6 classic hues (DEFAULTS ke saath sync — appearance dialog seeding)
    "success": "#008000", "warning": "#800000",
    "danger": "#c00000", "neutral": "#404040",
}
_STATUS_BASE_DARK = {
    "success": "#34d399", "warning": "#fbbf24",
    "danger": "#f87171", "neutral": "#94a3b8",
}
_STATUS_NAMES = ("success", "warning", "danger", "neutral")
_STATUS_KEYS = tuple(f"{n}{s}" for n in _STATUS_NAMES
                     for s in ("", "_bg", "_text")) \
    + tuple(f"on_{n}" for n in _STATUS_NAMES)


def _mix(c1: str, c2: str, t: float) -> str:
    """Do hex colors blend karo: t=0 -> c1, t=1 -> c2 (QColor-safe hex)."""
    h1 = (c1 or "#000000").lstrip("#")
    h2 = (c2 or "#000000").lstrip("#")
    if len(h1) != 6 or len(h2) != 6:
        return c1
    try:
        a = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
        b = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    except ValueError:
        return c1
    return "#{:02x}{:02x}{:02x}".format(
        *(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))


def _resolve_status(tokens: dict[str, str], mode: str) -> dict[str, str]:
    """User status bases (ya mode defaults) se derived palette banao.

    bg = cell tint (light: white-mix, dark: dark-mix), text = readable
    variant, on_* = base ke upar contrast-safe label (WCAG).
    """
    out: dict[str, str] = {}
    defaults = _STATUS_BASE_DARK if mode == "dark" else _STATUS_BASE_LIGHT
    for name in _STATUS_NAMES:
        base = tokens.get(name) or defaults[name]
        out[name] = base
        if mode == "dark":
            out[f"{name}_bg"] = _mix(base, "#101020", 0.78)
            out[f"{name}_text"] = _mix(base, "#ffffff", 0.62)
        else:
            out[f"{name}_bg"] = _mix(base, "#ffffff", 0.86)
            out[f"{name}_text"] = _mix(base, "#000000", 0.70)
        out[f"on_{name}"] = ("#ffffff" if _is_dark(base) else "#0f172a")
    return out


def status_colors() -> dict[str, str]:
    """User-editable semantic status palette (active tokens se derived).

    Keys: success/warning/danger/neutral (base hues) + *_bg (soft cell
    tint) + *_text (readable text variant) + on_* (contrast-safe label).
    """
    return {k: _active[k] for k in _STATUS_KEYS if k in _active}


def status_base_defaults(mode: str = "light") -> dict[str, str]:
    """Mode ke liye default status base hues (dialog seeding ke liye)."""
    src = _STATUS_BASE_DARK if mode == "dark" else _STATUS_BASE_LIGHT
    return dict(src)


def is_dark() -> bool:
    return _active["mode"] == "dark"


# ============================================================ apply/save
def apply_theme(app: QApplication, theme: str | None = None) -> None:
    """Load saved tokens (ya 'dark'/'light' quick mode) aur QSS lagao."""
    global _active
    saved = load_tokens()
    if theme in ("dark", "light"):
        saved["mode"] = theme
    _active = _resolve(saved)
    app.setStyleSheet(_glass_qss(_active))
    from PyQt6.QtGui import QPalette, QColor
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(_active["bg"]))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(_active["text"]))
    pal.setColor(QPalette.ColorRole.Base, QColor(_active["surface_solid"]))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(_active["bg"]))
    pal.setColor(QPalette.ColorRole.Text, QColor(_active["text"]))
    pal.setColor(QPalette.ColorRole.Button, QColor(_active["surface_solid"]))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(_active["text"]))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(_active["accent"]))
    pal.setColor(QPalette.ColorRole.HighlightedText,
                 QColor(_active["on_accent"]))
    app.setPalette(pal)


def apply_tokens(app: QApplication, tokens: dict[str, str]) -> None:
    """User edits -> live re-apply (preview ke liye)."""
    global _active
    _active = _resolve(tokens)
    app.setStyleSheet(_glass_qss(_active))


def save_tokens(tokens: dict[str, str]) -> None:
    """Tokens ko QSettings me persist karo (JSON blob)."""
    s = QSettings("HMS_py", "appearance")
    keep = ("mode", "accent", "accent_hover", "bg", "surface_solid", "text",
            "text_dim", "blob1", "blob2", "blob3", "blob4",
            "header_grad_top", "header_grad_bottom", "glass_opacity",
            "radius", "success", "warning", "danger", "neutral",
            "sidebar_top", "sidebar_bottom", "sidebar_text",
            "sidebar_border", "bg_style", "bg_image_path")
    s.setValue("tokens", json.dumps({k: tokens.get(k, "") for k in keep}))
    s.sync()


def load_tokens() -> dict[str, str]:
    """Saved user tokens (empty dict agar nahi mile)."""
    s = QSettings("HMS_py", "appearance")
    raw = s.value("tokens", "")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return {k: str(v) for k, v in data.items() if v}
    except (ValueError, TypeError):
        return {}


def reset_tokens() -> None:
    s = QSettings("HMS_py", "appearance")
    s.clear()
    s.sync()


def preset_tokens(preset_name: str) -> dict[str, str]:
    """Preset naam -> token override dict (save ke liye ready)."""
    base = {"mode": PRESETS.get(preset_name, PRESETS["Ocean Frost (default)"])
            .get("mode", "light")}
    base.update(PRESETS.get(preset_name, {}))
    return base


def toggle_theme(app: QApplication) -> str:
    """Dark/light glass mode switch (tokens preserve karke)."""
    tokens = dict(load_tokens()) or dict(DEFAULTS)
    tokens["mode"] = "light" if _active["mode"] == "dark" else "dark"
    save_tokens(tokens)
    apply_theme(app)
    return _active["mode"]


def current_theme() -> str:
    return _active["mode"]


def get_font(size: int = 13, bold: bool = False) -> QFont:
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    return f
