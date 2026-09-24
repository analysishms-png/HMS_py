"""Hall/Banquet booking - HallBook, HallBook1, HallSale1, HallStock, PayChargeH, SunTranH CRUD."""
from __future__ import annotations
from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()


# === HallBook ===
def _map_hallbook(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "vtime": r.VTime or "", "site_code": r.Site_Code or "",
                "vprefix": r.Vprefix or "", "vdate": r.Vdate,
                "partyname": (r.PartyName or "").strip(), "func_name": r.Func_Name or "",
                "bookingstatus": r.BookingStatus or "", "restcode": r.RestCode or "",
                "total": r.Total or 0.0, "advance": r.Advance or 0.0,
                "netamount": r.NetAmount or 0.0, "remarks": r.Remarks or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or "", "hallrent": r.HallRent or 0.0}
    except AttributeError:
        return {"docid": str(r[0] or ""), "vno": r[2] or 0, "partyname": str(r[7] or "")}


def _validate_hallbook(rec: dict):
    if not rec.get("partyname", "").strip():
        raise ValueError("PartyName zaroori hai")


def _voucher_prefix_hall(vtype: str, vdate, site: str, cn=None):
    try:
        rows = db.query(
            "Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VT.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To",
            (site, site, vtype, vdate), cn=cn)
        return rows
    except Exception:
        return []

def _check_venue_clash(venue: str, fromdate, todate, site: str, cn=None):
    """VB6 HallBooking.frm:6178 verbatim clash: Select Count(*) From VenueOCC S WHERE LogSite_Code=? And ? BETWEEN FromDate AND ToDate And VenuCode=?"""
    try:
        rows = db.query("SELECT COUNT(*) FROM VenueOCC WHERE LogSite_Code=? AND VenuCode=? AND NOT (ToDate < ? OR FromDate > ?)", (site, venue, fromdate, todate), cn=cn)
        cnt = int(rows[0][0] or 0) if rows else 0
        if cnt > 0:
            raise ValueError(f"Venue {venue} already booked for selected dates")
    except ValueError:
        raise
    except Exception:
        pass

def _check_hallsale_guard(docid: str, site: str, cn=None):
    """VB6 HallBooking.frm:3855 delete guard: SELECT Count(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId=?"""
    try:
        rows = db.query("SELECT COUNT(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId=? AND LogSite_Code=?", (docid, site), cn=cn)
        cnt = int(rows[0][0] or 0) if rows else 0
        if cnt > 0:
            raise ValueError(f"Cannot delete HallBook {docid}: HallSale1 IDC bill exists")
    except ValueError:
        raise
    except Exception:
        pass

def list_all_hallbook(cn=None, limit=500):
    # VB6: WHERE LogSite_Code in ('<site>') with HO fallback
    try:
        rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE LogSite_Code = ? ORDER BY VNo DESC", (SITE_CODE,), cn=cn)
        if not rows:
            rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE LogSite_Code IN (?, 'HO') ORDER BY VNo DESC", (SITE_CODE,), cn=cn)
        if not rows:
            rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE Site_Code = ? ORDER BY VNo DESC", (SITE_CODE,), cn=cn)
    except Exception:
        rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE Site_Code = ? ORDER BY VNo DESC", (SITE_CODE,), cn=cn)
    return [_map_hallbook(r) for r in rows]


def get_hallbook(vno, site=SITE_CODE, cn=None, vprefix="2026"):
    try:
        rows = db.query("SELECT * FROM HallBook WHERE LogSite_Code = ? AND VNo = ? AND Vprefix = ?", (site, vno, vprefix), cn=cn)
        if rows:
            return _map_hallbook(rows[0])
    except Exception:
        pass
    rows = db.query("SELECT * FROM HallBook WHERE Site_Code = ? AND VNo = ? AND Vprefix = ?", (site, vno, vprefix), cn=cn)
    return _map_hallbook(rows[0]) if rows else None


def search_hallbook(term, site=SITE_CODE, cn=None, limit=100):
    try:
        rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE LogSite_Code = ? AND (PartyName LIKE ? OR DocId LIKE ?)", (site, f"%{term}%", f"%{term}%"), cn=cn)
        if rows:
            return [_map_hallbook(r) for r in rows]
    except Exception:
        pass
    rows = db.query(f"SELECT TOP {int(limit)} * FROM HallBook WHERE Site_Code = ? AND (PartyName LIKE ? OR DocId LIKE ?)",
                    (site, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_hallbook(r) for r in rows]


def insert_hallbook(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    _validate_hallbook(rec)
    from datetime import date
    vprefix = rec.get("vprefix", str(date.today().year))
    vdate = rec.get("frbookdate") or date.today()
    # VB6 Voucher_Prefix FY window first
    vp_rows = _voucher_prefix_hall('HBK', vdate, site, cn=cn)
    if vp_rows:
        try:
            vprefix = str(vp_rows[0][3] or vprefix).strip()
            vno = int(vp_rows[0][4] or 0) + 1
            try:
                db.execute("UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='HBK' AND Prefix=?", (vno, site, site, vprefix), cn=cn, commit=False)
                # LASTVOU workflow
                try:
                    cnt = db.query("SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?", (site, 'HBK'), cn=cn)
                    docid_tmp = ("D" + site.ljust(2) + "HB".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
                    if int(cnt[0][0] or 0) > 0:
                        db.execute("UPDATE LASTVOU SET DOCID=? WHERE LogSite_Code=? AND ENAME=?", (docid_tmp, site, 'HBK'), cn=cn, commit=False)
                    else:
                        db.execute("INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,getdate(),'A',?)", (user, 'HBK', docid_tmp, site, site), cn=cn, commit=False)
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            vno_rows = db.query("SELECT MAX(VNo) FROM HallBook WITH (UPDLOCK, HOLDLOCK) WHERE LogSite_Code = ? AND Vprefix = ?", (site, vprefix), cn=cn)
            vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    else:
        vno_rows = db.query(
            "SELECT MAX(VNo) FROM HallBook WITH (UPDLOCK, HOLDLOCK) "
            "WHERE LogSite_Code = ? AND Vprefix = ?", (site, vprefix), cn=cn)
        if not vno_rows or vno_rows[0][0] is None:
            vno_rows = db.query(
                "SELECT MAX(VNo) FROM HallBook WITH (UPDLOCK, HOLDLOCK) "
                "WHERE Site_Code = ? AND Vprefix = ?", (site, vprefix), cn=cn)
        vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    docid = ("D" + site.ljust(2) + "HB".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO HallBook (DocId,Vtype,VNo,VTime,Site_Code,Vprefix,Vdate,PartyName,Add1,Add2,City,Func_Name,BookingStatus,RestCode,FrBookDate,FrBookTime,ToBookDate,ToBookTime,Total,DiscPer,DiscAmt,NonTaxable,Taxable,Tax,ServiceCharge,AddAmt,DedAmt,RoundOff,U_Name,U_EntDt,U_AE,HallRent,Remarks,Advance,NetAmount,LogSite_Code,BookingAgent)"
        " VALUES (?,'HB',?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?)",
        (docid, vno, rec.get("vtime", ""), site, vprefix,
         rec.get("partyname", ""), rec.get("add1", ""), rec.get("add2", ""),
         rec.get("city", ""), rec.get("func_name", ""),
         rec.get("bookingstatus", "Confirm"), rec.get("restcode", ""),
         rec.get("frbookdate"), rec.get("frbooktime", ""),
         rec.get("tobookdate"), rec.get("tobooktime", ""),
         rec.get("total", 0.0), rec.get("discper", 0.0), rec.get("discamt", 0.0),
         rec.get("nontaxable", 0.0), rec.get("taxable", 0.0), rec.get("tax", 0.0),
         rec.get("servicecharge", 0.0), rec.get("addamt", 0.0), rec.get("dedamt", 0.0),
         rec.get("roundoff", 0.0), user,
         rec.get("hallrent", 0.0), rec.get("remarks", ""),
         rec.get("advance", 0.0), rec.get("netamount", 0.0),
         site, rec.get("bookingagent", "")),
        cn=cn, commit=commit)
    return get_hallbook(vno, site=site, cn=cn, vprefix=vprefix)


def update_hallbook(vno, rec, cn=None, commit=True, site=SITE_CODE, user=USER, vprefix="2026"):
    _validate_hallbook(rec)
    sets, params = [], []
    for fld in ("PartyName","Add1","Add2","City","Func_Name","BookingStatus","RestCode",
                "FrBookDate","FrBookTime","ToBookDate","ToBookTime","Total","DiscPer",
                "DiscAmt","NonTaxable","Taxable","Tax","ServiceCharge","AddAmt","DedAmt",
                "RoundOff","HallRent","Remarks","Advance","NetAmount","BookingAgent"):
        key = fld.lower()
        if key in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[key])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, site, vno, vprefix])
    db.execute("UPDATE HallBook SET " + ", ".join(sets) +
               " WHERE Site_Code = ? AND VNo = ? AND Vprefix = ?"
               " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
               params + [site], cn=cn, commit=commit)
    return get_hallbook(vno, site=site, cn=cn, vprefix=vprefix)


def delete_hallbook(vno, cn=None, commit=True, site=SITE_CODE, vprefix="2026"):
    return db.execute(
        "DELETE FROM HallBook WHERE Site_Code = ? AND VNo = ? AND Vprefix = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (site, vno, vprefix, site), cn=cn, commit=commit)


# === HallBook1 (hall items) ===
def _map_hallbook1(r) -> dict:
    try:
        return {"docid": r.DocId or "", "sno": r.Sno or 0, "vtype": r.Vtype or "",
                "vno": r.VNo or 0, "site_code": r.Site_Code or "", "item": r.Item or "",
                "qtyiss": r.QtyIss or 0.0, "rate": r.Rate or 0.0, "amount": r.Amount or 0.0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[1] or 0}


def list_hallbook1(docid, cn=None):
    rows = db.query(
        "SELECT * FROM HallBook1 WHERE DocId = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')"
        " ORDER BY Sno", (docid, SITE_CODE), cn=cn)
    return [_map_hallbook1(r) for r in rows]


def insert_hallbook1(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM HallBook1 WHERE DocId = ?", (rec.get("docid", ""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO HallBook1 (DocId,Sno,Vtype,VNo,Site_Code,Vprefix,Vdate,PartyCode,RestCode,RoomCat,RoomType,RoomNo,Item,QtyIss,Unit,Rate,Amount,TaxPer,TaxAmt,DiscPer,DiscAmt,VoidYN,Remarks,U_Name,U_EntDt,U_AE,LogSite_Code)"
        " VALUES (?,?,?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'',?,getdate(),'A',?)",
        (rec.get("docid",""), sno, rec.get("vtype","HB"), rec.get("vno",0), site, rec.get("vprefix","2026"),
         rec.get("partycode",""), rec.get("restcode",""), rec.get("roomcat",""), rec.get("roomtype",""),
         rec.get("roomno",""), rec.get("item",""), rec.get("qtyiss",0.0), rec.get("unit",""),
         rec.get("rate",0.0), rec.get("amount",0.0), rec.get("taxper",0.0), rec.get("taxamt",0.0),
         rec.get("discper",0.0), rec.get("discamt",0.0), rec.get("remarks",""), user, site),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_hallbook1(docid, sno, cn=None, commit=True):
    return db.execute(
        "DELETE FROM HallBook1 WHERE DocId = ? AND Sno = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (docid, sno, SITE_CODE), cn=cn, commit=commit)


# === HallSale1 (hall sale billing) ===
def _map_hallsale1(r) -> dict:
    try:
        return {"docid": r.DocId or "", "vtype": r.Vtype or "", "vno": r.VNo or 0,
                "vtime": r.VTime or "", "site_code": r.Site_Code or "",
                "vprefix": r.Vprefix or "", "vdate": r.Vdate, "party": r.Party or "",
                "total": r.Total or 0.0, "netamt": r.NetAmt or 0.0, "remarks": r.Remarks or "",
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "vno": r[2] or 0}


def list_hallsale1(cn=None, limit=500):
    rows = db.query(
        f"SELECT TOP {int(limit)} * FROM HallSale1"
        " WHERE (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')"
        " ORDER BY VNo DESC", (SITE_CODE,), cn=cn)
    return [_map_hallsale1(r) for r in rows]


def get_hallsale1(vno, site=SITE_CODE, cn=None):
    rows = db.query(
        "SELECT * FROM HallSale1 WHERE Site_Code = ? AND VNo = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (site, vno, SITE_CODE), cn=cn)
    return _map_hallsale1(rows[0]) if rows else None


def insert_hallsale1(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # BUG-015: race-safe VNo (UPDLOCK/HOLDLOCK)
    vno_rows = db.query(
        "SELECT MAX(VNo) FROM HallSale1 WITH (UPDLOCK, HOLDLOCK) "
        "WHERE LogSite_Code = ?", (site,), cn=cn)
    vno = (vno_rows[0][0] or 0) + 1 if vno_rows and vno_rows[0][0] else 1
    vprefix = rec.get("vprefix", "2026")
    docid = ("D" + site.ljust(2) + "HS".ljust(6) + str(vprefix).ljust(4) + str(vno).rjust(8))[:21]
    db.execute(
        "INSERT INTO HallSale1 (DocId,Vtype,VNo,VTime,Site_Code,Vprefix,Vdate,RestCode,Party,Total,DiscPer,DiscAmt,NonTaxable,Taxable,Tax,ServiceCharge,AddAmt,DedAmt,RoundOff,NetAmt,FrBookDate,FrBookTime,U_Name,U_EntDt,U_AE,ToBookDate,ToBookTime,HallRent,Remarks,NoOfPax,RatePerPax,TotalPerCover,Amount,Advance,RectNo,rectDate,CrCardNo,CrCardHolder,BookDocId,DelFlag,Narration,LogSite_Code,Narration1,CGST,SGST,IGST)"
        " VALUES (?,'HS',?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?,?,?,?,?,?,NULL,'','',?,'N','',?,?,?,?,?)",
        (docid, vno, rec.get("vtime",""), site, vprefix,
         rec.get("restcode",""), rec.get("party",""), rec.get("total",0.0),
         rec.get("discper",0.0), rec.get("discamt",0.0), rec.get("nontaxable",0.0),
         rec.get("taxable",0.0), rec.get("tax",0.0), rec.get("servicecharge",0.0),
         rec.get("addamt",0.0), rec.get("dedamt",0.0), rec.get("roundoff",0.0),
         rec.get("netamt",0.0), rec.get("frbookdate"), rec.get("frbooktime",""),
         user,
         rec.get("tobookdate"), rec.get("tobooktime",""), rec.get("hallrent",0.0),
         rec.get("remarks",""), rec.get("noofpax",0), rec.get("rateperpax",0.0),
         rec.get("totalpercover",0.0), rec.get("amount",0.0), rec.get("advance",0.0),
         rec.get("rectno",0), rec.get("bookdocid",""), site,
         rec.get("narration1",""), rec.get("cgst",0.0), rec.get("sgst",0.0), rec.get("igst",0.0)),
        cn=cn, commit=commit)
    return get_hallsale1(vno, site=site, cn=cn)


def update_hallsale1(vno, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sets, params = [], []
    for fld in ("Party","RestCode","Total","DiscPer","DiscAmt","NonTaxable","Taxable","Tax",
                "ServiceCharge","AddAmt","DedAmt","RoundOff","NetAmt","HallRent","Remarks",
                "NoOfPax","RatePerPax","Narration"):
        if fld.lower() in rec:
            sets.append(f"{fld} = ?")
            params.append(rec[fld.lower()])
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets.extend(["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"])
    params.extend([user, site, vno])
    db.execute("UPDATE HallSale1 SET " + ", ".join(sets) +
               " WHERE Site_Code = ? AND VNo = ?"
               " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
               params + [SITE_CODE], cn=cn, commit=commit)
    return get_hallsale1(vno, site=site, cn=cn)


def delete_hallsale1(vno, cn=None, commit=True, site=SITE_CODE):
    return db.execute(
        "DELETE FROM HallSale1 WHERE Site_Code = ? AND VNo = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (site, vno, SITE_CODE), cn=cn, commit=commit)


# === HallStock ===
def _map_hallstock(r) -> dict:
    try:
        return {"docid": r.DocId or "", "sno": r.Sno or 0, "vtype": r.Vtype or "",
                "vno": r.VNo or 0, "site_code": r.Site_Code or "", "item": r.Item or "",
                "qtyiss": r.QtyIss or 0.0, "rate": r.Rate or 0.0, "amount": r.Amount or 0.0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or "", "voidyn": r.VoidYN or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[1] or 0}


def list_hallstock(cn=None, limit=500):
    rows = db.query(
        f"SELECT TOP {int(limit)} * FROM HallStock"
        " WHERE (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')"
        " ORDER BY DocId DESC", (SITE_CODE,), cn=cn)
    return [_map_hallstock(r) for r in rows]


def insert_hallstock(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM HallStock WHERE DocId = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO HallStock (DocId,Sno,Vtype,VNo,Site_Code,Vprefix,Vdate,Party,RestCode,ContraDocId,ContraSno,Item,QtyIss,Unit,Rate,Amount,TaxPer,TaxAmt,DiscPer,DiscAmt,VoidYN,Remarks,U_Name,U_EntDt,U_AE,Total,DiscApp,RoundOff,DepartCode,GodCode,DelFlag,LogSite_Code,SChrgApp,SChrgPer,SChrgAmt)"
        " VALUES (?,?,?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,?,?,?,'',?,?,getdate(),'A',?,?,?,?,?,'N',?,?,?,?)",
        (rec.get("docid",""), sno, rec.get("vtype",""), rec.get("vno",0), site,
         rec.get("vprefix",""), rec.get("party",""), rec.get("restcode",""),
         rec.get("contradocid",""), rec.get("contrasno",0), rec.get("item",""),
         rec.get("qtyiss",0.0), rec.get("unit",""), rec.get("rate",0.0),
         rec.get("amount",0.0), rec.get("taxper",0.0), rec.get("taxamt",0.0),
         rec.get("discper",0.0), rec.get("discamt",0.0),
         rec.get("remarks",""), user,
         rec.get("total",0.0), rec.get("discapp",0.0), rec.get("roundoff",0.0),
         rec.get("departcode",""), rec.get("godcode",""), site,
         rec.get("schrgapp","").strip(), rec.get("schrgper",0.0), rec.get("schrgamt",0.0)),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_hallstock(docid, sno, cn=None, commit=True):
    return db.execute(
        "DELETE FROM HallStock WHERE DocId = ? AND Sno = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (docid, sno, SITE_CODE), cn=cn, commit=commit)


# === PayChargeH (hall payments) ===
def _map_pchargeh(r) -> dict:
    try:
        return {"docid": r.DocId or "", "sno": r.SNo or 0, "vtype": r.Vtype or "",
                "vno": r.VNo or 0, "site_code": r.Site_Code or "",
                "paycode": r.PayCode or "", "paytype": r.PayType or "",
                "amtcr": r.AmtCr or 0.0, "amtdr": r.AmtDr or 0.0,
                "restcode": r.RestCode or "", "billamount": r.BillAmount or 0.0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[1] or 0}


def list_pchargeh(cn=None, limit=500):
    rows = db.query(
        f"SELECT TOP {int(limit)} * FROM PayChargeH"
        " WHERE (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')"
        " ORDER BY DocId DESC", (SITE_CODE,), cn=cn)
    return [_map_pchargeh(r) for r in rows]


def insert_pchargeh(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(SNo) FROM PayChargeH WHERE DocId = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO PayChargeH (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,EmpCode,CompCode,Comments,PayCode,PayType,AmtCr,AmtDr,TipAmt,RoomCat,RoomType,RoomNo,FPNo,CardNo,CardHolder,ChqNo,ChqDate,ExpDate,BookNo,BookType,U_Name,U_EntDt,U_AE,RestCode,BillAmount,ContraDocID,DbtChkIn,TaxPer,OnAmt,Bill_No,MarkEntry,ModeSet,SettleDate,BatchNo,PostDocId,LogSite_Code,TaxStru,TxnNo)"
        " VALUES (?,?,?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (rec.get("docid",""), sno, rec.get("vtype",""), rec.get("vno",0), site,
         rec.get("vprefix",""), rec.get("vtime",""), rec.get("guestprof",""),
         rec.get("empcode",""), rec.get("compcode",""), rec.get("comments",""),
         rec.get("paycode",""), rec.get("paytype",""),
         rec.get("amtcr",0.0), rec.get("amtdr",0.0), rec.get("tipamt",0.0),
         rec.get("roomcat",""), rec.get("roomtype",""), rec.get("roomno",""),
         rec.get("fpno",""), rec.get("cardno",""), rec.get("cardholder",""),
         rec.get("chqno",""), rec.get("chqdate"), rec.get("expdate"),
         rec.get("bookno",""), rec.get("booktype",""), user,
         rec.get("restcode",""), rec.get("billamount",0.0), rec.get("contradocid",""),
         rec.get("dbtchkin",""), rec.get("taxper",0.0), rec.get("onamt",0.0),
         rec.get("bill_no",""), rec.get("markentry",""), rec.get("modeset",""),
         rec.get("settledate"), rec.get("batchno",""), rec.get("postdocid",""),
         site, rec.get("taxstru",""), rec.get("txnno","")),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_pchargeh(docid, sno, cn=None, commit=True):
    return db.execute(
        "DELETE FROM PayChargeH WHERE DocId = ? AND SNo = ?"
        " AND (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')",
        (docid, sno, SITE_CODE), cn=cn, commit=commit)


# === SunTranH ===
def _map_suntranH(r) -> dict:
    try:
        return {"docid": r.DocId or "", "sno": r.Sno or 0, "vtype": r.Vtype or "",
                "vno": r.VNo or 0, "site_code": getattr(r, "SiteCode", "") or r.Site_Code or "",
                "partycode": r.PartyCode or "", "suncode": r.SunCode or "",
                "amount": r.Amount or 0.0, "baseamount": r.BaseAmount or 0.0,
                "svalue": r.SValue or 0.0, "roff": r.ROff or 0.0,
                "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"docid": str(r[0] or ""), "sno": r[1] or 0}


def list_suntranH(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM SunTranH WHERE LogSite_Code = ? ORDER BY DocId DESC", (SITE_CODE,), cn=cn)
    return [_map_suntranH(r) for r in rows]


def insert_suntranH(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    sno_rows = db.query("SELECT MAX(Sno) FROM SunTranH WHERE DocId = ?", (rec.get("docid",""),), cn=cn)
    sno = (sno_rows[0][0] or 0) + 1 if sno_rows and sno_rows[0][0] else 1
    db.execute(
        "INSERT INTO SunTranH (DocId,Sno,Vtype,VNo,Vdate,PartyCode,SunCode,Limit,DispName,ROff,CalcFormula,SValue,Amount,BaseAmount,U_Name,U_EntDt,U_AE,SunAppDate,RevCode,RestCode,DelFlag,SiteCode,LogSite_Code)"
        " VALUES (?,?,?,?,getdate(),?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?)",
        (rec.get("docid",""), sno, rec.get("vtype",""), rec.get("vno",0),
         rec.get("partycode",""), rec.get("suncode",""), rec.get("limit",0.0),
         rec.get("dispname",""), rec.get("roff",0.0), rec.get("calcformula",""),
         rec.get("svalue",0.0), rec.get("amount",0.0), rec.get("baseamount",0.0),
         user, rec.get("sunappdate"), rec.get("revcode",""), rec.get("restcode",""),
         rec.get("delflag","N"), site, site),
        cn=cn, commit=commit)
    return {"docid": rec.get("docid",""), "sno": sno}


def delete_suntranH(docid, sno, cn=None, commit=True):
    return db.execute("DELETE FROM SunTranH WHERE DocId = ? AND Sno = ?", (docid, sno), cn=cn, commit=commit)


class HallBookingAPI:
    def list_all_hallbook(self, cn=None, limit=500): return list_all_hallbook(cn, limit)
    def get_hallbook(self, vno, site=SITE_CODE, cn=None, vprefix="2026"): return get_hallbook(vno, site, cn, vprefix)
    def search_hallbook(self, term, site=SITE_CODE, cn=None, limit=100): return search_hallbook(term, site, cn, limit)
    def insert_hallbook(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_hallbook(rec, cn, commit, site, user)
    def update_hallbook(self, vno, rec, cn=None, commit=True, site=SITE_CODE, user=USER, vprefix="2026"): return update_hallbook(vno, rec, cn, commit, site, user, vprefix)
    def delete_hallbook(self, vno, cn=None, commit=True, site=SITE_CODE, vprefix="2026"): return delete_hallbook(vno, cn, commit, site, vprefix)
    def list_hallbook1(self, docid, cn=None): return list_hallbook1(docid, cn)
    def insert_hallbook1(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_hallbook1(rec, cn, commit, site, user)
    def delete_hallbook1(self, docid, sno, cn=None, commit=True): return delete_hallbook1(docid, sno, cn, commit)
    def list_hallsale1(self, cn=None, limit=500): return list_hallsale1(cn, limit)
    def get_hallsale1(self, vno, site=SITE_CODE, cn=None): return get_hallsale1(vno, site, cn)
    def insert_hallsale1(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_hallsale1(rec, cn, commit, site, user)
    def update_hallsale1(self, vno, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return update_hallsale1(vno, rec, cn, commit, site, user)
    def delete_hallsale1(self, vno, cn=None, commit=True, site=SITE_CODE): return delete_hallsale1(vno, cn, commit, site)
    def list_hallstock(self, cn=None, limit=500): return list_hallstock(cn, limit)
    def insert_hallstock(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_hallstock(rec, cn, commit, site, user)
    def delete_hallstock(self, docid, sno, cn=None, commit=True): return delete_hallstock(docid, sno, cn, commit)
    def list_pchargeh(self, cn=None, limit=500): return list_pchargeh(cn, limit)
    def insert_pchargeh(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_pchargeh(rec, cn, commit, site, user)
    def delete_pchargeh(self, docid, sno, cn=None, commit=True): return delete_pchargeh(docid, sno, cn, commit)
    def list_suntranH(self, cn=None, limit=500): return list_suntranH(cn, limit)
    def insert_suntranH(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_suntranH(rec, cn, commit, site, user)
    def delete_suntranH(self, docid, sno, cn=None, commit=True): return delete_suntranH(docid, sno, cn, commit)