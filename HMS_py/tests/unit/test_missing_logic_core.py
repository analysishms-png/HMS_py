"""Unit tests: P1 missing-logic core writers (Room Change, Merge Charge,
Re-Settlement, Table Change, KOT Transfer). No live DB - sab db.query /
db.execute mocks hain. run: python -m pytest tests/unit -q"""
import datetime
from types import SimpleNamespace

import pytest

from HMS_py.core import db, fo_ops, pos_kot


class FakeCn:
    def __init__(self):
        self.committed = False
        self.closed = False

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True

    def cursor(self):
        return self


def _apply(monkeypatch, query=None, execute=None, next_vno=None, connect=None):
    if query is not None:
        monkeypatch.setattr(db, "query", query)
    if execute is not None:
        monkeypatch.setattr(db, "execute", execute)
    if next_vno is not None:
        monkeypatch.setattr(db, "next_vno", next_vno)
    if connect is not None:
        monkeypatch.setattr(db, "connect", connect)
    else:
        monkeypatch.setattr(db, "connect", lambda: FakeCn())


def _recorder():
    calls = []

    def rec(sql, params=(), cn=None, commit=True):
        calls.append({"sql": sql, "params": params, "commit": commit})
        return 1
    return rec, calls


# ------------------------------------------------------------
# Room Change
# ------------------------------------------------------------
def _roomocc_row():
    return SimpleNamespace(
        DocId="DKKCHK   2025    1000", SNo=2, FolioNo=10, Vtype="CHK",
        Site_Code="KK", Vprefix="2025", GuestProf="PYT1", RoomCat="SUP",
        RoomType="RO", RoomNo="101", RateCode="RC1", RoomRate=1800.0,
        ChkInDate=datetime.date(2025, 1, 1), ChkInTime="12:00",
        Adult=2, Children=0, DepDate=datetime.date(2025, 1, 5),
        DepTime="12:00", ChkOutDate=None, ChkOutTime=None, Type="",
        U_Name="ADMIN", U_EntDt=datetime.datetime(2025, 1, 1),
        U_AE="A", UserchkoutDate=None, ChkoutUser=None, NewRoomNo=None,
        Reason=None, PlanCode="CP1", PlanAmt=1800.0, IncInRate="Y",
        LogSite_Code="KK", PlanDisc=0.0, PlanDiscAmt=0.0,
        PlanDiscAppon="", RRTaxInc="Y", RRServiceChrg="N",
        ChngDate=None, ExtraBed="", RoomTarrif=2000.0,
        RoomTaxStru="", RackRate=2500.0)


def test_room_change_moves_guest(monkeypatch):
    rec, calls = _recorder()
    epubx = {"n": 10}

    def fq(sql, params=(), cn=None):
        if sql.startswith("SELECT DocId, SNo, FolioNo"):
            return [_roomocc_row()]
        if "SELECT TOP 1 RoomCat FROM RoomMast" in sql:
            return [SimpleNamespace(RoomCat="STD")]
        if "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ?" in sql:
            return [(0,)]
        if "SELECT TOP 1 FolioNo, Name, BookingDocId" in sql:
            return [SimpleNamespace(FolioNo=10, Name="PYT Guest",
                                    BookingDocId="BKR2025     101")]
        if "SELECT MAX(SNo) FROM RoomOcc" in sql:
            return [(2,)]
        if "FROM PlanDetails WHERE DocId = ?" in sql:
            return []
        if "FROM EPABX_IN" in sql:
            epubx["n"] += 1
            return [(epubx["n"],)]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    cn = FakeCn()
    res = fo_ops.room_change("DKKCHK   2025    1000", "201", "fault",
                             user="T1", cn=cn)
    assert cn.committed and cn.closed is False
    assert res["old_room"] == "101" and res["new_room"] == "201"
    assert res["new_sno"] == 3 and res["folio"] == 10
    inserts = [c for c in calls if "INSERT INTO RoomOcc" in c["sql"]]
    updates = [c for c in calls if "UPDATE RoomOcc" in c["sql"]]
    assert len(inserts) == 1 and len(updates) == 2
    assert inserts[0]["params"][8] == "201"  # RoomNo
    checkout = [c for c in updates if "Type = 'C'" in c["sql"]]
    assert checkout and checkout[0]["params"][2] == "201"
    roommast = [c for c in calls if "UPDATE RoomMast SET RoomStat = 'D'" in c["sql"]]
    assert roommast and roommast[0]["params"][1] == "101"
    epabx = [c for c in calls if "EPABX_IN" in c["sql"]]
    assert len(epabx) == 2


def test_room_change_rejects_occupied_new_room(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if sql.startswith("SELECT DocId, SNo, FolioNo"):
            return [_roomocc_row()]
        if "SELECT TOP 1 RoomCat FROM RoomMast" in sql:
            return [SimpleNamespace(RoomCat="STD")]
        if "SELECT COUNT(*) FROM RoomOcc WHERE RTRIM(RoomNo) = ?" in sql:
            return [(1,)]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="occupied"):
        fo_ops.room_change("DKKCHK   2025    1000", "201", cn=FakeCn())
    assert not calls


def test_room_change_rejects_same_room(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if sql.startswith("SELECT DocId, SNo, FolioNo"):
            return [_roomocc_row()]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="same"):
        fo_ops.room_change("DKKCHK   2025    1000", "101", cn=FakeCn())
    assert not calls


# ------------------------------------------------------------
# Merge Charge
# ------------------------------------------------------------
def _folio(docid, folio):
    return SimpleNamespace(DocId=docid, FolioNo=folio, GuestProf="PYT1",
                           Name="Guest", BookingDocId="", Vprefix="2025",
                           Vdate=datetime.date(2025, 1, 1))


def test_merge_charge_moves_lines(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if params and params[0] == "101":
            return [_folio("SRCDOC", 5)]
        if params and params[0] == "102":
            return [_folio("TGTDOC", 6)]
        return [(100.0,)]

    _apply(monkeypatch, query=fq, execute=rec)
    cn = FakeCn()
    res = fo_ops.merge_charge("101", "102", cn=cn, site="KK")
    assert cn.committed
    assert res["folio_from"] == 5 and res["folio_to"] == 6
    gfsql = [c for c in calls if "UPDATE GuestFolio" in c["sql"]]
    assert gfsql and gfsql[0]["params"][:2] == ("TGTDOC", 6)
    pc = [c for c in calls if "UPDATE PayCharge" in c["sql"]]
    assert len(pc) == 2
    rehome = [c for c in pc if "FolioNoDocid = ?," in c["sql"]]
    assert rehome and rehome[0]["params"][:2] == ("TGTDOC", 6)


def test_merge_charge_same_folio_rejected(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        return [_folio("DOC1", 5)]

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="same"):
        fo_ops.merge_charge("101", "102", cn=FakeCn())
    assert not calls


def test_merge_charge_no_target_folio_rejected(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if params and params[0] == "101":
            return [_folio("SRCDOC", 5)]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="in-house"):
        fo_ops.merge_charge("101", "102", cn=FakeCn())


# ------------------------------------------------------------
# Re-Settlement
# ------------------------------------------------------------
def test_re_settlement_reverses_and_reposts(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if "FROM GuestFolio" in sql:
            return [SimpleNamespace(FolioNo=5, GuestProf="PYT1", Vprefix="2025")]
        if "SELECT TOP 1 RoomCat, RoomType, RoomNo" in sql:
            return [SimpleNamespace(RoomCat="SUP", RoomType="RO", RoomNo="101")]
        if "SELECT TOP 1 DocId, AmtCr FROM PayCharge" in sql:
            return [SimpleNamespace(DocId="OLD REC", AmtCr=500.0)]
        return []

    counter = {"n": 9000}

    def fake_vno(*a, **k):
        counter["n"] += 1
        return counter["n"]

    _apply(monkeypatch, query=fq, execute=rec, next_vno=fake_vno)
    cn = FakeCn()
    res = fo_ops.re_settlement("SRCDOC", [
        {"paycode": "KKCASH", "amount": 300.0, "comments": "CASH"},
        {"paycode": "KKVISA", "amount": 200.0, "comments": "CARD"},
    ], cn=cn, site="KK")
    assert cn.committed
    assert res["new_vnos"] == [9001, 9002]
    dels = [c for c in calls if c["sql"].startswith("DELETE")]
    assert dels and "SMALL" not in dels[0]["sql"]
    ins = [c for c in calls if c["sql"].startswith("INSERT")]
    assert len(ins) == 2
    assert ins[0]["params"][0] == "DKKREC   2025    9001"
    assert ins[0]["params"][10] == 300.0
    assert ins[1]["params"][10] == 200.0


def test_re_settlement_no_prior_receipt(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if "FROM GuestFolio" in sql:
            return [SimpleNamespace(FolioNo=5, GuestProf="PYT1", Vprefix="2025")]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="receipt"):
        fo_ops.re_settlement("SRCDOC", [{"paycode": "KKCASH", "amount": 100}],
                             cn=FakeCn())


def test_re_settlement_sum_mismatch(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if "FROM GuestFolio" in sql:
            return [SimpleNamespace(FolioNo=5, GuestProf="PYT1", Vprefix="2025")]
        if "SELECT TOP 1 DocId, AmtCr FROM PayCharge" in sql:
            return [SimpleNamespace(DocId="OLD REC", AmtCr=500.0)]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="match"):
        fo_ops.re_settlement("SRCDOC", [{"paycode": "KKCASH", "amount": 400}],
                             cn=FakeCn())


# ------------------------------------------------------------
# Table Change / KOT Transfer (pos_kot)
# ------------------------------------------------------------
def test_table_change_updates_pending_kots(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if "SELECT COUNT(*) FROM KOT" in sql:
            return [(3,)]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    cn = FakeCn()
    n = pos_kot.table_change("KKFOM", "T3", "T9", cn=cn, site="KK")
    assert n == 1 and cn.committed
    upd = [c for c in calls if c["sql"].startswith("UPDATE")]
    assert upd and upd[0]["params"][0] == "T9"
    assert "U_AE1 = 'E'" in upd[0]["sql"] and "Pending = 'Y'" in upd[0]["sql"]


def test_table_change_no_pending_rejected(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        return [(0,)]

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="pending"):
        pos_kot.table_change("KKFOM", "T3", "T9", cn=FakeCn())
    assert not calls


def test_kot_transfer_room_service_syncs_roomcat(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        if "SELECT TOP 1 RoomCat FROM RoomOcc" in sql:
            return [SimpleNamespace(RoomCat="DELUXE")]
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    cn = FakeCn()
    res = pos_kot.kot_transfer("KKFOM", "ROOMALKOT2025123", "204",
                               room_service=True, cn=cn, site="KK")
    assert res["roomcat_updated"] and cn.committed
    upd = [c for c in calls if c["sql"].startswith("UPDATE")]
    assert "RoomCat = ?" in upd[0]["sql"]
    assert upd[0]["params"][:2] == ("204", "DELUXE")
    assert "AND DocId = ?" in upd[0]["sql"]


def test_kot_transfer_room_service_no_guest(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    with pytest.raises(ValueError, match="in-house"):
        pos_kot.kot_transfer("KKFOM", "ROOMALKOT2025123", "204",
                             room_service=True, cn=FakeCn())


def test_kot_transfer_normal_by_vno(monkeypatch):
    rec, calls = _recorder()

    def fq(sql, params=(), cn=None):
        return []

    _apply(monkeypatch, query=fq, execute=rec)
    cn = FakeCn()
    res = pos_kot.kot_transfer("KKFOM", "42", "T9", room_service=False,
                               cn=cn, site="KK")
    assert cn.committed
    upd = [c for c in calls if c["sql"].startswith("UPDATE")]
    assert "AND VNo = ?" in upd[0]["sql"]
    assert upd[0]["params"][0] == "T9"
    assert not res["roomcat_updated"]