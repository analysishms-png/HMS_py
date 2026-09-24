# UI FRONTOFFICE2 — VB6 → Python Exact Parity Report

> **Focus:** FRONT OFFICE (CheckIn, CheckIn List, Room Status, Display Rack, Bill Reprint, ReSettlement, Merge Folio, WalkIn, PlanMaster)
> **VB6 Sources:** `fdCheckIn.frm`, `FdCheckOut.frm`, `fdDisplayFolio.frm`, `fdRoomChange.frm`, `FdRoomDisplay.frm`, `FdReSetlement.frm`, `fdWalkInEntry.frm`
> **Screenshots:** `02_Operations\{02_WalkIn_CheckIn.png, 03_CheckIn_List.png, 04_Room_Status.png, 05_Bill_Reprint.png, 06_Bill_ReSettlement.png, 08_Merge_Folio.png, 10_InHouse_Room_Status.png}`
> **Python Sources:** `ui/folio_ui.py`, `ui/checkout_ui.py`, `ui/fo_sub_forms_ui.py`, `ui/frontoffice.py`, `ui/front_office_dashboard.py`, `ui/roomstatus_ui.py`, `ui/plan_master.py`
> **Date:** 2026-09-24 | **Mode:** UI-only — **Do NOT modify DB** — frontend logic, same control behavior, same colors/sizes, same fonts, same validation verbatim
> **Workspace:** `PYTHONE\COMPARE_WORKSPACE\UI_FRONTOFFICE2_COMPARE.md`
> **Rule:** PARAM-BOUND SAME SQL as VB6 verbatim. No schema change.

---

## 0. Sources Read ONE BY ONE Fully

### 0.1 VB6 .frm — Full Read Log

| # | File | Lines | Client W×H twips (px) | BackColor BGR→RGB | Border/Style | Read? |
|---|------|-------|----------------------|------------------|-------------|-------|
| V1 | `fdCheckIn.frm` | 459 | **ClientWidth 11340× ClientHeight 4515** → **756×301 px** (÷15) | `BackColor &HC6B7A4&` → B=C6 G=B7 R=A4 → **#A4B7C6** dusty blue-gray | `BorderStyle 1 Fixed Single`, `MaxButton 0 MinButton 0 Visible 0 MDIChild -1 KeyPreview -1 WhatsThisHelp -1 ClientLeft 45 ClientTop 615 ScaleMode 1` | ✅ full |
| V2 | `FdCheckOut.frm` | 2836+ | **ClientWidth 14625× ClientHeight 8310** → **975×554 px**; interior `Frame1 16800×9375 at -15,-30` overflow borderless | `BackColor &HC0C0C0&` → B=C0 G=C0 R=C0 → **#C0C0C0** mid-gray; inner Frame1 `&HFFC0C0&` → **#C0C0FF** pale lavender | `ControlBox 0 KeyPreview -1 ScaleMode 1 AutoRedraw 0` | ✅ full |
| V3 | `fdDisplayFolio.frm` | 1356 header + ~1800 code | **ClientWidth 14235× ClientHeight 8985** → **949×599 px** | `BackColor &HFFC0C0&` → **#C0C0FF** | `ControlBox 0 KeyPreview -1 LockControls -1` | ✅ full |
| V4 | `fdRoomChange.frm` | 1281 header + ~3000 code | **ClientWidth 12270× ClientHeight 8595** → **818×573 px** | `BackColor &HFFC0C0&` → **#C0C0FF** | `ControlBox 0 KeyPreview -1 LockControls -1 Font Tahoma 8.25 400` | ✅ full |
| V5 | `FdRoomDisplay.frm` | 302 | **ClientWidth 14190× ClientHeight 8355** → **946×557 px**, `WindowState 2 Maximized` | `BackColor &HFFC0C0&` → **#C0C0FF**; nested `FrmPic Back &HCBFCF9& → B=CB G=FC R=F9 → #F9FCCB` pale cream; `FrmRoom Back &HFFC0FF& → B=FF G=C0 R=FF → #FFC0FF` bright pink | `WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1` + `Picture frx:0 Icon frx:52A` | ✅ full |
| V6 | `FdReSetlement.frm` | 2000 header + 3784 code | **ClientWidth 9555× ClientHeight 7350** → **637×490 px**, `WindowState 2 Maximized` | `BackColor &HFFC0C0&` → **#C0C0FF**; inner `Shape5 Fill &HC0FFC0& → B=C0 G=FF R=C0 → #C0FFC0` mint fill; `LTxt Back &HFFFFFF&` white | `WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 Font Tahoma 9.75 400` | ✅ full |
| V7 | `fdWalkInEntry.frm` | ~12200 chars header | **ClientWidth 13995× ClientHeight 8595** → **933×573 px**, `WindowState 2 Maximized` | `BackColor &HFFC0C0&` → **#C0C0FF**; inner `FrmPackage Back &H80FF80& → B=80 G=FF R=80 → #80FF80` light mint; `Frame1 Back &HC0FFFF& → B=C0 G=FF R=FF → #FFFFC0` pale yellow (visual yellow) | `WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 LockControls -1` | ✅ full |

### 0.2 Python .py — Full Read Log

| # | File | Lines | Root Widget | FixedSize? | StyleSheet / Colors | Read? |
|---|------|-------|-------------|------------|---------------------|-------|
| P1 | `ui/folio_ui.py` | 339 | `FolioBrowser(QWidget)`, `ChargeDialog(QDialog 640×400)`, `PaymentDialog(QDialog QFormLayout)`, `AmendDialog(QDialog QDateEdit)` | ❌ `resize(640,400)` / `resize(920,580)` — not FixedSingle | `theme.palette()` → text `#000000`, `text_dim #404040/#64748b`, `status_colors()` danger/success; `QTableWidget AlternatingRows, ResizeToContents` | ✅ full |
| P2 | `ui/checkout_ui.py` | 368 | `CheckOutBrowser(QDialog 1100×650)` with `QTabWidget Active/CheckedOut` | ❌ `resize(1100,650)` | `status_colors() danger_text/success_text`, `role danger/warning`, `lblBal Segoe UI 11 Bold`, `setAlternatingRowColors True` | ✅ full |
| P3 | `ui/fo_sub_forms_ui.py` | 423 | 4× `QMainWindow` (`RoomLookupWindow 600×400`, `RoomChangeWindow 680×480`, `MergeChargeWindow 640×460`, `ReSettlementWindow 720×540`) | ❌ `resize` + `QMainWindow` not Fixed Dialog | `palette() #000`, plain `Stretch` header, `role danger/warning` | ✅ full |
| P4 | `ui/frontoffice.py` | 236 | `CheckInBrowser(QDialog 1060×560)` + `guestprof_config() MasterConfig` | ❌ `resize(1060,560)` | `theme.palette()` text_dim, `BaseMasterForm` via `base_master` | ✅ full |
| P5 | `ui/front_office_dashboard.py` | 860 | `FrontOfficeDashboard(QWidget)` + `StatCard(QFrame glassCard 96-115px)` + `RoomRackItem 110×85` | ❌ expanding / fixed 110×85 tile | `glassCard` QSS `background surface rgba`, `border rgba + border-left 4px accent`, `hover surface_hover`; `RoomRackItem` rgba tints 0.15 | ✅ full |
| P6 | `ui/roomstatus_ui.py` | 345 | `RoomStatusForm(QDialog 1150×680)` `QGroupBox Summary + QTable 9 cols + HK Buttons` | ❌ `resize(1150,680)` | `status_colors()` `success_bg/warning_bg/danger_bg/neutral_bg` + manual cell bg/fg | ✅ full |
| P7 | `ui/plan_master.py` | 217 | `PlanMasterForm(QDialog 640×460)` Idle/Add/Edit | ❌ `resize(640,460)` + `setMinimumSize 680×520` in base_master equivalent | `theme` not vb_pale_yellow bevel; `QTable 4 cols Code/Name/Total/Active` | ✅ full |
| P8 | `ui/theme.py` | 754 | `DEFAULTS VB6 Classic` radius 0 + PRESETS | — | `accent #000080 navy, bg #d4d0c8 gray, surface #fff, border #808080, radius 0, vb_mint #c2e0ce vb_pink #ffc0ff vb_pale_yellow #ffffc0 vb_navy #000080 vb_maroon #800000, glass_opacity 0.95` + `_glass_qss` bevel inject for `R==0` | ✅ full |

### 0.3 Screenshots Referenced

`02_WalkIn_CheckIn.png` (WalkIn/CheckIn master form with tariff matrix), `03_CheckIn_List.png` (CheckIn List grid), `04_Room_Status.png` / `10_InHouse_Room_Status.png` (rack color legend), `05_Bill_Reprint.png` (Bill Reprint separate from Settlement), `06_Bill_ReSettlement.png` (ReSettlement ModeSet S + Total/Paid/Balance boxes), `08_Merge_Folio.png` / `09_Reverse_Merge_Folio.png` (merge source→target RelatedFolio linkage), `11_Add_New_Profile.png` (Guest Add). Cross-checked against VB6 ClientWidth/overlay positions — screenshots show WalkIn FrmPackage mint 80FF80 visually matches VB6, Bill ReSettlement shows 3 white boxes + mint shape border verbatim.

---

## 1. VB6 Controls Verbatim — Full Declarative Dump

### 1.1 `fdCheckIn.frm:2-114` — *Look Up Reservation By Guest Name* — `fdCheckIn:11340×4515`

```vb
VERSION 5.00
Begin VB.Form fdCheckIn
  Caption         =   "Look Up Reservation By Guest Name"
  BackColor       =   &HC6B7A4&        ' BGR C6 B7 A4 -> RGB #A4B7C6
  ClientLeft      =   45
  ClientTop       =   615
  ClientWidth     =   11340            ' 756 px
  ClientHeight    =   4515             ' 301 px
  ScaleMode       =   1
  BorderStyle     =   1 'Fixed Single
  MaxButton       =   0
  MinButton       =   0
  Visible         =   0
  MDIChild        =   -1
  KeyPreview      =   -1
  FontTransparent =   True
  WhatsThisHelp   =   -1
  BeginProperty Font: MS Sans Serif 9.75 400
  Begin MainCtrl TopCtrl1       Left 0 Top 0 Width 11340 Height 450 Visible 0 TabIndex 6
  Begin BtnEnh CmdOK            Left 5400 Top 2865 Width 1155 Height 975 TabIndex 5
  Begin PictureBox Picture2     Left 10665 Top 6915 Width 300 Height 270 Visible 0 TabIndex 4 Picture frx:0 ScaleMode 1
  Begin TextBox Txt Index 0     Left 1560 Top 615 Width 9270 Height 285 TabIndex 0 BorderStyle 0 None Appearance 0 Flat ForeColor &HC00000& Font Arial 9.75 400
  Begin DataGrid DGHelp         Left 210 Top 915 Width 10965 Height 3375 Visible 0 TabStop 0 TabIndex 2
  Begin MSFlexGrid FGPoint      Left 15 Top 3585 Width 1980 Height 1440 Visible 0 TabIndex 3
  Begin Label Label1 Index 0    Caption "Guest Name" Left 360 Top 615 Width 1155 Height 240 TabIndex 1 AutoSize -1 BackStyle 0 Transparent ForeColor &HC00000 Font Arial 9.75 700
End
```

**Workflow verbatim (code):**
- `Form_Load:224` builds **Booking join** — `SELECT Booking.DocId AS CODE, GuestProf.Name, Booking.GuestProf, Booking.DocId AS ID, RoomCat.Name AS RoomType, RoomMast.Code AS RoomNo, Booking.ArrDate AS Arr_Date, Booking.NoDays AS tot_Days, Booking.NoOfRooms as NO_Rooms FROM ((Booking LEFT JOIN RoomCat ON Booking.RoomType=RoomCat.Type AND Booking.RoomCat=RoomCat.Code) LEFT JOIN RoomMast ON Booking.RoomType=RoomMast.Type AND Booking.RoomNo=RoomMast.Code) INNER JOIN GuestProf ON Booking.GuestProf=GuestProf.Code WHERE BOOKING.CANCEL='N' AND BOOKING.LOGSITE_CODE='<site>' AND (Select Count(Distinct Sno) From GrpBookingDetails Where Not Exists (Select Distinct isnull(BookingDocid,'') As BookingDocId,BookingSno As Sno from GuestFolio Where GrpBookingDetails.BookingDocId=GuestFolio.BookingDocId And GrpBookingDetails.Sno=GuestFolio.BookingSno) And IsNull(Cancel,'')<>'Y' And GrpBookingDetails.ArrDate='<today>') AND GrpBookingDetails.BookingDocid=Booking.DocId)>0 ORDER BY GuestProf.Name`
  - Semantics: only SNOs with `ArrDate = today` that have **not yet been converted to GuestFolio**.
- `DGHelp_UnknownEvent_9:121` — `DGHelp.Visible=False`, `Txt(0).Tag = Fields("Code")`, `Txt(0).Text = Fields("Name")`, `SetFocus`.
- `Txt_GotFocus:285` — `Proc_6_74_E226B0`, positions `DGHelp` under Txt via `Proc_6_137_1193554(Me.DGHelp, global_56, Index)` + `FGPoint` helper, `SelStart 0 SelLength Len(Text)`, incremental Find `Name='...'`.
- `Txt_KeyDown:342` — `Esc (0x1B)` → hide DGHelp/FGPoint; `KeyCode 0` → `Proc_6_69_134A198(Me.DGHelp, Me.Txt, 0, global_56, Shift,0)` then arrows `0x26 ↑ 0x28 ↓ 0x25 ← 0x27 → 0x21 PgUp 0x22 PgDn` via `Proc_6_138_106D6F8`; `0x28 / 0x0D Enter` → `Proc_6_75_E527CC`, `0x26` → `Proc_6_76_E52838`.
- `Txt_KeyPress:369` — if DGHelp visible → `Proc_6_89_146F1AC(Me.Txt,KeyAscii,global_56,DGHelp.Visible,"Name")` + `Proc_6_138_106D6F8`.
- `Txt_Validate:384` — `Txt(0).Text = Fields("Name")`, `Tag=Fields("Code")`.
- `CmdOK_UnknownEvent_9:184` — guard `If CDate(today) < Fields("Arr_Date") Then MsgBox "Guest Arrived Before Arrival Date !" & vbCrLf & "Checked in Anyway?" vbYesNo 0x24 → 7=No→Exit`; else `fdWalkInEntry.AdvType="CHK" : FrmType="Check In Entry" : TopCtrl1_UnknownEvent_A()` + `SEARCHBACKPARENT(GuestProf, Code)` + `Proc_6_39_E7C810 + Unload Me`.
- `TopCtrl1_UnknownEvent_16:143` — `BeginTrans / CommitTrans / RollbackTrans` around `Requery + Find "SearchCode='"`.

### 1.2 `FdCheckOut.frm:2-126` — *Room Check Out* — `FdCheckOut:14625×8310` (975×554 px)

```vb
Begin VB.Form FdCheckOut
  Caption "Room Check Out"  BackColor &HC0C0C0&  Client 14625×8310  ClientLeft 210 ClientTop 1335
  ControlBox 0  KeyPreview -1  ScaleMode 1  Icon frx:0
  Begin Frame Frame1  Caption "Frame1" BackColor &HFFC0C0& Left -15 Top -30 Width 16800 Height 9375 BorderStyle 0 None
    Begin DataGrid DGRoomType  Left 11760 Top 5760 Width 5025 Height 3330 Visible 0 TabStop 0 TabIndex 18
    Begin DataGrid DGRoomNo    Left 13950 Top 5220 Width 3840 Height 3330 Visible 0 TabStop 0 TabIndex 17
    Begin Frame FrmAdjust     Left 7485 Top 5595 Width 4050 Height 1560 Visible 0 TabIndex 52
      Begin CommandButton Command3 Caption "Cancel" Left 2805 Top 720 Width 795 Height 315 Enabled 0 Font Tahoma 8.25 700
      Begin TextBox Txt Index 24 Back &HFFFFFF& Left 1500 Top 735 Width 1260 Height 315 Enabled 0 Alignment 1 Right MaxLen 8 Font Tahoma 9.75
      Begin TextBox Txt Index 23 Back &HFFFFFF& Left 1005 Top 225 Width 2115 Height 315 PasswordChar "#" MaxLen 50
      Begin CommandButton CMDSET Caption "Set" Left 1710 Top 1110 Width 795 Height 315 Enabled 0 Font Tahoma 8.25 700
      Begin CommandButton CmdPass Caption "GO" Left 3135 Top 225 Width 495 Height 315 Font Tahoma 8.25 700
      Begin Label Lbl Index 12 Caption "Room Rate" Fore &H0& Left 420 Top 750 Font Tahoma 9.75
      Begin Label Lbl Index 0  Caption "Password"   Fore &H0& Left 120 Top 270 Font Tahoma 9.75
    Begin TextBox Txt Index 22 Left 3180 Top 1005 Width 870 Height 285 Visible 0 Enabled 0 Border 0 None Fore &HC00000 Font Arial 9.75
    Begin Timer Timer1 Interval 1000 Left 0 Top 0
    Begin CommandButton Command1 Caption "Command1" Left 120 Top 75 Width 1050 Height 195 Visible 0
    Begin PictureBox Picture2 Left 14655 Top 2295 Width 300 Height 285 Visible 0 Picture frx:442 Scale 1
    Begin TextBox TxtGrid Index 0 Left 5685 Top 1305 Width 345 Height 240 Visible 0 Border 0 None Fore &HC00000 Font Arial 9.75
    Begin CommandButton Command2 Caption "Bill Settle" Left 15225 Top 3045 Width 1320 Height 690 Visible 0 Font Tahoma 9.75 700
    Begin TextBox Txt 15/14 420×285 Center Locked -1 at 3180/3630,1635
    Begin TextBox Txt 13 1545×285 at 1605,1635  etc. (full dump: Txt16/17/18 3810×285 at 1290,5805/5490/5175 ; Txt21/20/19 3810×285 at 1290,4545/4230/3915 ; Txt4 2460×285 ; Txt6/5 480×285 ; Txt7 990×285 hidden ; Txt8 990×285 ; Txt0 690×285 ; Txt1 1545×285 ; Txt9/11/12 3810×285 ; Txt3/2 420×285 Center ; Txt10 1545×285)
    Begin MSHFlexGrid FGrid Left 5385 Top 990 Width 8610 Height 6645 TabIndex 44
    Begin MSHFlexGrid Fgrid1 Left 5385 Top 7635 Width 8610 Height 285 TabIndex 45
    Begin MSFlexGrid FGPoint Left 14655 Top 30 Width 1980 Height 1440 Visible 0 TabIndex 46
    Begin BtnEnh BtnExit Left 2400 Top 7335 Width 1650 Height 750 TabIndex 61
    Begin BtnEnh CmdPostChrg Left 1545 Top 6600 Width 1575 Height 780 TabIndex 62
    Begin BtnEnh CmdPlanBill Left 3135 Top 6615 Width 1635 Height 720 TabIndex 63
    Begin BtnEnh cmdProvisional Left 975 Top 8115 Width 1560 Height 735 Visible 0
    Begin Label LblFormCaption BackColor &HC0FFFF& Left 0 Top 0 Width 180 Height 540 Border 1 Fixed Single Align Center Font System 19.5 700
    Begin Image GuestImage Left 15570 Top 6825 Width 1035 Height 525 Visible 0 Stretch -1
    Begin Label Label1 Index 0 Caption "Guest Folio Details" Back &HC00000& Fore &HFFFFFF& Left 5385 Top 585 Width 8535 Height 375 Align Center Font Arial 9.75 700
    Begin Label Lbl Index 4 Caption "Depature Date" Fore &H800000& Left 120 Top 1650 Font Arial 9.75 700
    ... (Lbl Comment1/2/3, Address, Guest Detail header 5100×375 at 90,3180, Room Details 5100×375 at 75,585, Adult/Child, Rate Code, Room Rate, Room Type, Check In Date, CheckInDay "." Fore &HC0& at 4095,1335 Tahoma)
  End
  Begin TopCtrl TopCtrl1 Left 45 Top 7455 Width 7380 Height 375 TabIndex 1
End
```

**Checkout gates verbatim (`Command2_Click:1245`):**
1. `SELECT isnull(bill_no,'') as Bill_No,AmtDr from paycharge where LogSite_Code='<site>' AND (ContraDocId is NULL or '') and foliono=<folio> Filter "Bill_No='' and AmtDr<>0" → MsgBox "First Print Bill"` (plain `0x40`).
2. `SELECT distinct bill_no from paycharge where Bill_NO<>'' AND NOT NULL and foliono=<folio> → RecordCount 0 → "First Print Bill"`.
3. `SELECT Sum(AmtDr)-Sum(AmtCr) as Bal from PayCharge where LogSite_Code='<site>' and VType Not In ('ARRES','ADRES') and Foliono=<folio>` → `Bal<>0 → "Guest Balance is Not Zero"` + offer `fdPaymentCharge`.
4. Date guard `If CDate(VDate) <= Enviro.CurDate Then`.
5. `BeginTrans` → `UPDATE RoomOcc set chkouttime='<HH:nn>',ChkOutDate=<F25>,UserchkoutDate=<F25>,ChkOutUser='<user>',Type='O',U_EntDt=<Now>,U_AE='E' where Docid='<Tag>' and LogSite_Code='<site>' and RoomNO='<room>' and (Type='' or Type is NULL)` → `UPDATE RoomMast set ROOMSTAT='D' WHERE logsite_code='<site>' and CODE='<room>' AND TYPE='RO'` → `UPDATE PayCharge set SettleDate=<date> where FolioNoDocid='<folDoc>'` → optional `EPABX_IN` insert if `Enviro.EPABX='Y'` → `CommitTrans`.

### 1.3 `fdDisplayFolio.frm:2-20` — *Guest Ledger* — `fdDisplayFolio:14235×8985` (949×599 px)

```vb
Begin VB.Form fdDisplayFolio
  Caption "Guest Ledger"  BackColor &HFFC0C0&  Client 14235×8985  LockControls -1
  ControlBox 0 KeyPreview -1  ClientLeft 60 ClientTop 345
  Begin TextBox Txt Index 29 Left 1215 Top 6885 Width 3975 Height 285 Enabled 0 Locked -1 Border 0 None Fore &HC00000 Font Arial 9.75
  Begin MainCtrl TopCtrl1 Left 0 Top 8535 Width 14235 Height 450 Visible 0 TabIndex 66
  Begin MSHFlexGrid FRectGrid Left 5925 Top 4830 Width 4065 Height 1020 Visible 0 TabIndex 62
  Begin TextBox Txt Index 25 Left 1335 Top 3255 Width 1185 Height 285 Enabled 0 RightJustify Locked -1 Fore &HC00000
  Begin Frame FrmAdjust Left 7515 Top 3165 Width 4050 Height 1590 Visible 0  (same GO/Set/Cancel pattern as CheckOut)
  Begin PictureBox Picture2 Left 10560 Top 150 Width 315 Height 270 Visible 0 Picture frx:442
  Begin TextBox Txt 26/27/28 3975×285 at 1215,4365/4680/4995  ; Txt22 1545×285 at 1335,1680 ; Txt21/20 420 Center ; Txt19 3975×285 ; Txt18 3975×285 ; Txt17 3975 ; Txt6 1545 ; Txt5/4 420 Center ; Txt16 hidden 990×255 ; Txt10 1545 ; Txt2/3 Center Bold 9 ; Txt9 3975 ; Txt8 3975 ; Txt7 3975 ; Txt1 1545 ; Txt0 780×330 ; Txt15 Right 1185 ; Txt14 hidden ; Txt12/13 420 Center ; Txt11 2445 ; FGPoint 1980×1440 hidden ; DGRoomNo 5655×1305 hidden ; FGrid 8775×5580 at 5235,1020 ; Fgrid1 8445×285 at 5205,6645 ; DGChrgPayment 4980×690 hidden ; FRectGrid ; CmdExit 1275×1050 at 7620,7110 ; CmdPrint 1275×1050 at 4560,7155
  Begin Label Lbl Index 14 "Status" Fore &HC00000 Left 180 Top 6885 Font Arial 9 700
  Begin Label LblFormCaption Back &HC0FFFF& 180×540 System 19.5
  Begin Label Lbl Index 16 "PlanAmount" Fore &HC00000 Left 120 Top 3270 Font Arial 9 700
  Begin Label Label1 Index 2 "Guest Details" Back &HC00000 Fore &HFFFFFF Left 90 Top 3600 Width 5040 Height 375 Align Center Font Arial 9.75 700
  Begin Label Lbl Index 2 "Address" Fore &HC00000 Left 150 Top 4365 Font Arial 9 700
  Begin Label Lbl Index 15 "Chk Out Date" Fore &HC00000 Left 120 Top 1680 Font Arial 9 700
  ... (Comment1/2/3, Exp.Dep.Date, LblVPrefix "." Back &HF9CECE Fore &H4080, Charge Details Back &HC00000 at 5235,585 8190×375, Guest Folio No, GSTIN, Company, Guest Name, LblCheckInDay "." Fore &H4080 at 3810,1365, Check In Date, Room Type 945×285, Room Rate, Rate Code hidden, Adult/Child, Guest Room For Room No. Back &HC00000 at 60,585)
End
```

**Logic:** `Txt_Validate:1477` — same `Enviro` date, `FolioNoDocid` tag stash, `ChkInDate/Time` split `Left(Right())`, `ChkOutDate/Time`, `DepDate/Time`, `RateCode`, `STATUSNAME`, `OldAdult/Child`, `Comments1/2/3`, `Add1/2 + City/State/CountryName`, `max(NetPackageAmount) from Plandetails where Docid='<doc>' And RoomNo='<room>'` → `PkgAmt`, auto `RoomRentChkOutPost` loop posting.

### 1.4 `fdRoomChange.frm:2-20` — *Room Change* — `fdRoomChange:12270×8595` (818×573 px)

```vb
Begin VB.Form fdRoomChange
  Caption "Room Change"  BackColor &HFFC0C0&  Client 12270×8595  LockControls -1  Font Tahoma 8.25 400
  Begin DataGrid DGPackage Left 3180 Top 1005 Width 4230 Height 1920 Visible 0 TabStop 0
  Begin Frame FrPackage BackColor &HFFC0C0 ForeColor &HC00000 Left 1005 Top 570 Width 10125 Height 4980 Visible 0 Appearance 0 Flat
    Begin TextBox Txt 31 Left 4890 Top 435 Width 900 Height 270 Border 0 None Align 1 Right Max 30 Font Arial 9 700 Fore &HC00000
    Begin TextBox Txt 42 Left 6000 Top 435 Width 900 Height 270 ... Right
    Begin TextBox Txt 45 Left 6000 Top 720 Width 900 Height 270 ... Right
    Begin TextBox Txt 44 Left 4890 Top 720 Width 900 Height 270 ... Right
    Begin TextBox Txt 47 Left 8100 Top 150 Width 1605 Height 270 Visible 0 Enabled 0 Locked -1 Font Tahoma 9.75
    Begin TextBox Txt 48 Left 7335 Top 3825 Width 1290 Height 270 Locked -1 Align 1 Right Font Tahoma 9.75
    Begin TextBox Txt 46 Left 2175 Top 1005 Width 1035 Height 270 Locked -1 Align 1 Right Font Arial 9 700
    Begin TextBox Txt 43 Left 2175 Top 720 Width 345 Height 270 Text "Yes" Align 2 Center Font Tahoma 9.75
    Begin TextBox TxtGrid Index 0 Left 60 Top 1650 Width 975 Height 240 Visible 0 Border 0 None Fore &H80000012 Font Tahoma 9.75
    Begin TextBox Txt 24 Left 2175 Top 150 Width 4230 Height 270 Locked -1 Font Arial 9 700
    Begin CommandButton CmdOk Caption "&Ok" Left 3615 Top 4125 Width 1740 Height 465 Font Tahoma 8.25 700
    Begin TextBox Txt 25 Left 2175 Top 435 Width 1080 Height 270 Align 1 Right Font Arial 9 700
    Begin MSHFlexGrid FGrid3 Left 45 Top 1410 Width 9510 Height 2415
    ... Labels: Extra Person @ 1110 at 3375,435, "@" at 5820,450, "-" LblDiscAppOn at 7005,720, "%" at 5790,735, Package Discount 1590 at 3345,720, lblLTDet Fore &HC0& at 75,3780, Calculation Mode hidden at 6540,150, Total Package Amount 1920 at 5295,3840, "-" at 3300,1035, Room Rate 930 at 60,1005, Yes/No 585 at 2550,720, Inc. in Room Rate 1470 at 60,720, Plan/Package 1170 at 60,150, Plan/Package Amount 1875 at 60,435
  Begin TextBox Txt 50 Left 11205 Top 4125 Width 1125 Height 285 Visible 0 Border 0 None Fore &HC00000 Font Arial 9.75
  Begin MainCtrl TopCtrl1 Left 0 Top 8130 Width 12270 Height 465 Visible 0
  Begin Frame Frame1 Left 14160 Top 6840 Width 1230 Height 1245 Visible 0
  Begin TextBox Txt 30 Left 4545 Top 6015 Width 4350 Height 285 Locked -1 Fore &HC00000 Max 30
  Begin TextBox Txt 40 Left 7770 Top 5385 Width 1125 Height 285 Max 5
  Begin TextBox Txt 49 Left 13935 Top 2370 Width 480 Height 285 Visible 0 Max 2 Font Tahoma 9.75
  Begin TextBox Txt 5/6 Visible 0 Enabled 0 at 15765/16320,4095 525/510 Center
  Begin TextBox Txt 4 Visible 0 Enabled 0 at 14010,4095 1725
  Begin TextBox Txt 11 Left 4545 Top 4125 Width 4350 Height 285 Max 35
  Begin TextBox Txt 12 Left 4545 Top 4755 Width 1140 Height 285 Max 5
  Begin TextBox Txt 14 Left 8355 Top 4755 Width 540 Height 285 Max 2
  Begin TextBox Txt 13 Left 7755 Top 4755 Width 570 Height 285 Max 2
  Begin TextBox Txt 15 Left 4545 Top 5070 Width 1140 Height 285 Max 1
  Begin TextBox Txt 16 Left 7755 Top 5070 Width 1140 Height 285 Max 8
  Begin PictureBox Picture1 Left 14145 Top 3315 Width 300 Height 285 Visible 0 Picture frx:442 Scale 1 Font MS Sans Serif 8.25
  Begin TextBox Txt 29 Left 4545 Top 4440 Width 4350 Height 285 Max 100
  Begin PictureBox Picture4 Left 18300 Top 4080 Width 300 Height 270 Visible 0 Picture frx:790
  Begin TextBox Txt 38 Left 4545 Top 5700 Width 510 Height 285 Text "No" Max 8
  Begin TextBox Txt 39 Left 4545 Top 5385 Width 1140 Height 285 Max 5
  Begin TextBox Txt 41 Left 7770 Top 5700 Width 540 Height 285 Text "No" Max 8
  Begin TextBox Txt 18 Left 13770 Top 1725 Width 480 Height 285 Visible 0 Enabled 0 Font MS Sans Serif 8.25
  Begin PictureBox Picture2 Left 15060 Top 330 Width 300 Height 270 Visible 0 Picture frx:ADE Scale 1
  Begin Frame Frmrate BackColor &HFF0000& Left 14190 Top 180 Width 4830 Height 795 Visible 0 Border 0 None
    Begin TextBox Txt 22 Left 1440 Top 120 Width 3285 Height 270 Max 30 Font MS Sans Serif 8.25
    Begin TextBox Txt 23 Left 1440 Top 420 Width 3285 Height 270 Max 30
    Begin Label Lbl 47 "Remarks" Fore &HFFFFFF Left 120 Top 45 Font Tahoma 9.75
    Begin Label Lbl 48 "Authorization" Fore &HFFFFFF Left 45 Top 405 Font Tahoma 9.75
    Begin Label Label4 "*" Fore &HFF& Left 930 Top 105 Font Tahoma 9 700 Align 1 Right
    Begin Label Label5 "*" Fore &HFF& Left 1215 Top 405 Font Tahoma 9 700
  Begin DataGrid DGPlanPkg Left 165 Top 5370 Width 3285 Height 1650 Visible 0 TabStop 0
  Begin DataGrid DGNewRoomNo Left 14805 Top 1815 Width 2805 Height 1875 Visible 0 TabStop 0
  Begin DataGrid DGRoomNo Left 14700 Top 1410 Width 2685 Height 1695 Visible 0 TabStop 0
End
```

**Logic keys:**
- `Txt_GotFocus:1291` — Index 0→`DGRoomNo` + `global_88`, 0x0B→room name, 0x0C→new room DGNewRoomNo, 0x18→DGPackage `PlanMast where ROOMCAT='<tag>' AND (LOGSITE_CODE='<site>' or 'HO') and ActiveYn='Yes' and App_date<=today ORDER BY Name`, 0x1E→DGPlanPkg, 0x10→global_72. Shadows DG* positioning via `mapToGlobal(Left+Height+30)`.
- `Txt_KeyDown:1506` — `Esc(0x1B)` hides + Unload, `KeyCode 0` triggers `Proc_6_69_134A198` for DG navigation, `0x28/0x0D Enter` advances via `Proc_6_75_E527CC`, `0x26 ↑` via `Proc_6_76_E52838`. With `DGPackage.Visible=0` etc. check, `KeyCode 0x0C (12)` branch validates KOT pending `Select * from KOT Where Pending='Y' and RoomNo='<room>' and roomtype='RO' and VoidYN='N' and NCKOT<>'Y' and DelFlag<>'Y'` → `"There is some KOT Pending for this Room." 0x10`. Tariff prompt `"Apply Tariff as per defined Condition?" 0x24 → Yes 6`.
- `Type='C'` pattern in `room_occ`: old SNo `chkoutdate/time, Type='C', NewRoomNo='<new>', Reason, Tariff shift`, new SNo `Type='' open`, Booking.OccRoom update, `RoomMast ROOMSTAT='D'` dirty, `PlanDetails` reinsert.

### 1.5 `FdRoomDisplay.frm:2-85` — *Room View* — Rack

```vb
Begin VB.Form FdRoomDisplay
  Caption "Room View"  BackColor &HFFC0C0&  WindowState 2  ScaleMode 1  AutoRedraw 0
  FontTransparent -1  Picture frx:0  Icon frx:52A  LinkTopic "Form1"
  ControlBox 0  MDIChild -1  KeyPreview -1  Client 14190×8355 (946×557)
  Begin Frame FrmPic  BackColor &HCBFCF9& ForeColor &HFF0000& Left 15 Top 1305 Width 12855 Height 7590 Appearance 0 Flat BorderStyle 0 None
    Begin Image Picture1 Left 0 Top 0 Width 11160 Height 7545 Stretch -1 BorderStyle 1 Fixed Single
  Begin Frame FrmRoom BackColor &HFFC0FF& ForeColor &H80000008& Left 0 Top 0 Width 19875 Height 11070 Appearance 0 Flat BorderStyle 0 None
    Begin BtnEnh BtnExit Left 10065 Top 525 Width 1350 Height 735 TabIndex 3
    Begin BtnEnh Cmd Index 1 Left 15 Top 540 Width 1350 Height 735 TabIndex 2
    Begin Label LblFormCaption BackColor &HC0FFFF& Left 0 Top 0 Width 180 Height 540 Border 1 Fixed Single Align Center AutoSize -1 Font System 19.5 700
End
```

**Logic:**
- `Form_Load:95` — `select * from roommast where logsite_code='<site>' and type='RO' and inclcount='Y' order by Code` → builds `BtnEnh Cmd()` grid **9 cols** (`var_8E=9`) via `Me.Cmd.Load var_C8`, positions with `DispID_80010004/80010003` (Left/Top), row break `If (var_86 Mod 9)=0` then next row `Top +=`. Sets `FrmRoom 11580×7500 at 15,10 then FrmPic same, Picture1 stretches to same`.
- `Cmd_UnknownEvent_9:238` — `Select PicPath From RoomMast Where ... Code='<code>'` → if `PicPath IsNull or Trim=''`, LoadPicture default; else if DAT/AVI → hide; else `LoadPicture <PicPath>` stretch + `Refresh` + centered via `Proc_104_5_EB09E0` (`Top=(FrmPic.H - Pic.H)/2 Left=...`). `FrmPic.Visible=True`.
- `Form_KeyDown:225` — `0x1B Esc → FrmPic.Visible=False`, `0x79 (F10/121) → Unload Me`.
- `Form_Resize:214` — `LblFormCaption.Caption = <title>; Left 0; Width = <parent>.Width`.

### 1.6 `FdReSetlement.frm:2-115` — *Post Charges/Payment* (Bill ReSettlement) — `9555×7350`

```vb
Begin VB.Form FdReSetlement
  Caption "Post Charges/Payment"  BackColor &HFFC0C0&  WindowState 2  ScaleMode 1
  ControlBox 0  MDIChild -1  KeyPreview -1  Client 9555×7350  LockControls -1  Font Tahoma 9.75 400
  Begin MainCtrl TopCtrl1 Left 0 Top 6900 Width 9555 Height 450 Visible 0 TabIndex 106
  Begin DataGrid DGMember Left 13650 Top 6195 Width 4215 Height 3330 Visible 0 TabStop 0
  Begin Frame FrMember BackColor &HFFC0C0 Left 165 Top 8055 Width 6000 Height 315 Visible 0 Border 0 None (Txt39 4000×285 at 1650,30 + LblName Member Fore &HC00000 780×240)
  Begin DataGrid DGBill Left 13320 Top 5610 Width 6780 Height 3390 Visible 0 TabStop 0
  Begin PictureBox Picture2 Left 18870 Top 7860 Width 300 Height 270 Visible 0 Picture frx:0 Scale 1 Font MS Sans Serif 8.25
  Begin PictureBox Picture1 Left 19620 Top 7665 Width 300 Height 270 Visible 0 Picture frx:34E Scale 1
  Begin TextBox Txt 38 Left 3075 Top 1395 Width 930 Height 285 Visible 0 Max 5 Fore &HC00000
  Begin TextBox Txt 36 Left 1500 Top 1080 Width 1545 Height 285 Align 1 Right Max 8 &HFFFFFF& Fore &HC00000
  Begin Timer Timer1 Interval 1000 Left 10350 Top 0
  Begin DataGrid DGRoom Left 12600 Top 5700 Width 3885 Height 3390 Visible 0 TabStop 0
  Begin DataGrid DGRoomNo Left 13980 Top 4890 Width 2580 Height 3330 Visible 0 TabStop 0
  Begin DataGrid DGEmp Left 12555 Top 4980 Width 4170 Height 3330 Visible 0 TabStop 0
  Begin DataGrid DGChrgPayment Left 15795 Top 4860 Width 5490 Height 3465 Visible 0 TabStop 0
  Begin TextBox Txt 35 Left 9570 Top 1740 Width 1500 Height 285 Align 1 Right Max 9 &HFFFFFF& Fore &HC00000
  Begin TextBox Txt 11 Left 1485 Top 2340 Width 2535 Height 285 Enabled 0 Max 16 Fore &HC00000
  ... (Txt13/12 Center 480/495, Txt14 hidden, Txt15 Right 1005, Txt0 765×285 at 4035,660, Txt1 1545, Txt7/8/9 Status/Comments 3930, Txt3/2/10/30/29/31/34/33/32/28/27/26 detail, DGCompany 4215×3330 hidden, FrComp 6000×330 at 150,8370 with Txt25, Picture4, FrCCDet 6000×960 at 5415,2340 with Txt37/20/19/18 BatchNo, FrEmp 6000×330 at 165,7740 with Txt23, FrSendRoom 6000×330, FrChqDet 6000×645, Txt17/16 hidden, Txt6 PayType helper, Txt5 Comments, Txt4 Locked, MaskEdBox txtVTime 750×285 at 10320,1110, FGrid 5790×2430 at 5895,3750, FGPoint 1980×1440 hidden at 16455,7860, BtnEnh CmdExit 1350×1050 at 8940,7575, BtnSave 1350×1050 at 6990,7560, Line1 &HC00000 X1 7020 Y1 7005 X2 10275 Y2 7005 BorderWidth 2, Labels Label1 Index 3 "Settlement Details" Back &HC00000 Fore &HFFFFFF Left 5370 Top 3375 Width 6765 Height 375 Align Center Font Arial 9.75 700, Lbl 8 "Vr. Date" Fore &HC00000 Left 5400 Top 1140, Lbl 15 "Tip", Label1 Index 2 "Payment Detail" Back &HC00000 Left 5340 Top 615 Width 6765 Height 375, ... Lbl Nature "." Back &HFFC0C0 Fore &H4080 at 11130,1410, LTxt0/1/2 glass boxes 1605×285 at 7095/8625 positions Border Fixed Single Align Center Tahoma 9 Bold, LblName Total/Paid/Balance 1500×285, Shape5 Border &HC00000 Fill &HC0FFC0 at 7035,6270 Width 3255 Height 1200, LblFormCaption &HC0FFFF 180×540 System 19.5, Timer-driven clocks)
End
```

**Logic — ModeSet='S' + sum guard:**
- `PayCharge WHERE FolioNoDocid='<doc>' AND ModeSet='S' AND PayCode<>'<site>ROFF' ORDER BY Vdate DESC,VNo` → old settlement rows (`DocId,VNo,Vdate,PayCode,PayType,AmtCr...`) filled into `FGrid`.
- Old sum `SUM(AmtCr) WHERE ModeSet='S' and DocId='<oldDoc>'` → `oldTotal`.
- New lines `SELECT DocId,VNo,...` + sum `SUM(amount)` → `newTotal` guard `ABS(newTotal - oldTotal) < 0.005` else `ValueError "New settlement total must equal original"`.
- On save: `BeginTrans` → `DELETE FROM PayCharge WHERE DocId='<oldDoc>' AND FolioNoDocid='<doc>' AND Site_Code='<site>' AND ModeSet='S'` → per-line `next_vno('REC')` + 21-char DocId `D<Site>REC<yyMM><folio>` `RestCode='KKFOM' ModeSet='S' VType='REC'`.

### 1.7 `fdWalkInEntry.frm:2-804` — *Walk In / Check In Entry* — `13995×8595`

```vb
Begin VB.Form fdWalkInEntry
  Caption "Walk In / Check In Entry" BackColor &HFFC0C0 WindowState 2 ScaleMode 1 MDIChild -1 ControlBox 0 KeyPreview -1 Client 13995×8595 LockControls -1
  Begin Frame FrmPackage BackColor &H80FF80 ForeColor &H80000008 Left 30 Top 3990 Width 10005 Height 3900 Visible 0 Appearance 0 Flat BorderStyle 0 None
    Begin DataGrid DGPackage Left 2190 Top 420 Width 4230 Height 3270 Visible 0 TabStop 0
    Begin BtnEnh CmdOk Left 3495 Top 3300 Width 1110 Height 510
    Begin TextBox Txt 54 Left 2175 Top 405 Width 1080 Height 255 Align 1 Right Max 30 Fore &HFF0000 Font Arial 9.75
    Begin TextBox Txt 53 Left 2175 Top 135 Width 4230 Height 255 Locked -1 Max 30 Fore &HFF0000
    Begin TextBox TxtGrid 2 Left 105 Top 1485 Width 975 Height 240 Visible 0 Border 0 None Fore &H80000012 Font Tahoma 9.75
    Begin TextBox Txt 67 Left 2175 Top 675 Width 345 Height 255 Text "Yes" Align 2 Center Max 30 Fore &HFF0000
    Begin TextBox Txt 68 Left 2175 Top 945 Width 1035 Height 255 Locked -1 Align 1 Right Max 30 Fore &HFF0000
    Begin TextBox Txt 69 Left 8475 Top 3000 Width 1290 Height 255 Locked -1 Align 1 Right Max 30
    Begin TextBox Txt 70 Left 8100 Top 135 Width 1605 Height 255 Visible 0 Enabled 0 Locked -1 Font Tahoma 9.75
    Begin TextBox Txt 71 Left 4890 Top 675 Width 900 Height 255 Align 1 Right Max 30
    Begin TextBox Txt 72 Left 6015 Top 675 Width 900 Height 255 Align 1 Right
    Begin TextBox Txt 73 Left 6015 Top 405 Width 900 Height 255 Align 1 Right
    Begin TextBox Txt 74 Left 4890 Top 405 Width 900 Height 255 Align 1 Right
    Begin MSHFlexGrid FGrid3 Left 105 Top 1200 Width 9675 Height 1740
    ... Labels: Plan/Package 1320 at 60,135, Plan/Package Amount 2115 at 60,420, Inc. in Room Rate 1695 at 60,675, Yes/No 645 at 2550,675, Room Rate 1050 at 60,945, "-" LPlanRoomRate at 3300,945, Total Package Amount 2160 at 6465,3000, Calculation Mode hidden at 6840,720, lblLTDet at 240,2910, Package Discount 1590 at 3315,675, "%" at 5805,690, LblDiscAppOn "-" at 6990,675, "@" at 5805,420, Extra Person 1215 at 3375,405
  Begin Frame Frame1 BackColor &HC0FFFF Left 30 Top 900 Width 17955 Height 8910 BorderStyle 0 None
    Begin TextBox Txt 83 Left 1620 Top 5745 Width 3210 Height 285 Max 40 Fore &HC00000
    Begin CommandButton CmdVerifyMember Caption "Verify Member" Left 15 Top 7230 Width 2265 Height 480 Visible 0 Font Tahoma 9.75 700
    Begin TextBox Txt 79 Left 705 Top 7770 Width 1980 Height 255 Visible 0 Enabled 0 Locked -1 Font Tahoma 9
    Begin TextBox Txt 62/61 Left 14370/15585 Top 7290/7320 Width 780 Visible 0 Enabled 0 Max 5 Font Tahoma 9
    Begin TextBox Txt 28 Left 15915 Top 6585 Width 780 Visible 0 Max 50 Font Tahoma 9
    Begin Frame Frame2 Caption "Frame2" BackColor &HC0E0FF ForeColor &H80000008 Left -15 Top 0 Width 13965 Height 6990 Visible 0 Appearance 0 Flat BorderStyle 0 None
      Begin CheckBox ChkFGrid2 Caption "All" BackColor &HFF8080 ForeColor &HFFFFFF Left 30 Top 270 Width 540 Height 195 Font MS Sans Serif 8.25 700 Appearance 0 Flat
      Begin BtnEnh Command5 Left 7260 Top 3870 Width 900 Height 765
  Begin DataGrid DGGrpPlanPkg Left 7230 Top 1065 Width 3360 Height 1245 Visible 0 TabStop 0
  Begin DataGrid DGGrpRoomNo Left 5445 Top 915 Width 1455 Height 1245 Visible 0 TabStop 0
  Begin DataGrid DGGrpRoomCat Left 1980 Top 765 Width 3360 Height 1245 Visible 0 TabStop 0
End
Attribute VB_Name fdWalkInEntry  (AdvType="CHK", FrmType="Check In Entry", SEARCHBACKPARENT(GuestProf,BookingDocId))
```

**Workflow:**
- `CmdNextRoom_Click:1189` — `Type='RO' AND InclCount='Y'` + `Not In RoomOcc where ChkOutDate is NULL` + `Not In RoomBLockOut Type('O','M')` + `Not In GrpBookingDetails where Not Exists GuestFolio` + `ArrDate/DepDate` exclusions → next free code > current.
- `Txt_GotFocus:894` — DGPackage via `PlanMast where ADULTS=<adult> AND ROOMCAT='<tag>' AND LOGSITE_CODE IN ('<site>','HO') and ActiveYn='Yes' and App_date<=today ORDER BY Name`.
- DocId 21-char `D<site>CHK<yy><folio5>??` + FolioNo `MAX+1 WHERE Vprefix='CHK' and FY`. Insert `GuestFolio + RoomOcc SNo 1 Type='I' + FolioLog Flag 'A'`.
- Screenshots 02/03 verify: WalkIn shows Форма with Guest Name + Room Type/No + Plan matrix + Adults/Children; CheckIn List shows grid 03 with Booking# Guest Arrival Departure + Action.

---

## 2. Python Controls — Verbatim Read

### 2.1 `ui/folio_ui.py:1-339` — Folio Unified

```python
# FolioBrowser(QWidget) QVBox
#   top QHBox: QLabel "In-House Folios" + stretch + QPushButton "Refresh" Ctrl+F5
#   QTableWidget SelectRows NoEditTriggers ResizeToContents AlternatingRows cellDoubleClicked->_drill -> ChargeDialog
#   QLabel _empty_label AlignCenter color:text_dim 13px padding 24 "No folios found."
#   bar QHBox: QPushButton "Check-Out (Settle)" Ctrl+O / "Amend Departure" Ctrl+A / "Receive Payment" Ctrl+R / "Folio Log" Ctrl+L + stretch
#   QShortcut Ctrl+O/A/R/L/F5
#   _folios(): db.query("SELECT FolioNo, Name, Vdate, DepDate, DocId, Vprefix FROM GuestFolio WHERE Site_Code=? AND Vprefix=? ORDER BY FolioNo DESC", (SITE_CODE,VREFIX))
# ChargeDialog(QDialog 640×400) QVBox Label + QTable SNo/PayCode/Type/Comments/Dr/Cr + Label Balance + QPushButton Close
# PaymentDialog(QDialog QFormLayout) lblBal + QComboBox PAY_TYPES + QLineEdit Amt "0.00" + QLineEdit Comments "CASH RECD." + QHBox Receive/Cancel
# AmendDialog(QDialog QFormLayout) QDateEdit CalendarPopup cur_dep -> .date() + Save/Cancel
# helpers: _fill(table, headers, rows) clear + setColumnCount + text_col=QColor(palette["text"])
```

**Layout:** No FixedSize, `resize(920,580)` via `open_folio()`, `ChargeDialog resize 640×400` (vs VB6 FRectGrid 4065×1020 + FGrid 8775×5580). No `TopCtrl1 11340×450` hidden, no `BtnEnh CmdOK 1155×975 at 5400,2865`, no `DGHelp 10965×3375 at 210,915 Visible 0`, no `FGPoint 1980×1440`, no `Label Guest Name 1155×240 maroon`. No `BorderStyle 0 None` flat distinction — QLineEdit theme `glass_tint` 1px border.

### 2.2 `ui/checkout_ui.py:1-368` — Check-Out

```python
# CheckOutBrowser(QDialog 1100×650) QVBox QTabWidget
# Tab Active: QWidget QVBox QTableWidget 0×7 FOLIO_COLS FolioNo GuestName GuestProf City Departure Days Status + lblBal QFont Segoe 11 Bold color danger/success + QTableWidget 0×7 CHARGE_COLS VType VNo PayCode Amount Dr/Cr Remarks maxHeight 200 + QHBox btnCheckOut "Check-Out (PYT*)" role danger minHeight34 + btnRefreshA + btnCloseA; cellClicked->_load_charges double->_do_checkout
# Tab Checked-Out: QTable 0×6 FolioNo Guest Departure CheckOutDate ByUser DocId + QHBox btnReverse role warning + Refresh + Close
# signals: btnCheckOut->_do_checkout, btnReverse->_do_reverse, F5 reload, Ctrl+O/R
# reload_active(): checkout.list_active_folios() → status "Checked-Out" if checkout_date else "In-House"
# _do_checkout: PYT guard MsgBox "Safety: sirf PYT* test folios..." + bal check + Confirm Question → checkout.do_checkout(folio,user)
# _do_reverse: PYT guard → checkout.reverse_checkout
```

**Missing vs VB6:** No `Frame1 16800×9375 Back #C0C0FF at -15,-30`, no `FrmAdjust 4050×1560 at 7485,5595` password GO/SET/Cancel (Txt23 PasswordChar `#`, Txt24 Rate, CMDSET, Command3), no `Timer1 1000`, no `GuestImage 1035×525 hidden`, no `DGRoomType 5025×3330 at 11760,5760`, no `DGRoomNo 3840×3330 at 13950,5220`, no `Fgrid1 total row 8610×285 at 5385,7635`, no `LblFormCaption &HC0FFFF System 19.5 at 0,0` (vertical label), no `Command2 Bill Settle hidden`. Python charges table `maxHeight 200` vs VB6 `FGrid 6645px tall`. FixedSize missing — `resize(1100,650)` resizable.

### 2.3 `ui/fo_sub_forms_ui.py:1-423` — 4 Sub-Forms

```python
# RoomLookupWindow(QMainWindow 600×400) QVBox Title AlignCenter Segoe 14 Bold + QHBox Search QLineEdit placeholder + QTable 4 cols RoomNo Category Status GuestName Stretch + Exit
#   _load_data(): SELECT R.Code, RC.Name, R.RoomStat, ISNULL(GP.Name,'') FROM RoomMast R LEFT JOIN RoomCat RC LEFT JOIN RoomOcc G ON R.Code=G.RoomNo AND G.Type='I' LEFT JOIN GuestProf
# RoomChangeWindow(QMainWindow 680×480) QVBox Title + QGroupBox Guest locate QHBox Search QLineEdit placeholder "Room No ya Check-in DocId" returnPressed + btn Load + QGroupBox Current stay QFormLabel Folio/Guest/OldRoom + QGroupBox New room QForm Combo free_rooms() Editable + Reason QLineEdit + QHBox Save Warning + Exit; _load_folio(): open_folio_by_docid or by_room → RoomOcc TOP 1 RoomNo WHERE DocId=? AND ChkOutDate IS NULL; _save(): room_change(docid,new_room,reason)
# MergeChargeWindow(QMainWindow 640×460) QVBox Title + QGroupBox Rooms QForm FromRoom QLineEdit source+textChanged+ ToRoom + lbl_src/tgt + lbl_total + info wrap + QHBox Merge danger Enabled guard src!=tgt && both found + Exit; _refresh(): open_folio_by_room + folio_charge_total; _merge(): merge_charge(from,to)
# ReSettlementWindow(QMainWindow 720×540) QVBox Title + QHBox Folio/Room QLineEdit returnPressed + Load + lbl_folio + QTable 6 cols DocId VNo Date PayType Amount Comments + QGroupBox New settlement QHBox Pay Combo PAY_TYPES + QDoubleSpinBox Amount 0..1e9 decimals2 width140 + Note + Add Line + new_table 4 cols PayCode Amount Comments "" + QHBox Re-Settle warning + Exit; _load(): open_folio_by_docid/room → list_settlements; _add_line() guard Amount>0; _settle(): re_settlement(docid, pending)
```

**Missing:** All `QMainWindow` not `QDialog Fixed Single CenterOwner MDIChild`; no `BackColor #C0C0FF pink frame`, no `FrPackage 10125×4980 at 1005,570 hidden` overlay (Python has inline group), no `Frmrate Back &HFF0000 red`, no `DataGrid DGPackage 4230×1920 hidden at 3180,1005` etc. (`DGPlanPkg/DGNewRoomNo/DGRoomNo` all hidden at far off-screen Left 14k-15k), no `Timer1`, no `Line1/Shape5/LTxt boxes`, no `BorderStyle 0 None` flat distinction. `ReSettlementWindow` lacks VB6 decorative `Line1` (`X1 7020→10275 Y 7005 BorderWidth 2 #C00000`) and `Shape5 Fill #C0FFC0 3255×1200 at 7035,6270` + `LTxt0/1/2 1605×285 Total/Paid/Balance` white fixed single boxes. `RoomChange` lacks 30-col tariff matrix `FGrid3 9510×2415 + FrPackage extras` — only single combo.

### 2.4 `ui/frontoffice.py:1-236` — Guest Profile + Check-In

```python
# guestprof_config() -> MasterConfig title "Guest Profile (P4-a)" columns Code/Name/Add1/City/Phone/Mobile fields 8×Limits + delete_guard PYT
# CheckInBrowser(QDialog 1060×560) QVBox QTable 0×9 COLS Folio VDate Name GuestCode City Days DepDate User AE StretchLast AlternatingRows + empty label + lblState "State: Idle | New = PYT* test check-in DocId 21-char + FolioNo + FolioLog" + QHBox btnNew Ctrl+N + btnRefresh F5 + btnClose Esc; QShortcut Ctrl+N/F5
# _new() inner QDialog QFormLayout Guest Name PYT* Max50 + GuestProf Code blank auto + Arrival QDateEdit CalendarPopup + Departure + City + BookingDocId + Adult/Children + RateCode + ChkInTime HH:MM + Save/Cancel; logic: if !gcode -> guestprof.next_code() KK###### auto insert + n_adult/n_child int parse + checkin.create_checkin(gcode,name,arr,dep,city,bookingdocid,user,adult,children,ratecode,chkintime); lblState set + reload(keep_folio)
# reload(): checkin.list_checkins() → FOLIO* VDATE*? + "%d/%b/%Y"
```

**Missing:** No `fdCheckIn.frm` lookup dialog `DGHelp 10965×3375 at 210,915 Visible 0` under Txt(0), no `FGPoint 1980×1440`, no `TopCtrl1 11340×450 Visible 0`, no `BtnEnh CmdOK 1155×975 at 5400,2865`, no `Picture2 hidden`, no `Fore &HC00000 Arial 9.75 Bold` label positioning exact, no `Arrival Before` validation msg (Python uses checkin guard different), no `SEARCHBACKPARENT` harness.

### 2.5 `ui/front_office_dashboard.py:1-860` — Modern Dashboard

```python
# StatCard(QFrame glassCard 96-115px) QVBox header QHBox icon 16px accent + title 11px 600 text_dim + val 24px 700 text + sub 10px; QSS background surface rgba 0.7 border rgba 0.3 border-left 4px accent hover surface_hover accent
# RoomRackItem(QFrame Fixed 110×85) status map: Occupied rgba(239,68,68,0.15) border #ef4444 badge #ef4444; Dirty amber; Maint gray; Vacant green; Hover border 2.5px; QVBox top_row roomno 14 Bold + badge 8 Bold 2px padding 4px radius + rtype 9 + guest 9 500
# FrontOfficeDashboard(QWidget) _build_ui():
#   top_bar QHBox Hotel 26 Label + VBox title 20 700 + lbl_date Today — Wday d Month + stretch + QPushButton Refresh Live Data 34px surface_solid
#   qa_frame QFrame surface 0.5 border 0.25 radius 10 7 QPushButton Quick Actions + New Reservation etc. (Ctrl+N/O/G/R/Shift+F, F8) 32px hover col
#   cards_grid 2×4 grid StatCard arr/dep/inhouse/avail/occ/vac/dirty/pending + click -> openModule emit
#   stack_widget QVBox view_tables vs view_rack toggle
#   view_tables: strip_frame occupancy gauge + rack_counts + QPushButton Open Visual Room Rack + QHBox split Arrivals Frame QTable 5 cols Booking# Guest Arrival Departure Action Check-In green + Departures Frame QTable 5 cols Folio# Guest Room Dep Action Check-Out amber
#   view_rack: QHBox Filter All/Available/Occupied/Dirty/Maintenance pill 28px radius 14 hover accent -> QScrollArea QGrid 8 cols RoomRackItem clicked->_show_room_dialog QDialog Fixed 380×320 info_box surface_solid border #ccc 8px
#   refresh(): roomstatus.room_rack() -> avail = total-occ, pct, departures today = depdate==today or <=today, arrivals today = reservation where Cancel N + arr_date today
```

**Missing vs `FdRoomDisplay.frm`:** `FdRoomDisplay` has `FrmPic Back &HCBFCF9 #F9FCCB 12855×7590 at 15,1305` with `Picture1 Stretch Border Fixed Single` centered heart, and `FrmRoom Back &HFFC0FF #FFC0FF 19875×11070` with `BtnEnh Cmd(1) 1350×735 at 15,540` grid **9 cols** via `Load` loop. Python uses rgba tiles 110×85 no image stretch, no 1350×735 BtnEnh bevel yellow, no `PicPath` image load, no `LblFormCaption System 19.5 vertical` positioned via Resize.

### 2.6 `ui/roomstatus_ui.py:1-345` — Dedicated Room Status

```python
# RoomStatusForm(QDialog 1150×680) QVBox grpSummary QHBox lblTotal/Occ/Vac/Dirty/Maint/Pct Bold Segoe 10 + QTable 9 cols RoomNo/Name/Category/Maid/Status/Folio/Guest/Departure/Check-In NoEdit SelectRows StretchLast AlternatingNo manual bg/fg + lblDetail bg glass_tint 6px 8px radius + QGroupBox HK Actions QHBox btnVacant success bg #008000 / btnDirty warning #800000 / btnMaint neutral / btnOOO danger + Refresh/Close; Shortcuts F5 Ctrl+V/D; reload(): roomstatus.room_rack() + _status_palette() success_bg etc. + colors.get(stat) + housekeeping_summary(); _on_select(): detail label; _selected_roomno(); _set_status(): Occupied guard (folio && new!=Dirty → warn), Maint/OOO -> block_out/unblock_room, Vacant -> unblock+update_hk_status, else update_hk_status
```

**Parity:** Core status palette maps correctly `success #008000 / warning #800000 / danger #c00000 / neutral #404040` via `status_colors()` → `_status_palette()`; matches VB6 `VB6 Classic hues`. Occupied→Dirty rule matches VB6 HKHouseOpStk pattern. Still missing `InclCount='Y'` strict filter (uses `roomstatus` API which must enforce), and decorative `Line/Shape` missing.

### 2.7 `ui/plan_master.py:1-217` — Plan Master

```python
# PlanMasterForm(QDialog 640×460) state Idle/Add/Edit string + edit_code; QVBox QTable 4 cols Code/Name/Total/Active + QForm Code/Name/Total/Package + QHBox New/Edit/Delete/Save/Cancel/Exit +.lblState; set_state() enabled toggle + state label; reload(): plans.list_plans() Code Name Total ActiveYN; _on_new(): clear+enable focus Code; _on_edit(): get(code)->fields->disable Code; _on_save(): guard code&&name required total float pkg -> exists(code) check -> insert() else update(); _on_delete(): PYT guard MsgBox "Safety..." -> question -> delete()
# base_master.py provides full TopCtrl AEDP parity: DGHelp popup 280×220 under Txt.Height+2, ListView Nature enum 19 items, SearchViewer F3 SearchCode HO, audit labels U_Name/U_AE/U_EntDt Times New Roman red 9pt, button bar bevel yellow/ navy accent.
```

---

## 3. Compare: Layout Sizes / Colors BGR→RGB / Fonts / Controls / Workflow

### 3.1 Layout Sizes — Twips→Px (/15)

| VB6 Form | Client W×H twips | Px | Python Dialog | Size | Δ | Verdict |
|----------|----------------|-----|---------------|------|---|---------|
| `fdCheckIn` | 11340×4515 | **756×301** | `CheckInBrowser` + `DGHelpPopup` vs `fallback table` | `1060×560` (CheckIn) / `ChargeDialog 640×400` | +304 px W, +259 px H | ❌ **VB6 tiny lookup (301 tall) intentionally helper**; Python full browser bigger — acceptable but not Fixed Single 756×301 |
| `FdCheckOut` | 14625×8310 | **975×554** (+Frame1 1120×625 overflow) | `CheckOutBrowser` | **1100×650** | +125 W +96 H | ⚠️ close; VB6 overflow frame intentional |
| `fdDisplayFolio` | 14235×8985 | **949×599** | `folio_ui ChargeDialog` or `checkout_ui` reuse | **640×400** vs **1100×650** | −309 W −199 H | ❌ guest ledger half-width in Python |
| `fdRoomChange` | 12270×8595 | **818×573** | `RoomChangeWindow` | **680×480** | −138 W −93 H | ❌ loses FrPackage 675×332 overlay area |
| `FdRoomDisplay` | 14190×8355 (max) | **946×557** (max 1325×738 inc. FrmRoom) | `Dashboard view_rack grid 8-col` vs `RoomStatusForm 1150×680` | tiles scroll infinite | — | ⚠️ maximized vs scroll |
| `FdReSetlement` | 9555×7350 | **637×490** (inside Frame 126) | `ReSettlementWindow` | **720×540** | +83 W +50 H | ⚠️ Python wider — hides decorative frames |
| `fdWalkInEntry` | 13995×8595 | **933×573** (inner Frame1 1197×8910+1725 overflow) | `frontoffice CheckInBrowser` | **1060×560** | +127 W −13 H | ⚠️ similar |
| `FindMess` (bonus) | 10995×5715 | **733×381** | *(no Python)* | — | MISSING | ❌ |

**VB6 `fdCheckIn` grid verbatim vs Python:** `DGHelp Width 10965 twips = 731 px` inside `11340 = 756 px` leaves 25 px margin; Height `3375 = 225 px` tall popup centered under field. Python `ReSettlement DGBill 6780×3390 (452×226 px) at 13320,5610 off-screen`, `DGMember 4215×3330 (281×222)`, `DGChrgPayment 5490×3465 (366×231)` — ALL hidden off-screen far-right (X > 12k = 800 px beyond 637 px viewport) — true popup pattern. Python uses inline full-width tables `Stretch` — visually opposite.

### 3.2 Colors BGR→RGB Decode (VB6 `&H00BBGGRR&` → RGB `#RRGGBB`)

| VB6 Literal | Hex `00BBGGRR` | B | G | R | RGB `#RRGGBB` | Python Token / QSS | Match? |
|-------------|---------------|---|---|---|---------------|-------------------|--------|
| `fdCheckIn Back &HC6B7A4&` | `00 C6 B7 A4` | C6 | B7 | A4 | **#A4B7C6** dusty blue-gray | `VB6_GRAY #d4d0c8` (gray) | ❌ **deviation — unique dusty blue lost** |
| Most forms Back `&HFFC0C0&` | `00 FF C0 C0` | FF | C0 | C0 | **#C0C0FF** pale lavender | `bg #d4d0c8` gray | ❌ lavender→gray (visual close but hex not exact) |
| `FdCheckOut Back &HC0C0C0&` | `00 C0 C0 C0` | C0 | C0 | C0 | **#C0C0C0** mid-gray | `bg #d4d0c8` approx | ⚠️ close gray (C0 vs D4) |
| `FdRoomDisplay FrmPic &HCBFCF9&` | `00 CB FC F9` | CB | FC | F9 | **#F9FCCB** pale cream-yellow | *(no mapping)* | ❌ |
| `FdRoomDisplay FrmRoom &HFFC0FF&` | `00 FF C0 FF` | FF | C0 | FF | **#FFC0FF** bright pink | `vb_pink #ffc0ff` | ✅ exact |
| `fdWalkInEntry FrmPackage &H80FF80&` | `00 80 FF 80` | 80 | FF | 80 | **#80FF80** light mint | *(no mapping)* — dashboard mint is `#34d399` dark mode | ❌ |
| `fdWalkInEntry Frame1 &HC0FFFF&` | `00 C0 FF FF` | C0 | FF | FF | **#FFFFC0** pale yellow (see note) | `vb_pale_yellow #ffffc0` | ✅ visual yellow (see note) |
| `LblFormCaption &HC0FFFF&` | same | — | — | — | **#FFFFC0** pale yellow | `sidebar?` not mapped | ❌ header uses gray |
| `&HC00000&` Txt Fore / Header Back | `00 C0 00 00` | C0 | 00 | 00 | **#0000C0** navy blue (BGR trap!) | `theme text #000000` black; `danger #c00000` red (looks like #C00000) | ❌ **VB6 BGR blue, intent was maroon — both Python `#c00000` and `#0000c0` off**; screenshot shows maroon-ish dark red header (`&HC00000` visually dark red in 16-bit palette despite BGR) — keep `#800000` maroon for parity |
| `&H800000&` Lbl Fore | `00 80 00 00` | 80 | 00 | 00 | **#000080** navy | `vb_navy #000080` / `vb_maroon #800000` both exist; labels use `#000000` | ❌ should be `#800000` maroon per screenshot |
| `&HFFC0FF&` pink already | — | — | — | — | — | ✅ |
| `&HC0FFC0& Shape5 Fill` | `00 C0 FF C0` | C0 | FF | C0 | **#C0FFC0** mint fill | — | ❌ |
| `&HC000& ???` | — | — | — | — | — | — | — |
| `&HCBF9FC` etc. | — | — | — | — | — | — | — |
| Login mint `&HC2E0CE` maps to `#C2E0CE` | `00 C2 E0 CE` | C2 | E0 | CE | **#CEE0C2**? compute BB=C2 GG=E0 RR=CE → RGB CE E0 C2 → **#CEE0C2**? Actually but theme `vb_mint #c2e0ce` swaps? Let's decode VB6 mint `&HCEE0C2&` = 00 CE E0 C2 => BB=CE GG=E0 RR=C2 => RGB C2 E0 CE => **#C2E0CE** ✅ so theme mint correct | `vb_mint #c2e0ce` | ✅ |

> **BGR Note:** VB6 `&H00BBGGRR` low byte = Red. For `&HFFFFC0&` (00 FF FF C0) → BB=FF GG=FF RR=C0 → RGB C0 FF FF → **#C0FFFF cyan** if strict. But VB6 screenshot of WalkIn `Frame1` clearly shows pale **yellow** `#FFFFC0`, not cyan. The theming code intentionally stores `#ffffc0` as visual yellow parity (swapped B↔R) — document as **visual parity > strict hex**. Same inversion for lavender `#FFC0C0` vs `#C0C0FF` swapped in theme's `vb_pale_yellow`. Keep visual yellow for parity.

### 3.3 Fonts

| VB6 Spec | Size pt | Python | Gap |
|----------|---------|--------|-----|
| Form Font `MS Sans Serif 9.75 400` | 9.75 ≈ **13 px** | global `Segoe UI 13px` via `_glass_qss *` | ✅ size matches; family fallback Segoe acceptable |
| Label `Arial 9.75 Bold 700 Fore &H800000` maroon | 9.75 | `QLabel maroon 12px Segoe #800000` or `Arial 9.75` in base_master | ⚠️ color not #800000 in most FO forms (uses #000000 black); weight 700 ✅ |
| TextBox `Arial 9.75 400 Fore &HC00000` navy-blue-ish | 9.75 | `QLineEdit 9.75 Arial #000` | ⚠️ color black vs navy |
| `LblFormCaption System 19.5 Bold 700` vertical pale yellow 180×540 | 19.5 | `QLabel 18-20 Bold horizontal` | ⚠️ rotation missing (VB6 vertical caption via `LblFormCaption.Caption = Proc_6_?? + Chr`) |
| `Tahoma 9.75 / 8.25` FrmAdjust, ReSettlement | 9.75/8.25 | Tahoma loaded but QSS falls back to Segoe | ⚠️ Tahoma not explicitly registered |
| `Times New Roman 12 Bold` audit footer (if present) | 12 | base_master audit labels Times 9pt red ✅ | ✅ in base_master |
| `Arial Narrow 8.25 Bold 700` TxtSearch FindMess | 8.25 | — | missing module |

### 3.4 Controls — VB6 vs Python Parity Matrix

| VB6 Control | Props (L,T,W,H) | Python Widget | Props | Parity |
|-------------|-----------------|---------------|-------|--------|
| `MainCtrl TopCtrl1` | 11340×450 at 0,0 Visible 0 | *(none in FO; base_master has state machine but FO browsers use manual)* | — | ❌ **missing TopCtrl state machine A/E/D/P/Search** in all FO browsers except plan_master |
| `BtnEnh CmdOK` | 1155×975 bevel yellow at 5400,2865 | `QPushButton role danger` flat | flat not bevel, not yellow #FFFFC0 | ❌ |
| `BtnEnh BtnExit / CmdPostChrg / CmdPlanBill` | 1650×750 / 1575×780 / 1635×720 at 2400,7335 etc. bevel yellow | `QPushButton role danger/warning` flat red/maroon | color/height similar but bevel missing | ❌ |
| `TextBox Txt(0)` | 9270×285 Border 0 None Flat MaxLen 50 Fore &HC00000 Arial 9.75 | `QLineEdit` `border 1px solid #808080` inset | BorderStyle 0 vs inset differs | ❌ (visual) |
| `DataGrid DGHelp` | 10965×3375 at 210,915 Visible 0 TabStop 0 Col widths SearchCode 4000 vs Name 1000 | `QTableWidget StretchLast` or `QListWidget popup` (in base_master) always visible filter | hidden popup vs always visible | ❌ (workflow gap F1) |
| `DataGrid DGBill / DGMember / DGRoom / DGChrgPayment` | 6780×3390 at 13320,5610 off-screen Visible 0 (popover) | `QTableWidget` full width 6 cols inline | off-screen popup vs inline | ❌ |
| `MSFlexGrid FGPoint` | 1980×1440 at 15,3585 Visible 0 TabStop helper | *(none)* | — | ❌ |
| `MSHFlexGrid FGrid 8610×6645` + `Fgrid1 total 8610×285` | at 5385,990 / 5385,7635 | `QTableWidget 7 cols maxHeight 200` | height not 6645, no total row | ❌ |
| `Frame FrmAdjust 4050×1560` GO/Set/Cancel password gate | hidden at 7485,5595 with Txt23 `#` + Txt24 Rate | *(none)* | — | ❌ **HIGH** |
| `Timer1 Interval 1000` | at 0,0 / 10350,0 | `QTimer` not wired in FO (dashboard uses Refresh click only) | — | ❌ |
| `PictureBox Picture2 300×270 hidden` | frx | *(none)* | decorative only | LOW |
| `Label Lbl Fore &H800000` AutoSize Transparent Arial 9.75 Bold | at precise Left/Top | `QLabel color #000000 text_dim` | color not maroon #800000 | ❌ |
| `Label Label1 Header Back &HC00000 Fore &HFFFFFF` | 8535×375 / 8190×375 Center Bold | `QLabel/QHeader` `header_grad_top #d4d0c8` gray | bg not #C00000 maroon | ❌ |
| `Frame FrPackage 10125×4980 Tariff Matrix` | at 1005,570 hidden + FGrid3 9510×2415 | `RoomChangeWindow` single Rate field | matrix missing | ❌ **HIGH** |
| `Frame Frmrate Back &HFF0000 4830×795 red` | at 14190,180 hidden Remarks/Authorization * | *(none)* | — | ❌ |
| `Line1 Border &HC00000 Width2 X1 7020→10275 Y 7005` + `Shape5 Fill &HC0FFC0 3255×1200` + `LTxt 0/1/2 1605×285 Total/Paid/Balance` | hidden decorative bill totals | *(none in ReSettlement)* | — | ❌ |
| `Image GuestImage Stretch -1 1035×525 hidden` + `Picture1 11160×7545 Stretch -1` | room photo stretched centered | `RoomRackItem` tiles no image | — | ❌ |
| `DataGrid DGPackage/DGNewRoomNo/DGRoomNo off-screen 2800×1800` | at 14k-15k Left hidden | `QComboBox free_rooms()` | hidden navigation vs combo | ❌ |
| `TopCtrl + MDI sbar Panels + world clocks + DealerLogo + mnuGrid` | MDIForm1 pict 1800×7680 etc. | dashboard top bar + theme | chrome missing | LOW |

### 3.5 Workflow — VB6 → Python Step-by-Step

| # | VB6 Workflow (verb) | VB6 Code Location | Python Implement | Gap |
|---|---------------------|-------------------|------------------|-----|
| W1 | **fdCheckIn grid 6780×3400 (actually 10965×3375) helper vs inline** | `fdCheckIn.frm:76 DGHelp 10965×3375 Visible 0` + `DGBill 6780×3390` ReSettlement | `folio_ui`/`frontoffice` single visible table `StretchLast` | ❌ **hidden popup versus always-visible table** — power user lost autocomplete scope |
| W2 | **Booking join today-only Count Distinct SNO `>0` Order By Name** | `fdCheckIn Form_Load L234` see SQL above | `frontoffice` `GuestFolio WHERE Site_Code AND Vprefix` + `checkin.list_checkins()` (today booking filter missing) | ❌ **query entirely different** — shows all folios, not today-available SNOs |
| W3 | **Arrival-before guard `Guest Arrived Before Arrival Date ! Checked in Anyway? 0x24 Yes/No`** | `CmdOK_UnknownEvent_9:184` | `frontoffice._new()` uses `checkin.create_checkin` with `Vdate<=today?` maybe but no MsgBox text verbatim; `folio_ui._settle()` shows `Check-Out done Bill_No` not check-in guard | ❌ message text not verbatim |
| W4 | **RoomChange old row `Type='C'` + `NewRoomNo='<new>' Reason + NewRoom insert Type='' open SNo+1** | `fdRoomChange.frm` + `core.fo_ops.room_change()` (30-col) | `core.fo_ops.room_change` mirrors ✅ `UPDATE RoomOcc SET ChkOutDate/ChkOutTime Type='C' NewRoomNo + INSERT new SNo MAX+1 Type='I'` | ✅ backend correct; **UI missing Reason MaxLen 100 guard + FrPackage tariff overlay + KOT pending check** |
| W5 | **Merge Folio `mFolio + RelatedFolioNo` 3-step UPDATE** | `fdRoomChange/fo_ops MergeCharge` `UPDATE PayCharge SET RelatedFolioNo=FolioNo ...?` Actually `core.fo_ops.merge_charge` : `UPDATE GuestFolio SET mFolio='<target>', RelatedFolioNo=?` + shift `PayCharge.FolioNoDocid` + `GuestFolio.FolioNoDocid` | `core.fo_ops.merge_charge(from,to)` mirrors ✅ | ✅ but UI `MergeChargeWindow` lacks RelatedFolio display panel (shows only lbl_src/tgt name, not folio linkage detail) |
| W6 | **ReSettlement `ModeSet='S' sum guard `ABS(sum(new)-old) <0.005` + delete old then insert per-line `ModeSet='S' RestCode='KKFOM'` `next_vno('REC')` DocId 21-char** | `FdReSetlement.frm` code ~L400-900; `core.fo_ops.re_settlement` | `core.fo_ops.re_settlement()` implements ✅ guard + `ModeSet='S'` + `PayCode<>'ROFF'` filter | ✅ but Python `ReSettlementWindow._add_line` collects `cmb_paycode CurrentData` vs VB6 `Txt23-type`? Slight; **SNo hard 1 vs MAX+1** minor drift |
| W7 | **RoomStatus `InclCount='Y'` + `type='RO'` + `logsite_code IN ('<site>','HO')`** | `FdRoomDisplay.Form_Load L110: select * from roommast where ... type='RO' and inclcount='Y' order by Code` also WalkIn KOT exclusion `InclCount='Y'` | `core.roomstatus.room_rack()` currently `SELECT ... FROM RoomMast WHERE RTRIM(Type)='RO' AND (LogSite_Code=? OR 'HO') ORDER BY Code` **missing `InclCount='Y'`** and some dashboards use `room_occ.room_availability` with same miss | ❌ **InclCount filter gap** |
| W8 | **Bill Reprint vs ReSettlement distinction** | `05_Bill_Reprint.png` separate module `FdReSetlement Print` + `FdDisplayFolio Print` `CmdPrint 1275×1050 at 4560,7155` prints `FGrid` preview, versus `FdReSetlement` settlement `BtnSave` modifies PayCharge ModeSet S | `folio_ui ChargeDialog` has single `Close` button, `checkout_ui` has `Check-Out`/`Reverse` only; no dedicated `Bill Reprint` menu `FrmFolio` preview | ❌ separate reprint flow missing |
| W9 | **PlanMaster tariff matrix `DGPackage` + extras `% @` labels** | `fdRoomChange FrPackage FGrid3 9510×2415 + DGPackage 4230×1920` + `fdWalkInEntry FrmPackage FGrid3 9675×1740 + 8 rate labels` | `plan_master.PlanMasterForm QTable 4 cols` only basic Code/Name/Total/Active; matrix `High/Rack/Disc1-3 × Single/Multiple/Extra/...` not rendered | ❌ matrix detail missing |
| W10 | **Validation messages verbatim** | `"First Print Bill" (0x40)` / `"Guest Balance is Not Zero" (0x41)` / `"There is some KOT Pending for this Room." (0x10)` / `"Apply Tariff as per defined Condition?" (0x24)` / `"Guest Arrived Before Arrival Date !" & vbCrLf & "Checked in Anyway?" (0x24)` / `Delete "Delete Record ?" (0x24 Confirmation)` / `Cancel "Cancel ?" "Terminate Process"` | Python Hinglish `"Pehle folio select karo"` / `"Safety: sirf PYT* test folios..."` | ❌ **text not verbatim VB6** |

---

## 4. MISSING Frontend UI Bugs — Gap Table (Frontend-Only, No DB Change)

| # | VB6 Feature (file:line) | VB6 Verbatim / Size / Color / Font | Python Current | Impact | Severity |
|---|--------------------------|------------------------------------|----------------|--------|----------|
| F1 | `fdCheckIn.frm:76` `DataGrid DGHelp 10965×3375 at 210,915 Visible 0` + `MSFlexGrid FGPoint 1980×1440 at 15,3585` + `Txt(0) 9270×285 Fore &HC00000` + `Label Guest Name 1155×240 &HC00000` + `TopCtrl1 11340×450 Hidden` | Hidden helper popup under Txt with `Tag=Code` `Text=Name` twin-field + FGPoint keyboard buffer + `Proc_6_137_1193554` positioning & `Tag` stash + arrow/PageUpDown + incremental `Name` filter; lookup W 731 px inside 756 px dialog | `folio_ui.py`/`frontoffice.py` single visible `QTableWidget stretch` + no popup; `CheckInBrowser` table is always visible; no Tag/Code split (`currentText` only); no `FGPoint` | Lookup not 1:1; duplicates Name collides; future SEARCHBACKPARENT check-in may link wrong Booking DocId | **HIGH** |
| F2 | `FdCheckOut.frm:42-76` `Frame FrmAdjust 4050×1560 at 7485,5595 Visible 0` with `Txt24 Rate 1260×315 Enabled 0` + `Txt23 Password 2115×315 PasswordChar "#"` + `CmdPass "GO" 495×315` + `CMDSET "Set" 795×315 Enabled 0` + `Command3 "Cancel" 795×315 Enabled 0` | Password gates room-rate override (Enviro authorization) → enable `Txt24` + `CMDSET` | `checkout_ui.py` has no FrmAdjust, no password field, no GO gating — any user can change rate implicitly via checkout | Auth bypass — rate tamper without password | **HIGH** |
| F3 | `fdWalkInEntry / fdRoomChange FrPackage FGrid3 9510×2415 at 45,1410` + `FrmPackage 10125×4980 at 1005,570 hidden` with 8 rate labels (`Extra Person @ % Disc` etc. 900×270 fields Arial 9 Bold 700) + `SRate` tariff cells | Full tariff matrix overlay centered modal (`#80FF80` mint or `#FFC0C0` pink) with `DGPackage 4230×1920` / `FGrid3` + `LPlanRoomRate "-"` etc. | `RoomChangeWindow` shows single `QComboBox free_rooms + Reason QLineEdit + Save`; `frontoffice` shows Adult/Child textual; `plan_master` shows 4 columns only | Cannot view/edit `High/Rack/Disc1-3` rates per room category — parity fails for rate masters | **HIGH** |
| F4 | `fdCheckIn 6780×900?` Actually `DGBill 6780×3390 at 13320,5610 Visible 0` (452×226 px off-screen) + `DGMember 4215×3330` + `DGChrgPayment 5490×3465` — floating popup pattern | DataGrids hidden far-right (`Left 13000+` = 800 px beyond 637 px viewport) acting as popups summoned via GotFocus, not inline tables | `fo_sub_forms_ui ReSettlementWindow` inline `QTable 6 cols` + `new_table 4 cols` always visible `Stretch` | Visual contradiction — VB6 *never* shows inline tables; always modal/popup — screenshot `06_Bill_ReSettlement` shows single focused panel, not all tables at once | **MED-HIGH** |
| F5 | `FdRoomDisplay.frm:19` `Frame FrmPic Back &HCBFCF9 &HCBFCF9→#F9FCCB pale cream 12855×7590` + `Picture1 11160×7545 Stretch -1 Border Fixed Single centered` + `FrmRoom Back &HFFC0FF #FFC0FF 19875×11070` with **BtnEnh Cmd(1) 1350×735 per room 9-col grid** via `Load` loop | Rack built dynamically 9 cols creating `BtnEnh` yellow bevel buttons, each with `PicPath` image stretch + centered via `Proc_104_5_EB09E0`; `LblFormCaption &HC0FFFF System 19.5 vertical` via Resize | `front_office_dashboard` `RoomRackItem 110×85 rgba tints + badge 3-letter` grid 8 cols; `roomstatus_ui` `QTable 9 cols` row-per-room with manual bg/fg | Icon size 1350×735 (≈90×49 px) vs 110×85 tile close but bevel/image missing; visual parity off | **MED** |
| F6 | `FdCheckOut.frm:206` `Timer1 Interval 1000` + `FdReSetlement Timer1 1000 at 10350,0` + `LblCheckInDay "." Fore &HC0& at 4095,1335 Tahoma 9.75` + `frontoffice dashboard lbl_date` | Timer ticks update `LblCheckInDay.Caption = Format(Date,"DDDD")` + clocks `2340/2655 hh/mm` + `LblFormCaption.Width` auto | `checkout_ui`/`folio_ui` no Timer; `dashboard` has manual Refresh button only; `LblCheckInDay` not wired | Live date/day label frozen — not MDI clock-accurate but screenshot shows live date | **LOW-MED** |
| F7 | `LblFormCaption Back &HC0FFFF &HC0FFFF→#FFFFC0 pale yellow 180×540 Border 1 Fixed Single Align Center AutoSize -1 Font System 19.5 Bold 700` at `0,0` + `Label1 Header Back &HC00000 &HC00000→#0000C0 navy (BGR trap) Fore &HFFFFFF 8535×375` Center Arial 9.75 Bold + `Lbl Fore &H800000 &H800000→#000080 navy (or #800000 maroon)` `Arial 9.75 Bold` + `Transparent BackStyle` | Pale-yellow vertical caption strip 12×36 px (180 twips wide) + navy/red headers spanning 569 px; all Lbl maroon bold | Python `header_grad_top #d4d0c8` gray, `text #000000` black, `danger #c00000` flat, `lblState #64748b` dim; no vertical caption; no maroon labels | Visual identity washed — theme `VB6 Classic radius0` not applied per-label | **LOW** (cosmetic) |
| F8 | `BorderStyle 1 Fixed Single + 2px outset/inset bevel + radius 0` (theme injects `QPushButton outset #ffffff #808080` / `QLineEdit inset`) | VB6 classic sharp bevel buttons (`BtnEnh` yellow `#FFFFC0` outset, TextBox `Appearance 0 Flat BorderStyle 0 None` + `Border 2px inset`) | Python `theme.DEFAULTS radius "0"` does inject bevel CSS, but only for `property vb6="true"`; most FO buttons use `role danger/warning` with flat `background #c00000/#800000` no bevel | Bevel not consistently applied — screenshot appears flat modern vs VB6 beveled | **LOW** |
| F9 | `Core room_rack InclCount='Y'` `select * from roommast where logsite_code='<site>' and type='RO' and inclcount='Y' order by Code` (`FdRoomDisplay/Form_Load L110` + `fdWalkInEntry Type In ('O','M') block out filter`) | Filters dirty/maint occupancy accurately excluding `InclCount='N'` non-count rooms | `core.roomstatus.room_rack()` current `WHERE RTRIM(Type)='RO' AND (LogSite=? OR 'HO')` **missing `InclCount='Y'`**; `roomstatus_ui` itself uses `roomstatus.room_rack()` so bug propagates; `front_office_dashboard` counts `total-len(type RO)` off | Dashboard over-counts rooms (includes e.g. store/house-use) vs VB6 correct  | **HIGH** (data-correctness visual) |
| F10 | `ReSettlement ModeSet='S' sum guard + LTxt/Shape/Line decorative bill box` `Shape5 Border &HC00000 Fill &HC0FFC0 at 7035,6270 3255×1200 BorderWidth 2` + `Line1 X1 7020→10275 Y1/Y2 7005 border &HC00000 Width2` + `LTxt0/1/2 Back &HFFFFFF Border 1 Fixed Single 1605×285 Align Center Tahoma 9 Bold Total/Paid/Balance` + `FrCCDet/FrChqDet/FrEmp/FrComp` off-screen frames | Settlement preview framed with 3 white boxes inside mint shape bordered maroon + separator line | `ReSettlementWindow` single new_table 4 cols no shape, no line, no white boxes; totals shown only in lbl `Folio … charges: 1,234.00` | Screenshot `06_Bill_ReSettlement.png` mismatch — VB6 boxing missing | **MED** |
| F11 | `TopCtrl1 9555×450 / 14235×450 / 12270×465 / 7380×375 at 45,7455 Visible 0` state machine A=ADD, B=CANCEL "Cancel ?" Terminate Process 0x04, C=DELETE "Delete Record ?" Confirmation 0x24 + BeginTrans, D=EDIT, F=Find "Records Not Present For Searching." SearchCode HO, 16=SAVE Duplicate guard "**Already Exist *" / "Duplicate Name" | TopCtrl dispatches all CRUD with `BeginTrans/Commit/Rollback`, MsgBox verbatim, audit `U_Name/U_AE/U_EntDt` Times New Roman red, sbar `Panels(5) For Site :` + clocks | FO browsers implement `lblState Idle` string only; `plan_master` uses `base_master BaseMasterForm` with proper `TopCtrl AEDP + DGHelp + FindViewer SearchCode HO + Duplicate guard + audit labels Times New Roman` — but sub-forms `fo_sub_forms_ui` lack state machine, `checkout_ui` lacks `TopCtrl`, `folio_ui` lacks `TopCtrl` | Consistency: plan_master ✅, FO browsers partially ❌ | **MED** |
| F12 | `FindMess.frm Back &H80C0FF→#FFC080 (BGR peach) 10995×5715 Border Fixed Single + GridSel 10965×5685 + TxtSearch Back &HFFFF80→ #80FFFF pale yellow 2055×240 Visible 0 Arial Narrow 8.25 Bold + menus FSR/FNSR/RF/SA/SD filter + Wingdings delivered toggle Solved Y/N` | Housekeeping GuestMessage finder with filter puzzles `15595518/16777152` colors + filter overlay | No Python module for GuestMessage finder (closest `guest_services_ui` or `guest_lookup_ui` is name search only, not message status) | Entire module missing for HK messaging | **MED** (module gap) |
| F13 | `Bill Reprint (05_Bill_Reprint.png)` `FdReSetlement` `CmdPrint 1275×1050 at 4560,7155` prints `FGrid` preview (`FdReSetlement.frx` Picture2), distinct from `ReSettlement` `BtnSave` which modifies PayCharge `ModeSet S` | Separate Reprint path: `FGrid`/`FRectGrid` 4065×1020 preview without DB modify | `folio_ui ChargeDialog` has no Print button; `checkout_ui` has no Reprint tab; only `fo_sub_forms_ui ReSettlementWindow` handles settlement | Bill preview printing missing — cannot re-print settled bill without altering | **MED** |
| F14 | `CheckIn List 03_CheckIn_List.png` In-House list `Folio/Guest/Arrival/Departure columns + double-click drill` | In-House filter with `ChkOutDate IS NULL` | `frontoffice.CheckInBrowser` shows `GuestFolio WHERE Vprefix` + `Days/User/AE/City/GuestCode` extra columns; not InHouse filtered; no drill to charges (drill only in `folio_ui` which is separate) | Column superset confusion + drill routing split across two browsers | **LOW-MED** |
| F15 | `Merge Folio 08_Merge_Folio.png` source/target panels `From Room/To Room` with `RelatedFolioNo` linkage display + folio panel detail (folio number, guest name, balance) + `mFolio` column | `FrmMergeCharge` with `DataGrid DGChrgPayment 5490×3465 hidden` underlying paycharge shift | `MergeChargeWindow 640×460` two `QLineEdit` + `lbl_src/tgt` one-liner `folio - name` + `lbl_total charges`; no RelatedFolio panel | Simplified but core link displayed only as to-folio number in success MsgBox | **LOW** |
| F16 | `Validation verbatim` `MsgBox` texts: `"Guest Arrived Before Arrival Date !" & vbCrLf & "Checked in Anyway?" vbYesNo 0x24` / `"First Print Bill" vbCritical 0x40` / `"Guest Balance is Not Zero" vbYesNo 0x41` / `"There is some KOT Pending for this Room." vbCritical 0x10` / `"Apply Tariff as per defined Condition?" vbYesNo 0x24` / `"Delete Record ?" "Confirmation" 0x24` / `"Cancel ?" "Terminate Process"` + duplicate `"**Already Exist *"` / `"Duplicate Name"` + `"Records Not Present For Searching."` / `"No Records To Search."` | VB6 exact English + `vbCrLf` + `&H24,&H40,&H41,&H10` icons | Python Hinglish `"Pehle folio select karo"` / `"Safety: sirf PYT* test folios..."` / Named buttons in Hindi | UX diverges from VB6 manual screenshots; auditors compare text | **LOW-MED** (wording) |

---

## 5. Debug Fixes — Make Python UI EXACTLY VB6 Same Frontend Logic (No DB Change)

> All patches are **UI-layer only**. Reuse `core.*` with **param-bound SAME SQL** as VB6 verbatim. Keep `PYT*` guard. Verify with `python -m py_compile <file>`.

### 5.1 Fix F1 — DGHelp Tag/Code Popup (fdCheckIn `11340×450 TopCtrl` + `DGHelp 10965×3375` + `FGPoint` + `Tag=Code`)

**Problem:** No hidden helper; Tag/Code stashing lost; incremental `Name` filter not per-field; sizing not VB6 `Left 210 Top 915 Width 10965 Height 3375` inside 11340 client (popup 25 px margin).

**Patch — Drop-in `QListWidget` popup matching VB6 geometry (`ui/folio_ui.py` + `ui/frontoffice.py` + `ui/fo_sub_forms_ui.py` common helper):**

```python
# common/helper: fdCheckIn DGHelp parity
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtGui import QFont

class _VB6_DGHelp(QListWidget):
    """VB6 DataGrid DGHelp 10965×3375 at 210,915 Visible 0 → popup under field.
    Popup width = field.width() (min 280), max-height 225 = 3375 twips ÷15.
    Stores Tag=Code (UserRole), Text=Name like DGHelp_UnknownEvent_9."""
    def __init__(self, parent, field: "QLineEdit", on_pick):
        super().__init__(parent)
        self._field = field
        self._on_pick = on_pick
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setMaximumHeight(225)      # 3375 /15 = 225 px — VB6 DGHelp height
        self.setMinimumWidth(280)
        self.setStyleSheet("QListWidget{background:#fff;border:1px solid #808080;border-radius:0px;"
                           "font-family:'Arial';font-size:9.75pt;color:#000;}"
                           "QListWidget::item{padding:4px 6px;} QListWidget::item:selected{background:#000080;color:#fff;}")
        self.itemClicked.connect(self._pick)
        self.itemActivated.connect(self._pick)
    def _pick(self, it: QListWidgetItem):
        code = it.data(Qt.ItemDataRole.UserRole)
        name = it.data(Qt.ItemDataRole.UserRole + 1)
        self._field.setText(str(name))                 # VB6: Txt.Text = Fields("Name")
        self._field.setProperty("vb_tag", str(code))   # VB6: Txt.Tag  = Fields("Code")
        self.hide()
        self._field.setFocus()
        if self._on_pick:
            self._on_pick(code, name)

# Usage in CheckInBrowser (fdCheckIn parity):
self._dg = _VB6_DGHelp(self.window(), self.txt_search, self._on_code_picked)  # field = Txt(0)
self.txt_search.textEdited.connect(self._dg_reload)
def _dg_reload(self, pat: str):
    # VB6 SQL verbatim (today SNO filter) — param-bound:
    # NOTE: reuse Booking join exactly as VB6 L234; placeholder for SITE_CODE + pattern closure.
    # Fallback if Booking module not loaded: show GuestProf filtered by Name LIKE pat.
    rows = db.query(
        "SELECT B.DocId AS CODE, GP.Name FROM ((Booking B "
        "LEFT JOIN RoomCat RC ON B.RoomType=RC.Type AND B.RoomCat=RC.Code) "
        "LEFT JOIN RoomMast RM ON B.RoomType=RM.Type AND B.RoomNo=RM.Code) "
        "INNER JOIN GuestProf GP ON B.GuestProf=GP.Code "
        "WHERE B.CANCEL='N' AND B.LOGSITE_CODE=? AND GP.Name LIKE ? "
        "AND (SELECT COUNT(DISTINCT Sno) FROM GrpBookingDetails GB "
        "WHERE NOT EXISTS (SELECT isnull(BookingDocid,'') FROM GuestFolio GF "
        "WHERE GB.BookingDocId=GF.BookingDocId AND GB.Sno=GF.BookingSno) "
        "AND IsNull(GB.Cancel,'')<>'Y' AND GB.ArrDate=CAST(GETDATE() AS date) "
        "AND GB.BookingDocid=B.DocId)>0 ORDER BY GP.Name", (SITE_CODE, f"%{pat}%"))
    self._dg.clear()
    for code, name in rows[:60]:
        it = QListWidgetItem(name); it.setData(Qt.ItemDataRole.UserRole, code)
        it.setData(Qt.ItemDataRole.UserRole+1, name)
        f = it.font(); f.setFamily("Arial"); f.setPointSizeF(9.75); it.setFont(f); self._dg.addItem(it)
    if self._dg.count():
        pt = self.txt_search.mapToGlobal(QPoint(0, self.txt_search.height()+2))  # VB6 Top = Txt.Top+Height+0x1E (~2px)
        self._dg.move(pt); self._dg.setFixedWidth(max(self.txt_search.width(), 280)); self._dg.show(); self._dg.raise_()
    else: self._dg.hide()
```

**Key binding parity (VB6 `Txt_KeyDown:342`):**

```python
# On the host field, install eventFilter:
def eventFilter(self, obj, ev):
    if obj is self.txt_search and ev.type()==QEvent.Type.KeyPress:
        if ev.key()==Qt.Key.Key_Escape:  # 0x1B → hide like Proc_60_19_E86200
            self._dg.hide(); return True
        if ev.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up, Qt.Key.Key_PageDown, Qt.Key.Key_PageUp):
            if self._dg.isVisible():
                self._dg.setFocus(); return True
    return super().eventFilter(obj, ev)
```

Fixes `fdCheckIn` dedicated lookup `756×301 Fixed Single CenterOwner MDIChild` — set dialog `setFixedSize(756,301)` + modal:

```python
dlg = QDialog(parent); dlg.setWindowFlag(Qt.WindowType.WindowTitleHint); dlg.setFixedSize(756,301)
# CenterOwner
if parent: dlg.move(parent.geometry().center() - dlg.rect().center())
```

---

### 5.2 Fix F2 — FrmAdjust Password Gate (FdCheckOut 4050×1560 at 7485,5595)

**Problem:** No auth for rate override; `Txt23 "#"` + `Txt24` disabled until `GO` passes.

**Patch — Overlay `QFrame` exactly at VB6 twips scaled `/15`:**

```python
# ui/checkout_ui.py inside CheckOutBrowser.__init__ after main layout
from PyQt6.QtWidgets import QFrame
self._frm_adjust = QFrame(self); self._frm_adjust.setVisible(False)
# VB6 Frame 4050×1560 at 7485,5595 inside Frame1 at -15,-30 → effective center overlay
# Screen px: 270×104 at (499,373) — use centered overlay via QStackedLayout instead of absolute
self._frm_adjust.setStyleSheet("QFrame{background:#C0C0FF;border:1px solid #808080;border-radius:0px;}")
# inner: password # + GO / Rate disabled + Set(+Cancel)
from PyQt6.QtWidgets import QLineEdit, QPushButton, QFormLayout
self._adj_pwd = QLineEdit(); self._adj_pwd.setEchoMode(QLineEdit.EchoMode.Password); self._adj_pwd.setPlaceholderText("Password")
self._adj_rate = QLineEdit(); self._adj_rate.setEnabled(False); self._adj_rate.setAlignment(Qt.AlignmentFlag.AlignRight)
self._adj_rate.setStyleSheet("QLineEdit{font-family:'Tahoma';font-size:9.75pt;}")
_btn_go = QPushButton("GO"); _btn_go.setStyleSheet("font-family:'Tahoma';font-weight:700;background:#ffffc0;border:2px outset #ffffff #808080;")
_btn_set = QPushButton("Set"); _btn_set.setEnabled(False); _btn_set.setProperty("vb6", True)
_btn_cancel = QPushButton("Cancel"); _btn_cancel.setStyleSheet(btn_qss)
_btn_go.clicked.connect(self._adj_check_pwd); _btn_set.clicked.connect(self._adj_apply_rate); _btn_cancel.clicked.connect(lambda: self._frm_adjust.hide())
_form = QFormLayout(self._frm_adjust); _form.addRow("Password", self._adj_pwd); _form.addRow(_btn_go); _form.addRow("Room Rate", self._adj_rate); _form.addRow(_btn_set); _form.addRow(_btn_cancel)

def _adj_check_pwd(self):
    # VB6 Enviro/UserPermission check — reuse core.auth or enviro verify; keep param-bound
    if core.check_rate_password(self._adj_pwd.text()):  # or db.query SELECT Password FROM Enviro? or UserPermission
        self._adj_rate.setEnabled(True); self.findChild(QPushButton, None).setEnabled(True)  # _btn_set
    else:
        QMessageBox.warning(self, "Password", "Invalid Password!")
```

Wire `CmdPostChrg` (Post Charge) to show this frame before editing `RoomRate` cell; `CMDSET` commits `UPDATE RoomOcc ... RoomRate='<rate>'` only after auth.

---

### 5.3 Fix F3 — Tariff Matrix Dialog (FrPackage FGrid3 9510×2415)

**Problem:** Rate matrix invisible; cannot parity-check `High/Rack/Disc` tariff conditions.

**Patch — Read-only matrix dialog matching VB6 `Frame FrPackage` 10125×4980 `#FFC0C0` on mint `#80FF80`:**

```python
# ui/fo_sub_forms_ui.py RoomChangeWindow.add:
self.btn_matrix = QPushButton("Tariff Matrix…")
self.btn_matrix.setProperty("vb6", True)
self.btn_matrix.clicked.connect(self._open_matrix)

def _open_matrix(self):
    dlg = QDialog(self); dlg.setWindowTitle("Tariff Matrix (Read-Only) — PrPackage @ RoomCategory");
    dlg.resize(860, 360); dlg.setStyleSheet("QDialog{background:#FFC0C0;} QTableWidget{background:#fff;gridline-color:#808080;}")
    tbl = QTableWidget(7, 6, dlg)  # rows=tariff conditions, cols=rates
    tbl.setHorizontalHeaderLabels(["High", "Rack", "Disc1", "Disc2", "Disc3", "Net"])
    tbl.setVerticalHeaderLabels(["Single", "Multiple", "Extra", "Weekend", "Weekly", "Monthly", "Corporate"])
    tbl.setStyleSheet("QHeaderView::section{background:#d4d0c8;border:1px outset #fff #808080;font-family:'Arial';font-size:9.75pt;font-weight:700;}"
                      "QTableWidget{border:2px inset #808080 #fff; font-family:'Arial'; font-size:9pt;}")
    # fill from PlanMast/Tariff table if exists; else leave blank — NO DB write
    # Example: rows = db.query("SELECT ... FROM RoomTariff WHERE RoomCat=? ...") if table exists
    lay = QVBoxLayout(dlg); lay.addWidget(tbl)
    cb = QPushButton("Close"); cb.clicked.connect(dlg.accept); lay.addWidget(cb)
    dlg.exec()
```

Place labels `Extra Person @ % Disc — Lbl69 @ 3375,435 1110 width, "@" 180 at 5820,450, "%" 135 at 5790,735` exactly via `setStyleSheet("color:#C00000;font-family:'Arial';font-size:9pt;font-weight:700")`.

---

### 5.4 Fix F4 — Timer + `LblCheckInDay` DDDD

**Problem:** Live date/day frozen.

**Patch:**

```python
# in each FO browser that shows LblCheckInDay / lbl_date
from PyQt6.QtCore import QTimer
from datetime import datetime
self.timer = QTimer(self); self.timer.setInterval(1000); self.timer.timeout.connect(self._tick); self.timer.start()
self.lblCheckInDay = QLabel(datetime.now().strftime("%A"))  # VB6 Format(Date,"DDDD")
self.lblCheckInDay.setStyleSheet("font-family:'Tahoma';font-size:9.75pt;color:#C00000;")
def _tick(self):
    self.lblCheckInDay.setText(datetime.now().strftime("%A"))
    if hasattr(self, "lbl_date"):
        self.lbl_date.setText(f"Today — {datetime.now().strftime('%A, %d %B %Y')}")
```

Position `LblCheckInDay at 4095,1335` → mapped to right of `ChkInDate` field ( VB6 `3600+?` ).

---

### 5.5 Fix F5 — Maroon Labels + Precise Arial 9.75 Bold

**Problem:** All Lbl black `#000000`; VB6 maroon `&H800000→#800000` (or navy `#000080` per BGR) bold 700.

**Patch — Per-label stylesheet + base_master pattern:**

```python
lbl = QLabel("Guest Name")
lbl.setStyleSheet("font-family:'Arial';font-size:9.75pt;font-weight:700;color:#800000;background:transparent;")
# Batch via property:
# QLabel[role="maroon"]{color:#800000;font-family:'Arial';font-size:9.75pt;font-weight:700;background:transparent;}
# Apply: lbl.setProperty("role","maroon")
```

Verify screenshot `04_Room_Status.png` maroon header vs black body.

---

### 5.6 Fix F6 — Pink Frame + Pale-Yellow Bevel Buttons `radius 0`

**Problem:** Buttons flat red/maroon, not VB6 pale yellow `&HFFFFC0→#FFFFC0` outset bevel; frames transparent.

**Patch — Wrap data groups in pink frame + set button property `vb6`:**

```python
box = QFrame(); box.setStyleSheet("QFrame{background:#FFC0FF;border:1px solid #808080;border-radius:0px;}"
                                  "QLabel{color:#800000;font-weight:700;background:transparent;font-family:'Arial';font-size:9.75pt;}")
btn = QPushButton("Accept"); btn.setProperty("vb6", True)  # triggers theme bevel: outset #ffffff #808080
# theme radius "0" already injects for R==0: QPushButton[vb6=true]{background:#ffffc0;border:2px outset #ffffff #808080}
```

Check `ui/theme.py:553` — `QPushButton[vb6="true"]{background:#ffffc0;border:2px outset ...}` active when `palette radius==0`.

---

### 5.7 Fix F7 — InclCount Filter (`room_rack` InclCount='Y')

**Current bug:** `core.roomstatus.room_rack()` omits `InclCount='Y'` — dashboard counts store rooms.

**Patch — UI-layer guard (no DB schema change, but SQL fix in `core` caller is param-bound same as VB6):**

```python
# ui/front_office_dashboard.py + ui/roomstatus_ui.py should call filtered query:
rows = db.query(
    "SELECT RTRIM(Code), RTRIM(Name), RTRIM(RoomCat), RTRIM(RoomStat) FROM RoomMast "
    "WHERE RTRIM(Type)='RO' AND InclCount='Y' AND (LogSite_Code=? OR LogSite_Code='HO') "
    "ORDER BY Code", (SITE_CODE,))
# Until core fixed, filter client-side:
self._rack_data = [r for r in raw_rack if r.get("inclcount","Y").upper()=="Y"]  # temporary visual parity
# Permanent fix in core.roomstatus.room_rack() add AND InclCount='Y' (no schema change)
```

---

### 5.8 Fix F8 — ReSettlement Decorative Shape/Line/LTxt Boxes

**Problem:** Screenshot mismatch — no bordered totals.

**Patch — Recreate `Shape5 + Line1 + LTxt0/1/2` as `QFrame` with `QLabel` boxes:**

```python
# inside ReSettlementWindow _build_ui, below FGrid:
shape = QFrame(); shape.setStyleSheet("QFrame{background:#C0FFC0;border:2px solid #C00000;border-radius:0px;}")
shape.setFixedSize(217, 80)  # 3255×1200 twips → 217×80 px
shape_lay = QVBoxLayout(shape)
for title, lbl_ref in [("Total Amount","LTxt0"),("Paid Amount","LTxt1"),("Balance","LTxt2")]:
    row = QHBoxLayout()
    lab = QLabel(title); lab.setStyleSheet("background:#fff;border:1px solid #808080;color:#C00000;font-family:'Tahoma';font-size:9pt;font-weight:700;")
    lab.setFixedSize(100, 19)  # 1500×285 → 100×19
    val = QLabel("-"); val.setStyleSheet("background:#fff;border:1px solid #808080;color:#800000;font-family:'Tahoma';font-size:9pt;font-weight:700;")
    val.setFixedSize(107, 19); val.setAlignment(Qt.AlignmentFlag.AlignCenter)
    row.addWidget(lab); row.addWidget(val); shape_lay.addLayout(row)
# line separator
line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color:#C00000;")
```

---

### 5.9 Fix F9 — TopCtrl State + Audit Footer + Find Viewer

**Problem:** FO browsers state only `lblState Idle` string.

**Patch — Add base_master-style button bar + SearchViewer (F3) + audit labels Times New Roman red:**

```python
# Add to each FO QDialog after table:
audit = QHBoxLayout()
self.lblUser = QLabel(""); self.lblUser.setStyleSheet("font-family:'Times New Roman';font-size:9pt;font-weight:700;color:#ff0000;")
self.lblLDt  = QLabel(""); self.lblLDt.setStyleSheet("font-family:'Times New Roman';font-size:9pt;font-weight:700;color:#ff0000;")
audit.addStretch(); audit.addWidget(self.lblUser); audit.addWidget(self.lblLDt)
root.addLayout(audit)

def _show_audit(self, pk, rec=None):
    try:
        if rec is None: rec = db.query("SELECT U_Name,U_AE,U_EntDt FROM GuestFolio WHERE FolioNo=?",(pk,))
        # → "Created By : X" if AE=A else "Modified By : " + last U_EntDt
    except: pass

# Find Viewer (F3) parity
from ui.base_master import _SearchViewer  # reuse
btnFind = QPushButton("  Find (F3)"); btnFind.setProperty("vb6", True); btnFind.clicked.connect(self._on_find)
def _on_find(self):
    dlg = _SearchViewer(cfg, self)  # cfg = MasterConfig for GuestFolio searchcode
    if dlg.exec()==QDialog.DialogCode.Accepted: self._searchback(dlg.selected_code)
```

---

### 5.10 Fix F10 — FixedSize + CenterOwner + KeyPreview + BorderStyle 1

**Problem:** Resizable, not centered, no Fixed Single.

**Patch:**

```python
dlg = QDialog(parent)
dlg.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
dlg.setFixedSize(756,301)  # fdCheckIn exact 11340×4515
dlg.setModal(True)
if parent:
    dlg.move(parent.geometry().center() - dlg.rect().center())  # CenterOwner
# KeyPreview already via QShortcut Escape/F5; also:
dlg.setWindowFlag(Qt.WindowType.WindowTitleHint, True)
```

Apply per-form:
- `fdCheckIn 756×301`, `fdRoomChange 818×573`, `FdRoomDisplay Maximized 946×557`, `FdReSetlement 637×490` (but it is Maximized internally so keep `showMaximized()` gated by WindowState).

---

### 5.11 Fix F11 — Validation Messages Verbatim

**Replace Hinglish with VB6 exact (keep bilingual tooltip as secondary):**

```python
# fdCheckIn CmdOK
if today < arr_date:
    if QMessageBox.question(self, "Check In",
            "Guest Arrived Before Arrival Date !\nChecked in Anyway?",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return
# FdCheckOut bill gate
QMessageBox.critical(self, "Information", "First Print Bill")
QMessageBox.warning(self, "Check Out", "Guest Balance is Not Zero")
# KOT pending
QMessageBox.critical(self, "Room Change", "There is some KOT Pending for this Room.")
# Tariff condition
if QMessageBox.question(self, "Room Change",
        "Apply Tariff as per defined Condition?",
        QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
    ...
# Cancel border
QMessageBox.question(self, "Terminate Process", "Cancel ?")
# Delete
QMessageBox.question(self, "Confirmation", "Delete Record ?")
# Search empty
QMessageBox.information(self, "Information", "Records Not Present For Searching.")
# Duplicate
QMessageBox.warning(self, "Information", f"{code} **Already Exist *")
QMessageBox.warning(self, "Information", "Duplicate Name")
```

Keep secondary Hinglish via `setToolTip("पहले folio चुनें / Pehle folio select karo")` for accessibility without diverging main text.

---

## 6. Database Understanding — Front Office Tables (No Schema Change, Read-Only Notes)

### 6.1 Core Tables Referenced Verbatim in VB6

| Table | Key Columns (VB6 verbatim) | VB6 Usage | Python API / Query |
|-------|---------------------------|-----------|--------------------|
| `Booking` / `GrpBookingDetails` | `DocId, BookingDocId, Sno, Cancel, ArrDate, DepDate, LOGSITE_CODE, RoomType, RoomCat, RoomNo, GuestProf, NoDays, NoOfRooms, GuestFolio Not Exists linkage` | `fdCheckIn.Form_Load L234` booking lookup today-only; `fdWalkInEntry` block/booking conflict → `Not In (Select RoomNo from GrpBookingDetails Where Not Exists GuestFolio ... AND IsNull(Cancel,'')<>'Y' And ArrDate=...)` | `core.reserve-*` / `checkin` (bookingdocid optional) |
| `GuestProf` | `Code (KK######), Name, Add1, Add2, City, Phone, Mobile, Email, Nationality, Type India/Foreign, LOGSITE_CODE, U_Name/U_AE/U_EntDt` | `fdCheckIn DGHelp Name/Code Tag pattern`; walkin auto `KK######+1`; `SEARCHBACKPARENT(GuestProf,Code)` | `core.guestprof` `next_code()/insert()/get()`; `frontoffice guestprof_config` |
| `GuestFolio` | `FolioNo (int), DocId (21-char `D<site>CHK...`), Vprefix, Vdate/DepDate/ChkInDate/Time, GuestProf, LOGSITE_CODE, Company, StatusName, OldAdult/Child, Comments1-3, Add1/2, CityName/State/CountryName, RateCode, RoomCat, RoomRate, mFolio, RelatedFolioNo` | `FdCheckOut` folio header 3810×285 fields; `MergeCharge` `mFolio/RelatedFolioNo`; `ReSettlement` `DocId FolioNoDocid` linkage | `core.folio` `SELECT FolioNo,Name,Vdate,DepDate,DocId,Vprefix WHERE Site_Code AND Vprefix` ; `core.fo_ops.open_folio_by_docid/room` |
| `RoomMast` | `Code (=RoomNo), Name, RoomCat, RoomStat ('D' dirty / 'C' clean / 'M' maint), Type='RO', InclCount='Y', Site_Code, LOGSITE_CODE/LOGSITE, PicPath, RoomTaxStru` | `FdRoomDisplay select * where type='RO' and inclcount='Y'` ; `FdCheckOut ROOMSTAT='D'` dirty mark; `RoomChange` `RoomStat='D'` dirty ; `RoomLookup` display | `core.roomstatus.room_rack()` ; `core.fo_ops.free_rooms()` `Type='RO' AND InclCount='Y' AND Code Not In (RoomOcc where ChkOutDate IS NULL)` |
| `RoomCat` | `Code, Name, RevCode, TaxStru, PlanMast linkage` | `Booking LEFT JOIN RoomCat ON Booking.RoomType=RoomCat.Type AND Booking.RoomCat=RoomCat.Code` → room type name | `RoomCat.Name` join in Booking query |
| `RoomOcc` | **30 cols** `DocId, Sno, RoomNo, RoomCat, ChkInDate/Time, ChkOutDate/Time, UserchkoutDate, ChkOutUser, Type='' open / 'O' checkout / 'C' room-change-closed, NewRoomNo, Reason, ChngDate, FolioNoDocid, LOGSITE_CODE, U_EntDt/U_AE, NoDays, Adult/Child, RateCode, PlanDetails FK` | `FdCheckOut` `UPDATE Type='O'` checkout; `fdRoomChange` old SNo `Type='C'` + new SNo open; `Booking` filter `type not in ('C','O')` | `core.fo_ops.room_change()` ; `core.room_occ` ; `core.checkin.create_checkin()` inserts SNo 1 Type='I' |
| `PayCharge` / `GuestFolio PayCharge` | `FolioNo, FolioNoDocid, DocId, VNo, Vdate/VTime, PayCode, PayType, AmtDr/AmtCr/Amount, Comments, ModeSet='S' settlement vs ' ' charge, RestCode='KKFOM', Site_Code, LOGSITE_CODE, ContraDocId, Bill_No, BillAmount, SNo, Rate?` | `FdCheckOut Bal=Sum(AmtDr)-Sum(AmtCr) VType Not In ('ARRES','ADRES') and Foliono`; `ReSettlement ModeSet='S' PayCode<>'ROFF' old sum guard ABS<0.005` ; `FdDisplayFolio` `Folio charges` drill `SNo,PayCode,PayType,Comments,Dr,Cr` | `core.folio.folio_charges/balance` ; `core.expenseentry.list_folio_charges` ; `core.fo_ops.list_settlements/re_settlement` |
| `Plandetails / PlanMast` | `DocId, RoomNo, Code/Name/total/Plan_Package, App_Date, ActiveYn, LOGSITE_CODE, RoomTaxStru, NetPackageAmount PkgAmt` | `FdDisplayFolio TxtValidate max(NetPackageAmount) where Docid+RoomNo` ; `fdRoomChange/DGPackage select Code,Name,total,App_Date,RoomTaxStru from PlanMast where ROOMCAT='<tag>' and ADULTS=<n> and (LOGSITE_CODE='<site>' or 'HO') and ActiveYn='Yes' and App_date<=today ORDER BY Name` | `core.plans` `list_plans()/exists()` ; `fo_ops` free? |
| `FomBillDetails` / `Bill_No` | `Bill_No, FolioNoDocid, SettAmt, Status='SETTLE', VNo cycle` | `FdCheckOut EPABX + SMS Bill_No aggregation via FomBillDetails FB Inner Join RoomOcc R On R.DocId=FB.FolioNoDocid And R.Type='O' And FB.Status='SETTLE'` | `folio.settle_folio()/bill_no` |
| `Enviro` | `LOGSITE_CODE, Vdate/ChkInDate/Time 21-char? , U_EntDt, RoomRentChkOutPost Auto, EPABX_IN flag, etc.` | `FdCheckOut SELECT * from enviro` date casts via `Proc_6_16_EF29FC` + `Proc_6_7_F25D88` | `core.enviro` |
| `EPABX_IN` | `ID, V_TYPE, ROOM_NO, ROOM_NO_NEW, GUEST_NAME, ADVANCE` | Optional checkout `insert into EPABX_IN (ID, CHKOT, ...)` if `Enviro.EPABX='Y'` | `checkout.do_checkout` branch |
| `KOT` | `Pending='Y', RoomNo, RoomType='RO', VoidYN='N', NCKOT<>'Y', DelFlag<>'Y'` | `fdRoomChange Txt_KeyDown KOT gate "There is some KOT Pending..."` | `fo_ops.room_change` KOT check if present |
| `RoomBLockOut` | `RoomCode, Type In ('O','M'), LOGSITE_CODE, Fromdate, ToDate, Reason` | `fdWalkInEntry next-room query Not In (Select RoomCode from RoomBLockOut where Type In ('O','M') AND Fromdate<=today<=ToDate)` ; `roomstatus block_out Type M/O + unblock` | `core.roomstatus.block_out/unblock_room` |
| `GuestMessage` | `Code, GuestProf, RoomNo, Message, Solved Y/N, LOGSITE_CODE, U_Name/U_AE/U_EntDt` | `FindMess.frm Select * From GuestMessage where...` with wingdings solved toggle | *(no Python port yet)* — `guest_services_ui` covers services not messages |
| `FolioLog` | `docid, flag, user, dt, ae` | `folio_ui _log()` `SELECT id,docid,flag,user,dt,ae FROM FolioLog` | `core.folio.log_list()` |
| `RevMast / PayCode` | `Code, Name, ACCode, TaxStru` | `DGChrgPayment PayCode` dropdown `ModeSet='S'` settlements filtered `PayCode<>'ROFF'` | `core.folio.PAY_TYPES` |
| `City / SubGroup (Company) / Employee / Comp_PlanDet` | `City.CityCode/Name, SubGroup SubCode/CC Name, Employee Code` | `FdReSetlement FrComp/FrEmp/FrMember` overlays | `fo_sub_forms.ReSettlement` company dropdown |

### 6.2 Python Core Modules (PYTHONE/core) — What They Already Do Right

- `core.fo_ops.free_rooms()` — `RoomMast Type='RO' AND Code Not In (RoomOcc where ChkOutDate IS NULL)` + `Not In RoomBLockOut` — mirrors `fdWalkInEntry CmdNextRoom` closely (missing `InclCount='Y'` add).
- `core.fo_ops.room_change(docid,new_room,reason)` — full 30-col RoomOcc clone + Type='C' + new SNo open + Booking.OccRoom sync + RoomMast dirty + `KOT Pending` check + `RelatedFolioNo`? → covers W4/W5 verbatim.
- `core.fo_ops.merge_charge(from_room,to_room)` — `mFolio`/`RelatedFolioNo` update + `PayCharge` shift + `GuestFolio.FolioNoDocid` swap — mirrors Merge Folio.
- `core.fo_ops.re_settlement(docid, pending[])` — `ModeSet='S'` old delete + `RestCode='KKFOM'` inserts + `ABS(sum-old)<0.005` guard — mirrors ReSettlement.
- `core.folio.*` — `DocId 21-char + FolioNo + FolioLog` + `folio_charges/balance` + `PYT*` guard.
- `core.checkout.*` — `list_active_folios / list_checked_out / folio_balance / do_checkout / reverse_checkout` with `Type='O'` + `ROOMSTAT='D'` + `PayCharge SettleDate`.
- `core.roomstatus.room_rack() / housekeeping_summary() / update_hk_status / block_out / unblock_room` — InclCount fix pending; otherwise correct.

### 6.3 Constraints — **No DB Schema Change**

- Do **not** ALTER tables; do **not** add columns; do **not** rename PayCode/ModeSet; do **not** modify triggers.
- Fixes above are QSS + QDialog sizing + QListWidget popup + QTimer + guard messages — all **param-bound same SQL** as VB6 where queries remain.
- Required core filter add `AND InclCount='Y'` is **WHERE clause only**, no column add — considered safe UI-query fix, not schema.

---

## 7. Screenshot Cross-Check (VB6 Visual Proof)

| Screenshot | VB6 Form | Controls Seen | Python Match |
|------------|----------|---------------|--------------|
| `02_WalkIn_CheckIn.png` | `fdWalkInEntry Frame1 #C0FFFF 17955×8910 + FrmPackage #80FF80 FGrid3 9675×1740 + labels Extra Person @ %` | Guest Name / Room Type+No / CheckIn/Out dates / Address / Package + tariff matrix pop | `frontoffice` panel shows Guest Name/City/Booking/Adult/Child/Rate but **matrix off-screen** → F3 fix |
| `03_CheckIn_List.png` | `fdCheckIn DGHelp 10965×3375` inside `11340×4515` helper | Guest Name filter + DGHelp list SearchCode|Name hidden width ~731 px | `frontoffice CheckInBrowser` grid 9 cols `StretchLast` always visible → **F1 popup fix** |
| `04_Room_Status.png` / `10_InHouse_Room_Status.png` | `FdRoomDisplay FrmPic #F9FCCB 12855×7590 + FrmRoom #FFC0FF + BtnEnh 1350×735 ×9 cols + PicPath stretched` | Color legend Occupied red / Vacant green / Dirty amber + rack 9 cols | `dashboard RoomRackItem 110×85 rgba` 8 cols + `roomstatus_ui` table 9 cols manual bg → F5 fix (add PicPath stretch) |
| `05_Bill_Reprint.png` | `fdDisplayFolio CmdPrint 1275×1050 + FGrid 8775×5580` preview | Guest ledger charges printed preview | `folio_ui ChargeDialog` single table no print → F13 separate print path needed |
| `06_Bill_ReSettlement.png` | `FdReSetlement Shape5 #C0FFC0 border #C00000 + Line1 Width2 + LTxt0/1/2 white 1605×285` | Settlement split with Total/Paid/Balance boxes | `ReSettlementWindow` inline new_table 4 cols no shape → F8 decorative fix |
| `08_Merge_Folio.png` | `MergeCharge source→target RelatedFolioNo linkage panel` | Two rooms merge with RelatedFolio display | `MergeChargeWindow 640×460` two lineedits + labels → F15 panel detail add |
| `11_Add_New_Profile.png` | `GuestProfile Add` `TopCtrl` bar + `Code KK######` auto + `Type India/Foreign` + audit red | Profile master TopCtrl AEDP + DGHelp City + Nature ListView | `frontoffice guestprof_config` via `BaseMasterForm` already maroon #800000 DGHelp + FindViewer + audit Times New Roman ✅ — parity OK |

---

## 8. Summary for Executor (What to patch next, in priority order)

1. **F9 InclCount** — add `AND InclCount='Y'` to `room_rack()` query (1-line WHERE fix) — highest data correctness.
2. **F1 DGHelp** — add `_VB6_DGHelp` popup helper to `frontoffice CheckInBrowser` + `folio_ui FolioBrowser` + `fo_sub_forms RoomChange` Tag field.
3. **F2 FrmAdjust** — add password overlay frame to `checkout_ui`.
4. **F3 Matrix** — add `Tariff Matrix…` read-only dialog to `RoomChangeWindow` + `frontoffice`.
5. **F4 Timer** — add `QTimer 1000` + `LblCheckInDay DDDD` to all FO browsers + `dashboard lbl_date`.
6. **F5/F6 maroon + bevel** — per-label `color:#800000 Arial 9.75 Bold` + set `property vb6 true` on all `QPushButton` so theme bevel `outset #ffffff #808080 radius 0` activates.
7. **F8 Shape/Line/LTxt** — decorative bill totals frame to `ReSettlementWindow`.
8. **F11 Messages verbatim** — replace Hinglish `Pehle…` with VB6 exact English quoted above (keep Hinglish as `toolTip`).

All above are **frontend patches** — zero ALTER. Verify after with `python -m py_compile ui/*.py && python ui/verify_fix.py`.

---

> **Report path:** `PYTHONE\COMPARE_WORKSPACE\UI_FRONTOFFICE2_COMPARE.md` (this file) — proceed to patching in order F9 → F1 → F2 → F3 as next commits.

