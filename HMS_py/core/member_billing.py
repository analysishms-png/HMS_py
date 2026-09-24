"""Member billing - MemberFamily, MemBill, MemEnviro, MemCatChngDetail, MemProposedMemInf CRUD."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === MemberFamily ===
def _map_family(r) -> dict:
    try:
        return {"subcode": r.SubCode or "", "sno": r.SNo or 0, "name": (r.Name or "").strip(),
                "relationship": r.Relationship or "", "gender": r.Gender or "",
                "dob": r.DOB, "phone": r.Phone or "", "mobile": r.Mobile or "",
                "email": r.Email or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"subcode": str(r[0] or ""), "sno": r[1] or 0}


def list_family(subcode, cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM MemberFamily WHERE SubCode = ? ORDER BY SNo", (subcode,), cn=cn)
    return [_map_family(r) for r in rows]


def insert_family(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(SNo) FROM MemberFamily WHERE SubCode = ?", (rec.get("subcode",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO MemberFamily (SubCode,SNo,Relationship,Name,Gender,DOB,Phone,Mobile,Email,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)",
        (rec.get("subcode",""), sno, rec.get("relationship",""), rec.get("name",""),
         rec.get("gender",""), rec.get("dob"), rec.get("phone",""),
         rec.get("mobile",""), rec.get("email",""), site, site, user),
        cn=cn, commit=commit)
    return {"subcode": rec.get("subcode",""), "sno": sno}


def delete_family(subcode, sno, cn=None, commit=True):
    return db.execute("DELETE FROM MemberFamily WHERE SubCode = ? AND SNo = ?", (subcode, sno), cn=cn, commit=commit)


# === MemBill ===
def _map_membill(r) -> dict:
    try:
        return {"docid": r.Docid or "", "vdate": r.vdate, "vno": r.vno or 0,
                "vprefix": r.vprefix or "", "vtype": r.Vtype or "", "memcode": r.MemCode or "",
                "memcatcode": r.MemCatCode or "", "cardno": r.cardno or "",
                "mthyear": r.MthYear or "", "netamount": r.NetAmount or 0.0,
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or "",
                "billdate": r.BillDate, "amount": r.Amount or 0.0, "roundoff": r.RoundOff or 0.0}
    except AttributeError:
        return {"docid": str(r[0] or ""), "vno": r[2] or 0}


def list_membill(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM MemBill WHERE Site_Code = ? ORDER BY vno DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_membill(r) for r in rows]


def get_membill(docid, cn=None):
    rows = db.query("SELECT * FROM MemBill WHERE Docid = ?", (docid,), cn=cn)
    return _map_membill(rows[0]) if rows else None


def insert_membill(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    vno_rows = db.query("SELECT MAX(vno) FROM MemBill WHERE Site_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "MB".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO MemBill (Docid,vdate,vno,vprefix,Vtype,MemCode,MemCatCode,cardno,MthYear,NetAmount,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,BillDate,RoundOff,Amount)"
        " VALUES (?,getdate(),?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?)",
        (docid, vno, vprefix, rec.get("vtype","MB"), rec.get("memcode",""),
         rec.get("memcatcode",""), rec.get("cardno",""), rec.get("mthyear",""),
         rec.get("netamount",0.0), site, user, site,
         rec.get("billdate"), rec.get("roundoff",0.0), rec.get("amount",0.0)),
        cn=cn, commit=commit)
    return get_membill(docid, cn=cn)


def delete_membill(docid, cn=None, commit=True):
    return db.execute("DELETE FROM MemBill WHERE Docid = ?", (docid,), cn=cn, commit=commit)


# === MemEnviro ===
def _map_memenviro(r) -> dict:
    try:
        return {"bill_header": r.Bill_Header or "", "bill_footer": r.Bill_Footer or "",
                "bill_printtype": r.Bill_PrintType or "", "site_code": r.Site_Code or "",
                "bill_message": r.BillMessage or "", "bill_payduedate": r.BillPayDueDate or 0}
    except AttributeError:
        return {"bill_header": str(r[0] or "")}


def list_memenviro(cn=None):
    rows = db.query("SELECT * FROM MemEnviro WHERE Site_Code = ?", (SITE_CODE,), cn=cn)
    return [_map_memenviro(r) for r in rows]


def get_memenviro(site=SITE_CODE, cn=None):
    rows = db.query("SELECT * FROM MemEnviro WHERE Site_Code = ?", (site,), cn=cn)
    return _map_memenviro(rows[0]) if rows else None


def update_memenviro(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Bill_Header","Bill_Footer","Bill_PrintType","BillMessage","BillPayDueDate"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    params.append(site)
    db.execute("UPDATE MemEnviro SET " + ", ".join(sets) + " WHERE Site_Code = ?", params, cn=cn, commit=commit)
    return get_memenviro(site, cn=cn)


# === MemCatChngDetail ===
def _mapcatchng(r) -> dict:
    try:
        return {"code": r.Code or "", "type": r.Type or "", "memcode": r.MemCode or "",
                "oldcat": r.OldCat or "", "newcat": r.NewCat or "",
                "frmonth": r.FrMonth or "", "tomonth": r.ToMonth or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "memcode": str(r[2] or "")}


def list_catchng(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM MemCatChngDetail WHERE Site_Code = ? ORDER BY Code",
                    (SITE_CODE,), cn=cn)
    return [_mapcatchng(r) for r in rows]


def insert_catchng(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO MemCatChngDetail (Code,Type,MemCode,OldCat,NewCat,FrMonth,ToMonth,Site_Code,LogSite_Code,U_AE,U_EntDt,U_Name)"
        " VALUES (?,?,?,?,?,?,?,?,?,'A',getdate(),?)",
        (rec.get("code",""), rec.get("type",""), rec.get("memcode",""),
         rec.get("oldcat",""), rec.get("newcat",""), rec.get("frmonth",""),
         rec.get("tomonth",""), site, site, user),
        cn=cn, commit=commit)
    return rec


# === MemProposedMemInf ===
def _map_proposed(r) -> dict:
    try:
        return {"subcode": r.SubCode or "", "sno": r.SNo or 0, "pmemcode": r.PMemCode or "",
                "membertype": r.MemberType or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"subcode": str(r[0] or ""), "sno": r[1] or 0}


def list_proposed(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM MemProposedMemInf WHERE Site_Code = ? ORDER BY SubCode",
                    (SITE_CODE,), cn=cn)
    return [_map_proposed(r) for r in rows]


def insert_proposed(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO MemProposedMemInf (SubCode,SNo,PMemCode,MemberType,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE)"
        " VALUES (?,?,?,?,?,?,?,getdate(),'A')",
        (rec.get("subcode",""), rec.get("sno",0), rec.get("pmemcode",""),
         rec.get("membertype",""), site, site, user),
        cn=cn, commit=commit)
    return rec


class MemberBillingAPI:
    def list_family(self, subcode, cn=None, limit=500): return list_family(subcode, cn, limit)
    def insert_family(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_family(rec, cn, commit, site, user)
    def delete_family(self, subcode, sno, cn=None, commit=True): return delete_family(subcode, sno, cn, commit)
    def list_membill(self, cn=None, limit=500): return list_membill(cn, limit)
    def get_membill(self, docid, cn=None): return get_membill(docid, cn)
    def insert_membill(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_membill(rec, cn, commit, site, user)
    def delete_membill(self, docid, cn=None, commit=True): return delete_membill(docid, cn, commit)
    def get_memenviro(self, site=SITE_CODE, cn=None): return get_memenviro(site, cn)
    def update_memenviro(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_memenviro(rec, cn, commit, site, user)
    def list_catchng(self, cn=None, limit=500): return list_catchng(cn, limit)
    def insert_catchng(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_catchng(rec, cn, commit, site, user)
    def list_proposed(self, cn=None, limit=500): return list_proposed(cn, limit)
    def insert_proposed(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_proposed(rec, cn, commit, site, user)


# Phase A (api-mismatch audit): UI member_billing_ui list_all/get/insert
# call karta tha — MemBill ke canonical fns ke aliases.
list_all = list_membill
get = get_membill
insert = insert_membill
