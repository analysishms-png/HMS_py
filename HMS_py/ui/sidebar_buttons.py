"""Dynamic Sidebar UI Buttons — built from User_Module per-module wise (VB6 MDIForm1 logic).

DATA FLOW (VB6 → Python):
   User_Module table (flag='9') ──→ menu.roots() ──→ build_sidebar_buttons()
   Analysis.ini key 9 ──→ module display order
   menuHelp table ──→ user-specific permissions (restricted users)
   Opt1=module, Opt2=group, Opt3=item, Opt4=sub-item (VB6 MDI tree)

Each button is a dict: {icon, label, mod_target, action, shortcut}
  - icon: emoji/char for sidebar display
  - label: display text
  - mod_target: module name used to load menu bar on click
  - action: callable or None (for direct openers)
  - shortcut: Alt+1..9 for first 9 module buttons

VB6 Logic mapping:
  - User_Module flag='9' → sidebar root (L1 node)
  - Flag='N' + Opt1<>0 + O2=O3=O4=0 → sidebar root (L1 node)
  - Flag='E' → entry form leaf
  - Flag='R' → report leaf
  - Flag='V' → hidden (never shown)
  - Param_Str 'AEDP' → full rights, '***P' → print-only
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HMS_py.core import menu as _menu
from HMS_py.core import menu_help as _mh
from HMS_py.ui import theme as _theme


# ── Icon mapping (CV6 module names → sidebar icons) ──────────────
_ICONS: dict[str, str] = {
    "dashboard":       "📊",
    "reservations":    "📅",
    "reservation":     "📅",
    "frontoffice":     "🏨",
    "front office":    "🏨",
    "roomstatus":      "🚪",
    "room status":     "🚪",
    "guests":          "👥",
    "guest":           "👥",
    "foliobilling":    "💳",
    "folio":           "💳",
    "checkin":         "📥",
    "checkout":        "📤",
    "housekeeping":    "🧹",
    "house keeping":   "🧹",
    "pointofsale":     "🍽",
    "point of sale":   "🍽",
    "pos":             "🍽",
    "inventory":       "📦",
    "banquet":         "🥂",
    "nightaudit":      "🌙",
    "night audit":     "🌙",
    "finance":         "💰",
    "mainsetup":       "📋",
    "main setup":      "📋",
    "hrpayroll":       "👔",
    "hr payroll":      "👔",
    "hr":              "👔",
    "membersmgmt":     "🎗",
    "members mgmt":    "🎗",
    "members":         "🎗",
    "epabx":           "📡",
    "messaging":       "💬",
    "extras":          "📨",
    "extrasms":        "📨",
    "utility":         "🛠",
    "dashboards":      "📊",
    "reports":         "📋",
    "report":          "📋",
}

_LABEL_ALIAS: dict[str, str] = {
    "reservations": "Reservations",
    "housekeeping": "Housekeeping",
    "pointofsale":  "Point of Sale",
    "hrpayroll":    "HR / Payroll",
    "hr payroll":   "HR / Payroll",
    "membersmgmt":  "Members Mgmt",
    "extrasms":     "Extras / SMS",
    "frontoffice":  "Front Office",
}

# ── Direct action shortcuts (no menu load) ───────────────────────
DIRECT_ACTIONS: dict[str, str] = {
    "__action_checkin":       "Check In",
    "__action_checkout":      "Check Out",
    "__action_room_status":   "Room Status",
    "__action_guest_profile": "Guest Profile",
    "__action_folio":         "Folio Log",
}

# ── Auto-open modules (open primary form + load menu) ────────────
AUTO_OPEN: dict[str, str] = {
    "reservation": "Reservation/Cancellation",
    "main setup":  "Main Setup",
    "front office": "Front Office",
    "dashboard":   "Dashboard",
}


def _icon_for(name: str) -> str:
    """Get icon for a module name (normalized key lookup)."""
    key = "".join(ch for ch in str(name or "").lower() if ch.isalnum())
    return _ICONS.get(key, "📁")


def _label_for(name: str) -> str:
    """Get display label for a module name."""
    key = "".join(ch for ch in str(name or "").lower() if ch.isalnum())
    return _LABEL_ALIAS.get(key, str(name or "").title())


def _norm_caption(name: str) -> str:
    """Normalize caption for comparison (matches menu_help._norm_caption)."""
    s = str(name or "").strip()
    s = s.replace("\r", "").replace("\n", "")
    s = s.replace("- HMS_py", "").strip()
    s = s.replace("- HMS", "").strip()
    while "  " in s:
        s = s.replace("  ", " ")
    if "(" in s and s.rstrip().endswith(")"):
        base = s.rsplit("(", 1)[0].strip()
        if base:
            s = base
    return s.strip().lower()


def _build_action_buttons() -> list[dict]:
    """Build the ACTIONS section buttons (pinned quick-access shortcuts).

    VB6 MDIForm1: These are not from menuHelp — they are hardcoded
    quick-action buttons available to all users.
    """
    return [
        {"icon": "📊", "label": "Dashboard",       "mod_target": "Dashboard",
         "action": None, "shortcut": "Alt+1", "type": "action"},
        {"icon": "🚪", "label": "Room Status",     "mod_target": "__action_room_status",
         "action": "Room Status", "shortcut": "Alt+2", "type": "action"},
        {"icon": "👥", "label": "Guests",          "mod_target": "__action_guest_profile",
         "action": "Guest Profile", "shortcut": "Alt+3", "type": "action"},
        {"icon": "💳", "label": "Folio/Billing",   "mod_target": "__action_folio",
         "action": "Folio Log", "shortcut": "Alt+4", "type": "action"},
        {"icon": "📥", "label": "Check-In",        "mod_target": "__action_checkin",
         "action": "Check In", "shortcut": "Alt+5", "type": "action"},
        {"icon": "📤", "label": "Check-Out",       "mod_target": "__action_checkout",
         "action": "Check Out", "shortcut": "Alt+6", "type": "action"},
    ]


def _build_module_buttons(user: str = "SA") -> list[dict]:
    """Build MODULES section buttons from User_Module per-module wise.

    Primary source: User_Module table (flag='9') via menu.roots()
    User-specific permissions: menuHelp table for restricted users.
    Analysis.ini key 9 defines the display order.
    """
    _DASHBOARD_NORM = "dashboard"
    _user = user or "SA"

    # Get roots from User_Module (per-module wise)
    roots = _menu.roots()
    # Filter out non-sidebar items
    all_roots = [r for r in roots
                 if str(r.get("name", "")).strip() not in ("-", "Windows", "Exit", "MDI", "PlanPopup")]

    # For restricted users, filter by menuHelp permissions
    if not _mh.full_access(_user):
        allowed_captions = set(_mh.by_caption(_user).keys())
        all_roots = [r for r in all_roots
                     if _mh._norm_caption(r.get("name", "")).lower() in allowed_captions]

    buttons = []
    idx = 7  # Action buttons use Alt+1..6, modules start at Alt+7
    for r in all_roots:
        name = r.get("name", "")
        if _norm_caption(name) == _DASHBOARD_NORM:
            continue  # Dashboard is in ACTIONS section
        btn = {
            "icon": _icon_for(name),
            "label": _label_for(name),
            "mod_target": name,
            "action": None,
            "shortcut": f"Alt+{idx}" if idx <= 15 else None,
            "type": "module",
            "opt1": None,
            "code": r.get("code"),
            "srno": r.get("srno"),
        }
        idx += 1
        buttons.append(btn)
    return buttons


def build_all_buttons(user: str = "SA") -> dict[str, list[dict]]:
    """Build complete sidebar button structure.

    Returns: {"ACTIONS": [...], "MODULES": [...]}
    """
    actions = _build_action_buttons()
    modules = _build_module_buttons(user)
    return {"ACTIONS": actions, "MODULES": modules}


def get_sidebar_sources(user: str = "SA") -> list[dict]:
    """Get raw sidebar module sources from User_Module (per-module wise).

    Primary: User_Module table (flag='9')
    Fallback for restricted users: menuHelp table
    """
    _user = user or "SA"
    roots = _menu.roots()
    filtered = [r for r in roots
                if str(r.get("name", "")).strip() not in ("-", "Windows", "Exit", "MDI", "PlanPopup")]
    if not _mh.full_access(_user):
        allowed_captions = set(_mh.by_caption(_user).keys())
        filtered = [r for r in filtered
                     if _mh._norm_caption(r.get("name", "")).lower() in allowed_captions]
    return [{"name": r.get("name", ""), "code": r.get("code"),
             "srno": r.get("srno"), "opt1": None} for r in filtered]


def get_module_tree(user: str = "SA") -> dict[str, list[dict]]:
    """Get full module tree from User_Module (per-module wise).

    Returns: {module_name: [{code, name, flag, srno, children...}]}
    """
    roots = _menu.roots()
    tree: dict[str, list[dict]] = {}
    for r in roots:
        name = r.get("name", "")
        if name and name.strip() not in ("-", "Windows", "Exit", "MDI"):
            tree.setdefault(name, []).append({
                "code": r.get("code"), "name": name,
                "flag": "9", "srno": r.get("srno"),
                "children": []})
    return tree


def get_all_modules(user: str = "SA") -> list[str]:
    """Get ordered list of all module names from User_Module."""
    roots = _menu.roots()
    seen: list[str] = []
    for r in roots:
        name = r.get("name", "")
        if name and name.strip() not in ("-", "Windows", "Exit", "MDI"):
            if name not in seen:
                seen.append(name)
    return seen


def build_qt_sidebar(parent, user: str = "SA", on_click=None):
    """Build the complete sidebar as Qt widgets.

    Args:
        parent: QWidget parent
        user: username (determines which User_Module rows to show)
        on_click: callback(module_name: str, button: QPushButton) or None
                   If None, uses the default MainWindow._on_sidebar_click

    Returns:
        (buttons: list[QPushButton], section_labels: list[QLabel])
    """
    from PyQt6.QtWidgets import QPushButton, QLabel, QScrollArea, QWidget, QVBoxLayout
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QCursor

    p = _theme.palette()
    accent = p.get('accent', '#4f46e5')
    accent_soft = p.get('accent_soft', 'rgba(79,70,229,0.12)')
    text = p.get('text', '#1e293b')
    text_dim = p.get('text_dim', '#64748b')

    all_btns = build_all_buttons(user)
    buttons: list[QPushButton] = []
    section_labels: list[QLabel] = []

    btn_qss = f"""
        QPushButton[sidebar-btn="true"] {{
            background: transparent;
            color: {text};
            border: none;
            border-radius: 6px;
            font-size: 10pt;
            font-weight: 500;
            text-align: left;
            padding: 7px 10px;
        }}
        QPushButton[sidebar-btn="true"]:hover {{
            background: {accent_soft};
            color: {accent};
        }}
        QPushButton[sidebar-btn="true"]:checked {{
            background: {accent_soft};
            color: {accent};
            border-left: 3.5px solid {accent};
            font-weight: 700;
        }}
    """

    for sec_title, items in all_btns.items():
        sec_lbl = QLabel(sec_title)
        sec_lbl.setStyleSheet(f"""
            color: {text_dim};
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 1px;
            padding-top: 8px;
            padding-bottom: 2px;
            padding-left: 6px;
            background: transparent;
        """)
        section_labels.append(sec_lbl)

        for item in items:
            b = QPushButton(f"{item['icon']}  {item['label']}")
            b.setProperty("sidebar-btn", True)
            b.setProperty("icon_only", item["icon"])
            b.setProperty("full_text", f"{item['icon']}  {item['label']}")
            b.setProperty("mod_target", item["mod_target"])
            b.setCheckable(True)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(btn_qss)
            b.setToolTip(item["label"])
            b.setAccessibleName(item["mod_target"])

            def _make_click_handler(mod_target, btn_widget):
                def handler():
                    if on_click:
                        on_click(mod_target, btn_widget)
                    elif hasattr(parent, '_on_sidebar_click'):
                        parent._on_sidebar_click(mod_target, btn_widget)
                return handler

            b.clicked.connect(_make_click_handler(item["mod_target"], b))
            buttons.append(b)

    return buttons, section_labels


def generate_sidebar_report(user: str = "SA") -> str:
    """Generate a text report of all sidebar buttons and their data.

    Data source: User_Module table (per-module wise) + menuHelp permissions.
    """
    lines = []
    ap = lines.append
    w = 70
    ap("=" * w)
    ap("HMS SIDEBAR BUTTONS — DYNAMIC REPORT")
    ap(f"User: {user}  |  Generated: User_Module (flag='9') + Analysis.ini key 9")
    ap("=" * w)
    ap("")

    # ACTIONS section
    actions = _build_action_buttons()
    ap("── ACTIONS (pinned quick-access) ──")
    for i, a in enumerate(actions, 1):
        ap(f"  {i}. {a['icon']} {a['label']:<20} target={a['mod_target']:<30} short={a['shortcut']}")
    ap("")

    # MODULES section
    modules = _build_module_buttons(user)
    ap("── MODULES (User_Module per-module wise) ──")
    for i, m in enumerate(modules, 7):
        opt1 = m.get("opt1") or "?"
        ap(f"  {m['shortcut'] or '?'}  {m['icon']} {m['label']:<20} target={m['mod_target']:<30} srno={m.get('srno')}")
    ap("")

    # User_Module data
    ap("── USER_MODULE RAW DATA ──")
    sources = get_sidebar_sources(user)
    ap(f"  User_Module count: {len(sources)}")
    for s in sources:
        ap(f"    {s['name']:<25} code={s.get('code')} srno={s.get('srno')}")
    ap("")

    ap("── USER_MODULE TREE ──")
    tree = get_module_tree(user)
    for mod_name, leaves in tree.items():
        ap(f"  {mod_name}: {len(leaves)} entries")
    ap("")
    ap("=" * w)
    ap("END REPORT")
    ap("=" * w)

    return "\n".join(lines)


if __name__ == "__main__":
    """Standalone test: print sidebar button report."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    report = generate_sidebar_report("SA")
    print(report)
    # Also write to file for reference
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "_qa", "sidebar_buttons_report.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {out_path}")


# ============================================================
# VB6-STYLE SIDEBAR (VB6 MDIForm1 appearance)
# ============================================================
VB6_COLORS = {
    "bg": "#d0d0d0",
    "panel": "#e8e8e8",
    "button_bg": "#d0d0d0",
    "button_fg": "#000000",
    "button_hover": "#c0c0c0",
    "button_selected": "#9dc3e6",
    "button_border": "#808080",
    "header_bg": "#000080",
    "header_fg": "#ffffff",
    "text": "#000000",
    "text_dim": "#404040",
}

VB6_SECTION_STYLE = """
    QLabel {
        background: #000080;
        color: #ffffff;
        font-size: 9pt;
        font-weight: bold;
        padding: 3px 6px;
        border: 1px solid #000080;
    }
"""

VB6_BUTTON_STYLE = """
    QPushButton[sidebar-btn="true"] {
        background: #d0d0d0;
        color: #000000;
        border: 1px solid #808080;
        border-radius: 0px;
        font-size: 9pt;
        font-weight: normal;
        text-align: left;
        padding: 4px 8px;
        padding-left: 8px;
    }
    QPushButton[sidebar-btn="true"]:hover {
        background: #c0c0c0;
        color: #000000;
        border: 1px solid #606060;
    }
    QPushButton[sidebar-btn="true"]:checked {
        background: #9dc3e6;
        color: #000000;
        border: 1px solid #406080;
        font-weight: bold;
    }
"""

VB6_COLLAPSE_STYLE = """
    QPushButton {
        background: #d0d0d0;
        color: #000000;
        border: 1px solid #808080;
        font-size: 8pt;
        font-weight: bold;
        padding: 2px 6px;
    }
    QPushButton:hover {
        background: #c0c0c0;
    }
"""

def get_vb6_sidebar_style(is_collapsed: bool = False) -> dict[str, str]:
    """Return VB6-style QSS strings for sidebar widgets."""
    return {
        "sidebar": f"""
            QFrame {{
                background: #d0d0d0;
                border-right: 2px solid #808080;
            }}
        """,
        "button": VB6_BUTTON_STYLE,
        "section": VB6_SECTION_STYLE,
        "collapse": VB6_COLLAPSE_STYLE,
        "scrollarea": "QScrollArea { border: none; background: #d0d0d0; }",
    }


def build_vb6_buttons(parent, user: str = "SA", on_click=None) -> tuple[list, list]:
    """Build VB6-style sidebar buttons (no icons, flat style).

    Returns: (buttons, section_labels)
    """
    from PyQt6.QtWidgets import QPushButton, QLabel
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QCursor

    all_btns = build_all_buttons(user)
    buttons: list = []
    section_labels: list = []

    for sec_title, items in all_btns.items():
        if sec_title == "ACTIONS":
            continue  # Skip ACTIONS in VB6 mode (too modern)
        sec_lbl = QLabel(sec_title.upper())
        sec_lbl.setStyleSheet(VB6_SECTION_STYLE)
        sec_lbl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        section_labels.append(sec_lbl)

        for item in items:
            b = QPushButton(item["label"])
            b.setProperty("sidebar-btn", True)
            b.setObjectName("vb6SidebarBtn")
            b.setCheckable(True)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(VB6_BUTTON_STYLE)
            b.setToolTip(item["label"])
            b.setAccessibleName(item["mod_target"])

            if item["mod_target"].startswith("__action_"):
                b.clicked.connect(
                    lambda _, ac=item.get("action", ""):
                    on_click(ac) if on_click else None)
            else:
                b.clicked.connect(
                    lambda _, m_name=item["mod_target"]:
                    on_click(m_name) if on_click else None)
            buttons.append(b)

    return buttons, section_labels
