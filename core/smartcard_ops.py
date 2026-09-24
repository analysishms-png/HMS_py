"""Smart Card operations - SmartCardRegistration, SmartCardLedger, SmartCardReIssueDetail, SmartCardMaster."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === SmartCardRegistration ===
def _map_reg(r) -> dict:
    try:
        return {"code": r.Code or "", "cardtype": r.CardType or "", "cardno": r.CardNo or "",
                "name": (r.Name or "").strip(), "addr": r.Addr or "", "phone": r.Phone or "",
                "cashamt": r.CashAmt or 0.0, "securityamt": r.SecurityAmt or 0.0,
                "issdate": r.IssDate, "validupto": r.ValidUpto, "blockedyn": r.BlockedYN or "",
                "serialno": r.SerialNo or "", "currbal": r.CurrBal or 0.0, "securbal": r.SecurBal or 0.0,
                "membercode": r.MemberCode or "", "rewardbal": r.RewardBal or 0.0,
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "name": str(r[3] or "")}


def list_all_reg(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SmartCardRegistration WHERE Site_Code = ? ORDER BY Code", (SITE_CODE,), cn=cn)
    return [_map_reg(r) for r in rows]


def list_reg(cn=None, limit=500):
    return list_all_reg(cn, limit)


def get_reg(code, cn=None):
    rows = db.query("SELECT * FROM SmartCardRegistration WHERE Code = ?", (code,), cn=cn)
    return _map_reg(rows[0]) if rows else None


def search_reg(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SmartCardRegistration WHERE Site_Code = ? AND (Code LIKE ? OR Name LIKE ? OR CardNo LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_reg(r) for r in rows]


def insert_reg(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO SmartCardRegistration (Code,CardType,CardNo,Name,Addr,Phone,CashAmt,SecurityAmt,BlockedYN,SerialNo,U_Name,U_EntDt,U_AE,Site_Code,LogSite_Code,CurrBal,MemberCode,RewardBal)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,0,?,?)",
        (rec.get("code",""), rec.get("cardtype",""), rec.get("cardno",""),
         rec.get("name",""), rec.get("addr",""), rec.get("phone",""),
         rec.get("cashamt",0.0), rec.get("securityamt",0.0),
         rec.get("blockedyn","N"), rec.get("serialno",""),
         user, site, site, rec.get("membercode",""), rec.get("rewardbal",0.0)),
        cn=cn, commit=commit)
    return get_reg(rec.get("code",""), cn=cn)


def update_reg(code, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Name","Addr","Phone","CashAmt","SecurityAmt","BlockedYN","CurrBal","SecurBal","MemberCode","RewardBal","CardNo","CardType"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, code])
    db.execute("UPDATE SmartCardRegistration SET " + ", ".join(sets) + " WHERE Code = ?", params, cn=cn, commit=commit)
    return get_reg(code, cn=cn)


def delete_reg(code, cn=None, commit=True):
    return db.execute("DELETE FROM SmartCardRegistration WHERE Code = ?", (code,), cn=cn, commit=commit)


# === SmartCardLedger ===
def _map_ledger(r) -> dict:
    try:
        return {"code": r.Code or "", "vtype": r.VType or "", "vno": r.VNo or 0,
                "vdate": r.VDate, "type": r.Type or "", "narration": r.Narration or "",
                "amtcr": r.AmtCr or 0.0, "amtdr": r.AmtDr or 0.0,
                "prebalance": r.PreBalance or 0.0, "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "vtype": str(r[1] or "")}


def list_ledger(code, cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SmartCardLedger WHERE Code = ? ORDER BY VDate DESC", (code,), cn=cn)
    return [_map_ledger(r) for r in rows]


def insert_ledger(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO SmartCardLedger (Code,VType,VNo,VDate,VPrefix,Type,Narration,AmtCr,AmtDr,DocId,VSNO,HW_Id,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,PreBalance)"
        " VALUES (?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?)",
        (rec.get("code",""), rec.get("vtype",""), rec.get("vno",0),
         rec.get("vprefix",""), rec.get("type",""), rec.get("narration",""),
         rec.get("amtcr",0.0), rec.get("amtdr",0.0), rec.get("docid",""),
         rec.get("vsno",0), rec.get("hw_id",""),
         site, user, site, rec.get("prebalance",0.0)),
        cn=cn, commit=commit)
    return rec


# === Auto Settle Card Balance (VB6 MemAutoSettleCardBalance.frm) ===
def auto_settle_pending(cn=None, limit=500):
    """Fill-grid query (VB6 Proc_341_19): active member cards jinke paas
    outstanding balance hai (CurrBal<>0 ya SecurBal<>0).

    Returns list[dict]: code, cardno, name, serialno, curr_bal, secur_bal,
    member_name, mem_category.
    """
    rows = db.query(
        "SELECT SC.Code, SC.CardNo, SC.Name, SC.SerialNo, SC.CurrBal, "
        "SC.SecurBal, S.Name AS MemberName, M.Name AS MemCategory "
        "FROM SmartCardRegistration SC "
        "LEFT JOIN SubGroup S ON SC.MemberCode = S.SubCode "
        "INNER JOIN MemCatMast M ON S.CompanyType = M.Code "
        "WHERE (SC.LogSite_Code = ? OR SC.LogSite_Code = 'HO') "
        "AND S.ActiveYN = 0 AND (SC.CurrBal <> 0 OR SC.SecurBal <> 0) "
        "ORDER BY SC.Code",
        (SITE_CODE,), cn=cn)
    out = []
    for r in rows:
        try:
            out.append({
                "code": r.Code or "", "cardno": r.CardNo or "",
                "name": r.Name or "", "serialno": r.SerialNo or "",
                "curr_bal": float(r.CurrBal or 0),
                "secur_bal": float(r.SecurBal or 0),
                "member_name": r.MemberName or "",
                "mem_category": r.MemCategory or "",
            })
        except AttributeError:
            continue
    return out


def auto_settle_card(code: str, secur_settle: str = "C",
                     cn=None, commit=True, site=SITE_CODE, user=USER):
    """Ek card settle (VB6 CmdSave + Proc_341_20): ledger refund entry
    ('Agnst. Auto Refund' narration) + registration zero-out.

    secur_settle: 'C' = cash refund (AmtCr), 'R' = reverse to SecurBal
    (VB6 DGRestType 'C'/'R' radio). Returns dict.
    """
    code = str(code or "").strip()
    if not code:
        raise ValueError("Card Code zaroori hai")
    head = db.query(
        "SELECT CurrBal, SecurBal, LastTransAmt, LastTransDate "
        "FROM SmartCardRegistration WHERE Code = ?", (code,), cn=cn)
    if not head:
        raise ValueError(f"Card '{code}' SmartCardRegistration me nahi mila")
    curr = float(head[0].CurrBal or 0)
    sec = float(head[0].SecurBal or 0)

    def _go(c, commit_):
        if curr == 0 and sec == 0:
            return {"code": code, "refund": 0.0, "ledger_rows": 0,
                    "registration_rows": 0}
        ledger_rows = 0
        if curr != 0:
            insert_ledger({
                "code": code, "vtype": "ASB", "vno": 0,
                "type": "Refund", "narration": "Agnst. Auto Refund",
                "amtcr": abs(curr), "amtdr": 0.0, "prebalance": curr,
            }, cn=c, commit=False, site=site, user=user)
            ledger_rows += 1
        if sec != 0 and secur_settle == "C":
            insert_ledger({
                "code": code, "vtype": "ASB", "vno": 0,
                "type": "Refund", "narration": "Agnst. Auto Refund (Security)",
                "amtcr": abs(sec), "amtdr": 0.0, "prebalance": sec,
            }, cn=c, commit=False, site=site, user=user)
            ledger_rows += 1
        reg_rows = db.execute(
            "UPDATE SmartCardRegistration SET CurrBal = 0, SecurBal = 0, "
            "LastTransAmt = ?, LastTransDate = getdate() WHERE Code = ?",
            (abs(curr), code), cn=c, commit=False)
        if commit_:
            c.commit()
        return {"code": code, "refund": abs(curr) + (abs(sec) if secur_settle == "C" else 0),
                "ledger_rows": ledger_rows, "registration_rows": reg_rows}

    if cn is not None:
        return _go(cn, commit)
    own = db.connect()
    try:
        return _go(own, commit)
    except Exception:
        own.rollback()
        raise
    finally:
        own.close()


# === SmartCardReIssueDetail ===
def _map_reissue(r) -> dict:
    try:
        return {"trans_id": r.Trans_Id or 0, "cardregid": r.CardRegId or "",
                "hw_id": r.HW_Id or "", "issdate": r.IssDate, "validupto": r.ValidUpto,
                "remark": r.Remark or "", "oldhw_id": r.OldHW_Id or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"trans_id": r[0] or 0, "cardregid": str(r[1] or "")}


def list_reissue(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SmartCardReIssueDetail WHERE Site_Code = ? ORDER BY Trans_Id DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_reissue(r) for r in rows]


def insert_reissue(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Trans_Id) FROM SmartCardReIssueDetail", cn=cn)
    trans_id = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO SmartCardReIssueDetail (Trans_Id,CardRegId,HW_Id,IssDate,ValidUpto,Remark,OldHW_Id,OldIssDate,OldValidUpto,U_Name,U_EntDt,U_AE,Site_Code,LogSite_Code)"
        " VALUES (?,?,?,getdate(),?,?,?,?,?,?,getdate(),'A',?,?)",
        (trans_id, rec.get("cardregid",""), rec.get("hw_id",""),
         rec.get("validupto"), rec.get("remark",""), rec.get("oldhw_id",""),
         rec.get("oldissdate"), rec.get("oldvalidupto"), user, site, site),
        cn=cn, commit=commit)
    return {"trans_id": trans_id}


# === SmartCardMaster ===
def _map_master(r) -> dict:
    try:
        return {"contradocid": r.ContraDocid or "", "hw_id": r.HW_Id or "",
                "membercode": r.MemberCode or "", "cardregid": r.CardRegId or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"contradocid": str(r[0] or ""), "hw_id": str(r[1] or "")}


def list_master(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SmartCardMaster ORDER BY ContraDocid", cn=cn)
    return [_map_master(r) for r in rows]


def insert_master(rec, cn=None, commit=True, user=USER):
    db.execute(
        "INSERT INTO SmartCardMaster (ContraDocid,HW_Id,MemberCode,CardRegId,U_Name,U_EntDt,U_AE)"
        " VALUES (?,?,?,?,?,getdate(),'A')",
        (rec.get("contradocid",""), rec.get("hw_id",""),
         rec.get("membercode",""), rec.get("cardregid",""), user),
        cn=cn, commit=commit)
    return rec


class SmartCardAPI:
    def list_all(self, cn=None, limit=500): return list_all_reg(cn, limit)
    def get(self, code, cn=None): return get_reg(code, cn)
    def search(self, term, cn=None, limit=100): return search_reg(term, cn, limit)
    def insert(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_reg(rec, cn, commit, site, user)
    def update(self, code, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_reg(code, rec, cn, commit, site, user)
    def delete(self, code, cn=None, commit=True): return delete_reg(code, cn, commit)
    def list_ledger(self, code, cn=None, limit=500): return list_ledger(code, cn, limit)
    def insert_ledger(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_ledger(rec, cn, commit, site, user)
    def list_reissue(self, cn=None, limit=500): return list_reissue(cn, limit)
    def insert_reissue(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_reissue(rec, cn, commit, site, user)
    def list_master(self, cn=None, limit=500): return list_master(cn, limit)
    def insert_master(self, rec, cn=None, commit=True, user=USER): return insert_master(rec, cn, commit, user)