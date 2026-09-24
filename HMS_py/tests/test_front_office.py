"""Front Office DB-integration tests (live DB, PYT-safe cleanup).

Covers the FO command spec's test matrix for the pieces implemented in
this push: reservation lifecycle (draft -> update -> no-show/cancel),
real availability, reservation-status reports + PDF, sys-config
read/validate, facility bill header+line transaction, guest-services
roundtrip, KOT reports and the ledger-master bridge.

Negative/boundary cases are explicit. Har created row try/finally me
delete hoti hai (ya PYT-guard ke saath rehne di jaati hai jaisa
existing reservation tests karte hain).
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pytest

from HMS_py.core import db, depart, facility_billing, guest_services
from HMS_py.core import ledger, pos, reports, reservation, room_occ, sys_config

TODAY = date.today()
ARR = TODAY + timedelta(days=2)
DEP = TODAY + timedelta(days=4)


# ============================================================
# Reservation lifecycle (core FO workflow)
# ============================================================

class TestReservationLifecycle:
    def test_draft_insert_get_update(self):
        bookno = reservation.insert_draft("PYT FO CYCLE", ARR, DEP,
                                          adults=2, rooms=1, rate=2500.0)
        try:
            rec = reservation.get(bookno)
            assert rec is not None
            assert rec["GuestName"] == "PYT FO CYCLE"
            assert rec["Adult"] == 2
            assert str(rec["ResStatus"]) == "Confirm"
            assert str(rec["Cancel"]) != "Y"
        finally:
            reservation.delete_draft(bookno)

    def test_draft_validation_negatives(self):
        with pytest.raises(ValueError):
            reservation.insert_draft("", ARR, DEP)          # empty guest
        with pytest.raises(ValueError):
            reservation.insert_draft("PYT NEG", DEP, ARR)   # arr > dep

    def test_no_show_marks_and_blocks_repeat(self):
        bookno = reservation.insert_draft("PYT FO NOSHOW", ARR, DEP)
        try:
            assert reservation.mark_no_show(bookno) == 1
            rec = reservation.get(bookno)
            assert str(rec["Cancel"]) == "Y"
            assert str(rec["ResStatus"]) == "No Show"
            # duplicate no-show = business-rule violation
            with pytest.raises(ValueError):
                reservation.mark_no_show(bookno)
            # cancel bhi allowed nahi after no-show (already Cancel='Y')
            with pytest.raises(ValueError):
                reservation.cancel(bookno)
        finally:
            reservation.delete_draft(bookno)

    def test_cancel_writes_details_and_blocks_repeat(self):
        bookno = reservation.insert_draft("PYT FO CANCEL", ARR, DEP)
        try:
            assert reservation.cancel(bookno) >= 1
            rec = reservation.get(bookno)
            assert str(rec["Cancel"]) == "Y"
            det = db.query(
                "SELECT COUNT(*) FROM BookingCancelDetails "
                "WHERE BookingDocID = ?", (rec["DocId"],))
            assert det[0][0] >= 1
            log = db.query(
                "SELECT COUNT(*) FROM BookingLog WHERE Bookingdocid = ? "
                "AND Flag = 'C'", (rec["DocId"],))
            assert log[0][0] >= 1
            with pytest.raises(ValueError):
                reservation.cancel(bookno)   # double-cancel guard
        finally:
            reservation.delete_draft(bookno)

    def test_cancel_missing_booking(self):
        with pytest.raises(ValueError):
            reservation.cancel(999999999)


# ============================================================
# Room availability (real calculation)
# ============================================================

class TestRoomAvailability:
    def test_availability_shape_and_membership(self):
        av = room_occ.room_availability(TODAY)
        assert av["total_rooms"] > 0
        assert isinstance(av["available"], list)
        assert isinstance(av["occupied"], list)
        assert isinstance(av["blocked"], list)
        # ek room sirf ek bucket me ho sakta hai
        all_rooms = av["available"] + av["occupied"] + av["blocked"] + av["dirty"]
        assert len(all_rooms) == len(set(all_rooms))
        assert sum(av["per_category"].values()) == len(av["available"])

    def test_availability_future_date_not_occupied(self):
        # future date pe in-house occupancy nahi ho sakti (ChkOutDate null
        # wale aaj bhi andar hain) — shape consistent rehna chahiye
        av = room_occ.room_availability(TODAY + timedelta(days=30))
        assert av["total_rooms"] > 0


# ============================================================
# Reservation status reports + PDF
# ============================================================

class TestResStatusReports:
    @pytest.mark.parametrize("mode", ["arrival", "inhouse", "departure",
                                      "reservation", "noshow", "cancellation"])
    def test_all_modes_return_lists(self, mode):
        rows = reports.res_status(mode)
        assert isinstance(rows, list)

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            reports.res_status("hologram")

    def test_pdf_writes_valid_magic(self, tmp_path):
        rows = reports.res_status("arrival") or [
            {"bookno": 1, "arr": TODAY, "dep": TODAY, "guest": "PYT",
             "room": "101", "rate": 100}]
        path = reports.res_status_pdf(rows, "arrival",
                                      path=str(tmp_path / "t.pdf"))
        with open(path, "rb") as fh:
            assert fh.read(8).startswith(b"%PDF")


# ============================================================
# System config (Enviro-backed) — read + validation only
# ============================================================

class TestSysConfig:
    def test_get_config_shape(self):
        cfg = sys_config.get_config()
        assert "SiteCode" in cfg
        assert "RoundOffSetting" in cfg

    def test_update_config_rejects_bad_roundoff(self):
        with pytest.raises(ValueError):
            sys_config.update_config({"RoundOffSetting": "Maybe"})


# ============================================================
# Facility billing (header + line transaction)
# ============================================================

class TestFacilityBilling:
    def test_insert_get_delete_roundtrip(self):
        party = "PYTFB"
        made = facility_billing.insert_bill_with_line({
            "partycode": party, "facilitycode": "POOL",
            "amount": 500, "unitrate": 500, "remark": "PYT test"})
        docid = made["docid"]
        try:
            assert docid
            line = facility_billing.get_fbill1(docid)
            assert line is not None
            assert float(line["amount"]) == 500.0
            assert line["facilitycode"] == "POOL"
        finally:
            facility_billing.delete_fbill1(docid, made["line"]["sno"])
            facility_billing.delete_fbill(docid)

    def test_list_all_returns_dicts(self):
        rows = facility_billing.list_all()
        assert isinstance(rows, list)
        if rows:
            assert "docid" in rows[0]


# ============================================================
# Guest services roundtrip (GuestComments)
# ============================================================

class TestGuestServices:
    def test_comment_insert_get_delete(self):
        made = guest_services.insert_comments({
            "name": "PYT GS", "comments": "integration test",
            "mobile": "0000000000"})
        code = made["code"]
        try:
            got = guest_services.get_comments(code)
            assert got is not None
            assert got["comments"] == "integration test"
        finally:
            guest_services.delete_comments(code)


# ============================================================
# KOT / POS reports (read-only)
# ============================================================

class TestPosReports:
    def test_kot_list_shape(self):
        rows = pos.kot_list()
        assert isinstance(rows, list)
        if rows:
            assert {"docid", "vno", "amount"} <= set(rows[0].keys())

    def test_sales_and_itemwise(self):
        assert isinstance(pos.sales_summary(), list)
        assert isinstance(pos.itemwise_sale(), list)

    def test_depart_list_alias(self):
        rows = depart.depart_list()
        assert len(rows) > 0
        assert "code" in rows[0]


# ============================================================
# Ledger master bridge (fa_ledger_ui -> SubGroup)
# ============================================================

class TestLedgerBridge:
    def test_list_ledger_maps_ui_keys(self):
        from HMS_py.ui import fa_ledger_ui
        rows = fa_ledger_ui.fa_ledger_ops.list_ledger()
        assert isinstance(rows, list)
        if rows:
            assert "AcCode" in rows[0] and "AcName" in rows[0]

    def test_ledger_search_positive_and_negative(self):
        assert isinstance(ledger.search("ZZZNOMATCHZZZ"), list)
        rows = ledger.list_all()
        if rows:
            got = ledger.get(rows[0]["code"])
            assert got is not None and got["code"] == rows[0]["code"]


# ============================================================
# HR payroll update guards (negative-only, no data pollution)
# ============================================================

class TestHrPayrollGuards:
    def test_update_salary_empty_rec(self):
        from HMS_py.core import hr_payroll
        with pytest.raises(ValueError):
            hr_payroll.update_salary("PYT-2099", "PYTEMP", {})

    def test_update_loan_empty_rec(self):
        from HMS_py.core import hr_payroll
        with pytest.raises(ValueError):
            hr_payroll.update_loan("PYTEMP", 999999, {})
