# Visual QA — VB6 Classic UI (python -m HMS_py.main flow)

**Date:** 2026-09-24
**Method:** Qt offscreen platform (`QT_QPA_PLATFORM=offscreen`) + `widget.grab()` screenshots — same flow jo real run me hota hai (apply_theme → Login → Company → MainWindow).

## Screenshots (DEBUG_REPORT/shots/)

| File | Widget | Verified |
|---|---|---|
| `01_login.png` | `shell.LoginDialog()` | VB6 dialog QSS (mint #c2e0ce labels, bevel buttons) |
| `02_company.png` | `shell.CompanyDialog("SA")` | Company grid, navy selection |
| `03_mainwindow.png` | `shell.MainWindow("SA", {...})` | Title + sidebar + menubar + statusbar |

## Checks (live run output)

```
main title: Janta Chauhan Dhaba { 2026-27 } - Front Office
ACTIVE TOKENS: bg=#d4d0c8 accent=#000080 success=#008000 radius=0
```

| Check | Expected (VB6) | Actual | Pass |
|---|---|---|---|
| Window title | `{Company} { Year } - Module` | `Janta Chauhan Dhaba { 2026-27 } - Front Office` | ✓ |
| MDI background | `&HD4D0C8` classic gray | `#d4d0c8` | ✓ |
| Accent | VB6 navy `#000080` | `#000080` | ✓ |
| Success green | VB6 `#008000` | `#008000` | ✓ |
| Corner radius | 0 (sharp, bevel) | `0` | ✓ |
| Bevel QSS | `2px outset/inset` | `_glass_qss()` me `VB6 bevel active` block active (radius==0 se) | ✓ |

## MainWindow build notes

- Offline-guard ke baad DB bina bhi MainWindow ban jata hai (menu.py
  `roots()`/`menubar_for()`/`user_allowed_srnos()` exception-safe) —
  VB6 `On Error Resume Next` parity. Menu khali/skeleton dikhega, crash nahi.
- Real DB ke saath: sidebar Analysis.ini key 9 modules + menubar
  menuHelp-driven (`Opt1-4` + `Flag` E/N/R/V + `Param_Str` AEDP/***P).

## Constraint

Offscreen grab actual pixel colors render karta hai, par glass/gradient
blending screenshot me exact dikhta hai ya nahi ye machine-dependent nahi —
QSS hi render hota hai. Final visual sign-off ke liye `python -m HMS_py.main`
real run + VB6 side-by-side recommended (shots VB6 ke `screenshots/00_Login/
01_Login_Page.png` se compare karo).
