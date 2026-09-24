"""Facility billing - FacilityBill, FacilityBill1, FacilityBill2,
LocationFacility, SunTranFacility, DenominationDetail, DenominationFormat CRUD."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === FacilityBill ===
def _map_fbill(r) -> dict:
    try:
        return {"docid": r.Docid or "", "vtype": r.VType or "", "vdate": r.Vdate,
                "vno": r.Vno or 0, "vprefix": r.Vprefix or "", "partycode": r.PartyCode or "",
                "locationcode": r.LocationCode or "", "remark": r.Remark or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "vno": r[3] or 0}


def list_fbill(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM FacilityBill WHERE Site_Code = ? ORDER BY Vno DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_fbill(r) for r in rows]


def get_fbill(docid, cn=None):
    rows = db.query("SELECT * FROM FacilityBill WHERE Docid = ?", (docid,), cn=cn)
    return _map_fbill(rows[0]) if rows else None


def insert_fbill(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK)
    vno_rows = db.query(
        "SELECT MAX(Vno) FROM FacilityBill WITH (UPDLOCK, HOLDLOCK) "
        "WHERE Site_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "FB".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        # 16 columns == 16 VALUES == 12 markers — order matters:
        # ToPeriod=?, U_AE='A', U_Name=?, U_EntDt=getdate(), Site/LogSite=?, Remark=?
        "INSERT INTO FacilityBill (Docid, VType, Vdate, Vno, Vprefix, "
        "PartyCode, LocationCode, DueDate, ForPeriod, ToPeriod, U_AE, "
        "U_Name, U_EntDt, Site_Code, LogSite_Code, Remark) "
        "VALUES (?, 'FB', getdate(), ?, ?, ?, ?, ?, ?, ?, 'A', ?, getdate(), ?, ?, ?)",
        (docid, vno, vprefix, rec.get("partycode", ""),
         rec.get("locationcode", ""), rec.get("duedate"),
         rec.get("forperiod"), rec.get("toperiod"),
         user, site, site, rec.get("remark", "")),
        cn=cn, commit=commit)
    return get_fbill(docid, cn=cn)


def delete_fbill(docid, cn=None, commit=True):
    return db.execute("DELETE FROM FacilityBill WHERE Docid = ?", (docid,), cn=cn, commit=commit)


# === FacilityBill1 (facility bill details) ===
def _map_fbill1(r) -> dict:
    try:
        return {"docid": r.Docid or "", "vno": r.Vno or 0, "sno": r.Sno or 0,
                "vtype": r.VType or "", "partycode": r.PartyCode or "",
                "facilitycode": r.FacilityCode or "", "unitrate": r.UnitRate or 0.0,
                "amount": r.Amount or 0.0, "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[2] or 0}


def list_fbill1(docid, cn=None):
    rows = db.query("SELECT * FROM FacilityBill1 WHERE Docid = ? ORDER BY Sno", (docid,), cn=cn)
    return [_map_fbill1(r) for r in rows]


def insert_fbill1(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM FacilityBill1 WHERE Docid = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO FacilityBill1 (Docid, Vno, Sno, VType, Vdate, Vprefix, "
        "PartyCode, FacilityCode, Unit, UnitRate, Amount, AppDate, U_AE, "
        "U_Name, U_EntDt, Site_Code, LogSite_Code) "
        "VALUES (?, ?, ?, ?, getdate(), ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, getdate(), ?, ?)",
        (rec.get("docid", ""), rec.get("vno", 0), sno,
         rec.get("vtype", "FB"), rec.get("vprefix", "2026"),
         rec.get("partycode", ""), rec.get("facilitycode", ""),
         rec.get("unit", ""), rec.get("unitrate", 0.0),
         rec.get("amount", 0.0), user, site, site),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid", ""), "sno": sno}


def delete_fbill1(docid, sno, cn=None, commit=True):
    return db.execute("DELETE FROM FacilityBill1 WHERE Docid = ? AND Sno = ?", (docid, sno), cn=cn, commit=commit)


# === FacilityBill2 (facility tax) ===
def _map_fbill2(r) -> dict:
    try:
        return {"docid": r.DocId or "", "docid1": r.Docid1 or "", "sno": r.SNo or 0,
                "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "taxcode": r.TaxCode or "", "basevalue": r.BaseValue or 0.0,
                "taxper": r.TaxPer or 0.0, "taxamt": r.TaxAmt or 0.0,
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[2] or 0}


def list_fbill2(docid, cn=None):
    rows = db.query("SELECT * FROM FacilityBill2 WHERE DocId = ? ORDER BY SNo", (docid,), cn=cn)
    return [_map_fbill2(r) for r in rows]


def insert_fbill2(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(SNo) FROM FacilityBill2 WHERE DocId = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO FacilityBill2 (DocId,Docid1,SNo1,Vtype,VNo,Site_Code,Vprefix,Vdate,RestCode,TaxCode,BaseValue,TaxPer,TaxAmt,U_Name,U_EntDt,U_AE,DelFlag,LogSite_Code,SNo)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A','N',?,?)",
        (rec.get("docid",""), rec.get("docid1",""), sno, rec.get("vtype",""),
         rec.get("vno",0), site, rec.get("vprefix","2026"),
         rec.get("vdate"), rec.get("restcode",""),
         rec.get("taxcode",""), rec.get("basevalue",0.0), rec.get("taxper",0.0),
         rec.get("taxamt",0.0), user, site, sno),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_fbill2(docid, sno, cn=None, commit=True):
    return db.execute("DELETE FROM FacilityBill2 WHERE DocId = ? AND SNo = ?", (docid, sno), cn=cn, commit=commit)


# === LocationFacility ===
def _map_locfac(r) -> dict:
    try:
        return {"lccode": r.LcCode or "", "fcrcode": r.FcCode or "",
                "unitrate": r.UnitRate or 0.0, "dueon": r.DueOn or "",
                "startmonth": r.StartMonth or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"lccode": str(r[0] or ""), "fcrcode": str(r[1] or "")}


def list_locfac(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM LocationFacility WHERE Site_Code = ? ORDER BY LcCode",
                    (SITE_CODE,), cn=cn)
    return [_map_locfac(r) for r in rows]


def insert_locfac(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO LocationFacility (LcCode,AppDate,FcCode,UnitRate,DueOn,StartMonth,U_AE,U_Name,U_EntDt,Site_Code,LogSite_Code)"
        " VALUES (?,getdate(),?,?,?,?,'A',?,getdate(),?,?)",
        (rec.get("lccode",""), rec.get("fcrcode",""), rec.get("unitrate",0.0),
         rec.get("dueon",""), rec.get("startmonth",""), user, site, site),
        cn=cn, commit=commit)
    return rec


def delete_locfac(lccode, cn=None, commit=True):
    return db.execute("DELETE FROM LocationFacility WHERE LcCode = ?", (lccode,), cn=cn, commit=commit)


# === SunTranFacility ===
def _map_sunfac(r) -> dict:
    try:
        return {"docid": r.DocId or "", "sno": r.Sno or 0, "vtype": r.Vtype or "",
                "vno": r.VNo or 0, "site_code": getattr(r, "SiteCode", "") or r.Site_Code or "",
                "partycode": r.PartyCode or "", "suncode": r.SunCode or "",
                "amount": r.Amount or 0.0, "baseamount": r.BaseAmount or 0.0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[1] or 0}


def list_sunfac(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SunTranFacility WHERE LogSite_Code = ? ORDER BY DocId DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_sunfac(r) for r in rows]


def insert_sunfac(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM SunTranFacility WHERE DocId = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO SunTranFacility (DocId,Sno,Vtype,VNo,Vdate,PartyCode,SunCode,Limit,DispName,ROff,CalcFormula,SValue,Amount,BaseAmount,U_Name,U_EntDt,U_AE,SunAppDate,RevCode,RestCode,DelFlag,SiteCode,LogSite_Code)"
        " VALUES (?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?)",
        (rec.get("docid",""), sno, rec.get("vtype",""), rec.get("vno",0),
         rec.get("partycode",""), rec.get("suncode",""), rec.get("limit",0.0),
         rec.get("dispname",""), rec.get("roff",0.0), rec.get("calcformula",""),
         rec.get("svalue",0.0), rec.get("amount",0.0), rec.get("baseamount",0.0),
         user, rec.get("sunappdate"), rec.get("revcode",""), rec.get("restcode",""),
         rec.get("delflag","N"), site, site),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_sunfac(docid, sno, cn=None, commit=True):
    return db.execute("DELETE FROM SunTranFacility WHERE DocId = ? AND Sno = ?", (docid, sno), cn=cn, commit=commit)


# === DenominationDetail ===
def _map_dendetail(r) -> dict:
    try:
        return {"sno": r.Sno or 0, "sno1": r.Sno1 or 0, "vdate": r.Vdate,
                "name": r.Name or "", "denominationtype": r.DenominationType or "",
                "denominationvalue": r.DenominationValue or 0.0, "denominationunit": r.DenominationUnit or 0,
                "denominationtotal": r.DenominationTotal or 0.0,
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"sno": r[0] or 0, "name": str(r[3] or "")}


def list_dendetail(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM DenominationDetail WHERE Site_Code = ? ORDER BY Sno DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_dendetail(r) for r in rows]


def insert_dendetail(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM DenominationDetail", cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO DenominationDetail (Sno,Sno1,Vdate,Name,DenominationType,DenominationValue,DenominationUnit,DenominationTotal,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,getdate(),?,?,?,?,?,?,?,getdate(),'A',?)",
        (sno, rec.get("sno1",0), rec.get("name",""), rec.get("denominationtype",""),
         rec.get("denominationvalue",0.0), rec.get("denominationunit",0),
         rec.get("denominationtotal",0.0), site, user, site),
        cn=cn, commit=commit)
    return {"sno": sno}


def delete_dendetail(sno, cn=None, commit=True):
    return db.execute("DELETE FROM DenominationDetail WHERE Sno = ?", (sno,), cn=cn, commit=commit)


# === DenominationFormat ===
def _map_denformat(r) -> dict:
    try:
        return {"sno": r.Sno or 0, "denominationtype": r.DenominationType or "",
                "denominationvalue": r.DenominationValue or 0.0, "denominationunit": r.DenominationUnit or 0,
                "denominationtotal": r.DenominationTotal or 0.0,
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"sno": r[0] or 0, "denominationtype": str(r[1] or "")}


def list_denformat(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM DenominationFormat WHERE Site_Code = ? ORDER BY Sno",
                    (SITE_CODE,), cn=cn)
    return [_map_denformat(r) for r in rows]


def insert_denformat(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM DenominationFormat WHERE Site_Code = ?", (site,), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO DenominationFormat (Sno,DenominationType,DenominationValue,DenominationUnit,DenominationTotal,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,?,?,?,getdate(),'A',?)",
        (sno, rec.get("denominationtype",""), rec.get("denominationvalue",0.0),
         rec.get("denominationunit",0), rec.get("denominationtotal",0.0),
         site, user, site),
        cn=cn, commit=commit)
    return {"sno": sno}


def delete_denformat(sno, cn=None, commit=True):
    return db.execute("DELETE FROM DenominationFormat WHERE Sno = ?", (sno,), cn=cn, commit=commit)


class FacilityBillingAPI:
    def list_fbill(self, cn=None, limit=500): return list_fbill(cn, limit)
    def get_fbill(self, docid, cn=None): return get_fbill(docid, cn)
    def insert_fbill(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_fbill(rec, cn, commit, site, user)
    def delete_fbill(self, docid, cn=None, commit=True): return delete_fbill(docid, cn, commit)
    def list_fbill1(self, docid, cn=None): return list_fbill1(docid, cn)
    def insert_fbill1(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_fbill1(rec, cn, commit, site, user)
    def delete_fbill1(self, docid, sno, cn=None, commit=True): return delete_fbill1(docid, sno, cn, commit)
    def list_fbill2(self, docid, cn=None): return list_fbill2(docid, cn)
    def insert_fbill2(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_fbill2(rec, cn, commit, site, user)
    def delete_fbill2(self, docid, sno, cn=None, commit=True): return delete_fbill2(docid, sno, cn, commit)
    def list_locfac(self, cn=None, limit=500): return list_locfac(cn, limit)
    def insert_locfac(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_locfac(rec, cn, commit, site, user)
    def delete_locfac(self, lccode, cn=None, commit=True): return delete_locfac(lccode, cn, commit)
    def list_sunfac(self, cn=None, limit=500): return list_sunfac(cn, limit)
    def insert_sunfac(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_sunfac(rec, cn, commit, site, user)
    def delete_sunfac(self, docid, sno, cn=None, commit=True): return delete_sunfac(docid, sno, cn, commit)
    def list_dendetail(self, cn=None, limit=500): return list_dendetail(cn, limit)
    def insert_dendetail(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_dendetail(rec, cn, commit, site, user)
    def delete_dendetail(self, sno, cn=None, commit=True): return delete_dendetail(sno, cn, commit)
    def list_denformat(self, cn=None, limit=500): return list_denformat(cn, limit)
    def insert_denformat(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_denformat(rec, cn, commit, site, user)
    def delete_denformat(self, sno, cn=None, commit=True): return delete_denformat(sno, cn, commit)


# ============================================================
# Phase A (api-mismatch audit): UI facility_billing_ui list_all/
# get/insert call karta tha. FacilityBill header me Amount column
# nahi hai (schema-verified) — bill = header (FacilityBill) + line
# (FacilityBill1). insert() dono ek transaction me banata hai.
# ============================================================
def get_fbill1(docid, cn=None):
    rows = db.query("SELECT * FROM FacilityBill1 WHERE Docid = ? ORDER BY Sno",
                    (docid,), cn=cn)
    return _map_fbill1(rows[0]) if rows else None


def insert_bill_with_line(rec, cn=None, commit: bool = True) -> dict:
    own = cn is None
    cn = cn or db.connect()
    try:
        hdr = insert_fbill({"partycode": rec.get("partycode", ""),
                            "remark": rec.get("remark", "")},
                           cn=cn, commit=False)
        line = insert_fbill1({"docid": hdr["docid"], "vno": hdr["vno"],
                              "partycode": rec.get("partycode", ""),
                              "facilitycode": rec.get("facilitycode", ""),
                              "unitrate": rec.get("unitrate", 0) or 0,
                              "amount": rec.get("amount", 0) or 0},
                             cn=cn, commit=False)
        if commit:
            cn.commit()
        return {**hdr, "line": line}
    finally:
        if own:
            cn.close()


def list_all(cn=None, limit: int = 500) -> list:
    rows = db.query(
        f"SELECT TOP {int(limit)} * FROM FacilityBill1 "
        "ORDER BY Docid DESC, Sno", cn=cn)
    return [_map_fbill1(r) for r in rows]


get = get_fbill1
insert = insert_bill_with_line
