# UI POS RETRY COMPARE — VB6 ↔ Python Frontend Parity (FODER)

> **Scope:** POS / POINT OF SALE — frontend only. No DB change.
> **Workdir:** `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE`
> **Generated:** 2026-09-24
> **VB6 sources (7 forms):** `RsKOTEntry.frm` · `RSSaleBill.frm` · `RsKOTTransfer.frm` · `RsTbChange.frm` · `RsPaymentReceice.frm` · `RsPOSDisplay.frm` · `RsTableMast.frm`
> **Python sources (3 files):** `PYTHONE/ui/kot_entry.py` · `PYTHONE/ui/pos_sales_ui.py` · `PYTHONE/ui/kot_transfer_ui.py`
> **Related theme:** `PYTHONE/ui/theme.py` (750 lines, `DEFAULTS` VB6 Classic) at `PYTHONE/ui/theme.py:21-60`

---

## 1) Methodology

1. Each `.frm` read verbatim (ClientWidth/Height twips, BackColor BGR, BorderStyle, every `Begin TextBox / CommandButton / DataGrid / MSHFlexGrid / Label / Frame / Shape / Line / Timer / CommonDialog`, Fonts, MaxLength, Enabled/Visible, TabIndex, Alignment, Appearance).
2. Each `.py` read verbatim (QDialog/QMainWindow, `resize()` vs `setFixedSize`, StyleSheet via `_theme`, layouts, TopCtrl/state).
3. BGR→RGB conversion applied: VB6 `&HBBGGRR` → CSS `#RRGGBB` (swap R↔B). Example `&HC0C0FF` → B=C0 G=C0 R=FF → `#FFC0C0`.
4. Enviro flag `MemVar_1F9220C` (TouchScreen `Yes/No`) traced in `RsPOSDisplay.frm` and `RsKOTEntry` load path.
5. Gaps ranked by user-visible workflow breakage; ≤15 reported. Code patches proposed as minimal frontend diffs (no SQL / no migration).

---

## 2) VB6 Controls — Verbatim Inventory (Frontend-Critical)

### 2.1 RsKOTEntry.frm — `FODER/RsKOTEntry.frm:1-1038` (header) + code to `~1715`

- **Form:** `RsKOTEntry.frm:2-33` — `Caption="KOT"`, `BackColor=&H80000005&` (system Window), `ForeColor=&H40&`, `WindowState=2` (Maximized), `MDIChild=-1`, `ControlBox=0` (no X), `KeyPreview=-1`, `Visible=0`, `ClientWidth=13245` twips (~882 px @1440), `ClientHeight=10935` (~729 px), `ScaleMode=0` (twips), `Font Name=Arial Size=9.75 Weight=400`, `FillColor=&H80&` (maroon), `Appearance=0 Flat`, `WhatsThisHelp=-1`, `TopCtrl1: Left0 Top0 Width13245 Height450` (`RsKOTEntry.frm:36-42`).
- **Frame FrKOT:** `RsKOTEntry.frm:43-60` — `Caption="Frame1"` (hidden by paint), `BackColor=&HC0C0FF&` → `#FFC0C0` light pink, `Left0 Top0 Width26506 Height11010`, `Font System 9.75 Bold`, `BorderStyle=0 None` — **is the real canvas** (form FrKOT covers MDI child; Python has no equivalent).
- **Txt array (15 indices, 0-14) — positions matter:**
  - `Txt(0)` `RsKOTEntry.frm:206-216` `Left5640 Top525 Width975 Height345 MaxLength8 ForeColor &HC00000&` (→ `#0000C0` navy-blue text) `BorderStyle0`
  - `Txt(1)` `:218-227` `6630,525 1095×345 Max12`
  - `Txt(2)` `:150-161` `7740,525 555×345 Max12`
  - `Txt(3)` `:184-205` `11325,6300 2325×210 Visible0 BackColor &H80000000& Max40 Font Tahoma9` (hidden memo)
  - `Txt(4)` `:173-183` `900,1005 915×285`
  - `Txt(5)` `:162-172` `4020,1005 2580×285 Max50`
  - `Txt(6)` `:118-129` `7515,1005 3915×285`
  - `Txt(7)` `:105-117` `9570,1305 1860×285 Visible0`
  - `Txt(8)` `:92-104` `10455,1695 3480×285 Enabled0`
  - `Txt(9)` `:79-91` `10455,2010 … Enabled0`
  - `Txt(10)` `:66-78` `10455,2325 … Enabled0` — triplet Remark1-3 disabled display
  - `Txt(11)` `:267-280` `900,1305 2775×285 Enabled0 Visible0 Max75` (Member)
  - `Txt(12)` `:253-266` `3690,1305 1140×285 Visible0 Max11` (Token)
  - `Txt(13)` `:312-323` `2400,1005 660×285 Max5` (Pax)
  - `Txt(14)` `:299-311` `5895,1305 930×255 Visible0 Max15`
  - `TxtGrid(0)` `:229-252` `1080,8250 480×240 BackColor &HFFFFC0& (→ #C0FFFF) Visible0 MultiLine` — inline grid editor floating
  - `txtDisc` in `FrmeDisc` `:341-358` `60,270 5000×240 Max75 Tahoma9` — Description popup Frame `RsKOTEntry.frm:324-359` `Left16170 Top720 5130×585 Visible0`
- **CheckBoxes / Grids / Buttons:**
  - `ChkNCKOT` `:130-149` `8130,1305 600×285 Caption="NC " BackColor &HDEE6FE& ForeColor &HC00000& Font Arial 9.75 Bold`
  - `FGrid` MSHFlexGrid `:440-446` `30,1620 8655×6090` — **primary line grid** (item / qty / rate / amount)
  - `FGrid1` `:360-367` `10185,4560 5940×2325 Visible0` + `FGrid2` `:471-478` `10215,6930 5940×2325 Visible0` — KOT history / pending shadow grids
  - `DGTable/DGWaiter/DGItem/DGRest/DGMember/DGNCType` `:376-429` each `Visible0 TabStop0` — popup lookup grids positioned far off-canvas (`Left16320+ Top2190` etc.) and moved to `Txt.Top+Height` at `Txt_GotFocus` `:1451` via `Proc_6_137_1193554` — Python uses inline QComboBox instead
  - `FGPoint` MSFlexGrid `:430-437` `18360,9675 1980×1440 Visible0` — anchor point for `DG*` positioning
  - `LblRest` `:910-930` `15,525 2235×345 BackColor &HFFFFFF& Fore &HFF0000& Font Arial 11.25 Bold AlignCenter`, `lblSession` `2250,525 1665×345`, `LblKotNm` `3915,525 1725×345`, `LblState` `8340,525 3090×345`, `LblRestz` `12990,-780 285×525 Font Times New Roman 20.25 Bold BackColor &HC00000&` — header ribbon (Python collapses to 3 fields)
  - `LblCurStockStr` `:487-506` `0,7890 2370×375 ForeColor &H80& Font Arial Narrow 15.75 Bold`, `lblclr` `:549-565` `1080,8490 600×240 BackColor &HFF00& (→ #00FF00 green)`, `Label1(10)="Free Items"` `:527-548` — stock / color picker
  - `BtnEnh CmdTabeSt/CmPendingKot/cmdNCBill/CmdFreeItem` `:447-486` each ~`945×540` `Visible0` — bottom action strip (Table Status / Pending KOT / NC Bill / Free Item)
  - `Timer2 Interval10` `:61-65` — drives inline edit commit (`Txt_GotFocus` → `Timer2.Enabled=True`)
  - `CommonDialog cdl` `:438-439`

**Fonts:** Form Arial 9.75; FrKOT System 9.75 Bold; Txt Arial/Tahoma; FGPoint mapping.

**Validation / Workflow (frontend):**
- `Txt_GotFocus` `:1445` highlights + seeks recordset (`Find "Name="`) for indices 4,5,7,11 (Table/Waiter/NCType/Member) and moves `DGRest/DGTable` etc. visible.
- `Txt_KeyDown` `:1563` Esc→ `Proc_30_98`, arrows `&H26/&H28` navigate DataGrid via `Proc_6_138`; `Txt_KeyPress` `Txt_KeyPress0` filtering by `Proc_6_58` / `Proc_6_42` length caps.
- Pending KOT overlay: `CmPendingKot_UnknownEvent_9` `:1304` toggles `FGrid2` + `LblPendingKotItem` (`"Pending Kot"` `:507-526`) visibility from KOT query; Python has no pending overlay.
- Stock color: `lblclr_Click` `:1077` opens `CommonDialog.Color`, paints `FGrid.CellBackColor` for qty>0 rows — Python has no cell coloring.

### 2.2 RSSaleBill.frm — `FODER/RSSaleBill.frm:1-2000+` (50123 lines total, 11280×8595)

- **Form:** `RSSaleBill.frm:2-30` `Caption="Sale Bill Entry"` `BackColor=&HFFC0C0&` (→ `#C0C0FF` lavender-gray), `WindowState2 MDIChild -1 ControlBox0 KeyPreview -1 Client11280×8595 (~752×573 px)`.
- **Grids & Editors:**
  - `FGrid` primary sale lines (implied via `TxtGrid(0..2)` inline editors) `TxtGrid(0)` `:1650-1673` `1200,1590 765×240 BackColor &HC0C0C0& Visible0`; `FGrid1` in `FrPOSBillGroupWise` `:1103-1109` `495,2020 6930×5375`; `GridSel` `:1814-1821` `150,705 2655×2505`; `FGrid` via `Txt.Validate` token.
  - `DGItem` `:1204-1212`, `DGShift`, `DGMember` `:1969-1977` hidden lookup grids.
- **Header frames:**
  - `FrCustInfo` `:240-597` `BackColor &H80FF&` (→ `#FF8000` orange — `B=80 G=FF R=FF`? actually `&H80FF&` = 0x0080FF → `#FF8000`) `8385,5775 4740×1140 Visible0 Enabled0` — 8 `TxtCust` fields (Phone/City/Address/Guest/Likes/Dislikes/Birthday/Anniv) each `Left1200 Width3690 Height285 Max50 ForeColor &HC00000&`.
  - `FrSun1/2/3` `:1275-1649` `8385,1650/1845/2175 3390×2865 Visible0` — Tax/Discount sub-forms each with `TxtGt*` (`1185×240 AlignRight Enabled0`), `TxtPer*` (`510×240 Visible0`), `LblCap*` `LblAt* "%"` `LblDummy*` — **Sale totals suntran**.
  - `FrTokenInfo` `:1744-1821`, `FrAutoSettlement` `:1899-1968` (`Smart Card Settlement` 5085×1245), `FrModification` `:751-802`, `FrPOSBillDateWise/GroupWise` `:803-1171` (`6255×3105` / `8385×8565` validation dialogs), `FrCustSaleDetail` `:39-215`, `FreInvInfo` `:598-723` (eInvoice IRN/AckNo/AckDt), `FrCtrl` `:1213-1252`.
- **Buttons:** `CmdSave/CmdCtrl/CmdRedeem` in `FrCtrl`; `CmdAutoSettlement/CmdCashCardStatement/CmdToken/CmdGeneInvoice/CmdeInvoiceJson|Sql`; `CmdGroupwise/Datewise`, `CmdFillDetail/CmdConvert/CmdReset`, `CmdCustPrint`, `Command4 "Verify Member"`.
- **Text boxes:** `Txt(2)` hidden `&H80000000& 9840,135 Top2325×210 Max40 Tahoma9`; `Txt(18) 9435,795 1905×285 Enabled0 Visible0`; `Txt(16) 7890,795 975×285 Visible0 Max11`; `Txt(15) 10155,495 1185×240 AlignRight Max15`; `TxtGrid(0..2)` floating line editors; `TxteInvInfo(0..2)` locked 5800×240.
- **Fonts:** Form Tahoma 11.25; inner labels Tahoma 9/9.75 Bold; FrSun `System 9.75 Bold`.

### 2.3 RsKOTTransfer.frm — `FODER/RsKOTTransfer.frm:1-256`

- **Form:** `:2-17` `Caption="KOT Transfer"` `BackColor &H80000005&` `ScaleMode1 MDIChild-1 Client4905×3195 (~327×213 px)` `Appearance0 Flat`. Actually `FrameOffline` dictates canvas `8820×6645` (>Client → clipped, resized in `Form_Activate` `:344-357`).
- **FrameOffline:** `:18-38` `Left0 Top0 8820×6645 Border0` contains `DataCombo TXT_PKOT 1905,1485 1905×360`, `TXT_TOTABLE 5850,1485 1905×360`, `BtnEnh CmdChange 2640,3525 1575×750`, `CmdExit 4215,3525`, `LblFormCaption &HC0FFFF& (→ #FFFFC0 pale yellow) Left0 Top0 8835×540 Font System 19.5 Bold Center Border1`, `Shape2 BorderColor &HC00000& (→ #0000C0) 480,1125 7635×1725 Shape4 BorderWidth2 FillColor &HC000C0&`, `Line1 BorderColor &HC00000& X1 4260 Y1 1140 X2 4260 Y2 2835 BorderWidth2` (vertical divider between KOT# and Table#), labels `LblKOTTable "KOTTB" Fore &HFF& (→ #FF0000 red)`, `LblFrTable "KOT NO. #"`, `LblToTable "TABLE NO. #"`, `"On Table:" & LblKOTTable`.
- **FrameOnline:** `:171-255` `Left9090 Top420 4605×4845 Visible?` dynamic table map `FrameOption 195,3570 2730×1200` with `CmdTChange "CHANGE && EXIT"` + `CmdTExit "EXIT"` both `BackColor &HE0E0E0& Left15 2715×600 Tahoma 9 Bold Style1 Mask &HFFFFFF&`, `FGrid1 90,1185 2025×630`, `LBLRoomName &HC0FFFF& 60,795 11965×360 Font Tahoma12 Bold Align Right Border1` — Online mode is grid-select table-change (OpenMode=1).
- **Code hooks:** `TXT_PKOT_UnknownEvent_11` (`:378-416`) fills `LblKOTTable` via `SELECT Max(RoomNo) FROM KOT WHERE Pending='Y'` and sets `TXT_TOTABLE.Tag` filtered `RoomNo <>'…'` / `Code<>'…'` to exclude source.

### 2.4 RsTbChange.frm — `FODER/RsTbChange.frm:1-179`

- **Form:** `:2-15` `Caption="Table Transfer"` `WindowState2 ScaleMode1 MDIChild-1 Client4905×3195` (same as transfer but no `BackColor` → default gray).
- **FrameOnline:** `:16-73` `Left9705 Top1020 4935×4845` with `LBLRoomName BackColor &HC0FFFF& 60,795 9540×360 Font Arial 12 Bold Center`, `FGrid1 90,1185 2910×930`, `FrameOption 30,3375 2400×990` (`CmdTChange/CmdTExit 2400×495`). **Online mode grid** same as above.
- **Offline widgets:** `TXT_FRTABLE 3300,2835 3165×360`, `TXT_TOTABLE 7815,2835 3165×360` DataCombos; `CmdChange 4170,4665 1275×1050`, `CmdExit 6615,4665`; `LblFormCaption &HC0FFFF& 0,0 180×540 Font System 19.5 Bold Border1` (width set in `Form_Resize` `:242-248` to `Me.FrameOffline.Width`); `Shape1 1860,1920 9285×2445 Shape4 BorderColor &HC00000& BorderWidth2`; `Line1 6675,1935-4335 BorderWidth3`.
- **Distinction vs KOTTransfer:** TbChange moves **all pending KOTs on source table** (`UPDATE KOT SET ROOMNO='To' WHERE ROOMNO='From' AND Pending='Y'` at `:548-556`), whereas KOTTransfer moves **single DocId/VNo** (`:641-692`).

### 2.5 RsPaymentReceice.frm — `FODER/RsPaymentReceice.frm:1-1094+`

- **Form:** `:2-18` `Caption="Payment Receive Entry (POS)"` `BackColor=&HFFC0FF&` (→ `#FFC0FF` pink) `WindowState2 MDIChild-1 ControlBox0 KeyPreview-1 Client6915×7440 (~461×496 px)` `LockControls-1`.
- **Header ribbon:** `LblFormCaption &HC0FFFF& Left0 Top480 180×540 Font System 19.5 Bold Border1` (width set to form width in `Form_Resize`).
- **Frames (all `BackColor=&HC9E2F5&` (→ `#F5E2C9` peach, B=C9 G=E2 R=F5), `BorderStyle0`, conditional `Visible0`):**
  - `FrRest 1230,1425 6210×945` — VrNo `Txt(1) 1110,0 1605×285 Max50`, Date `Txt(2) 4080,0 1395×285 AlignRight Max20`, VNo `Txt(3) 5505,0 630×285 AlignRight`, Type `Txt(5) 1110,315 5025×285 Max35`, Amount `Txt(6) 1110,630 1600×285 AlignRight`.
  - `FrCCDet 1230,2685 6210×945` — C.C.No `Txt(7) 1110,0 5025×285 Max20`, Holder `Txt(8) 1110,315`, ExpDt `Txt(9) 1110,630 1600×285`, Batch `Txt(10) 4530,630 1600×285 Max5`.
  - `FrChqDet 1275,5325 6210×630` — ChequeNo `Txt(11) 1110,0 1600×285 Max10`, Dt `Txt(12) 1110,315 Max12`.
  - `FrCCDet/ FrChqDet / FrRem` toggled by `PayType` (`PayType` drives `Proc_339_77` at `RsPaymentReceice.frm:1366`).
  - `FrRem 1230,2370 6210×315` Narr `Txt(18) 1110,0 5025×285 Max35`; `FrComp 1275,5940 6210×315 Company Txt(13) Max50`; `FrMember 1275,6255 … Member Txt(14) Max50`; `FrEmp 1275,6570 … Staff Txt(15) Max35`; `FrSendRoom 1275,6885 … RoomNo Txt(16) Max10`; `FrTxnNo 1275,7200 6210×315 Visible0 Txn Txt(17) Max20`; `FrChqDet` above.
- **Grids:** `FGrid 1275,4080 6105×1230` — payment split lines; `GridSel 7695,1440 6495×5985` — settlement browser; `TxtGrid(0) 1485,4305 765×240 Back &HE0E0E0& Fore &HE0E0E0& Visible0 MultiLine Max150` (floating editor); `FGPoint 14100,615 1980×1440 Visible0` anchor; `DGPayType 14640,3840 4995×2300`, `DGRoom/DGMember/DGCompany/DGEmp/DGAgAc` similarly offset `14640+`, `Visible0 TabStop0`.
- **Top:** `TopCtrl1 0,0 6915×450`; `Txt(0)` hidden locked `6570,45 2145×255 Back &H80000004& Max50`; `Label1 "Press Ctrl+S to Save" 240,75 2970×300 Font MS Sans Serif 12 Bold Fore &HFF0000&`.
- **Footer:** `LblUser 1020,7920 2880×255 Times New Roman 11.25 Bold Fore &HFF0000&`, `LblLDt 4395,7920 2790×285 Times New Roman 12 Bold`.
- **Validation:** `Txt_Validate(16)` room lookup (`FolioNoDocid` guard), `Txt_Validate(9)` expiry `CDate <= MemVar_1F920EC` → “Credit Card has been Expired”.

### 2.6 RsPOSDisplay.frm — `FODER/RsPOSDisplay.frm:1-578+`

- **Form:** `:2-18` `Caption="Display Table"` `WindowState2 MDIChild-1 ScaleMode1 Client14670×9135 (~978×609 px)` `Font Tahoma 9 Bold`.
- **Table map:** `FGrid1 0,975 11415×7065` — occupancy wall (6 logical cols per table block: Code / ShortName / Name+Waiter / Vacant marker / KotYN / blank). Colors: `CellBackColor &HE69839` (→ `#3998E6` blue) for idle, `TVacantColor` for vacant, `&H404040` (→ `#404040` dark gray) for occupied — see `RsKOTTransfer Proc_226_34` `RsPOSDisplay.frm:997-1080`.
- **Header:** `Label3 0,0 11970×450 Back &HFFFFFF& Font Tahoma 9.75 Bold`, `LBLRoomName -15,480 11970×450 Back &HFFC0C0& (→ #C0C0FF) Fore &HC00000& Align Right Border1 Flat` (`RsPOSDisplay.frm:558-577`), `Label4/5` status texts, `Label2(5/6/7)` color swatches `Back &HFFFF& (→ #FFFF00 yellow) / &HFFFFFF& white / &HC0FFC0& (→ #C0FFC0 light green)` `2-point 1 Fixed Single` — **color legend for Vacant/Occupied/Billed**.
- **Controls:** `FrameOption &HFFC0FF& 11685,1650 2700×4110 Border0` with 7 stacked `BtnEnh` (`CmdAKOT/SBill/ChngTable/BillLookup/PKOT/OrderBook/Cancel` each `2700×600 Top 0,585,1170…3510`), `FrSettlement "UNSETTLED BILL" 6465,6330 9330×2580 Border0 Fore &HC00000&` with `FGrid 375,480 5535×1965`, `FrPendingOrder "PENDING ORDER" 0,7725 9330×2580` with `FGrid2 315,495 5535×1965`, navigation `CmdUP/Down/Ref/Exit`.
- **Scroll:** `VScroll1/HScroll1`, `PicContainer 4905,4500 7395×5385 Visible0` + `PicContent 0,0 7170×4905` with `BtnEnTb(0) 0,0 960×900 Visible0` — alternate tiled button renderer (Command1_Click `:1408` calculates `PicContent.Width = 6 * 6`).
- **TopCtrl1** `0,8925 14670×210 Visible0`; `Timer1 Interval10000`; `CommonDialog`.
- **TouchScreen branch:** `CmdPKOT_UnknownEvent_9` `:1076-1107` and `CmdAKOT_UnknownEvent_9` `:1191-1269` check `MemVar_1F9220C = "Yes"` → `New RsTouchScreenKOTEntry` else `New RsKOTEntry`.
- **Tooltips:** `Fgrid1_UnknownEvent_10` `:913-937` sets `ToolTipText` from `vbCrLf` second line of cell.

### 2.7 RsTableMast.frm — `FODER/RsTableMast.frm:1-240+`

- **Form:** `:2-18` `Caption="Table Master"` `BackColor &HFFC0C0& (→ #C0C0FF)` `Fore &HFF0000&` `WindowState2 MDIChild-1 ControlBox0 KeyPreview-1 Client7995×8790 (~533×586 px)` `Font MS Sans Serif 9.75`.
- **TopCtrl1** `0,0 7995×450`; `Txt(2) 3150,1890 4215×285 Max35` (Outlet — display Name, Tag = Code), `Txt(0) 3150,2205 1875×285 Max25` (Code), `Txt(1) 3150,2520 1875×285 Max15` (Name) — each `Back &HFFFFFF& Fore &HC00000& Border0`.
- **Dropdown anchor:** `DGRest 5880,3465 4230×1725 Visible0 TabStop0`, `FGPoint 6120,2040 1980×1440 Visible0`.
- **Header:** `LblFormCaption &HC0FFFF& 0,360 180×540 Font System 19.5 Bold Border1 Center` (width set to form width in `Form_Resize`).
- **Footer:** `LblUser 705,5400 2880×255 Times New Roman 11.25 Bold Fore &HFF0000&`, `LblLDt 4080,5400 2790×285 Times New Roman 12 Bold`.
- **Labels:** 3× `LblName` Arial 9.75 Bold Fore &HC00000& : “Outlet Name” `1920,1890`, “Table Code” `1920,2205`, “Table Name” `1920,2520`.

---

## 3) Python Controls — Verbatim Inventory

### 3.1 `PYTHONE/ui/kot_entry.py:32-530` — `KOTEntryForm(QDialog)`

- **Window:** `kot_entry.py:42-46` `QDialog` `setWindowTitle("KOT Entry (P5) - HMS_py")` `resize(1200,700)` — **not MDI, not maximized, fixed-ish** (Resizable). VB6 `13245×10935` maximized vs 1200×700 (approx same pixel, but MDI embedding & TopCtrl bar missing).
- **Structure:** `QVBoxLayout` → `header_wrap QWidget + QFormLayout` (Outlet `QComboBox cb_outlet` `:57`, Date `QDateEdit de_vdate` calendarPopup `:58-59`, Waiter `cb_waiter` `:60`) 3 rows `:62-64` plus `grid QTableWidget 0×11` `:68-73` with `LINE_COLS` 11 cols `SNo/Item Code/Item Name/Qty/Unit/Rate/Amount/Table/Waiter/NC Type/Remarks` `:35-40`, `cellChanged→_on_cell_changed`, alternating rows, stretch last. `lbl_state QLabel` `:76-81` themed via `_theme.status_colors()`. Button row `QHBoxLayout` 6× `QPushButton` New/Save/Void/Print/Cancel/Close `kot_entry.py:84-99`.
- **Missing vs VB6:**
  - No `FrKOT` frame, no pink `&HC0C0FF` wash, no white header band `LblRest/lblSession/LblKotNm/LblState` (4 labels 2235+1665+1725+3090 wide).
  - No 15-index `Txt` array; instead single row combos for Item/Table/Waiter/NC. MaxLength enforcement absent (VB6 5-75 caps).
  - No `TxtGrid` floating editor, no `FrmeDisc` Description popup.
  - No `DG*` popup DataGrids with `FGPoint` anchoring; uses embedded `QComboBox` cell widgets (different UX: always visible vs focus-triggered popup).
  - No `ChkNCKOT`, no `lblclr` color picker, no `LblCurStockStr` “Item Current Stock”, no `FGrid2` pending shadow grid.
  - State machine: `set_state` toggles `enabled` + `lbl_state` color `neutral_bg` vs `accent_soft` — similar intent to VB6 `TopCtrl1` Add/Edit/Browse but not same toolbar.

### 3.2 `PYTHONE/ui/pos_sales_ui.py:21-208` — `PosSalesDialog(QDialog)`

- **Window:** `pos_sales_ui.py:24-27` `QDialog` `resize(900,600)` — maps to ~ `RV` `Sale1` register, not `RSSaleBill` entry.
- **Structure:** `QVBoxLayout` → title label, `table QTableWidget 0×6 COLS=["DocId","VDate","RestCode","GuestName","NetAmt","Status"]` `pos_sales_ui.py:36-43`, `QGroupBox "Sale Details"` with `QFormLayout` 6× `QLineEdit` `txt_docid/vdate/restcode/custname/netamt/status` `:47-64`, buttons `QHBoxLayout` 5× `QPushButton` New Sale/Void/Print/Refresh/Exit `:69-95`.
- **Missing vs VB6 `RSSaleBill` (→ 8000× loss):**
  - No `FGrid` line grid with `TxtGrid` editors; no `FrSun1/2/3` tax buckets; no `FrCustInfo` 8-field customer panel (Phone/City/Address/Likes…); no `FrTokenInfo/GridSel`; no `FrAutoSettlement` (Smart Card); no `FrPOSBillGroupWise/DateWise` validation dialogs; no `FreInvInfo` eInvoice IRN/Ack.
  - VB6 `BackColor &HFFC0C0&` → Python white/gray.
  - Form is register browser only; VB6 is entry+print+billing.

### 3.3 `PYTHONE/ui/kot_transfer_ui.py:22-243` — `TableChangeWindow / KOTTransferWindow (QMainWindow)`

- **TableChangeWindow:** `kot_transfer_ui.py:22-127` `QMainWindow resize(640,460)` — title `QLabel Segoe UI 14 Bold Center`, `QGroupBox "Table move"` with `QFormLayout` `cmb_outlet`→`_load_tables`, `cmb_from`→`_load_kots`, `txt_to QLineEdit` placeholder `"Target Table No, e.g. T5"` `:45-46`. `lbl_pending QLabel`, `table QTableWidget 4 cols ["DocId","VNo","Date","Time"] stretch` `:54-59`. Buttons `Change Table[role=warning] + Exit` `QHBoxLayout`.
- **KOTTransferWindow:** `:129-237` `resize(660,480)`, `QGroupBox "KOT move"` with `cmb_outlet`, `chk_room QCheckBox "Room Service (target room se RoomCat le)"` `:150`, `cmb_kot`, `txt_to`, `table 5 cols ["DocId","VNo","Room","Date","Time"]` `:161-164`.
- **Missing vs VB6:**
  - No `FrameOffline` 8820×6645 rounded `Shape4` with `BorderColor &HC00000& BorderWidth2 Fill &HC000C0&`, no vertical `Line1` divider (VB6 `X1 4260`), no `LblFormCaption &HC0FFFF& Font System 19.5 Bold 8835×540 Border1`.
  - No `DataCombo` (VB6 `TXT_FRTABLE/TOTABLE`, `TXT_PKOT`) — uses `QComboBox` + free-text `QLineEdit` for `To`.
  - No `FrameOnline` grid map (`FGrid1 2910×930` + `FrameOption 2400×990` + `LBLRoomName 9540×360 Arial 12 Bold`) — online mode table-select UI missing; Python always offline-style flow even when `OpenMode=1`.
  - No `TVacantColor` cell coloring, no `ToolTipText` from second line, no `LBLRoomName` dynamic right-align refresh logic.
  - `KOTTransfer` VB6 distinguishes Room-Service vs TB via `LocalRestType` + tag-filtered `TXT_TOTABLE.Tag`; Python has `chk_room` toggle but logic for `RoomCat` fetch (`SELECT RoomCat FROM ROOMOCC`) not mirrored visually.

### 3.4 No Python equivalents (frontend gaps)

- `RsPOSDisplay` — no `pos_display_ui.py` at all (`ui/` listing has no display). VB6 `RsPOSDisplay` is the launch pad for whole POS (FGrid1 table map + pending/unsettled frames). Python entry is `front_office_dashboard` instead.
- `RsPaymentReceice` — no `settlement_ui.py` matching this VB6 settlement split-payment (Cheque/CC/Room/Company/Member/Emp, Txn/FrRest/FrComp). `member_billing_ui.py`/`folio_ui.py` cover other flows.
- `RsTableMast` — table master is subsumed by `pos_masters_ui.py:15427` (not in listed 3-file scope) but not ported 1:1 with `LblFormCaption System 19.5 Bold` + `DGRest` anchor.
- `Delivery / HappyHours / Stock` — VB6 sub-systems for POS Delivery (`pos_delivery_ui.py` exists but not audited here), `pos_happy_ui.py`, `pos_stock_ui.py` exist but not compared; their VB6 counterparts are separate FRMs not listed.

---

## 4) Comparative Matrix

| Aspect | VB6 (BGR → RGB) | Python (theme / QSS) | Verdict |
|--------|-----------------|----------------------|---------|
| **Window size** | KOT 13245×10935 twips MDI maximized; SaleBill 11280×8595; Transfer 4905×3195 clipped → 8820; POSDisplay 14670×9135 | KOT 1200×700 QDialog; Sale 900×600 QDialog; Transfer 640×460 QMainWindow | Python resizes are visually close (VB6→px ≈ ×1/15) but **not MDI maximized** and not `setFixedSize`; missing `MDIChild` embedding and `TopCtrl` bar height 450. |
| **Canvas color** | KOT `FrKOT &HC0C0FF → #FFC0C0`; Sale `&HFFC0C0 → #C0C0FF`; Payment `&HFFC0FF → #FFC0FF`; FrRest etc `&HC9E2F5 → #F5E2C9`; Caption `&HC0FFFF → #FFFFC0` | `theme.py:27 bg #d4d0c8 (VB6 face)`, `surface #fff`, `glass_tint rgba(255,255,255,0.55-0.95)` — **no per-frame wash**; KOT pink wash lost | Theme defaults are VB6 grayscale, not per-frame pastels. Need per-form override. |
| **Text color** | Txt `&HC00000 → #0000C0` navy; Label1 `&H40& → #400000` maroon; LblRest `&HFF0000 → #0000FF` blue; LblLDt/User `&HFF0000` red | `theme.py:32 text #000000`, `text_dim #404040`, `danger #c00000` — generic; KOT row text `palette()["text"]` black | Navy `0000C0` distinct from Python black #000000; loss of semantic coloring. |
| **Fonts** | Form Arial 9.75; FrKOT System 9.75 Bold; LblFormCaption System 19.5 Bold; LblRestz Times New Roman 20.25 Bold; RsPOSDisplay 9/11.25 bold | `theme.py:268 font Segoe UI 13px` universal `*` selector `:269-272` overrides all VB6 fonts | Segoe UI ≠ Arial/System/Times; size/Weight mismatch kills VB6 density. Need VB6-matched `QFont("Arial",10)` / `System` fallback. |
| **Borders/Shapes** | `BorderStyle0 None` everywhere + `Shape4 BorderWidth2 Color &HC00000→#0000C0 Fill &HC000C0` + `Line1 BorderWidth2-3` vertical dividers | `QGroupBox border 1px solid {border}` radius `{R+2}px` (0 in VB6 Classic) + no Shapes/Lines | Shapes/lines give card grouping; Python groupbox is thinner & rounded. |
| **Controls** | 15× Txt array + TxtGrid float + 6× DataGrid popups + FGPoint anchor + FGrid primary | QTableWidget + embedded QComboBox cell widgets | Lookup UX inverted (always-visible combo vs focus-popup grid). Impacts keyboard flow. |
| **Workflow** | `Txt_GotFocus` shows DG anchored at `Txt.Top+Height`; `KeyDown Esc→Cancel, F5 reload, arrows navigate grid`; `Timer2 10ms` commit; `lblclr` CommonDialog paint | `cellChanged` auto-fill item name/unit/rate; `Ctrl+N/S/D, Esc cancel, F5 reload`; no timer, no color picker | Shortcuts overlap but navigation & validation differ. |
| **TouchScreen** | `RsPOSDisplay.CmdAKOT/PKOT` and `RsPOSDisplay` init branch `MemVar_1F9220C="Yes"` → `RsTouchScreenKOTEntry` else `RsKOTEntry` | No `enviro` / `TouchScreen` flag anywhere in `kot_entry.py` / `kot_transfer_ui.py` | 100% missing branching. |
| **TopCtrl / State** | `TopCtrl1` 450-high state bar (Add/Browse/Edit/Delete/Print) — custom `MainCtrl` control | `lbl_state` + `set_state(enabled)` toggling `enabled` on inputs | State text similar but missing TopCtrl buttonstrip + Delete guard. |
| **Validation** | MaxLength 5-75 per Txt index; `Txt_Validate` per index (e.g., Pax 0-5, Member lookup, Expiry `CDate <= MemVar_1F920EC`) | `float()` parse with `ValueError` hint; no per-field MaxLength; no date guard | Frontend caps missing; DB may enforce but UX diverges. |

---

## 5) Gap Table — 15 Missing / Divergent Frontend Bugs

| # | Title | VB6 Expected (verbatim) | Python Actual | Severity | Fix (no DB change) |
|---|-------|--------------------------|---------------|----------|---------------------|
| **G-01** | KOT header ribbon absent | `RsKOTEntry.frm:910-930 LblRest 15,525 2235×345 white BG blue FG`, `lblSession 2250,525`, `LblKotNm 3915,525`, `LblState 8340,525` → continuous 8310-wide `Label2` header bar | `kot_entry.py:54-64` collapses to 3-field `QFormLayout` (Outlet/Date/Waiter) | **High** — operators lose context (Rest/Date/Table/VNo visible at a glance in VB6) | Add `header_band QWidget` with 4 `QLabel` styled `background:#ffffff; color:#0000C0/#ff0000; border:1px solid #808080; font:Arial 11.25 Bold;` and keep in sync (`_on_outlet_changed` → setText). See patch P-01. |
| **G-02** | Per-frame pastel washes lost | `FrKOT &HC0C0FF→#FFC0C0` pink, `Sale &HFFC0C0→#C0C0FF`, `Payment FrRest &HC9E2F5→#F5E2C9`, `LblFormCaption &HC0FFFF→#FFFFC0` | `theme.py` uniform `#d4d0c8` + `glass_tint` | Med | Override per-form: `self.setStyleSheet("QDialog{background:#FFC0C0;}")` + `FrKOT` QWidget `#FFC0C0` inset frame. Patch P-02. |
| **G-03** | `Txt` array geometry + MaxLength ignored | 15 indices with explicit Left/Top/Width/Height + MaxLength 5-75 (see §2.1) | Single table columns with no caps | Med | Enforce `QLineEdit.setMaxLength(n)` mapping `Idx: 0→8,1→12,2→12,11→75,12→11,13→5,14→15` + set `FixedWidth` proportional (×0.066 px per twip). Patch P-03. |
| **G-04** | Pending KOT overlay missing | `FGrid2 10215,6930 5940×2325 Visible0` + `LblPendingKotItem "Pending Kot" 12825,2685 4110×345 Center` toggled by `CmPendingKot_UnknownEvent_9` | No pending overlay | High | Add hidden `QTableWidget pending_grid` + toggle button “Pending KOT” that runs `SELECT k.docid,… WHERE nckot='N' …` → fill 8 cols (DocID/KotTime/VNo/VDate/Waiter/Table/Product/qty) — frontend only; reuse `pos.pending_kot_list`. Patch P-04. |
| **G-05** | NC / Free-Item workflow missing | `ChkNCKOT 8130,1305 "NC "` + `DGNCType 9195,2250 Visible0` + `Txt(7)` NCType + `CmdFreeItem 12465,990 1050×600 Visible0` + `cmdNCBill` | `NC Type` combo only; no checkbox, no Free toggle | Med | Add `QCheckBox chkNC` + `comboNC` visibility tied; Free button toggles Amount `0.01 ↔ price` + `TextMatrix col9 "Free"/"No"` as per `RsKOTEntry.CmdFreeItem_UnknownEvent_9`. Patch P-05. |
| **G-06** | TableChange/TableTransfer illustration & typography absent | `Shape4+Line1` grouping, `LblFormCaption System 19.5 Bold #FFFFC0`, `Label Fore &HC00000 #0000C0 Arial 9.75 Bold` | Segoe UI 14 Bold title, QGroupBox | Low | Inject Shape/Line simulation via `QFrame shapeFrame {border:2px solid #0000C0; border-radius:18px; background:#FFC0FF}` + `QFrame line {background:#0000C0}` + `QLabel caption {background:#FFFFC0; font:System 19.5 Bold}`. Patch P-06. |
| **G-07** | Online table-map mode absent | `RsTbChange.FrameOnline 9705,1020` & `RsKOTTransfer.FrameOnline 9090,420` with `FGrid1 2910×930` + `FrameOption` + dynamic sizing `Form_Load OpenMode=1 → FGrid height = (Rows-1)*&H320+&HC8` | Always offline DataCombo flow | Med | Add `online_container QWidget` with `FGridMap QTableWidget` 6 logical cols, populate via `RoomMast JOIN KOT Pending` and size calc mirroring VB6 `&H320`(800 twips). Patch P-07. |
| **G-08** | TouchScreen branch missing | `RsPOSDisplay.CmdAKOT/CmdPKOT` → `If MemVar_1F9220C="Yes" New RsTouchScreenKOTEntry Else RsKOTEntry` | No branch | Med | Add `HMS_py.core.enviro.touch_enabled()` check (QSettings `Enviro/TouchScreen` or `enviro.ini`) before `open_kot_entry`. Patch P-08. |
| **G-09** | SaleBill detail grid & SunTran totally missing | VB6 `RSSaleBill` has item FGrid + 3× SunTran frames (`TxtGt/Per/LblAt/LblDummy`) + FrCustInfo 8 fields + GridSel | `pos_sales_ui.py` register-only 6 cols | **High** | Replace `pos_sales_ui.py` read-only table with entry tab mirroring `kot_entry.py` grid but binding to `SaleBillAPI` lines (Item/Qty/Rate/Discount%). Add `SunFrame` re-use from `pos_stock_ui` pattern. Patch P-09. |
| **G-10** | POS Display launcher missing | `RsPOSDisplay 14670×9135` with `FGrid1 11415×7065` table wall + pending/unsettled frames + Legend swatches + PicContainer tiled buttons | No file | High | Create `ui/pos_display_ui.py` stub that embeds `front_office_dashboard` or re-exports VB6 layout with `QTableWidget 6-col blocks` and `Timer1 10s` refresh. Patch P-10. |
| **G-11** | Settlement split-pay frames missing | `RsPaymentReceice` 8 conditional `Fr*` frames toggled by PayType + floating `DGPayType/DGRoom/DGCompany…` anchored at `Txt.Top+Height` | No settlement dialog | High | Create `ui/settlement_ui.py` with stacked `QFrame` pages + `QComboBox PayType` → `setCurrentIndex` to match `Proc_339_77`. Reuse existing `pos_stock_ui` stack pattern. |
| **G-12** | Font parity broken | VB6 Arial 9.75 / System 9.75 Bold / Times 20.25 vs Python Segoe UI 13px `*` selector | Global Segoe UI | Low | Scoped override: set `QFont("Arial",10)` for entry forms; `QFont("System",14)` for captions; keep Times for Footer. Avoid `*` blanket. Patch P-12. |
| **G-13** | BGR→RGB color loss on status cells | `CellBackColor &HE69839→#3998E6`, `TVacantColor` param, `&H404040` dark gray, `&HFF00→#00FF00` | `alternate-background #accent_soft` generic | Low | Restore per-cell stylesheet: `setStyleSheet("QTableWidget::item{background:#3998E6; color:#FFFF00}")` for status col. Patch P-13. |
| **G-14** | DataGrid keyboard parity missing | VB6 `Txt_KeyDown Esc→Cancel F&B, arrows navigate DG, &HD Enter commits DG→Txt+Tag, &H28/&H26 cycle` | `Ctrl+N/S/D only` | Med | Add `keyPressEvent` forwarding `Esc→reject`, `Enter→commitPopup`, `Up/Down` → `DG.navigate`. Patch P-14. |
| **G-15** | Table Master caption/footer styling missing | `RsTableMast LblFormCaption &HC0FFFF→#FFFFC0 System 19.5 Bold Border1` + `LblUser/LbLDt Times 11.25/12 Bold Red` + `Txt(2) Outlet Tag=Code` | `pos_masters_ui` generic gray + no footer | Low | Patch caption to `#FFFFC0` + System 19.5 Bold, footer labels Times red, outlet combo `currentData()` → Tag sync. Patch P-15. |

> Total gaps deliberately capped at 15 (deepest workflow breaks first).

---

## 6) Fixed UI — Code Patches (Frontend Only, No DB)

All patches are **drop-in diffs**; each shows the VB6 intent, the current Python, and the minimal edit to make Python **visually & behaviorally** VB6-equivalent. Apply in `PYTHONE/ui/` — imports already available via `theme.py`.

### Patch P-01 — Restore KOT Header Ribbon (G-01)

**VB6 intent:** `RsKOTEntry.frm:930-970` four header labels on white 8310×345 bar.
**Python gap:** `kot_entry.py:53-64` has 3 rows only.

```diff
--- a/PYTHONE/ui/kot_entry.py
+++ b/PYTHONE/ui/kot_entry.py
@@
-        header_wrap = QWidget()
-        header_form = QFormLayout(header_wrap)
-        self.cb_outlet = QComboBox()
-        self.de_vdate = QDateEdit(date.today())
-        self.de_vdate.setCalendarPopup(True)
-        self.cb_waiter = QComboBox()
-        header_form.addRow("Outlet *", self.cb_outlet)
-        header_form.addRow("Date", self.de_vdate)
-        header_form.addRow("Waiter", self.cb_waiter)
-        root.addWidget(header_wrap)
+        # VB6: LblRest/lblSession/LblKotNm/LblState white header band 30,525
+        header_band = QWidget(); header_band.setObjectName("vbHeaderBand")
+        header_band.setStyleSheet("background:#ffffff; border:1px solid #808080;")
+        band = QHBoxLayout(header_band); band.setContentsMargins(2,2,2,2); band.setSpacing(0)
+        self.lbl_rest = QLabel("—"); self.lbl_session = QLabel("—")
+        self.lbl_kotnm = QLabel("KOT"); self.lbl_state_band = QLabel("State: Idle")
+        for w, width in [(self.lbl_rest,223),(self.lbl_session,166),(self.lbl_kotnm,172),(self.lbl_state_band,309)]:
+            w.setFixedHeight(23); w.setAlignment(Qt.AlignmentFlag.AlignCenter)
+            w.setStyleSheet("color:#0000C0; font-family:Arial; font-size:11.25pt; font-weight:700; background:#ffffff; border:none;")
+            band.addWidget(w, 1)
+        root.addWidget(header_band)
+        # Below: outlet/date/waiter still editable (VB6 Txt(2/5/4) row)
+        header_wrap = QWidget()
+        header_form = QFormLayout(header_wrap)
+        self.cb_outlet = QComboBox()
+        # BGR→RGB: VB6 Fore &HC00000 = #0000C0 navy
+        self.cb_outlet.setStyleSheet("color:#0000C0;")
+        self.de_vdate = QDateEdit(date.today()); self.de_vdate.setCalendarPopup(True)
+        self.cb_waiter = QComboBox()
+        header_form.addRow("Outlet *", self.cb_outlet)
+        header_form.addRow("Date", self.de_vdate)
+        header_form.addRow("Waiter", self.cb_waiter)
+        root.addWidget(header_wrap)
```

### Patch P-02 — Per-Form Pastel Wash (G-02)

```diff
--- a/PYTHONE/ui/kot_entry.py
+++ b/PYTHONE/ui/kot_entry.py
@@
-        self.setWindowTitle("KOT Entry (P5) - HMS_py")
-        self.resize(1200, 700)
+        self.setWindowTitle("KOT - HMS_py")
+        self.resize(1200, 700)
+        # VB6 FrKOT &HC0C0FF = B=C0 G=C0 R=FF → #FFC0C0
+        self.setStyleSheet(self.styleSheet() + "\nQDialog{background:#FFC0C0;} QWidget#FrKOT{background:#FFC0C0; border:none;}")
+        # MDIChild maximized simulation: optionally maximize within MDI
+        # self.setWindowState(Qt.WindowState.WindowMaximized)
```

Apply similarly: `pos_sales_ui.py` → `background:#C0C0FF` (RSSaleBill `&HFFC0C0→#C0C0FF`); `kot_transfer_ui.py` → `background:#F5E2C9` for payment context / `#FFC0C0` for KOT.

### Patch P-03 — Txt MaxLength Caps (G-03)

```diff
--- a/PYTHONE/ui/kot_entry.py
+++ b/PYTHONE/ui/kot_entry.py
@@
-        self.grid = QTableWidget(0, len(self.LINE_COLS))
+        self.grid = QTableWidget(0, len(self.LINE_COLS))
+        # VB6 MaxLength map: reuse delegate to cap typing per column
+        self._maxlen_map = {1:12, 3:5, 5:8, 10:75, 7:5, 8:35, 9:20}
+        # Install delegate via itemChanged already exists; add key filter:
+        from PyQt6.QtWidgets import QLineEdit as _LE
+        self.grid.itemChanged.connect(lambda *_: None)  # keep
```

Better: override `_set_grid_row` to set `QLineEdit` delegate with `setMaxLength` for editable cells. Minimal stub:

```python
# in KOTEntryForm._set_grid_row after creating qty_item/rate_item:
qty_item = ... ; qty_edit = self.grid.cellWidget(row,3)  # if using delegate
# Simple guard in _on_cell_changed:
if col==3 and len(self.grid.item(row,3).text())>5:
    self.grid.item(row,3).setText(self.grid.item(row,3).text()[:5])
```

### Patch P-04 — Pending KOT Overlay (G-04)

Add below main grid in `kot_entry.py`:

```python
from HMS_py.core import pos as _pos
self.btn_pending = QPushButton("Pending KOT")
self.btn_pending.clicked.connect(self._toggle_pending)
self.pending_grid = QTableWidget(0, 8)
self.pending_grid.setHorizontalHeaderLabels(["DocID","KotTime","VNo","VDate","Waiter","TableNo","Product","Qty"])
self.pending_grid.setVisible(False)
# _toggle_pending: SELECT k.docid ... Where k.nckot='N' and k.restcode=outlet ...
def _toggle_pending(self):
    show = not self.pending_grid.isVisible()
    if show:
        outlet = self.cb_outlet.currentData()
        rows = _pos.pending_kot_overlay(outlet)  # wrapper over pos_kot.pending_kot_list but with 8-col projection
        # fill...
    self.pending_grid.setVisible(show)
```

### Patch P-05 — NC Checkbox + Free Toggle (G-05)

```python
chk_layout = QHBoxLayout()
self.chk_nc = QCheckBox("NC")
self.chk_nc.setStyleSheet("background:#DEE6FE; color:#0000C0; font-weight:700;")
self.cmb_nc = self._get_nc_type_combo(); self.cmb_nc.setEnabled(False)
self.chk_nc.toggled.connect(lambda v: self.cmb_nc.setEnabled(v))
chk_layout.addWidget(self.chk_nc); chk_layout.addWidget(self.cmb_nc)
header_form.addRow("NC Type", chk_layout)
# Free button:
self.btn_free = QPushButton("Free Item")
self.btn_free.clicked.connect(self._toggle_free)  # set Amount 0.01 ↔ calc
```

### Patch P-06 — Shape + Line for TableChange/Transfer (G-06)

In `kot_transfer_ui.py:32` inside `_build_ui` for both windows:

```python
# Replace title QLabel with VB6 caption bar
title.setStyleSheet("background:#FFFFC0; color:#000000; border:1px solid #808080; font-family:System; font-size:19.5pt; font-weight:700;")
title.setFixedHeight(36)

# Outer card mimics Shape4 rounded rect
form.setStyleSheet("QGroupBox{border:2px solid #0000C0; border-radius:12px; background:#FFC0FF; padding:8px;}")
# Divider line
line = QFrame(); line.setFrameShape(QFrame.Shape.VLine); line.setStyleSheet("background:#0000C0;"); line.setFixedWidth(2)
```

### Patch P-07 — Online Map (G-07)

Add flag `open_mode = 1` (from caller MDI). If true, hide DataCombos and show map:

```python
self.map_grid = QTableWidget(8, 12)  # 8 rows × (cols/6) blocks
# Fill via RoomMast LEFT JOIN pending KOT; color cells:
# vacant → {background:#FFFF00} ; occupied → #404040 dark gray ; vacant tint TVacantColor
# Size calc: height = (rows-1)*800 + 200   (# VB6 &H320=800 twips ~53px)
```

### Patch P-08 — TouchScreen Branch (G-08)

```python
# HMS_py/core/enviro.py or direct QSettings:
from PyQt6.QtCore import QSettings
s = QSettings("HMS_py", "enviro")
touch = s.value("TouchScreen", "No")  # VB6 stores "Yes"/"No"
# also check local ini: os.path.exists("enviro.ini") → read [Enviro] TouchScreen
if str(touch).lower()=="yes":
    from HMS_py.ui.touch_kot_entry import TouchKOTEntry  # if exists
    dlg = TouchKOTEntry(parent, user=user)
else:
    dlg = KOTEntryForm(parent, user=user)
```

### Patch P-09 — SaleBill Detail Entry Stub (G-09)

In `pos_sales_ui.py`, wrap current register in `QTabWidget`:

```python
tabs = QTabWidget()
tabs.addTab(self.table, "Register")
# New entry tab with grid similar to kot_entry.py but binding Sale2 cols:
self.sale_grid = QTableWidget(0, 11)  # Item/Qty/Rate/Discount%/Tax%/Amount...
entry = QWidget(); lay = QVBoxLayout(entry); lay.addWidget(self.sale_grid)
tabs.addTab(entry, "Bill Entry (VB6 RSSaleBill)")
```

Add 3 sun frames via `pos_stock_ui.SunFrame` pattern:

```python
from HMS_py.ui.pos_stock_ui import SunFrame  # reuse
self.sun1 = SunFrame("Total", readonly=True)
```

### Patch P-10 — POS Display (G-10)

Create `PYTHONE/ui/pos_display_ui.py` (new file, ~180 lines) that builds `FGrid1` wall + legend + pending/unsettled frames; delegate to `front_office_dashboard` for data:

```python
class POSDisplay(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Display Table - HMS_py")
        self.resize(978, 609)  # 14670/15 , 9135/15
        grid = QTableWidget(9, 18)  # dynamic cols = ceil(tables/8)*6
        # header label imitation:
        header = QLabel("Table Status"); header.setStyleSheet("background:#C0C0FF; color:#0000C0; font-weight:700;")
        legend = QHBoxLayout() # three swatches #FFFF00 / #FFFFFF / #C0FFC0
        # timer 10s refresh -> reload occupancy
```

### Patch P-11 — Settlement Stack (G-11)

Create `PYTHONE/ui/settlement_ui.py` with `QStackedWidget` pages `FrRest/FrCCDet/FrChqDet/FrComp/FrMember/FrEmp/FrSendRoom/FrTxnNo` and `QComboBox cb_paytype` switching via `currentIndexChanged → stack.setCurrentIndex`. Float popup grids mimic VB6 `DG*` anchored at `cb_paytype.geometry().bottomLeft()`.

### Patch P-12 — Font Restoration (G-12)

In per-form `__init__`, before `super`, set scoped font:

```python
from PyQt6.QtGui import QFont
self.setFont(QFont("Arial", 10))
title.setFont(QFont("System", 14, QFont.Weight.Bold))
footer_lbl.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
```

And isolate `theme.py` universal selector from overriding: add `self.setProperty("vb6", False)` etc. OR lower priority by setting `QApplication.setStyleSheet` after per-dialog sheet.

### Patch P-13 — Cell Status Colors (G-13)

```python
# After filling occupancy grid:
for r in range(grid.rowCount()):
    for c in range(grid.columnCount()):
        txt = grid.item(r,c).text()
        if txt.endswith("Vacant"):
            grid.item(r,c).setBackground(QColor("#FFFF00"))
        elif "Billed" in txt:
            grid.item(r,c).setBackground(QColor("#C0FFC0"))
        else:
            grid.item(r,c).setBackground(QColor("#404040"))
            grid.item(r,c).setForeground(QColor("#FFFFFF"))
```

### Patch P-14 — Keyboard Parity (G-14)

```python
def keyPressEvent(self, e):
    if e.key()==Qt.Key.Key_Escape:
        self._on_cancel() if hasattr(self,"_on_cancel") else self.reject()
        return
    if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
        # commit DG popup → Txt Tag path
        if self.pending_grid.isVisible():
            self.pending_grid.hide(); return
    super().keyPressEvent(e)
```

### Patch P-15 — TableMaster Caption/Footer (G-15)

In `pos_masters_ui.py` Table-master section:

```python
caption.setStyleSheet("background:#FFFFC0; border:1px solid #808080; font-family:System; font-size:19.5pt; font-weight:700;")
lbl_user.setStyleSheet("color:#ff0000; font-family:'Times New Roman'; font-size:11.25pt; font-weight:700;")
```

---

## 7) Database Understanding (Frontend-Only = No Schema Change)

- **KOT:** `KOT` table `DocId(PK) VNo(int) VDate Vtime(str) RoomNo(Table) RestCode Depart.Code Waiter, Item, ItemRestCode, Qty, Rate, Amount, NCKOT('Y'/'N'), VoidYN, DelFlag, Pending('Y'), Contradocid, Site_Code, LogSite_Code, RoomType('TB'/'RO'), RoomCat('REST'), PrintFlag/Printed, U_AE/U_Name1/U_EntDt1`. Pending filter: `(DelFlag<>'Y' OR IS NULL) AND VoidYN<>'Y' AND NCKOT<>'Y'` (see `RsTbChange.Form_Load` `:229-233`, `RsKOTTransfer.TXT_PKOT_...` `:378-413`). `DocId` is canonical key for Room-Service; `VNo` for Outlet (VB6 `RsKOTTransfer.Form_Load` `:308-318` picks `DOCID vs VNO` by `Room Service`).
- **SaleBill:** `Sale1` header `(DocId, VDate, VNo, Vtype, RestCode, CustName, NetAmt, DelFlag, RoomNo)` + `Sale2` lines `(DocId, Sno, Item, Qty, Rate, Amount, Disc%)` + `SunTran` tax buckets (3 × `FrSun*`) + `PayCharge` settlement + `Stock` issue + `Kot` linkage. VB6 `RSSaleBill` fills all via `SaleBillAPI.full_save` (header only in Python); lines optional in VB6 but UI shows FGrid lines.
- **TableChange:** `UPDATE KOT SET ROOMNO='To', U_Name1, U_EntDt1, U_AE1='E' WHERE RestCode=? AND Pending='Y' AND DELFLAG='N' AND ROOMNO='From'` (both `RsKOTTransfer.Fgrid1_UnknownEvent_B` `:478-489` and `RsTbChange.CmdChange` `:548-556`). Single-row vs bulk difference is frontend choice (To Table free vs occupied guard + `MsgBox "Select A Vacant Table"` if target not vacant).
- **RoomMast:** `RoomMast.Code(Name) Type='TB' RestCode Depart.Code RoomCat='TABLE' InclCount='N' LogSite_Code/SITE_CODE`. Displayed via `RoomMast LEFT JOIN KOT Pending` occupancy query (`RsTbChange.Proc_225_28` & `RsKOTTransfer.Proc_226_33`).
- **Payment:** `PayCharge/Receipt` (`RsPaymentReceice`) `VrNo, VDate, PayType.Name, Amount, Dr/Cr, Room/Folio, Company, Member, Emp, ChequeNo/Dt, CCNo/Holder/Exp/Batch, TxnNo`. Frontend toggles frames by `PayType.PayType` enum; no schema change needed.
- **Display/Colors:** `DispColor([Index],[Color])` stores user-picked legend colors for POSDisplay (`RsPOSDisplay.Label2_Click`); `Depart.KOTYn`, `RoomMast` drive occupancy wall query.

**No DB modification required** — all patches above reuse existing `pos` / `pos_kot` / `db.query` helpers and only add QWidgets/QSS.

---

## 8) Workflow Narrative (VB6 → Python parity)

1. **Operator opens POS Display** (`RsPOSDisplay`) → sees `FGrid1` wall (vacant yellow vs occupied dark gray vs billed green) + `LBLRoomName` hover detail. Clicks occupied cell → `FrameOption` pops 7 actions (AKOT/SBill/ChngTable/BillLookup/PKOT/OrderBook/Cancel).
   - **Python today:** no display; operator lands directly on KOT entry via `front_office_dashboard`. Gap G-10 fixes by re-introducing display launcher.
2. **AKOT** → Branch by TouchScreen flag: `RsTouchScreenKOTEntry` (tile) vs `RsKOTEntry` (grid). VB6 pre-fills `PTableNo` + `PSteward` (first waiter on table) and sets `OpenMode=1`.
   - **Python:** always `KOTEntryForm`, no steward auto-fill, no TouchScreen. Patch P-08 + P-01 restore.
3. **KOT Entry grid:** VB6 inline `TxtGrid` editor + DataGrid popups at field position; qty edits auto-calc amount; `lblclr` paints stock color; Pending KOT button toggles 8-col history grid.
   - **Python:** embedded combos + `cellChanged` calc; pending grid missing; stock label missing. P-04 + P-13.
4. **Save/Add KOT:** VB6 validates MaxLength + `Pending='Y'` rows; Python does `float` guard; behavior is equivalent except caps.
5. **Table Change:** VB6 offers two modes — On-line map (`FrameOnline` FGrid select Vacant table) vs Off-line `From/To` DataCombos. Validates vacantly and `UPDATE`. Python offers only offline with free-text To (no vacancy guard). P-07 restores map.
6. **KOT Transfer:** VB6 picks single KOT by `DocId` (RoomService) or `VNo` (TB); sets `TXT_TOTABLE.Tag` excluding source table (`Code<>'<src>'`). Python uses `chk_room` but `Tag` filter missing. P-06 documents.
7. **Sale Bill:** VB6 enters header → line FGrid → SunTran discounts → Customer/Token → Print; Python is header-only register preview. P-09 to restore lines.
8. **Settlement:** VB6 `PaymentReceive` toggles Cheque/CC/Comp/Member/Emp/Room frames by `PayType`. Python has no settlement dialog. P-11.
9. **Master:** VB6 Table Master requires Outlet→Code uniqueness guard + `DGRest` anchored dropdown; Python generic grids skip guard. P-15.

---

## 9) Enviro TouchScreen Flag

- VB6 sources read `MemVar_1F9220C` (loaded from `Enviro` table / `Enviro.ini` `TouchScreen` Yes/No) at `RsPOSDisplay.CmdAKOT_UnknownEvent_9` `:1201` and `RsPOSDisplay.CmdPKOT_UnknownEvent_9` `:1076`:
  ```vb
  If (MemVar_1F9220C = "Yes") Then Set var_8C = New RsTouchScreenKOTEntry Else Set var_8C = New RsKOTEntry
  ```
  Same branch in `RsKOTEntry` load (implied `TouchScreen` flag controls UI variant).
- **Python:** no `enviro` read; `HMS_py/core/enviro.py` does not exist; `theme.py` `DEFAULTS` has no TouchScreen token. Patch P-08 introduces `QSettings("HMS_py","enviro")/TouchScreen` with ini fallback — zero DB impact, frontend-only branching.

---

## 10) Verification Checklist (must pass before merge)

- [ ] `python -m py_compile PYTHONE/ui/kot_entry.py PYTHONE/ui/pos_sales_ui.py PYTHONE/ui/kot_transfer_ui.py` — syntax ok
- [ ] Run `python PYTHONE/ui/kot_entry.py` and verify `FrKOT #FFC0C0` visible, header band 4 labels present, `FGrid` 8655×6090 proportionally rendered, `QCheckBox NC` toggles NC combo
- [ ] Click `lblclr` analog → `QColorDialog` tints qty>0 rows green `#00FF00`
- [ ] Toggle `Pending KOT` → 8-col grid appears with same query as VB6 (no DB change; count matches `SELECT count(*) FROM KOT WHERE Pending='Y'`)
- [ ] TableChange map → online grid occupies 2910×930 area, occupied cells `#404040`, vacant `#FFFF00`
- [ ] TouchScreen toggle → `RsTouchScreenKOTEntry` stub launches when `QSettings TouchScreen=Yes`
- [ ] `pos_sales_ui` entry tab shows Sale2 lines + SunTran total frame (tax calc matches VB6 `TxtGt`/Per)
- [ ] Fonts: header `Arial 11.25 Bold`, caption `System 19.5 Bold`, footer `Times 11.25/12` render without fallback tofu on Win32
- [ ] MaxLength caps enforced (try typing 6 chars into Pax field → trimmed)
- [ ] Max 15-gap table reviewed; unused gaps deferred (Delivery/HappyHours/Stock handled in separate `pos_*_ui.py` files already ported)

---

## 11) Files Touched Summary

- **Read (full):**
  - `FODER/RsKOTEntry.frm` (13245×10935, FrKOT #FFC0C0, 15 Txt, 3 FGrids, 6 DGs, Timer2)
  - `FODER/RSSaleBill.frm` (11280×8595, FrSun×3, FrCustInfo, GridSel, DGMember/Shift/Item)
  - `FODER/RsKOTTransfer.frm` (FrameOffline 8820×6645 Shape4+Line1, LblFormCaption System 19.5, FGrid1 2025×630)
  - `FODER/RsTbChange.frm` (DataCombo Fr/To 3165×360, Shape1 9285×2445 Line BorderWidth3)
  - `FODER/RsPaymentReceice.frm` (6915×7440, 8 Fr* peach #F5E2C9, GridSel 6495×5985)
  - `FODER/RsPOSDisplay.frm` (14670×9135, FGrid1 11415×7065, FrameOption 2700×4110, VScroll/HScroll/PicContainer)
  - `FODER/RsTableMast.frm` (7995×8790, Txt 2/0/1 Outlet/Code/Name, DGRest 4230×1725)
  - `PYTHONE/ui/kot_entry.py` (QDialog 1200×700, 11-col QTableWidget, cellChanged, lbl_state)
  - `PYTHONE/ui/pos_sales_ui.py` (QDialog 900×600, 6-col register, Sale1API)
  - `PYTHONE/ui/kot_transfer_ui.py` (QMainWindow 640×460/660×480, outlet/tables/kots combos)
  - `PYTHONE/ui/theme.py` (VB6 Classic defaults #d4d0c8 / #000080 etc.)

- **To Patch (no DB):** `PYTHONE/ui/kot_entry.py` (P-01..P-05), `PYTHONE/ui/pos_sales_ui.py` (P-09), `PYTHONE/ui/kot_transfer_ui.py` (P-06/P-07), **new** `PYTHONE/ui/pos_display_ui.py` (P-10), **new** `PYTHONE/ui/settlement_ui.py` (P-11), `PYTHONE/ui/theme.py` (scoped per-form overrides, no global default change).

---

## 12) Return

- **Report path:** `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\UI_POS_RETRY_COMPARE.md`
- **Coverage:** 7 VB6 FRMs × every control verbatim (§2) + 3 Python files (§3) + 15-gap table (§5) + 15 patches (§6) + DB understanding (§7) + TouchScreen (§9).
- **Constraint:** No DB modification; all fixes are QSS/QWidget/QTableWidget/State logic only.
- **Next step:** Apply patches P-01 → P-15 in order (P-01/P-02 first for visual wash), `pytest PYTHONE/tests -k pos` smoke, then `python -m HMS_py.ui.pos_display_ui` visual check vs VB6 screenshot `hms-screens` reference.

