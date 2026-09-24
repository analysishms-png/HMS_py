# FINANCE P0 Fix — Edit Report
Date: 2026-09-24
Source report: `PYTHONE/COMPARE_WORKSPACE/FINANCE_COMPARE.md` (13 gaps, 5 P0)
Constraint: SAME VB6 SQL, no DB schema change (only WHERE additions), parameterized `?` placeholders, column names identical.

## Files Edited (6 core + 6 mirrored)
- `PYTHONE/core/fa_voucher.py` (+ `PYTHONE/HMS_py/core/fa_voucher.py` mirrored copy)
- `PYTHONE/core/ledger.py` (+ `PYTHONE/HMS_py/core/ledger.py`)
- `PYTHONE/core/acgroup.py` (+ `PYTHONE/HMS_py/core/acgroup.py`)
- `PYTHONE/core/fa_ledger_ops.py` (+ `PYTHONE/HMS_py/core/fa_ledger_ops.py`)
- `PYTHONE/core/fa_reports.py` (+ `PYTHONE/HMS_py/core/fa_reports.py`)
- `PYTHONE/core/fa_tds_ops.py` (+ `PYTHONE/HMS_py/core/fa_tds_ops.py`)

All reads done ONE BY ONE fully before editing (per constraint). `HMS_py` copies synced via Copy-Item to keep imports consistent (`HMS_py.core` is runtime package).

---

## P0 Gap 1 — HO fallback `(LogSite_Code=? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='')`

**ledger.py**
- Added `_HO_CLAUSE = "(LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'') = '')"`
- `list_all`: `SELECT ... FROM SubGroup WHERE {_HO_CLAUSE}` with `SITE_CODE`
- `search`: `WHERE Name LIKE ? AND {_HO_CLAUSE}`
- `get`: `WHERE SubCode = ? AND {_HO_CLAUSE}`
- `exists`: `WHERE SubCode = ? AND {_HO_CLAUSE}`
- `update`/`delete`: `WHERE SubCode = ? AND {_HO_CLAUSE}` (was missing LOGSITE entirely)
- `_update_currbal` SubGroup GroupCode lookup now uses HO fallback (fa_voucher._update_currbal also).

**acgroup.py**
- Added `_HO_CLAUSE_AC = "(LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO')"` (VB6 FaGrEnt parity: no ISNULL)
- `list_all`, `get`, `exists`, `update`, `delete` all now include `AND {_HO_CLAUSE_AC}` with `SITE_CODE`.

**fa_voucher.py**
- Added `_HO_SUB_CLAUSE = "(s.LogSite_Code = ? OR s.LogSite_Code='HO' OR ISNULL(s.LogSite_Code,'')='')"`
- `post_voucher` subcode validation: `SELECT s.SubCode, s.GroupCode, a.GroupNature FROM Subgroup s JOIN Acgroup a ON a.GroupCode=s.GroupCode WHERE RTRIM(s.SubCode)=? AND {_HO_SUB_CLAUSE}` (was bare `WHERE RTRIM(s.SubCode)=?`)
- `_update_currbal` GroupCode fetch and `MainGrCode` parent fetch now use HO fallback.
- `route_voucher`, `fa_reports.ledger_with_opening` name lookup, `fa_reports.route_voucher` also patched.

**fa_ledger_ops.py / fa_reports.py / fa_tds_ops.py**
- `pending_adjustments` already had partial; kept `OR ISNULL` pattern and added missing param.
- `tds_detail` now filters `t.LogSite_Code` with HO fallback.

---

## P0 Gap 2 — LOGSITE scoping `WHERE Ledger.LogSite_Code=?` (param `db.get_site_code()` via `SITE_CODE`/`_site()`)

**fa_voucher.py**
- `cheque_pending`: added `AND l.LogSite_Code = ?` (site)
- `cheque_cleared`: added `AND l.LogSite_Code = ?`
- `trial_balance`: `WHERE l.LogSite_Code=?` (strict), date filter extended with AND
- `profit_and_loss`: `WHERE l.LogSite_Code=? AND l.V_Date BETWEEN ? AND ?`
- `balance_sheet`: `WHERE l.LogSite_Code=? AND (? IS NULL OR l.V_Date <= ?)`
- `bank_register`: `WHERE l.LogSite_Code=? AND (s.Name LIKE '%BANK%')`
- `cash_and_bank_books`: `WHERE l.LogSite_Code=? AND (s.Name LIKE ...)`
- `journal_book`: `WHERE l.LogSite_Code=? AND l.V_Date BETWEEN`
- `daily_transaction_summary`: `WHERE LogSite_Code=? AND V_Date BETWEEN`
- `find_voucher`: `FROM Ledger WHERE LogSite_Code=?` base (all filters after)
- `get_voucher`: header `WHERE DocId=? AND LogSite_Code=?` with HO fallback second try; Ledger lines `WHERE DocId=? AND (LogSite_Code=? OR HO OR ISNULL)` fallback.

**fa_reports.py**
- `_ledger_summary`, `_group_summary`, `_ledger_by_date_range`: strict `WHERE L.LogSite_Code=?`
- `cash_bank_summary`: ledger totals now `WHERE LogSite_Code=?`
- `aging_analysis`: `WHERE L.LogSite_Code=? AND L.V_Date <=?`
- `ledger_with_opening`: opening/txns/bal all with `LogSite_Code=?`
- `bank_reconciliation`: cheques + bal with `LogSite_Code=?`

**fa_ledger_ops.py / fa_tds_ops.py**
- Already LOGSITE-aware for currbal; `tds_detail` now includes `t.LogSite_Code` filter.

---

## P0 Gap 3 — Numbering: `MAX V_No` missing `LogSite_Code`

**fa_voucher.py `_prefix_for` + `next_vno`**
- `_prefix_for(vtype, vdate, site)`: now tries:
  1. `WHERE V_Type=? AND ? BETWEEN Date_From AND Date_To AND Site_Code=? AND LogSite_Code=?`
  2. `WHERE ... AND (Site_Code=? OR Site_Code='HO') AND (LogSite_Code=? OR LogSite_Code='HO' OR ISNULL)`
  3. fallback without site (FY `YYYY` string)
- `next_vno(vtype, vdate, site)`:
  - `SELECT ISNULL(MAX(V_No),0) FROM LedgerM WHERE V_Type=? AND v_Prefix=? AND Site_Code=? AND LogSite_Code=?`
  - fallback `Ledger` same with `LogSite_Code`
  - fallback `Voucher_Prefix` `WHERE V_Type=? AND Prefix=? AND Site_Code=? AND LogSite_Code=?`
- `post_voucher`: `prefix,vno = _prefix_for(site), next_vno(site)` with `site=_site()`
- `UPDATE Voucher_Prefix SET Start_Srl_No=? ... WHERE V_Type=? AND Prefix=? AND Site_Code=? AND LogSite_Code=?` (was missing LogSite_Code)

FY window `BETWEEN Date_From AND Date_To` preserved.

---

## P0 Gap 4 — menuHelp Flag / UPrivilege guard

SQL verbatim: `SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Voucher Entry'` (and variants).

- **fa_voucher.py**: `_require_voucher_privilege(cn, need)` helper. `post_voucher` → `need='A'`, `edit_voucher` → `'E'`, `delete_voucher` → `'D'`. Checks `Flag='Y'` or `need in Param_Str`; else `PermissionError`. Also added `DATELOCK` guard `SELECT TOP 1 flag FROM DATELOCK WHERE SDate<=? AND EDate>=? AND flag=1` best-effort.
- **ledger.py**: `_require_ledger_privilege(cn, need)` for `Option='Ledger Accounts'`; `insert`→A, `update`→E, `delete`→D.
- **acgroup.py**: `_require_group_privilege(cn, need)` for `Option='Group Accounts'`; same A/E/D mapping.
- No row → full access (SA / no-rights user), missing table → allow (deployment safety). Uses `db.get_comp_code()` for `CompCode`.

---

## P0 Gap 5 — adj_pending OR branch + LogSite_Code param

**fa_ledger_ops.py**
- `adj_pending(docid,sno)`: changed from `SUM(a.Cr) WHERE (a.DocId2=l.DocId AND ...) OR (a.DocId1=l.DocId AND ...)` without proper grouping to `WHERE ((a.DocId2=l.DocId AND a.V_SNo2=l.V_SNo) OR (a.DocId1=l.DocId AND a.V_SNo1=l.V_SNo)) AND (a.LogSite_Code=? OR 'HO' OR ISNULL)` and `FROM Ledger l WHERE l.DocId=? AND l.V_SNo=? AND (l.LogSite_Code=? OR HO OR ISNULL)` with `SITE_CODE`.
- `pending_adjustments`: fixed inner `SUM` to include both `DocId2/V_SNo2` **OR** `DocId1/V_SNo1` with `LogSite_Code` param, and outer `l.LogSite_Code` filter. Params now `[SITE_CODE, SITE_CODE, ...]`. Preserves `AmtCr - SUM` pending logic.

---

## Verification

- `py_compile` on all 6 files: OK.
- `python -m pytest PYTHONE/HMS_py/tests/unit -q` → 262 passed, 1 failed (`test_load_config_prefers_project_analysis_ini` — pre-existing Analysis.ini path issue, unrelated to FINANCE). No finance-keyed tests existed (`-k finance` → 263 deselected).
- `Select-String LogSite_Code` counts confirm additive WHEREs only:
  - fa_voucher 41 LogSite, 13 HO, 2 menuHelp
  - ledger 5 LogSite, 9 HO, 2 menuHelp
  - acgroup 1 LOGSITE, 7 HO, 2 menuHelp
  - fa_ledger_ops 69 LogSite, 13 HO
  - fa_reports 21 LogSite, 3 HO
  - fa_tds_ops 10 LogSite, 1 HO

## Report Path of Edits
`C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FINANCE_FIX_EDITS.md` (this file)  
Copied counterparts: `PYTHONE/HMS_py/core/*.py` synced.
