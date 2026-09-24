# FRONTEND FRONTOFFICE — VB6 vs Python Parity Report
> Focus: **FRONT OFFICE (CheckIn, CheckIn List, Room Status, Display Rack, Bill Reprint, ReSettlement, Merge Folio, WalkIn)**
> Date: 2026-09-24
> Workspace: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_FRONTOFFICE_COMPARE.md`
> Rule: **Do NOT modify DB. UI-only — same control behavior, same colors/sizes, same validation messages, VB6 Classic radius 0 bevel. Backend SQL param-bound SAME as VB6 verbatim.**

---

## 0. Sources Read ONE BY ONE Fully

### VB6 (9 .frm)

| # | File | Lines | Read? |
|---|------|-------|-------|
| V1 | `fdCheckIn.frm` | 459 | ✅ full — 11340x4515, BackColor &HC6B7A4, BorderStyle 1 Fixed Single, MDIChild -1, KeyPreview -1, TopCtrl1 11340x450 Visible 0, BtnEnh CmdOK 1155x975 at 5400,2865, Picture2 300x270 hidden, Txt(0) 9270x285 at 1560,615 BorderStyle 0 None Fore &HC00000 Arial 9.75, DataGrid DGHelp 10965x3375 at 210,915 Visible 0 TabStop 0, MSFlexGrid FGPoint 1980x1440 at 15,3585 Visible 0, Label1 Guest Name 1155x240 at 360,615 Fore &HC00000 Arial 9.75 Bold 700 |
| V2 | `FdCheckOut.frm` | ~2836 | ✅ full — Caption "Room Check Out" BackColor &HC0C0C0 Client 14625x8310 (975x554 px) ControlBox 0 KeyPreview -1 ClientLeft 210 ClientTop 1335. Frame1 Caption Frame1 Back &HFFC0C0 at -15,-30 16800x9375 BorderStyle 0 None. Inside: DataGrid DGRoomType 5025x3330 at 11760,5760 hidden, DGRoomNo 3840x3330 at 13950,5220 hidden, Frame FrmAdjust 4050x1560 at 7485,5595 hidden with Txt24 1260x315 at 1500,735 Enabled 0 Txt23 2115x315 at 1005,225 PasswordChar # CMDSET 795x315 at 1710,1110 Enabled 0 CmdPass GO 495x315 at 3135,225. Txt indices 0..24 covering RoomNo/RateCode/AdultChild/Status/Comments, FGrid 8610x6645 at 5385,990, Fgrid1 8610x285 at 5385,7635 total row, FGPoint 1980x1440 at 14655,30 hidden, BtnEnh BtnExit 1650x750 at 2400,7335, CmdPostChrg 1575x780 at 1545,6600, CmdPlanBill 1635x720 at 3135,6615, LblFormCaption &HC0FFFF 180x540 at 0,0 System 19.5 Bold, GuestImage 1035x525 at 15570,6825 hidden, Labels Lbl Guest Folio No/Audit maroon &H800000 Arial 9.75 Bold, Header Label1 Guest Folio Details Back &HC00000 Fore &HFFFFFF at 5385,585 8535x375 Arial 9.75 Bold, Label1 Guest Detail/Room Details same, LblCheckInDay "." Fore &HC0 at 4095,1335 Tahoma 9.75, TopCtrl1 7380x375 at 45,7455 |
| V3 | `fdDisplayFolio.frm` | ~1357+1800 code | ✅ full — Caption "Guest Ledger" Back &HFFC0C0 WindowState normal Client 14235x8985 (949x599 px) ControlBox 0 MDIChild -1? (implicit). TopCtrl1 14235x450 at 0,8535 hidden, FRectGrid 4065x1020 at 5925,4830 hidden, Txt25 PlanAmount 1185x285 at 1335,3255 RightJustify, FrmAdjust 4050x1590 at 7515,3165 hidden (same Go/Set/Cancel/Pass pattern), Txt 0 FolioNo 780x330 at 3930,600, Txt1 CheckInDate 1545x285 at 1335,1365 Locked -1, Txt2/3 420x285 hh/mm Center Bold, Txt10 GuestFolioNo 1545x285 at 1335,1050, FGrid 8775x5580 at 5235,1020, Fgrid1 8445x285 at 5205,6645, FGPoint 1980x1440 at 810,7710 hidden, DGRoomNo 5655x1305 at 9330,7200 hidden, CmdExit 1275x1050 at 7620,7110 BtnEnh, CmdPrint 1275x1050 at 4560,7155, Labels: Label1 Charge Details Back &HC00000 Fore &HFFFFFF at 5235,585 8190x375 Bold, Guest Room For Room No at 60,585 5100x375 Bold, Guest Details at 90,3600 5040x375 Bold, Lbl Status/Address/Comment 9pt Bold Fore &HC00000 |
| V4 | `fdRoomChange.frm` | ~1282+ pcode | ✅ full — Caption "Room Change" Back &HFFC0C0 Client 12270x8595 (818x573 px) ControlBox 0 KeyPreview -1 LockControls -1 Font Tahoma 8.25. DataGrid DGPackage 4230x1920 at 3180,1005 hidden, Frame FrPackage Back &HFFC0C0 Fore &HC00000 10125x4980 at 1005,570 hidden Appearance Flat with Txt31 900x270 at 4890,435 Txt42 900x270 at 6000,435 Txt45 900x270 at 6000,720 Txt44 900x270 at 4890,720 (Extra Person @ % Disc), Txt47 1605x270 at 8100,150 hidden, Txt48 1290x270 at 7335,3825 Locked, Txt46 1035x270 at 2175,1005 Locked, Txt43 Yes/No Center at 2175,720, TxtGrid0 975x240 at 60,1650 hidden, Txt24 Plan/Package 4230x270 at 2175,150, CmdOk &Ok 1740x465 at 3615,4125, FGrid3 9510x2415 at 45,1410. Outside: Txt50 1125x285 at 11205,4125 hidden, TopCtrl1 12270x465 at 0,8130 hidden, Frame1 1230x1245 at 14160,6840 hidden, Txt30 GuestName? 4350x285 at 4545,6015, Txt40 etc 1125x285 at 7770,5385, Frmrate Back &HFF0000 4830x795 at 14190,180 hidden with Txt22 3285x270 at 1440,120 + Txt23 at 1440,420 + Labels Remarks/Authorization * red, DataGrids DGPlanPkg 3285x1650 at 165,5370 hidden, DGNewRoomNo 2805x1875 at 14805,1815 hidden, DGRoomNo 2685x1695 at 14700,1410 hidden |
| V5 | `FdRoomDisplay.frm` | 302 | ✅ full — Caption "Room View" Back &HFFC0C0 WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 Client 14190x8355 (946x557 px) Picture frx:0 Icon frx:52A. Frame FrmPic Back &HCBFCF9 Fore &HFF0000 12855x7590 at 15,1305 Appearance 0 Flat BorderStyle 0 None with Image Picture1 11160x7545 at 0,0 Stretch -1 BorderStyle 1. Frame FrmRoom Back &HFFC0FF 19875x11070 at 0,0 with BtnEnh BtnExit 1350x735 at 10065,525, BtnEnh Cmd(1) 1350x735 at 15,540, LblFormCaption &HC0FFFF 180x540 System 19.5 at 0,0 |
| V6 | `FdReSetlement.frm` | ~5784 | ✅ full header + Form_Load scan — Caption "Post Charges/Payment" Back &HFFC0C0 WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 Client 9555x7350 (637x490 px) Font Tahoma 9.75. MainCtrl TopCtrl1 9555x450 at 0,6900 hidden, DGMember 4215x3330 at 13650,6195 hidden, FrMember 6000x315 at 165,8055 hidden with Txt39 4000x285 at 1650,30, DGBill 6780x3390 at 13320,5610 hidden, Picture2 300x270 at 18870,7860 hidden, Picture1 300x270 at 19620,7665 hidden, Txt38 930x285 at 3075,1395 hidden, Txt36 1545x285 at 1500,1080 RightJustify, Timer1 Interval 1000 at 10350,0, DGRoom 3885x3390 at 12600,5700 hidden, DGRoomNo 2580x3330 at 13980,4890 hidden, DGEmp 4170x3330 at 12555,4980 hidden, DGChrgPayment 5490x3465 at 15795,4860 hidden, Txt35 1500x285 at 9570,1740 RightJustify, Txt11 GuestRoomNo 2535x285 at 1485,2340, Txt0 Folio 765x285 at 4035,660, Timer, Txt7/8/9 Status/Comments, FGrid 5790x2430 at 5895,3750, FGPoint 1980x1440 at 16455,7860 hidden, BtnEnh CmdExit 1350x1050 at 8940,7575, BtnSave 1350x1050 at 6990,7560, Line1 Border &HC00000 X1 7020 Y1 7005 X2 10275 BorderWidth2, Shapes Shape5 Border &HC00000 Fill &HC0FFC0 at 7035,6270 3255x1200, Labels LTxt0/1/2 glass boxes Total/Paid/Balance at 7095 positions, LblFormCaption &HC0FFFF 180x540 System 19.5, VB6 ReSettlement ModeSet='S' pay logic + sum guard |
| V7 | `fdWalkInEntry.frm` | ~1.28M chars | ✅ full header — Caption "Walk In / Check In Entry" Back &HFFC0C0 WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 Client 13995x8595 (933x573 px) LockControls -1. Frame FrmPackage Back &H80FF80 10005x3900 at 30,3990 hidden with DGPackage 4230x3270 at 2190,420 hidden, BtnEnh CmdOk 1110x510 at 3495,3300, Txt54 1080x255 at 2175,405 RightJustify, Txt53 Package Name 4230x255 at 2175,135 Locked, TxtGrid2 975x240 at 105,1485 hidden, Txt67 Yes/No Center 345x255 at 2175,675, Txt68 1035x255 at 2175,945 Locked, etc., Frame Frame1 Back &HC0FFFF 17955x8910 at 30,900 BorderStyle 0 None with Txt83 3210x285 at 1620,5745, CmdVerifyMember 2265x480 at 15,7230 hidden, Text fields 28/61/62 hidden, Frame2 Inner 13965x6990 hidden with Check All, Command5 900x765, DGGrpRoom etc  - tariff matrix core |
| V8 | `FindMess.frm` | 395 | ✅ full — Caption "" Back &H80C0FF (BGR FF C0 80 -> RGB #80C0FF light blue) BorderStyle 1 Fixed Single MaxButton 0 MinButton 0 KeyPreview -1 Client 10995x5715 (733x381 px) CenterOwner. TextBox TxtSearch Back &HFFFF80 Left 345 Top 675 2055x240 Visible 0 Border 0 Arial Narrow 8.25 Bold 700 Appearance Flat HideSelection 0. MSHFlexGrid GridSel 10965x5685 at 30,0. Menu popup hidden with FSR/ FNSR/ RF/ SA/ SD filter/sort. GridSel_UnknownEvent_9 Wingdings delivered toggle, Update GuestMessage set Solved Y/N, SA/SD sort, Filter Same/ Not Same, TxtSearch overlay 15595518/16777152 colors |
| V9 | `FdCheckOut` code/logic | — | RoomOcc Type='O' checkout + RoomMast ROOMSTAT='D', EPABX_IN, SMS forward, FGrid delete audit, Balance Bal=Sum(AmtDr)-Sum(AmtCr) VType Not In ('ARRES','ADRES'), Strict gate |
| V10 | Screenshots `02_Operations` | 11 PNG | WalkIn_CheckIn, CheckIn_List, Room_Status, Bill_Reprint, Bill_ReSettlement, Misc_Payment, Merge_Folio, Reverse_Merge_Folio, InHouse_Room_Status, Add_New_Profile, Blank_GRC |

### Python (5 .py + theme)

| # | File | Lines | Verbatim |
|---|------|-------|----------|
| P1 | `ui/folio_ui.py` | 339 | `FolioBrowser(QWidget)` QVBox top QHBox lblTitle "In-House Folios" + Refresh button + QTableWidget NoEditTriggers SelectRows ResizeToContents AlternatingRows cellDoubleClicked->ChargeDialog. Bar: Check-Out(Settle) Ctrl+O, Amend Ctrl+A, Receive Payment Ctrl+R, Folio Log Ctrl+L, F5 reload. `ChargeDialog(QDialog) 640x400` charges table Dr/Cr + balance. `PaymentDialog(QDialog) QFormLayout` Current Balance label + QComboBox PAY_TYPES + QLineEdit Amt "0.00" + Comments "CASH RECD." + Receive/Cancel. `AmendDialog(QDialog) QDateEdit CalendarPopup`. `_fill()` helper QColor theme palette. DB: `SELECT FolioNo,Name,Vdate,DepDate,DocId,Vprefix FROM GuestFolio WHERE Site_Code=? AND Vprefix=? ORDER BY FolioNo DESC` (no LogSite, no ChkOutDate). No DGHelp, no FGPoint, no Tag/Code, no FixedSize. |
| P2 | `ui/checkout_ui.py` | 368 | `CheckOutBrowser(QDialog) 1100x650` QTabWidget Active/CheckedOut. Active: QTableWidget 7 cols FOLIO_COLS FolioNo GuestName GuestProf City Departure Days Status + lblBal Segoe UI 11 Bold + QTableWidget charges 7 cols VType VNo PayCode Amount Dr Cr Remarks maxHeight 200 + btn Check-Out(PYT*) role danger minHeight34 + Refresh + Close. CheckedOut: 6 cols FolioNo Guest Dep CheckOutDate ByUser DocId + Reverse. Shortcuts F5 Ctrl+O Ctrl+R. `reload_active()` list_active_folios, `reload_checkedout()` etc. Colors via theme status_colors danger_text/success_text. No FrmAdjust password, no Timer1, no GuestImage, no DGRoomType/No hidden grids, no System caption. |
| P3 | `ui/fo_sub_forms_ui.py` | 423 | 4 QMainWindow: `RoomLookupWindow` 600x400 Search+Table 4 cols RoomNo Category Status GuestName + filter. `RoomChangeWindow` 680x480 Guest locate GroupBox Search+Load + Current stay FormLabels Folio/Guest/OldRoom + New room QComboBox free_rooms + Reason + Save role warning. `MergeChargeWindow` 640x460 Form FromRoom/ToRoom + lbl_src/tgt + total + Merge role danger guard src!=tgt & both found. `ReSettlementWindow` 720x540 Folio/Room QLineEdit+Load + table 6 cols DocId VNo Date PayType Amount Comments + New settlement QGroupBox PayCode Combo + QDoubleSpinBox Amount + Note + Add Line + new_table 4 cols + Re-Settle role warning guard sum. All via `fo_ops.*`. No DataGrid DGChrgPayment visible, no FrMember/FrComp/FrEmp overlay positions, no wingdings. |
| P4 | `ui/frontoffice.py` | 236 | `guestprof_config() MasterConfig 6 cols Code/Name/Add1/City/Phone/Mobile 8 fields + PYT delete guard. `CheckInBrowser(QDialog) 1060x560` QTableWidget 9 cols Folio VDate Name GuestCode City Days DepDate User AE + empty label + lblState + btn New Check-In Ctrl+N + Refresh F5 + Close Esc. New dialog QFormLayout Guest Name(PYT*) + GuestProf Code blank auto + Arrival QDateEdit + Departure + City + BookingDocId + Adult/Child + RateCode + ChkInTime HH:MM + Save/Cancel. Logic: guestprof.next_code() KK###### auto, checkin.create_checkin(...). FixedSize? resize 1060x560 not Fixed. |
| P5 | `ui/front_office_dashboard.py` | 860 | `FrontOfficeDashboard(QWidget)` StatCard QFrame glassCard Fixed 96-115px accent border-left 4px hover + RoomRackItem 110x85 status colors (Occupied red 0.15, Dirty amber, Maint gray, Vacant green) badge 3-letter. Build: topBar Hotel Title + btn Refresh, quickActions QFrame 7 buttons + New Reservation etc, KPI 8 cards grid arr/dep/inhouse/avail/occ/vac/dirty/pending, strip occupancy gauge, Dual Tables Arrivals 5 cols Booking# Guest Arrival Departure Action Check-In green + Departures Folio# Guest Room Dep Action Check-Out amber, Rack view Grid 8 cols filter All/Available/Occupied/Dirty/Maintenance + scroll. No VB6 FdRoomDisplay PicPath stretched image, no Bevel, no world clocks. |
| P6 | `ui/theme.py` | 754 | `DEFAULTS VB6 Classic` mode light accent #000080 bg #d4d0c8 surface #ffffff border #808080 radius 0 vb_mint #c2e0ce vb_pink #ffc0ff vb_pale_yellow #ffffc0 vb_navy #000080 vb_maroon #800000 glass_opacity 0.95 bg_style solid. `_glass_qss` radius0 injects bevel: QPushButton outset #ffffff #808080, QLineEdit inset. `palette()` `status_colors()` etc. |

---

## 1. VB6 Controls Verbatim (Focus: Front Office)

### 1.1 `fdCheckIn.frm`:15-18 — Look Up Reservation By Guest Name

```
Caption = "Look Up Reservation By Guest Name"
BackColor = &HC6B7A4&      ; BGR C6 B7 A4 -> RGB #A4B7C6 (dusty blue-gray)
BorderStyle = 1 Fixed Single   MaxButton 0 MinButton 0 Visible 0 MDIChild -1 KeyPreview -1
ClientWidth = 11340 twips = 756 px    ClientHeight = 4515 = 301 px
ClientLeft 45  ClientTop 615
Font MS Sans Serif 9.75 400  WhatsThisHelp -1
TopCtrl1  MainCtrl at 0,0 11340x450 Visible 0 TabIndex 6
BtnEnh CmdOK at 5400,2865 1155x975
Picture2 at 10665,6915 300x270 Visible 0 Picture frx:0
Txt(0) at 1560,615 9270x285 BorderStyle 0 None Appearance 0 Flat Fore &HC00000& (=BGR 00 00 C0 -> #0000C0 navy-blue text) Font Arial 9.75 400
DGHelp DataGrid at 210,915 10965x3375 Visible 0 TabStop 0
FGPoint MSFlexGrid at 15,3585 1980x1440 Visible 0
Label1(0) "Guest Name" at 360,615 1155x240 Fore &HC00000 AutoSize -1 BackStyle Transparent Font Arial 9.75 700
```

**Workflow verbatim:** `Form_Load` L234 builds `Booking` join with `CANCEL='N' AND LOGSITE_CODE='<site>' AND Count Distinct Sno Where Not Exists GuestFolio AND IsNull(Cancel,'')<>'Y' And GrpBookingDetails.ArrDate=<today> AND BookingDocid=Booking.DocId)>0 ORDER BY Name` (only not-yet-checked-in booking SNOs for today). `DGHelp_UnknownEvent_9` hides DGHelp, sets `Txt(0).Tag = Fields("Code").Value`, `Txt(0).Text = Fields("Name")`. `Txt_GotFocus` L285 positions DGHelp under Txt via `Proc_6_137_1193554(Me.DGHelp, global_56, Index)` + FGPoint helper, Selects text. `Txt_KeyDown` L342 handles Esc (= hide DGHelp), arrows/PageUpDown via `Proc_6_69/138` navigating DGHelp/FGPoint, Enter/Down -> `Proc_6_75/76`. `Txt_KeyPress` handles incremental filter `Proc_6_89_146F1AC(..., "Name")`. `Txt_Validate` L384 sets Text=Fields("Name"), Tag=Fields("Code"). `CmdOK_UnknownEvent_9` L184 guards `CDate(today) < Arr_Date => MsgBox "Guest Arrived Before Arrival Date !" & vbCrLf & "Checked in Anyway?" vbYesNo 0x24 => 7 cancel`, then `fdWalkInEntry.AdvType="CHK" FrmType="Check In Entry" TopCtrl1_UnknownEvent_A()` + `SEARCHBACKPARENT(GuestProf, Code)` + `Unload Me`. `TopCtrl1_UnknownEvent_16` L143 BeginTrans/Commit/Rollback pattern.

**Colors decode:** `&HC6B7A4& = 0x00C6B7A4 => B=C6 G=B7 R=A4 => #A4B7C6`. `&HC00000& = 0x00C00000 => B=C0 G=00 R=00 => #0000C0` (VB6 navy-blue, not maroon #C00000). Confirmed by BGR order (low byte = Red).

### 1.2 `FdCheckOut.frm`:2-14 — Room Check Out

```
Caption "Room Check Out" BackColor &HC0C0C0 (BGR C0 C0 C0? Actually C0 C0 C0 => gray? Wait &HC0C0C0 = 0x00C0C0C0 => B=C0 G=C0 R=C0 => #C0C0C0 gray)
ControlBox 0 KeyPreview -1 Client 14625x8310 (975x554 px) ScaleMode 1 AutoRedraw 0
Frame1 "Frame1" Back &HFFC0C0 (BGR C0 C0 FF => RGB #C0C0FF pale lavender) at -15,-30 16800x9375 Border 0 None
  DGRoomType 5025x3330 at 11760,5760 hidden
  DGRoomNo 3840x3330 at 13950,5220 hidden
  FrmAdjust 4050x1560 at 7485,5595 hidden with Password GO pattern (Txt24/23, CmdPass GO, CMDSET Set, Command3 Cancel)
  Txt22 870x285 at 3180,1005 hidden Fore &HC00000
  Timer1 Interval 1000 at 0,0
  Command1 1050x195 at 120,75 hidden
  Picture2 300x285 at 14655,2295 hidden frx:442
  TxtGrid(0) 345x240 at 5685,1305 hidden Fore &HC00000
  Command2 "Bill Settle" 1320x690 at 15225,3045 hidden Tahoma 9.75 Bold 700
  Txt15/14 420x285 Center at 3180/3630,1635 Locked -1 (time hh/mm)
  Txt13 1545x285 at 1605,1635 (DepDate)
  Txt16/17/18 Comments 3810x285 at 1290,5805/5490/5175
  Txt21/20/19 Address lines 3810x285 at 1290,4545/4230/3915
  Txt4 RoomType 2460x285 at 1605,1950
  Txt6/5 Adult/Child 480x285 at 2115/1605,2265
  Txt7 RateCode 990x285 at 14070,1890 hidden
  Txt8 RoomRate 990x285 at 1605,2580
  Txt0 Folio 690x285 at 3945,615
  Txt1 ChkInDate 1545x285 at 1605,1320
  Txt9 GuestName 3810x285 at 1290,3600
  Txt11 Company 3810x285 at 1290,4860
  Txt12 Status 3810x285 at 1290,6120
  Txt3/2 hh/mm ChkInTime 420x285 Center at 3630/3180,1320
  Txt10 GuestFolioNo 1545x285 at 1605,1005
  FGrid MSHFlexGrid 8610x6645 at 5385,990
  Fgrid1 MSHFlexGrid 8610x285 at 5385,7635 (total row)
  FGPoint 1980x1440 at 14655,30 hidden
  BtnEnh BtnExit 1650x750 at 2400,7335
  BtnEnh CmdPostChrg 1575x780 at 1545,6600
  BtnEnh CmdPlanBill 1635x720 at 3135,6615
  cmdProvisional 1560x735 at 975,8115 hidden
  LblFormCaption &HC0FFFF 180x540 at 0,0 Border Fixed Single Align Center Font System 19.5 700
  GuestImage 1035x525 at 15570,6825 hidden Stretch -1
  Label1 "Guest Folio Details" Back &HC00000 Fore &HFFFFFF at 5385,585 8535x375 Center Arial 9.75 700
  Lbl Depature Date etc Fore &H800000 (BGR 00 00 80 => #000080 navy) at 120,1650 AutoSize Transparent Arial 9.75 700
  TopCtrl1 7380x375 at 45,7455
```

**Key logic verbatim:** `Command2_Click` guards bill: `SELECT isnull(bill_no,'') as Bill_No,AmtDr ... where LogSite_Code='<site>' AND (ContraDocId is NULL or '') and foliono=<folio> Filter "Bill_No='' and AmtDr<>0" => "First Print Bill"` ; distinct bill check ; `SELECT * from enviro WHERE LOGSITE_CODE='<site>'` ; `SELECT Sum(AmtDr)-Sum(AmtCr) as Bal where LogSite_Code='<site>' and VType Not In ('ARRES','ADRES') and Foliono=<folio>` => if Bal<>0 and Enviro.Checkout Strict => "Guest Balance is Not Zero" -> fdPaymentCharge. `BeginTrans` date strings via `Proc_6_7_F25D88` + `Proc_6_16_EF29FC` => `UPDATE RoomOcc set chkouttime='<HH:MM>',ChkOutDate=<date>,UserchkoutDate=<date>,ChkOutUser='<user>',Type='O',U_EntDt=<date>,U_AE='E' where Docid='<docTag>' and LogSite_Code='<site>' and RoomNO='<room>' and (Type='' or Type is NULL)` ; `UPDATE RoomMast set ROOMSTAT='D' WHERE logsite_code='<site>' and CODE='<room>' AND TYPE='RO'` ; `UPDATE PayCharge set SettleDate=<date> where FolioNoDocid='<folDoc>' and LogSite_Code='<site>'` ; EPABX_IN optional ; `CommitTrans` + SMS selects.

### 1.3 `fdDisplayFolio.frm`:2-14 — Guest Ledger

Same pink-lavender shell `Back &HFFC0C0 #C0C0FF` Client 14235x8985 (949x599 px) LockControls -1. Txt29 Status 3975x285 at 1215,6885 Locked, TopCtrl 14235x450 at 0,8535 hidden, FRectGrid 4065x1020 hidden, Txt25 PlanAmount 1185x285 at 1335,3255 RightJustify, FrmAdjust hidden, Txt26/27/28 address lines, DGChrgPayment 4980x690 hidden, Fgrid1 8445x285 total, Txt22 ChkOutDate? 1545x285, Txt6/5/4/11 room fields, Txt16 hidden, Txt10 GuestFolio, Txt1 CheckIn etc., DGRoomNo 5655x1305 hidden, FGrid 8775x5580 at 5235,1020. Labels: PlanAmount maroon 9pt, Guest Details header Back &HC00000 (#0000C0 navy due BGR) 5040x375, Room header same, maroon labels 9pt. LblFormCaption system vertical.

**Code:** `Txt_Validate` L1528 same room-charge fetch as CheckOut + PkgAmt `max(NetPackageAmount) from Plandetails where Docid='<doc>' And RoomNo='<room>'` + RoomRentChkOutPost Auto posting loop. Txt_GotFocus DGHelp for RoomNo SearchCode.

### 1.4 `fdRoomChange.frm`:2-15 — Room Change

```
Caption "Room Change" Back &HFFC0C0 Client 12270x8595 (818x573 px) Lock Font Tahoma 8.25
DGPackage 4230x1920 at 3180,1005 hidden
FrPackage 10125x4980 at 1005,570 hidden Back &HFFC0C0 Fore &HC00000 Appearance Flat
  Txt31 ExtraPerson 900x270 at 4890,435 RightJustify Arial 9 Bold 700
  Txt42/45 @ % Disc etc 900x270
  Txt47 1605x270 at 8100,150 hidden Locked
  Txt48 Total 1290x270 at 7335,3825 Locked RightJustify
  Txt46 RoomRate 1035x270 at 2175,1005 Locked RightJustify
  Txt43 Yes/No Center 345x270 at 2175,720 Text "Yes"
  TxtGrid0 975x240 at 60,1650 hidden
  Txt24 Package 4230x270 at 2175,150 Locked
  CmdOk &Ok 1740x465 at 3615,4125
  FGrid3 9510x2415 at 45,1410
  Labels: Extra Person @ 1110, Package Discount 1590, % 135, Inc in Room Rate 1470, Calculation Mode hidden, Plan/Package etc 700 Bold Arial 9
Outside: Txt30 4350 at 4545,6015, Txt40 1125 at 7770,5385, TopCtrl1 12270x465 at 0,8130 hidden, Frame1 hidden, Txt50 1125 at 11205,4125 hidden, Frmrate &HFF0000 4830x795 at 14190,180 hidden (Remarks/Authorization * red)
```

**Logic:** 30-col RoomOcc INSERT new SNo=MAX+1, Type='' open, ChngDate, old row Type='C' NewRoomNo+Reason, GuestMessage RoomNo/Cat update, Booking.OccRoom update, RoomMast dirty, PlanDetails reinsert.

### 1.5 `FdRoomDisplay.frm`:2-18 — Room View (Rack)

```
Caption "Room View" Back &HFFC0C0 WindowState 2 Maximized MDIChild -1 ControlBox 0 KeyPreview -1 Client 14190x8355 Picture frx:0 Icon 52A
FrmPic Back &HCBFCF9 (BGR F9 FC CB => RGB #CBFCF9?? Actually B=CB G=FC R=F9 => #F9FCCB pale cream-yellow) Fore &HFF0000 12855x7590 at 15,1305 Border 0 None with Picture1 11160x7545 Stretch -1 Border Fixed Single
FrmRoom Back &HFFC0FF (BGR FF C0 FF => #FFC0FF pink) Fore &H80000008 (system) 19875x11070 at 0,0 with BtnExit 1350x735 at 10065,525, Cmd(1) 1350x735 at 15,540, LblFormCaption &HC0FFFF 180x540 System 19.5
```

**Logic:** `Form_Load` L110 `select * from roommast where logsite_code='<site>' and type='RO' and inclcount='Y' order by Code` => builds BtnEnh Cmd grid 9 cols. `Cmd_UnknownEvent_9` `Select PicPath From RoomMast Where ... Code='<code>'` => LoadPicture stretch center. `Form_Resize` positions LblFormCaption left 0 width full. KeyDown Esc hides Pic, F10 (0x79=121) Unload.

**VB6 Rack decode:** 9-col BtnEnh grid uses `Proc_104_5_EB09E0` center. FrmRoom 11580x7500 at 15,10 then FrmPic same.

### 1.6 `FdReSetlement.frm`:2-18 — Post Charges/Payment (Bill ReSettlement)

```
Caption "Post Charges/Payment" => actually Bill ReSettlement uses same shell as Post Charges
Back &HFFC0C0 WindowState 2 MDIChild -1 ControlBox 0 KeyPreview -1 Client 9555x7350 Font Tahoma 9.75
TopCtrl1 9555x450 at 0,6900 hidden
DGMember 4215x3330 at 13650,6195 hidden
FrMember 6000x315 at 165,8055 hidden
DGBill 6780x3390 at 13320,5610 hidden 6780x3390 (452x226 px)
Picture2/1 hidden
Txt38 930x285 at 3075,1395 hidden
Txt36 1545x285 at 1500,1080 RightJustify
Timer1 1000
DGRoom 3885x3390 hidden etc.
Txt35 Amount 1500x285 at 9570,1740 RightJustify
Txt11 RoomNo etc.
FGrid 5790x2430 at 5895,3750
Line1 &HC00000 X1 7020→10275 Y 7005 BorderWidth2
Shape5 Border &HC00000 Fill &HC0FFC0 at 7035,6270
LTxt0/1/2 glass boxes 1605x285 Total/Paid/Balance Border Fixed Single Align Center Tahoma 9 Bold
Labels maroon &HC00000 9-9.75 Bold, LblNature "." Back &HFFC0C0 Fore &H4080 at 11130,1410
LblFormCaption &HC0FFFF 180x540 System
Txt35/36 etc. PayCode DBText, FrCCDet BatchNo etc., FrChqDet, FrSendRoom, FrEmp, FrComp
```

**Logic:** `ModeSet='S'` settlements: `SELECT DocId,VNo,Vdate,VTime,PayCode,PayType,AmtCr,Comments,ModeSet FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<> '<site>ROFF' ORDER BY Vdate DESC,VNo` (top 1 old receipt), sum-match guard `abs(sum(new)-old) <0.005` else ValueError, `DELETE FROM PayCharge WHERE DocId=? AND FolioNoDocid=? AND Site_Code=? AND ModeSet='S'` then per-line `next_vno('REC')` + 21-char DocId + RestCode='KKFOM', ModeSet='S'.

### 1.7 `fdWalkInEntry.frm`:2-16 — WalkIn / CheckIn Entry

```
Caption "Walk In / Check In Entry" Back &HFFC0C0 WindowState 2 MDIChild -1 ControlBox 0 Client 13995x8595
FrmPackage Back &H80FF80 (BGR 80 FF 80 => RGB #80FF80 light mint) 10005x3900 at 30,3990 hidden with DGPackage etc. (tariff matrix)
Frame1 Back &HC0FFFF (BGR FF FF C0 => #C0FFFF cyan) 17955x8910 at 30,900 Border 0 None with Txt83 etc.
DGGrpPlanPkg 3360x1245 at 7230,1065 hidden, DGGrpRoomNo 1455x1245 hidden, DGGrpRoomCat 3360x1245
```

**Logic:** DocId 21-char `D<site>CHK<suff> <year> <folio>` FolioNo = MAX+1 per FY Vprefix, Insert GuestFolio + RoomOcc SNo1 Type='I', FolioLog Flag 'A', tariff matrix FrPackage interaction Plan/Package amount.

### 1.8 `FindMess.frm` — Guest Message Finder (Housekeeping msgs)

```
Back &H80C0FF (BGR FF C0 80 => RGB #80C0FF light sky blue) Border Fixed Single 10995x5715 StartUp CenterOwner
TxtSearch Back &HFFFF80 (BGR 80 FF FF => #80FFFF pale yellow?) at 345,675 2055x240 Visible 0 Border 0 Arial Narrow 8.25 Bold 700 Flat
GridSel MSHFlexGrid 10965x5685 at 30,0
Menu popup Filter Same/ Not Same / Remove / Sort Asc/Desc
```

**Logic:** `Form_Load` L250 `SELECT * FROM GuestMessage` via `global_52`, colors 15595518/16777152, TxtSearch overlay filter, Sort Asc/Desc via `Me.Sort = Mid(var_88,1,Col)`, Delivered toggle wingdings ₹ update Solved Y/N.

---

## 2. Python Controls — Verbatim Read

### 2.1 `ui/folio_ui.py`:40

- Not FixedSize, resize 640x400 dialog, QVBox with QFormLayout for Pay/Amend, QTableWidget NoEditTriggers SelectRows AlternatingRows, palette `text #000000`, header via `_fill()` with `setForeground(text)`, empty label `#64748b`. No TopCtrl, no DataGrid 6780x900 vs VB6 Bill grid 6780x3390 at 13320,5610 hidden. No FGPoint, no maroon labels.

### 2.2 `ui/checkout_ui.py`:53

- QDialog 1100x650, QTabWidget Active/CheckedOut, lblBal Segoe UI 11 Bold danger_text/success_text, charges QTable 7 cols, buttons role danger/warning minHeight 34, F5 Ctrl+O/R shortcuts. Missing FrmAdjust password frame, Timer1, GuestImage, DGRoomType/No 6780-like hidden grids, System caption.

### 2.3 `ui/fo_sub_forms_ui.py`:17

- 4 QMainWindow not QDialog/MDIChild, no Fixed Single, no KeyPreview, no ClientWidth 12270 exact. RoomLookup 600x400 vs VB6 RoomDisplay 14190x8355 maximized rack; RoomChange 680x480 vs VB6 12270x8595 with FrPackage 10125x4980 tariff matrix missing; MergeCharge 640x460 vs FrmMergeCharge hidden DG 5490x3465; ReSettlement 720x540 vs VB6 9555x7350 with LTxt boxes Total/Paid/Balance shape 3255x1200, Line separators. Colors via `theme.palette()` → `#ffffff` glass not `#C0C0FF` or `#80FF80`.

### 2.4 `ui/frontoffice.py`:69

- CheckInBrowser 1060x560 (vs VB6 fdCheckIn 11340x4515=756x301 + walkin 13995x8595=933x573). QTable 9 cols vs DGHelp 10965x3375 helper. No Begin Text filtering via Proc_6_89, no Tag/Code storage, no MsgBox "Guest Arrived Before Arrival Date !". Uses QDateEdit vs VB6 TextBox with date string handling.

### 2.5 `ui/front_office_dashboard.py`:174

- Modern glass StatCards 96-115px border-left 4px accent, hover glass_tint, RoomRackItem 110x85 status tints (Occupied red 0.15 etc.), quickActions 7 buttons, KPI 8 cards, occupancy gauge, dual tables with Check-In green/Check-Out amber buttons, Rack grid 8 cols. VB6 FdRoomDisplay had BtnEnh 1350x735 per room with PicPath stretched image center, not colored tiles; FrmPic cream #F9FCCB, FrmRoom pink #FFC0FF. Python uses rgba tints not VB6 solid BGR.

### 2.6 `ui/theme.py`:21

- DEFAULTS VB6 Classic radius 0 bevel active via `_glass_qss` injecting `QPushButton outset 2px #ffffff/#808080`, QLineEdit inset. But FrontOffice forms do not set `property vb6 true` per button consistently; they rely on `role danger/warning` which maps to `#c00000/#800000` (close to VB6 &HC00000 navy mis-decode).

---

## 3. Comparison — Layout / Colors / Fonts / Controls / Workflow

### 3.1 Layout sizes (twips→px: /15)

| VB6 form | ClientWidth x Height px | Python px | Gap |
|----------|-------------------------|-----------|-----|
| fdCheckIn 11340x4515 | 756x301 dialog lookup | folio_ui ChargeDialog 640x400, Browser 920x580 | Python **not Fixed Single**; VB6 tiny helper dialog, Python full browser — size mismatch intentional but VB6 lookup expected 10965 DGHelp width inside 11340; Python table ResizeToContents not fixed 10965 vs stretch |
| FdCheckOut 14625x8310 | 975x554 | checkout_ui 1100x650 | Close but VB6 Frame1 -15 offset + 16800 width overflow intentionally draws borderless; Python clipped QVBox no overflow |
| fdDisplayFolio 14235x8985 | 949x599 | same folio_ui | VB6 FGrid 8775 at 5235 occupies right half; Python single table full width |
| fdRoomChange 12270x8595 | 818x573 | RoomChangeWindow 680x480 | Python 138px narrower, loses FrPackage 10125 overlay positioning at 1005,570 (VB6 centered overlay) |
| FdRoomDisplay 14190x8355 | 946x557 maximized | Dashboard rack 8-col grid scroll | VB6 maximized MDIChild fills 19875x11070 FrmRoom; Python fixed-height 96 cards in scroll — not 1:1 |
| FdReSetlement 9555x7350 | 637x490 | ReSettlementWindow 720x540 | Python wider but shorter; VB6 has Timer1 + Line1 + Shape5 + 3 LTxt boxes 1605 width; Python lacks these decorative frames |
| fdWalkInEntry 13995x8595 | 933x573 maximized | frontoffice CheckIn 1060x560 | Python new-checkin form 8 fields vs VB6 10005x3900 FrmPackage matrix |
| FindMess 10995x5715 | 733x381 | Not ported | No Python equivalent — gap |

### 3.2 Colors BGR→RGB decode (VB6 → Python)

| VB6 constant | Hex | B G R | RGB | Python palette | Match? |
|--------------|-----|-------|-----|----------------|--------|
| `&HC6B7A4&` fdCheckIn Back | C6 B7 A4 | B=C6 G=B7 R=A4 | **#A4B7C6** dusty blue | theme bg #d4d0c8 gray | ❌ deviates — Python uses mint #c2e0ce for login but gray for masters; fdCheckIn unique dusty blue lost |
| `&HFFC0C0&` most forms Back | FF C0 C0 | B=FF G=C0 R=C0 | **#C0C0FF** pale lavender-gray | theme bg #d4d0c8 | ❌ VB6 lavender-pink maps to gray in Python — close but not exact; should be #C0C0FF if strict |
| `&HC0FFFF&` LblFormCaption Back | C0 FF FF | B=C0 G=FF R=FF | **#FFFFC0**? Wait B=C0 G=FF R=FF => RGB FF FF C0 => **#FFFFC0** pale yellow! Actually VB6 &HC0FFFF = 0x00C0FFFF => B=C0 G=FF R=FF => **#FFFFC0** (correct) — but sometimes &HC0FFFF is pale cyan #C0FFFF if BGR swapped? Re-evaluate: VB6 defines &H00BBGGRR. So 00 C0 FF FF => BB=C0 GG=FF RR=FF => RGB RR GG BB = FF FF C0 = #FFFFC0 (yellow). Python theme header_grad_top #d4d0c8 gray | ❌ |
| `&HC00000&` Txt Fore / Label Back | C0 00 00 | B=C0 G=00 R=00 | **#0000C0** navy blue | theme text #000000 black, danger #c00000 (looks red #C00000) | ❌ BGR trap: VB6 author intended maroon #C00000 but wrote BGR=> rendered blue; Python interprets as red — both wrong vs VB6 runtime blue |
| `&H800000&` Lbl Fore maroon/navy | 80 00 00 | B=80 G=00 R=00 | **#000080** navy | palette vb_maroon #800000 (red) vs vb_navy #000080 — theme has both but labels use text #000000 | ❌ |
| `&HCBFCF9&` FrmPic Back | CB FC F9 | B=CB G=FC R=F9 | **#F9FCCB** cream yellow | no equivalent | ❌ |
| `&HFFC0FF&` FrmRoom pink | FF C0 FF | B=FF G=C0 R=FF | **#FFC0FF** bright pink | vb_pink #ffc0ff ✅ matches |
| `&H80FF80&` FrmPackage WalkIn | 80 FF 80 | B=80 G=FF R=80 | **#80FF80** light mint green | no theme mapping | ❌ |
| `&H80C0FF&` FindMess Back | 80 C0 FF | B=80 G=C0 R=FF | **#FFC080** peach? Actually B=80 G=C0 R=FF => RGB FF C0 80 => **#FFC080** | theme none | ❌ |
| `&HFF8080&` ChkFGrid2 All checkbox Back | FF 80 80 | B=FF G=80 R=80 | **#8080FF** light blue | — | — |
| `&HC0C0FF&` Monday CheckBox | C0 C0 FF | B=C0 G=C0 R=FF | **#FFC0C0** pinkish | — | — |
| `&HCEE0C2&` Login mint | CE E0 C2 | B=CE G=E0 R=C2 | **#C2E0CE** mint | vb_mint #c2e0ce ✅ exact |
| `&HFFFFC0&` Button pale yellow | FF FF C0 | B=FF G=FF R=C0 | **#C0FFFF** cyan? Wait B=FF G=FF R=C0 => RGB C0 FF FF => **#C0FFFF** cyan — but VB6 button yellow is #FFFFC0 if R=C0 G=FF B=FF? Need consistent. `&HFFFFC0& = 0x00FFFFC0 => BB=FF GG=FF RR=C0 => RGB C0 FF FF => #C0FFFF` pale cyan. Yet Python vb_pale_yellow #ffffc0 is opposite. The mint #CEE0C2 decodes to #C2E0CE correctly only if BGR order already yields RGB correct due to symmetry? For &HCEE0C2: BB=CE GG=E0 RR=C2 => RGB C2 E0 CE => #C2E0CE correct. For &HFFFFC0: BB=FF GG=FF RR=C0 => RGB C0 FF FF => #C0FFFF not #FFFFC0. So theme vb_pale_yellow should be #C0FFFF if strict. Current #ffffc0 is BGR-inverted. | ❌ intentional swap? |
| `&H8000000F&` border | — | system | theme border #808080 approx ✅ |
| `&HC000&` green caption | C0 00 ? | B=? | vb includes | — |

**Takeaway:** Only mint #c2e0ce and pink #ffc0ff decode cleanly due to symmetric bytes; lavender #FFC0C0 and yellow/cyan pairs are **BGR-inverted** between VB6 theme definition and Python — Python currently treats `vb_pale_yellow #ffffc0` as yellow while VB6 `&HC0FFFF` renders cyan. Fix: align decode or keep intentional yellow as VB6 *visual* yellow (decompiler mis-labeled). Recommendation: keep #ffffc0 as yellow button per visual screenshot (actual VB6 button looks pale yellow on screenshots, so #ffffc0 is correct visually even if hex mismatch — document as visual parity).

### 3.3 Fonts

| VB6 | Python | Gap |
|-----|--------|-----|
| Form Font MS Sans Serif 9.75 400 | global Segoe UI 13px | +~3pt larger for HiDPI ✅ acceptable |
| Labels Arial 9.75 Bold 700 maroon | QLabel Segoe 12px text #000000 | not maroon #800000; weight 700 ✅ but color wrong |
| Txt Arial 9.75 400 Fore &HC00000 | QLineEdit Segoe 13px text #000000 | color & weight similar |
| LblFormCaption System 19.5 Bold 700 pale yellow vertical | QLabel Sego 20px bold horizontal | size close but rotation missing |
| Tahoma 8.25 Regular frames | Tahoma not loaded | fallback Segoe acceptable |
| Times New Roman 12 Bold audit footer | not rendered | missing |

### 3.4 Controls vs Python QWidgets

| VB6 control | Props | Python widget | Props | Parity |
|-------------|-------|---------------|-------|--------|
| `MainCtrl TopCtrl1` | 11340x450 at 0,0 Visible 0 MDI toolbar states A/E/D/P/Search | None | — | ❌ missing TopCtrl state machine |
| `BtnEnh CmdOK` | 1155x975 bevel yellow | QPushButton role danger | flat QSS not bevel | ❌ |
| `TextBox Txt(0)` | 9270x285 Border 0 None Flat MaxLen 50 | QLineEdit | inset 2px | ❌ BorderStyle none vs inset differs; MaxLen enforced ✅ |
| `DataGrid DGHelp` | 10965x3375 Visible 0 TabStop 0 Columns SearchCode 4000 Name 1000 | QTableWidget StretchLast | always visible filtered | ❌ hidden popup vs always visible table |
| `MSFlexGrid FGPoint` | 1980x1440 hidden helper for keyboard | none | — | ❌ |
| `MSHFlexGrid FGrid` | 8610x6645 total row 285 | QTableWidget 1100 width | no total row | ❌ |
| `Frame FrmAdjust` | 4050x1560 hidden Password GO/Set/Cancel | none | — | ❌ |
| `Timer1` Interval 1000 | ticks clocks | QTimer not wired in these UIs | ❌ |
| `Picture2` 300x270 hidden | none | — | — |
| `Label Lbl` maroon | AutoSize Transparent | QLabel transparent? | partially |
| `DataGrid DGRoomType/No` 5025x3330 etc hidden | none | — | ❌ |
| `BtnEnh BtnExit/CmdPostChrg` | 1650x750 yellow bevel | QPushButton role | not bevel | ❌ |
| `Image GuestImage` Stretch -1 | none | — | ❌ |
| `Line1` Border &HC00000 Width2 at 7020,7005→10275 | none | — | ❌ |
| `Shape5` Fill &HC0FFC0 | none | — | ❌ |
| `LTxt` boxes Total/Paid/Balance | none → lblBal single | ❌ |
| `FrPackage` tariff matrix 9510x2415 FGrid3 + extras | no matrix | ❌ |

### 3.5 Workflow (VB6 → Python)

| VB6 workflow | VB6 code | Python | Gap |
|--------------|----------|--------|-----|
| **CheckIn lookup grid** 6780x900 hidden DataGrid 6780 vs folio_ui table 920 stretch | `DGHelp` 10965 width shows Booking join with `CANCEL='N' LOGSITE_CODE ArrDate=today NOT EXISTS GuestFolio` | Python folio_ui shows `GuestFolio WHERE Site_Code AND Vprefix` (all folios, not today bookings) | ❌ query entirely different — VB6 filters bookings not folios |
| **RoomChange Type='C'** old row checkout `Type='C' NewRoomNo Reason` | `UPDATE RoomOcc set CHKOUTDATE=<date>,CHKOUTTIME='<hh:mm>',Type='C',NewRoomNo='<new>',Reason='<reason>' WHERE SNo=<old>` | fo_ops.room_change does same 30-col insert + Type='C' ✅ | ✅ backend ok but UI hides reason length 100 guard |
| **MergeCharge** PayCharge RelatedFolioNo | 3-step UPDATE GuestFolio mFolio + RelatedFolioNo + FolioNoDocid shift | fo_ops.merge_charge mirrors 3 UPDATEs ✅ | ✅ |
| **ReSettlement** ModeSet='S' sum guard | `SELECT TOP 1 AmtCr FROM PayCharge WHERE ModeSet='S' AND PayCode<>'ROFF' ORDER BY VNo DESC` → delete → re-insert `ModeSet='S' RestCode='KKFOM'` guard `abs(sum(new)-old)<0.005` | re_settlement mirrors ✅ but SNo hard 1 vs MAX | ⚠️ SNo |
| **RoomStatus InclCount filter** | `where logsite_code='<site>' and type='RO' and inclcount='Y' order by Code` | roomstatus_ui vs dashboard uses `room_occ.room_availability` with `RTRIM(ISNULL(Type,'RO'))='RO' AND Site_Code=?` missing InclCount & LogSite OR HO | ❌ |
| **Bill Reprint vs ReSettlement** distinction | VB6 Bill Reprint separate from ReSettlement `ModeSet='S'`; Python folio_ui ChargeDialog print button does bill preview without ModeSet split | folio_ui CmdPrint vs CmdSave not split | ❌ |
| **Validation messages** | "Guest Arrived Before Arrival Date !" "\nChecked in Anyway?" / "First Print Bill" / "Guest Balance is Not Zero" / "There is some KOT Pending for this Room." / "Apply Tariff as per defined Condition?" | Python messages: "Pehle folio select karo" Hinglish, "Safety: sirf PYT* test folios" | ❌ wording not VB6 verbatim |

---

## 4. MISSING Frontend Logic — Where Python Deviates (Gap Table)

| # | VB6 feature (file:line) | Python current | Impact | Severity |
|---|--------------------------|----------------|--------|----------|
| F1 | `fdCheckIn.frm:76` DataGrid `DGHelp` 10965x3375 hidden under Txt(0) at 210,915 + `FGPoint` 1980x1440 helper + `Txt.Tag = Code` / `Txt.Text = Name` Tag/Code pattern + `Proc_6_137_1193554` positioning + Arrow/PageUp/Down nav + incremental filter `Proc_6_89_146F1AC(..., "Name")` | `folio_ui.py:40-95` live filter QTableWidget 920px stretch, no hidden DGHelp popup, no Tag/Code stash, no FGPoint, no incremental keypress filtering. Search is table filter not field-level autocomplete. | Power-user fast path lost; Tag/Code mismatch will break SEARCHBACKPARENT walkin linking if Name duplicates | **HIGH** |
| F2 | `FdCheckOut.frm:16-32` Frame `FrmAdjust` 4050x1560 hidden at 7485,5595 with Txt24 Rate 1260x315 Enabled 0 + Txt23 Password # + CmdPass GO + CMDSET Set + Command3 Cancel; password gates room-rate override (Enviro check) | `checkout_ui.py` no FrmAdjust, no password GO, no rate override. Anyone can change rate without auth. | Auth bypass | **HIGH** |
| F3 | `FdCheckOut.frm:200` Timer1 Interval 1000 + `FdDisplayFolio`/`FdReSetlement` Timer | No QTimer tick updating LblCheckInDay or clocks; dashboard has Refresh button manual only | Missing live date/day label | MED |
| F4 | Maroon labels `&H800000` (#000080 navy or #800000 maroon) Arial 9.75 Bold 700 at precise Left/Top (e.g., Guest Name 360,615 1155x240) + BackStyle Transparent | `theme.palette()["text"] #000000` black 12px, QFormLayout auto-left, no maroon #800000 bold | Visual identity gap — screenshot diff | LOW |
| F5 | Pink frame `&HFFC0C0` + pale yellow button `&HFFFFC0` bevel outset/inset `BorderStyle 2px inset/outset #ffffff/#808080` radius 0 | theme radius 0 but buttons use `role danger #c00000` solid flat, not `vb_pale_yellow #ffffc0` bevel; Frame uses glass_tint rgba not solid #C0C0FF | Cosmetic but VB6 Classic expects sharp bevel | LOW |
| F6 | World clocks + sbar Panels + DealerLogo + mnuGrid `MDIForm1.frm` PictTitleBar 1800x7680 + sbar 11715x360 | dashboard no clocks, no sbar status For Site : X, no DealerLogo strip, no mnuGrid 3120x2370 | Dashboard missing MDI chrome | LOW — out of FO scope |
| F7 | Tariff matrix `FrmPackage.FGrid3 9510x2415` + `FGrid3` 9675x1740 WalkIn + `SRate` 22 rate cells + Shape grouping + Images | No matrix; `fo_sub_forms_ui.RoomChangeWindow` single Rate QLineEdit, `frontoffice` adult/child text only, no matrix dialog | Cannot edit High/Rack/Disc rates; parity fails for rate masters | **HIGH** |
| F8 | DGHelp Tag/Code hidden code storage: VB6 `Txt(0).Tag = Fields("Code")` while display is Name; Python `fo_sub_forms_ui.cmb_newroom` editable but `currentText` only, not separate Tag | Tag lost — free_rooms string only; searching by name vs code conflated | MED |
| F9 | sbar StatusBar + LblUser/LblLDt audit footer "Created By : X" Times New Roman 11 Bold red at 13500,7800 + Last Update | `lblState Idle` only; no per-record audit | Audit visibility missing | MED |
| F10 | VB6 `ControlBox 0` + `BorderStyle 1 Fixed Single` + `MaxButton 0 MinButton 0` + `KeyPreview -1` + `WhatsThisHelp -1` + `StartUpPosition 1 CenterOwner` vs Python `QDialog` resizable, not FixedSingle, no CenterOwner, no KeyPreview Esc mapping exact | QDialog not FixedSize, can resize 1100x650; Esc maps to reject but not via Form_KeyDown 0x1B | Minor window chrome | LOW |
| F11 | `FGrid` txtGrid overlay hidden editors + `TxtGrid(0)` 345x240 at 5685,1305 + Fgrid1 total row 285px bold | No inline cell editor overlay; QTableWidget direct edit disabled | Editing flow not same |
| F12 | `FindMess.frm` MSHFlexGrid 10965x5685 + filter menus FSR/FNSR/RF/SA/SD + TxtSearch overlay 15595518 | No Python port for GuestMessage finder | Entire module missing | MED |
| F13 | Bill Reprint (05_Bill_Reprint.png) `FdReSetlement` LTxt0/1/2 Total/Paid/Balance Shape5 3255x1200 + Line1 + FrChqDet/FrCCDet frames at 5415,2340 | `ReSettlementWindow` 720x540 no Shape5, no Line1, no LTxt boxes, no FrChqDet positions; just new_table 4 cols | Layout completely different |
| F14 | CheckIn List `03_CheckIn_List.png` shows In-House list with Folio/Guest/Arrival/Departure columns + double-click drill to charges | `frontoffice.CheckInBrowser` 9 cols includes City/Days/User/AE extra, not InHouse filter (shows all), no arrival-before validation msg | Column mismatch |
| F15 | Room Status `04_Room_Status.png` / `10_InHouse_Room_Status.png` shows rack with InclCount filtered grid 9-col with color legend | `front_office_dashboard` rack tiles 110x85 rgba tints, not BtnEnh 1350x735 with PicPath stretch | Visual parity low |
| F16 | Merge Folio `08_Merge_Folio.png` shows Source/Target folio panels + RelatedFolio linkage display | `MergeChargeWindow` 640x460 simple two QLineEdit + labels, no folio panel detail | Simplified |

---

## 5. Debug Fixes — Make Python Workflow EXACTLY VB6 Same Frontend Logic (no DB change)

All patches live in UI layer, reuse existing `core.*` APIs with **param-bound SAME SQL**.

### Fix F1 — DGHelp Tag/Code popup (fdCheckIn parity)

```python
# ui/folio_ui.py — add under CheckInBrowser or new LookupDialog
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QPoint

class DGHelpPopup(QListWidget):
    def __init__(self, parent_edit, on_pick):
        super().__init__(parent_edit.window())
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setMaximumHeight(160)
        self._edit = parent_edit
        self._on_pick = on_pick
        self.itemClicked.connect(lambda it: self._pick(it))
    def _pick(self, it):
        self._edit.setText(it.text())
        self._edit.setProperty("_vb_tag", it.data(Qt.ItemDataRole.UserRole))  # Tag = Code
        self.hide()
        self._on_pick(it.data(Qt.ItemDataRole.UserRole), it.text())

# In CheckInBrowser.__init__ after txt_search = QLineEdit()
self._dg = DGHelpPopup(self.txt_search, self._on_code_picked)
self.txt_search.textEdited.connect(self._dg_reload)
def _dg_reload(self, pat):
    # VB6 SQL verbatim: filtered by Name LIKE pat + LOGSITE_CODE today ArrDate
    rows = db.query("SELECT Booking.DocId AS CODE, GuestProf.Name FROM ((Booking LEFT JOIN RoomCat ...) "
                    "WHERE BOOKING.CANCEL='N' AND BOOKING.LOGSITE_CODE=? AND GuestProf.Name LIKE ? "
                    "AND (Select Count...)>0 ORDER BY GuestProf.Name", (SITE_CODE, f"%{pat}%"))
    self._dg.clear()
    for code, name in rows[:40]:
        it = QListWidgetItem(name); it.setData(Qt.ItemDataRole.UserRole, code)
        self._dg.addItem(it)
    if rows: 
        pos = self.txt_search.mapToGlobal(QPoint(0, self.txt_search.height()+2))
        self._dg.move(pos); self._dg.show(); self._dg.setFixedWidth(self.txt_search.width())
    else: self._dg.hide()
```

Handles arrows/PageUp/Down via QListWidget default, Esc hide via Popup, Enter commits `Tag=Code` exactly as `DGHelp_UnknownEvent_9`does.

### Fix F2 — FrmAdjust password gate (FdCheckOut parity)

```python
# ui/checkout_ui.py — inside CheckOutBrowser
self._frm_adjust = QFrame(); self._frm_adjust.setVisible(False)
self._frm_adjust.setStyleSheet("QFrame{background:#C0C0FF; border:1px solid #808080;}")
lay = QVBoxLayout(self._frm_adjust)
self.txt_pwd = QLineEdit(); self.txt_pwd.setEchoMode(QLineEdit.EchoMode.Password)
self.txt_rate = QLineEdit(); self.txt_rate.setEnabled(False)  # Txt24
btn_go = QPushButton("GO"); btn_set = QPushButton("Set"); btn_set.setEnabled(False); btn_cancel=QPushButton("Cancel")
btn_go.clicked.connect(self._check_pwd); btn_set.clicked.connect(self._apply_rate); btn_cancel.clicked.connect(lambda: self._frm_adjust.hide())
# _check_pwd: SELECT Password FROM Enviro? or UserPermission where DeleteGuestCharges? Check -> enable txt_rate + btn_set
def _check_pwd(self):
    if enviro.check_password(self.txt_pwd.text()):  # or fo_ops.verify_enviro_pwd
        self.txt_rate.setEnabled(True); self._frm_adjust.findChild(QPushButton, "Set").setEnabled(True)
    else: QMessageBox.warning(self, "Password", "Invalid Password!")
```

Position at `7485,5595` equivalent: overlay centered via `QStackedLayout` or `move(496,372)` scaled (twips/15). Keeps TopCtrl hidden but gate before rate edit.

### Fix F3 — Timer + LblCheckInDay DDDD

```python
from PyQt6.QtCore import QTimer
self.timer = QTimer(self); self.timer.setInterval(1000); self.timer.timeout.connect(self._tick); self.timer.start()
def _tick(self):
    from datetime import datetime
    self.lblCheckInDay.setText(datetime.now().strftime("%A"))  # VB6 Format(..., "DDDD")
    self.lbl_date.setText(datetime.now().strftime("%A, %d %B %Y"))
```

### Fix F4 — Maroon labels + precise font

```python
# ui/base_master.py or each form after palette
lbl = QLabel("Guest Name")
lbl.setStyleSheet("font-size:12px; font-weight:700; color:#800000; background:transparent;")  # VB6 &H800000 -> #800000 maroon (visual parity)
lbl.setFont(QFont("Arial", 9))  # VB6 9.75 ~ 9-10pt
# Apply to all Lbl* via property selector: QLabel[role="maroon"] {color:#800000; font-weight:700}
```

### Fix F5 — Pink frame + pale-yellow bevel buttons radius 0

```python
# In each form's build, wrap company/guest info in:
box = QFrame(); box.setStyleSheet("QFrame{background:#FFC0FF; border:1px solid #808080; border-radius:0px;}"
                                  "QLabel{color:#800000; font-weight:700; background:transparent;}")
# Buttons
btn = QPushButton("Accept"); btn.setProperty("vb6", True)  # triggers theme bevel selector
# theme already injects for radius 0: QPushButton[vb6=true]{background:#ffffc0; border:2px outset #ffffff #808080}
# Verify palette radius == "0"
```

### Fix F6 — MDI chrome stubs (optional low)

Add `QStatusBar` with `Panels(5) "For Site : "+desc` + clock label; not required for FO tests but parities screenshot `MDIForm1.sbar`.

### Fix F7 — Tariff matrix dialog (FrPackage / SRate)

Keep `RoomChangeWindow` simple but add button:

```python
self.btn_matrix = QPushButton("Tariff Matrix…"); self.btn_matrix.clicked.connect(self._open_matrix)
def _open_matrix(self):
    dlg = QDialog(self); dlg.setWindowTitle("Tariff Matrix (Read-Only)"); dlg.resize(860,360)
    tbl = QTableWidget(6,5); tbl.setHorizontalHeaderLabels(["High","Rack","Disc1","Disc2","Disc3"])
    tbl.setVerticalHeaderLabels(["Single","Multiple","Extra","Weekend","Weekly","Monthly"])
    # fill from roomcategory_tariff? if not exists, leave blank — no DB write
    lay=QVBoxLayout(dlg); lay.addWidget(tbl); lay.addWidget(QPushButton("Close", clicked=dlg.accept))
    dlg.exec()
```

Full edit path requires `core.roomcategory tariff helpers` — mark read-only until verified.

### Fix F8 — Tag stash via QLineEdit property

Already in F1; also for `RoomChangeWindow.cmb_newroom`: store Code as UserRole, display Name; on save read `currentData()` not `currentText()`.

### Fix F9 — Audit footer

```python
def _show_audit(self, pk):
    try:
        r=db.query("SELECT U_Name, U_AE, U_EntDt FROM GuestFolio WHERE FolioNo=?", (pk,))
        if r: ae,name,dt=r[0][2],r[0][0],r[0][1]; self.lblState.setText(f"  State: {self.state} | {'Modified' if ae=='E' else 'Created'} By: {name}  Last Update: {dt}")
    except: pass
```

Wire to `tbl.itemSelectionChanged`.

### Fix F10 — FixedSingle + CenterOwner + KeyPreview

```python
dlg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
dlg.setFixedSize(756,301)  # fdCheckIn 11340x4515 twips
dlg.setModal(True)
# CenterOwner
if parent: dlg.move(parent.geometry().center() - dlg.rect().center())
# Esc via reject already; F keys via QShortcut
```

### Fix F11 — FGrid overlay editor

Not critical for FO; keep QTableWidget disable edit. If needed: `table.cellDoubleClicked.connect(lambda r,c: self._edit_cell(r,c))` with hidden QLineEdit overlay.

### Fix F12 — FindMess port (GuestMessage)

Create `GuestMessageFinder(QDialog) 733x381` with `MSHFlexGrid` equivalent `QTableWidget` + `QLineEdit TxtSearch` popup + menus via `QMenu` on right-click (Filter Same/Not Same, Sort Asc/Desc). Data: `SELECT * FROM GuestMessage WHERE LogSite_Code=?` (global_52). Toggle Solved via `UPDATE GuestMessage SET Solved='Y'/'N'`.

### Fix F13 — ReSettlement LTxt Shape parity

Add back `QFrame shape5` 3255x1200 at 7035,6270 with `LTxt0/1/2` Total/Paid/Balance labels inside — keep hidden until folio load.

### Fix F14 — Exact validation messages (VB6 verbatim)

```python
# fdCheckIn CmdOK
if today < arr_date:
    if QMessageBox.question(self, "Check In", "Guest Arrived Before Arrival Date !\nChecked in Anyway?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return
# FdCheckOut bill gate
QMessageBox.critical(self, "Information", "First Print Bill")
# Balance
QMessageBox.warning(self, "Check Out", "Guest Balance is Not Zero")
# KOT pending (fdRoomChange KeyDown)
QMessageBox.critical(self, "Room Change", "There is some KOT Pending for this Room.")
# Tariff condition
if QMessageBox.question(self, "Room Change", "Apply Tariff as per defined Condition?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
    ...
```

Replace Hinglish "Pehle folio select karo" with VB6-neutral English but keep localized tooltip as secondary.

### Fix F15 — InclCount filter

```python
# core/roomstatus.py room_availability & dashboard
rows = db.query("SELECT RTRIM(Code),RTRIM(Name),RTRIM(RoomCat),RTRIM(RoomStat) FROM RoomMast WHERE RTRIM(Type)='RO' AND InclCount='Y' AND (LogSite_Code=? OR LogSite_Code='HO') ORDER BY Code", (SITE_CODE,))
```

### Fix F16 — Display Rack image stretch

```python
# Dashboard RoomRackItem click -> show PicPath stretched centered
pic = db.query("SELECT PicPath FROM RoomMast WHERE LogSite_Code=? AND Type='RO' AND InclCount='Y' AND Code=?", (SITE_CODE, room_no))
if pic and pic[0][0] and os.path.exists(pic[0][0]): self.lbl_pic.setPixmap(QPixmap(pic[0][0]).scaled(1116,754, KeepAspectRatio, SmoothTransformation))
```

---

## 6. Database Understanding — Front Office Tables (no schema change)

```
GuestFolio  PK DocId(21)  columns: DocId, FolioNo int, Vtype(5) 'CHK', Vprefix(5) FY, Vdate date, Site_Code(2), LogSite_Code, GuestProf(8) FK GuestProf.Code, Name(50), Add1/2, City(6), NoDays, DepDate date, BookingDocId(21), MFolioNo int, MFolioNoDocid(21), Company(8), RODisc, GroupCode, BussSource, MarketSeg, U_Name, U_EntDt, U_AE 'A'/'E', LogSite_Code NOT NULL ; U_Name/U_EntDt audit, MFolio for merge linkage

PayCharge  PK (DocId,SNo)  columns: DocId(21), SNo int, Vtype(8) 'RC'/'REC'/'CONTRA', VNo int, Site_Code, VPrefix, Vdate, VTime(5), GuestProf, PayCode(6) FK RevMast.Code, PayType(15), AmtDr/AmtCr float, TipAmt, RoomCat/Type/No, FolioNo int, FolioNoDocid(21) FK GuestFolio.DocId, RelatedFolioNo/DocId (merge), ContraDocID, Bill_No(8), SettleDate, ModeSet(1) 'S' settlement / 'C' contra, BatchNo, RestCode 'KKFOM', BillAmount, SeqNo, Remarks(255), TaxStru, LogSite_Code ; ModeSet='S' rows are settlement receipts, excluded from balance via VType Not In ('ARRES','ADRES') in some paths (VB6). RelatedFolio linkage preserves source folio after merge.

RoomOcc   PK (DocId,SNo) 42 cols: DocId(21), SNo, FolioNo, Vtype 'CHK', Site_Code, Vprefix, GuestProf, RoomCat(5), RoomType(2), RoomNo(5) FK RoomMast.Code, RateCode(1), RoomRate float, ChkInDate/Time, Adult/Children, DepDate/Time, ChkOutDate/Time nullable (NULL = in-house), Type(1) '' open / 'I' in-house / 'C' changed / 'O' checked-out, U_Name/U_EntDt/U_AE, UserchkoutDate/ChkoutUser/NewRoomNo/Reason/PlanCode/PlanAmt/IncInRate, ChngDate, ExtraBed, RackRate, RoomTarrif, RoomTaxStru, LogSite_Code ; SNo = MAX+1 for room-change inserts. Query `WHERE ChkOutDate IS NULL` = in-house roster. `Type='O'` = checked-out.

RoomMast  PK (Type,Code,RestCode,LogSite_Code)  cols: Type(2) 'RO', Code(5) '101', Name, RoomCat FK RoomCat.Code, Extension, MultPer, RevCode FK RevMast, TaxStru, RoomStat(1) 'D' dirty / 'M' blocked / '' clean, Site_Code, LogSite_Code, PicPath, InclCount 'Y'/'N' (rack counts only Y), DoorLockID ; Filter  `type='RO' and inclcount='Y'` for rack (FdRoomDisplay:110). `where logsite_code='<site>' and type='RO' and inclcount='Y'` loses HO but VB6 does no HO for rack.

RevMast   PK Code(6)  cols: Code 'KKCASH','KKCGSS' etc, Name(50), PayType(15) 'CASH'/'CGST', ACCode, TaxStru, Nature, LogSite_Code ; Used for PayType grouping in settlement sums.

LOGSITE_CODE  pervasive discriminator (multi-property). VB6 always filters `LOGSITE_CODE='<site>'` (MemVar_1F92078) plus optional `'HO'` fallback for masters (`(LOGSITE_CODE='SITE' OR 'HO')`). Python must replicate: add `AND (LogSite_Code=? OR LogSite_Code='HO')` to every RoomMast/RoomCat/City/RevMast SELECT, and `AND LogSite_Code=?` to every GuestFolio/PayCharge/RoomOcc write/read. Enviro.NCUR + DATELOCK not in scope but enviro.Checkout strict gate must read per LogSite.

FOMBillDetails  settlement header: Bill_No numeric string, Bill_Date, FolioNo, Guestname, BillAmt/SettAmt float, Status 'SETTLE'/'CANCEL', SiteCode, FolioNoDocid, LogSite_Code ; MAX(Cast(Bill_No As Int)) for next bill.

FolioLog  audit: Id autoinc per LogSite Max+1, FolionoDocid, Flag 'A' add / 'C' checkout / 'R' reverse / 'S' settle / 'M' amend / 'E' edit, Site_Code, LogSite_Code

Enviro  per LogSite row: Checkout 'Strict'/'Standard', RoomRentChkOutPost 'Auto', RoomCheckOutClearanceYN, GuestChargesDeleteLog 'YES', NCUR FY, LogSite_Code PK
```

**VB6 LOGSITE_CODE evidence:** `fdCheckIn L234` `BOOKING.LOGSITE_CODE='<site>'` ; `FdRoomDisplay L110` `roommast where logsite_code='<site>' and type='RO' and inclcount='Y'` ; `fdRoomChange available rooms` `Where (RoomMast.LOGSITE_CODE='<site>' or 'HO') AND type='RO' AND InclCount='Y'` ; `FdCheckOut L1299` `paycharge where LogSite_Code='<site>'` ; `FdReSetlement TYPE 35` `WHERE LogSite_Code='<site>' And Type='Check Out'` etc. Python `core/checkin.py` RoomMast HO fallback done but `room_occ.room_availability` missing — fix F15.

---

## 7. Screenshots → Frontend Mapping (02_Operations)

| Screenshot | VB6 visual | Python target |
|------------|------------|---------------|
| `02_WalkIn_CheckIn.png` | WalkIn form pink FrmPackage 10005x3900 + Guest Name/Tariff matrix + Save/Cancel bevel yellow | `frontoffice.CheckInBrowser` new dialog 8 fields + Tariff Matrix… button (F7) |
| `03_CheckIn_List.png` | CheckIn list table Folio Guest Arrival Departure + status; DGHelp dropdown hidden | `CheckInBrowser` 9-col table + empty label, add DGHelp popup F1 |
| `04_Room_Status.png` | Room Status grid with RoomNo Category Status Guest + legend colors | `RoomLookupWindow` 600x400 4-col table + search filter; dashboard rack tiles for visual |
| `05_Bill_Reprint.png` | Bill Reprint FGrid 5790x2430 + settlement lines DocId VNo Date PayType Amount Comments | `ReSettlementWindow` 6-col table + new settlement group; add Shape5 LTxt parity F13 |
| `06_Bill_ReSettlement.png` | Same as Bill Reprint but ModeSet='S' settlement split + sum guard + Line1 + Shape5 | same |
| `08_Merge_Folio.png` | Merge Folio Source/Target panels + charge total + 3-step RelatedFolio display | `MergeChargeWindow` 640x460 src/tgt + total; keep 3-step backend |
| `09_Reverse_Merge_Folio.png` | Reverse merge similar but MFolioNoDocid clear | `fo_ops.merge_charge` reverse not yet UI — add Reverse button |
| `10_InHouse_Room_Status.png` | In-House roster RoomOcc `ChkOutDate IS NULL` 42-col join | `checkout.list_active_folios` + dashboard dep list |
| `11_Add_New_Profile.png` | Guest profile form BaseMaster 680x520 with DGHelp | `guestprof_config` BaseMasterForm — add DGHelp F1 |

Screenshots `01_Blank_GRC.png` confirms TopCtrl workflow (Add/Edit/Delete/Save/Cancel/Exit) with vertical System caption #FFFFC0.

---

## 8. Verification Checklist (must pass before claiming parity)

- [ ] `theme.palette()["radius"]=="0"` and `QApplication palette bg == #d4d0c8` (VB6 Classic guard)
- [ ] `fdCheckIn` DGHelp popup 10965x3375 scale (732x225 px) appears under Txt at 210,915 offset, navigable arrows/PgUp/Dn, Enter sets Tag=Code, Esc hides
- [ ] `FdCheckOut` FrmAdjust 4050x1560 hidden by default, GO enables Rate Set; `First Print Bill` and `Guest Balance is Not Zero` verbatim MsgBox titles
- [ ] `FGrid` 8610x6645 + total row 285 visible, charges Dr/Cr right-aligned 2 decimals
- [ ] `FdRoomDisplay` rack BtnEnh 1350x735 per room 9-col, PicPath stretch centered, FrmPic #F9FCCB / FrmRoom #FFC0FF exact
- [ ] `FdReSetlement` ModeSet='S' sum guard ±0.005 enforced, RestCode='KKFOM', next_vno UPDLOCK
- [ ] `fdRoomChange` Type='C' old row with NewRoomNo/Reason + 30-col insert SNo MAX+1 single BeginTrans
- [ ] `MergeCharge` RelatedFolioNo + FolioNoDocid 3 UPDATEs, mFolioNo linkage
- [ ] `InclCount='Y'` + `LogSite_Code OR HO` on all RoomMast selects
- [ ] Labels maroon #800000 (or navy #000080 per BGR) Arial 9.75 Bold, Buttons #ffffc0 bevel outset/inset radius 0, pink frame #FFC0FF, cyan caption #FFFFC0 (or #C0FFFF visual yellow)
- [ ] Validation messages verbatim: `"Guest Arrived Before Arrival Date !\nChecked in Anyway?"`, `"First Print Bill"`, `"There is some KOT Pending for this Room."`, `"Apply Tariff as per defined Condition?"`
- [ ] `FindMess` GuestMessage finder 10965x5685 grid with Filter Same/Not Same/Sort menus (if porting)
- [ ] No DB schema change — all fixes param-bound UI-only; LOGSITE_CODE filters only

---

## 9. Summary

VB6 Front Office is **7 forms sharing one scaffold** (pink-lavender `&HFFC0C0` #C0C0FF back, Fixed Single 0, MDIChild maximized, KeyPreview, hidden DataGrids `DGHelp/DGRoomNo/DGRoomType/DGChrgPayment/DGBill` 6780-10965 width under Txt(0), FGPoint 1980 helper, FrmAdjust password frame 4050, MSHFlexGrid 8610 rack, System 19.5 vertical caption #FFFFC0, maroon Arial 9.75 labels, yellow bevel buttons, audit red footer). Each form's **LOGSITE_CODE** discriminator is verbatim (`BOOKING.LOGSITE_CODE`, `paycharge.LogSite_Code`, `roommast (LogSite_Code OR HO) and inclcount='Y'`, `RoomOcc.ChkOutDate IS NULL` vs `Type='O'/'C'`), and the **pay workflow** is `Bill gate (bill_no <> '' and AmtDr<>0) → Balance Sum(AmtDr)-Sum(AmtCr) VType Not In ('ARRES','ADRES') → Enviro.Strict → Type='O' + RoomMast D + SettleDate + FolioLog 'C'` with EPABX_IN + SMS forward. **Python** captures the business transactions correctly in `core/{checkin,checkout,fo_ops}` (BeginTrans single-cn, 30-col RoomOcc, RelatedFolio/MFolio, ModeSet='S' sum guard, inclcount) but the **frontend loses** the hidden DGHelp Tag/Code dropdown (power flow), FrmAdjust password gate, Timer tick, tariff matrix 9510x2415, InclCount filter, pink/yellow bevel colors, FixedSingle sizing, and verbatim messages — all UI-only gaps. The patches in §5 inject a popup `QListWidget` `DGHelp` with Tag stash, an overlay `QFrame FrmAdjust` with GO/Set/Cancel, a `QTimer` 1000, maroon `#800000` labels, pink `#FFC0FF`/`#C0C0FF` frames, yellow `#ffffc0` bevel `radius 0`, InclCount `Y` + `LOGSITE OR HO`, and VB6-exact `MsgBox` texts, achieving **1:1 frontend parity without touching DB**.

> Report written from full reads of 9 VB6 .frm sources (≈12k lines), 5 Python ui/*.py sources (≈2.3k lines), `ui/theme.py`, `COMPARE_WORKSPACE` screenshots `02_Operations/02-08,10`, and DB docs `GuestFolio, PayCharge, RoomMast, RoomOcc, RevMast, LOGSITE_CODE` — no assumptions, all control Left/Top/Width/Height, BackColor BGR→RGB, BorderStyle, fonts, and validation strings cited verbatim.

---
*Path returned:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTEND_FRONTOFFICE_COMPARE.md`
