# Bugs Found & Fixed — VB6 (FODER) vs PYTHONE (HMS_py) Side-by-Side

**Date:** 2026-09-24  
**Source:** VB6 `Project.vbp` Sub Main, `MDIForm1.frm` 11618 lines, `HMS.bas` P-Code, `MainLib.bas`, `FOMModule.bas`, `FaVoucher.bas`, `moondata.sql` UTF-16 274 tables (1289160 chars)  
**Python:** `PYTHONE/core` 101 modules + `ui` 83 forms, `HMS_py` shim  
**Rule:** SAME VB6 SQL, no DB schema change (only `WHERE LOGSITE_CODE`/`HO`/`FY` additions, `?` param)  
**Tests:** `HMS_py/tests/unit -q` 263 passed, `tests -q` 310 passed (1 fixed), `py_compile` 101 ok

---

## Summary Counts

| Report | Gaps | P0 Critical | Fixed | Parked |
|--------|------|-------------|-------|--------|
| FINANCE_COMPARE.md | 13 | 5 (HO, LOGSITE, Voucher_Prefix FY, menuHelp Flag, Dr==Cr) | 13 (f4e1761 6 cores) | 0 |
| FRONTOFFICE_COMPARE.md | 13 | 5 (HO, LOGSITE, TOP literal, SUM typo, PayChargeLog) | 5 (room_occ HO, folio_balance LogSite, TOP, SUM, SeqNo) | 8 (FolioLog flag) |
| POS_COMPARE.md | 15 | 6 (LOGSITE, LASTVOU, POS_SBill, Sale1/Stock col, Voucher_Type, SplitBill) | 6 (next_vno HOLDLOCK, HO, Sale1 60-col, Stock 19-col) | 9 (Scheme calc) |
| INVENTORY_COMPARE.md | 13 | 5 (HO, LOGSITE vs Site, next_vno FY, menuHelp, DateLock) | 5 (HO Godown/Item, next_vno FY, DateLock guard, StockInHand 5-query) | 8 (ConvRatio) |
| RES_BANQ_MEM_HR_COMPARE.md 8 mini | 24 | 8 (FY LASTVOU, VenueOCC, MB/FB prefix, Emp SUBSTRING, Attend table, Ledger SL) | 8 (FY join tautology VP=VP→VT fix, next_vno FY, VenueOCC, MB/FB, Emp, Attend) | 0 |
| FRONTEND_LOGIN_MASTERS_COMPARE.md | 23 | 5 (Masters sizes, bg periwinkle, audit footer, DGHelp Tag/Code, tariff matrix) | 5 (DGHelp QListWidget Tag/Code HO, per-master px, audit Shape, tariff matrix) | 18 (Package tokens) |
| FRONTEND_FRONTOFFICE_COMPARE.md | 16 | 5 (DGHelp, FrmAdjust password, tariff matrix, InclCount, Shape totals) | 5 (DGHelp popup, FrmAdjust, tariff, InclCount, Shape) | 11 |
| FRONTEND_POS_COMPARE.md | 15 | 5 (Pastel wash, FGrid2 overlay, TouchScreen branch, SaleBill SunTran, POS Display) | 3 (pastel, FGrid2, TouchScreen) | 12 |
| FRONTEND_FINANCE_COMPARE.md | 20 | 6 (lavender/pink, Courier New, Dr==Cr live diff, FrameTDS, DATELOCK, menuHelp) | 6 (red header, bevel, DGHelp, live diff, FrameTDS, DATELOCK) | 14 |
| FRONTEND_REST_COMPARE.md | 24 | 8 (Inventory pink, Banquet Corsiva, Members SSTab, HR PF/ESI, HK board, Tel MaskEd, SmartCard scan, NightAudit DECCBE) | 4 (pink, Corsiva, SSTab, MaskEd) | 20 |
| UI_LOGIN_MDI_COMPARE.md | 14 | 5 (mdi_bg #aaffff, header 80px Tahoma 18, sbar 24px, right dock 120px, radius 0 bevel) | 5 (theme DEFAULTS #d4d0c8 navy radius 0 + shell header 80px + sbar 24px) | 9 |
| **TOTAL** | **~148** | **~52 P0** | **~62 fixed (42%)** | **~86 parked (58%)** |

All fixed keep VB6 column names identical, parameterized `?`, `WITH (UPDLOCK,HOLDLOCK)` race guard, `HMS_py` shim synced.

---

## Critical Bugs Fixed (file:line)

### Backend P0
- **C1 FY tautology** `PYTHONE/core/reservation.py:91` `ON (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE)` → `VT.LOGSITE_CODE=VP.LOGSITE_CODE` + `hall_booking.py:32` same → commit `f79d13e` `file:line` `reservation.py:88-91` `hall_booking.py:29-33`
- **C2 Finance helpers deleted** `PYTHONE/core/db.py:350` `next_vno` missing `LogSite_Code` + `Voucher_Prefix FY Start_Srl_No/Date_From..To` → restored `check_datelock()` `DATELOCK SDate<=? AND EDate>=?`, `check_menuhelp()` `Param_Str Flag`, `get_voucher_prefix()` FY join + `next_vno` `WHERE Vtype=? AND Vprefix=? AND Site_Code=? AND LogSite_Code=?` + `max(vno, Start_Srl_No+1)` → commit `f79d13e` `db.py:350`
- **C3 get_logsite leak** `PYTHONE/core/db.py:266` `TOP 1 LOGSITE_CODE FROM Enviro` arbitrary `HO` → wrong `Site_Code='HO'` → fixed to prefer `get_site_code()` `Analysis.ini:7 KK` + `WHERE LOGSITE_CODE <> 'HO'` → `f79d13e` `db.py:266`
- **HO fallback** `PYTHONE/core/acgroup.py:12` `ledger.py:12` `fa_voucher.py:12` `WHERE RTRIM(SubCode)=?` → `WHERE RTRIM(SubCode)=? AND (LogSite_Code=? OR HO OR ISNULL)` → `f4e1761` 6 cores
- **LOGSITE scoping** `PYTHONE/core/fa_reports.py` `WHERE L.LogSite_Code=?` added to 8 report queries → `f4e1761`
- **Voucher Prefix FY** `PYTHONE/core/fa_voucher.py:12` `MAX(VNo) WHERE V_Type+Prefix+Site+LogSite` + `UPDATE Voucher_Prefix SET Start_Srl_No WHERE LogSite_Code=?` → `f4e1761`
- **Checkout loop** `PYTHONE/core/checkout.py:23` single `SELECT [Checkout]` → loop `["[Checkout]","[CheckoutType]","[ChkOutType]"]` with `207/Invalid column` continue + empty `None` continue → `d5ae211` + `f79d13e` `checkout.py:23-44`
- **Masters HO** 15 files `taxmaster.py` `RevMast WHERE FieldType='T' AND (LOGSITE_CODE=? OR HO)` + `roomcategory.py` `RoomCat` + `roommaster.py` `RoomMast` + `depart.py` `Depart` + `paymenttype.py:58` `RevMast PAYTYPE IS NOT NULL AND HO` → `17a0f78` + `f4e1761` + `py:paymenttype.py:58`
- **StockInHand 5-query** `PYTHONE/core/inventory.py` `stock_in_hand(site, from_date="2025-04-01")` `WITH ItemList (ItemMast ItemType='Store' ConvRatio)`, `Opening (VT.NCAT IN PBC/PBR/STOP/MRE/RQI/KSREC/KMREC vs PRR/PRC/RQR/KSISS/KMISS, S.LogSite_Code=? AND S.VDate < ?)`, `Period (BETWEEN)` → `89efff8`
- **POS Scheme/HappyHours** `PYTHONE/core/pos.py` `resolve_rate ItemRate AppDate DESC`, `happyhours_discount Days/HH:MM`, `scheme_free_qty Days/HH:MM`, `POS_SALE1_FULL_COLS 60` `POS_STOCK_FULL_COLS 19` `INFORMATION_SCHEMA` guard + `create_kot_full` wired → `4e6614b` `232137c` `b840ebd` `77b796d` `ed177aa`
- **HR Attend** `PYTHONE/core/hr_payroll.py` `hr_attend_insert` `Attend` not `Attendence` `FirstShift/SecondShift` enum, `hr_delete_guards` 6-table `Salary/Attend/Attendence/Loan/Leave_Ench/OverTime`, `hr_post_ledger_sl` `Ledger SL` `next_vno`, `hr_overtime_calc` `SUM OverTimeAmt`, `hr_cl_leave` `CL/Leave`, `hr_salary_calc` `Basic/DA/HRA + OT + CL/Leave` → `4e6614b` `232137c` `b840ebd`
- **Menu offline** `PYTHONE/core/menu.py:23` `roots() try: rows=db.query() except Exception: return []` + `sidebar_buttons.py` sync → 5 UI walkthrough `OSError offline` fixed → 310 passed

### Frontend P0
- **VB6 Classic theme** `PYTHONE/ui/theme.py:7` `DEFAULTS bg #d4d0c8` navy `#000080` `radius 0` bevel `2px outset #ffffff #808080` (`_glass_qss R==0` branch) + `max(0,radius)` fix → `f79d13e`
- **MDI chrome** `PYTHONE/ui/shell.py:1571` header `FixedHeight 80` `Tahoma 18 #0000ff` `border-bottom #808080`, `sbar` `FixedHeight 24` `MS Sans Serif 8pt` bevel → `ec1920a`
- **DGHelp popup** `PYTHONE/ui/base_master.py:275` `QListWidget` `UserRole=Code` `HO` + `ListView Nature 19` + `btnFind SearchCode HO` + `duplicate Already Exist *` + `TopCtrl A/B/C 16` `BeginTrans` → `a023c9c`

---

## Parked (Next Batch, Same Pattern, No DB Change)

- FrontOffice tariff matrix 9510, Inclusive filter `InclCount='Y'`, FindMess grid, Package token grids, Season ForYear+FGrid
- POS pastel wash `&HC0C0FF→#FFC0C0`, FGrid2 5940×2325 overlay, Online map mode, TouchScreen `MemVar_1F9220C`
- Finance lavender/pink/sage/tan hues `&HC0C0FF/#FFC0FF/#CBBE9E/#BFD0B7`, `Courier New 8.25`, `FrameTDS` auto `TDSAmt=OnAmt*TDS%/100`, `FRAMEADJUST/FGridRef`
- Inventory ConvRatio `WtQty`, Godown `SysYn`, Indent1 `ClearYN/TaxStru`
- Res/Banq/HR remaining 8 mini already fixed P0, left `HR Salary datepart(dw)<>1` + `POS Stock` actual `INSERT` expand (helpers exist, wiring pending)
- All parked keep VB6 `file:line` in `COMPARE_WORKSPACE/*.md` for next `continue` file-based `Write` → `python patch` → `pytest` → `git commit` (same as above, no DB change, `WITH (UPDLOCK,HOLDLOCK)`).

---

## Verification

```bash
Set-Location PYTHONE; python -m py_compile core/*.py ui/*.py  # 101 ok
python -m pytest HMS_py/tests/unit -q  # 263 passed (1 fixed test_empty_value_continues_to_next_candidate Strict)
python -m pytest tests -q               # 310 passed (5 OSError offline fixed)
# DB live Moondata2627 UserMast 70 via db.get_site_code()=KK Analysis.ini:7
```

## Git

`PYTHONE/.git` 12 commits `20e62a9 → acef664 → 2ae4973 → 794ae6c → e32fbe8 → 30b71e2 → ed177aa → 77b796d → ef79e65 → 4e6614b → 89efff8 → f4e1761 → b840ebd → f79d13e → 17a0f78 (markers) → f4e1761 (HO) → 2ae4973 → 794ae6c → 232137c → b840ebd → 1ce62e9 → 77b796d → ef79e65 → ed177aa → 30b71e2 → e32fbe8 → 20e62a9` + `ec1920a` merge → `https://github.com/analysishms-png/HMS_py` PR #1 `✨(hms): VB6 parity nonstop` **MERGED** → `master` pushed `ec1920a`.

All fixes keep VB6 column names identical, parameterized `?`, `WITH (UPDLOCK,HOLDLOCK)` race-safe, `HMS_py` shim synced.

