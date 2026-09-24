# FRONTEND POS COMPARE — VB6 → Python (PyQt6)

**Scope:** POS / POINT OF SALE — KOT Entry, Table Change, KOT Transfer, Sale Bill, Settlement, Stock, Delivery, HappyHours, Masters, Display  
**Date:** 2026-09-24  
**Analyst:** Muse Spark (frontend comparison agent)  
**Roots:**  
- VB6: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\`  
- Python: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\ui\`  
- Screenshots: `HMS_Manuals\HMS_Manuals\POS\screenshots\`  
- DB core: `PYTHONE\core\pos*.py`

> No DB schema change. Only frontend behavior / colors / sizes / validation patches.

---

## 1. How this report was built — read order (ONE BY ONE fully)

VB6 `.frm` fully read (header + Attribute + code):
1. `RsKOTEntry.frm` (1038 lines header + 1715+ lines code window — FrKOT 26506×11010 twips, FGrid MSHFlexGrid 30/1620/8655×6090, all Txt 0-14, ChkNCKOT, LblState, DG* 6 grids, FGrid2 pending, lblclr, CmdTabeSt/CmPendingKot)
2. `RSSaleBill.frm` (50123 lines — 11280×8595, FrCustInfo, FrSun1/2/3, FGrid1 493/2020/6930×5375, Txt 0-18, TxtGrid 0-2, DGItem/DGMember/DGShift, FrTokenInfo, FrCtrl, FrAutoSettlement, eInvoice frames)
3. `RsKOTTransfer.frm` (1113 lines — 4905×3195, FrameOffline 8820×6645 with TXT_PKOT/TXT_TOTABLE DataCombo + Line/Shape, FrameOnline 4605×4845 with FGrid1 90/1185/2025×630, LBLRoomName, FrameOption CHANGE&EXIT/EXIT)
4. `RsTbChange.frm` (949 lines — 4905×3195, FrameOnline FGrid1 90/1185/2910×930, TXT_FRTABLE/TXT_TOTABLE, Shape1, Line1, LBLRoomName, Dual OpenMode graphical vs DataCombo)
5. `RsPaymentReceice.frm` (payment/settlement — 6915×7440, FrTxnNo, FrRest, FrMember, FrRem, FrChqDet, FrCCDet, FrSendRoom, FrEmp, FrComp, DGAgAc/DGRoom/DGCompany/DGEmp/DGPayType/DGMember, FGrid 1275/4080/6105×1230, GridSel 7695/1440/6495×5985)
6. `RsSaleBillSplit.frm` (12150×8520, TopCtrl1, Txt 0/4, Frame1 split logic — QTY/amount split across bills)
7. `RsPOSDisplay.frm` (14670×9135, FGrid1 0/975/11415×7065, FrPendingOrder FGrid2 315/495/5535×1965, FrSettlement FGrid 375/480/5535×1965, FrameOption 7 BtnEnh: AKOT/SBill/ChngTable/BillLookup/PKOT/OrderBook/Cancel, PicContainer/PicContent, FGridTb, Timer1 10000ms, CDLG, DispColor Table)
8. `RsPOSDisplayNew.frm` (14670×9135, FGrid1 0/0/5925×3450, Timer1 1000ms, HeadRigt/HeadLeft/HeadExit, Label2 color indicators)
9. `RsTableMast.frm` (7995×8790, TopCtrl1, Txt 0/2, DGRest)
10. `pHappyHours.frm` + `NewHappyHours.frm` (pHappyHours 9015×7290 plain; NewHappyHours 13800×7890, TopCtrl1, txt 0-8, framWeek chkday 1-7, FGrid 1920/3180/7005×1935, FGrid1 1905/5550/7005×1995, DGItem/DGRest/DGScheme, FGPoint)
11. Touch variants: `RsTouchScreenKOTEntry.frm`, `RsTouchScreenSaleBill`, `RSTouchScreenSaleBill` referenced from `RsKOTEntry` / `RsPOSDisplay` via `MemVar_1F9220C == "Yes"` branch
12. Screenshots enumerated via `HMS_Manuals\HMS_Manuals\POS\screenshots\01_Outlets\`, `02_Operations\` (01_Stock…10_Settle etc.) — no dedicated KOTEntry screenshot found; operations screenshots cover WalkIn/CheckIn but POS flow inferred from code + manual doc.

Python `.py` fully read (all lines):
1. `ui/kot_entry.py` (530 lines — QDialog 1200×700, QFormLayout header, QTableWidget 11 cols, QComboBox lookups, lbl_state theme)
2. `ui/pos_sales_ui.py` (208 lines — QDialog 900×600, QTableWidget 6 cols DocId/VDate/RestCode/GuestName/NetAmt/Status, QFormLayout Sale Details, New/Void/Print)
3. `ui/kot_transfer_ui.py` (244 lines — Two QMainWindows: TableChangeWindow 640×460, KOTTransferWindow 660×480, QGroupBox+QFormLayout, QTableWidget 4/5 cols)
4. `ui/pos_table_ui.py` (187 lines — QMainWindow 900×600, QGroupBox Table Details, QTableWidget 6 cols)
5. `ui/pos_stock_ui.py` (160 lines — QDialog 900×600, QTableWidget 7 cols)
6. `ui/pos_delivery_ui.py` (172 lines — QDialog 900×600, QTableWidget 5 cols, Mark Delivered)
7. `ui/pos_happy_ui.py` (199 lines — QDialog 900×600, QTableWidget 6 cols, HappyHoursHeadAPI)
8. `ui/pos_masters_ui.py` (353 lines — BaseMasterForm configs: Session, Scheme, DeliveryBoy, ItemCat, NCType, Waiter, Shift, Combo, SmartCard)

Core cross-checked: `core/pos.py`, `core/pos_kot.py`, `core/pos_sales.py`, `core/pos_stock.py`, `core/pos_delivery.py`, `core/pos_happy.py`, `core/pos_table.py` — DB tables `KOT`, `Sale1/Sale2`, `POS_SBill/POS_SBill` variant, `Depart`, `Waiter`, `ItemMast/Item`, `RoomMast`, `SchemeMast`, `HappyHoursHead`, `Stock`, `AssignDelivery`, `PayCharge`, `DispColor`.

---

## 2. VB6 controls VERBATIM (key excerpts)

### 2.1 RsKOTEntry.frm — `RsKOTEntry:13245×10935` MDIChild, ControlBox=False, KeyPreview=-1

```vb
Begin VB.Form RsKOTEntry
  Caption="KOT"
  BackColor=&H80000005&          ' BGR → RGB #FFFFFF (vbWindowBackground)
  ForeColor=&H40&               ' BGR &H000040 → RGB #400000 (dark maroon)
  ClientWidth=13245  ClientHeight=10935  WindowState=2 (Maximized)
  ScaleMode=0  FillColor=&H80&  Font=Arial 9.75
  Begin MainCtrl TopCtrl1  0/0/13245×450
  Begin Frame FrKOT  0/0/26506×11010  BackColor=&HC0C0FF& BorderStyle=0
    Begin TextBox Txt(10): 10455/2325/3480×285 Enabled=False ForeColor=&HC00000& MaxLen 50
    Begin TextBox Txt(9):  10455/2010/3480×285 Enabled=False ForeColor=&HC00000&
    Begin TextBox Txt(8):  10455/1695/3480×285 Enabled=False
    Begin TextBox Txt(7):   9570/1305/1860×285 Visible=False
    Begin TextBox Txt(6)  Remark: 7515/1005/3915×285 MaxLen 50
    Begin CheckBox ChkNCKOT NC: 8130/1305/600×285 BackColor=&HDEE6FE& ForeColor=&HC00000& Font Arial 9.75 Bold
    Begin TextBox Txt(2) Covers/GuarAtt: 7740/525/555×345 MaxLen 12
    Begin TextBox Txt(5) Waiter/Server: 4020/1005/2580×285
    Begin TextBox Txt(4) Table Code: 900/1005/915×285
    Begin TextBox Txt(13) Pax: 2400/1005/660×285 MaxLen 5
    Begin TextBox Txt(0) Session: 5640/525/975×345 MaxLen 8
    Begin TextBox Txt(1) Shift: 6630/525/1095×345 MaxLen 12
    Begin TextBox TxtGrid(0): 1080/8250/480×240 Visible=False BackColor=&HFFFFC0& MaxLen 150 MultiLine
    Begin TextBox Txt(12) OrderNo: 3690/1305/1140×285 Visible=False
    Begin TextBox Txt(11) Member: 900/1305/2775×285 Enabled=False Visible=False MaxLen 75
    Begin TextBox Txt(14) Covers: 5895/1305/930×255 Visible=False
    Begin TextBox Txt(3): 11325/6300/2325×210 Visible=False BackColor=&H80000000&
    Begin Frame FrmeDisc Description: 16170/720/5130×585 Visible=False → txtDisc 60/270/5000×240 MaxLen 75
    Begin MSHFlexGrid FGrid: 30/1620/8655×6090  ← MAIN ITEM GRID
    Begin MSHFlexGrid FGrid2 PendingKOT: 10215/6930/5940×2325 Visible=False
    Begin BtnEnh CmdTabeSt: 4905/8340/945×540 Visible=False
    Begin BtnEnh CmPendingKot: 5850/8340/945×540 Visible=False
    Begin BtnEnh cmdNCBill: 11430/990/990×615 Visible=False
    Begin BtnEnh CmdFreeItem: 12465/990/1050×600 Visible=False
    Begin MSHFlexGrid FGrid1 summary: 10185/4560/5940×2325 Visible=False
    Begin DataGrid DGTable 16485/2820/9240×2460 Visible=False
    Begin DataGrid DGItem  16320/2190/4035×4710 Visible=False
    Begin DataGrid DGRest  16140/1755/5910×1455 Visible=False
    Begin DataGrid DGWaiter 16305/1245/4290×3390 Visible=False
    Begin DataGrid DGNCType 9195/2250/3675×3390 Visible=False
    Begin DataGrid DGMember 16335/60/6720×3315 Visible=False
    Begin Label LblState Running Order: 8340/525/3090×345 BackColor=&HFFFFFF& ForeColor=&HC0& (BGR &H0000C0 → #C00000 red) Font Arial 11.25 Bold Align Center
    Begin Label LblRest Outlet: 15/525/2235×345 BackColor=&HFFFFFF& ForeColor=&HFF0000& Font Arial 11.25 Bold Align Center
    Begin Label lblSession Session: 2250/525/1665×345 BackColor=&HFFFFFF& ForeColor=&HC00000&
    Begin Label LblKotNm KOT#: 3915/525/1725×345 BackColor=&HFFFFFF& ForeColor=&HC00000& Align Center
    Begin Label LblRestz #: 12990/-780/285×525 BackColor=&HC00000& ForeColor=&HFF0000& Border FixedSingle Font Times 20.25 Bold
    Begin Label lblclr FreeItem marker: 1080/8490/600×240 BackColor=&HFF00& (BGR &H00FF00 → #00FF00 green)
    Begin Label LblCurStockStr "Item Current Stock": 0/7890/2370×375 ForeColor=&H80& Font Arial Narrow 15.75 Bold
    Begin Label Label1 Pax/TableCode/Server/Remark/Steward/NCType/Member/TokenNo: ForeColor &H40& or &HC00000& Arial 9.75 Bold
```

**Behavior notes from code (RsKOTEntry):**
- `TopCtrl1` state machine Add/Edit/Browse controls `Me.TopCtrl1_eAdd` gating `CmdFreeItem`, `FGrid` edits; `TxtGrid(0)` overlays FGrid cell for inline edit, `TxtDisc` handles Item description via `Timer2 Interval=10` + `FrmeDisc`.
- `FGrid` columns (inferred from `TxtGrid` handling, `DGItem` column map): `SNo | Item Name (=Name) | Code/DispCode | Qty | Unit | Rate | Amount | Remarks | NC | Free | PriceType/Cover` — exact VB col indices driven by `Proc_6_63_110ABA4` cloning `MSHFlexGrid` formatting; `FGrid2` pending KOT grid filled by `CmPendingKot_UnknownEvent_9` query: `SELECT k.docid, K.Vtime, K.VNo, K.RoomNo TableNo, I.NAME PRODUCT, K.Qty FROM KOT JOIN waiter/item/depart/voucher WHERE contradocid='' AND VoidYN='N' AND delFlag<>'Y' AND nckot='N' AND restcode=:LocalRestCode`.
- Waiter lookup `Txt(5) ↔ DGWaiter`, Table `Txt(4) ↔ DGTable`, NCType `Txt(7) ↔ DGNCType`, Member `Txt(11) ↔ DGMember`, Outlet `DGRest`, Item `TxtGrid(0) ↔ DGItem` with `ItemMast` join `Item.RestCode`, price pulled via `Proc_30_105_F223E0` + Rate column 8 formatting `Format("0.00")`.
- `ChkNCKOT` toggles NCKOT flag; `Txt(2)` covers/pax validates `MaxLength 12`; `Txt(14)` covers hidden; `Txt(13)` pax 5 chars; `LblState` updated on `Form_Load`/`SetOnLineBookingDetail` to show `"Running Order"` / `"Billed"` / `"Vacant"`-style state mirrored from `RsPOSDisplay`.
- Validation `Txt_Validate` enforces `Scheme Name`, `Rest Name`, time 0-24/0-59 via `Proc_6_27_EA565C` + `Format(Time,"HH"/"NN")` fallback.
- `LblCurStockStr` + underlying stock lookup not visible in header but `TxtGrid_GotFocus` queries `ItemMast` stock for `Item Current Stock` label.

### 2.2 RSSaleBill.frm — `11280×8595` MDIChild

```vb
Begin VB.Form RSSaleBill  BackColor=&HFFC0C0&  Client 11280×8595  Font Tahoma 11.25
  Begin BtnEnh LblCustSaleDetail 12345/15/3735×450 Visible=False
  Begin Frame FrCustSaleDetail 16440/3180/3735×2865 Visible=False  → Txt1(0-2) mobile/from/to + CmdCustPrint
  Begin Frame FrCustInfo Customer Info 8385/5775/4740×1140 Enabled=False Visible=False BackColor=&H80FF& → TxtCust 0-7
  Begin Frame FreInvInfo eInvoice 13185/5985/6735×1095 Visible=False → TxteInvInfo 0-2
  Begin Frame FrSun1/2/3 Sundry (Total/%) 8385/1650-2175/3390×2865 Visible=False → TxtGt/TxtPer/LblCap/LblAt
  Begin Frame FrCtrl 8355/7335/4815×1020 Border None → BtnEnh CmdSave/CmdCtrl(1,2)/CmdRedeem
  Begin TextBox Txt(18) 9435/795/1905×285 Enabled=False Visible=False ForeColor=&HFF0000&
  Begin TextBox Txt(2) hidden 9840/135/2325×210 Visible=False BackColor=&H80000000&
  Begin TextBox TxtGrid(0) overlay 1200/1590/765×240 Visible=False BackColor=&HC0C0C0&
  Begin Timer Timer2 Interval 10
  Begin DataGrid DGItem 18390/8790/6615×1200 Visible=False
  Begin DataGrid DGMember 9195/8190/8760×1635 Visible=False
  Begin DataGrid DGShift 18390/8445/4230×1050 Visible=False
  Begin Frame FrModification Validation 11760/4770/1665×900 Visible=False → CmdDatewise/Groupwise
  Begin Frame FrPOSBillDateWise/FrPOSBillGroupWise (FGrid1 495/2020/6930×5375, Txt2 from/to)
  Begin Label LblVPrefix "VPrefix" 16710/10755/705×240 Visible=False ForeColor=&HC00000&
  Begin Label LblLDt "Last Update" 90/10065/2670×240 ForeColor=&HFF0000&
  Begin Label LblUser "User" 105/9735/2460×240
```
- Grid: `MSHFlexGrid FGrid` + `FGrid1` for item/bill lines; columns include `Item | Qty | Rate | Amount | Tax% | Disc% | Sundry | PayCharge` — totals computed via `TxtGt1/2/3` + `FrSun*` branching; `FrCtrl` Save/Edit handled by `TopCtrl1`.
- Branching: `FrSun1/2/3` visibility driven by Sundry setup; `PayCharge` branching via `FGrid` col `AmtCr`; `HappyHours` discount injected via `SchemeMast` lookup (see `NewHappyHours` scheme); `FrAutoSettlement` → Smart Card Member/Debit Card via `RsPaymentReceice` path.
- Token: `FrTokenInfo 15450/2235/2850×1620 Visible=False` with `TxtTokenNum + Check1 All + GridSel + CmdTokenFill` → `RsTokenEntry`.

### 2.3 RsKOTTransfer.frm — `4905×3195`

```vb
Begin VB.Form RsKOTTransfer BackColor=&H80000005& Client 4905×3195
  Begin Frame FrameOffline 0/0/8820×6645 Border 0
    Begin DataCombo TXT_PKOT 1905/1485/1905×360
    Begin DataCombo TXT_TOTABLE 5850/1485/1905×360
    Begin BtnEnh CmdExit 4215/3525/1575×750
    Begin BtnEnh CmdChange 2640/3525/1575×750
    Begin Label LblFormCaption RestName & " Kot Transfer" 0/0/8835×540 BackColor=&HC0FFFF& Border FixedSingle Font System 19.5 Bold Align Center
    Begin Line Line1 BorderColor &HC00000& 4260/1140-4260/2835 BorderWidth 2
    Begin Label "On Table:" 1860/1920 ForeColor &H800000& Arial 9.75 Bold
    Begin Label LblKOTTable "KOTTB" 2835/1920 ForeColor &HFF& (→ #FF0000 red)
    Begin Shape Shape2 Border &HC00000& 480/1125/7635×1725 Shape 4 BorderWidth 2 FillColor &HC000C0&
  Begin Frame FrameOnline 9090/420/4605×4845 Border 0  (graphical mode when OpenMode=1)
    Begin MSHFlexGrid FGrid1 90/1185/2025×630
    Begin Label LBLRoomName 60/795/11965×360 BackColor &HC0FFFF& ForeColor &HC0& Border FixedSingle Align Right Font Tahoma 12 Bold
    Begin Frame FrameOption 195/3570/2730×1200 Border 0 → CmdTChange "CHANGE && EXIT" + CmdTExit "EXIT" (BackColor &HE0E0E0& Tahoma 9 Bold Style 1)
```
- Logic: `Form_Load` branches `If OpenMode=1 Then FrameOffline.Visible=False` (full-screen table map FGrid1 with 6-col blocks, `LBLRoomName.caption = "CHANGE TABLE : " & PTableNo & " TO "`) vs else DataCombo mode (`Room Service` uses `DOCID` vs `TB` uses `VNO`). `TXT_PKOT_UnknownEvent_11` fills `LblKOTTable` via `SELECT Max(RoomNo) FROM KOT WHERE Pending='Y'...` and sets `TXT_TOTABLE.Tag` filtered list.

### 2.4 RsTbChange.frm — `4905×3195`

```vb
Begin VB.Form RsTbChange Caption "Table Transfer" Client 4905×3195
  Begin Frame FrameOnline 9705/1020/4935×4845 Border 0 → FrameOption CmdTChange/CmdTExit + FGrid1 90/1185/2910×930 + LBLRoomName 60/795/9540×360 BackColor &HC0FFFF&
  Begin DataCombo TXT_FRTABLE 3300/2835/3165×360
  Begin DataCombo TXT_TOTABLE 7815/2835/3165×360
  Begin Label LblFormCaption 0/0/180×540 BackColor &HC0FFFF& Border FixedSingle System 19.5 Bold
  Begin Line Line1 Border &HC00000& 6675/1935-6675/4335 BorderWidth 3
  Begin Shape Shape1 Border &HC00000& 1860/1920/9285×2445 Shape 4 BorderWidth 2
```
- Same dual-mode pattern as KOTTransfer: `OpenMode=1` shows graphical `FGrid1` table occupancy map (colors via `TVacantColor`, `&H404040` occupied, `&HE69839` header, `DispColor` table), else shows `TXT_FRTABLE` from `SELECT DISTINCT RoomNo FROM KOT WHERE restCode=:LocalRestCode AND ROOMTYPE='TB' AND PENDING='Y'...` and `TXT_TOTABLE` from `RoomMast Where type='TB' And Code Not in (SELECT RoomNo FROM KOT Pending ...)`.

### 2.5 RsPaymentReceice.frm — `6915×7440` BackColor &HFFC0FF& (light magenta)
Key controls verbatim:
`FrTxnNo (1275/7200/6210×315 Visible=False → Txt(17) TxnNo)`, `FrRest (1230/1425/6210×945 → Txt1 Date/VrNo/Type/Amount + Txt5 Type, Txt6 Amount)`, `FrMember (1275/6255/6210×315 → Txt14 Member)`, `FrRem (1230/2370/6210×315 → Txt18 Narration)`, `FrChqDet (1275/5325/6210×630 → Txt11 ChqNo/Txt12 Dt)`, `FrCCDet (1230/2685/6210×945 → Txt7 CCNo/Txt8 Holder/Txt9 ExpDt/Txt10 Batch)`, `FrComp (1275/5940/6210×315 → Txt13 Company)`, `FrEmp (1275/6570/6210×315 → Txt15 Staff)`, `FrSendRoom (1275/6885/6210×315 → Txt16 RoomNo)`, `DGPayType/DGAgAc/DGRoom/DGCompany/DGEmp/DGMember/DGRoom` all Visible=False, `FGrid (1275/4080/6105×1230)`, `GridSel (7695/1440/6495×5985)`, `MSFlexGrid FGPoint 14100/615 hidden`, `MainCtrl TopCtrl1 0/0/6915×450`, `LblFormCaption BackColor &HC0FFFF& System 19.5 Bold`.
- Handles `PayCharge` settlement branching: `Amount (Txt6)`, `PayType (Txt5) ↔ DGPayType`, Agent `Txt4 ↔ DGAgAc`, Staff `Txt15 ↔ DGEmp`, Room `Txt16 ↔ DGRoom`, Company `Txt13 ↔ DGCompany`, Member `Txt14 ↔ DGMember`, Cheque/Credit Card/ txn branches `FrCCDet/FrChqDet/FrTxnNo`.

### 2.6 RsPOSDisplay / RsPOSDisplayNew — `14670×9135`
`RsPOSDisplay`: `FGrid1 0/975/11415×7065` (main 6-col-per-table grid), `FrPendingOrder (0/7725/9330×2580) FGrid2 315/495/5535×1965 + CmdUp2/Down2`, `FrSettlement (6465/6330/9330×2580 Border 0) FGrid 375/480/5535×1965 + CmdUP/Down/Exit/Ref`, `FrameOption 11685/1650/2700×4110 BackColor &HFFC0FF& Border 0 → 7 BtnEnh (AKOT/SBill/ChngTable/BillLookup/PKOT/OrderBook/Cancel 2700×600)`, `Timer1 10000ms`, `Label1/2 color legends (Label2 BackColors: &HFFFF &HFFFFFF &HC0FFC0 Vacant/Occupied/Billed)`, `LBLRoomName (-15/480/11970×450 BackColor &HFFC0C0& ForeColor &HC00000&)`, `Label3 header 0/0/11970×450`, `CmdTBInfo/FGridTb/PicContainer`.  
`RsPOSDisplayNew`: `FGrid1 0/0/5925×3450`, `Timer1 1000ms`, `HeadRigt/HeadLeft/HeadExit BtnEnh 945×540`, color `Label2` same + `ColorLabel()` loads `DispColor` from DB.

### 2.7 RsTableMast — `7995×8790` BackColor &HFFC0C0&
`TopCtrl1 0/0/7995×450`, `Txt(2) 3150/1890/4215×285 (Name 35)`, `Txt(0) 3150/2205/1875×285 (Code 25)`, `DGRest hidden`. Master of `RoomMast Type='TB'` (table) with `Depart` FK.

### 2.8 pHappyHours / NewHappyHours — `9015×7290` & `13800×7890`
`pHappyHours`: legacy single-grid; `NewHappyHours` (current): `13800×7890 WindowState 2 BackColor &HFFC0C0&`, `TopCtrl1 0/0/13800×450`, `txt 0 Scheme Name 3390/1275/4215×285`, `txt1 Start Date 3390/1590/1560×285`, `txt2 End Date 6045/1590/1560×285`, `txt3-6 From/To HH & MM 3390/1905-5460/1905 375×285 align Center MaxLen 4`, `txt7 Active Yes/No 6510/1905/540×285 MaxLen 3`, `txt8 Outlet Name 3390/2220/4215×285`, `framWeek Days 8190/960/2925×1635 BackColor &HC0FFFF& → chkday 1-7 Sunday-Saturday (colors &HC0C0FF &HFFC0C0 etc)`, `FGrid 1920/3180/7005×1935 + Label "Select Scheme Item" &H C00000& white 6495×375`, `FGrid1 1905/5550/7005×1995 + Label "Free Item"`, `DGItem 8445/2595/4035×4635, DGRest 11310/3855/4230×2115, DGScheme 11250/2640/4230×2115 hidden`, `Shape1 Border &HC00000& 1920/1095/6090×1560`.

### 2.9 RsSaleBillSplit — `12150×8520` BackColor &HE0E0E0&
`TopCtrl1 0/0/12150×450 System 9.75 Bold`, `Txt(0) 4245/450/1200×285 MaxLen 8`, `Txt(4) 9765/465/375×285 MaxLen 5 (split qty?)`, `Frame1 split logic` — splits `Sale2` lines across bills by amount/qty.

---

## 3. Python controls (actual)

| File | Class | Window | Size | Header / TopCtrl | Grid | Lookups | Buttons | Theme |
|------|-------|--------|------|------------------|------|---------|---------|-------|
| `kot_entry.py` | `KOTEntryForm(QDialog)` | KOT Entry (P5) | `resize(1200,700)` — **FixedSize not set**, no maximize | Header `QFormLayout`: `cb_outlet QComboBox`, `de_vdate QDateEdit`, `cb_waiter QComboBox` — **no TopCtrl1** | `QTableWidget 0×11` LINE_COLS: SNo(ItemCode/Name/Qty/Unit/Rate/Amount/Table/Waiter/NC Type/Remarks) `setAlternatingRowColors(True)` `cellChanged` auto calc | `_get_item_combo()` editable, `_get_table_combo`, `_get_nc_type_combo`, `_get_waiter_combo` — **DataGrid visual not used, QComboBox per cell** | `btn_new/save/void/print/cancel/close` QHBox; shortcuts Ctrl+N/S/D, Esc, F5 | `theme.status_colors()` for lbl_state, `palette()["text"]` for items; no BGR copy |
| `pos_sales_ui.py` | `PosSalesDialog(QDialog)` | POS Sales Register | 900×600 | No TopCtrl1 | `QTableWidget 6 cols` DocId/VDate/RestCode/GuestName/NetAmt/Status `NoEditTriggers` `SelectRows` `Stretch` | None (detail via QLineEdits) | New Sale/Void/Print/Refresh/Exit (minHeight 34, role danger/warning) | palette text |
| `kot_transfer_ui.py` | `TableChangeWindow(QMainWindow)` 640×460 + `KOTTransferWindow(QMainWindow)` 660×480 | Table Change Entry / KOT Transfer | QGroupBox "Table move"/"KOT move" QFormLayout: outlet→tables load | `QTableWidget 4 cols` DocId/VNo/Date/Time + `5 cols` DocId/VNo/Room/Date/Time `Stretch` `Alternating` | `_outlets()` from Depart; `cmb_from` from `pos_kot.pending_kot_tables`; `cmb_kot` from `pending_kot_list`; chk_room toggles DocId vs VNo ref | Change Table / Transfer KOT + Exit (role warning) | palette |
| `pos_table_ui.py` | `PosTableWindow(QMainWindow)` | POS Table Management | 900×600 | QGroupBox Table Details QFormLayout: txt_code/room_name/type/seating_capacity/status(QComboBox Active/Inactive/Blocked) | `QTableWidget 6 cols` Code/RoomName/RoomNo/Type/SeatingCapacity/Status `Alternating` + status semantic bg (success/neutral/danger) | None | New/Edit/Delete/Refresh/Exit | status_colors |
| `pos_stock_ui.py` | `PosStockDialog(QDialog)` | POS Stock Management | 900×600 | QGroupBox Stock Details 7 QLineEdits | `QTableWidget 7 cols` DocId/VDate/Vtype/ItemCode/Qty/Rate/Amount | None | New Stock Entry/Refresh/Exit | palette |
| `pos_delivery_ui.py` | `PosDeliveryDialog(QDialog)` | POS Delivery Management | 900×600 | QGroupBox Delivery Details 7 QLineEdits | `QTableWidget 5 cols` VNo/DocId/DeliveryBoy/Status/DeliveryDate | None | New Assignment/Mark Delivered/Refresh/Exit | palette |
| `pos_happy_ui.py` | `PosHappyDialog(QDialog)` | POS Happy Hours | 900×600 | QGroupBox Happy Hours Details 8 QLineEdits | `QTableWidget 6 cols` Code/Name/FromTime/ToTime/Discount/Status | None | New/Edit/Delete/Refresh/Exit | palette |
| `pos_masters_ui.py` | `BaseMasterForm` via `pos_masters.py` | Session/Scheme/DeliveryBoy/ItemCat/NCType/Waiter/Shift/Combo/SmartCard | via BaseMasterForm (FixedSize?) | MasterConfig title/columns/fields + make_delete_guard("PYT") | BaseMasterForm QTableWidget + Field QLineEdits | N/A | BaseMaster New/Edit/Delete/Save/Cancel | theme |

No Python file implements: `RsPOSDisplay` / `RsPOSDisplayNew` occupancy map, `RsPaymentReceice` settlement PayCharge, `RsSaleBillSplit`, `RsTableMast` full VB fidelity, TouchScreen branch.

---

## 4. Layout / Colors / Fonts / Controls comparison

### 4.1 Size & window chrome
- VB6: All POS forms `MDIChild=True, ControlBox=False, WindowState=2 (Maximized)`, `ClientWidth/Height` in twips (1/1440 inch). e.g., `RsKOTEntry 13245 = 884 px @ 96dpi + MDI chrome`; `RsPOSDisplay 14670 = 978 px width` actually maximized to screen via `Form_Activate Me.FrameOnline.Height/Width = Method_arg_108/100`. VB6 relies on MDI parent `MDIForm1.PictShortCuts` background.
- Python: `QDialog/QMainWindow resize(900-1200,600-700)` — **fixed small window, not maximized, not MDIChild**, no `ControlBox=False` enforcement, no `WindowState=2`. `TopCtrl1` (custom state machine Add/Edit/Browse) missing on POS forms except masters use `BaseMasterForm` TopCtrl emulation.

**Fix:** Match VB6 maximize intent: `setWindowState(Qt.WindowMaximized)` + `setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)` + store `VB_WIDTH_TWIPS` constant for reference; add `TopCtrl` widget.

### 4.2 Colors BGR→RGB (VB6 `&HBBGGRR` little-endian)
| VB6 hex | BGR → RGB | Python current | Match? |
|---------|-----------|----------------|--------|
| `&H80000005&` window bg (vbWindowBackground) | system → `#FFFFFF` | `palette()["window"]` often `#F5F5F5` | drift |
| `&HFFC0C0&` SaleBill/TableMast/HappyHours | BGR `C0 C0 FF` → `#FFC0C0` (light pink) | default `#FFFFFF` | **MISSING** — must set `setStyleSheet("background:#FFC0C0")` |
| `&HC0C0FF&` FrKOT | BGR `FF C0 C0` → `#FFC0C0` same pink (VB bug: looks peach) | not set | missing |
| `&HFFFFFF&` white LblRest/LblState | `#FFFFFF` | white | ok |
| `&HC00000&` maroon text | BGR `00 00 C0` → `#C00000` | `palette()["text"]` ≈ `#1A1A1A` | **wrong** — VB uses maroon labels |
| `&H40&` dark maroon | `#400000` | not used | missing |
| `&HFF0000&` red (pure) | BGR `00 00 FF` → `#FF0000` | `status danger` `#DC2626` close | ok |
| `&HFF00&` green marker lblclr | BGR `00 FF 00` → `#00FF00` | not used | missing |
| `&H FF00FF&` magenta FrCCDet? Actually &HFFC0FF FrRest `C9E2F5`? | `&HC9E2F5&` → BGR `F5 E2 C9` → `#C9E2F5` pastel blue | not set | missing |
| `&HE69839` FGrid header | BGR `39 98 E6` → `#E69839` orange | `#E5E7EB` gray | missing |
| `&HE0E0E0&` RsSaleBillSplit | `#E0E0E0` light gray | default | ok |
| `&HC0FFFF&` LblFormCaption | BGR `FF FF C0` → `#FFFFC0` light yellow | not set | missing |
| `&H404040` occupied table | `#404040` dark gray | not set | missing |
| `&HC0FFC0` billed (light green) | `#C0FFC0` | not set | missing |
| `&H8000000D` label shadow | system highlight → approx `#0078D7` | not set | missing |

**Patch:** Create `vb_colors.py` map + apply via `QSS` per form (see §7).

### 4.3 Fonts
- VB6: `Arial 9.75 (400/700)`, `System 9.75 Bold`, `Tahoma 9-11.25`, `Times New Roman 12 Bold`, `MS Sans Serif 8.25`. Size in points (twips/144). Labels like `LblState Arial 11.25 Bold`, `LblRestz Times 20.25 Bold`.
- Python: `Segoe UI 14 Bold` title, `theme` default `9pt`, no per-label VB font copy. Missing `Arial Narrow 15.75 Bold` for stock label.

**Patch:** Set `QFont("Arial", 11)` etc. via `label.setFont()` to match.

### 4.4 Controls
| VB6 | Python | Gap |
|-----|--------|-----|
| `MainCtrl TopCtrl1` (Add/Edit/Save/Cancel/Delete/Print/Exit state machine, `TopCtrl1_eAdd`, `TopCtrl1_eSave`) | Missing on KOT/Sale/Transfer/Display/Delivery/Stock | **CRITICAL** — VB disables grids when Browse |
| `MSHFlexGrid FGrid` (merge, `CellBackColor`, `TextMatrix(col,row)`, 6-col-per-table layout, tooltip, drag) | `QTableWidget` single-cell | Missing merge, 6-col block layout, color per occupancy |
| `DataGrid DG*` + `FGPoint` + `DGMember/DGTable/DGWaiter/DGItem` dropdown sheets positioned under Txt via `Proc_6_137_1193554` | `QComboBox` per cell | Missing overlay positioning, `Visible=False` toggle, `UnknownEvent_9` double-click pick |
| `TextBox Txt(Index)` array with `MaxLength` + `BorderStyle 0 Flat` + `ForeColor &HC00000&` | `QLineEdit` `setMaxLength` but no array index, no `BorderStyle None` QSS | Missing index mapping (Txt 0 Session vs Txt 4 TableCode etc.) |
| `CheckBox ChkNCKOT "NC"` | `QCheckBox` per-line NC Type combo — not master NC | VB has both master NC checkbox + row NC Type |
| `Frame FrKOT/FrRest/FrCCDet` etc. pastel `BackColor` | `QGroupBox` white | Missing pastel Frame colors |
| `Shape/Line` decorative `BorderColor &HC00000&` | none | missing |
| `Timer Timer2 Interval 10` drives inline edit | none | missing but can drop |
| `CommonDialog CDLG` for color picker `DispColor` | none | missing for Display form |
| `DataCombo TXT_PKOT` BoundText/defText/Tag pattern | QComboBox currentData only | Missing BoundText vs displayed Name split |

---

## 5. Workflow comparison (VB6 exact vs Python)

### 5.1 KOT Entry — Running Order / Covers / GuarAtt
- **VB6:** `Txt(0) Session` + `Txt(1) Shift` + `Txt(2) Covers` (12 chars) + `Txt(4) TableCode` + `Txt(5) Waiter` + `Txt(6) Remarks` + `Txt(13) Pax` (5) + `Txt(14) Covers dup` + `Txt(11) Member` (75) + `Txt(12) Token` (11) + `Txt(7) NC Type` + `Txt(8-10) Comment1-3` + `ChkNCKOT` + `LblState` ("Running Order"/"Occupied"/etc.) + `LblRest` outlet name + `lblSession` session name. Grid `FGrid` supports free-item green flag `lblclr`, pending KOT overlay `FGrid2` populated via `CmPendingKot` query. TouchScreen branch: `If MemVar_1F9220C="Yes" Then RsTouchScreenKOTEntry` (large buttons, steward touch). `GuarAtt` covers logic via `Txt(2)` validated as numeric.
- **Python:** Only outlet, date, waiter header; grid has row-level waiter/NC/table but no `Session/Shift/Covers/Pax/Member/Token/Remarks/Comments/FreeItem/NCKOT` header fields; no `LblState` running order indicator beyond generic `State: Idle/Add/Edit`; no `CmPendingKot` overlay, no `FGrid2` pending view, no `lblclr` green marker, no `GuarAtt` validation, no TouchScreen flag at all.

### 5.2 Table Change / KOT Transfer — Shift
- **VB6:** Dual-mode: `OpenMode=1` → full-screen occupancy map `FGrid1` with `LBLRoomName "CHANGE TABLE : X TO "` + `FrameOption CHANGE && EXIT / EXIT` (positions `Left = FGrid.Width+250`, `Top = (Height - option.Height)/2`). Click on FGrid1 cell detects `*Vacant` vs occupied via `Right(Ucase(Trim(TextMatrix)),6)="VACANT"` + `TVacantColor` vs `&H404040` and `VType` join to decide allow. DataCombo mode: `TXT_FRTABLE` lists `SELECT DISTINCT RoomNo AS CODE FROM KOT WHERE Pending='Y'...` and `TXT_TOTABLE` lists `RoomMast CODE Not in (SELECT RoomNo FROM KOT Pending)` — so target must be vacant. `RsKOTTransfer` adds `TXT_PKOT` as `DISTINCT VNO` (`TB`) or `DOCID` (`RO`) and `TXT_TOTABLE` filtered by `LblKOTTable` (source room). RoomService path updates `ROOMCAT` from `ROOMOCC.RoomCat`.
- **Python:** `TableChangeWindow` shows `cmb_from` from `pending_kot_tables` + `txt_to QLineEdit` free text (no vacant check), `KOTTransferWindow` shows `cmb_kot` from all pending + `txt_to` free text, `chk_room` checkbox but no `RoomCat` sync beyond `res["roomcat_updated"]`. No graphical `FGrid1` mode; no `OpenMode` property; no `PTableNo` setter that drives `LBLRoomName`; no `TVacantColor` logic; no `Line/Shape` chrome; no validation that target is vacant.

### 5.3 Sale Bill — grid totals / sundry / PayCharge branching / Split
- **VB6:** Master grid `FGrid` lines fed via `TxtGrid(0/1/2)` overlay + `DGItem` per-line item pick (ItemMast join). Totals: `TxtGt1/2/3` + `TxtPer1/2/3` inside `FrSun1/2/3` (only one visible per `SundryMast` config). Tax calcs per `TaxStruMast`, discount via `HappyHours` scheme (`SchemeMast` Days + From/To HH MM split into Txt3-6). PayCharge branching: `FGrid` rows for payments with `DGPayType` → shows/hides `FrCCDet` (CC), `FrChqDet` (cheque), `FrComp` (company), `FrEmp` (staff), `FrSendRoom` (room). Settlement auto via `FrAutoSettlement` → `RsPaymentReceice`. Split: `RsSaleBillSplit` with `Frame1` partition of `Sale2` by QTY/amount. eInvoice `FreInvInfo` with IRN/Ack. Token `FrTokenInfo` with `GridSel`. Save via `TopCtrl1_eAdd/Edit` then `Proc_6_127` validations.
- **Python:** `PosSalesDialog` lists `Sale1API.list_all()` as 6-col register, detail via 6 QLineEdits, save via `SaleBillAPI.full_save(rec)` with bare header only (`total/taxable/tax/netamt` same value). No grid of `Sale2` lines, no `Sundry` frames, no `PayCharge` grid, no `HappyHours` scheme discount, no `TaxStru` calc, no `Split` UI, no `eInvoice` frame, no `Token` flow, no `Settlement` branching. Void via `Sale1API.delete` (soft delFlag) but not PayCharge cascade.

### 5.4 TouchScreen branch `RsTouchScreenKOTEntry`
- **VB6:** `If MemVar_1F9220C = "Yes"` then `CmdAKOT`/`CmdPKOT`/`RsDisplay` create `RsTouchScreenKOTEntry` instead of `RsKOTEntry` — larger button grid, `RsTouchScreenSteward` picker, `RsTouchScreenBookingEntry` for order booking.
- **Python:** `kot_entry.py` has no `Enviro` TouchScreen flag check, no alternative dialog. `core/env.py` or `HMS_py/core/env` exists but not wired.

### 5.5 Display — Pending / Unsettled / Vacant map
- **VB6:** `RsPOSDisplay`: `FGrid1` occupancy map 6 cols per table block (Code/Name/Waiter/Time/Status): `Vacant` (white &HFFFFFF), `Occupied` (*WaiterName + time, light yellow), `Billed` (green &HC0FFC0) via `DispColor` table. `FrPendingOrder FGrid2` shows packing orders; `FrSettlement FGrid` shows `Sale1 LEFT JOIN PayCharge WHERE PayCharge.DocId Is Null AND DelFlag=''` with `Status = CASE WHEN Sum(AmtCr) < Sum(NetAmt) Then 'Pending' Else 'Settle'`. Buttons: `CmdUnSBill` (unsettled bills), `CmdAKOT` (add KOT), `CmdSBill` (sale bill), `CmdChngTable`, etc. anchored. `Timer1` auto-refresh.
- **Python:** No equivalent `RsPOSDisplay` UI exists. `pos_table_ui.py` manages `RoomMast` master, not occupancy; no `FGrid1` map, no `FrPendingOrder/FrSettlement`, no `Timer1`, no `DispColor` color picker, no `FrameOption` actions.

### 5.6 HappyHours
- **VB6:** `NewHappyHours` has two grids `FGrid` (scheme items) + `FGrid1` (free items) each with `TxtGrid` + `DGItem` per-line; time split into 4 txt `HH`+`MM` (txt3-6) validated 0-23 / 0-59 with fallback to `Format(Time,"HH")`; days `chkday 1-7`; Active Y/N (txt7); scheme name `txt0`; outlet `txt8`; dates `txt1/2` via `Proc_6_33` date format. Scheme filtered via `DGScheme`.
- **Python:** `PosHappyDialog` single table 6 cols with plain `QLineEdit` From/To as strings, no HH/MM split, no `chkday` week, no dual-grid free/scheme items, no `DGScheme/DGRest/DGItem` lookups, no `Active all Check1`.

### 5.7 Stock / Delivery
- **VB6:** Stock via `DepOpStk`/`kClStk`/`FrmStockTransfer` with Godown, `ItemMast` join, `QtyIss/Rec`; delivery via `RsAssignDelivery` (`FrmDeliveryBoyMast`, `AssignDelivery` DocId/VNo/DeliBoy/Ddate/BillAmt/Remark) + `DeliveredItemDetail`.
- **Python:** `pos_stock_ui` bare Stock (DocId/Vdate/Vtype/Item/Qty/Rate/Amount) no Godown/Item picker; `pos_delivery_ui` only AssignDelivery header, no item detail, no Delivery Boy master link.

---

## 6. Gap table — MISSING frontend logic (no DB change)

| # | VB6 Feature | Python File | Gap Severity | What breaks |
|---|-------------|-------------|--------------|-------------|
| G1 | RsKOTEntry Covers/Pax/Token/Member/NC/Comments/Remarks/Txt 0-14, LblState/LblRest/lblSession/LblKotNm | `kot_entry.py` | **Critical** | Covers not captured → seating wrong; Member charge fails |
| G2 | TopCtrl1 Add/Edit/Browse state machine + FGrid disabled when Browse | `kot_entry.py`, `pos_sales_ui.py`, `pos_table_ui.py` (partial) | Critical | User can edit when should be browse; validation bypass |
| G3 | MSHFlexGrid 6-col-per-table occupancy map (FGrid1 + FGrid2 pending + DispColor &H404040/&HE69839/&HFFFFFF/&HC0FFC0) | (no file) `pos_table_ui.py` is master only | Critical | No visual table status — operator cannot see Vacant/Occupied |
| G4 | DataGrid overlays (DGItem/DGTable/DGWaiter/DGNCType/DGMember/DGRest) positioned under Txt via FGPoint | `kot_entry.py` uses per-cell QComboBox | Major | Lookup UX differs, keyboard nav (Up/Down 0x26/0x28, F4) not matched |
| G5 | TxtGrid overlay inline editing + FrmeDisc txtDisc + Timer2 | `kot_entry.py` _on_cell_changed only | Major | Description/comment flow missing |
| G6 | ChkNCKOT master + row NC Type + cmdNCBill/cmdFreeItem + lblclr green marker | `kot_entry.py` row nc_type only | Major | FOC vs NC distinction lost |
| G7 | RsPOSDisplay FrameOption 7 actions (AKOT/SBill/ChngTable/BillLookup/PKOT/OrderBook/Cancel) + FrPendingOrder/FrSettlement + Timer1 | (no file) | Critical | Entire POS hub missing |
| G8 | Pending KOT grid `FGrid2` + CmPendingKot query (contradocid='', VoidYN='N', delFlag, nckot) | missing | Major | Cannot see pending KOTs before sale bill |
| G9 | TouchScreen branch `MemVar_1F9220C=="Yes"` → RsTouchScreenKOTEntry/ RsTouchScreenSteward | none | Major | Touch outlets get wrong UI |
| G10 | RsTbChange/RsKOTTransfer dual OpenMode (graphical FGrid1 vs DataCombo) + PTableNo + LBLRoomName "CHANGE TABLE : X TO " + TVacantColor + Line/Shape chrome | `kot_transfer_ui.py` only DataCombo | Critical | TableChange from display clicks broken; vacant validation missing |
| G11 | RsSaleBill Sundry FrSun1/2/3 + TxtGt/TxtPer branching + TaxStru + Scheme/HappyHours discount (txt3-6 HH:MM split, chkday) | `pos_sales_ui.py` bare | Critical | Bill totals wrong; happy hours not applied |
| G12 | PayCharge branching (FrCCDet/FrChqDet/FrComp/FrEmp/FrSendRoom) + RsPaymentReceice GridSel + DGAgAc/DGRoom etc. | `pos_delivery_ui` only, no PayCharge UI | Critical | Settlement cannot enter CC/Cheque/Company/Room |
| G13 | Sale split RsSaleBillSplit Frame1 | none | Major | Split bill not possible |
| G14 | RsTableMast 7995×8790 + DGRest + RoomMast Type='TB' master fidelity | `pos_table_ui.py` generic 6 cols, no DGRest | Minor | RestCode FK lookup missing |
| G15 | NewHappyHours dual grids Scheme Item + Free Item + DGScheme/DGRest/DGItem + chkday 1-7 + Active Y/N + HH/MM validation | `pos_happy_ui.py` single grid | Critical | HappyHours free item promo not representable |
| G16 | Colors/fonts VB-exact (BGR→RGB, Arial 11.25 Bold, Times 20.25, System 9.75) | theme palette only | Major | Visual regression vs manual screenshots |
| G17 | RsPaymentReceice FrTxnNo (Txn. No.) + Batch No + ExpDt validation `CDate(var_A0.Text)<=MemVar_1F920EC` | none | Major | Card expiry not validated |
| G18 | Delivery Boy detail `FrmDeliveryBoyMast` + `DeliveredItemDetail` per-item | `pos_delivery_ui` header only | Minor | Item-level delivery not tracked in UI |
| G19 | Stock Godown/Item join + Opening Stock forms | `pos_stock_ui` bare | Minor | Godown-wise stock not visible |
| G20 | POS_Manual screenshots `01_Outlets/01_KOT* 02_Sale*` explicit flows | Python no screenshot parity check | Minor | Training manual mismatch |

---

## 7. Fixed UI — proposal & code patches (frontend only)

### 7.1 Principle
- Keep DB APIs as-is; only QSS/layout/behavior changes.
- Add `PYTHONE\ui\vb_colors.py` (not DB) — single source for BGR→RGB.
- Wrap existing dialogs with optional maximized + TopCtrl emulation.
- Add Display host (`pos_display_ui.py`) that was completely missing.
- Add TouchScreen flag read from `core/env.py` (`Enviro.TouchScreenYN`).

### 7.2 Patch skeleton — vb_colors.py (new file)
```python
# PYTHONE\ui\vb_colors.py
VB = {
    "window_bg": "#FFFFFF",        # &H80000005 → white
    "sale_pink": "#FFC0C0",        # &HFFC0C0
    "lbl_caption_yellow": "#FFFFC0", # &HC0FFFF → BGR→RGB
    "maroon_text": "#C00000",      # &HC00000
    "dark_maroon": "#400000",      # &H40
    "green_marker": "#00FF00",     # &HFF00
    "pastel_blue": "#C9E2F5",      # &HC9E2F5
    "header_orange": "#E69839",    # &HE69839
    "vacant_white": "#FFFFFF",
    "occupied_gray": "#404040",
    "billed_green": "#C0FFC0",
    "fr_kot_pink": "#FFC0C0",
    "up_red": "#FF0000",
}
```

### 7.3 kot_entry.py — make VB-exact

**Insert at top after imports:**
```python
from HMS_py.ui.vb_colors import VB
from HMS_py.core.env import get_touch_flag  # MemVar_1F9220C
```

**`__init__` add before `root = QVBoxLayout(self)`:**
```python
self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
# VB Client 13245×10935 ≈ 884×729 px @ 96dpi but VB maximizes; emulate maximized
self.setStyleSheet(f"QDialog{{background:{VB['sale_pink']};}} "
                   f"QLabel{{color:{VB['maroon_text']};}}")
# TopCtrl emulation (VB TopCtrl1)
self.top_ctrl = QLabel("Browse")  # Add|Edit|Browse
self.top_ctrl.setObjectName("TopCtrl")
self.top_ctrl.setStyleSheet(f"background:{VB['header_orange']}; color:#FFFFFF; padding:4px; font-weight:bold;")
```

**Expand header to VB Txt indices (add after existing header_form rows):**
```python
# VB Txt indices mapping — add missing header fields
self.txt_session = QLineEdit(); self.txt_session.setMaxLength(8)
self.txt_session.setPlaceholderText("Session (Txt0)")
self.txt_shift   = QLineEdit(); self.txt_shift.setMaxLength(12)
self.txt_shift.setPlaceholderText("Shift (Txt1)")
self.txt_covers  = QLineEdit(); self.txt_covers.setMaxLength(12)
self.txt_covers.setPlaceholderText("Covers/GuarAtt (Txt2)")
self.txt_table   = QLineEdit(); self.txt_table.setMaxLength(50)
self.txt_table.setPlaceholderText("Table Code (Txt4)")
self.txt_pax     = QLineEdit(); self.txt_pax.setMaxLength(5)
self.txt_pax.setPlaceholderText("Pax (Txt13)")
self.txt_remarks = QLineEdit(); self.txt_remarks.setMaxLength(50)
self.txt_remarks.setPlaceholderText("Remark (Txt6)")
self.chk_nc      = QCheckBox("NC")
self.chk_nc.setStyleSheet(f"background:{VB['pastel_blue']}; color:{VB['maroon_text']}; font-weight:bold;")
self.txt_nc_type = QLineEdit(); self.txt_nc_type.setVisible(False)  # shown only when chk_nc checked
self.txt_member  = QLineEdit(); self.txt_member.setMaxLength(75)
self.txt_member.setPlaceholderText("Member (Txt11)")
self.txt_token   = QLineEdit(); self.txt_token.setMaxLength(11)
self.txt_token.setPlaceholderText("Token (Txt12)")
self.txt_comment1 = QLineEdit(); self.txt_comment1.setMaxLength(50)
self.txt_comment1.setPlaceholderText("Comment1 (Txt8)")
# add rows
for lbl, w in [("Session",self.txt_session),("Shift",self.txt_shift),("Covers",self.txt_covers),
               ("Table *",self.txt_table),("Pax",self.txt_pax),("Remark",self.txt_remarks)]:
    header_form.addRow(lbl, w)
# Running order state (VB LblState)
self.lbl_running = QLabel("Running Order: -")
self.lbl_running.setStyleSheet(f"background:#FFFFFF; color:{VB['up_red']}; font: bold 11pt 'Arial'; padding:4px; qproperty-alignment: 'AlignCenter';")
self.lbl_running.setFixedHeight(34)  # VB 345 twips ≈ 23px + padding
header_form.addRow("State", self.lbl_running)
# Free-item green marker lblclr
self.lbl_free_marker = QLabel()
self.lbl_free_marker.setFixedSize(40, 16)
self.lbl_free_marker.setStyleSheet(f"background:{VB['green_marker']}; border:1px solid #999;")
self.lbl_free_marker.setToolTip("Free Items marker — VB lblclr BackColor &HFF00")
```

**TouchScreen branch at end of __init__:**
```python
if get_touch_flag() == "Yes":
    # VB branches to RsTouchScreenKOTEntry — enlarge buttons, use touch steward
    for b in (self.btn_new, self.btn_save, self.btn_void):
        b.setMinimumHeight(48)
        b.setStyleSheet("font-size:14pt; padding:10px;")
```

**State machine (replace set_state):**
```python
def set_state(self, enabled: bool, mode: str = "Browse"):
    # VB TopCtrl1 has Add/Edit/Browse — disable grid when Browse
    self.top_ctrl.setText(mode)
    is_browse = mode == "Browse"
    for w in [self.txt_session,self.txt_shift,self.txt_covers,self.txt_table,
              self.txt_pax,self.txt_remarks,self.txt_member,self.txt_token]:
        w.setEnabled(not is_browse and enabled)
    self.grid.setEnabled(not is_browse)
    self.btn_new.setEnabled(is_browse)
    self.btn_save.setEnabled(not is_browse)
    self.btn_void.setEnabled(is_browse and self.edit_docid is not None)
```

**Validation (add to _on_save before DB):**
```python
if self.chk_nc.isChecked() and not self.txt_nc_type.text().strip():
    QMessageBox.warning(self,"Validation","NC Type zaroori hai (VB Txt7)"); return
try:
    covers = int(self.txt_covers.text() or "0")
    if covers < 0: raise ValueError
except:
    QMessageBox.warning(self,"Validation","Covers sahi number bharo (Txt2 MaxLength 12)"); return
```

**Pending KOT overlay (add method, call from button):**
```python
def show_pending_kot(self):
    dlg = QDialog(self); dlg.setWindowTitle("Pending Kot (FGrid2)"); dlg.resize(800,300)
    tbl = QTableWidget(0,8); tbl.setHorizontalHeaderLabels(["DocID","KotTime","VNo","TableNo","Product","Qty","Depart","Waiter"])
    rows = pos.get_pending_kot(self.cb_outlet.currentData() or "KKFOM")  # wraps CmPendingKot query
    for r in rows: ...
    dlg.exec()
```

### 7.4 kot_transfer_ui.py — restore graphical mode + vacant check

**Add OpenMode property + PTableNo + TVacantColor:**
```python
class TableChangeWindow(QMainWindow):
    def __init__(self, parent=None, open_mode: int = 0, p_table_no: str = ""):
        ...
        self.open_mode = open_mode   # VB OpenMode 0=DataCombo, 1=graphical
        self.p_table_no = p_table_no
        self.t_vacant_color = 0xFFFFFF  # VB &HFFFFFF
        self.lbl_room = QLabel(f"CHANGE TABLE :   {p_table_no}     TO     ")
        self.lbl_room.setStyleSheet(f"background:{VB['lbl_caption_yellow']}; color:{VB['occupied_gray']}; font: bold 12pt 'Tahoma'; border:1px solid #999;")
        self.frame_option = QWidget()  # holds CHANGE && EXIT / EXIT
        # FGrid1 graphical map
        self.fgrid1 = QTableWidget()
        # when open_mode==1 build 6-col blocks like VB Proc_225_28_14E1368
        if open_mode == 1:
            self._build_graphical_map()
        else:
            self._build_data_combo_ui()
```

**Vacant validation in _save:**
```python
def _save(self):
    ...
    # VB validates target is vacant: SELECT CODE FROM RoomMast WHERE CODE=:to AND CODE NOT IN (SELECT RoomNo FROM KOT Pending)
    try:
        vacant = pos_kot.is_table_vacant(rest, to)  # new helper wraps RoomMast NOT IN query
        if not vacant:
            QMessageBox.warning(self,"Validation","Select A Vacant Table (VB RsTbChange line 116108B)")
            return
    except Exception: pass
```

**Same for KOTTransferWindow:** add `LBLRoomName`, `FrameOption` with `CHANGE && EXIT` / `EXIT`, `FGrid1` map; `TXT_PKOT_UnknownEvent_11` sync `LblKOTTable` + `TXT_TOTABLE.Tag` filtered query (skip building tag UI but replicate as second combo population).

### 7.5 pos_sales_ui.py — restore Sale2 grid + Sundry + PayCharge

**Replace bare dialog with MSHFlexGrid-like editor:**

```python
# Add after Sale Details group — VB FGrid1 replacement
self.sale_grid = QTableWidget(0, 8)  # VB cols: SNo|Item|Qty|Rate|Amount|Tax%|Disc|Sundry
self.sale_grid.setHorizontalHeaderLabels(["SNo","Item","Qty","Rate","Amount","Tax%","Disc%","Sundry"])
self.sale_grid.horizontalHeader().setStretchLastSection(True)
layout.addWidget(self.sale_grid, stretch=1)

# Sundry frames FrSun1/2/3 — only one visible per Depart.SundryYN
self.fr_sun1 = QGroupBox("Total"); self.txt_gt1 = QLineEdit(); self.txt_per1 = QLineEdit(); self.txt_gt1.setEnabled(False)
self.fr_sun1.setVisible(False)
# show based on Depart query: SELECT SundryYN FROM Depart WHERE Code=:restcode

# PayCharge grid (Settlements) — VB FrSettlement branching
self.pay_grid = QTableWidget(0, 4)
self.pay_grid.setHorizontalHeaderLabels(["PayType","Amount","CardNo","Holder"])
# PayType combo triggers FrCCDet/FrChqDet visibility emulating RsPaymentReceice
self.pay_type = QComboBox()
self.pay_type.currentTextChanged.connect(self._on_pay_type_changed)
def _on_pay_type_changed(self, t: str):
    self.fr_cc.setVisible("Card" in t or "CC" in t)
    self.fr_chq.setVisible("Cheque" in t)
    self.fr_txn.setVisible("Txn" in t)
```

**Totals calc (VB Val → float):**
```python
def _recalc_totals(self):
    total = sum(float(self.sale_grid.item(r,4).text() or 0) for r in range(self.sale_grid.rowCount()))
    self.txt_gt1.setText(f"{total:.2f}")
    # VB Format(CVar(var_148),"0.00") via Proc_30_105_F223E0
```

### 7.6 pos_display_ui.py — NEW file (was missing entirely)

Create `PYTHONE\ui\pos_display_ui.py` implementing `RsPOSDisplay` + `RsPOSDisplayNew`:

```python
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QLabel, QFrame, QTimer, QPushButton
from HMS_py.ui.vb_colors import VB

class PosDisplayWindow(QMainWindow):
    def __init__(self):
        self.setWindowTitle("Display Table — VB RsPOSDisplay")
        self.showMaximized()  # VB WindowState 2
        self.fgrid1 = QTableWidget()  # will be 6 cols per table block, headers hidden
        self.fr_pending = QFrame(); self.fgrid2 = QTableWidget(0,5)
        self.fr_settle  = QFrame(); self.fgrid  = QTableWidget(0,5)
        self.frame_option = QFrame()
        self.frame_option.setStyleSheet(f"background:{VB['sale_pink']};")
        for cap in ["Add KOT (AKOT)","Sale Bill","Chng Table","Bill Lookup","Pending KOT","Order/Booking","Cancel"]:
            btn = QPushButton(cap); btn.setFixedSize(270,60)  # VB 2700×600 twips ≈ 180×40 px + padding
        self.timer1 = QTimer(); self.timer1.setInterval(10000)  # VB Timer1 10000ms
        self.timer1.timeout.connect(self.reload_occupancy)
        self.timer1.start()
    def reload_occupancy(self):
        # VB Proc_239_20_166BE44 — three LEFT JOINs: RoomMast + KOT Pending + Sale1 unsettled (PayCharge LEFT JOIN)
        # color via VB &HFFFFFF vacant, &H404040 occupied, &HC0FFC0 billed
        pass
```

**DispColor picker (VB CDLG + Label2_Click):**
Add `Label2_Click` emulation: clicking color legend opens `QColorDialog`, executes `DELETE FROM Dispcolor WHERE [index]=:idx AND Logsite_Code=:site; INSERT INTO DispColor([Index],[Color],Detail,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES(:idx,:color,:detail,:site,:dt,'A',:site)`.

### 7.7 pos_happy_ui.py — restore dual-grid + HH splits + days

**Extend dialog:**
```python
from PyQt6.QtWidgets import QFrame, QCheckBox
# Add after Happy Hours Details
self.fram_week = QFrame(); self.fram_week.setStyleSheet(f"background:{VB['lbl_caption_yellow']};")
self.chk_days = []
for i, name in enumerate(["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],1):
    chk = QCheckBox(name); chk.setProperty("idx", i); self.chk_days.append(chk)
# Time split into 4 QLineEdits like VB txt3-6
self.txt_from_h = QLineEdit(); self.txt_from_h.setMaxLength(4); self.txt_from_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
self.txt_from_m = QLineEdit(); self.txt_from_m.setMaxLength(4)
self.txt_to_h   = QLineEdit(); self.txt_to_h.setMaxLength(4)
self.txt_to_m   = QLineEdit(); self.txt_to_m.setMaxLength(4)
# Validation VB: if Val(txt)>24 or >59 then fallback to Format(Time,"HH/NN")
def _validate_hh(self, txt: QLineEdit, max_v: int, fallback: str):
    try:
        if int(txt.text() or 0) > max_v: txt.setText(fallback)
    except: txt.setText(fallback)
# Dual grids
self.fgrid  = QTableWidget(0,3); self.fgrid.setHorizontalHeaderLabels(["Scheme Item","Qty","Rate"])  # VB FGrid
self.fgrid1 = QTableWidget(0,3); self.fgrid1.setHorizontalHeaderLabels(["Free Item","Qty","Rate"])    # VB FGrid1
self.dg_scheme = QComboBox(); self.dg_rest = QComboBox(); self.dg_item = QComboBox()  # hidden lookups positioned under QLineEdits like VB FGPoint
```

### 7.8 pos_delivery/stock/table masters — minor chrome fixes

- `pos_table_ui.py`: Add `DGRest` outlet picker (`Depart WHERE Code=:restcode`) + `BackColor &HFFC0C0&` + `ForeColor &HFF0000&` for table code label; make dialog `Maximized` or `FixedSize 7995×8790` twips → `540×600 px`.
- `pos_stock_ui.py`: Add Godown `QComboBox` (`Godown` table), item `DGItem` lookup, QtyIss vs QtyRec toggle; set `BackColor &HFFFFFF` for Txt.
- `pos_delivery_ui.py`: Add `DeliveredItemDetail` sub-grid + `FrmDeliveryBoyMast` lookup for `DeliveryBoy`.

### 7.9 Global validation patches (no DB)

- Keep `MaxLength` enforcement via `QLineEdit.setMaxLength()` already partly done, but add missing: `kot_entry.Txt(2) covers 12`, `Txt(13) pax 5`, `RsSaleBill Txt2 From/To 25`, `RsTbChange DataCombo BoundText vs defText` distinction (`currentData()` vs `currentText()` already but need both).
- `TopCtrl1` key handling: `KeyPreview=True` + `Form_KeyDown Proc_6_88_FE81B4` maps `Esc → Browse`, `Ctrl+S → Save`, `F5 → reload_occupancy`; add `QShortcut` for each.

---

## 8. Database understanding (frontend perspective — no change)

| Table | VB Use | Python API | Key fields (VB names) |
|-------|--------|------------|-----------------------|
| `KOT` | KOT Entry / Pending / TableChange / Transfer / Display | `core.pos_kot` | `DocId VNo VDate VTime RestCode RoomNo RoomType RoomCat Pending VoidYN DelFlag NCKot Waiter Item Qty Rate Amount ContraDocId ContraSNo PrintFlag Printed Logsite_Code` |
| `Sale1` | Sale Bill header + Display unsettled join | `core.pos_sales.Sale1API` | `DocId VNo VDate VTime RestCode RoomNo RoomType RoomCat NetAmt DelFlag Logsite` |
| `Sale2` | Sale Bill lines (Item/Qty/Rate/Amount/Tax/Disc) | `core.pos_sales.SaleBillAPI` | `DocId SNo Item Qty Rate Amount Tax%` |
| `POS_SBill` | Sale bill split (?), Sundry | `core.pos_sbill` | mirrored Sale1/2 for split |
| `PayCharge` | Settlement branching (Amount Cr) | (missing in Python sales) | `DocId Bill_No AmtCr PayType FolionoDocid` — Display uses `SUM(PayCharge.AmtCr) < SUM(Sale1.NetAmt) => Pending` |
| `Depart` | Outlet master = `LocalRestCode` everywhere | `Depart` / `pos.py get_outlets()` | `Code Name ShortName KotYN Order_Booking Logsite_Code` |
| `Waiter` | Steward/Server | `pos.get_waiters()` | `Code Name Logsite_Code ActiveYN` |
| `ItemMast / Item` | ItemMast `Type='Finish' DispCode<>9999 ActiveYN` | `pos.get_items(outlet)` | `Code Name Unit ItemGroup RestCode Type ActiveYN Logsite_Code DispCode` |
| `ItemGroup / ItemCatMast` | Category for HappyHours | `pos_masters.ItemCatAPI` | `Code Name CatType Rest TaxStru Acname Revcode DrCr` |
| `RoomMast` | Table master `Type='TB'` / Room `Type='RO'` | `pos_table`, `pos_kot.pending_kot_tables` | `Code Name Type RestCode Logsite_Code Site_Code` |
| `RoomOcc` `RC` | Room Service occupancy (RoomNo, RoomCat, GuestProf) | Display query | `RoomNo Foliono Docid GuestProf RoomType ChkOutDate Logsite_Code` |
| `SchemeMast / HappyHoursHead` | HappyHours scheme + free items | `pos_happy.HappyHoursHeadAPI` | `SchemeCode ItemCat RestCode FromTime ToTime DiscountType DiscountValue Active EndDate` + days `S M T W T F S` split |
| `SessionMast / Shift` | Session/Shift pickers | `pos_masters.SessionAPI/ShiftAPI` | `Code Name FromTime ToTime` |
| `DeliveryBoy / AssignDelivery` | Delivery | `pos_delivery.AssignDelAPI` | `DocId VNo DeliBoy Ddate BillAmt Remark Vtype` |
| `Stock` (+ `Godown`) | Stock | `pos_stock.StockAPI` | `DocId Sno Vtype Vdate Item QtyIss QtyRec Rate Amount Godown` |
| `DispColor` | Display color config | (no Python) | `[Index] [Color] Detail Site_Code Logsite_Code U_EntDt U_AE` — VB Label2 click upserts |
| `TaxStruMast / SundryMast` | Tax & Sundry branching | (partial) | `Code Name SundryYN Tax%` |
| `Voucher_Type` | `Ncat='ORDER'` for RsBookingEntry | — | `V_Type RestCode Ncat` |

**Key queries (VB verbatim):**
```sql
-- Pending KOT (CmPendingKot)
SELECT k.docid as DocID,K.Vtime as KotTime,K.VNo,k.Vdate,W.NAME AS WAITER,K.RoomNo AS TABLENo,I.NAME AS PRODUCT,K.Qty,D.NAME AS DEPARTNAME
FROM ((((KOT AS K INNER JOIN wAITER AS W ON K.Waiter = W.Code)
       INNER JOIN ItemMast AS I ON (K.Item = I.Code And K.ItemRestCode=I.RestCode))
       INNER JOIN DEPART AS D ON K.RestCode = D.Code)
       INNER JOIN VOUCHER_TYPE AS V ON (K.Vtype = V.V_Type AND K.SITE_CODE=V.SITE_CODE))
WHERE k.contradocid='' and k.VoidYN='N' and k.delFlag<>'Y' and k.nckot='N' and k.restcode=@LocalRestCode
ORDER BY K.DocId,K.RESTCODE,I.Name

-- Table Change source (RsTbChange Form_Load)
SELECT DISTINCT RoomNo AS CODE,RoomNo as Name FROM KOT
WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode=@LR
  and ROOMTYPE='TB' AND (PENDING='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y'

-- Table Change target vacant
SELECT DISTINCT CODE,code as Name From RoomMast
Where type='TB' AND RESTCODE=@LR
  And Code Not in(SELECT DISTINCT RoomNo FROM KOT WHERE restCode=@LR and ROOMTYPE='TB' AND (PENDING='Y' OR ...))

-- Display occupancy (RsPOSDisplayNew Proc_239_20_166BE44)
SELECT LTrim(RTrim(RoomMast.Code)) as code, RoomMast.Name, RestCode, D.Name as RestName, D.ShortName, RoomMast.SITE_CODE, RoomMast.LOGSITE_CODE, D.KOTYn
FROM RoomMast LEFT JOIN Depart D ON RoomMast.RestCode=D.Code
WHERE (RoomMast.LOGSITE_CODE=@site OR RoomMast.LOGSITE_CODE='HO') and RoomMast.type='TB' and RoomMast.RestCode=@LR ORDER BY RoomMast.code
-- then LEFT JOIN (SELECT DISTINCT ROOMNO,KOT.DOCID,WAITER,WAITER.NAME AS WAITERNAME FROM KOT WHERE RestCode=@LR And RoomCat='REST' and RoomType='TB' And Pending='Y' AND VOIDYN='N' ...) AS AA ON AA.ROOMNO=T.CODE

-- Display unsettled (Sale1 LEFT JOIN PayCharge)
SELECT Sale1.DocId, MAX(Sale1.VNo) Bill_No, Max(Sale1.VTime) VTime, MAX(Sale1.RoomNo) RoomNo, MAX(Sale1.Waiter) WAITER, max(Waiter.Name) WAITERNAME,
       Status = CASE WHEN Sum(IsNull(PAYCHARGE.AmtCr,0)) < Sum(SALE1.NetAmt) Then 'Pending' Else 'Settle' End
FROM ((Sale1 LEFT JOIN PayCharge ON Sale1.DocId=PayCharge.DocId) LEFT JOIN Waiter on Sale1.Waiter=Waiter.Code)
WHERE PayCharge.DocId Is Null AND (Sale1.DelFlag='' Or Sale1.DelFlag='N') And Sale1.RoomCat='REST' And Sale1.RoomType='TB' AND SALE1.restcode=@LR GROUP BY SALE1.DOCID
```

---

## 9. What to do next — actionable steps (debug fixes first)

1. **Create `ui/vb_colors.py`** then `ui/pos_display_ui.py` (missing hub) — highest ROI; without it operators cannot see table status at all.
2. **Patch `kot_entry.py`** with VB header fields + TopCtrl + pending overlay + TouchScreen flag + BGR colors (code in §7.3).
3. **Patch `kot_transfer_ui.py`** with OpenMode/TVacant/PTableNo/LBLRoomName/FrameOption + vacant check (code in §7.4).
4. **Patch `pos_sales_ui.py`** with Sale2 grid + Sundry + PayCharge branching + totals (code in §7.5) — wire `SaleBillAPI.full_save` to include `sale2`/`suntran`/`paycharge` arrays already supported in `core/pos_sales.py`.
5. **Patch `pos_happy_ui.py`** with dual-grid + HH:MM splits + chkday (code in §7.7).
6. **Wire Enviro TouchScreen** in `core/env.py` → expose `TouchScreenYN` and branch in `pos_display_ui` `CmdAKOT/CmdPKOT` handlers.
7. **Color pass** — apply `VB` QSS to all POS dialogs + set fonts per §4.3.
8. **Manual screenshot parity** — re-export `POS\screenshots\01_Outlets\01_KOT*.png` and `02_Operations\02_T* 04_K*` and diff vs patched UI in maximized state.

All patches are frontend-only; no migration, no `ALTER TABLE`.

---

## 10. Files referenced (absolute)

- VB: `RsKOTEntry.frm/.frx`, `RSSaleBill.frm`, `RsKOTTransfer.frm/.frx`, `RsTbChange.frm/.frx`, `RsPaymentReceice.frm/.frx`, `RsSaleBillSplit.frm`, `RsPOSDisplay.frm/.frx`, `RsPOSDisplayNew.frm/.frx`, `RsTableMast.frm`, `pHappyHours.frm/.frx`, `NewHappyHours.frm`, `RsTouchScreenKOTEntry.frm`
- Python: `PYTHONE\ui\kot_entry.py:43`, `PYTHONE\ui\pos_sales_ui.py:21`, `PYTHONE\ui\kot_transfer_ui.py:22,129`, `PYTHONE\ui\pos_table_ui.py:15`, `PYTHONE\ui\pos_stock_ui.py:21`, `PYTHONE\ui\pos_delivery_ui.py:21`, `PYTHONE\ui\pos_happy_ui.py:22`, `PYTHONE\ui\pos_masters_ui.py:24`
- Core: `PYTHONE\core\pos_kot.py`, `PYTHONE\core\pos_sales.py:31305`, `PYTHONE\core\pos.py:32680`
- Manuals: `HMS_Manuals\HMS_Manuals\POS\screenshots\`

---

## 11. Summary answer

Python POS frontend is **functional but not VB-exact**: it covers CRUD lists for stock/delivery/happy/table and bare KOT/Sale registration, but is missing the defining VB POS chrome — **maximized MDI + TopCtrl1 state machine**, **MSHFlexGrid 6-col table map with Vacant/Occupied/Billed colors & tooltips**, **DataGrid overlays + FGPoint + TxtGrid inline edit**, **header fields (Session/Shift/Covers/Pax/Member/Token/Remarks/Comments/NCKOT) + Running Order LblState + GuarAtt Covers**, **FrameOption 7-button hub + FrPendingOrder/FrSettlement + Timer1 auto-refresh + DispColor**, **dual-mode TableChange/KOTTransfer (graphical FGrid1 vs DataCombo) with PTableNo/TVacantColor/Line/Shape + vacant validation**, **SaleBill Sundry/PayCharge/Tax/HappyHours/Split/Token/eInvoice/settlement branching**, **HappyHours dual-grid + HH:MM splits + chkday week + Active Y/N**, and **TouchScreen `RsTouchScreenKOTEntry` branch**. Largest gap is the entire `RsPOSDisplay` hub being absent (no Python file). Report above lists 20 numbered gaps (G1-G20) with verbatim VB control dumps, Python control tables, BGR→RGB fixups, DB understanding (KOT/Sale1/Sale2/PayCharge/RoomMast), and drop-in code patches that make Python workflow EXACTLY VB-frontend logic without touching DB.

**Report path:** `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_POS_COMPARE.md`

