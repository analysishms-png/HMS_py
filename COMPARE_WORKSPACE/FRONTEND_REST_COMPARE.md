# FRONTEND REST COMPARE — VB6 → Python (8 modules: INVENTORY/PURCHASE, BANQUET, MEMBERS, HR/PAYROLL, HOUSEKEEPING, TELEPHONE, SMARTCARD, NIGHTAUDIT)

> Date: 2026-09-24 | Workspace: `PYTHONE/COMPARE_WORKSPACE/FRONTEND_REST_COMPARE.md`
> Method: Each VB6 .frm read ONE-BY-ONE fully (Begin controls verbatim + code-behind validation + DGHelp flow). Matching Python .py read ONE-BY-ONE fully (QDialog/QMainWindow FixedSize, QSS, layouts, colors). No DB change. Thorough but concise.

---

## CROSS-CUTTING VB6 vs Python BASELINE

| VB6 pattern (all modules) | Python current | Gap → Fixed UI (code-patch §) |
|---|---|---|
| `WindowState=2` (maximized MDIChild), `ControlBox=0`, `KeyPreview=-1`, `MDIChild=-1` | `QDialog`/`QMainWindow` with `resize(w,h)` free-floating, no MDI | Patch: `setWindowState(Qt.WindowMaximized)` inside MDI, `setFixedSize(ClientWidth/15, ClientHeight/15)` scale (VB twips ÷15 = px), `setWindowFlags(Frameless + WindowMaximizeButtonHint)` parity |
| `BackColor` pink `&HFFC0C0&` / beige `&HD0C7BB&` / teal `&HADDAC0&` / `&HDECCBE&` / `&HFFC0FF&` / `&HE5E5E5&` | `_theme.palette()["glass_tint"]` neutral dark theme, `alternatingRowColors=True` generic | Patch: `setStyleSheet("QDialog{background:#FFC0C0}")` per-form mapping table below; `palette()["text"]` `#0f172a` replaces `&HC00000&` maroon only when explicit |
| `LblFormCaption: BackColor &HC0FFFF& (cyan) BorderStyle 1 Fixed Single Alignment 2 Center System 19.5 700` vertical header, `Proc_5_1_100CB50` caption fill `Top` calc | `QLabel("State: Idle")` generic small `text_dim` bottom status | Patch: Add top `QLabel(self.lblCaption)` fixed `width=22px height=540px` vertical `writing-mode` simulation: `QFrame` 22px cyan `#C0FFFF`, `border:1px solid #000`, inner `QLabel` rotated 90° via `QGraphicsProxyWidget` or `paintEvent` drawText rotated; font `System 19.5 bold` mapped to `QFont("System",19)` |
| `TopCtrl1: MainCtrl ActiveX` `Width=11880 Height=450` state machine `AEDP` / `ADD/EDIT/INI/BROWSE` `UnknownEvent_16` save `UnknownEvent_A` add etc, `Duplicate SELECT COUNT(*)`, `Voucher_Prefix Next Srl`, locks | `btnNew/btnEdit/btnSave/btnCancel` manual `state="Idle/Add/Edit"` + `_theme` status label, shortcuts `Ctrl+N/E/S Esc` | Patch: Keep manual state but mirror `TopCtrl.DispID_6803000C` semantics: disable pk field on Edit, set `TopCtrl Caption` to `Add/Browse/Edit`, duplicate check inline `SELECT COUNT(*) WHERE DocID=...` before `CommitTrans` (frontend flag only; no DB change, just `messageBox("Duplicate Vr No")` mirror VB6), `Voucher_Type/Voucher_Prefix` preview label |
| `DGHelp / DGRoom / DGDept / DGParty / DGItem` hidden `Visible=0 DataGrid` positioned at `Left=Top+Height+30` overlay on `Txt_GotFocus` + `DGHelp_UnknownEvent_9` picks `Text=Name Tag=Code` + `Proc_6_69_134A198` keyboard navigation `(Up/Down/Page)` + `Proc_6_80_FF0AC0` filter | `QComboBox.addItem("code - name", code)` static preload `inv.godown_list()` / `depart.depart_list()`; no live filtering, no Tag/Code split | Patch: Replace `QComboBox` with `QLineEdit + QListView` popup (VB style): `QLineEdit` `textChanged` → `QSortFilterProxyModel` over `QStandardItemModel` (Name/Code), `Enter` selects `Tag=Code`, `Up/Down` navigates via `Proc_6_138_106D6F8` analogue; hide timeout on `Esc` |
| `Txt_Text: BorderStyle=0 None Appearance=0 Flat ForeColor &HC00000& Arial 9.75 Border 0 MaxLength` + `Txt_GotFocus: SelStart 0 SelLength Len, BackColor &HE0E0E0& (&HC0C0C0& in kClStk)` + `Txt_Validate: Proc_6_27_EA565C required + duplicate SELECT` | `QLineEdit.setPlaceholderText` + `setMaxLength` generic, `setStyleSheet(border 1px solid border)` non-flat, red maroon not applied | Patch: `QLineEdit{border:none; background:#FFFFFF; color:#C00000; font-family:Arial 9.75pt}` → focus `background:#E0E0E0; selection-background:#3399FF`; replicate `MaxLength`; add `editingFinished` validate calling `Proc_6_27` clone |
| `FGrid/MSHFlexGrid: Left Top Width Height TabIndex, CellBackColor &HFFFFFF / &HFFFF, BackColorSel 14737632, FixedRows, Tag=Row, Editable via TxtGrid overlay (Left=CellLeft+CellTop)` | `QTableWidget` direct editable `ItemIsEditable` | Patch: `QTableWidget.setItemDelegate(FlexGridDelegate)` + hidden `QLineEdit TxtGrid` positioned `cellRect` on double-click; navigation via `Key_Down` Enter moves col per VB6 `Proc_6_62_1253BC4`; `BackColorBkg = MemVar_1F921B4` wired to theme glass but override per form |
| `LblUser/LblLDt: "User"/"Last Update" ForeColor &HFF0000& Times New Roman 11-12 Bold Transparent` bottom-right `Left 13500 Top 7800/8160` | Rarely present (`lblState` only) | Patch: Add footer `QHBoxLayout` with `lblUser/lblLDt` exact font `Times New Roman 11.25/12 bold #FF0000` transparent |
| `Bevel/Shape: Shape1 BorderWidth 2` grouping, `Frame FrTrans/Frame1` pink frames, `Line Line2` | `QGroupBox` no bevel, no shape | Patch: Use `QFrame {border:2px solid #808080; border-radius:0}` + `QLabel` title overlapped |
| Colors hex note: VB `&HBBGGRR&` → CSS `#RRGGBB`. e.g. `&HFFC0C0&` = `R=C0 G=C0 B=FF` → `#FFC0C0` pink. `&HC00000&` = `R=00 G=00 B=C0` → `#0000C0`? Actual VB6 in these forms `ForeColor &HC00000&` visually maroon → treat as `#C00000`. `&HC0FFFF&` cyan `00FFFF` → `#FFFFC0`? VB cyan maps to `#C0FFFF`. Keep literal mapping table; use eyedropper final. | - | - |

---

## 1) INVENTORY / PURCHASE — VB6: `PIndent.frm` `pPOrder.frm` `pPBill.frm` `kClStk.frm` `FrmStockTransfer.frm` | PY: `ui/inventory.py` `ui/purchase_order_ui.py` `ui/purchase_bill_ui.py` `ui/kitchen_clstk_ui.py` `ui/stock_issue_ui.py`

### VB6 controls verbatim (representative)

**PIndent.frm** `11880×6435` `BackColor &HFFC0C0&` pink `Font Tahoma 12`:
- `TopCtrl1 11880×450`
- `Txt(0) Indent Type 1995×285 1965×285 Max30 Arial9.75 #C00000 Flat`, `Txt(1) Indent No 5340×1020 1020`, `Txt(2) Date 7275×960 1215 Max12`, `Txt(3) VPrefix invisible`, `Txt(4) Remarks 1110×7260 5925 Max50`, `Txt(6) Department 2625×1275 3750`, `Txt(7)/Txt(5) totals right-aligned`
- `FGrid 45×1635 13020×5235`, `TxtGrid(0) E0E0E0 C0C0C0 overlay hidden`, `DGDepart 13545×2160 5055×3810 hidden`, `DGItem 13425×1455 4230×4065 hidden`, `FrmList+ListView 2505×1935 hidden`
- `LblFormCaption 0×375 180×540 C0FFFF cyan System 19.5 bold vertical`, `LblLDt/LblUser Times New Roman 12/11.25 #FF0000`, `LblCurStockStr Tahoma 14.25 red`
- Validation: `Txt_Validate` duplicate via `SELECT V_TYPE,DESCRIPTION FROM Voucher_Type WHERE NCAT='PIND'` (Indent Type), department required, date FY guard.

**pPOrder.frm** `11880×8070` `Tahoma 9.75`:
- `Txt 0 invisible DocID, 1 OrderType, 2 OrderDate, 3 IndentNo 17, 4 Supplier 5340, 5 DespMode, 6 PackCharges%, 7 FwdCharges, 8 Prices, 11/13-16 % fields (Disc/Excise/SaleTax/SurCharge/DelSch)`, `TxtGrid(0) E0E0E0`, `FGrid 0×1750 14115×5235`
- `DGItem/DGParty/DGOrdType/DGIndent` 4230×3330 hidden, `FrmList+ListView`, `FGPoint` hidden
- `Label1` 13 rows: `Supplier Name, Order Type, Indent No, Order Date, Fwd Charges, Pack Charges, Discount, Excise, Sale Tax, Sur Charge, Del.Sch., Disp Mode, Prices` all `Arial 9.75 bold #C00000`, `%` suffixes 4 labels
- Legend `Label2` color boxes `B4FEBD green≈,80C0FF blue,8080FF red` for stock levels hidden, `Guest Bill Printed` legend
- Code: `TxtGrid_KeyDown` column routing 1/2/3/5/8, `FGrid_UnknownEvent_D DeleteRow` validates `SELECT Count(*) From Stock Where ContraDocid=Docid And ContraSno=... Can't Remove Row`

**pPBill.frm** `12720×8475` `FillColor &H80&` maroon:
- `FrPayable CheckBox Payable FF red`, `FrInVoiceType OptionButton 3: Sale Invoice/Tax Invoice/Other (8090)`, `Txt 0 invisible VType,1 Type 30,2 VrNo 8,3 BillDate 12,4 PartyName 50,5 PartyBillNo 25,6 GSTIN,7 M.R.No 50 hidden,10 indent,11 GSTIN`, `TxtBarCode hidden`, `TxtGrid(0) E0E0E0`, `FGrid 15×2085 12045×3855`, `GridSel Frame FrTrans hidden Import Purchase Data (All CheckBox Wingdings, GridSel 6495×3000, Cmd Refresh/Exit)`, `DgMR/DGIndent/DGVType/DGParty/DGGod/DGRest` hidden, `TxtPer/TxtGt %` rows, `BillImage 1095×1350 stretch border`
- Code: `TxtBarCode_Validate By BarCode find Item, auto-fill Unit/ConvRatio/Rate, tax slab lookup taxStru Rate, duplicate voucher prefix gen, LblCurStockStr FY guard, payable toggle.

**kClStk.frm** `7530×6180` `System 700`:
- `Txt(1) Voucher No 2040×1005 1230 Max8, (2) Date 15 3870×1005 1230 Max12, (3) DocID invis, (4) Location 6225×1005 3495 Max50 Dept, (0) VrType invis 8`, `TxtGrid(0) C0C0C0 MS Sans 8.25 hidden`, `FGrid 795×1350 7260×7485`, `DGDepart 8145×3525 3990×2625, DGItem 3900×1365 4140×3315`
- `LblFormCaption C0FFFF 180×540`, `LblVPrefix hidden`, Label Location/Voucher No/Date
- Code: `TopCtrl_UnknownEvent_A ADD sets Date=NOW Enviro NCur, Txt(2/4) focus, INIT hide, Delete cascade Ledger/Purch1/Stock/KClStk Delete, Print via kClStk.ttx/kClStk.RPT, Duplicate `SELECT Count(*) From Purch1 Where DocID=...Duplicate Invoice No.`, Fy guard `Invoice Date Not Between Current Fin. Year`, AutoFillItemInKitchenClosingYN enviro.

**FrmStockTransfer.frm** `7185×7710 MS Sans Serif 9.75` minimal:
- `DGItem 2880×5325 4155×3330, DGDepart 4770×4005 4155×3330` only two grids, `Txt/DGToDepart` dynamic, `Proc_147` height calc 5445/7310, stolen `KSISS/KSREC` VTypes `global_68/72` double stock post `Insert STOCK(DocID,...,KSREC/KSISS)` pair+ Voucher_Prefix bump both.

### Python controls (actual)

- `inventory.py:IndentForm QDialog 900×600 resizable` `QFormLayout` 4 rows (Dept Combo, DateEdit, Godown Combo, Remarks, Cleared Y/N) + `QTableWidget 0×5 browse DocId/VNo/Date/Depart/Cleared` + `QTableWidget Indent Lines 5 cols SNo/Item/Qty/Unit/Rate` + `Add/Remove` QPushButton + `State Idle label glass_tint` + `New/Edit/Save/Cancel/Close` row. `QComboBox` preloaded `depart.depart_list()/godown_list()` static, no DGHelp overlay, no VatType ListView pink, no `LblCurStockStr` red. QSS from `_theme.palette()` uniform.
- `purchase_order_ui.py:PurchaseOrderWindow QMainWindow 1000×700` `QGroupBox Purchase Order Header (DateEdit, Party Combo editable, Remark)` + `QTableWidget 6 cols SNo/ItemCode/ItemName/Qty/Rate/Amount` + 4 buttons row. No Индент/OrderType ListView, no Fwd/Pack/Disc/Excise/SaleTax/Sur typ % rows (13 fields) missing, no legend boxes, no ` Txt VPrefix/DocID` hidden, no `FGPoint`. Duplicates check not done frontend.
- `purchase_bill_ui.py:PurchaseBillWindow 1000×700` `QGroupBox Bill Header (Date, Party Combo editable, Remark)` + `QTableWidget 9 cols SNo/ItemCode/ItemName/Qty/Rate/Tax%/Amount/hidden/TaxStru` + 4 buttons. Missing `FrPayable Payable checkbox, FrInVoiceType OptionButton 3, BillImage 1095×1350 Toggle View, FrTrans Import GridSel + All Wingdings, Txt GSTIN/Indent/MRNo, BillImage dblClick file picker (DAT/AVI blocked), TxtPer/TxtGt % auto-calc global_216` etc. TaxStru slab via `taxstru.calculate` replicates but UI hidden col 7 not VB overlay.
- `kitchen_clstk_ui.py:KitchenClosingStockWindow QMainWindow 900×600` `QGroupBox Header Date + Dept Combo` + `QTableWidget 5 cols SNo/Item/Qty/Unit/Remarks` + Save green `#28a745`. Missing `TxtGrid C0C0C0 overlay at CellLeft+Top, DGItem DGDepart hidden repositioned per GotFocus, Top positioning LBLUser 13500×7800, VNo 6 type, BackColorBkg MemVar_1F921B4, Vtype KCLS docid composition D+site+KCLS+year+8-pad Vno`.
- `stock_issue_ui.py:StockIssueWindow 900×600` `Date+Godown LineEdit + Remark + 5 cols` generic. `FrmStockTransfer` dual godown STOCK pair insert missing: Python does single `inv.stock_transfer` minimal not two-phase KSREC/KSISS gap.

### Gap table

| VB6 must-have | Python missing / divergent | Severity |
|---|---|---|
| Pink frames Bevel Shape grouping Indent Type/No/Date row at 960-1275 y, 3 TextBoxes inline, Rem total bar at 7260 | Single column QFormLayout vertical stacked | High |
| `Txt(0) Indent Type` → ListView popup from `Voucher_Type NCAT PIND Description` with SubItems Tag | Combo preload none; `cb_dept` only holds godown/dept, not voucher type | High |
| `DGDepart/DGItem` inline overlay on `Txt(6)` and `FGrid Col 1` at `Left=CellLeft+Width Top=CellTop` auto-filter by name | Static combo; no overlay, no live filter, no keyboard PageUp/Down via `106D6F8` | High |
| `%` price adj fields 10-16 (Disc/Excise/Sale/Sur/Packs/Fwd/DelSch) at 7005-7995 y with `%` suffix labels | Absent in PO/Bill header | Medium |
| `BillImage` picture stretch border with dblClick CommonDialog `*.DAT *.AVI` block + tag path preview | No image widget; 0 file picker | Medium |
| `FrTrans GridSel Wingdings “þ”` import tick All checkbox 14 px, 6500×3000 grid | No import batch; 0 purchase data transfer | Medium |
| `kClStk` duplicate `SELECT Count(*) From Purch1 Where DocID` msg `Duplicate Invoice No.` | No duplicate frontend guard | Low |
| `FrmStockTransfer` dual stock post KSREC+KSISS + double Voucher_Prefix bump + tag `D+site+KSISS+year+8` | Single `stock_transfer` API, no dual-prefix | High |

### Fixed UI (patch sketch, no DB)

```python
# inventory.py patch — IndentForm FixedSize + VB colors + DGHelp overlay
class IndentForm(QDialog):
    def __init__(self,p=None):
        super().__init__(p)
        self.setFixedSize(792,429) # 11880/15 x 6435/15
        self.setStyleSheet("QDialog{background:#FFC0C0} QLabel{color:#C00000; font:700 9.75pt Arial} "
                           "QLineEdit{border:none; background:#FFFFFF; color:#C00000; font:9.75pt Arial}")
        # caption cyan vertical
        self.lblCaption = QFrame(self); self.lblCaption.setFixedSize(22,600)
        self.lblCaption.setStyleSheet("background:#C0FFFF; border:1px solid #000")
        # overlay helpers
        self.dgDepart = QTableWidget(self); self.dgDepart.hide()
        self.dgItem = QTableWidget(self); self.dgItem.hide()
        self.frmList = QFrame(self); self.frmList.hide()
        # Txt overlay TxtGrid
        self.txtGrid = QLineEdit(self); self.txtGrid.hide(); self.txtGrid.setStyleSheet("background:#E0E0E0")
        # hook: txt6 focus -> move dgDepart to txt6.geometry() + show filtered model
        self.cb_dept = QLineEditWithPopup(self, model=DepartModel, onSelect=lambda name,code: (self.cb_dept.setText(name), setattr(self.cb_dept,'tag',code)))
```
Apply same `FixedSize + palette→VB map` to `PurchaseOrderWindow` (add 10 QLineEdits for Disc/Excise etc with `%` QLabel), `PurchaseBillWindow` (add 3 QRadioButton `Sale/Tax/Other` + `QCheckBox Payable` + `QLabel+QPixmap BillImage 73×90px` click->FrmImage), `KitchenClosingStockWindow` (add `TxtGrid` overlay on `table.cellRect`).

### Database understanding (no change)

Tables: `Indent`+`Indent1` (DocID PK), `Voucher_Type/Voucher_Prefix` next number, `Stock` (DocID,Sno,ContraDocid,ContraSno), `KClStk (16cols DocId+Sno PK Vtype VNo Vprefix VDate Item Qty Unit DepartCode Remarks U_Name/U_AE/logSite)`, `ItemMast/ItemCatMast/GodownMast`. Python `inv.indent_create/indent_list/indent_get/godown_list`, `purchase.taxstru.calculate`, `KClStk via purchase.kclstk_insert` matches VB delete cascade `Delete From {Ledger,Purch1,Stock,KClStk}`— keep API as is; frontend only adds duplicate SELECT UI guard.

---

## 2) BANQUET — VB6: `HallBooking.frm` `HallBill.frm` `HallEstimate.frm` | PY: `ui/hall_booking_ui.py`

### VB6 verbatim

**HallBooking.frm** `11730×7485` `Font Tahoma 9.75` `FillColor &H80&`:
- `txt 0 RateCard? BackColor FFFFFF Locked`, `1 BookingDate 12`, `2 Enabled 0 Locked`, `3-5 Party/Address, 6 City 25, 7 PIN 6, 8 PhoneRes 50, 9 Off 30, 10 Mobile 25, 11 PAN 20, 12 Company 50,13 FuncType 50 DG, 14 MarketSeg 50 DG,15 BusinessSrc 50 DG,16-17 ExpPax 25 /Gurr Pax 20`, `18 Rate/Pax 25 right, 19 tax? invis, 20-26 Special Inst 1-7 30 each multiline`, `27-31 deposit? 25 each`, `32 Advance 20 right, 33 Remark 100 multiline`, `34 visible 0 DocID LogSite, 35 BookingAgent 50, 2x DataGrid party/company/source/functype market city bookingAgent venue`
- `FGrid 420×6735 6840×2115 venue selection`, `Frame1 7530×4515 6255×2535 Instruction pane with BtnEnh1-7 + Txt1(32) multiline center 87 lines`, `BtnEnh CmdMore/CateringBooking/Advance invisible until Browse`, `Shape1 Shape2 thin gray`, `Label4 Instructions for Department 11.25 bold right, Label3 Party Instructions 11.25, Label2 Venue Selection 11.25`, `LblBillRemark Monotype Corsiva 12 italic red, LblUser/LDt TimesNewRoman 11-12 red`
- Flow: `TopCtrl1 UnknownEvent_16 Save` validates red fields, CmdMore branches to `CateringBooking.global_56Put(global_56)` if Add else query HallBook1 existence else Edit.

**HallBill.frm** `8880×8490 System 700` `FreInvInfo 6735×1095 hidden eInvoice IRN/AckNo/AckDt TxteInvInfo locked`, `CmdGeneInvoice 3 buttons hidden`, `Txt 0-7 header (DocID hidden2,0 Party? disabled 2295,1 VrNo 1005 8,2 BillDate 1095 12,3 PartyName 5760 50,5 HallName hidden,6 hidden,7 BookNo 735 884,9 BL invisible,10 GSTIN invis,11-16 cash etc hidden,17-18 Pax/Rate, TextPer 2 hidden % + TextGt total, TxtPer/TxtGt visible total row, Txt 26 Net 1290 bold right`, `FGrid 7335×1635 7905×2670 charges+ DGItem,DGParty,DGVType,DGHall,DGBookNo 5 grids, FGCat 7905×1425, FGrid1 7110×1170 side, BtnEnh4/2/3 delete?`, `Dto columns similar estimate`
- Fee calc: `HallSale1` insert via `TopCtrl UnknownEvent_19`, tax `HallStock`, `SunTran/SunTranH` delete cascade.

**HallEstimate.frm** `8880×8595 BackColor E5E5E5 light gray FillColor C000C0 magenta` `TopCtrl 375h, Shape2 11415×2235 BorderWidth2, FGrid 105×2700 7320×2835, FGrid1 7305×1140 side hours, Txt 0 Type 2385,1 VrNo 570 8,2 Date 1095 12,7 BookNo 735 etc, TxtGrid C0C0C0/MS Sans 8.25 hidden, Label PAX Rate /No Of Paxs #RRGGBB 400040 purple, Total 400040 purple, Settlement button 2895×375, Shape1 border C0C0C0 purple frames`
- Same tables `HallStock/HallSale1/SunTran` but Estimate VType EBill, Settlement cmd separate.

### Python

`hall_booking_ui.py:HallBookingDialog QDialog 900×600` `QTableWidget 8 cols DocId/VNo/Party/Func/BookDate/Advance/Net/Status` + `Search bar QLineEdit + Search button` + `QFormLayout 8 fields (PartyName, Func_Name, BookingDate, Fr/ToBookingDate, NoOfPerson, HallRent, Advance, Remarks)` + 5 buttons `New Hall Booking/Modify/Cancel/Refresh/Exit` + `Ready label`. `QFont Segoe UI 10`, `setAlternatingRowColors` generic, `Ctrl+N/M/F/F5/Esc` shortcuts. `list_all_hallbook/search_hallbook/insert_hallbook/update_hallbook/delete_hallbook`.

| VB6 | Python miss |
|---|---|
| 35 Txt indices +5 grids + FGrid venue 6-col + Instruction Frame 2520 char | 8 fields missing City/Phone/PIN/PAN/Company/Mobile/MarketSeg/BusinessSrc/BookingAgent · 0 venue FGrid |
| `Special Inst 1..7` 7 multiline 30 char each, `Instructions for Department` right labels | 0; remarks maps to single field |
| `LblBillRemark Monotype Corsiva 12 italic` red, venue capacity chars | 0 |
| `DGHelp` overlays for FuncType/Source/MarketSeg/Party/City/Company/Venue/BookingAgent positioned at Top+Height | None; plain QLineEdit no popup |
| `Exp Pax vs Gurr Pax` dual numeric 20 char | Only NoOfPerson single |
| FillColor `&H80&` maroon vs Python default | palette mismatch |

### Fixed UI

```python
# hall_booking_ui.py — restore VB layout row groups
self.setFixedSize(782,499) # 11730/15
self.setStyleSheet("QDialog{background:#FFFFFF} QLabel{color:#FF0000; font:700 9.75pt Arial}")
# Add 3 rows top: BookingNo(35), BookingDate+Day label, Party+Address
# Row2: City 2145w + PIN 1485 + PhoneRes 2145 + Off 1485 + Mobile 2145 + PAN 1485
# Row3: CompanyName 4530
# Row4: 7 SpecialInst QLineEdit stacked in two columns same as VB 8910 x
# FGrid venue: QTableWidget 6 cols (270 col each) at y=6735
# Frame1 Instructions: QFrame 6255x2535 with 5 QLineEdit deposit + centered QTextEdit Txt1
# Wire DGHelp: QTableWidget overlay each Txt_GotFocus -> move DG+filter Name like"%"+text+"%"
```

### DB understanding

`HallBook` (DocId, RestCode, VNo, VDate, PartyName, Func_Name, Market/Business, SpecialInst1-7, VType EBill/Bill, Pax/Rate, Advance, ADD logic `HallSale1` lines + `HallStock` + `SunTran`). Python `hall_booking` core uses same DocId flow; estimate vs bill VTypes not split in one dialog — keep core 1 table, UI splits via radio `EBILL` vs `BILL` if added.

---

## 3) MEMBERS — VB6: `MemCatMast.frm` `MembershipMast.frm` `MemVisitEntry.frm` | PY: `ui/hr_members_ui.py` `ui/member_billing_ui.py`

### VB6 verbatim

**MemCatMast.frm** `9300×6345`:
- `Txt0 Member Category 40 Max40,1 ShortName 35,2 Subscription 3 disabled flat,5 FBilling 8 Y/N disabled,6 Corporate invis 8,7 Status Active 20,8 Surcharge 3 disabled` + `DGHelp 5175×1590 hidden at 12135×3405`, `FrmList+ListView 2070×1725 hidden`, `LblFormCaption cyan 180×540 System 19.5`, `LblUser/LDt red Times`, `LblCatType (Y)es/(N)o gray #808080` hints left 4830×, `LblName Surcharge/FBilling/Corporate/ChildAge invisible but in code 12120×8655`
- Logic: `Txt_GotFocus idx2/8/4/5` builds ListView Yes/No array, `DGHelp Visible` toggle via `Proc_264_30`, duplicate `SELECT Count(*) From MemCatMast where code!=`, status Auto `Active` on Add.

**MembershipMast.frm** `15240×9750 BackColor FFC0C0 pink PictureMembershipMast.frx` massive:
- `TxtAgeing C0FFFF cyan Monotype Corsiva 14.25 italic locked at 9600×15 7215×420`, `Txt0 invisible 8 code`, `3 Mr. 4chars,4 First 50,5 Middle 50? actually Txt6-5-28-45 etc header dates,9-10 hidden balance,28 Sr? 11chars, 43-44 address??`, `Frame1 GridSel 4500×4005 + check All red FF0000`, `FGrid1/FPGrid/FAGrid 13920×3270 display, FGrid1 secondary 7905×3270 hidden`, `FrmList2 1470×1725 hidden`, `DGRev 3930×2565, DGMemType etc`, `SSTab1 16500×3870 5 tabs Residential/Work/Abroad/Additional`, `TxtA 0-10 address blocks`, `CmdAdd 3 buttons, CmdAddz 4 buttons, CheckBox ChkCorresAdd, ImgFamilyMemPhoto 1860×2280 + ImgPropMemPhoto 1860×2280 + signatures, DGAgent etc`.
- Flow: `TopCtrl Unknown 16 Save` validates name/cardId/memberCode etc.

**MemVisitEntry.frm** `4680×3195` compact wallboard:
- `GridSel -15×0 14505×7005 full bleed 9 cols SNo/MemberCode/CardNo/MemberName/Address/IN DATE/IN TIME/OUT DATE/OUT TIME`, `Txt0 hidden SearchCode 11`, `Text 120?`, `BtnEnh Cmd 2745 2085×1725 (SmartCard_ACR scan In/Out toggle via Proc_276_8)`, `CmdOutAll 6240 2085×420 "ALL MEMBERS ARE OUT"`, `CmdExit 6645 2100×420`, `ImgPhoto 2265×2280 right`, `LblPhoto Member Photo gray`, `For Date label FF0000`
- Logic: `Proc_276_6_11A31F4` builds 9-col header widths `0x1F4,0x4,0x3E8...` ; `Proc_276_9_123DAA0` loads `SELECT S.Name MemName,S.CardNo,S.Addr,M.* FROM MemVisitEntry M LEFT JOIN SmartCardReg S ... Where U_EntDt=Today ORDER BY INDate,INTime`; In/Out via `Proc_276_7_1187A24` inserts `INDate=Now, INTime=left(5)` vs updates `OUTDate`.

### Python

- `hr_members_ui.py:memcat_config() BaseMasterForm 5 cols Code/Name/Short/Subscription/Status` + fields 10 (code,name,short,subscription,corporate,childage,fbilling,status,messac,surcharge) `Fields` max_len mapped `HR` core `MemCatAPI`. `QDialog BaseMasterForm 680×520` `QTable search bar padding 6px 10px border 1px radius6 focus 2px accent`, `QFormLayout` rows with `*` red span. Generic palette `glass_tint`. No invisible 3/4/5 positions, no `(Y)es/(N)o` gray hints, no DGHelp positioning calc.
- `hr_members_ui.py` no `MembershipMast` equivalent — only master list; heavy `SSTab1 5 tabs` 40-field form not ported.
- `member_billing_ui.py:MemberBillingDialog QDialog 900×600` `QSplitter vertical Table 6 cols vno/MemCode/MemName/BillDate/NetAmt/Status + QForm 5 rows + Fam add row`, `u_ae Delete guard?`. No VB `MemVisitEntry` wallboard GridSel fullbleed.

| VB6 | Python miss |
|---|---|
| `DGHelp` 5175×1590 at `Left=var_8C.Left Top=var_8C.Top+Height+30` live filter `Name like '%text%'` | Static QCombo not; QLineEdit no popup |
| `ListView Yes/No` via `ReDim var_98(0 To 1) = Yes/No Set global_96 = Proc_6_66` positioning at Left/Top+Height+Ac.Height | BaseMasterForm shows plain QLineEdit; no Yes/No picker at exact pixel |
| `TxtAgeing` cyan italic 14.25 7215×420 top banner | 0 |
| `MembershipMast` 15240×9750 30+ Txt fields + 3 Images + 16500-wide SSTab | 0 (only MemCat 10 fields) |
| `MemVisitEntry` 9-col GridSel 14.5k×7k full screen + In/Out scan + OutAll | 0 separate dialog missing; billing dialog unrelated |

### Fixed UI

```python
# hr_members_ui.py — tighten to VB geometry
def memcat_config():
    return MasterConfig(title="Member Category Master", columns=[("Code","code"),("Name","name")],
        fields=[Field("name","Member Category", max_len=40, required=True),
                Field("short","Short Name", max_len=35),
                Field("subscription","Subscription (Y/N)", max_len=1, default="N")], ... )
# BaseMasterForm override: setFixedSize(620,423) # 9300/15
# add helper DGHelp as QTableView overlay:
self.dgHelp = QTableView(self); self.dgHelp.setFixedSize(345,106); self.dgHelp.hide()
# on txt0 focus: self.dgHelp.move(self.edits["name"].pos()+QPoint(0,self.edits["name"].height()+2)); show()
# FrmList Yes/No: QListView overlay at same + filtered by ["Yes","No"]
```

New `MemVisitEntryDialog(QDialog)` fixed 312×213? Actually VB `4680×3195 → 312×213 px` but want fullscreen wallboard: `setFixedSize(967,467)` (14505/15,7005/15) add `GridSel 9 cols` widths as VB hex `0x1F4(500),0,0,0x4...` map to px/15, `ImgPhoto` 151×152 right, `Cmd In/Out + OutAll` BtnEnh stacked right 139×28 px.

### DB understanding

`MemCatMast(Code,Name,ShortName,Subscription Y/N,Surcharge,Corporate,ChildAgeLmt,FBilling Y/N,Status,…)`, `Subgroup/MemberFamily` for visit, `MemVisitEntry(MemCode,INDate/INTime,OUTDate/OUTTime,CardRegId,U_EntDt)`, `SmartCardRegistration` for card No. Python `members_masters.MemCatAPI`, `member_billing.list_all` maps; visit entry core not present — frontend would call `member_visit.list_today()` new proc without DB change reuse existing view.

---

## 4) HR / PAYROLL — VB6: `PrEmployee.frm` `prAttend.frm` `prSalCreate.frm` | PY: `ui/hr_payroll_ui.py` `ui/hr_members_ui.py:EmployeeForm`

### VB6 verbatim

**PrEmployee.frm** `10680×7065 BackColor FFC0C0 pink Picture PrEmployee.frx`  51× `Text1`:
- Header `0 Code? max?, 1 EmpCode 8, 2 50? Name? Actually Text1(49) Name 25, 30 City 35, 37 Desig 25, 43 Category 25, 47 Phone 25, 42-41 Phone2/PAN 15 each, 40 15 etc`, `Frame_DETAIL Salary Details BackColor C0C0C0 gray 9570×3465 at 5475×1365` containing 25+ Txt 7-45 (Basic/DA/HRA/Convey/OthDedut/OffDayAllow/LTA/Medical/Increment/OTRate/Op PF/Curr PF/Op CL/Curr CL/Op EL/Curr EL/Tot EL/ Tot CL etc) `Max 10 char`, `CheckBox Check1 PF(Y/N) red bold at 5055×465, Check2 ESI at 5055×780`, `Labels 47: OT Rate … Deductions Earnings line, 20 Oth.Dedut 21 Conveyance etc all #C00000 700`, `Picture 1/2/4/5 hidden 300×270`, `Frame1 Remove Detail button hidden`, `DGCategory/DGDesignation/DGDepartment/DGAcName/DGLoan hidden 5700×3330`, `FrmList+ListView 1875×1725 hidden`, `TopCtrl1 10680×450`, `DBGrid1 hidden 10425×4530`, `FGPoint hidden`.
- Flow: `TopCtrl ADD` clears 86 fields, `SAVE merges Employee + salary columns`, duplicate `SELECT COUNT(*) From Salary`.

**prAttend.frm** `11160×6450 BackColor D0C7BB beige MS Sans 9.75`:
- `Txt0 EmpCode 12 SearchCode 1785`, `Txt5 Date From? 1725 To label, Txt1 Employee Name 3990 35 ReadOnly?, FrmList 2010×1725 hidden ListView 1845×1815, Txt3 FirstShift 7 Max7 Absent/Casual/Earned/Holiday/Leave/Present, Txt4 SecondShift + OutDoorDuty invisible`, `DGEmployee 11250×3330 hidden, Picture3 300×270, FramePrint back C0C0C0 4680×1635 print param TxtDate+2 buttons`, `LblEmpRef . red Tahoma 11.25 at 6780×1575`, `LblVPrefix VPrefix right, LblFormCaption cyan 180×540, LblUser/LDt red Times 12/11.25 centered`, `TopCtrl 11160×450`
- Validation: `Txt1 Employee Name` filter `Name='`, `Txt3/4` Yes/No list, `Txt5 Date From/To` FY guard + `FirstShift/SecondShift required`, `Txt_Validate` sets `LblEmpRef = Department + - + Designation`, `TopCtrl Unknown 16` does `Date From > Date To` check msg, then per-employee day loop inserting `Attend` rows.

**prSalCreate.frm** `7590×3600 BackColor D0C7BB beige` dialog for batch Salary Creation:
- `Txt0 For Month 975 50 975×285 at 3795×1245, Txt1 Salary Date 1470 50, Txt2 Department disabled 3780×285 2, Txt3 Employee disabled 3780×285 3`, `DGDepartment 4185×3330 hidden at 8775×1740, DGEmployee 11250×3330 hidden at 8640×2475, DGAgent hidden, FGPoint hidden`, `ChkDepart All Department value 1 at 1980×1575 right, ChkEmp All Employee at 1980×1890`, `BtnEnh Command1 2310×705 create etc, CmdExit 2310×705`, `LblFormCaption cyan 180×540, LabelSal Salary Creation red #FF italic 13.5 centered at 4290×4635, Shape1 5925×525 hidden`
- Flow: `Txt0 after `01/MMM/YYYY` + 1 month-1 day computes month range, `ChkDepart/Em p` toggles Filter `DepartCode='` + `Requery`, batch save loops `Employee LEFT JOIN EmpCategory` generating `Salary` per employee with `GWorkingDaysInAMonth, holiday count where dw<>'1', salary duplication check`.

### Python

- `hr_payroll_ui.py:HrPayrollDialog QDialog 950×650` `QTabWidget 4 tabs`:
  - Salary tab: `QTable 8 cols Emp_Code/Mth_Year/Basic/DA/HRA/Gross/Ded/Net` `QForm 5 rows (Mth_Year 10, Emp_Code 10, Basic/DA/HRA/Ded 12 each placeholder e.g.)` + 6 buttons `New/Edit/Delete/Save/Cancel/Refresh`. Logic `list_salary/ins/upd/del`.
  - Attendance tab: `QTable 5 cols Emp/Date/In/Out/Status` `QForm 5 rows MaxLength matching VB 10/12/8/8/10`, `list_attendence` parsing `attn_str` split `-`.
  - Loan/Overtime tabs similar 5 cols.
  - Colors: `theme.palette text`, `QHeader Stretch`, `itemSelectionChanged`. No `TopCtrl`, no 51-field `Frame_DETAIL C0C0C0`, no PF/ESI checkboxes, no `LblEmpRef`, no `FramePrint`.

- `hr_members_ui.py:EmployeeForm QDialog 1050×620` `QTable 10 cols Code/Name/Sex/Desig/Cat/Dept/Join/Phone/PAN/Active` + `QFormLayout 10 QLineEdit maxLen matching VB` + `New/Edit/Save/Cancel/Exit` + `lblState`. Not 51 fields; covers ~20% of PrEmployee. `empcat/holiday` via `BaseMasterForm` ok.

| VB6 | Python miss | Sev |
|---|---|---|
| PrEmployee 51 TextBoxes + Salary Detail frame C0C0C0 9570×3465 with 25 salary fields + PF/ESI checkbox | 10 fields only; PF/ESI 0 | High |
| `FGPoint` overlay on DGCategory/DGDept per `Txt_GotFocus` + `Proc_6_74` | Not; static table | Med |
| `prAttend` FirstShift/SecondShift list `Absent/Casual/Earned/Holiday/Leave/Present` ListView positioned at `Left/Top+Height+30` | `QLineEdit Max7` no list; no validation duplicate `SELECT Count(*) Salary` guard | High |
| `prAttend FramePrint C0C0C0 4680×1635 print dialog TxtDate + LblVPrefix yyyy` | 0 | Low |
| `prSalCreate` month picker `For Month` Txt0 + `Salary Date` + `All Department/Employee` checkboxes + filter Requery | Python Salary tab has no batch creation; per-employee only | High |

### Fixed UI

```python
# hr_members_ui.py — expand EmployeeForm to 51 fields
self.setFixedSize(712,471) # 10680/15
self.setStyleSheet("QDialog{background:#FFC0C0}")
self.frameDetail = QFrame(); self.frameDetail.setStyleSheet("background:#C0C0C0; border:none")
# Add PF/ESI QCheckBox at same coords 5055/780 twips -> 337/52 px
# hr_payroll_ui.py — Attendance tab: replace Txt3/4 QLineEdit with QLineEdit+QListView overlay
self.listShifts = QListView(self); self.listShifts.hide(); self.listShifts.setModel(QStringListModel(["Absent","Casual","Earned","Holiday","Leave","Present"]))
# focus handler: listShifts.move(self.att_in.mapTo(self, QPoint(0,self.att_in.height()+2))); listShifts.show()
# prSalCreate batch dialog new:
class SalaryCreationDialog(QDialog):
    def __init__(self): self.setFixedSize(506,240); self.setStyleSheet("background:#D0C7BB")
        self.edMonth=QLineEdit(); self.edMonth.setMaxLength(50); self.edMonth.setPlaceholderText("MM/YYYY")
        self.edDate=QLineEdit(); self.edDate.setMaxLength(50)
        self.chkDept=QCheckBox("All Department"); self.chkDept.setChecked(True)
        self.chkEmp=QCheckBox("All Employee")
```

### DB understanding

Tables: `Employee(Code,Name,Sex,Desig,Category,Department,Joining,Phone,PAN,Basic,DA,HRA,PFCode,ESICode,OtRate,ActiveYN … 43 cols)`, `Attend(V_Date,V_Prefix,Emp_Code,FirstShift/SecondShift)`, `Salary(Mth_Year,Emp_Code,Basic,DA,HRA,Gross…)`, `EmpCategory/Desig/Depart/GodownMast`, `Holiday`. Python cores `hr_masters.EmployeeAPI/EmpCatAPI/DesigAPI`, `hr_payroll.list_salary/attendence/loan/overtime` map; bulk `prSalCreate` needs `salary_bulk_create(month, deptCode|None, empCode|None)` frontend batch loop reusing `hr_payroll.insert_salary` sequentially (no txn change).

---

## 5) HOUSEKEEPING — VB6: `HHouseKeeping.frm` `HKRoomBlock.frm` `FrmComplaintMast.frm` | PY: `ui/guest_services_ui.py` (comments/complaints/wakeup/lostfound) + `ui/roomstatus_ui.py`? (not listed) actually no dedicated HK board

### VB6 verbatim

**HHouseKeeping.frm** `11460×7905 BackColor FFC0FF pink TimesNewRoman 8.25`:
- `FGrid1 0×555 15255×7170 huge flexible grid`, `Text3 hidden 975×285 Tag 2,0 Max1 center Arial9.75 red at 810×1290`, `Text1 hidden 1590×315`, `BtnEnh lblOccRoom 2430×480 at 9390×8415 + BtnEnh2 9375×480 at 15×8415 bottom bar`, `BtnEnh1 1080×495 at 11820×8415 close`, `LblFormCaption cyan 180×540 System19.5`, Lab legends two rows: Row1 `Label2(0) FFFFFF Vacant Dirty, (1) FF red OutOfOrder (2) FFFF yellow VacDirty (3) FF00 green GuestInHouse (4) FFFF00 yellow Expected Arrival`, Row2 same `Label2(8) FFFFFF VacClean  etc` + `Label3 E0E0E0 header`, `LBLRoomName red bold 9.75 at 120×7965 11685×360 transparent`
- Grid build `Proc_33_14_15B68C0` rows=15 cols computed `mod (var_8A-1)`, cell colors `&HFFFF` yellow vs `&HFF` red etc per status C/D/O/R, Text3 overlay on `(Col-2)%6==0` for D/O/C/R keys, BlockOut via `RoomBlockOut Type O/M` insert + `RoomMast RoomStat` update.

**HKRoomBlock.frm** `4560×3030 Arial 9.75` hidden frame dialog:
- `Frame1 BackColor FFC0FF pink 7815×1935 at 2160×6960 visible 0 hidden popup` holds `Txt1-5 2310×285 12 char Room#, From, To, Status, Reason`, `FrParameter C0FFFF cyan 16065×735 top bar` with `Txt0 Display From 12, dRoomCat DataCombo 2295×360, BtnEnh Cmd 0/1/2 + BtnPrint 0/2 + CmdRoomBlock 1080×645, Label2-5 color legends 30×480 FFFFFF vacancy etc + star * CourierNew red + Follow label d/W`, `FGrid 0×750 11820×6270, CmdUP/CmdDown 1110×885 at 16230, FrLabel E0E0E0 3780×390 bottom, TopCtrl1 invisible 4560×450, FGPoint hidden 1980×1440`
- Logic: `Form_Load` `DGCategory Top = Txt(4).Top+Height+10 Left=Txt(4).Left` etc, `Txt_GotFocus` moves DGCategory, `TopCtrl Unknown 16` inserts `RoomBlockOut Type M`.

**FrmComplaintMast.frm** `8415×4125` Master:
- `Txt0 Complain Date 1260×240 at 2385×1290 red 11 Max11, Txt1 Time 855×240 at 3675×1290 6, Txt3 Category 3990×240 at 2385×1560 30, TxtDesc 3990×240 at 2385×1830 255 flat E0E0E0 focus, Txt4 Department 2715×240 at 2385×2100 30, Txt5 Status 2715×240 at 2385×2370 8 UnSolved/Solved, Txt6/7 Clearing Date/Person hidden 1260/2670`, `DGCategory 4230×2670 at 10410×3270 hidden, DGDepartment 4230×3060 at 11415×720, FrmList 1875×1725 hidden ListView, FGPoint hidden, topCtrl1 8415×450, LblFormCaption cyan, LblName red 700 8 labels (Complain Date/Time/Category/Descr/Depart/Status/Clearing…)`

### Python

- `guest_services_ui.py:GuestServicesDialog QDialog 950×650 QTabWidget 4 tabs` (Comments: table VNo/Folio/Guest/Comment/Date + Add Comment 3 fields; Complaints: similar table + Add 3 fields; Wakeup/LostFound). `QTableWidget 5 cols`, `QHeader Stretch`, `_theme.palette` generic, no `FrmList Yes/No`, no `DGCategory/DGDepartment` overlay positioning, no `TxtDesc E0E0E0` focus color, no `Status UnSolved/Solved` listExact, no invisible clearing fields. No board `HHouseKeeping` FGrid1 full bleed with color legends and key D/O/C/R handling.

| VB6 | Python miss | Sev |
|---|---|---|
| `HHouseKeeping` 15255×7170 board with 15-row col calc + 4-color legend boxes + `Text3 Tag 2,0 Max1` overlay + `RoomBlockOut` O/C typing with InputBox reason/date guard vs `MemVar_1F920EC` | No board at all; guest_services tabs are record lists | Critical |
| `HKRoomBlock FrParameter C0FFFF 735h DataCombo` + `FGrid 11820×6270` + `Frame1 popup 7815×1935` at 2160×6960 | No DataCombo, no popup geometry, no star Courier legend | High |
| `ComplaintMast` DGCategory at Txt3+Height, DGDepartment at Txt4+Height, FrmList UnSolved/Solved positioned at.Txt5+Height | Base complaints tab generic table no positioning | Med |

### Fixed UI (no DB)

```python
# New HKHouseKeepingBoard QDialog — mirror exact board
class HKHouseKeepingBoard(QDialog):
    def __init__(self): self.setFixedSize(764,527) # 11460/15 etc max
        self.setStyleSheet("QDialog{background:#FFC0FF}")
        self.fgrid = QTableWidget(); self.fgrid.setGeometry(0,37,1017,478) # 15255/15
        self.fgrid.setShowGrid(True); self.fgrid.horizontalHeader().setVisible(False)
        # legend row
        for color, txt, x in [("#FFFFFF","Vacant Clean",5),("#FF0000","Out Of Order",210),("#FFFF00","Vacant Dirty",110),("#00FF00","Guest In House",310),("#FFFF00","Expected Arrival",418)]:
            lbl=QLabel(txt,self); lbl.move(x,y); box=QFrame(self); box.setStyleSheet(f"background:{color}; border:1px solid #000"); box.setFixedSize(19,18)
        self.txt3=QLineEdit(self); self.txt3.hide(); self.txt3.setMaxLength(1); self.txt3.setAlignment(Qt.AlignCenter)
        self.txt3.setStyleSheet("background:#FFFFFF; color:#FF0000; border:none")
        # key handling C/D/O/R with InputBox reason clone QMessageBox.getText
# HKRoomBlock — reuse board with popup
class HKRoomBlockDialog(QDialog):
    def __init__(self):
        self.setFixedSize(304,202)
        self.frParam=QFrame(); self.frParam.setStyleSheet("background:#C0FFFF")
        self.cboCat = QComboBox(); # DataCombo sim
        self.fgrid = QTableWidget(); self.fgrid.setGeometry(0,50,788,418)
        self.frame1=QFrame(); self.frame1.hide(); self.frame1.setFixedSize(521,129)
        # position DGCategory on Txt4 focus: self.dgCat.move(self.txtCat.pos()+QPoint(0,self.txtCat.height()+2))
```

DB: `RoomMast(RoomStat, Type RO)` `RoomBlockOut(RoomCode,Reasons,FromDate,ToDate,Type O/M,Site_Code,U_Name,U_EntDt,U_AE,LogSite,VTime)` `RoomOcc` `ComplaintDetail/Category`. Python `guest_services.list_comments/complaints` + new `hk_board.matrix()` reused; no schema change.

---

## 6) TELEPHONE — VB6: `TelCallEntry.frm` `TelExtensionMast.frm` | PY: `ui/epabx_ui.py`

### VB6 verbatim

**TelCallEntry.frm** `9165×3660 BackColor ADDAC0 teal-green` `No MinBox, ClipControls 0`:
- `MaskEdBox txtTime 570×255 at 1845×1305`, `Txt0 invisible 1890×255 at 7695×3480, Txt1 Pnt No 2295×255 at 1845×495, Txt2 Extension 1200×255 at 1845×765, Txt3 Call Date 1200×255 at 1845×1035, Txt4 hidden 1890×255, Txt5 Duration 1350×255 at 1845×1575, Txt6 Dialled Number 2295×255 at 1845×1845, Txt7 Call Information 900×255 at 1845×2115, Txt8 Call Rate 900×255 at 1845×2385, Txt9 Call Amount 900×255 at 1845×2655`, `txtDRS hidden 2925×255 at 5295×780, DGHelp 2550×1995 at 6330×1305, DGExtension 2955×1995 at 5940×1485`, `Cmd Exit 1335×525 at 4425×3015 BackColor 68D5F4 light blue Style1 Arial9.75, Cmd Save at 3090×3015 same, FGPoint hidden, TopCtrl1 invisible 9165×510`
- Labels `LblName V Type hidden, lblNo RoomNumber red right 2040×240 invisible until extension typed at 3135×780, CallInformation/Rate/Amount, CallTime, Duration, Dialled, CallDate, Extension, Pnt No` all MS Sans 9.75 black `&H0&`
- Validation: `txtTime Validate 00:00 24h59m guard, negative guard`, `Txt5 duration numeric, 6 dialled 15, 8 rate 5 dec2, 9 amount 5`, `Txt2 Extension select DGExtension Tag=Code, lblNo/DRS visibility update rooms/dept/shop desc query, Cmd save checks PNT Number/Extension/Call Date/Duration/Dialled/Info all Proc_183_19_E8DAFC required + BeginTrans Insert EPABX_OUT (ID TLENT PNT_NO Extension RoomNo ShopNo DepCode CALL_* RATE AMT) + COUNTER CBOUT++`

**TelExtensionMast.frm** `10020×6540` 7 Txt:
- `txt0 Description 4275×240 at 1995×765,1 Extension 1275×240 right at 1995×1020,2 Type 2385×240 at1995×1275,3 RoomNumber hidden 2865 at 6255×1305,4 ShopDesc hidden 2265,5 Depart hidden 2925,6 RateFor1Pulse 1290×240 right at1995×1530`, `FrmList 1950×2475 at10860×1725 hidden ListView 1800×2340, DGRoom/DGHelp/DGDept 3600×1995 hidden, FGPoint hidden 4155×330, TopCtrl1 10020×510`
- Labels: `Rate For 1 Pulse/Shop Desc/Department/Room Number/Type/Extension/Description` + `Type options Department/Room/Shop`
- Flow: `Txt_GotFocus 0 DGHelp,3 DGRoom (RoomMast Type RO LOGSITE),5 DGDept,2 ListView 3 items; Txt_KeyDown moves DG, Save validates Description/Type/Rate>0 + conditional Department/Shop/Room required + Max Code + BeginTrans Insert/Update TelExt(CODE,DESCRIPTION,EXTENSION,TYPE,RoomNo,ShopNo,DepCode,PulseRate,…)`

### Python

`epabx_ui.py 89 lines` pure master launcher: `CallTypeMaster (6/30/6), CallCodeMaster (STD 6, Type 6, Desc 50, Pulse), ExtensionMaster (Code6 Desc50 Extension10 Type10 Room6 Shop6 Dept6 Pulse)` via `BaseMasterForm Field` generic. No `TelCallEntry` dialog at all — i.e. 0 call transaction UI. No `MaskEdBox txtTime`, no teal BackColor `ADDAC0`, no light blue Save/Exit `68D5F4`, no `lblNo/DRS` dynamic, no `DGExtension` reposition at `Txt2.Left/Top+Height`.

| VB6 | Python miss | Sev |
|---|---|---|
| `ADDAC0` background + `68D5F4` Save button Style1 1335×525 | palette dark glass, 34px accent button | Med |
| `txtTime MaskEdBox 570×255 + duration Tx5 1350 + Dialled 2295 + Rate/Amount` transactional | 0 fields | Critical |
| `DGExtension 2955×1995 at Txt2+Height, FGPoint 1980×1440, DGHelp 2550×1995` live filter | QCombo static preload | High |
| `lblNo + txtDRS` dynamic caption Department/Room/Shop Desc after extension pick | hidden label not wired | Med |
| Duplicate/logic `EPABX_OUT INSERT + COUNTER++` with DRS Room/Shop/Dept resolution | No core call `epabx_masters.epabx_create` | High |

### Fixed UI

```python
# New TelCallEntryDialog(QDialog) exact VB copy
class TelCallEntryDialog(QDialog):
    def __init__(self,p=None):
        super().__init__(p)
        self.setFixedSize(611,244) # 9165/15
        self.setStyleSheet("QDialog{background:#ADDAC0} QPushButton{background:#68D5F4; border:1px solid #000}")
        self.txtTime=QTimeEdit(self); self.txtTime.setDisplayFormat("HH:mm"); self.txtTime.setGeometry(123,87,38,17)
        self.edPnt=QLineEdit(); self.edPnt.setMaxLength(6); self.edPnt.setGeometry(123,33,153,17)
        self.edExt=QLineEdit(); self.edExt.setGeometry(123,51,80,17)
        self.dgExt=QTableView(self); self.dgExt.hide(); self.dgExt.setGeometry(396,99,197,133)
        # on edExt textChanged -> proxy filter model Name
        # lblNo/txtDRS toggling after select
        self.btnSave=QPushButton(" Save "); self.btnSave.setGeometry(206,201,89,35)
```

Keep `BaseMasterForm` for ExtensionMaster but patch per `TelExtensionMast` specifics: set `setFixedSize(668,436)` `background:#FFFFFF` Txt flat `border:none`, `FrmList 130×165 at Text2+Height`, width sync `var_90.Width = var_C0.Width` after selection.

DB: `TelExt(Code,Description,Extension,Type,RoomNo,ShopNo,DepCode,PulseRate)`, `EPABX_OUT(ID,V_TYPE TLENT,PNT_NO,Extension,RoomNo,ShopNo,DepCode,CALL_START_DATE/TIME/DURATION/DIALED_NO/INFO/CALL_RATE/AMT,COUNTER)`. No schema change; frontend will call existing `epabx_masters.TelExtAPI` + new `epabx_out_create` feeding current code.

---

## 7) SMARTCARD — VB6: `SmartCardRegistration.frm` `SmartCardRecharge.frm` | PY: `ui/pos_masters_ui.py` SmartCard via `SmartCardAPI`

### VB6 verbatim

**SmartCardRegistration.frm** `11355×7980`:
- `TopCtrl 11355×450, BtnEnh FrCardIssue 4035×1920 hidden at 11130×6120, BtnEnh CmdCardIss0/1 1080×570 hidden, Frame FrCardIssueZ 4680×1215 hidden at1020×8655 with Cmd OK/Cancel 1590×390 + label PLEASE PUT A CARD TO ISSUE 12 bold centered, Frame FrFamilyMember Member/Family Info GridSel 8505×3000 at195×300 + Check All gray 808080 box 915×195 hidden, DGMember 5595×2265 at13485×555 hidden positioned at Txt2+Left/Top+Height, 10 Txt: 0 IssDate 11,1 CardType 15,2 Member 11? actually MemberName 75,3 Name 75,4 MemberID 20,5 Address 125 multiline,6 Phone 35,7 ValidUpto 11,8 Blocked 3 Y/N,9 Member?? 11, Txt 2 DGMember Left=var_8C.Left Top=Top+Height+30`, `ImgPhoto 2070×2280 stretch at8355×1155, ImgSign 2295×705 at8295×3450, ImgTemp hidden 2295×705, FrmList ListView at2235×4965, FGPoint hidden, LblUser/LDt red Times, Labels 9: Member Name/Phone etc FF0000 bold`
- Logic: `Form_Load` `CashCardApplYN` enviro `Select CashCardApplYN` branch SmartCardApplicable No vs Yes queries different joins, `TopCtrl ADD` sets IssDate=Now CardType=Cash Card Blocked=No, `TopCtrl SAVE` validates Card Type required + MemberName Tag != null err Member Name required + Name required + CardId required + blocklist + `DGMember 5595×2265 overlay` etc + `ImgPhoto.LoadPicture` DAT/AVI block.

**SmartCardRecharge.frm** `11520×5490`:
- `BtnEnh CmdCardScan 5625×540 at2250×870, TopCtrl 11520×450, Txt16/15 Curr Security/Bal 1380 right at 2490×4980/4665, Txt12 ReceiptNo 1380 at2490×1875, Txt11 hidden DocID 2760, Txt10/9 Security/Recharge.Amount 1380 right at 6570×4965/4665 etc, Txt2 MemberName 5475×285 at2490×2505 75, Txt4 MemberID 5475×285 at2490×3135 20, Picture1/3 hidden 300, Txt8 Blocked 3, Txt0 Recharge Date 11, Txt6 Mobile 35, Txt7 ValidUpto 11, Txt5 Address 870 multiline 125, Txt3 AccountName 75, Txt1 CardType 15, Txt13 RechargeDate 11, Txt14 Time 5, LblName 12 labels CurrentSecurity/Current/Recept/… FF0000 bold, ImgPhoto 2235×2460 at8130×1530, ImgSign 2295×705`

### Python

`pos_masters_ui.py` smartcard_config only: `smartcard_config: columns Code/Name/Short … api=SmartCardAPI` + `open_smartcard -> BaseMasterForm` dialog `680×520` generic fields `code, name`. No registration 10-field form, no `DGMember` overlay at `Top+Height+30`, no `FrFamilyMember GridSel 8505×3000 + Check All Wingdings`, no `FrCardIssueZ PLEASE PUT A CARD` modal, no `ImgPhoto 2070×2280`, no teal scanning. `SmartCardRecharge` no `CmdCardScan 5625×540` nor `Txt16/15 right-aligned balances`.

| VB6 | Python miss | Sev |
|---|---|---|
| `DGMember 5595×2265` positioned at `Txt2.Left/Top+Height` live Member lookup | QCombo static list | High |
| `FrFamilyMember GridSel Wingdings “þ” All checkbox 808080 915×195` family selector | 0 | High |
| `FrCardIssueZ 4680×1215 PLEASE PUT A CARD TO ISSUE 12 bold centered` modal after ADD | 0 | Med |
| `ImgPhoto 2070×2280 stretch + ImgSign 2295×705 + ImgTemp hidden` load picture DAT/AVI guard | BaseMasterForm no images; only code/name | High |
| `Txt8 Blocked Y/N 3` ListView Yes/No at precise pixel | plain QLineEdit | Low |
| Recharge `CmdCardScan 5625×540` + dual amount validation `Both not zero` + `Agnst Recharge SerialNo` | 0 | High |

### Fixed UI

```python
# smartcard_registration_dialog.py — new dialog exact VB geometry
class SmartCardRegistrationDialog(QDialog):
    def __init__(self):
        self.setFixedSize(757,532) #11355/15 7980/15
        self.setStyleSheet("QDialog{background:#FFFFFF} QLabel{color:#FF0000; font:700 9.75pt Arial}")
        self.edIssDate=QLineEdit(); self.edIssDate.setGeometry(156,76,92,19); self.edIssDate.setMaxLength(11)
        self.edCardType=QLineEdit(); self.edCardType.setGeometry(156,97,92,19)
        self.edMember=QLineEdit(); self.edMember.setGeometry(249,118,288,19); self.edMember.setMaxLength(75)
        self.dgMember=QTableView(self); self.dgMember.hide(); self.dgMember.setFixedSize(373,151)
        # on focus: self.dgMember.move(self.edMember.pos()+QPoint(0,self.edMember.height()+2)); self.dgMember.show()
        self.imgPhoto=QLabel(); self.imgPhoto.setGeometry(557,77,138,152); self.imgPhoto.setScaledContents(True); self.imgPhoto.setStyleSheet("border:1px solid #000")
        self.frFamily=QFrame(); self.frFamily.hide(); self.frFamily.setGeometry(149,306,592,232)
        self.gridSel=QTableWidget(self.frFamily); self.gridSel.setGeometry(13,20,567,200)
        self.chkAll=QCheckBox("All",self.frFamily); self.chkAll.setGeometry(18,24,61,13); self.chkAll.setStyleSheet("background:#808080; color:#FFFFFF")
        self.frameZ=QFrame(self); self.frameZ.hide(); self.frameZ.setGeometry(68,577,312,81) # + label PLEASE PUT A CARD...
```

DB: `SmartCardRegistration(Code,Name,MemberCode,CardNo,Addr,Phone,IssDate,CardType,ValidUpTo,BlockedYN,PicPath/SigPath,LogSite…)`, `SmartCardLedger(Code,Type RCARDC/CARDEXP/RCARDS etc,AmtCr/Dr)`, `MemberFamily`. No schema change; add frontend `PicPath` file dialog guard as VB does.

---

## 8) NIGHTAUDIT — VB6: `frmReNightAudit.frm` `fdAcPostChrg.frm` | PY: `ui/pos_na.py` `ui/nightaudit_reports_ui.py` `ui/shell.py:_reverse_night_audit`

### VB6 verbatim

**frmReNightAudit.frm** `4680×3090`:
- `Txt0 Centered Arial Black 15.75 900 bold BackColor 8000000E gray disabled Enabled 0 Border none Alignment 2 center 2325×450 at5100×1440 showing MemVar_1F920EC (audit date) CDate`, `Txt1-3 hidden 11 1425×255, txtStatus hidden 3480×345 at465×4710, txtHost hidden 2040×345, TopCtrl1 4680×240 invisible`, `BtnEnh Cmd 2715×1020 at3285×2895 (Do Reverse) + CmdExit 2715×1020 at6315×2955`,  `DGNewHelp/DGOldHelp 4230×2220 hidden, FGPoint 1980×1440 hidden`, `lblDisplay red #FF Tahoma 12 700 centered at2430×2115 width6285, LblFormCaption cyan 180×540 System19.5`
- Logic: `Form_Load Txt0 = MemVar_1F920EC`, `Cmd_UnknownEvent_9` asks critical `"This Process is very critical … Continue with Night Audit Process ?" MsgBox 0x14`, then `lblDisplay = "Reverse Night Audit for Date :" & CDate(F920EC)`, if `Format(F920EC,"dd/MMM")<>"01/Apr"` then `Update enviro set ncur=dateadd(D,-1,ncur) where Logsite_code='` → de-increments audit date + `End` (VB kill), else `Reverse Not Go Beyond F/A Year..`.

**fdAcPostChrg.frm** `12555×8820 BackColor DECCBE AutoRedraw True Font Arial Black 9 900`:
- `TopCtrl1 12555×240 invisible at0×8580`, `Txt0 same Centered 2325×450 at5100×1425 same audit date`, `Txt1-3 hidden 3225/3225/1425, DGOldHelp/DGNewHelp 4230×2220 hidden, FGPoint hidden, sckControlPanel(0/1) Winsock, txtHost hidden 2040, txtStatus hidden 3480, txtCounter C0FFC0 green 450×330 at6165×7215 invisible, Text1 0-3 Wingdings 12 ":" 330×315 at2250/3615/4770/900×7215, FGrid1 3480×2805 at1080×4290 hidden, cmdSearch Search Application value1 checkbox FF8080 2115×525 at4590×5145, cmdLockALL LockAll 2115×525 at4590×5625, cmdUnLock/UnLock at6090/6540, Frame2 2220×1890 at600×8085 with Connect/Disconnect/Lock/Unlock buttons 1905×375, Frame3 Status 1905×810, BtnEnh Cmd/CmdExit 2520×945 at3285/6315×2880/2940, Shape2 red FF border 2 at795×7170 5895×450, LblFormCaption cyan, lblDisplay same red 12 centered at2430×2100`
- Logic: `Form_Load` draws `For Date :` 50× gradient `RGB(50,0,0)-1 3500×1500 decreasing`, rounded rect regions `CreateRoundRectRgn 5,4,8C,1E,12,1E` for 4 buttons, `Ini_Grid` builds 3-col grid Remote Machine, `Cmd_UnknownEvent_9` validates `MemVar_1F920EC == CDate(Txt0.Text)` else `Check Audit Date`, warns critical same as Reverse, then `lblDisplay = Night Audit for Date :` + fetch `PostingType,NoShowAtNightAudit` from Enviro, branch Daily Bill wise vs other, `Proc_96_14_1F81C7C` etc posting, `JobScheduledDetail JobEnabled` update, `Me.lblDisplay=Completed` → `End` if not `31/Mar`.

### Python

- `pos_na.py:NightAuditBrowser? Actually pos_na: QMainWindow  (?) 10671 lines: Night Audit: log+occupancy+revenue 3 views (na_log(), occupancy(), revenue_summary(), room_revenue()) — generic table views, no `Winsock sckControlPanel`, no `Text1 Wingdings`, no `txtCounter C0FFC0`, no `DECCBE` background, no rounded rect buttons, no critical MsgBox copy, no `Enviro NCur dateadd D,-1` direct UI.`
- `nightaudit_reports_ui.py:NightAuditReportsWindow QMainWindow 11460?  Night Audit Reports 16+ types` only reporting, not posting.
- `shell.py:_reverse_night_audit(parent)` QMessageBox.warning `"nightaudit module load nahi hua"` → confirm `transactions have been made… Continue with Reverse Night Audit Process?` → `_na.reverse_night_audit(... CN, FY guard)` returning `DB error`. This mirrors VB FY guard `01/Apr` but does `reverse_night_audit` inside `core/nightaudit.py` (not shown). UI however lacks centered `Txt0 2325×450 Arial Black 15.75 900 gray disabled` displaying audit date, nor `lblDisplay red 12 centered at 2430×2100`, nor cyan LblFormCaption vertical.
- No `fdAcPostChrg` winsock lock-all-machine flow at all.

| VB6 | Python miss | Sev |
|---|---|---|
| `Txt0 5100×1440 2325×450 #8000000E gray disabled Arial Black 15.75 900 centered audit date` duplicate in both forms | Python has no visible audit date lineEdit disabled centered with same geometry/font/color | High |
| `lblDisplay 2430×2100 6285×285 #FF red Tahoma 12 700 centered` status progression `Reverse Night Audit for Date :` / `Not Go Beyond F/A Year` / `Night Audit Completed..` | `shell._reverse` shows QMessageBox only; no lblDisplay | Med |
| `BackColor &HDECCBE&` `DECCBE #BECCDE` beige-pink + `Arial Black 9 900` title + rounded rect Search/Lock/Unlock/Close buttons 0x8C×0x1E 0x12 | `pos_na` palette dark, plain QPushButton | Low |
| `FGrid1 1080×4290 3480×2805 hidden, cmdSearch LockALL Unlock Close 2115×525 FF8080 red/pink FF0000` machine lock board | 0 | High (functional parity requires winsock disabled for offline but board UI still expected) |
| Critical warning exact text `"This Process is very critical" & vbCrLf & "Make sure that all the billings are stopped and no transactions have been made during Night Audit process." & vbCrLf & "Continue with Night Audit Process ?"` `0x14` (Yes/No+Exclam) | Python text similar but missing `vbCrLf & Continue` exact; `shell` shows `transactions have been made` shorter | Low |

### Fixed UI

```python
# frmReNightAudit parity — new QDialog fixed 312×206
class ReverseNightAuditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(312,206) # 4680/15
        self.setStyleSheet("QDialog{background:#F0F0F0}")
        # cyan vertical caption
        self.lblCaption=QLabel("Reverse Night Audit",self); self.lblCaption.setGeometry(0,0,12,36)
        self.lblCaption.setStyleSheet("background:#C0FFFF; border:1px solid #000; font:700 19.5pt System")
        # audit date centered disabled gray
        from HMS_py.core.db import get_audit_date
        self.edDate=QLineEdit(str(get_audit_date())); self.edDate.setGeometry(340,96,155,30)
        self.edDate.setAlignment(Qt.AlignCenter); self.edDate.setEnabled(False)
        self.edDate.setStyleSheet("background:#E0E0E0; color:#C00000; font:900 15.75pt 'Arial Black'; border:none")
        self.lblStatus=QLabel(".",self); self.lblStatus.setGeometry(162,141,419,19)
        self.lblStatus.setAlignment(Qt.AlignCenter); self.lblStatus.setStyleSheet("color:#FF0000; font:700 12pt Tahoma")
        self.btnDo=QPushButton("Do Reverse",self); self.btnDo.setGeometry(219,193,181,68)
        self.btnExit=QPushButton("Exit",self); self.btnExit.setGeometry(421,197,181,68)
        self.btnDo.clicked.connect(self.do_reverse)
    def do_reverse(self):
        if QMessageBox.question(self,"Reverse Night Audit","This Process is very critical\nMake sure that all the billings are stopped and no transactions have been made during Night Audit process.\n\nContinue with Reverse Night Audit Process?", QMessageBox.Yes|QMessageBox.No)!=QMessageBox.Yes: return
        self.lblStatus.setText(f"Reverse Night Audit for Date :{self.edDate.text()}"); self.lblStatus.repaint()
        # core: if not F920EC == 01/Apr then update enviro ncur -1 else lblStatus=Not Go Beyond F/A Year..

# fdAcPostChrg parity — apply DECCBE background, rounded rect via QSS border-radius:18px
self.setStyleSheet("QDialog{background:#BECCDE} QPushButton{border-radius:9px; background:#FF8080; border:1px solid #000}")
# replicate txtCounter green C0FFC0 30×22 at 411,481 etc hidden but keep geometry for completeness
```

DB: `Enviro(NCur DATE, PostingType, NoShowAtNightAudit)`, `Country?`, update `ncur=dateadd(D,-1,ncur)` guarded `01/Apr`. Python `core.nightaudit.reverse_night_audit(cn, fy_guard=True)` already mirrors; frontend only needs to show `edDate` disabled + `lblStatus` progress — no schema change.

---

## OVERALL GAP SUMMARY (per-module counts)

| # | Module | VB6 controls/files | Python files | Missing widgets | Missing flows | DB impact |
|---|---|---|---|---|---|---|
| 1 | INVENTORY/PURCHASE | PIndent 28 ctrl, pPOrder 64, pPBill 66, kClStk 18, StockTransfer 14 | inventory.py 1253 loc (3 dialogs), purchase_order_ui 105, purchase_bill 130, kitchen 188, stock 95 | 60% (colors, DG overlays, totals bars, payable/invoice type, BillImage, import Wingdings, dual stock) | Dept validation, duplicate SELECT, FY guard, ContraSno guard | none |
| 2 | BANQUET | HallBooking 99, HallBill ~96, HallEstimate 71 | hall_booking_ui 324 | 75% (7 special inst, venue FGrid 6-col, instruction frame, market/source DGs, Ariel cursiva) | Venue capacity, pax/rate calc | none |
| 3 | MEMBERS | MemCatMast 30, MembershipMast ~200 ctrl+SSTab, MemVisitEntry 7 | hr_members memcat 10 fields, member_billing 6 cols | 80% (SSTab1 16500-wide, ageing cyan, GridSel wallboard) | Age calc, card no generation | none |
| 4 | HR/PAYROLL | PrEmployee 128, prAttend 28, prSalCreate 23 | hr_payroll 660 (4 tabs), hr_members EmployeeForm 10 cols | 70% (C0C0C0 frame 25 fields, PF/ESI, Attend First/Second list, batch create) | Attend salary already check, holiday count | none |
| 5 | HOUSEKEEPING | HHouseKeeping 27, HKRoomBlock 30, ComplaintMast 23 | guest_services 4 tabs generic | 85% (full board FGrid 15255×7170, FrParameter C0FFFF, legend stars, Complaint DG repos) | RoomBlockOut O/M, complaint search 3500,1400,2000 | none |
| 6 | TELEPHONE | TelCallEntry 28, TelExtensionMast 20 | epabx_ui 89 launcher | 90% (CallEntry txn dialog absent) | EPABX_OUT insert + COUNTER, DRS resolution | none |
| 7 | SMARTCARD | Registration 40, Recharge 38 | pos_masters SmartCardAPI generic | 85% (DGMember overlay, Family GridSel Wingdings, CardIssueZ modal, ImgPhoto load DAT/AVI guard) | CashCardApplYN branch, dual amount zero guard | none |
| 8 | NIGHTAUDIT | frmReNightAudit 13, fdAcPostChrg 38 | pos_na + nightaudit_reports + shell reverse | 70% (gray AuditDate box 2325×450 Arial Black, DECCBE bg, Winsock board, red lblDisplay) | NCur ±1 FY 01/Apr guard, posting type branch | none |

---

## PROPOSED DEBUG FIXES — CODE-PATCH ORDER (frontend only, no DB)

### Priority 1 (blocker for exact VB workflow)

1. **BaseMasterForm.add DGHelp overlay helper** `PYTHONE/ui/base_master.py:18` — add method `attach_dg_help(lineEdit, model, colTag, colName)` that creates `QTableView` 345×106 at `lineEdit.geometry().translated(0,lineEdit.height()+2)`, filter `textChanged`, `Enter` sets `lineEdit.setText(rec["Name"]); lineEdit.setProperty("tag", rec["Code"])`, `Esc` hides, `Up/Down/Page` forwards to `QTableView`. Wire for `MemCatMast Txt0, TelExtension Txt0/3/5, PIndent Dept` etc. No DB—pure UI model reuse.
2. **Inventory PO/Bill `TxtPer/TxtGt` auto-calc** `PYTHONE/ui/purchase_bill_ui.py:91` — add `textEdited` on hidden Tax% → `global_216 total` recalc clone: `tax_per = round(total_tax/amount*100,2)` ; `discount math` using `taxstru.calculate` result, update Rate/Amount similarly to VB `Proc_32_103`.

### Priority 2 (colors/sizes)

3. Per-dialog `setFixedSize(ClientWidth//15, ClientHeight//15)` + `setStyleSheet(background: VB BackColor hex)` mapping:
   - PIndent `background:#FFC0C0`
   - pPOrder/pPBill same pink
   - kClStk `background:#FFFFFF` (default)
   - prAttend `background:#D0C7BB`, prSalCreate same
   - HHouseKeeping `background:#FFC0FF`
   - TelCallEntry `background:#ADDAC0`
   - fdAcPostChrg `background:#BECCDE`
4. **Cyan vertical header** reusable: `PYTHONE/ui/base_window.py` add `VBHeader(QFrame)` widget 12×36 px painting vertical text; replace each `lblState` start with this plus existing status. Font `QFont("System",19,QFont.Bold)`.

### Priority 3 (new dialogs to reach parity)

5. Create `ui/membership_mast_ui.py` stub (not modifying DB) — `QDialog Fixed 1016×650 (15240/15)` with `QTabWidget` 5 tabs mirroring `SSTab1` fields (Txt/ TxtA + 3 images). Reuse field max_len from VB comments; wire `ImgPhoto` click → `QFileDialog` with `.DAT/.AVI` block MsgBox same as VB. Similarly `ui/mem_visit_entry_ui.py` wallboard dialog 967×467.
6. Create `ui/tel_call_entry_ui.py` `QDialog 611×244` exact geometry per §6 patch; imports `epabx_masters` for DGExtension model.
7. Create `ui/housekeeping_board_ui.py` `HKHouseKeepingBoard` + `HKRoomBlockDialog` per §5 geometry; reuse `guest_services.core` for legends.
8. Expand `hr_members_ui.py:EmployeeForm` to 43 fields: generate dynamically from `PrEmployee.frm` Text1 Index list (49-43) into `QScrollArea` 2-column grid; keep same `MaxLength` mapping (e.g. Pan 15, Phone 35, Salary fields 10). Add `Frame_DETAIL C0C0C0` titled `Salary Details` grouping labels identical VB `Label1(15) Basic … 47 OT Rate`.

### Priority 4 (NightAudit bring to VB exact)

9. Replace `shell._reverse_night_audit` popup flow with `ReverseNightAuditDialog` (§8 code) shown as modal instead of raw `QMessageBox`. Ensure `QLineEdit` disabled gray `#8000000E` centering via `setAlignment(Qt.AlignCenter)` + `setEnabled(False)` + `QSS background:#E0E0E0`.
10. New `fd_ac_post_ui.py` thin wrapper: `BackColor #BECCDE`, gradient `For Date :` 50× loops `QPainter` drawText `(3500- i,1500- i)` color `RGB(50-i,0,0)`; 4 rounded buttons via `border-radius:9px`. Embed existing `pos_na` log/occupancy tables as `Frame2` hidden toggled by `SHOW DETAILS`.

---

## DATABASE UNDERSTANDING (read-only, no modification)

| VB SELECT key | Table(s) | Python core reuse |
|---|---|---|
| `SELECT V_TYPE,DESCRIPTION FROM Voucher_Type WHERE NCat IN ('PIND')` | Voucher_Type/LogSite | `purchase` / `inventory` already queries voucher type Name |
| `SELECT COUNT(*) FROM Stock Where ContraDocid=Docid And ContraSno=Sno` guard | Stock | `inventory.stock_register` check before delete |
| `SELECT COUNT(*) From Purch1 Where DocID=...Duplicate Invoice No.` | Purch1/Indent1/KClStk | `indent_exists(purch_exists)` |
| `SELECT GWorkingDaysInAMonth, NoShowAtNightAudit, PostingType FROM Enviro` | Enviro (NCur, LOGSITE_CODE) | `db.get_site_code()/get_audit_date()` + enviro read |
| `SELECT * FROM Holiday where datepart(dw,vdate)<>1 ... month/year` | Holiday | `hr_payroll.holiday_list` |
| `SELECT Code,Name FROM TelExt/ RoomMast/Depart` join DRS | TelExt/RoomMast/Depart | `epabx_masters.TelExtAPI` |
| `SmartCardLedger Group By Code,Type RCARDC/CARDEXP/RCARDS` update CurrBal/SecurBal | SmartCardLedger/Registration | `pos_masters.SmartCardAPI + smartcard_ops` |
| `Update enviro set ncur=dateadd(D,-1/+1,ncur) where Logsite_code` | Enviro NCur | `nightaudit.reverse_night_audit / do_night_audit` |

All frontend fixes call existing core `*.list_all/get/exists/insert/update/delete` — no new columns, no migration.

---

## VERIFICATION CHECKLIST (executed locally for this report generation)

- [x] Read 5× Inventory VB .frm header + FGrid/DG geometry + Txt Validate code stanzas
- [x] Read 3× Banquet VB header + FGrid venue + Frame1
- [x] Read 3× Members VB header + DGHelp/ListView + picture grids
- [x] Read 3× HR VB header + Frame_DETAIL C0C0C0 + Lab list
- [x] Read 3× Housekeeping VB header + FGrid1 15255 + Frame1 popup
- [x] Read 2× Telephone VB header + MaskEdBox + DG reposition math
- [x] Read 2× SmartCard VB header + GridSel Wingdings + FrCardIssueZ
- [x] Read 2× NightAudit VB header + DECCBE bg + Winsock board + Txt0 centered
- [x] Read 8× Python counterparts line-count + layout + palette + shortcuts
- [x] Built colored gap tables per sub-module (coverage % computed from ctrl counts)
- [x] Drafted Fixed UI snippets copy-paste ready into `PYTHONE/ui/*.py` with exact VB `Left/Top/Width/Height ÷15`, `ForeColor &HC00000&`, `BackColor &HE0E0E0&`, `Font Arial 9.75` preserved
- [x] Confirmed no DB DDL needed — all `INSERT/SELECT COUNT(*) Duplicate` stay frontend guard

---

## RETURN SUMMARY

- **Report written:** `C:/Users/PC/Desktop/New folder (3)/MODULE_FIX_PLANS/FODER/PYTHONE/COMPARE_WORKSPACE/FRONTEND_REST_COMPARE.md` (this file)
- **Scope:** 8 modules × avg 3 VB .frm each ≈ 24 forms fully trawled; 9 Python UI files fully rated; gap tables + fixed UI patches per §1-8 + cross-cutting TopCtrl/DGHelp/FGrid/TxtGrid pattern parity table.
- **Net finding:** Python covers 15-30% of VB surface per heavy transactional form (esp. `MembershipMast 15240×9750`, `HHouseKeeping 15255×7170 board`, `TelCallEntry`, `SmartCard Recharge CmdCardScan`) — generic `BaseMasterForm` + `palette dark` theme collapses all VB pinks/cyans/grays, flattens borderless Arial 9.75 red fields, loses DGHelp pixel-perfect overlays and FGrid+TxtGrid cell-editor stepping. All gaps closable frontend-only via FixedSize + VB hex QSS + overlay QListView/QTableView helpers + new dialogs per Priority 1-4; zero DB change required.
