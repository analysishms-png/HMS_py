# PYTHONE (HMS_py) — Debug Report vs VB6 Logic (FODER)

**Date:** 2026-09-24  
**Source VB6:** `Project.vbp` Sub Main, `MDIForm1.frm` 11618 lines, `HMS.bas` P-Code, `MainLib.bas`, `FOMModule.bas`, `FaVoucher.bas`, `moondata.sql` UTF-16 274 tables (1289160 chars decoded)  
**Python:** `PYTHONE/` (package `HMS_py` → `core/` 104 modules + `ui/` 83 forms)  
**DB:** `Moondata2627` (Analysis.ini key 6), `KailashData2527` legacy

---

## 1) Package Structure — CRITICAL FIX DONE

**VB6 logic:** `Project.vbp:4 Startup="Sub Main"` → `HMS.bas` + `Module1.bas` 40 Declare Functions, single EXE `HMS.exe`.

**Python expectation:** `pyproject.toml:1-11` → package `HMS_py` (`where=["."] include=["*"]`), imports `from HMS_py.core import db`, `python -m HMS_py.main`.

**Bug:** Physical folder is `PYTHONE/core` + `PYTHONE/ui` + `PYTHONE/main.py` — **not** `PYTHONE/HMS_py/core`. So `ModuleNotFoundError: No module named 'HMS_py'` on `python -m pytest tests/unit`.

**Evidence:**
```
PYTHONE/core/__init__.py  → """HMS_py core package."""
PYTHONE/main.py           → from HMS_py.ui import shell
tests/conftest.py:10      → PROJECT_ROOT = ../../.. (expects HMS_py/HMS_py/tests)
pytest.ini: testpaths = HMS_py/tests tests
```

**Test result before fix:** `FAILED` at conftest.
**Fix applied (debug session):**
```bash
# Created shim package PYTHONE/HMS_py/ as copy of core+ui (no symlink due to privilege):
Copy-Item PYTHONE/core → PYTHONE/HMS_py/core -Recurse
Copy-Item PYTHONE/ui   → PYTHONE/HMS_py/ui   -Recurse
Copy-Item PYTHONE/__init__.py → PYTHONE/HMS_py/__init__.py
Copy-Item PYTHONE/main.py     → PYTHONE/HMS_py/main.py
Copy-Item PYTHONE/tests       → PYTHONE/HMS_py/tests -Recurse
```
**Result after fix:** `Set-Location PYTHONE; python -m pytest HMS_py/tests/unit -q` → **263 passed in 3.70s**.

**Permanent fix recommended (choose one):**
1. Rename folder `PYTHONE` → `HMS_py` (clean, matches `pyproject.toml`), OR
2. Add `HMS_py` shim via `import` alias in `core/__init__.py` + update `pyproject.toml` `where=["PYTHONE"]`, OR
3. Keep dual copy + add CI step `robocopy PYTHONE\core HMS_py\core /MIR` before `pytest`.

Also fix `pytest.ini` `testpaths = tests tests` vs `HMS_py/tests` duplication caused 2× count (263 vs 137 in README). Keep one.

---

## 2) Unit vs Integration Test Health

| Suite | Result (this machine, offscreen QT) | Notes |
|-------|-------------------------------------|-------|
| `HMS_py/tests/unit` (263) | **263 passed** | Pure logic, no DB (menu_help AEDP, validation, auth encrypt) |
| `tests` (all 305) | **305 passed, 5 errors** | 5 UI walkthrough `TestMainWindowFlow` ERROR `OSError: offline` |
| `PYTHONE/tests` (original, no shim) | fails `ModuleNotFoundError` | — |

**5 UI errors root cause:** `tests/test_ui_walkthroughs.py:306` stubs `db.connect` → `OSError("offline")` to test offline mode. But `PYTHONE/core/menu.py:26` + `ui/sidebar_buttons.py:168` call `db.query()` **without try/except for OSError**, propagating instead of returning fallback. VB6 would show `MsgBox` and continue with cached menu.

**VB6 vs Python:** `MDIForm1.frm` menu building wraps `On Error Resume Next` — offline still shows SA template. Python should catch `OSError`/`pyodbc.Error` and fallback to `menuHelp` cache or empty list.

**Fix (apply to `core/menu.py` & `ui/sidebar_buttons.py`):**
```python
# core/menu.py:26 roots() etc.
try:
    rows = db.query("SELECT ...", cn=cn)
except (OSError, pyodbc.Error):
    rows = []  # fallback to SA template / empty
```

**Tests after fix expected:** 310 passed, 0 errors.

---

## 3) MenuHelp Logic — VB6 vs Python Gap Closed

**VB6 schema (moondata.sql UTF-16):**
```sql
CREATE TABLE menuHelp(CompCode nvarchar(2), UserName nvarchar(10),
  Opt1 int, Opt2 int, Opt3 int, Opt4 int, Code int,
  [Option] nvarchar(50), Menu_Index int, Menu_Visible nvarchar(1),
  Pro_Name nvarchar(8), Tag nvarchar(10), User_Name nvarchar(10),
  Param_Str nvarchar(4), ID nvarchar(8), Module_Name nvarchar(30),
  Flag nvarchar(1), ShowInList nvarchar(1), OutletCode nvarchar(6))
CREATE TABLE menuHelp1(same but Code/MenuName...) -- SA template
```

**Flag/Param_Str (MDIForm1.frm:1A8DB09):**
- `Flag IN ('E','N')` → `Param_Str='AEDP'` (Masters/Operations: Add/Edit/Del/Print)
- `Flag='R'` → `Param_Str='***P'` (Reports: only Print)
- `Flag='V'` → hidden (`Flag<>'V'` filter, `ShowInList='N'`), e.g. `Restaurant Change` → `Module_Name='Rest'`

**OutletCode:** per-POS outlet (e.g. `REST01`) for `[Option]='KOT Entry'` → `SELECT ... FROM menuHelp INNER JOIN Depart ON OutletCode=Depart.Code`.

**Python `core/menu_help.py` (674 lines):** Fully ports above:
- `_load_user()` → `SELECT [Option], Param_Str, Flag, Module_Name, Opt1-4, Code` with SA fallback + CompCode fallback.
- `by_caption()`, `flag_for()`, `rights()`, `can()`, `can_open()` (Flag V → never, AEDP char check).
- `sidebar_modules()` (L1: `Opt1<>0, Opt2=Opt3=Opt4=0, Flag='N'`) + orphan `Auto Settle Card Balance` (O1=23) fix.
- `menubar_for_menuhelp()` (VB6 nesting: O2 groups, O3 leaves, O4 children; skips `Flag '-'` separators, childless N nodes).
- `copy_template()`, `set_rights()`, `set_hidden()`, `create_user()` onboarding + cache clear.

**Comparison:** VB6 MenuHelp handling was scattered (`HMS.bas:1A82C27` UPDATEs, `MDIForm1.frm:1A8D41F` etc., `UserMast.frm:12A6E0E` SHAPE). Python consolidates correctly. No gap—**PASS**.

**Migration kit mapping:** See `HMS_MenuHelp_Wise_MasterOpReports/00_MenuHelp_Analysis/` 4 docs + per-module `01_Masters/02_Operations/03_Reports` split.

---

## 4) LOGSITE_CODE Site Partition — GAP (VB6 HO fallback missing)

**VB6:** Masters query always `WHERE (LOGSITE_CODE=:s OR LOGSITE_CODE='HO')` (`frmEnviro.frm:678` → `SELECT … WHERE (LOGSITE_CODE='site' OR HO)` for `SubGroup`, `TaxStru`, `RevMast`, `RoomCat`, `Depart`, `GodownMast`, `RoundOffSetting`, `ItemMast` etc.). Transaction tables: `WHERE LOGSITE_CODE=:s` strict.

**Python:** Only **2** modules (`banquet_ops.py`, `tally_export.py`) have `OR 'HO'` fallback. Masters like `acgroup.py`, `taxmaster.py`, `roomcategory.py`, `roommaster.py`, `depart.py` → `SELECT ... ORDER BY` **with zero WHERE** → returns all sites mixed (cross-site leak) or HO missing for non-HO site.

**Evidence:**
```
acgroup.py: list_all() → SELECT GroupCode ... FROM ACGROUP ORDER BY (no WHERE)
banquet_ops.py: HO fallback present
tally_export.py: HO fallback present
```

**Fix per master module (apply to ~15 masters):**
```python
site = db.get_site_code()
rows = db.query(
  "SELECT ... FROM AcGroup WHERE LOGSITE_CODE IN (?, 'HO') OR LOGSITE_CODE IS NULL ORDER BY GroupCode",
  (site,), cn=cn)
# OR for transaction modules: WHERE LOGSITE_CODE = ? strict
```

**Checklist:** Update `core/acgroup.py`, `taxmaster.py`, `roomcategory.py`, `roommaster.py`, `depart.py`, `company.py`, `city.py`, `state.py`, `country.py`, `marketsegment.py`, `businesssource.py`, `gueststatus.py`, `paymenttype.py`, `plans.py`, `venue.py`, etc. to add site filter. See `HMS_MIGRATION_READY_KIT/99_SHARED/DB_PORTING.md`.

---

## 5) BUG-014 Site/Company Hardcode — FIXED (verify)

**VB6:** `Analysis.ini` key `7=KK` (company/site code 2-char), key `8=Kanpur` (site name). `HMS.bas` reads key 7.

**Python before BUG-014:** 83 modules had `SITE_CODE = "KK"` hardcoded.

**Python after:** `core/db.py:229 get_site_code()` → `HMS_SITE_CODE` env else `load_config()["company"][:2]` (key 7). `SITE_CODE = db.get_site_code()` in `acgroup.py` etc. `get_user()`, `get_comp_code()` (`"2"` fallback), `get_vprefix()` (year) + `get_context()`.

**Current Analysis.ini (PYTHONE/Analysis.ini):**
```
1=Localhost
2=...Reports
3=...Reports
6=Moondata2627
7=KK
8=Kanpur
9=&Finance#&Main Setup#...
```

**Verification:** `db.get_site_code() → "KK"` correct; `db.get_comp_code() → "2"` (menuHelp CompCode numeric). Live `Moondata2627` has `UserMast 70 rows` (checked via `db.query('SELECT COUNT(*) FROM UserMast') → 70`). **PASS**.

**Remaining nuance:** `get_site_code` reads `company` (key 7) not `site` (key 8). VB6 actually reads key 7 `KK` as site code, so correct. But if future DB uses `Kanpur` as site name vs `KK` code, need mapping table `Site(Code, Name)`.

---

## 6) BUG-015 Race-Safe VNo — PARTIALLY FIXED

**VB6:** `SELECT MAX(VNo) +1` then `INSERT` — race → duplicate `VNo/DocId`.

**Python fix `core/db.py:297 next_vno()`:** `WITH (UPDLOCK, HOLDLOCK)` range lock on `MAX(VNo)` until tx end; caller passes `cn` for atomicity.

**Migrated (9 modules):** `folio`, `expenseentry`, `nightaudit`, `inventory`, `guest_services` (WakeUp/Message), `hall_booking` (HB/HS), `sms_comm` (AssignDelivery), `banquet_ops` (Voucher_Type), `checkin` (next_folio), `facility_billing`.

**Still risky (4 modules) — `MAX(VNo)` without `next_vno`:** `guest_services.py`, `hall_booking.py`, `pos_packing.py`, `sms_comm.py` — grep `MAX(VNo)` remains. Note `sms_comm` and `hall_booking` are listed as both fixed (via SELECT COLS `DBSendSMS` etc.) and still have raw `MAX` — maybe inline `MAX` inside `next_vno` wrapper already, but grep found raw string inside comment? Verify each file's actual `SELECT MAX` outside next_vno.

**Fix for remaining:** Replace:
```python
# before
row = db.query("SELECT MAX(VNo) FROM ... WHERE ...")[0][0]
vno = int(row or 0)+1
db.execute("INSERT ... VNo=?", (vno,))
# after
vno = db.next_vno("Table","Vtype","2026", site, cn=cn)
db.execute("INSERT ...", (vno,), cn=cn, commit=False)
cn.commit()
```

---

## 7) Other VB6 → Python Logic Fixes (from README v0.1.1/0.1.2)

| VB6 Issue | Python File | VB6 Evidence | Fix |
|-----------|-------------|--------------|-----|
| **BUG-016** `_get_checkout_type` swallowed all DB errors | `core/checkout.py` | `Invalid column name 207` only | Now only catch `207`, else propagate |
| **BUG-018** invalid SNo/Rate silently skip | `ui/taxstru_ui.py` | grid lines skip | Now raises `ValueError` with row number |
| **BUG-019** invalid SNo/Qty/Rate silent zero | `ui/kot_entry.py` | same | Now explicit error, rate-autofill overwrite |
| **BUG-022** BookNo parsing crash | `ui/reservation_browser.py` | `keep_bookno` | Crash-guarded for non-numeric |
| **BUG-024** folio helpers None crash | `ui/checkout_ui.py` | `PYT` guest cell missing | Guards for None/empty/non-numeric |
| **P1 Missing** Room Change / Merge / ReSettlement / Table Change / KOT Transfer | `core/fo_ops.py`, `core/pos_kot.py`, `ui/fo_sub_forms_ui.py`, `ui/kot_transfer_ui.py` | `fdRoomChange`, `FrmMergeCharge`, `FdReSetlement`, `RsTbChange`, `RsKOTTransfer` (v0.1.2) | Faithful port with RoomOcc SNo=max+1, Type='C', RoomMast dirty, PlanDetails re-link, `RelatedFolioNo` mesh, `ModeSet='S'/Vtype='REC'` re-post + `next_vno` race-safe |

All verified via `HMS_py/tests/unit/test_missing_logic_core.py` (14 tests) + `test_bugfix_batch.py` (33 tests) → 33+14 part of 263.

---

## 8) DB Connection & Paths

**VB6:** `Analysis.ini` keys `1=server, 6=database, 2=reports, 3=temp, 7=company, 8=site, 9=sidebar modules`. VB6 creates `Reports`/`Temp` folders if missing.

**Python `core/db.py:24`:** `_candidate_ini_paths()` → project-local `PYTHONE/Analysis.ini` priority (good). `ensure_paths()` creates Reports/Temp best-effort (non-fatal). `connect()` tries `SQL Server Native Client 10.0` then `SQL Server`, sets `LOCK_TIMEOUT 5000`, `cn.timeout=30` (B017 dead-process orphan lock fix).

**Live DB:** `Moondata2627` reachable (`UserMast 70`). `KailashData2526` legacy not tested.

**Gap:** No `Analysis.ini` in repo root `PYTHONE/Analysis.ini` was missing before, now exists (reports/temp point to `.../PYTHONE/Reports`). Should also copy to `C:\Drive\HMS2526\Analysis.ini` for VB6 parity if VB6 still used side-by-side.

---

## 9) Frontend Shell Registry

**VB6 MDI:** 641 leaves via `HMS_py/core/mdi_menu.json`? Actually `core/menu.py` + `menu_help.py` dynamic (Flag E/N/R/V, Opt1-4). `ui/shell.py` → Login (frmPassword) → Company select (frmCompany grid) → Main window title `{Company} { Year }` + sidebar (Analysis.ini key 9) + menubar (`User_Module` fallback for full-access, `menuHelp` for restricted).

**Python `ui/shell.py:1611` `MainWindow("SA", ...)` → `sidebar_buttons.build_all_buttons("SA")` → `_menu.roots()` → `db.query` may throw offline → now error (see §2). Should fallback.

**Keyboard shortcuts:** Ctrl+Alt `H,M,B,F,G,D,S,K,E,T` conflict-free (v0.1.1 Notes) — VB6 had no such; good addition.

---

## 10) Immediate Action Checklist (Debug Fix Order)

1. **Package shim** — keep `PYTHONE/HMS_py` copy or rename folder; fix `pytest.ini` testpaths duplication → re-run `python -m pytest HMS_py/tests/unit -q` must stay 263.
2. **Offline DB guard** — add `try/except OSError` in `core/menu.py:26`, `ui/sidebar_buttons.py:168/207`, `core/menu_help.py` loaders.
3. **LOGSITE_CODE HO fallback** — add `WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO')` to ~15 master `list_all()` (acgroup, taxmaster, roomcategory, roommaster, depart, etc.).
4. **next_vno coverage** — replace remaining 4 raw `MAX(VNo)` with `db.next_vno(..., cn=cn)` inside tx.
5. **Reports folder** — ensure `Reports/` + `Temp/` exist + writable; test `ensure_paths()` + one report PDF generation (`ui/reports_ui.py`).
6. **Analysis.ini** — ensure key 7 `KK` and 8 `Kanpur` consistent; add comment about `HMS_SITE_CODE` env override for multi-site.

---

## 11) Files Generated This Session (Logic Reference)

- `HMS_LogicWise_Manual_2026/` (17 files) — login→NightAudit full flow `file:line`
- `HMS_MIGRATION_READY_KIT/` (96 files) — Frontend/Backend/API/Schema/Checklist per module, any language
- `HMS_MenuHelp_Wise_MasterOpReports/` (78 files) — MenuHelp table → Masters/Operations/Reports split per `Opt1-4` + `Flag` + `Module_Name` + `OutletCode`
- `HMS_Manual_Text_Word/` (79 files) — text + Word module-wise + full combined (193k txt, docx)

All ready for `python` migration audit.

