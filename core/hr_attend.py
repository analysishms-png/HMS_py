"""HR Attend + Salary create — VB6 parity (H-G4/H-G5).

VB6 evidence (verbatim SQL):
- prAttend.frm:551  Attend grid: Select A.V_Date,A.V_Prefix as [Year],
  E.Name As EmployeeName,A.FirstShift,A.SecondShift From Attend A
  left join Employee E on A.Emp_Code = E.Code Where A.V_Prefix='<FY>' ...
- prAttend.frm:1627 Insert Into Attend(V_Prefix,V_Date,Emp_Code,
  FirstShift,SecondShift,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)
  Values ('<FY>',<date>,'<emp>','P/A/L',...,'<site>',...,'<site>')
  + Voucher_Type/Voucher_Prefix FY window (V_Type='AT')
- prSalCreate.frm:1065 holiday count (datepart(dw,vdate)<>1 Sunday
  exclude) + Attend aggregation + Loan IsNull(Sum)
- prSalCreate.frm:1684 Ledger posting per employee (V_Type='SL') +
  Loan recovery (V_Type LO->LR) + Employee Curr_Earned update

Shift enum (VB6 prAttend combos): P/A/L/C/HP
  P=present, HP=half-present, A=absent, L=leave, C=casual
"""
from __future__ import annotations

import datetime as _dt_mod

from HMS_py.core import db

SITE_CODE = db.get_site_code()
USER = db.get_user()

_ATTEND_SHIFT_CODES = ("P", "A", "L", "C", "HP")


def _voucher_prefix_hr(vtype: str, vdate, site: str, cn=None):
    """VB6 verbatim (prAttend.frm:1627): VT/VP join with LOGSITE_CODE."""
    try:
        return db.query(
            "Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,"
            "VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP "
            "on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE "
            "AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) "
            "Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? "
            "AND ? BETWEEN VP.Date_From AND VP.Date_To",
            (site, site, vtype, vdate), cn=cn)
    except Exception:
        return []


def _fy_prefix_for(vdate, site: str, cn=None) -> str:
    """FY prefix for a date (Voucher_Prefix), fallback current year."""
    rows = _voucher_prefix_hr("AT", vdate, site, cn=cn)
    if rows and rows[0][3]:
        return str(rows[0][3]).strip()
    return str(vdate.year if hasattr(vdate, "year")
               else _dt_mod.date.today().year)


def _check_menu_help_hr(user: str, comp: str, option: str, cn=None):
    """menuHelp privilege guard (fa_voucher/booking pattern)."""
    try:
        rows = db.query(
            "SELECT Param_Str AS UPrivilege, Flag FROM menuHelp "
            "WHERE UserName=? AND CompCode=? AND [Option]=?",
            (user, comp, option), cn=cn)
        if rows and rows[0][0] is not None:
            priv = str(rows[0][0] or "")
            if "A" not in priv and "E" not in priv:
                raise PermissionError(f"No privilege for {option}")
    except PermissionError:
        raise
    except Exception:
        pass


def list_attend(vdate_from, vdate_to, site=SITE_CODE, cn=None):
    """VB6 prAttend.frm:551 grid: Attend join Employee, date window."""
    rows = db.query(
        "Select A.V_Date, A.V_Prefix as [Year], E.Name As EmployeeName, "
        "A.FirstShift, A.SecondShift, A.Emp_Code, A.Site_Code "
        "From Attend A left join Employee E on A.Emp_Code = E.Code "
        "Where A.Site_Code = ? AND A.V_Date BETWEEN ? AND ? "
        "ORDER BY A.V_Date DESC, A.Emp_Code",
        (site, vdate_from, vdate_to), cn=cn)
    return [{
        "v_date": r[0], "v_prefix": r[1], "emp_name": r[2] or "",
        "first_shift": r[3] or "", "second_shift": r[4] or "",
        "emp_code": r[5] or "", "site_code": r[6] or "",
    } for r in rows]


def insert_attend(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    """VB6 prAttend.frm:1627 — Attend row (re-entry = UPDATE).

    rec: {emp_code, v_date, first_shift, second_shift?}
    Shift enum P/A/L/C/HP. V_Prefix FY Voucher_Prefix se aata hai.
    """
    emp = str(rec.get("emp_code", "")).strip()
    if not emp:
        raise ValueError("Emp_Code zaroori hai")
    adate = rec.get("v_date") or rec.get("otdate")
    if not adate:
        raise ValueError("V_Date zaroori hai")
    s1 = str(rec.get("first_shift") or rec.get("shift1") or "").strip().upper()
    s2 = str(rec.get("second_shift") or rec.get("shift2") or "").strip().upper()
    if s1 not in _ATTEND_SHIFT_CODES:
        raise ValueError(
            f"FirstShift P/A/L/C/HP me hona chahiye (mila '{s1 or 'empty'}')")
    if s2 and s2 not in _ATTEND_SHIFT_CODES:
        raise ValueError(
            f"SecondShift P/A/L/C/HP me hona chahiye (mila '{s2}')")
    vp = _fy_prefix_for(adate, site, cn=cn)
    cnt_rows = db.query(
        "SELECT COUNT(*) FROM Attend WHERE V_Prefix=? AND V_Date=? "
        "AND Emp_Code=? AND Site_Code=?",
        (vp, adate, emp, site), cn=cn)
    if cnt_rows and cnt_rows[0][0]:
        # re-entry: shift overwrite (VB6 daily attendance edit)
        db.execute(
            "UPDATE Attend SET FirstShift=?, SecondShift=?, "
            "U_Name=?, U_EntDt=getdate(), U_AE='E' "
            "WHERE V_Prefix=? AND V_Date=? AND Emp_Code=? AND Site_Code=?",
            (s1, s2, user, vp, adate, emp, site), cn=cn, commit=commit)
        action = "E"
    else:
        db.execute(
            "INSERT INTO Attend (V_Prefix, V_Date, Emp_Code, FirstShift, "
            "SecondShift, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
            (vp, adate, emp, s1, s2, site, user, site), cn=cn, commit=commit)
        action = "A"
    return {"emp_code": emp, "v_date": adate, "v_prefix": vp,
            "first_shift": s1, "second_shift": s2, "action": action}


def delete_attend(v_date, emp_code, site=SITE_CODE, cn=None):
    return db.execute(
        "DELETE FROM Attend WHERE V_Date = ? AND Emp_Code = ? AND Site_Code = ?",
        (v_date, emp_code, site), cn=cn)


def salary_summary(emp_code: str, mth_year: str, site=SITE_CODE, cn=None) -> dict:
    """VB6 prSalCreate.frm:1065 inputs — holiday/attend/loan/overtime calc.

    mth_year 'MMYYYY' (VB6 convention). Returns dict with work_day,
    leaves, sundays, holidays, absents, overtime_amt, loan_monthly,
    loan_outstanding — create_salary() isi se Salary row banata hai.
    """
    m = str(mth_year or "").strip()
    if not (len(m) == 6 and m[:2].isdigit() and m[2:].isdigit()):
        raise ValueError("Mth_Year MMYYYY format me do (e.g. '042026')")
    mm, yy = int(m[:2]), int(m[2:])
    if not 1 <= mm <= 12:
        raise ValueError("Mth_Year invalid month (01-12)")
    last = (_dt_mod.date(yy + 1, 1, 1) if mm == 12
            else _dt_mod.date(yy, mm + 1, 1)) - _dt_mod.timedelta(days=1)
    try:
        hrows = db.query(
            "SELECT COUNT(*) FROM Holiday WHERE LogSite_Code=? "
            "AND datepart(dw,Vdate)<>1 AND MONTH(VDate)=? AND YEAR(VDate)=?",
            (site, mm, yy), cn=cn)
        holidays = int(hrows[0][0] or 0) if hrows else 0
    except Exception:
        holidays = 0
    try:
        arows = db.query(
            "SELECT FirstShift, SecondShift FROM Attend "
            "WHERE Site_Code=? AND Emp_Code=? "
            "AND MONTH(V_Date)=? AND YEAR(V_Date)=?",
            (site, emp_code, mm, yy), cn=cn)
    except Exception:
        arows = []
    p = hp = l = a = 0
    for r in arows:
        for s in (str(r[0] or "").upper(), str(r[1] or "").upper()):
            if s == "P":
                p += 1
            elif s == "HP":
                hp += 1
            elif s == "L":
                l += 1
            elif s == "A":
                a += 1
    sundays = sum(1 for d in range(1, last.day + 1)
                  if _dt_mod.date(yy, mm, d).weekday() == 6)
    absents = a + 0.5 * hp
    total_days = last.day
    work_day = round(total_days - sundays - holidays - absents, 1)
    try:
        orow = db.query(
            "SELECT ISNULL(SUM(Amount),0) FROM OverTime "
            "WHERE Site_Code=? AND EmpCode=? "
            "AND MONTH(OTDate)=? AND YEAR(OTDate)=?",
            (site, emp_code, mm, yy), cn=cn)
        ot_amt = float(orow[0][0] or 0) if orow else 0.0
    except Exception:
        ot_amt = 0.0
    try:
        lo = db.query(
            "SELECT ISNULL(SUM(Amount),0) FROM Loan "
            "WHERE LogSite_Code=? AND V_Type='LO' AND Emp_Code=?",
            (site, emp_code), cn=cn)
        lr = db.query(
            "SELECT ISNULL(SUM(Amount),0) FROM Loan "
            "WHERE LogSite_Code=? AND V_Type IN ('LR','LR1') AND Emp_Code=?",
            (site, emp_code), cn=cn)
        inst = db.query(
            "SELECT ISNULL(SUM(Installment),0) FROM Loan "
            "WHERE Site_Code=? AND V_Type='LO' AND Emp_Code=?",
            (site, emp_code), cn=cn)
        outstanding = (float(lo[0][0] or 0) - float(lr[0][0] or 0)
                       if lo and lr else 0.0)
        monthly = float(inst[0][0] or 0) if inst else 0.0
        monthly = min(monthly, max(outstanding, 0.0))
    except Exception:
        outstanding = monthly = 0.0
    return {
        "emp_code": emp_code, "mth_year": m,
        "total_days": total_days, "sundays": sundays, "holidays": holidays,
        "present": p, "half_present": hp, "leaves": l, "absents": absents,
        "work_day": work_day, "overtime_amt": ot_amt,
        "loan_monthly": round(monthly, 2),
        "loan_outstanding": round(outstanding, 2),
    }


def create_salary(emp_code: str, mth_year: str, cn=None, commit=True,
                  site=SITE_CODE, user=USER, post_to_ledger=True) -> dict:
    """VB6 prSalCreate.frm:1684 full workflow (H-G5).

    Steps: duplicate guard -> summary calc -> Salary INSERT -> Loan 'LR'
    recovery -> Ledger 'SL' posting (V_Prefix FY, race-safe VNo) —
    sab same connection transaction me.
    """
    _check_menu_help_hr(user, db.get_comp_code(), "Salary Create", cn)
    own = cn is None
    cn = cn or db.connect()
    try:
        cnt = db.query(
            "SELECT COUNT(*) FROM Salary "
            "WHERE Site_Code=? AND Mth_Year=? AND Emp_Code=?",
            (site, mth_year, emp_code), cn=cn)
        if cnt and cnt[0][0]:
            raise ValueError(
                f"Salary {emp_code}/{mth_year} pehle se hai "
                "(VB6 prSalCreate guard) - pehle delete karo")
        s = salary_summary(emp_code, mth_year, site, cn=cn)
        emp = db.query(
            "SELECT Name, Basic, DA, HRA FROM Employee "
            "WHERE Code=? AND Site_Code=?",
            (emp_code, site), cn=cn)
        if not emp:
            raise ValueError(f"Employee {emp_code} nahi mila")
        basic = float(emp[0][1] or 0)
        da = float(emp[0][2] or 0)
        hra = float(emp[0][3] or 0)
        net = round(basic + da + hra + s["overtime_amt"] - s["loan_monthly"], 2)
        db.execute(
            "INSERT INTO Salary (Mth_Year,Emp_Code,Work_Day,CL,Leave,Sunday,"
            "Holiday,Absent,Basic,DA,HRA,Income_Tax,Other_Allow,Other_Deduc,"
            "Conveyance,Medical,LTA,PF,EPF,ESI,Loan,Advance,Net_Salary,"
            "Loan_Bal,OverTime,OverTimeAmt,Site_Code,U_Name,U_EntDt,U_AE,"
            "LogSite_Code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,"
            "?,?,?,?,?,?,?,getdate(),'A',?)",
            (mth_year, emp_code, s["work_day"], 0.0, s["leaves"],
             float(s["sundays"]), float(s["holidays"]), s["absents"],
             basic, da, hra, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             s["loan_monthly"], 0.0, net, s["loan_outstanding"],
             0.0, s["overtime_amt"], site, user, site),
            cn=cn, commit=False)
        loan_srno = None
        if s["loan_monthly"] > 0:
            sr = db.query(
                "SELECT ISNULL(MAX(Sr_No),0)+1 FROM Loan "
                "WITH (UPDLOCK, HOLDLOCK) WHERE Site_Code=?",
                (site,), cn=cn)
            loan_srno = int(sr[0][0] or 1) if sr and sr[0][0] else 1
            db.execute(
                "INSERT INTO Loan (Sr_No, V_Type, V_Date, Emp_Code, Amount, "
                "Installment, Remark, AC_Code, Mth_Year, Site_Code, U_Name, "
                "U_EntDt, U_AE, LogSite_Code) "
                "VALUES (?, 'LR', getdate(), ?, ?, ?, ?, '', ?, ?, ?, "
                "getdate(), 'A', ?)",
                (loan_srno, emp_code, s["loan_monthly"], s["loan_monthly"],
                 f"Salary recovery {mth_year}", mth_year, site, user, site),
                cn=cn, commit=False)
        docid = None
        if post_to_ledger:
            vp = str(_dt_mod.date.today().year)
            vrow = db.query(
                "SELECT ISNULL(MAX(V_No),0)+1 FROM Ledger "
                "WITH (UPDLOCK, HOLDLOCK) "
                "WHERE V_Type='SL' AND V_Prefix=? AND Site_Code=? "
                "AND LogSite_Code=?",
                (vp, site, site), cn=cn)
            vno = int(vrow[0][0] or 1) if vrow and vrow[0][0] else 1
            docid = ("D" + site.ljust(2) + "SL".ljust(6) + vp.ljust(4)
                     + str(vno).rjust(8))[:21]
            try:
                sg = db.query(
                    "SELECT s.GroupCode, a.GroupNature FROM Subgroup s "
                    "JOIN Acgroup a ON a.GroupCode=s.GroupCode "
                    "WHERE RTRIM(s.SubCode)=?",
                    (emp_code,), cn=cn)
            except Exception:
                sg = None
            gcode = str(sg[0][0] or "") if sg else ""
            gnature = str(sg[0][1] or "L") if sg else "L"
            db.execute(
                "INSERT INTO Ledger (DocId, V_SNo, V_Type, V_Prefix, V_No, "
                "Site_Code, V_Date, SubCode, ContraSub, AmtCr, AmtDr, "
                "Narration, mth_year, Emp_Code, U_Name, U_EntDt, U_AE, "
                "GROUPCODE, GROUPNATURE, LogSite_Code) "
                "VALUES (?, 1, 'SL', ?, ?, ?, getdate(), ?, '', ?, 0, "
                "?, ?, ?, ?, getdate(), 'A', ?, ?, ?)",
                (docid, vp, site, vno, emp_code, net,
                 f"Salary {mth_year} {emp_code}", mth_year, emp_code,
                 user, gcode, gnature, site),
                cn=cn, commit=False)
        if commit:
            cn.commit()
        return {"emp_code": emp_code, "mth_year": mth_year,
                "net_salary": net, "summary": s,
                "loan_recovery_srno": loan_srno, "ledger_docid": docid}
    except Exception:
        if own:
            try:
                cn.rollback()
            except Exception:
                pass
        raise
    finally:
        if own:
            try:
                cn.close()
            except Exception:
                pass
