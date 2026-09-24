# INVENTORY / PURCHASE — VB6 vs Python Side-by-Side Compare (EXACT SQL, No Schema Change)

> **Module:** INVENTORY / PURCHASE — Indent, POrder, M.R., Purchase Bill, ReqSlip, Stock Issue, KClStk, StockTransfer, Opening Stock, Godown
> **Date:** 2026-09-24
> **Sources (VB6 decompiled, read FULL):** `PIndent.frm`, `pPOrder.frm`, `pMREntry.frm`, `pPBill.frm`, `pReqSlip.frm`, `pGIss.frm`, `kClStk.frm`, `FrmStockTransfer.frm`, `DepOpStk.frm`, `FrmOPStock.frm`, `Godown.frm`, `HMS.bas` (MatRep/MatVatR + MDI Inventory menus), `moondata.sql` (UTF-16 tables Indent/Indent1, POrder/POrder1, Purch1/Purch2, Stock/mCurStk/KClStk, TransIn/TransOut, GodownMast, ItemMast/ItemGrp/ItemCatMast, Voucher_Type, Voucher_Prefix, DateLock, Enviro, Help/MenuHelp, StockInHand .sql)
> **Python:** `PYTHONE/core/inventory.py:1`, `PYTHONE/core/purchase.py:1`, `PYTHONE/core/item.py:1`, `PYTHONE/HMS_py/core/db.py:1`, `PYTHONE/ui/inventory.py:1`, `purchase_order_ui.py:1`, `purchase_bill_ui.py:1`, `stock_issue_ui.py:1`, `stock_receive_ui.py:1`, `kitchen_clstk_ui.py:1`, `requisition_slip_ui.py:1`, `stock_adjust_ui.py:1`
> **Rule:** SAME VB6 SQL verbatim — no DB schema change. Report only; no writes performed during compare.

---

## 0) Executive summary

- VB6 is **LOGSITE_CODE + HO-fallback + NCAT + Voucher_Prefix.Date_From/To** driven. Every lookup is `LOGSITE_CODE='current' OR LOGSITE_CODE='HO'`, joined to `Voucher_Type` on **both** `Site_Code` and `LogSite_Code`, filtered by `NCAT` (`PIND`, `PORD`, `MRE`, `RQI`, `RQR`, `PBC`/`PBR`/`PRR`/`PRC`, `STOP`, `KSREC`/`KSISS`/`KMREC`/`KMISS`, `BMTC`/`RQS` etc.), and numbered via `Voucher_Type.Number_Method + Voucher_Prefix(Date_From,Date_To,Prefix,Start_Srl_No)` + `LastVou` + `DateLock`.
- Python is **SITE_CODE-only, MAX(VNo)+1, no Voucher_Prefix range, no HO fallback in most queries, no menuHelp check, no DateLock, no Enviro flags, and StockInHand is a single `SUM(QtyRec-QtyIss)` without NCAT/ConvRatio split**. That makes counts/balances diverge from VB6 on multi-site DBs and on Purchase-Unit mode.
- Highest-risk gaps: `next_vno` ignores `Voucher_Prefix.Start_Srl_No` and period window; `StockInHand` ignores `ConvRatio` and `S.GodownCode`/`S.Unit` grouping; `Godown`/`Item`/`Depart` combos miss `LOGSITE_CODE='HO'`; Purchase Bill `TaxStru` slab is flat `/2` not per `TaxStru.NATURE`; Opening Stock `STOP` is routed through generic `ADJ`; KClStk misses `AutoFillItemInKitchenClosingYN`.
- Fix posture: **patch SQL strings to VB6-verbatim, keep all writes parameterized, keep tables untouched**, gate with `menuHelp` + `DateLock` + `NegativeStockAllowYN` as VB6 does.

---

## 1) VB6 SQL — Verbatim (with exact source file)

### 1.1 Indent — `PIndent.frm`

```sql
-- Voucher type picker (Txt(0)) — PIndent.frm:Txt_GotFocus ~1199AFB
SELECT V_TYPE,DESCRIPTION FROM Voucher_Type
WHERE Site_Code='<Site_Code>' and logsite_code='<LogSite_Code>'
  and NCAT IN ('PIND') ORDER BY DESCRIPTION

-- Item lookup (Form_Load ~10483A2)
SELECT I.Code,I.Name as Name,I.Unit,I.PurchRate as Rate,I.LPurRate,
       I.ConvRatio as ConvFactor,I.IssueUnit as WtUnit,IC.taxStru
FROM ItemMast I INNER JOIN ItemCatMast IC ON I.ItemCatCode=IC.Code
WHERE (I.LOGSITE_CODE='<LogSite>' OR I.LOGSITE_CODE='HO')
  AND I.ItemType='Store' AND I.ActiveYN<>'No' ORDER BY I.Name

-- Department combo (Form_Load ~104842C)
SELECT Code,Name,Code as DCode,RestType FROM Depart
WHERE (LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND RestType='Store' AND RestType<>'FOM' AND OutletYn='N' ORDER BY Name

-- Browse list (Form_Load ~10484A8)
SELECT DocID as SearchCode,Remarks,I.Site_Code,I.LogSite_Code
FROM Indent I INNER JOIN Voucher_Type V
  ON (I.Vtype=V.V_Type AND I.LogSite_Code=V.LogSite_Code)
WHERE V.LOGSITE_CODE='<LogSite>' AND V.NCAT='PIND' ORDER BY DocID

-- DateLock gate (pPOrder/pPBill/pGIss common)
SELECT Name, Srno, IsNull(SDate,'') as SDate, IsNull(EDate,'') as EDate
FROM DateLock WHERE Name='Purchase Order Entry'  -- or 'Purchase Bill Entry' / Indent
```

`Indent` header `Indent.DocId` is 21-char `D + Site(2) + VType(6,ljust) + VPrefix(4,ljust) + VNo(8,rjust)` (`_make_docid` matches), `VTime='08:00'`, `ClearYN='N'`, both `Site_Code` and `LogSite_Code` populated.

### 1.2 Purchase Order — `pPOrder.frm`

```sql
-- Voucher picker
SELECT Description,V_Type FROM Voucher_Type
WHERE Site_Code='<Site>' AND LogSite_Code='<LogSite>' AND NCAT='PORD'

-- Supplier (SubGroup)
SELECT SubCode As Code,Name,(Add1+' '+Add2) As Address,C.CityName
FROM SubGroup LEFT JOIN City C ON SubGroup.CityCode=C.CityCode
WHERE ActiveYN=1 AND (Subgroup.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND Nature IN ('Supplier') ORDER BY Name

-- Item combo (Store)
SELECT I.Code,I.Name as Name,I.Unit,
       CASE WHEN I.LPurRate<=0 THEN I.PurchRate ELSE I.LPurRate END as PurchRate,
       I.ConvRatio as ConvFactor,I.IssueUnit as WtUnit,P.Name as GrpName,IC.taxStru
FROM (ItemMast I INNER JOIN ItemGrp P ON I.ItemGroup=P.Code)
     INNER JOIN ItemCatMast IC ON I.ItemCatCode=IC.Code
WHERE (I.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND I.ItemType='Store' ORDER BY I.Name  -- VB6 also filters IC.Active? no

-- Indent pending for PO (Indent1.ClearYN='Y' exclusion)
SELECT I.Docid as code, LTrim(right(I.Docid,8)) as Name
FROM Indent I WHERE (I.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND I.DOCID NOT IN (SELECT INDENTDOCID FROM PORDER1 WHERE Logsite_Code='<LogSite>')
  AND ... -- plus I.Vtype IN (SELECT V_TYPE FROM VOUCHER_TYPE WHERE NCAT IN (...) )

-- Next number — VB6 canonical (used in EVERY voucher)
SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No
FROM Voucher_Type VT INNER JOIN Voucher_Prefix VP
  ON (VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE
      AND VP.LOGSITE_CODE=VP.LOGSITE_CODE)
WHERE (VP.SITE_CODE='<Site>' AND VP.LOGSITE_CODE='<LogSite>'
       AND VP.V_Type='<VType>' AND '<VDate>' BETWEEN VP.Date_From AND VP.Date_To)

-- Enviro flags (pPOrder)
SELECT SmartPurchaseOrder,RateEditableInPO,DateEditableOnRequisitionYN
FROM Enviro WHERE LogSite_Code='<LogSite>'

-- Lines read-back
SELECT P1.*,I.Name As ItemName
FROM POrder1 P1 LEFT JOIN ItemMast I ON P1.ItemCode=I.Code AND I.ItemType='Store'
WHERE P1.DocID='<DocId>'  ORDER BY P1.Sno

-- ClearYN reversal guard on delete
SELECT IndentDocId,IndentSno FROM POrder1 WHERE Docid='<DocId>'
SELECT ClearYn FROM Indent1 WHERE Docid='<IndentDocId>' AND Sno=<Sno>
```

### 1.3 M.R. (Material Receipt) — `pMREntry.frm`

```sql
-- Voucher + Godown (SysYN='Y')
SELECT Description,V_Type FROM Voucher_Type
WHERE logSite_Code='<LogSite>' AND Site_Code='<Site>' AND NCAT='MRE'
SELECT Code,Name FROM GodownMast
WHERE (LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO') AND SysYN='Y' ORDER BY Name

-- Item (Store, ItemCat join, HO)
SELECT I.Code,I.BarCode,I.Name as Name,I.Unit,I.PurchRate as Rate,
       I.ConvRatio,I.IssueUnit,I.RestCode
FROM ItemMast I INNER JOIN ItemCatMast IC ON I.ItemCatCode=IC.Code
WHERE (I.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND I.ItemType='Store' -- + ActiveYN filter via ItemMast.ActiveYN

-- Browse GIN
SELECT G.DocID as SearchCode,V.Description As GINType,G.VNo As GINNo,
       cast(G.VDate as VarChar(11)) As GINDate,G.PartyName
FROM GIN G INNER JOIN Voucher_Type V
  ON (G.VType=V.V_Type AND G.LogSite_Code=V.LogSite_Code)
WHERE G.VDATE>=<From> AND G.VDATE<=<To> AND G.LogSite_Code='<LogSite>'

-- Pending POrders for MR
SELECT DISTINCT P1.Docid as Code,ltrim(Right(max(P1.DocId),8)) as Name,
       Max(P1.Vtype) as V_type,Max(P1.VDate) as V_Date,Max(SG.Name) As PartyName
FROM (POrder1 P1 LEFT JOIN Stock S
        ON (P1.Docid=S.ContraDocid AND P1.Sno=S.ContraSno))
LEFT JOIN SubGroup SG ON P1.PartyCode=SG.SubCode
-- WHERE P1.Qty - SUM(S.QtyRec) > 0 grouping

-- Rate fallback (VB6 rule for MR lines)
SELECT CASE WHEN LPurRate<=0 THEN PurchRate ELSE LPurRate END As Rate
FROM ItemMast WHERE Code='<Item>' AND RestCode='<RestCode>'
SELECT TOP 1 ItemRate As Rate FROM Purch2
WHERE VType IN ('PBPB','PBPC') AND Item='<Item>' AND RestCode='<Rest>'
```

### 1.4 Purchase Bill — `pPBill.frm`

```sql
-- Taxes per slab
SELECT TS.Code,TS.Limit,TS.TaxCode,RM.Name,TS.Rate,RoundOff,TS.CONDAPP,TS.NATURE
FROM TaxStru AS TS LEFT JOIN RevMast AS RM ON TS.TaxCode=RM.Code
WHERE TS.Code='<TaxStru>'

-- Purchase godown from Enviro
SELECT E.PurChaseGodown,G.Name FROM Enviro E
LEFT JOIN GodownMast G ON E.PurChaseGodown=G.Code
WHERE E.LOGSITE_CODE='<LogSite>'

-- Browse Purch1
SELECT DISTINCT P.DocId as SearchCode,P.DocID,P.LogSite_Code,P.Site_Code
FROM Purch1 P INNER JOIN VOUCHER_TYPE V
  ON (P.VTYPE=V.V_TYPE AND P.logSite_Code=V.LogSite_Code)
WHERE P.VDATE BETWEEN '<From>' AND '<To>' AND V.NCAT IN ('PBC','PBR',...)

-- Lines + tax structure name
SELECT DISTINCT S.*,I.Name as ItemName,DispCode,S.DiscApp as DApp,
       S.RoundOff as ROff,s.TaxStru as TaxCode,RateEdit,D.Code as DepartCode,
       D.ShortName as DepartName,G.Name as GodownName,TaxStru.Name as TaxStructure,
       S.AcCode As SaleAcCode,SG.Name As SaleAcName
FROM (((((Purch2 S LEFT JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
  LEFT JOIN ItemCatMast IC ON I.ItemCatCode=IC.Code) ...)

-- InvoiceNo auto
SELECT IsNull(Max(InvoiceNo),0)+1 FROM Purch1 WHERE LOGsite_code='<LogSite>'

-- DateLock + RoundOff + SundryType date gate
SELECT Name,Srno,IsNull(SDate,'') as SDate,IsNull(EDate,'') as EDate
FROM DateLock WHERE Name='Purchase Bill Entry'
SELECT RoundOffType FROM RoundOffSetting WHERE ModuleName='Purchase Bill'
SELECT * FROM SundryType WHERE V_Type='<LogSite>PURC'
  AND AppDate IN (SELECT DISTINCT TOP 1 AppDate FROM SundryType WHERE V_Type='<LogSite>PURC')
```

### 1.5 ReqSlip / Stock Issue — `pReqSlip.frm` + `pGIss.frm`

```sql
-- Requisition Slip list (Indent1 pending)
SELECT DISTINCT I1.VTime,I1.DocId,I1.VDate,I1.Remarks,G.Name AS Location,
       G.Code AS LocationCode,I1.VNo,I1.Vtype,I1.Vprefix,ItemMast.Name,
       Indent1.Qty,Indent1.Unit,Indent1.Sno,G1.Name AS Godown,G1.Code AS GodownCode,
       Indent1.Rate,Indent1.Amount
FROM Indent AS I1 LEFT JOIN Indent1 ON I1.DocId=Indent1.DocId
LEFT JOIN GodownMast G ON I1.Department=G.Code
LEFT JOIN GodownMast G1 ON I1.Godown=G1.Code
WHERE I1.LOGSITE_CODE='<LogSite>' AND I1.VType IN (SELECT V_Type FROM Voucher_Type WHERE NCAT='RQS')

-- GIss pending aggregation (grouped by Sno)
SELECT Indent1.Sno,Max(ItemMast.Name) as ItemName,Max(Indent1.Item) as ItemCode,
       Max(Indent1.Unit) as Unit,Max(Indent1.WTUnit) as WtUnit,
       Max(Indent1.DocId) as DocId,Max(GodownMast.Name) as Department,
       Indent.Department as DepartCode,Sum(Indent1.Qty) as ReqQty,'' as QtyIss,
       CASE WHEN MAX(ItemMast.LPurRate)<=0 THEN MAX(ItemMast.PurchRate) ELSE MAX(ItemMast.LPurRate) END
FROM (Indent INNER JOIN Indent1 ON ...) INNER JOIN ItemMast ON ...
GROUP BY Indent1.Sno,Indent.Department ...

-- Enviro guards for issue
SELECT ReqCompWise,BanquetKitchen,RateEditableInStockIssue,NegativeStockAllowYN,
       DateEditableOnRequisitionYN
FROM Enviro WHERE LOGSITE_CODE='<LogSite>'

-- Stock balance guard (VB6 checks before issue)
SELECT Isnull(Sum(S.RecdQty),0) AS Qty
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
WHERE S.LogSite_Code='<LogSite>' AND S.GodownCode='<Godown>' AND S.Item='<Item>'
-- and NCAT filter in-period vs opening
```

### 1.6 KClStk — `kClStk.frm`

```sql
-- Browse
SELECT DISTINCT Docid as SearchCode,K.Vtype As VType,
       Convert(Varchar(10),K.VNo) as VrNo,Convert(Varchar(12),K.VDate,103) as VDate,
       GodownMast.NAME AS Location
FROM KClStk K LEFT JOIN GodownMast ON K.DEPARTCODE=GodownMast.CODE ORDER BY VRno

-- Lines
SELECT KS.VDATE,KS.VTYPE,KS.VNO,KS.SNO,I.NAME ITEMNAME,KS.UNIT,KS.QTY,
       ISNULL(KS.REMARKS,'') REMARKS,KS.U_NAME,G.NAME LOCATION,KS.DEPARTCODE,KS.ITEM
FROM KClStk KS LEFT JOIN ITEMMAST I ON KS.ITEM=I.CODE AND I.ITEMTYPE='Store'
LEFT JOIN GODOWNMAST G ON KS.DEPARTCODE=G.CODE
WHERE KS.DOCID='<DocId>' ORDER BY KS.Sno

-- Item pool (Kitchen closing allowed)
SELECT Code,I.Name as Name,I.IssueUnit As Unit,I.PurchRate as Rate
FROM ItemMast I
WHERE (LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND (type IN ('Consumables','Store Item','Raw Material')
       OR (type='Finish' AND DirectSale='Y'))

-- Godown pool (Kitchen)
SELECT G.Code,G.Name FROM GodownMast G LEFT JOIN Depart D ON D.Code=G.Code
WHERE (G.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND D.RestType IN ('Kitchen','Staff Kitchen') ORDER BY G.Name

-- AutoFill flag (VB6)
SELECT AutoFillItemInKitchenClosingYN,DateEditableOnRequisitionYN
FROM enviro WHERE LogSite_Code='<LogSite>'
```

### 1.7 StockTransfer — `FrmStockTransfer.frm` + `FrmOPStock.frm` / `DepOpStk.frm`

```sql
-- StockTransfer source/target godowns (VB6 filters Depart RestType)
SELECT G.Code,G.Name FROM GodownMast G INNER JOIN Depart D
  ON (D.Code=G.Code AND D.LogSite_Code=G.LogSite_Code)
WHERE (G.LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND D.RestType IN (...) -- often 'Store' or not, but VB6 does joined fallback

-- Stock item for transfer (Store)
SELECT I.Code,I.Name,I.Unit,I.IssueUnit,I.PurchRate as Rate,I.ConvRatio
FROM ItemMast I WHERE (LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND I.ItemType='Store'

-- Opening Stock STOP — FrmOPStock.frm VERBATIM
SELECT Stock.DocId AS SearchCode,Stock.Vno,CAST(Vdate AS VarChar(11)) as OpeningDate,
       ItemMast.name as ItemName,Stock.QtyRec,Depart.Name as Department
FROM (Stock INNER JOIN ItemMast ON Stock.Item=ItemMast.Code AND ItemMast.ItemType='Store')
     INNER JOIN Depart ON Stock.DepartCode=Depart.Code
WHERE Stock.Vtype='STOP' ORDER BY Depart.Name

SELECT Stock.Vdate,Stock.Sno,Stock.Item,Stock.QtyRec Qty,Stock.Unit WtUnit,
       Stock.Rate,Stock.Amount,Stock.DepartCode,Stock.GodownCode,Stock.RecdQty WtQty,
       Stock.ConvRatio,ItemMast.Name as ItemName,ItemMast.IssueUnit Unit,
       GodownMast.Name as GodownName,Stock.GodownCode
FROM (Stock INNER JOIN ItemMast ON Stock.Item=ItemMast.Code AND ItemMast.ItemType='Store')
     INNER JOIN GodownMast ON Stock.GodownCode=GodownMast.Code
WHERE Stock.DocId='<DocId>' ORDER BY Stock.Sno

SELECT * FROM Stock WHERE VType='STOP' AND LogSite_Code='<LogSite>' AND Item='<Item>'
```

### 1.8 Godown — `Godown.frm`

```sql
SELECT G.Code as SearchCode,G.Name,G.shortname FROM GODOWNMAST G
WHERE (LOGSITE_CODE='<LogSite>' OR LOGSITE_CODE='HO')
  AND (SysYN<>'Y' OR SysYN IS NULL) ORDER BY G.Name

SELECT IsNull(Max(CAST(SUBSTRING(Code,3,4) AS INT)),1)+1 AS MyCode
FROM GodownMast WHERE SysYn<>'Y' AND Site_Code='<Site>'

SELECT Count(*) FROM GodownMast WHERE Name='<Name>'  -- and shortName duplicate check
```

### 1.9 StockInHand / Reports — `Stock In Hand.txt`, `StockInHand_Query.sql`, `StockInHand_PurchaseUnit.sql`, `HMS.bas:MatRep_Click` (NCAT lists)

**Single report uses 5 queries + VB combiner** (`HMS.bas` StkINHand @ `rInventRepView`):

**Mode 1 — Wt. Unit (group by S.Unit):**

```sql
-- 1) Main list  (VDate <= ToDate)
SELECT DISTINCT Item, I.Name AS ItemName, S.Unit AS IssueUnit,
       I.MaxStock*I.ConvRatio AS MaxStock, I.MinStock*I.ConvRatio AS MinStock,
       I.ReStock*I.ConvRatio AS ReStock, I.Type, I.DirectSale,
       ISNULL(ItemGrp.Name,'') ItemGrpName, I.ActiveYN
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
LEFT JOIN ItemGrp ON ItemGrp.Code=I.ItemGroup
WHERE S.LogSite_Code='<Site>' AND VDate<=<ToDate>
  -- optional: AND I.Type IN (...) AND I.ItemGroup IN (...) AND S.Item IN (...) AND S.GODOWNCODE IN (...)
  AND VT.NCAT IN ('PBC','PBR','PRR','PRC','STOP','MRE','RQI','RQR','KSREC','KSISS','KMREC','KMISS')
ORDER BY I.Name

-- 2) Opening Receipts (VDate < FromDate)
SELECT S.Item, SUM(S.QtyRec) AS Qty, S.Unit, SUM(S.Amount) AS Amt
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
WHERE S.LogSite_Code='<Site>' AND S.VDate < <FromDate>
  AND VT.NCAT IN ('PBC','PBR','STOP','MRE','RQI','KSREC','KMREC') AND S.QtyRec>0
GROUP BY S.Item,S.Unit HAVING SUM(S.QtyRec)>0

-- 3) Opening Issues (VDate < FromDate)
SELECT S.Item, SUM(S.QtyIss) AS Qty, S.Unit, SUM(S.Amount) AS Amt
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
WHERE S.LogSite_Code='<Site>' AND S.VDate < <FromDate>
  AND VT.NCAT IN ('PRR','PRC','RQR','KSISS','KMISS') AND S.QtyIss>0
GROUP BY S.Item,S.Unit HAVING SUM(S.QtyIss)>0

-- 4) Period Receipts (BETWEEN FromDate AND ToDate)
SELECT S.Item, SUM(S.QtyRec) AS Qty, S.Unit, SUM(S.Amount) AS Amt
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
WHERE S.LogSite_Code='<Site>' AND S.VDate BETWEEN <FromDate> AND <ToDate>
  AND VT.NCAT IN ('PBC','PBR','MRE','RQI','STOP','KSREC','KMREC') AND S.QtyRec>0
GROUP BY S.Item,S.Unit HAVING SUM(S.QtyRec)>0

-- 5) Period Issues (BETWEEN FromDate AND ToDate)
SELECT S.Item, SUM(S.QtyIss) AS Qty, S.Unit, SUM(S.Amount) AS Amt
FROM ((Stock S INNER JOIN ItemMast I ON S.Item=I.Code AND I.ItemType='Store')
      INNER JOIN Voucher_type VT ON (S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code))
WHERE S.LogSite_Code='<Site>' AND S.VDate BETWEEN <FromDate> AND <ToDate>
  AND VT.NCAT IN ('PRR','PRC','RQR','STOP','KSISS','KMISS') AND S.QtyIss>0
GROUP BY S.Item,S.Unit HAVING SUM(S.QtyIss)>0
-- Closing = OpRec - OpIss + PerRec - PerIss (Qty + Amt) in VB, then grid.
```

**Mode 2 — Purchase Unit (ConvRatio multiplied, group by S.Item only):**

```sql
-- Key diff: SUM(S.QtyRec*S.ConvRatio) and SUM(S.QtyIss*S.ConvRatio)
-- Opening Receipts:
SELECT S.Item, SUM(S.QtyRec*S.ConvRatio) AS Qty, SUM(S.Amount) AS Amt ... GROUP BY S.Item
-- Opening/Period Issues/Receipts use S.ConvRatio factor; VB6 source has a decompiler
-- glitch on one Mode-2 Issues query checking QtyRec>0 but logically QtyIss>0 — keep VB6 verbatim.
```

**Combined CTE (verified from `StockInHand_Query.sql`):** `ItemList` (ItemMast LEFT JOIN ItemGrp, `ItemType='Store'`) + `Opening` (CASE per NCAT on VDate<@FromDate) + `Period` (BETWEEN) + `LEFT JOIN` computes `ClosingQty/ClosingValue` with `ISNULL`. Site-filtered via `S.LogSite_Code=@SiteCode` and `VT` on `V_Type + LogSite_Code`.

### 1.10 MDI / HMS.bas — Inventory menus (`MatRep_Click`, `MatVatR_Click`)

```vb
' HMS.bas:MatRep_Click(Index)
' 0 PurchaseReg, 1 PurchaseSumm, 2 CashCreditPurch, 3 StockRegStore, 4 StockSummStore,
' 5 StockINHand, 6 KitchenStkRep, 7 ExcessConsumption, 8 RestIssue, 9 StoreIssReg,
' 11 DailyStoreIssRpt, 12 PurchaseLedger, 13 IssueReg, 15 StockSummaryP/SBasis,
' 16 ABCAnalysis, 17 PurchBill, 18 StoreIssueReport
' Each: rInventRepView.GRepFormName = "<Name>" ; Show

' MatVatR_Click: VATRegister, VATRegisterII/III, Form24AnnexureA, FormIII, UPVATXXIV
' All via rInventRepView — crystal expects Stock/Voucher_Type NCAT-filtered data.
```

---

## 2) Python SQL — Actual (what the migrated code runs)

### `core/inventory.py:70` — Godown

```sql
-- godown_list  (inventory.py:90)
SELECT Code, Name, ShortName, DepartCode, SysYn, U_Name, U_EntDt, U_AE
FROM GodownMast ORDER BY Code
-- NO Site/LOGSITE/HO/SysYn filter  vs VB6 §1.8

-- godown_get / exists / delete — same, PK only
```

### `core/inventory.py:152` — Indent

```sql
-- indent_list
SELECT TOP 200 DocId, VNo, VDate, Department, ClearYN, Godown
FROM Indent WHERE Site_Code = ? AND Vprefix = ? ORDER BY VNo DESC
-- VB6: Indent I JOIN Voucher_Type V ON I.Vtype=V.V_Type AND I.LogSite_Code=V.LogSite_Code
--      WHERE V.LOGSITE_CODE=? AND V.NCAT='PIND'  — missing in Python

-- indent_get — SELECT ... FROM Indent WHERE DocId=?
-- indent_create — INSERT Indent (DocId,'RQ',VNo,Site_Code,Vprefix,VDate,'08:00',Dept,Remarks,User,'N',Site,Godown,'')
```

### `core/inventory.py:232` — GIN / Purchase Receipt (MRE)

```sql
-- purchase_list (GIN)
SELECT TOP 200 DocId, VNo, VDate, PartyName FROM GIN
WHERE Site_Code=? AND Vprefix=? AND Vtype='MRCR' ORDER BY VNo DESC

-- gin_lines — Purch2 WHERE ContraDocId=?  (correct)
-- gin_create: INSERT GIN header + INSERT Purch2 (Vtype='PBPB' HARDCODED — BUG, should be MRE context)
--            + INSERT Stock (Vtype='MRE', QtyIss=0/QtyRec=..., GodownCode, IndentDocId/IndentSNo)
```

### `core/inventory.py:375` — POrder

```sql
SELECT TOP 200 DocId, VNo, VDate, PartyCode, Remark
FROM POrder WHERE Site_Code=? AND Vprefix=? AND VType='PORD'

-- porder_create:
-- INSERT POrder (DocId,VNo,VDate,'PORD',VPrefix,Site,Party,U_Name,'A',Site)
-- INSERT POrder1 (.. PartyCode,ItemCode,Qty,Unit,Rate,PerUnit=0,Amount,U_Name,'A',IndentDocId/IndentSNo,Spec,ConvRatio=1,WtQty=0,WtUnit='',Site,TaxStru='',TaxAmt=0,Total=Amount)
-- UPDATE Indent1 SET ClearYN='Y' WHERE DocId=? AND Sno=?  (per line)
```

### `core/purchase.py:198` — Purchase Bill (Purch1/Purch2)

```sql
-- purchase_bill_create:
-- vno = db.next_vno('Purch1', vtype, vprefix, site, cn)
-- docid = D + site + vtype(6) + vprefix(4) + VNo(8)  [:21]
-- INSERT Purch1 (DocId,VNo,Vdate,VType,Vprefix,Site_Code,RestCode='',Party,Total,Taxable=total,Tax,ServiceCharge,RoundOff,NetAmt,User,'A','N',...,CGST,SGST,IGST=net)
--   CGST/SGST = tax/2 flat — NOT per TaxStru.NATURE (VB6 rates via TaxStru TS+RM join)
-- INSERT Purch2 per line (Vtype=Vtype param, Site, Item, Qty, Unit, Rate, Amount, TaxPer/TaxAmt, Disc, GodCode='', TaxStru, AcCode='')
-- INSERT Stock per line (DocId,Sno,Vtype,VNo,Site,Vprefix,VDate,Party,Godown,Item,QtyRec=qty,AccQty=qty,Unit,Rate,Amount,User,'A',ContraDocId=docid,ContraSno=i,LogSite=site,'N')
```

### `core/inventory.py:570` — Stock operations

```sql
-- _next_vno  -> db.next_vno('Stock', vtype, vprefix, site, cn)
--   = SELECT MAX(VNo) FROM [Stock] WITH (UPDLOCK,HOLDLOCK)
--     WHERE [Vtype]=? AND Vprefix=? AND Site_Code=?   (inventory.py:136)

-- stock_create:
-- INSERT Stock (DocId,Sno,Vtype,VNo,Site_Code,VPrefix,VDate,VTime,PartyCode='',RestCode='',Room*='',Item,QtyIss/QtyRec split,Unit,Rate,Amount,User,'A',LogSite, GodownCode,'N')

-- stock_transfer (BMTC — two-row pair):
-- INSERT Stock (..., QtyIss=abs(qty) OR 0, QtyRec=abs(qty) OR 0, Amount=abs, ContraDocId=docid, ContraSno=paired, GodownCode=from/to)

-- stock_balance:
SELECT TOP 50 s.GodownCode, g.Name AS Godown, s.Item, i.Name AS ItemName,
       SUM(s.QtyRec - s.QtyIss) AS Bal
FROM Stock s LEFT JOIN GodownMast g ON g.Code=s.GodownCode
LEFT JOIN ItemMast i ON i.Code=s.Item
WHERE s.Site_Code=? AND s.Vprefix=? GROUP BY ... HAVING SUM(...)>0 ORDER BY SUM DESC
-- VB6: LogSite_Code filter + Voucher_Type NCAT + per-dept/godown + ConvRatio mode missing

-- stock_register / stock_register_detailed / kitchen_stock_report etc:
-- SELECT ... FROM Stock s LEFT JOIN ItemMast/GodownMast WHERE s.Site_Code=? (+ Vprefix? + Vdate range) GROUP BY ...
-- VB6: INNER JOIN Voucher_type VT ON S.VType=VT.V_Type AND S.LogSite_Code=VT.LogSite_Code + NCAT lists + Unit/ConvRatio grouping
```

### `core/purchase.py:536` — KClStk / INDENT1 / PORDER1 — direct table APIs

```sql
-- kclstk_list: SELECT TOP 500 ... FROM KClStk ORDER BY DocId,Sno
-- kclstk_insert: INSERT KClStk (DocId,Sno,Vtype,VNo,Site,Vprefix,Vdate,Item,Qty,Unit,DepartCode,Remarks,User,'A',Site)
-- indent1_list/lines/insert — INDENT1  (uppercase table name — live DB is INDENT1; Python uses correct quoting via db.query)
-- porder1_list/lines/insert — PORDER1
```

### `HMS_py/core/db.py:297` — next_vno

```python
SELECT MAX(VNo) FROM [table] WITH (UPDLOCK,HOLDLOCK)
WHERE [Vtype]=? AND Vprefix=? AND Site_Code=?
-- VB6: SELECT VT.Number_Method,VP.V_Type,VP.Date_From,VP.Prefix,VP.Start_Srl_No
--      FROM Voucher_Type+Voucher_Prefix WHERE VP.SITE_CODE=? AND LOGSITE_CODE=?
--        AND V_Type=? AND ? BETWEEN Date_From AND Date_To
--      + LastVou(ENAME='...', LogSite_Code) + DateLock(SDate/EDate)
```

---

## 3) Gap table — VB6 vs Python (flag: missing / diverged / wrong)

| Area | VB6 behavior (source) | Python current | Severity | Fix (SAME SQL, no schema) |
|---|---|---|---|---|
| **HO fallback (`LOGSITE_CODE='x' OR 'HO'`)** | Every master lookup: `ItemMast (I.LOGSITE_CODE='cur' OR 'HO')`, `Depart ...(OR 'HO')`, `GodownMast (G.LOGSITE_CODE='cur' OR 'HO')`, `SubGroup (LOGSITE_CODE='cur' OR 'HO')`, `Indent (I.LOGSITE_CODE='cur' OR 'HO')`, `Voucher_Type (Site+LogSite)` — `PIndent.frm:Form_Load`, `pPOrder.frm:Form_Load`, `pMREntry`, `pPBill`, `pGIss`, `kClStk`, `Godown.frm` | `inventory.py:90` `godown_list` has **no filter**; `indent_list` filters only `Indent.Site_Code` (no LogSite/HO, no Voucher_Type NCAT join); `item` lookups in many UIs use `ItemMast` without HO; `purchase_bill_ui` TaxStru lookup misses `(LOGSITE='cur' OR 'HO')` | **CRITICAL** — site-filtered DB shows fewer rows; HO masters invisible; PIndent dept combo differs | Add `WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO')` to every master SELECT; `Indent` browse must `JOIN Voucher_Type ON I.Vtype=V.V_Type AND I.LogSite_Code=V.LogSite_Code WHERE V.LOGSITE_CODE=? AND V.NCAT='PIND'` (or `'PORD'`/`'MRE'` etc.). Keep parameterized. |
| **LOGSITE vs Site_Code duality** | Tables have **both** `Site_Code` (company) and `LogSite_Code` (login site). Search uses `LogSite_Code`; header insert writes both (`SITE_CODE=site`, `LOGSITE_CODE=logsite`). `moondata.sql` defines both as `varchar(2) NOT NULL`. | Python reads `SITE_CODE = db.get_site_code()[:2]` (`db.py:229` — actually company `KK`) and uses `SITE_CODE` everywhere; `LOGSITE_CODE` inserts duplicate same value (`SITE_CODE`), search on `Site_Code` only. Multi-site dbs collapse. | **HIGH** | Split `SITE_CODE` (company, key 7) vs `LOG_SITE` (login site, `MemVar_1F92078` — env `HMS_SITE_CODE` already exists). Pass `logsite=logsite` in queries; writes: `Site_Code=company[:2]`, `LogSite_Code=logsite`. Add param in all selects. |
| **`next_vno` — Voucher_Prefix range + Number_Method** | `SELECT VT.Number_Method,VP.Prefix,VP.Start_Srl_No,VP.Date_From,VP.Date_To FROM Voucher_Type+Voucher_Prefix WHERE VP.V_Type=? AND VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND ? BETWEEN Date_From AND Date_To` + `LastVou` + `DateLock` check. `Number_Method` may be `Manual` vs `Auto`; `Start_Srl_No` seeds first number; period windows mean VNo resets per FY/prefix. Used in every TopCtrl Save. | `db.next_vno()` does `MAX(VNo) WHERE Vtype=? AND Vprefix=? AND Site_Code=?` with `UPDLOCK` — ignores `Voucher_Prefix.Date_From/To`, `Start_Srl_No`, `Number_Method`, `LastVou`, `DateLock`. Risk: duplicate or off-by-gap DocIds, wrong prefix window. | **CRITICAL** | Reimplement `next_vno` with VB6 SQL: `SELECT ISNULL(MAX(VNo), VP.Start_Srl_No-1)+1 ...` joining `Voucher_Prefix` window + `DateLock` pre-check; fallback to `LastVou` when `Number_Method='Manual'`. Keep `UPDLOCK,HOLDLOCK` + `Vprefix` still. No schema: `Voucher_Prefix`/`Voucher_Type`/`DateLock` already in `moondata.sql`. |
| **menuHelp / Help permission gating** | `HMS.bas` + `Project.vbp` TopCtrl checks `SELECT Param_Str FROM menuHelp WHERE UserName=? AND CompCode=? AND [Option]=?` and `Help` table per `FName/CtrlIndex`. Denied users blocked before `Add/Edit/Delete`. | Python `db.get_comp_code()` returns `"2"` but never queried; no `menuHelp`/`Help` check in `inventory.py`/`purchase.py`. Any user can post. | **HIGH** (audit) | Add `def check_menuhelp(option, user, compcode)` that runs VB6 query; call at UI `Save/Delete` entry (raise `PermissionError` if no row). No schema change — tables exist. |
| **DateLock enforcement** | `SELECT Name,Srno,IsNull(SDate,''),IsNull(EDate,'') FROM DateLock WHERE Name='Purchase Order Entry'` (or `Purchase Bill Entry`, `Stock`). VB6 blocks save if `VDate` outside `SDate..EDate`. | Python has no `DateLock` check in any `*_create`. Back-dated entries slip. | **MEDIUM** | Add `check_datelock(name, vdate)` before any `INSERT` and raise with VB6 wording. |
| **StockInHand — ConvRatio / NCAT / grouping** | 5-query mode + `ConvRatio` modes (see §1.9). `NCAT` lists explicit; `S.Unit` grouping in Mode 1, pure `S.Item` in Mode 2; amounts via `SUM(S.Amount)` not `qty*rate`. | `inventory.stock_in_hand()`, `stock_balance()`, `stock_register()`, `kitchen_stock_report()` use `SUM(QtyRec-QtyIss)` or `*Rate`, without `NCAT`, without `LOGSITE_CODE` join to `Voucher_type`, without `S.Unit` grouping, without `S.ConvRatio` on Purchase-Unit. Returns wrong Bal for `STOP`/`KS*` types. | **CRITICAL** (report mismatch) | Patch `stock_in_hand` et al to run the exact 5-query / CTE from §1.9 with VB6 NCAT lists, `LOGSITE_CODE` filter, `S.Unit` vs `S.ConvRatio` branch, param `godown`/`group`/`item` as optional `<Filters>`. |
| **Godown CRUD — SysYn + LOGSITE** | `Godown.frm`Browse: `(LOGSITE_CODE='cur' OR 'HO') AND (SysYN<>'Y' OR NULL)`; insert checks duplicate `Name`/`shortName`; code gen `SUBSTRING(Code,3,4)` +1 where `SysYn<>'Y'`. | `godown_list` ignores SysYn/LOGSITE/HO; `_validate` checks only code/name length; no duplicate Name/ShortName check; `godown_insert` no `SUBSTRING` auto-code path, no LOGSITE. | **MEDIUM** | Add `WHERE (LogSite_Code=? OR 'HO') AND (SysYn<>'Y' OR NULL)` and duplicate guards `SELECT COUNT(*) WHERE Name=?` before insert/update (VB6 wording). |
| **Indent lines — INDENT1.ClearYN + TaxStru** | `Indent1` holds `Rate, Amount, Specification, ClearYN, ConvFactor, WtQty, WtUnit, TaxStru, TaxAmt, Total` per line; pending = `(IsNull(ClearYN,'')<>'Y')` via `PORDER1`/`Stock` linked `ClearYN='Y'`. Tax via `TaxStru`. | Python `indent_create` writes **header only** (no INDENT1 rows) — caller `ui/inventory.py:342` later loops `INDENT1API.insert` per line via UI; direct API `indent_create` alone leaves header orphan. Also `ClearYN` default `''` not `'N'`. | **HIGH** | Make `indent_create(lines=...)` accept lines atomically (header+lines same cn/transaction), replicate VB6 `INDENT1` fields incl. `ConvFactor=WtQty/Qty`, `WtUnit`, `TaxStru`. Ensure `ClearYN=''` for pending. |
| **Purchase Bill Tax slab** | `TaxStru` joined `RevMast` per `TS.Code` rows (CGST/SGST/IGST/Service via `TS.NATURE/CONDAPP`), `RoundOffSetting.ModuleName='Purchase Bill'`. Header `CGST/SGST/IGST/ServiceCharge/RoundOff/NetAmt` computed from slabs. | `purchase.purchase_bill_create` computes `CGST=tax/2, SGST=tax/2` flat — interstate IGST vs intra CGST+SGST flipped; ignores `TaxStru.NATURE`; `RoundOff` is `round(total+tax)-...` not `RoundOffSetting`. | **MEDIUM** | Replace flat split with `taxstru.calculate(tax_stru, amount)` already present but use `calc["cgst"/"sgst"/"igst"/"service"]` per line + `RoundOffSetting.RoundOffType` for `RoundOff`. |
| **Opening Stock VType STOP** | `FrmOPStock` `Vtype='STOP'` rows: `Stock` joined `ItemMast (ItemType='Store') + Depart + GodownMast`; save respects `Stock.Vtype='STOP'` not `ADJ`. | Python has no `opening_stock_create`; `stock_adjust` uses `Vtype='ADJ'` — wrong NCAT, wrong VType. | **MEDIUM** | Add `opening_stock_create()` with `Vtype='STOP'`, `NCAT=STOP`, same VB6 joins; keep `ADJ` separate. |
| **KClStk AutoFill + Kitchen dept filter** | `SELECT AutoFillItemInKitchenClosingYN... FROM Enviro WHERE LogSite_Code=?`; if `Y`, auto-fill items `type IN ('Consumables','Store Item','Raw Material') OR (Finish+DirectSale='Y')` and `Depart.RestType IN ('Kitchen','Staff Kitchen')`. | `kitchen_clstk_ui._load_lookups` pulls `Depart` without RestType filter; ignores `AutoFillItemInKitchenClosingYN`; Vprefix is `str(vdate.year)` not VB6 `Voucher_Prefix.Prefix`. | **LOW** | Add enviro flag branch + correct `WHERE RestType IN (...)` + `Voucher_Prefix` lookup for `Prefix`. |
| **Enviro flags never read** | Many: `SmartPurchaseOrder`, `RateEditableInPO/StockIssue`, `NegativeStockAllowYN`, `ExpMfdDateInMR`, `PurChaseGodown`, `BarCodeFeatureInPurchase`, `DateEditableOnRequisitionYN`, `ImportOptionInPurchase`, `RateInclTax`. | Python ignores all; issue/receive allow negative silently; MR ignores Exp/Mfd dates. | **MEDIUM** | Thread `Enviro` reads into validators (e.g., reject `Qty > Bal` when `NegativeStockAllowYN='N'`; block `Rate` edit when flag `N`). No column changes — just SELECT. |
| **DOCID length / padding** | `D(1)+Site(2)+VType(6 ljust)+VPrefix(4 ljust)+VNo(8 rjust) =21` exact (`_make_docid` OK) but some Python paths `[:21]` slice — VB6 pads VType first, not truncate. | OK on normal VTypes (≤5), but slice could hide long VType bug. `kClStk` private DocId uses `site.ljust(2)` not `SITE_CODE[:2]` — drift. | **LOW** | Keep `_make_docid` single canonical, remove `[:21]` slicing, unify `site.ljust(2)` vs `SITE_CODE` casing. |
| **Frontend: TopCtrl1 parity** | VB6 `MainCtrl TopCtrl1` gives `Add/Edit/Delete/Browse/Print/Exit` state machine, `FGrid` with `FGPoint` picker, `LblFormCaption` caption swap, `Esc`/`F5`/`Ctrl+*` shortcuts, `BillImage` browse, `GridSel` import. | Python UIs are custom `QDialog` with partial shortcuts, missing `Browse` state, `DGHelp`/`FGPoint` keyboard search (`Proc_6_137_...`), `DateLock` message, `LblCurStockStr` live stock tooltip, image viewer. | **MEDIUM** (UX) | Documented below §4 — see fixes for next_vno + Help hint that restore TopCtrl parity without touching schema. |

---

## 4) Fixed workflow — EXACT VB6, SAME SQL (no schema change)

### 4.1 Indent (PIndent) — `core/inventory.py:175` + `ui/inventory.py:86`

```
VB6 TopCtrl1.Add:
  DateLock check (Indent or PIND) -> Voucher_Type(NCAT='PIND') pick
  -> Site=Vsite, LogSite=cur, Vprefix=VP.Prefix where VDate BETWEEN Date_From/To
  -> _make_docid(RQ,Vprefix,Vno) ; INSERT Indent (DocId,RQ,VNo,Site,Vprefix,VDate,VTime='08:00',Department,Godown,Remarks,User,'N',LogSite,RefDocId='')
  -> loop lines: INSERT INDENT1 (DocId,Sno,Vtype=RQ,VNo,VDate,Site,Vprefix,Item,Qty,Unit,Rate,Amount,Specification,ClearYN='',ConvFactor,WtQty,WtUnit,LogSite,TaxStru,TaxAmt,Total)
  -> FGrid Browse: Indent JOIN Voucher_Type ON LogSite+NCAT
Python fix: make indent_create(dept,vdate,godown,lines,remarks) atomic (one cn, commit=False per row, final cn.commit), add HO-fallback SELECTs, LogSite param, DateLock guard.
```

**Frontend:** `PIndent.FrmList+DGItem+DGDepart+FGrid+TxtGrid(0)` picker = `Item Code LIKE 'Name%'` live filter via `DGItem` on `KeyUp` (`F9E524`/`116BAE8`) + `Department` via `DGDepart`. Python `IndentForm` needs: Vtype ListView (NCAT='PIND'), Depart combo `WHERE (LOGSITE='cur' OR 'HO')`, Item grid F1-search fallback, `LblCurStockStr` shows `stock_balance(Item)` on `TxtGrid` focus, `Esc` cancels picker.

### 4.2 Purchase Order (pPOrder) — `core/inventory.py:384` + `ui/purchase_order_ui.py:14`

```
VB6: DateLock('Purchase Order Entry') -> VT='PORD' via Voucher_Prefix window
     -> INSERT POrder header (Docid,VNo,VDate,VP.Prefix,Party,...)
     -> INSERT POrder1 per line (IndentDocId/IndentSno linkage when SmartPurchaseOrder='Y')
     -> UPDATE Indent1 SET ClearYN='Y' WHERE DocId=IndentDocId AND Sno=IndentSno
     -> contra: Stock rows NOT written for PO; Stock only via MRE/Purchase Bill later
Python fix: align porder_create to same INSERT cols, enforce SmartPurchaseOrder branch (when 'N', Indent linkage skipped), pass HO-fallback item list, validate RateEditableInPO.
```

**Frontend:** `pPOrder.frm:FGrid` cols `Item(1)/Qty(3)/Rate(8)/Amount(9)` with `FGrid_UnknownEvent_12` tooltip and `Proc_6_63_...` picker; `txt_OrderType(1)` is `V_Type` list. Python `PurchaseOrderWindow` needs: OrderType combo (NCAT='PORD'), `txt_Txt(0)` VType, indent picker `LTrim(Right(DocId,8))` list, rate lock when `RateEditableInPO='N'`.

### 4.3 M.R. / GIN (pMREntry) — `core/inventory.py:277` + `ui/inventory.py:365`

```
VB6: pMREntry save:
  INSERT GIN (DocId,MRCR,VNo,Site,Vprefix,VDate,PartyCode/Name,Godown,Remark,User,'A',LogSite)
  loop Purch2 (ContraDocId=GIN.DocId, Vtype=PBPB per line) — BUT Python hardcodes 'PBPB'; VB6 actually inserts Purch2 with Vtype from voucher (often 'PBPB' vs 'MRCR' mix)
  loop Stock (Vtype='MRE', QtyRec=line.qty, Rate fallback CASE LPurRate/PurchRate, Exp/Mfd dates when Enviro.ExpMfdDateInMR='Y', GodownCode maybe purchase godown default)
  UPDATE Indent1 ClearYN='Y' per matched indent line
Debug: fix Purch2 Vtype to header Vtype param (not hard-coded 'PBPB'), add ExpDate/MfdDate cols when env flag Y, use purchase godown fallback, keep LogSite split.
```

### 4.4 Purchase Bill (pPBill) — `core/purchase.py:198` + `ui/purchase_bill_ui.py:14`

```
VB6 pPBill.Save:
  DateLock('Purchase Bill Entry') + SundryType date gate
  InvoiceNo = MAX(InvoiceNo)+1 WHERE LOGSITE=cur
  Next VNo via Voucher_Prefix window (not MAX alone)
  INSERT Purch1 header (rest as in §1.4)
  INSERT Purch2 lines with TaxStru slab (TS+RM join per NATURE), SaleAcCode from ItemCatMast.AcName->SubGroup.Name
  INSERT Stock lines (Vtype='PBPB', QtyRec, AccQty, GodownCode=purchase godown or line godown, AcCode/SunCode)
  INSERT SunTran rows (SundryType VAT lines) + RoundOffSetting
  Update ItemMast.LPurRate/LPurDate per item? (check — pPBill does update LPR)
Python fix: already calls taxstru.calculate but must NOT split /2; use RoundOffSetting table; loop ItemMast LPurRate update; add SunTran VAT rows (optional but VB6 does).
```

### 4.5 Requisition Slip / Stock Issue (pReqSlip/pGIss) — `core/inventory.py:617` + `ui/requisition_slip_ui.py:29` / `stock_issue_ui.py:13`

```
VB6 pReqSlip+pGIss:
  Browse: Indent1 pending (IsNull(ClearYN,'')<>'Y') JOIN Indent+Godown+ItemMast
  Issue: INSERT Stock (Vtype='RQI', QtyIss=qty, QtyRec=0, Amount=qty*rate, GodownCode, ContraDocId=IndentDocId/ContraSno, LogSite)
         UPDATE Indent1 SET ClearYN='Y' per line
         guard: SELECT SUM(RecdQty) guard + NegativeStockAllowYN='N' block
Python fix: keep stock_issue(lines) as is but add pre-check query §1.5 balance guard + env flag; requisition_slip db_pending_lines already correct (RTRIM ClearYN, GroupBy, CASE LPurRate) — add LOGSITE filter to match VB6: WHERE I.LOGSITE_CODE=? AND I.VType IN (SELECT V_Type FROM Voucher_Type WHERE NCAT='RQS')
```

### 4.6 KClStk — `FrmStockTransfer.frm` vs `kClStk.frm` + `core/purchase.py:538` + `ui/kitchen_clstk_ui.py:24`

```
VB6 kClStk.Save:
  DateLock('Purchase Bill Entry' reused? plus 'Kitchen Stock' gate)
  Next VNo via Voucher_Prefix for Vtype='KCLS' (KClStk table — not Stock)
  INSERT KClStk per line (DocId,Sno,Vtype=KCLS,VNo,Vprefix,Vdate,Item,Qty,Unit,DepartCode,Remarks,User,'A',LogSite)
  AutoFill path: when AutoFillItemInKitchenClosingYN='Y', prefill items from ItemMast type filter §1.6
Python fix: already does VNo via MAX(VNo) on KClStk (correct table) but uses str(vdate.year) for Vprefix — replace with Voucher_Prefix.Prefix SELECT (Branch: SELECT Prefix FROM Voucher_Prefix WHERE V_Type='KCLS' AND SITE_CODE=? AND LOGSITE_CODE=? AND ? BETWEEN Date_From AND Date_To). Add Depart RestType filter as in §1.6.
```

### 4.7 StockTransfer — `FrmStockTransfer.frm` + `core/inventory.py:528` + `ui/inventory.py:819`

```
VB6 StockTransfer is actually Kitchen transfer (KSISS/KSREC) in VB6 stock table: paired ContraDocId/ContraSno rows with Vtype KSISS/KSREC (check FrmStockTransfer SELECTs: VTYPE='KSREC' etc.)
Python stock_transfer uses Vtype='BMTC' — not in VB6 NCAT list — and pairs ContraDocId=docid.
Fix: keep BMTC if Python-specific, OR add KSISS/KSREC pair path (two inserts: KSISS QtyIss + KSREC QtyRec) to match VB6 crystal NCAT includes.
```

### 4.8 Opening Stock — `FrmOPStock.frm` / `DepOpStk.frm` + `core/inventory.py` missing

```
VB6 FrmOPStock.Save:
  INSERT Stock (Vtype='STOP', QtyRec=qty, RecdQty=WtQty, Unit=WtUnit, RecdUnit=Unit, ConvRatio, DepartCode, GodownCode, Rate, Amount, LogSite)
  Guard: SELECT * FROM Stock WHERE VType='STOP' AND LogSite_Code=? AND Item=?  (dup check)
Python fix: add opening_stock_create(dept, godown, vdate, lines, vprefix) with Vtype='STOP' exactly; keep stock_adjust('ADJ') separate.
```

### 4.9 Godown — `Godown.frm` + `core/inventory.py:70` + `ui/inventory.py:53`

```
VB6 Godown.Full: Browse (LOGSITE OR HO) AND SysYN<>'Y', duplicate Name/shortName checks, auto code SUBSTRING.
Python fix: see §3 row Godown CRUD — add WHERE + duplicate guards; ui uses BaseMasterForm via Field limits — enlarge theme to show LogSite/HO hint.
```

---

## 5) Frontend vs Backend notes — checklist

### Backend (core) — must stay DB-identical

- [ ] `db.next_vno(table,vtype,vprefix,site,logsite)` rewrite with `Voucher_Prefix` window + `Start_Srl_No` + `UPDLOCK,HOLDLOCK` + `DateLock` + `LastVou` fallback (HMS.bas TopCtrl pattern). No column add.
- [ ] Add helpers: `get_logsite()`, `check_datelock(name,vdate)`, `check_menuhelp(option)`, `get_enviro_flag(name)`, `get_voucher_prefix(vtype,vdate)`, `check_negative_stock(item,godown,qty)` — all SELECTs only.
- [ ] Every master SELECT add `(LOGSITE_CODE=? OR LOGSITE_CODE='HO')` + `Voucher_Type` join on both Site+LogSite where NCAT matters.
- [ ] `StockInHand` family: split into Mode 1 (Wt.Unit) vs Mode 2 (ConvRatio) branches, NCAT lists as in §1.9, `S.LogSite_Code=?` + `VT.LogSite_Code` join, `S.Unit` vs `S.Item` GROUP BY, `SUM(S.Amount)` not `qty*rate`.
- [ ] `Purch1.InvoiceNo` = `MAX(InvoiceNo)+1 WHERE LOGSITE=?` (not Site). `RoundOffSetting` lookup for `RoundOff`.
- [ ] `Purch2 Vtype` not hard-coded `'PBPB'` — pass header Vtype (`MRCR` vs `PBPB` vs `MRE`). `KClStk Vprefix` from `Voucher_Prefix`, not `str(year)`.
- [ ] Add `opening_stock_create()` for `STOP`; keep `stock_adjust('ADJ')` separate.
- [ ] Indent header+lines atomic transaction; `ClearYN=''` default; `WtQty = Qty*ConvRatio` when Purchase-Unit mode flag.

### Frontend (ui) — VB6 parity without schema

- [ ] `PIndent`: add Vtype picker (NCAT='PIND'), HO-aware Depart/Godown combos, `DGDepart` onclick sets `Txt(6).Tag=Code`, `FGrid.TxtGrid(0)` picker with `DGItem` live filter (`KeyUp` -> `LIKE Name%` + arrow nav), `LblCurStockStr` live `StockInHand` per item on focus, `DTPicker` for `Txt(2)` date validation same as `Txt_Validate`.
- [ ] `pPOrder`: `Txt(1)` is `Order Type` (V_Type list filtered NCAT='PORD'), `SubGroup` supplier picker with `CityName` join and `LOGSITE HO`, `Indent` picker `LTrim(Right(DocId,8))` pending only, `FGrid` cols 1/3/8 editable, `RateEditableInPO` respects, `PackCharge/ForwardCharges/DiscPer` etc. footer fields (currently collapsed into `remark`).
- [ ] `pMREntry`: `GIN` browse uses `GIN VDATE range` + `LogSite`, `Item` picker with `BarCode` + `ItemCatMast taxStru`, `Godown` SysYN filter, `ChalQty/RecdQty/AccQty/RejQty` flow (currently missing), `ExpDate/MfdDate` when flag `Y`.
- [ ] `pPBill`: `BillImage` click/browse (`CommonDialog` filter `*.*`, invalid `DAT/AVI` reject), `TaxStru` combo `(LOGSITE OR HO)`, `Godown` combo `(LOGSITE OR HO)`, `Supplier` `ViewSubGroup` `Left(MainGrCodeS,3) IN (230,240,280,040)`, `InvoiceType` `Opt(0..2)` (Sale/Tax/Other), `Payable` checkbox `Payable smallint`, grid cols include `DiscApp/RoundOff/SaleAc`, `Import` `GridSel` for transfer folder `C:\Analysis\Transfer`.
- [ ] `pReqSlip/pGIss`: pending list grouped by Sno with `CASE LPurRate` rate, issue qty editable col 9, `NegativeStockAllowYN` guard message `Can't Remove Row :Related Entry Exists In Stock`, `ReqCompWise` grouping.
- [ ] `kClStk`: `Vprefix` from `Voucher_Prefix`, `Depart` filter `Kitchen/Staff Kitchen`, `AutoFillItemInKitchenClosingYN='Y'` auto-fills closing lines, `Sno` renum on delete, `FGrid_UnknownEvent_D` guard `SELECT COUNT(*) FROM Stock WHERE ContraDocId=...`.
- [ ] `Godown`: duplicate Name/ShortName guard + Code auto `SUBSTRING(Code,3,4)` when `SysYn<>'Y'`.
- [ ] Global TopCtrl parity: ` Esc` cancels, `F5` refresh, `Ctrl+N/S/E/B` state machine, `HelpDesc` tooltip from `Help FName/CtrlIndex`, `menuHelp.Param_Str` pre-check, `DateLock` message in status label, `LastVoucher`/`LastVou` persistence.

---

## 6) Debug fixes — copy-paste SQL patches (Same VB6 SQL, no schema change)

```python
# db.py — LOGSITE + next_vno VB6-verbatim (drop-in)
def get_logsite() -> str:
    return os.environ.get("HMS_LOGSITE", os.environ.get("HMS_SITE_CODE","")).strip()[:2].upper() or get_site_code()[:2]

def get_vprefix_for(vtype: str, vdate, cn=None, logsite=None):
    logsite = logsite or get_logsite()
    site = get_site_code()
    rows = query(
        "SELECT Prefix, Start_Srl_No, Date_From, Date_To, Number_Method "
        "FROM Voucher_Prefix VP INNER JOIN Voucher_Type VT "
        " ON VT.V_Type=VP.V_Type AND VT.SITE_CODE=VP.SITE_CODE AND VP.LOGSITE_CODE=VP.LOGSITE_CODE "
        "WHERE VP.V_Type=? AND VP.SITE_CODE=? AND VP.LOGSITE_CODE=? AND ? BETWEEN VP.Date_From AND VP.Date_To",
        (vtype, site, logsite, vdate), cn=cn)
    return (rows[0].Prefix.strip(), int(rows[0].Start_Srl_No or 1), rows[0].Number_Method) if rows else (str(vdate.year), 1, 'Auto')

def _vb6_next_vno(table: str, vtype: str, vdate, cn=None, logsite=None, company=None):
    # DateLock first
    name_map = {'Indent':'Indent','POrder':'Purchase Order Entry','GIN':'M.R. Entry','Purch1':'Purchase Bill Entry','Stock':'Stock Issue'}
    nm= name_map.get(table,'')
    if nm:
        check_datelock(nm, vdate, cn=cn, logsite=logsite)
    prefix, start_no, method = get_vprefix_for(vtype, vdate, cn=cn, logsite=logsite)
    site = company or get_site_code()
    logsite = logsite or get_logsite()
    col = 'Vtype' if table=='Stock' else ('VType' if table in ('Purch1','POrder','GIN') else 'Vtype')
    # Use Vprefix=prefix in WHERE (VB6 does)
    rows = query(
        f"SELECT MAX(VNo) FROM [{table}] WITH (UPDLOCK,HOLDLOCK) "
        f"WHERE [{col}]=? AND Vprefix=? AND Site_Code=? AND LogSite_Code=?",
        (vtype, prefix, site, logsite), cn=cn)
    return max(int(rows[0][0] or 0)+1, start_no)

# master SELECT template — add to every lookup
WHERE (LOGSITE_CODE=? OR LOGSITE_CODE='HO')  -- cur logsite param + fallback
# Indent browse template
SELECT DocID as SearchCode,Remarks,I.Site_Code,I.LogSite_Code
FROM Indent I INNER JOIN Voucher_Type V ON I.Vtype=V.V_Type AND I.LogSite_Code=V.LogSite_Code
WHERE V.LOGSITE_CODE=? AND V.NCAT=? ORDER BY DocID

# StockInHand — paste the CTE from StockInHand_Query.sql / StockInHand_PurchaseUnit.sql
# and add WHERE S.LogSite_Code=? + VT.LogSite_Code join + optional filters
# (keep 5-query variant for VB6-equivalence testing)

# Purchase Bill LPurRate update (add after Stock insert)
query("UPDATE ItemMast SET LPurRate=?, LPurDate=? WHERE Code=? AND (LOGSITE_CODE=? OR LOGSITE_CODE='HO')",
      (rate, vdate, item, logsite), cn=cn)
```

Validation matrix for post-fix:

| Check | How | Pass criteria |
|---|---|---|
| HO fallback count | `SELECT COUNT(*) FROM Indent WHERE LOGSITE_CODE='HO'` vs new `indent_list` rows including HO | rowcount matches VB6 browse (+HO) |
| Vprefix window | Insert two docs on `31-Mar` and `01-Apr` straddling `Voucher_Prefix.Date_To` | different `Prefix` + VNo reset to `Start_Srl_No` |
| DateLock block | save with `VDate < SDate` on `Purchase Bill Entry` | exception with VB6 text, DB unchanged |
| menuHelp block | save as non-SA user without `menuHelp [Option]='Purchase Order Entry'` | `PermissionError` before any INSERT |
| StockInHand | Run `stock_in_hand` vs 5-query VB6 on same From/To + site | qty diff < 0.001 and amounts equal |
| Purch Bill tax | `Purch2 TaxStru=...` where `TS.NATURE='IGST'` interstate item | Header `IGST>0, CGST=SGST=0` (not /2) |
| Opening STOP | `opening_stock_create` with 1 line item | single `Stock Vtype='STOP'` row, `NCAT='STOP'` included in StockInHand |
| KClStk Vprefix | `KClStk` on `31-12-2025` | `Vprefix` equals `Voucher_Prefix.Prefix` for KCLS, not `2025` |
| Godown dup | insert duplicate Name | `Count(*)` guard raises before INSERT |

No `ALTER TABLE` required — all patches are SELECT/INSERT-SELECT string changes.

---

## 7) MDI Inventory menus — `HMS.bas:MatRep_Click`

`MatRep` 0..18 map to `rInventRepView.GRepFormName` values noted in §1.10. Python `pyproject.toml` / `HMS_py/ui` menu wiring should route these 16 report names to the patched `Stock*` report functions (reuse `StockInHand_Query.sql` CTE + VB6 `<Filters>` dynamic append). `MatVatR` 0/10/11/12/15/16 route to `VATRegister*` / `Form24AnnexureA` / `FormIII` / `UPVATXXIV` — same `Voucher_Type NCAT` gate but separate sundry joins.

---

## 8) References (file:line for quick nav)

- `PIndent.frm:1`, `pPOrder.frm:1`, `pMREntry.frm:1`, `pPBill.frm:1`, `pReqSlip.frm:1`, `pGIss.frm:1`, `kClStk.frm:1`, `FrmStockTransfer.frm:1`, `DepOpStk.frm:1`, `FrmOPStock.frm:1`, `Godown.frm:1`, `HMS.bas:150` (MatRep_Click), `HMS.bas:349` (MatVatR_Click), `moondata.sql` (Stock/Indent/POrder/Purch/GodownMast/ItemMast/KClStk), `Stock In Hand.txt:1`, `StockInHand_Query.sql:1`, `StockInHand_PurchaseUnit.sql:1`
- `PYTHONE/core/inventory.py:70` (Godown), `PYTHONE/core/inventory.py:152` (Indent), `PYTHONE/core/inventory.py:277` (GIN/MRE), `PYTHONE/core/inventory.py:384` (POrder), `PYTHONE/core/inventory.py:570` (Stock ops), `PYTHONE/core/purchase.py:198` (Purch Bill), `PYTHONE/core/purchase.py:536` (KClStk/INDENT1/PORDER1), `PYTHONE/HMS_py/core/db.py:297` (next_vno), `PYTHONE/ui/inventory.py:86` (IndentForm), `PYTHONE/ui/purchase_order_ui.py:14`, `PYTHONE/ui/purchase_bill_ui.py:14`, `PYTHONE/ui/stock_issue_ui.py:13`, `PYTHONE/ui/stock_receive_ui.py:1`, `PYTHONE/ui/kitchen_clstk_ui.py:24`, `PYTHONE/ui/requisition_slip_ui.py:29`, `PYTHONE/ui/stock_adjust_ui.py:13`

---

## 9) Result

Report written to: `C:\Users\PC\Desktop\New folder (3)\MODULE_FIX_PLANS\FODER\PYTHONE\COMPARE_WORKSPACE\INVENTORY_COMPARE.md`

Return `Summary` above + path. No DB modified.

