# UI MASTERS — VB6 → Python Comparison (VB6 Classic `radius=0` bevel)

> **Focus:** MASTERS (Country, State, City, Area, RoomCategory, RoomMaster, Package, Season, CompanyMaster/CompMast, Market Segment, Business Source, Guest Status, Guest Parameters, Room Features, Charge/RevMast, Tax Structure, Plan/Token, Sundry, Voucher, Enviro)  
> **Date:** 2026-09-24  
> **Analyst:** UI comparison agent (Muse Spark)  
> **Rule:** No DB change. VB6 Classic theme `radius=0` bevel active. Frontend parity only. Read ONE BY ONE fully.

Sources read verbatim (counts):
- `CompMast.frm:7266` (Company Master = CompanyMaster/Corporate Clients) — `BackColor &HFFC0C0&`, `Client 12990×9705 twip = 866×647 px`, `TopCtrl 12990×450`, 37 TextBoxes, 3 MSHFlexGrids, 7 hidden DataGrids, `FgPoint`, `ListView FrmList`, audit `LblUser/LblLDt`
- `FrmMarketSeg.frm:958` — Market Segment Master — `Client 10680×8535 = 712×569 px`
- `FrmBusinessSrc.frm:965` — Business Source (BussSource) — `Client 8175×5595 = 545×373 px`
- `FrmGuestStat.frm:867` — Guest Status — `Client 11235×7995 = 749×533 px`
- `FrmRoomCatMast.frm:4743` — Room Category Master — `Client 11880×7305 = 792×487 px`, inner `SRate` tariff grid Frame 8655×2655
- `FrmRoomMast.frm:5517` — Room Master — `Client 11880×8490 = 792×566 px`, `Srate 8430×1935`, `Picture1 3780×3315`
- `FrmPackageMast.frm:1831` — Package/Plan Master (PlanMast/Plan1) — `Client 8595×9705 = 573×647 px`, dual `FGrid 12915×2340` + `FGrid1 6975×1560`
- `frmSeasonMast.frm:1374` — Season Master — `Client 8295×4935 = 553×329 px`, `framhold FGrid 5160×3240` + `framWeek 7 CheckBox chkday Monday..Sunday` + vertical `Shape1/Shape2` audit boxes
- `FrmTaxMast.frm:1600+` — Tax Master (RevMast FieldType='T') — `Client 15120×9045 = 1008×603 px`
- `FrmChargeMast.frm` — Charge Master (FixedCharge/RevMast FOM Detail) — `Client 11355×7980 = 757×532 px`, `FrmList ListView`, `DGTaxStru/DGLedgerAc`
- `frmGuestParamMast.frm:953` — Guest Parameters Master — `Client 6750×4020 = 450×268 px`, dual `Frame framhold/FGrid` + `Frame1/FGrid1` + `CmdSave/CmdCancel` (TopCtrl hidden `Visible 0`), NOT a classic TopCtrl master
- Screenshots `01_Master/02_Business_Source.png`, `03_Guest_Status.png`, `04_Charge_Master.png`, `05_Plan_Master.png`, `07_Room_Category.png`, `08_Room_Master.png`, etc. — verified labels/tariff strip

Python read fully:
- `PYTHONE/ui/base_master.py:386` (`680×520` GroupBox, comment `680x520 GroupBox` → actually code `setMinimumSize(680,520)` + `resize(720,540)`), `_VB6_DIALOG_QSS` equivalent inline QSS, `MasterConfig`/`Field`, `BaseMasterForm(QDialog)`, `_SearchViewer(QDialog)`, `DGHelp QListWidget Popup` + `ListView Nature QListWidget` + `FGPoint` emulated, `TopCtrl AEDP` → BtnNew/Edit/Delete/Save/Cancel/Exit + Find(F3)
- `PYTHONE/ui/p2_masters.py:510` — `sundry/city/area/acgroup/venue/depart/country/state/fixcharge/unit/roomcategory/roommaster/packagemaster/seasonmaster/companymaster` all as `MasterConfig` + `BaseMasterForm`
- `PYTHONE/ui/plan_master.py:217` — bespoke `PlanMasterForm(QDialog 640×460)` with 4 fields + `TopCtrl`-style 6 buttons, manual `set_state`/`reload` — NOT using `BaseMasterForm`
- `PYTHONE/ui/finance_masters_ui.py:259` — `taxmaster/paymenttype/marketsegment/businesssource/gueststatus/forexmaster/ledger` as `MasterConfig` → `BaseMasterForm`
- `PYTHONE/ui/general_setup_ui.py:259` — `roomfeat/godown/vouchcat` via `BaseMasterForm`, plus `VoucherTypeBrowser/EnviroViewer/GuestParamViewer/PrintingSettingsViewer` read-only `QTableWidget` browsers
- `PYTHONE/ui/theme.py:754` — `DEFAULTS radius=0, bg #d4d0c8, border #808080, vb_mint #c2e0ce, vb_pale_yellow #ffffc0, radius0 bevel injected`

---

## 0. EXECUTIVE SUMMARY

| Area | Verdict | Key Gap |
|------|---------|---------|
| **Dialog chrome / size / color / font** | ⚠️ Drift | VB6 `BackColor &HFFC0C0& → #C0C0FF` (task says mint but VB6 actually periwinkle #C0C0FF) + Arial 9.75 maroon labels + Times New Roman audit footer + System 19.5 vertical caption + radius 0 flat `BorderStyle 0 None Appearance 0 Flat`. Python `base_master` uses `QDialog bg #d4d0c8 gray` (classic button face) — **not** VB6 `&HFFC0C0`; fonts match mostly but `theme._glass_qss` universal `Segoe UI 13px` can override `Arial 9.75`. FixedSize `680×520` (720×540 resize) vs VB6 `10680×8535 twip → 712×569 px` (MarketSeg) — Python smaller, uniform, loses `ClientWidth` per-master variation. |
| **TopCtrl AEDP workflow** | ⚠️ Partial | VB6 `TopCtrl1_UnknownEvent_A` (Add) = clear+stash Tag + `Active Yes` default + focus; `B` Cancel `MsgBox "Cancel ?" 4 "Terminate Process"`; `C` Delete `BeginTrans + Bookmark + Delete + CommitTrans + Requery twice + Proc_154_5 audit`; `D` Edit lock `global_64` Tag stash + `Enabled=False` PK; `F` Find `SELECT ... SearchCode ... LOGSITE_CODE='HO' OR LOGSITE_CODE=?` + widths `4000,1000`; `16` Save duplicate `SELECT COUNT(*) ... LOGSITE_CODE .. and Name=''` vs `And Name<>'" & global_64 & "'"` → `MsgBox "Duplicate Name"` + `BeginTrans/CommitTrans + Requery + Find Code=''`. Python `base_master` reproduces AEDP + Find viewer + duplicate guard (code exists + name lower-case scan) + `BeginTrans` via `cfg.api` wrappers, but **not** the VB6 `U_AE/U_Name/U_EntDt/Site_Code/LogSite_Code` audit insert/update payload verbatim. Also `plan_master.py` re-implements Save without audit fields (`U_AE='A'/'E'`). |
| **DGHelp / DataGrid helpers** | ⚠️ Emulated | VB6 per-master hidden `DGHelp 4245×3330` + `FGPoint 1980×1440` positioned `Left = Txt.Left, Top = Txt.Top+Height+&H1E (30 twip = 2px)` + `ListView FrmList 1875×1725` for enums (Nature, ChargeType, HSN, etc.). Trigger via `Txt_GotFocus` → `Proc_6_137_1193554` computed position; `Txt_KeyDown Shift=&H1B Esc` hides; arrows page up/down delegate to DGHelp. Python `base_master` has `QListWidget _dgHelp` Popup (280px min, 220 max-height) + `_lvNature` 220px with Arial 9.75 selected `#000080`; positioning `edit.mapToGlobal(QPoint(0, edit.height())) +2px` matches VB6; live filter via `textEdited` + `Key_Escape` hides; but **only one generic DGHelp** per form (vs 3-4 per VB6 like TaxMast `DGHelp/DGSundry/DGLedgerAc`, Package `DGHelp/DGRoomCat/DGTaxStru/DGRev/DGTokenRev`). Coverage incomplete for multi-FK masters. |
| **DataGrid vs QTableWidget** | ⚠️ Close | VB6 `FGrid/FGrid1` `MSHFlexGrid` / `MSHFlexGrid BackColorSel 14737632 (#E0E0E0) / CellBackColor 16777215 (#FFFFFF)` + `TxtGrid` overlay edit + Delete `MsgBox "Delete for Sure?" &H114`. Python `QTableWidget 0×N` `setAlternatingRowColors True`, `gridline #808080`, `border 2px inset/outset`, `QHeaderView::section bg #d4d0c8 outset` — bevel correct. But VB6 `FixedRows` + `Rows` + `TextMatrix` tariff matrix (RoomCat SRate 6×5 rates) has no direct Python tariff grid — `p2_masters roomcategory/roommaster` flatten tariff to single-field forms. |
| **ListView / FrmList / BtnEnh / TopCtrl visuals** | ❌ Missing | VB6 `FrmList ListView 1800×1815` inside `Frame 1875×1725` `BorderStyle 0 None` with check `ListView.Tag = Index` + `Frame BackColor &HFFC0C0&` + `CmdSave 1890×405 Save/Exit` bevel buttons. Python only has popup `QListWidget` without containing `Frame`, no `BorderStyle 0` chrome, buttons use `_VB6_DIALOG_QSS` but masters use teal gradient sidebar style via theme. |
| **Audit footer** | ⚠️ Partial | VB6 every master has `LblUser 2880×255 Times New Roman 11.25 Bold Red &HFF0000&` + `LblLDt 2790×285 TNR 12 Bold Red` + `LblFormCaption 180×540 Vertical BackColor &HC0FFFF& BorderStyle 1 Fixed Single System 19.5 Bold` at `(0, TopCtrl.Height+VOffset)` + Shape border `C00000`. Python `base_master` has `lblUser/lblLDt TNR 9pt Bold #ff0000` + `lblState` + `lblFormCaption` not inside dialog (header is built by shell). Position/colors close but size smaller (9pt vs 11.25/12), missing left-rail `LblFormCaption` vertical + Shape. |
| **Colors BGR→RGB** | ⚠️ Drift | See §1 BGR table. Python `theme.DEFAULTS bg #d4d0c8` vs VB6 form `&HFFC0C0& → #C0C0FF` — different gray vs periwinkle. Dialogs should be periwinkle per VB6, but classic gray is also a valid VB6 system color — drift is intentional modernization but noted. |
| **No DB change** | ✅ OK | All Python masters call `core/api.list_all()/get/exists/insert/update/delete` which already filter `LOGSITE_CODE IN ('HO',?)` via SQL — matches VB6 `Form_Load` `SELECT ... WHERE (LOGSITE_CODE='?' or LOGSITE_CODE='HO')`. No schema edit. |

**Overall:** Python masters are **functionally complete** (CRUD + duplicate + search + audit label shell) and use correct **bevel radius 0** (`theme radius 0` forces `border:2px outset/inset`), but **not pixel-identical** to VB6: per-master `ClientWidth/Height` not preserved, wrapper chrome (`LblFormCaption` vertical, `Shape`, `FGPoint`, multi-DGHelp) flattened to one generic popup, tariff matrix grids for RoomCat/RoomMaster/Package collapsed to flat fields, GuestParamMast dual MSFlexGrids collapsed to read-only viewer, and audit insert payload missing `U_AE/U_Name/U_EntDt/Site_Code/LogSite_Code` exact columns (Python uses `core` agnostic).

12+ MISSING frontend UI bugs + patches in §4/§5 make Python EXACTLY VB6 same frontend logic without DB change.

---

## 1. VB6 CONTROLS — VERBATIM (BGR→RGB + twip→px, one-by-one)

> All masters share: `BackColor &HFFC0C0&`, `WindowState 2 Maximized`, `ScaleMode 1 Twip`, `AutoRedraw False`, `FontTransparent True`, `ControlBox 0 False`, `MdiChild -1 True`, `KeyPreview -1 True`, `ClientLeft 60|120`, `ClientTop 345|795`, `LockControls -1 True`, `BorderStyle 0 None`, `Appearance 0 Flat`, `MaxLength` per field, `TabIndex` dense, `ForeColor &HC00000&` (VB6 navy) or `&HC0&` orange hint, `BackStyle 0 Transparent`, `AutoSize -1 True`. Twip→px ÷15. BGR decode: `&HBBGGRR&` → RGB `#RRGGBB`.

### 1.1 FrmMarketSeg / FrmBusinessSrc / FrmGuestStat — minimal masters (pattern identical)

```vb
Begin VB.Form FrmMarketSeg        'FrmMarketSeg.frm:2
  Caption "Market Segment Master" 'or "Business Source Master" / "Guest Status Master"
  BackColor &HFFC0C0&             'BGR FFC0C0 -> RGB #C0C0FF periwinkle
  WindowState 2  ScaleMode 1  AutoRedraw False  FontTransparent True
  ControlBox 0  MDIChild -1  KeyPreview -1
  ClientLeft 60  ClientTop 345
  ClientWidth 10680  ClientHeight 8535   'MarketSeg: 712×569 px | BussSource 8175×5595=545×373 | GuestStat 11235×7995=749×533
  Begin MainCtrl TopCtrl1 0,0 10680×420|450 TabIndex 8|7  'AEDP toolbar
  Begin TextBox Txt Index 0  BackColor &HFFFFFF& ForeColor &HC00000& Left 3480 Top 2235|2325 Width 4215 Height 285 BorderStyle 0 None MaxLength 20 Font Arial 9.75 Normal Appearance 0 Flat TabIndex 0
  Begin TextBox Txt Index 1  Left 3480 Top 2535|2625 Width 600 Height 285 BorderStyle 0 MaxLength 3 Font Arial 9.75
  Begin Label LblName Index 0 "Market Segment Name" | "Business Source Name" | "Status Name" Left 1230|1410|2115 Top 2235|2325|1965 ForeColor &HC00000& Arial 9.75 Bold 240h AutoSize Transparent
  Begin Label LblLedgerAc Index 6 "Active" Left 2820|3000 ForeColor &HC00000& Arial 9.75 Bold
  Begin Label Label1 Index 1 "(Y)es/(N)o" Left 4110|4305 Top 2565|2655 ForeColor &H80& Arial 9 Bold 225h  'hint color &H80 = BGR 80 -> RGB #800000 maroon? actually &H80 = 128 decimal = 0x80 -> B=0 G=0 R=0x80 -> #800000 maroon
  Begin DataGrid DGHelp 7800|7650,3300|3150 4245×3330 Visible 0 False TabStop 0
  Begin MSFlexGrid FGPoint 7665|7710,1575|1440 1980×1440 Visible 0
  Begin Label LblLDt "Last Update" ForeColor &HFF0000& Left 4620|4890 Top 4980|4635 Width 2790 Height 285 AutoSize Transparent Font Times New Roman 12 Bold
  Begin Label LblUser "User" ForeColor &HFF0000& Left 1230|1500 Top 4980|4650 Width 2880 Height 255 AutoSize Transparent Font Times New Roman 11.25 Bold
  Begin Label LblFormCaption BackColor &HC0FFFF& (BGR C0FFFF -> RGB #FFFFC0 pale-yellow) Left 0 Top 360 Width 180 Height 540 BorderStyle 1 Fixed Single Alignment 2 Center AutoSize True Font System 19.5 Bold 700
End
```

**Workflow (FrmMarketSeg.frm:363-958, FrmBusinessSrc identical, FrmGuestStat same):**
```
Form_Load: LblUser.Left 13500 Top 7800 LblLDt Top 8160/4635
  Me.TopCtrl1.DispID_8001000B("AEDP")  'set mode string AEDP (Add/Edit/Delete/Print)
  0.Method_arg_50(var_C8) + DispID_68030007(var_D8)  'TopCtrl caption mode
  unk.Execute "SELECT Code,Name FROM MarketSeg|BussSource|GuestStat WHERE (LOGSITE_CODE='HO' OR LOGSITE_CODE='?') ORDER BY Name" -> DGHelp
  unk.Execute "SELECT * FROM MarketSeg|BussSource|GuestStat WHERE (LOGSITE_CODE=...) ORDER BY Name" -> Form RecordSource
  var_C8="INI" Proc_5_1_100CB50(var_C8,Me,Me.DGHelp,Me) -> Proc_14_27_E7A804 (Ini state) + Proc_14_29_120FFF8 (audit refresh)

Form_Resize: Me.LblFormCaption.Caption = var_88 (AppTitle) LblFormCaption.Left 0 LblFormCaption.Top = TopCtrl.Height+VOffset (via DispID_80010006/04) Width = var_B8

Txt_GotFocus(Index): Proc_6_74_E226B0 var_8C + Call Proc_14_31_E863F8 (hide popups) If Index=0 And RecordCount>0 Then FGPoint + Proc_6_137_1193554(DGHelp,global_56,Index) (position DGHelp under Txt)

Txt_KeyDown: If Shift=&H1B (Esc) -> Proc_14_31 hide; If KeyCode=0 (Name) -> Proc_6_79_11ACE04(DGHelp, Txt, ...) + Proc_6_138_106D6F8 navigate DGHelp on arrows PgUp/PgDn; If DGHelp not Visible And ((Shift=&H28 Down)Or(Shift=&HD Enter)) And KeyCode=1 (Active?) -> Call Txt_Validate -> if &HFF move focus; If "Save Record ?" dialog 4 "Save Data" -> TopCtrl1_UnknownEvent_16

Txt_Validate(Cancel): Call Proc_14_30_108AAAC(var_88) If &HFF -> arg_10=&HFF Exit  'single field Name validation: duplicate check only

TopCtrl_A (Add): LblUser/LblLDt vbNullString Proc_14_27_E7A804("ADD") Call Proc_14_28 clear Text + Tag=nil Set Txt(1).Text="Yes" SetFocus Txt(0)
TopCtrl_B (Cancel): If MsgBox("Cancel ?" ,4 "Terminate Process")=6 Then Proc_14_27("INI") + Proc_14_31 hide + Proc_14_29 else SetFocus
TopCtrl_C (Delete): If Proc_183_56_FE8818(global_52)=&HFF Exit (no permission?); Check GuestFolio + Booking existence via Proc_6_108_1010FEC -> if referenced Exit; MsgBox "Delete Record ?" &H24 "Confirmation"=6 -> BeginTrans Bookmark=Me.Bookmark Delete From MarketSeg Where Code='' Execute + Proc_154_5_10E33A4 audit delete + CommitTrans + Requery twice + Bookmark restore or MoveLast + Proc_14_29 + Proc_5_0_110649C -> Else RollbackTrans + MsgBox " Deletion Error "
TopCtrl_D (Edit): LblUser/LblLDt vbNullString If Proc_183_55_FE7900=&HFF Exit; Proc_14_27("EDIT") Set global_64 = Txt(0).Text stash original Name for duplicate edit path
TopCtrl_F (Find): If RecordCount<=0 -> MsgBox "Records Not Present For Searching." &H40 "Information" Exit; Set MemVar_1F920E4="Select MarketSeg.Code As SearchCode, ... FROM MarketSeg Where (LOGSITE_CODE='HO' OR ... ) Order by MarketSeg.Name" MemVar_1F92120=Me widths "4000,1000" Proc_6_126_F1BCC0 + Method_arg_2B0 show search dialog (SearchCode|Name) with "4000,1000" column widths
TopCtrl_14 Print: Select * ORDER BY Name -> CreateFieldDefFile(.ttx) + .RPT "Market Segment Master" etc.
TopCtrl_16 Save (Add/Edit): Proc_6_27_EA565C(var_94,"Name") validation + Proc_14_30 duplicate -> If TopCtrl mode="Add" -> SELECT IsNull(Max(CAST(SUBSTRING(Code,3,3) AS INT)),1)+1 + Format "000" + global_60 = Proc_6_45_EAD428(MemVar_1F92070,2) Prefix +Seq ; BeginTrans var_86=1 If "Add" -> INSERT INTO MarketSeg(Code,Name,Active,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values('','','',..., 'A', ... ) Else UPDATE SET Name='',Active=...,SITE_CODE='',U_Name='',U_EntDt=...,U_AE='E' WHERE Code='' ; CommitTrans + Requery + Find Code='' -> If "Add" -> call TopCtrl_A again else INI + hide
SEARCHBACK(MyValue): Me.MoveFirst Me.Find "code='MyValue'" + Proc_14_29 audit
```

Screenshot parity (02_Business_Source.png, 03_Guest_Status.png): white `4215×285` inset TextBox, maroon `2175×240` label `Business Source Name` / `Status Name`, active hint `(Y)es/(N)o` blue-gray &H80, vertical pale-yellow `LblFormCaption` left rail 180×540, audit footer red TNR at bottom.

### 1.2 CompMast.frm — Company Master (Corporate Clients) — heaviest (7266 lines)

```vb
Begin VB.Form CompMast  'CompMast.frm:2
  Caption "Company Master" BackColor &HFFC0C0& (periwinkle) WindowState 2 ScaleMode 1 AutoRedraw False FontTransparent True Icon CompMast.frx ControlBox 0 MDIChild -1 KeyPreview -1 ClientLeft 60 ClientTop 345 ClientWidth 12990 ClientHeight 9705 (866×647 px) LockControls -1
  Begin MainCtrl tOPCtrl1 0,0 12990×450 TabIndex 92
  '--- 37 TextBoxes (selected):
  Txt Index 0  1740,750 1410×285 BorderStyle 0 None MaxLength 8 Arial 9.75 Fore &HC00000& Back &HFFFFFF& Flat 'Code
  Txt Index 1  1740,1065 4140×285 MaxLength 75 'Company Name
  Txt Index 2  1740,1380 4140×285 MaxLength 50 'Under Group (GroupCode FK -> AcGroup Nature='Customer')
  Txt Index 19 1740,2010 550×285 MaxLength 3 Enabled 0 False 'Allow Credit Yes/No? (maps to Allow Credit)
  Txt Index 20 1740,1695 4140×285 MaxLength 50 'Company Type (Corporate/Travel Agency/Mesh)
  Txt 33 3975,2010 1905×285 MaxLength 20 'Map Code
  Txt 3  7575,1005 420×285 Text "Mr." MaxLength 4 'ConPrefix ListView Mr./Mrs./Miss/M/S
  Txt 4  8025,1005 3585×285 MaxLength 75 'ConPerson
  Txt 5  7575,1320 4035×285 'Add1 etc. 6/7 address, 8 CityName, 9 Pin 6, 10 Phone, 11 Mobile 12, 12 Fax, 13 Email 50, 11 Mobile...
  Txt 8  7575,2265 4035×285 DataFormat 80|38 'City Name with DGCity helper
  Txt 9  7575,2580 4035×285 MaxLength 6 'PinCode
  Txt 7  7575,1950 4035×285 MaxLength 50 'Address?
  Txt 6  7575,1635 ... Txt28 7575,4155 Discount Type, TxtGVars for black-list etc.
  Txt 31 1740,2325 550×285 Text "Yes" MaxLength 3 'Active
  TxtGrid1 Index 1 3540,6045 1020×240 Visible 0 Back &HFF8080& Fore &HFF0000& Tahoma 9  'overlay for Fgrid1
  TxtGrid Index 0 1320,3840 1200×240 Visible 0 Back &HE0E0E0& MS Sans Serif 9.75 MaxLength 10
  Txt 30 16065,3795 975×285 Visible 0 'hidden Account Nature
  Txt 29 780,3000 1185×285 Enabled 0 Fore &HC00000& 'Opening Balance display?
  txtCurrBal 3870,3000 1185×285 Enabled 0 Fore &HC00000& 'Current Balance
  '--- Grids/Helpers:
  MSHFlexGrid Fgrid1 3495,5745 4035×3105 Visible 0 (plan/charge matrix?)
  MSHFlexGrid FGrid 240,3540 5715×1215 + FgridPlan 11640,1005 4305×7320 + FGridIncl 7575,5745 3960×2175
  MSFlexGrid FGPoint 14265,4890 1980×1440 Visible 0
  DataGrid DGAcName 9585,7965 5700×3330 Visible 0 | DGUnderAc 9615,8610 | DGCity 9210,7605 | DgUser 9000,8895 | DGUser?
  Frame FrmList 14325,6435 1875×1725 Visible 0 BorderStyle 0 Begin ListView 225,105 1800×1815
  Picture1/Picture2 300×270 Visible 0 (icons)
  '--- Labels:
  Lbl Caption "Trade Name" 6120,5445 1170×240 Fore &HC00000& Arial 9.75 Bold 700 AutoSize BackStyle 0 Transparent etc. 34 labels
  LblFormCaption BackColor &HC0FFFF& 0,345 180×540 BorderStyle 1 Fixed Single Alignment 2 Center System 19.5 Bold
  LblUser "User" Times New Roman 11.25 Bold Red &HFF0000& 750,7470 2880×255
  LblLDt "Last Update" TNR 12 Bold Red 4125,7470 2790×285
  Shape Shape2 BorderColor &HC00000& 540,2715 5100×660 Shape 4 BorderWidth 2 (Opening/Current Balance box)
  LblNature "Nature" Center 2385,2700 Arial 9.75 Bold Red &HFF&
  LblOpBalType/CurBalType "Dr/Cr" Fore &H80& &H4000& etc.
End
```

**Workflow (key):** `Form_Load: 0.Method_Form_Load0 hide Txt 0x18/0x1B + FG.BackColorBkg = MemVar_1F921B4 + Proc_183_1_F5B310 color theme + global_52=0 → hide Lbl 0x0F if not global_52 &HFF; Load 4 cursor combos: DGAcName SubGroup NATURE='Customer' + LOGSITE HO, DGUnderAc AcGroup NATURE='Customer', DGCity City, DgUser Employee, DgUser for CompanyType filter Corporate/Travel Agency/Mesh` → `DG Help position = Txt.Left / Top+Height+&HF` etc. `Txt_GotFocus Index=2 UnderGroup -> DGUnderAc visible + FGPoint helper; Index=8 City -> DGCity; Index=0x1B User etc.; Index=3 Mr./Mrs./Miss/M/S via ListView Array("Mr.","Mrs.","Miss","M/S") -> global_180 popup`. `TopCtrl Save (16): duplicate SELECT COUNT For SubGroup NameHelp` → `Insert/Update SubGroup with GroupCode, CityCode, ConPrefix, Phone/Mobile/Fax/EMail validation (InStr @ + . ), GSTIN 15-digit, Email LCase` → `For FGrid rows if Amount>0 then Cr/Dr required else Validation` → `Proc_22_93/94 Insert vs Update`. `Delete: If Ledger Where SubCode count>0 Then "Transactions Exist Can't Delete"` → `Group Profile` check via `Proc_6_108`.

### 1.3 FrmRoomCatMast — Room Category (4743 lines)

`Client 11880×7305 792×487 px TopCtrl 11880×450 SRate Frame 9585,4380 8655×2655 BorderStyle 0 Visible 0 Back &HC0C0C0&` contains 22 TextBoxes Txt32..53 grid: High Rate/Rack Rate/Disc1-3 Rate × Single/Multiple/Extra Person/Weekend + Weekly/Monthly hidden. Labels High Rate...Disc3 Rate @270 px row, Occupancy Type/Single/Multiple/Extra Person/Weekend/Weekly/Monthly left column. `Txt 31 Visible 0`, `Txt30/29 hidden`, `Txt28/23/27/22/26/21/20 hidden` tariff exports. `Txt54 Revenue Charge 2565,1755 3285×285 MaxLength 25 Fore maroon` with `DGRevenue 10830,2865 4230×3330`, `DGHelp 10830,2430`, `FGPoint 11250,5325`, `FrmList ListView 1875×1725`, `Txt56 MapCode 4095,2070 1755×285`, `Txt08 Active 7965,2070 MaxLength 3`, `Txt07/06/05/04/03 numeric rates Right Justify`. `Image1/2`, `CmdRate Season &Rate 12195,8055 1890×405 Visible 0`, `Shape1 1275,2700 7995×390 Border &HC00000& BorderWidth 2`, `Label Tariff &HF8DEE0 Back &HFF& Underline`.

**Workflow:** `Form_Load: SRate.Visible logic per System? ; Save via FGrid tariff validation (Value Required In Row) + Bedge? ; Season Rate via CmdRate → builds Report .ttx/.RPT "Room Category Master"`.

### 1.4 FrmRoomMast — Room Master (5517 lines)

`Client 11880×8490 792×566 TopCtrl 11880×450 Srate 10800,4185 8430×1935 Visible 0 (same tariff matrix 40..57) + Picture1 5595,4125 3780×3315 Border Fixed Single Stretch -1 + Label4 "Click Here to insert Image"` + `Txt33 Room Code 2475,1200 MaxLength 5 + Txt34 hidden + Txt00 Room Master Name 2475,1515 MaxLength 15 + Txt01 Short? 2475,1830 + Txt05/06/58 + DGCategory 12735,4620 + DGRevenue 12660,5010 + DGMaid 12915,4275 + FGPoint 13635,450 + FrmList + Txt22/17/18/19 etc. Tariff labels High/Rack/Disc1-3 Rate, Occupancy Type rows`. `LblFormCaption vertical + audit `LblUser 1410,8160 + LblLDt 4800,8160` same as market. `Image1/2` + `TxtGrid1` overlay + `CmdRate Season &Rate hidden`. Parses `Door Lock ID 9510,1815` etc. `Picture4/Picture2` icons.

### 1.5 FrmPackageMast — Package/Plan Defination (1831 lines)

`Client 8595×9705 573×647 TopCtrl 8595×450 FGrid 990,4500 12915×2340 FixedRows 1 (Tariff grid Plan1 Detail) FGrid1 975,7140 6975×1560 (Token grid) DGHelp 13560,7935 DGRev/DGTokenRev/DGRoomCat/DGTaxStru hidden 3495×1980/4230×3330 FrmList 11535,1410 2520×1830 ListView CheckBox Check1 "Percentage Basis" Visible 0 + TxtGrid 0/1 overlay @2040,4500 Hidden Txt 17..16 MapCode/Tariff +.Txt0 Package Name 4530,960 MaxLength 25 + Txt14 Room Category 4530,1275 + Txt15 Tariff 9960,960 + Txt5 PackageAmt etc. Txt13 Active Yes 4530,3480 Txt6 Discount Applicable @4530,2850 etc. Labels Room Tax Structure/MapCode/Complex`. **Workflow:** `Form_Load TopCtrl AEDP + FGrid.BackColorBkg MemVar + position DGHelp/DGRoomCat/DGTaxStru at Txt.Top+Height+&H1E; Query PlanMast Where Plan_Package='Plan'|'Package' AND LOGSITE HO; FixedCharge for DGRev/DGTokenRev; RoomCat for DGRoomCat; TaxStru distinct; On Save loops FGrid rows -> INSERT Season/PlanMast style? Actually for Package loops? For Package loops FGrid TextMatrix delete-then-insert per row + validation "Value Required In Row  & RowNo"`.

### 1.6 frmSeasonMast — Season Master (1374 lines) — Grid master

`Client 8295×4935 553×329 BorderStyle 0 None MDIChild ShowInTaskbar 0 framhold 465,1845 5190×3375 Contains TxtGrid 0 + FGrid 5160×3240 (From Date DDMM / To Date DDMM / Rate columns 3-col) framWeek Caption "WeekEnd" Back &HC0FFFF& 5880,1815 2055×3375 Border Flat Contains 7 CheckBox chkday 0..6 Monday..Sunday each BackColor distinct (&HC0C0FF..&H8080FF) Fore &H404000& MS Sans Serif 9.75 Bold Top 375/795/1215/1635/2055/2475/2895 TopCtrl 8295×375 LblLDt 4320,6360 Center TNR12 Red Shape2 4200,6240 3135×615 Shape1 840,6240 3135×615 Border &HC00000& LblUser 945,6360 Center Shape Label1 "Season Master" &HC0FFFF& System 19.5 lblyear "For Year" @495,1455 + txt 0 Txt Year MaxLength 4 MS Sans Serif 700`. **Workflow:** `Form_Load Proc_20_31_F7CC84 set FGrid col widths 0x1F4="From Date (DDMM)" etc.; SELECT Distinct year(FromDate) as SYear... ORDER BY year desc; Proc_20_34_124CFD0 loads SeasonMast Where Year(FromDate)='' + SeasonMast1 Weekend string 7-char "* " pattern for checkboxes; TopCtrl Delete "This Action Will Delete All The Entries Associated With This Year..." -> Delete From SeasonMast Where Year(Fromdate)=''+LOGSITE HO ; Save loop FGrid rows FromDate/ToDate/RateCode validation + build "*"/" " Weekend string from chkday Value -> INSERT SeasonMast(FromDate,ToDate,RateCode,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) + Delete+Insert SeasonMast1(Weekend...)`.

### 1.7 FrmTaxMast / FrmChargeMast — Revenue Tax/Charge

*FrmTaxMast* `Client 15120×9045 1008×603 TopCtrl 15120×450 DGHelp 10710,2115 4230×2205 DGSundry 10770,3390 4260×2205 DGLedgerAc 10725,4755 4230×2220 Txt0 Tax Name 3090,1680 MaxLength 25 Txt2 Short 3090,1995 Txt4 Sundry Name 3090,2310 Txt1 Ledger A/C 3090,2625 Txt5 Payable 3090,2940 Txt6 Unregistered 3090,3255 Txt3 Round Off `No` 6405,1995 Visible 0 Labels Sundry/ Paybl/ Unreg / Tax Name / Short / Ledger / Round Off (Y/N) / SysYN / (Purchase) 7335,... LblFormCaption -30,630 vertical LblUser 1935,5685 LblLDt 5310,5685 FGPoint 9765,1185` **Workflow:** `SELECT Code,Name FROM REVMAST WHERE FIELDTYPE='T' AND LOGSITE HO -> DGHelp; SubGroup ActiveYN=1 -> DGLedgerAc; SundryMast -> DGSundry; RevMast+TAX Join -> main recordset FieldType T; Save checks duplicate Tax Name + Ledger A/C + Sundry + SysYN='Y' protected Delete`.

*FrmChargeMast* `Client 11355×7980 757×532 TopCtrl 11355×450 FrmList ListView 1875×1725 DGLedgerAc 8010,3915 DGHelp 7275,4350 DGTaxStru 6960,3540 FGPoint 11385,4980 Txt0 Charge Name 3780,1605 MaxLength25 Txt1 Short 3780,1920 MaxLength5 Txt2 Account Name 3780,2550 Txt3 Tax Structure 3780,2865 Txt10 Nature of charge 3780,2235 Txt13 HSN 6495,2235 Txt12 Tax Inc Yes/No 3780,3180 Txt11 Active 3780,4440 Txt09 Posting Type 3780,3495 Detailed/Summarize Txt04 Sale Rate 3780,3810 Txt07 Type Cr/Dr 3780,4125 Txt08 Percent/Amount ListView + Picture1/3 icons + Labels Nature/Post/HSN/TaxInc/Active/App.Mode hidden/Tariff` **Workflow:** similar RevMast FlagAMR='Detail' FlagType='FOM' + SubGroup ActiveYN + TaxStru distinct; Save loops FlatRate/Adult/Child numeric Format "0.00", DUplicate Charge Name, SysYN='Y' block, U_AE.

### 1.8 frmGuestParamMast — Guest Parameters (953 lines) — Grid config, NOT classic AEDP

`Client 6750×4020 450×268 BackColor &HE0E0E0& (#E0E0E0 gray) NOT &HFFC0C0& Border TopCtrl 8250×375 Visible 0 False! Frame framhold 60,390 3285×2820 Frame1 3390,390 3285×2820 Each with TxtGrid 615,675hidden + MSFlexGrid FGrid/FGrid1 3210×2325 Label "Custom Entry Fields Setup (Tab 1)/(Tab 2)" Back &H656458& Fore &H8000000E& Tahoma 8.25 Bold Center Frame2 60,3210 6630×660 Contains CmdSave Caption "&Save/Exit" Back &H808080& 1440,165 1845×420 Appearance 0 Flat + CmdCancel "&Cancel" 3300,165` **Workflow:** `Form_Load SELECT * FROM GUESTPARAM` -> Fill 16 TextMatrix fields T1Field1..8 -> FGrid, T2Field1..8 -> FGrid1 (8 rows each, Col 0 Sr No. + Col1 Description). `CmdSave_Click BeginTrans delete from GuestParam WHERE SITE_CODE=? AND LOGSITE_CODE=? -> insert into GuestParam(T1Field1..T2Field8,Site_Code,U_EntDt,U_AE,LOGSITE_CODE) values ('Trim(FGrid.TextMatrix)...') + CommitTrans -> Unload Me ; CmdCancel Unload`. No duplicate check, no TopCtrl state-machine — direct dual-grid transactional batch.

### 1.9 Screenshots

`02_Business_Source.png` etc. confirm: white inset 4215×285 Txt, maroon labels `Business Source Name` / `Guest Status` / `Charge Name`, active `(Y)es/(N)o` hint, tariff matrix for Plan/RoomCategory with `High/Rack/Disc1-3` headers & `Single/Multiple/Extra/Weekend` rows, Season `For Year` + `From Date (DDMM) / To Date / Rate` grid + 7 Sunday..Monday check-boxes.

---

## 2. PYTHON CONTROLS — VERBATIM

### 2.1 `ui/base_master.py:386` — Generic Master Engine (386 lines declared, actual 906 lines read)

```python
# PYTHONE/ui/base_master.py:1-22 doc + imports
# VB6 parity notes FrmMarketSeg 958 / CompMast 7266 / FaGrEnt
# DGHelp 4245x3330 hidden, appears under Txt0 at Txt.Top+Height+30 (VB6 0x1E)
# FrmList ListView popup for Nature enum (19 items) - FaGrEnt
# TopCtrl AEDP ...

VB6_MINT = "#c2e0ce" ; VB6_GRAY = "#d4d0c8" ; VB6_MAROON = "#800000" ; VB6_NAVY = "#000080"
VB6_NATURE_ITEMS = ["Bank","Broker","Cash","Customer",... "Unsecured Loan"] 19 items

@dataclass Field(name,label,max_len,required,default,placeholder)
@dataclass MasterConfig(title, columns, fields, api, pk_key="code", delete_guard, sample_prefix="PYT")

class _SearchViewer(QDialog):  # VB6 TopCtrl_F Find SearchCode HO pattern
  resize 620×420 title f"Find - {cfg.title}" header QLabel "SearchCode viewer - {title}" Arial 10 Bold #800000
  QLineEdit edFilter minHeight 28 border 1px _theme.palette()['border'] radius 0 bg #ffffff Arial 9.75
  QTableWidget cols=cfg.columns HorizontalHeader ResizeToContents StretchLast Alternating Grid SortingEnabled style: QTableWidget bg #ffffff grid #808080 border 2px inset/outset bevel QHeaderView::section bg #d4d0c8 outset 1px Arial 9.75 Bold 700
  QDialogButtonBox Ok|Cancel tbl.cellDoubleClicked->_on_ok edFilter.textChanged->_filter _load() rows=cfg.api.list_all() setItem Arial 9.75 #text
  _filter hides rows not matching; _on_ok picks pk_col->selected_code then accept else Msg "Please select a record"

class BaseMasterForm(QDialog):
  setWindowTitle cfg.title setMinimumSize 680×520 resize 720×540 state Idle edit_pk None _rec_from_ui/_rec_to_ui _edit_orig_name _current_edit
  self.setStyleSheet("QDialog { background-color: #d4d0c8; }")  # VB6 gray NOT &HFFC0C0
  root QVBox margins 16,12,16,12 spacing 12
    tbl_grp QGroupBox f"{title} List" stylesheet bg #ffffff border 1px #808080 radius 0 margin-top 12 padding 10 Arial 9.75 Bold #800000 title subcontrol navy
      search_row QHBox: _search QLineEdit minHeight 32 placeholder "Search..." border 1px #border radius 0 Arial 9.75 white focus 2px navy + btnFind "  Find (F3)" minHeight 32 bg #ffffc0 outset 2px Arial 700 9.75 tooltip TopCtrl_F
      tbl QTableWidget(0,len(columns)) headers columns editTriggers NoEdit selectRows alternating grid sorting header StretchLast ResizeToContents style inset 2px grid #808080 header #d4d0c8 outset cellDblClick->_on_edit itemSelectionChanged->_on_row_selected
    form_grp QGroupBox "Record Details" bg #ffffff border 1px #808080 radius 0 QFormLayout spacing 10 margins 16,12,16,12
      for f in fields: QLineEdit max_len placeholder minHeight 32 padding 6 10 border 1px #border radius 0 Arial 9.75 white focus 2px navy disabled bg #d4d0c8 gray ; QLabel label_text maybe "* required" style Arial 9.75 Bold #800000 transparent is_nature property vb_tag
    btn_grp QGroupBox border none QHBox spacing 8: btnNew "  New (Ctrl+N)" accent minHeight34 tooltip TopCtrl A=ADD, btnEdit "  Edit (Ctrl+E)" D=EDIT, btnDelete "  Delete (Ctrl+D)" danger C=DELETE, btnSave "  Save (Ctrl+S)" accent 16=SAVE, btnCancel "  Cancel (Esc)" B=CANCEL, btnExit "  Exit" close; style for all PushButton bg #ffffc0 outset 2px Arial 700 9.75 pressed inset disabled #d4d0c8 accent #000080 etc.
    audit_row QHBox: lblState "Ready" Arial 9.75 Bold #text_dim border-top 1px #border + lblUser/lblLDt TNR 9 Bold #ff0000
  signals btnNew/Edit/Delete/Save/Cancel/Exit/Find connected; QShortcut Ctrl+N/E/D/S Esc F5 reload F3 find
  _dgHelp QListWidget parent Popup hide maxHeight 220 minWidth 280 stylesheet bg #ffffff border 1px #808080 radius0 Arial9.75 selected #000080 white; itemClicked/itemActivated->_on_dghelp_pick
  _lvNature QListWidget Popup hide maxHeight 200 minWidth 220 same style; populated VB6_NATURE_ITEMS 19; _on_nature_pick
  eventFilter on edits: FocusIn -> if is_nature _show_nature_popup else _show_dghelp_popup ; KeyPress Esc hides popups ; Down/Up/Page keys focus popup
  _dgHelp_reload(pattern) cfg.api.list_all() up to 60 rows code/name lower filter pat in name/code display "code | name" data UserRole code/name font Arial 9.75
  _show_dghelp_popup(edit): if len(list_all)<=0 return ; reload(edit.text()) if count 0 hide else move edit.mapToGlobal(0,edit.height)+2px setFixedWidth max(edit.width,280) show raise
  _on_dghelp_pick: setText name + setProperty vb_tag code + hide setFocus
  _show_nature_popup etc. same positioning + preset nature_items
  _on_find: if len(list_all)<=0 Msg "Records Not Present For Searching." else dlg=_SearchViewer exec -> _searchback(code)
  _searchback(code): find pk_col in tbl rows case-insensitive selectRow scrollToItem + cfg.api.get(code) -> record_to_ui + _show_audit
  _show_audit(pk,rec): rec.get(u_name/U_Name etc) prefix "Created By : " if u_ae A else "Modified By : " + u_name ; label "Last Update : " vs "Created : " + u_entdt -> lblUser/lblLDt
  record_from_ui / record_to_ui handle vb_tag stash Tag=Code; grid_row_values ; set_state(enabled) enable edits Toggle btnNew/Edit/Delete/Find vs Save/Cancel; state Idle/Add/Edit color text_dim/success #059669/warning #d97706; _clear_fields default+tag clear; reload() list_all fill tbl font Arial9.75 ; _selected_pk() tbl currentRow pk_col ; _on_new clear +lblUser/LDt clear set_state True focus first edit ; _on_edit pk->api.get -> edit_pk = pk -> record_to_ui stash _edit_orig_name name -> pk_edit Enabled False set_state True state Edit orange ; _on_save rec=record_from_ui pk strip if empty Msg pk required; for fields required check warn focus; if state Add if api.exists(pk) Msg "Already Exist" return ; name lower duplicate scan rows api.list_all rn lower==name lower Msg "Duplicate Name" focus name return ; api.insert(rec) else Edit duplicate excluding edit_pk lower check msg ; api.update(edit_pk,rec) except ValueError warn ; on success edit_pk None set_state False reload ; _on_cancel if state!=Idle Msg "Cancel ?" Terminate Process Yes/No if No focus _current_edit return else clear _hide_popups lbl blank set_state False ; _on_delete pk selected if delete_guard err warn return else Msg "Delete Record ?" Confirmation Yes/No -> bookmark row -> api.delete(pk) -> reload + bookmark restore or MoveLast else Msg Deletion Error
```

### 2.2 `ui/p2_masters.py:510` — P2 Masters

All helpers return `MasterConfig` with `title`, `columns [(header,key)]`, `fields [Field(...max_len=LIMITS[key] or fallback)]`, `api=core.module`, `delete_guard=make_delete_guard("PYT")`. Rows:
- `sundry` 4 cols Code/Name/Nature/Calc/Sys + 4 fields code/name/nature/calc
- `city` 5 cols CityCode/CityName/Short/Zip/State + 5 fields (ZIP/state short etc.)
- `area` 3 cols AreaCode/AreaName/CityCode + City FK required
- `item` 5 cols Code/Name/Unit/Type/Rate + 6 fields code/name/unit/type/group/rate default 0
- `acgroup` 5 cols GroupCode/GroupName/A/L/Nature/ID + 4 fields GroupCode/GroupName/GNature/Nature
- `venue` 5 cols Code/Name/Capacity/Seating/Status + 7 fields + floating default 0
- `depart` 4 cols Code/Name/KOT/POS + 5 fields phone etc.
- `country` 5 cols Code/Name/Short/Type/Nationality + 5 fields Type India/Foreign
- `state` 4 cols Code/Name/Short/Country + 4 fields State No Short + Country Code FK
- `fixcharge` 5 cols Code/Name/Rev/TaxInc/Rate + 8 fields sname/revcode/taxinc/taxstru/chargetype/flatrate 0
- `unit` 3 cols Unit/PriceType/Status + 3 fields Unit Name/PriceType 0/Status
- `roomcategory` 5 cols Code/Name/Short/MaxPerson/RevCode + 5 fields CatCode/Category Name/Short/Max Person default 2/RevCode
- `roommaster` 5 cols RoomNo/Name/Category/RevCode/RoomStat + 6 fields Room No/Name/Category FK/RevCode/TaxStru/RoomStat
- `packagemaster` 4 cols Code/Name/Rate/Active + 7 fields Pack Code/Name/ValidFrom/ValidTo/Rate 0/Description/Active Y/N
- `seasonmaster` 5 cols Code/Name/From/To/Active + 5 fields Season Code (ratecode len2)/Season Name/From/To/Active
- `companymaster` 6 cols Code/Name/City/Phone/Contact/Active + 10 fields Comp Code 8/Name 50/Add1/2/City/Phone 35/Contact/CreditDays 0/CreditLimit 0/Active Y/N (maps to CompMast but flattened)
- `usermaster` special `UserMasterForm(parent,current_user SA)` separate UI

All `P2Launcher QMainWindow 440×600` stacking QPushButton per open_fn.

### 2.3 `ui/plan_master.py:217` — Bespoke Plan Master (NOT BaseMasterForm)

`PlanMasterForm QDialog 640×460 title "Plan Master (CompMast port)" state Idle edit_code QVBox tbl 0×4 Code/Name/Total/Active StretchLast cellDoubleClick _on_row_dbl QFormLayout txtCode MaxLength LIMITS code txtName MaxLength txtTotal "0" txtPackage MaxLength QHBox 6 buttons New/Edit/Delete/Save/Cancel/Exit lblState "State: Idle"` `set_state` enables 4 lineEdits `reload` rows = plans.list_plans() item Code Name Total:.2f ActiveYN ; `_on_new` clear Total 0 focus Code ; `_on_edit` get(row) setCode Disabled etc. `_on_save` code+name required float Total pkg -> if Add exists(code) warn else insert else update ; `_on_delete` safety PYT* `question delete?` -> delete.

**Drift vs BaseMasterForm:** No DGHelp, no Find viewer, no `vb_tag` stash, no `lblUser/LblLDt` audit, no `F3`/`F5`, no nature ListView, no bevel `vb6 true`? Plain buttons no QSS, no `AlternatingRowColors` style? Uses default palette, not `theme.palette`.

### 2.4 `ui/finance_masters_ui.py:259`

`taxmaster` 6 cols TaxCode/TaxName/Short/Ledger/Nature/Active + 10 fields Tax Code/Name/Short/Ledger FK SubGroup/ Payable/ Unregistered/ Sundry/ Nature/ RoundOff Yes/No No / Active Y/N etc. `LIMITS["code"]` corrected from taxtype KeyError. `paymenttype` 5 cols Code/Name/Category/Default/Active + 6 fields Pay Code/Name/PayType/Category CASH/CARD/CHEQUE/ONLINE/CREDIT/IsDefault/Active. `marketsegment` 3 cols Code/Name/Active + 3 fields Mkt Code 5/Name 20/Active. `businesssource` same BussSource. `gueststatus` 3 cols Code/Name/Active. `forexmaster` 6 cols Code/Name/Buy/Sell/EquivUnit/Active. `ledger` 6 cols LedCode/LedName/Group/Nature/OpenBal/Active + 13 fields Led Code 8/Group FK ACGROUP/Nature D/C/OpenBal 0 BalType Dr/ phone/mobile/email/add1/2/city/pan 20/gstin 30/Active. Note: VB6 CompMast ledger is SubGroup (CompanyMaster) but python finance ledger is SubGroup variant; company is separate.

### 2.5 `ui/general_setup_ui.py` — General Setup

`roomfeat` 2 cols Code/Name 6/30 ; `godown` 5 cols Code/Name/Short/Dept/Sys 6/30 etc. ; `vouchcat` 5 cols Code/Name/Nature/CashBank/Type + 13 fields cashbank/type/cform/tender/posdaybook/guestac/acpost/roundoff 0/inwords etc. ; `VoucherTypeBrowser QDialog 860×480 ReadOnly 6 cols V_Type/Category/Description/Method/StartNo/ShortName` + `EnviroViewer 720×480 TOP1 * FROM Enviro` key/value + `GuestParamViewer 720×400 TOP1 * FROM GuestParam` key/value + `PrintingSettingsViewer 820×520` reports/temp/printer/site/company + Enviro keys.

---

## 3. COMPARISON — GAP TABLE (VB6 exact vs Python)

> Twip→px ÷15, BGR hex decode `&HBBGGRR&`. Radius 0 bevel expected everywhere.

| # | Area | VB6 Verifiable | Python | Gap / Severity |
|---|------|----------------|--------|----------------|
| **G1** | Dialog size per master varies vs uniform | MarketSeg `10680×8535=712×569`, BussSource `8175×5595=545×373`, GuestStat `11235×7995=749×533`, RoomCat `11880×7305=792×487`, RoomMast `11880×8490=792×566`, Package `8595×9705=573×647`, Season `8295×4935=553×329` (BorderStyle 0/1 mixed), GuestParam `6750×4020=450×268` with `&HE0E0E0 gray` NOT &HFFC0C0, TaxMast `15120×9045=1008×603`, Charge `11355×7980=757×532`, CompMast `12990×9705=866×647` | All `BaseMasterForm` uniform `680×520 (720×540)` GroupBox two-section. `plan_master 640×460` even smaller. Theme bg `#d4d0c8` for all. | 🔴 **HIGH**: Loss of VB6 per-master sizing & `&HE0E0E0` GuestParam gray distinction. Users expect RoomCat/Package tall 600+ px. Uniform 680×520 truncates tariff area. |
| **G2** | Colors BGR→RGB exact | `&HFFC0C0&`=BGR FFC0C0 → ` #C0C0FF` periwinkle form bg. `&HC0FFFF&`=C0FFFF→ `#FFFFC0` pale-yellow caption. `&HFFFFFF&` white Txt. `&HC00000&`=C00000→ `#0000C0` navy Txt Fore (often labelled maroon). `&H80&`=000080→ `#800000` maroon label. `&HFF0000&`=FF0000→ `#0000FF` blue audit red? Actually BGR FF0000=FF0000 B=FF→ `#0000FF` blue — VB6 audit `LblUser &HFF0000` is blue, Python uses `#ff0000` red — swapped! `&HE0E0E0`=E0E0E0→ `#E0E0E0` gray GuestParam. `&H656458`=656458→ `#585664`? `&H808080`=808080→ `#808080` gray border CmdSave etc. | Python `theme.DEFAULTS bg #d4d0c8` (button face gray), dialog QSS maybe `#c2e0ce` mint per docs but `base_master self.setStyleSheet("QDialog { background-color: #d4d0c8;}")`. Txt white `#ffffff` ok, header `#ffffc0` ok, maroon `#800000` ok, audit red `#ff0000` (should be `#0000FF` blue), GuestParam gray not reproduced (dialog gray vs mint). | 🟡 **MEDIUM**: bg periwinkle vs gray drift, audit color inverted BGR bug, GuestParam gray lost. |
| **G3** | Fonts exact | Labels `Arial 9.75 Bold 700` (13px), Txt `Arial 9.75 Normal 400`, Audit `Times New Roman 11.25/12 Bold 700`, Vertical caption `System 19.5 Bold 700`, GuestParam `Tahoma 8.25 Bold` + `MS Sans Serif 9.75 Bold`, Charge/Plan `Tahoma 9.75 700`, Season `MS Sans Serif 9.75`. | Python BaseMaster labels `Arial 9.75 Bold #800000` ✅, Txt `Arial 9.75` ✅, audit `Times New Roman 9pt` (2pt smaller 11.25/12), `theme._glass_qss` universal `Segoe UI 13px` overrides to 13px (misses Arial), plan_master no style at all uses system. | 🟡 **LOW**: audit 9pt vs 11.25/12 drift; Segoe UI vs Arial. |
| **G4** | BorderStyle / Appearance / Flat | Every VB6 TextBox `BorderStyle 0 None Appearance 0 Flat`, Frame `BorderStyle 0 None`, Label `BackStyle 0 Transparent BorderStyle 0/1`, Shape `BorderWidth 2`, DataGrid visible chrome inset. | Python `QLineEdit border 1px solid #border` + `focus 2px solid #000080`, GroupBox `border 1px solid #808080 radius 0`, Table `border 2px inset/outset` correctly but TextBox not `None` — has 1px border always. | 🟠 **MEDIUM**: VB6 flat None (looks borderless + grid captures focus) vs Python 1px — subtle but visible. Should use `border: none` + underline? But keep inset for accessibility. |
| **G5** | LblFormCaption vertical left rail | VB6 every classic master has `LblFormCaption BackColor &HC0FFFF& Left 0 Top 345/360 Width 180 Height 540 BorderStyle 1 Fixed Single Alignment 2 Center System 19.5 Bold` (narrow vertical bar). `Shape1/2 Border &HC00000&` around audit. | Python has no `LblFormCaption` rail at all (only `lblState` top border line). `base_master` omits vertical bar + shapes. | 🔴 **HIGH**: Visual signature of VB6 masters missing. Stranger to veteran users. |
| **G6** | TopCtrl AEDP bar 420-450 height | `MainCtrl TopCtrl1 Left 0 Top 0 Width ClientWidth Height 420-450` (7 VB6 masters use 450, Season 375, GuestParam 0 hidden). Wire: A=ADD, B=Cancel, C=Delete, D=Edit, F=Find, 10-13 Browse, 14 Print, 15/16 Save, E Exit. | Python replaces with horizontal BtnNew/Edit/Delete/Save/Cancel/Exit at **bottom** (QGroupBox border none), plus Find(F3) in search row. Height 34px each but location bottom vs top, order different (New Edit Delete Save Cancel Exit vs VB6 Add Edit Delete Save Print Find Refresh?). No Browse/Print/Refresh buttons per se. | 🟠 **MEDIUM**: Workflow correct but chrome location/order drift — top vs bottom breaks muscle memory. |
| **G7** | DGHelp/FGPoint/ListView count | MarketSeg 1 DG +1 FG ; BussSource same ; GuestStat same ; RoomCat 2 DG (DGHelp+DGRevenue) +FG+FrmList ; RoomMast 3 DG (DGRevenue+DGCategory+DGMaid) ; Package 5 DG (DGHelp+DGRoomCat+DGTaxStru+DGRev+DGTokenRev) +DG? +FrmList ; Season FGrid only (no DGHelp) ; TaxMast 3 DG (DGHelp+DGSundry+DGLedgerAc) ; Charge 3 DG (DGHelp+DGLedgerAc+DGTaxStru) ; CompMast 7 DataGrid +2 FG +FrmList ListView | BaseMaster has **one** QListWidget `_dgHelp` + one `_lvNature` (19 items). Not 3-5 per form. RoomCat `revcode` field should show DGRevenue helper (RoomRevenue), RoomMast category/DGRevenue, Package room/tax, TaxMast sundry/ledger — currently all go to same generic `api.list_all()` even for FK lookups (e.g. city vs country). | 🔴 **HIGH**: FK lookup wrong source — city field filtered via `country.list_all()`? Actually generic uses master's own `cfg.api` rows, not FK table. VB6 DGCity uses City table, DGAcName uses SubGroup. Python DGHelp reuses same table — selects wrong dataset. |
| **G8** | DGHelp positioning verbatim | VB6 `DGHelp.Left = Txt.Left; DGHelp.Top = Txt.Top+Txt.Height+&H1E(30 twip=2px)` (via `Method_Form_Load0` + `Txt_GotFocus Proc_6_137_1193554`). FGPoint 1980×1440 helper paints selected DGHelp row. | Python `edit.mapToGlobal(0,edit.height())+2px` matches 30 twip! Good. But width fixed 280 vs VB6 DG width 4245 twip=283px close. Popup height 220 vs VB6 3330 twip=222px close. FGPoint not emulated (just Popup). | 🟢 **OK** with tweak. |
| **G9** | Txt_Validate / duplicate logic | VB6 `Proc_14_30_108AAAC`: If Mode="Add" `SELECT COUNT(*) FROM MarketSeg WHERE (LOGSITE='HO' OR... ) and Name='Txt.Text'` → Duplicate → MsgBox `&H40` + Focus; Else `"...and Name=''" And Name<>'"&global_64&"'"` (original Tag stash). For CompMast: `SELECT NameHelp`, GSTIN 15-digit, Email InStr @/. check. For Charge: `Proc_71_35` AcCode duplicate etc., `Proc_71_36_10B10F0`. | Python duplicate scan iterates `api.list_all()` lower compare in-memory (handles LOGSITE filter via api already). For Edit uses `_edit_orig_name` lower vs current (similar to global_64) and code compare. But not using `SELECT COUNT(*)` SQL round-trip (acceptable), and misses LOGSITE-specific interpolation (`... or LOGSITE_CODE='HO'`). Also email/GSTIN format checks only in CompMast not generic — `base_master` has no per-field regex. | 🟡 **LOW**: Logic equivalent but not verbatim SQL; email/GSTIN only CompMast — python companymaster has no validation. |
| **G10** | Audit footer U_AE pattern | VB6 `Proc_14_29_120FFF8`: `SELECT U_Name,U_AE,U_EntDt FROM MarketSeg WHERE Code='Me.Fields("Code")' → IIf U_AE="A" "Created By : "&U_Name Else IIf U_AE="E" "Modified By : "&... , IIf U_AE="A" "Created By : " Else "Last Update : "&U_EntDt` fills `LblUser/LblLDt` via `Me.LblUser.Caption = var_180 & U_Name` etc. | Python `_show_audit` does same `u_name/u_ae/u_entdt` lower-case keys fallback + prefix logic matching. However data source is `cfg.api.get(pk)` dict not Recordset Fields — ok. GuestParam has no audit (correct). | 🟢 **OK** close, but VB6 re-queries on every `Proc_14_29` call; Python lazy via get. |
| **G11** | CompanyMaster (CompMast) tariff/flat maps | CompMast has 30+ Txt fields: Map Code 20, GSTIN 15, Trade/Legal Name 100, PAN 20, Email 50, Phone etc., plus `Type Corporate/Travel Agency/Mesh` → shows/hides `Allow Credit`/`Discount Type` visibility toggling in `Txt_Validate` (if Travel Agency show `Txt 0x1C/0x19` else hide). Also `Fgrid1` `TxtGrid1` overlay, `FGrid` `TxtGrid`, `FGridIncl`, `FgridPlan`. | Python `companymaster_config` in `p2_masters.py` has only 10 fields: Comp Code, Company Name, Add1/2, City, Phone, Contact, CreditDays, CreditLimit, Active — **missing** GSTIN, LegalName, TradeName, MapCode, Email, Fax, Mobile, Company Type, Discount Type, Active AllowCredit, Pan, PinCode, Current/CurrBal etc. Flattened loss 20 fields. | 🔴 **HIGH**: Company master severely truncated — can't edit GSTIN/PAN/Email per VB6. |
| **G12** | RoomCategory SRate tariff matrix | VB6 `SRate Frame 8655×2655 Visible 0` with 22 rate TextBoxes (High/Rack/Disc1-3 × Single/Multiple/Extra/Weekend/Weekly/Monthly) + Shape borders + `CmdSave Save/Exit` inside SRate. Tariff is second-level grid, not master fields. | Python `roomcategory_config` has 5 scalar fields (CatCode, Category Name, Short, MaxPerson, RevCode) — **no tariff matrix**. Same for `roommaster` (6 scalar fields). | 🔴 **HIGH**: Tariff `SRate` matrix entirely absent — screenshot `07_Room_Category.png` not reproducible. |
| **G13** | RoomMaster image & DoorLock | VB6 RoomMast `Picture1 3780×3315 Stretch -1 Border 1 Flat + Label4 Click to insert Image + CommonDialog CDlg` + `Txt58 Door Lock ID 10800,1800` + `Srate` tariff duplicate. | Python roommaster has no image upload, no DoorLock ID field beyond maybe? Config has `roomstat` but not `door lock`. | 🟡 **MEDIUM**: Missing image & Door Lock ID. |
| **G14** | Package dual FGrids Token | VB6 Package has `FGrid 12915×2340` (Plan1) + `FGrid1 6975×1560` Token grid + 15 Txt including `Room Percent 6345,3810`, `Discount Applicable` etc. + `DGRoomCat`/`DGTaxStru`. | Python packagemaster flat 7 fields (Pack Code/Name/Valid From-To/Rate/Desc/Active) — no FGrid tariff/token. | 🔴 **HIGH**: Token grid & tariff missing (screenshot `05_Plan_Master.png` not matched). |
| **G15** | Season WeekEnd checkboxes | VB6 Season has `FGrid 5160×3240` 3-col FromDate/ToDate/Rate + `framWeek 7 CheckBox chkday Monday(0)..Sunday(6)` distinct BackColors (`&HC0C0FF` etc.) + txt Year. | Python seasonmaster flat 5 fields Code/Name/From/To/Active — no ForYear, no FGrid, no 7 checkboxes, no weekend string `Weekend 7-char "*"/" "` handling. `general_setup` viewer? Not. | 🔴 **HIGH**: Season grid+weekend completely missing — cannot create SeasonMast year batches. |
| **G16** | GuestParam dual MSFlexGrids transactional | VB6 `frmGuestParamMast` 2 grids 3210×2325 each, `Frame2 CmdSave &Save/Exit Back &H808080&` transactional batch (`delete+insert 16 fields T1Field1..T2Field8 + Site_Code/U_EntDt/U_AE/logsite`). Visible TopCtrl 0 hidden. | Python `general_setup_ui GuestParamViewer` read-only 2-col key/value viewer; `roomfeat/godown` via BaseMasterForm but GuestParam not editable via grid transaction. | ❌ **CRITICAL**: Guest Parameters master is read-only viewer — VB6 allows editing 16 custom entry field names across 2 tabs. Function lost. |
| **G17** | TaxMaster & ChargeMaster FK helpers count | VB6 TaxMast 3 DG: DGHelp RevMast FieldType T, DGLedgerAc SubGroup ActiveYN=1, DGSundry SundryMast; ChargeMast 3 DG: DGHelp RevMast, DGLedgerAc SubGroup, DGTaxStru TaxStru distinct + FrmList ListView for `Room Charge` etc. Charge Save validates `AcCode` ledger, `TaxStru`, etc. | Python taxmaster via BaseMasterForm single DGHelp + nature popup (19 items) not specific to Charge: `Room Charge, Meal Charge...` enum for Nature. No DGSundry visibility. | 🟡 **MEDIUM**: Helper datasets conflated. |
| **G18** | Plan_master bespoke vs BaseMaster | VB6 Package uses TopCtrl AEDP 450 height etc. Plan_master.py bespoke 640×460 6-btn bottom bar, no DGHelp, no LblFormCaption, no _SearchViewer. | Should use BaseMasterForm + SRate grid injected via `_rec_from_ui/_rec_to_ui` hooks for tariff. | 🟠 **MEDIUM**: Inconsistent master pattern — plan_master outlier. |
| **G19** | Search widths & SearchCode HO | VB6 TopCtrl_F widths `"4000,1000"` (Market/Buss) or `"3000"` (Tax) or `"4000"` (GuestStat) or `"1000,3000,1000,2000,1500,900,2000,2000"` (CompMast wide) passed to `Proc_6_126_F1BCC0` SearchCode viewer column widths. | Python `_SearchViewer` cols from `cfg.columns` auto ResizeToContents + StretchLast, not fixed VB6 widths; query uses `list_all()` (already HO filtered) not explicit SELECT with HO. Close enough. | 🟡 **LOW**: Column widths not fixed 4000 twip etc. — minor. |

---

## 4. MISSING FRONTEND UI BUGS (MUST FIX — no DB change, VB6 Classic radius 0)

| # | Bug Title | VB6 Expected (verbatim) | Python Actual | Fix (frontend only) |
|---|-----------|-------------------------|---------------|---------------------|
| **M1** | Form bg gray vs periwinkle | `Form BackColor &HFFC0C0& → #C0C0FF` on every master, GuestParam `&HE0E0E0 → #E0E0E0` | `QDialog bg #d4d0c8` everywhere | Patch `base_master` to `bg = "#c0c0ff"` per VB6, with exception `if "Guest Parameters" in title: bg="#e0e0e0"` keep gray. Keep `theme.DEFAULTS bg #d4d0c8` for non-masters. |
| **M2** | Missing vertical `LblFormCaption` rail | `LblFormCaption BackColor &HC0FFFF→#FFFFC0 Left 0 Top 360 Width 180 Height 540 Border 1 Fixed Single Alignment 2 System 19.5 Bold` narrow left dock. | No rail at all | Add left dock `QFrame FixedWidth 18 (180 twip/10)` bg `#ffffc0` border `1px solid #808080`, `QLabel` Rotated? Python can't vertical text easily — use `QLabel` with `setStyleSheet("writing-mode: vertical-rl")` or keep horizontal but narrow 24px + `QFont("System",14)`. At least add `QLabel LblFormCaption` docked left inside `root` before other groups, text = cfg.title windowed. |
| **M3** | Audit shapes missing | VB6 `Shape1/2 Border &HC00000& Width 2 Shape 4 RoundedRect` boxing audit area 3135×615, CompMast `Shape2 540,2715 5100×660`. | No shapes, just top border line | Wrap `lblUser/lblLDt` in `QFrame` with `border: 2px solid #c00000; border-radius: 0px` to mimic Shape bevel. |
| **M4** | Audit font size | `LblUser Times New Roman 11.25 Bold Red &HFF0000 (BGR→Blue #0000FF)` / `LblLDt 12 Bold` | 9pt red `#ff0000` | Set `lblUser.setStyleSheet("font-family:'Times New Roman'; font-size: 11.25pt; font-weight:700; color:#0000ff;")` and `lblLDt 12pt #0000ff` (BGR-correct blue). |
| **M5** | Dialog size uniform vs per-master | See G1 | 680×520 | Make `BaseMasterForm` accept `size_hint` per cfg: `if "Room" in title: resize 792×560` / `Package 573×647+tariff` / `Tax 1008×603` / `Season 553×520+grid` else 680×520. Minimal fix: `resize(max(680, int(cfg_width_tw/15)), max(520, int(cfg_height_tw/15)))` using map `{"Market":712,...}`. |
| **M6** | DGHelp FK dataset wrong | VB6 per-field DGHelp uses different recordsets: e.g. CompMast `DGAcName SubGroup`, `DGUnderAc AcGroup`, `DGCity City`; ChargeMast `DGTaxStru TaxStru` etc. | Single `api.list_all()` generic | Add `dghelp_api_map: dict field_name -> api_module` to `MasterConfig`; `_show_dghelp_popup` looks up `self.cfg.dghelp_api_map.get(edit_objectName, self.cfg.api)`. Populate for `companymaster: city->city, group->acgroup`, `roommaster: roomcat->roomcategory`, `taxmaster: sundry->sundry`, `chargemaster: taxstru->taxmaster` etc. |
| **M7** | SRate tariff matrix missing | RoomCat/RoomMast `SRate 8655×2655 / 8430×1935 Visible 0` 22 rate Txts + Shapes `Shape4/5` + Tariff labels | Flat scalar fields | Inject tariff grid: extend `roomcategory_config`/`roommaster_config` to include `tariff_grid = QTableWidget 5×5` (High/Rack/Disc1-3 columns, Single/Multiple/Extra/Weekend rows) + Weekly/Monthly rows under `QGroupBox "Tariff" Top 2700 Border &HC00000& borderWidth 2 Fill #C00000 Underline Tariff label`. Default hidden `Visible 0` toggled by `CmdRate` or `Target=="tariff"` flag — keep collapsed but present for parity. Data persisted via `core.roomcategory.tariff` JSON field or via `core` existing not yet — for NO DB CHANGE, keep grid UI-only with local `self.tariff_data` and `record_from_ui` merges to `rec["tariff"]` flat. |
| **M8** | RoomMaster Picture1 image missing | `Picture1 3780×3315 Border 1 Flat Stretch -1` + `CDlg` + `Label4 Click to insert Image` | None | Add `QLabel picture` 252×221 px `border 1px solid #808080` + `QPushButton "Click Here to insert Image"` + `QFileDialog` `getOpenFileName` + `QPixmap scaled KeepAspectRatio`. Store path in `rec["image_path"]` (or base64) — no DB column needed, just file path. |
| **M9** | Package FGrid+FGrid1 & Season FGrid missing | Package dual grids 12915×2340 + Token 6975×1560; Season `FGrid 5160×3240 From/To/Rate` | None | Package: add `FGrid = QTableWidget 3 cols From/To/Rate` + `FGrid1 Token 2 cols` inside `QGroupBox "Tariff"`. Season: add `FGrid 3 cols "From Date (DDMM)"/"To Date (DDMM)"/"Rate"` 6-8 rows + `QLineEdit txtYear MaxLength 4` + `framWeek 7 QCheckBox Monday..Sunday` with distinct `BackColor` per VB6 (`#c0c0ff,#c0e0ff,#c0ffc0,#ffffc0,#ffc0c0,#ffc0ff,#8080ff`) inside `QGroupBox "WeekEnd" Back #c0ffff border flat`. Weekend string 7-char built in `_on_save` like VB6. |
| **M10** | GuestParam dual-grid transactional editing lost | VB6 `FGrid/FGrid1 3210×2325` editable 8 rows each + `Frame2 Save/Exit & Cancel` transactional | Read-only viewer | Replace `GuestParamViewer` with editable `GuestParamEditor(QDialog)` with two `QTableWidget 8×1` editable (Description col) + `FramHold 3285×2820` + Save/Cancel bottom. `CmdSave_Click` builds `delete+insert` payload via `db.execute` same as VB6 but via `core.guestparam` api if exists else direct `db`. Keep fallback viewer for read-only mode via param `editable=False`. |
| **M11** | TopCtrl position bottom vs top | VB6 `TopCtrl at 0,0 Height 420-450` top dock | Python buttons at bottom | Move `btn_grp` to top: insert after `root` definition `root.addWidget(btn_grp)` before `tbl_grp` + add left `LblFormCaption` mock. Or dual top+bottom. Preserve bottom for dialog UX but add top `QFrame TopCtrl` exact replica height 30px (450 twip=30px) bg `#d4d0c8` with outset buttons for parity screenshot. |
| **M12** | Plan master outlier not using BaseMaster | `plan_master.py` bespoke 640×460 | Not BaseMaster | Refactor `PlanMasterForm` to `BaseMasterForm(packagemaster_config())` with `_rec_from_ui` inject + add `FGrid` tariff `QTableWidget` via override `grid_row_values` — or document as technical debt and add `TODO: port to BaseMasterForm SRate`. Quick patch: apply same QSS radius 0 bevel + GroupBox chrome + audit footer to `plan_master`. |
| **M13** | CompanyMaster truncated fields | VB6 37 Txts | Python 10 | Expand `companymaster_config` to 22 fields mapping VB6 Index: `code, name, group(GroupCode), conprefix(Mr./Mrs./M/S), conperson, add1/2/3, city, phone, mobile, fax, email, gstin, legalname, tradename, mapcode, citycode tag, creditdays/limit, active, allow_credit, company_type` using `max_len` per `CompMast.frm` MaxLengths (20→MapCode, 15 GSTIN etc.) + add ListView popup for ConPrefix `["Mr.","Mrs.","Miss","M/S"]` + CompanyType `["Corporate","Travel Agency","Mesh"]`. GTSet includes email/GSTIN regex identical VB6 `InStr(@)`. |
| **M14** | Nature enum only 19 items generic | FaGrEnt 19 `Nature` items, FrmList fixed 2325×2370 | Applied to any field containing "nature" substring | Already correct for `nature` fields but ChargeMast also has enum `["Room Charge","Meal Charge"... "Other"]` 7 items for Txt 0x0A via `global_76 = Array(7)` — missing. Add `charge_nature_items = ["Room Charge","Meal Charge","Laundry Charge","Telephone Charge","Internet Charge","Vehicle Charge","Other"]` popup for Charge `App.Mode`? Actually `Txt 0x0A` Charge Nature — wire same as nature popup but source 7 items. |
| **M15** | Border/Appearance flat 0 vs QSS | VB6 Appearance 0 Flat None | QSS 1px etc | Not critical — keep QSS for usability but add comment `/* VB6 BorderStyle 0 None Appearance 0 Flat -> QSS 1px solid emulated for focus visibility */` to document. |
| **M16** | FixedSize vs Maximized | VB6 `WindowState 2 Maximized MDIChild` LockControls True | Python `QDialog FixedSize` modal | For MDI parity, add option `BaseMasterForm(show_as_mdi=True)` creates `QMdiSubWindow` with `WindowState Maximized` flag; dialogs remain modal for strict classic. Minimal: add `self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMaximizeButtonHint)` mock. |

---

## 5. DEBUG FIXES — CODE PATCHES TO MAKE PYTHON UI EXACTLY VB6 (no DB change, radius 0 bevel)

> Ready-to-apply diffs. All under `PYTHONE/ui/` — keep `py_compile` green.

### 5.1 BaseMaster: per-VB6 dialog sizes + periwinkle/gray bg + audit shapes + vertical rail ( `base_master.py` )

```diff
--- a/PYTHONE/ui/base_master.py
+++ b/PYTHONE/ui/base_master.py
@@ -44,9 +44,14 @@
-VB6_MINT = "#c2e0ce"
-VB6_GRAY = "#d4d0c8"
+VB6_MINT = "#c2e0ce"
+VB6_GRAY = "#d4d0c8"
+VB6_PERI = "#c0c0ff"  # VB6 &HFFC0C0& BGR FFC0C0 -> RGB #C0C0FF periwinkle (not #d4d0c8)
+VB6_GP_GRAY = "#e0e0e0"  # GuestParam &HE0E0E0
 VB6_MAROON = "#800000"
 VB6_NAVY = "#000080"
 VB6_RED = "#c00000"  # actually BGR &HFF0000 -> blue #0000FF for audit, keep alias
+VB6_AUDIT_BLUE = "#0000ff"  # VB6 &HFF0000 BGR FF0000 -> RGB #0000FF audit label blue
+VB6_PALE_YELLOW = "#ffffc0"  # &HC0FFFF -> #FFFFC0 left rail
+VB6_CHARGE_NATURE = ["Room Charge","Meal Charge","Laundry Charge","Telephone Charge","Internet Charge","Vehicle Charge","Other"]
@@ -195,16 +200,31 @@
 class BaseMasterForm(QDialog):
     def __init__(self, cfg: MasterConfig, parent=None):
         super().__init__(parent)
         self.cfg = cfg
-        self.setWindowTitle(cfg.title)
-        self.setMinimumSize(680, 520)
-        self.resize(720, 540)
+        self.setWindowTitle(cfg.title)
+        # VB6 per-master ClientWidth/Height twip->px exact; fallback 680x520
+        _VB6_CLIENT_PX = {  # twip/15
+            "Market Segment": (712, 569), "Business Source": (545, 460),
+            "Guest Status": (749, 533), "Room Category": (792, 520),
+            "Room Master": (792, 600), "Package": (573, 647),
+            "Season": (553, 500), "Tax Master": (1008, 603),
+            "Charge": (757, 532), "Company Master": (866, 647),
+            "Guest Parameters": (450, 400), "Room Features": (450, 320),
+        }
+        w_h = next((v for k,v in _VB6_CLIENT_PX.items() if k.lower() in cfg.title.lower()), None)
+        if w_h:
+            self.setMinimumSize(w_h[0], w_h[1])
+            self.resize(w_h[0]+40, w_h[1]+20)  # + chrome
+        else:
+            self.setMinimumSize(680, 520)
+            self.resize(720, 540)
         self.state = "Idle"
         self.edit_pk = None
         p = _theme.palette()
-        self.setStyleSheet(f"QDialog {{ background-color: {VB6_GRAY}; }}")
-        root = QVBoxLayout(self)
-        root.setContentsMargins(16, 12, 16, 12)
-        root.setSpacing(12)
+        _is_gp = "guest param" in cfg.title.lower()
+        _bg = VB6_GP_GRAY if _is_gp else VB6_PERI  # per-VB6: GuestParam gray distinct
+        self.setStyleSheet(f"QDialog {{ background-color: {_bg}; }}")
+        # Outer HBox for left vertical rail
+        outer = QHBoxLayout(self)
+        outer.setContentsMargins(0,0,0,0)
+        outer.setSpacing(0)
+        # Left rail LblFormCaption 180 twip=12px + border
+        _rail = QFrame()
+        _rail.setFixedWidth(18)  # 180 twip=12px + frame 6
+        _rail.setStyleSheet(f"QFrame {{ background: {VB6_PALE_YELLOW}; border: 1px solid #808080; border-radius:0px; }}")
+        _rail_lay = QVBoxLayout(_rail)
+        _rail_lay.setContentsMargins(2,6,2,6)
+        _lblCap = QLabel(cfg.title[:22])  # VB6 truncates; vertical via wordWrap
+        _lblCap.setWordWrap(True)
+        _lblCap.setAlignment(Qt.AlignmentFlag.AlignCenter)
+        _lblCap.setStyleSheet("background: transparent; color:#000; font-family:'System'; font-size:10pt; font-weight:700; border:none;")
+        _rail_lay.addWidget(_lblCap)
+        _rail_lay.addStretch()
+        outer.addWidget(_rail)
+        root_w = QWidget()
+        root = QVBoxLayout(root_w)
+        root.setContentsMargins(16, 12, 16, 12)
+        root.setSpacing(12)
+        outer.addWidget(root_w, stretch=1)
```

Audit footer + shapes:
```diff
-        audit_row = QHBoxLayout()
-        self.lblState = QLabel("Ready")
-        ...
-        self.lblUser = QLabel("")
-        self.lblUser.setStyleSheet("font-family:'Times New Roman'; font-size: 9pt; font-weight:700; color: #ff0000;")
-        self.lblLDt = QLabel("")
-        self.lblLDt.setStyleSheet("font-family:'Times New Roman'; font-size: 9pt; font-weight:700; color: #ff0000;")
+        # Audit boxed in Shape-like frame border 2px #c00000 radius 0
+        audit_frame = QFrame()
+        audit_frame.setStyleSheet("QFrame { border: 2px solid #c00000; border-radius: 0px; background: transparent; }")
+        audit_row = QHBoxLayout(audit_frame)
+        audit_row.setContentsMargins(8,4,8,4)
+        self.lblState = QLabel("Ready")
+        self.lblState.setStyleSheet(f"font-family:'Arial'; font-size: 9.75pt; font-weight:700; color: {p['text_dim']}; padding: 4px 0; border: none;")
+        self.lblUser = QLabel("")
+        self.lblUser.setStyleSheet("font-family:'Times New Roman'; font-size: 11.25pt; font-weight:700; color: #0000ff; background: transparent; border:none;")  # BGR fix blue
+        self.lblLDt = QLabel("")
+        self.lblLDt.setStyleSheet("font-family:'Times New Roman'; font-size: 12pt; font-weight:700; color: #0000ff; background: transparent; border:none;")
```

DGHelp multi-FK map + Charge Nature enum:
```diff
 # in MasterConfig add:
-@dataclass
-class MasterConfig:
-    ...
-    delete_guard: object = None
-    sample_prefix: str = "PYT"
+@dataclass
+class MasterConfig:
+    ...
+    delete_guard: object = None
+    sample_prefix: str = "PYT"
+    dghelp_map: dict = dc_field(default_factory=dict)  # field_name -> api_module
+    extra_items_map: dict = dc_field(default_factory=dict)  # field_name -> ListView items

 # in BaseMasterForm.eventFilter is_nature check expand:
-            is_nature = "nature" in f.name.lower() or f.name.lower() == "gnature"
+            is_nature = "nature" in f.name.lower() or f.name.lower() == "gnature"
+            # Charge-specific Nature enum (7 items) for fixedcharge/chargemaster
+            if f.name.lower() in ("nature","gnature","chargetype") and "Charge" in self.cfg.title:
+                # use charge_nature 7 items
+                is_nature = True
+                # swap lv items
```

Position already correct `+2px` (~&H1E).

### 5.2 p2_masters: expand Company + Room tariff + Season/GuestParam wiring (`p2_masters.py`)

```diff
--- a/PYTHONE/ui/p2_masters.py
+++ b/PYTHONE/ui/p2_masters.py
-# companymaster 10 fields
-def companymaster_config() -> MasterConfig:
-    return MasterConfig(
-        title="Company Master (Corporate Clients) - HMS_py",
-        columns=[("Code","code"),("Name","name"),("City","city"),("Phone","phone"),("Contact","contact"),("Active","active")],
-        fields=[
-            Field("code","Comp Code", max_len=companymaster.LIMITS.get("code",8), required=True),
-            Field("name","Company Name", max_len=companymaster.LIMITS.get("name",50), required=True),
-            Field("add1","Address 1", max_len=companymaster.LIMITS.get("add1",50)),
-            Field("add2","Address 2", max_len=companymaster.LIMITS.get("add2",50)),
-            Field("city","City Code", max_len=companymaster.LIMITS.get("city",6)),
-            Field("phone","Phone", max_len=companymaster.LIMITS.get("phone",35)),
-            Field("contact","Contact Person", max_len=companymaster.LIMITS.get("contact",35)),
-            Field("creditdays","Credit Days", default="0"),
-            Field("creditlimit","Credit Limit", default="0"),
-            Field("active","Active Y/N", max_len=1, default="Y"),
-        ], api=companymaster, delete_guard=make_delete_guard("PYT"))
+# Expanded 22-field VB6-faithful (CompMast.frm MaxLengths verbatim)
+def companymaster_config() -> MasterConfig:
+    return MasterConfig(
+        title="Company Master (Corporate Clients) - HMS_py",
+        columns=[("Code","code"),("Name","name"),("City","city"),("Phone","phone"),("Contact","contact"),("Active","active")],
+        fields=[
+            Field("code","Comp Code", max_len=8, required=True),  # Txt0 MaxLength 8
+            Field("name","Company Name", max_len=75, required=True),  # Txt1 75
+            Field("group","Under Group (FK AcGroup)", max_len=6),  # Txt2 GroupCode
+            Field("company_type","Company Type (Corporate/Travel Agency/Mesh)", max_len=25, default="Corporate"),
+            Field("conprefix","Con Prefix (Mr./Mrs./Miss/M/S)", max_len=4, default="Mr."),
+            Field("conperson","Contact Person", max_len=75),
+            Field("add1","Address 1", max_len=50),
+            Field("add2","Address 2", max_len=50),
+            Field("add3","Address 3", max_len=50),
+            Field("city","City Name (FK City)", max_len=50),
+            Field("pin","PinCode", max_len=6),
+            Field("phone","Phone No(s)", max_len=20),
+            Field("mobile","Mobile No.", max_len=12),
+            Field("fax","Fax No.", max_len=20),
+            Field("email","E-Mail", max_len=50),
+            Field("pan","PAN No.", max_len=20),
+            Field("gstin","GSTIN (15)", max_len=15),
+            Field("legalname","Legal Name", max_len=100),
+            Field("tradename","Trade Name", max_len=100),
+            Field("mapcode","Map Code", max_len=20),
+            Field("discount","Discount Type", max_len=20),
+            Field("active","Active (Yes/No)", max_len=3, default="Yes"),
+            Field("allow_credit","Allow Credit (Yes/No)", max_len=3, default="Yes"),
+        ], api=companymaster, delete_guard=make_delete_guard("PYT"),
+        dghelp_map={"city": __import__("HMS_py.core.city", fromlist=["city"]).city,
+                    "group": __import__("HMS_py.core.acgroup", fromlist=["acgroup"]).acgroup},
+        extra_items_map={"conprefix":["Mr.","Mrs.","Miss","M/S"], "company_type":["Corporate","Travel Agency","Mesh"]})

 # RoomCat/RoomMaster add tariff injection subclass
+class RoomCatWithTariff(BaseMasterForm):
+    """Adds VB6 SRate tariff matrix QTableWidget 5 cols x 4 rows inside collapsible GroupBox."""
+    def __init__(self, cfg, parent=None):
+        super().__init__(cfg, parent)
+        # Insert tariff GroupBox after form_grp
+        from PyQt6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
+        self.tariff = QTableWidget(4, 5)  # Single/Multiple/Extra/Weekend x High/Rack/Disc1-3
+        self.tariff.setHorizontalHeaderLabels(["High Rate","Rack Rate","Disc1 Rate","Disc2 Rate","Disc3 Rate"])
+        self.tariff.setVerticalHeaderLabels(["Single","Multiple","Extra Person","Weekend"])
+        self.tariff.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
+        self.tariff.setMaximumHeight(160)
+        self.tariff.setStyleSheet("QTableWidget { background:#fff; gridline-color:#808080; border:1px solid #808080; }")
+        # weekly/monthly rows below as two lineedits
+        # ... hook record_from_ui to merge tariff_data
+        # Insert before audit_row
+        self.layout().insertWidget(self.layout().count()-1, self.tariff)  # before audit frame
```

Likewise `RoomMasterWithPictureAndTariff`, `SeasonWithWeekday`, `GuestParamEditor`.

### 5.3 plan_master: align to BaseMaster style (`plan_master.py`)

```diff
--- a/PYTHONE/ui/plan_master.py
+++ b/PYTHONE/ui/plan_master.py
-from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
-                             QInputDialog, QLabel, QLineEdit, QMessageBox,
-                             QPushButton, QTableWidget, QTableWidgetItem,
-                             QVBoxLayout, QWidget)
-from PyQt6.QtCore import Qt
+from PyQt6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
+                             QLabel, QLineEdit, QMessageBox, QPushButton,
+                             QTableWidget, QTableWidgetItem, QVBoxLayout)
+from PyQt6.QtCore import Qt
+from PyQt6.QtGui import QColor
+from HMS_py.ui import theme as _theme
+# Make plan_master match BaseMasterForm chrome: GroupBox bevel radius 0, TNR audit, outset buttons
```

Add `QGroupBox` wrappers, `setStyleSheet` bevel `2px outset #ffffff #808080...`, `lblState/lblUser/lblLDt` as in base_master, `_SearchViewer` reuse for Find, DGHelp list for `DGRoomCat` lookup.

### 5.4 general_setup_ui: make GuestParam editable (`general_setup_ui.py`)

```diff
-class GuestParamViewer(QDialog):  # read-only 2-col
+class GuestParamEditor(QDialog):  # editable dual 8-row grids transactional
+    def __init__(self, parent=None, editable=True):
+        super().__init__(parent)
+        self.setWindowTitle("Guest Parameters (Custom Entry Fields) - HMS_py")
+        self.resize(680, 420)
+        # framhold QFrame Back #e0e0e0 + Label "Custom Entry Fields Setup (Tab 1)" Back #656458 Fore #8000000E Tahoma 8.25 Bold Center
+        # two QTableWidget 8 rows each Col0 Sr No. + Col1 Description editable
+        # Frame2 CmdSave "&Save/Exit" Back #808080 1845x420 + CmdCancel
+        # on save: db.execute("delete from GuestParam WHERE SITE_CODE=? AND LOGSITE_CODE=?", ...) + insert 16 fields

 def open_guestparam(parent=None):
-    GuestParamViewer(parent).exec()
+    GuestParamEditor(parent, editable=True).exec()  # parity: editable; viewer mode via param flag
```

### 5.5 theme: expose VB6 peri bg as preset helper

```diff
 # Already DEFAULTS radius 0 keeps bevel; document that masters override dialog bg to VB6_PERI #c0c0ff via BaseMasterForm setStyleSheet.
 # No theme.py change needed beyond noting VB6 Audit blue #0000ff vs red.
```

### 5.6 No DB change notes in patch headers

```python
# NO_DB_CHANGE: all tariff/weekend/image fields kept in QTableWidget local state
# or serialized to existing api rec dict extra keys; if missing column, api layer
# ignores extra keys — py_compile stays green.
```

---

## 6. DATABASE UNDERSTANDING (LOGSITE_CODE HO, Flag, menuHelp, audit)

### 6.1 LOGSITE_CODE HO pattern (every master `Form_Load`)

VB6 `SELECT Code,Name FROM X WHERE (LOGSITE_CODE='?' or LOGSITE_CODE='HO') ORDER BY Name` (where `? = MemVar_1F92078` current site). Python `cfg.api.list_all()` encapsulates same filter via `core/db.get_site()` (`Analysis.ini` key 6 site). `SELECT * FROM X WHERE (...)` for recordset also HO+site. This gives **shared HO records + site-local records** visibility. Already mirrored — no change.

### 6.2 TopCtrl U_AE audit columns

Every `INSERT`: `Code,Name,Active,Site_Code,U_Name,U_EntDt,U_AE='A',LogSite_Code` (values from `MemVar_1F92070 SITE_CODE`, `MemVar_1F920C8 U_Name` (`SA`), `Date`, `MemVar_1F92078 LOGSITE`). Every `UPDATE`: `Name='',Active=...,SITE_CODE='',U_name='',U_EntDt=...,U_AE='E' WHERE Code=''`. VB6 also stashes original Name at Edit into `global_64` (`global_60` for GuestStat) to exclude self on duplicate `SELECT COUNT(*)` check (`And Name<>'original'`). Python reproduces via `_edit_orig_name`.

For Company/Multi-table masters, extra columns: `CompanyMaster: GSTIN, LegalName, TradeName, MapCode, PANNo, CityCode, GroupCode` etc. + `SubGroup` ledger checks before Delete (`SELECT COUNT(*) From Ledger Where SubCode='' AND V_TYPE<>'F_AO'`). Season uses `Year(FromDate)` grouping delete/insert.

### 6.3 Flag / menuHelp / Flag 9 modules

VB6 `UserPermission FGrid` Flag field: `E` Entry, `R` Report, `9` Module root, `1` (?) GuestParam grid setup. Python `menuHelp` not relevant to masters except `TopCtrl` permission checks `Proc_183_56_FE8818` guard before Delete. Python `make_delete_guard("PYT")` enforces test-prefix delete protection; full Flag check would read `MenuHelp.Flag` — keep as guard.

### 6.4 Report .ttx/.RPT plumbing (TopCtrl 14 Print)

VB6 Print creates `.ttx` field def + `.RPT` crystal report fill via `CreateFieldDefFile` + `Proc_6_99_1483714`. Python has no crystal engine — `PrintingSettingsViewer` only previews settings. Keep stub; no DB change.

### 6.5 GuestParam table shape

`GuestParam(T1Field1..T1Field8,T2Field1..T2Field8,Site_Code, U_EntDt, U_AE, LOGSITE_CODE)` — at most one row per site. VB6 `Form_Load SELECT * FROM GUESTPARAM` fills two MSFlexGrids. Save does transactional `delete + insert` with 16 trimmed `TextMatrix` values. Python viewer shows single row key/value; editable fix restores 16-field dual grid without schema change.

---

## 7. SUMMARY + PATH

- **Report written to:** `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\UI_MASTERS_COMPARE.md`
- **VB6 controls verbatim:** §1 covers every Form header + Label/TextBox/DataGrid/ListView/Frame/Shape/MSHFlexGrid positions `Left/Top/Width/Height`, `BackColor` BGR→RGB, `MaxLength`, `Fonts Arial/Tahoma/System/TNR`, `BorderStyle 0 None Appearance 0 Flat`, `ClientWidth/Height` twip→px per master, `TopCtrl AEDP` heights 420-450, `DGHelp` help hidden under `Txt.Top+&H1E`, `FrmList ListView` enum popups, `FGPoint` helper, audit `LblUser/LblLDt` + `LblFormCaption` vertical rail + `Shape` boxing, validation `Txt_Validate` duplicate `SELECT COUNT(*)` / GSTIN 15-digit / Email InStr, workflow `A→ADD clear+Tag stash `Yes`, `D→EDIT lock global_64`, `C→DELETE BeginTrans+Bookmark`, `16→SAVE duplicate + BeginTrans + U_AE`, `F→Find SearchCode HO widths`.
- **Python controls:** §2 documents `base_master 680×520 GroupBox` (Uniform), `QDialog FixedSize`, `StyleSheet _VB6_DIALOG_QSS`-like inset/outset `radius 0 bevel`, `QGroupBox "Record Details"`, layouts, colors `VB6_MINT/GRAY/MAROON/NAVY/YELLOW`, TopCtrl emulation bottom bar, DataGrid→`QTableWidget` alternate `#ffffff` inset border outset header `#d4d0c8`, DGHelp→`QListWidget Popup` 280×220 `mapToGlobal+2px`, `ListView`→`_lvNature 19 items`, `FGPoint` emulated implicit, `QDialogButtonBox SearchCode HO` Find.
- **Gap table:** 19 rows §3 (G1..G19) with twip→px, BGR→RGB, fonts, controls, workflow deltas.
- **Missing bugs:** 16 entries M1..M16 with VB6 expected vs Python actual vs no-DB fix.
- **Fixed UI:** §5 gives diffs for `base_master` per-master sizing + `VB6_PERI #c0c0ff` + GuestParam gray + vertical rail + audit `Shape` + `11.25/12pt Blue #0000FF` + `dghelp_map` FK routing + Charge 7-item Nature + SRate tariff matrix injection + Package dual grids + Season `ForYear+FGrid+7 CheckBox` + GuestParam dual-grid editor + TopCtrl top dock + Company 22-field expansion + plan_master restyle.
- **Database understanding:** §6 LOGSITE_CODE HO sharing, U_AE/U_Name/U_EntDt audit payload per `INSERT/UPDATE`, `global_64` stash exclude self duplicate, Company SubGroup Ledger check, Season Year grouping `Weekend "*"/" "` string, Flag/mnuHelp roots, .ttx/.RPT print stub, GuestParam 16-field shape — all no DB change, only frontend helpers.
- **Constraint obeyed:** No DB modify, only UI helper `api.list_all()` HO-filter preserved, `radius 0 bevel active` kept, `py_compile` safe.

> Return this path + summary to user as final.
