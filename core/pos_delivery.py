"""POS Delivery module - AssignDelivery/DeliveryBoy/GuestReward CRUD.

Tables verified in DB KailashData2526:
  AssignDelivery - delivery tracking (DocId, DeliBoy, BillAmt)
  DeliveryBoy    - delivery boy master (already in pos_masters.py, ref provided)
  GuestReward    - reward points (DocId, CustCode, RewardPoint, RedemPoint)
"""
from __future__ import annotations

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# ============================================================
# AssignDelivery - Delivery Tracking
# ============================================================
_ASSIGNDEL_COLS = (
    "DocId, Vtype, VNo, Vprefix, Vdate, Ddate, RestCode, DeliBoy, "
    "BillAmt, Remark, Site_Code, U_Name, U_AE, U_EntDt, LogSite_Code"
)


def _map_assign(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "vtype": r.Vtype or "",
            "vno": int(r.VNo or 0), "vprefix": r.Vprefix or "",
            "vdate": r.Vdate, "ddate": r.Ddate,
            "restcode": r.RestCode or "", "deliboy": r.DeliBoy or "",
            "billamt": float(r.BillAmt or 0), "remark": r.Remark or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "vtype": vals[1] or "",
            "vno": int(vals[2] or 0), "vprefix": vals[3] or "",
            "vdate": vals[4], "ddate": vals[5],
            "restcode": vals[6] or "", "deliboy": vals[7] or "",
            "billamt": float(vals[8] or 0), "remark": vals[9] or "",
            "u_name": vals[11] or "", "u_ae": vals[12] or "",
        }


def _validate_assign(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def assign_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_ASSIGNDEL_COLS} FROM AssignDelivery ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_assign(r) for r in rows]


def assign_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_ASSIGNDEL_COLS} FROM AssignDelivery WHERE DocId = ?",
        (docid,), cn=cn)
    return _map_assign(rows[0]) if rows else None


def assign_search(deliboy: str, cn=None, limit: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_ASSIGNDEL_COLS} FROM AssignDelivery "
        "WHERE DeliBoy LIKE ? ORDER BY U_EntDt DESC",
        (f"%{deliboy}%",), cn=cn)
    return [_map_assign(r) for r in rows]


def assign_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_assign(rec)
    return db.execute(
        "INSERT INTO AssignDelivery (DocId, Vtype, VNo, Vprefix, Vdate, "
        "Ddate, RestCode, DeliBoy, BillAmt, Remark, Site_Code, "
        "U_Name, U_AE, U_EntDt, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), ?)",
        (rec["docid"], rec.get("vtype", ""), int(rec.get("vno") or 0),
         rec.get("vprefix", ""), rec.get("vdate"), rec.get("ddate"),
         rec.get("restcode", ""), rec.get("deliboy", ""),
         float(rec.get("billamt") or 0), rec.get("remark", ""),
         SITE_CODE, USER, "A", SITE_CODE),
        cn=cn, commit=commit)


def assign_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE AssignDelivery SET DeliBoy = ?, BillAmt = ?, Remark = ?, "
        "Ddate = ?, U_Name = ?, U_AE = 'E', U_EntDt = getdate() "
        "WHERE DocId = ?",
        (rec.get("deliboy", ""), float(rec.get("billamt") or 0),
         rec.get("remark", ""), rec.get("ddate"), USER, docid),
        cn=cn, commit=commit)


def assign_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM AssignDelivery WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _AssignDelAPI:
    LIMITS = {"docid": 30, "vtype": 5, "deliboy": 10, "remark": 50}
    @staticmethod
    def list_all(cn=None, limit=500): return assign_list(cn, limit)
    @staticmethod
    def get(docid, cn=None): return assign_get(docid, cn)
    @staticmethod
    def search(deliboy, cn=None, limit=100): return assign_search(deliboy, cn, limit)
    @staticmethod
    def insert(rec, cn=None, commit=True): return assign_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return assign_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return assign_delete(docid, cn, commit)

AssignDelAPI = _AssignDelAPI()


# ============================================================
# GuestReward - Reward Points
# ============================================================
_GUESTREWARD_COLS = (
    "DocId, CustCode, Vdate, DepartName, BillNo, BillAmt, RewardPoint, "
    "RedemPoint, MobileNo, Site_code, LogSite_Code, U_Name, U_AE, "
    "U_EntDt, Total, DiscAmt, RestCode, SchemeCode, SaleUpTo, "
    "RPointOnAmt, RewardValue, RedeemValue, RegId, DiscPer"
)


def _map_reward(r) -> dict:
    try:
        return {
            "docid": r.DocId or "", "custcode": r.CustCode or "",
            "vdate": r.Vdate, "departname": r.DepartName or "",
            "billno": r.BillNo or "", "billamt": float(r.BillAmt or 0),
            "rewardpoint": float(r.RewardPoint or 0),
            "redeempoint": float(r.RedemPoint or 0),
            "mobileno": r.MobileNo or "",
            "total": float(r.Total or 0),
            "discamt": float(r.DiscAmt or 0),
            "restcode": r.RestCode or "", "schemecode": r.SchemeCode or "",
            "saleupto": float(r.SaleUpTo or 0),
            "rpointonamt": float(r.RPointOnAmt or 0),
            "rewardvalue": float(r.RewardValue or 0),
            "redeemvalue": float(r.RedeemValue or 0),
            "regid": r.RegId or "",
            "discper": float(r.DiscPer or 0),
            "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
        }
    except AttributeError:
        vals = list(r)
        return {
            "docid": vals[0] or "", "custcode": vals[1] or "",
            "vdate": vals[2], "departname": vals[3] or "",
            "billno": vals[4] or "", "billamt": float(vals[5] or 0),
            "rewardpoint": float(vals[6] or 0),
            "redeempoint": float(vals[7] or 0),
            "mobileno": vals[8] or "",
            "total": float(vals[13] if len(vals) > 13 else 0),
            "discamt": float(vals[14] if len(vals) > 14 else 0),
            "restcode": vals[15] if len(vals) > 15 else "",
            "schemecode": vals[16] if len(vals) > 16 else "",
            "saleupto": float(vals[18] if len(vals) > 18 else 0),
            "rpointonamt": float(vals[19] if len(vals) > 19 else 0),
            "rewardvalue": float(vals[20] if len(vals) > 20 else 0),
            "redeemvalue": float(vals[21] if len(vals) > 21 else 0),
            "regid": vals[22] if len(vals) > 22 else "",
            "discper": float(vals[23] if len(vals) > 23 else 0),
            "u_name": vals[11] or "", "u_ae": vals[12] or "",
        }


def _validate_reward(rec: dict):
    if not rec.get("docid", "").strip():
        raise ValueError("DocId zaroori hai")


def reward_list(cn=None, limit: int = 500) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_GUESTREWARD_COLS} FROM GuestReward ORDER BY U_EntDt DESC",
        cn=cn)
    return [_map_reward(r) for r in rows]


def reward_get(docid: str, cn=None) -> dict | None:
    rows = db.query(
        f"SELECT {_GUESTREWARD_COLS} FROM GuestReward WHERE DocId = ?",
        (docid,), cn=cn)
    return _map_reward(rows[0]) if rows else None


def reward_search(custcode: str, cn=None, limit: int = 100) -> list[dict]:
    rows = db.query(
        f"SELECT TOP {int(limit)} {_GUESTREWARD_COLS} FROM GuestReward "
        "WHERE CustCode LIKE ? ORDER BY U_EntDt DESC",
        (f"%{custcode}%",), cn=cn)
    return [_map_reward(r) for r in rows]


def reward_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_reward(rec)
    return db.execute(
        "INSERT INTO GuestReward (DocId, CustCode, Vdate, DepartName, "
        "BillNo, BillAmt, RewardPoint, RedemPoint, MobileNo, Site_code, "
        "LogSite_Code, U_Name, U_AE, U_EntDt, Total, DiscAmt, RestCode, "
        "SchemeCode, SaleUpTo, RPointOnAmt, RewardValue, RedeemValue, "
        "RegId, DiscPer) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?)",
        (rec["docid"], rec.get("custcode", ""), rec.get("vdate"),
         rec.get("departname", ""), rec.get("billno", ""),
         float(rec.get("billamt") or 0), float(rec.get("rewardpoint") or 0),
         float(rec.get("redeempoint") or 0), rec.get("mobileno", ""),
         SITE_CODE, SITE_CODE, USER, "A",
         float(rec.get("total") or 0), float(rec.get("discamt") or 0),
         rec.get("restcode", ""), rec.get("schemecode", ""),
         float(rec.get("saleupto") or 0), float(rec.get("rpointonamt") or 0),
         float(rec.get("rewardvalue") or 0), float(rec.get("redeemvalue") or 0),
         rec.get("regid", ""), float(rec.get("discper") or 0)),
        cn=cn, commit=commit)


def reward_update(docid: str, rec: dict, cn=None, commit: bool = True) -> int:
    return db.execute(
        "UPDATE GuestReward SET RewardPoint = ?, RedemPoint = ?, "
        "BillAmt = ?, Total = ?, DiscAmt = ?, "
        "U_Name = ?, U_AE = 'E', U_EntDt = getdate() WHERE DocId = ?",
        (float(rec.get("rewardpoint") or 0), float(rec.get("redeempoint") or 0),
         float(rec.get("billamt") or 0), float(rec.get("total") or 0),
         float(rec.get("discamt") or 0), USER, docid),
        cn=cn, commit=commit)


def reward_delete(docid: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM GuestReward WHERE DocId = ?", (docid,),
                      cn=cn, commit=commit)


class _GuestRewardAPI:
    LIMITS = {"docid": 30, "custcode": 10, "billno": 15, "mobileno": 15}
    @staticmethod
    def list_all(cn=None, limit=500): return reward_list(cn, limit)
    @staticmethod
    def get(docid, cn=None): return reward_get(docid, cn)
    @staticmethod
    def search(custcode, cn=None, limit=100): return reward_search(custcode, cn, limit)
    @staticmethod
    def insert(rec, cn=None, commit=True): return reward_insert(rec, cn, commit)
    @staticmethod
    def update(docid, rec, cn=None, commit=True): return reward_update(docid, rec, cn, commit)
    @staticmethod
    def delete(docid, cn=None, commit=True): return reward_delete(docid, cn, commit)

GuestRewardAPI = _GuestRewardAPI()
