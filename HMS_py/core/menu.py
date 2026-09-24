"""Menu model v3 - DB-driven (User_Module + User1), evidence-documented.

EVIDENCE:
- User_Module.code == MDIForm1.frm VB6 menu control names (FA, Mast,
  FrontDesk...); flag: 9=sidebar root, 1=submenu header, 0=leaf.
- Nesting: flag=1 item ke baad same-code flag=0 rows = uske children
  (probe: 43 'Tax Master' GENMas flag=1 -> 44-47 GENMas flag=0).
  NOTE: decompiled MDIForm1.frm nesting flattened hai - flag hi sachi.
- Menubar groups = DISTINCT Module_Name, MIN(srno) order.
  PROD screenshot order se chhota antar hai (EPABX/SmartCard hidden,
  Members Mgmt last) - REQUIRES MANUAL REVIEW (runtime menu-order ka
  koi column nahi mila; MIN(srno) sabse defensible).
- Sidebar = Analysis.ini key 9 (#-list, & accelerator strip karke),
  User_Module flag=9 se resolve.
- Rights: User1 (USER_NAME, SRNO==User_Module.srno); rows na hon =
  full access (SA 617/617).
"""
from __future__ import annotations

from HMS_py.core import db


def roots() -> list[dict]:
    """flag=9 sidebar roots [{code, name, srno}].

    Offline guard (VB6 MDIForm1 `On Error Resume Next` parity): DB na ho
    to khali list — shell ko crash hone ke bajaye SA template/cache
    fallback dikhana hai.
    """
    try:
        rows = db.query(
            "SELECT code, name, srno FROM User_Module "
            "WHERE flag='9' ORDER BY srno")
    except Exception:
        return []
    return [{"code": r[0], "name": r[1], "srno": r[2]}
            for r in rows]


def sidebar_modules() -> list[dict]:
    """Ini key 9 order; fallback: sab roots (utility rows chhod kar)."""
    cfg = db.load_config()
    wanted = cfg.get("modules")
    all_roots = roots()
    if not wanted:
        return [r for r in all_roots
                if str(r["name"]) not in ("-", "Windows", "Exit", "MDI",
                                          "PlanPopup",
                                          "Sale Bill Modification")]
    low = {str(r["name"]).lower(): r for r in all_roots}
    out = []
    for w in wanted:
        w = str(w).replace("&", "").strip().lower()
        if w in low:
            out.append(low[w])
    return out or [r for r in all_roots
                   if str(r["name"]) not in ("-", "Windows", "Exit", "MDI")]


def user_allowed_srnos(username: str) -> set | None:
    """User1.SRNO set; None = full access.

    Offline/DB-error -> None (full access) — VB6 jaisa fail-open so app
    offline bhi menu dikhaaye.
    """
    try:
        rows = db.query("SELECT SRNO FROM User1 WHERE USER_NAME = ?",
                        (username,))
    except Exception:
        return None
    if not rows:
        return None
    return {r[0] for r in rows}


def menu_name_allowed(menu_name: str, username: str = "SA") -> bool:
    """Check whether a menu leaf is permitted for the given user.

    Logic mirrors DB-driven rights: if User1 has no row for this user,
    full access is granted. If there are rights, the menu leaf must map
    to a User_Module.srno recorded for this user.
    """
    if not menu_name or not str(menu_name).strip():
        return True
    allowed = user_allowed_srnos(username)
    if allowed is None:
        return True

    def _normalize(value: str) -> str:
        v = str(value).strip()
        v = v.replace("- HMS_py", "").strip()
        v = v.replace("- HMS", "").strip()
        v = "".join(ch for ch in v if ch not in "\r\n")
        while "  " in v:
            v = v.replace("  ", " ")
        if "(" in v and v.rstrip().endswith(")"):
            base = v.rsplit("(", 1)[0].strip()
            if base:
                v = base
        return v.strip().lower()

    name = _normalize(menu_name)
    try:
        rows = db.query(
            "SELECT srno, name FROM User_Module WHERE LOWER(name) = LOWER(?) "
            "OR LOWER(name) = LOWER(?)",
            (menu_name, name),
        )
    except Exception:
        return True
    if not rows:
        return True
    # Support UI titles like 'Session Master (POS)' matching DB leaf 'Session Master'.
    return any(int(r[0]) in allowed for r in rows if r and r[0] is not None)


def _group_rows(module_name: str) -> list[dict]:
    rows = db.query(
        "SELECT code, name, flag, srno FROM User_Module "
        "WHERE Module_Name = ? AND flag <> '9' ORDER BY srno",
        (module_name,))
    return [{"code": r[0], "name": r[1], "flag": r[2], "srno": r[3]}
            for r in rows]


def _build_dropdown(rows: list[dict], allowed: set | None) -> list[dict]:
    """flag nesting: flag=1 => submenu; same-code flag=0 follow => children."""
    out: list[dict] = []
    cur: dict | None = None

    def leaf_ok(it: dict) -> bool:
        return allowed is None or it["srno"] is None or it["srno"] in allowed

    for r in rows:
        it = {"name": r["name"], "code": r["code"], "srno": r["srno"],
              "children": []}
        if r["flag"] == 1:
            cur = it
            out.append(cur)
        elif cur is not None and r["code"] == cur["code"]:
            if leaf_ok(it):
                cur["children"].append(it)
        else:
            cur = None
            if leaf_ok(it):
                out.append(it)
    # prune empty submenus (rights ne sab children kaat diye)
    return [it for it in out
            if it["children"] or leaf_ok(it)]


def menubar_for(module_name: str, username: str = "SA") -> list[dict]:
    """Sidebar module -> [{name, items:[{name, srno, children:[...]}]}].

    Pehla row (name == module name, flag=1) = menu-title khud - skip."""
    allowed = user_allowed_srnos(username)
    groups: list[dict] = []
    seen: dict[str, dict] = {}
    # groups = DISTINCT Module_Name is module ki range me
    root = next((r for r in roots() if r["name"] == module_name), None)
    if root is None:
        return []
    nxt = next((r["srno"] for r in roots() if r["srno"] > root["srno"]),
               10 ** 9)
    try:
        rows = db.query(
            "SELECT code, name, flag, srno, Module_Name FROM User_Module "
            "WHERE srno >= ? AND srno < ? AND flag <> '9' ORDER BY srno",
            (root["srno"], nxt))
    except Exception:
        return []
    for r in rows:
        g = r[4] or r[1]
        if g not in seen:
            entry = {"name": g, "rows": []}
            seen[g] = entry
            groups.append(entry)
        seen[g]["rows"].append(
            {"code": r[0], "name": r[1], "flag": r[2], "srno": r[3]})
    out = []
    for g in groups:
        rows_g = g["rows"]
        # Title-skip sirf jab group ka pehla flag=1 row title ho AUR aage
        # rows hon (single flag=1 row = khud action item, e.g. Messaging
        # InBox/OutBox - VB6 me unpe click hota tha).
        if (rows_g and len(rows_g) > 1 and rows_g[0]["flag"] == 1 and
                str(rows_g[0]["name"]).lower() == str(g["name"]).lower()):
            rows_g = rows_g[1:]
        items = _build_dropdown(rows_g, allowed)
        if items:
            out.append({"name": g["name"], "items": items})
    return out
