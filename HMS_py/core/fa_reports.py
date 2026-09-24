"""Financial Aggregate Reports (VB6: FaMagic port).

7 report types that Python was missing:
1. Balance Sheet
2. Profit & Loss Account
3. Trial Balance (Group-wise)
4. Trial Balance (Ledger-wise)
5. Cash Flow
6. Fund Flow
7. Cash & Bank Summary
"""
from __future__ import annotations

import datetime

from HMS_py.core import db

SITE_CODE = db.get_site_code()  # BUG-014: Analysis.ini-driven (was hardcoded "KK")


def _get_group_nature_map(cn=None) -> dict:
    """Load ACGROUP -> GroupNature mapping for classification."""
    rows = db.query(
        "SELECT GroupCode, GroupName, GroupNature FROM ACGROUP ORDER BY GroupCode",
        cn=cn,
    )
    return {r.GroupCode: {"name": r.GroupName or "", "nature": r.GroupNature or ""}
            for r in rows}


def _ledger_summary(date_to=None, cn=None) -> list[dict]:
    """SUM(AmtDr), SUM(AmtCr) per SubCode with group info and LOGSITE scoping.

    VB6 FaMagic: open-type reports aggregate LEDGER by SubCode,
    then join ACGROUP for GroupNature classification.
    
    Net calculation respects GroupNature sign convention:
    - Assets (A), Expenses (E): net = Dr - Cr
    - Liabilities (L), Revenue (R): net = Cr - Dr
    """
    sc = SITE_CODE
    if date_to:
        rows = db.query(
            "SELECT L.SubCode, S.Name, S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? AND L.V_Date <= ? "
            "GROUP BY L.SubCode, S.Name, S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode, L.SubCode",
            (sc, date_to), cn=cn,
        )
    else:
        rows = db.query(
            "SELECT L.SubCode, S.Name, S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? "
            "GROUP BY L.SubCode, S.Name, S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode, L.SubCode",
            (sc,), cn=cn,
        )
    result = []
    for r in rows:
        dr = float(r.DrTotal or 0)
        cr = float(r.CrTotal or 0)
        gn = r.GroupNature or ""
        # Sign convention per GroupNature (BUG-H03 fix)
        if gn in ("L", "R"):  # Liabilities, Revenue
            net = cr - dr
        else:  # Assets (A), Expenses (E), or unknown
            net = dr - cr
        result.append({
            "subcode": r.SubCode or "",
            "name": (r.Name or "").strip(),
            "groupcode": r.GroupCode or "",
            "groupnature": gn,
            "dr_total": dr,
            "cr_total": cr,
            "net": net,
        })
    return result


def _group_summary(date_to=None, cn=None) -> list[dict]:
    """SUM(AmtDr-AmtCr) per GroupCode with group info and LOGSITE scoping.
    
    Net calculation respects GroupNature sign convention:
    - Assets (A), Expenses (E): net = Dr - Cr
    - Liabilities (L), Revenue (R): net = Cr - Dr
    """
    sc = SITE_CODE
    if date_to:
        rows = db.query(
            "SELECT S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? AND L.V_Date <= ? "
            "GROUP BY S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode",
            (sc, date_to), cn=cn,
        )
    else:
        rows = db.query(
            "SELECT S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? "
            "GROUP BY S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode",
            (sc,), cn=cn,
        )
    result = []
    for r in rows:
        dr = float(r.DrTotal or 0)
        cr = float(r.CrTotal or 0)
        gn = r.GroupNature or ""
        # Sign convention per GroupNature (BUG-H03 fix)
        if gn in ("L", "R"):  # Liabilities, Revenue
            net = cr - dr
        else:  # Assets (A), Expenses (E), or unknown
            net = dr - cr
        result.append({
            "groupcode": r.GroupCode or "",
            "groupnature": gn,
            "dr_total": dr,
            "cr_total": cr,
            "net": net,
        })
    return result


def _group_detail(date_to=None, cn=None) -> list[dict]:
    """Per-subcode detail with group info for drill-down reports."""
    return _ledger_summary(date_to=date_to, cn=cn)


def _ledgers_by_group_nature(nature: str, date_to=None, cn=None) -> list[dict]:
    """Get all ledger accounts under a specific GroupNature, with balances."""
    ledgers = _ledger_summary(date_to=date_to, cn=cn)
    groups = _get_group_nature_map(cn=cn)

    result = []
    for entry in ledgers:
        gn = entry["groupnature"]
        if not gn:
            grp = groups.get(entry["groupcode"])
            if grp:
                gn = grp["nature"]
        if gn == nature:
            result.append(entry)
    return result


def _ledgers_by_nature_grouped(nature: str, date_to=None, cn=None) -> list[dict]:
    """Ledgers grouped by their ACGROUP for balance sheet / P&L layout."""
    ledgers = _ledger_summary(date_to=date_to, cn=cn)
    groups = _get_group_nature_map(cn=cn)

    by_group: dict[str, list[dict]] = {}
    for entry in ledgers:
        gn = entry["groupnature"]
        if not gn:
            grp = groups.get(entry["groupcode"])
            if grp:
                gn = grp["nature"]
        if gn == nature:
            gc = entry["groupcode"]
            if gc not in by_group:
                by_group[gc] = []
            by_group[gc].append(entry)

    result = []
    for gc, items in by_group.items():
        grp_name = groups.get(gc, {}).get("name", gc)
        total = sum(i["net"] for i in items)
        children = [
            {"group": gc, "name": i["name"], "amount": i["net"]}
            for i in items if abs(i["net"]) > 0.005
        ]
        result.append({
            "group": gc,
            "group_name": grp_name,
            "amount": total,
            "children": children,
        })
    return result


# ============================================================
# 1. Balance Sheet
# ============================================================
def balance_sheet(cn=None, date_to=None) -> dict:
    """VB6 FaMagic OpenType='BALSHEET'.

    Query ACGROUP where GroupNature='A' (Assets) and 'L' (Liabilities).
    For each group, SUM(AmtDr-AmtCr) from LEDGER as opening balance.

    Returns: {assets: [{group, name, amount}], liabilities: [{group, name, amount}],
              total_assets, total_liabilities, balanced: bool}
    """
    assets = _ledgers_by_nature_grouped("A", date_to=date_to, cn=cn)
    liabilities = _ledgers_by_nature_grouped("L", date_to=date_to, cn=cn)

    total_assets = sum(a["amount"] for a in assets)
    total_liabilities = sum(l["amount"] for l in liabilities)

    return {
        "assets": assets,
        "liabilities": liabilities,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "balanced": abs(total_assets - total_liabilities) < 0.01,
    }


# ============================================================
# 2. Profit & Loss Account
# ============================================================
def profit_and_loss(cn=None, date_from=None, date_to=None) -> dict:
    """VB6 FaMagic OpenType='PROFLOSS'.

    Query ACGROUP where GroupNature='E' (Expenditure) and 'R' (Revenue).
    When date_from is provided, filter LEDGER entries within the date range.

    Returns: {expenditure: [{group, name, amount}], revenue: [{group, name, amount}],
              total_expenditure, total_revenue, net_profit_or_loss}
    """
    if date_from:
        ledgers = _ledger_by_date_range(date_from, date_to, cn=cn)
    else:
        ledgers = _ledger_summary(date_to=date_to, cn=cn)

    groups = _get_group_nature_map(cn=cn)

    def _classify(entries):
        by_group: dict[str, list[dict]] = {}
        for entry in entries:
            gn = entry["groupnature"]
            if not gn:
                grp = groups.get(entry["groupcode"])
                if grp:
                    gn = grp["nature"]
            if gn:
                if gn not in by_group:
                    by_group[gn] = []
                by_group[gn].append(entry)
        return by_group

    classified = _classify(ledgers)

    expenditure = []
    for entry in classified.get("E", []):
        expenditure.append({
            "group": entry["groupcode"],
            "name": entry["name"],
            "amount": entry["net"],
        })

    revenue = []
    for entry in classified.get("R", []):
        revenue.append({
            "group": entry["groupcode"],
            "name": entry["name"],
            "amount": entry["net"],
        })

    total_expenditure = sum(e["amount"] for e in expenditure)
    total_revenue = sum(r["amount"] for r in revenue)
    net_profit_or_loss = total_revenue - total_expenditure

    return {
        "expenditure": expenditure,
        "revenue": revenue,
        "total_expenditure": total_expenditure,
        "total_revenue": total_revenue,
        "net_profit_or_loss": net_profit_or_loss,
    }


def _ledger_by_date_range(date_from, date_to=None, cn=None) -> list[dict]:
    """Get ledger summary within a date range with LOGSITE scoping."""
    sc = SITE_CODE
    if date_to:
        rows = db.query(
            "SELECT L.SubCode, S.Name, S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? AND L.V_Date BETWEEN ? AND ? "
            "GROUP BY L.SubCode, S.Name, S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode, L.SubCode",
            (sc, date_from, date_to), cn=cn,
        )
    else:
        rows = db.query(
            "SELECT L.SubCode, S.Name, S.GroupCode, S.GroupNature, "
            "SUM(L.AmtDr) AS DrTotal, SUM(L.AmtCr) AS CrTotal "
            "FROM LEDGER L "
            "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
            "WHERE L.LogSite_Code = ? AND L.V_Date >= ? "
            "GROUP BY L.SubCode, S.Name, S.GroupCode, S.GroupNature "
            "ORDER BY S.GroupCode, L.SubCode",
            (sc, date_from), cn=cn,
        )
    result = []
    for r in rows:
        dr = float(r.DrTotal or 0)
        cr = float(r.CrTotal or 0)
        gn = r.GroupNature or ""
        # Sign convention per GroupNature (match _ledger_summary)
        if gn in ("L", "R"):  # Liabilities, Revenue
            net = cr - dr
        else:  # Assets (A), Expenses (E), or unknown
            net = dr - cr
        result.append({
            "subcode": r.SubCode or "",
            "name": (r.Name or "").strip(),
            "groupcode": r.GroupCode or "",
            "groupnature": gn,
            "dr_total": dr,
            "cr_total": cr,
            "net": net,
        })
    return result


# ============================================================
# 3. Trial Balance (Group-wise)
# ============================================================
def trial_balance_group(cn=None, date_to=None) -> list[dict]:
    """VB6 FaMagic OpenType='GROUPTRIAL'.

    Group LEDGER by GroupCode, show DR/CR totals per group.

    Returns: [{groupcode, groupname, groupnature, dr_total, cr_total, net}]
    """
    groups = _get_group_nature_map(cn=cn)
    summary = _group_summary(date_to=date_to, cn=cn)

    result = []
    for g in summary:
        gc = g["groupcode"]
        grp = groups.get(gc, {})
        result.append({
            "groupcode": gc,
            "groupname": grp.get("name", ""),
            "groupnature": g["groupnature"],
            "dr_total": g["dr_total"],
            "cr_total": g["cr_total"],
            "net": g["net"],
        })
    return result


# ============================================================
# 4. Trial Balance (Ledger-wise)
# ============================================================
def trial_balance_ledger(cn=None, date_to=None) -> list[dict]:
    """VB6 FaMagic OpenType='LEDTRIAL'.

    Group LEDGER by SubCode, show DR/CR/Net per ledger account.

    Returns: [{subcode, name, groupcode, dr_total, cr_total, net}]
    """
    summary = _ledger_summary(date_to=date_to, cn=cn)

    result = []
    for entry in summary:
        result.append({
            "subcode": entry["subcode"],
            "name": entry["name"],
            "groupcode": entry["groupcode"],
            "dr_total": entry["dr_total"],
            "cr_total": entry["cr_total"],
            "net": entry["net"],
        })
    return result


# ============================================================
# 5. Cash Flow
# ============================================================
def cash_flow(cn=None, date_from=None, date_to=None) -> dict:
    """VB6 FaMagic OpenType='CASHFLOW'.

    Classify LEDGER entries as cash vs non-cash based on GroupNature.
    Operating: current assets/liabilities (GroupNature A/L with cash-like groups)
    Investing: fixed assets
    Financing: long-term liabilities / equity

    Returns: {operating_inflow, operating_outflow, investing_inflow,
              investing_outflow, financing_inflow, financing_outflow,
              net_operating, net_investing, net_financing, net_change}
    """
    if date_from:
        ledgers = _ledger_by_date_range(date_from, date_to, cn=cn)
    else:
        ledgers = _ledger_summary(date_to=date_to, cn=cn)

    groups = _get_group_nature_map(cn=cn)

    # Cash/bank group codes (common VB6 pattern - groups with "Cash" or "Bank" in name)
    cash_keywords = ("cash", "bank", "cash in hand", "bank account")

    def _is_cash_group(groupcode: str) -> bool:
        grp = groups.get(groupcode)
        if not grp:
            return False
        name_lower = (grp.get("name", "") or "").lower()
        return any(kw in name_lower for kw in cash_keywords)

    # Classification based on VB6 FaMagic patterns:
    # Cash groups: operating cash flow
    # Non-cash asset groups (e.g., debtors, inventory): operating
    # Fixed asset groups: investing
    # Capital/reserve groups: financing
    # Loan groups: financing

    operating_inflow = 0.0
    operating_outflow = 0.0
    investing_inflow = 0.0
    investing_outflow = 0.0
    financing_inflow = 0.0
    financing_outflow = 0.0

    for entry in ledgers:
        gn = entry["groupnature"]
        if not gn:
            grp = groups.get(entry["groupcode"])
            if grp:
                gn = grp["nature"]

        net = entry["net"]
        is_cash = _is_cash_group(entry["groupcode"])

        if gn == "A":
            if is_cash:
                # Cash movements are part of operating
                if net > 0:
                    operating_inflow += net
                else:
                    operating_outflow += abs(net)
            else:
                # Other assets - investing
                if net > 0:
                    investing_inflow += net
                else:
                    investing_outflow += abs(net)
        elif gn == "L":
            if is_cash:
                if net > 0:
                    operating_inflow += net
                else:
                    operating_outflow += abs(net)
            else:
                # Liabilities - financing
                if net > 0:
                    financing_inflow += net
                else:
                    financing_outflow += abs(net)
        elif gn == "R":
            # Revenue - operating
            if net > 0:
                operating_inflow += net
            else:
                operating_outflow += abs(net)
        elif gn == "E":
            # Expenditure - operating
            if net > 0:
                operating_inflow += net
            else:
                operating_outflow += abs(net)

    return {
        "operating_inflow": operating_inflow,
        "operating_outflow": operating_outflow,
        "investing_inflow": investing_inflow,
        "investing_outflow": investing_outflow,
        "financing_inflow": financing_inflow,
        "financing_outflow": financing_outflow,
        "net_operating": operating_inflow - operating_outflow,
        "net_investing": investing_inflow - investing_outflow,
        "net_financing": financing_inflow - financing_outflow,
        "net_change": (operating_inflow - operating_outflow +
                       investing_inflow - investing_outflow +
                       financing_inflow - financing_outflow),
    }


# ============================================================
# 6. Fund Flow
# ============================================================
def fund_flow(cn=None, date_to=None) -> dict:
    """VB6 FaMagic OpenType='FUNDFLOW'.

    Changes in working capital from SUBGROUPCURRBAL.
    Sources: increase in liabilities, decrease in assets
    Applications: decrease in liabilities, increase in assets

    Returns: {sources: [...], applications: [...], net_change}
    """
    rows = db.query(
        "SELECT SC.SubCode, SG.Name, SG.GroupCode, SG.GroupNature, "
        "SC.Curr_Bal "
        "FROM SUBGROUPCURRBAL SC "
        "LEFT JOIN SubGroup SG ON SG.SubCode = SC.SubCode "
        "WHERE SC.LogSite_Code = ? "
        "ORDER BY SG.GroupCode, SC.SubCode",
        (SITE_CODE,), cn=cn,
    )

    sources = []
    applications = []

    for r in rows:
        bal = float(r.Curr_Bal or 0)
        gn = r.GroupNature or ""
        if abs(bal) < 0.005:
            continue

        entry = {
            "subcode": r.SubCode or "",
            "name": (r.Name or "").strip(),
            "groupcode": r.GroupCode or "",
            "groupnature": gn,
            "amount": bal,
        }

        if gn == "L":
            # Liability increase = source of funds
            if bal > 0:
                sources.append(entry)
            else:
                applications.append(entry)
        elif gn == "A":
            # Asset increase = application of funds
            if bal > 0:
                applications.append(entry)
            else:
                sources.append(entry)

    net_change = sum(s["amount"] for s in sources) - sum(a["amount"] for a in applications)

    return {
        "sources": sources,
        "applications": applications,
        "net_change": net_change,
    }


# ============================================================
# 7. Cash & Bank Summary
# ============================================================
def cash_bank_summary(cn=None, date_to=None) -> list[dict]:
    """VB6 FaMagic OpenType='CASHBANKSUM'.

    Summarize cash and bank accounts from LEDGER.
    Shows opening (from SUBGROUPCURRBAL), receipts (DR total), payments (CR total),
    and closing balance.

    Returns: [{subcode, name, opening, receipts, payments, closing}]
    """
    groups = _get_group_nature_map(cn=cn)
    cash_keywords = ("cash", "bank", "cash in hand", "bank account")

    def _is_cash_bank(groupcode: str) -> bool:
        grp = groups.get(groupcode)
        if not grp:
            return False
        name_lower = (grp.get("name", "") or "").lower()
        return any(kw in name_lower for kw in cash_keywords)

    # Get current balances
    cbal_rows = db.query(
        "SELECT SC.SubCode, SG.Name, SG.GroupCode, SC.Curr_Bal "
        "FROM SUBGROUPCURRBAL SC "
        "LEFT JOIN SubGroup SG ON SG.SubCode = SC.SubCode "
        "WHERE SC.LogSite_Code = ? "
        "ORDER BY SC.SubCode",
        (SITE_CODE,), cn=cn,
    )

    # Get DR/CR totals from LEDGER with LOGSITE scoping
    if date_to:
        ledger_rows = db.query(
            "SELECT SubCode, SUM(AmtDr) AS DrTotal, SUM(AmtCr) AS CrTotal "
            "FROM LEDGER WHERE LogSite_Code = ? AND V_Date <= ? "
            "GROUP BY SubCode ORDER BY SubCode",
            (SITE_CODE, date_to), cn=cn,
        )
    else:
        ledger_rows = db.query(
            "SELECT SubCode, SUM(AmtDr) AS DrTotal, SUM(AmtCr) AS CrTotal "
            "FROM LEDGER WHERE LogSite_Code = ? GROUP BY SubCode ORDER BY SubCode",
            (SITE_CODE,), cn=cn,
        )

    ledger_map = {}
    for r in ledger_rows:
        ledger_map[r.SubCode] = {
            "dr_total": float(r.DrTotal or 0),
            "cr_total": float(r.CrTotal or 0),
        }

    result = []
    for r in cbal_rows:
        gc = r.GroupCode or ""
        if not _is_cash_bank(gc):
            continue

        sc = r.SubCode or ""
        name = (r.Name or "").strip()
        closing_bal = float(r.Curr_Bal or 0)

        lg = ledger_map.get(sc, {"dr_total": 0, "cr_total": 0})
        receipts = lg["dr_total"]
        payments = lg["cr_total"]

        # Opening = closing - receipts + payments (reverse calculation)
        opening = closing_bal - receipts + payments

        result.append({
            "subcode": sc,
            "name": name,
            "opening": opening,
            "receipts": receipts,
            "payments": payments,
            "closing": closing_bal,
        })

    return result


# ============================================================
# 8. Aging Analysis (VB6: FaAgingReport)
# ============================================================
def aging_analysis(cn=None, date_to=None, aging_days=None) -> dict:
    """VB6 aging: categorize outstanding amounts by age buckets.
    Buckets: 0-30, 31-60, 61-90, 91-120, 120+ days."""
    import datetime as _dt
    if aging_days is None:
        aging_days = [30, 60, 90, 120]
    today = date_to or _dt.date.today()

    rows = db.query(
        "SELECT L.SubCode, S.Name, S.GroupCode, SG.GroupNature, "
        "L.V_Date, L.AmtDr, L.AmtCr "
        "FROM LEDGER L "
        "LEFT JOIN SubGroup S ON S.SubCode = L.SubCode "
        "LEFT JOIN AcGroup SG ON SG.GroupCode = S.GroupCode "
        "WHERE L.LogSite_Code = ? AND L.V_Date <= ? ORDER BY L.SubCode, L.V_Date",
        (SITE_CODE, today), cn=cn)

    accounts = {}
    for r in rows:
        sc = (r.SubCode or "").strip()
        if not sc:
            continue
        if sc not in accounts:
            accounts[sc] = {
                "name": (r.Name or "").strip(),
                "groupcode": r.GroupCode or "",
                "nature": r.GroupNature or "", "entries": []}
        accounts[sc]["entries"].append({
            "vdate": r.V_date, "dr": float(r.AmtDr or 0),
            "cr": float(r.AmtCr or 0)})

    def _calc_aging(entries):
        net = sum(e["dr"] - e["cr"] for e in entries)
        if abs(net) < 0.005:
            return None
        buckets = [0.0] * (len(aging_days) + 1)
        remaining = abs(net)
        direction = "dr" if net > 0 else "cr"
        for e in sorted(entries, key=lambda x: x["vdate"]):
            amt = e["dr"] if direction == "dr" else e["cr"]
            if amt <= 0:
                continue
            age = (today - e["vdate"]).days if hasattr(e["vdate"], "days") else 0
            idx = len(aging_days)
            for i, lim in enumerate(aging_days):
                if age <= lim:
                    idx = i
                    break
            alloc = min(amt, remaining)
            buckets[idx] += alloc
            remaining -= alloc
            if remaining <= 0:
                break
        return {"buckets": buckets, "total": net}

    debtors = {}
    creditors = {}
    for sc, info in accounts.items():
        res = _calc_aging(info["entries"])
        if res is None:
            continue
        entry = {"subcode": sc, "name": info["name"],
                 "buckets": res["buckets"], "total": res["total"]}
        if info["nature"] == "A":
            debtors[sc] = entry
        elif info["nature"] == "L":
            creditors[sc] = entry

    labels = [f"0-{aging_days[0]}"]
    for i in range(1, len(aging_days)):
        labels.append(f"{aging_days[i-1]+1}-{aging_days[i]}")
    labels.append(f"{aging_days[-1]+1}+")

    return {"bucket_labels": labels, "debtors": debtors, "creditors": creditors,
            "total_debtors": sum(d["total"] for d in debtors.values()),
            "total_creditors": sum(c["total"] for c in creditors.values())}


# ============================================================
# 9. Ledger with Opening Balance (VB6: FaLedgerOpening)
# ============================================================
def ledger_with_opening(subcode: str, date_from=None, date_to=None,
                        cn=None) -> dict:
    """VB6 ledger with opening balance: carry-forward from previous FY."""
    import datetime as _dt
    if date_from is None:
        date_from = _dt.date(_dt.date.today().year, 4, 1)
    if date_to is None:
        date_to = _dt.date.today()

    opening_rows = db.query(
        "SELECT ISNULL(SUM(AmtDr), 0), ISNULL(SUM(AmtCr), 0) "
        "FROM LEDGER WHERE LogSite_Code = ? AND SubCode = ? AND V_Date < ?",
        (SITE_CODE, subcode, date_from), cn=cn)
    opening_bal = float(opening_rows[0][0] or 0) - float(opening_rows[0][1] or 0)

    txns = db.query(
        "SELECT DocId, V_Date, V_Type, V_No, AmtDr, AmtCr, Narration, "
        "ContraSub FROM LEDGER WHERE LogSite_Code = ? AND SubCode = ? AND V_Date BETWEEN ? AND ? "
        "ORDER BY V_Date, DocId",
        (SITE_CODE, subcode, date_from, date_to), cn=cn)

    transactions = []
    running = opening_bal
    for r in txns:
        dr = float(r.AmtDr or 0)
        cr = float(r.AmtCr or 0)
        running += dr - cr
        transactions.append({
            "docid": r.DocId or "", "vdate": r.V_date,
            "vtype": r.V_Type or "", "vno": r.V_No,
            "amt_dr": dr, "amt_cr": cr,
            "narration": (r.Narration or "").strip(),
            "contra_sub": (r.ContraSub or "").strip(),
            "running_bal": running})

    name_rows = db.query(
        "SELECT Name FROM SubGroup WHERE SubCode = ? AND (LogSite_Code = ? OR LogSite_Code='HO' OR ISNULL(LogSite_Code,'')='')", (subcode, SITE_CODE), cn=cn)
    name = (name_rows[0][0] or "").strip() if name_rows else ""

    return {"subcode": subcode, "name": name, "date_from": date_from,
            "date_to": date_to, "opening_bal": opening_bal,
            "transactions": transactions, "closing_bal": running,
            "total_dr": sum(t["amt_dr"] for t in transactions),
            "total_cr": sum(t["amt_cr"] for t in transactions)}


# ============================================================
# 10. Bank Reconciliation Statement (VB6: FaBRS)
# ============================================================
def bank_reconciliation(subcode: str, date_to=None, cn=None) -> dict:
    """VB6 bank reconciliation: cleared vs pending cheques."""
    if date_to is None:
        date_to = datetime.date.today()

    all_cheques = db.query(
        "SELECT DocId, V_SNo, V_Date, Chq_No, Chq_Date, Clg_Date, "
        "AmtDr, AmtCr FROM Ledger "
        "WHERE LogSite_Code = ? AND SubCode = ? AND Chq_No <> '' AND V_Date <= ? ORDER BY V_Date",
        (SITE_CODE, subcode, date_to), cn=cn)

    cleared = []
    pending = []
    for r in all_cheques:
        entry = {"docid": r.DocId, "sno": r.V_SNo, "vdate": r.V_date,
                 "chq_no": r.Chq_No or "", "chq_date": r.Chq_Date,
                 "clg_date": r.Clg_Date,
                 "amt_dr": float(r.AmtDr or 0), "amt_cr": float(r.AmtCr or 0)}
        if r.Clg_Date:
            cleared.append(entry)
        else:
            pending.append(entry)

    bal_rows = db.query(
        "SELECT ISNULL(SUM(AmtDr), 0), ISNULL(SUM(AmtCr), 0) "
        "FROM LEDGER WHERE LogSite_Code = ? AND SubCode = ? AND V_Date <= ?",
        (SITE_CODE, subcode, date_to), cn=cn)
    bank_book_bal = float(bal_rows[0][0] or 0) - float(bal_rows[0][1] or 0)

    return {"subcode": subcode, "date_to": date_to,
            "bank_book_bal": bank_book_bal,
            "cleared": cleared, "pending": pending,
            "cleared_count": len(cleared), "pending_count": len(pending),
            "cleared_dr": sum(c["amt_dr"] for c in cleared),
            "cleared_cr": sum(c["amt_cr"] for c in cleared),
            "pending_dr": sum(p["amt_dr"] for p in pending),
            "pending_cr": sum(p["amt_cr"] for p in pending)}


# ============================================================
# 11. Voucher Type Routing (VB6: FaVrEnt Auto-routing)
# ============================================================
def route_voucher(subcode: str, cn=None) -> str:
    """FA-6: NCat-based routing via Voucher_Type (VB6 FaVoucher Proc_7) with HO fallback."""
    rows = db.query(
        "SELECT SG.GroupName FROM SubGroup S "
        "JOIN AcGroup SG ON SG.GroupCode = S.GroupCode "
        "WHERE RTRIM(S.SubCode) = ? AND (S.LogSite_Code = ? OR S.LogSite_Code='HO' OR ISNULL(S.LogSite_Code,'')='')", (subcode, SITE_CODE), cn=cn)
    name = (rows[0][0] if rows else "" or "").upper()
    # NCat preference from live Voucher_Type (CNT/JV/PMT/RCT, VB6 branch)
    want: list[str] = []
    if "CASH" in name:
        want = ["RCT", "PMT"]
    elif "BANK" in name:
        want = ["RCT", "PMT"]
    elif "CASH" in (subcode or "").upper():
        want = ["RCT", "PMT"]
    else:
        want = ["JV"]
    for ncat in want:
        r = db.query(
            "SELECT TOP 1 V_Type FROM Voucher_Type WHERE NCat = ? "
            "ORDER BY V_Type", (ncat,), cn=cn)
        if r and (r[0][0] or "").strip():
            return (r[0][0] or "").strip()
    return "JV"
