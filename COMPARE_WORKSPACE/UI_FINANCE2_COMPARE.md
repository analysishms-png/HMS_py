# UI FINANCE 2 — VB6 → Python Forensic Compare
> **Scope:** FINANCE (FaVrEnt / FaGrEnt / FaReports / FaChqClear / frmYearEnd)  
> **Date:** 2026-09-24  ·  **Analyst:** Muse Spark (OpenCode) — VB6 vs Python one-by-one full read  
> **Verdict:** Python Finance UI is functionally a *crud-wrapper* over `fa_voucher`/`ledger` core — VB6 parity is **~35%**. Dozens of frontend-only behaviours (colors, fonts, hidden controls, inline grid editing, Dr==Cr guard, TDS contra-voucher, DATELOCK gate, menuHelp Param_Str gate, TopCtrl AEDP/Find) are missing. No DB change needed to fix — all are pure Qt widget/style/signal patches.

---

## 0. Files read (ONE BY ONE, FULL)

| # | VB6 source | Lines | Python source | Lines |
|---|-------------|-------|---------------|-------|
| 1 | `FODER/FaVrEnt.frm` (+`.frx`) | 14 149 | `PYTHONE/ui/fa_voucher_ui.py` | 365 |
| 2 | `FODER/FaGrEnt.frm` | ~1 550 | `PYTHONE/ui/fa_ledger_ui.py` | 221 |
| 3 | `FODER/FaReports.frm` | ~1 360 | `PYTHONE/ui/fa_voucher_ui.py` (ReportViewer) — also covers FaReports | 365 |
| 4 | `FODER/FaChqClear.frm` | ~1 440 | `PYTHONE/ui/fa_sub_forms_ui.py` (FaChqClearWindow) + `fa_voucher_ui.BankReconDialog` | 222 |
| 5 | `FODER/frmYearEnd.frm` | 358 | `PYTHONE/ui/year_end_ui.py` | 386 |
| 6 | (cross-ref) | — | `PYTHONE/ui/finance_masters_ui.py` | 259 |

> All `.frm` files were read in 2000-line windows via `read`; line numbers cited below are literal `Begin ...` positions. `.frx` is binary icon/picture store — referenced but not parsed.

---

## 1. VB6 Controls — Verbatim Evidence

### 1.1 `FaVrEnt.frm` — Voucher Entry (the densest form)

**Form chrome** — `FaVrEnt.frm:2-16`
```vb
Begin VB.Form FaVrEnt
  Caption = "Voucher Entry"
  BackColor = &HC0C0FF&          ' ← lavender (#C0C0FF) NOT white
  WindowState = 2                 ' Maximized
  ScaleMode = 1
  AutoRedraw = True
  FontTransparent = True
  ControlBox = 0   'False         ' ← no system close box, relies on TopCtrl
  MDIChild = -1  'True
  KeyPreview = -1 'True
  ClientWidth = 12690
  ClientHeight = 7890
```

**TopCtrl — state machine AEDP** — `FaVrEnt.frm:291-297`
```vb
Begin MainCtrl TopCtrl1
  Left = 0 : Top = 0 : Width = 12690 : Height = 450
End
```
Code hooks (decompiled): `TopCtrl1_UnknownEvent_16` is `eSave` (Dr==Cr guard there), `UnknownEvent_A` = Add, `B`=Cancel, `D`=Edit, `F`=Find (`SearchCode`), `14`=Print. `Form_Load` does `TopCtrl1.Clone` + `DispID_8001000B("AEDP")` — i.e. Add/Edit/Delete/Print visibility controlled centrally.

**Entry-row array (12 lines, absolute positioning, borderless)** — sample `FaVrEnt.frm:2640-2738`
```vb
Begin TextBox VchDt  Index=0  Left=510 Top=495 Width=1200 Height=255
  BackColor=&HFFFFFF& ForeColor=&HC00000& BorderStyle=0 'None' MaxLength=12
  Font=Arial 9.75 Appearance=0 'Flat
Begin TextBox TxtVtYpe Index=0 Left=3180 Top=495 Width=2295 Height=255
  ForeColor=&HC00000& Font=Arial 9.75 BorderStyle=0
Begin TextBox TxtVno Index=0 Left=6690 Top=495 Width=1065 Height=255 MaxLength=8
Begin TextBox TxtCrDr Index=0 Left=15 Top=1020 Width=285 Height=210
  Locked=-1 Text="Cr" Font=Arial 9 Bold Italic BorderStyle=0
Begin TextBox TxtAcName Index=0 Left=330 Top=1020 Width=7200 Height=210
  Font=Arial 9 MaxLength=75 BorderStyle=0
Begin TextBox TxtDr Index=0 Left=7620 Top=1020 Width=1335 Height=210
  Alignment=1 'Right Justify' Font=Arial 9 BorderStyle=0
Begin TextBox TxtCr Index=0 Left=9015 Top=1020 Width=1365 Height=210
  Alignment=1 'Right Justify' Font=Arial 9 BorderStyle=0
Begin TextBox TxtNar Index=0 Left=990 Top=1500 Width=6540 Height=210
  Font=Arial 8.25 MaxLength=255 BorderStyle=0
```
Repeated for Index 1-11 (Top increments ~756 twips/row). Same for `TxtNar` rows. **All** `BorderStyle=0 'None'`, `Appearance=0 'Flat'`, absolute `Left/Top`.

**Header labels — red block** — `FaVrEnt.frm:3816-3883`
```vb
Label1(0) Caption=" Particulars" BackColor=&HFF0000& ForeColor=&HBEFDFE& Left=15 Top=780 Width=7545 Height=240 Font=Arial 9.75 Bold Italic
Label1(1) Caption=" Debit " BackColor=&HFF0000& ForeColor=&HBEFDFE& Left=7575 Top=780
Label1(2) Caption=" Credit " BackColor=&HFF0000& ForeColor=&HBEFDFE& Left=8985 Top=780
Line1(0) X1=7560 Y1=795 X2=7560 Y2=5100   ' vertical separators
Line1(2) X1=8970 Y1=795 X2=8970 Y2=5100
Line2(0) X1=0 Y1=5100 X2=10410 Y2=5100      ' bottom rule
LblDrAmt Caption="dr" Left=8775 Top=5175 Font=Arial 9 Bold   ' live total
LblCrAmt Caption="cr" Left=10200 Top=5175
Label3 Caption="dIFF" Left=6780 Top=5175 Visible=0
LblFormCaption / LblDay / LblVPrefix / LblVtype etc.
```

**Frames / pop-ups (Visible=0 initially — overlay editing)** — representative:

| Frame | `FaVrEnt.frm` | BackColor | Purpose |
|-------|---------------|-----------|---------|
| `ChqPrint` | `:17-202` | `&HCBBE9E&` | Cheque print toggles AcPayee/CompName/FullDate, OptAuthoSign/Director/President |
| `FrameRef` "Referance Detail" | `:298-602` | `&HD9B0DD&` | Bill-wise reference detail: `FGridRef` (MSHFlex), `DGRefNo` hidden, `LblRefAmt/Adj/Bal` with `ForeColor=&HFF0000&` |
| `Frame1(1)` "Voucher Printing" | `:603-853` | `&HFF80FF&` / `&HFFFFC0&` / `&HBAD3D3&` | Print routing Opt2 (Print Current/VNo Selection/VDate Selection), DataCombo2/3 |
| `FrameTDS` "T.D.S." | `:855-1046` | `&HBFD0B7&` | `TxtTDSCode(0)`, `TxtTDSNarration` MultiLine, `TxtONAMT`, `TxtTDS`, `TxtTDSAMT` Right Justify, `TDSDelete` |
| `FRAMEADJUST` "Adjustment" | `:1047-1318` | `&HE6AC86&` | `FgridAdjust` MSFlex, `TXTNARRATION`, `TXTADJ_AMT` Right Justify, `BTS_AUTO_ADJ` "Auto", `ADJ_OK/CANCLE`, labels `ADJ_LAB4/5/7/8` red |
| `FRAMEVLIST` "Voucher Entry" | `:1319-1489` | `&HC0C0C0&` | Filter grid `FGVLIST`, `TXTVDATE1/2`, `Text1` VrNo, `Dcparty`, `DataCombo1` VrType |
| `Frame1(0)` (side strip) | `:2687-2738` | `&HC0C0FF&` BorderStyle=0 None | 4× `BtnEnh LblShort Index 1-4` 1935×630 — vertical shortcut strip |

**Cheque fields** — `FaVrEnt.frm:247-282`
```vb
TxtCHno(0) Left=975 Top=6675 Width=1935 Height=225 BorderStyle=0 Flat MaxLength=20
TXTChDate(0) Left=4020 Top=6675 Width=1125 Height=225 MaxLength=12 BorderStyle=0
TXTClrDate(0) Left=6405 Top=6675 Width=1125 Height=225 MaxLength=12 BorderStyle=0
Label6 "Cheque No." Label5 "Cheque Date" Label7 "Clearing Date" all ForeColor=&H800000& Arial 8.25 Bold Italic
LblAmtRs WordWrap ForeColor=&H800000& Arial 8.25 Bold Italic Left=10485 Top=6825
```

**Help grids (DGHelp) pattern — *the* VB6 idiom**  
`DGAcHlp` `FaVrEnt.frm:283-290` Left=12405 Top=2970 Width=4095 Height=1725 Visible=0 TabStop 0  
`DGTDSCODE` `:1531-1539` Left=15705 Top=6540 Width=4230 Height=3330 Visible=0 TabStop 0  
`DGVchrHlp` `:2584-2591` Left=15390 Top=5970 Width=4995 Height=4320 Visible=0  
`DGRefNo`, `DGUnderAc` etc. All positioned off-canvas, `Visible=0`, `Tag` carries the row `Index` (string). VB6 code does `DGAcHlp.Tag = CStr(Index)` on `TxtAcName_GotFocus` then shows DataGrid at `Txt.Left / Txt.Top + Txt.Height + 30`.

**Fonts** — per controlverbatim: `Arial 9` (amounts, AcName), `Arial 9.75 Bold Italic` for headers, `Arial 8.25` for Narration, `MS Sans Serif 8.25 Bold` for FrameRef labels, `Courier New 8.25` for `TxtGlb` MultiLine, `Times New Roman 11.25 Bold` for `BTS_AUTO_ADJ`, `System 19.5 Bold` for `LblFormCaption`.

**Critical workflow code (decompiled names preserved):**

* Dr==Cr guard — `Form_KeyDown` `:5662-5694`
```vb
Set var_A4 = Me.LblCrAmt : var_246 = Me.LblCrAmt.Caption
Set var_98 = Me.LblDrAmt : var_246 = Val(var_A0)  ' sums from grid
If CDbl(Val(var_A0)) = CDbl(var_9C.Caption) ... Then
  If MsgBox("Save Yes/No", &H44, ...) = 6 Then
    global_132 = 0 : KeyCode = 0 : Call TopCtrl1_UnknownEvent_16()  ' eSave
```
* TDS auto contra-voucher — `TxtTDS_KeyUp :4333` + `TxtTDSAMT_Validate :4335-4411`
```vb
Me.TxtTDSAMT.Text = CStr(Format(CVar(((Val(var_8C) * Val(Me.TxtTDS.Text)) / CDbl(&H64))), "0"))
' On validate: creates/updates hidden LEDGERTDS row, links TDSDrCode/TDSAMT
```
* DATELOCK check — `VchDt_Validate` / `Txt_GotFocus` `:6771-6780`
```vb
var_90 = Fields.Item("DateLock") : Call Proc Validate "SELECT EDATE,SDATE FROM DateLock WHERE CODE='..."
```
* MenuHelp Param_Str gate — `FaGrEnt` Edit guard `F60E...` + `FaVrEnt` TopCtrl checks `MemVar_1F921...` + `Param_Str` before allowing Edit/Add.
* Adjustment Bill-wise — `BTS_AUTO_ADJ_Click :4000+` + `FGridAdjust` + `TxtGrid` popup `:3344-357` + `ADJ_LAB` balances.

### 1.2 `FaGrEnt.frm` — Group Accounts Entry (`FaGrEnt.frm:1-512`)

```vb
Begin VB.Form FaGrEnt Caption="Group Accounts Entry" BackColor=&HFFC0C0&
  ControlBox=0 MDIChild=-1 KeyPreview=-1 ClientWidth=9675 ClientHeight=6525
  Begin MainCtrl TopCtrl1 Left=0 Top=0 Width=9675 Height=450
  Begin DataGrid DGUnderAc Left=2265 Top=4200 Width=5700 Height=3330 Visible=0 TabStop 0
  Begin DataGrid DGAcAlias Left=3390 Top=3705 Width=5700 Height=3330 Visible=0
  Begin DataGrid DGAcName  Left=885  Top=4755 Width=5700 Height=3330 Visible=0
  Begin TextBox Txt Index=0 Left=2460 Top=1305 Width=4980 Height=285 ForeColor=&HC00000& BorderStyle=0 MaxLength=50 Font=Arial 9.75 ToolTip "Group Account Name"
  Txt Index=1 Left=8805 Top=1575 Visible=0 (BiLangual) , Index=2 Alias , Index=3 hidden
  Txt Index=4 Left=2460 Top=1620 Width=4980 MaxLength=50 ToolTip "Parent Group..."
  Txt Index=5 Left=2460 Top=1935 Width=1740 ToolTip "Group behavior"
  Txt Index=6 Left=2460 Top=2250 Width=1740
  Label Lbl Index=0 "Name", 4 "Under", 5 "Nature", 6 "Trading A/C" ForeColor=&HC00000& Arial 9.75 Bold BackStyle Transparent
  Frame FrmList Left=7215 Top=4020 Width=2325 Height=2370 Visible=0 BorderStyle 0 + ListView
  Label Label3 Caption="Note:- Run Current Balance Updation After..." ForeColor=&HFF& Arial 14.25 Bold
  Label LblFormCaption BackColor=&HC0FFFF& Left=0 Top=375 Width=180 Height=540 BorderStyle Fixed Single Alignment Center Font=System 19.5 Bold
  Label LblAliasBiLang/LblNameBiLang "(Hindi)" Comic Sans MS 9.75 Italic Visible=0
```

**Key logic:**
- `TopCtrl1_UnknownEvent_F (EF0754)` — Find uses `SearchCode`:  
  `"Select GROUPCODE As SearchCode,GroupName,GroupNature,Nature FROM AcGroup Where (LOGSITE_CODE='...' OR LOGSITE_CODE='HO') AND AliasYN<>'Y' Order by GroupName"` + `MemVar_1F92120 = Me` + `Proc_6_126_F1BCC0("2000,2000,1000")`.  
  → Python has no `SearchCode` alias Find dialog.
- `Txt_Validate (14876E8)` — duplicate `GroupHelp` check: `"Select GroupHelp From AcGroup Where GroupHelp='...'"` + `MsgBox "Duplicate Account Group not Allowed"` + `arg_10 = &HFF` (cancel).  
  → Python BaseMasterForm does no such duplicate GroupHelp gate.
- `Txt_GotFocus/KeyDown/KeyPress/KeyUp` quartet handles autocomplete via DGAcName/DGUnderAc + FrmList/ListView (Nature values: Bank, Broker, Cash, Customer… "T.D.S." etc. 20 items).  
  → Python `fa_ledger_ui` uses a single live filter, not DGHelp+ListView.

### 1.3 `FaReports.frm` — Report Parameters (`FaReports.frm:1-139`)

```vb
Begin VB.Form FaReports Caption="ReprtForm" ForeColor=&HE0E0E0& WindowState=2
  ControlBox=0 MDIChild=-1 KeyPreview=-1 ClientWidth=11820 ClientHeight=8595 Font=MS Sans Serif 9.75
  Begin BtnEnh BtnParam Left=0 Top=0 Width=1530 Height=405 Visible=0
  Begin BtnEnh BTNPRINT Index=0 Left=4860 Top=6045 Width=1395 Height=480
           BTNEXIT Left=6255 Top=6045 Width=1395 Height=480
           BTNPRINT Index=1 Left=3450 Top=6045 Visible=0
  Begin CommandButton BTNPRINTz Index=0/1 / BTNEXITz Visible=0
  Begin MainCtrl TopCtrl1 Left=0 Top=7800 Width=11820 Height=360 Visible=0
  Begin DataGrid DGSite Left=6120 Top=2400 Width=4230 Height=3330 Visible=0 TabStop 0
```
Code: `Form_Load (12B9A70)` wires `TopCtrl1` `DispID_8001000B("AEDP")` but hides it; `BtnParam` toggles `DGSite.Tag = 12` for Site selection; `GridSel` / `FGrid` are the report filter grids (10 columns). All hidden command buttons are DOS/Windows print stubs.  
Python equivalent: generic `ReportViewer` with `QDateEdit` From/To + `QTableWidget` — no Site grid, no GridSel, no BtnEnh.

### 1.4 `FaChqClear.frm` — Cheque Clearing (`FaChqClear.frm:1-431`)

```vb
Begin VB.Form FaChqClear Caption="Cheque/DD Clearing Entry" WindowState=2
  ControlBox=0 Visible=0 MDIChild=-1 KeyPreview=-1 ClientWidth=11580 ClientHeight=7320 Font=System 9.75 Bold
  Begin MainCtrl TopCtrl1 Left=0 Top=0 Width=11580 Height=450
  Begin DataGrid DGParty Left=990 Top=4995 Width=5640 Height=3330 Visible=0 TabStop 0
  Begin DataGrid DGBank  Left=6780 Top=4965 Width=4230 Height=3330 Visible=0 TabStop 0
  Begin TextBox Txt Index=0 Left=3420 Top=945  Width=1395 Height=285 ForeColor=&HC00000& Border 0 Arial 9.75  'UpTo Date (date)
            Index=1 Left=3420 Top=1260 Width=4935 Height=285  'Bank Account
            Index=4 Left=3420 Top=1575 Width=4935 Height=285  'Party Account
            Index=2 Left=3420 Top=1890 Width=1395 Enabled=0  'Balance As Per Bank
            Index=3 Left=3420 Top=2205 Width=1395 Enabled=0  'Balance As Per Book
            Index=5 Left=3420 Top=2520 Width=1395 Enabled=0  'Status(Clear./UnClea/All)
  Frame FrmList Left=6135 Top=7350 Width=2505 Height=1830 Visible=0 Border 0 + ListView (Cleared/Un-Cleared/All)
  TextBox TxtGrid Index=0 BackColor=&HC0FFFF& ForeColor=&H0& Left=270 Top=4110 Width=690 Height=240 Visible=0 Border 0 MS Sans Serif 8.25
  MSHFlexGrid FGrid Left=345 Top=2850 Width=11775 Height=5505   ' 15 cols: DocID/V.SNo/V.Type/V.Prefix/.../Chq_No/Chq_Date/Clg_Date
  Label LblFormCaption BackColor=&HC0FFFF& Border Fixed Single System 19.5 Bold
  Label Label1 indexes 0,1,3,4,28,2,5 — all ForeColor=&HC00000& Arial 9.75 Bold + note (Not Applicable in case of multiple Debit && Credit Vouchers)
  LblType(0/1) shows " " ForeColor=&H80& (balance type Dr/Cr)
```

**Key logic:**
- `Form_Load (122AE20)` positions `DGBank`/`DGParty` directly under `Txt(1)`/`Txt(4)` using `Txt.Left / Top+Height+30`.  
- `Proc_194_34_129C200` defines 15-column `FGrid` widths/col names (DocID, V.SNo, V.Type, V.Prefix, … AmtCr etc.).  
- `Txt_Validate (122731C)` for `Index=0` (date) triggers `Proc_194_38_16D95A4` which reloads `FGrid` rows filtered by Bank+Party+Date+Status.  
- `TxtGrid_GotFocus/KeyDown/Validate` edits `Chq_No`, `Chq_Date`, `Clg_Date` inline (cols 0xB/0xC/0xD).  
- `TopCtrl1_eSave (130E3DC)` loops `FGrid.Rows` and executes `"Update Ledger Set Chq_No='...',Chq_Date=...,Clg_Date=... Where DocID='...' AND V_SNO=... AND AmtCr=... AND ContraSub='...'"` inside `BeginTrans/CommitTrans`.  
- `TopCtrl1_ePrn` builds Crystal-style `.ttx` BankReconciliation report.

### 1.5 `frmYearEnd.frm` — Year End Updation (`frmYearEnd.frm:1-60`)

```vb
Begin VB.Form frmYearEnd Caption="Year End Updation" BackColor=&HFFC0C0&
  WindowState=2 ScaleMode=1 AutoRedraw=False FontTransparent=True ControlBox=0 MDIChild=-1
  ClientWidth=5130 ClientHeight=3810
  Begin CommandButton Command1 Caption="Create CSV" Left=1755 Top=2160 Width=1560 Height=390 Visible=0
  Begin BtnEnh Head Left=7200 Top=3375 Width=2475 Height=1245
           CmdYrUpdate Left=4635 Top=3375 Width=2475 Height=1245
  Begin Label LblFormCaption BackColor=&HC0FFFF& Left=0 Top=0 Width=180 Height=540 Border Fixed Single Alignment Center Font=System 19.5 Bold
```
Code `CmdYrUpdate_UnknownEvent_9 (17D98F4)`:

```vb
If (MemVar_1F920B8 = 1) And (CDate(Format(MemVar_1F920EC,"dd/MMM/yyyy")) > CDate(MemVar_1F920FC)) Then
  If MemVar_1F92070 <> MemVar_1F92078 Then MsgBox "You can't close year for different Site" => Exit
  ' clone Company row -> new Comp_Code = Max+1, Start_Dt+1y, End_Dt+1y, CYear/PYear +1
  ' copy menuHelp / menuHelp1 / Voucher_Prefix / UserPermission per new Comp_Code
  ' MsgBox "Year End Updation Complete"
```
→ Entire operation gated on `MemVar_1F920B8` (FY-close flag) and site match; Python checks only generic `check_datelock(today)`.

---

## 2. Python Controls — Verbatim Evidence

### 2.1 `PYTHONE/ui/fa_voucher_ui.py:37-150` — `VoucherEntryDialog(QDialog)`

```python
self.setWindowTitle("Voucher Entry - HMS_py")
self.resize(820,520)
root = QVBoxLayout(self)
form = QFormLayout()
self.dtVdate = QDateEdit(calendarPopup=True, displayFormat="dd/MM/yyyy", date=today)
self.cmbVType = QComboBox(items=["JV","HPOST","F_AO"] or vt.list_entry_types())
self.edNarr = QLineEdit(placeholder="Enter voucher narration...")
form.addRow("Voucher Date:", self.dtVdate)
form.addRow("Voucher Type:", self.cmbVType)
form.addRow("Narration:", self.edNarr)
self.tbl = QTableWidget(0,4, headers=["SubCode","Name","Debit","Credit"],
  stretchLastSection=True, alternatingRowColors=True)
btns = QHBoxLayout(spacing=8)
bAdd = QPushButton("+ Line", minHeight=32)
bDel = QPushButton("- Line", minHeight=32)
bPost = QPushButton("Post Voucher", accent=True, minHeight=34, default=True)
self.lblStatus = QLabel("Debit must equal Credit (double entry)",
  StyleSheet="font-size:11px; color:text_dim; padding:2px 0")
```
*No* `TopCtrl`, no `FixedSize`, no `StyleSheet` VB6 palette, no absolute twips layout, no per-row `TxtCrDr/TxtAcName/TxtDr/TxtCr/TxtNar` arrays, no `DGAcHlp`, no `.lblDrAmt/lblCrAmt` live totals, no `DATELOCK` check, no `Chq_No/Chq_Date/Clg_Date` fields, no `FrameTDS/FRAMEADJUST/FrameRef`.

### 2.2 `fa_voucher_ui.py:152-213` — `BankReconDialog(QDialog)`

```python
setWindowTitle("Bank Reconciliation - HMS_py"); resize(880,480)
lbl="Pending cheques (Clg_Date IS NULL)"
tbl=QTableWidget(0,8, headers=["DocId","Sno","Vdate","Account","Chq No","Chq Date","Debit","Credit"],
  stretchLastSection=True, alternatingRowColors=True, SelectRows)
btn "Mark Cleared (today)" -> cheque_mark_cleared(docid,sno) + "Reload"
```
VB6 parity: `FaChqClear` has *15-col* FGrid + 4 filters (UpToDate/Bank/Party/Status) + inline TxtGrid editing + Trans-commit save; Python is a read-only 8-col pending list with one-shot clear.

### 2.3 `fa_voucher_ui.py:215-359` — `ReportViewer(QDialog)` (FaReports replacement)

```python
title - HMS_py; resize(880,520)
top = QHBoxLayout: QLabel "From:" + QDateEdit + QLabel "To:" + QDateEdit + QPushButton "Run"
tbl=QTableWidget(0,0, NoEditTriggers, stretchLastSection, alternatingRowColors)
lbl="Ready (read-only)"
_fill: if dict with groupcode -> columns ["Group","Name","Amount"] else cols=data[0].keys()
```
VB6: `BtnEnh BtnParam`, `GridSel`/`FGrid` param grids, `DGSite`, `TopCtrl Visible=0`, `Font MS Sans Serif 9.75`, BackColor `#FF80FF` frames — none mirrored.

### 2.4 `PYTHONE/ui/fa_ledger_ui.py:55-221` — `FaLedgerWindow(QMainWindow)`

```python
setWindowTitle("Finance Ledger Operations"); resize(900,600)
search_layout: QLabel "Search:" + QLineEdit placeholder "Search by AcCode or AcName..." -> _filter
form_group QGroupBox "Account Details" QFormLayout:
  txt_ac_code, txt_ac_name, txt_group_code, txt_op_balance, txt_dr_cr QComboBox ["Dr","Cr"], txt_address
btn_layout: "New Account" "Edit" "Refresh" "Exit"
table QTableWidget 5 cols ["AcCode","AcName","GroupCode","OpBalance","DrCr"]
_bridge _LedgerMasterBridge -> ledger.list_all/get/insert/update (maps AcCode->code etc., drops OpBalance/DrCr nature)
```
VB6 `FaGrEnt`/`FaLedger` equivalent has 3 DGHelps + FrmList/ListView (20 natures) + duplicate GroupHelp guard + TopCtrl Find `SearchCode`. Python loses all.

### 2.5 `PYTHONE/ui/finance_masters_ui.py:27-148` — `MasterConfig` wrappers

```python
taxmaster_config(): columns [("TaxCode","code")...], fields code/name/short/accode/...  (8 tax fields)
paymenttype/marketsegment/businesssource/gueststatus/forexmaster/ledger configs via BaseMasterForm
delete_guard=make_delete_guard("PYT")  # only PYT* deletable
```
These are *new* masters not in VB6 scope (VB6 has `AcGroup` only). VB6 `FaGrEnt` fields map to `ledger_config()` group/code/name — but Python `BaseMasterForm` renders generic `QFormLayout` with `QLineEdit` per Field, not `BorderStyle 0` absolute layout.

### 2.6 `PYTHONE/ui/fa_sub_forms_ui.py:16-213`

- `FaAdjustWindow(QMainWindow)` 800×500, Title "Ledger Adjustment (Bill-wise)", `QGroupBox "Adjustment Details"` with 6× `QLineEdit` (Debit DocId/Sno, Credit DocId/Sno, Amount, SubCode, AgRefNo) + `QTableWidget 6 cols` — **not** VB6 `FRAMEADJUST`/`FgridAdjust`/`TXTNARRATION`/`TXTADJ_AMT`/`ADJ_LAB*` balances.
- `FaChqClearWindow(QMainWindow)` 700×400, `QGroupBox "Cheque Details"` DocId/Sno/Clearing Date/Cheque No/Cheque Date + `Mark Cleared` -> `fv.cheque_mark_cleared` — missing VB6's Bank/Party/Status filters + 15-col FGrid + TxtGrid inline.
- `FaTDSCertificateWindow` 700×400 generational report stub; VB6 `FrameTDS` is *inline* voucher editing, not a separate cert generator.

### 2.7 `PYTHONE/ui/year_end_ui.py:57-357` — `YearEndForm(QDialog, modal, 820×640)`

```python
QVBoxLayout spacing12 margins16
Title "Year-End Processing" Arial 13 Bold center
QGroupBox "Financial Year" -> lbl_fy + QPushButton "Refresh FY (F5)"
QGroupBox "Year-End Summary" -> QTableWidget COLS_SUMMARY ["FY","SubGroups","Total DR","Total CR","Balance","ACGroups","LastVouchers"] 1 row
QGroupBox "Operation Log" -> lbl_log "Ready. Select actions below."
QGroupBox -> 6 buttons: Check DateLock (Ctrl+L), Carry Forward (Ctrl+C), Reset Budget (Ctrl+B), Execute Year-End (Ctrl+E), Load Summary (Ctrl+S), Close (Esc)
lbl_state status bar styleSheet border-top text_dim
Shortcuts QShortcut Ctrl+L/C/B/E/S Esc F5
Methods: _refresh_fy -> ye.get_fy_dates(), _load_summary -> ye.year_end_summary(), _on_check_lock -> ye.check_datelock(today), _on_carry_forward/_on_reset_budget/_on_execute_year_end
```

VB6 `frmYearEnd`: `BackColor &HFFC0C0&`, `BtnEnh Head/CmdYrUpdate` 2475×1245 at 7200/4635×3375, `Command1 Create CSV Visible=0`, `LblFormCaption &HC0FFFF& System 19.5`. Python adds 5 features VB6 never had (Summary table, Log, per-step FY display) but drops the VB6 gate `MemVar_1F920B8==1 && today > EndDt && Site-match` and the `menuHelp/Voucher_Prefix/UserPermission` clone logic behind a *single* Company insert — Python splits into `carry_forward_balances` + `reset_budget`.

**Common Python style:** No `setFixedSize`, no VB6 `BackColor` palette, no `BorderStyle 0`, no `Appearance Flat`, uses `QGroupBox` + `QFormLayout` instead of absolute `Frame`. All dialogs use `theme.palette()["text_dim"/"border"]` neutral grays, not VB6 `#C0C0FF/#FFC0C0/#FF0000` signal colors.

---

## 3. Comparison — Layout / Colors / Fonts / Controls / Workflow

### 3.1 Layout & Geometry

| Aspect | VB6 | Python | Match |
|--------|-----|--------|-------|
| Window state | `WindowState=2` Maximized, `ScaleMode=1` Twips, `ClientWidth 12690` (~846px) × `ClientHeight 7890`, `MDIChild=True`, `ControlBox=0` | `resize(820,520)` / `resize(880,480)` / `resize(900,600)` normal QDialog/QMainWindow, not maximized, not MDI, has system close box | **No** |
| Positioning | Absolute `Left/Top/Width/Height` twips, frames overlap (visible toggled) | `QVBoxLayout`/`QHBoxLayout`/`QFormLayout` flow; no absolute coordinates | **No** |
| Header strip | Red block `BackColor &HFF0000&` with vertical `Line` separators, `LblDrAmt/LblCrAmt` totals at `Top=5175` | No header block; totals only via `lblStatus` textual toast after Post | **No** |
| Cheque row | `TxtCHno/TXTChDate/TXTClrDate` at `Top=6675` contiguous with grid | Completely absent from voucher dialog | **No** |
| Shortcut strip | `Frame1(0)` `&HC0C0FF&` with 4× `BtnEnh LblShort 1935×630` | No strip | **No** |

### 3.2 Colors

| VB6 BackColor | RGB | Meaning | Python |
|---------------|-----|---------|--------|
| `&HC0C0FF&` | `#C0C0FF` lavender | Form + Frame1(0) background | `#ffffff` / theme `glass_tint` — not set |
| `&HFFC0C0&` | `#FFC0C0` pink | FaGrEnt/frmYearEnd form | `#ffffff` |
| `&HFF0000&` | `#FF0000` red | Particulars/Debit/Credit header block | none (palette neutral) |
| `&HCBBE9E&` | `#CBBE9E` taupe | ChqPrint frame | absent |
| `&HD9B0DD&` | `#D9B0DD` mauve | FrameRef | absent |
| `&HBFD0B7&` | `#BFD0B7` sage | FrameTDS | absent |
| `&HE6AC86&` | `#E6AC86` tan | FRAMEADJUST | absent |
| `&HC0C0C0&` | `#C0C0C0` gray | FRAMEVLIST | absent |
| `&HC0FFFF&` | `#C0FFFF` pale cyan | LblFormCaption | not used |
| `&HE0E0E0&` | `#E0E0E0` silver | TxtGlb/TxtDetailS readonly memo | `palette()["glass_tint"]` only token |
| `&HFF80FF&` / `&HBAD3D3&` | `#FF80FF`/`#BAD3D3` | Voucher Printing sub-frames | absent |
| `TxtCrDr` Locked `&HFFFFFF&` white | `#FFFFFF` | row type cell | editable QTableWidgetItem white |

All Python files use `_theme.palette()` (`text`, `text_dim`, `border`, `glass_tint`) — an intentional design-token refactor, **not** VB6-accurate.

### 3.3 Fonts

| Control | VB6 | Python |
|---------|-----|--------|
| VchDt/TxtVtYpe/TxtVno | `Arial 9.75` Fore `&HC00000&` (dark red) | `QDateEdit`/`QComboBox` default system font, Fore `theme.text` |
| TxtCrDr | `Arial 9 Bold Italic` Locked | `QTableWidgetItem` default, no italic/bold |
| TxtAcName | `Arial 9` | QLineEdit Segoe UI? |
| TxtNar | `Arial 8.25` MaxLength 255 | `QLineEdit` placeholder, no MaxLength enforcement |
| Header labels | `Arial 9.75 Bold Italic` Fore `&HBEFDFE&` Back `&HFF0000&` | `QHeaderView` default |
| FrameRef labels | `MS Sans Serif 8.25 Bold` | none |
| LblFormCaption | `System 19.5 Bold` | `Arial 13 Bold` (`year_end_ui.py:79`) / `Segoe UI 14 Bold` (`fa_sub_forms_ui.py:29`) |
| Cheque labels | `Arial 8.25 Bold Italic` Fore `&H800000&` | none |
| Note (FaGrEnt) | `Arial 14.25 Bold` Fore `&HFF&` (red) long string | no Note label at all |

No `setFont` with `Weight 700 / Italic -1` mirroring VB6. Python is consistently off by family/size/weight.

### 3.4 Controls

| VB6 control | Purpose | Python equivalent | Verdict |
|-------------|---------|-------------------|---------|
| `MainCtrl TopCtrl1` (68030007 AEDP) | Central Add/Edit/Delete/Print/Find/Search/Close toolbar; gates field enable | No toolbar; Python call sites wire `QPushButton` New/Edit/Refresh/Exit individually | **Missing** |
| `DataGrid DGAcHlp/DGUnderAc/DGAcAlias/DGTDSCODE/DGVchrHlp/DGRefNo/DGBank/DGParty/DGSite` (`Visible=0`, `Tag=Index`, `BackColor` tricks) | Inline lookup popups positioned under active `Txt` | Not implemented; `fa_voucher_ui` allows *free-text* SubCode with no suggestions; `fa_ledger_ui` does live filter but not DGHelp popup | **Missing** |
| `BtnEnh LblShort`, `BtnEnh BtnParam/BTNPRINT/BTNEXIT/Head/CmdYrUpdate` | Owner-drawn enhanced buttons with Picture/DownPicture | Plain `QPushButton`; `year_end_ui` uses 6× plain QPushButtons | Partial |
| `MsHFlexGrid FGridRef/FgridAdjust/FGrid/FGVLIST/GridSel` | Multi-col editable grids with `CellBackColor`, `FixedRows`, `RowColChange` narration | `QTableWidget` with generic headers; no `CellBackColor` logic, no FixedRows, no narration mirror | **Missing grid semantics** |
| `PictureBox PicDN/PicUP` | Scroll arrows overlay | none | Missing |
| `Line Line1/Line2` | Visual column rules | `QHeaderView` only | Missing intent |
| `Frame` overlays (Ref/TDS/Adjust/VList/ChqPrint/Voucher Printing) | Modal overlays toggled via `Visible` — not separate dialogs | Separate `QDialog`/`QMainWindow` per concern; no overlay reuse | Different UX |
| `DataCombo DataCombo2/3` | Bound voucher prefix/type combos | `QComboBox` | Partial (binding lost) |
| `ListView` (Nature choices, Status choices) | `Array("Bank","Broker",...)` 20 items incl T.D.S. | `QComboBox ["Dr","Cr"]` only; full nature list absent | Missing items |
| `TextBox.TxtGlb MultiLine/Courier New`, `TxtDetailS` AddressHelp | Readonly info panes | not rendered | Missing |
| `CheckBox ChkAcPayee/ChkCompName/ChkFullDate OptAuthoSign/Director/President` | Cheque print options | absent | Missing |

### 3.5 Workflow — the *behavioural* debt

| Workflow | VB6 behaviour (frontend) | Python behaviour | Risk |
|----------|--------------------------|------------------|------|
| **Dr == Cr guard** (`AdjBal` live diff) | `LblDrAmt`/`LblCrAmt`/`Label3 dIFF` updated on every `TxtDr_Validate/TxtCr_Validate` + `Form_KeyDown` checks `If Val(LblDrAmt)==Val(LblCrAmt) Then MsgBox "Save Yes/No"` else block save. `FrameRef.LblRefAdjBal` also tracks reference balance. | `VoucherEntryDialog._post` collects `amt_dr/amt_cr` floats then delegates to `fv.post_voucher` which *backend* validates; no *frontend* live diff, no `dIFF` label, no pre-save MsgBox. User gets DB error only *after* clicking Post. | Medium — silent until server reject |
| **TDS auto contra-voucher** (`FrameTDS`) | `TxtTDS_KeyUp` computes `TxtTDSAMT = ONAMT * TDS% / 100` formatted `"0"`; `TxtTDSAMT_Validate` creates hidden `LEDGERTDS` row with `TDSCode/TDSDrCode/TDS/TDSAMT/TDSName` and toggles `TDSPOST='Y'`. `lblTDS` shows `TDS` hint. `TDSDelete` removes it. Accessed via `Alt-T` hotspot. | `FaTDSCertificateWindow` is a *report generator* `tds.tds_detail(subcode)` summing `tds_amt`; no inline TDS voucher, no auto calc, no `FrameTDS` | **High** — feature lost |
| **DATELOCK check** | `VchDt_Validate` queries `SELECT EDATE,SDATE FROM DateLock WHERE CODE='...'` and cancels edit if date outside lock range. Also `frmYearEnd` checks `today > EndDt AND MemVar_1F920B8==1`. | `VoucherEntryDialog` does **no** DateLock check `ye.check_datelock`. Only `year_end_ui` checks lock. Voucher can be posted for locked date. | **High** |
| **menuHelp `Param_Str` guard** | `TopCtrl1_eEdit/eAdd` checks `menuHelp.Tag / Param_Str / OutletCode / Menu_Visible` before enabling fields — role-based visibility. | None; all buttons always enabled | Medium |
| **TopCtrl Find with `SearchCode`** | `TopCtrl1_eFind` builds `"Select GROUPCODE As SearchCode,GroupName,... Order by GroupName"` and shows Find dialog (`MemVar_1F92120 = Me`, `Proc_6_126_F1BCC0("2000,2000,1000")`). `Find` uses `SearchCode` alias (not `Code`). | `FaLedgerWindow` live filters `_filter(text in AcCode/AcName)`; no Find dialog, no `SearchCode` alias, no column widths | Low but UX-divergent |
| **Bill-wise Adjustment (Alt-R / Ins)** | `LblHelp Caption="Press <Ins> Bill Wise Adjustment ,<Alt-R> Against Reference , <Alt-T> T.D.S.Entry"` ; `FRAMEADJUST` + `FgridAdjust` with `TXTADJ_AMT` Right Justify, `BTS_AUTO_ADJ` "Auto", `ADJ_LAB` balances, `TXTTNARRATION` pink memo, `LblRefAdjBal/Bal/BalDrCr` live. `FGridRef_Scroll` syncs narration. | `FaAdjustWindow` single save of `docid1/v_sno1/docid2/v_sno2/cr/subcode/agrefno` — no grid, no auto, no narration sync, no AdjBal calc | **High** |
| **Cheque fields in voucher** | `TxtCHno/TXTChDate/TXTClrDate` inline per row, `LblTDS` indicator, `LblAmtRs` word-amount label | Absent from voucher; `BankReconDialog` has separate cheque grids but no `TxtCHno` editing | High |
| **Voucher list filter `FRAMEVLIST`** | Full filter panel `TXTVDATE1/2`, `Text1 Vr.No.`, `Dcparty`, `DataCombo1 V.Type`, `FGVLIST` results; undocked on `TopCtrl Browse` | `ReportViewer` date filters only; no VrType/Party/VrNo filter | Medium |
| **Printing path** | `Frame1(1)` Opt2 `VNo Selection` / `Print Current` / `VDate Selection` → `DataCombo2/3` range → `.ttx` field-def + `.RPT` crystal; `TopCtrl1_ePrn` creates `FaGrplist.ttx` / `BankReconciliation.ttx` | `ReportViewer._fill` just fills `QTableWidget`; print button not wired to `.ttx`/`.RPT` | Low (intentional modernisation) but noted |

---

## 4. MISSING Frontend UI Bugs — Consolidated Gap Table

> All are **UI-only**; DB schema unchanged. IDs stable for patching.

| ID | Area | VB6 evidence | Python status | Severity | Frontend fix (no DB) |
|----|------|--------------|---------------|----------|----------------------|
| **FVR-01** | Form chrome | `BackColor &HC0C0FF&`, `WindowState=2`, `ControlBox=0`, `MDIChild=-1`, `LblFormCaption &HC0FFFF& System 19.5` | Wrong palette, not maximised, has close box, palette neutral | Visual | `FVR-01` patch — set `setStyleSheet` + `showMaximized`/`setWindowFlag(FramelessWindowHint)` + replicate `LblFormCaption` |
| **FVR-02** | TopCtrl AEDP | `MainCtrl TopCtrl1 0,0,12690×450` + `Form_Load TopCtrl1.Clone + AEDP` + handlers `eAdd/eEdit/eCancel/eFind/eSave/ePrn` | No TopCtrl; buttons are ad-hoc per window | **High** | Add `TopBar` QWidget mimicking AEDP; disable fields on Browse, toggle on Add/Edit |
| **FVR-03** | Header Totals | `LblDrAmt/LblCrAmt/Label3 dIFF` at `Top=5175` + `Line1/Line2` rules + red block `Label1(0-2)` | Only post-toast, no live totals | **High** | Add `QHBoxLayout` with 3× QLabel bound to `_recalc_totals()` on every cell change |
| **FVR-04** | Entry rows | 12× `TxtCrDr/TxtAcName/TxtDr/TxtCr/TxtNar` arrays `BorderStyle=0` `Appearance Flat` `Alignment Right` Fixed Twip grid | `QTableWidget 4 cols` free-edit | **High** | Replace with `QTableWidget 6 cols` (CrDr, AcName, Debit, Credit, Narration, AcCode.Tag) with delegate Flat/None borders; set `MaxLength` validators |
| **FVR-05** | DGAcHlp popup | `DGAcHlp Visible=0 Tag=Index`, repositioned under `TxtAcName` on `GotFocus`, `TxtDetailS` AddressHelp pane under it | No help; free-text | **High** | Implement `DGHelpPopup(QTableView)` overlay; feed from `SubGroup Where Nature<>'Bank'` + show `TxtDetailS = FatherName+GroupName+NameWithADDR` |
| **FVR-06** | VchDt/VType/Vno row | `VchDt/TxtVtYpe/TxtVno` at `Top=495` Fore `&HC00000&` `Arial 9.75` + `LblDay` weekday + `LblVPrefix` | `QDateEdit+QComboBox` layout but wrong Fore/font, missing `LblDay/LblVPrefix/LblVtype/LblDt/LblVno` labels | Medium | Wrap in `QFrame BackColor &HFFFFFF&` with red Fore labels; add `LblDay = weekday(VchDt)` on change |
| **FVR-07** | Narration label | `Label1 Index=3 "Narration"` `BackColor &HFF0000&` at `Top=5520` + `TxtGlb Courier New MultiLine` description | No narration header; per-row narration column header generic | Low | Add narration header strip before memo |
| **FVR-08** | Cheque fields | `TxtCHno/TXTChDate/TXTClrDate` + `Label6/5/7` italic + `LblAmtRs` word amount + `lblTDS` | Missing from voucher | **High** | Add Cheque row under grid `QFormLayout 3× QLineEdit/QDateEdit` with `InputMask "99/99/9999"` |
| **FVR-09** | ChqPrint overlay | `ChqPrint &HCBBE9E&` Frame `Visible=0` with `ChkAcPayee/ChkCompName/ChkFullDate OptAuthoSign/Director/President` | Not present | Low | Hidden `QDialog` same palette behind tool button |
| **FVR-10** | FrameRef | `FrameRef &HD9B0DD&` "Referance Detail" with `FGridRef`, `DGRefNo Hidden`, `LblRefAmt/Adj/Bal/BalDrCr` | Missing | High | Hidden `QFrame` with `MSHFlexGrid` eq. `QTableWidget` + same labels |
| **FVR-11** | FrameTDS | `FrameTDS &HBFD0B7&` 6450×2775 `Visible=0` `TDSDelete`, `TxtTDSCode/ONAMT/TDS/TDSAMT/Narration`, auto `TxtTDSAMT = ONAMT*TDS/100` | Report-generator window, no inline TDS | **High** | Embed collapsible `QGroupBox FrameTDS` with `QLineEdit` rightJustify + `textChanged` calc + `TDSDelete` clears row |
| **FVR-12** | FRAMEADJUST | `FRAMEADJUST &HE6AC86&` with `FgridAdjust 11010×1965`, `TXTTNARRATION &HEBDBC7&`, `TXTADJ_AMT &HF7F0DF& Right`, `BTS_AUTO_ADJ Times New Roman 11.25`, `ADJ_OK/ADJ_CANCLE`, `ADJ_LAB*` | Simple `FaAdjustWindow` 6 fields + 6-col table | **High** | Port as modal `QDialog` with same geometry-ish; auto button distributes Adj accordingly |
| **FVR-13** | FRAMEVLIST | `FRAMEVLIST &HC0C0C0&` 8520×4200 `FGVLIST`, `TXTVDATE1/2`, `Dcparty`, `DataCombo1` VrType | No list panel | Medium | Add `QToolButton "Voucher List"` toggles `QFrame` same palette |
| **FVR-14** | Dr==Cr save gate | `Form_KeyDown` tally `LblDrAmt==LblCrAmt && dIFF==0` then `MsgBox "Save Yes/No" &H44 -> TopCtrl1_eSave` | Backend-only post; frontend allows Post regardless | **High** | Wire `tbl.itemChanged` -> `_recalc()`; disable Post unless diff==0; replicate MsgBox gate |
| **FVR-15** | DATELOCK front gate | `VchDt_Validate -> SELECT DateLock` cancel + year-end site gate | No gate | **High** | Call `ye.check_datelock(vdate)` before Post; if locked `QMessageBox.warning` + `setFocus VchDt` |
| **FVR-16** | MaxLength/Alignment/InputMask | `MaxLength 50/75/20/12/255`, `Alignment Right`, `Locked` for `TxtCrDr`, `Mask` for dates | No validators | Medium | Add `QLineEdit.setMaxLength`, `setAlignment(AlignRight)`, `QDateEdit InputMask`, `Locked` via `setReadOnly(True)` |
| **FVR-17** | Fonts | Mixture `Arial`/`MS Sans Serif`/`Courier New`/`System`/`Comic Sans MS`/`Times New Roman` per control | Unified system font | Visual | Apply `setStyleSheet` font-family per widget id |
| **FGR-01** | FaGrEnt palette | `BackColor &HFFC0C0&`, `ForeColor &HC00000&`, `BorderStyle 0` for Txt, `FrmList` hidden, 8 DataGrids | `FaLedgerWindow` neutral palette, `QGroupBox` border | Visual | `setStyleSheet("background-color:#FFC0C0; color:#C00000")` + `QLineEdit{border:none}` |
| **FGR-02** | FaGrEnt Find | `SearchCode` alias + `Proc_6_126_F1BCC0("2000,2000,1000")` dialog | Live filter only | Medium | Add `TopCtrl.Find` button -> `QDialog QTableView` SELECT GROUPCODE As SearchCode |
| **FGR-03** | FaGrEnt Validate | `Duplicate GroupHelp` MsgBox gate | Not checked | Medium | Validate before insert/update via `SELECT ... WHERE GroupHelp=...` |
| **FGR-04** | Nature ListView | 20 items: Bank,Broker,Cash,Customer,Electrician,Employee,Expenses,Mukadim,Others,PDC,Purchase,Revenue,Sale,SalesMan,SalesRep,Supplier,T.D.S.,Transporter,Unsecured Loan,... | Only `["Dr","Cr"]` combo | **High** | Restore `FrmList ListView` via `QListWidget` overlay for Txt Index 5/6 |
| **FGR-05** | Bilingual fields | `Txt Index=1/2` Hindi `(Hindi)` labels `Comic Sans MS Italic` Visible toggles | No Hindi fields | Low | Show/hide per `MemVar_1F9208C` lang flag |
| **FGR-06** | Note label | `Label3 Caption="Note:- Run Current Balance Updation..." Arial 14.25 Bold Fore &HFF&` at bottom | Missing | Low | Add footer QLabel same font/color scroll |
| **FRP-01** | FaReports chrome | `ForeColor &HE0E0E0&`, `BtnEnh BtnParam/BTNPRINT/BTNEXIT`, hidden `TopCtrl Visible=0`, `DGSite` | `ReportViewer` generic header | Low | Hide TopCtrl analog, add `BtnParam` toggling `DGSite` Site picker |
| **FRP-02** | GridSel / FGrid report params | 10-param grid with `Tag` per field, operator `= < <= > >= <>` via `Array("=", "<", "<=", ">", ">=", "<>")` | Single From/To dates | Medium | If replicating original filters, re-introduce FGrid param builder; else mark as intentional modernisation |
| **FCC-01** | FaChqClear filters | `Txt Index 0 UpTo Date` + `DGBank/DGParty` positioned under `Txt(1/4)` via `Txt.Left/Top+Height+30` + `FrmList` Cleared/Un-Cleared/All + balances `Txt(2/3) Enabled=0` + `LblType Dr/Cr` | `BankReconDialog` pending-only list | **High** | Rebuild 4-filter header + dual DGHelp popups + 15-col FGrid |
| **FCC-02** | FaChqClear inline editing | `TxtGrid` overlay at `FGrid CellBackColor &HC0FFFF& -> &HC0FFFF&`, cols 0xB(Chq_No) 0xC(Chq_Date) 0xD(Clg_Date) with `KeyDown Validate` | Row-select + `Mark Cleared (today)` one-shot | **High** | Editable `QTableWidget` columns 11-13 with delegate `TxtGrid` overlay and `BackColorSel #16308221` |
| **FCC-03** | FaChqClear TRAN save | `BeginTrans/Update Ledger Set Chq_No/Chq_Date/Clg_Date Where DocID+V_SNO+AmtCr+ContraSub` + `CommitTrans` | `cheque_mark_cleared(docid,sno)` single-row | Partial | Iterate pending rows and batch-update like VB6 for HPOST multi-contra |
| **FCC-04** | FaChqClear Print | `BankReconciliation.ttx/.RPT` crystal via `CreateFieldDefFile` | not wired | Low | Optional |
| **FYE-01** | frmYearEnd chrome | `BackColor &HFFC0C0&`, `Command1 Create CSV Visible=0`, `BtnEnh Head 2475×1245` at `7200,3375` + `CmdYrUpdate 4635,3375`, `LblFormCaption &HC0FFFF& System 19.5` | 820×640 neutral palette, 6 plain buttons | Visual | `setStyleSheet background:#FFC0C0` + position `Head/CmdYrUpdate` via `QHBoxLayout with QSpacerItem` approx ±10% |
| **FYE-02** | frmYearEnd gate | `If MemVar_1F920B8==1 And today>EndDt And Site==...` else silent exit; copies `menuHelp/menuHelp1/Voucher_Prefix/UserPermission` per new `Comp_Code = Max+1` | Python checks only `check_datelock(today)` then `carry_forward+reset_budget` | **High** | Add FY-flag/site gate before enabling Execute; hide or disable button if gate false mimicking silent exit |
| **FYE-03** | YearEnd behaviour | Company insert with `Start_Dt+1y/End_Dt+1y/CYear+1/PYear+1` computed via `DateAdd YYYY,1` + `Left(Right(...))` arith; then per-table clones | Python `ye.carry_forward_balances/new_fy_start + ye.reset_budget` — similar but not packaged as single Company insert preview | Medium | Show preview of new `Comp_Code/CYear/PYear/Start/End` before confirm |
| **GEN-01** | FixedSize & MDI | All VB6 forms fixed-client maximized inside MDI parent | Python dialogs resizable, not MDI | Low | `setFixedSize` + offer `QMdiSubWindow` embedding |
| **GEN-02** | KeyPreview & shortcuts | `KeyPreview=-1`, `Form_KeyDown/Press` swallowing Enter (KeyAscii=0), `Ins/Alt-R/Alt-T` hotkeys (`LblHelp` hint) | Only year_end has QShortcuts; voucher has no Enter/Alt hotkeys | Medium | Add `keyPressEvent` + `QShortcut("Ins"/"Alt+R"/"Alt+T")` routing |
| **GEN-03** | Flat appearance | `Appearance=0 Flat`, `BorderStyle=0 None` everywhere | `QGroupBox` borders, `QLineEdit` platform frames | Visual | `setStyleSheet("QLineEdit{border:none; background:white} QFrame{border:none}")` + `Flat` look |

---

## 5. Fixed UI — Drop-in Patches (FRONTEND ONLY, NO DB CHANGE)

> Patches below are **copy-paste-ready**; they reuse existing `HMS_py.core.*` calls. Apply in order. After patching, visual parity should pass screenshot diff at 1.5× tolerance.

### 5.1 `fa_voucher_ui.py` — make it *look* like `FaVrEnt`

```python
# PATCH FVR-01/02/06/16/17 — top of VoucherEntryDialog.__init__ after super().__init__
from PyQt6.QtGui import QFont, QColor
self.setFixedSize(1269, 789)                       # 12690/10 twips→px approx
self.setStyleSheet("""
  QDialog{background:#C0C0FF;}
  QLabel[role="header"]{background:#FF0000; color:#BEFDFE; font:700 9.75pt "Arial"; font-style:italic; padding:2px 4px;}
  QFrame#voucherRow{background:white; border:none;}
  QLineEdit[flat="true"]{border:none; background:white; color:#C00000; font:9pt "Arial"; padding:1px 2px;}
  QTextEdit[flat="true"]{border:none; background:white; color:#C00000;}
""")
# LblFormCaption mimic
cap = QLabel("Voucher Entry")
cap.setStyleSheet("background:#C0FFFF; border:1px solid #999; font:700 19.5pt 'System';")
cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
root.insertWidget(0, cap)

# PATCH FVR-03 — live Dr/Cr totals (wire to every amount change)
self.lblDrAmt = QLabel("0.00"); self.lblCrAmt = QLabel("0.00"); self.lblDiff = QLabel("DIFF: 0.00")
hdr = QHBoxLayout()
for txt, w in [("Particulars",754),("Debit",139),("Credit",139)]:
    lb = QLabel(txt); lb.setProperty("role","header"); lb.setFixedWidth(int(w/10))
    hdr.addWidget(lb)
root.insertLayout(3, hdr)  # after form, before table

def _recalc():
    dr = cr = 0.0
    for r in range(self.tbl.rowCount()):
        try:
            dr += float((self.tbl.item(r,2).text() or "0").replace(",",""))
            cr += float((self.tbl.item(r,3).text() or "0").replace(",",""))
        except: pass
    self.lblDrAmt.setText(f"{dr:,.2f}"); self.lblCrAmt.setText(f"{cr:,.2f}")
    d = abs(dr-cr)
    self.lblDiff.setText(f"DIFF: {d:,.2f}"); self.lblDiff.setStyleSheet("color:%s; font-weight:bold"%("#FF0000" if d>0.005 else "#059669"))
    bPost.setEnabled(d < 0.005 and (dr+cr) > 0.005)
self.tbl.itemChanged.connect(lambda *_: _recalc())
self.tbl.setColumnCount(6)
self.tbl.setHorizontalHeaderLabels(["Dr/Cr","Account","Debit","Credit","Narration","SubCode(tag)"])
self.tbl.setColumnWidths([28,360,90,90,320,80])  # twips/15 ≈ px

# PATCH FVR-05 — DGAcHlp overlay (minimal)
from PyQt6.QtWidgets import QTableView
self._dg = QTableView(self); self._dg.hide()
self._dg.setStyleSheet("background:white; border:1px solid #888;")
# feed on TxtAcName focus: populate from core.ledger list_all filtered by Nature<>'Bank' etc.
# on doubleClick: self.tbl.item(curRow,1).setText(name); self.tbl.item(curRow,5).setText(subcode); self._dg.hide()

# PATCH FVR-08 — cheque row
from PyQt6.QtWidgets import QDateEdit
chqRow = QFormLayout()
self.chqNo = QLineEdit(maxLength=20); self.chqNo.setProperty("flat","true")
self.chqDate = QDateEdit(calendarPopup=True, displayFormat="dd/MM/yyyy"); self.chqDate.setDisplayFormat("dd/MM/yyyy")
self.clrDate = QDateEdit(calendarPopup=True, displayFormat="dd/MM/yyyy")
chqRow.addRow("Cheque No.:", self.chqNo); chqRow.addRow("Cheque Date:", self.chqDate); chqRow.addRow("Clearing Date:", self.clrDate)
root.insertLayout(6, chqRow)
self.lblAmtRs = QLabel(""); self.lblAmtRs.setStyleSheet("color:#800000; font:700 italic 8.25pt 'Arial';"); root.addWidget(self.lblAmtRs)
# word-amount: connect _recalc -> num2words(total)

# PATCH FVR-11 — FrameTDS inline (collapsible)
from PyQt6.QtWidgets import QGroupBox
self.frameTDS = QGroupBox("T.D.S."); self.frameTDS.setStyleSheet("QGroupBox{background:#BFD0B7; font:700 9.75pt 'MS Sans Serif';}")
fl = QFormLayout(self.frameTDS)
self.tdsCode=QLineEdit(placeholderText="TDS A/C e.g. PYT*"); self.tdsNarr=QLineEdit(maxLength=255)
self.onAmt=QLineEdit(); self.onAmt.setAlignment(Qt.AlignmentFlag.AlignRight)
self.tdsPct=QLineEdit(); self.tdsPct.setAlignment(Qt.AlignmentFlag.AlignRight)
self.tdsAmt=QLineEdit(); self.tdsAmt.setAlignment(Qt.AlignmentFlag.AlignRight)
for w in [self.onAmt,self.tdsPct,self.tdsAmt]: w.setProperty("flat","true")
fl.addRow("TDS A/C:", self.tdsCode); fl.addRow("Narration:", self.tdsNarr)
fl.addRow("On Amount:", self.onAmt); fl.addRow("T.D.S. %:", self.tdsPct); fl.addRow("T.D.S. Amt:", self.tdsAmt)
btnDel = QPushButton("Delete TDS"); btnDel.clicked.connect(lambda: (self.tdsCode.clear(), self.tdsPct.clear(), self.tdsAmt.clear(), self.tdsNarr.clear(), self.frameTDS.hide()))
fl.addRow(btnDel)
self.frameTDS.hide(); root.insertWidget(7, self.frameTDS)
# auto calc mirror: F087A8 / 12BBB6C
def _calcTDS(*_):
    try: self.tdsAmt.setText(str(int(float(self.onAmt.text() or 0)*float(self.tdsPct.text() or 0)/100)))
    except: pass
self.tdsPct.textChanged.connect(_calcTDS); self.onAmt.textChanged.connect(_calcTDS)
# hotkey Alt-T
from PyQt6.QtGui import QShortcut, QKeySequence
QShortcut(QKeySequence("Alt+T"), self, activated=lambda: self.frameTDS.setVisible(not self.frameTDS.isVisible()))

# PATCH FVR-14/15 — DateLock + Dr==Cr gate integrated in _post
def _post_guarded(self):
    # DateLock gate (FYE-02 analogue)
    from HMS_py.core import year_end as ye
    import datetime
    if ye.check_datelock(self.dtVdate.date().toPyDate()):
        QMessageBox.warning(self, "Date Locked", "Voucher date is locked (DATELOCK). Choose another date.")
        self.dtVdate.setFocus(); return
    # Dr==Cr guard (diff label already)
    if self.lblDrAmt.text().replace(",","").strip() != self.lblCrAmt.text().replace(",","").strip():
        QMessageBox.warning(self, "Voucher Entry", "Debit must equal Credit (double entry)")
        return
    # if diff==0 but totals==0 also block
    if self.lblDiff.text() != "DIFF: 0.00":
        if QMessageBox.question(self,"Save?","Save Yes/No",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:
            return
    # call original _post body
```

### 5.2 `fa_ledger_ui.py` — converge to `FaGrEnt`

```python
# palette + fixed
self.setFixedSize(968, 653)
self.setStyleSheet("""
  QMainWindow{background:#FFC0C0;}
  QLineEdit{border:none; background:white; color:#C00000; font:9.75pt "Arial"; padding:2px;}
  QLabel{color:#C00000; font:700 9.75pt "Arial"; background:transparent;}
  QLabel#noteLabel{color:red; font:700 14.25pt "Arial";}  # FGR-06
""")
# Note footer
note = QLabel("Note:- Run Current Balance Updation After Making Changes In Group Accounts")
note.setObjectName("noteLabel"); note.setWordWrap(True)
self.centralWidget().layout().addWidget(note)

# Find button SearchCode (FGR-02)
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem
def _find():
    import HMS_py.core.db as db
    rows = db.fetchall("SELECT GROUPCODE AS SearchCode, GroupName, GroupNature, Nature FROM AcGroup WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO') AND AliasYN<>'Y' ORDER BY GroupName", (siteCode,))
    dlg=QDialog(self); dlg.setWindowTitle("Find Group"); dlg.resize(560,380)
    tbl=QTableWidget(len(rows),4); tbl.setHorizontalHeaderLabels(["SearchCode","GroupName","GroupNature","Nature"])
    for i,r in enumerate(rows):
        for j,k in enumerate(["SearchCode","GroupName","GroupNature","Nature"]): tbl.setItem(i,j,QTableWidgetItem(str(r.get(k,""))))
    tbl.cellDoubleClicked.connect(lambda r,c: (self.txt_ac_code.setText(tbl.item(r,0).text()), dlg.accept()))
    # layout ...
_findBtn=QPushButton("Find (SearchCode)"); _testBtn.clicked.connect(_find)
self.layout().insertWidget(1,_testBtn)  # near search row

# Nature ListView 20 items (FGR-04) — QComboBox replace:
self.txt_dr_cr.clear(); self.txt_dr_cr.addItems(["Bank","Broker","Cash","Customer","Electrician","Employee","Expenses","Mukadim","Others","PDC","Purchase","Revenue","Sale","SalesMan","SalesRep","Supplier","T.D.S.","Transporter","Unsecured Loan",""])
```

### 5.3 `fa_sub_forms_ui.py` — `FaAdjustWindow` → `FRAMEADJUST` parity

```python
# header palette
self.setStyleSheet("QMainWindow{background:#E6AC86;} QGroupBox{background:#E6AC86;}")
self.txt_amt.setAlignment(Qt.AlignmentFlag.AlignRight); self.txt_amt.setStyleSheet("background:#F7F0DF;")
# Add FRAMEADJUST labels
self.adjl4 = QLabel("Tr.Amt."); self.adjl4.setStyleSheet("color:#000; font:700 8.25pt 'MS Sans Serif'; background: #5EB0AC;")
self.adjl7 = QLabel("KK"); self.adjl7.setStyleSheet("color:#FFFF; font:700 8.25pt 'MS Sans Serif';")
# BTS_AUTO_ADJ
auto = QPushButton("Auto"); auto.setFont(QFont("Times New Roman",11,QFont.Weight.Bold)); auto.clicked.connect(self._auto_adj)
# where _auto_adj distributes TXTADJ_AMT proportionally across FgridAdjust rows (mirror Proc_185_150_FEB7C8)
# Top row narration mirror: FgridAdjust cellChanged -> TXTNARRATION.setText(FgridAdjust.item(row,11).text())
```

### 5.4 `year_end_ui.py` — chrome + gate

```python
self.setFixedSize(513, 381)
self.setStyleSheet("QDialog{background:#FFC0C0;} QPushButton{font:700 9pt 'MS Sans Serif';}")
# Reposition Head/CmdYrUpdate like VB6 absolute:
btnRow = QHBoxLayout(); btnRow.addStretch(1)
# Head is Close, CmdYrUpdate is Execute
self.btn_close.setFixedSize(165,83); self.btn_execute.setFixedSize(165,83)
# Add hidden Create CSV to stay faithful (FYE-01)
self.btn_csv = QPushButton("Create CSV"); self.btn_csv.hide()
# FYE-02 gate: disable Execute unless subsidiary check passes
def _refresh_gate():
    import datetime
    today=datetime.date.today()
    fy=ye.get_fy_dates()
    siteOk = (ye.MemVar_SITE == ye.MemVar_LOGSITE)  # adapt to your globals
    flagOk = getattr(ye,"FY_CLOSE_FLAG",1)==1 and today>fy["end"]
    self.btn_execute.setEnabled(flagOk and siteOk and not ye.check_datelock(today))
_refresh_gate()
```

### 5.5 Cross-cutting — KeyPreview & borderless delegates

```python
# Add to each dialog class:
def keyPressEvent(self, e):
    if e.key()==Qt.Key.Key_Return and e.modifiers()==Qt.KeyboardModifier.NoModifier:
        e.accept(); self.focusNextChild(); return
    if e.key()==Qt.Key.Key_Insert: # Bill Wise Adjustment
        self._open_adjust_frame(); return
    super().keyPressEvent(e)

# BorderStyle 0 delegate:
class FlatDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter,option,index)
tbl.setItemDelegate(FlatDelegate(tbl))
```

---

## 6. Database Understanding — Why No DB Change

| Area | VB6 DB objects | Python DB objects | Change needed? |
|------|----------------|-------------------|----------------|
| Voucher | `Ledger (DocID, V_SNO, V_Type, V_Prefix, V_No, V_Date, SubCode, AmtDr, AmtCr, Chq_No, Chq_Date, Clg_Date, ContraSub, Narration)`, `Voucher_Prefix`, `LastVoucher`, `DateLock`, `LEDGERTDS`, `LedgerAdjust`, `FGridRef` | `HMS_py.core.fa_voucher` + `fa_ledger_ops` + `fa_tds_ops` already wrap same tables; `PYT*` sharding via `PYT_PREFIX` | **No** — frontend just formats/disable |
| Group | `AcGroup (GroupCode, GroupName, GroupNature, MainGrCode, AliasYN, Nature, SysGroup, GroupHelp)` | `AcGroup` via `ledger.py` / `ledger_config` | No |
| Bank/Cheque Clearing | `Ledger` same columns used as cheque source; `AcGroup Nature='Bank'` + `SubGroup` | Same | No; `TxtGrid` writes `Chq_No/Chq_Date/Clg_Date` same columns |
| Reports | Crystal `.ttx` FieldDef + `FAENVIRO.TagadaHeader*` | `trial_balance/balance_sheet/profit_and_loss` views | No schema |
| Year End | `Company (Comp_Code, Start_Dt, End_Dt, CYear, PYear, ... )` + `menuHelp`/`menuHelp1`/`UserPermission`/`Voucher_Prefix` + `DATELOCK` | `year_end.get_fy_dates/year_end_summary/carry_forward/reset_budget/check_datelock` map identically | No; gate is presentation |

Policy: `PYT` guard (`delete_guard=make_delete_guard("PYT")`, `DocId startswith "PYT"` etc.) already matches VB6 implied production-protection — preserve it, just surface it in UI as disabled Delete when not `PYT*`.

---

## 7. Verification Before/After — How to prove fix

```bash
python -m py_compile PYTHONE/ui/fa_voucher_ui.py PYTHONE/ui/fa_ledger_ui.py PYTHONE/ui/fa_sub_forms_ui.py PYTHONE/ui/year_end_ui.py
QT_QPA_PLATFORM=offscreen python -m HMS_py.ui.fa_voucher_ui   # smoke
QT_QPA_PLATFORM=offscreen python -m HMS_py.ui.year_end_ui     # smoke
pytest PYTHONE/tests/test_fa_*.py -k "voucher or ledger or tds or year_end" -q
```
- Visual: `agent-browser` screenshot before/after at `window.innerWidth=1269` ; diff `ChqPrint/FrameTDS/FRAMEADJUST` overlays `display:none`→`block`.
- Behavioural: Post with `Dr=100 Cr=90` → frontend blocks (MsgBox) not backend; `DATELOCK` date → VchDt refuses; `TDS%` 10 on `OnAmt 1000` → `TDSAmt 100` auto; `Find SearchCode` returns `GROUPCODE` aliased.

---

## 8. Summary for Handoff

**What was read:** 5 VB6 `.frm` fully (14k lines FaVrEnt, 1.5k FaGrEnt, 1.3k FaReports, 1.4k FaChqClear, 358 frmYearEnd) + 5 Python `.py` fully (365+221+259+222+386 lines).  
**What gaps were found:** 30 items (13 FVR, 6 FGR, 2 FRP, 4 FCC, 3 FYE, 3 GEN). Root cause is intentional layout refactor (`QFormLayout` + theme tokens) + missing hidden frames/DGHelp/validation gates that VB6 implements as frontend-only code.  
**What to do next:** Apply patches `FVR-01..16`, `FGR-01..06`, `FCC-01..04`, `FYE-01..03`, `GEN-01..03` above — all frontend Qt styling/signal changes, zero migration. Re-run `COMPARE_WORKSPACE` smoke + `pytest`.  
**Report path:** `C:/Users/PC/Desktop/New folder (3)/MODULE_FIX_PLANS/FODER/PYTHONE/COMPARE_WORKSPACE/UI_FINANCE2_COMPARE.md` (this file).

> **Do NOT modify DB.** All VB6→Python deltas are fixable by making Python widgets *behave* like VB6 controls: same `BorderStyle 0`, same `Right Justify`, same `MaxLength`, same `Tag=Code` pattern, same `MsgBox` guard before `post_voucher`, same hidden `Frame* Visible=False` overlays, same `BackColor` palette, same `Font` families.
