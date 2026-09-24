# POS Module — VB6 ↔ Python Comparison & Fix Plan
> **Module:** POS / POINT OF SALE (KOT, Sale1/Sale2, POS_SBill, Settlement/PayCharge/SunTran, SplitBill, Scheme/HappyHours, Waiter/Table/Session, Stock)  
> **Date:** 2026-09-24  
> **Sources inspected ONE BY ONE (full):**  
> VB6: `RsKOTEntry.frm`, `RSSaleBill.frm`, `RsKOTTransfer.frm`, `RsTbChange.frm`, `RsPaymentReceice.frm`, `RsSaleBillSplit.frm`, `pHappyHours.frm`, `NewHappyHours.frm`, `RsTableMast.frm`, `HMS.bas` (POSEnt 13 cases + POSMas + MDIForm1), `POSBillPrint.bas`, `moondata.sql` (UTF-16)  
> Python: `core/pos_kot.py`, `core/pos_sales.py`, `core/pos.py`, `core/pos_entry.py`, `core/pos_stock.py`, `core/pos_masters.py`, `core/pos_happy.py`, `core/pos_table.py`, `ui/kot_entry.py`, `ui/pos_sales_ui.py`, `ui/kot_transfer_ui.py`, `ui/pos_table_ui.py`, `ui/pos_stock_ui.py`  
> **Constraint:** SAME VB6 SQL verbatim, **no DB schema change**, frontend/backend workflow must match VB6 exactly.

---

## 1) VB6 SQL — Verbatim (exact strings as in decompiled VB6)

### 1.1 KOT — Pending / Existence Checks / Next VNo / Running Order

```sql
-- RsKOTEntry: Pending KOT grid (CmPendingKot)
SELECT k.docid as DocID,K.Vtime as KotTime,K.VNo,k.Vdate,W.NAME AS WAITER,K.RoomNo AS TABLENo,I.NAME AS PRODUCT,K.Qty,D.NAME AS DEPARTNAME
FROM ((((KOT AS K INNER JOIN wAITER AS W ON K.Waiter = W.Code)
INNER JOIN ItemMast AS I ON (K.Item = I.Code And K.ItemRestCode=I.RestCode))
INNER JOIN DEPART AS D ON K.RestCode = D.Code)
INNER JOIN VOUCHER_TYPE AS V ON (K.Vtype = V.V_Type AND K.SITE_CODE=V.SITE_CODE))
where k.contradocid='' and k.VoidYN='N' and k.delFlag<>'Y' and k.nckot='N' and k.restcode='<LocalRestCode>' Order By K.DocId,K.RESTCODE,I.Name

-- RsKOTEntry: Duplicate VNo check (Txt Validate)
Select Count(*) From KOT Where DocID='<docid>'

-- RsKOTEntry: Pax/GuarAtt fallback (Txt Validate - Table)
SELECT ISNULL(MAX(GUARATT),1) FROM (SELECT TOP 1 GUARATT FROM KOT WHERE RestCode='<LocalRestCode>' And Pending='Y' AND VOIDYN<>'Y' AND (DELFLAG='N' or DELFLAG='') AND NCKOT<>'Y' AND ROOMNO='<table>'' Order By Vno Desc)Q

-- RsKOTEntry: Running Order vs New Order (Txt Validate - Table)
Select Top 1 VNo From KOT Where VDate=<vdate> And RestCode='<LocalRestCode>' And RoomCat='<roomcat>' And RoomType='<roomtype>' And RoomNo='<roomno>' And Pending='Y' AND VOIDYN<>'Y' AND (DELFLAG='N' or DELFLAG='') AND NCKOT<>'Y' And IsNull(ContraDocId,'')='' Order By VNo desc

-- RsKOTEntry: RoomServicefolionoDocid resolved + bill printed check
Select mFolioNoDocId From GuestFolio Where DocId='<RoomOcc.DocId>'
Select count(Distinct Bill_no) from paycharge where bill_no is not null and bill_no<>'' and FolionoDocid='<foliodocid>'

-- RSSaleBill / RsSaleBillSplit base: Voucher type + Sundry + LastVou
Select 'B'+ShortName as Adv_Type From Depart Where Code='<RestCode>'
Select Count(*) From Depart Where Code='<RestCode>' And RestType='Production'   -- block Production
Select V_Type from Voucher_Type Where Ncat='ORDER' and RestCode='<RestCode>'
Select V_Type from Voucher_Type Where Ncat='PADV' and RestCode='<RestCode>'
Select 'B'+ShortName From Depart Where Code='<RestCode>'  (Voucher resolution)
Select S.DocId as SearchCode,S.DocID From Sale1 S INNER JOIN VOUCHER_TYPE V ON S.VTYPE=V.V_TYPE WHERE S.LOGSITE_CODE='<LOGSITE>' AND S.VDate=<vdate> AND S.DELFLAG='N' AND S.VTYPE='<vtype>' ORDER BY S.DOCID
Select I.Code,I.Name as Name,IC.RoundOff,I.RateEdit,I.Kitchen,I.Unit,IG.Name as ItemGroup,DispCode,IC.taxStru,D.Name as OutLetName,D.Code as OutLetCode,I.DiscApp,I.SChrgApp,I.RateIncTax From ((ItemMast I INNER join ItemGrp IG on I.ItemGroup=IG.Code) INNER Join Depart D On D.Code=I.RestCode) INNER join ItemCatMast IC on IC.Code=I.ItemCatCode Where (I.LOGSITE_CODE='<LOGSITE>' or I.LOGSITE_CODE='HO') AND I.Type='Finish' And I.DispCode <>9999 Order by I.Name
SELECT COUNT(*) FROM LASTVOU WHERE LOGSITE_CODE='<LOGSITE>' AND ENAME='<ename>' AND UNAME='<user>'
SELECT DOCID FROM LASTVOU WHERE LOGSITE_CODE='<LOGSITE>' AND ENAME='<ename>' AND UNAME='<user>'

-- ItemRate lookup (POSBillPrint.bas)
Select Rate,Appdate From ItemRate Where ItemCode='<item>' And AppDate <=<vdate> Order by Appdate Desc

-- RsTbChange: From/To population + KOTTransfer To vacancy exclusion
SELECT DISTINCT RoomNo AS CODE,RoomNo as Name  FROM KOT WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode='<LocalRestCode>' and ROOMTYPE='TB' AND (PENDING ='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y'
SELECT DISTINCT CODE,code as Name From RoomMast Where type='TB' AND RESTCODE='<LocalRestCode>' And Code Not in(SELECT DISTINCT RoomNo AS CODE FROM KOT WHERE restCode='<LocalRestCode>' and ROOMTYPE='TB' AND (PENDING ='Y' OR DELFLAG IS NULL) AND (DELFLAG<>'Y' OR DELFLAG IS NULL) and (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y') ORDER BY code

-- RsKOTTransfer: Source list depends on RoomType
-- Room Service:
SELECT DISTINCT DOCID AS CODE,VNO as Name FROM KOT WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode='<LocalRestCode>' and ROOMTYPE='RO' AND (PENDING ='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y' ORDER BY VNO
SELECT RC.DOCID AS CODE, LTrim(RTrim(RC.RoomNo)) AS Name FROM Depart D, (ROOMOCC AS RC LEFT JOIN GuestProf ON (RC.GuestProf = GuestProf.Code and RC.LogSite_Code=GuestProf.LogSite_Code)) where (RC.LOGSITE_CODE='<LOGSITE>' or RC.LOGSITE_CODE='HO') and RC.ROOMType in('RO') AND RC.CHKOUTDATE IS NULL And D.Code='<LocalRestCode>' Order by LTrim(RTrim(RC.RoomNo))
-- Table (TB):
SELECT DISTINCT VNO AS CODE,VNO as Name FROM KOT WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode='<LocalRestCode>' and ROOMTYPE='TB' AND (PENDING ='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y'
SELECT DISTINCT CODE,code as Name From RoomMast Where type='TB' AND RESTCODE='<LocalRestCode>' ORDER BY code
-- Max ROOMNO for tapped KOT (RsKOTTransfer TXT_PKOT)
SELECT Max(RoomNo) FROM KOT WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode='<LocalRestCode>' and ROOMTYPE='RO' AND (PENDING ='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y' And DOCID='<docid>'
SELECT Max(RoomNo) FROM KOT WHERE (DELFLAG<>'Y' OR DELFLAG IS NULL) AND restCode='<LocalRestCode>' and ROOMTYPE='TB' AND (PENDING ='Y' OR PENDING IS NULL) AND (NCKOT<>'Y' OR NCKOT IS NULL) AND VOIDYN<>'Y' And VNO=<vno>

-- RsKOTTransfer: Updates (transactional)
-- Room Service (reference = DOCID):
Update Kot Set ROOMNO='<to>',ROOMCAT='<RoomOcc.RoomCat>',U_Name1='<user>',U_EntDt1=<getdate>,U_AE1='E' Where RestCode='<LocalRestCode>' and Pending ='Y' and (DELFLAG='N' OR DELFLAG IS NULL OR DELFLAG='') and DOCID='<DOCID>'
SELECT * FROM ROOMOCC RC WHERE DocId='<targetroom_docid>' And (RC.LOGSITE_CODE='<LOGSITE>' or RC.LOGSITE_CODE='HO') and RC.ROOMType in('RO') AND RC.CHKOUTDATE IS NULL
-- Table (reference = VNO):
Update Kot Set ROOMNO='<to>',U_Name1='<user>',U_EntDt1=<getdate>,U_AE1='E' Where RestCode='<LocalRestCode>' and Pending ='Y' and (DELFLAG='N' OR DELFLAG IS NULL OR DELFLAG='') and VNO=<vno>

-- RsTbChange: Bulk table change
Update Kot Set ROOMNO='<to>',U_Name1='<user>',U_EntDt1=<getdate>,U_AE1='E' Where RestCode='<LocalRestCode>' and Pending ='Y' and (DELFLAG='N' OR DELFLAG IS NULL OR DELFLAG='') and ROOMNO='<from>'

-- NC Bill printing (RsKOTEntry cmdNCBill) — per-kitchen separate / combined
SELECT k.docid as DocID,K.Vtime as KotTime,K.VNo,k.Vdate,W.name as WaiterName,k.RoomNo as TableNo,K.Remarks,K.NCType From (KOT K Left Join Waiter W on K.Waiter=W.Code) Where K.DocID='<docid>'
Select K.Sno,I.Name as ItemName,K.Qty,K.rate, Depart.ShortName From (KOT K Left Join ItemMast I on K.Item=I.Code And K.ItemRestCode=I.RestCode) LEFT JOIN Depart ON I.Kitchen=Depart.Code Where K.DocID='<docid>'
Select distinct(Depart.ShortName),Depart.Name,Depart.Code,Depart.Printer,Depart.PrintType From (KOT K Left Join ItemMast I on K.Item=I.Code And K.ItemRestCode=I.RestCode) LEFT JOIN Depart ON I.Kitchen=Depart.Code Where K.DocID='<docid>'
SELECT KOTPrinting FROM Enviro
Select K.Sno,I.Name as ItemName,K.Qty,K.Rate, Depart.ShortName,Depart.Code,dEPART.nAME AS KITCHEN,Depart.PrintType From (KOT K Left Join ItemMast I on K.Item=I.Code And K.ItemRestCode=I.RestCode) LEFT JOIN Depart ON I.Kitchen=Depart.Code Where K.DocID='<docid>' AND Depart.Code='<kitchen>' AND I.Kitchen='<kitchen>' and K.VoidYN<>'Y'
-- Enviro check
Select CKOTPrintYN From Depart Where Code='<LocalRestCode>'
SELECT DISTINCT DOCID FROM KOT WHERE ROOMNO='<tableno>' AND CONTRADOCID IS NULL  -- for LblState New vs Running

-- POSBillPrint (Sale Bill printing) — Stock aggregation + headers + sundry
Select Sale1.* ,W.Name as WaiterName From Sale1 left join waiter W on sale1.waiter=w.code Where Sale1.DocID='<docid>'
Select MAX(S.SNO)AS SRNO,MAX(S.TAXPER) AS TAXPER,MAX(S.RATE) AS RATE,SUM(S.QTYISS) AS QTY,SUM(S.AMOUNT) AS AMT,MAX(I.NAME) AS ITEMNAME From Stock S LEFT JOIN ITEMMAST I ON I.CODE=S.ITEM  Where S.DocID='<docid>' GROUP BY S.ITEM ORDER BY MAX(I.NAME)
Select st.sno,st.SunCode,st.dispname,St.AMOUNT From Suntran St  Where St.DocID='<docid>' order by sno
SELECT Distinct(I.Kitchen) AS Kitchen,D.Name AS Department FROM (ItemMast I INNER JOIN Stock S ON I.Code=S.Item)  INNER JOIN Depart D ON I.Kitchen=D.Code WHERE S.DocID='<docid>' ORDER BY I.Kitchen
Select R.NAME,R.HEADER1,R.HEADER2,R.HEADER3,R.HEADER4,R.COMPANYTITLE,R.OUTLETTITLE From DEPART R  Where R.CODE='<outlet>'
SELECT Slogan1 FROM Depart WHERE Code='<outlet>'
SELECT Slogan2 FROM Depart WHERE Code='<outlet>'
SELECT TOKENPrint FROM Depart Where Code='<outlet>'
Select RateInclTax from depart where code='<outlet>'
Select KOtYn from depart where Code='<outlet>'
Select ShortName,Code from Depart Where Code='<outlet>'
Select Count(*) From SundryType WHERE V_Type='<vtype>'
SELECT COUNT(*) FROM LASTVOU WHERE LOGSITE_CODE='<LOGSITE>' AND ENAME='<ename>' AND UNAME='<user>'  (reused)

-- RsSaleBillSplit: Split logic uses Stock/Sale1 header + FGrid distribution
-- HMS.bas POSEnt 13 cases:
-- Index 0: Change Rest (FrmChangeRest if MemVar_1F811A4 empty)
-- Index 1: RsTbChange
-- Index 2: RSSaleBill
-- Index 3: fdNDAcPostChrg (Item wise Sale) — checks Depart.RestType!='Production'
-- Index 4: POSBillReprint
-- Index 5: RsSaleBillSplit
-- Index 6: RsPOSDisplay
-- Index 7: RsBookingEntry (Voucher_Type Ncat='ORDER')
-- Index 8: RSSaleBillDisplay
-- Index 9: POSAdvanceDepDialog (Voucher_Type Ncat='PADV', 'B'+ShortName)
-- Index 10: RsKOTTransfer
-- Index 11: RsTokenEntry
-- Index 12: RsAssignDelivery
-- Index 13: RsPaymentReceice
-- Also: Enviro.TouchScreen read at POSEnt entry: Select * from Enviro (TouchScreen='Yes'/'No')
-- POSMas 28+ cases: OutLetMast, OutLetSundry, FrmWaiterMast, RsTableMast, FrmItemMast, FrmItemGroupMast (RestType='Finish'), RsMenuItemEntry, FrmMenuRate, FrmNCType, frmSessionMast, FrmConsumMast9999, SchemeMast, pHappyHours, NewHappyHours, frmComboMast, etc.

-- RsPaymentReceice: PayType branching
Select count(Distinct Bill_no) from paycharge where bill_no is not null and bill_no<>'' and FolionoDocid='<foliodocid>'
Credit Card ExpDate check: if CDate(Txt[9]) <=  MemVar_1F920EC then "Credit Card has been Expired"
Void check via paycharge Distinct Bill_no >0 blocks re-print for Room Service
```

### 1.2 Settlement / POS_SBill / PayCharge / SunTran / Void

VB6 settlement in `RSSaleBill` (full-save transactional):
- Writes `Sale1` header + `Sale2` (tax lines Group-by Item), `SunTran` (sundry), `PayCharge` (multiple paytypes, Room/Company/Emp/Member branching), `Stock` (`QtyIss` per item, `GodownCode`, `RestCode`, `LogSite_Code`), then **closes KOTs**: `UPDATE KOT SET Pending='N', ContraDocId='<Sale DocId>' WHERE DocId='<KOT DocId>'` (link), and for `RSSaleBillSplit` distributes to `SplitBillDetail` (`DocId/VNo/VDate/VTime/RestCode/TableNo/SNo/SNo1/ItemName/OQty/Rate/BillQty/BillCat/Site_Code/LogSite_Code`), plus `POS_SBill (DocId, OutletDocId, OutletCode)` for multi-outlet split.

`POS_SBill` schema: PK `(DocId, OutletDocId)`, `OutletCode varchar(6)`.

Void / Delete in VB6:
```sql
-- Sale bill void/delete (RSSaleBill):
UPDATE KOT SET Pending='Y', ContraDocId=NULL, ContraSNo=0 WHERE ContraDocId='<sale_docid>'
DELETE FROM Sale2 WHERE DocId='<sale_docid>'
DELETE FROM SunTran WHERE DocId='<sale_docid>'
DELETE FROM PayCharge WHERE DocId='<sale_docid>'
DELETE FROM Stock WHERE DocId='<sale_docid>'   -- implicitly via Sale delete
DELETE FROM Sale1 WHERE DocId='<sale_docid>'
DELETE FROM SplitBillDetail WHERE DocId='<sale_docid>'  -- if split
DELETE FROM POS_SBill WHERE DocId='<sale_docid>'
```

### 1.3 Scheme / HappyHours

VB6 `pHappyHours` (Apply) — constructs dynamic filter `var_9C` based on which header fields filled (ItemCat / ItemGroup / RestCode) + date overlap guard:
```sql
-- Guard: overlapping discount already exists for same RestCode
Select HappyHours.* From HappyHours
Where ItemCode In (Select Code From ItemMast <where_ItemCat/Group/Rest filter> AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO'))
AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO')
And (AppDate Between <start> And <end> Or EndDate Between <start> And <end>)
And isNull(Active,'')='Y' And RestCode='<rest>'

-- If overlap found and user declines, abort; if continues, insert only Code Not In (overlap set)
Select DispCode,Code As ItemCode,Name As ItemName,ItemCatCode,ItemGroup From ItemMast <where> And Code Not In (<overlap ItemCodes>) AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO') Order By Code
-- Rate source:
Select ItemCode,Rate,AppDate From ItemRate Where RestCode='<rest>' AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO') Order By AppDate Desc,ItemCode
-- Line calc (VB6): ValueType Percent vs Amount → grid  columns Rate/Value/DisAmt inserted into HappyHours (SchemeCode, RestCode, ItemCode, AppDate, DiscountType, DiscountValue, FromTime/ToTime, Active='Y', EndDate, Site_Code, LogSite_Code)
```

VB6 `NewHappyHours` (Free Items / SchemeItemDetail + FreeItemDetail):
```sql
-- Headers: txt[0]=Scheme Name (SchemeMast.Name), txt[8]=Outlet Name (Depart.Name)
-- Days built from 7 checkboxes chkday(1..7) -> varchar(7) e.g. 'YYYYNNN'
-- Grid FGrid (buy):  Item + Qty
-- Grid FGrid1 (free): FreeItem + FreeQty
-- Insert head: SchemeMast (Code, Name, Startdate, Enddate, FromTime, ToTime, Days, Active, Site_Code, LogSite_Code)
-- Then:
INSERT INTO SchemeItemDetail (Code, SNo, SchemeCode, Appdate, Enddate, FromTime, ToTime, RestCode, ItemCode, Qty, Site_Code, LogSite_Code, Days, Active, Rate)
INSERT INTO FreeItemDetail  (Code, SNo, SchemeCode, RestCode, FreeItem, FreeQty, Site_Code, LogSite_Code)
-- Item lookup for both grids:
Select I.Code,I.Name as Name,I.Unit,IG.Name as ItemGroup,DispCode,D.Name as OutLetName,D.Code as OutLetCode From (ItemMast I INNER join ItemGrp IG on I.ItemGroup=IG.Code)INNER Join Depart D On D.Code=I.RestCode Where (I.LOGSITE_CODE='<LOGSITE>' or I.LOGSITE_CODE='HO') AND (I.ACTIVEYN='Yes' ...) AND I.Type='Finish' And I.DispCode<>9999 AND D.Code='<rest>' Order by I.Name
```

---

## 2) Python SQL — Actual (What the port does today)

| Area | Python module | SQL used | VB6 verbatim matched? |
|---|---|---|---|
| **KOT creation `create_kot()`** (`core/pos.py:306-369`) | `_next_kot_vno()` → `SELECT ISNULL(MAX(CAST(VNo AS int)),0)+1 FROM KOT WHERE RestCode=? AND CONVERT(date,VDate)=?` ; `INSERT INTO KOT (DocId,VNo,VDate,VType,VPrefix,Site_Code,RestCode,RoomCat,RoomType,RoomNo,Pending,Sno,VTime,Item,Qty,VoidYN,Waiter,U_Name,U_EntDt,U_AE,NCKOT,Rate,Amount,Reasons,Remarks,LogSite_Code,NCType,Printed,FreeSno,SchemeCode,Description,Party,ItemRestCode,TokenNo) VALUES (?,?,?,?,?,?,?,?,?, 'Y', ?,?,?,?,?,?,?, 'N',?,?,?,?,?,?,?,?, '',..., ...)` | ❌ **Deviated:** VB6 KOT header `RoomCat/RoomType` is populated from `Depart/Enviro` (REST vs RO vs TB). Python hardcodes `''`. VB6 `LogSite_Code` uses **`MemVar_1F92078` (LOGSITE from Enviro/Site)**, Python uses `SITE_CODE` (Analysis.ini) and even hardcodes `'KK'` inside `create_kot` Value list — mismatch. VB6 `VType` is resolved from `Voucher_Type` (`'B'+ShortName` + Ncat logic), Python hardcodes `"K"`. VB6 `Vprefix` from `Voucher_Type`, Python `"K"`. VB6 `TokenNo` increments via Bottom.
| **KOT next_vno** | `pos.py:_next_kot_vno()` | Uses `RestCode + VDate` only | ❌ VB6 uses **`RestCode + RoomCat + RoomType + RoomNo + VDate`** for running order and **LOGSITE-aware**. Also VB6 `LASTVOU` sequence (`LASTVOU.ENAME` per RestCode+LOGSITE+UNAME) is the canonical next VNo; Python ignores `LASTVOU` entirely.
| **Pending lists** (`pos_kot.py`) | `_KOT_PENDING = "Pending='Y' AND ISNULL(VoidYN,'N')<>'Y' AND ISNULL(NCKOT,'N')<>'Y' AND ISNULL(DelFlag,'') IN ('','N') AND ISNULL(ContraDocId,'')=''"` ; `pending_kot_tables()` / `pending_kot_list()` | ✅ **Mostly correct** — matches VB6 `Pending='Y' AND VOIDYN<>'Y' AND (DELFLAG='N' or DELFLAG='') AND NCKOT<>'Y' AND ContraDocId=''` pattern. |
| **TableChange / KOTTransfer updates** | `pos_kot.py: table_change()`, `kot_transfer()` | `UPDATE KOT SET RoomNo=?,U_Name1=?,U_EntDt1=getdate(),U_AE1='E' WHERE RestCode=? AND <pending> AND RTRIM(RoomNo)=?` ; Room Service variant sets `RoomCat` from `RoomOcc` | ✅ Structure correct; ⚠️ LOF: VB6 uses `LOGSITE_CODE` filter on RoomMast lookup, and RoomService also resolves via `(RC.LOGSITE_CODE='<LOGSITE>' or RC.LOGSITE_CODE='HO')` — Python now does this for `kot_transfer` RO path but **not for `table_change()` vacancy list**.
| **To-Table vacancy list** | `pos_kot.py: pending_kot_tables()` vs `RsTbChange` | Python filters `KOT` pending grouped by RoomNo. VB6 derives vacancy as `RoomMast WHERE Type='TB' AND RESTCODE='<rc>' And Code NOT IN (SELECT DISTINCT RoomNo FROM KOT ...)` | ❌ Python `_outlets()` in `kot_transfer_ui.py` adds synthetic `KKFOM` and queries `Depart` not `RoomMast`; vacancy To-list diverges from VB6.
| **Sale1 / Sale2 / SunTran / PayCharge / Stock full-save** (`pos_sales.py:sale_bill_full_save()`) | `INSERT INTO Sale1 (...) VALUES (?,?,?,?,?,?,?,?,... getdate(),'A', ?)` ; `INSERT INTO Sale2 (...LogSite_Code,SeqNo)` ; `INSERT INTO SunTran (...SiteCode,LogSite_Code)` ; `INSERT INTO PayCharge (...)` ; `INSERT INTO Stock (QtyIss,LogSite_Code,DelFlag)` ; `UPDATE KOT SET Pending='N',ContraDocId=? WHERE DocId=? AND ISNULL(VoidYN,'N')<>'Y'` | ⚠️ Partial: Schema columns trimmed (VB6 `Sale1` has `FolioNo int`, `HouseKeep/FrontOff/...`, `MenuSpl1-4`, `FrBookDate/FrBookTime/ToBookDate/ToBookTime`, `ExpAtt/GuarAtt/CoverRate`, `FuncName`, `BookDocId/HallRent/...`, `U_EntDt/U_AE/DeliveredYN/PRINTED/RecNo/...` — Python drops many). `LogSite_Code` uses `SITE_CODE` (analysis.ini) not VB6 `MemVar_1F92078` (LOGSITE). VB6 Stock also inserts `ContraDocId/ContraSno/RoomCat/RoomNo/Remarks/KOTDocId/KOTSno/VTime/Total/RoundOff/DepartCode/ShiftCode/RefDocId` — Python omits most.
| **POS_SBill** | *Not implemented* in Python | VB6: `POS_SBill (DocId, OutletDocId, OutletCode)` — settlement linkage for split/multi-outlet | ❌ **Missing module** — no `core/pos_sbill.py`, no API. `RsSaleBillSplit` → `SplitBillDetail` exists but `POS_SBill` never written/read.
| **SplitBillDetail** | `pos_kot.py:_SPLITBILL_COLS` + `splitbill_*` | `INSERT INTO SplitBillDetail (DocId,VNo,VDate,VTime,RestCode,TableNo,SNo,SNo1,ItemName,OQty,Rate,BillQty,BillCat,Site_Code,U_Name,U_EntDt,U_AE,DelFlag,LogSite_Code)` | ✅ Columns match VB6 PK + `BillCat`. ⚠️ VB6 SplitBillDetail is written together with `SplitSale1/SplitSale2` + Stock redistribution (see §3).
| **Scheme / HappyHours** | `pos_happy.py` + `pos_masters.py` (SchemeMast/SessionMast/ItemCat) | `HappyHours (SchemeCode,RestCode,ItemCode,AppDate,DiscountType,DiscountValue,FromTime,ToTime,Active,EndDate,Site_Code,LogSite_Code)` ; `HappyHoursHead` ; `SchemeItemDetail (Code,SNo,SchemeCode,Appdate,Enddate,FromTime,ToTime,RestCode,ItemCode,Qty,Days,Active,Rate)` ; `FreeItemDetail (Code,SNo,SchemeCode,RestCode,FreeItem,FreeQty)` | ⚠️ VB6 `pHappyHours` discount calculation is **`HappyHoursHead` driven** (SchemeCode PK) + per-item `FromTime/ToTime` windows + `LOGSITE='HO'` fallback on **ItemMast filter** + ItemRate join for base rate — Python stores rows but has **no `resolve_rate(item, RestCode, AppDate)`** via `ItemRate`, and **no calc at bill time** (RSSaleBill never applies `HappyHours`/`SchemeItemDetail` to `Sale1.DiscAmt/DiscPer` or Stock `Rate`). `NewHappyHours` day-string built wrong (VB6 7 checkboxes → `Days varchar(7)` positional `"MTW..."`, Python stores verbatim `days`).
| **Waiter / Table / Session masters** | `pos_masters.py` (Waiter/NCType/Session/Scheme/ItemCat/DeliveryBoy/Shift/Combo), `pos_table.py` (RoomMast Type='TB'), `pos.py:get_waiters/get_tables/get_items/get_nc_types` | Mixed `Depart` / `RoomMast` / `ItemMast` lookups | ⚠️ `pos.py:get_tables()` ignores `LOGSITE_CODE` and `RESTCODE` filter (VB6 `RoomMast Where type='TB' AND RESTCODE='<LocalRestCode>' AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO')`). `get_items()` missing `ItemMast. Type='Finish' And DispCode<>9999 And ACTIVEYN='Yes'` + `ItemRate` join. `get_waiters()` missing `RestCode` scoping.
| **LOGSITE / HO fallback / menuHelp OutletCode** | Across all Python | Python uses `db.get_site_code()` (Analysis.ini) for every insert as both `Site_Code` and `LogSite_Code` | ❌ VB6 pattern everywhere is `(LOGSITE_CODE='<MemVar_1F92078>' OR LOGSITE_CODE='HO')` on **reads**, and **insert** `Site_Code=MemVar_1F92078, LogSite_Code=MemVar_1F92078` (current site). `HO` rows are shared masters; Python never filters `HO` on reads, and hardcodes `LogSite_Code='KK'` in `create_kot()`. `menuHelp` `OutletCode` (RestCode) scoping is missing in `pos.py:get_items()` and `pos_sales_ui` sale list.
| **Enviro.TouchScreen / KOTPrinting / RateInclTax** | `pos_entry.py` / `HMS.bas:POSEnt_Click` entry guard | VB6 reads `Select * from Enviro` and branches on `TouchScreen` (`"Yes"` → touch form, else offline form), also `KOTPrinting` (`'Seperate for All Kitchen'` vs combined), `RateInclTax` | ❌ Python `pos_entry.py` stubs `posent_click(index)` as pure dict routing with `menu_name_allowed()` only; no `Enviro` TouchScreen branch, no `Depart.RestType` guard (`Production` blocked for Item-wise Sale), no `Voucher_Type` Adv_Type resolution.
| **Bill printing** | `ui: none` (only info stub) vs `POSBillPrint.bas` | VB6 writes `C:\\reptmp\\TEXTFILE.TXT` → `TYPE ... > <Printer>` / `SBILL.BAT` / `SBILL.PIF`, with outlet headers (`Depart.HEADER1-4`, `COMPANYTITLE`, `OUTLETTITLE`), `Slogan1/2`, waiter, KOTNo, Stock aggregation, SunTran lines, per-kitchen token sections | ❌ Python `kot_entry.py:_on_print()` and `pos_sales_ui.py:_print_sale()` are `"coming soon"` stubs.

---

## 3) Gap Table (Must-Fix, Should-Fix, Nice-to-Have)

| # | Gap | VB6 evidence | Python current | Impact | Priority |
|---|---|---|---|---|---|
| G1 | **LOGSITE vs SITE_CODE conflation** — every SELECT misses `OR LOGSITE_CODE='HO'` fallback | `RsKOTEntry`, `RsKOTTransfer`, `NewHappyHours`, `pHappyHours`, `RSSaleBill` — all ItemMast/Depart/RoomOcc reads use `(LOGSITE_CODE='<LOGSITE>' OR LOGSITE_CODE='HO')` | Python uses `SITE_CODE` from `Analysis.ini` for both columns; `create_kot` even hardcodes `'KK'` | HO masters invisible; multi-site data missing; TO-lists wrong | 🔴 Must-Fix |
| G2 | **NEXT_VNO via LASTVOU, not MAX(VNo)** — VB6 uses LASTVOU sequence per `LOGSITE+ENAME+UNAME`; also `VDate+RoomCat+RoomType+RoomNo` discrimination | `RsKOTEntry` / `RsTbChange` — `SELECT COUNT(*)/DOCID FROM LASTVOU WHERE LOGSITE_CODE=... AND ENAME=... AND UNAME=...` | `pos.py:_next_kot_vno()` does `MAX(CAST(VNo AS int))+1 WHERE RestCode=? AND CONVERT(date,VDate)=?` | Duplicate VNo under concurrent users / date-boundary; diverges from VB6 numbering | 🔴 Must-Fix |
| G3 | **POS_SBill completely absent** | `moondata.sql` `POS_SBill`; `RsSaleBillSplit` settlement writes `POS_SBill` forOutletDocId split | No module, no API, no UI | Multi-outlet split/settlement data loss; reprint fails | 🔴 Must-Fix |
| G4 | **Sale1 full col set truncated** — VB6 inserts 60+ cols incl. `FolioNo int, HouseKeep/FrontOff/Engg/Security/Chef/Board, MenuSpl1-4, FrBookDate/ToBookDate, ExpAtt/GuarAtt, CoverRate, FuncName, BookDocId/HallRent/TotalPerCover/Amount/Advance/RecNo/CrCard..., DeliveredYN, PRINTED, AU_Name/AU_EntDt, Redemption, DiscRemark, CGST/SGST/IGST/EditRemark` | `moondata.sql Sale1` + `RSSaleBill.frm` header mapping | `pos_sales.py:SALE1_COLS` only ~31 cols; `sale1_insert()` omits audit `U_Name1/U_EntDt1/U_AE1`, `LogSite_Code` wrong, `FolioNo` absent | Bill reprint, night-audit, eInvoice, hall/room folio posting break | 🔴 Must-Fix |
| G5 | **Stock full col set truncated** — VB6 Stock has `ContraDocId/ContraSno, RoomCat/RoomNo, Remarks, KOTDocId/KOTSno/VTime, Total/RoundOff, DepartCode, GodownCode, ShiftCode, RefDocId, FreeSno, SchemeCode, SeqNo, VoidYN` | `POSBillPrint` + `RSSaleBill` Stock insert | `pos_sales.py:sale_bill_full_save()` Stock insert only 12 cols | Kitchen stock, audit trail, scheme free-item linkage lost | 🔴 Must-Fix |
| G6 | **RoomCat/RoomType not populated on KOT** | `RsKOTEntry` resolves `RoomCat` from `RoomMast/Depart` (REST/TB/RO) + `RoomType` | `pos.py:create_kot()` sets `RoomCat='',RoomType=''` | `Running Order` check, printing, reports partition by RoomCat fail | 🔴 Must-Fix |
| G7 | **Voucher_Type resolution (VType/VPrefix/Adv_Type)** | `HMS.bas:POSEnt_Click` Index 3/9 — `Select 'B'+ShortName...`, `V_Type Where Ncat='ORDER'/'PADV'` | Python hardcodes `Vtype='K'/'SAL'`, `Vprefix='K'` | Voucher series mismatch, advance deposit vs. sale confusion | 🔴 Must-Fix |
| G8 | **SplitBillDetail business rule — BillCat/SNo1/OQty vs BillQty** | `RsSaleBillSplit.frm` — distributes `OQty` into up to 3 `BillCat (1..3)` with `FGrid` → `TxtGt1/2/3` totals, `SNo1` ties to original line | Python stores rows but never enforces `OQty = Σ BillQty` nor `BillCat 1..3` | Split bills unbalanced, settlement short | 🟡 Should-Fix |
| G9 | **Scheme/HappyHours calculation never applied at bill time** | `pHappyHours` / `NewHappyHours` + `POSBillPrint` rate lookup (`ItemRate`) + `RateInclTax` handling | Python CRUD only; `pos_sales` never reads `HappyHours`/`SchemeItemDetail`/`FreeItemDetail`/`ItemRate` | Discounts & free items never affect NetAmt; VB6 workflow not replicated | 🔴 Must-Fix |
| G10 | **Enviro flags — TouchScreen / KOTPrinting / RateInclTax / KotYN / AutoSplit** | `HMS.bas:POSEnt_Click` (`Select * from Enviro` → `TouchScreen`), `Depart.RateInclTax`, `Depart.KotYN`, `Depart.AutoSplit`, `Enviro.KOTPrinting` | Python mast list ignores all flags; `pos_entry.py` stubbed | Touch vs offline forms wrong, printing topology wrong, tax double-count | 🟡 Should-Fix |
| G11 | **PayCharge branching (Room/Company/Emp/Member/CreditCard)** | `RsPaymentReceice.frm` — frames `FrSendRoom/FrComp/FrEmp/FrMember/FrCCDet/FrChqDet`, `DGMember/DGCompany/DGRoom/DGEmp`, `ExpDate` validation vs `MemVar_1F920EC`, `paycharge` Distinct Bill_no guard | `pos_sales.py:paycharge_insert()` generic, no paytype routing, no folio-guard | Room folio double-bill, expired card accepted, member credit unchecked | 🟡 Should-Fix |
| G12 | **Table vacancy & outlet scoping via RoomMast + LOGSITE** | `RsTbChange` / `RsKOTTransfer` — `RoomMast Where type='TB' AND RESTCODE='<rc>' AND (LOGSITE_CODE='<LOGSITE>' or LOGSITE_CODE='HO')` | `pos.py:get_tables()` / `pos_kot.py:pending_kot_tables()` ignore RESTCODE & LOGSITE; `kot_transfer_ui._outlets()` fabricates `KKFOM` | Wrong table lists, cross-outlet leakage, vacancy guard broken | 🔴 Must-Fix |
| G13 | **Item lookup scoping — Type='Finish', DispCode<>9999, ACTIVEYN, ItemRate, Kitchen/Depart join** | `RsKOTEntry` / `RSSaleBill` DGItem — `ItemMast INNER join ItemGrp INNER join Depart INNER join ItemCatMast` with all predicates | `pos.py:get_items()` bare `ItemMast Where RestCode=?` + fallback `SELECT *` | Ghost items, hidden items shown, wrong rates (RateInclTax) | 🔴 Must-Fix |
| G14 | **NightAudit guard — KOTAtNightAudit/POSBillAtNightAudit** | `HMS.bas:NightAuditoR_Click Index 2` — `Select KOTAtNightAudit,POSBillAtNightAudit from Enviro where logsite_code='...'` blocks `fdAcPostChrg` | No guard in Python; KOT/bill mods allowed during audit | Audit trail breach | 🟡 Should-Fix |
| G15 | **Frontend gaps (PyQt parity)** | VB6: TopCtrl1 state machine (Add/Edit/Browse), FGrid inline grid with `TxtGrid` popup, `LblState New Order/Running Order`, `DG*` lookup popups (`FGPoint` shim), Member verify, NC Bill `ChkNCKOT` per-kitchen printing, Covers (`GuarAtt`), Remarks/Comments1..3, Token binding | `kot_entry.py` custom QTableWidget but: no `LblState Running Order` auto from VB6 `Select Top 1 VNo ...` query, no `GuarAtt/Covers` field, no `Member`/`NCType` header sync, `pos_sales_ui` is browser-only (no `RSSaleBill` bill-entry grid), `kot_transfer_ui` missing vacancy-aware To-list (VB6 excludes occupied tables) | Workflow mismatch (operators forced to think differently) | 🟡 Should-Fix |

---

## 4) Fixed Workflow (Exact VB6 — SAME SQL, no schema change)

### 4.1 KOT Entry — VB6-exact sequence (RsKOTEntry)

```text
1. Resolve LOGSITE = Enviro.LOGSITE_CODE (fallback Analysis.ini only if Enviro empty)
2. Resolve LocalRestCode = POSMas/RsTableMast selection (also labelled LblRest)
3. Validate Txt[0]=VNo (non-zero, dup check Select Count(*) From KOT Where DocID='<docid>')
4. Validate Txt[1]=VDate between MemVar_1F920F4..MemVar_1F920FC (fin year)
5. Waiter: Txt[5] must exist in Waiter (LOGSITE_CODE='<LOGSITE>' or 'HO') and (ActiveYN='Yes' ...)
6. Table: Txt[4] = RoomMast.Code Where type='TB' AND RESTCODE='<LocalRestCode>' AND (LOGSITE_CODE='<LOGSITE>' or 'HO')
   - If Pax (Txt[13]) == 0: SELECT ISNULL(MAX(GUARATT),1) FROM (SELECT TOP 1 GUARATT FROM KOT WHERE RestCode='<rc>' And Pending='Y' ... AND ROOMNO='<tbl>' Order By Vno Desc)Q  → fill GuarAtt
   - If 'RO': resolve RoomOcc.GuestProf → GuestFolio.mFolioNoDocId → Select count(Distinct Bill_no) from paycharge where FolionoDocid='<foliodocid>' >0 → block "Guest Room Bill Already printed"
   - Then: Select Top 1 VNo From KOT Where VDate=<vdate> And RestCode='<rc>' And RoomCat='<roomcat>' And RoomType='<roomtype>' And RoomNo='<roomno>' And Pending='Y' ... Order By VNo desc
         → if Found: LblState='Running Order' else 'New Order'
7. FGrid lines: Item lookup via ItemMast query with LOGSITE+HO / Type='Finish' / DispCode<>9999 / ACTIVEYN; Unit from ItemMast.Unit; Rate via Select Rate,Appdate From ItemRate Where ItemCode='<code>' And AppDate <=<vdate> Order by Appdate Desc (respect Depart.RateInclTax)
8. Scheme/HappyHours overlay (if applicable):
   - If pHappyHours active for (RestCode, Item, AppDate, FromTime/ToTime) → DiscountType/DiscountValue → Rate' = Rate - disc (or % calc)
   - If NewHappyHours SchemeItemDetail/FreeItemDetail match (Qty threshold, Days includes weekday, FromTime/ToTime) → insert free line FreeSno->link, SchemeCode set
9. Next VNo: SELECT DOCID FROM LASTVOU WHERE LOGSITE_CODE='<LOGSITE>' AND ENAME='<B'+ShortName>' AND UNAME='<user>' ; if none, MAX(VNo)+1 per RestCode+VDate as fallback
10. INSERT KOT per Sno: (DocId, Sno, Vtype='<Voucher_Type.V_Type>', Vtime, VNo, Site_Code='<LOGSITE>', Vprefix='<Voucher_Type.Prefix>', Vdate, RestCode, RoomCat, RoomType, RoomNo, Item, Qty, Rate, Amount, VoidYN='N', Waiter, Pending='Y', KOTType, U_Name, U_EntDt=getdate(), U_AE='A', DelFlag='N', NCKOT, ContraDocId='', ContraSNo=0, Reasons, Remarks, LogSite_Code='<LOGSITE>', NCTYPE, FreeSno, Printed='N', Description, SchemeCode, Party, ItemRestCode=I.RestCode, SeqNo, GuarAtt, TokenNo)
    All on ONE connection/transaction; LASTVOU incremented.
11. NC path: if ChkNCKOT=1 → NC Bill print per Depart.PrintType / Enviro.KOTPrinting ('Seperate for All Kitchen' → loop per Depart.Code)
```

**Python fixes required** (no schema change):
- Replace `pos.py:create_kot()` hardcodes: source `VType/VPrefix` from `Voucher_Type` (`Select 'B'+ShortName From Depart Where Code=?` → `Voucher_Type Where V_Type=?`), resolve `RoomCat='REST'` + `RoomType='TB'|'RO'` from `RoomMast`, set both `Site_Code` and `LogSite_Code = LOGSITE` (Enviro), not `SITE_CODE`/`'KK'`, include `ItemRestCode` from ItemMast, use `ItemRate` for Rate, honour `RateInclTax`, and write `LOGSITE`-aware.
- Replace `_next_kot_vno()` with **LASTVOU** sequence: `SELECT DOCID FROM LASTVOU WHERE LOGSITE_CODE=? AND ENAME=? AND UNAME=?` else fallback `MAX(VNo)`.
- Add `LOGSITE_CODE='HO'` OR to every read (ItemMast/Depart/RoomMast/RoomOcc/Waiter).

### 4.2 Settlement (Sale / POS_SBill / SplitBill) — VB6-exact sequence

```text
1. Pre-check: Select 'B'+ShortName From Depart Where Code='<RestCode>' ; if RestType='Production' abort; V_Type from Voucher_Type Ncat check; SundryType count >0
2. next_vno: LASTVOU same as KOT (ENAME per Depart ShortName), else MAX(VNo) per RestCode+VDate
3. Build header (Sale1): DocId, Vtype, VNo, Vtime, Site_Code=LOGSITE, Vprefix, Vdate, RestCode, RoomCat, RoomType, RoomNo, FolioNo (int), Party, Total, DiscPer, DiscAmt, NonTaxable, Taxable, Tax, ServiceCharge, AddAmt, DedAmt, RoundOff, NetAmt, Remark, Waiter, FrBookDate/ToBookDate, MenuSpl1-4, FuncName, HouseKeep/...Chef/Board, KOTNo (csv of KOT DocIds), TokenNo, ExpAtt/GuarAtt/CoverRate, U_Name/U_EntDt/U_AE='A', HallRent/TotalPerCover/Amount/Advance, RecNo/RecDate/CrCard..., DelFlag='N', PRINTED='N', LogSite_Code=LOGSITE, DeliveredYN, PhoneNo/CustName/Addr1/Addr2/CashRecd/BookNo/SeqNo/CardNo/ServiceTax=CGST+SGST+IGST, EditRemark, Redemption/DiscRemark/CGST/SGST/IGST, FolionoDocid (from GuestFolio if RO), AU_Name/AU_EntDt
4. Build details (Sale2 / Tax lines): GROUP BY Item → BaseValue/TaxPer/TaxAmt per TaxCode; Sale2 (DocId,Sno,SNo1,Vtype,VNo,Site_Code,Vprefix,Vdate,RestCode,TaxCode,BaseValue,TaxPer,TaxAmt,U_Name,U_EntDt,U_AE='A',DelFlag='N',LogSite_Code,SeqNo)
5. Sundry (SunTran): per voucher SundryType → SunTran (DocId,Sno,Vtype,VNo,Vdate,PartyCode,SunCode,Limit,DispName,ROff,CalcFormula,SValue,Amount,BaseAmount,U_Name/U_EntDt/U_AE='A',SunAppDate=getdate(),RevCode,RestCode,DelFlag='N',SiteCode=LOGSITE,LogSite_Code=LOGSITE,SeqNo)
6. PayCharge: per paytype row → PayCharge (DocId,SNo,Vtype,VNo,Site_Code,VPrefix,Vdate,VTime,GuestProf/EmpCode/CompCode/Comments,PayCode,PayType,AmtCr/AmtDr,TipAmt,RoomCat/RoomType/RoomNo/FolioNo,CardNo/CardHolder/ChqNo/ChqDate/ExpDate,BookNo/BookType,U_Name/U_EntDt/U_AE='A',RestCode,BillAmount,ContraDocID,TaxPer,OnAmt,Split,Bill_No,SettleDate,BatchNo,Remarks,RefNo,PlanCode,SeqNo,RefDocId,LogSite_Code=LOGSITE,AU_Name/AU_EntDt) — branch per Frm* visibility (Room/Company/Emp/Member)
7. Stock: per Sale item → Stock (DocId,Sno,Vtype,VNo,Site_Code,Vprefix,Vdate,PartyCode,RestCode,RoomCat/RoomType/RoomNo,ContraDocId/ContraSno,Item,QtyIss (abs),QtyRec=0,Unit,Rate,Amount,TaxPer/TaxAmt,DiscPer/DiscAmt,VoidYN,Remarks,KOTDocId/KOTSno,VTime,U_Name/U_EntDt/U_AE='A',Total/RoundOff,DepartCode,GodownCode,DelFlag='N',LogSite_Code=LOGSITE,FreeSno,SchemeCode,SeqNo,ShiftCode,RefDocId)
8. KOT close: UPDATE KOT SET Pending='N', ContraDocId='<SaleDocId>', ContraSNo=0, U_Name1='<user>',U_EntDt1=getdate(),U_AE1='E' WHERE DocId IN (<kot docids>) AND ISNULL(VoidYN,'N')<>'Y'
9. If split: write SplitBillDetail per line (DocId,VNo,VDate,VTime,RestCode,TableNo,SNo,SNo1,ItemName,OQty,Rate,BillQty,BillCat 1..3,Site_Code,U_Name/U_EntDt/U_AE='A',DelFlag='N',LogSite_Code) and SplitSale1/SplitSale2 heads + POS_SBill (DocId, OutletDocId, OutletCode) for each outlet slice — all same txn.
10. Commit one txn on shared `cn`; on error rollback whole bill. Increment LASTVOU.
```

**Python `sale_bill_full_save()` — what to change without schema change:**
- Add `POS_SBill` write (new file `core/pos_sbill.py` or inside `pos_sales.py`) — reuse VB6 PK, no schema change.
- Expand `sale1_insert()`/`stock` insert to full col-list (missing cols filled with defaults: `FolioNo=0`, `HouseKeep=''`, `MenuSpl1..4=''`, `ExpAtt=0`, etc.) so VB6 reports/reprint see expected columns (currently truncated).
- Make Stock write carry `RoomCat/RoomType/RoomNo/ContraDocId/KOTDocId/VTime/DepartCode/GodownCode/SchemeCode/FreeSno/SeqNo`.
- Make PayCharge carry `LOGSITE` from Enviro (not `SITE_CODE`) and respect `Bill_No` linkage.
- Add HappyHours/Scheme calc hook before Total → NetAmt (see §4.3).

### 4.3 Scheme / HappyHours — Bill-time calc (VB6-exact, no new tables)

VB6 does discount at **pHappyHours Apply time** (pre-populates `HappyHours` rows) and at **RSSaleBill line calc time** (reads `HappyHours` + `HappyHoursHead` + `ItemRate` + `SchemeItemDetail/FreeItemDetail`).

Python fix (add helper, no schema change):

```python
# core/pos_happy.py — add (uses SAME VB6 SQL verbatim)
def resolve_rate(item_code: str, rest_code: str, vdate, cn=None) -> float:
    # Select Rate,Appdate From ItemRate Where ItemCode=? And AppDate <=? Order by Appdate Desc
    ...

def happyhours_discount(item_code: str, rest_code: str, vdate, vtime: str, cn=None) -> tuple[str,float]:
    # Select HappyHours.* From HappyHours Where ItemCode=? AND RestCode=? AND (LOGSITE_CODE=? or LOGSITE_CODE='HO')
    #   AND (AppDate Between ... Or EndDate Between ...) AND isNull(Active,'')='Y' AND FromTime<=vtime<=ToTime
    # Returns (DiscountType, DiscountValue)
    ...

def scheme_free_qty(scheme_code: str, item_code: str, qty: float, vdate, vtime, days_str, cn=None) -> float:
    # SchemeItemDetail + FreeItemDetail + Days + FromTime/ToTime match
    ...

# Call from sale_bill_full_save() per line:
#   base_rate = resolve_rate(item, rest, vdate)
#   disc_type, disc_val = happyhours_discount(item, rest, vdate, vtime)
#   line_rate = apply_discount(base_rate, disc_type, disc_val, rest RateInclTax flag)
```

VB6 `Days` is 7-char positional `"SMTWTFS"` (checked boxes → `Y`); Python must store same.

### 4.4 Waiter / Table / Session — VB6-exact masters

- **Waiter** — `Waiter (Code, Name, ActiveYN, RestCode, Site_Code, LogSite_Code)` — VB6 lists via `Waiter` where `LOGSITE_CODE` in (`LOGSITE`,'HO') and `RestCode` filter; Python must add it.
- **Table (RoomMast Type='TB')** — VB6 `RsTableMast` is `RoomMast` (`Type='TB'`, `Code`, `Name`, `RoomNo`, `RoomCat`, `RestCode`, `SeatingCapacity`, `HouseKeepStat`, `RoomStat`, `LOGSITE_CODE`). Python `pos_table.py` maps via `RoomMast` but must persist `SeatingCapacity/RoomStat` and filter `LOGSITE`.
- **Session** — `SessionMast (Code, Name, FromTime, ToTime)` used by kitchen display (leave intact; already correct).

---

## 5) Frontend / Backend Notes (What to change in UI)

### Backend (`core/`)

| File | Change | VB6 ref |
|---|---|---|
| `pos.py` | Fix `get_outlets()` → `SELECT Code, Name, ShortName, RestType, KotYn, RateInclTax FROM Depart WHERE (POS='Y' OR KotYn='Y') AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')` ; `get_tables(rest)` → `RoomMast WHERE Type='TB' AND RESTCODE=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')`; `get_items(rest)` → full `ItemMast INNER JOIN ItemGrp/Depart/ItemCatMast` with `Type='Finish' AND DispCode<>9999 AND ACTIVEYN='Yes'` + HO fallback + `ItemRate` join; `get_waiters(rest)` → `Waiter WHERE RestCode=? AND (LOGSITE_CODE=? OR HO)` ; replace `create_kot()` → VB6 col-complete + `LOGSITE` + `RoomCat/RoomType/ItemRestCode` + `LASTVOU` + `ItemRate`; replace `_next_kot_vno()` → LASTVOU | `RsKOTEntry.frm` DGItem/DGRest, `RSSaleBill` DGItem |
| `pos_kot.py` | Keep pending predicate (already good); add `vacant_tables(rest, logsite)` → VB6 `RoomMast NOT IN (SELECT RoomNo FROM KOT pending)`; add `roomcat_for_table` helper; keep `table_change/kot_transfer` but ensure both use `LOGSITE` and transaction + LASTVOU not needed there | `RsTbChange`, `RsKOTTransfer` |
| `pos_sales.py` | Expand `SALE1_COLS`/`STOCK` cols to VB6-full; add `pos_sbill.py` (`POS_SBill` CRUD — PK DocId+OutletDocId); extend `sale_bill_full_save()` to write POS_SBill + full Stock + `FolioNo` + `RoomCat/RoomType` + `KOTNo` csv + free-item linkage; hook happy/scheme calc | `RSSaleBill.frm`, `POSBillPrint.bas` |
| `pos_happy.py` | Add `resolve_rate()`, `happyhours_discount()`, `scheme_free_qty()` helpers using verbatim VB6 SQL; keep CRUD | `pHappyHours.frm`, `NewHappyHours.frm` |
| `pos_entry.py` | Implement `Enviro.TouchScreen` branch (`Select TouchScreen, KOTPrinting, RateInclTax, KotYN, AutoSplit From Enviro/Depart`) and `Depart.RestType!='Production'` block + `Voucher_Type` `Ncat` checks before dispatch; return `TouchScreen` flag to caller | `HMS.bas:POSEnt_Click` lines 142BD4B...142C7E4 |
| `pos_masters.py` | Add `LOGSITE_CODE` filter to `waiter_list/nctype_list/itemcat_list` (HO fallback) | `POSMas_Click` |
| **NEW** `pos_sbill.py` | `POS_SBillAPI` — `list_by_doc(docid)`, `insert(docid, outlet_docid, outlet_code)`, `delete(docid)` — verbatim `POS_SBill` PK | `RsSaleBillSplit` |

### Frontend (`ui/`)

| File | Change | VB6 ref |
|---|---|---|
| `kot_entry.py` | Add header: `Covers (GuarAtt)`, `Member (Name/Code/CardNo)`, `Table` (Txt[4]) + `Remarks` + `NC Type` header (ChkNCKOT + Txt[7]), `LblState` auto-set via `Select Top 1 VNo ...` query; item grid: unit/rate auto from `ItemRate`+`RateInclTax`; show `RoomCat/RoomType` hidden but persisted; `Member verify` button → `FrmGuestStat` credit check (`PayCharge Distinct Bill_no` guard) | `RsKOTEntry.frm` |
| `pos_sales_ui.py` | Replace browser-only `PosSalesDialog` with true **Bill Entry** (`RSSaleBill`): header fields `VNo/VDate/RoomNo/Pax/Waiter/Remark`, `FGrid` item grid (Rate/Qty/Amount/Tax), `TxtPer/TxtGt` totals, `SunTran` sundry rows, `PayCharge` paytype frame switching (Room/Company/Emp/Member/CreditCard), `Split` toggle → `RsSaleBillSplit`, `Print` → `POSBillPrint` preview; keep current browser as `pos_sales_browser.py` | `RSSaleBill.frm` |
| `kot_transfer_ui.py` | Vacant To-table combo must be **vacant only** (VB6 `Code Not in (SELECT DISTINCT RoomNo FROM KOT pending)`) + `LOGSITE_CODE` filter; RoomService path shows `RoomOcc` guest names; single-call `pos_kot.kot_transfer()` txn | `RsKOTTransfer.frm`, `RsTbChange.frm` |
| `pos_table_ui.py` | Persist `SeatingCapacity` + `RoomStat` (Active/Inactive) + `RestCode` + `RoomCat` + `LOGSITE_CODE`; filter by outlet; colour `TVacantColor` handling | `RsTableMast.frm` `RoomMast` |
| `pos_stock_ui.py` | Show full `Stock` cols (`QtyIss/QtyRec/Unit/Rate/Amount, KOTDocId/KOTSno, GodownCode, SchemeCode/FreeSno, ShiftCode, RefDocId, VoidYN`) + filter by `DocId` | `Stock` `RsKitchenStk.frm` |
| `pos_happy_ui.py` (new) | Create `pHappyHours`-faithful Apply screen: header `Outlet/ItemGroup/ItemCat/StartDate/EndDate/PerAmt/Value/Days/From-To`, `FGrid` preview, `HappyHours` guard (`AppDate Between ... Or EndDate Between ...` + HO fallback) | `pHappyHours.frm` |
| `pos_happy_free_ui.py` (new) | Create `NewHappyHours`-faithful screen: `Scheme Name/Outlet/Start/End/From-To/Active/`, `FGrid` (buy) + `FGrid1` (free), 7 day checkboxes → `Days` string, bulk inserts | `NewHappyHours.frm` |

---

## 6) Debug Checklist — Verify EXACT VB6 Workflow (No Schema Change)

Run **against a copy of live KailashData2526** (never prod), and confirm each step uses the verbatim SQL above (print/log the SQL + params).

- [ ] **LOGSITE split:** `SELECT LOGSITE_CODE, Site_Code FROM Enviro` returns correct `MemVar_1F92078`; every SELECT includes `OR LOGSITE_CODE='HO'`; every INSERT sets `Site_Code=LOGSITE, LogSite_Code=LOGSITE`.
- [ ] **KOT create:** Create KOT for Outlet `XYZ`, Table `T1`, Item `ITEM001` at `2026-09-24 12:00`; observe `KOT` row has `RoomCat='REST'`, `RoomType='TB'`, `ItemRestCode=I.RestCode`, `Rate` from `ItemRate`, `VType/VPrefix` from `Voucher_Type`, `LogSite_Code=LOGSITE`, `Pending='Y'`, `Sno` sequential; `LASTVOU` incremented; second create same date increments `VNo` per LASTVOU not MAX.
- [ ] **Running Order** — second KOT same `RoomNo/VDate/RestCode` shows `LblState='Running Order'` via `Select Top 1 VNo ... Order By VNo desc`.
- [ ] **Table Change** — pending KOTs move: `UPDATE KOT SET ROOMNO...WHERE ROOMNO='<from>'` in one txn; To-list excludes occupied tables (vacant guard).
- [ ] **KOT Transfer (TB)** — `UPDATE KOT SET ROOMNO...WHERE VNO=?`; **(RO)** — `UPDATE KOT SET ROOMNO...,ROOMCAT=(RoomOcc.RoomCat) WHERE DOCID=?` after `RoomOcc` HO-aware lookup.
- [ ] **Settlement** — `sale_bill_full_save()` on one `cn` writes `Sale1` + `Sale2` + `SunTran` + `PayCharge` + `Stock` + `UPDATE KOT Pending='N',ContraDocId` + `POS_SBill`/`SplitBillDetail` (if split) atomically; `LASTVOU` bump; rollback on any fail.
- [ ] **SplitBillDetail** — `OQty = Σ BillQty` per `SNo/SNo1/BillCat`; `BillCat 1..3` totals in `TxtGt1..3`.
- [ ] **HappyHours** — `Select HappyHours ... AppDate Between ... Or EndDate Between ...` guard blocks duplicate; Apply fills `FGrid` with `ItemRate`; bill line Rate reflects `DiscountType/Value`.
- [ ] **NewHappyHours** — 7 day checkboxes → `Days` e.g. `YYYYNNN`; `SchemeItemDetail` + `FreeItemDetail` rows inserted with `LOGSITE`; free item appears in bill as 0-rate line linked via `FreeSno`.
- [ ] **PayCharge** — Room transfer guarded by `Select count(Distinct Bill_no) from paycharge where FolionoDocid=?` >0 blocks; CreditCard `ExpDate` validated; Member credit via `FrmGuestStat`.
- [ ] **Printing** — `POSBillPrint.bas` output matches VB6 layout (header `COMPANYTITLE/OUTLETTITLE/HEADER1-4`, `Slogan1/2`, waiter, `TOKENPrint` per-kitchen split when `Enviro.KOTPrinting='Seperate for All Kitchen'`).
- [ ] **NightAudit guard** — `Select KOTAtNightAudit,POSBillAtNightAudit from Enviro where logsite_code=?` blocks KOT/Sale edits when `Yes`.
- [ ] **No schema change** — all writes use existing columns only; no ALTER/CREATE; `POS_SBill` already exists in `moondata.sql`.

---

## 7) Evidence & Paths

- VB6 decompiled text (P-Code) — `FODER/*.frm`, `FODER/*.bas`, `FODER/MDIForm1.frm`, `FODER/POSBillPrint.bas`
- Live schema — `FODER/moondata.sql` (UTF-16, `CREATE TABLE [dbo].[KOT]`, `[Sale1]`, `[Sale2]`, `[Stock]`, `[SunTran]`, `[PayCharge]`, `[SplitBillDetail]`, `[POS_SBill]`, `[HappyHours]`, `[HappyHoursHead]`, `[SchemeMast]`, `[SchemeItemDetail]`, `[FreeItemDetail]`, `[Waiter]`, `[Depart]`, `[ItemMast]`, `[Enviro]`, `[ItemRate]`, `[LASTVOU]`, `[RoomMast]`, `[RoomOcc]`, `[GuestFolio]`, `[Voucher_Type]`, etc.)
- Python — `PYTHONE/core/pos*.py` (`pos_kot.py:1-547`, `pos_sales.py:1-666`, `pos.py:1-524`, `pos_entry.py:1-124`, `pos_stock.py:1-213`, `pos_masters.py:1-849`, `pos_happy.py:1-431`, `pos_table.py:1-252`), `PYTHONE/ui/kot_entry.py`, `pos_sales_ui.py`, `kot_transfer_ui.py`, `pos_table_ui.py`, `pos_stock_ui.py`
- Previous POS report for contrast — `PYTHONE/COMPARE_WORKSPACE/FINANCE_COMPARE.md`

---

## 8) What to Do Next (Ordered)

1. **Create `core/pos_sbill.py`** (POS_SBill CRUD) + wire into `sale_bill_full_save()` (transactional).
2. Fix `LOGSITE`/`HO` everywhere — add helper `get_logsite(cn)` in `core/db.py` (read `Enviro.LOGSITE_CODE`) and change every read to `... AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')`.
3. Replace `pos.py` KOT next-VNo + create path with **LASTVOU + ItemRate + RoomCat/RoomType/Voucher_Type** exact.
4. Expand `pos_sales.py` col-lists + wire HappyHours/Scheme calc into bill totals.
5. Rebuild `pos_sales_ui` as `RSSaleBill`-faithful entry; keep current browser as separate dialog.
6. Add `pos_happy_ui` + `pos_happy_free_ui` for `pHappyHours`/`NewHappyHours`.
7. Run full debug checklist on staging; log SQL verbatim vs VB6 strings above; no schema change.

---

*Report written to `PYTHONE/COMPARE_WORKSPACE/POS_COMPARE.md` — covers KOT, Sale1/Sale2 pagination, POS_SBill settlement, SplitBill, Scheme/HappyHours, Waiter/Table/Session, HO/LOGSITE/next_vno/menuHelp OutletCode/Scheme calc/TouchScreen-Enviro; SAME VB6 SQL, workflow, and column semantics preserved.*
