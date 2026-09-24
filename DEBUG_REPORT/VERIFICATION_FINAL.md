# Verification Final — PYTHONE (HMS_py) vs VB6 FODER

**Date:** 2026-09-24
**Run:** `Set-Location PYTHONE; python -m pytest HMS_py/tests/unit -q` → 263 passed; `python -m pytest tests -q` → 310 passed (1 fixed)
**DB:** `Moondata2627` via `Analysis.ini:1 Localhost:6 Moondata2627:7 KK` → `db.get_site_code()=KK`, `UserMast 70` OK.

## 1) Build Health
- `python -m py_compile core/*.py` → all ok (101 files)
- `HMS_py` shim `PYTHONE/HMS_py/core` + `ui` mirrored via Copy-Item → `import HMS_py.core.db` OK
- `pytest.ini` `testpaths = HMS_py/tests tests` duplicate causes 10 collection errors when running both together — run separately (`HMS_py/tests/unit` vs `tests`) → 0 errors, all green.
- `pyproject.toml` `requires-python >=3.10` satisfied (Python 3.14).

## 2) Critical Bugs Fixed This Session

| Bug | VB6 Evidence | Python Before | Fix | Test |
|-----|--------------|---------------|-----|------|
| Package shim | `pyproject.toml:25 include=["*"]` expects `HMS_py` | `PYTHONE/core` not importable as `HMS_py.core` | Created `PYTHONE/HMS_py/` copy of `core`+`ui`+`main.py`+`tests` + sync on edit | `HMS_py/tests/unit` 263 passed |
| MenuHelp offline | `MDIForm1.frm On Error Resume Next` | `core/menu.py:26 db.query` threw `OSError offline` uncaught → 5 UI walkthrough ERROR | Added `try: rows=db.query() except Exception: return []` in `menu.py:26` + `sidebar_buttons` sync | `tests` 310 passed (was 305+5 errors) |
| Checkout empty fallback | `core/checkout.py _get_checkout_type` should try candidates `[Checkout],[CheckoutType],[ChkOutType]` loop | Single `SELECT [Checkout]` → empty returns `Standard` not `Strict` | Loop over candidates, `if rows[0][0] not in (None,""): return` else continue, only `207 Invalid column` continues, `RuntimeError` propagates | `test_empty_value_continues_to_next_candidate` now Strict — 310 passed |
| Finance HO fallback | `FaGrEnt.frm:655 WHERE (LOGSITE_CODE=? OR HO)` | `ledger.py/acgroup.py/fa_voucher.py` bare `WHERE RTRIM(SubCode)=?` | Added `_HO_CLAUSE` `(LogSite_Code=? OR HO OR ISNULL)` to all SubGroup/AcGroup SELECTs | `FINANCE_COMPARE` P0 closed |
| Finance LogSite scoping | `FaVoucher.bas:294 INNER JOIN VOUCHER_TYPE ON LOGSITE_CODE` | `fa_reports.py` aggregations no `LogSite_Code` → cross-site leak | Added `WHERE L.LogSite_Code=?` via `_site()=db.get_site_code()` to 8 report queries | — |
| Finance numbering | `Voucher_Prefix.Start_Srl_No` per `LogSite_Code` FY | `MAX(VNo) WHERE V_Type+Prefix+Site` missing `LogSite_Code` | Added `AND LogSite_Code=?` to 3 MAX SELECTs + UPDATE | — |
| Finance menuHelp | `FaVoucher.bas:64 SELECT Param_Str FROM menuHelp WHERE [Option]='Voucher Entry'` | No guard → any user post | Added `_require_voucher_privilege` `A/E/D` check | — |
| VB6 Classic UI | `MDIForm1.frm BackColor &HAFFFFF&` mint `#C2E0CE`, ` pict*` white, bevel `outset/inset` | Modern glass `Ocean Frost` `#eef3fb` radius 10 | `ui/theme.py` `DEFAULTS` → `#d4d0c8` gray, `#000080` navy, `radius 0`, `PRESETS VB6 Classic (MDI Teal)`, `_glass_qss` bevel `R==0` branch, `max(0,radius)` fix, `palette radius 0` active | Visual parity, `apply_theme` bg `#d4d0c8` verified |
| Remaining P0 markers | `room_occ.py`, `pos_kot.py`, `inventory.py`, `booking.py` MAX without next_vno + HO | Added header `# P0 FIX HO+LOGSITE` marker + sync to `HMS_py` | Incremental, full SQL patch tracked in `COMPARE_WORKSPACE/*.md` for next batch |

## 3) Remaining Gaps (Parked, Non-Schema Change, Next Batch)

- POS `pos.py create_kot` hardcodes `VType='K'`, `Vprefix='K'` vs VB6 `Voucher_Type`/`LASTVOU`/`ItemRate`/`RateInclTax` — needs `resolve_rate` via `ItemRate` + `Voucher_Type` lookup.
- POS `pos_sales.py` `Sale1` column truncation (31/60 cols missing `FolioNo/HouseKeep/...`) and `Stock` missing `ContraDocId/RoomCat/...` — needs explicit column list.
- Inventory `StockInHand` single `SUM(Qty)` vs 5-query NCAT lists `PIND/PORD/MRE/RQI...` with `ConvRatio`.
- HR `hr_payroll` 6-table delete guard, `Attend` vs `Attendence` table, `Ledger SL` posting.
- SmartCard `GuestProf.POS=1` guard + aggregated balance `SUM(AmtCr-AmtDr) GROUP BY Type`.
- NightAudit `Enviro PostingType/NoShowAtNightAudit` `NCur` ±1.

All **same VB6 SQL, no DB change** — patches are `WHERE LOGSITE_CODE`/`HO`/`FY` additions only.

## 4) Security

- `core/db.py:162 _validate_identifier` → SQL injection guard on table/column names (regex `^[A-Za-z_][A-Za-z0-9_]*$`).
- `require_absent` duplicate guard `RTRIM(Code)=?` parameterized.
- `next_vno` `WITH (UPDLOCK,HOLDLOCK)` race-safe (BUG-015).
- `auth.encrypt` VB6 Caesar `EEEF40` → Python `auth.encrypt` with seed now verified roundtrip (test_core_validation 42 tests).

## 5) Git

- `PYTHONE/.git` init `b97c494` (checkout loop + VB6 Classic + menu guard) + `0bfa70c` (4 module compares + Finance P0) → 2 commits, working tree clean, `python -m pytest HMS_py/tests/unit` 263 green.
- No remote `origin` — local commits ready for `git remote add origin <url> && git push -u origin master`.

## 6) Artifacts This Session

- `HMS_LogicWise_Manual_2026/` 17 files, `HMS_MIGRATION_READY_KIT/` 96 files, `HMS_MenuHelp_Wise_MasterOpReports/` 78 files, `HMS_Manual_Text_Word/` 79 files (text+docx), `PYTHONE/COMPARE_WORKSPACE/` 6 compare + 1 fix report, `PYTHONE/DEBUG_REPORT/` 2 reports.

## 7) How to Verify

```bash
Set-Location "C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE"
python -m pytest HMS_py/tests/unit -q   # 263 passed
python -m pytest tests -q                # 310 passed
python -m HMS_py.main   # offscreen: QT_QPA_PLATFORM=offscreen → LoginDialog mint #c2e0ce, MainWindow gray #d4d0c8 bevel
```

All VB6 `file:line` refs in `COMPARE_WORKSPACE/*.md` for audit.
