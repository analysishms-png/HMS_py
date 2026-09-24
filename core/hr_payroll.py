"""HR/Payroll - Salary, Attendence, Loan, Leave_Ench, OverTime CRUD."""
from __future__ import annotations
from HMS_py.core import db
def _logsite(cn=None):
    try:
        return db.get_logsite_code(cn=cn)
    except Exception:
        return db.get_site_code()

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")
USER = db.get_user()

# === Salary ===
def _map_salary(r) -> dict:
    try:
        return {"mth_year": r.Mth_Year or "", "emp_code": r.Emp_Code or "", "work_day": r.Work_Day or 0.0, "cl": r.CL or 0.0, "leave": r.Leave or 0.0, "sunday": r.Sunday or 0.0, "holiday": r.Holiday or 0.0, "absent": r.Absent or 0.0, "basic": r.Basic or 0.0, "da": r.DA or 0.0, "hra": r.HRA or 0.0, "net_salary": r.Net_Salary or 0.0, "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"Emp_Code": str(r[0] or "")}


def list_salary(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Salary WHERE Site_Code = ? ORDER BY Emp_Code DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_salary(r) for r in rows]


def get_salary(Mth_Year, Emp_Code, cn=None):
    rows = db.query("SELECT * FROM Salary WHERE Mth_Year = ? AND Emp_Code = ?", (Mth_Year, Emp_Code), cn=cn)
    return _map_salary(rows[0]) if rows else None


def search_salary(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Salary WHERE Site_Code = ? AND (Emp_Code LIKE ? OR Mth_Year LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_salary(r) for r in rows]


def insert_salary(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # varchar Emp_Code par MAX()+1 int crash karta tha — PK Mth_Year+Emp_Code hai
    new_pk = rec.get("emp_code", "")
    db.execute(
        "INSERT INTO Salary (Mth_Year,Emp_Code,Work_Day,CL,Leave,Sunday,Holiday,Absent,Basic,DA,HRA,Income_Tax,Other_Allow,Other_Deduc,Conveyance,Medical,LTA,PF,EPF,ESI,Loan,Advance,Net_Salary,Loan_Bal,OverTime,OverTimeAmt,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)",
        (rec.get("mth_year",""), rec.get("emp_code",""), rec.get("work_day",0.0), rec.get("cl",0.0), rec.get("leave",0.0), rec.get("sunday",0.0), rec.get("holiday",0.0), rec.get("absent",0.0), rec.get("basic",0.0), rec.get("da",0.0), rec.get("hra",0.0), rec.get("income_tax",0.0), rec.get("other_allow",0.0), rec.get("other_deduc",0.0), rec.get("conveyance",0.0), rec.get("medical",0.0), rec.get("lta",0.0), rec.get("pf",0.0), rec.get("epf",0.0), rec.get("esi",0.0), rec.get("loan",0.0), rec.get("advance",0.0), rec.get("net_salary",0.0), rec.get("loan_bal",0.0), rec.get("overtime",0.0), rec.get("overtime_amt",0.0), site, user, site),
        cn=cn, commit=commit)
    return get_salary(rec.get("mth_year",""), new_pk, cn=cn)


def delete_salary(Mth_Year, Emp_Code, cn=None, commit=True):
    return db.execute("DELETE FROM Salary WHERE Mth_Year = ? AND Emp_Code = ?", (Mth_Year, Emp_Code), cn=cn, commit=commit)

# === Attendence ===
def _map_attendence(r) -> dict:
    try:
        return {"mth_year": r.Mth_Year or "", "emp_code": r.Emp_Code or "", "attn_str": r.Attn_Str or "", "site_code": r.Site_Code or ""}
    except AttributeError:
        return {"Emp_Code": str(r[0] or "")}


def list_attendence(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Attendence WHERE Site_Code = ? ORDER BY Emp_Code DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_attendence(r) for r in rows]


def get_attendence(Mth_Year, Emp_Code, cn=None):
    rows = db.query("SELECT * FROM Attendence WHERE Mth_Year = ? AND Emp_Code = ?", (Mth_Year, Emp_Code), cn=cn)
    return _map_attendence(rows[0]) if rows else None


def search_attendence(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Attendence WHERE Site_Code = ? AND (Emp_Code LIKE ? OR Mth_Year LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_attendence(r) for r in rows]


def insert_attendence(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # varchar Emp_Code par MAX()+1 int crash karta tha — PK Mth_Year+Emp_Code hai
    new_pk = rec.get("emp_code", "")
    db.execute(
        "INSERT INTO Attendence (Mth_Year,Emp_Code,Attn_Str,Site_Code,LogSite_Code) VALUES (?,?,?,?,?)",
        (rec.get("mth_year",""), rec.get("emp_code",""), rec.get("attn_str",""), site, site),
        cn=cn, commit=commit)
    return get_attendence(rec.get("mth_year",""), new_pk, cn=cn)


def delete_attendence(Mth_Year, Emp_Code, cn=None, commit=True):
    return db.execute("DELETE FROM Attendence WHERE Mth_Year = ? AND Emp_Code = ?", (Mth_Year, Emp_Code), cn=cn, commit=commit)

# === Loan ===
def _map_loan(r) -> dict:
    try:
        return {"sr_no": r.Sr_No or 0, "v_type": r.V_Type or "", "v_date": r.V_Date, "emp_code": r.Emp_Code or "", "amount": r.Amount or 0.0, "installment": r.Installment or 0.0, "remark": r.Remark or "", "ac_code": r.AC_Code or "", "mth_year": r.Mth_Year or "", "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"Sr_No": str(r[0] or "")}


def list_loan(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Loan WHERE Site_Code = ? ORDER BY Sr_No DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_loan(r) for r in rows]


def get_loan(Sr_No, cn=None):
    rows = db.query("SELECT * FROM Loan WHERE Sr_No = ?", (Sr_No,), cn=cn)
    return _map_loan(rows[0]) if rows else None


def search_loan(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Loan WHERE Site_Code = ? AND (Emp_Code LIKE ? OR Remark LIKE ?)",
                    (SITE_CODE, f"%{term}%", f"%{term}%"), cn=cn)
    return [_map_loan(r) for r in rows]


def insert_loan(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    code_rows = db.query("SELECT MAX(Sr_No) FROM Loan", cn=cn)
    new_pk = (code_rows[0][0] or 0) + 1 if code_rows and code_rows[0][0] else 1
    # 14 columns = 10 params + 4 literals ('LD', getdate(), getdate(), 'A')
    db.execute(
        "INSERT INTO Loan (Sr_No, V_Type, V_Date, Emp_Code, Amount, Installment, "
        "Remark, AC_Code, Mth_Year, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) "
        "VALUES (?, 'LD', getdate(), ?, ?, ?, ?, ?, ?, ?, ?, getdate(), 'A', ?)",
        (new_pk,
         rec.get("emp_code", ""),
         rec.get("amount", 0.0),
         rec.get("installment", 0.0),
         rec.get("remark", ""),
         rec.get("ac_code", ""),
         rec.get("mth_year", ""),
         site,
         user,
         site),
        cn=cn, commit=commit)
    return get_loan(new_pk, cn=cn)


def delete_loan(Sr_No, cn=None, commit=True):
    return db.execute("DELETE FROM Loan WHERE Sr_No = ?", (Sr_No,), cn=cn, commit=commit)

# === Leave_Ench ===
def _map_leave_ench(r) -> dict:
    try:
        return {"sr_no": r.Sr_No or 0, "l_date": r.L_Date, "emp_code": r.Emp_Code or "", "leave_ench": r.Leave_Ench or 0.0, "amt_ench": r.Amt_Ench or 0.0, "ac_code": r.AC_Code or "", "site_code": r.Site_Code or "", "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"Sr_No": str(r[0] or "")}


def list_leave_ench(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Leave_Ench WHERE Site_Code = ? ORDER BY Sr_No DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_leave_ench(r) for r in rows]


def get_leave_ench(Sr_No, cn=None):
    rows = db.query("SELECT * FROM Leave_Ench WHERE Sr_No = ?", (Sr_No,), cn=cn)
    return _map_leave_ench(rows[0]) if rows else None


def search_leave_ench(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM Leave_Ench WHERE Site_Code = ? AND (Emp_Code LIKE ?)",
                    (SITE_CODE, f"%{term}%"), cn=cn)
    return [_map_leave_ench(r) for r in rows]


def insert_leave_ench(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    code_rows = db.query("SELECT MAX(Sr_No) FROM Leave_Ench", cn=cn)
    new_pk = (code_rows[0][0] or 0) + 1 if code_rows and code_rows[0][0] else 1
    db.execute(
        "INSERT INTO Leave_Ench (Sr_No,L_Date,Emp_Code,Leave_Ench,Amt_Ench,AC_Code,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,?,?,getdate(),'A',?)",
        (new_pk, rec.get("l_date"), rec.get("emp_code",""), rec.get("leave_ench",0.0), rec.get("amt_ench",0.0), rec.get("ac_code",""), site, site),
        cn=cn, commit=commit)
    return get_leave_ench(new_pk, cn=cn)


def delete_leave_ench(Sr_No, cn=None, commit=True):
    return db.execute("DELETE FROM Leave_Ench WHERE Sr_No = ?", (Sr_No,), cn=cn, commit=commit)

# === OverTime ===
def _map_overtime(r) -> dict:
    try:
        return {"empcode": r.EmpCode or "", "otdate": r.OTDate, "otime": r.OTime or 0.0, "site_code": r.Site_Code or "", "amount": r.Amount or 0.0, "remark": r.Remark or "", "otrate": r.OTRate or 0.0, "u_name": r.U_Name or "", "u_ae": r.U_AE or ""}
    except AttributeError:
        return {"EmpCode": str(r[0] or "")}


def list_overtime(cn=None, limit=500):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM OverTime WHERE Site_Code = ? ORDER BY EmpCode DESC",
                    (SITE_CODE,), cn=cn)
    return [_map_overtime(r) for r in rows]


def get_overtime(EmpCode, cn=None):
    rows = db.query("SELECT * FROM OverTime WHERE EmpCode = ?", (EmpCode,), cn=cn)
    return _map_overtime(rows[0]) if rows else None


def search_overtime(term, cn=None, limit=100):
    rows = db.query(f"SELECT TOP {int(limit)} * FROM OverTime WHERE Site_Code = ? AND (EmpCode LIKE ?)",
                    (SITE_CODE, f"%{term}%"), cn=cn)
    return [_map_overtime(r) for r in rows]


def insert_overtime(rec, cn=None, commit=True, site=SITE_CODE, user=USER):
    # varchar EmpCode par MAX()+1 int crash karta tha — PK EmpCode+OTDate hai
    new_pk = rec.get("empcode", "")
    db.execute(
        "INSERT INTO OverTime (EmpCode,OTDate,OTime,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,Amount,Remark,OTRate) VALUES (?,getdate(),?,?,?,?,getdate(),'A',?,?,?)",
        (new_pk, rec.get("otime",0.0), site, user, site, rec.get("amount",0.0), rec.get("remark",""), rec.get("otrate",0.0)),
        cn=cn, commit=commit)
    return get_overtime(new_pk, cn=cn)


def delete_overtime(EmpCode, cn=None, commit=True):
    return db.execute("DELETE FROM OverTime WHERE EmpCode = ?", (EmpCode,), cn=cn, commit=commit)


class HRPayrollAPI:
    # H-G4/H-G5 VB6 Attend/Salary-create parity (hr_attend re-export)
    from HMS_py.core import hr_attend as _ha

    def list_attend(self, vfrom, vto, cn=None, site=SITE_CODE):
        return self._ha.list_attend(vfrom, vto, site=site, cn=cn)

    def insert_attend(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER):
        return self._ha.insert_attend(rec, cn=cn, commit=commit, site=site, user=user)

    def delete_attend(self, v_date, emp_code, cn=None, site=SITE_CODE):
        return self._ha.delete_attend(v_date, emp_code, site=site, cn=cn)

    def salary_summary(self, emp_code, mth_year, cn=None, site=SITE_CODE):
        return self._ha.salary_summary(emp_code, mth_year, site=site, cn=cn)

    def create_salary(self, emp_code, mth_year, cn=None, commit=True,
                      site=SITE_CODE, user=USER, post_to_ledger=True):
        return self._ha.create_salary(emp_code, mth_year, cn=cn, commit=commit,
                                      site=site, user=user,
                                      post_to_ledger=post_to_ledger)
    def list_salary(self, cn=None, limit=500): return list_salary(cn, limit)
    def get_salary(self, mth_year, emp_code, cn=None): return get_salary(mth_year, emp_code, cn)
    def search_salary(self, term, cn=None, limit=100): return search_salary(term, cn, limit)
    def insert_salary(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_salary(rec, cn, commit, site, user)
    def delete_salary(self, mth_year, emp_code, cn=None, commit=True): return delete_salary(mth_year, emp_code, cn, commit)
    def list_attendence(self, cn=None, limit=500): return list_attendence(cn, limit)
    def get_attendence(self, mth_year, emp_code, cn=None): return get_attendence(mth_year, emp_code, cn)
    def search_attendence(self, term, cn=None, limit=100): return search_attendence(term, cn, limit)
    def insert_attendence(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_attendence(rec, cn, commit, site, user)
    def delete_attendence(self, mth_year, emp_code, cn=None, commit=True): return delete_attendence(mth_year, emp_code, cn, commit)
    def list_loan(self, cn=None, limit=500): return list_loan(cn, limit)
    def get_loan(self, sr_no, cn=None): return get_loan(sr_no, cn)
    def search_loan(self, term, cn=None, limit=100): return search_loan(term, cn, limit)
    def insert_loan(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_loan(rec, cn, commit, site, user)
    def delete_loan(self, sr_no, cn=None, commit=True): return delete_loan(sr_no, cn, commit)
    def list_leave_ench(self, cn=None, limit=500): return list_leave_ench(cn, limit)
    def get_leave_ench(self, sr_no, cn=None): return get_leave_ench(sr_no, cn)
    def search_leave_ench(self, term, cn=None, limit=100): return search_leave_ench(term, cn, limit)
    def insert_leave_ench(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_leave_ench(rec, cn, commit, site, user)
    def delete_leave_ench(self, sr_no, cn=None, commit=True): return delete_leave_ench(sr_no, cn, commit)
    def list_overtime(self, cn=None, limit=500): return list_overtime(cn, limit)
    def get_overtime(self, empcode, cn=None): return get_overtime(empcode, cn)
    def search_overtime(self, term, cn=None, limit=100): return search_overtime(term, cn, limit)
    def insert_overtime(self, rec, cn=None, commit=True, site=SITE_CODE, user=USER): return insert_overtime(rec, cn, commit, site, user)
    def delete_overtime(self, empcode, cn=None, commit=True): return delete_overtime(empcode, cn, commit)


# ============================================================
# Phase A (api-mismatch audit): UI hr_payroll_ui.py in update fns ko
# call karta tha par core me the hi nahi -> Edit buttons AttributeError.
# ============================================================
def update_salary(mth_year, emp_code, rec, cn=None, commit=True,
                  user=USER) -> dict:
    sets, params = [], []
    for fld in ("Work_Day", "CL", "Leave", "Sunday", "Holiday", "Absent",
                "Basic", "DA", "HRA", "Income_Tax", "Other_Allow",
                "Other_Deduc", "Conveyance", "Medical", "LTA", "PF", "EPF",
                "ESI", "Loan", "Advance", "Net_Salary", "Loan_Bal",
                "OverTime", "OverTimeAmt"):
        key = fld.lower()
        if key in rec:
            sets.append(fld + " = ?")
            params.append(float(rec[key] or 0))
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets += ["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"]
    params += [user, mth_year, emp_code]
    db.execute("UPDATE Salary SET " + ", ".join(sets) +
               " WHERE Mth_Year = ? AND Emp_Code = ?", params,
               cn=cn, commit=commit)
    return get_salary(mth_year, emp_code, cn=cn)


def update_attendence(emp_code, date_or_mth, rec, cn=None, commit=True,
                      user=USER) -> dict:
    # UI (Emp_Code, Date, rec) bhejta hai; DB key Mth_Year+Emp_Code hai.
    # Attn_Str = "In-Out-Status" composite (VB6 Attendence string pattern).
    attn = rec.get("attn_str")
    if attn is None:
        parts = [str(rec.get("intime", "") or ""),
                 str(rec.get("outtime", "") or ""),
                 str(rec.get("status", "") or "")]
        attn = "-".join(p for p in parts if p)
    mth = str(rec.get("mth_year") or "")
    d = str(date_or_mth or "")
    if not mth and len(d) >= 7 and d[4:5] == "-":
        mth = d[:7]
    db.execute(
        "UPDATE Attendence SET Attn_Str = ?, U_Name = ?, "
        "U_EntDt = getdate(), U_AE = 'E' WHERE Mth_Year = ? AND Emp_Code = ?",
        (attn, user, mth, emp_code), cn=cn, commit=commit)
    return get_attendence(mth, emp_code, cn=cn)


def update_loan(emp_code, sr_no, rec, cn=None, commit=True,
                user=USER) -> dict:
    sr = rec.get("sr_no", sr_no)
    sets, params = [], []
    if "amount" in rec:
        sets.append("Amount = ?"); params.append(float(rec["amount"] or 0))
    if "installment" in rec:
        sets.append("Installment = ?"); params.append(float(rec["installment"] or 0))
    if "remark" in rec:
        sets.append("Remark = ?"); params.append(str(rec["remark"] or ""))
    if "ac_code" in rec:
        sets.append("AC_Code = ?"); params.append(str(rec["ac_code"] or ""))
    if "mth_year" in rec:
        sets.append("Mth_Year = ?"); params.append(str(rec["mth_year"] or ""))
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets += ["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"]
    params += [user, sr]
    db.execute("UPDATE Loan SET " + ", ".join(sets) + " WHERE Sr_No = ?",
               params, cn=cn, commit=commit)
    return get_loan(sr, cn=cn)


def update_overtime(empcode, date_or_none, rec, cn=None, commit=True,
                    user=USER) -> dict:
    sets, params = [], []
    if "otime" in rec:
        sets.append("OTime = ?"); params.append(float(rec["otime"] or 0))
    if "otrate" in rec:
        sets.append("OTRate = ?"); params.append(float(rec["otrate"] or 0))
    if "amount" in rec:
        sets.append("Amount = ?"); params.append(float(rec["amount"] or 0))
    if "remark" in rec:
        sets.append("Remark = ?"); params.append(str(rec["remark"] or ""))
    if not sets:
        raise ValueError("Koi field update nahi diya")
    sets += ["U_Name = ?", "U_EntDt = getdate()", "U_AE = 'E'"]
    params += [user, empcode]
    db.execute("UPDATE OverTime SET " + ", ".join(sets) +
               " WHERE EmpCode = ?", params, cn=cn, commit=commit)
    return get_overtime(empcode, cn=cn)
def hr_attend_insert(emp_code: str, att_date, status: str, cn=None) -> int:
    """VB6 Attend table (not Attendence) - FirstShift/SecondShift enum Absent/Casual/Earned"""
    _valid = {"P","A","C","E","L","H"}
    if status not in _valid:
        raise ValueError(f"Status must be one of { _valid }")
    return db.execute("INSERT INTO Attend (EmployeeCode, AttendDate, Status, LogSite_Code) VALUES (?,?,?,?)", (emp_code, att_date, status, _logsite(cn) if 'def _logsite' in open(__file__, encoding='utf-8', errors='ignore').read() else db.get_site_code()), cn=cn)

def hr_delete_guards(emp_code: str, cn=None) -> bool:
    """VB6 6-table delete guard: Salary/Attend/Attendence/Loan/Leave_Ench/OverTime"""
    for tbl, col in [("Salary","EmployeeCode"),("Attend","EmployeeCode"),("Attendence","EmployeeCode"),("Loan","EmployeeCode"),("Leave_Ench","EmployeeCode"),("OverTime","EmployeeCode")]:
        rows = db.query(f"SELECT 1 FROM {tbl} WHERE {col}=?", (emp_code,), cn=cn)
        if rows:
            raise ValueError(f"Cannot delete {emp_code}: exists in {tbl}")
    return True
def hr_post_ledger_sl(emp_code: str, amount: float, vdate=None, cn=None) -> int:
    """VB6 Ledger SL posting: INSERT INTO Ledger (V_Type='SL', V_No via next_vno, Site_Code, LogSite_Code, SubCode=emp_code, AmtDr=amount)"""
    import datetime
    if vdate is None:
        vdate = datetime.date.today().isoformat()
    site = _logsite(cn)
    vprefix = db.get_vprefix()
    vno = db.next_vno("Ledger", "SL", vprefix, site=site, cn=cn)
    return db.execute("INSERT INTO Ledger (V_Type, V_No, Vprefix, VDate, SubCode, AmtDr, Site_Code, LogSite_Code) VALUES ('SL', ?, ?, ?, ?, ?, ?, ?)", (vno, vprefix, vdate, emp_code, amount, site, site), cn=cn)
def _count_holiday_non_sunday(from_date, to_date, cn=None) -> int:
    """VB6 Holiday DATEPART(dw)<>1 - Sunday=1, so exclude Sundays"""
    rows = db.query("SELECT COUNT(*) FROM Holiday WHERE HolidayDate BETWEEN ? AND ? AND DATEPART(dw, HolidayDate) <> 1 AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')", (from_date, to_date, db.get_site_code()), cn=cn)
    return int(rows[0][0] or 0) if rows else 0
def hr_loan_post(emp_code: str, loan_amt: float, cn=None) -> int:
    """VB6 Loan LO->LR: INSERT Loan (V_Type='LO', AmtDr=loan_amt) then Ledger LR posting via hr_post_ledger_sl"""
    site = _logsite(cn)
    vprefix = db.get_vprefix()
    vno = db.next_vno("Loan", "LO", vprefix, site=site, cn=cn)
    db.execute("INSERT INTO Loan (V_Type, V_No, Vprefix, EmployeeCode, AmtDr, Site_Code, LogSite_Code) VALUES ('LO', ?, ?, ?, ?, ?, ?)", (vno, vprefix, emp_code, loan_amt, site, site), cn=cn)
    # VB6: Ledger LR = Loan Repayment (deduction) -> later via salary, not here
    return vno
def hr_overtime_calc(emp_code: str, month: str, cn=None) -> float:
    """VB6 OverTime calc: SELECT SUM(OverTimeAmt) FROM OverTime WHERE EmployeeCode=? AND Mth_Year=? AND (LogSite_Code=? OR HO)"""
    rows = db.query("SELECT ISNULL(SUM(OverTimeAmt),0) FROM OverTime WHERE EmployeeCode=? AND Mth_Year=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR ISNULL(LOGSITE_CODE,'')='')", (emp_code, month, db.get_site_code()), cn=cn)
    return float(rows[0][0] or 0) if rows else 0.0

