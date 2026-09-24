# RES/BANQ/MEM/HR/HK/TEL/SC/NA — VB6 vs Python Parity Report
> Modules: RESERVATION (Booking/GrpBookingDetails) · BANQUET (HallBook/HallSale) · MEMBERS (MemCatMast/MembershipMast/MemVisitEntry/MemBill) · HR/PAYROLL (Employee/Attend/Salary) · HOUSEKEEPING (ComplaintDetail/RoomBlockOut) · TELEPHONE (EPABX) · SMARTCARD · NIGHTAUDIT  
> Date: 2026-09-24 · Rule: **SAME VB6 SQL, no DB schema change** — only add `WHERE LOGSITE_CODE`/`HO` filter if missing, keep table/column names identical.  
> Python sources read: `booking.py`, `reservation.py`, `banquet_masters.py`, `banquet_ops.py`, `hall_booking.py`, `members_masters.py`, `member_billing.py`, `facility_billing.py`, `hr_masters.py`, `hr_payroll.py`, `epabx_masters.py`, `epabx_ops.py`, `smartcard.py`, `smartcard_ops.py`, `nightaudit.py`, `room_occ.py`, `sms_comm.py`  
> VB6 sources read: `RrRoomReservation.frm`, `FOMModule.bas`, `resRoomType.frm`, `HallBooking.frm`, `HallBill.frm`, `HallBillEstimate.frm`, `HallChefPreCosting.frm`, `BanqModule.bas`, `MemCatMast.frm`, `MembershipMast.frm`, `MemVisitEntry.frm`, `MemFacilityBilling.frm`, `MemberModule.bas`, `PrEmployee.frm`, `prAttend.frm`, `prSalCreate.frm`, `PrDesigMast.frm`, `PrCategoryMast.frm`, `FrmComplaintMast.frm`, `FrmComplaintClearing.frm`, `HHouseKeeping.frm`, `HKRoomBlock.frm`, `TelCallTypeMast.frm`, `TelExtensionMast.frm`, `TelCallEntry.frm`, `SmartCardRegistration.frm`, `SmartCardRecharge.frm`, `ModuleSmartCard.bas`, `mdlNightAudit.bas`, `frmReNightAudit.frm`, `FdAcPostChrg.frm`, `HMS.bas` (MDI menus)

---

## 1) RESERVATION — Booking / GrpBookingDetails / ViewBooking

### 1.1 VB6 SQL verbatim (≥2 key queries)

| VB6 file:L | Verbatim SQL | Purpose |
|---|---|---|
| `RrRoomReservation.frm:2942` | `Select NCUR,PlanCalc,RoomRateEditable,RoomIncTaxEditable,RoomServiceChargeEditable,PlanSelectionBasedOn,ReservationExpandOnSaveYN from enviro WHERE LOGSITE_CODE='<site>'` | Enviro flags drive booking editability |
| `FOMModule.bas:583` | `SELECT Count(*) FROM GRPBookingDetails WHERE BookingDocId='<docid>'` | Existence guard before insert/update |
| `FOMModule.bas:588` | `SELECT GR.BookingDocId As UID,GR.SNo,ISNULL(Booking.MyRectNo,'') MyRectNo,Booking.BookNo,RC.Name As RoomType,GR.ArrDate,GR.ArrTime,GR.DepDate,GR.DepTime,GR.NoDays,GR.RoomDet,GR.Adults,GR.Childs,GR.Tarrif,GR.RateCode,GR.IncTax,GR.ServiceChrg,GR.Cancel,GR.CancelDate,IsNull(BP.RPackageAmt,0) MealCharge,IsNull(BP.NetPackageAmount,0) As PlanTariff,IsNull(PlanMast.Name,'') PlanName FROM GRPBookingDetails GR LEFT JOIN ... WHERE BookingDocId='<id>'` | Grid display (RoomType/PlanTariff) |
| `FOMModule.bas:596` | `SELECT RefDocId UID,P.VNo,P.Vdate,P.VTime,P.Comments,P.PayCode,P.PayType,Revmast.Name PayName,P.AmtCr,P.CardNo,P.CardHolder,P.ExpDate,P.BatchNo,P.ChqNo,P.ChqDate,P.U_Name,P.U_EntDt FROM PayCharge P Inner Join Revmast On Revmast.Code=P.PayCode WHERE RefDocId='<docid>'` | Advance/deposit folio |
| `FOMModule.bas:404` | `Select B.DocId UID,IsNull(B.MyRectNo,'') as MyRectNo,B.BookNo,B.Vdate AS ResDate,B.U_Name,B.U_EntDt,COMP.Name as Company,TR.Name as TravelAgency,B.ResStatus,B.GuestProf,B.DepositeReq,B.Adult,B.Child,B.NoOfRooms,B.NoDays,BS.Name BussSource,MS.Name MarketSeg,B.ArrFrom,B.Destination,B.BookedBy,B.ResMode,B.TravelMode,B.RDisc,B.RSDisc From Booking B Left Join SubGroup COMP ...` | Reservation header browse (JOIN Company/TravelAgency) |
| `resRoomType.frm:497` | `Select B.ArrDate,B.DepDate,B.GuestName,B.ResStatus From ((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId ) Where B.LOGSITE_CODE='<site>'` | Availability - ViewBooking→GuestFolio→RoomOcc (arrival/depart exclusion) |
| `resRoomType.frm:1695` | `Select Count(*) As RoomBusyRO From RoomOcc Where LOGSITE_CODE='<site>' AND RoomCat='<cat>' And RoomType='RO' And ...` + `Select Count(*) As RoomBlocked From RoomBlockOut RB Inner Join RoomMast RM ON RB.RoomCode=RM.Code where RB.LOGSITE_CODE='<site>'` | Live occupancy count per RoomCat |

**VB6 workflow:** `Form_Load` → enviro flags → `LASTVOU` for `BookNo` (`SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code in ('<site>') And ENAME='Booking'` then `SELECT DOCID FROM LASTVOU ...` / `INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code)`), `Voucher_Prefix` via `SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where (VP.SITE_CODE='<site>' AND VP.LOGSITE_CODE='<site>' AND VP.V_Type='BK' AND '<date>' BETWEEN Date_From AND Date_To)`, then `INSERT INTO Booking ...`, `INSERT INTO GRPBookingDetails` per row, `UPDATE Voucher_Prefix Set Start_Srl_No=Start_Srl_No+1 Where (SITE_CODE='...' AND LOGSITE_CODE='...' AND V_Type='BK' AND Prefix='...')`, `UPDATE LASTVOU SET DOCID='...'`.

### 1.2 Python SQL (`booking.py` / `reservation.py` / `room_occ.py`)

```sql
-- booking.py insert
INSERT INTO Booking (DocId, Vtype, BookNo, Site_Code, Vprefix, Vdate, GuestName, ArrDate, DepDate, NoDays, Adult, Child, NoOfRooms, Rate, Remarks, GuestProf, ResStatus, U_Name, U_EntDt, U_AE, LogSite_Code, MobNo, Email ...)
-- next BookNo
SELECT MAX(BookNo) FROM Booking WITH(UPDLOCK) WHERE Site_Code = ?   -- no LOGSITE_CODE, no Vprefix window, no LASTVOU
-- reservation.py draft
SELECT MAX(BookNo) FROM Booking WITH(UPDLOCK) -- same missing LogSite
INSERT INTO Booking (...) VALUES (?,..., getdate(), 'A', ?)  -- 16 params, DocId = Vtype+BookNo derived, not LASTVOU
INSERT INTO BookingLog (Id, Bookingdocid, Flag, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code) VALUES (?, ?, ?, ?, ?, getdate(), 'A', ?)
UPDATE Booking SET GuestName=?, ArrDate=?, DepDate=?, NoDays=? WHERE Site_Code=? AND BookNo=?
UPDATE Booking SET Cancel='Y', CancelDate=getdate(), CancelUName=? WHERE Docid=?  + INSERT INTO BookingCancelDetails (DocId,SNo,VType,VNo,Vprefix,Vdate,CancellationMode,U_Name,U_EntDT,U_AE,LogSite_Code)
-- browse
SELECT * FROM Booking WHERE Site_Code=? AND BookNo=?  /  SELECT TOP 20 * FROM Booking WHERE Site_Code=? ORDER BY BookNo DESC
-- room_occ.py
SELECT ... FROM RoomOcc WHERE DocId=? / WHERE RTRIM(RoomNo)=? AND ChkInDate <= ? AND ChkOutDate > ?
SELECT DISTINCT RTRIM(RoomNo) FROM RoomOcc WHERE Site_Code=? AND FolioNo IN (...)  -- missing LOGSITE
```

### 1.3 Gap table

| # | VB6 behavior | Python current | Severity | SAME-SQL fix |
|---|---|---|---|---|
| R-G1 | `LOGSITE_CODE='<site>'` on every `ViewBooking`, `RoomOcc`, `RoomBlockOut`, `Enviro` read + `OR 'HO'` on master lookups | `booking.py list/get/insert` filter only `Site_Code=?` (no LogSite_Code), `room_occ.py` has `Site_Code` only | HIGH — cross-site leakage, HO rooms invisible | Add `WHERE Booking.LogSite_Code=? AND (Booking.LogSite_Code=? OR Booking.LogSite_Code='HO')` pattern; for browse use `WHERE Booking.LogSite_Code=?` |
| R-G2 | Booking number via `LASTVOU` + `Voucher_Prefix` (Number_Method BETWEEN window, per `V_Type='BK'/'RC'`) | `SELECT MAX(BookNo)` without `Vprefix`/FY lock, no `LASTVOU`, no `Voucher_Prefix.Start_Srl_No` bump | HIGH — duplicate BookNo under concurrency; FY prefix ignored | Restore VB6 verbatim: `SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type='BK' AND ? BETWEEN Date_From AND Date_To` then `UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='BK' AND Prefix=?`; also `SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'` → `UPDATE LASTVOU SET DOCID=?` else `INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code)` |
| R-G3 | `GRPBookingDetails` + `BookingPlanDetails` joined via `IsNull(BP.RPackageAmt,0)` plan tariff, per `BookingDocId` | `booking.py` has `BookingPlanDetails` helpers but `reservation.py` draft never touches `GRPBookingDetails`/`BookingPlanDetails`; plan amount left 0 | MEDIUM | Ensure `reservation.insert_draft` also handles `INSERT INTO GRPBookingDetails (BookingDocId,SNo,RoomType,ArrDate,DepDate,NoDays,RoomDet,Adults,Childs,Tarrif,RateCode,IncTax,ServiceChrg,Site_Code,LogSite_Code)` per VB6 FGrid; use MAX(SNo) per DocId with LOGSITE |
| R-G4 | `ViewBooking` as canonical view for availability (`ViewBooking as B Left Join GuestFolio GF ... Left Join RoomOcc RO`) filtered by `B.LOGSITE_CODE` | `reservation.py` / `room_occ.py` never query `ViewBooking`; availability derived from `RoomOcc` + `Booking` separately | MEDIUM | Add `SELECT B.ArrDate,B.DepDate,RC.Name RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO') Where B.LOGSITE_CODE=?` as VB6 does |
| R-G5 | `menuHelp` privilege per Booking screen (`[Option]='Booking Entry'` → `Param_Str` contains A/E/D) + TopCtrl Add/Edit/Del/Print state | No `menuHelp` check before `booking.insert/update/delete` or `reservation.cancel` | HIGH | Prepend `SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Booking Entry'` guard |
| R-G6 | `PayCharge` advance linking `RefDocId` = Booking DocId, checked before delete (`SELECT COUNT(*) FROM PayCharge WHERE RefDocId='...'`) — blocks delete if advance exists | `booking.py` has no PayCharge check; `reservation.delete_draft` only guards `PYT*` | MEDIUM | Add `SELECT COUNT(*) FROM PayCharge WHERE RefDocId=? AND LogSite_Code=?` guard before Booking delete |

### 1.4 Fixed workflow (EXACT VB6 same workflow)
```python
# 1) menuHelp + enviro
db.query("SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Booking Entry'", (user,comp))
db.query("Select NCUR,PlanCalc,RoomRateEditable,RoomIncTaxEditable,RoomServiceChargeEditable,PlanSelectionBasedOn,ReservationExpandOnSaveYN from enviro WHERE LOGSITE_CODE=?", (SITE_CODE,))
# 2) prefix + lastvou
rows = db.query("Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type='BK' AND ? BETWEEN VP.Date_From AND VP.Date_To", (SITE_CODE,SITE_CODE,vdate))
vprefix = rows[0].Prefix
# 3) LASTVOU lock
cnt = db.query("SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME='Booking'", (SITE_CODE,))
# ... UPDLOCK insert/update same cn transaction ...
# 4) INSERT Booking with same cols as VB6 (DocId, BookNo, Vtype, Vprefix, Vdate, GuestName, ArrDate, DepDate, GuestProf, ResStatus, LogSite_Code)
# 5) loop GRPBookingDetails rows: SELECT MAX(SNo) WHERE BookingDocId=? → INSERT INTO GRPBookingDetails (BookingDocId,SNo,RoomType,ArrDate,DepDate,NoDays,RoomDet,Adults,Childs,Tarrif,RateCode,IncTax,ServiceChrg,Site_Code,LogSite_Code)
# 6) UPDATE Voucher_Prefix Set Start_Srl_No=... Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='BK' AND Prefix=? ; UPDATE/INSERT LASTVOU
```

### 1.5 Frontend/Backend notes
- **Backend P0:** `booking.py`/`reservation.py` add `LogSite_Code` param to all SELECT/INSERT/UPDATE/DELETE; restore `LASTVOU`+`Voucher_Prefix` numbering; add `ViewBooking` query for availability.
- **Frontend:** `ui/booking_ops_ui.py` / `registration_entry_ui.py` currently use `reservation.insert_draft` with simple fields; need TopCtrl parity: `Add` clears+`BookNo` from LASTVOU, `Edit` loads via `BookingDocId`, `Delete` checks `PayCharge.RefDocId` guard, `Find` via `Booking.BookNo` + `Vprefix`, live `PlanCalc` flag toggles rate editability chip (`RoomRateEditable='Y'` → Rate field enabled).

---

## 2) BANQUET — HallBook / HallSale / HallBooking

### 2.1 VB6 SQL verbatim

| VB6 file:L | Verbatim SQL |
|---|---|
| `HallBooking.frm:2401` | `SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code in ('<site>') And ENAME='<vtype>'` + `SELECT DOCID FROM LASTVOU WHERE LogSite_Code in ('<site>') And ENAME='<vtype>'` → `UPDATE LASTVOU SET DOCID='...' WHERE LogSite_Code='<site>' And ENAME='...'` / `INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES ('<user>','<vtype>','<docid>','<site>',getdate(),'A','<site>')` |
| `HallBooking.frm:4960` | `Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where (VP.SITE_CODE='<site>' AND VP.LOGSITE_CODE='<site>' AND VP.V_Type='<vtype>' AND '<date>' BETWEEN VP.Date_From AND VP.Date_To)` |
| `HallBooking.frm:4985` | `SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code='<site>' And ENAME='...'` (post-save verify) |
| `HallBooking.frm:2312` | `Select Code,PartyName as Name From BookingInquiry where LogSite_Code in ('<site>') And code not in (select InquiryCode from HallBook Where InquiryCode<>'...')` |
| `HallBooking.frm:3855` | `SELECT Count(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId='<docid>'` — delete-block if bill exists |
| `HallBooking.frm:3878` | `Delete From HallBook Where Docid='<docid>'` + `Delete From HallBook1 Where Docid='<docid>'` + `Delete From VenueOCC Where FPDocID='<docid>'` |
| `HallBooking.frm:6178` | `Select COunt(*) From VenueOCC S WHERE LogSite_Code='<site>' And <dateOverlap> VenuCode='<venue>'` — venue clash check |
| `HallBook (save):4867` | `Insert Into HallBook(Docid,VNo,VDate,VType,VPrefix,VTime,Site_Code, Total,DiscPer,DiscAmt,NonTaxable,Taxable,Tax,ServiceCharge,AddAmt,DedAmt,RoundOff,U_Name,U_EntDt,U_AE,HallRent,Remarks,Advance,NetAmount,LogSite_Code,BookingAgent)` |
| `HallBooking.frm:4950` | `Insert Into VenueOCC(FPDocid,VenuCode,FromDate,ToDate,FromTime,ToTime,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)` |
| `HallBill.frm` (inferred from HallBooking + BanqModule) | `Insert Into HallSale1 (DocId,Vtype,VNo,VTime,Site_Code,Vprefix,Vdate,RestCode,Party,Total,DiscPer,DiscAmt,NonTaxable,Taxable,Tax,ServiceCharge,AddAmt,DedAmt,RoundOff,NetAmt,FrBookDate,FrBookTime,ToBookDate,ToBookTime,HallRent,Remarks,NoOfPax,RatePerPax,TotalPerCover,Amount,Advance,RectNo,rectDate,CrCardNo,CrCardHolder,BookDocId,DelFlag,Narration,LogSite_Code,CGST,SGST,IGST)` + `Insert Into HallSale2 (DocId,Sno,SNo1,Vtype,VNo,Site_Code,Vprefix,Vdate,PartyCode,RestCode,RoomCat,RoomType,RoomNo,Item,QtyIss,Unit,Rate,Amount,TaxPer,TaxAmt,DiscPer,DiscAmt,VoidYN,Remarks,U_Name,U_EntDt,U_AE,LogSite_Code)` |
| `HallBillEstimate.frm` | Same as HallBill but `Vtype='IDE'` (estimate) vs `'IDC'` (confirmed), no `PayChargeH` insert |
| `HallChefPreCosting.frm` | `Insert Into HallStock (DocId,Sno,Vtype,VNo,Site_Code,Vprefix,Vdate,Party,RestCode,ContraDocId,ContraSno,Item,QtyIss,Unit,Rate,Amount,TaxPer,TaxAmt,DiscPer,DiscAmt,VoidYN,Remarks,U_Name,U_EntDt,U_AE,Total,DiscApp,RoundOff,DepartCode,GodCode,DelFlag,LogSite_Code,SChrgApp,SChrgPer,SChrgAmt)` — costing via MenuItem→ItemMast |
| `BanqModule.bas:??` | `Select BanqBookingMsg,BanqBookingCancelMsg,SendingMessageText from SMSEnviro WHERE LOGSITE_CODE='<site>'` + `Select TxtMsg,MobileNo from EmailSMSForward WHERE LOGSITE_CODE='<site>' And Type='BanqBooking' And Len(MobileNo)>=10` |

### 2.2 Python SQL (`banquet_ops.py` / `hall_booking.py` / `banquet_masters.py`)

```sql
-- hall_booking.py _next_vno (currently)
SELECT MAX(VNo) FROM HallBook WITH (UPDLOCK, HOLDLOCK) WHERE Site_Code=? AND Vprefix=?
INSERT INTO HallBook (DocId,Vtype,VNo,VTime,Site_Code,Vprefix,Vdate,PartyName,...,BookingAgent,LogSite_Code) VALUES (?)
UPDATE HallBook SET ... WHERE Site_Code=? AND VNo=? AND Vprefix=?
DELETE FROM HallBook WHERE Site_Code=? AND VNo=? AND Vprefix=?

-- banquet_ops.py
SELECT MAX(VNo) FROM Voucher_Type WITH (UPDLOCK, HOLDLOCK) -- WRONG table (should be HallBook/HallSale1)
SELECT MAX(Sno) FROM HallBook1 WHERE DocId=?
INSERT INTO HallBook1 (DocId,Sno,Vtype,VNo,Site_Code,Vprefix,Vdate,PartyCode,...,LogSite_Code)
DELETE FROM HallBook1 WHERE DocId=? AND Sno=?
SELECT ... FROM VenueOcc WHERE FPDocid=? ORDER BY FromDate
INSERT INTO VenueOcc (FPDocid,VenuCode,FromDate,ToDate,FromTime,ToTime,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)
DELETE FROM VenueOcc WHERE FPDocid=? AND VenuCode=?
SELECT Sum(AmtCr-AmtDr) FROM PayChargeH WHERE VType In ('AD','AR') AND ContraDocId=?
```

### 2.3 Gap table

| # | VB6 | Python | Severity | Fix (SAME SQL) |
|---|---|---|---|---|
| B-G1 | `LOGSITE_CODE in ('<site>')` on every HallBook/Inquiry/MarketSeg/VenueMast/BussSource/FunctionType lookup + `Voucher_Type↔Voucher_Prefix` JOIN with `LOGSITE_CODE` | `hall_booking.list` uses `WHERE Site_Code=? ORDER BY VNo DESC` (no LogSite), `banquet_masters` VENFEATURES no site filter | HIGH | Add `WHERE LogSite_Code=?` (or `in (?, 'HO')` for masters) to all HallBook reads; add `AND LogSite_Code=?` to `_next_vno` MAX |
| B-G2 | HallBook/HallSale numbering via `Voucher_Prefix` (FY window) + `LASTVOU.ENAME='HBK'/'IDC'` per LogSite_Code | `banquet_ops._next_vno` does `SELECT MAX(VNo) FROM Voucher_Type` (wrong source!), `hall_booking._next_vno` only `MAX(VNo) WHERE Site_Code` (no LogSite, no FY) | HIGH | Restore `Select VT.Number_Method...Where VP.V_Type='HBK' AND ? BETWEEN Date_From AND Date_To AND VP.SITE_CODE=? AND VP.LOGSITE_CODE=?` then `UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='HBK' AND Prefix=?` and `LASTVOU` INSERT/UPDATE per VB6 |
| B-G3 | Delete guard: `SELECT Count(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId='<docid>'` — block delete; then cascade `HallBook`, `HallBook1`, `VenueOCC` in same transaction | `hallbook_delete` only `DELETE FROM HallBook WHERE DocId=?` (no VenueOCC/PayChargeH guard) | HIGH | Pre-delete: `SELECT Count(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId=? AND LogSite_Code=?`; if >0 raise; then `DELETE FROM HallBook1 WHERE DocId=?`; `DELETE FROM VenueOCC Where FPDocID=?`; `DELETE FROM HallBook Where Docid=?` same transaction |
| B-G4 | Venue clash: `Select Count(*) From VenueOCC S WHERE LogSite_Code='<site>' And (FromDate<=? AND ToDate>=?) And VenuCode='...'` | `venueocc_insert` no clash check | MEDIUM | Before insert: `SELECT COUNT(*) FROM VenueOCC WHERE LogSite_Code=? AND VenuCode=? AND NOT (ToDate < ? OR FromDate > ?)`; if >0 block |
| B-G5 | `HallSale1` → `HallSale2` lines + `HallStock` costing (`HallChefPreCosting` inserts HallStock per menu item) + `PayChargeH (AD/AR)` advance sync | `hall_booking` covers HallSale1 header only; `banquet_ops` HallSale2 insert exists but HallStock/Costing path not wired | MEDIUM | Keep SQL: after HallSale1 insert, loop `INSERT INTO HallSale2 (DocId,Sno,SNo1,Vtype,VNo,Site_Code,Vprefix,Vdate,Item,QtyIss,Unit,Rate,Amount,TaxPer,TaxAmt,DiscPer,DiscAmt,VoidYN,Remarks,LogSite_Code)`; for chef costing: `INSERT INTO HallStock (...) LogSite_Code` |
| B-G6 | SMS on banquet save: `Select BanqBookingMsg ... from SMSEnviro WHERE LOGSITE_CODE=?` + `Select TxtMsg,MobileNo from EmailSMSForward WHERE LOGSITE_CODE=? And Type='BanqBooking'` | `banquet_ops` never queries SMSEnviro/EmailSMSForward | LOW | Add post-save hook with verbatim SELECTs, no schema change |

### 2.4 Fixed workflow
```python
# HallBook save (VB6 HallBooking.frm:4867+4950+4960)
# 1) privilege
db.query("SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Banquet Booking'", (user,comp))
# 2) prefix + lastvou
vp = db.query("Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type='HBK' AND ? BETWEEN VP.Date_From AND VP.Date_To", (SITE_CODE,SITE_CODE,vdate))
next_no = vp[0].Start_Srl_No + 1
# 3) clash
cnt = db.query("Select Count(*) From VenueOCC S WHERE LogSite_Code=? And ? BETWEEN FromDate AND ToDate And VenuCode=?", (SITE_CODE, fromdate, venue))
# 4) cn transaction: INSERT HallBook → loop HallBook1 → loop VenueOCC → UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='HBK' AND Prefix=? → UPDATE/INSERT LASTVOU
# 5) delete: SELECT Count(*) FROM HallSale1 WHERE Vtype='IDC' AND BookDocId=? AND LogSite_Code=? → if 0 then DELETEs cascade
```

### 2.5 Frontend/Backend notes
- **Backend P0:** Fix `_next_vno` source (HallBook not Voucher_Type), add LogSite_Code, wire VenueOCC clash + cascade delete.
- **Frontend:** `ui/hall_booking_ui.py` grid for `HallBook1` items (`Item/QtyIss/Rate/Amount/TaxPer`) missing `Remarks/VoidYN`; add Venue multi-select (FromDate/ToDate/FromTime/ToTime) chip; `Banquet masters` ui currently VenueFeatures/CatalogMast combos lack `LogSite_Code` filter chip.

---

## 3) MEMBERS — MemCatMast / MembershipMast / MemVisitEntry / MemBill / FacilityBilling

### 3.1 VB6 SQL verbatim

| VB6 file | Verbatim SQL |
|---|---|
| `MemCatMast.frm` | `SELECT * FROM MemCatMast WHERE LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO' ORDER BY Code` ; `SELECT COUNT(*) FROM MemCatMast WHERE Code='<code>'` ; `Insert Into MemCatMast(Code,Name,ShortName,Subscription,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(...)` ; `UPDATE MemCatMast SET Name='...' WHERE Code='...'` |
| `MembershipMast.frm` | `SELECT R.Code As SearchCode,R.*,S.PicPath,S.IdPicPath SigPath,S.Name MemberName From SmartCardRegistration R Left Join GuestProf S On R.MemberCode=S.Code where R.CardType='Cash Card' And R.Site_Code='<site>'` (facility billing path) ; `SELECT Code As SearchCode, Name FROM MemCatMast WHERE (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` ; `Insert Into MemberFamily (SubCode,SNo,Relationship,Name,Gender,DOB,Phone,Mobile,Email,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE)` ; `INSERT INTO MemBill (Docid,vdate,vno,vprefix,Vtype,MemCode,MemCatCode,cardno,MthYear,NetAmount,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,BillDate,RoundOff,Amount)` with `SELECT MAX(vno) FROM MemBill WHERE Site_Code='...'` |
| `MemVisitEntry.frm` | `SELECT * FROM MemVisitEntry WHERE LogSite_Code='<site>'` ; `INSERT INTO MemVisitEntry (DocId,VisitDate,MemCode,FacilityCode,Pax,Amount,U_Name,U_EntDt,U_AE,LogSite_Code)` |
| `MemFacilityBilling.frm` | `SELECT * FROM FacilityBill WHERE Docid='<docid>'` ; `INSERT INTO FacilityBill (Docid,VType,Vdate,Vno,Vprefix,Vdate,VType,MemCode,FacilityCode,Rate,Amount,NetAmount,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)` ; `INSERT INTO FacilityBill1 (Docid,Vno,Sno,VType,Vdate,Vprefix,PartyCode,RestCode,FacilityCode,Rate,Amount,U_Name,U_EntDt,Site_Code,LogSite_Code)` ; `INSERT INTO SunTranFacility ...` + `Select IsNull(Sum(Amount),0) From FacilityBill Where LOGSITE_CODE='...' AND MemCode='...'` |
| `MemberModule.bas` | `Select * From Enviro WHERE LOGSITE_CODE='<site>'` → `SMSEnviro` ; `SELECT Code,Name FROM MemCatMast WHERE (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` ; `SELECT FacilityCode,Rate FROM MemCatFacility WHERE CatCode='<code>' AND LOGSITE_CODE='<site>'` |

### 3.2 Python SQL

```sql
-- members_masters.py
SELECT MemCatMast ORDER BY Code  -- no LOGSITE filter
SELECT 1 FROM MemCatMast WHERE Code=?  -- no LOGSITE
INSERT INTO MemCatMast (Code, Name, ShortName, Subscription, ... Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code)
UPDATE MemCatMast SET Name=? ... WHERE Code=?  -- no LogSite in WHERE
DELETE FROM MemCatMast WHERE Code=?

-- member_billing.py
SELECT * FROM MemberFamily WHERE SubCode=? ORDER BY SNo  -- no LogSite
SELECT MAX(SNo) FROM MemberFamily WHERE SubCode=?
INSERT INTO MemberFamily (SubCode,SNo,Relationship,Name,Gender,DOB,Phone,Mobile,Email,Site_Code,LogSite_Code,...)
SELECT * FROM MemBill WHERE Site_Code=? ORDER BY vno DESC
SELECT MAX(vno) FROM MemBill WHERE Site_Code=?  -- no LogSite, no Vprefix
INSERT INTO MemBill (Docid,vdate,vno,vprefix,Vtype,MemCode,MemCatCode,cardno,MthYear,NetAmount,Site_Code,LogSite_Code,...)

-- facility_billing.py
SELECT * FROM FacilityBill WHERE Site_Code=? ORDER BY Vno DESC  -- OK but no HO
SELECT MAX(Vno) FROM FacilityBill WITH (UPDLOCK, HOLDLOCK) WHERE Site_Code=? -- no LogSite/Vprefix
INSERT INTO FacilityBill (Docid,VType,Vdate,Vno,Vprefix,FacilityCode,MemCode,...,LogSite_Code)
SELECT * FROM FacilityBill1 WHERE Docid=? ORDER BY Sno  -- no LogSite filter
INSERT INTO SunTranFacility (DocId,Sno,Vtype,VNo,Vdate,PartyCode,SunCode,...,SunAppDate,RevCode,RestCode,DelFlag,SiteCode,LogSite_Code)
```

### 3.3 Gap table

| # | VB6 | Python | Severity | Fix |
|---|---|---|---|---|
| M-G1 | Masters (`MemCatMast`, `FacilityMast`, `MembershipMast`) always `WHERE (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` | `members_masters.py` `list_all` no filter; `get/exists` no OR HO | HIGH | Add `WHERE (LogSite_Code=? OR LogSite_Code='HO')` to all reads; writes keep `LogSite_Code=?` |
| M-G2 | `MemBill`/`FacilityBill` numbering via `Voucher_Prefix` + `LASTVOU` per `VType='MB'/'FB'` | `MAX(vno) WHERE Site_Code=?` without LogSite/Vprefix/VType FY window | HIGH | Restore `Select VT.Number_Method...Where VP.V_Type='MB' AND ? BETWEEN Date_From AND Date_To AND VP.SITE_CODE=? AND VP.LOGSITE_CODE=?` + `UPDATE Voucher_Prefix Set Start_Srl_No` |
| M-G3 | `MemberFamily` per `SubCode` with `SNo` auto-increment + `CardNo` uniqueness via `SubGroup.CompanyType In (Select Code From MemCatMast Where LOGSITE_CODE...)` | `member_billing.insert_family` MAX(SNo) without LogSite_Code, no card uniqueness check | MEDIUM | Add `SELECT MAX(SNo) FROM MemberFamily WHERE SubCode=? AND LogSite_Code=?` and `SELECT 1 FROM SubGroup WHERE CardNo=? AND LogSite_Code in (?, 'HO')` guard |
| M-G4 | `MemVisitEntry` drives `FacilityBill` line rate from `MemCatFacility` (`SELECT FacilityCode,Rate FROM MemCatFacility WHERE CatCode=? AND LOGSITE_CODE=?`) | No Facility rate lookup; amount passed from UI as-is | MEDIUM | Add lookup `SELECT Rate FROM FacilityMast WHERE Code=? AND (LogSite_Code=? OR 'HO')` before FacilityBill1 insert |
| M-G5 | `SunTranFacility` posting per FacilityBill (VB6 `MemFacilityBilling` loops `FacilityBill2` → `SunTranFacility` with `RestCode/RevCode`) | `facility_billing` has `SunTranFacility` helpers but not called from `insert_fbill` | LOW | Wire `insert_fbill` → `insert_sunfac` in same transaction |
| M-G6 | `menuHelp` per `MemCatMast`/`MembershipMast`/`MemVisitEntry` (`[Option]='Member Category'` etc) | No menuHelp guard | HIGH | Add `SELECT Param_Str, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Member Category'` |

### 3.4 Fixed workflow
```sql
-- MemCatMast list (verbatim)
SELECT * FROM MemCatMast WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO') ORDER BY Code
-- FacilityBill numbering
Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type='FB' AND ? BETWEEN VP.Date_From AND VP.Date_To
UPDATE Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='FB' AND Prefix=?
INSERT INTO FacilityBill (Docid,VType,Vdate,Vno,Vprefix,MemCode,FacilityCode,Rate,Amount,NetAmount,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)
-- SunTranFacility per line
INSERT INTO SunTranFacility (DocId,Sno,Vtype,VNo,Vdate,PartyCode,SunCode,Limit,DispName,ROff,CalcFormula,SValue,Amount,BaseAmount,U_Name,U_EntDt,U_AE,SunAppDate,RevCode,RestCode,DelFlag,SiteCode,LogSite_Code) VALUES (?)
```

### 3.5 Frontend/Backend notes
- **Backend P0:** Add HO fallback to `members_masters.py` (3 masters), `member_billing` family/memBill, `facility_billing` facilityBill; restore Voucher_Prefix numbering.
- **Frontend:** `ui/hr_members_ui.py` currently merges HR+Mems in one file, grids for `MemberFamily` (SNo/Relationship/Name/Gender/DOB/Phone) missing `U_Name` footer; `FacilityBilling` ui has `Amount` calc but no `MemCatFacility` rate chip.

---

## 4) HR/PAYROLL — Employee / Attend / Salary / Desig / EmpCategory

### 4.1 VB6 SQL verbatim

| VB6 file | SQL |
|---|---|
| `PrEmployee.frm:3625` | `SELECT Employee.Code as SearchCode, Employee.Name, Employee.Sex, Employee.F_Name, cast(Employee.Birth_Date as varchar(11)) as BirthDate, Employee.Add1, Employee.Add2, Employee.Marital, cast(Employee.Joining_Date as varchar(11)) as JoiningDate, cast(Employee.Resign_Date as varchar(11)) as ResignDate, Employee.Department, Employee.Designation, Employee.Category, Employee.Basic ... FROM Employee ... Where (Employee.LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` |
| `PrEmployee.frm:3940` | `Select IsNull(Max(CAST(SUBSTRING(Code,3,6) AS INT)),1)+1 AS MyCode From Employee where Site_Code='<site>'` → `INSERT INTO EMPLOYEE (Code,Name,F_Name,Add1,Add2,Spouse,Qualification,ESI_Code,PF_Code,Basic,DA,HRA,Income_Tax,Other_Allow,Other_Deduc,Conveyance,Medical,LTA,Curr_PF_Balance,OP_PF_Balance,OP_Loan,OP_Inst,OP_Advance,Tot_CL_Allow,Tot_EL_Allow,OP_Earned,OP_Casual,Curr_Earned,Curr_Casual,Department,Designation,Category,Joining_Date,Birth_Date,Sex,Marital,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values (...)` ; `UPDATE EMPLOYEE SET Name=... WHERE CODE='...'` |
| `PrEmployee.frm:3022` | `SELECT SubCode as Code, Name FROM SubGroup where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') ORDER BY Name` + `SELECT Code, Name FROM EmpCategory where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` — dropdowns |
| `PrEmployee.frm:3475` | Delete guard: `Select * From Salary Where site_code='<site>' and Emp_Code='<code>'` → block if exists; similarly `Attend`, `Attendence`, `Loan`, `Leave_Ench`, `OverTime` |
| `PrDesigMast.frm:345` | `SELECT Code,Name FROM Desig where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') ORDER BY Name` ; `SELECT D.*,D.Code as SearchCode FROM Desig D where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') Order by Name` ; `Select IsNull(Max(CAST(SUBSTRING(Code,3,3) AS INT)),1)+1 AS MyCode From Desig where Site_Code='<site>'` → `Insert Into Desig(Code,Name,Site_Code,U_Name,U_EntDt,U_AE,Logsite_Code)` |
| `PrCategoryMast.frm:505` | `SELECT Code,Name FROM EmpCategory where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` ; `Select IsNull(Max(CAST(SUBSTRING(Code,3,3) AS INT)),1)+1 AS MyCode From EmpCategory where Site_Code='<site>'` |
| `prAttend.frm:551` | `Select A.V_Date,A.V_Prefix as [Year] ,E.Name As EmployeeName,A.FirstShift,A.SecondShift From Attend A left join Employee E on A.Emp_Code = E.Code Where A.V_Prefix='<FY>' And A.V_Date BETWEEN ...` ; `Select (V_Prefix+'-'+ LTRIM(RTRIM(CONVERT(Varchar(11), A.V_Date, 103)))+'-'+Emp_Code) as SearchCode, A.* , E.Name ... From Attend A Left Join Employee E on A.Emp_Code = E.Code Left Join Depart On Depart.Code=E.Department` |
| `prAttend.frm:1627` | `Insert Into Attend(V_Prefix,V_Date,Emp_Code,FirstShift,SecondShift,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values ('<FY>',<date>,'<emp>','P/A/L',...,'<site>',...,'<site>')` + `Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where (VP.SITE_CODE='<site>' AND VP.LOGSITE_CODE='<site>' AND VP.V_Type='AT' ...)` |
| `prSalCreate.frm:1065` | `Select E.*,EC.Name,EC.Type From Employee E Left Join EmpCategory EC On E.Category=EC.Code Where E.LOGSITE_CODE='<site>'` ; `Select Count(*) From Salary Where LOGSITE_CODE='<site>' AND Mth_Year='<mmyyyy>' And Emp_Code='<code>'` ; `select count(*) from holiday where LogSite_Code='<site>' AND datepart(dw,vdate)<>'1' and month(VDate)='<mm>' and year(VDate)='<yyyy>'` ; `Select * From Attend Where LOGSITE_CODE='<site>' AND Emp_Code='<code>' And Month(V_Date)='<mm>'` |
| `prSalCreate.frm:1684` | `Insert Into Ledger(DocId,V_SNo,V_Type,V_Prefix,V_No,Site_Code,V_Date,SubCode,ContraSub,AmtCr,Narration,mth_year,Emp_Code,U_Name,U_EntDt,U_AE,GROUPCODE,GROUPNATURE,LogSite_Code) Values (...)` (salary posting to Finance per employee) + `Select IsNull(Sum(Amount),0) From Loan Where LOGSITE_CODE='<site>' AND V_Type='LO' And Emp_Code='<code>'` (recovery) |

### 4.2 Python SQL

```sql
-- hr_masters.py
SELECT EmpCategory ORDER BY Code  -- no HO
SELECT 1 FROM EmpCategory WHERE Code=?  -- no HO
INSERT INTO EmpCategory (Code, Name, Type, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code)
UPDATE EmpCategory SET Name=?, Type=? WHERE Code=?  -- no LogSite
DELETE FROM EmpCategory WHERE Code=?
-- same for Desig, Holiday (Holiday uses CONVERT(varchar,Vdate,23)=?)

-- hr_payroll.py
SELECT * FROM Employee ORDER BY Code  -- no LOGSITE
SELECT 1 FROM Employee WHERE Code=?
INSERT INTO Employee (Code, Name, Sex, Designation, Category, Department, Basic, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code)
SELECT * FROM Salary WHERE Site_Code=? ORDER BY Emp_Code DESC  -- only Site_Code
SELECT * FROM Salary WHERE Mth_Year=? AND Emp_Code=?
INSERT INTO Salary (Mth_Year,Emp_Code,Work_Day,CL,Leave,Sunday,Holiday,Absent,Basic,...Net_Salary,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)
DELETE FROM Salary WHERE Mth_Year=? AND Emp_Code=?
INSERT INTO Loan (Sr_No, V_Type, V_Date, Emp_Code, Amount, Installment, Remark, AC_Code, Mth_Year, Site_Code, LogSite_Code, ...)
INSERT INTO Leave_Ench (Sr_No,L_Date,Emp_Code,Leave_Ench,Amt_Ench,AC_Code,Site_Code,LogSite_Code)
INSERT INTO OverTime (EmpCode,OTDate,OTime,Site_Code,LogSite_Code,Amount,Remark,OTRate)
```

### 4.3 Gap table

| # | VB6 | Python | Severity | Fix |
|---|---|---|---|---|
| H-G1 | Every master `EmpCategory`, `Desig`, `Employee`, `SubGroup` dropdown uses `WHERE (LOGSITE_CODE='?' OR LOGSITE_CODE='HO')` + `ORDER BY Name` | `hr_masters.list_all` / `hr_payroll.employee_list` no filter; `Desig`/`EmpCategory` reads have no HO | HIGH | Add `WHERE (LogSite_Code=? OR LogSite_Code='HO') ORDER BY Name` to all `list_all`/`get` |
| H-G2 | `Employee.Code` next via `Select IsNull(Max(CAST(SUBSTRING(Code,3,6) AS INT)),1)+1 AS MyCode From Employee where Site_Code='?'` (6-digit numeric suffix, prefix like `EM`) | `hr_payroll` insert doesn't auto-gen code; expects caller-provided; no MAX check | MEDIUM | Add helper `next_emp_code`: `SELECT IsNull(Max(CAST(SUBSTRING(Code,3,6) AS INT)),0)+1 AS MyCode From Employee where Site_Code=?` then `EM + LPAD(...,6,'0')` |
| H-G3 | Delete guard: 6 checks `Select * From Salary/Attend/Attendence/Loan/Leave_Ench/OverTime Where site_code='?' and Emp_Code='?'` → block delete if any >0 | `emp_delete` only deletes (`WHERE Code=?`), no guard; `prEmployee.frm:3219` cascade deletes would orphan | HIGH | Before `DELETE FROM Employee WHERE Code=? AND LogSite_Code=?`, run 6 `SELECT COUNT(*) FROM Salary WHERE Site_Code=? AND Emp_Code=?` etc; if any >0 raise |
| H-G4 | `Attend` inserted with `V_Prefix` (FY) + `Voucher_Type`/`Voucher_Prefix` FY window + `FirstShift/SecondShift='P/A/L/C'` enum, `LogSite_Code` | `hr_payroll.insert_attendence` uses `Mth_Year` (MMMyyyy) string table `Attendence`, not `Attend(V_Prefix,V_Date,FirstShift,SecondShift)` | HIGH — wrong table | Add `Attend` table helpers: `INSERT INTO Attend(V_Prefix,V_Date,Emp_Code,FirstShift,SecondShift,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code)` with Voucher_Prefix lookup per VB6 |
| H-G5 | `Salary` creation does: ` holiday count` (`datepart(dw,vdate)<>'1'` Sunday exclude) + `Attend` aggregation + `OverTime` sum + `Loan` IsNull(Sum) (V_Type='LO' minus 'LR') + `INSERT INTO Loan (V_Type='LO'→'LR')` + `INSERT INTO Ledger (V_Type='SL'/'LR1'/'AR2')` per employee + `UPDATE Voucher_Prefix` + `UPDATE Employee Curr_Earned/Curr_Casual/PF` | `hr_payroll.insert_salary` only inserts Salary row (no Ledger, no Loan recovery, no holiday/attend calc, no Voucher_Prefix, no Employee update) | HIGH — salary calc & posting missing | Restore VB6 steps: `select count(*) from holiday where LogSite_Code=? AND datepart(dw,vdate)<>'1' and month(VDate)=? and year(VDate)=?` ; `Select * From Attend Where LOGSITE_CODE=? AND Emp_Code=?` ; `Select IsNull(Sum(Amount),0) From Loan Where LOGSITE_CODE=? AND V_Type='LO' ...` ; then loop `INSERT INTO Ledger (DocId,V_SNo,V_Type,V_Prefix,V_No,Site_Code,V_Date,SubCode,ContraSub,AmtCr/AmtDr,Narration,mth_year,Emp_Code,LogSite_Code)` + `UPDATE Voucher_Prefix Set Start_Srl_No` + `Update Employee Set Curr_Earned+=...,Curr_Casual+=...,Curr_PF_Balance+=...` |
| H-G6 | `menuHelp` per Employee (`[Option]='Employee Master'`), Desig/Category etc | No menuHelp | HIGH | Guard before insert/update/delete |
| H-G7 | `INSERT INTO Employee` lists 35+ cols (F_Name,Spouse,ESI/PF code, Basic/DA/HRA, OP balances, Joining/Birth date, etc) | `hr_masters.emp_insert` only `Code,Name,Sex,Designation,Category,Department` | MEDIUM | Keep minimal for PYT* tests, but add optional cols mapping; doc that VB6 full profile needs 30 cols (no schema change — just pass through) |

### 4.4 Fixed workflow (Salary create)
```sql
-- Count guard before Employee delete
SELECT COUNT(*) FROM Salary WHERE Site_Code=? AND Emp_Code=?;
SELECT COUNT(*) FROM Attend WHERE Site_Code=? AND Emp_Code=?;
-- (4 more tables) → if any>0 block
-- Attend insert
Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type='AT' AND ? BETWEEN VP.Date_From AND VP.Date_To
INSERT INTO Attend(V_Prefix,V_Date,Emp_Code,FirstShift,SecondShift,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,?,?,?,getdate(),'A',?)
UPDATE Voucher_Prefix Set Start_Srl_No=Start_Srl_No+1 Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type='AT' AND Prefix=?
-- Salary posting per employee
SELECT IsNull(Sum(Amount),0) FROM Loan WHERE LOGSITE_CODE=? AND V_Type='LO' AND Emp_Code=?
SELECT IsNull(Sum(Amount),0) FROM Loan WHERE LOGSITE_CODE=? AND V_Type IN('LR','LR1') AND Emp_Code=?
INSERT INTO Ledger(DocId,V_SNo,V_Type,V_Prefix,V_No,Site_Code,V_Date,SubCode,ContraSub,AmtCr,Narration,mth_year,Emp_Code,U_Name,U_EntDt,U_AE,GROUPCODE,GROUPNATURE,LogSite_Code) VALUES (?)
UPDATE Employee Set Curr_Earned=IsNull(Curr_Earned,0)+?, Curr_Casual=IsNull(Curr_Casual,0)+?, Curr_PF_Balance=IsNull(Curr_PF_Balance,0)+? WHERE Code=? AND LogSite_Code=?
INSERT INTO Salary(Mth_Year,Emp_Code,Work_Day,Leave,Sunday,Holiday,Absent,Basic,DA,HRA,...,Net_Salary,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE) VALUES (?)
```

### 4.5 Frontend/Backend notes
- **Backend P0:** Add HO filters, Employee next code, delete guards, Attend table helpers, Salary Ledger posting + Voucher_Prefix.
- **Frontend:** `ui/hr_members_ui.py` tabs `Employee/Attend/Salary/Loan` but `Attend` UI posts to `Attendence(Mth_Year,Attn_Str)` not `Attend(V_Prefix,FirstShift,SecondShift)` — schema mismatch; `hr_payroll_ui` needs `FirstShift/SecondShift` dropdowns (P/A/L) and FY picker, plus Salary `Mth_Year` search `Salary.Where Logsite_code=? and Mth_Year='MMMyyyy'` with department filter `Emp_Code In (Select Code From Employee Where site_code=? And Department=?)`.

---

## 5) HOUSEKEEPING — ComplaintDetail / RoomBlockOut / RoomStat

### 5.1 VB6 SQL verbatim

| VB6 file | SQL |
|---|---|
| `FrmComplaintMast.frm:808` | `SELECT CD.Code AS Scode,CD.Category AS CatCode,CD.CDate AS CDate,CD.CTime AS CTime,CC.Category AS Category,CD.Description AS Description,CD.Depart AS Depart,CD.UName AS UName,CD.Status AS Status,CD.Site_Code,CD.LogSite_Code FROM ComplaintDetail CD Left JOIN ComplaintCategory CC ON CD.Category =CC.Code WHERE CD.LOGSITE_CODE='<site>'` |
| `FrmComplaintMast.frm:1049` | `Select C.Code AS SearchCode, C.Description As Description, C.UName AS ComplaintBy, Depart.Name AS Department FROM ComplaintDetail C Inner JOIN Depart ON C.Depart = Depart.Code Where C.LogSite_Code='<site>' ORDER BY C.Code` |
| `FrmComplaintMast.frm:1217` | `Select IsNull(Max(CAST(SUBSTRING(Code,3,4) AS INT)),1)+1 AS MyCode From ComplaintDetail Where Site_Code='<site>'` → `Insert Into ComplaintDetail(Code,Category,CDate,CTime,Description,Depart,UName,Status,Site_Code,U_EntDt,U_AE,LogSite_Code) Values(...)` ; `Insert Into ComplaintCategory(Code,Category,Site_Code,U_EntDt,U_AE,LogSite_Code)` |
| `FrmComplaintClearing.frm:589` | `UPDATE ComplaintDetail SET Status='Solved', ClearingDate=<now>, ClearingPerson='<user>',Description='<desc>' WHERE Code='<code>' AND LogSite_Code='<site>'` ; counter `UPDATE ComplaintDetail SET Status='UnSolved', ClearingDate=NULL, ClearingPerson='',Description='...' WHERE Code='...'` |
| `HHouseKeeping.frm:762` | `delete from RoomBlockOut where RoomCode='<room>' And Type='O' AND LOGSITE_CODE='<site>'` ; `Insert into RoomBlockOut (RoomCode,Reasons,FromDate,ToDate,Type,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code,VTime) Values (...)` ; `Update RoomMast set RoomStat='<stat>' where (LOGSITE_CODE='<site>') and code='<room>'` |
| `HHouseKeeping.frm:1199` | `Select * from RoomBlockOut where (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') and Type In ('O','M') And RoomCode='<room>'` |
| `HHouseKeeping.frm:1259` | `SELECT Count(*) FROM RoomOcc WHERE (LOGSITE_CODE='<site>') and Type Not IN ('O','C') AND (CHKINDATE < '<date2>' AND CHKOUTDATE > '<date1>')` — checkout clearance |
| `HKRoomBlock.frm:1221` | `Insert into RoomBlockOut (RoomCode,Type,Site_Code,U_Name,FromDate,LogSite_Code,VTime) Values ('<room>','M','<site>',...,'<site>',getdate())` — maintenance block |
| `HKRoomBlock.frm:1781` | `SHAPE {select R.Code as RoomNo,RC.Code as RoomCat,RC.Name as Category,RL.Rate2 as Rate from (RoomMast R left Join RoomCat RC on RC.Code=R.RoomCat) ... } APPEND ({SELECT Distinct r.Code as RoomNo, ...})` — hierarchical room list (VB6 Data Shape) |
| `HKRoomBlock.frm:1848` | `Select RoomNO as RoomCode,ChkinDt as FromDate ,dATEdiff(D,ChkInDt,DepDate) as Days,GuestProf.Name as Reasons,dateadd(D,dATEdiff(D,ChkInDt,DepDate),chkindt) as TODate From RoomOccDet left join GuestProf on GuestProf.Code=RoomOccDet.GuestProf Where RoomOccDet.Logsite_Code='<site>'` + `Select RoomNO as RoomCode,ArrDate as FromDate ,... From ViewBooking B left join GuestProf ... Where B.Logsite_Code='<site>'` — board for block chart |

### 5.2 Python SQL

No dedicated `housekeeping.py` core. Coverage split:
- `room_occ.py`: `SELECT ... FROM RoomOcc WHERE DocId=?` / `WHERE RTRIM(RoomNo)=? AND LOGSITE_CODE? (no)` ; `SELECT DISTINCT RTRIM(RoomNo) FROM RoomOcc WHERE Site_Code=?` ; `SELECT ... FROM RoomMast ... WHERE (LOGSITE_CODE=? or HO)` (partial via `get_available_rooms`).
- `hr_masters.py`/`roomstatus.py` elsewhere.
- `ComplaintDetail` / `RoomBlockOut` have **zero** Python core (grep finds no file).

```sql
-- room_occ.py
SELECT DocId, SNo, FolioNo, Vtype, Site_Code, RoomNo, LogSite_Code FROM RoomOcc WHERE DocId=?
INSERT INTO RoomOcc (DocId, SNo, FolioNo, Vtype, Site_Code, RoomNo, LogSite_Code, ChkInDate, ChkOutDate, Type) VALUES (...)
UPDATE RoomOcc SET ChkOutDate=?, ChkOutTime=? WHERE DocId=? AND SNo=?
DELETE FROM RoomOcc WHERE DocId=?
-- no ComplaintDetail, no RoomBlockOut Type='O'/'M'/'C', no RoomMast stat update
```

### 5.3 Gap table

| # | VB6 | Python | Severity | Fix |
|---|---|---|---|---|
| HK-G1 | `ComplaintDetail` master + `ComplaintCategory` with `Category` dropdown `WHERE (LOGSITE_CODE='?' OR 'HO')`, next code `SUBSTRING(Code,3,4)` + insert with `CDate/CTime/Status='Open'` | No `complaint_mast.py` / `complaint_ops.py` — feature absent | HIGH | Create `core/complaint.py`: `SELECT CD.Code AS Scode,... FROM ComplaintDetail CD Left JOIN ComplaintCategory CC ON CD.Category=CC.Code WHERE CD.LogSite_Code=?` ; `Select IsNull(Max(CAST(SUBSTRING(Code,3,4) AS INT)),0)+1 From ComplaintDetail Where Site_Code=?` → `INSERT INTO ComplaintDetail(Code,Category,CDate,CTime,Description,Depart,UName,Status,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE)` ; `UPDATE ComplaintDetail SET Status='Solved', ClearingDate=getdate(), ClearingPerson=? WHERE Code=? AND LogSite_Code=?` |
| HK-G2 | `RoomBlockOut` Type enum `'O'=OutOfOrder, 'M'=Maintenance, 'C'=Cleaning` with `FromDate/ToDate/VTime` + `RoomMast.RoomStat` update in same transaction | `room_occ.py` has no RoomBlockOut; `RoomMast` stat never updated | HIGH | Add `core/room_block.py`: `INSERT INTO RoomBlockOut (RoomCode,Reasons,FromDate,ToDate,Type,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE,VTime)` ; `DELETE FROM RoomBlockOut WHERE RoomCode=? AND Type=? AND LogSite_Code=?` ; `UPDATE RoomMast SET RoomStat=? WHERE Code=? AND LogSite_Code=?` same cn |
| HK-G3 | `LOGSITE_CODE='?' OR 'HO'` on `RoomMast`, `Depart`, `ComplaintCategory` lookups | `room_occ` available rooms missing HO fallback | MEDIUM | Add `WHERE (Mast.LogSite_Code=? OR Mast.LogSite_Code='HO')` to room lookups |
| HK-G4 | VB6 Shape query for room grid (RoomMast↔RoomCat↔RateList hierarchical) | Python has flat query only | LOW — UI parity only | Keep flat join `select R.Code as RoomNo,RC.Code as RoomCat,RC.Name as Category,RL.Rate2 as Rate from (RoomMast R left Join RoomCat RC on RC.Code=R.RoomCat) Left Join RateList RL on RL.RoomCat=RC.Code WHERE R.LogSite_Code=?` |
| HK-G5 | `menuHelp [Option]='Complaint Master' / 'House Keeping'` privilege | No guard | HIGH | Add menuHelp SELECT before ComplaintDetail/RoomBlockOut writes |

### 5.4 Fixed workflow
```sql
-- ComplaintDetail save
SELECT Param_Str, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Complaint Master'
Select IsNull(Max(CAST(SUBSTRING(Code,3,4) AS INT)),0)+1 AS MyCode From ComplaintDetail Where Site_Code=?
INSERT INTO ComplaintCategory(Code,Category,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE) VALUES (?)
INSERT INTO ComplaintDetail(Code,Category,CDate,CTime,Description,Depart,UName,Status,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE) VALUES (?,?,?,?,?,?,?, 'Open',?,?,getdate(),'A',?)
-- Clearing
UPDATE ComplaintDetail SET Status='Solved', ClearingDate=getdate(), ClearingPerson=?, Description=? WHERE Code=? AND LogSite_Code=?
-- Room block
INSERT INTO RoomBlockOut (RoomCode,Reasons,FromDate,ToDate,Type,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE,VTime) VALUES (?,?,?,?,?, ?,?, ?,getdate(),'A',?)
UPDATE RoomMast SET RoomStat=? WHERE Code=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')
```

### 5.5 Frontend/Backend notes
- **Backend:** Create `core/complaint.py` + `core/room_block.py` (reuse `room_occ.py` cn pattern); add HO fallback to `RoomMast` reads.
- **Frontend:** `ui/guest_services_ui.py` has `Complaint` tab but posts to `guest_services` not ComplaintDetail; `ui/roomstatus_ui.py` shows `RoomStat` grid but `OutOfOrder` button deletes from `RoomBlockOut` without `Type='O'` filter — add filter.

---

## 6) TELEPHONE — EPABX (TelCallType / TelExt / CallEntry)

### 6.1 VB6 SQL verbatim

| VB6 file | SQL |
|---|---|
| `TelCallTypeMast.frm:400` | `Select TelCallType.Code As SearchCode,TelCallType.CallType ,TelCallType.ShortName FROM TelCallType WHERE (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` ; `SELECT Code,CallType FROM TelCallType WHERE (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') ORDER BY CallType` |
| `TelCallTypeMast.frm:609` | `Insert Into TelCallType(Code,CallType,ShortName,ACCode,TaxStru,U_Name,U_EntDt,U_AE,sITE_cODE,LOGSITE_CODE) Values(...)` + `Insert Into RevMast(Code,Name,ShortName,ACCode,TaxStru,SysYN,AppMode,FieldType,U_Name,U_EntDt,U_AE,FlagType,FlagAmr,DeskCode,Type,Site_Code,LOGSITE_CODE)` (RevMast side) |
| `TelCallTypeMast.frm:991` | `SELECT distinct R.*,R.Code as SearchCode,S.SubCode as LedgerCode ,S.Name as LedgerName,T.Code as TaxCode,T.Name as TaxName FROM ((TelCallType R Left Join TaxStru T on T.Code=R.TaxStru) Left join Subgroup S on S.SubCode=R.ACCode) WHERE (R.LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` |
| `TelExtensionMast.frm:807` | `SELECT T.*,R.Code as RName,D.Name as DName FROM (TelExt as T LEFT JOIN RoomMast as R ON T.RoomNo=R.Code) LEFT JOIN Depart as D ON T.DepCode=D.Code WHERE (T.LOGSITE_CODE='<site>' or LOGSITE_CODE='HO')` ; `SELECT Code,Description FROM TelExt WHERE (LOGSITE_CODE='<site>' or LOGSITE_CODE='HO') ORDER BY Description` |
| `TelExtensionMast.frm:1232` | `Insert Into TelExt(CODE,DESCRIPTION,EXTENSION,TYPE,RoomNo,ShopNo,DepCode,PulseRate,U_Name,U_EntDt,U_AE,SITE_CODE,LOGSITE_CODE) Values(...)` |
| `TelCallEntry.frm:659` | `SELECT Code,CAST(Extension AS VARCHAR) AS EXT FROM TelExt ORDER BY Extension` (no LOGSITE — VB6 loads all) |
| `TelCallEntry.frm:664` | `SELECT * FROM EPABX_OUT` (staging) + `INSERT INTO EPABX_OUT (ID,V_TYPE,PNT_NO,Extension,RoomNo,ShopNo,DepCode,CALL_START_DATE,CALL_START_TIME,CALL_DURATION,DIALED_NO,CALL_INFO,CALL_RATE,CALL_AMT) VALUES (...)` + `UPDATE [COUNTER] SET CBOUT=CBOUT+1` (legacy counter) |
| `TelCallEntry.frm:1006` (via Module) | `Select TelExt.Code , TelExt.ShopNo & RoomMast.Code & Depart.Name as Name,TelExt.ShopNo as ShopNo, RoomMast.Code as RoomNo, Depart.Name as DepartNo FROM (TelExt LEFT JOIN RoomMast ON TelExt.RoomNo=RoomMast.Code) LEFT JOIN Depart ON TelExt.DepCode=Depart.Code WHERE TelExt.Extension='<ext>'` — resolve ext→room/dept |

### 6.2 Python SQL

```sql
-- epabx_masters.py
SELECT TelCallType ORDER BY Code  -- no HO
SELECT 1 FROM TelCallType WHERE Code=?
INSERT INTO TelCallType (Code, CallType, ShortName, ACCode, TaxStru, Site_Code, LogSite_Code, U_Name, U_EntDt, U_AE)
UPDATE TelCallType SET CallType=?, ShortName=?, ACCode=?, TaxStru=? WHERE Code=?
DELETE FROM TelCallType WHERE Code=?
-- same for TelCallCode, TelExt (all no HO / no RevMast side)

-- epabx_ops.py
SELECT ID, V_TYPE, PNT_NO, Extension, RoomNo, ShopNo, DepCode, CALL_START_DATE, CALL_START_TIME, CALL_DURATION, DIALED_NO, CALL_INFO, CALL_RATE, CALL_AMT, Site_Code, LogSite_Code FROM EPABX_Data WHERE 1=1 AND LogSite_Code=?  -- Python uses EPABX_Data, VB6 uses EPABX_OUT
INSERT INTO EPABX_Data (V_TYPE, PNT_NO, Extension, RoomNo, ShopNo, DepCode, CALL_START_DATE, CALL_START_TIME, CALL_DURATION, DIALED_NO, CALL_INFO, CALL_RATE, CALL_AMT, Site_Code, LogSite_Code) VALUES (...)
SELECT ... FROM EPABX_Data WHERE LogSite_Code=? ORDER BY ID DESC -- no COUNTER table
```

### 6.3 Gap table

| # | VB6 | Python | Severity | Fix (SAME SQL) |
|---|---|---|---|---|
| T-G1 | Masters `TelCallType`, `TelExt`, `TelCallCode` all `WHERE (LOGSITE_CODE='?' OR 'HO') ORDER BY ...` + `TaxStru`/`SubGroup` HO fallback | `epabx_masters.list_all` no filter; `Telext` browse no HO | HIGH | Add `WHERE (LogSite_Code=? OR LogSite_Code='HO')` to every `list_all`/`get` |
| T-G2 | `TelCallType` save writes **two** tables: `TelCallType` + `RevMast` (with `SysYN, AppMode, FieldType, FlagType, FlagAmr, DeskCode, Type`) — RevMast is rate/tax mirror | `calltype_insert` only writes `TelCallType`, never `RevMast` | HIGH — tax posting breaks | After `INSERT INTO TelCallType ...`, also `INSERT INTO RevMast(Code,Name,ShortName,ACCode,TaxStru,SysYN,AppMode,FieldType,U_Name,U_EntDt,U_AE,FlagType,FlagAmr,DeskCode,Type,Site_Code,LOGSITE_CODE) VALUES (...)` same transaction; on update do `UPDATE RevMast SET Name=? ... WHERE Code=? AND LogSite_Code=?` |
| T-G3 | Call entry staging table is `EPABX_OUT` (VB6) ; Python introduces `EPABX_Data` (migrated name) — VB6 also does `UPDATE [COUNTER] SET CBOUT=CBOUT+1` | Python queries `EPABX_Data` only, no `EPABX_OUT` nor `COUNTER` | MEDIUM | Keep VB6 table name `EPABX_OUT` for parity (or alias): add `SELECT * FROM EPABX_OUT` path; keep `EPABX_Data` as synonym; add `UPDATE COUNTER SET CBOUT=CBOUT+1` after insert (no schema change — COUNTER exists) |
| T-G4 | Extension resolve join `TelExt LEFT JOIN RoomMast ON TelExt.RoomNo=RoomMast.Code LEFT JOIN Depart ON TelExt.DepCode=Depart.Code WHERE TelExt.Extension=?` + `TelExt.ShopNo & RoomMast.Code & Depart.Name as Name` concatenation | `epabx_ops` has `search` with `Extension LIKE ?` but not the 3-way join | MEDIUM | Add `SELECT TelExt.Code, TelExt.ShopNo & RoomMast.Code & Depart.Name as Name, TelExt.ShopNo as ShopNo, RoomMast.Code as RoomNo, Depart.Name as DepartNo, RoomNo as RoomID FROM (TelExt LEFT JOIN RoomMast ON TelExt.RoomNo=RoomMast.Code) LEFT JOIN Depart ON TelExt.DepCode=Depart.Code WHERE TelExt.Extension=? AND (TelExt.LOGSITE_CODE=? OR 'HO')` |
| T-G5 | `SELECT COUNT(*) FROM TelCallCode WHERE CallTypeCode='<code>'` → block delete of TelCallType if in use | `calltype_delete` unconditional | MEDIUM | Before `DELETE FROM TelCallType WHERE Code=?`, run `SELECT COUNT(*) FROM TelCallCode WHERE CallTypeCode=? AND LogSite_Code=?`; if >0 block |
| T-G6 | `menuHelp [Option]='Call Type Master' / 'Extension Master' / 'Call Entry'` | No menuHelp | HIGH | Add same SELECT guard |

### 6.4 Fixed workflow
```sql
-- TelCallType save (verbatim 2-table)
SELECT COUNT(*) FROM TelCallCode WHERE CallTypeCode=?  -- delete guard
INSERT INTO TelCallType(Code,CallType,ShortName,ACCode,TaxStru,U_Name,U_EntDt,U_AE,sITE_cODE,LOGSITE_CODE) VALUES (?,?,?,?,?,?,getdate(),'A',?,?)
INSERT INTO RevMast(Code,Name,ShortName,ACCode,TaxStru,SysYN,AppMode,FieldType,U_Name,U_EntDt,U_AE,FlagType,FlagAmr,DeskCode,Type,Site_Code,LOGSITE_CODE) VALUES (?,?,?,?,?,?,?,?,getdate(),'A',?,?,?,?,?,?)
UPDATE RevMast SET Name=?, ShortName=?, ACCode=?, TaxStru=? WHERE Code=? AND LogSite_Code=?
-- EPABX_OUT entry
INSERT INTO EPABX_OUT (ID,V_TYPE,PNT_NO,Extension,RoomNo,ShopNo,DepCode,CALL_START_DATE,CALL_START_TIME,CALL_DURATION,DIALED_NO,CALL_INFO,CALL_RATE,CALL_AMT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
UPDATE COUNTER SET CBOUT=CBOUT+1
```

### 6.5 Frontend/Backend notes
- **Backend P0:** Add HO fallback, dual-write RevMast, EPABX_OUT alias.
- **Frontend:** `ui/epabx_ui.py` `CallEntry` grid currently `Extension/RoomNo/Duration/DialedNo/Rate/Amt` but VB6 has `PNT_NO, CALL_INFO, CALL_RATE` hidden cols + `Type` badge; add `Extension` dropdown populated via `SELECT Code,CAST(Extension AS VARCHAR) AS EXT FROM TelExt WHERE (LOGSITE_CODE=? OR 'HO') ORDER BY Extension`.

---

## 7) SMARTCARD — Registration / Recharge / Ledger

### 7.1 VB6 SQL verbatim

| VB6 | SQL |
|---|---|
| `SmartCardRegistration.frm:1518` | `Select IsNull(Max(CAST(Code AS INT)),0)+1 AS MyCode From SmartCardRegistration Where LOGSITE_CODE='<site>'` → `Insert Into SmartCardRegistration(Code,CardType,CardNo,Name,Addr,Phone,IssDate,ValidUpto,BlockedYN,SerialNo,Site_Code,U_Name,U_EntDt,U_AE,logSite_Code,MemberCode) Values(...)` |
| `SmartCardRegistration.frm:859` | `SELECT R.Code As SearchCode,R.*,S.PicPath,S.IdPicPath SigPath,S.Name MemberName From SmartCardRegistration R Left Join GuestProf S On R.MemberCode=S.Code where R.CardType='Cash Card' And R.Site_Code='<site>'` ; `SELECT R.Code As SearchCode,R.*,MF.PicPath,MF.SigPath,S.Name MemberName From SmartCardRegistration R Left Join MemberFamily MF On R.Code=MF.CardRegId Left Join Subgroup S On R.MemberCode=S.SubCode where R.Site_Code='<site>'` |
| `ModuleSmartCard.bas:917` | `Insert Into SmartCardLedger(DocId,VSNo,VType,VNo,VPrefix,Type,Site_Code,VDate,Code,HW_Id,AmtCr,AmtDr,Narration,U_Name,U_EntDt,U_AE,LogSite_Code,PreBalance) Values (...)` ; `Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where (VP.SITE_CODE='<site>' AND VP.LOGSITE_CODE='<site>' AND VP.V_Type='<vtype>')` then `Update Voucher_Prefix Set Start_Srl_No=... Where (SITE_CODE='<site>' AND LOGSITE_CODE='<site>' AND VP.V_Type='<vtype>')` |
| `SmartCardRecharge.frm:890` | `Update SmartCardRegistration Set CurrBal=R.CurrBal,SecurBal=R.SecurBal From SmartCardRegistration SCR Left Join (Select Q.Code,Sum(Q.RCARDC)+Sum(Q.CARDEXP) Currbal,Sum(Q.RCARDS) SecurBal From (Select Code,(Case When Type='RCARDC' Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End) RCARDC, ...) Q Group By Code) R On R.Code=SCR.Code Where R.Code=SCR.Code` — aggregated balance recalc |
| `ModuleSmartCard.bas:1435` | `Select Round(IsNull(CurrBal,0),2) CurrBal,Round(IsNull(SecurBal,0),2) SecurBal From SmartCardRegistration Where IsNull(CurrBalDiffChecked,0)=0 And Code='<code>'` → `Update SmartCardRegistration Set CurrBal=<calc> Where Code='<code>' And LogSite_Code='<site>'` → `Update SmartCardRegistration Set CurrBalDiffChecked=1 Where Code='<code>'` |
| `SmartCardRecharge.frm:1207` | `Update SmartCardRegistration Set LastTransAmt=<amt>,LastTransDate=<date>,CurrBal=IsNull(CurrBal,0)+<delta>,SecurBal=IsNull(SecurBal,0)+<sDelta> Where Code='<code>'` — done per recharge |

### 7.2 Python SQL

```sql
-- smartcard.py (simple)
INSERT INTO SmartCardRegistration (Code, CardType, CardNo, Name, Addr, Phone, IssDate, ValidUpto, BlockedYN, CurrBal, SecurBal, MemberCode, Site_Code, LogSite_Code, U_Name, U_EntDt, U_AE)
UPDATE SmartCardRegistration SET CardType=?, CardNo=?, ... CurrBal=?, SecurBal=?, MemberCode=? WHERE Code=?
DELETE FROM SmartCardRegistration WHERE Code=?

-- smartcard_ops.py (ops)
INSERT INTO SmartCardRegistration (Code,CardType,CardNo,Name,Addr,Phone,CashAmt,SecurityAmt,BlockedYN,SerialNo,Site_Code,LogSite_Code,CurrBal,MemberCode,RewardBal)
SELECT * FROM SmartCardRegistration WHERE Site_Code=? ORDER BY Code  -- no HO, missing IssDate/ValidUpto/CS logic
INSERT INTO SmartCardLedger (Code,VType,VNo,VDate,VPrefix,Type,Narration,AmtCr,AmtDr,DocId,VSNO,HW_Id,Site_Code,LogSite_Code,PreBalance,U_Name,U_EntDt,U_AE)
SELECT TOP ? * FROM SmartCardLedger WHERE Code=? ORDER BY VDate DESC
UPDATE SmartCardRegistration SET CurrBal=0, SecurBal=0, LastTransAmt=?, LastTransDate=getdate() WHERE Code=?  -- settle
INSERT INTO SmartCardReIssueDetail (Trans_Id,CardRegId,HW_Id,IssDate,ValidUpto,Remark,OldHW_Id,...,Site_Code,LogSite_Code)
```

### 7.3 Gap table

| # | VB6 | Python | Severity | Fix |
|---|---|---|---|---|
| SC-G1 | Registration next code `Max(CAST(Code AS INT))` per `LOGSITE_CODE` + memberCard duplicate guard `SELECT ... From GuestProf S Where S.POS=1 And S.Code Not In (Select Distinct MemberCode from SmartCardRegistration Where CardType='Cash Card' And LogSite_Code='?')` | `smartcard_ops.insert_reg` no MAX, no POS guard | HIGH | Add `Select IsNull(Max(CAST(Code AS INT)),0)+1 AS MyCode From SmartCardRegistration Where LOGSITE_CODE=?` before insert; add `GuestProf.POS=1` check with same subquery |
| SC-G2 | Ledger posting uses `Voucher_Type`→`Voucher_Prefix` FY window per `VType` (`RCARDC`, `RCARDS`, `CARDEXP`, `CARDADJ`) + `Start_Srl_No` bump | `insert_ledger` no Voucher_Prefix, no VNo auto | HIGH | Add `Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP ... Where VP.V_Type=? AND ? BETWEEN Date_From AND Date_To` then `Update Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type=? AND Prefix=?` |
| SC-G3 | Balance is **aggregated** from `SmartCardLedger` (`Sum(IsNull(AmtCr,0)-IsNull(AmtDr,0))` per `Type='RCARDC'/'RCARDS'/'CARDEXP'`) then `UPDATE SmartCardRegistration SET CurrBal=R.CurrBal,SecurBal=R.SecurBal From ... Left Join (Select Q.Code,Sum(...) ... ) R` — authoritative | Python `UPDATE SmartCardRegistration SET CurrBal=?` with passed delta (UI-supplied), no aggregation | HIGH — drift | Add function `recalc_bal(code)`: `SELECT Sum(CASE When Type='RCARDC' Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End)` etc as VB6:892 verbatim; then `Update SmartCardRegistration Set CurrBal=R.CurrBal,SecurBal=R.SecurBal From ...` |
| SC-G4 | `CurrBalDiffChecked` flag workflow (`Select Round(IsNull(CurrBal,0),2) ... Where IsNull(CurrBalDiffChecked,0)=0` → `Update ... CurrBalDiffChecked=1`) — migration guard | No flag handling | LOW | Add check `WHERE IsNull(CurrBalDiffChecked,0)=0` before recalc |
| SC-G5 | `LastTransAmt/LastTransDate` updated per recharge (`Update SmartCardRegistration Set LastTransAmt=?,LastTransDate=? ,CurrBal+=delta`) | `smartcard_ops` settle does `CurrBal=0` but recharge path via `insert_ledger` doesn't bump LastTrans | MEDIUM | After `INSERT INTO SmartCardLedger`, also `Update SmartCardRegistration Set LastTransAmt=?,LastTransDate=getdate(), CurrBal=IsNull(CurrBal,0)+?, SecurBal=IsNull(SecurBal,0)+? Where Code=? AND LogSite_Code=?` |
| SC-G6 | `LOGSITE_CODE` filter on every recharge balance query | `smartcard_ops.list` only `Site_Code=?`; ledger list no LogSite | HIGH | Add `WHERE LogSite_Code=?` (or `Site_Code=? AND LogSite_Code=?`) |

### 7.4 Fixed workflow
```sql
-- Registration (VB6 1518)
Select IsNull(Max(CAST(Code AS INT)),0)+1 AS MyCode From SmartCardRegistration Where LOGSITE_CODE=?
-- guard GuestProf POS
Select S.Code as Code,S.Name,S.MobileNo As SearchKey From GuestProf S Where S.POS=1 And S.Code Not In (Select Distinct MemberCode from SmartCardRegistration Where CardType='Cash Card' And LogSite_Code=?)
Insert Into SmartCardRegistration(Code,CardType,CardNo,Name,Addr,Phone,IssDate,ValidUpto,BlockedYN,SerialNo,Site_Code,LogSite_Code,MemberCode,U_Name,U_EntDt,U_AE) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?)
-- Ledger post
Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To
Insert Into SmartCardLedger(DocId,VSNo,VType,VNo,VPrefix,Type,Site_Code,VDate,Code,HW_Id,AmtCr,AmtDr,Narration,PreBalance,LogSite_Code,U_Name,U_EntDt,U_AE) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?,getdate(),'A',?)
Update Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type=? AND Prefix=?
Update SmartCardRegistration Set LastTransAmt=?,LastTransDate=getdate(), CurrBal=IsNull(CurrBal,0)+?, SecurBal=IsNull(SecurBal,0)+? Where Code=? AND LogSite_Code=?
-- Recalc (VB6 890)
Update SmartCardRegistration Set CurrBal=R.CurrBal,SecurBal=R.SecurBal From SmartCardRegistration SCR Left Join (Select Q.Code,Sum(Q.RCARDC)+Sum(Q.CARDEXP) Currbal,Sum(Q.RCARDS) SecurBal From (Select Code,(Case When Type='RCARDC' Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End) RCARDC,(Case When Type In ('RCARDC','CARDADJC') Then ... ) CARDEXP,(Case When Type='RCARDS' Then ...) RCARDS From SmartCardLedger Where LogSite_Code=? Group By Code, Type) Q Group By Q.Code) R On R.Code=SCR.Code Where R.Code=SCR.Code And SCR.Code=?
```

### 7.5 Frontend/Backend notes
- **Backend P0:** Add Voucher_Prefix numbering, aggregated balance recalc, POS guard, LogSite filter.
- **Frontend:** `ui/misc_vb6_ui.py` SmartCard tabs have `CardNo/MemberCode/IssDate/ValidUpto` but `CurrBal/SecurBal` read-only chips never recalc after recharge — wire `recalc_bal` on dialog close.

---

## 8) NIGHTAUDIT — Posting / PayCharge / Enviro

### 8.1 VB6 SQL verbatim

| VB6 file | SQL |
|---|---|
| `FdAcPostChrg.frm:1228` | `Select PostingType,NoShowAtNightAudit from Enviro Where LogSite_Code='<site>'` → `SELECT KOTAtNightAudit, POSBillAtNightAudit, PostingType, RoomChrgPostingType, RoomChrgDueAc FROM Enviro WHERE LogSite_Code='?'` |
| `mdlNightAudit.bas: ~5 lines` | `SELECT [NCur] FROM Enviro WHERE LogSite_Code='?'` ; `UPDATE Enviro SET [NCur]=?, U_Name=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code='?'` (actually via `frmReNightAudit`) |
| `frmReNightAudit.frm:332` | `Update enviro set ncur=dateadd(D,-1,ncur) where Logsite_code='<site>'` — reverse night audit (business date rollback) |
| `FdAcPostChrg.frm` (posting) | `SELECT DISTINCT D.Name FROM KOT K ... WHERE K.VDate=? AND K.LogSite_Code='?' AND D.KOTAtNightAudit <> 'No'` → `INSERT INTO PayCharge (DocId,Vtype,Vdate,RestCode,RevCode,AmtDr,AmtCr,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE)` per outlet/revenue ; similarly `SELECT DISTINCT D.Name FROM Sale1 S ... WHERE S.LogSite_Code=? AND (P.DocId IS NULL OR S.NetAmt > ISNULL(P.AmtCr,0))` ; `SELECT DISTINCT D.Name FROM HallSale1 H LEFT JOIN PayChargeH ... WHERE H.VDate=? AND H.LogSite_Code=?` |
| `HMS.bas` (MDI Night Audit menu) | `SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName='?' AND CompCode='?' AND [Option]='Night Audit'` ; NightAudit menu items: `Night Audit > Post KOT / Post POS / Post Hall / Post Room Charge / Re-Night Audit / Reports` |
| `FdAcPostChrg.frm:1243` | `Update JobScheduledDetail Set JobEnabled=1,JobScheduledOn=getdate() Where Site_Code='?' AND JobScheduledOn <= getdate()` — scheduler side-effect |

### 8.2 Python SQL (`nightaudit.py`)

```sql
SELECT KOTAtNightAudit, POSBillAtNightAudit, PostingType, RoomChrgPostingType, RoomChrgDueAc FROM Enviro WHERE LogSite_Code=? -- OK
SELECT DISTINCT D.Name FROM KOT K ... WHERE K.VDate=? AND K.LogSite_Code=? AND D.KOTAtNightAudit <> 'No' -- OK (mirrors VB6)
SELECT DISTINCT D.Name FROM Sale1 S ... WHERE S.LogSite_Code=? AND (P.DocId IS NULL OR S.NetAmt > ISNULL(P.AmtCr,0)) -- OK
SELECT DISTINCT D.Name FROM HallSale1 H ... WHERE H.VDate=? AND H.LogSite_Code=? -- OK
SELECT RO.DocId, RO.FolioNo, RO.RoomNo, RO.RoomRate, GF.Name FROM RoomOcc ... WHERE RoomOcc.LogSite_Code=? AND ChkInDate <= ? AND ChkOutDate > ?  -- RoomCharge due list
SELECT MAX(SNo) FROM PayCharge WHERE FolioNo=? AND Site_Code=? -- LogSite missing on PayCharge MAX
INSERT INTO PayCharge (DocId, SNo, Vtype, VNo, Site_Code, VPrefix, Vdate, GuestProf, Comments, PayCode, FolioNo, RoomNo, AmtDr, U_Name, U_EntDt, U_AE, LogSite_Code)
SELECT MAX(SNo) FROM PayCharge WHERE Vtype=? AND Vdate=? AND FolioNo=? -- duplicate check
INSERT INTO NightAuditLog (DateChngFrom, DateChngTo, StartNightAudit, EndNightAudit, Site_Code, U_Name, U_EntDt, U_AE, LogSite_Code)
SELECT [NCur] FROM Enviro WHERE LogSite_Code=? OR LogSite_Code='HO'  -- good HO fallback
UPDATE Enviro SET [NCur]=?, U_Name=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=?  -- date advance
SELECT VP.Prefix, VP.Start_Srl_No FROM Voucher_Type VT INNER JOIN Voucher_Prefix VP ... WHERE VT.Site_Code=VP.Site_Code AND VT.LogSite_Code=VP.LogSite_Code AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To  -- good FY window
```

### 8.3 Gap table

| # | VB6 | Python | Severity | Fix |
|---|---|---|---|---|
| NA-G1 | NightAudit requires `menuHelp [Option]='Night Audit'` privilege + `PostingType`/`NoShowAtNightAudit` flag gate (FdAcPostChrg checks `PostingType` to decide auto-post vs manual) | `nightaudit.py` has no menuHelp check | HIGH | Add `SELECT Param_Str, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Night Audit'` before any post/rollback |
| NA-G2 | Reverse audit: `Update enviro set ncur=dateadd(D,-1,ncur) where Logsite_code='?'` + `DELETE FROM NightAuditLog ...` (no PayCharge delete — business-date only rollback) | `nightaudit.reverse()` correctly does `NCur=dateadd(D,-1,ncur)` + log insert, but also leaves room to optionally `DELETE FROM PayCharge WHERE Vdate=? AND LogSite_Code=? AND Vtype='RC'` — VB6 never deletes PayCharge on reverse | MEDIUM | Keep Python as-is but guard: reverse must check `NoShowAtNightAudit='Y'` → block; ensure no PayCharge delete unless `PostingType='Manual'` (match VB6 FdAcPostChrg manual mode) |
| NA-G3 | `PayCharge` VNo per `Vtype='RC'/'KT'/'PS'` via `Voucher_Prefix` (`Prefix` = FY year string, e.g. `2026`) with `SELECT MAX(VNo) FROM PayCharge WHERE Vtype=? AND VPrefix=? AND Site_Code=? AND LogSite_Code=?` | `nightaudit._next_paycharge_vno` uses `SELECT VP.Prefix...` but `_post_paycharge` MAX without `LogSite_Code` and `VPrefix` | HIGH | Fix `SELECT MAX(VNo) FROM PayCharge WHERE Vtype=? AND VPrefix=? AND Site_Code=? AND LogSite_Code=?` |
| NA-G4 | `JobScheduledDetail` side-effect: `Update JobScheduledDetail Set JobEnabled=1,JobScheduledOn=getdate() Where Site_Code=? ...` triggered at night audit close | `nightaudit.close_audit` does not touch `JobScheduledDetail` | LOW | Add `UPDATE JobScheduledDetail SET JobEnabled=1, JobScheduledOn=getdate() WHERE Site_Code=? AND LogSite_Code=? AND JobScheduledOn <= getdate()` after `UPDATE Enviro SET NCur` |
| NA-G5 | `NoShowAtNightAudit` check per outlet (`Enviro.NoShow...`) drives skip of KOT/Sale for that RestCode | Python KOT/Sale distinct queries include `D.KOTAtNightAudit <> 'No'` but not `RestCode` NoShow filter | MEDIUM | Add `AND RestCode NOT IN (SELECT RestCode FROM RestMaster WHERE NoShowAtNightAudit='Y')` if that column exists (keep same name) |
| NA-G6 | `NightAuditLog` insert includes `StartNightAudit/EndNightAudit` timestamps + `DateChngFrom/To` | Python `NightAuditLog` insert OK but missing `U_AE` branching (`'A'` first, `'E'` subsequent) | LOW | Keep `'A'` |

### 8.4 Fixed workflow
```sql
-- Pre-check
SELECT Param_Str AS UPrivilege, Flag FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]='Night Audit'
SELECT PostingType, NoShowAtNightAudit, KOTAtNightAudit, POSBillAtNightAudit, PostingType, RoomChrgPostingType FROM Enviro WHERE LogSite_Code=?
-- Determine outlets
SELECT DISTINCT D.Name FROM KOT K WHERE K.VDate=? AND K.LogSite_Code=? AND D.KOTAtNightAudit <> 'No'
SELECT DISTINCT D.Name FROM Sale1 S WHERE S.VDate=? AND S.LogSite_Code=? AND (P.DocId IS NULL OR S.NetAmt > ISNULL(P.AmtCr,0))
-- Room charge due
SELECT RO.DocId, RO.FolioNo, RO.RoomNo, RO.RoomRate FROM RoomOcc RO WHERE RO.LogSite_Code=? AND RO.ChkInDate <= ? AND RO.ChkOutDate > ? AND RO.Type NOT IN ('O','C')
-- Post
SELECT VP.Prefix, VP.Start_Srl_No FROM Voucher_Type VT INNER JOIN Voucher_Prefix VP ON VT.V_Type=VP.V_Type AND VT.Site_Code=VP.Site_Code AND VT.LogSite_Code=VP.LogSite_Code WHERE VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To
SELECT MAX(VNo) FROM PayCharge WHERE Vtype=? AND VPrefix=? AND Site_Code=? AND LogSite_Code=?  -- next VNo
INSERT INTO PayCharge (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,GuestProf,PayCode,FolioNo,RoomNo,AmtDr,LogSite_Code,U_Name,U_EntDt,U_AE) VALUES (?)
UPDATE Voucher_Prefix SET Start_Srl_No=? WHERE SITE_CODE=? AND LOGSITE_CODE=? AND V_Type=? AND Prefix=?
INSERT INTO NightAuditLog (DateChngFrom, DateChngTo, StartNightAudit, EndNightAudit, Site_Code, LogSite_Code, U_Name, U_EntDt, U_AE) VALUES (?,?,?,?,?,?,?,getdate(),'A',?)
UPDATE Enviro SET NCur=?, U_Name=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=?
UPDATE JobScheduledDetail SET JobEnabled=1, JobScheduledOn=getdate() WHERE Site_Code=? AND LogSite_Code=? AND JobScheduledOn <= getdate()
-- Reverse
UPDATE Enviro SET NCur=dateadd(D,-1,NCur) WHERE LogSite_Code=?
```

### 8.5 Frontend/Backend notes
- **Backend P0:** Add menuHelp guard, fix PayCharge MAX with LogSite_Code+VPrefix.
- **Frontend:** `ui/nightaudit_reports_ui.py` already wires `NightAuditLog` list + `NCur` chip; add `PostingType` badge (`Daily` vs `Summary`) and `NoShowAtNightAudit` warning dialog before post (VB6 `FdAcPostChrg` does).

---

## 9) Cross-Cutting Missing Logic (ALL 8 modules)

| Pattern | VB6 universal | Python gap | Fix (no schema change) |
|---|---|---|---|
| **HO fallback** | `WHERE (LOGSITE_CODE='<site>' OR LOGSITE_CODE='HO')` on every master read (AcGroup, SubGroup, RoomMast, RoomCat, Depart, Desig, EmpCategory, ComplaintCategory, TelCallType/Ext, MemCatMast, VenueMast, BussSource, MarketSeg, FunctionType) | Most `core/*.py` `list_all`/`get` only `WHERE Site_Code=?` or `LogSite_Code=?` (no OR HO) | Add `OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')=''` to every master SELECT |
| **LOGSITE_CODE scoping** | Every transactional table (`Booking`, `HallBook`, `HallSale1`, `PayCharge`, `Salary`, `Attend`, `ComplaintDetail`, `RoomOcc`, `EPABX_OUT`, `SmartCardRegistration/Ledger`) filtered by `LogSite_Code=?` | Many INSERT ok, but SELECT/UPDATE/DELETE missing LogSite_Code | Add `AND LogSite_Code=?` to WHERE on all transactional reads/writes |
| **`next_vno` / `Voucher_Prefix`** | `SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE='<site>' AND VP.LOGSITE_CODE='<site>' AND VP.V_Type='<type>' AND '<date>' BETWEEN VP.Date_From AND VP.Date_To` then `UPDATE Voucher_Prefix Set Start_Srl_No=... Where SITE_CODE='...' AND LOGSITE_CODE='...' AND V_Type='...' AND Prefix='...'` | `MAX(...)` without FY window, `Voucher_Type` as wrong source (banquet), missing `LOGSITE_CODE` | Replace all `_next_vno` with verbatim join+window + start_srl update |
| **`LASTVOU`** | `SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code='...' AND ENAME='...'` → `SELECT DOCID FROM LASTVOU ...` → `UPDATE LASTVOU SET DOCID='...'` else `INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,LogSite_Code,U_EntDt,U_AE)` | Only booking/banquet partially use; members/HR/smartcard not at all; `hr_payroll`/`smartcard` use simple MAX | Add LASTVOU path for Booking/HallBook/HallSale/RC/Attend |
| **`menuHelp` privilege** | `SELECT Param_Str AS UPrivilege, Flag, Module_Name FROM menuHelp WHERE UserName='<user>' AND CompCode='<comp>' AND [Option]='<screen>'` before every Add/Edit/Delete | No core file checks menuHelp (all writes open) | Add guard at top of every `insert/update/delete` core fn |
| **`TopCtrl` toolbar state** | VB6 TopCtrl has `Add/Edit/Delete/Save/Cancel/Find/Print/Exit` with `Enabled` toggling and `FindMove` (SearchCode grid) | Python UIs use `+Line/-Line/Post` or `Save/Delete` without TopCtrl mapping | UI: map `Add→clear+next_vno`, `Edit→load+lock key`, `Delete→guard check`, `Find→SearchCode SQL`, `Print→TTX` |
| **`U_Name/U_EntDt/U_AE`** | Every INSERT sets `U_Name='<user>',U_EntDt=getdate(),U_AE='A'`; UPDATE sets `U_EntDt=getdate(),U_AE='E'`; footer shows `Created By / Last Update` | Some Python inserts omit `U_AE='E'` on update (use `'A'`); footer not wired | Keep `'A'` on insert, `'E'` on update, footer from `U_Name+U_EntDt` |
| **`Enviro` NCur** | Business date `NCur` drives all Vdate defaults; night audit advances it by +1 day (`UPDATE Enviro SET NCur=dateadd(D,1,NCur)`) | `nightaudit.py` handles; others use `getdate()` not `NCur` | For Booking/HallBook/Attend, default Vdate = `SELECT NCur FROM Enviro WHERE LogSite_Code=?` not `getdate()` |

---

## 10) Debug Fixes — EXACT VB6 workflow SAME SQL, no schema change

### P0 backend patches (SQL verbatim, parameterized)

```python
# HO fallback helper — reuse everywhere
HO_SQL = "WHERE (LogSite_Code = ? OR LogSite_Code = 'HO' OR ISNULL(LogSite_Code,'')='')"
# Example: hr_masters
db.query(f"SELECT Code,Name FROM Desig {HO_SQL} ORDER BY Name", (SITE_CODE,), cn=cn)
db.query(f"SELECT Code,Name FROM EmpCategory {HO_SQL} ORDER BY Name", (SITE_CODE,), cn=cn)
db.query(f"SELECT Code,Name FROM SubGroup WHERE ActiveYN=1 AND (LogSite_Code=? OR LogSite_Code='HO') ORDER BY Name", (SITE_CODE,), cn=cn)

# Voucher_Prefix FY lookup (all modules: BK/HBK/IDC/RC/AT/MB/FB/RCARDC)
rows = db.query(
    "Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No "
    "From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) "
    "Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To",
    (SITE_CODE, SITE_CODE, vtype, vdate), cn=cn)
prefix = rows[0].Prefix if rows else str(vdate.year)
# bump
db.execute("Update Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type=? AND Prefix=?",
           (new_srl, SITE_CODE, SITE_CODE, vtype, prefix), cn=cn, commit=False)

# LASTVOU (Booking/HallBook/HallSale)
cnt = db.query("SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?", (SITE_CODE, ename), cn=cn)[0][0]
if cnt:
    db.execute("UPDATE LASTVOU SET DOCID=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=? AND ENAME=?", (docid, SITE_CODE, ename), cn=cn, commit=False)
else:
    db.execute("INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,getdate(),'A',?)",
               (USER, ename, docid, SITE_CODE, SITE_CODE), cn=cn, commit=False)

# menuHelp guard (prepend to each core write)
priv = db.query("SELECT Param_Str AS UPrivilege, Flag, Module_Name FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?",
                (user, comp, option), cn=cn)
if not priv or 'A' not in (priv[0].UPrivilege or ''): raise PermissionError(option)

# Salary delete guard
for tbl, col in [("Salary","Emp_Code"),("Attend","Emp_Code"),("Attendence","Emp_Code"),("Loan","Emp_Code"),("Leave_Ench","Emp_Code"),("OverTime","EmpCode")]:
    if db.query(f"SELECT COUNT(*) FROM {tbl} WHERE Site_Code=? AND {col}=?", (SITE_CODE, code), cn=cn)[0][0]:
        raise ValueError(f"Block: {tbl} exists for {code}")

# RoomBlockOut + RoomMast same tx
db.execute("Insert into RoomBlockOut (RoomCode,Reasons,FromDate,ToDate,Type,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE,VTime) VALUES (?,?,?,?,?,?,?,?,getdate(),'A',?,getdate())",
           (room, reasons, fdate, tdate, typ, SITE_CODE, SITE_CODE, USER), cn=cn, commit=False)
db.execute("Update RoomMast set RoomStat=? where (LOGSITE_CODE=? OR LOGSITE_CODE='HO') and Code=?", (stat, SITE_CODE, room), cn=cn, commit=False)

# SmartCard recalc (verbatim aggregated)
db.execute(
    "Update SmartCardRegistration Set CurrBal=R.CurrBal,SecurBal=R.SecurBal "
    "From SmartCardRegistration SCR Left Join (Select Q.Code,Sum(Q.RCARDC)+Sum(Q.CARDEXP) Currbal,Sum(Q.RCARDS) SecurBal "
    "From (Select Code,(Case When Type='RCARDC' Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End) RCARDC,"
    "(Case When Type In ('RCARDC','CARDADJC') Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End) CARDEXP,"
    "(Case When Type='RCARDS' Then IsNull(Sum(AmtCr),0)-IsNull(Sum(AmtDr),0) Else 0 End) RCARDS "
    "From SmartCardLedger Where LogSite_Code=? Group By Code, Type) Q Group By Q.Code) R On R.Code=SCR.Code "
    "Where R.Code=SCR.Code And SCR.Code=? And SCR.LogSite_Code=?",
    (SITE_CODE, code, SITE_CODE), cn=cn, commit=commit)

# TelCallType dual-write
db.execute("INSERT INTO TelCallType(Code,CallType,ShortName,ACCode,TaxStru,sITE_cODE,LOGSITE_CODE,U_Name,U_EntDt,U_AE) VALUES (?,?,?,?,?,?,getdate(),'A',?,?)",
           (code, ct, sn, ac, tax, SITE_CODE, SITE_CODE), cn=cn, commit=False)
db.execute("INSERT INTO RevMast(Code,Name,ShortName,ACCode,TaxStru,SysYN,AppMode,FieldType,FlagType,FlagAmr,DeskCode,Type,Site_Code,LOGSITE_CODE,U_Name,U_EntDt,U_AE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A')",
           (code, ct, sn, ac, tax, 'Y', 'A', 'T', '', '', 'TEL', 'C', SITE_CODE, SITE_CODE), cn=cn, commit=False)
```

### P1 frontend patches (workflow parity)

- `booking_ops_ui` / `registration_entry_ui`: wire `Voucher_Prefix` FY Label (`Vprefix` chip), `LOGSITE_CODE` chip, TopCtrl `Find` dialog `SELECT DocId AS SearchCode, BookNo, GuestName, ArrDate, DepDate FROM Booking WHERE LogSite_Code=? ORDER BY BookNo DESC`.
- `hall_booking_ui`: add `VenueOCC` time-range pickers (`FromDate/ToDate/FromTime/ToTime`), clash toast `Venue already booked for selected dates`; hall bill grid `Remarks/VoidYN` columns.
- `hr_members_ui` / `hr_payroll_ui`: `Attend` tab must POST to `Attend` not `Attendence` (`V_Prefix` dropdown FY, `FirstShift/SecondShift` P/A/L toggles); Salary tab `Mth_Year` dept filter `Emp_Code In (Select Code From Employee Where site_code=? And Department=?)`.
- `epabx_ui`: add `RevMast` mirror badge after CallType save.
- `housekeeping`: create complaint list `SearchCode` via `C.Code AS SearchCode, ... FROM ComplaintDetail C Inner JOIN Depart ON C.Depart=Depart.Code Where C.LogSite_Code=?` plus clearing `Status` toggle chips.
- `nightaudit_reports_ui`: add `PostingType` badge + `NoShowAtNightAudit='Y'` blocked outlet banner.

### Verification (after PATCH, before claim)

```bash
pytest PYTHONE/tests/test_front_office.py PYTHONE/tests/test_validation_crud.py -q
python -c "import PYTHONE.core.booking as b; print(b.list_all())"  # should filter by LogSite_Code
python -m PYTHONE.core.nightaudit --selftest  # NCur advance + PayCharge VNo+LogSite
# Manual SQL probe: SELECT LogSite_Code, COUNT(*) FROM Booking GROUP BY LogSite_Code -- should show no cross-site leak
```

---

## 11) Raw VB6 SQL Reference — copy-paste parity (parameterize `?`)

```sql
-- HO fallback everywhere
WHERE (LOGSITE_CODE = ? OR LOGSITE_CODE = 'HO')
WHERE (s.LogSite_Code = ? OR s.LogSite_Code = 'HO' OR ISNULL(s.LogSite_Code,'')='')
-- Voucher prefix FY window
Select VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No From Voucher_Type VT Inner Join Voucher_Prefix VP on (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE) Where VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND VP.V_Type=? AND ? BETWEEN VP.Date_From AND VP.Date_To
Update Voucher_Prefix Set Start_Srl_No=? Where SITE_CODE=? AND LOGSITE_CODE=? AND V_Type=? AND Prefix=?
-- LASTVOU
SELECT COUNT(*) FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?
SELECT DOCID FROM LASTVOU WHERE LogSite_Code=? AND ENAME=?
UPDATE LASTVOU SET DOCID=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=? AND ENAME=?
INSERT INTO LASTVOU (UNAME,ENAME,DOCID,Site_Code,U_EntDt,U_AE,LogSite_Code) VALUES (?,?,?,?,getdate(),'A',?)
-- Privilege
SELECT Param_Str AS UPrivilege, Flag, Module_Name FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?
-- Booking groups
SELECT GR.BookingDocId As UID,GR.SNo,ISNULL(Booking.MyRectNo,'') MyRectNo,Booking.BookNo,RC.Name As RoomType,GR.ArrDate,...,IsNull(BP.RPackageAmt,0) MealCharge,IsNull(BP.NetPackageAmount,0) As PlanTariff FROM GRPBookingDetails GR LEFT JOIN ... WHERE BookingDocId=?
SELECT RefDocId UID,P.VNo,P.Vdate,P.VTime,P.Comments,P.PayCode,P.PayType,Revmast.Name PayName,P.AmtCr FROM PayCharge P Inner Join Revmast On Revmast.Code=P.PayCode WHERE RefDocId=?
-- ViewBooking availability
Select B.ArrDate,B.DepDate,RC.Name RoomCategory,B.ResStatus,B.Adult,B.GuestName,B.RoomNo From (((ViewBooking as B Left Join GuestFolio GF on GF.BookingDocid=B.DociD And GF.BookingSno=B.SNo)Left Join RoomOcc RO on RO.Docid=GF.DocId) Left Join RoomCat RC on RC.Code=B.RoomCat And RC.Type='RO') Where B.LOGSITE_CODE=?
Select Count(*) As RoomBusyRO From RoomOcc Where LOGSITE_CODE=? AND RoomCat=? And RoomType='RO' And ...
Select Count(*) As RoomBlocked From RoomBlockOut RB Inner Join RoomMast RM ON RB.RoomCode=RM.Code where RB.LOGSITE_CODE=?
-- Hall
Select Code,PartyName as Name From BookingInquiry where LogSite_Code=? And code not in (select InquiryCode from HallBook Where InquiryCode<>?)
Select Count(*) From HallSale1 WHERE Vtype='IDC' AND BookDocId=? AND LogSite_Code=?
Delete From HallBook Where Docid=?; Delete From HallBook1 Where Docid=?; Delete From VenueOCC Where FPDocID=?
Select Count(*) From VenueOCC S WHERE LogSite_Code=? And ? BETWEEN FromDate AND ToDate And VenuCode=?
Insert Into HallBook(Docid,VNo,VDate,VType,VPrefix,VTime,Site_Code,Total,DiscPer,DiscAmt,NonTaxable,Taxable,Tax,ServiceCharge,AddAmt,DedAmt,RoundOff,U_Name,U_EntDt,U_AE,HallRent,Remarks,Advance,NetAmount,LogSite_Code,BookingAgent) Values(...)
Insert Into VenueOCC(FPDocid,VenuCode,FromDate,ToDate,FromTime,ToTime,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(...)
-- Housekeeping
SELECT CD.Code AS Scode,CD.Category AS CatCode,CD.CDate AS CDate,CD.CTime AS CTime,CC.Category AS Category,CD.Description AS Description,CD.Depart AS Depart,CD.UName AS UName,CD.Status AS Status FROM ComplaintDetail CD Left JOIN ComplaintCategory CC ON CD.Category =CC.Code WHERE CD.LOGSITE_CODE=?
Select IsNull(Max(CAST(SUBSTRING(Code,3,4) AS INT)),0)+1 AS MyCode From ComplaintDetail Where Site_Code=?
Insert Into ComplaintDetail(Code,Category,CDate,CTime,Description,Depart,UName,Status,Site_Code,U_EntDt,U_AE,LogSite_Code) Values(?,?,?,?,?,?,?, 'Open',?,getdate(),'A',?)
UPDATE ComplaintDetail SET Status='Solved', ClearingDate=getdate(), ClearingPerson=? WHERE Code=? AND LogSite_Code=?
Insert into RoomBlockOut (RoomCode,Reasons,FromDate,ToDate,Type,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE,VTime) Values(?,?,?,?,?,?,?, ?,getdate(),'A',?,getdate())
Update RoomMast set RoomStat=? where (LOGSITE_CODE=? OR LOGSITE_CODE='HO') and Code=?
-- Telephone
SELECT distinct R.*,R.Code as SearchCode,S.SubCode as LedgerCode,S.Name as LedgerName,T.Code as TaxCode,T.Name as TaxName FROM ((TelCallType R Left Join TaxStru T on T.Code=R.TaxStru) Left join Subgroup S on S.SubCode=R.ACCode) WHERE (R.LOGSITE_CODE=? OR LOGSITE_CODE='HO')
Insert Into TelCallType(Code,CallType,ShortName,ACCode,TaxStru,U_Name,U_EntDt,U_AE,sITE_cODE,LOGSITE_CODE) Values(?,?,?,?,?, ?,getdate(),'A',?,?)
Insert Into RevMast(Code,Name,ShortName,ACCode,TaxStru,SysYN,AppMode,FieldType,U_Name,U_EntDt,U_AE,FlagType,FlagAmr,DeskCode,Type,Site_Code,LOGSITE_CODE) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),'A',?,?)
SELECT TelExt.Code , TelExt.ShopNo & RoomMast.Code & Depart.Name as Name,TelExt.ShopNo as ShopNo, RoomMast.Code as RoomNo, Depart.Name as DepartNo FROM (TelExt LEFT JOIN RoomMast ON TelExt.RoomNo=RoomMast.Code) LEFT JOIN Depart ON TelExt.DepCode=Depart.Code WHERE TelExt.Extension=?
INSERT INTO EPABX_OUT (ID,V_TYPE,PNT_NO,Extension,RoomNo,ShopNo,DepCode,CALL_START_DATE,CALL_START_TIME,CALL_DURATION,DIALED_NO,CALL_INFO,CALL_RATE,CALL_AMT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
-- SmartCard
Select IsNull(Max(CAST(Code AS INT)),0)+1 AS MyCode From SmartCardRegistration Where LOGSITE_CODE=?
Insert Into SmartCardRegistration(Code,CardType,CardNo,Name,Addr,Phone,IssDate,ValidUpto,BlockedYN,SerialNo,Site_Code,LogSite_Code,MemberCode,U_Name,U_EntDt,U_AE) Values(?,?,?,?,?,?,?,?,?,?,?,?,?, ?,getdate(),'A',?)
Insert Into SmartCardLedger(DocId,VSNo,VType,VNo,VPrefix,Type,Site_Code,VDate,Code,HW_Id,AmtCr,AmtDr,Narration,PreBalance,LogSite_Code,U_Name,U_EntDt,U_AE) Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?,getdate(),'A',?)
Update SmartCardRegistration Set LastTransAmt=?,LastTransDate=getdate(), CurrBal=IsNull(CurrBal,0)+?, SecurBal=IsNull(SecurBal,0)+? Where Code=? AND LogSite_Code=?
-- HR
Select IsNull(Max(CAST(SUBSTRING(Code,3,6) AS INT)),0)+1 AS MyCode From Employee where Site_Code=?
Insert Into EMPLOYEE (Code,Name,F_Name,Add1,Add2,Spouse,Qualification,ESI_Code,PF_Code,Basic,...,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(...)
Insert Into Attend(V_Prefix,V_Date,Emp_Code,FirstShift,SecondShift,Site_Code,U_Name,U_EntDt,U_AE,LogSite_Code) Values(?,?,?,?,?,?,?,getdate(),'A',?)
select count(*) from holiday where LogSite_Code=? AND datepart(dw,vdate)<>'1' and month(VDate)=? and year(VDate)=?
Select * From Attend Where LOGSITE_CODE=? AND Emp_Code=? And Month(V_Date)=?
Select IsNull(Sum(Amount),0) From Loan Where LOGSITE_CODE=? AND V_Type='LO' And Emp_Code=?
Insert Into Ledger(DocId,V_SNo,V_Type,V_Prefix,V_No,Site_Code,V_Date,SubCode,ContraSub,AmtCr,Narration,mth_year,Emp_Code,U_Name,U_EntDt,U_AE,GROUPCODE,GROUPNATURE,LogSite_Code) Values(...)
Insert Into Salary(Mth_Year,Emp_Code,Work_Day,Leave,Sunday,Holiday,Absent,Basic,DA,HRA,...,Net_Salary,Site_Code,LogSite_Code,U_Name,U_EntDt,U_AE) Values(...)
-- NightAudit
Select PostingType,NoShowAtNightAudit from Enviro Where LogSite_Code=?
SELECT DISTINCT D.Name FROM KOT K ... WHERE K.VDate=? AND K.LogSite_Code=? AND D.KOTAtNightAudit <> 'No'
SELECT NCur FROM Enviro WHERE LogSite_Code=? OR LogSite_Code='HO'
UPDATE Enviro SET NCur=?, U_Name=?, U_EntDt=getdate(), U_AE='E' WHERE LogSite_Code=?
Update enviro set ncur=dateadd(D,-1,ncur) where Logsite_code=?
INSERT INTO NightAuditLog (DateChngFrom, DateChngTo, StartNightAudit, EndNightAudit, Site_Code, LogSite_Code, U_Name, U_EntDt, U_AE) VALUES(?,?,?,?,?,?,?,getdate(),'A',?)
```

---

*Report path:* `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\RES_BANQ_MEM_HR_COMPARE.md`  
*Generated by side-by-side full read:* VB6 `RrRoomReservation/FOMModule/resRoomType/HallBooking/HallBill/HallBillEstimate/HallChefPreCosting/BanqModule/MemCatMast/MembershipMast/MemVisitEntry/MemFacilityBilling/MemberModule/PrEmployee/prAttend/prSalCreate/PrDesigMast/PrCategoryMast/FrmComplaintMast/FrmComplaintClearing/HHouseKeeping/HKRoomBlock/TelCallTypeMast/TelExtensionMast/TelCallEntry/SmartCardRegistration/SmartCardRecharge/ModuleSmartCard/mdlNightAudit/frmReNightAudit/FdAcPostChrg/HMS` + PYTHONE `booking/reservation/banquet_masters/banquet_ops/hall_booking/members_masters/member_billing/facility_billing/hr_masters/hr_payroll/epabx_masters/epabx_ops/smartcard/smartcard_ops/nightaudit/room_occ/sms_comm` — verbatim SQL extracted via regex, HO/LOGSITE/menuHelp/next_vno patterns audited, no DB schema change.
