## Summary

VB6 Analysis HMS (Project.vbp / HMS.bas / moondata.sql 274 tables, UTF-16) → Python HMS_py parity, same SQL, no DB schema change, frontend VB6 Classic, multi-agent, module-wise, todo, source one-by-one.

## Changes (11 commits, 263/310 green)

**Backend 5 parallel agents (COMPARE_WORKSPACE 6 reports):**
- Finance 13 gaps (HO SubGroup, LogSite scoping, Voucher_Prefix FY LogSite, menuHelp AEDP, Dr==Cr) → f4e1761 6 cores
- FrontOffice 13 gaps (HO RoomOcc, LogSite PayCharge, TOP literal, SUM typo)
- POS 15 gaps (LOGSITE vs SITE_CODE, LASTVOU vs MAX, POS_SBill, Sale1/Stock 60/19-col, Scheme/HappyHours, OutletCode)
- Inventory 13 gaps (HO Godown/Item, next_vno FY, DateLock, StockInHand 5-query NCAT)
- Res/Banq/HR 8 mini (FY LASTVOU, VenueOCC, MB/FB, Employee SUBSTRING, Attend, Ledger SL)

FrontEnd 5 agents (FRONTEND_* 5 reports) → a023c9c base_master DGHelp QListWidget Tag/Code HO + ListView Nature 19 + Find SearchCode HO

**Manuals:** HMS_LogicWise_Manual_2026 17, HMS_MIGRATION_READY_KIT 96, HMS_MenuHelp_Wise_MasterOpReports 79, HMS_Manual_Text_Word 79 (text+docx)

**UI:** theme.py DEFAULTS VB6 Classic bg #d4d0c8 navy #000080 radius 0 bevel, Login 390x310 Company 640x470 pixel-exact, MainWindow teal sidebar

**Tests:** HMS_py/tests/unit 263 passed, tests 310 passed, py_compile 101 ok

**No DB schema change** — only WHERE LOGSITE_CODE / HO / FY additions, parameterized `?`.

## Testing

- `Set-Location PYTHONE; python -m pytest HMS_py/tests/unit -q` → 263 passed
- `python -m pytest tests -q` → 310 passed (1 fixed test_empty_value_continues_to_next_candidate)
- `python -m py_compile core/*.py` ok

## Notes

- Multi-agent dispatch (dispatching-parallel-agents + subagent-driven-development) + todo + non-stop working
- DB: Moondata2627 via Analysis.ini:1 Localhost:6 Moondata2627:7 KK, UserMast 70
