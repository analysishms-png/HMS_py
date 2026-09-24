# P0 FIX HO+LOGSITE (VB6 parity) - 2026-09-24 via multi-agent compare
"""Inventory core (P5): Godown master CRUD + Indent/Purchase/Stock documents.

EVIDENCE (live):
- GodownMast 64 rows: Code varchar(6) PK, Name varchar(25), ShortName(6),
  DepartCode(6) FK, SysYn(1), audit cols.
- Indent 959 rows: DocId 'DKKRQ    2026     895' (Vtype RQ), VNo, VDate,
  Department (outlet), ClearYN flag, Godown. Lines NOT in separate table
  (Stock.IndentDocId all empty) -> header browse only.
- Purchase: GIN Vtype='MRCR' (421 docs) - PartyName header + Purch2 lines.
- Purchase Order: POrder Vtype='PORD' (6 docs) + POrder1 lines.
- Purchase Bill: Purch2 Vtype='PBPB' (394 docs) - linked to GIN via ContraDocId.
- Stock: Vtypes: BMM (KOT), RQI (Issue), RQR (Receive), BKREC (Store Receive),
  PBPB (Purchase Bill), RQ (Indent?).
- Stock balance: Sum(QtyRec - QtyIss) per Godown+Item (Stock Register base).
Writes: Godown master CRUD + Indent/Purchase/Stock document entry.
VB6 patterns: PIndent, pMREntry, pPOrder, pPBill, pReqSlip, RsStoreRecEntry, pGIss, kClStk.
"""
from __future__ import annotations

from datetime import date, datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
LOGSITE_CODE = db.get_logsite()
USER = db.get_user()
LIMITS = {"code": 6, "name": 25, "short": 6, "depart": 6}
SELECT_COLS = ("Code, Name, ShortName, DepartCode, SysYn, "
               "U_Name, U_EntDt, U_AE")


# ============================================================
# Item Category Grouping (VB6 pattern: RICE, OIL, WHISKY, SUGAR, ATTA, TEA, WINE, VODKA, FRUIT, OTHER)
# Used by KitchenStkRep, StockRegister, RStockRegister, etc.
# ============================================================
ITEM_CATEGORIES = (
    ("RICE%", "RICE"),
    ("OIL%", "OIL"),
    ("WHKY%", "WHISKY"),
    ("SUGR%", "SUGAR"),
    ("ATTA%", "ATTA"),
    ("TEA%", "TEA"),
    ("WINE%", "WINE"),
    ("VODKA%", "VODKA"),
    ("FRT%", "FRUIT"),
)


def get_item_category(item_code: str) -> str:
    """Map item code to VB6 category group.
    Returns: RICE, OIL, WHISKY, SUGAR, ATTA, TEA, WINE, VODKA, FRUIT, or OTHER
    """
    item_upper = (item_code or "").upper()
    for pattern, cat in ITEM_CATEGORIES:
        if item_upper.startswith(pattern.rstrip("%")):
            return cat
    return "OTHER"


def item_category_case_sql(col: str = "S.Item") -> str:
    """Return SQL CASE expression for item categorization (VB6 compatible).
    Usage: SELECT ..., item_category_case_sql() AS GrpName FROM Stock S ...
    """
    cases = " ".join(f"WHEN {col} LIKE '{p}' THEN '{c}'" for p, c in ITEM_CATEGORIES)
    return f"CASE {cases} ELSE 'OTHER' END"


# ============================================================
# Godown master (CRUD)
# ============================================================
def _map_godown(r) -> dict:
    return {"code": r.Code, "name": (r.Name or "").strip(),
            "short": (r.ShortName or "").strip(),
            "depart": r.DepartCode or "", "sysyn": r.SysYn or "",
            "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}


def _validate_godown(rec: dict):
    if not rec.get("code", "").strip():
        raise ValueError("Code zaroori hai")
    if len(rec["code"]) > LIMITS["code"]:
        raise ValueError(f"Code max {LIMITS['code']} chars")
    if not rec.get("name", "").strip():
        raise ValueError("Name zaroori hai")
    if len(rec["name"]) > LIMITS["name"]:
        raise ValueError(f"Name max {LIMITS['name']} chars")
    if len(rec.get("depart", "")) > LIMITS["depart"]:
        raise ValueError(f"depart max {LIMITS['depart']} chars")


def godown_list(cn=None, logsite: str | None = None) -> list[dict]:
    """VB6 Godown.frm browse: (LOGSITE_CODE='cur' OR 'HO') AND (SysYN<>'Y' OR NULL)."""
    ls = (logsite or db.get_logsite())[:2].upper()
    rows = db.query(
        f"SELECT {SELECT_COLS} FROM GodownMast "
        "WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO') AND (SysYN <> 'Y' OR SysYN IS NULL) "
        "ORDER BY Name", (ls,), cn=cn)
    # Fallback if no rows (HO-only DB) — return all non-sys to avoid empty
    if not rows:
        try:
            rows = db.query(f"SELECT {SELECT_COLS} FROM GodownMast WHERE (SysYN <> 'Y' OR SysYN IS NULL) ORDER BY Name", cn=cn)
        except Exception:
            rows = db.query(f"SELECT {SELECT_COLS} FROM GodownMast ORDER BY Code", cn=cn)
    return [_map_godown(r) for r in rows]


def godown_list_all(cn=None) -> list[dict]:
    """Unfiltered (internal/tests)."""
    rows = db.query(f"SELECT {SELECT_COLS} FROM GodownMast ORDER BY Code", cn=cn)
    return [_map_godown(r) for r in rows]


def godown_get(code: str, cn=None) -> dict | None:
    rows = db.query(f"SELECT {SELECT_COLS} FROM GodownMast WHERE Code = ?", (code,), cn=cn)
    return _map_godown(rows[0]) if rows else None


def godown_exists(code: str, cn=None) -> bool:
    return bool(db.query("SELECT 1 FROM GodownMast WHERE Code = ?", (code,), cn=cn))


def _godown_dup_check(name: str, short: str, cn=None, exclude_code: str | None = None):
    """VB6 duplicate guard: Name/ShortName must be unique (Godown.frm)."""
    if name:
        sql = "SELECT COUNT(*) FROM GodownMast WHERE Name = ?"
        params = [name.strip()]
        if exclude_code:
            sql += " AND Code <> ?"
            params.append(exclude_code)
        try:
            rows = db.query(sql, tuple(params), cn=cn)
            if rows and int(rows[0][0] or 0) > 0:
                raise ValueError(f"Godown Name '{name}' already exists")
        except ValueError:
            raise
        except Exception:
            pass
    if short:
        sql = "SELECT COUNT(*) FROM GodownMast WHERE ShortName = ?"
        params = [short.strip()]
        if exclude_code:
            sql += " AND Code <> ?"
            params.append(exclude_code)
        try:
            rows = db.query(sql, tuple(params), cn=cn)
            if rows and int(rows[0][0] or 0) > 0:
                raise ValueError(f"Godown ShortName '{short}' already exists")
        except ValueError:
            raise
        except Exception:
            pass


def godown_insert(rec: dict, cn=None, commit: bool = True) -> int:
    _validate_godown(rec)
    _godown_dup_check(rec.get("name",""), rec.get("short",""), cn=cn)
    ls = db.get_logsite()
    return db.execute(
        "INSERT INTO GodownMast (Code, Name, ShortName, DepartCode, "
        "SysYn, U_Name, U_EntDt, U_AE, Site_Code, LogSite_Code) "
        "VALUES (?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?)",
        (rec["code"], rec["name"], rec.get("short", ""),
         rec.get("depart", ""), rec.get("sysyn", "N"), USER,
         SITE_CODE, ls), cn=cn, commit=commit)


def godown_update(code: str, rec: dict, cn=None, commit: bool = True) -> int:
    _validate_godown(rec)
    _godown_dup_check(rec.get("name",""), rec.get("short",""), cn=cn, exclude_code=code)
    return db.execute(
        "UPDATE GodownMast SET Name = ?, ShortName = ?, DepartCode = ?, "
        "SysYn = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' WHERE Code = ?",
        (rec["name"], rec.get("short", ""), rec.get("depart", ""),
         rec.get("sysyn", "N"), USER, code), cn=cn, commit=commit)


def godown_delete(code: str, cn=None, commit: bool = True) -> int:
    return db.execute("DELETE FROM GodownMast WHERE Code = ?", (code,), cn=cn, commit=commit)


# ============================================================
# Document numbering helpers
# ============================================================
def _make_docid(vtype: str, vprefix: str, vno: int, site: str | None = None) -> str:
    """'D'+site(2)+vtype.ljust(6)+vprefix(4)+VNo.rjust(8) = 21 char — VB6 canonical no slice."""
    s = (site or SITE_CODE)[:2].upper()
    return "D" + s + vtype.ljust(6)[:6] + vprefix.ljust(4)[:4] + str(vno).rjust(8)


def _next_vno(vtype: str, vprefix: str, cn=None, vdate=None) -> int:
    # P0 #3: Voucher_Prefix window + LogSite_Code
    return db.next_vno("Stock", vtype, vprefix, site=SITE_CODE, cn=cn, vdate=vdate, logsite=db.get_logsite())


def _next_vno_table(table: str, vtype: str, vprefix: str, cn=None, vdate=None) -> int:
    """For tables with their own VNo sequence (GIN, POrder, etc.). P0 #3 adds LogSite_Code + prefix window."""
    vtype_col = "Vtype" if table == "Stock" else "VType"
    return db.next_vno(table, vtype, vprefix, site=SITE_CODE,
                       vtype_col=vtype_col, cn=cn, vdate=vdate, logsite=db.get_logsite())


# ---- VB6 master helpers (HO fallback) ----

def item_lookup_store(cn=None, logsite: str | None = None) -> list:
    """VB6 PIndent/pPOrder Item lookup: (LOGSITE_CODE='cur' OR 'HO') AND ItemType='Store'."""
    ls = (logsite or db.get_logsite())[:2].upper()
    try:
        rows = db.query(
            "SELECT I.Code,I.Name as Name,I.Unit,I.PurchRate as Rate,I.LPurRate,"
            " I.ConvRatio as ConvFactor,I.IssueUnit as WtUnit,IC.taxStru "
            "FROM ItemMast I INNER JOIN ItemCatMast IC ON I.ItemCatCode=IC.Code "
            "WHERE (I.LOGSITE_CODE=? OR I.LOGSITE_CODE='HO') AND I.ItemType='Store' AND I.ActiveYN<>'No' ORDER BY I.Name",
            (ls,), cn=cn)
        return rows
    except Exception:
        return db.query("SELECT Code, Name, Unit FROM ItemMast WHERE ItemType='Store' ORDER BY Name", cn=cn)


def depart_lookup_store(cn=None, logsite: str | None = None) -> list:
    """VB6 Depart combo: (LOGSITE_CODE='cur' OR 'HO') AND RestType='Store'."""
    ls = (logsite or db.get_logsite())[:2].upper()
    try:
        return db.query(
            "SELECT Code,Name,Code as DCode,RestType FROM Depart "
            "WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO') AND RestType='Store' AND RestType<>'FOM' AND OutletYn='N' ORDER BY Name",
            (ls,), cn=cn)
    except Exception:
        return db.query("SELECT Code, Name FROM Depart ORDER BY Name", cn=cn)


def subgroup_lookup_supplier(cn=None, logsite: str | None = None) -> list:
    """VB6 SubGroup supplier: (LOGSITE_CODE='cur' OR 'HO') AND Nature='Supplier'."""
    ls = (logsite or db.get_logsite())[:2].upper()
    try:
        return db.query(
            "SELECT SubCode As Code,Name,(Add1+' '+Add2) As Address,C.CityName "
            "FROM SubGroup LEFT JOIN City C ON SubGroup.CityCode=C.CityCode "
            "WHERE ActiveYN=1 AND (Subgroup.LOGSITE_CODE=? OR Subgroup.LOGSITE_CODE='HO') AND Nature IN ('Supplier') ORDER BY Name",
            (ls,), cn=cn)
    except Exception:
        return db.query("SELECT SubCode As Code, Name FROM SubGroup WHERE Nature='Supplier' ORDER BY Name", cn=cn)


def voucher_type_list(ncat: str, cn=None, logsite: str | None = None, site: str | None = None) -> list:
    """VB6 Voucher_Type picker: Site_Code + LogSite_Code + NCAT."""
    ls = (logsite or db.get_logsite())[:2].upper()
    s = (site or SITE_CODE)[:2].upper()
    return db.query(
        "SELECT V_Type,DESCRIPTION FROM Voucher_Type WHERE Site_Code=? and logsite_code=? and NCAT IN (?) ORDER BY DESCRIPTION",
        (s, ls, ncat), cn=cn)


# ============================================================
# Indent (Vtype='RQ') - header only (lines in Stock with IndentDocId/IndentSno)
# ============================================================
def indent_list(cn=None, vprefix: str = "2026", top: int = 200, logsite: str | None = None) -> list:
    """VB6 Indent browse: JOIN Voucher_Type ON Vtype+LogSite_Code WHERE V.LOGSITE_CODE=? AND V.NCAT='PIND'."""
    ls = (logsite or db.get_logsite())[:2].upper()
    try:
        rows = db.query(
            f"SELECT TOP {int(top)} I.DocId as SearchCode, I.VNo, I.VDate, I.Department, I.ClearYN, I.Godown, I.Remarks, I.Site_Code, I.LogSite_Code "
            f"FROM Indent I INNER JOIN Voucher_Type V ON (I.Vtype=V.V_Type AND I.LogSite_Code=V.LogSite_Code) "
            f"WHERE V.LOGSITE_CODE=? AND V.NCAT='PIND' AND I.Vprefix=? ORDER BY I.DocId",
            (ls, vprefix), cn=cn)
        return [{"docid": r.SearchCode if hasattr(r,'SearchCode') else r.DocId, "vno": r.VNo, "vdate": r.VDate,
                 "dept": r.Department or "", "clear": r.ClearYN or "",
                 "godown": r.Godown or ""} for r in rows]
    except Exception:
        rows = db.query(
            f"SELECT TOP {int(top)} DocId, VNo, VDate, Department, ClearYN, "
            "Godown FROM Indent WHERE LogSite_Code = ? AND Vprefix = ? "
            "ORDER BY VNo DESC", (ls, vprefix), cn=cn)
        return [{"docid": r.DocId, "vno": r.VNo, "vdate": r.VDate,
                 "dept": r.Department or "", "clear": r.ClearYN or "",
                 "godown": r.Godown or ""} for r in rows]


def indent_get(docid: str, cn=None) -> dict | None:
    rows = db.query("SELECT DocId, Vtype, VNo, Vprefix, VDate, Department, "
                    "Remarks, U_Name, U_AE, ClearYN, Godown, RefDocId "
                    "FROM Indent WHERE DocId = ?", (docid,), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {"docid": r[0], "vtype": r[1], "vno": r[2], "vprefix": r[3],
            "vdate": r[4], "dept": r[5] or "", "remarks": r[6] or "",
            "u_name": r[7] or "", "u_ae": r[8] or "",
            "clear": r[9] or "", "godown": r[10] or "", "ref_docid": r[11] or ""}


def indent_create(dept: str, vdate, godown: str, vprefix: str = "2026",
                   remarks: str = "", user: str = USER, cn=None, commit: bool = True) -> dict:
    """Create new Indent (VB6 PIndent 'Add' flow). P0: menuHelp + DateLock + Voucher_Prefix window + LogSite."""
    vdate = vdate or date.today()
    # P0 #4 menuHelp + #5 DateLock
    try:
        db.check_menuhelp("Indent", cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    try:
        db.check_datelock("Indent", vdate, cn=cn)
    except ValueError:
        raise
    except Exception:
        pass
    # P0 #3: prefix window determines effective Vprefix
    eff_prefix, _, _ = db.get_voucher_prefix("RQ", vdate, cn=cn, logsite=db.get_logsite(), site=SITE_CODE)
    use_prefix = eff_prefix or vprefix
    vno = _next_vno_table("Indent", "RQ", use_prefix, cn=cn, vdate=vdate)
    docid = _make_docid("RQ", use_prefix, vno)
    ls = db.get_logsite()
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "INSERT INTO Indent (DocId, Vtype, VNo, Site_Code, Vprefix, VDate, "
            "VTime, Department, Remarks, U_Name, U_EntDt, U_AE, ClearYN, "
            "LogSite_Code, Godown, RefDocId) "
            "VALUES (?, 'RQ', ?, ?, ?, ?, '08:00', ?, ?, ?, getdate(), 'A', 'N', ?, ?, '')",
            (docid, vno, SITE_CODE, use_prefix, vdate, dept, remarks, user,
             ls, godown), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno, "vprefix": use_prefix}
    finally:
        if own:
            cn.close()


def indent_update(docid: str, dept: str, vdate, godown: str,
                  remarks: str = "", clear: str = "N", user: str = USER,
                  cn=None, commit: bool = True) -> int:
    own = cn is None
    cn = cn or db.connect()
    try:
        n = db.execute(
            "UPDATE Indent SET Department = ?, VDate = ?, Godown = ?, "
            "Remarks = ?, ClearYN = ?, U_Name = ?, U_EntDt = getdate(), U_AE = 'E' "
            "WHERE DocId = ?",
            (dept, vdate, godown, remarks, clear, user, docid),
            cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
    finally:
        if own:
            cn.close()


def indent_delete(docid: str, cn=None, commit: bool = True) -> int:
    # Safety: only PYT* test indents
    if not docid.startswith("DKKRQ"):
        raise ValueError("Safety: sirf PYT* test indents delete ho sakte hain")
    return db.execute("DELETE FROM Indent WHERE DocId = ?", (docid,), cn=cn, commit=commit)


# ============================================================
# GIN / Purchase Receipt (Vtype='MRCR') - header + Purch2 lines
# ============================================================
def purchase_list(cn=None, vprefix: str = "2026", top: int = 200, logsite: str | None = None) -> list:
    """Purchase Register base: GIN MRCR docs. P0: LogSite strict."""
    ls = (logsite or db.get_logsite())[:2].upper()
    rows = db.query(
        f"SELECT TOP {int(top)} DocId, VNo, VDate, PartyName "
        "FROM GIN WHERE LogSite_Code = ? AND Vprefix = ? AND Vtype = 'MRCR' "
        "ORDER BY VNo DESC", (ls, vprefix), cn=cn)
    return [{"docid": r.DocId, "vno": r.VNo, "vdate": r.VDate,
             "party": (r.PartyName or "").strip()} for r in rows]


def gin_get(docid: str, cn=None) -> dict | None:
    """Get GIN header."""
    rows = db.query(
        "SELECT DocId, Vtype, VNo, Vprefix, VDate, PartyCode, PartyName, "
        "GodownCode, Remark, U_Name, U_AE, OCDocid, OCDate, POrdDocid, POrdDate "
        "FROM GIN WHERE DocId = ?", (docid,), cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {"docid": r[0], "vtype": r[1], "vno": r[2], "vprefix": r[3],
            "vdate": r[4], "party_code": r[5] or "", "party_name": (r[6] or "").strip(),
            "godown": r[7] or "", "remark": r[8] or "",
            "u_name": r[9] or "", "u_ae": r[10] or "",
            "oc_docid": r[11] or "", "oc_date": r[12],
            "pord_docid": r[13] or "", "pord_date": r[14]}


def gin_lines(docid: str, cn=None) -> list:
    """GIN lines from Purch2 (ContraDocId = GIN.DocId)."""
    rows = db.query(
        "SELECT Sno, Item, QtyRec, Unit, Rate, Amount, TaxPer, TaxAmt, "
        "DiscPer, DiscAmt, VoidYN, Remarks, GodownCode, ChalQty, RecdQty, "
        "AccQty, RejQty, IndentDocId, IndentSno, ItemRestCode "
        "FROM Purch2 WHERE ContraDocId = ? ORDER BY Sno", (docid,), cn=cn)
    return [{"sno": r[0], "item": r[1] or "", "qty_rec": r[2] or 0,
             "unit": r[3] or "", "rate": r[4] or 0, "amount": r[5] or 0,
             "tax_per": r[6] or 0, "tax_amt": r[7] or 0,
             "disc_per": r[8] or 0, "disc_amt": r[9] or 0,
             "void": r[10] or "", "remarks": r[11] or "",
             "godown": r[12] or "", "chal_qty": r[13] or 0,
             "recd_qty": r[14] or 0, "acc_qty": r[15] or 0,
             "rej_qty": r[16] or 0, "indent_docid": r[17] or "",
             "indent_sno": r[18] or 0, "item_rest_code": r[19] or ""} for r in rows]


def gin_create(party_code: str, party_name: str, godown: str, vdate,
                lines: list[dict], vprefix: str = "2026",
                user: str = USER, remark: str = "",
                cn=None, commit: bool = True) -> dict:
    """Create GIN (Purchase Receipt) with lines (VB6 pMREntry 'Add' flow). P0: DateLock + LogSite + prefix window."""
    if not lines:
        raise ValueError("At least one line required")
    vdate = vdate or date.today()
    try:
        db.check_datelock("M.R. Entry", vdate, cn=cn)
    except ValueError:
        raise
    except Exception:
        pass
    eff_prefix, _, _ = db.get_voucher_prefix("MRCR", vdate, cn=cn, logsite=db.get_logsite(), site=SITE_CODE)
    use_prefix = eff_prefix or vprefix
    vno = _next_vno_table("GIN", "MRCR", use_prefix, cn=cn, vdate=vdate)
    docid = _make_docid("MRCR", use_prefix, vno)
    
    own = cn is None
    cn = cn or db.connect()
    try:
        # Header - GIN table doesn't have VTime column
        party_name = party_name or ""
        ls = db.get_logsite()
        db.execute(
            "INSERT INTO GIN (DocId, Vtype, VNo, Site_Code, Vprefix, VDate, "
            "PartyCode, PartyName, GodownCode, Remark, U_Name, U_EntDt, U_AE, "
            "LogSite_Code) "
            "VALUES (?, 'MRCR', ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
            (docid, vno, SITE_CODE, use_prefix, vdate,
             party_code, party_name,
             godown, remark or "", user, ls),
            cn=cn, commit=False)
        
# Lines - insert into Purch2 with ContraDocId = GIN.DocId
        for i, line in enumerate(lines, 1):
            sno = i
            item = line.get("item", "")
            qty_rec = float(line.get("qty_rec") or 0)
            unit = line.get("unit", "")
            rate = float(line.get("rate") or 0)
            amount = float(line.get("amount") or 0)
            tax_per = float(line.get("tax_per") or 0)
            tax_amt = float(line.get("tax_amt") or 0)
            disc_per = float(line.get("disc_per") or 0)
            disc_amt = float(line.get("disc_amt") or 0)
            line_godown = line.get("godown", "")
            remarks = line.get("remarks", "")
            indent_docid = line.get("indent_docid", "")
            indent_sno = int(line.get("indent_sno") or 0)

            db.execute(
                "INSERT INTO Purch2 (DocId, Sno, Vtype, VNo, Site_Code, Vprefix, Vdate, "
                "PartyCode, Item, QtyIss, QtyRec, Unit, Rate, Amount, TaxPer, TaxAmt, DiscPer, DiscAmt, "
                "VoidYN, Remarks, ContraDocId, ContraSno, VTime, U_Name, U_EntDt, U_AE, "
                "GodCode, LogSite_Code) "
                "VALUES (?, ?, 'PBPB', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
                "'N', ?, ?, ?, '00:00', ?, getdate(), 'A', ?, ?)",
                (docid, sno, vno, SITE_CODE, use_prefix, vdate,
                 party_code, item, 0, qty_rec, unit, rate, amount,
                 tax_per, tax_amt, disc_per, disc_amt,
                 remarks, docid, sno,
                 user, line_godown, ls), cn=cn, commit=False)
        
        # Write Stock rows (VB6 pMREntry lines 216622-216638)
        for i, line in enumerate(lines, 1):
            qty_rec = float(line.get("qty_rec") or 0)
            rate = float(line.get("rate") or 0)
            amount = float(line.get("amount") or 0)
            item = line.get("item", "")
            godown_code = line.get("godown", godown)
            indent_docid = line.get("indent_docid", "")
            indent_sno = int(line.get("indent_sno") or 0)
            db.execute(
                "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, VPrefix, "
                "VDate, VTime, PartyCode, RestCode, RoomCat, RoomType, RoomNo, "
                "Item, QtyIss, QtyRec, Unit, Rate, Amount, U_Name, U_EntDt, "
                "U_AE, LogSite_Code, GodownCode, DelFlag, IndentDocId, IndentSNo) "
                "VALUES (?, ?, 'MRE', ?, ?, ?, ?, '00:00', '', '', '', '', "
                "?, ?, 0, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, 'N', ?, ?)",
                (docid, i, vno, SITE_CODE, use_prefix, vdate, "", item, qty_rec,
                 line.get("unit", ""), rate, amount, user, ls,
                 godown_code, indent_docid, indent_sno), cn=cn, commit=False)
            # ClearYN: mark linked indent lines as fulfilled
            if indent_docid and indent_sno:
                db.execute(
                    "UPDATE Indent1 SET ClearYN = 'Y' "
                    "WHERE DocId = ? AND Sno = ?",
                    (indent_docid, indent_sno), cn=cn, commit=False)
        
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno}
    finally:
        if own:
            cn.close()


# ============================================================
# Purchase Order (POrder + POrder1)
# ============================================================
def porder_list(cn=None, vprefix: str = "2026", top: int = 200, logsite: str | None = None) -> list:
    ls = (logsite or db.get_logsite())[:2].upper()
    rows = db.query(
        f"SELECT TOP {int(top)} DocId, VNo, VDate, PartyCode, Remark "
        "FROM POrder WHERE LogSite_Code = ? AND Vprefix = ? AND VType = 'PORD' "
        "ORDER BY VNo DESC", (ls, vprefix), cn=cn)
    return [{"docid": r[0], "vno": r[1], "vdate": r[2],
             "party_code": r[3] or "", "remark": r[4] or ""} for r in rows]


def porder_create(party_code: str, vdate, lines: list[dict],
                   vprefix: str = "2026", user: str = USER,
                   cn=None, commit: bool = True) -> dict:
    """Create Purchase Order (POrder + POrder1 lines). P0: menuHelp + DateLock + prefix window + LogSite."""
    if not lines:
        raise ValueError("At least one line required")
    if not party_code or not party_code.strip():
        raise ValueError("PartyCode zaroori hai")
    vdate = vdate or date.today()
    try:
        db.check_menuhelp("Purchase Order Entry", cn=cn)
    except PermissionError:
        raise
    except Exception:
        pass
    try:
        db.check_datelock("Purchase Order Entry", vdate, cn=cn)
    except ValueError:
        raise
    except Exception:
        pass
    eff_prefix, _, _ = db.get_voucher_prefix("PORD", vdate, cn=cn, logsite=db.get_logsite(), site=SITE_CODE)
    use_prefix = eff_prefix or vprefix
    vno = _next_vno_table("POrder", "PORD", use_prefix, cn=cn, vdate=vdate)
    docid = _make_docid("PORD", use_prefix, vno)
    ls = db.get_logsite()
    own = cn is None
    cn = cn or db.connect()
    try:
        db.execute(
            "INSERT INTO POrder (DocId, VNo, VDate, VType, VPrefix, Site_Code, "
            "PartyCode, U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, ?, 'PORD', ?, ?, ?, ?, getdate(), 'A', ?)",
            (docid, vno, vdate, use_prefix, SITE_CODE, party_code.strip(), USER, ls),
            cn=cn, commit=False)
        
        # Lines - use header party_code as default, allow line-level override
        header_party = party_code.strip()
        for i, line in enumerate(lines, 1):
            line_party = line.get("party_code", "").strip() or header_party
            db.execute(
                "INSERT INTO POrder1 (DocId, Sno, VNo, VDate, VType, VPrefix, Site_Code, "
                "PartyCode, ItemCode, Qty, Unit, Rate, PerUnit, Amount, U_Name, U_EntDt, "
                "U_AE, IndentDocId, IndentSno, Specification, ConvRatio, WtQty, WtUnit, "
                "LogSite_Code, TaxStru, TaxAmt, Total) "
                "VALUES (?, ?, ?, ?, 'PORD', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', "
                "?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (docid, i, vno, vdate, vprefix, SITE_CODE,
                 line_party, line["item"], line["qty"], line["unit"],
                 line["rate"], 0, line.get("amount", 0), USER,
                 line.get("indent_docid", ""), line.get("indent_sno", 0),
                 line.get("specification", ""), 1, 0, "",
                 SITE_CODE, line.get("tax_stru", ""), 0, line.get("amount", 0)),
                 cn=cn, commit=False)
        
        # ClearYN: mark linked indent lines as fulfilled
        for line in lines:
            indent_docid = line.get("indent_docid", "")
            indent_sno = int(line.get("indent_sno") or 0)
            if indent_docid and indent_sno:
                db.execute(
                    "UPDATE Indent1 SET ClearYN = 'Y' "
                    "WHERE DocId = ? AND Sno = ?",
                    (indent_docid, indent_sno), cn=cn, commit=False)
        
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno}
    finally:
        if own:
            cn.close()


def porder_delete(docid: str, cn=None, commit: bool = True) -> dict:
    """Delete Purchase Order and reverse ClearYN on linked indent lines."""
    own = cn is None
    cn = cn or db.connect()
    try:
        # Reverse ClearYN on linked indent lines (row-wise pairing)
        db.execute(
            "UPDATE Indent1 SET ClearYN = '' "
            "WHERE EXISTS ("
            "SELECT 1 FROM POrder1 p "
            "WHERE p.DocId = ? AND p.IndentDocId = Indent1.DocId "
            "AND ISNULL(p.IndentSno, 0) = Indent1.Sno)",
            (docid,), cn=cn, commit=False)
        # Delete POrder1 lines
        db.execute("DELETE FROM POrder1 WHERE DocId = ?", (docid,), cn=cn, commit=False)
        # Delete POrder header
        db.execute("DELETE FROM POrder WHERE DocId = ?", (docid,), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"deleted": docid}
    finally:
        if own:
            cn.close()


# ============================================================
# Stock Operations (Issue/Receive/Adjustment)
# ============================================================
VTYPES = {
    "issue": "RQI",      # Store Issue
    "receive": "RQR",    # Store Receive
    "adjust": "ADJ",     # Adjustment
    "bkrec": "BKREC",    # Store Receive (RsStoreRecEntry)
    "transfer": "BMTC",  # Stock transfer between godowns
}


def build_transfer_lines(item: str, from_godown: str, to_godown: str,
                        qty: float, unit: str = "", rate: float = 0,
                        amount: float | None = None,
                        remarks: str = "") -> list[dict]:
    """Build balanced pair for inter-godown transfer.

    Business meaning:
    - outgoing row: negative qty/amount from source godown
    - incoming row: positive qty/amount to destination godown
    - mapped to Stock rows with ContraDocId/ContraSno pair for VB6 traceability
    """
    if not item or not from_godown or not to_godown:
        raise ValueError("Item, from_godown and to_godown zaroori hain")
    if from_godown == to_godown:
        raise ValueError("Source and destination godown same nahi ho sakta")
    qty = float(qty or 0)
    if qty <= 0:
        raise ValueError("Qty > 0 hona chahiye")
    amt = float(amount) if amount is not None else (qty * float(rate or 0))
    base_note = remarks.strip()
    return [
        {
            "item": item,
            "godown": from_godown,
            "qty": -qty,
            "unit": unit,
            "rate": float(rate or 0),
            "amount": -amt,
            "remarks": f"{base_note} -> {to_godown}".strip(" -"),
        },
        {
            "item": item,
            "godown": to_godown,
            "qty": qty,
            "unit": unit,
            "rate": float(rate or 0),
            "amount": amt,
            "remarks": f"{base_note} from {from_godown}".strip(" -"),
        },
    ]


def stock_next_vno(vtype: str, vprefix: str = "2026", cn=None) -> int:
    return _next_vno(vtype, vprefix, cn)


def stock_transfer(item: str, from_godown: str, to_godown: str,
                   qty: float, unit: str = "", rate: float = 0,
                   amount: float | None = None, vdate=None,
                   vprefix: str = "2026", user: str = USER,
                   remarks: str = "", cn=None, commit: bool = True) -> dict:
    """Create a BMTC stock transfer pair between two godowns.

    Live DB pattern: same DocId, two Stock rows, paired with ContraDocId/ContraSno.
    """
    lines = build_transfer_lines(item, from_godown, to_godown, qty, unit, rate, amount, remarks)
    vdate = vdate or date.today()
    vtype = "BMTC"
    vno = stock_next_vno(vtype, vprefix, cn=cn)
    docid = _make_docid(vtype, vprefix, vno)
    vtime = datetime.now().strftime("%H:%M")
    own = cn is None
    cn = cn or db.connect()
    try:
        for i, line in enumerate(lines, 1):
            qty_val = float(line["qty"])
            qty_iss = abs(qty_val) if qty_val < 0 else 0
            qty_rec = abs(qty_val) if qty_val > 0 else 0
            contra_sno = 2 if qty_val < 0 else 1
            db.execute(
                "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, VPrefix, VDate, VTime, "
                "PartyCode, RestCode, RoomCat, RoomType, RoomNo, Item, QtyIss, QtyRec, "
                "Unit, Rate, Amount, U_Name, U_EntDt, U_AE, LogSite_Code, GodownCode, "
                "DelFlag, ContraDocId, ContraSno) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, 'N', ?, ?)",
                (docid, i, vtype, vno, SITE_CODE, vprefix, vdate, vtime,
                 "", "", "", "", "", line["item"], qty_iss, qty_rec,
                 line.get("unit", ""), line.get("rate", 0), abs(line.get("amount", 0)),
                 user, SITE_CODE, line["godown"], docid, contra_sno),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno, "vtype": vtype}
    finally:
        if own:
            cn.close()


def stock_create(vtype: str, lines: list[dict], vdate=None, vprefix: str = "2026",
                 user: str = USER, cn=None, commit: bool = True) -> dict:
    """Create Stock document (Issue/Receive/Adjustment).
    lines: [{"item", "godown", "qty", "unit", "rate", "amount", "remarks"}]
    For vtype='RQI' (Issue): QtyIss = qty, QtyRec = 0
    For vtype='RQR' (Receive): QtyIss = 0, QtyRec = qty
    For vtype='ADJ' (Adjust): QtyRec = max(qty,0), QtyIss = max(-qty,0)
    """
    if not lines:
        raise ValueError("At least one line required")
    
    vdate = vdate or date.today()
    vno = stock_next_vno(vtype, vprefix, cn=cn)
    docid = _make_docid(vtype, vprefix, vno)
    vtime = datetime.now().strftime("%H:%M")
    
    own = cn is None
    cn = cn or db.connect()
    try:
        for i, line in enumerate(lines, 1):
            qty = float(line.get("qty", 0))
            if vtype == "RQI":      # Issue
                qty_iss, qty_rec = qty, 0
            elif vtype == "RQR":    # Receive
                qty_iss, qty_rec = 0, qty
            else:                   # ADJ - positive = receive, negative = issue
                qty_iss, qty_rec = (0, qty) if qty >= 0 else (-qty, 0)
            
            db.execute(
                "INSERT INTO Stock (DocId, Sno, Vtype, VNo, Site_Code, VPrefix, VDate, VTime, "
                "PartyCode, RestCode, RoomCat, RoomType, RoomNo, Item, QtyIss, QtyRec, "
                "Unit, Rate, Amount, U_Name, U_EntDt, U_AE, LogSite_Code, GodownCode, "
                "DelFlag) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?, ?, 'N')",
                (docid, i, vtype, vno, SITE_CODE, vprefix, vdate, vtime,
                 "", "", "", "", "", line["item"], qty_iss, qty_rec,
                 line.get("unit", ""), line.get("rate", 0), line.get("amount", 0),
                 user, SITE_CODE, line["godown"]),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"docid": docid, "vno": vno, "vtype": vtype}
    finally:
        if own:
            cn.close()


def stock_issue(lines: list[dict], vdate=None, vprefix: str = "2026",
                user: str = USER, cn=None, commit: bool = True) -> dict:
    """Requisition Issue (Vtype='RQI'). lines: [{"item", "godown", "qty", "unit", "rate",
    "indent_docid", "indent_sno"}]"""
    own = cn is None
    cn = cn or db.connect()
    try:
        result = stock_create("RQI", lines, vdate, vprefix, user, cn, commit=False)
        # ClearYN: mark linked indent lines as fulfilled
        for line in lines:
            indent_docid = line.get("indent_docid", "")
            indent_sno = int(line.get("indent_sno") or 0)
            if indent_docid and indent_sno:
                db.execute(
                    "UPDATE Indent1 SET ClearYN = 'Y' "
                    "WHERE DocId = ? AND Sno = ?",
                    (indent_docid, indent_sno), cn=cn, commit=False)
        if commit:
            cn.commit()
        return result
    finally:
        if own:
            cn.close()


def stock_receive(lines: list[dict], vdate=None, vprefix: str = "2026",
                  user: str = USER, cn=None, commit: bool = True) -> dict:
    """Requisition Receive (Vtype='RQR'). lines: [{"item", "godown", "qty", "unit", "rate"}]"""
    return stock_create("RQR", lines, vdate, vprefix, user, cn, commit)


def kitchen_stock_issue(lines: list[dict], vdate=None, vprefix: str = "2026",
                        user: str = USER, cn=None, commit: bool = True) -> dict:
    """Kitchen Stock Issue (Vtype='KSISS', NCat='KSISS')."""
    return stock_create("KSISS", lines, vdate, vprefix, user, cn, commit)


def kitchen_stock_receive(lines: list[dict], vdate=None, vprefix: str = "2026",
                          user: str = USER, cn=None, commit: bool = True) -> dict:
    """Kitchen Stock Receive (Vtype='KSREC', NCat='KSREC')."""
    return stock_create("KSREC", lines, vdate, vprefix, user, cn, commit)


def kitchen_material_issue(lines: list[dict], vdate=None, vprefix: str = "2026",
                           user: str = USER, cn=None, commit: bool = True) -> dict:
    """Kitchen Material Issue (Vtype='KMISS', NCat='KMISS')."""
    return stock_create("KMISS", lines, vdate, vprefix, user, cn, commit)


def kitchen_material_receive(lines: list[dict], vdate=None, vprefix: str = "2026",
                             user: str = USER, cn=None, commit: bool = True) -> dict:
    """Kitchen Material Receive (Vtype='KMREC', NCat='KMREC')."""
    return stock_create("KMREC", lines, vdate, vprefix, user, cn, commit)


def bakery_stock_receive(lines: list[dict], vdate=None, vprefix: str = "2026",
                         user: str = USER, cn=None, commit: bool = True) -> dict:
    """Bakery Stock Receive (Vtype='BKREC', NCat='BKREC')."""
    return stock_create("BKREC", lines, vdate, vprefix, user, cn, commit)


# Vtype -> (description, direction) mapping for all stock issue/receipt types
STOCK_VTYPE_MAP = {
    "RQI": ("Requisition Issue", "issue"),
    "RQR": ("Requisition Receipt", "receive"),
    "KSISS": ("Kitchen Stock Issue", "issue"),
    "KSREC": ("Kitchen Stock Receive", "receive"),
    "KMISS": ("Kitchen Material Issue", "issue"),
    "KMREC": ("Kitchen Material Receive", "receive"),
    "BKREC": ("Bakery Stock Receive", "receive"),
    "MRE": ("M.R. Entry", "receive"),
    "STOP": ("Raw Item Opening Stock", "receive"),
}


def stock_adjust(lines: list[dict], vdate=None, vprefix: str = "2026",
                 user: str = USER, cn=None, commit: bool = True) -> dict:
    """Stock Adjustment (Vtype='ADJ'). lines: [{"item", "godown", "qty", "unit", "rate"}]
    Positive qty = increase stock, Negative = decrease."""
    return stock_create("ADJ", lines, vdate, vprefix, user, cn, commit)


def validate_stock_line(line: dict) -> None:
    """Validate a single stock line dict. Raises ValueError on invalid."""
    if not line.get("item", "").strip():
        raise ValueError("Item code zaroori hai")
    if not line.get("godown", "").strip():
        raise ValueError("Godown code zaroori hai")
    qty = line.get("qty", 0)
    try:
        qty = float(qty)
    except (ValueError, TypeError):
        raise ValueError("Qty numeric hona chahiye")
    if qty <= 0:
        raise ValueError("Qty positive honi chahiye")
    rate = line.get("rate", 0)
    try:
        float(rate)
    except (ValueError, TypeError):
        raise ValueError("Rate numeric hona chahiye")


def stock_movements(vtype: str = None, godown: str = None, item: str = None,
                    vprefix: str = "2026", cn=None, top: int = 200) -> list:
    """List stock movements filtered by vtype/godown/item."""
    sql = (f"SELECT TOP {int(top)} DocId, Sno, Vtype, VNo, VDate, Item, "
           "GodownCode, QtyIss, QtyRec, Rate, Amount, U_Name, VTime "
           "FROM Stock WHERE Site_Code = ? AND Vprefix = ? ")
    params: list = [SITE_CODE, vprefix]
    if vtype:
        sql += "AND Vtype = ? "
        params.append(vtype)
    if godown:
        sql += "AND GodownCode = ? "
        params.append(godown)
    if item:
        sql += "AND Item = ? "
        params.append(item)
    sql += "ORDER BY VDate DESC, DocId DESC"
    rows = db.query(sql, tuple(params), cn=cn)
    return [{"docid": r.DocId or "", "sno": r.Sno, "vtype": r.Vtype or "",
             "vno": r.VNo, "vdate": r.VDate, "item": r.Item or "",
             "godown": r.GodownCode or "",
             "qty_iss": float(r.QtyIss or 0), "qty_rec": float(r.QtyRec or 0),
             "rate": float(r.Rate or 0), "amount": float(r.Amount or 0),
             "user": r.U_Name or "", "vtime": r.VTime or ""} for r in rows]


# ============================================================
# Reports (read-only)
# ============================================================
def stock_balance(cn=None, vprefix: str = "2026", top: int = 50) -> list:
    """Stock Summary: Godown+Item balance (QtyRec - QtyIss)."""
    rows = db.query(
        f"SELECT TOP {int(top)} s.GodownCode, g.Name AS Godown, "
        "s.Item, i.Name AS ItemName, SUM(s.QtyRec - s.QtyIss) AS Bal "
        "FROM Stock s "
        "LEFT JOIN GodownMast g ON g.Code = s.GodownCode "
        "LEFT JOIN ItemMast i ON i.Code = s.Item "
        "WHERE s.Site_Code = ? AND s.Vprefix = ? "
        "GROUP BY s.GodownCode, g.Name, s.Item, i.Name "
        "HAVING SUM(s.QtyRec - s.QtyIss) > 0 "
        "ORDER BY SUM(s.QtyRec - s.QtyIss) DESC",
        (SITE_CODE, vprefix), cn=cn)
    return [{"godown": r.GodownCode or "",
             "godown_name": (r.Godown or "").strip(),
             "item": r.Item or "", "item_name": (r.ItemName or "").strip(),
             "bal": r.Bal or 0.0} for r in rows]


def stock_register(godown: str = None, item: str = None,
                   vprefix: str | None = None, cn=None, top: int = 200,
                   vdate_from=None, vdate_to=None) -> list:
    """Stock Register: detailed movements per item/godown (read-only).

    VB6 evidence: Crystal StkRegStore.rpt/StockRegister.rpt (TTX cols:
    Item/VDate/VType/VNo/Particular/RecQty/RecAmt/IssQty/IssAmt/BalQty)
    are DATE-WINDOW based - not FY-pinned. Live Stock rows are all
    Vprefix='2025' (13253), so default vprefix=None = no prefix filter
    (earlier hardcoded '2026' returned 0 rows = BUG, fixed).
    """
    sql = f"SELECT TOP {int(top)} DocId, Vtype, VNo, VDate, Item, GodownCode, " \
          "QtyIss, QtyRec, Rate, Amount, U_Name, VTime " \
          "FROM Stock WHERE Site_Code = ? "
    params = [SITE_CODE]
    if vprefix:
        sql += "AND Vprefix = ? "
        params.append(vprefix)
    if vdate_from is not None:
        sql += "AND Vdate >= ? "
        params.append(vdate_from)
    if vdate_to is not None:
        sql += "AND Vdate <= ? "
        params.append(vdate_to)
    if godown:
        sql += "AND GodownCode = ? "
        params.append(godown)
    if item:
        sql += "AND Item = ? "
        params.append(item)
    sql += "ORDER BY VDate DESC, VNo DESC, Sno"
    rows = db.query(sql, tuple(params), cn=cn)
    return [{"docid": r.DocId, "vtype": r.Vtype, "vno": r.VNo,
             "vdate": r.VDate, "item": r.Item or "", "godown": r.GodownCode or "",
             "qty_iss": r.QtyIss or 0, "qty_rec": r.QtyRec or 0,
             "rate": r.Rate or 0, "amount": r.Amount or 0,
             "user": r.U_Name or "", "vtime": r.VTime} for r in rows]


def purchase_register(vprefix: str = "2026", cn=None, top: int = 200) -> list:
    """Purchase Register with GIN + POrder + PBPB."""
    rows = db.query(
        f"SELECT TOP {int(top)} DocId, VNo, VDate, PartyName, Vtype "
        "FROM GIN WHERE Site_Code = ? AND Vprefix = ? AND Vtype IN ('MRCR') "
        "UNION "
        f"SELECT TOP {int(top)} DocId, VNo, VDate, PartyCode, Vtype "
        "FROM POrder WHERE Site_Code = ? AND Vprefix = ? AND Vtype = 'PORD' "
        "UNION "
        f"SELECT TOP {int(top)} DocId, VNo, Vdate, Party, Vtype "
        "FROM Purch1 WHERE Site_Code = ? AND Vprefix = ? AND Vtype = 'PBPB' "
        "ORDER BY VDate DESC, VNo DESC",
        (SITE_CODE, vprefix, SITE_CODE, vprefix, SITE_CODE, vprefix), cn=cn)
    return [{"docid": r[0], "vno": r[1], "vdate": r[2],
             "party": (r[3] or "").strip(), "vtype": r[4]} for r in rows]


# ============================================================
# Helper: Get next indent VNo for Stock lines
# ============================================================
def _get_indent_sno(indent_docid: str, cn=None) -> int:
    rows = db.query(
        "SELECT MAX(IndentSNo) FROM Stock WHERE IndentDocId = ?",
        (indent_docid,), cn=cn)
    return (rows[0][0] or 0) + 1 if rows and rows[0][0] else 1


# ============================================================
# Purch2 lines from GIN (for display)
# ============================================================
def gin_purch2_lines(docid: str, cn=None) -> list:
    """Get Purch2 lines linked to a GIN (ContraDocId = GIN.DocId)."""
    return gin_lines(docid, cn=cn)


# ============================================================
# eInvoice Config (P6-5) - eInvoiceEnviro table (1 row)
# VB6: eInvoice.bas / frmCompany.frm
# ============================================================
EINVIOCE_COLS = "ASPId, ASPPwd, eInvUserName, eInvPwd"


def _einvoice_missing_table_err() -> ValueError:
    return ValueError(
        "eInvoice config table not present in this DB. "
        "Feature is disabled for schema compatibility."
    )


def _einvoice_query_safe(sql: str, params=(), cn=None):
    try:
        return db.query(sql, params, cn=cn)
    except Exception as exc:
        msg = str(exc)
        if "Invalid object name 'eInvoiceEnviro'" in msg or "eInvoiceEnviro" in msg and "does not exist" in msg:
            return []
        raise


def einvoice_get(cn=None) -> dict | None:
    """Read eInvoice config (single row). Returns None if table missing."""
    rows = _einvoice_query_safe(
        f"SELECT {EINVIOCE_COLS} FROM eInvoiceEnviro", cn=cn)
    if not rows:
        return None
    r = rows[0]
    return {"asp_id": (r[0] or "").strip(),
            "asp_pwd": (r[1] or "").strip(),
            "einv_user": (r[2] or "").strip(),
            "einv_pwd": (r[3] or "").strip()}


def einvoice_upsert(rec: dict, cn=None, commit: bool = True) -> int:
    """Insert or update eInvoice config (single-row table).
    If row exists UPDATE, else INSERT. Safe if table missing.
    """
    existing = einvoice_get(cn=cn)
    if existing is None:
        # Check if table exists before trying INSERT
        if not _einvoice_query_safe("SELECT 1 FROM eInvoiceEnviro WHERE 1=0", cn=cn):
            raise _einvoice_missing_table_err()
        return db.execute(
            f"INSERT INTO eInvoiceEnviro ({EINVIOCE_COLS}) "
            "VALUES (?, ?, ?, ?)",
            (rec.get("asp_id", ""), rec.get("asp_pwd", ""),
             rec.get("einv_user", ""), rec.get("einv_pwd", "")),
            cn=cn, commit=commit)
    else:
        if not _einvoice_query_safe("SELECT 1 FROM eInvoiceEnviro WHERE 1=0", cn=cn):
            raise _einvoice_missing_table_err()
        return db.execute(
            "UPDATE eInvoiceEnviro SET ASPId = ?, ASPPwd = ?, "
            "eInvUserName = ?, eInvPwd = ?",
            (rec.get("asp_id", ""), rec.get("asp_pwd", ""),
             rec.get("einv_user", ""), rec.get("einv_pwd", "")),
            cn=cn, commit=commit)


# ============================================================
# VB6-style Inventory Reports (read-only)
# ============================================================

def kitchen_stock_report(cn=None, vdate_from=None, vdate_to=None, top: int = 200) -> list:
    """
    Kitchen Stock Report (KitchenStkRep.txt)
    VB6 Evidence: MatRep_Click, Material > Reports
    Source Tables: Stock + ItemMast
    Output: Kitchen, GrpName, Item, KitchenStock, Unit
    """
    sql = f"""
        SELECT TOP {int(top)} 
            ISNULL(NULLIF(S.ItemRestCode, S.RestCode), 'KITCHEN') AS Kitchen,
            {item_category_case_sql('S.Item')} AS GrpName,
            S.Item, 
            SUM(ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) AS KitchenStock,
            MAX(ISNULL(S.Unit,'')) AS Unit
        FROM Stock S
        LEFT JOIN ItemMast I ON I.Code = S.Item
        WHERE S.Site_Code = ?
    """
    params = [SITE_CODE]
    
    if vdate_from is not None:
        sql += " AND S.Vdate >= ?"
        params.append(vdate_from)
    if vdate_to is not None:
        sql += " AND S.Vdate <= ?"
        params.append(vdate_to)
        
    sql += " GROUP BY ISNULL(NULLIF(S.ItemRestCode,S.RestCode),'KITCHEN'), " + \
           f"{item_category_case_sql('S.Item')}, S.Item" + \
           " ORDER BY Kitchen, GrpName, S.Item"
    
    rows = db.query(sql, tuple(params), cn=cn)
    return [{
        "kitchen": r.Kitchen or "",
        "grp_name": r.GrpName or "",
        "item": r.Item or "",
        "kitchen_stock": float(r.KitchenStock or 0),
        "unit": r.Unit or ""
    } for r in rows]


def stock_register_detailed(godown: str = None, item: str = None, 
                           vdate_from=None, vdate_to=None, 
                           cn=None, top: int = 200) -> list:
    """
    Store-wise Stock Register (StockRegister.txt)
    VB6 Evidence: Housekeeping > Reports [Sub: HouseREP_Click]
    Source Tables: Stock + ItemMast + GodownMast
    Output: GrpName, Item, OpeningQty, PurchaseQty, IssueQty, ClosingQty, ClosingValue
    """
    # VB6 uses date window @F to @T, not FY-pinned
    sql = f"""
        SELECT TOP {int(top)} 
            CASE
                WHEN S.Item LIKE 'RICE%' THEN 'RICE'
                WHEN S.Item LIKE 'OIL%'  THEN 'OIL'
                WHEN S.Item LIKE 'WHKY%' THEN 'WHISKY'
                WHEN S.Item LIKE 'SUGR%' THEN 'SUGAR'
                WHEN S.Item LIKE 'ATTA%' THEN 'ATTA'
                WHEN S.Item LIKE 'TEA%'  THEN 'TEA'
                WHEN S.Item LIKE 'WINE%' THEN 'WINE'
                WHEN S.Item LIKE 'VODKA%' THEN 'VODKA'
                WHEN S.Item LIKE 'FRT%'  THEN 'FRUIT'
                ELSE 'OTHER'
            END AS GrpName,
            S.Item,
            SUM(CASE WHEN S.Vdate < ? THEN ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0) ELSE 0 END) AS OpeningQty,
            SUM(CASE WHEN S.Vdate BETWEEN ? AND ? THEN ISNULL(S.QtyRec,0) ELSE 0 END) AS PurchaseQty,
            SUM(CASE WHEN S.Vdate BETWEEN ? AND ? THEN ISNULL(S.QtyIss,0) ELSE 0 END) AS IssueQty,
            SUM(CASE WHEN S.Vdate <= ? THEN ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0) ELSE 0 END) AS ClosingQty,
            SUM(CASE WHEN S.Vdate <= ? THEN (ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) * ISNULL(S.Rate,0) ELSE 0 END) AS ClosingValue
        FROM Stock S
        LEFT JOIN ItemMast I ON I.Code = S.Item
        LEFT JOIN GodownMast G ON G.Code = S.GodownCode
        WHERE S.Site_Code = ?
    """
    params = []
    
    # Date parameters appear 5 times in query (OpeningQty, PurchaseQty x2, IssueQty x2, ClosingQty x2, ClosingValue x2)
    # Actually: OpeningQty uses vdate_from, PurchaseQty/IssueQty use both, Closing uses vdate_to
    from_date = vdate_from or date(1900, 1, 1)  # Far past if not specified
    to_date = vdate_to or date(9999, 12, 31)    # Far future if not specified
    
    params.extend([from_date, from_date, to_date, from_date, to_date, from_date, to_date, SITE_CODE])
    
    if godown:
        sql += " AND S.GodownCode = ?"
        params.append(godown)
    if item:
        sql += " AND S.Item = ?"
        params.append(item)
        
    sql += " GROUP BY "
    sql += "CASE WHEN S.Item LIKE 'RICE%' THEN 'RICE' WHEN S.Item LIKE 'OIL%' THEN 'OIL' WHEN S.Item LIKE 'WHKY%' THEN 'WHISKY' WHEN S.Item LIKE 'SUGR%' THEN 'SUGAR' WHEN S.Item LIKE 'ATTA%' THEN 'ATTA' WHEN S.Item LIKE 'TEA%' THEN 'TEA' WHEN S.Item LIKE 'WINE%' THEN 'WINE' WHEN S.Item LIKE 'VODKA%' THEN 'VODKA' WHEN S.Item LIKE 'FRT%' THEN 'FRUIT' ELSE 'OTHER' END, S.Item"
    sql += " ORDER BY GrpName, S.Item"
    
    rows = db.query(sql, tuple(params), cn=cn)
    return [{
        "grp_name": r.GrpName or "",
        "item": r.Item or "",
        "opening_qty": float(r.OpeningQty or 0),
        "purchase_qty": float(r.PurchaseQty or 0),
        "issue_qty": float(r.IssueQty or 0),
        "closing_qty": float(r.ClosingQty or 0),
        "closing_value": float(r.ClosingValue or 0)
    } for r in rows]


def r_stock_register(vdate_from=None, vdate_to=None, cn=None, top: int = 200) -> list:
    """
    R-STOCK REGISTER (RStockRegister.txt)
    VB6 Evidence: Proc_165_2_1E3A588, Rest_Click [code-generated]
    Source Tables: Stock + ItemMast (WHERE RestCode <> '')
    Output: RestCode, Item, OpeningQty, ReceiptQty, IssueQty, ClosingQty, ClosingValue
    """
    from_date = vdate_from or date(1900, 1, 1)
    to_date = vdate_to or date(9999, 12, 31)
    
    sql = f"""
        SELECT TOP {int(top)} 
            S.RestCode,
            S.Item,
            SUM(CASE WHEN S.Vdate < ? THEN ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0) ELSE 0 END) AS OpeningQty,
            SUM(CASE WHEN S.Vdate BETWEEN ? AND ? THEN ISNULL(S.QtyRec,0) ELSE 0 END) AS ReceiptQty,
            SUM(CASE WHEN S.Vdate BETWEEN ? AND ? THEN ISNULL(S.QtyIss,0) ELSE 0 END) AS IssueQty,
            SUM(CASE WHEN S.Vdate <= ? THEN ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0) ELSE 0 END) AS ClosingQty,
            SUM(CASE WHEN S.Vdate <= ? THEN (ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) * ISNULL(S.Rate,0) ELSE 0 END) AS ClosingValue
        FROM Stock S
        LEFT JOIN ItemMast I ON I.Code = S.Item
        WHERE S.Site_Code = ? AND ISNULL(S.RestCode,'') <> ''
    """
    params = [from_date, from_date, to_date, from_date, to_date, from_date, to_date, SITE_CODE]
    
    sql += " GROUP BY S.RestCode, S.Item ORDER BY S.RestCode, S.Item"
    
    rows = db.query(sql, tuple(params), cn=cn)
    return [{
        "rest_code": r.RestCode or "",
        "item": r.Item or "",
        "opening_qty": float(r.OpeningQty or 0),
        "receipt_qty": float(r.ReceiptQty or 0),
        "issue_qty": float(r.IssueQty or 0),
        "closing_qty": float(r.ClosingQty or 0),
        "closing_value": float(r.ClosingValue or 0)
    } for r in rows]


def stock_in_hand(cn=None, top: int = 200) -> list:
    """
    Stock In Hand - current balance of every item (StockINHand.txt)
    VB6 Evidence: StockInHand report
    Source Tables: Stock + ItemMast
    Output: Item, Description, Unit, BalanceQty, BalanceValue, Godown, Location
    """
    sql = f"""
        SELECT TOP {int(top)} 
            S.Item,
            ISNULL(I.Name, '') AS Description,
            ISNULL(S.Unit, '') AS Unit,
            SUM(ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) AS BalanceQty,
            SUM((ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) * ISNULL(S.Rate,0)) AS BalanceValue,
            ISNULL(S.GodownCode, '') AS Godown,
            ISNULL(S.Remarks, '') AS Location
        FROM Stock S
        LEFT JOIN ItemMast I ON I.Code = S.Item
        WHERE S.Site_Code = ?
        GROUP BY S.Item, I.Name, S.Unit, S.GodownCode, S.Remarks
        HAVING SUM(ISNULL(S.QtyRec,0)-ISNULL(S.QtyIss,0)) <> 0
        ORDER BY BalanceQty DESC
    """
    rows = db.query(sql, (SITE_CODE,), cn=cn)
    return [{
        "item": r.Item or "",
        "description": r.Description or "",
        "unit": r.Unit or "",
        "balance_qty": float(r.BalanceQty or 0),
        "balance_value": float(r.BalanceValue or 0),
        "godown": r.Godown or "",
        "location": r.Location or ""
    } for r in rows]


# ============================================================
# VB6-style Inventory Reports (read-only) - Continued
# ============================================================

def kitchen_stock_summary(cn=None, top: int = 200,
                          vdate_from=None, vdate_to=None) -> list:
    """
    Kitchen Stock Summary (KitchenStkSumm.txt)
    VB6 Evidence: Kitchen Stock Summary report
    Source Tables: Stock
    Output: Item, IssuedToKitchen, KitchenStockValue
    """
    sql = f"""
        SELECT TOP {int(top)} 
            S.Item,
            SUM(ISNULL(S.QtyIss,0)) AS IssuedToKitchen,
            SUM(ISNULL(S.QtyIss,0)) * MAX(ISNULL(S.Rate,0)) AS KitchenStockValue
        FROM Stock S
        WHERE S.Site_Code = ? AND ISNULL(S.QtyIss,0) > 0
    """
    params = [SITE_CODE]
    if vdate_from is not None:
        sql += " AND S.Vdate >= ?"
        params.append(vdate_from)
    if vdate_to is not None:
        sql += " AND S.Vdate <= ?"
        params.append(vdate_to)
    sql += " GROUP BY S.Item ORDER BY KitchenStockValue DESC"
    rows = db.query(sql, tuple(params), cn=cn)
    return [{
        "item": r.Item or "",
        "issued_to_kitchen": float(r.IssuedToKitchen or 0),
        "kitchen_stock_value": float(r.KitchenStockValue or 0)
    } for r in rows]
def gin_delete(docid: str, cn=None, commit: bool = True) -> dict:
    """Delete GIN (Purchase Receipt) and reverse ClearYN on linked indent lines.
    
    VB6 equivalent: pMREntry delete flow with ClearYN reversal.
    """
    own = cn is None
    cn = cn or db.connect()
    try:
        # Reverse ClearYN on linked indent lines (row-wise pairing via Stock)
        db.execute(
            """UPDATE Indent1 SET ClearYN = ''
            WHERE EXISTS (
                SELECT 1 FROM Stock s
                WHERE s.DocId = ? AND s.IndentDocId = Indent1.DocId
                AND ISNULL(s.IndentSNo, 0) = Indent1.Sno)""",
            (docid,), cn=cn, commit=False)
        # Delete Purch2 lines (GIN lines)
        db.execute("DELETE FROM Purch2 WHERE ContraDocId = ?", (docid,), cn=cn, commit=False)
        # Delete GIN header
        db.execute("DELETE FROM GIN WHERE DocId = ?", (docid,), cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"deleted": docid}
    finally:
        if own:
            cn.close()

