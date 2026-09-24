"""System Configuration (VB6: PrinterSetup, RoundOffSetting, DateLock, Site, etc).

Tables:
- RoundOffSetting: Round-off rules (9 cols)
- DATELOCK: Date lock settings (9 cols) - note: uppercase in DB
- Site: Site master (10 cols)
- menuHelp: Menu permissions (19 cols)
- menuHelp1: Menu permissions detail (12 cols)
- UserPermission: User permissions (18 cols)
- SundryTypeFix: Fixed sundry types (17 cols)
- PrinterSetup: NOT FOUND in DB

Schema: verified from live KailashData2526 DB.
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# RoundOffSetting - Round-off Rules
# PK: RoundOFFType + ModuleName + Site_Code
# ============================================================
def _map_roundoff(r) -> dict:
    try:
        return {
            "code": r.Code or "", "department": (r.Department or "").strip(),
            "roundoff_type": r.RoundOFFType or "",
            "module_name": (r.ModuleName or "").strip(),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        c, d, rt, un, _, site, uae, mn, lgs = r
        return {
            "code": c or "", "department": (d or "").strip(),
            "roundoff_type": rt or "",
            "module_name": (mn or "").strip(),
            "u_name": un or "", "u_ae": uae or "",
        }


def roundoff_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    rows = db.query(
        f"SELECT TOP {int(limit)} Code, Department, RoundOFFType, U_Name, "
        "U_EntDt, Site_Code, U_AE, ModuleName, LogSite_Code "
        "FROM RoundOffSetting ORDER BY RoundOFFType, ModuleName", cn=cn)
    return [_map_roundoff(r) for r in rows]


def roundoff_get(roundoff_type: str, module_name: str,
                 cn=None) -> dict | None:
    rows = db.query(
        "SELECT Code, Department, RoundOFFType, U_Name, U_EntDt, "
        "Site_Code, U_AE, ModuleName, LogSite_Code "
        "FROM RoundOffSetting WHERE RoundOFFType = ? AND ModuleName = ? "
        "AND Site_Code = ?",
        (roundoff_type, module_name, SITE_CODE), cn=cn)
    return _map_roundoff(rows[0]) if rows else None


def roundoff_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("roundoff_type", "").strip():
        raise ValueError("RoundOFFType zaroori hai")
    if not rec.get("module_name", "").strip():
        raise ValueError("ModuleName zaroori hai")
    return db.execute(
        "INSERT INTO RoundOffSetting (Code, Department, RoundOFFType, "
        "U_Name, U_EntDt, Site_Code, U_AE, ModuleName, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), ?, 'A', ?, ?)",
        (rec.get("code", ""), rec.get("department", ""),
         rec["roundoff_type"], USER, SITE_CODE,
         rec["module_name"], SITE_CODE),
        cn=cn, commit=commit)


def roundoff_update(roundoff_type: str, module_name: str, rec: dict,
                    cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE RoundOffSetting SET Code = ?, Department = ?, "
        "U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
        "WHERE RoundOFFType = ? AND ModuleName = ? AND Site_Code = ?",
        (rec.get("code", ""), rec.get("department", ""),
         USER, roundoff_type, module_name, SITE_CODE),
        cn=cn, commit=commit)


def roundoff_delete(roundoff_type: str, module_name: str,
                    cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM RoundOffSetting WHERE RoundOFFType = ? "
        "AND ModuleName = ? AND Site_Code = ?",
        (roundoff_type, module_name, SITE_CODE), cn=cn, commit=commit)


class _RoundOffSettingAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return roundoff_list(cn, limit)
    @staticmethod
    def get(rt, mn, cn=None): return roundoff_get(rt, mn, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return roundoff_insert(rec, cn, commit)
    @staticmethod
    def update(rt, mn, rec, cn=None, commit=True): return roundoff_update(rt, mn, rec, cn, commit)
    @staticmethod
    def delete(rt, mn, cn=None, commit=True): return roundoff_delete(rt, mn, cn, commit)

RoundOffSettingAPI = _RoundOffSettingAPI()


# ============================================================
# DATELOCK - Date Lock Settings
# PK: CODE + srno
# ============================================================
def _map_datelock(r) -> dict:
    try:
        return {
            "code": r.CODE or "", "name": (r.NAME or "").strip(),
            "level1": r.LEVEL1 or "", "level2": r.LEVEL2 or "",
            "id": r.id or "", "srno": r.srno or 0,
            "flag": r.flag, "sdate": r.SDate, "edate": r.EDate,
        }
    except AttributeError:
        c, n, l1, l2, i, sr, fl, sd, ed = r
        return {
            "code": c or "", "name": (n or "").strip(),
            "level1": l1 or "", "level2": l2 or "",
            "id": i or "", "srno": sr or 0,
            "flag": fl, "sdate": sd, "edate": ed,
        }


def datelock_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    rows = db.query(
        f"SELECT TOP {int(limit)} CODE, NAME, LEVEL1, LEVEL2, id, srno, "
        "flag, SDate, EDate FROM DATELOCK ORDER BY CODE, srno", cn=cn)
    return [_map_datelock(r) for r in rows]


def datelock_get(code: str, srno: int, cn=None) -> dict | None:
    rows = db.query(
        "SELECT CODE, NAME, LEVEL1, LEVEL2, id, srno, flag, SDate, EDate "
        "FROM DATELOCK WHERE CODE = ? AND srno = ?",
        (code, srno), cn=cn)
    return _map_datelock(rows[0]) if rows else None


def datelock_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("code", "").strip():
        raise ValueError("CODE zaroori hai")
    return db.execute(
        "INSERT INTO DATELOCK (CODE, NAME, LEVEL1, LEVEL2, id, srno, "
        "flag, SDate, EDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["code"], rec.get("name", ""), rec.get("level1", ""),
         rec.get("level2", ""), rec.get("id", ""),
         rec.get("srno", 0), rec.get("flag", 0),
         rec.get("sdate"), rec.get("edate")),
        cn=cn, commit=commit)


def datelock_update(code: str, srno: int, rec: dict,
                    cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE DATELOCK SET NAME = ?, LEVEL1 = ?, LEVEL2 = ?, id = ?, "
        "flag = ?, SDate = ?, EDate = ? WHERE CODE = ? AND srno = ?",
        (rec.get("name", ""), rec.get("level1", ""),
         rec.get("level2", ""), rec.get("id", ""),
         rec.get("flag", 0), rec.get("sdate"), rec.get("edate"),
         code, srno),
        cn=cn, commit=commit)


def datelock_delete(code: str, srno: int, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM DATELOCK WHERE CODE = ? AND srno = ?",
        (code, srno), cn=cn, commit=commit)


class _DateLockAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return datelock_list(cn, limit)
    @staticmethod
    def get(code, srno, cn=None): return datelock_get(code, srno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return datelock_insert(rec, cn, commit)
    @staticmethod
    def update(code, srno, rec, cn=None, commit=True): return datelock_update(code, srno, rec, cn, commit)
    @staticmethod
    def delete(code, srno, cn=None, commit=True): return datelock_delete(code, srno, cn, commit)

DateLockAPI = _DateLockAPI()


# ============================================================
# Site - Site Master
# PK: Site_Code
# ============================================================
def _map_site(r) -> dict:
    try:
        return {
            "comp_code": r.CompCode or "", "site_code": r.Site_Code or "",
            "site_desc": (r.Site_Desc or "").strip(),
            "site_type": r.SiteType or "",
            "short_name": (r.Short_Name or "").strip(),
            "send_date": r.SendDate, "rec_date": r.RecDate,
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        cc, sc, sd, un, _, uae, st, sn, snd, rd = r
        return {
            "comp_code": cc or "", "site_code": sc or "",
            "site_desc": (sd or "").strip(),
            "site_type": st or "",
            "short_name": (sn or "").strip(),
            "send_date": snd, "rec_date": rd,
            "u_name": un or "", "u_ae": uae or "",
        }


def site_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    rows = db.query(
        f"SELECT TOP {int(limit)} CompCode, Site_Code, Site_Desc, U_Name, "
        "U_EntDt, U_AE, SiteType, Short_Name, SendDate, RecDate "
        "FROM Site ORDER BY Site_Code", cn=cn)
    return [_map_site(r) for r in rows]


def site_get(site_code: str, cn=None) -> dict | None:
    rows = db.query(
        "SELECT CompCode, Site_Code, Site_Desc, U_Name, U_EntDt, U_AE, "
        "SiteType, Short_Name, SendDate, RecDate "
        "FROM Site WHERE Site_Code = ?", (site_code,), cn=cn)
    return _map_site(rows[0]) if rows else None


def site_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("site_code", "").strip():
        raise ValueError("Site_Code zaroori hai")
    if not rec.get("site_desc", "").strip():
        raise ValueError("Site_Desc zaroori hai")
    return db.execute(
        "INSERT INTO Site (CompCode, Site_Code, Site_Desc, U_Name, "
        "U_EntDt, U_AE, SiteType, Short_Name, SendDate, RecDate) "
        "VALUES (?, ?, ?, ?, getdate(), 'A', ?, ?, ?, ?)",
        (rec.get("comp_code", SITE_CODE), rec["site_code"],
         rec["site_desc"], USER,
         rec.get("site_type", ""), rec.get("short_name", ""),
         rec.get("send_date"), rec.get("rec_date")),
        cn=cn, commit=commit)


def site_update(site_code: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE Site SET Site_Desc = ?, SiteType = ?, Short_Name = ?, "
        "SendDate = ?, RecDate = ?, U_Name = ?, U_EntDt = getdate(), "
        "U_AE = 'E' WHERE Site_Code = ?",
        (rec.get("site_desc", ""), rec.get("site_type", ""),
         rec.get("short_name", ""), rec.get("send_date"),
         rec.get("rec_date"), USER, site_code),
        cn=cn, commit=commit)


def site_delete(site_code: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM Site WHERE Site_Code = ?", (site_code,),
        cn=cn, commit=commit)


class _SiteAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return site_list(cn, limit)
    @staticmethod
    def get(site_code, cn=None): return site_get(site_code, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return site_insert(rec, cn, commit)
    @staticmethod
    def update(site_code, rec, cn=None, commit=True): return site_update(site_code, rec, cn, commit)
    @staticmethod
    def delete(site_code, cn=None, commit=True): return site_delete(site_code, cn, commit)

SiteAPI = _SiteAPI()


# ============================================================
# menuHelp - Menu Permissions
# PK: CompCode + UserName + Opt1 + Opt2 + Opt3 + Opt4 + Code
# ============================================================
def _map_menuhelp(r) -> dict:
    try:
        return {
            "comp_code": r.CompCode or "", "username": r.UserName or "",
            "opt1": r.Opt1 or 0, "opt2": r.Opt2 or 0,
            "opt3": r.Opt3 or 0, "opt4": r.Opt4 or 0,
            "code": r.Code or 0,
            "option": (r.Option or "").strip(),
            "menu_index": r.Menu_Index or 0,
            "menu_visible": r.Menu_Visible or "Y",
            "pro_name": r.Pro_Name or "",
            "tag": r.Tag or "",
            "user_name": r.User_Name or "",
            "param_str": r.Param_Str or "",
            "id": r.ID or "",
            "module_name": r.Module_Name or "",
            "flag": r.Flag or "",
            "show_in_list": r.ShowInList or "",
            "outlet_code": r.OutletCode or "",
        }
    except AttributeError:
        cc, un, o1, o2, o3, o4, c, opt, mi, mv, pn, tg, \
            usr, ps, i, mn, fl, sil, ol = r
        return {
            "comp_code": cc or "", "username": un or "",
            "opt1": o1 or 0, "opt2": o2 or 0,
            "opt3": o3 or 0, "opt4": o4 or 0,
            "code": c or 0,
            "option": (opt or "").strip(),
            "menu_index": mi or 0,
            "menu_visible": mv or "Y",
            "pro_name": pn or "",
            "tag": tg or "",
            "user_name": usr or "",
            "param_str": ps or "",
            "id": i or "",
            "module_name": mn or "",
            "flag": fl or "",
            "show_in_list": sil or "",
            "outlet_code": ol or "",
        }


def menuhelp_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    cols = ("CompCode, UserName, Opt1, Opt2, Opt3, Opt4, Code, Option, "
            "Menu_Index, Menu_Visible, Pro_Name, Tag, User_Name, "
            "Param_Str, ID, Module_Name, Flag, ShowInList, OutletCode")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM menuHelp ORDER BY Code", cn=cn)
    return [_map_menuhelp(r) for r in rows]


def menuhelp_get(comp_code: str, username: str, opt1: int, opt2: int,
                 opt3: int, opt4: int, code: int, cn=None) -> dict | None:
    cols = ("CompCode, UserName, Opt1, Opt2, Opt3, Opt4, Code, Option, "
            "Menu_Index, Menu_Visible, Pro_Name, Tag, User_Name, "
            "Param_Str, ID, Module_Name, Flag, ShowInList, OutletCode")
    rows = db.query(
        f"SELECT {cols} FROM menuHelp WHERE CompCode = ? AND UserName = ? "
        "AND Opt1 = ? AND Opt2 = ? AND Opt3 = ? AND Opt4 = ? AND Code = ?",
        (comp_code, username, opt1, opt2, opt3, opt4, code), cn=cn)
    return _map_menuhelp(rows[0]) if rows else None


def menuhelp_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO menuHelp (CompCode, UserName, Opt1, Opt2, Opt3, Opt4, "
        "Code, Option, Menu_Index, Menu_Visible, Pro_Name, Tag, User_Name, "
        "Param_Str, ID, Module_Name, Flag, ShowInList, OutletCode) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.get("comp_code", SITE_CODE), rec.get("username", ""),
         rec.get("opt1", 0), rec.get("opt2", 0),
         rec.get("opt3", 0), rec.get("opt4", 0),
         rec.get("code", 0), rec.get("option", ""),
         rec.get("menu_index", 0), rec.get("menu_visible", "Y"),
         rec.get("pro_name", ""), rec.get("tag", ""),
         rec.get("user_name", ""), rec.get("param_str", ""),
         rec.get("id", ""), rec.get("module_name", ""),
         rec.get("flag", ""), rec.get("show_in_list", ""),
         rec.get("outlet_code", "")),
        cn=cn, commit=commit)


def menuhelp_delete(comp_code: str, username: str, opt1: int, opt2: int,
                    opt3: int, opt4: int, code: int,
                    cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM menuHelp WHERE CompCode = ? AND UserName = ? "
        "AND Opt1 = ? AND Opt2 = ? AND Opt3 = ? AND Opt4 = ? AND Code = ?",
        (comp_code, username, opt1, opt2, opt3, opt4, code),
        cn=cn, commit=commit)


class _MenuHelpAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return menuhelp_list(cn, limit)
    @staticmethod
    def get(cc, un, o1, o2, o3, o4, c, cn=None): return menuhelp_get(cc, un, o1, o2, o3, o4, c, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return menuhelp_insert(rec, cn, commit)
    @staticmethod
    def delete(cc, un, o1, o2, o3, o4, c, cn=None, commit=True): return menuhelp_delete(cc, un, o1, o2, o3, o4, c, cn, commit)

MenuHelpAPI = _MenuHelpAPI()


# ============================================================
# menuHelp1 - Menu Permissions Detail
# PK: CompCode + UserName + Opt1 + Opt2 + Opt3 + Opt4 + Code
# ============================================================
def _map_menuhelp1(r) -> dict:
    try:
        return {
            "comp_code": r.CompCode or "", "username": r.UserName or "",
            "opt1": r.Opt1 or 0, "opt2": r.Opt2 or 0,
            "opt3": r.Opt3 or 0, "opt4": r.Opt4 or 0,
            "code": r.Code or 0,
            "menu_name": (r.MenuName or "").strip(),
            "menu_index": r.MenuIndex or 0,
            "menu_caption": (r.MenuCaption or "").strip(),
            "param_str": r.Param_Str or "",
            "flag": r.Flag or "",
        }
    except AttributeError:
        cc, un, o1, o2, o3, o4, c, mn, mi, mc, ps, fl = r
        return {
            "comp_code": cc or "", "username": un or "",
            "opt1": o1 or 0, "opt2": o2 or 0,
            "opt3": o3 or 0, "opt4": o4 or 0,
            "code": c or 0,
            "menu_name": (mn or "").strip(),
            "menu_index": mi or 0,
            "menu_caption": (mc or "").strip(),
            "param_str": ps or "",
            "flag": fl or "",
        }


def menuhelp1_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    cols = ("CompCode, UserName, Opt1, Opt2, Opt3, Opt4, Code, "
            "MenuName, MenuIndex, MenuCaption, Param_Str, Flag")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM menuHelp1 ORDER BY Code", cn=cn)
    return [_map_menuhelp1(r) for r in rows]


def menuhelp1_get(comp_code: str, username: str, opt1: int, opt2: int,
                  opt3: int, opt4: int, code: int, cn=None) -> dict | None:
    cols = ("CompCode, UserName, Opt1, Opt2, Opt3, Opt4, Code, "
            "MenuName, MenuIndex, MenuCaption, Param_Str, Flag")
    rows = db.query(
        f"SELECT {cols} FROM menuHelp1 WHERE CompCode = ? AND UserName = ? "
        "AND Opt1 = ? AND Opt2 = ? AND Opt3 = ? AND Opt4 = ? AND Code = ?",
        (comp_code, username, opt1, opt2, opt3, opt4, code), cn=cn)
    return _map_menuhelp1(rows[0]) if rows else None


def menuhelp1_insert(rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "INSERT INTO menuHelp1 (CompCode, UserName, Opt1, Opt2, Opt3, Opt4, "
        "Code, MenuName, MenuIndex, MenuCaption, Param_Str, Flag) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.get("comp_code", SITE_CODE), rec.get("username", ""),
         rec.get("opt1", 0), rec.get("opt2", 0),
         rec.get("opt3", 0), rec.get("opt4", 0),
         rec.get("code", 0), rec.get("menu_name", ""),
         rec.get("menu_index", 0), rec.get("menu_caption", ""),
         rec.get("param_str", ""), rec.get("flag", "")),
        cn=cn, commit=commit)


def menuhelp1_delete(comp_code: str, username: str, opt1: int, opt2: int,
                     opt3: int, opt4: int, code: int,
                     cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM menuHelp1 WHERE CompCode = ? AND UserName = ? "
        "AND Opt1 = ? AND Opt2 = ? AND Opt3 = ? AND Opt4 = ? AND Code = ?",
        (comp_code, username, opt1, opt2, opt3, opt4, code),
        cn=cn, commit=commit)


class _MenuHelp1API:
    @staticmethod
    def list_all(cn=None, limit=500): return menuhelp1_list(cn, limit)
    @staticmethod
    def get(cc, un, o1, o2, o3, o4, c, cn=None): return menuhelp1_get(cc, un, o1, o2, o3, o4, c, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return menuhelp1_insert(rec, cn, commit)
    @staticmethod
    def delete(cc, un, o1, o2, o3, o4, c, cn=None, commit=True): return menuhelp1_delete(cc, un, o1, o2, o3, o4, c, cn, commit)

MenuHelp1API = _MenuHelp1API()


# ============================================================
# UserPermission - User Permissions
# PK: CompCode + UserName + LogSite_Code
# ============================================================
def _map_userperm(r) -> dict:
    try:
        return {
            "comp_code": r.CompCode or "", "username": r.UserName or "",
            "logsite": r.LogSite_Code or "",
            "pos_discount_upto": float(r.POSDiscountAllowUpto or 0),
            "cancel_guest_bill": r.CancelGuestBill or "",
            "change_room_dtl": r.ChangeRoomDtl or "",
            "delete_guest_charges": r.DeleteGuestCharges or "",
            "pos_settlement": r.POSSettlementYN or "",
            "change_guest_charges": r.ChangeGuestCharges or "",
            "backcolor": r.backcolor or 0,
            "change_guest_profile": r.ChangeGuestProfile or "",
            "facility_billing": r.FacilityBilling or "",
            "edit_item_in_kot": r.EditItemInKOT or "",
            "fom_discount_upto": float(r.FOMDiscountAllowUpto or 0),
            "cancel_reservation": r.CancelReservation or "",
            "free_item_allow": r.FreeItemAllow or "",
            "refund_cash_card": r.RefundCashCardAmt or "",
        }
    except AttributeError:
        cc, un, ls, pdu, cgb, crd, dgc, site, ps, cgc, bc, cgp, \
            fb, eik, fdu, ci, fia, rcca = r
        return {
            "comp_code": cc or "", "username": un or "",
            "logsite": ls or "",
            "pos_discount_upto": float(pdu or 0),
            "cancel_guest_bill": cgb or "",
            "change_room_dtl": crd or "",
            "delete_guest_charges": dgc or "",
            "pos_settlement": ps or "",
            "change_guest_charges": cgc or "",
            "backcolor": bc or 0,
            "change_guest_profile": cgp or "",
            "facility_billing": fb or "",
            "edit_item_in_kot": eik or "",
            "fom_discount_upto": float(fdu or 0),
            "cancel_reservation": ci or "",
            "free_item_allow": fia or "",
            "refund_cash_card": rcca or "",
        }


def userperm_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    cols = ("CompCode, UserName, LogSite_Code, POSDiscountAllowUpto, "
            "CancelGuestBill, ChangeRoomDtl, DeleteGuestCharges, "
            "Site_Code, POSSettlementYN, ChangeGuestCharges, backcolor, "
            "ChangeGuestProfile, FacilityBilling, EditItemInKOT, "
            "FOMDiscountAllowUpto, CancelReservation, FreeItemAllow, "
            "RefundCashCardAmt")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM UserPermission ORDER BY UserName",
        cn=cn)
    return [_map_userperm(r) for r in rows]


def userperm_get(username: str, cn=None) -> dict | None:
    cols = ("CompCode, UserName, LogSite_Code, POSDiscountAllowUpto, "
            "CancelGuestBill, ChangeRoomDtl, DeleteGuestCharges, "
            "Site_Code, POSSettlementYN, ChangeGuestCharges, backcolor, "
            "ChangeGuestProfile, FacilityBilling, EditItemInKOT, "
            "FOMDiscountAllowUpto, CancelReservation, FreeItemAllow, "
            "RefundCashCardAmt")
    rows = db.query(
        f"SELECT {cols} FROM UserPermission WHERE UserName = ? "
        "AND LogSite_Code = ?",
        (username, SITE_CODE), cn=cn)
    return _map_userperm(rows[0]) if rows else None


def userperm_insert(rec: dict, cn=None, commit: bool = True) -> int:
    if not rec.get("username", "").strip():
        raise ValueError("UserName zaroori hai")
    return db.execute(
        "INSERT INTO UserPermission (CompCode, UserName, LogSite_Code, "
        "POSDiscountAllowUpto, CancelGuestBill, ChangeRoomDtl, "
        "DeleteGuestCharges, Site_Code, POSSettlementYN, "
        "ChangeGuestCharges, backcolor, ChangeGuestProfile, "
        "FacilityBilling, EditItemInKOT, FOMDiscountAllowUpto, "
        "CancelReservation, FreeItemAllow, RefundCashCardAmt) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.get("comp_code", SITE_CODE), rec["username"], SITE_CODE,
         float(rec.get("pos_discount_upto") or 0),
         rec.get("cancel_guest_bill", ""),
         rec.get("change_room_dtl", ""),
         rec.get("delete_guest_charges", ""),
         SITE_CODE,
         rec.get("pos_settlement", ""),
         rec.get("change_guest_charges", ""),
         rec.get("backcolor", 0),
         rec.get("change_guest_profile", ""),
         rec.get("facility_billing", ""),
         rec.get("edit_item_in_kot", ""),
         float(rec.get("fom_discount_upto") or 0),
         rec.get("cancel_reservation", ""),
         rec.get("free_item_allow", ""),
         rec.get("refund_cash_card", "")),
        cn=cn, commit=commit)


def userperm_update(username: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE UserPermission SET POSDiscountAllowUpto = ?, "
        "CancelGuestBill = ?, ChangeRoomDtl = ?, DeleteGuestCharges = ?, "
        "POSSettlementYN = ?, ChangeGuestCharges = ?, backcolor = ?, "
        "ChangeGuestProfile = ?, FacilityBilling = ?, EditItemInKOT = ?, "
        "FOMDiscountAllowUpto = ?, CancelReservation = ?, "
        "FreeItemAllow = ?, RefundCashCardAmt = ? "
        "WHERE UserName = ? AND LogSite_Code = ?",
        (float(rec.get("pos_discount_upto") or 0),
         rec.get("cancel_guest_bill", ""),
         rec.get("change_room_dtl", ""),
         rec.get("delete_guest_charges", ""),
         rec.get("pos_settlement", ""),
         rec.get("change_guest_charges", ""),
         rec.get("backcolor", 0),
         rec.get("change_guest_profile", ""),
         rec.get("facility_billing", ""),
         rec.get("edit_item_in_kot", ""),
         float(rec.get("fom_discount_upto") or 0),
         rec.get("cancel_reservation", ""),
         rec.get("free_item_allow", ""),
         rec.get("refund_cash_card", ""),
         username, SITE_CODE),
        cn=cn, commit=commit)


def userperm_delete(username: str, cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM UserPermission WHERE UserName = ? AND LogSite_Code = ?",
        (username, SITE_CODE), cn=cn, commit=commit)


class _UserPermissionAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return userperm_list(cn, limit)
    @staticmethod
    def get(username, cn=None): return userperm_get(username, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return userperm_insert(rec, cn, commit)
    @staticmethod
    def update(username, rec, cn=None, commit=True): return userperm_update(username, rec, cn, commit)
    @staticmethod
    def delete(username, cn=None, commit=True): return userperm_delete(username, cn, commit)

UserPermissionAPI = _UserPermissionAPI()


# ============================================================
# SundryTypeFix - Fixed Sundry Types
# PK: SundryCode + SNo + Site_Code
# ============================================================
def _map_sundryfix(r) -> dict:
    try:
        return {
            "sundry_code": r.SundryCode or "", "sno": r.SNo or 0,
            "disp_name": (r.DispName or "").strip(),
            "calc_formula": r.CalcFormula or "",
            "per_or_amt": r.PerOrAmt or "",
            "round_off": r.RoundOff or "",
            "svalue": float(r.SValue or 0),
            "limit": float(r.Limit or 0),
            "post_ac": r.PostAc or "",
            "nature": (r.Nature or "").strip(),
            "calc_sign": r.CalcSign or "",
            "sys_yn": r.SysYN or "",
            "grp": r.Grp or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        sc, sn, dn, cf, pa, ro, sv, lm, pa2, na, cs, sy, gr, \
            site, un, uae, lgs = r
        return {
            "sundry_code": sc or "", "sno": sn or 0,
            "disp_name": (dn or "").strip(),
            "calc_formula": cf or "",
            "per_or_amt": pa or "",
            "round_off": ro or "",
            "svalue": float(sv or 0),
            "limit": float(lm or 0),
            "post_ac": pa2 or "",
            "nature": (na or "").strip(),
            "calc_sign": cs or "",
            "sys_yn": sy or "",
            "grp": gr or "",
            "u_name": un or "", "u_ae": uae or "",
        }


def _validate_sundryfix(rec: dict):
    if not rec.get("sundry_code", "").strip():
        raise ValueError("SundryCode zaroori hai")
    if not rec.get("disp_name", "").strip():
        raise ValueError("DispName zaroori hai")


def sundryfix_list(cn=None, limit: int = 500) -> list[dict]:
    # Validate and sanitize limit to prevent SQL injection
    limit = int(limit) if limit else 500
    if limit < 1:
        limit = 1
    elif limit > 10000:
        limit = 10000
    cols = ("SundryCode, SNo, DispName, CalcFormula, PerOrAmt, RoundOff, "
            "SValue, Limit, PostAc, Nature, CalcSign, SysYN, Grp, "
            "Site_Code, U_EntDt, U_AE, LogSite_Code")
    rows = db.query(
        f"SELECT TOP {int(limit)} {cols} FROM SundryTypeFix ORDER BY SundryCode, SNo",
        cn=cn)
    return [_map_sundryfix(r) for r in rows]


def sundryfix_get(sundry_code: str, sno: int, cn=None) -> dict | None:
    cols = ("SundryCode, SNo, DispName, CalcFormula, PerOrAmt, RoundOff, "
            "SValue, Limit, PostAc, Nature, CalcSign, SysYN, Grp, "
            "Site_Code, U_EntDt, U_AE, LogSite_Code")
    rows = db.query(
        f"SELECT {cols} FROM SundryTypeFix WHERE SundryCode = ? AND SNo = ? "
        "AND Site_Code = ?",
        (sundry_code, sno, SITE_CODE), cn=cn)
    return _map_sundryfix(rows[0]) if rows else None


def sundryfix_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_sundryfix(rec)
    return db.execute(
        "INSERT INTO SundryTypeFix (SundryCode, SNo, DispName, CalcFormula, "
        "PerOrAmt, RoundOff, SValue, Limit, PostAc, Nature, CalcSign, "
        "SysYN, Grp, Site_Code, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (rec["sundry_code"], rec.get("sno", 0), rec["disp_name"],
         rec.get("calc_formula", ""), rec.get("per_or_amt", ""),
         rec.get("round_off", ""), float(rec.get("svalue") or 0),
         float(rec.get("limit") or 0), rec.get("post_ac", ""),
         rec.get("nature", ""), rec.get("calc_sign", ""),
         rec.get("sys_yn", ""), rec.get("grp", ""),
         SITE_CODE, SITE_CODE),
        cn=cn, commit=commit)


def sundryfix_update(sundry_code: str, sno: int, rec: dict,
                     cn=None, commit: bool = True) -> int:
    _validate_sundryfix(rec)
    return db.execute(
        "UPDATE SundryTypeFix SET DispName = ?, CalcFormula = ?, "
        "PerOrAmt = ?, RoundOff = ?, SValue = ?, Limit = ?, "
        "PostAc = ?, Nature = ?, CalcSign = ?, SysYN = ?, Grp = ?, "
        "U_EntDt = getdate(), U_AE = 'E' "
        "WHERE SundryCode = ? AND SNo = ? AND Site_Code = ?",
        (rec["disp_name"], rec.get("calc_formula", ""),
         rec.get("per_or_amt", ""), rec.get("round_off", ""),
         float(rec.get("svalue") or 0), float(rec.get("limit") or 0),
         rec.get("post_ac", ""), rec.get("nature", ""),
         rec.get("calc_sign", ""), rec.get("sys_yn", ""),
         rec.get("grp", ""),
         sundry_code, sno, SITE_CODE),
        cn=cn, commit=commit)


def sundryfix_delete(sundry_code: str, sno: int,
                     cn=None, commit: bool = True) -> int:
    return db.execute(
        "DELETE FROM SundryTypeFix WHERE SundryCode = ? AND SNo = ? "
        "AND Site_Code = ?",
        (sundry_code, sno, SITE_CODE), cn=cn, commit=commit)


class _SundryTypeFixAPI:
    @staticmethod
    def list_all(cn=None, limit=500): return sundryfix_list(cn, limit)
    @staticmethod
    def get(sundry_code, sno, cn=None): return sundryfix_get(sundry_code, sno, cn)
    @staticmethod
    def insert(rec, cn=None, commit=True): return sundryfix_insert(rec, cn, commit)
    @staticmethod
    def update(sundry_code, sno, rec, cn=None, commit=True): return sundryfix_update(sundry_code, sno, rec, cn, commit)
    @staticmethod
    def delete(sundry_code, sno, cn=None, commit=True): return sundryfix_delete(sundry_code, sno, cn, commit)

SundryTypeFixAPI = _SundryTypeFixAPI()



# ============================================================
# Phase A: sys_config_ui get_config/update_config call karta tha.
# Enviro me DateLock col nahi (Datelock alag table hai); UI labels
# real config par map kiye — koi schema invention nahi.
# ============================================================
def get_config(cn=None) -> dict:
    from HMS_py.core import enviro
    e = enviro.get(cn=cn)
    val = e.get("RoundOff")
    return {"RoundOffSetting": "Yes" if val in (1, True) else
            ("No" if val in (0, False) else ""),
            "SiteCode": SITE_CODE,
            "NCKOTPercentage": e.get("NCKOTPercentage", ""),
            "CheckoutTime": e.get("CheckoutVar", "")}


def update_config(rec: dict, cn=None, commit: bool = True) -> int:
    from HMS_py.core import enviro
    changes = {}
    if "RoundOffSetting" in rec:
        s = str(rec["RoundOffSetting"]).strip().lower()
        if s not in ("yes", "no", ""):
            raise ValueError("RoundOffSetting: 'Yes'/'No' hi")
        changes["RoundOff"] = "Yes" if s == "yes" else "No"
    if "NCKOTPercentage" in rec:
        changes["NCKOTPercentage"] = rec["NCKOTPercentage"]
    if "CheckoutTime" in rec:
        changes["CheckoutVar"] = rec["CheckoutTime"]
    if changes:
        enviro.update_settings(changes, cn=cn, commit=commit)
    return 1
