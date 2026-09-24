---
name: vb6-python-parity
description: >-
  VB6 HMS codebase aur Python (PyQt6) port ke beech side-by-side parity
  comparison karne ka systematic workflow. Use when the user asks to
  compare VB6 and Python code, find missing forms/features/logic in the
  port, or implement VB6-faithful behavior. Covers form inventory
  extraction, menu-tree mapping, per-form parity matrix, and the
  porting recipe (schema -> core ops -> UI -> shell registry -> verify).
---

# VB6 ↔ Python Parity Workflow

Project context: VB6 HMS (decompiled .frm/.bas/.frx at project root,
e.g. `frmCompany.frm`, `MDIForm1.frm`) vs Python port in
`HMS_py/` (`HMS_py/core/*.py` logic, `HMS_py/ui/*_ui.py` forms,
`HMS_py/ui/shell.py` MDI shell). DB is SQL Server via
`HMS_py/core/db.py` (`db.query`, tables live in the same DB the VB6
app used — mostly EMPTY schema-only except a few populated tables).

## 1. Inventory extract (VB6 side)

- Forms: `*.frm` at project root. `Begin VB.Form <Name>` +
  `Caption = "..."` line 2-4. Key evidence inside:
  - Data source: `DataSource =`, `RecordSource =`, or SQL strings in
    `Private Sub Form_Load` / `Cmd*_Click`.
  - Tables: grep `FROM <table>` / `INSERT INTO` / `UPDATE <table>` in
    the .frm (decompiled SQL is inline, often via `Execute`/`OpenRes`).
  - Buttons: `Begin VB.CommandButton Cmd<Name>` + `Caption = "..."`.
- Menu: `MDIForm1.frm` `Begin VB.Menu mnu<Name>` tree (nested Begin/End
  = submenu levels). menuHelp table rows mirror this (Opt1..Opt4).
- Shared logic: `*.bas` modules (FaLib.bas, BanqModule.bas, ...).

## 2. Inventory extract (Python side)

- Form openers: `HMS_py/ui/shell.py` `_form_registry()` — keys are the
  menu leaf captions. This is the single source of truth for
  "implemented & wired".
- Blocked/missing: captions resolved to `_coming_soon(...)` or absent
  from registry. `_qa/audit_menuhelp_dynamic.py` walks menuHelp tree vs
  registry + reports-engine and writes MENUHELP_MISSING_OPTIONS.txt.
- Core logic per table: `HMS_py/core/*.py` (one file per domain:
  folio.py, checkin.py, pos_sales.py, smartcard_ops.py, ...).

## 3. Parity matrix (side-by-side)

For each VB6 form produce one matrix row:

```
| VB6 form | Caption | VB6 tables (evidence) | Python UI | Python core | Status |
```

Status values:
- `DONE`       — UI + core + registry wired + verified
- `PARTIAL`    — wired but logic differs from VB6 (note the diff)
- `UI-ONLY`    — form exists, core logic missing (queries inline in UI)
- `BLOCKED-TBL`— tables absent in DB (VB6 form also table-less or legacy)
- `MISSING`    — no Python port at all

Generate programmatically (never hand-wave): scan `*.frm` captions,
grep inline SQL for table names, then probe DB with
`SELECT COUNT(*) FROM <table>` (catch "table absent" separately), and
diff against shell registry keys (case-insensitive: menuHelp captions
arrive lowercase; registry keys are original-case).

Write the report to `VB6_PARITY_MATRIX.txt` at project root with
sections per status bucket + per-module counts.

## 4. Porting recipe (implementing a MISSING item)

Order matters (tests depend on it):

1. **Schema probe first**: `db.query("SELECT TOP 1 * FROM <table>")` —
   if absent, port is `BLOCKED-TBL`, document in matrix (VB6 evidence:
   form was unused there too) and STOP. Never invent tables.
2. **Core logic** `HMS_py/core/<domain>.py`: port the VB6 Sub/Function
   bodies faithfully — copy the fill-query (WHERE clauses, JOINs, ORDER
   BY) and the save-sequence (INSERT/UPDATE order, transaction with
   `cn.commit()`). Name helpers after the VB6 semantics
   (e.g. `auto_settle_pending` from `Fill`/`Proc_341_20`).
3. **UI** `HMS_py/ui/<domain>_ui.py`: grid+buttons pattern for
   list/action forms (`open_<name>(parent=None)` factory returning a
   modal QDialog); CRUD masters use `base_master.py` config pattern.
   VB6 captions/labels stay verbatim (VB6 quirks included).
4. **Registry wire** in `shell.py` `_form_registry()`: exact VB6 menu
   caption as key (the audit is caption-keyed).
5. **Verify**: `python -m py_compile` + headless smoke
   (offscreen QApplication + open the form + exercise core helper +
   `pytest HMS_py/tests`). Add the caption to the audit script's
   wired-list if it maintains one.

## 5. Conventions & gotchas

- DB access always via `HMS_py/core/db.py`; never open second
  connections inside one transaction (self-deadlock seen in practice).
- Reserved words in queries need brackets: `[Option]`.
- Case-insensitive registry lookups (`_reg_ci`) — menuHelp lowercases
  captions; plain dict `.get()` misses.
- VB6 BGR colors decode: `&HCEE0C2&` -> `#C2E0CE` (reverse pairs).
- `menuHelp.Param_Str` rights: 'AEDP' full; missing letters = no right;
  Flag 'V' = hidden; Flag '-'/'S' = separator rows (never clickable).
- Parallel agents edit this repo: commit early per task
  (`git add <files> && git commit`), keep changes file-scoped.
