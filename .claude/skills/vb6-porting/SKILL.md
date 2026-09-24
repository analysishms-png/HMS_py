# VB6 Porting Agent Skill

## Description
Specialized agent for porting VB6 HMS (Hotel Management System) code to Python/PyQt6.
Use this skill when the user says 'port VB6', 'VB6 to Python', 'find missing forms', 'side-by-side comparison', 'port module', or 'VB6 form'.

## Workflow

### Step 1: Understand the VB6 Source
- VB6 source is in `FODER/` directory (.frm, .bas, .cls, .frx files)
- `FODER/HMS.bas` contains MDIForm1 event handlers (995K lines of decompiled P-Code)
- `VB6_VS_PYTHON_LOGIC_COMPARISON.txt` (897 lines) has complete system analysis
- `FODER/DECOMPILE_REPORT.txt` lists 494 decompiled files
- `mdi_menu.json` has the VB6 MDI menu tree structure (3291 lines)

### Step 2: Map VB6 to Python
Use this mapping:
- VB6 .frm form → Python ui/*.py module (PyQt6 QDialog/QMainWindow)
- VB6 .bas module → Python core/*.py module (business logic)
- VB6 MDIForm1 → shell.py MainWindow
- VB6 menuHelp table → core/menu_help.py
- VB6 Analysis.ini → same file (shared config)
- VB6 ADODB → Python pyodbc (core/db.py)
- VB6 MSFlexGrid → QTableWidget
- VB6 Crystal Reports → reports.py (print-to-file)

### Step 3: Identify Missing Pieces
Key resources:
- `VB6_VS_PYTHON_LOGIC_COMPARISON.txt` Part K (Known Gaps) lists 20 missing tables and 50+ unported forms
- `mdi_menu.json` lists all 24 top-level menus with ~180 leaf items
- `sidebar_buttons.py` AUTO_OPEN and DIRECT_ACTIONS define what's implemented
- `shell.py` _form_registry defines what has Python openers
- `debug_mainsetup.py` compares VB6 MDI items vs registry vs workbench

### Step 4: Implementation Pattern
When porting a VB6 form:
1. Read the VB6 .frm file for structure and event handlers
2. Read the corresponding core/*.py for business logic
3. Create ui/*_ui.py using BaseMasterForm or QDialog
4. Add entry to shell.py _form_registry
5. Add to menuHelp table data if needed
6. Add to debug_mainsetup.py vb6_menus dict if it's a MainSetup item
7. Add tests to tests/unit/ or tests/database/

### Step 5: Known Missing Items (Priority Order)

#### Tables Not in DB (20):
HallBill, CateringBook, EventMast, BanquetSundry, TelCall, Extension, SmartCard, RewardPoint, BookingInquiry + 11 more

#### Forms Not Ported (50+):
MDIForm1 (partial), frmWelcome, frmYearEnd, eInvoice.bas, frmGodrejLockSettings, MemberSMS, FrmJobScheduler, Touch Screen variants (10+)

#### Features Not Implemented:
Crystal Reports, Touch Screen UI, Smart Card encode/decode, Door Lock integration, E-Invoice/GST API, SMS HTTP, Win32 SendInput, ZIP compression, Tally XML export, Multi-site data transfer

#### Known Python Bugs (10):
pos_sales.py vals[50] duplicate, inventory.py hardcoded KK000265, + 8 more (all documented in VB6_VS_PYTHON_LOGIC_COMPARISON.txt Part K4)

## Agent Usage
When dispatched, this agent should:
1. Read VB6 source files to understand form structure
2. Cross-reference with Python code to find gaps
3. Create implementation plans for each missing form/module
4. Write the Python implementation
5. Add to _form_registry, sidebar_buttons, debug_mainsetup
6. Add tests
7. Verify all tests pass

Output format: Structured JSON with {module: status, missing_items: list, implementation_plan: string}
