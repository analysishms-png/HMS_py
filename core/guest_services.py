"""Guest services - GuestComments, ComplaintDetail, ComplaintCategory,
LostFoundDetail, GuestWakeUp, GuestMessage, GuestStat CRUD."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === GuestComments ===
def _map_comments(r) -> dict:
    try:
        return {"code": r.Code or "", "name": (r.Name or "").strip(), "city": r.City or "",
                "mobile": r.MobileNo or "", "company": r.Company or "", "comments": r.Comments or "",
                "vtype": r.VType or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "name": str(r[1] or "")}


def list_comments(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestComments WHERE Site_Code = ? ORDER BY Code DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_comments(r) for r in rows]


def get_comments(code, cn=None):
    rows = db.query("SELECT * FROM GuestComments WHERE Code = ?", (code,), cn=cn)
    return _map_comments(rows[0]) if rows else None


def search_comments(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestComments WHERE Site_Code = ? AND (Name LIKE ? OR Comments LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_comments(r) for r in rows]


def insert_comments(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    code_rows = db.query("SELECT MAX(Code) FROM GuestComments", cn=cn)
    code = (code_rows[0][0] or 0) + 1 if code_rows and code_rows[0][0] else 1
    db.execute(
        "INSERT INTO GuestComments (Code,Name,Add1,Add2,City,MobileNo,Company,VType,Site_Code,U_Name,Comments,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,getdate(),?,?)",
        (code, rec.get("name",""), rec.get("add1",""), rec.get("add2",""),
         rec.get("city",""), rec.get("mobile",""), rec.get("company",""),
         rec.get("vtype",""), site, user, rec.get("comments",""), "A", site),
        cn=cn, commit=commit)
    return get_comments(code, cn=cn)


def update_comments(code, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Name","Add1","Add2","City","MobileNo","Company","Comments","VType"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, code])
    db.execute("UPDATE GuestComments SET " + ", ".join(sets) + " WHERE Code = ?", params, cn=cn, commit=commit)
    return get_comments(code, cn=cn)


def delete_comments(code, cn=None, commit=True):
    return db.execute("DELETE FROM GuestComments WHERE Code = ?", (code,), cn=cn, commit=commit)


# === ComplaintDetail ===
def _map_complaint(r) -> dict:
    try:
        return {"code": r.Code or "", "cdate": r.CDate, "category": r.Category or "",
                "description": r.Description or "", "depart": r.Depart or "",
                "status": r.Status or "", "clearingperson": r.ClearingPerson or "",
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "description": str(r[4] or "")}


def list_complaint(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM ComplaintDetail WHERE Site_Code = ? ORDER BY Code DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_complaint(r) for r in rows]


def get_complaint(code, cn=None):
    rows = db.query("SELECT * FROM ComplaintDetail WHERE Code = ?", (code,), cn=cn)
    return _map_complaint(rows[0]) if rows else None


def search_complaint(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM ComplaintDetail WHERE Site_Code = ? AND (Description LIKE ? OR Category LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_complaint(r) for r in rows]


def insert_complaint(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    code_rows = db.query("SELECT MAX(Code) FROM ComplaintDetail", cn=cn)
    code = (code_rows[0][0] or 0) + 1 if code_rows and code_rows[0][0] else 1
    db.execute(
        "INSERT INTO ComplaintDetail (Code,CDate,CTime,Category,Description,Depart,UName,Status,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,getdate(),?,?,?,?,?,?,?,?,getdate(),?,?)",
        (code, rec.get("ctime",""), rec.get("category",""), rec.get("description",""),
         rec.get("depart",""), user, rec.get("status","Open"), site, user, "A", site),
        cn=cn, commit=commit)
    return get_complaint(code, cn=cn)


def update_complaint(code, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Category","Description","Depart","Status","ClearingPerson"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, code])
    db.execute("UPDATE ComplaintDetail SET " + ", ".join(sets) + " WHERE Code = ?", params, cn=cn, commit=commit)
    return get_complaint(code, cn=cn)


def delete_complaint(code, cn=None, commit=True):
    return db.execute("DELETE FROM ComplaintDetail WHERE Code = ?", (code,), cn=cn, commit=commit)


# === ComplaintCategory ===
def _map_ccat(r) -> dict:
    try:
        return {"code": r.Code or "", "category": r.Category or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "category": str(r[1] or "")}


def list_complaint_category(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM ComplaintCategory WHERE Site_Code = ? ORDER BY Code",
                    (SITE_CODE,), cn=cn)
    return [_map_ccat(r) for r in rows]


def insert_complaint_category(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO ComplaintCategory (Code,Category,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,getdate(),?,?)",
        (rec.get("code",""), rec.get("category",""), site, user, "A", site),
        cn=cn, commit=commit)
    return rec


def delete_complaint_category(code, cn=None, commit=True):
    return db.execute("DELETE FROM ComplaintCategory WHERE Code = ?", (code,), cn=cn, commit=commit)


# === LostFoundDetail ===
def _map_lostfound(r) -> dict:
    try:
        return {"code": r.Code or "", "fdate": r.FDate, "farea": r.FArea or "",
                "description": r.Description or "", "status": r.Status or "",
                "contactno": r.ContactNo or "", "site_code": r.Site_Code or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "description": str(r[5] or "")}


def list_lostfound(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM LostFoundDetail WHERE Site_Code = ? ORDER BY Code DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_lostfound(r) for r in rows]


def get_lostfound(code, cn=None):
    rows = db.query("SELECT * FROM LostFoundDetail WHERE Code = ?", (code,), cn=cn)
    return _map_lostfound(rows[0]) if rows else None


def search_lostfound(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM LostFoundDetail WHERE Site_Code = ? AND (Description LIKE ? OR Code LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_lostfound(r) for r in rows]


def insert_lostfound(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    code_rows = db.query("SELECT MAX(Code) FROM LostFoundDetail", cn=cn)
    code = (code_rows[0][0] or 0) + 1 if code_rows and code_rows[0][0] else 1
    db.execute(
        "INSERT INTO LostFoundDetail (Code,FDate,FTime,FArea,FindBy,Description,UName1,ContactNo,Status,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,getdate(),?,?,?,?,?,?,?,?,?,getdate(),?,?)",
        (code, rec.get("ftime",""), rec.get("farea",""), rec.get("findby",""),
         rec.get("description",""), rec.get("uname1",""), rec.get("contactno",""),
         rec.get("status","Open"), site, user, "A", site),
        cn=cn, commit=commit)
    return get_lostfound(code, cn=cn)


def update_lostfound(code, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("FArea","FindBy","Description","ClaimedBy","ContactNo","DeliveredBy","Status"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, code])
    db.execute("UPDATE LostFoundDetail SET " + ", ".join(sets) + " WHERE Code = ?", params, cn=cn, commit=commit)
    return get_lostfound(code, cn=cn)


def delete_lostfound(code, cn=None, commit=True):
    return db.execute("DELETE FROM LostFoundDetail WHERE Code = ?", (code,), cn=cn, commit=commit)


# === GuestWakeUp ===
def _map_wakeup(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
                "vdate": r.Vdate, "vtime": r.VTime or "", "roomno": r.RoomNo or "",
                "wdate": r.WDate, "wtime": r.WTime or "",
                "guestprof": r.GuestProf or "", "folio": r.FolioNo or 0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "roomno": str(r[9] or "")}


def list_wakeup(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestWakeUp WHERE Site_Code = ? ORDER BY VNo DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_wakeup(r) for r in rows]


def insert_wakeup(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK); no Vtype/Vprefix filter
    # in this table's MAX query - keep raw lock query here.
    vno_rows = db.query(
        "SELECT MAX(VNo) FROM GuestWakeUp WITH (UPDLOCK, HOLDLOCK) "
        "WHERE Site_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "WK".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO GuestWakeUp (DocId,Vtype,VNo,Site_Code,Vprefix,Vdate,VTime,RoomCat,RoomType,RoomNo,RemReqd,GuestProf,FolioNo,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,'WK',?,?,?,getdate(),?,?,?,?,?,?,?,?,getdate(),'A',?)",
        (docid, vno, site, vprefix, rec.get("vtime",""),
         rec.get("roomcat",""), rec.get("roomtype",""), rec.get("roomno",""),
         rec.get("remreqd",""), rec.get("guestprof",""), rec.get("folio",0), user, site),
        cn=cn, commit=commit)
    return {"docid": docid, "vno": vno}


def delete_wakeup(docid, cn=None, commit=True):
    return db.execute("DELETE FROM GuestWakeUp WHERE DocId = ?", (docid,), cn=cn, commit=commit)


# === GuestMessage ===
def _map_message(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "site_code": r.Site_Code or "", "vprefix": r.Vprefix or "",
                "vdate": r.Vdate, "roomno": r.RoomNo or "", "caller": r.Caller or "",
                "message": r.Message or "", "guestprof": r.GuestProf or "",
                "folio": r.FolioNo or 0, "solved": r.Solved or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "message": str(r[10] or "")}


def list_message(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestMessage WHERE Site_Code = ? ORDER BY VNo DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_message(r) for r in rows]


def insert_message(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK)
    vno_rows = db.query(
        "SELECT MAX(VNo) FROM GuestMessage WITH (UPDLOCK, HOLDLOCK) "
        "WHERE Site_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "MS".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO GuestMessage (DocId,Vtype,VNo,Site_Code,Vprefix,Vdate,RoomCat,RoomType,RoomNo,Caller,Telephone,Message,RecdDate,RecdTime,GuestProf,FolioNo,U_Name,U_EntDt,U_AE,Solved,LogSite_Code)"
        " VALUES (?,'MS',?,?,?,getdate(),?,?,?,?,?,?,getdate(),?,?,?,?,getdate(),'A','N',?)",
        (docid, vno, site, vprefix, rec.get("roomcat",""), rec.get("roomtype",""),
         rec.get("roomno",""), rec.get("caller",""), rec.get("telephone",""),
         rec.get("message",""), rec.get("rcdtime",""),
         rec.get("guestprof",""), rec.get("folio",0), user, site),
        cn=cn, commit=commit)
    return {"docid": docid, "vno": vno}


def update_message(docid, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Message","Caller","Telephone","Solved"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, docid])
    db.execute("UPDATE GuestMessage SET " + ", ".join(sets) + " WHERE DocId = ?", params, cn=cn, commit=commit)
    return {"docid": docid}


def delete_message(docid, cn=None, commit=True):
    return db.execute("DELETE FROM GuestMessage WHERE DocId = ?", (docid,), cn=cn, commit=commit)


# === GuestStat ===
def _map_stat(r) -> dict:
    try:
        return {"code": r.Code or "", "name": (r.Name or "").strip(),
                "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"code": str(r[0] or ""), "name": str(r[1] or "")}


def list_stat(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM GuestStat WHERE Site_Code = ? ORDER BY Code",
                    (SITE_CODE,), cn=cn)
    return [_map_stat(r) for r in rows]


def insert_stat(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    db.execute(
        "INSERT INTO GuestStat (Code,Name,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,getdate(),?,?)",
        (rec.get("code",""), rec.get("name",""), site, user, "A", site),
        cn=cn, commit=commit)
    return rec


def delete_stat(code, cn=None, commit=True):
    return db.execute("DELETE FROM GuestStat WHERE Code = ?", (code,), cn=cn, commit=commit)


class GuestServicesAPI:
    def list_comments(self, cn=None, limit=500): return list_comments(cn, limit)
    def get_comments(self, code, cn=None): return get_comments(code, cn)
    def search_comments(self, term, cn=None, limit=100): return search_comments(term, cn, limit)
    def insert_comments(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_comments(rec, cn, commit, site, user)
    def update_comments(self, code, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_comments(code, rec, cn, commit, site, user)
    def delete_comments(self, code, cn=None, commit=True): return delete_comments(code, cn, commit)
    def list_complaint(self, cn=None, limit=500): return list_complaint(cn, limit)
    def get_complaint(self, code, cn=None): return get_complaint(code, cn)
    def search_complaint(self, term, cn=None, limit=100): return search_complaint(term, cn, limit)
    def insert_complaint(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_complaint(rec, cn, commit, site, user)
    def update_complaint(self, code, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_complaint(code, rec, cn, commit, site, user)
    def delete_complaint(self, code, cn=None, commit=True): return delete_complaint(code, cn, commit)
    def list_lostfound(self, cn=None, limit=500): return list_lostfound(cn, limit)
    def get_lostfound(self, code, cn=None): return get_lostfound(code, cn)
    def insert_lostfound(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_lostfound(rec, cn, commit, site, user)
    def update_lostfound(self, code, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_lostfound(code, rec, cn, commit, site, user)
    def delete_lostfound(self, code, cn=None, commit=True): return delete_lostfound(code, cn, commit)
    def list_wakeup(self, cn=None, limit=500): return list_wakeup(cn, limit)
    def insert_wakeup(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_wakeup(rec, cn, commit, site, user)
    def delete_wakeup(self, docid, cn=None, commit=True): return delete_wakeup(docid, cn, commit)
    def list_message(self, cn=None, limit=500): return list_message(cn, limit)
    def insert_message(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_message(rec, cn, commit, site, user)
    def update_message(self, docid, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_message(docid, rec, cn, commit, site, user)
    def delete_message(self, docid, cn=None, commit=True): return delete_message(docid, cn, commit)
    def list_stat(self, cn=None, limit=500): return list_stat(cn, limit)
    def insert_stat(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_stat(rec, cn, commit, site, user)
    def delete_stat(self, code, cn=None, commit=True): return delete_stat(code, cn, commit)


# Phase A: UI singular/plural dono naam use karta tha — aliases.
insert_comment = insert_comments
delete_comment = delete_comments
list_complaints = list_complaint
