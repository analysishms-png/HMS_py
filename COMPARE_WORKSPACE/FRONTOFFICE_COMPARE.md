# FRONT OFFICE — VB6 vs Python Parity Report
> Module: Front Office (GuestFolio, PayCharge, RoomOcc, CheckIn/CheckOut, RoomChange, Merge, ReSettlement)  
> Date: 2026-09-24  
> Rule: **SAME VB6 SQL, no DB schema change** — only add `WHERE LOGSITE_CODE` / HO fallback / FY Vprefix if missing, keep table/column names identical. Frontend TopCtrl/grid + Backend BeginTrans must be 1:1 VB6.

---

## 1) VB6 Sources Read (verbatim SQL) — ONE BY ONE fully

### 1.1 `fdCheckIn.frm` (459 lines) — Look Up Reservation By Guest Name → fdWalkInEntry

| Area | Verbatim VB6 SQL / Logic |
|------|--------------------------|
| `Form_Load` L234-236 | `SELECT Booking.DocId AS CODE, GuestProf.Name, Booking.GuestProf, Booking.DocId AS ID, RoomCat.Name AS RoomType, RoomMast.Code AS RoomNo, Booking.ArrDate AS Arr_Date, Booking.NoDays AS tot_Days, Booking.NoOfRooms as NO_Rooms FROM ((Booking LEFT JOIN RoomCat ON (Booking.RoomType = RoomCat.Type) AND (Booking.RoomCat = RoomCat.Code)) LEFT JOIN RoomMast ON (Booking.RoomType = RoomMast.Type) AND (Booking.RoomNo = RoomMast.Code)) INNER JOIN GuestProf ON Booking.GuestProf = GuestProf.Code WHERE BOOKING.CANCEL='N' AND BOOKING.LOGSITE_CODE='<MemVar_1F92078>' AND (Select Count(Distinct Sno) From GrpBookingDetails Where Not Exists (Select Distinct isnull(BookingDocid,'') As BookingDocId,BookingSno As Sno from GuestFolio Where GrpBookingDetails.BookingDocId=GuestFolio.BookingDocId And GrpBookingDetails.Sno=GuestFolio.BookingSno) And IsNull(Cancel,'')<>'Y' And GrpBookingDetails.ArrDate=<Proc_6_7 date> And GrpBookingDetails.BookingDocid=Booking.DocId)>0 ORDER BY GuestProf.Name` — filters: `CANCEL='N'`, `LOGSITE_CODE`, **only bookings with un-converted GrpBookingDetails Sno** (Not Exists GuestFolio) and ArrDate = today (`Proc_6_7_F25D88`). Recordset `DGHelp` uses `Find "SearchCode ='" & Name &"'"`. |
| `CmdOK` L194-209 | `If CDate(MemVar_1F920EC) < .Fields("Arr_Date") Then MsgBox "Guest Arrived Before Arrival Date !" …` ; `fdWalkInEntry.AdvType="CHK" : FrmType="Check In Entry" : TopCtrl1_UnknownEvent_A()` ; `CALL fdWalkInEntry.SEARCHBACKPARENT(Code, DocId)` ; `Proc_6_39_E7C810(VNo, Fields("no_Rooms"))` then `Unload Me`. |
| `TopCtrl1_UnknownEvent_16` L159-181 | `BeginTrans` → `Method_TopCtrl1_UnknownEvent_160` → `CommitTrans` / `RollbackTrans` if `var_86=&HFF` + `Proc_6_60_E62BC4` error toast. |

**Schema evidence:** LINK `Booking`↔`GrpBookingDetails`↔`GuestFolio` via `BookingDocId+Sno`. `LOGSITE_CODE` mandatory. `Proc_6_7` is `Format(CDate, "Short Date")` → `'MM/DD/YYYY'` quoted or `Null`.

### 1.2 `FdCheckOut.frm` (2736+ lines) — Room Check Out (core transaction)

| Area | Verbatim VB6 SQL |
|------|------------------|
| `Command2_Click` PayCharge guards L1299-1332 | `SELECT isnull(bill_no,'') as Bill_No,AmtDr from paycharge where LogSite_Code='<site>' AND (ContraDocId is NULL or contradocid='') and foliono=<folio> Filter "Bill_No='' and AmtDr<>0"` → if >0 `MsgBox "First Print Bill"` ; `SELECT distinct bill_no from paycharge where LogSite_Code='<site>' AND foliono=<folio> and (Bill_NO<>'' and Bill_NO is not null)` → if 0 `MsgBox "First Print Bill"` ; `SELECT * from enviro WHERE LOGSITE_CODE='<site>'` (checkout type). |
| Balance check L1364-1399 | `SELECT Sum(AmtDr)-Sum(AmtCr) as Bal from PayCharge where LogSite_Code='<site>' AND FolioNo=<folio> and VType Not In ('ARRES','ADRES')` → if `Bal<>0` and `Enviro.Checkout='Strict'` → `MsgBox "Guest Balance is Not Zero"` → branch to `fdPaymentCharge.OpenMode=1 : ParentForm="Check Out"` then `GoTo loc_18DF282` (retry loop). |
| Core checkout UPDATEs L1407-1437 | `BeginTrans` ; `Proc_6_7` date strings for `ChkOutDate/UserchkoutDate/U_EntDt` ; `UPDATE RoomOcc set chkouttime='<HH:MM>',ChkOutDate=<date>,UserchkoutDate=<date>,ChkOutUser='<user>',Type='O',U_EntDt=<date>,U_AE='E' where Docid='<folioDocId>' and LogSite_Code='<site>' and RoomNO='<room>' and (Type='' or Type is NULL)` ; `UPDATE RoomMast set ROOMSTAT='D' WHERE logsite_code='<site>' and CODE='<room>' AND TYPE='RO'` ; `UPDATE PayCharge set SettleDate=<date> where FolioNoDocid='<folDocId>' and LogSite_Code='<site>'` (then VType not in). |
| EPABX audit L1438-1456 | `SELECT iif(IsNull(Max(ID)),1,Max(ID)+1)AS MyCode From EPABX_IN` → `insert into EPABX_IN (ID,V_TYPE,ROOM_NO,ROOM_NO_NEW,GUEST_NAME,ADVANCE) VALUES (<id>,'CHKOT','<room>','<new>','<name>',0)` (if `MemVar_1F921D0="Y"`). |
| SMS L1459-1468 | `SELECT TxtMsg,MobileNo from EmailSMSForward WHERE LOGSITE_CODE='<site>' And Type='Check Out' And Len(MobileNo)>=10 And Len(TxtMsg)>0` ; `SELECT CheckOutMsg,SendingMessageText from SMSEnviro WHERE LOGSITE_CODE='<site>'`. |
| Reverse checkout branch L1566-1720 | `SELECT Count(*) from RoomOcc where logsite_code='<site>' and RoomNO='<room>' and CHkoutDate is NULL` → if >0 `Already Occupied` ; `BeginTrans` ; `UPDATE RoomOcc set chkouttime='',ChkOutDate=NULL,Type='',U_EntDt=<date>,U_AE='E' where Type='O' AND FolioNo=<folio> and logsite_code='<site>' and RoomNO='<room>'` ; `CommitTrans`. |
| `Txt_Validate` L2375-2577 | Fills `Txt(0)=RoomNo`, `Txt(A)=FolioNo`, `Txt(A).Tag=DocId`, `SELECT ChkinDate,ChkinTime from RoomOcc where Sno=1 and Docid=<docid>` → paints `LblCheckInDay=Format(..., "DDDD")`, `Txt(1)=ChkInDate`, `Txt(2/3)=hh/mm split`, plus Guest `Name/Company/GSTIN/Status`. Loop `For ChkInDate To NCUR : SELECT ROOMOCC.*,RevMast.ACCode… FROM ROOMOCC JOIN RoomCat ON … JOIN RevMast … JOIN GuestFolio … WHERE >=chkindate and LogSite_Code='<site>' and Docid=<doc>` → RoomRentChkOutPost `Auto` charge posting guard: `SELECT RTrim(IsNull(Max(Bill_No),'')) from Paycharge where Vtype in ('RC') and Site_Code='<site>' and FolioNoDOCID='<docid>'` ; `SELECT Count(*) from Paycharge where Vtype in ('RC') and Site_Code='<site>' and Vdate=<date> and FolioNoDOCID='<doc>' And (RelatedFolioNo=<folio> Or RelatedFolioNo=0)` . |
| FGrid delete L1963-2133 | `SELECT DeleteGuestCharges FROM UserPermission WHERE LOGSITE_CODE='<site>' And CompCode='<comp>' And UserName='<user>'` ; `SELECT GuestChargesDeleteLog from Enviro where logsite_code='<site>'` → if `Delete="Yes"` ask `Reason` → `BeginTrans` → `INSERT INTO PayChargeLog SELECT * FROM PayCharge WHERE DOCID='<fgridDoc>' [AND SNO=<row>]` → `SELECT Max(SeqNo) From PayChargeLog WHERE DOCID='<doc>'` → `UPDATE PayChargeLog Set SeqNo=<max+1>,Remarks='<time>Delete Reason:<reason>',U_Name='<user>',U_EntDt=<date> Where IsNull(SeqNo,0)=0 And DOCID='<doc>' [AND SNO…]` → `DELETE FROM PAYCHARGE WHERE DOCID='<doc>' [AND SNO … And isnull(bill_no,'')='']` → `CommitTrans`. |

### 1.3 `fdDisplayFolio.frm` (1800+ lines) — Guest Ledger (read-only browse + PlanDetails)

| Area | Verbatim VB6 SQL |
|------|------------------|
| `Txt_Validate` L1528-1797 | `Select * from Enviro where LogSite_Code='<site>'` ; `SELECT ChkinDate,ChkinTime from RoomOcc where Sno=1 and Docid=<docid>` ; charge grid via `SELECT … From RoomOcc WHERE >=chkindate and ChngDate=(Top 1 … Order By ChngDate Desc,Sno Desc) and LogSite_Code='<site>' and Docid=<doc>` (same as CheckOut) ; `SELECT RTrim(IsNull(Max(Bill_No),'')) from Paycharge where Vtype in ('RC') and Site_Code='<site>' and FolioNoDOCID` ; `SELECT Count(*) … Vtype in ('RC') and Site_Code='<site>' and Vdate=<date>` ; `SELECT max(NetPackageAmount) as PkgAmt from Plandetails where Docid='<doc>' And RoomNo='<room>'` . Displays `Txt(25)=PlanAmount`. RoomRentChkOutPost `Auto` posting logic identical to FdCheckOut (nested loops). |
| Top filters | `SELECT FolioNo, Name, Vdate, DepDate, DocId, Vprefix FROM GuestFolio WHERE Site_Code=? AND Vprefix=?` (Python) vs VB6 `FrmHouseStatus:1065` join variant (below). |

### 1.4 `fdRoomChange.frm` (379k chars) — Room Change (30-col RoomOcc insert)

Extracted verbatim patterns (from p-code scan):

```vb
SELECT Code as SearchCode,Code as RoomNo, Name as Quot from roommast where type='RO' and Code='<code>'        ' validation
SELECT RoomNO from roomOcc where ChkOutDate is NULL and RoomNO <> '<old>'                                  ' free check
SELECT RoomMast.RoomCat,RoomCat.Name,Revmast.TaxStru as RoomTaxStru From RoomMast Left Join RoomCat … Where (RoomMast.LOGSITE_CODE='<site>' …)
SELECT Code as SearchCode, Code as RoomNo,Name as Quot from RoomMast Where LogSite_Code='<site>' and Type='RO' And Code not in (Select RoomNo from RoomOcc where type not in ('C','O') AND ROOMNO …)      ' available rooms
SELECT RoomCode from RoomBLockOut where Type In ('O','M') And ToDate ?
SELECT MULTPER,* FROM ROOMMAST WHERE LogSite_Code='<site>' and TYPE='RO' AND ROOMCAT='<cat>'
SELECT MAX(sno) AS SNO from RoomOcc where DocId='<doc>' and Site_Code='<site>' and RoomNO='<old>'
SELECT MAX(sno) AS SNO from RoomOcc where DocId='<doc>'
SELECT iif(IsNull(Max(ID)),1,Max(ID)+1)AS MyCode From EPABX_IN
INSERT INTO EPABX_IN (ID,V_TYPE,ROOM_NO,ROOM_NO_NEW,GUEST_NAME) VALUES (<id>,'CHKOT','<old>','<new>','<name>')
INSERT INTO EPABX_IN (ID,V_TYPE,ROOM_NO,ROOM_NO_NEW,GUEST_NAME) VALUES (<id>,'CHKIN','<new>','<old>','<name>')
INSERT INTO RoomOcc (DocID,Sno,FolioNo,VType,Site_Code,vPrefix,GuestProf,RoomCat,RoomType,RoomNo,RateCode,RoomRate,ChkInDate,ChkInTime,aDult,Children,DepDate,DepTime,Type,U_Name,U_EntDt,U_AE,LogSite_Code,RRTaxInc,RRServiceChrg,ChngDate,ExtraBed,RoomTarrif,RoomTaxStru,RackRate) VALUES (<30 cols>)
UPDATE RoomOcc Set PlanCode='<code>',PlanAmt=<amt>,IncInRate='<y>',PlanDisc=<pct>,PlanDiscAmt=<amt>,U_AE='E' WHERE SNo=<new> AND DocId='<doc>' AND Site_Code='<site>' AND RTRIM(RoomNo)='<new>'
UPDATE RoomOcc set CHKOUTDATE=<date>,CHKOUTTIME='<hh:mm>',Type='C',NewRoomNo='<new>',Reason='<reason>',U_Name='<user>',U_EntDt=<date>,U_AE='E' WHERE SNo=<old> AND DocId='<doc>' AND Site_Code='<site>' AND RTRIM(RoomNo)='<old>'
UPDATE GuestMessage set RoomNo='<new>',RoomCat='<newCat>' WHERE FolioNo=<folio> AND LogSite_Code='<site>' AND RTRIM(RoomNo)='<old>'
UPDATE Booking Set OccRoom='<new>' Where DocId='<bookingDocId>'
UPDATE RoomMast set RoomStat='D' Where Type='RO' And Code='<old>' AND (LogSite_Code='<site>' OR LogSite_Code='HO')
INSERT INTO PlanDetails (FolioNo,RoomNo,RevCode,Chrgcode,TaxInc,TaxStru,PrintOption,PostingMethod,ChargeType,FlatRate,Adult,Child,ExtraAdult,ExtraChild,NoOfDays,PlanPer,App_Date,FixRate,Site_Code,U_Name,U_EntDt,U_AE,Amount,PlanCode,Docid,NetPackageAmount,Logsite_Code,DiscAmt,PlanAppDate) VALUES (… new RoomNo …)
```

**Key:** VB6 RoomChange is a **single `BeginTrans` over 8 steps** (new RoomOcc row → plan update → old row checkout with `Type='C'` + `NewRoomNo`/`Reason` → GuestMessage → Booking.OccRoom → RoomMast dirty → PlanDetails delete+reinsert → EPABX_IN). New SNo = `MAX(SNo)+1`. No PayCharge touch (pure move).

### 1.5 `FdRevCheckOut.frm` (103k chars) — Reverse CheckOut

```vb
SELECT Count(*) from RoomOcc where logsite_code='<site>' and RoomNO='<room>' and CHkoutDate is NULL
SELECT ChkOutDate, ChkInDate … FROM RoomOcc WHERE DocId='<doc>' …
BeginTrans
UPDATE RoomOcc SET chkouttime='',ChkOutDate=NULL,Type='',UserChkOutDate=NULL,ChkoutUser=NULL,U_Name='<user>',U_EntDt=<date>,U_AE='E' WHERE DocId='<doc>' AND Type='O' AND FolioNo=<folio> and logsite_code='<site>' and RoomNO='<room>'
UPDATE PayCharge SET SettleDate=NULL, Bill_No=NULL WHERE FolioNoDocid='<doc>' AND Site_Code='<site>' AND Vtype NOT IN ('ARRES','ADRES')
UPDATE PayCharge SET ModeSet='' WHERE Site_Code='<site>' AND VPrefix='<fy>' AND FolioNo=<folio> AND ModeSet='S' AND PayCode <> '<site>ROFF'
UPDATE FOMBillDetails SET Status='CANCEL',U_Name='<user>',U_EntDt=<date>,U_AE='E' WHERE FolioNo=<folio> AND SiteCode='<site>' AND Status='SETTLE'
SELECT MFolioNoDocid FROM GuestFolio WHERE DocId='<doc>' → if mFolio → UPDATE RoomOcc Type='O' group rows WHERE DocId IN (SELECT DocId FROM GuestFolio WHERE MFolioNoDocid='<mFolio>')
INSERT INTO FolioLog (Id,FolionoDocid,Flag='R',Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)
CommitTrans
```

### 1.6 `fdRoomOcc.frm` (49k chars) + `FdRoomDisplay.frm` (302 lines) + `fdWalkInEntry.frm` (1.28M chars)

| Source | Verbatim VB6 |
|--------|--------------|
| `FdRoomDisplay.Form_Load` L110 | `select * from roommast where logsite_code='<site>' and type='RO' and inclcount='Y' order by Code` → builds `BtnEnh Cmd` grid (9-col rack). `Cmd_UnknownEvent_9` → `Select PicPath From RoomMast Where LogSite_Code='<site>' and type='RO' and inclcount='Y' and Code='<code>'`. |
| `fdRoomOcc` (roster) | `SELECT <42 cols> FROM RoomOcc WHERE Site_Code=? AND ChkOutDate IS NULL ORDER BY RoomNo` — used by reservation/rack; Ho-fallback not present (Site_Code only). |
| `fdWalkInEntry` (CHK creator) | VB6 DocId `D<site>CHK<suff> <year> <folio>` 21-char; FolioNo = `MAX(FolioNo)+1` per FY; inserts `GuestFolio (DocId,FolioNo,Vtype='CHK',Vprefix,Vdate,GuestProf,Name,City,NoDays,DepDate,BookingDocId,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)` then `RoomOcc (DocId,SNo=1,FolioNo,Vtype='CHK',Site_Code,Vprefix,GuestProf,RoomNo,RateCode,ChkInDate,ChkInTime='10:00',Adult=1,Children=0,DepDate,DepTime='10:00',Type='I',…)` (see checkin.py evidence). |

### 1.7 `FOMModule.bas` Proc_146 series (VB6 report bridges)

| Proc | Verbatim VB6 SQL |
|------|------------------|
| `Proc_146_1_1334068` L39 | `SELECT Max(P.VNO) AS RECTNO,Max(P.VDATE) AS RECTDATE,…Max(P.AMTCR) AS RECTAMT,Max(P.ROOMNO)…Max(GP.NAME) AS GUESTNAME,Max(R.NAME) As PayName,Max(P.TxnNo)… FROM (GUESTPROF GP left join GUESTFOLIO GF ON GF.GUESTPROF=GP.CODE) LEFT JOIN PAYCHARGE P ON GF.DOCID=P.FOLIONODOCID LEFT JOIN RevMast R ON P.PayCode = R.Code WHERE P.DOCID IN ('<csvDocIds>') AND P.VTYPE='REC' Group By P.DocId` |
| `Proc_146_2` L174 | `SELECT P.VNO AS RECTNO,P.VDATE AS RECTDATE,P.PAYTYPE AS RECTMODE,…P.AMTCR AS RECTAMT, … FROM (GUESTPROF GP left join GUESTFOLIO GF …) LEFT JOIN PAYCHARGE P ON GF.DOCID=P.FOLIONODOCID LEFT JOIN RevMast R ON P.PayCode = R.Code WHERE P.FOLIONODOCID IN ('<docIds>') AND P.VTYPE='REC' And MODESET='S' ORDER BY P.DOCID` ; also `Select max(Bill_No) from PayCharge where (Bill_no is not NULL and Bill_no<>'') and Folionodocid In ('<docIds>')` |
| `Proc_146_4` L404 | `Select B.DocId UID,…,COMP.Name as Company,TR.Name as TravelAgency,B.ResStatus… From Booking B Left Join SubGroup COMP … Where B.DocId='<doc>'` ; Guest detail: `SELECT GP.Code,GP.ConPrefix,…GP.PicPath,Country_1.Name As Nationality,…GFor … FROM GuestProf GP LEFT JOIN Country AS Country_1 ON GP.Nationality = Country_1.Code … Where GP.Code='<guestCode>' Order By P_SerialNo` ; plan: `SELECT GR.BookingDocId As UID,GR.SNo,…,IsNull(BP.RPackageAmt,0) MealCharge,… FROM (GRPBookingDetails GR Left Join RoomCat RC …) Left Join PlanMast … WHERE GR.BookingDocid='<doc>' Order By GR.BookingDocid,GR.SNo` |
| `Proc_146_3` L298 | `Fields.Append "UID" … "GuestName" … "P_GuestName" … "PAN_No"` (GRCRES TTX 58 fields). |

### 1.8 `MainLib.bas` Proc_6_7 / Proc_6_15 / Proc_6_38 + `MDIForm1.frm` FrontDesk menus

| Proc | Verbatim |
|------|----------|
| `Proc_6_7_F25D88` L413 | `If IsNull(arg_10) Or arg_10=vbNullString Or arg_10=Null Then var_94="Null" Else var_94="'" & Format(CDate(CDate(arg_10)), "Short Date") & "'"` — date quoting helper (all RoomOcc/GuestFolio dates). |
| `Proc_6_15_EF2C1C` | `U_EntDt` = `Format(Now, "Short Date")` family. |
| `Proc_6_38_E68A98` | `Trim(CVar(IsNull→""))` null-safe string. |
| `MDIForm1.frm` FDO 315-492 | `FA > Transaction: fate[0] Voucher Entry` style → **Front Office path:** `FDO+0 Reservation (Booking)` ; `FDO+1 Check In (fdCheckIn→fdWalkInEntry, AdvType="CHK")` ; `FDO+2 Folio Display (fdDisplayFolio, guest ledger read)` ; `FDO+3 Room Display (FdRoomDisplay rack)` ; `FDO+4 Room Change (fdRoomChange)` ; `FDO+5 Check Out (FdCheckOut, settle+checkout)` ; `FDO+6 Reverse Check Out (FdRevCheckOut, Type='O' reversal)` ; `FDO+7 Merge Charge (FrmMergeCharge / FrmRevMergeCharge)` ; `FDO+8 Re-Settlement (FdReSetlement, REC re-post)` ; `FDO+9 Night Audit (mdlNightAudit)`. Each multiplies menu `Param_Str`/`Flag` from `menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Front Office …'` before enabling. |

### 1.9 `moondata.sql` UTF-16 table defs (relevant cols)

```sql
-- GuestFolio PK (DocId) cols DocId(21),FolioNo int,Vtype(5),Vdate,Site_Code(2),Vprefix(5),GuestProf(8),Name(50),Add1/2,City(6),NoDays smallint, BookingDocId(21), MFolioNo int, MFolioNoDocid(21), Company(8), RODisc/RSDisc float, GroupCode, BussSource/MarketSeg, DepDate, LogSite_Code, U_Name/U_EntDt/U_AE
-- GuestProf PK (Code) 58+ cols, Site/LogSite_Code; PicPath/IdPicPath; City/StateName/CountryName denorm; Age int
-- PayCharge PK (DocId,SNo) cols DocId(21),SNo int,Vtype(8),VNo int,Site_Code(2),VPrefix(5),Vdate,VTime(5),GuestProf(8),PayCode(6),PayType(15),AmtCr/AmtDr float,TipAmt,RoomCat(5)/RoomType(2)/RoomNo(5),FolioNo int,FolioNoDocid(21),RelatedFolioNo/RelatedFolionoDocId,ContraDocID(21),Bill_No(8),SettleDate,ModeSet(1),BatchNo,RestCode(6),BillAmount,SeqNo,RefDocId,Remarks(255),AU_Name/AU_EntDt,TaxStru, LogSite_Code NOT NULL
-- PayChargeLog PK (DocId,SNo,SeqNo) same + SeqNo audit
-- RoomOcc PK (DocId,SNo) 42 cols DocId(21),SNo int,FolioNo int,Vtype(5),Site_Code(2),Vprefix(5),GuestProf(8),RoomCat(5),RoomType(2),RoomNo(5),RateCode(1),RoomRate float,ChkInDate/Time,Adult/Children,DepDate/Time,ChkOutDate/Time,Type(1) ('I'=in-house, 'C'=changed, 'O'=checked-out, ''=open),U_Name/U_EntDt/U_AE,UserchkoutDate/ChkoutUser/NewRoomNo/Reason/PlanCode/PlanAmt/IncInRate/RRTaxInc/RRServiceChrg/ChngDate/ExtraBed/RackRate/RoomTarrif/RoomTaxStru, LogSite_Code NOT NULL
-- RoomMast PK (Type,Code,RestCode,LogSite_Code) cols Type(2),Code(5),Name,RoomCat(5),Extension,MultPer,RevCode,TaxStru,RoomStat(1) ('D'=dirty, 'M'=blocked, ''=clean),Site_Code,LogSite_Code,DoorLockID
-- RevMast PK (Code) cols Code(6),Name(50),PayType(15),ACCode,TaxStru,Type, PAYTYPE, Nature, LogSite_Code
-- FOMBillDetails PK (Bill_No..composite, not DocId) cols Bill_No(50),Bill_Date,FolioNo int,Guestname, BillAmt/SettAmt float, Status('SETTLE'/'CANCEL'),U_Name/SiteCode, FolioNoDocid(21), LogSite_Code
-- GuestFolioAmend PK (FolioNo,Site_Code,OldDepDate) cols FolioNo,Site_Code,GuestProf,RoomNo,OldDepDate/Time,DepDate/Time, LogSite_Code
-- FolioLog cols Id,FolionoDocid(21),Flag('A' Add, 'C' CheckOut, 'R' Reverse, 'S' Settle, 'P' Pay, 'M' Amend, 'E' Edit, 'T' TokenReset, 'D' Diplomat),Site_Code,LogSite_Code
-- Enviro PK (LogSite_Code) cols Checkout('Strict'/'Standard'), RoomRentChkOutPost('Auto'/''), RoomCheckOutClearanceYN('Yes'/'No'), GuestChargesDeleteLog('YES'), NCUR, LogSite_Code
```

---

## 2) Python Sources Read (verbatim SQL)

### 2.1 `core/checkin.py` (432 lines)

```python
# list_checkins
SELECT TOP {top} DocId,FolioNo,Vtype,Vprefix,Vdate,GuestProf,Name,City,NoDays,DepDate,BookingDocId,U_Name,U_EntDt,U_AE FROM GuestFolio WHERE Site_Code=? AND Vprefix=? ORDER BY FolioNo DESC
# get / next_folio
SELECT {SELECT_COLS} FROM GuestFolio WHERE Site_Code=? AND Vprefix=? AND FolioNo=?
SELECT MAX(FolioNo) FROM GuestFolio WITH (UPDLOCK, HOLDLOCK) WHERE Site_Code=? AND Vprefix=?
# room assign
SELECT COUNT(*) FROM RoomMast WHERE RTRIM(Code)=? AND (LogSite_Code=? OR LogSite_Code='HO')
SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo)=? AND ChkOutDate IS NULL AND Site_Code=?
SELECT TOP 1 RTRIM(rm.Code) FROM RoomMast rm WHERE RTRIM(rm.Type)='RO' AND (rm.LogSite_Code=? OR rm.LogSite_Code='HO') AND rm.Code NOT IN (SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE ro.ChkOutDate IS NULL AND ro.Site_Code=?) ORDER BY rm.Code
# create_checkin INSERTs
INSERT INTO GuestFolio (DocId,FolioNo,Vtype,Vprefix,Vdate,GuestProf,Name,City,NoDays,DepDate,BookingDocId,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)
INSERT INTO RoomOcc (DocId,SNo,FolioNo,Vtype,Site_Code,Vprefix,GuestProf,RoomNo,RateCode,ChkInDate,ChkInTime,Adult,Children,DepDate,DepTime,Type,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,'CHK',?,?,?,?,?,?,?,?,?,?,?,'10:00','I',?,getdate(),'A',?)
# FolioLog
SELECT MAX(Id) FROM FolioLog WHERE LogSite_Code=?
INSERT INTO FolioLog (Id,FolionoDocid,Flag,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,getdate(),?,?)

# move_room / split_folio / group_checkin / delete_checkin similar — all param-bound, HO fallback on RoomMast only, Site_Code+Vprefix on GuestFolio/UpDLOCK
```

### 2.2 `core/folio.py` (771 lines)

```python
# next_billno
SELECT MAX(Cast(Bill_No As Int)) FROM FOMBillDetails WHERE LogSite_Code=?
# folio_charges / charges_detail
SELECT SNo,PayCode,PayType,Comments,AmtDr,AmtCr,Vdate FROM PayCharge WHERE Site_Code=? AND VPrefix=? AND FolioNo=? ORDER BY SNo
SELECT SNo,RTRIM(PayCode),RTRIM(PayType),AmtDr,AmtCr,Vdate FROM PayCharge WHERE FolioNo=? AND Site_Code=? AND VPrefix=? ORDER BY SNo
# folio_balance
SELECT SUM(AmtDr-AmtCr) FROM PayCharge WHERE Site_Code=? AND VPrefix=? AND FolioNo=?
# _get_settle_mode
SELECT [Checkout] FROM Enviro WHERE LogSite_Code=? OR LogSite_Code='HO'
# settle_folio INSERTs
SELECT DocId,Name FROM GuestFolio WHERE Site_Code=? AND Vprefix=? AND FolioNo=?
SELECT 1 FROM FOMBillDetails WHERE FolioNoDocid=? AND Status='SETTLE'
SELECT ISNULL(SUM(AmtDr),0),ISNULL(SUM(AmtCr),0) FROM PayCharge WHERE Site_Code=? AND VPrefix=? AND FolioNo=?
INSERT INTO FOMBillDetails (Bill_No,Bill_Date,FolioNo,Guestname,BillAmt,SettMode,SettAmt,Status,U_Name,SiteCode,U_EntDt,U_AE,FolioNoDocid,LogSite_Code) VALUES (?,getdate(),?,?,?,?,?,'SETTLE',?,?,getdate(),'A',?,?)
UPDATE PayCharge SET Bill_No=?,SettleDate=getdate() WHERE Site_Code=? AND VPrefix=? AND FolioNo=? AND Vtype NOT IN ('ARRES','ADRES')
# post_room_charge (RC)
# next_vno("PayCharge","RC",…) WITH UPDLOCK/HOLDLOCK
SELECT MAX(SNo) FROM PayCharge WHERE FolioNo=? AND Site_Code=?
INSERT INTO PayCharge (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,GuestProf,Comments,PayCode,FolioNo,FolioNoDocid,RoomNo,AmtDr,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)  # x3 if GST (KKCGSS/KKSGSS 5% each)
# receive_payment (REC 35-col)
SELECT TOP 1 RoomCat,RoomType,RoomNo FROM RoomOcc WHERE DocId=?
SELECT MAX(SNo) FROM PayCharge WHERE FolioNo=? AND Site_Code=?
INSERT INTO PayCharge (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,BillAmount,AmtCr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,CardNo,CardHolder,ChqNo,ChqDate,TxnNo,ExpDate,U_Name,U_EntDt,U_AE,RestCode,ModeSet,BatchNo,FolioNoDocid,LogSite_Code) VALUES (?,?,'REC',?,?,?,?,?,?,...,'KKFOM','S',?, ?,?)
# _create_contra (CONTRA)
INSERT INTO PayCharge (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,GuestProf,Comments,PayCode,AmtDr,U_Name,U_EntDt,U_AE,ContraDocId,ModeSet,LogSite_Code) VALUES (?,1,'CONTRA',?,?,?,?,...,,?,'C',?)
# amend_departure GuestFolioAmend
INSERT INTO GuestFolioAmend (FolioNo,Site_Code,GuestProf,RoomNo,OldDepDate,OldDepTime,DepDate,DepTime,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?, '', '', ?, '10:00', ?, '10:00', ?,getdate(),'A',?)
UPDATE GuestFolio SET DepDate=?, NoDays=DATEDIFF(day,Vdate,?),U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=?
UPDATE RoomOcc SET DepDate=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=? AND Site_Code=?
UPDATE PlanDetails SET NoofDays=? WHERE FolioNo=? AND Site_Code=? AND RoomNo=? AND DocId=? AND NoofDays=?
```

### 2.3 `core/checkout.py` (354 lines)

```python
# _get_checkout_type
SELECT [Checkout] FROM Enviro WHERE LogSite_Code=? OR LogSite_Code='HO'   # col probing "Checkout"/"CheckOutType"/…
# folio_balance
SELECT ISNULL(SUM(AmtDr),0),ISNULL(SUM(AmtCr),0) FROM PayCharge WHERE FolioNoDocid=? AND Site_Code=?
# list_active_folios
SELECT TOP {top} ro.DocId,gf.FolioNo,gf.Name,gf.GuestProf,gf.City,gf.NoDays,gf.DepDate,ro.ChkOutDate,ro.ChkoutUser,gf.U_Name,gf.U_AE,ro.RoomNo FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId=ro.DocId WHERE ro.Site_Code=? AND ro.Vprefix=? AND ro.ChkOutDate IS NULL ORDER BY gf.FolioNo DESC
# list_checked_out  (uses TOP (?) param placeholder — mismatch with other TOP {int})
SELECT TOP (?) ro.DocId,gf.FolioNo,gf.Name,gf.DepDate,ro.ChkOutDate,ro.ChkoutUser FROM RoomOcc ... WHERE ro.ChkOutDate IS NOT NULL ORDER BY gf.FolioNo DESC
# do_checkout
SELECT DocId,ChkOutDate,Type FROM RoomOcc WHERE Site_Code=? AND Vprefix=? AND FolioNo=? AND ChkOutDate IS NULL ORDER BY SNo
# clearance gate
UPDATE RoomOcc SET ChkOutDate=getdate(),ChkOutTime=CONVERT(varchar(5),getdate(),108),ChkoutUser=?,Type='O',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE Site_Code=? AND Vprefix=? AND FolioNo=? AND ChkOutDate IS NULL
INSERT INTO FolioLog (Id,FolionoDocid,Flag='C',…)
# reverse_checkout
SELECT DocId,ChkOutDate FROM RoomOcc WHERE Site_Code=? AND Vprefix=? AND FolioNo=? AND ChkOutDate IS NOT NULL ORDER BY SNo
UPDATE RoomOcc SET ChkOutDate=NULL,ChkOutTime='',ChkoutUser=NULL,UserChkOutDate=NULL,Type='',… WHERE Site_Code=? AND Vprefix=? AND FolioNo=? AND ChkOutDate IS NOT NULL
# MFolioNoDocid group reverse + FOMBillDetails/ PayCharge ModeSet/Bill_No nulling
SELECT MFolioNoDocid FROM GuestFolio WHERE DocId=?
UPDATE PayCharge SET SettleDate=NULL,Bill_No=NULL WHERE Site_Code=? AND VPrefix=? AND FolioNo=? AND Vtype NOT IN ('ARRES','ADRES')
UPDATE PayCharge SET ModeSet='' WHERE Site_Code=? AND VPrefix=? AND FolioNo=? AND ModeSet='S' AND PayCode<>?
UPDATE FOMBillDetails SET Status='CANCEL',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNo=? AND SiteCode=? AND Status='SETTLE'
INSERT INTO FolioLog Flag='R'
```

### 2.4 `core/fo_ops.py` (437 lines) — RoomChange / MergeCharge / ReSettlement

```python
# open_folio_by_room
SELECT TOP 1 gf.DocId,gf.FolioNo,gf.GuestProf,gf.Name,gf.BookingDocId,gf.Vprefix,gf.Vdate FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId=ro.DocId WHERE RTRIM(ro.RoomNo)=? AND ro.ChkOutDate IS NULL AND ro.Site_Code=? ORDER BY ro.ChkInDate DESC
# free_rooms
SELECT RTRIM(Code) FROM RoomMast … WHERE RTRIM(rm.Type)='RO' AND (rm.LogSite_Code=? OR 'HO') AND rm.Code NOT IN (SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE ro.ChkOutDate IS NULL AND ro.Site_Code=?)
# room_change (8-step) — see VB extract; Python mirrors 30-col INSERT + plan UPDATE + old checkout (Type='C' NewRoomNo/Reason) + GuestMessage + Booking.OccRoom + RoomMast dirty + PlanDetails reinsert + EPABX_IN (208-guard)
# merge_charge
SELECT … FROM RoomOcc… (src/tgt)
UPDATE GuestFolio SET mFolioNoDocid=?,mFolioNo=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=?
UPDATE PayCharge SET RelatedFolioNo=?,RelatedFolioNoDocId=? WHERE FolioNoDocid=? AND (ContraDocID IS NULL OR ContraDocID='')
UPDATE PayCharge SET FolioNoDocid=?,FolioNo=?,RelatedFolioNo=?,RelatedFolioNoDocId=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNoDocid=?
# re_settlement
SELECT DocId,VNo,Vdate,VTime,PayCode,PayType,AmtCr,Comments,ModeSet FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<>? ORDER BY Vdate DESC,VNo,U_EntDt
SELECT TOP 1 DocId,AmtCr FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<>? ORDER BY VNo DESC   → delete WHERE DocId=? AND FolioNoDocid=? AND Site_Code=? AND ModeSet='S'
# plus sum-match guard: sum(new lines) == old AmtCr ±0.005 else ValueError
INSERT INTO PayCharge (DocId,SNo,Vtype='REC',VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,TipAmt=0,RoomCat/RoomType/RoomNo,FolioNo,…) VALUES (1,'REC',…,'KKFOM','S',…)
```

### 2.5 `core/room_occ.py` (280 lines) + `core/roomstatus.py` + `core/guestprof.py`

```python
# room_occ SELECT_COLS = 42 cols (DocId,SNo,FolioNo,Vtype,Site_Code,Vprefix,…,RackRate)
# list_all / list_occupied
SELECT TOP {limit} {SELECT_COLS} FROM RoomOcc WHERE Site_Code=? AND ChkOutDate IS NULL ORDER BY RoomNo   # NO Vprefix, NO HO
# room_availability (Phase B)
SELECT RTRIM(Code),RTRIM(Name),RTRIM(RoomCat),RTRIM(RoomStat) FROM RoomMast WHERE RTRIM(ISNULL(Type,'RO'))='RO' AND Site_Code=?   # missing OR HO on LogSite_Code, missing InclCount filter
SELECT DISTINCT RTRIM(RoomNo) FROM RoomOcc WHERE Site_Code=? AND ChkOutDate IS NULL
SELECT DISTINCT RTRIM(b.RoomNo) FROM Booking b WHERE b.Site_Code=? AND ISNULL(b.Cancel,'N')<>'Y' AND ISNULL(b.RoomNo,'')<>'' AND b.DepDate>? AND ? >= b.ArrDate   # date overlap
SELECT DISTINCT RTRIM(b.RoomCode) FROM RoomBLockOut b WHERE b.RoomCode IS NOT NULL AND b.FromDate IS NOT NULL AND b.ToDate IS NOT NULL AND b.FromDate<=b.ToDate AND b.ToDate>=? AND b.FromDate<=?
# checkout (utility, not FdCheckOut flow)
UPDATE RoomOcc SET ChkOutDate=?,ChkOutTime=?,Type='O',… WHERE DocId=?
```

### 2.6 UI: `ui/folio_ui.py` (339 lines), `ui/checkout_ui.py`, `ui/fo_sub_forms_ui.py` (RoomChange/Merge/ReSet), `ui/frontoffice.py` (236 lines)

- `folio_ui.FolioBrowser` — `SELECT FolioNo,Name,Vdate,DepDate,DocId,Vprefix FROM GuestFolio WHERE Site_Code=? AND Vprefix=?` (no LogSite_Code, no ChkOutDate join — shows all folios, not just in-house). Buttons: Check-Out/Settle, Amend Departure, Receive Payment, Folio Log + Charge drill `folio_charges`/`folio_balance`. No TopCtrl state (`A/E/D/P`), no Find band.
- `frontoffice.CheckInBrowser` — `checkin.list_checkins()` grid `Folio|VDate|Name|GuestCode|City|Days|DepDate|User|AE` ; dialog New Check-In with `PYT*` default, `guestprof.next_code()` auto (`KK######`), adult/child/rate/chkintime fields, then `create_checkin(...)` mirroring VB `fdWalkInEntry.SearchBackParent`. Keeps `DocId 21-char` label.
- `fo_sub_forms_ui` — forms wire to `fo_ops.room_change / merge_charge / re_settlement` via `open_folio_by_room` resolvers (RO-combo from `free_rooms`). No `Reason` length 100 guard before call (core enforces).
- `checkout_ui` — binds `checkout.list_active_folios / do_checkout / reverse_checkout / clearance_list` ; clearance indicator wired to `RoomCheckOutClearanceYN`.

---

## 3) Gap Table — where Python deviates from VB6

| # | Area | VB6 behavior | Python current | Severity | SAME-SQL fix (no schema change) |
|---|------|--------------|----------------|----------|----------------------------------|
| **G1** | **HO fallback `(LOGSITE_CODE=? OR LOGSITE_CODE='HO')`** | `fdCheckIn` Booking `LOGSITE_CODE='<site>'`; `FdRoomDisplay` `RoomMast` `logsite_code='<site>' and type='RO' and inclcount='Y'` (no HO but site-only); `fdRoomChange` `RoomMast (LogSite_Code=? OR HO)`, `RoomBLockOut Type In ('O','M')`; `FdCheckOut` `PayCharge LogSite_Code='<site>'` (strict), `Enviro` `LogSite_Code='<site>'`; `FolioLog` logged per `LogSite_Code`; `mdI` Front Desk menus filtered by `CompCode/UserName/Flag`. | `checkin.py` RoomMast HO fallback **done**; `room_occ.py` `RoomMast WHERE Site_Code=?` **no** `LogSite_Code OR HO`; `fo_ops.room_change` RoomMast OK but `room_occ.list_all` misses HO & `InclCount='Y'`; `checkout.list_checked_out` uses `TOP (?)` placeholder (TOP expects literal, not param — will error on SQL Server); `folio_ui` browse `WHERE Site_Code=? AND Vprefix=?` **no** `LogSite_Code` & **no** `ChkOutDate IS NULL` join. | **HIGH** — site-HO rooms invisible; browse leaks HO/cross-site. | Add `(rm.LogSite_Code=? OR rm.LogSite_Code='HO' OR ISNULL(rm.LogSite_Code,'')='')` to every `RoomMast` SELECT (keep `Type='RO'` and `InclCount='Y'` where VB6 has it). Change `list_checked_out` to `TOP {int(top)}` literal (not `?`). Add `AND gf.LogSite_Code=?` (or `AND ro.LogSite_Code=?`) to browse SELECTs. Keep column names. |
| **G2** | **LOGSITE_CODE scoping on reports & ledger reads** | VB6 `PayCharge` ops always `WHERE LogSite_Code='<site>'` (or check `Site_Code`+`LogSite_Code` both); `FOMBillDetails` `LogSite_Code`; `RoomOcc` `Site_Code`+`LogSite_Code`. Even `Enviro` per `LogSite_Code`. | `folio.folio_charges/charges_detail` filter `Site_Code+VPrefix+FolioNo` but **no** `LogSite_Code`; `checkout.folio_balance` uses `FolioNoDocid+Site_Code` only (missing `LogSite_Code`); `fo_ops.re_settlement` MODESET list uses `PayCode<>?` ROFF but no `LogSite_Code` on sum; `room_occ.room_availability` `Site_Code=?` only. | **HIGH** — cross-site leakage on multi-site DB. | Add `AND LogSite_Code=?` (param `SITE_CODE`) to every `PayCharge`/`RoomOcc`/`FOMBillDetails` `SELECT` (keep existing `Site_Code` predicate). Param-bound. |
| **G3** | **Voucher/sequence numbers (`next_vno` / FolioNo / Bill_No)** | VB6 `FolioNo = MAX(FolioNo)+1` per FY (no lock literal but single-user VB6 EXE); `VNo` per `Vtype+VPrefix+Site_Code+LogSite_Code`; `FOMBillDetails Bill_No` numeric `MAX(Cast(Bill_No As Int))+1` per `LogSite_Code`; `EPABX_IN ID` = `IIF(IsNull(Max(ID)),1,Max(ID)+1)` (VB6 `fdRoomChange`). | `checkin.next_folio` correctly `MAX(FolioNo) WITH (UPDLOCK,HOLDLOCK) WHERE Site_Code=? AND Vprefix=?` — OK (add `LogSite_Code` for double-cover). `folio.next_billno` `MAX(Cast(Bill_No As Int)) WHERE LogSite_Code=?` — OK. `folio.post_room_charge` / `receive_payment` / `fo_ops.re_settlement` use `db.next_vno("PayCharge","RC/REC",vprefix,site)` with `UPDLOCK/HOLDLOCK` on same `cn` — OK vs VB6 lock. `EPABX_IN` in `fo_ops.room_change` correctly `COALESCE(MAX(ID),0)+1` with 208-guard (table may not exist). Gap: `checkout.list_checked_out` `TOP (?)` breaks MSSQL on prepare. | MEDIUM | Keep `UPDLOCK/HOLDLOCK` pattern; fix `TOP (?)` → `TOP {int(top)}` literal interpolation (VB6 uses literal). Add `AND LogSite_Code=?` to `next_folio` extra predicate. No schema change. |
| **G4** | **Dr==Cr + Zero-balance checkout guard** | `FdCheckOut.Command2_Click` L1364-1399: `SELECT Sum(AmtDr)-Sum(AmtCr) as Bal … VType Not In ('ARRES','ADRES')` → if `Bal<>0` and `Enviro.Checkout='Strict'` → `MsgBox "Guest Balance is Not Zero"` → branch to `fdPaymentCharge` settlement loop (GoTo retry). `Enviro.Checkout` empty → Strict (hard-block). `fdDisplayFolio` PayCharge delete guards `Bill_No<>''` re-delete block. | `folio.settle_folio` correctly reads `Enviro.Checkout` via `_get_settle_mode()` (HO fallback), `Standard` allows non-zero, else `abs(bal)>0.005` block — OK mirroring VB6. `checkout.do_checkout` replicates `Strict` check with `_get_checkout_type()` probing `Checkout`/`CheckOutType` cols, plus `check_clearance()` (RoomCheckOutClearanceYN). Gap: `checkout.folio_balance` uses `FolioNoDocid+Site_Code` **not** `FolioNo+ VType Not In ('ARRES','ADRES')` variant VB6 uses in one path — subtle difference on advance receipts. Also `folio.folio_balance` (other file) uses `Site_Code+VPrefix+FolioNo` not `FolioNoDocid`. Two balance variants coexist. | MEDIUM | Unify: keep `_get_settle_mode()` ST conspiracy (Strict default) ; ensure `checkout.folio_balance` also excludes `VType IN ('ARRES','ADRES')` when called from `do_checkout` (or provide param). Add `AND Vtype NOT IN ('ARRES','ADRES')` to balance SELECT if missing. Param-bound. |
| **G5** | **DocId 21-char spec (`D + site(2) + VType.ljust(6) + year(4).ljust(4) + VNo.rjust(8)`)** | VB6 `DocId='DKKCHK   2026     <folio>'` (`fdWalkInEntry` CHK), `DKKRC    2026     <vno>` (folio post), `DKKREC   2026     <vno>` (payment), `DPrefix=VType` padded. `U_AE` 'A' add / 'E' edit / 'C' cancel. | Python `checkin.make_docid`, `folio.make_pc_docid`, `folio.receive_payment` DocId builders all match VB6 21-char (tested live). `room_occ` inserts keep `Vtype='CHK'` literal. Gaps: `fo_ops.re_settlement` `INSERT PayCharge SNo=1` hard-coded but VB6 per-folio `MAX(SNo)+1` across existing lines (would clash on folio with existing REC). | LOW | Change `re_settlement` to compute `MAX(SNo)` per folio (as `post_room_charge` does) before insert; keep 21-char helper. |
| **G6** | **FolioNo vs FolioNoDocid dual-link** | VB6 `PayCharge` carries **both** `FolioNo` (int) and `FolioNoDocid` (21-char DocId). Settle uses `PayCharge.FolioNoDocid` + `FolioNo` ; `RoomOcc.FolioNo` vs `DocId`. Reverse checkout clears both `SettleDate/Bill_No` where `FolioNoDocid=?`. | `folio.receive_payment` correctly writes both `FolioNo` + `FolioNoDocid=GuestFolio.DocId` (plus `RelatedFolioNo/DocId` for merge). `folio.folio_charges` queries by `FolioNo` only (missing DocId link). `checkout.folio_balance` queries by `FolioNoDocid` (DocId) — OK. Dual helpers exist (`_resolve_folio` fallback across Vprefix). Gap: `fo_ops.folio_charge_total` does `SELECT SUM(DrAmt)` (col **does not exist** — real col is `AmtDr`, `DrAmt` typo) → always 0. | **HIGH** | Fix `folio_charge_total` to `SELECT ISNULL(SUM(AmtDr),0) FROM PayCharge WHERE FolioNoDocid=? AND Site_Code=?` (keep names; remove `DrAmt`). Ensure every PayCharge write populates **both** links as VB6 does. |
| **G7** | **menuHelp Flag / UPrivilege check (MDI TopCtrl)** | `MDIForm1.FDO_Click` + `FaVoucher.bas Proc_7_1` → `SELECT Param_Str AS UPrivilege,Flag FROM menuHelp WHERE UserName='<u>' AND CompCode='<c>' AND [Option]='Voucher Entry' / 'Front Office …'` then `Flag='Y'` and `Param_Str` contains `A/E/D/P` per action. | Python has `core/menu_help.py` but **no Front Office caller** checks it before write. Any user can create checkin / settle / merge / change. | **HIGH** — workflow guard missing. | Reuse SAME SQL: add at top of `create_checkin/delete_checkin`, `settle_folio/post_room_charge/receive_payment/amend_departure`, `checkout.do_checkout/reverse_checkout`, `fo_ops.room_change/merge_charge/re_settlement` : `SELECT Flag, Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?` ; if `Flag<>'Y'` or `Param_Str NOT LIKE '%A%'` raise `PermissionError`. Param-bound. No schema change. |
| **G8** | **BeginTrans / Commit / Rollback parity** | `FdCheckOut.Command2_Click` → `BeginTrans … Execute UPDATE RoomOcc / RoomMast / PayCharge / EPABX_IN … CommitTrans / RollbackTrans` ; `FdRevCheckOut` same; `fdRoomChange` single trans over 8 steps; `FGrid_UnknownEvent_D` delete `BeginTrans … Insert PayChargeLog … Update PayChargeLog SeqNo … Delete PayCharge … CommitTrans`. | Python: `checkin.create_checkin` is **not** wrapped in single transaction when `cn is None` (creates cn, then commits once — OK). `folio.settle_folio` correctly single `cn` try/commit. `fo_ops.room_change` correctly 8 steps on one `cn` with single commit — OK. Gap: `folio.post_room_charge` commits correctly but GST split does 3 rows on same `cn` OK. `checkout.do_checkout` correctly single commit. `room_occ.room_availability` has no transaction needed. Missing: `folio.delete_payment` / `checkout.reverse_checkout` correctly use single `cn`. **One miss:** `checkin.delete_checkin` deletes `GuestFolio + RoomOcc + PayCharge + FolioLog` on one `cn` but **single `DELETE GuestFolio` does not check `LOGSITE_CODE`** (VB6 per-site). | MEDIUM | Ensure every multi-write uses same `cn` with `try/except: rollback` semantics (already in most). Add `AND LogSite_Code=?` to `delete_checkin` deletes. Keep `BeginTrans` label in comments. |
| **G9** | **RoomStat / RoomBLockOut / InclCount handling (availability)** | VB6 `FdRoomDisplay 12F9CF3` → `where logsite_code='<site>' and type='RO' and inclcount='Y'` (rack excludes non-count). `fdRoomChange` available rooms `WHERE LogSite_Code='<site>' and Type='RO' And Code not in (Select RoomNo from RoomOcc where type not in ('C','O')) And Code not in (Select RoomCode from RoomBLockOut where Type In ('O','M') …)`. `RoomMast.RoomStat='D'` set on old room dirty (fdRoomChange `Update RoomMast set RoomStat='D' …`). | `room_occ.room_availability` correctly computes `occupied (ChkOutDate IS NULL)`, `booked (Booking Cancel<>'Y' DepDate>? and ArrDate <=?)`, `blocked (RoomBLockOut FromDate/ToDate valid)`, `dirty (RoomStat='D')`, `available`. But `rooms = SELECT … FROM RoomMast WHERE RTRIM(ISNULL(Type,'RO'))='RO' AND Site_Code=?` — **missing** `LogSite_Code OR HO`, **missing** `InclCount='Y'` filter, uses `Site_Code` instead of `LogSite_Code`. So unavailable rooms counted wrong. `free_rooms` in `fo_ops` correctly uses `LogSite_Code OR HO` + `ChkOutDate IS NULL` subquery. Inconsistent. | **HIGH** | Align `room_availability` to VB6: `SELECT … FROM RoomMast WHERE RTRIM(Type)='RO' AND InclCount='Y' AND (LogSite_Code=? OR LogSite_Code='HO')` (keep column names). |
| **G10** | **Merge / ReSettlement semantics (contra, RelatedFolio)** | VB6 `FrmMergeCharge` (BtnroomMerge): source `GuestFolio.mFolioNo/mFolioNoDocid = target`, then `UPDATE PayCharge SET RelatedFolioNo=?,RelatedFolioNoDocId=? WHERE FolioNoDocid=? AND (ContraDocID IS NULL OR ContraDocID='')` then `UPDATE PayCharge SET FolioNoDocid=?,FolioNo=?,RelatedFolioNo=?,RelatedFolioNoDocId=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNoDocid=?` (all rows). `FdReSetlement` (BtnSave): `SELECT TOP 1 DocId,AmtCr FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<>ROFF ORDER BY VNo DESC` → `IF Sum(new)!=old AmtCr → error` → `DELETE FROM PayCharge WHERE DocId=? AND FolioNoDocid=? AND Site_Code=? AND ModeSet='S'` → re-insert `Vtype='REC', ModeSet='S', RestCode='KKFOM'` per line (VNo = `MAX+1` per Vprefix). | `fo_ops.merge_charge` exactly replicates 3 UPDATEs (including RelatedFolioOnly first pass) — **OK**. `re_settlement` replicates sum-match guard + delete + per-line `next_vno('REC')` + 21-char DocId + `RestCode='KKFOM', ModeSet='S'` — **OK** but SNo hard-coded 1 vs MAX+1 (see G5). | LOW | Fix re_settlement SNo to `MAX(SNo)+1` per folio, keep VB6 21-char DocId. No schema change. |
| **G11** | **TopCtrl toolbar workflow mismatch** | VB6 `TopCtrl` (main bar) states: `Add` (clear form + lock fields), `Find` (`SearchCode LIKE '%'` help grid `DGHelp/DGRoomNo/DGRoomType`), `Edit` (`Enabled=False` guard on locked Txt), `Save` validates `GroupHelp/Nature` duplicates, `Delete` checks `Ledger COUNT(*) >0` block, `Print` via `CRViewer`, `Exit`. Field `Txt(0)` search always via `Me.Find "RoomNo ='…'"`. | Python UIs: `frontoffice.CheckInBrowser` has `New/Refresh/Close` (no TopCtrl state, no SearchCode help grid, no `DGHelp` filtering), `folio_ui.FolioBrowser` has table double-click drill but no `Find` band, no `TopCtrl` `AEDP` gating. `fo_sub_forms_ui` has RoomChange/Merge/ReSet dialogs but no `BeginTrans` status bar nor `Vprefix` FY combo. | MEDIUM | Backend fix first; UI: add TopCtrl-like `QToolBar` wiring to `menuHelp Flag`, `QComboBox` for Vprefix FY picker (`enviro.NCUR` window), `QLineEdit` Find with `SearchCode LIKE ?` live filter. Keep `Enabled` lock on `Txt(0)` after Save. |
| **G12** | **DATELOCK / negative-balance / checkout clearance guards** | `Enviro Checkout='Strict'/'Standard'` + `RoomCheckOutClearanceYN='Yes'` + `GuestChargesDeleteLog='YES'` checked before checkout/delete. `NCUR` (`enviro.NCUR`) gates `Vdate` allow window. | `folio._get_settle_mode` correctly reads `Enviro.Checkout` (HO fallback, Strict default). `checkout._get_checkout_type` probes `Checkout`/`CheckOutType` cols (MSSQL 207 guard) — good but probing adds dead paths; single `Checkout` col is correct per moondata.sql. `checkout.check_clearance` reads `RoomCheckOutClearanceYN` + `FOMBillDetails Status='SETTLE'` + `balance==0` — OK. `DATELOCK` (`DATELOCK.flag` nearly **never called** in `do_checkout`/`post_voucher` path — exists `year_end.check_datelock` but not wired to checkout). `GuestChargesDeleteLog` correctly read in `FdCheckOut.FGrid_UnknownEvent_D` delete but Python `folio.delete_payment` prompts `_log` but not per-row delete log SNo sequence. | MEDIUM | Add at top of `do_checkout`/`receive_payment` (if not already): `SELECT 1 FROM DATELOCK WHERE SDate<=? AND EDate>=? AND flag=1 AND (Site_Code=? OR LogSite_Code=?)` ; if locked raise. Keep `_get_checkout_type` to single `Checkout` col (drop probe). No schema change. |
| **G13** | **PayCharge LogSno / seq audit (PayChargeLog SeqNo PK)** | VB6 delete charge: `INSERT INTO PayChargeLog SELECT * FROM PayCharge WHERE DOCID='<doc>' [AND SNO=<n>]` → `SELECT Max(SeqNo) From PayChargeLog WHERE DOCID='<doc>'` → `UPDATE PayChargeLog Set SeqNo=<max+1>,Remarks='<time>Delete Reason:<reason>',U_Name='<user>',U_EntDt=<date> Where IsNull(SeqNo,0)=0 And DOCID='<doc>'` — multi-col PK (`DocId,SNo,SeqNo`). | Python `folio.delete_payment` does `INSERT INTO PayChargeLog SELECT *,getdate(),? FROM PayCharge WHERE DocId=?` — `*` expansion plus extra columns will **break** on MSSQL (column count mismatch — `PayChargeLog` has `SeqNo` NOT NULL extra vs `PayCharge`). Also `checkout.reverse_checkout` nulls `SettleDate/Bill_No` but does not write `PayChargeLog` audit before nulling. | **HIGH** | Fix: `INSERT INTO PayChargeLog (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,AmtDr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,CardNo,…,FolioNoDocid,LogSite_Code,RefNo,PlanCode,SeqNo,RelatedFolionoDocId,RefDocId,Remarks,AU_Name,AU_EntDt) SELECT DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,AmtDr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,CardNo,…,FolioNoDocid,LogSite_Code,RefNo,PlanCode,COALESCE((SELECT MAX(SeqNo) FROM PayChargeLog WHERE DocId=?),0)+1,RelatedFolionoDocId,RefDocId,? ,getdate()` or compute max first then explicit `VALUES`. Add `LogSite_Code` filter. |

---

## 4) Fixed Workflow (EXACTLY VB6 same workflow, SAME SQL)

### 4.1 Check-In — fixed sequence

```python
# 1) Privilege + DateLock + Site (VB6 fdCheckIn→fdWalkInEntry TopCtrl1_UnknownEvent_16)
rows = db.query("SELECT Flag, Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Front Office - Check In'", (user, comp), cn=cn)
if not rows or rows[0][0] != 'Y' or 'A' not in (rows[0][1] or ''): raise PermissionError("No Check-In privilege")
# NCUR window check via Enviro.NCUR if DATELOCK needed

# 2) Reservation lookup (VB6 Form_Load SQL verbatim)
rows = db.query(
  "SELECT Booking.DocId AS CODE, GuestProf.Name, Booking.GuestProf, Booking.DocId AS ID, RoomCat.Name AS RoomType, RoomMast.Code AS RoomNo, Booking.ArrDate AS Arr_Date, Booking.NoDays AS tot_Days, Booking.NoOfRooms as NO_Rooms "
  "FROM ((Booking LEFT JOIN RoomCat ON (Booking.RoomType = RoomCat.Type) AND (Booking.RoomCat = RoomCat.Code)) LEFT JOIN RoomMast ON (Booking.RoomType = RoomMast.Type) AND (Booking.RoomNo = RoomMast.Code)) "
  "INNER JOIN GuestProf ON Booking.GuestProf = GuestProf.Code "
  "WHERE BOOKING.CANCEL='N' AND BOOKING.LOGSITE_CODE=? AND (Select Count(Distinct Sno) From GrpBookingDetails Where Not Exists (Select Distinct isnull(BookingDocid,'') As BookingDocId,BookingSno As Sno from GuestFolio Where GrpBookingDetails.BookingDocId=GuestFolio.BookingDocId And GrpBookingDetails.Sno=GuestFolio.BookingSno) And IsNull(Cancel,'')<>'Y' And GrpBookingDetails.ArrDate=? And GrpBookingDetails.BookingDocid=Booking.DocId)>0 "
  "ORDER BY GuestProf.Name", (site, proc_6_7(today)), cn=cn)

# 3) FolioNo + DocId (VB6 21-char, HOLDLOCK)
# SELECT MAX(FolioNo) FROM GuestFolio WITH (UPDLOCK,HOLDLOCK) WHERE Site_Code=? AND Vprefix=? AND LogSite_Code=?
# DocId = "D"+site.ljust(2)+"CHK".ljust(6)+vprefix.ljust(4)+str(folio).rjust(8)

# 4) Free room resolve (VB6 free rooms literal)
# SELECT TOP 1 RTRIM(rm.Code) FROM RoomMast rm WHERE RTRIM(rm.Type)='RO' AND (rm.LogSite_Code=? OR rm.LogSite_Code='HO') AND rm.Code NOT IN (SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE ro.ChkOutDate IS NULL AND ro.Site_Code=? AND ro.LogSite_Code=?) ORDER BY rm.Code
# busy check: SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo)=? AND ChkOutDate IS NULL AND Site_Code=? AND LogSite_Code=?

# 5) Single cn transaction (BeginTrans parity):
# INSERT INTO GuestFolio (DocId,FolioNo,Vtype='CHK',Vprefix,Vdate,GuestProf,Name,City,NoDays= DATEDIFF(day, Vdate, DepDate), DepDate, BookingDocId, Site_Code, U_Name, U_EntDt=getdate(), U_AE='A', LogSite_Code)
# INSERT INTO RoomOcc (DocId,SNo=1,FolioNo,Vtype='CHK',Site_Code,Vprefix,GuestProf,RoomCat,RoomType,RoomNo,RateCode,RoomRate,ChkInDate,ChkInTime,Adult,Children,DepDate,DepTime='10:00',Type='I',U_Name,U_EntDt=getdate(),U_AE='A',LogSite_Code,RRTaxInc,RRServiceChrg,ChngDate,ExtraBed,RoomTarrif,RoomTaxStru,RackRate)
# INSERT INTO FolioLog (Id = MAX(Id)+1, FolionoDocid, Flag='A', Site_Code, U_Name, U_EntDt=getdate(), U_AE='A', LogSite_Code)
# commit else rollback
```

### 4.2 Check-Out (Bill-print gate → balance settle → checkout) — fixed

```sql
-- 1) Privilege
SELECT Flag, Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Front Office - Check Out'

-- 2) Bill gate (VB6 loc_18DEE2E…):
SELECT isnull(bill_no,'') as Bill_No,AmtDr from paycharge where LogSite_Code=? AND (ContraDocId is NULL or contradocid='') and foliono=? AND AmtDr<>0
-- if Filter("Bill_No='' and AmtDr<>0") count>0 → "First Print Bill"
SELECT distinct bill_no from paycharge where LogSite_Code=? AND foliono=? and (Bill_NO<>'' and Bill_NO is not null)
-- if 0 rows → "First Print Bill"
SELECT * from enviro WHERE LOGSITE_CODE=?  -- Checkout type

-- 3) Balance (VB6 VType Not In ('ARRES','ADRES')):
SELECT Sum(AmtDr)-Sum(AmtCr) as Bal from PayCharge where LogSite_Code=? AND FolioNo=? and VType Not In ('ARRES','ADRES')
-- if abs(Bal)>0.005 and Checkout!='Standard' → open fdPaymentCharge settlement loop

-- 4) Clearance
SELECT RoomCheckOutClearanceYN FROM Enviro WHERE LogSite_Code=?
SELECT TOP 1 Status,BillAmt FROM FOMBillDetails WHERE FolioNo=? AND SiteCode=? ORDER BY Bill_No DESC
SELECT ISNULL(SUM(AmtDr),0),ISNULL(SUM(AmtCr),0) FROM PayCharge WHERE FolioNoDocid=? AND Site_Code=? AND LogSite_Code=?

-- 5) BeginTrans:
UPDATE RoomOcc set chkouttime=CONVERT(varchar(5),getdate(),108),ChkOutDate=getdate(),UserchkoutDate=getdate(),ChkOutUser=?,Type='O',U_EntDt=getdate(),U_AE='E' where Docid=? and LogSite_Code=? and RoomNO=? and (Type='' or Type is NULL)
UPDATE RoomMast set ROOMSTAT='D' WHERE logsite_code=? and CODE=? AND TYPE='RO'
UPDATE PayCharge set SettleDate=getdate() where FolioNoDocid=? and LogSite_Code=?
-- EPABX_IN if feature present: SELECT COALESCE(MAX(ID),0)+1 FROM EPABX_IN → INSERT (ID,V_TYPE='CHKOT',ROOM_NO,ROOM_NO_NEW,GUEST_NAME)
INSERT INTO FolioLog (Id,FolionoDocid,Flag='C',Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)
-- SMS/Email forward selects verbatim (LogSite_Code scoped)
CommitTrans else RollbackTrans
```

### 4.3 Reverse Check-Out — fixed

```sql
SELECT Count(*) from RoomOcc where logsite_code=? and RoomNO=? and CHkoutDate is NULL -- block if occupied
BeginTrans
UPDATE RoomOcc SET chkouttime='',ChkOutDate=NULL,Type='',U_EntDt=getdate(),U_AE='E' WHERE DocId=? AND FolioNo=? and logsite_code=? and  RoomNO=? AND Type='O'
-- group members if MFolioNoDocid
SELECT MFolioNoDocid FROM GuestFolio WHERE DocId=?
UPDATE RoomOcc SET ChkOutDate=NULL,ChkOutTime='',ChkoutUser=NULL,UserChkOutDate=NULL,Type='',… WHERE DocId IN (SELECT DocId FROM GuestFolio WHERE MFolioNoDocid=?) AND Site_Code=? AND LogSite_Code=? AND Type='O'
UPDATE PayCharge SET SettleDate=NULL,Bill_No=NULL WHERE FolioNoDocid=? AND Site_Code=? AND LogSite_Code=? AND Vtype NOT IN ('ARRES','ADRES')
UPDATE PayCharge SET ModeSet='' WHERE Site_Code=? AND VPrefix=? AND FolioNo=? AND ModeSet='S' AND PayCode<>?
UPDATE FOMBillDetails SET Status='CANCEL',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNo=? AND SiteCode=? AND Status='SETTLE'
INSERT INTO FolioLog Flag='R'
CommitTrans
```

### 4.4 Room Change (8-step) — fixed

```sql
-- VB6 30-col INSERT literal, new SNo=MAX(SNo)+1, rest verbatim — see §1.4 snippet; same cn BeginTrans
-- Keep UPDATE GuestMessage/Booking/PlanDetails/Delete+Reinsert verbatim with LogSite_Code filter; EPABX_IN guarded 208
```

### 4.5 Merge + ReSettlement — fixed

```sql
-- Merge 3-step UPDATE verbatim
UPDATE GuestFolio SET mFolioNoDocid=?,mFolioNo=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=?
UPDATE PayCharge SET RelatedFolioNo=?,RelatedFolioNoDocId=? WHERE FolioNoDocid=? AND (ContraDocID IS NULL OR ContraDocID='')
UPDATE PayCharge SET FolioNoDocid=?,FolioNo=?,RelatedFolioNo=?,RelatedFolioNoDocId=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNoDocid=?

-- ReSet: sum-match guard then
SELECT TOP 1 DocId,AmtCr FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<>? ORDER BY VNo DESC
DELETE FROM PayCharge WHERE DocId=? AND FolioNoDocid=? AND Site_Code=? AND LogSite_Code=? AND ModeSet='S'
-- per new line: next_vno REC per FY/site/logSite (UPDLOCK,HOLDLOCK same cn), 21-char DocId, SNo=MAX(SNo)+1, RestCode='KKFOM', ModeSet='S'
INSERT INTO PayCharge (DocId,SNo,Vtype='REC',VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,U_Name,U_EntDt,U_AE,RestCode,ModeSet,BatchNo,FolioNoDocid,LogSite_Code) VALUES (…)

-- Charge delete audit (VB6 parity):
SELECT MAX(SeqNo) FROM PayChargeLog WHERE DocId=?
INSERT INTO PayChargeLog (explicit col-list incl SeqNo = max+1, Remarks, AU_Name/AU_EntDt) SELECT <same col-list> FROM PayCharge WHERE DOCID=? AND SNO=?
DELETE FROM PayCharge WHERE DocId=? AND SNo=? And isnull(bill_no,'')='' -- only unbilled rows deletable
```

### 4.6 Amend departure (GuestFolioAmend)

```sql
INSERT INTO GuestFolioAmend (FolioNo,Site_Code,GuestProf,RoomNo,OldDepDate,OldDepTime,DepDate,DepTime,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,… getdate(),'A',?)
UPDATE GuestFolio SET DepDate=?, NoDays=DATEDIFF(day,Vdate,?),U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=?
UPDATE RoomOcc SET DepDate=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=? AND Site_Code=? AND LogSite_Code=?
UPDATE PlanDetails SET NoofDays=? WHERE FolioNo=? AND Site_Code=? AND RoomNo=? AND DocId=? AND NoofDays=? -- oldNoDays match
INSERT INTO FolioLog Flag='M'
```

---

## 5) Frontend vs Backend Debug Notes

### Backend (core) — required patches (SAME-SQL, no schema change)

- [ ] **P0 `core/room_occ.py:room_availability`** — Change `FROM RoomMast WHERE RTRIM(ISNULL(Type,'RO'))='RO' AND Site_Code=?` → `WHERE RTRIM(Type)='RO' AND InclCount='Y' AND (LogSite_Code=? OR LogSite_Code='HO')` (VB6 12F9CF3). Add `LogSite_Code` to occupied/booked/blocked subqueries. Keep `InclCount` filter only for rack/availability, not for validation lookups.
- [ ] **P0 `core/room_occ.py:list_all/list_occupied/search`** — Add `AND (LogSite_Code=? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='')` and `Vprefix` where needed; param-bound `SITE_CODE`.
- [ ] **P0 `core/checkout.py:list_checked_out`** — `TOP (?)` → `TOP {int(top)}` literal interpolation (MSSQL syntax). Add `AND LogSite_Code=?` to SELECT. Fix copy-paste `TOP (?)` prepare error.
- [ ] **P0 `core/checkout.py:folio_balance` + `core/folio.py:folio_balance/charges_detail`** — Add `AND LogSite_Code=?` and one variant `AND Vtype NOT IN ('ARRES','ADRES')` for checkout balance (keep alias `Bal`); unify `charges_detail` vs `folio_charges` (one uses FolioNo only, one uses FolioNoDocid — pick DocId canonical `FolioNoDocid=? AND Site_Code=? AND LogSite_Code=?`).
- [ ] **P0 `core/folio.py:folio_charge_total`** — `SUM(DrAmt)` column does not exist → `SUM(AmtDr)` with `WHERE FolioNoDocid=? AND Site_Code=? AND LogSite_Code=?`. Current always returns 0.
- [ ] **P0 `core/fo_ops.py:re_settlement`** — `SNo` hard 1 → `MAX(SNo)+1` per folio (UPDLOCK,HOLDLOCK same cn). Keep VB6 21-char DocId.
- [ ] **P0 `core/folio.py:delete_payment` + `core/fo_ops` delete paths** — Expand `INSERT INTO PayChargeLog SELECT *,…` to explicit column list with `SeqNo = MAX(SeqNo)+1` (PayChargeLog has NOT NULL SeqNo + extra RefNo/PlanCode/RelatedFolionoDocId/AU_Name). Use `ISNULL` guard. Keep SAME column names.
- [ ] **P0 `core/checkin.py` + `core/folio.py` + `core/checkout.py` + `core/fo_ops.py`** — Add `AND LogSite_Code=?` to every PayCharge/RoomOcc/FOMBillDetails `DELETE/UPDATE` WHERE (multisite safety).
- [ ] **P1 `core/*` privilege gate** — At top of every write API add: `SELECT Flag, Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option] IN ('Front Office - Check In','Front Office - Check Out','Front Office - Room Change','Front Office - Merge Charge','Front Office - Re Settlement','Front Office - Amend')` ; gate on `Flag='Y'` and `Param_Str` contains `A/E/D` per op. Re-use SAME SQL.
- [ ] **P1 `core/checkout.py:_get_checkout_type`** — Collapse 4-probe to single `SELECT Checkout FROM Enviro WHERE LogSite_Code=? OR LogSite_Code='HO'` (moondata.sql col is `Checkout`); current probe swallows schema errors incorrectly.
- [ ] **P1 `core/folio.py:receive_payment` credit limit** — `SubGroup.AllowCredit/CreditLimit` query currently filters `GP.Company = SG.Code` but ignores `SG.LogSite_Code`; add `(SG.LogSite_Code=? OR SG.LogSite_Code='HO')`.
- [ ] **P1 `core/fo_ops.py:room_change` EPABX parity** — `EPABX_IN` 208 Invalid object name guard is correct; keep `Feature-detect` pattern. No change.

### Frontend (ui) — required patches

- [ ] `ui/frontoffice.py:CheckInBrowser` — Add FB6 parity: `QToolBar` `TopCtrl` (Add/Edit/Delete/Save/Cancel/Find/Print/Exit) wired to `menuHelp.Flag`; add `Find` help grid (`DGHelp` mimic) filtering `SearchCode LIKE ? OR Name LIKE ?` with `LOGSITE_CODE` filter; add `Vprefix` FY combo (from `VOUCHER_PREFIX` FY window); show `LOGSITE_CODE` chip. After Save, lock `Txt(0)` (RoomNo) as VB6 `Enabled=False`.
- [ ] `ui/folio_ui.py:FolioBrowser` — Change `_folios()` to use same VB6 in-house join: `SELECT … FROM RoomOcc ro INNER JOIN GuestFolio gf ON gf.DocId=ro.DocId WHERE ro.Site_Code=? AND ro.LogSite_Code=? AND ro.Vprefix=? AND ro.ChkOutDate IS NULL` (only in-house). Currently shows settled/cancelled folios too. Add `TopCtrl` `Find` Band + `U_Name/U_EntDt/U_AE` footer. Add `Dr==Cr` live indicator color (green 0.00, red otherwise) on `ChargeDialog`.
- [ ] `ui/fo_sub_forms_ui.py` (RoomChange/Merge/ReSettlement) — Add `Reason` MaxLength=100 counter (VB6 `Trim … [:100]`); add `ChngDate` `QDateEdit` default `NCUR` (Enviro) not `today`; add bulk `ModeSet='S'` filter for ReSettlement receipt picker (currently `Vdate DESC, VNo, U_EntDt`). Show `U_AE='E'` footer as VB6 does.
- [ ] `ui/checkout_ui.py` — Bind `RoomCheckOutClearanceYN` chip (Yes = checkout blocked until `bill_settled && balance_zero`); show `clearance_list` (`Bill_No,Bill_Date,FolioNo,Guestname,BillAmt,Status`) via `QTable` preview before checkout. Add `PayCharge` delete guard `Bill_No<>''` disable.
- [ ] All UIs — Show `U_Name/U_EntDt/U_AE` footer (`LblUser/LblLDt` mirror) from last `FolioLog` SeqNo. Wrap multi-grid saves in `QProgress` + `BeginTrans` toast (commit/rollback feedback).

### Verification command (after PATCH, before claim)

```bash
pytest PYTHONE/tests/test_frontoffice_*.py PYTHONE/tests/test_fo_ops*.py -q
python -m PYTHONE.core.checkin --selftest  # FolioNo HOLDLOCK + 21-char DocId + HO fallback
python -m PYTHONE.core.fo_ops --selftest  # room_change 8-step + merge 3-step + re_settlement sum-match
python -m PYTHONE.tools.frontoffice_smoke --headless  # TopCtrl FIND/PRINT grid parity
```

---

## 6) Raw SQL Reference — copy-paste parity (keep column names identical)

```sql
-- HO-fallback (VB6 window used everywhere)
WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO' OR ISNULL(LOGSITE_CODE,'')='')

-- RoomMast rack (FdRoomDisplay 12F9CF3)
SELECT * FROM RoomMast WHERE LogSite_Code=? AND Type='RO' AND InclCount='Y' ORDER BY Code

-- Free RO room (checkin + free_rooms)
SELECT TOP 1 RTRIM(rm.Code) FROM RoomMast rm WHERE RTRIM(rm.Type)='RO' AND (rm.LogSite_Code=? OR rm.LogSite_Code='HO') AND rm.Code NOT IN (SELECT RTRIM(ro.RoomNo) FROM RoomOcc ro WHERE ro.ChkOutDate IS NULL AND ro.Site_Code=? AND ro.LogSite_Code=?) ORDER BY rm.Code

-- Check-Out bill-gate
SELECT isnull(bill_no,'') as Bill_No,AmtDr FROM PayCharge WHERE LogSite_Code=? AND (ContraDocId IS NULL OR ContraDocID='') AND FolioNo=? AND AmtDr<>0  -- Filter Bill_No='' && AmtDr<>0 => First Print Bill
SELECT distinct bill_no FROM PayCharge WHERE LogSite_Code=? AND FolioNo=? AND (Bill_NO<>'' AND Bill_NO IS NOT NULL)

-- Zero-balance guard
SELECT Sum(AmtDr)-Sum(AmtCr) AS Bal FROM PayCharge WHERE LogSite_Code=? AND FolioNo=? AND VType NOT IN ('ARRES','ADRES')

-- RoomOcc checkout (strict AND Type='' OR NULL)
UPDATE RoomOcc SET ChkOutDate=getdate(),ChkOutTime=CONVERT(varchar(5),getdate(),108),UserChkOutDate=getdate(),ChkOutUser=?,Type='O',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=? AND LogSite_Code=? AND RoomNO=? AND (Type='' OR Type IS NULL)
UPDATE RoomMast SET RoomStat='D' WHERE LogSite_Code=? AND Code=? AND Type='RO'

-- Reverse
UPDATE RoomOcc SET ChkOutDate=NULL,ChkOutTime='',ChkoutUser=NULL,UserChkOutDate=NULL,Type='',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=? AND FolioNo=? AND LogSite_Code=? AND Type='O'
UPDATE PayCharge SET SettleDate=NULL,Bill_No=NULL WHERE FolioNoDocid=? AND Site_Code=? AND LogSite_Code=? AND Vtype NOT IN ('ARRES','ADRES')
UPDATE FOMBillDetails SET Status='CANCEL',U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNo=? AND SiteCode=? AND Status='SETTLE'

-- RoomChange 30-col INSERT (VB6)
INSERT INTO RoomOcc (DocId,SNo,FolioNo,Vtype,Site_Code,Vprefix,GuestProf,RoomCat,RoomType,RoomNo,RateCode,RoomRate,ChkInDate,ChkInTime,Adult,Children,DepDate,DepTime,Type,U_Name,U_EntDt,U_AE,LogSite_Code,RRTaxInc,RRServiceChrg,ChngDate,ExtraBed,RoomTarrif,RoomTaxStru,RackRate) VALUES (?,?,?,?,…)

-- Merge 3 UPDATEs
UPDATE GuestFolio SET mFolioNoDocid=?,mFolioNo=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE DocId=?
UPDATE PayCharge SET RelatedFolioNo=?,RelatedFolioNoDocId=? WHERE FolioNoDocid=? AND (ContraDocID IS NULL OR ContraDocID='')
UPDATE PayCharge SET FolioNoDocid=?,FolioNo=?,RelatedFolioNo=?,RelatedFolioNoDocId=?,U_Name=?,U_EntDt=getdate(),U_AE='E' WHERE FolioNoDocid=?

-- ReSettlement receipt re-post (VB6)
SELECT TOP 1 DocId,AmtCr FROM PayCharge WHERE FolioNoDocid=? AND ModeSet='S' AND PayCode<>? ORDER BY VNo DESC
DELETE FROM PayCharge WHERE DocId=? AND FolioNoDocid=? AND Site_Code=? AND LogSite_Code=? AND ModeSet='S'
INSERT INTO PayCharge (DocId,SNo,Vtype='REC',VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,U_Name,U_EntDt,U_AE,RestCode='KKFOM',ModeSet='S',BatchNo,FolioNoDocid,LogSite_Code) VALUES (?,?,?,?,…)

-- Privilege (MDI)
SELECT Flag, Param_Str, Module_Name FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?

-- Charge delete audit (PayChargeLog SeqNo PK)
SELECT ISNULL(MAX(SeqNo),0) FROM PayChargeLog WHERE DocId=?
INSERT INTO PayChargeLog (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf,Comments,PayCode,PayType,AmtCr,AmtDr,TipAmt,RoomCat,RoomType,RoomNo,FolioNo,CardNo,CardHolder,ChqNo,ChqDate,ExpDate,BookNo,BookType,U_Name,U_EntDt,U_AE,RestCode,BillAmount,ContraDocID,TaxPer,OnAmt,Split,Bill_No,MarkEntry,ModeSet,SettleDate,BatchNo,OldBill_No,PlanCharge,RelatedFolioNo,FolioNoDocid,LogSite_Code,RefNo,PlanCode,SeqNo,RelatedFolionoDocId,RefDocId,Remarks,AU_Name,AU_EntDt,TxnNo) SELECT … FROM PayCharge WHERE DOCID=? AND SNO=?
UPDATE PayChargeLog SET SeqNo=?,Remarks=?,AU_Name=?,AU_EntDt=getdate() WHERE DocId=? AND IsNull(SeqNo,0)=0
DELETE FROM PayCharge WHERE DocId=? AND SNo=? And isnull(bill_no,'')='' -- unbilled only
```

---

*Report path:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\FRONTOFFICE_COMPARE.md`  
*Generated by side-by-side full read of fdCheckIn.frm + FdCheckOut.frm + fdDisplayFolio.frm + fdRoomChange.frm + FdRoomDisplay.frm + FdRevCheckOut.frm + fdRoomOcc.frm + fdWalkInEntry.frm + FOMModule.bas Proc_146 + MainLib.bas Proc_6_7 + MDIForm1.frm FDO + moondata.sql GuestFolio/GuestProf/PayCharge/RoomOcc/RoomMast/RevMast/FolioLog/FOMBillDetails/GuestFolioAmend + checkin.py + folio.py + checkout.py + fo_ops.py + room_occ.py + guestprof.py/roomstatus.py + folio_ui.py + checkout_ui.py + fo_sub_forms_ui.py + frontoffice.py — verbatim SQL preserved, no DB schema change.*
