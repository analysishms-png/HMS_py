"""menuHelp module-wise rights + leaf metadata + VB6 MDIForm1 dynamic menu.

Evidence (FODER):
- FaVoucher.bas: SELECT Param_Str AS UPrivilege, Module_Name FROM menuHelp
  WHERE UserName=? AND CompCode=? AND [Option]=?  -> in-form button rights.
- UserPermission.frm: Param_Str positions -> [ADD]=1st='A', [EDIT]=2nd='E',
  [DELETE]=3rd='D', [PRINT]=4th='P'.
- HMS.bas / MDIForm1.frm: Flag E/N => Param_Str='AEDP'; Flag R => '***P'.
- menuHelp1 = SA template (UserName='SA'); menuHelp = per-user copy.
- Flag: E=Entry/Form, R=Report, N=Node/header, V=Hidden.

No menuHelp row for user => full access (User1 pattern, menu.py:15-16).
"""
from __future__ import annotations

from HMS_py.core import db

_CACHE: dict = {}


def _comp() -> str:
    try:
        return str(db.get_comp_code() or "2")
    except Exception:
        return "2"


def _norm_caption(v) -> str:
    s = str(v or "")
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


def _load_user(username: str) -> list[dict]:
    """menuHelp rows for user (fallback: SA template if none)."""
    key = (username or "SA").upper()
    if key in _CACHE:
        return _CACHE[key]
    _cols = "[Option], Param_Str, Flag, Module_Name, Opt1, Opt2, Opt3, Opt4, Code"
    try:
        rows = db.query(
            f"SELECT {_cols} FROM menuHelp WHERE UserName = ? AND CompCode = ?",
            (username or "SA", _comp()),
        )
    except Exception:
        rows = []
    if not rows and username and username.upper() != "SA":
        try:
            rows = db.query(
                f"SELECT {_cols} FROM menuHelp WHERE UserName = 'SA' AND CompCode = ?",
                (_comp(),),
            )
        except Exception:
            rows = []
    if not rows:
        # CompCode-mismatch safety: SA template rows kisi bhi CompCode par
        try:
            rows = db.query(
                f"SELECT {_cols} FROM menuHelp WHERE UserName = 'SA'")
        except Exception:
            rows = []
    out = []
    for r in rows:
        try:
            out.append({
                "caption": _norm_caption(r[0]),
                "caption_disp": str(r[0] or "").strip(),  # original-case display (VB6 parity)
                "param": str(r[1] or "").strip(),
                "flag": str(r[2] or "").strip().upper(),
                "module": str(r[3] or "").strip(),
                "opt1": str(r[4] or "").strip(),
                "opt2": str(r[5] or "").strip(),
                "opt3": str(r[6] or "").strip(),
                "opt4": str(r[7] or "").strip(),
                "code": int(r[8] or 0) if r[8] is not None else 0,
            })
        except Exception:
            continue
    _CACHE[key] = out
    return out


def clear_cache() -> None:
    _CACHE.clear()


# ==============================================================
# Permission editor backend (User Permissions UI, 2026-09-23)
# ==============================================================
def users_with_rights(cn=None) -> list[str]:
    """menuHelp rows wale users (incl. SA) + UserMast users (no rows)."""
    out: list[str] = []
    try:
        for r in db.query(
                "SELECT DISTINCT UserName FROM menuHelp WHERE UserName IS NOT NULL "
                "ORDER BY UserName", cn=cn):
            u = str(r[0] or "").strip()
            if u and u not in out:
                out.append(u)
    except Exception:
        pass
    try:
        for r in db.query("SELECT USER_NAME FROM UserMast ORDER BY USER_NAME", cn=cn):
            u = str(r[0] or "").strip()
            if u and u not in out:
                out.append(u)
    except Exception:
        pass
    return out


def set_rights(username: str, caption: str, param: str,
               cn=None, commit: bool = True) -> int:
    """Leaf ke Param_Str update (A/E/D/P positions, '*' = denied).

    VB6 UserPermission.frm pattern. Returns rows affected (0 = row absent).
    """
    n = db.execute(
        "UPDATE menuHelp SET Param_Str = ? WHERE UserName = ? AND [Option] = ? "
        "AND CompCode = ?",
        (str(param or "").strip(), username, _norm_caption(caption), _comp()),
        cn=cn, commit=commit)
    if commit:
        clear_cache()
    return n


def set_hidden(username: str, caption: str, hidden: bool = True,
               cn=None, commit: bool = True) -> int:
    """Flag V toggle (VB6: hidden leaf menu me dikhta hi nahi).

    Un-hide Flag='E' par restore hota hai (VB6 default form-flag).
    """
    n = db.execute(
        "UPDATE menuHelp SET Flag = ? WHERE UserName = ? AND [Option] = ? "
        "AND CompCode = ?",
        ("V" if hidden else "E", username, _norm_caption(caption), _comp()),
        cn=cn, commit=commit)
    if commit:
        clear_cache()
    return n


def copy_template(from_user: str, to_user: str,
                  cn=None, commit: bool = True) -> int:
    """VB6 MeUsers.frm: SA template -> naya user (delete + insert copy)."""
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "DELETE FROM menuHelp WHERE UserName = ? AND CompCode = ?",
            (to_user, _comp()), cn=cn, commit=False)
        n_ins = db.execute(
            "INSERT INTO menuHelp (CompCode, UserName, Opt1, Opt2, Opt3, Opt4, "
            "Code, [Option], Menu_Index, Menu_Visible, Pro_Name, Tag, User_Name, "
            "Param_Str, ID, Module_Name, Flag, ShowInList, OutletCode) "
            "SELECT CompCode, ?, Opt1, Opt2, Opt3, Opt4, Code, [Option], "
            "Menu_Index, Menu_Visible, Pro_Name, Tag, User_Name, Param_Str, "
            "ID, Module_Name, Flag, ShowInList, OutletCode "
            "FROM menuHelp WHERE UserName = ? AND CompCode = ?",
            (to_user, from_user, _comp()), cn=cn, commit=False)
        if commit:
            cn.commit()
            clear_cache()
        return int(n_ins or 0)
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            cn.close()


def delete_user_rights(username: str, cn=None, commit: bool = True) -> int:
    """User ke saare menuHelp rows delete (full-access par wapas)."""
    n = db.execute(
        "DELETE FROM menuHelp WHERE UserName = ? AND CompCode = ?",
        (username, _comp()), cn=cn, commit=commit)
    if commit:
        clear_cache()
    return n


def create_user(username: str, password: str, label: str = "",
                short: str = "", template_user: str = "SA",
                cn=None, commit: bool = True) -> dict:
    """Naya user onboarding (VB6 MeUsers.frm pattern):

    1. UserMast insert (VB6-encrypted password, core/usermaster se)
    2. menuHelp template copy (SA default; delete+insert idempotent)
    Returns {username, usermast_rows, menuhelp_rows}.

    username: max 10 chars (UserMast.USER_NAME limit), auto-uppercased.
    template_user: menuHelp template source (default SA).
    """
    from HMS_py.core import usermaster
    uname = str(username or "").strip().upper()
    if not uname:
        raise ValueError("Username zaroori hai")
    if len(uname) > 10:
        raise ValueError("Username max 10 chars (UserMast.USER_NAME)")
    if usermaster.exists(uname, cn=cn):
        raise ValueError(f"User '{uname}' pehle se hai")

    # Atomic onboarding: ek shared connection — db.execute(commit=False)
    # apna connection close-rollback karta hai, isliye yahan apna cn.
    own = cn is None
    cn2 = db.connect() if own else cn
    try:
        um_rows = usermaster.insert(
            {"username": uname, "label": (label or uname).strip()[:30],
             "short": (short or uname).strip()[:10], "active": "Y"},
            plain_password=str(password or ""), cn=cn2, commit=False)
        mh_rows = 0
        if template_user and str(template_user).strip().upper() != uname:
            mh_rows = copy_template(template_user, uname, cn=cn2,
                                    commit=False)
        if commit:
            cn2.commit()
        else:
            cn2.rollback()
    except Exception:
        try:
            cn2.rollback()
        except Exception:
            pass
        raise
    finally:
        if own:
            cn2.close()
    clear_cache()
    return {"username": uname, "usermast_rows": int(um_rows or 0),
            "menuhelp_rows": int(mh_rows or 0)}


def has_row(username: str, caption: str) -> bool | None:
    """Caption user ke (effective) menuHelp rows me hai? None = full-access.

    Restricted user + absent caption => False (VB6: leaf usko dikhti nahi).
    SA / no-rows users => None (kuch bhi restricted na karo).
    """
    if full_access(username):
        return None
    return _norm_caption(caption) in by_caption(username)


def entries(username: str = "SA") -> list[dict]:
    return list(_load_user(username))


def by_caption(username: str = "SA") -> dict[str, dict]:
    """Caption (normalized) -> first menuHelp row.

    Keys hamesha _norm_caption se normalize hote hain — synthetic/legacy
    raw-caption rows bhi mismatch-proof (test_rights_parse_aedp bug fix).
    """
    out: dict[str, dict] = {}
    for r in _load_user(username):
        c = _norm_caption(r.get("caption"))
        if c and c not in out:
            out[c] = r
    return out


def flag_for(caption: str, username: str = "SA") -> str | None:
    """E/R/N/V or None if leaf not in menuHelp for this user."""
    row = by_caption(username).get(_norm_caption(caption))
    return row["flag"] if row else None


def rights(username: str, caption: str) -> str:
    """Param_Str for leaf. Missing row/leaf => 'AEDP' (full access)."""
    row = by_caption(username).get(_norm_caption(caption))
    if not row:
        return "AEDP"
    p = row.get("param") or ""
    return p if p else "AEDP"


def can(username: str, caption: str, right: str) -> bool:
    """True if right in Param_Str (A/E/D/P). Right is case-insensitive.

    VB6 pattern: SubString(Param_Str,1..4) = A/E/D/P.
    """
    if not right:
        return True
    return str(right).upper() in (rights(username, caption) or "AEDP").upper()


def can_open(username: str, caption: str) -> bool:
    """Menu leaf open permission: Flag V => never; else any of A/E/D/P.

    Report (R) with only '***P' still opens (print-only report viewer).
    """
    flag = flag_for(caption, username)
    if flag == "V":
        return False
    if flag in ("E", "N", "R", None):
        # open = user may see leaf; deep AEDP checked by forms
        return True
    return True


def module_tree(username: str = "SA") -> dict[str, list[dict]]:
    """Module_Name -> leaf rows (Opt1..Opt4 hierarchy retained)."""
    out: dict[str, list[dict]] = {}
    for r in _load_user(username):
        out.setdefault(r["module"] or "UNMAPPED", []).append(r)
    return out


def modules(username: str = "SA") -> list[str]:
    seen: list[str] = []
    for r in _load_user(username):
        m = r["module"] or "UNMAPPED"
        if m not in seen:
            seen.append(m)
    return seen


# ==============================================================
# VB6 MDIForm1.frm dynamic menu (2026-09-23):
#   Sidebar : SELECT [Option] FROM MenuHelp WHERE Flag<>'V' AND Opt1<>0
#             AND Opt2=0 AND Opt3=0 AND Opt4=0 AND UserName=? AND CompCode=?
#   Menubar : same rows ORDER BY OPT1,OPT2,OPT3,OPT4; level = Opt1>Opt2>
#             Opt3>Opt4; Flag N=node, E=form, R=report, V=hidden;
#             [Option]='-' separator; Param_Str AEDP / ***P rights.
# ==============================================================
def _opt(row: dict, name: str) -> int:
    try:
        return int(str(row.get(name) or "0").strip() or "0")
    except Exception:
        return 0


def _row_code(row: dict) -> int:
    try:
        return int(row.get("code") or 0)
    except Exception:
        return 0


def full_access(username: str = "SA") -> bool:
    """True = user ka apna menuHelp rowset nahi hai (SA / no-rows fallback).

    VB6: menu user ke APNE menuHelp rows se banta hai — caption absent
    ho to wo leaf user ko dikhti hi nahi. Sirf full-access users ke liye
    hum User_Module gap-merge / ported-extras inject karte hain; restricted
    user ko strict sirf uske rows dikhenge (rights-leak fix 2026-09-23).
    """
    key = (username or "SA").upper()
    if key == "SA":
        return True
    try:
        rows = db.query(
            "SELECT COUNT(*) FROM menuHelp WHERE UserName = ? AND CompCode = ?",
            (username, _comp()))
        return not rows or not int(rows[0][0] or 0)
    except Exception:
        return True


def _tree_rows(username: str) -> list[dict]:
    """Visible, ordered menuHelp rows (VB6 ORDER BY OPT1,OPT2,OPT3,OPT4 + Code)."""
    rows = [r for r in _load_user(username)
            if r["flag"] not in ("V", "D")
            and r["caption"] not in ("", "-")]
    rows.sort(key=lambda r: (_opt(r, "opt1"), _opt(r, "opt2"),
                             _opt(r, "opt3"), _opt(r, "opt4"),
                             _row_code(r)))
    return rows


def _mh_item(row: dict) -> dict:
    return {"name": row.get("caption_disp") or row["caption"], "srno": None,
            "children": [], "flag": row["flag"], "module": row["module"]}


def sidebar_modules(username: str = "SA") -> list[dict]:
    """menuHelp se sidebar roots (VB6 MDIForm1 L89/11145 logic).

    L1 node = Opt1<>0, Opt2=0, Opt3=0, Opt4=0, Flag='N'.
    Orphan row [E] Auto Settle Card Balance (O1=23) included for complete coverage.
    Returns [{name, opt1, code, srno}] (srno=None: User_Module parity).
    """
    out: list[dict] = []
    seen: set[int] = set()
    for r in _tree_rows(username):
        o1, o2, o3, o4 = (_opt(r, "opt1"), _opt(r, "opt2"),
                          _opt(r, "opt3"), _opt(r, "opt4"))
        # L1 nodes: Opt1<>0, Opt2=Opt3=Opt4=0, Flag='N'
        is_l1 = o1 and o2 == 0 and o3 == 0 and o4 == 0 and r["flag"] == "N"
        if is_l1:
            if o1 in seen:
                continue
            seen.add(o1)
            out.append({"name": r["caption"], "opt1": o1, "srno": None,
                        "code": _row_code(r)})
        # Specific orphan row fix: [E] Auto Settle Card Balance (O1=23)
        # Only this specific row, not all non-L1 rows
        elif o1 == 23 and r["caption"] == "Auto Settle Card Balance":
            if o1 not in seen:
                seen.add(o1)
                out.append({"name": r["caption"], "opt1": o1, "srno": None,
                            "code": _row_code(r)})
    return out


def menubar_for_menuhelp(module_name: str, username: str = "SA") -> list[dict]:
    """menuHelp Opt-tree se menubar groups (VB6 MDIForm1 nesting).

    Group = Opt2 block (title: Flag='N' row, warna Module_Name fallback).
    Items: O3 leaves + O3 nodes (children = O4 leaves).
    Shape = menu.menubar_for jaisa: [{name, items:[{name, srno, children}]}]
    """
    root = next((r for r in _tree_rows(username)
                 if r["flag"] == "N"
                 and _opt(r, "opt2") == 0 and _opt(r, "opt3") == 0
                 and _opt(r, "opt4") == 0
                 and r["caption"].lower() == str(module_name).strip().lower()),
                None)
    if root is None:
        return []
    o1 = _opt(root, "opt1")
    rows = [r for r in _tree_rows(username) if _opt(r, "opt1") == o1]

    # O2=0 non-root rows (VB6: module menubar pe DIRECT items,
    # e.g. POS 'Payment Receive' O2=0,O3=11) - root-row khud chhod kar.
    direct = [r for r in rows if _opt(r, "opt2") == 0
              and (_opt(r, "opt3") or _opt(r, "opt4"))]

    groups: list[dict] = []
    by_o2: dict[int, dict] = {}
    for r in rows:
        o2, o3, o4 = _opt(r, "opt2"), _opt(r, "opt3"), _opt(r, "opt4")
        if o2 == 0:
            continue  # root row khud (direct list me already)
        g = by_o2.get(o2)
        if g is None:
            g = {"name": r["module"] or str(module_name), "rows": []}
            by_o2[o2] = g
            groups.append(g)
        g["rows"].append(r)

    out: list[dict] = []
    if direct:
        items: list[dict] = []
        cur_d: dict | None = None
        for r in direct:
            it = _mh_item(r)
            if r["flag"] == "N":
                cur_d = it
                items.append(cur_d)
            else:
                cur_d = None
                items.append(it)
        out.append({"name": str(module_name), "items": items})
    for g in groups:
        rows_g = g["rows"]
        # N-title row (O3=0,O4=0) group-name deta hai; baaki rows items hain
        title = next((r for r in rows_g if r["flag"] == "N"
                      and _opt(r, "opt3") == 0 and _opt(r, "opt4") == 0), None)
        gname = (title.get("caption_disp") or title["caption"]) if title \
            else g["name"]
        items_g: list[dict] = []
        cur: dict | None = None
        for r in rows_g:
            o3, o4 = _opt(r, "opt3"), _opt(r, "opt4")
            # Flag '-' = VB6 separator (caption ho ya na ho — e.g.
            # 'laundry memo'/'token entry' rows sep-flag ke saath caption
            # bhi rakhti hain). VB6 inhe LINE dikhata tha, clickable item
            # kabhi nahi — skip (disabled-junk fix, reason-map V2).
            if r["flag"] in ("-", "S"):
                continue
            # Title-level N rows (O3=0,O4=0, caption==gname) SAB skip:
            # title khud + DB me duplicate copies (admin/AMIR me
            # 'Reports'/'Operations' rows 2x hain — pehla title, baaki
            # ghost items ban rahe the).
            if (r["flag"] == "N" and o3 == 0 and o4 == 0
                    and _alnum(r["caption"]) == _alnum(gname)):
                continue
            # N-row jo group-title ko repeat kare (e.g. 'M.I.S.' node
            # under 'M.I.S.' group, O3-level) = VB6 me submenu TITLE,
            # action nahi — skip.
            if (r["flag"] == "N" and o3 != 0 and o4 == 0
                    and _alnum(r["caption"]) == _alnum(gname)):
                continue
            if r is title:
                continue
            it = _mh_item(r)
            if r["flag"] == "N" and o4 == 0:
                cur = it
                items_g.append(cur)
            elif o4 != 0 and cur is not None:
                cur["children"].append(it)
            else:
                cur = None
                items_g.append(it)
        # Childless O3-level N nodes (VB6 submenu header jiske items hi
        # nahi — 'M.I.S.', 'Point of Sale', 'Operations'...): builder ke
        # baad strip — VB6 me empty submenu render hi nahi hota tha.
        items_g = [x for x in items_g
                   if x["children"] or x["flag"] != "N"]
        if items_g:
            out.append({"name": gname, "items": items_g})
    return out


def orphan_rows(username: str = "SA") -> list[dict]:
    """menuHelp rows jinka Opt1 kisi L1 node se map nahi (DB data-gap).

    VB6 inhe silently drop karta hai (menubar walk parent N-node se hota
    hai); yahan report/audit ke liye exposed, menus me inject NAHI karte.
    """
    l1 = {m["opt1"] for m in sidebar_modules(username)}
    return [r for r in _tree_rows(username)
            if _opt(r, "opt1") not in l1 and _opt(r, "opt1") != 0]


def _alnum(s: str) -> str:
    return "".join(ch for ch in str(s or "").lower() if ch.isalnum())


def menubar_for(module_name: str, username: str = "SA") -> list[dict]:
    """Dynamic source: menuHelp tree, User_Module fallback + gap-merge.

    - menuHelp me module ho -> wahi source; User_Module ke extra captions
      (menuHelp me na hon) end me merge (koi ported leaf na chute).
    - menuHelp me module na ho (EPABX/Messaging/Members...) -> purana
      User_Module path (zero regression).
    """
    from HMS_py.core import menu as _um
    mh_groups = menubar_for_menuhelp(module_name, username)
    if not mh_groups:
        # Restricted user ke rows me module hi nahi -> VB6 jaisa hidden
        if not full_access(username):
            return []
        return _um.menubar_for(module_name, username)
    # Gap-merge (User_Module extras) sirf full-access users ke liye —
    # restricted user ko menuHelp se extra captions leak na hon.
    if not full_access(username):
        # Restricted path par bhi junk-sweep zaroori (consistency fix,
        # 2026-09-23): warna user rows ke quirky captions (LAUNDRY group ke
        # 'Laundry Memo'/'Memo Reprint' — template me sep/junk) disabled
        # items ban kar dikhte the jabki SA view me strip ho chuke thehte.
        return _sweep_junk(mh_groups)

    def _caps(groups: list[dict]) -> set[str]:
        out: set[str] = set()
        for g in groups:
            for it in g.get("items") or []:
                out.add(_alnum(it.get("name")))
                for ch in it.get("children") or []:
                    out.add(_alnum(ch.get("name")))
        return out

    have = _caps(mh_groups)

    def _open(leaf: dict) -> bool:
        # V-flag leaves fallback se wapas na aayen (VB6 hidden semantics)
        return can_open(username, leaf.get("name"))

    # Sidebar module-header names — User_Module me ye leaf rows ke roop me
    # galti se is modules ki ranges me hain (code='Pos'/'Mem'/... , flag=0).
    # VB6 me ye kabhi clickable items nahi the (submenu headers), isliye
    # gap-merge se aane par strip karte hain (disabled-junk, reason-map V2).
    _SIDEBAR_HEADERS = {
        "finance", "main setup", "reservation", "front office",
        "house keeping", "inventory", "point of sale", "pointofsale",
        "banquet", "night audit", "hrpayroll", "members mgmt",
        "membersmgmt", "extras", "epabx", "messaging", "utility",
        "dashboard",
    }

    def _fresh(items: list[dict]) -> list[dict]:
        out = []
        for it in items:
            if not _open(it):
                continue
            ch = [c for c in (it.get("children") or []) if _open(c)]
            nm = _alnum(it.get("name"))
            if nm in have or nm in _SIDEBAR_HEADERS:
                continue
            nit = dict(it)
            nit["children"] = ch
            out.append(nit)
            have.add(nm)
        return out

    um_groups = _um.menubar_for(module_name, username)
    extra: list[dict] = []
    for g in um_groups:
        new_items = _fresh(g.get("items") or [])
        if not new_items:
            continue
        # same-name mh group me merge (duplicate groups na banein)
        target = next((x for x in mh_groups
                       if _alnum(x["name"]) == _alnum(g["name"])), None)
        if target is not None:
            target["items"] = target.get("items") or []
            target["items"].extend(new_items)
        else:
            extra.append({"name": g["name"], "items": new_items})
    out = mh_groups + extra
    return _sweep_junk(out)


def _sweep_junk(groups: list[dict]) -> list[dict]:
    """Post-merge junk sweep (SA + restricted dono paths se used):
    flag '-' separators + childless N-titles + VB6 module/section-header
    junk — User_Module fallback se flags ke bina bhi aa sakte hain. VB6
    me ye kabhi clickable items nahi the (menuHelp khud inme se kai ko
    Flag='-' mark karta hai; baaki module-headers hain jinke code
    'Pos'/'Mem'/... sidebar headers hain).
    """
    _SIDEBAR_HEADERS = {
        "finance", "main setup", "reservation", "front office",
        "house keeping", "inventory", "point of sale", "pointofsale",
        "banquet", "night audit", "hrpayroll", "members mgmt",
        "membersmgmt", "extras", "epabx", "messaging", "utility",
        "dashboard",
    }
    _JUNK = _SIDEBAR_HEADERS | {
        "mis", "operations", "operation", "posoperations",
        "setup", "changesdepartment", "taxreport",
        "laundrymemo", "memoreprint", "tokenentry",
        "restaurantchange",
    }
    for g in groups:
        g["items"] = [
            {**it, "children": [c for c in (it.get("children") or [])
                                if c.get("flag") not in ("-", "S")
                                and _alnum(c.get("name")) not in _JUNK]}
            for it in (g.get("items") or [])
            if it.get("flag") not in ("-", "S")
            and (not (_alnum(it.get("name")) in _JUNK)
                 or it.get("children"))
        ]
        g["items"] = [it for it in g["items"]
                      if it["children"] or it.get("flag") != "N"]
    return [g for g in groups if g.get("items")]


def sidebar_sources(username: str = "SA") -> list[dict]:
    """Sidebar = menuHelp L1 nodes + (ini-9 me missing) User_Module roots.

    ini key 9 order pehle (jo menuHelp me mile), phir baaki menuHelp nodes,
    phir legacy-only roots (EPABX/Messaging/Members Mgmt jo DB me abhi
    Opt1 bucket me nahi bane).
    """
    from HMS_py.core import menu as _um
    mh = sidebar_modules(username)
    if not full_access(username):
        # Restricted user: sirf menuHelp modules (legacy roots leak na ho)
        return mh
    mh_names = {_alnum(m["name"]) for m in mh}
    legacy = [r for r in _um.sidebar_modules()
              if _alnum(r["name"]) not in mh_names
              and _alnum(r["name"]) not in
              {_alnum(x) for x in ("-", "Windows", "Exit", "MDI",
                                   "PlanPopup", "Sale Bill Modification")}]
    return mh + legacy
