"""FA Voucher engine (VB6 FaVrEnt.frm + FaChqClear.frm + FaReports port).

EVIDENCE (live + VB6):
- FaVrEnt.frm:13872 INSERT INTO LedgerM (DocId,V_Type,v_Prefix,V_No,...);
  :13719 INSERT INTO LEDGER (...SubCode,AmtCr,AmtDr,ContraSub,Narration,...);
  DocId (VB6 FaVrEnt.frm:13332): 'D'+site(2)+V_Type.ljust(5)+
  Prefix.ljust(5)+V_No.rjust(8) = 21 char.
- Voucher_Prefix table: V_Type/Date_From/Date_To/Prefix/Start_Srl_No
  (next V_No = MAX(V_No)+1 per V_Type+Prefix, else Start_Srl_No+1).
- FaChqClear.frm:663 'Update Ledger Set Chq_No=...,Chq_Date=...,Clg_Date=...'
  (bank reconciliation); :1752/:1760 cleared-vs-pending filter.
- Acgroup.GroupNature: A=Assets, L=Liabilities, E=Expenses, R=Revenue
  (live: A=14, L=12, E=3, R=4). Trial/PnL/BS group-wise on Ledger.
- Ledger live: V_Type 'HPOST' 11684 rows; LedgerM 0 rows (UI vouchers
  bante the — VB6 app me unka data Ledger me hi hai).
All writes transaction-scoped + PYT-guard; reports read-only.
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()
_HO_SUB_CLAUSE = "(s.LogSite_Code = ? OR s.LogSite_Code='HO' OR ISNULL(s.LogSite_Code,'')='')"


def _require_voucher_privilege(cn, need: str, user: str | None = None, comp: str | None = None):
    """VB6 FaVoucher.bas Proc_7_1 + MDI fame_Click guard.
    need: 'A' add, 'E' edit, 'D' delete, 'P' print. Flag='Y' allows, else Param_Str must contain need."""
    u = (user or USER or "").strip()
    c = (comp or db.get_comp_code() or "2")
    try:
        rows = db.query(
            "SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Voucher Entry'",
            (u, c), cn=cn)
    except Exception:
        return
    if not rows:
        return
    try:
        priv = ""
        flag = ""
        r = rows[0]
        if hasattr(r, 'UPrivilege'):
            priv = (r.UPrivilege or "").upper()
            flag = (r.Flag or "").upper() if hasattr(r, 'Flag') else ""
        else:
            priv = str(r[0] or "").upper()
            flag = str(r[1] or "").upper() if len(r) > 1 else ""
    except Exception:
        priv, flag = "", ""
    if flag == "Y" or need.upper() in priv:
        return
    raise PermissionError(f"Voucher Entry {need}-right denied for user '{u}' (Param_Str='{priv}', Flag='{flag}')")


def _site() -> str:
    try:
        return db.get_site_code() or SITE_CODE
    except Exception:
        return SITE_CODE


# ---------------------------------------------------------------- numbering
def _prefix_for(vtype: str, vdate, cn=None, site: str | None = None) -> tuple[str, str]:
    """(Prefix, FY-window) for V_Type at vdate from Voucher_Prefix (site+LOGSITE filtered, HO fallback)."""
    sc = site or _site()
    rows = db.query(
        "SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type = ? "
        "AND ? BETWEEN Date_From AND Date_To AND Site_Code = ? AND LogSite_Code = ? "
        "ORDER BY Date_From DESC",
        (vtype, vdate, sc, sc), cn=cn)
    if not rows:
        rows = db.query(
            "SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type = ? "
            "AND ? BETWEEN Date_From AND Date_To AND (Site_Code = ? OR Site_Code='HO') "
            "AND (LogSite_Code = ? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='') "
            "ORDER BY Date_From DESC",
            (vtype, vdate, sc, sc), cn=cn)
    if not rows:
        rows = db.query(
            "SELECT TOP 1 Prefix FROM Voucher_Prefix WHERE V_Type = ? "
            "AND ? BETWEEN Date_From AND Date_To ORDER BY Date_From DESC",
            (vtype, vdate), cn=cn)
    if not rows:
        # FY fallback: '2025' pattern
        fy = vdate.year if vdate.month >= 4 else vdate.year - 1
        return str(fy), None
    return rows[0][0], None


def next_vno(vtype: str, vdate, cn=None, site: str | None = None) -> int:
    """Next V_No: MAX(LedgerM.V_No)+1 else MAX(Ledger.V_No)+1 else
    Voucher_Prefix.Start_Srl_No+1 (VB6 numbering parity, site+LOGSITE filtered)."""
    sc = site or _site()
    prefix, _ = _prefix_for(vtype, vdate, cn=cn, site=sc)
    rows = db.query(
        "SELECT ISNULL(MAX(V_No), 0) FROM LedgerM WHERE V_Type = ? "
        "AND v_Prefix = ? AND Site_Code = ? AND LogSite_Code = ?",
        (vtype, prefix, sc, sc), cn=cn)
    mx = (rows[0][0] if rows else 0) or 0
    if not mx:
        rows = db.query(
            "SELECT ISNULL(MAX(V_No), 0) FROM Ledger WHERE V_Type = ? "
            "AND v_Prefix = ? AND Site_Code = ? AND LogSite_Code = ?",
            (vtype, prefix, sc, sc), cn=cn)
        mx = (rows[0][0] if rows else 0) or 0
    if not mx:
        rows = db.query(
            "SELECT ISNULL(Start_Srl_No, 0) FROM Voucher_Prefix "
            "WHERE V_Type = ? AND Prefix = ? AND Site_Code = ? AND LogSite_Code = ?",
            (vtype, prefix, sc, sc), cn=cn)
        mx = (rows[0][0] if rows else 0) or 0
    return int(mx) + 1


def _make_docid(vtype: str, prefix: str, vno: int) -> str:
    """VB6 FaVrEnt.frm:13332 — 21 char: D+site(2)+type(5)+prefix(5)+vno(8)."""
    return ("D" + SITE_CODE + str(vtype).ljust(5) +
            str(prefix).ljust(5) + str(vno).rjust(8))


# ---------------------------------------------------------------- posting
def post_voucher(lines: list[dict], vdate, narration: str = "",
                 vtype: str = "JV", user: str = USER,
                 chq_no: str = "", chq_date=None,
                 cn=None, commit: bool = True) -> dict:
    """Double-entry voucher: LedgerM header + n Ledger lines.
    VB6 patterns: CurrBal update, LedgerRef tracking, LedgerLog audit,
    ContraSub auto-fill, cheque date validation.

    lines: [{'subcode','amt_dr','amt_cr','narration'?,
             'agrefno'?'agref_type'?,'due_date'?,
             'adjustments'?=[{'docid2','v_sno2','cr','subcode'?,'agrefno'?}],
             'tds'?={'tdscode','tds_drcode','onamt','tds_pct'?,...}}, ...]
    Guard: har line ka SubCode live Subgroup me ho; total DR == total CR.
    Returns {'docid','vno','dr','cr', 'tds_docids'?}.
    """
    if not lines or len(lines) < 2:
        raise ValueError("Voucher me kam se kam 2 lines hone chahiye")
    vdate = vdate or datetime.date.today()
    if isinstance(vdate, str):
        vdate = datetime.date.fromisoformat(vdate)
    tot_dr = round(sum(float(l.get("amt_dr") or 0) for l in lines), 2)
    tot_cr = round(sum(float(l.get("amt_cr") or 0) for l in lines), 2)
    if abs(tot_dr - tot_cr) > 0.005:
        raise ValueError(f"Debit ({tot_dr}) != Credit ({tot_cr}) "
                         "— unbalanced voucher")
    if tot_dr == 0:
        raise ValueError("Voucher amount zero nahi ho sakta")
    # VB6 cheque date validation
    if chq_no and chq_date:
        if isinstance(chq_date, str):
            chq_date = datetime.date.fromisoformat(chq_date)
        if chq_date > vdate:
            raise ValueError("Cheque date voucher date se baad nahi ho sakta")
    # menuHelp guard (VB6 Proc_7_1) - require A for add
    _require_voucher_privilege(cn, 'A', user=user)
    # DATALOCK guard (VB6 FaVrEnt) - best-effort
    try:
        dl = db.query("SELECT TOP 1 flag FROM DATELOCK WHERE SDate <= ? AND EDate >= ? AND flag=1", (vdate, vdate), cn=cn)
        if dl:
            raise ValueError("Date locked (DATELOCK)")
    except ValueError:
        raise
    except Exception:
        pass
    # subcode validation + group info (VB6 fills GroupCode/GroupNature) with HO fallback
    subs = {}
    sc_site = _site()
    for l in lines:
        sc = (l.get("subcode") or "").strip()
        if not sc:
            raise ValueError("Har line me SubCode zaroori hai")
        if sc in subs:
            continue
        g = db.query(
            "SELECT s.SubCode, s.GroupCode, a.GroupNature FROM Subgroup s "
            "JOIN Acgroup a ON a.GroupCode = s.GroupCode "
            f"WHERE RTRIM(s.SubCode) = ? AND {_HO_SUB_CLAUSE}", (sc, sc_site), cn=cn)
        if not g:
            raise ValueError(f"SubCode '{sc}' live Subgroup me nahi mila")
        subs[sc] = (g[0][1], g[0][2])
    own = cn is None
    cn = cn or db.connect()
    try:
        sc_site = _site()
        prefix, _ = _prefix_for(vtype, vdate, cn=cn, site=sc_site)
        vno = next_vno(vtype, vdate, cn=cn, site=sc_site)
        docid = _make_docid(vtype, prefix, vno)
        cur = cn.cursor()
        cur.execute(
            "INSERT INTO LedgerM (DocId, V_Type, v_Prefix, V_No, Site_Code, "
            "V_Date, Narration, U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
            (docid, vtype, prefix, vno, SITE_CODE, vdate, narration,
             user, SITE_CODE))
        # Find contra pairs for ContraSub auto-fill (VB6 pattern)
        contra_pairs = _find_contra_pairs(lines, subs)
        for sno, l in enumerate(lines, start=1):
            sc = l["subcode"].strip()
            gc, gn = subs[sc]
            contra_sub = contra_pairs.get(sc, "")
            cur.execute(
                "INSERT INTO Ledger (DocId, V_SNo, V_Type, V_No, v_Prefix, "
                "Site_Code, V_Date, SubCode, AmtDr, AmtCr, ContraSub, "
                "Narration, Chq_No, Chq_Date, Clg_Date, GroupCode, "
                "GroupNature, AgRefNo, U_Name, U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, "
                "?, ?, ?, ?, getdate(), 'A', ?)",
                (docid, sno, vtype, vno, prefix, SITE_CODE, vdate, sc,
                 float(l.get("amt_dr") or 0), float(l.get("amt_cr") or 0),
                 contra_sub, l.get("narration", "") or narration,
                 chq_no or "", chq_date, gc, gn,
                 (l.get("agrefno") or "").strip(),
                 user, SITE_CODE))
            # VB6 CurrBal update: running balance per SubGroup
            _update_currbal(cn, sc, float(l.get("amt_dr") or 0),
                            float(l.get("amt_cr") or 0), vdate=vdate)
            # VB6 LedgerRef: har line ka pending Dr/Cr reference row (FA-4)
            _create_ledgerref(cn, docid, sno, sc, l, vdate=vdate)
        # FA-4: LEDGERADJ delete+reinsert (VB6 FaVrEnt loc_1B35E71)
        _write_ledgeradj(cn, docid, lines, user=user)
        # FA-5: TDS calc + LEDGERTDS + auto TDS contra-voucher
        tds_docids = _post_line_tds(cn, docid, prefix, vdate, lines,
                                    user=user)
        # VB6 LedgerLog: audit trail
        _log_voucher(cn, docid, "A", user)
        # VB6: UPDATE Voucher_Prefix SET Start_Srl_No = V_No (number consumed) with LogSite_Code
        try:
            cn.execute(
                "UPDATE Voucher_Prefix SET Start_Srl_No = ?, U_EntDt = getdate(), "
                "U_AE = 'E' WHERE V_Type = ? AND Prefix = ? AND Site_Code = ? AND LogSite_Code = ?",
                (vno, vtype, prefix, _site(), _site()))
        except Exception:
            pass
        # VB6 LASTVOU / LastVoucher: track last docid per user+vtype
        try:
            from HMS_py.core import fa_ledger_ops as flo
            flo.lastvou_upsert(
                {"user_name": user, "vtype": vtype, "docid": docid,
                 "v_prefix": prefix, "last_ent_date": vdate},
                cn=cn, commit=False)
        except Exception:
            pass
        if commit:
            cn.commit()
        res = {"docid": docid, "vno": vno, "dr": tot_dr, "cr": tot_cr}
        if tds_docids:
            res["tds_docids"] = tds_docids
        return res
    except Exception:
        try:
            cn.rollback()
        except Exception:
            pass
        raise
    finally:
        if own:
            cn.close()


def _find_contra_pairs(lines: list[dict], subs: dict) -> dict:
    """VB6 FaVrEnt ContraSub auto-fill.
    Har DR line ka ContraSub = pehli CR line ka SubCode;
    har CR line ka ContraSub = pehli DR line ka SubCode.
    Returns {subcode: contra_subcode}."""
    pairs: dict[str, str] = {}
    first_dr = ""
    first_cr = ""
    for l in lines:
        sc = (l.get("subcode") or "").strip()
        if not sc:
            continue
        if not first_dr and float(l.get("amt_dr") or 0) > 0:
            first_dr = sc
        if not first_cr and float(l.get("amt_cr") or 0) > 0:
            first_cr = sc
    if not first_dr or not first_cr:
        return pairs
    for l in lines:
        sc = (l.get("subcode") or "").strip()
        if not sc:
            continue
        if float(l.get("amt_dr") or 0) > 0:
            pairs.setdefault(sc, first_cr)
        if float(l.get("amt_cr") or 0) > 0:
            pairs.setdefault(sc, first_dr)
    return pairs


def _update_currbal(cn, subcode: str, dr: float, cr: float, vdate=None):
    """VB6 FaLib Proc_183_0: SUBGROUPCURRBAL delta + ACGROUPCURRBAL chain.

    Curr_Bal += (AmtDr - AmtCr) for (LogSite_Code, SubCode, V_Date);
    nahi mila to INSERT. Phir SubGroup.GroupCode se MainGrCode chain
    par ACGROUPCURRBAL me bhi same delta upsert hota hai."""
    delta = float(dr) - float(cr)
    if abs(delta) < 0.005:
        return
    sc_site = _site()
    g = db.query(
        f"SELECT GroupCode FROM SubGroup WHERE RTRIM(SubCode) = ? AND {_HO_SUB_CLAUSE}",
        (subcode, sc_site), cn=cn)
    groupcode = ((g[0][0] if g else "") or "").strip()
    rows = db.query(
        "SELECT ISNULL(Curr_Bal, 0) FROM SUBGROUPCURRBAL "
        "WHERE SubCode = ? AND LogSite_Code = ? AND V_Date = ?",
        (subcode, SITE_CODE, vdate), cn=cn)
    if rows:
        cn.execute(
            "UPDATE SUBGROUPCURRBAL SET Curr_Bal = ?, GroupCode = ? "
            "WHERE SubCode = ? AND LogSite_Code = ? AND V_Date = ?",
            (float(rows[0][0] or 0) + delta, groupcode,
             subcode, SITE_CODE, vdate))
    else:
        cn.execute(
            "INSERT INTO SUBGROUPCURRBAL (LogSite_Code, SubCode, V_Date, "
            "GroupCode, Curr_Bal, Site_Code) VALUES (?, ?, ?, ?, ?, ?)",
            (SITE_CODE, subcode, vdate, groupcode, delta, SITE_CODE))
    if not groupcode:
        return
    seen: set[str] = set()
    gc = groupcode
    for _ in range(10):
        if not gc or gc in seen:
            break
        seen.add(gc)
        ar = db.query(
            "SELECT ISNULL(Curr_Bal, 0) FROM ACGROUPCURRBAL "
            "WHERE GroupCode = ? AND LogSite_Code = ? AND V_Date = ?",
            (gc, SITE_CODE, vdate), cn=cn)
        if ar:
            cn.execute(
                "UPDATE ACGROUPCURRBAL SET Curr_Bal = ? "
                "WHERE GroupCode = ? AND LogSite_Code = ? AND V_Date = ?",
                (float(ar[0][0] or 0) + delta, gc, SITE_CODE, vdate))
        else:
            cn.execute(
                "INSERT INTO ACGROUPCURRBAL (LogSite_Code, GroupCode, "
                "V_Date, Curr_Bal, Site_Code) VALUES (?, ?, ?, ?, ?)",
                (SITE_CODE, gc, vdate, delta, SITE_CODE))
        p = db.query(
            "SELECT MainGrCode FROM AcGroup WHERE GroupCode = ? AND (LOGSITE_CODE = ? OR LOGSITE_CODE='HO')",
            (gc, sc_site), cn=cn)
        if not p:
            break
        parent = ((p[0][0] or "").strip())
        if not parent or parent == gc:
            break
        gc = parent


def _create_ledgerref(cn, docid: str, sno: int, subcode: str, line: dict,
                      vdate=None):
    """FA-4: LEDGERREF row per voucher line (VB6 FaVrEnt LedgerRef grid).
    Dr/Cr + DueDate + AgRefNo + AgRefType + V_Date copied to reference table."""
    from HMS_py.core import fa_ledger_ops as flo
    flo.ledgerref_insert({
        "docid": docid, "v_sno": sno,
        "dr": float(line.get("amt_dr") or 0),
        "cr": float(line.get("amt_cr") or 0),
        "subcode": subcode,
        "due_date": line.get("due_date"),
        "agrefno": (line.get("agrefno") or "").strip(),
        "agref_type": (line.get("agref_type") or "").strip(),
        "v_date": vdate,
    }, cn=cn, commit=False)


def _write_ledgeradj(cn, docid: str, lines: list[dict], user: str = USER):
    """FA-4: delete existing adj for this DocId1/DocId2 then re-insert
    (VB6 FaVrEnt loc_1B35E71 pattern)."""
    from HMS_py.core import fa_ledger_ops as flo
    db.execute(
        "DELETE FROM LEDGERADJ WHERE DocId1 = ? OR DocId2 = ?",
        (docid, docid), cn=cn, commit=False)
    pairs: list[dict] = []
    for sno, l in enumerate(lines, start=1):
        for a in (l.get("adjustments") or []):
            rec = {
                "docid1": (a.get("docid1") or docid).strip(),
                "v_sno1": int(a.get("v_sno1") or sno),
                "docid2": (a.get("docid2") or "").strip(),
                "v_sno2": int(a.get("v_sno2") or 0),
                "cr": float(a.get("cr") or 0),
                "subcode": (a.get("subcode") or l["subcode"]).strip(),
                "name": a.get("name", ""),
                "agrefno": (a.get("agrefno") or
                            l.get("agrefno") or "").strip(),
            }
            if rec["docid2"] and rec["cr"] > 0:
                pairs.append(rec)
    for rec in pairs:
        flo.ledgeradj_insert(rec, cn=cn, commit=False)


def _post_line_tds(cn, docid: str, prefix: str, vdate, lines: list[dict],
                   user: str = USER) -> list[str]:
    """FA-5: per-line TDS — TDSAMT=ONAMT*TDS/100, auto TDS contra-voucher,
    LEDGERTDS insert (VB6 FaVrEnt loc_F0875D). Returns linked TDSDocIds."""
    from HMS_py.core import fa_ledger_ops as flo
    from HMS_py.core import fa_tds_ops as fto
    linked: list[str] = []
    tds_vtype = None
    for sno, l in enumerate(lines, start=1):
        t = l.get("tds")
        if not t:
            continue
        tdscode = (t.get("tdscode") or t.get("TDSCode") or "").strip()
        tds_drcode = (t.get("tds_drcode") or t.get("TDSDrCode") or "").strip()
        if not tdscode or not tds_drcode:
            raise ValueError("TDS me TDSCode aur TDSDrCode zaroori hain")
        onamt = float(t.get("onamt") or l.get("amt_dr") or
                      l.get("amt_cr") or 0)
        tds_pct = float(t.get("tds") if t.get("tds") is not None
                        else t.get("tds_pct") or 0)
        tds_amt = float(t.get("tdsamt") or 0) or fto.tds_amt(onamt, tds_pct)
        if tds_amt <= 0:
            continue
        if tds_vtype is None:
            tds_vtype = (t.get("vtype") or "TDS").strip()
            vt = db.query(
                "SELECT 1 FROM Voucher_Type WHERE V_Type = ?",
                (tds_vtype,), cn=cn)
            if not vt:
                raise ValueError("There Must be a TDS Vr.Type")
        # auto contra: DR deductee (TDSDrCode), CR TDS payable (TDSCode)
        tres = post_voucher(
            [{"subcode": tds_drcode, "amt_dr": tds_amt,
              "narration": t.get("narration") or "TDS deduct"},
             {"subcode": tdscode, "amt_cr": tds_amt,
              "narration": t.get("narration") or "TDS deduct"}],
            vdate, narration=t.get("narration") or "TDS auto",
            vtype=tds_vtype, user=user, cn=cn, commit=False)
        linked.append(tres["docid"])
        flo.ledgertds_insert({
            "docid": docid, "v_sno": sno,
            "v_prefix": prefix, "v_date": vdate,
            "tdscode": tdscode, "tdsdrcode": tds_drcode,
            "tdsyn": t.get("tdsyn", "Y"),
            "onamt": onamt, "tds": tds_pct, "tdsamt": tds_amt,
            "tdspost": t.get("tdspost", ""),
            "tds_docid": tres["docid"], "tds_v_sno": 1,
        }, cn=cn, commit=False)
    return linked


def _log_voucher(cn, docid: str, flag: str, user: str):
    """VB6 LedgerLog audit: Ledger lines + LedgerM header (SeqNo = Max+1).
    flag ('A'/'D') signature me rehta hai; log row flo helpers se jaati hai."""
    try:
        from HMS_py.core import fa_ledger_ops as flo
        rows = db.query(
            "SELECT V_SNo, V_Type, V_No, v_Prefix, V_Date, SubCode, "
            "AmtCr, AmtDr, ContraSub, Chq_No, Chq_Date, Clg_Date, "
            "Narration, GroupCode, GroupNature "
            "FROM Ledger WHERE DocId = ? ORDER BY V_SNo",
            (docid,), cn=cn)
        seq_rows = db.query(
            "SELECT ISNULL(MAX(SeqNo), 0) FROM LedgerLog WHERE DocId = ?",
            (docid,), cn=cn)
        seq = int(seq_rows[0][0] or 0) if seq_rows else 0
        for r in rows:
            seq += 1
            flo.ledgerlog_insert({
                "docid": docid, "v_sno": r.V_SNo or 0,
                "vtype": r.V_Type or "", "vno": r.V_No or 0,
                "v_prefix": r.v_Prefix or "", "v_date": r.V_Date,
                "subcode": (r.SubCode or "").strip(),
                "amt_cr": float(r.AmtCr or 0),
                "amt_dr": float(r.AmtDr or 0),
                "contra_sub": r.ContraSub or "",
                "chq_no": r.Chq_No or "", "chq_date": r.Chq_Date,
                "clg_date": r.Clg_Date,
                "narration": (r.Narration or "").strip(),
                "groupcode": r.GroupCode or "",
                "groupnature": r.GroupNature or "",
                "u_name": user, "seqno": seq,
            }, cn=cn, commit=False)
        hm = db.query(
            "SELECT V_Type, v_Prefix, V_No, V_Date, Narration "
            "FROM LedgerM WHERE DocId = ?", (docid,), cn=cn)
        if hm:
            h = hm[0]
            hseq_rows = db.query(
                "SELECT ISNULL(MAX(SeqNo), 0) FROM LedgerMLog "
                "WHERE DocId = ?", (docid,), cn=cn)
            hseq = int(hseq_rows[0][0] or 0) if hseq_rows else 0
            flo.ledgermlog_insert({
                "docid": docid, "vtype": h.V_Type or "",
                "v_prefix": h.v_Prefix or "", "vno": h.V_No or 1,
                "v_date": h.V_Date,
                "narration": (h.Narration or "").strip(),
                "seqno": hseq + 1,
            }, cn=cn, commit=False)
    except Exception:
        pass  # audit trail best-effort (deployment me table missing ho sakti hai)


def delete_voucher(docid: str, cn=None, commit: bool = True,
                   user: str = USER) -> int:
    """Voucher delete (header + lines) — VB6 FaVrEnt delete parity.
    VB6 pattern: cascade delete LedgerRef/LedgerTDS, reverse CurrBal,
    log to LedgerLog before delete.
    Uses single connection for atomicity (BUG-H01 fix)."""
    _require_voucher_privilege(cn, 'D', user=user)
    own = cn is None
    cn = cn or db.connect()
    try:
        # Get voucher lines for CurrBal reversal + audit
        rows = db.query(
            "SELECT SubCode, AmtDr, AmtCr, V_Date FROM Ledger "
            "WHERE DocId = ?", (docid,), cn=cn)
        # Linked TDS vouchers (capture BEFORE LEDGERTDS cascade delete)
        tds_docs: list[str] = []
        try:
            tds_rows = db.query(
                "SELECT DISTINCT TDSDocId FROM LEDGERTDS WHERE DocId = ?",
                (docid,), cn=cn)
            tds_docs = [((r[0] or "").strip()) for r in tds_rows
                        if (r[0] or "").strip() and
                        (r[0] or "").strip() != docid]
        except Exception:
            pass
        # Cascade delete references
        try:
            db.execute("DELETE FROM LEDGERREF WHERE DocId = ?",
                       (docid,), cn=cn, commit=False)
        except Exception:
            pass
        try:
            db.execute("DELETE FROM LEDGERTDS WHERE DocId = ?",
                       (docid,), cn=cn, commit=False)
        except Exception:
            pass
        # FA-4/FA-8: LEDGERADJ cascade (VB6 FaVrEnt: DocId1 OR DocId2)
        try:
            db.execute(
                "DELETE FROM LEDGERADJ WHERE DocId1 = ? OR DocId2 = ?",
                (docid, docid), cn=cn, commit=False)
        except Exception:
            pass
        # Reverse CurrBal for each SubCode (VB6 Proc_183_0 delta reverse)
        for r in rows:
            sc = (r.SubCode or "").strip()
            if sc:
                _update_currbal(cn, sc, float(r.AmtCr or 0),
                                float(r.AmtDr or 0), vdate=r.V_Date)
        # TDS cascade: linked TDS voucher bhi reverse + delete
        for td in tds_docs:
            try:
                trows = db.query(
                    "SELECT SubCode, AmtDr, AmtCr, V_Date FROM Ledger "
                    "WHERE DocId = ?", (td,), cn=cn)
                for r in trows:
                    sc = (r.SubCode or "").strip()
                    if sc:
                        _update_currbal(cn, sc, float(r.AmtCr or 0),
                                        float(r.AmtDr or 0), vdate=r.V_Date)
                db.execute("DELETE FROM LEDGERREF WHERE DocId = ?",
                           (td,), cn=cn, commit=False)
                db.execute("DELETE FROM LEDGERTDS WHERE DocId = ?",
                           (td,), cn=cn, commit=False)
                db.execute(
                    "DELETE FROM LEDGERADJ WHERE DocId1 = ? OR DocId2 = ?",
                    (td, td), cn=cn, commit=False)
                _log_voucher(cn, td, "D", user)
                db.execute("DELETE FROM Ledger WHERE DocId = ?",
                           (td,), cn=cn, commit=False)
                db.execute("DELETE FROM LedgerM WHERE DocId = ?",
                           (td,), cn=cn, commit=False)
            except Exception:
                pass
        # Log before delete
        _log_voucher(cn, docid, "D", user)
        # Delete Ledger lines + header in same transaction
        n = db.execute("DELETE FROM Ledger WHERE DocId = ?", (docid,),
                       cn=cn, commit=False)
        db.execute("DELETE FROM LedgerM WHERE DocId = ?", (docid,),
                   cn=cn, commit=False)
        if commit:
            cn.commit()
        return n
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


def get_voucher(docid: str, cn=None) -> dict | None:
    """FA-8: header + lines for edit/display (LedgerM preferred, Ledger fallback) with LOGSITE filter."""
    sc_site = _site()
    hm = db.query(
        "SELECT DocId, V_Type, v_Prefix, V_No, V_Date, Narration "
        "FROM LedgerM WHERE DocId = ? AND LogSite_Code = ?", (docid, sc_site), cn=cn)
    if not hm:
        # HO fallback for voucher header
        hm = db.query(
            "SELECT DocId, V_Type, v_Prefix, V_No, V_Date, Narration "
            "FROM LedgerM WHERE DocId = ? AND (LogSite_Code = ? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='')", (docid, sc_site), cn=cn)
    if hm:
        h = hm[0]
        hdr = {"docid": h[0], "vtype": h[1] or "", "v_prefix": h[2] or "",
               "vno": int(h[3] or 0), "vdate": h[4],
               "narration": (h[5] or "").strip()}
    else:
        rows = db.query(
            "SELECT TOP 1 DocId, V_Type, v_Prefix, V_No, V_Date, Narration "
            "FROM Ledger WHERE DocId = ? AND (LogSite_Code = ? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='') ORDER BY V_SNo",
            (docid, sc_site), cn=cn)
        if not rows:
            return None
        h = rows[0]
        hdr = {"docid": h[0], "vtype": h[1] or "", "v_prefix": h[2] or "",
               "vno": int(h[3] or 0), "vdate": h[4],
               "narration": (h[5] or "").strip()}
    lrows = db.query(
        "SELECT V_SNo, SubCode, AmtDr, AmtCr, Narration, Chq_No, Chq_Date, "
        "AgRefNo FROM Ledger WHERE DocId = ? AND (LogSite_Code = ? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='') ORDER BY V_SNo",
        (docid, sc_site), cn=cn)
    lines = []
    chq_no, chq_date = "", None
    for r in lrows:
        if not chq_no and (r[5] or "").strip():
            chq_no = r[5] or ""
            chq_date = r[6]
        lines.append({"sno": int(r[0] or 0), "subcode": (r[1] or "").strip(),
                      "amt_dr": float(r[2] or 0), "amt_cr": float(r[3] or 0),
                      "narration": (r[4] or "").strip(),
                      "agrefno": (r[7] or "").strip()})
    hdr["lines"] = lines
    hdr["chq_no"] = chq_no
    hdr["chq_date"] = chq_date
    hdr["dr"] = sum(x["amt_dr"] for x in lines)
    hdr["cr"] = sum(x["amt_cr"] for x in lines)
    return hdr


def find_voucher(vtype: str | None = None, vno: int | None = None,
                 d_from=None, d_to=None, narration: str | None = None,
                 docid: str | None = None, cn=None) -> list[dict]:
    """FA-8: search vouchers (type/no/date/narration/docid) with LOGSITE scoping."""
    sc_site = _site()
    sql = ("SELECT DocId, V_Type, v_Prefix, V_No, V_Date, "
           "MAX(Narration) AS Narration, SUM(AmtDr), SUM(AmtCr) "
           "FROM Ledger WHERE LogSite_Code = ?")
    params: list = [sc_site]
    if docid:
        sql += " AND DocId = ?"
        params.append(docid)
    if vtype:
        sql += " AND V_Type = ?"
        params.append(vtype)
    if vno is not None:
        sql += " AND V_No = ?"
        params.append(int(vno))
    if d_from is not None:
        sql += " AND V_Date >= ?"
        params.append(d_from)
    if d_to is not None:
        sql += " AND V_Date <= ?"
        params.append(d_to)
    if narration:
        sql += " AND Narration LIKE ?"
        params.append(f"%{narration}%")
    sql += (" GROUP BY DocId, V_Type, v_Prefix, V_No, V_Date "
            "ORDER BY V_Date DESC, DocId")
    rows = db.query(sql, tuple(params), cn=cn)
    return [{"docid": r[0], "vtype": r[1] or "", "v_prefix": r[2] or "",
             "vno": int(r[3] or 0), "vdate": r[4],
             "narration": (r[5] or "").strip(),
             "dr": float(r[6] or 0), "cr": float(r[7] or 0)}
            for r in rows]


def edit_voucher(docid: str, lines: list[dict], vdate=None,
                 narration: str | None = None, vtype: str | None = None,
                 user: str = USER, chq_no: str | None = None,
                 chq_date=None, cn=None, commit: bool = True) -> dict:
    """FA-8: edit = load + delete + repost on one connection (VB6 FaVrEnt)."""
    if not lines or len(lines) < 2:
        raise ValueError("Voucher me kam se kam 2 lines hone chahiye")
    _require_voucher_privilege(cn, 'E', user=user)
    own = cn is None
    cn = cn or db.connect()
    try:
        old = get_voucher(docid, cn=cn)
        if not old:
            raise ValueError(f"Voucher '{docid}' nahi mila")
        vtype = vtype or old["vtype"]
        vdate = vdate or old["vdate"]
        if narration is None:
            narration = old.get("narration", "")
        if chq_no is None:
            chq_no = old.get("chq_no", "")
        if chq_date is None:
            chq_date = old.get("chq_date")
        delete_voucher(docid, cn=cn, commit=False, user=user)
        res = post_voucher(lines, vdate, narration=narration or "",
                           vtype=vtype, user=user,
                           chq_no=chq_no or "", chq_date=chq_date,
                           cn=cn, commit=False)
        if commit:
            cn.commit()
        res["replaces"] = docid
        return res
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


# ------------------------------------------------------ cheque reconciliation
def cheque_pending(subcode: str | None = None, cn=None) -> list[dict]:
    """Un-cleared cheques (VB6 FaChqClear:1760 Clg_Date IS NULL filter) with LOGSITE scoping."""
    sc_site = _site()
    sql = ("SELECT l.DocId, l.V_SNo, l.V_Date, l.SubCode, s.Name, "
           "l.Chq_No, l.Chq_Date, l.AmtDr, l.AmtCr "
           "FROM Ledger l LEFT JOIN Subgroup s ON s.SubCode = l.SubCode "
           "WHERE l.Chq_No <> '' AND (l.Clg_Date IS NULL OR l.Clg_Date > "
           "GETDATE()) AND l.LogSite_Code = ?")
    params: list = [sc_site]
    if subcode:
        sql += " AND l.SubCode = ?"
        params.append(subcode)
    rows = db.query(sql + " ORDER BY l.V_Date", tuple(params), cn=cn)
    return [{"docid": r[0], "sno": r[1], "vdate": r[2], "subcode": r[3],
             "name": r[4], "chq_no": r[5], "chq_date": r[6],
             "amt_dr": r[7], "amt_cr": r[8]} for r in rows]


def cheque_cleared(subcode: str | None = None, cn=None) -> list[dict]:
    """Cleared cheques (VB6 FaChqClear:1752 Clg_Date <= today filter) with LOGSITE scoping."""
    sc_site = _site()
    sql = ("SELECT l.DocId, l.V_SNo, l.V_Date, l.SubCode, s.Name, "
           "l.Chq_No, l.Chq_Date, l.Clg_Date, l.AmtDr, l.AmtCr "
           "FROM Ledger l LEFT JOIN Subgroup s ON s.SubCode = l.SubCode "
           "WHERE l.Chq_No <> '' AND l.Clg_Date IS NOT NULL AND "
           "l.Clg_Date <= GETDATE() AND l.LogSite_Code = ?")
    params: list = [sc_site]
    if subcode:
        sql += " AND l.SubCode = ?"
        params.append(subcode)
    rows = db.query(sql + " ORDER BY l.Clg_Date DESC", tuple(params), cn=cn)
    return [{"docid": r[0], "sno": r[1], "vdate": r[2], "subcode": r[3],
             "name": r[4], "chq_no": r[5], "chq_date": r[6],
             "clg_date": r[7], "amt_dr": r[8], "amt_cr": r[9]} for r in rows]


def cheque_mark_cleared(docid: str, sno: int, clg_date=None,
                        chq_no=None, chq_date=None,
                        cn=None, commit: bool = True) -> int:
    """VB6 FaChqClear.frm:663 — Clg_Date + Chq_No + Chq_Date UPDATE.
    Params jo None hain unki existing Ledger value preserve hoti hai."""
    clg = clg_date or datetime.date.today()
    if isinstance(clg, str):
        clg = datetime.date.fromisoformat(clg)
    if isinstance(chq_date, str) and chq_date:
        chq_date = datetime.date.fromisoformat(chq_date)
    rows = db.query(
        "SELECT Chq_No, Chq_Date FROM Ledger WHERE DocId = ? AND V_SNo = ?",
        (docid, sno), cn=cn)
    old_chq = ((rows[0][0] if rows else "") or "")
    old_chq_date = rows[0][1] if rows else None
    new_chq = old_chq if chq_no is None else chq_no
    new_chq_date = old_chq_date if chq_date is None else chq_date
    return db.execute(
        "UPDATE Ledger SET Clg_Date = ?, Chq_No = ?, Chq_Date = ? "
        "WHERE DocId = ? AND V_SNo = ?",
        (clg, new_chq, new_chq_date, docid, sno), cn=cn, commit=commit)


# ------------------------------------------------------------- statements
def trial_balance(d_from=None, d_to=None, cn=None) -> list[dict]:
    """Group-wise trial balance (Ledger grouped by GroupCode) with LOGSITE scoping."""
    sc_site = _site()
    sql = ("SELECT l.GroupCode, a.GroupName, a.GroupNature, "
           "SUM(l.AmtDr) AS Dr, SUM(l.AmtCr) AS Cr, "
           "SUM(l.AmtDr) - SUM(l.AmtCr) AS Bal "
           "FROM Ledger l LEFT JOIN Acgroup a ON a.GroupCode = l.GroupCode WHERE l.LogSite_Code = ?")
    params: list = [sc_site]
    if d_from and d_to:
        sql += " AND l.V_Date BETWEEN ? AND ?"
        params.extend([d_from, d_to])
    rows = db.query(sql + " GROUP BY l.GroupCode, a.GroupName, "
                         "a.GroupNature ORDER BY l.GroupCode", tuple(params), cn=cn)
    return [{"groupcode": r[0], "groupname": r[1] or "?",
             "nature": r[2] or "", "dr": r[3] or 0.0, "cr": r[4] or 0.0,
             "bal": r[5] or 0.0} for r in rows]


def profit_and_loss(d_from, d_to, cn=None) -> dict:
    """P&L: Revenue (R) = Cr-Dr; Expenses (E) = Dr-Cr (GroupNature signs) with LOGSITE."""
    sc_site = _site()
    rows = db.query(
        "SELECT a.GroupNature, l.GroupCode, a.GroupName, "
        "SUM(l.AmtDr) AS DrTot, SUM(l.AmtCr) AS CrTot "
        "FROM Ledger l JOIN Acgroup a ON a.GroupCode = l.GroupCode "
        "WHERE l.LogSite_Code = ? AND l.V_Date BETWEEN ? AND ? AND a.GroupNature IN ('E', 'R') "
        "GROUP BY a.GroupNature, l.GroupCode, a.GroupName "
        "ORDER BY a.GroupNature, l.GroupCode", (sc_site, d_from, d_to), cn=cn)
    income = []
    expense = []
    for r in rows:
        dr = float(r[3] or 0)
        cr = float(r[4] or 0)
        if r[0] == "R":
            income.append({"groupcode": r[1], "name": r[2],
                           "amount": cr - dr})
        else:
            expense.append({"groupcode": r[1], "name": r[2],
                            "amount": dr - cr})
    ti = sum(i["amount"] for i in income)
    te = sum(e["amount"] for e in expense)
    return {"income": income, "expense": expense,
            "total_income": ti, "total_expense": te, "net": ti - te}


def balance_sheet(as_on=None, cn=None) -> dict:
    """Balance sheet: Assets (A) vs Liabilities (L) group-wise with LOGSITE."""
    sc_site = _site()
    rows = db.query(
        "SELECT a.GroupNature, l.GroupCode, a.GroupName, "
        "SUM(l.AmtDr) - SUM(l.AmtCr) AS Bal "
        "FROM Ledger l JOIN Acgroup a ON a.GroupCode = l.GroupCode "
        "WHERE l.LogSite_Code = ? AND (? IS NULL OR l.V_Date <= ?) AND a.GroupNature IN ('A', 'L') "
        "GROUP BY a.GroupNature, l.GroupCode, a.GroupName "
        "ORDER BY a.GroupNature, l.GroupCode",
        (sc_site, as_on, as_on), cn=cn)
    assets = [{"groupcode": r[1], "name": r[2], "amount": r[3] or 0.0}
              for r in rows if r[0] == "A"]
    liab = [{"groupcode": r[1], "name": r[2], "amount": r[3] or 0.0}
            for r in rows if r[0] == "L"]
    return {"assets": assets, "liab": liab,
            "total_assets": sum(a["amount"] for a in assets),
            "total_liab": sum(l["amount"] for l in liab)}


def bank_register(d_from, d_to, cn=None) -> list[dict]:
    """Bank-book style register (Subgroup name LIKE %BANK%) with LOGSITE."""
    sc_site = _site()
    rows = db.query(
        "SELECT l.V_Date, l.DocId, s.Name, l.Chq_No, l.AmtDr, l.AmtCr "
        "FROM Ledger l JOIN Subgroup s ON s.SubCode = l.SubCode "
        "WHERE l.LogSite_Code = ? AND (s.Name LIKE '%BANK%') AND l.V_Date BETWEEN ? AND ? "
        "ORDER BY l.V_Date, l.DocId", (sc_site, d_from, d_to), cn=cn)
    return [{"vdate": r[0], "docid": r[1], "account": r[2],
             "chq_no": r[3] or "", "dr": r[4] or 0.0, "cr": r[5] or 0.0}
            for r in rows]


def cash_and_bank_books(d_from, d_to, cn=None) -> list[dict]:
    sc_site = _site()
    rows = db.query(
        "SELECT l.V_Date, l.DocId, s.Name, l.Chq_No, l.AmtDr, l.AmtCr "
        "FROM Ledger l JOIN Subgroup s ON s.SubCode = l.SubCode "
        "WHERE l.LogSite_Code = ? AND (s.Name LIKE '%BANK%' OR s.Name LIKE '%CASH%') "
        "AND l.V_Date BETWEEN ? AND ? ORDER BY l.V_Date, l.DocId",
        (sc_site, d_from, d_to), cn=cn)
    return [{"vdate": r[0], "docid": r[1], "account": r[2],
             "chq_no": r[3] or "", "dr": r[4] or 0.0, "cr": r[5] or 0.0}
            for r in rows]


def journal_book(d_from, d_to, cn=None) -> list[dict]:
    """Journal vouchers by type (live V_Type census basis) with LOGSITE."""
    sc_site = _site()
    rows = db.query(
        "SELECT l.DocId, l.V_Type, l.V_Date, COUNT(*) AS Lines, "
        "SUM(l.AmtDr) AS Dr, SUM(l.AmtCr) AS Cr "
        "FROM Ledger l WHERE l.LogSite_Code = ? AND l.V_Date BETWEEN ? AND ? "
        "GROUP BY l.DocId, l.V_Type, l.V_Date ORDER BY l.V_Date, l.DocId",
        (sc_site, d_from, d_to), cn=cn)
    return [{"docid": r[0], "vtype": r[1], "vdate": r[2], "lines": r[3],
             "dr": r[4] or 0.0, "cr": r[5] or 0.0} for r in rows]


def daily_transaction_summary(d_from, d_to, cn=None) -> list[dict]:
    sc_site = _site()
    rows = db.query(
        "SELECT V_Date, COUNT(DISTINCT DocId) AS Vouchers, SUM(AmtDr) AS Dr, "
        "SUM(AmtCr) AS Cr FROM Ledger WHERE LogSite_Code = ? AND V_Date BETWEEN ? AND ? "
        "GROUP BY V_Date ORDER BY V_Date", (sc_site, d_from, d_to), cn=cn)
    return [{"vdate": r[0], "vouchers": r[1], "dr": r[2] or 0.0,
             "cr": r[3] or 0.0} for r in rows]
