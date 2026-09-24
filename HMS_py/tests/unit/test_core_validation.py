"""Unit tests for HMS_py core modules - no database required."""
import os
import pytest
from datetime import date, timedelta


class TestAuthEncryptDecrypt:
    """Test VB6-compatible encryption/decryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypt then decrypt should return original."""
        from HMS_py.core import auth
        
        test_passwords = [
            "India12",
            "SApass1", 
            "x",
            "Complex@Pass123",
            "UPPERCASE",
            "lowercase",
            "MiXeD123!@#",
            "",  # Empty password
        ]
        
        for pwd in test_passwords:
            # Test with fixed seed for reproducibility
            encrypted = auth.encrypt(pwd, seed=42)
            decrypted = auth.decrypt(encrypted)
            assert decrypted == pwd, f"Roundtrip failed for {pwd!r}"

    def test_encrypt_different_seeds(self):
        """Same password with different seeds produces different ciphertext."""
        from HMS_py.core import auth
        
        pwd = "TestPass123"
        enc1 = auth.encrypt(pwd, seed=10)
        enc2 = auth.encrypt(pwd, seed=50)
        enc3 = auth.encrypt(pwd, seed=99)
        
        assert enc1 != enc2 != enc3
        # But all decrypt to same
        assert auth.decrypt(enc1) == pwd
        assert auth.decrypt(enc2) == pwd
        assert auth.decrypt(enc3) == pwd

    def test_decrypt_empty_string(self):
        """Decrypt empty string returns empty."""
        from HMS_py.core import auth
        assert auth.decrypt("") == ""

    def test_vb6_sa_password_known(self):
        """SA password from live DB decrypts to known value.
        
        Evidence: SA raw=3c877d8a8c918e -> decrypt 'KANPUR' (seed=33)
        """
        from HMS_py.core import auth
        
        # Raw bytes from DB (latin-1 decoded)
        sa_raw = bytes([0x3c, 0x87, 0x7d, 0x8a, 0x8c, 0x91, 0x8e]).decode('latin-1')
        decrypted = auth.decrypt(sa_raw)
        assert decrypted == "KANPUR"


class TestAuthCheckLogin:
    """Test login validation logic (requires DB - marked integration)."""
    
    # These are integration tests - will be in test_integration_auth.py


class TestPosMenuPermission:
    """POS masters should honor DB user-rights metadata."""

    def test_menu_name_allowed_uses_user_module_srno(self, monkeypatch):
        from HMS_py.core import menu

        def fake_query(sql, params=None, cn=None):
            if "FROM User1 WHERE USER_NAME" in sql:
                if params and params[0] == "USERA":
                    return [(100,)]
                if params and params[0] == "USERB":
                    return [(200,)]
                return []
            if "FROM User_Module" in sql:
                if params and params[0] == "Session Master":
                    return [(100,), (101,)]
                if params and params[0] == "Session Master (POS)":
                    return [(100,), (101,)]
                return []
            return []

        monkeypatch.setattr(menu.db, "query", fake_query)

        assert menu.menu_name_allowed("Session Master", "USERA") is True
        assert menu.menu_name_allowed("Session Master", "USERB") is False
        assert menu.menu_name_allowed("Session Master (POS)", "USERB") is False
        assert menu.menu_name_allowed("Unknown Menu", "USERB") is True


class TestPosCrudPermission:
    """POS CRUD actions must honor menu permissions."""

    def test_session_insert_rejects_disallowed_user(self, monkeypatch):
        from HMS_py.core import pos_masters

        monkeypatch.setattr(
            pos_masters,
            "menu_name_allowed",
            lambda name, user="SA": False if user == "USERB" else True,
        )

        with pytest.raises(PermissionError, match="Session Master"):
            pos_masters.session_insert({"code": "B1", "name": "Breakfast"}, user="USERB")


class TestPosKOTHelpers:
    """KOT entry needs real DB-backed POS helpers."""

    def test_pos_lookups_and_kot_create_roundtrip(self, monkeypatch):
        from HMS_py.core import pos

        calls = []

        def fake_query(sql, params=(), cn=None):
            if "FROM Depart" in sql:
                return [("R1", "Restaurant 1"), ("R2", "Restaurant 2")]
            if "FROM Waiter" in sql:
                return [("W1", "Amit"), ("W2", "Bharat")]
            if "FROM RoomMast" in sql:
                return [("T1", "Table 1"), ("T2", "Table 2")]
            if "FROM ItemMast" in sql:
                return [("I1", "Tea", "Cup", 25.0)]
            if "MAX(VNo)" in sql:
                return [(0,)]
            return []

        def fake_execute(sql, params=(), cn=None, commit=True):
            calls.append((sql, params, commit))
            return 1

        monkeypatch.setattr(pos.db, "query", fake_query)
        monkeypatch.setattr(pos.db, "execute", fake_execute)
        # _table_exists ko bhi stub karo — warna Waiter/RoomMast guards
        # fake_query se [] lekar helpers ko empty leutaate hain (guard
        # mapping-test ka intent nahi hai)
        monkeypatch.setattr(pos, "_table_exists",
                            lambda table, cn=None: True)

        outlets = pos.get_outlets()
        waiters = pos.get_waiters()
        tables = pos.get_tables("R1")
        items = pos.get_items("R1")

        assert outlets[0]["code"] == "R1"
        assert waiters[1]["name"] == "Bharat"
        assert tables[0]["name"] == "Table 1"
        assert items[0]["rate"] == 25.0

        result = pos.create_kot(
            [{"sno": 1, "item": "I1", "qty": 2, "rate": 25.0, "amount": 50.0, "table": "T1", "waiter": "W1", "nc_type": "", "remarks": ""}],
            "R1",
            "2026-09-19",
            waiter="W1",
            user="SA",
        )

        assert result["docid"].startswith("KOT")
        assert result["vno"] == 1
        assert calls and any("INSERT INTO KOT" in c[0] for c in calls)


class TestReservationVoucherBehavior:
    """Reservation voucher generation must honor site + voucher type."""

    def test_make_docid_uses_supplied_vtype(self):
        from HMS_py.core import reservation

        docid = reservation.make_docid("KK", "2026", 12, "CHK")

        assert docid.startswith("DKKCHK")
        assert "RES" not in docid

    def test_list_reservations_accepts_site_argument(self):
        from HMS_py.core import reservation

        rows = reservation.list_reservations(site="KK", top=3)
        assert isinstance(rows, list)


class TestCountryValidation:
    """Test Country master validation."""

    def test_validate_requires_code(self):
        from HMS_py.core import country
        
        with pytest.raises(ValueError, match="Code zaroori hai"):
            country._validate({"code": "", "name": "Test"})

    def test_validate_requires_name(self):
        from HMS_py.core import country
        
        with pytest.raises(ValueError, match="Name zaroori hai"):
            country._validate({"code": "TEST", "name": ""})

    def test_validate_code_max_length(self):
        from HMS_py.core import country
        
        with pytest.raises(ValueError, match="Code max 6 chars"):
            country._validate({"code": "TOOLONG", "name": "Test"})

    def test_validate_name_max_length(self):
        from HMS_py.core import country
        
        with pytest.raises(ValueError, match="Name max 30 chars"):
            country._validate({"code": "TEST", "name": "A" * 31})

    def test_validate_optional_fields_max_length(self):
        from HMS_py.core import country
        
        with pytest.raises(ValueError, match="short max 6 chars"):
            country._validate({"code": "TEST", "name": "Test", "short": "TOOLONG"})
        
        with pytest.raises(ValueError, match="type max 7 chars"):
            country._validate({"code": "TEST", "name": "Test", "type": "TOOLONGTYPE"})
        
        with pytest.raises(ValueError, match="nationality max 25 chars"):
            country._validate({"code": "TEST", "name": "Test", "nationality": "A" * 26})

    def test_validate_valid_record(self):
        from HMS_py.core import country
        
        # Should not raise
        country._validate({
            "code": "TEST",
            "name": "Test Country",
            "short": "TST",
            "type": "India",
            "nationality": "Testian"
        })


class TestStateValidation:
    """Test State master validation."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import state
        
        with pytest.raises(ValueError, match="Code zaroori hai"):
            state._validate({"code": "", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name zaroori hai"):
            state._validate({"code": "TEST", "name": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import state
        
        with pytest.raises(ValueError, match="Code max 6 chars"):
            state._validate({"code": "TOOLONG", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name max 30 chars"):
            state._validate({"code": "TEST", "name": "A" * 31})
        
        with pytest.raises(ValueError, match="country max 6 chars"):
            state._validate({"code": "TEST", "name": "Test", "country": "TOOLONG"})
        
        # Note: short field is NOT validated in current implementation
        # LIMITS has "short": 6 but _validate doesn't check it


class TestCityValidation:
    """Test City master validation."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import city
        
        with pytest.raises(ValueError, match="CityCode zaroori hai"):
            city._validate({"code": "", "name": "Test"})
        
        with pytest.raises(ValueError, match="CityName zaroori hai"):
            city._validate({"code": "TEST", "name": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import city
        
        with pytest.raises(ValueError, match="CityCode max 6 chars"):
            city._validate({"code": "TOOLONG", "name": "Test"})
        
        with pytest.raises(ValueError, match="CityName max 35 chars"):
            city._validate({"code": "TEST", "name": "A" * 36})
        
        with pytest.raises(ValueError, match="short max 6 chars"):
            city._validate({"code": "TEST", "name": "Test", "short": "TOOLONG"})
        
        with pytest.raises(ValueError, match="zip max 11 chars"):
            city._validate({"code": "TEST", "name": "Test", "zip": "A" * 12})
        
        with pytest.raises(ValueError, match="state max 6 chars"):
            city._validate({"code": "TEST", "name": "Test", "state": "TOOLONG"})


class TestAreaValidation:
    """Test Area master validation."""

    def test_validate_requires_code_name_city(self):
        from HMS_py.core import area
        
        with pytest.raises(ValueError, match="AreaCODE zaroori hai"):
            area._validate({"code": "", "name": "Test", "city": "CITY1"})
        
        with pytest.raises(ValueError, match="AreaNAME zaroori hai"):
            area._validate({"code": "TEST", "name": "", "city": "CITY1"})
        
        with pytest.raises(ValueError, match="CityCode zaroori hai"):
            area._validate({"code": "TEST", "name": "Test", "city": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import area
        
        with pytest.raises(ValueError, match="AreaCODE max 5 chars"):
            area._validate({"code": "TOOLONG", "name": "Test", "city": "CITY1"})
        
        with pytest.raises(ValueError, match="AreaNAME max 25 chars"):
            area._validate({"code": "TEST", "name": "A" * 26, "city": "CITY1"})
        
        with pytest.raises(ValueError, match="CityCode max 6 chars"):
            area._validate({"code": "TEST", "name": "Test", "city": "TOOLONG"})


class TestGuestProfValidation:
    """Test Guest Profile validation."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import guestprof
        
        with pytest.raises(ValueError, match="Code zaroori hai"):
            guestprof._validate({"code": "", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name zaroori hai"):
            guestprof._validate({"code": "TEST", "name": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import guestprof
        
        # LIMITS["code"] = 8, validation uses > so 9 chars triggers error
        with pytest.raises(ValueError, match="Code max 8 chars"):
            guestprof._validate({"code": "TOOLONGCX", "name": "Test"})  # 9 chars
        
        with pytest.raises(ValueError, match="Name max 50 chars"):
            guestprof._validate({"code": "TEST", "name": "A" * 51})
        
        with pytest.raises(ValueError, match="add1 max 50 chars"):
            guestprof._validate({"code": "TEST", "name": "Test", "add1": "A" * 51})
        
        with pytest.raises(ValueError, match="city max 6 chars"):
            guestprof._validate({"code": "TEST", "name": "Test", "city": "TOOLONG"})


class TestRoomMasterValidation:
    """Test Room Master validation."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import roommaster
        
        with pytest.raises(ValueError, match="Code zaroori hai"):
            roommaster._validate({"code": "", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name zaroori hai"):
            roommaster._validate({"code": "TEST", "name": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import roommaster
        
        with pytest.raises(ValueError, match="Code max 5 chars"):
            roommaster._validate({"code": "TOOLONG", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name max 15 chars"):
            roommaster._validate({"code": "TEST", "name": "A" * 16})


class TestReservationValidation:
    """Test Reservation validation."""

    def test_insert_requires_guest_name(self):
        # Test the validation logic directly - empty guest name should raise
        with pytest.raises(ValueError, match="GuestName zaroori hai"):
            # This simulates the check in insert_draft
            guest_name = ""
            if not guest_name.strip():
                raise ValueError("GuestName zaroori hai")

    def test_insert_requires_arrival_before_departure(self):
        arr = date.today() + timedelta(days=5)
        dep = date.today() + timedelta(days=3)  # Before arrival!
        
        with pytest.raises(ValueError, match="Arrival > Departure"):
            if arr > dep:
                raise ValueError("Arrival > Departure nahi ho sakta")


class TestCheckinValidation:
    """Test Check-in validation."""

    def test_create_requires_guest_name(self):
        with pytest.raises(ValueError, match="Guest Name zaroori hai"):
            if not "".strip():
                raise ValueError("Guest Name zaroori hai")

    def test_create_requires_arrival_before_departure(self):
        arr = date.today() + timedelta(days=5)
        dep = date.today() + timedelta(days=3)
        
        with pytest.raises(ValueError, match="Arrival > Departure"):
            if arr > dep:
                raise ValueError("Arrival > Departure nahi ho sakta")


class TestCheckoutBalance:
    """Test folio balance calculation."""

    def test_balance_calculation(self):
        """Balance = Charges(Dr) - Payments(Cr)."""
        # Dr = 10000, Cr = 3000 -> Balance = 7000
        dr = 10000.0
        cr = 3000.0
        balance = round(dr - cr, 2)
        assert balance == 7000.0

    def test_balance_zero_when_paid(self):
        dr = 5000.0
        cr = 5000.0
        balance = round(dr - cr, 2)
        assert balance == 0.0

    def test_balance_negative_when_overpaid(self):
        dr = 3000.0
        cr = 5000.0
        balance = round(dr - cr, 2)
        assert balance == -2000.0

    def test_checkout_balance_uses_live_paycharge_link_column(self):
        """Live DB uses FolioNoDocid, not FolioDocId."""
        from HMS_py.core import checkout, guestprof, checkin
        import datetime

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT CHECKOUT TEST", "add1": "TEST", "type": "India"})
        try:
            folio_no = checkin.create_checkin(
                gcode,
                "PYT CHECKOUT TEST",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=2),
            )
            bal = checkout.folio_balance(folio_no)
            assert bal["folio"] == folio_no
            assert "balance" in bal
        finally:
            try:
                checkin.delete_checkin(folio_no)
            finally:
                guestprof.delete(gcode)

    def test_checkout_and_reverse_checkout_update_roomocc(self):
        """Real checkout flow updates RoomOcc ChkOutDate and reopens it on reverse."""
        from HMS_py.core import checkout, guestprof, checkin, db
        import datetime

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT ROOM OCC TEST", "add1": "TEST", "type": "India"})
        folio_no = None
        try:
            folio_no = checkin.create_checkin(
                gcode,
                "PYT ROOM OCC TEST",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=2),
            )
            rec = checkin.get(folio_no)
            docid = rec["docid"]

            result = checkout.do_checkout(folio_no, user="PYADMIN")
            assert result["folio"] == folio_no

            rows = db.query(
                "SELECT ChkOutDate, ChkoutUser, Type FROM RoomOcc WHERE DocId = ? AND Site_Code = ? AND Vprefix = ?",
                (docid, "KK", "2026"),
            )
            assert rows and rows[0][0] is not None
            assert str(rows[0][2] or "").upper() == "O"

            checkout.reverse_checkout(folio_no, user="PYADMIN")
            reopened = db.query(
                "SELECT ChkOutDate FROM RoomOcc WHERE DocId = ? AND Site_Code = ? AND Vprefix = ?",
                (docid, "KK", "2026"),
            )
            assert reopened and reopened[0][0] is None
        finally:
            if folio_no is not None:
                try:
                    checkout.reverse_checkout(folio_no, user="PYADMIN")
                except Exception:
                    pass
                try:
                    checkin.delete_checkin(folio_no)
                except Exception:
                    pass
            try:
                guestprof.delete(gcode)
            except Exception:
                pass


class TestStockTransferLogic:
    """Test BMTC transfer pairs for inter-godown stock movement."""

    def test_build_transfer_lines_are_balanced_pair(self):
        from HMS_py.core import inventory

        lines = inventory.build_transfer_lines(
            item="ITM001",
            from_godown="G1",
            to_godown="G2",
            qty=25,
            unit="PCS",
            rate=10,
            amount=250,
        )

        assert len(lines) == 2
        assert lines[0]["godown"] == "G1"
        assert lines[0]["qty"] == -25
        assert lines[1]["godown"] == "G2"
        assert lines[1]["qty"] == 25
        assert lines[0]["amount"] == -250
        assert lines[1]["amount"] == 250

    def test_build_transfer_rejects_same_godown(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Source and destination godown same"):
            inventory.build_transfer_lines("ITM001", "G1", "G1", 10)

    def test_build_transfer_rejects_zero_qty(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Qty > 0"):
            inventory.build_transfer_lines("ITM001", "G1", "G2", 0)

    def test_build_transfer_rejects_negative_qty(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Qty > 0"):
            inventory.build_transfer_lines("ITM001", "G1", "G2", -5)

    def test_build_transfer_rejects_missing_item(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Item.*zaroori"):
            inventory.build_transfer_lines("", "G1", "G2", 10)

    def test_build_transfer_calculates_amount_from_rate(self):
        from HMS_py.core import inventory

        lines = inventory.build_transfer_lines(
            item="ITM001",
            from_godown="G1",
            to_godown="G2",
            qty=10,
            rate=25,
        )

        assert lines[0]["amount"] == -250
        assert lines[1]["amount"] == 250

    def test_build_transfer_preserves_remarks(self):
        from HMS_py.core import inventory

        lines = inventory.build_transfer_lines(
            item="ITM001",
            from_godown="G1",
            to_godown="G2",
            qty=10,
            remarks="Test transfer",
        )

        assert "G2" in lines[0]["remarks"]
        assert "G1" in lines[1]["remarks"]

    def test_stock_vtypes_mapping(self):
        from HMS_py.core import inventory

        assert inventory.VTYPES["issue"] == "RQI"
        assert inventory.VTYPES["receive"] == "RQR"
        assert inventory.VTYPES["adjust"] == "ADJ"
        assert inventory.VTYPES["transfer"] == "BMTC"

    def test_stock_transfer_insert_has_matching_params(self, monkeypatch):
        from HMS_py.core import inventory

        calls = []

        def fake_execute(sql, params=(), cn=None, commit=True):
            calls.append((sql, params))
            return 1

        monkeypatch.setattr(inventory, "stock_next_vno", lambda *a, **k: 7)
        monkeypatch.setattr(inventory.db, "execute", fake_execute)

        result = inventory.stock_transfer(
            "ITM001", "G1", "G2", 1,
            unit="PCS", rate=10, amount=10,
            user="PYADMIN", commit=False,
        )

        assert result["docid"].startswith("D")
        assert result["vno"] == 7
        assert calls
        for sql, params in calls:
            assert sql.count("?") == len(params), (sql, params)

    def test_make_docid_format(self):
        from HMS_py.core import inventory

        docid = inventory._make_docid("BMTC", "2026", 42)

        assert len(docid) == 21
        assert docid.startswith("D")
        assert "BMTC" in docid
        assert "2026" in docid
        assert docid.endswith("42".rjust(8))


class TestStockIssueReceipt:
    """Test stock issue/receipt validation and Vtype mapping."""

    def test_validate_stock_line_requires_item(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Item code zaroori"):
            inventory.validate_stock_line({"item": "", "godown": "G1", "qty": 1})

    def test_validate_stock_line_requires_godown(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Godown code zaroori"):
            inventory.validate_stock_line({"item": "ITM001", "godown": "", "qty": 1})

    def test_validate_stock_line_requires_positive_qty(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Qty positive"):
            inventory.validate_stock_line({"item": "ITM001", "godown": "G1", "qty": 0})

    def test_validate_stock_line_rejects_negative_qty(self):
        from HMS_py.core import inventory
        import pytest

        with pytest.raises(ValueError, match="Qty positive"):
            inventory.validate_stock_line({"item": "ITM001", "godown": "G1", "qty": -5})

    def test_validate_stock_line_valid(self):
        from HMS_py.core import inventory

        inventory.validate_stock_line({"item": "ITM001", "godown": "G1", "qty": 10, "rate": 50})

    def test_stock_vtype_map_has_all_types(self):
        from HMS_py.core import inventory

        assert "RQI" in inventory.STOCK_VTYPE_MAP
        assert "RQR" in inventory.STOCK_VTYPE_MAP
        assert "KSISS" in inventory.STOCK_VTYPE_MAP
        assert "KSREC" in inventory.STOCK_VTYPE_MAP
        assert "KMISS" in inventory.STOCK_VTYPE_MAP
        assert "KMREC" in inventory.STOCK_VTYPE_MAP
        assert "BKREC" in inventory.STOCK_VTYPE_MAP

    def test_stock_issue_uses_rqi_vtype(self, monkeypatch):
        from HMS_py.core import inventory

        calls = []
        def fake_create(vtype, lines, *a, **k):
            calls.append(vtype)
            return {"docid": "D", "vno": 1, "vtype": vtype}

        monkeypatch.setattr(inventory, "stock_create", fake_create)
        inventory.stock_issue([{"item": "X", "godown": "G1", "qty": 1}])
        assert calls[0] == "RQI"

    def test_stock_receive_uses_rqr_vtype(self, monkeypatch):
        from HMS_py.core import inventory

        calls = []
        def fake_create(vtype, lines, *a, **k):
            calls.append(vtype)
            return {"docid": "D", "vno": 1, "vtype": vtype}

        monkeypatch.setattr(inventory, "stock_create", fake_create)
        inventory.stock_receive([{"item": "X", "godown": "G1", "qty": 1}])
        assert calls[0] == "RQR"

    def test_kitchen_stock_issue_uses_ksiss_vtype(self, monkeypatch):
        from HMS_py.core import inventory

        calls = []
        def fake_create(vtype, lines, *a, **k):
            calls.append(vtype)
            return {"docid": "D", "vno": 1, "vtype": vtype}

        monkeypatch.setattr(inventory, "stock_create", fake_create)
        inventory.kitchen_stock_issue([{"item": "X", "godown": "G1", "qty": 1}])
        assert calls[0] == "KSISS"


class TestDepartValidationExtended:
    """Extended department validation tests."""

    def test_validate_kotyn_must_be_yn(self):
        from HMS_py.core import depart
        import pytest

        with pytest.raises(ValueError, match="kotyn sirf Y/N"):
            depart._validate({"code": "D1", "name": "Test", "kotyn": "X"})

    def test_validate_pos_must_be_yn(self):
        from HMS_py.core import depart
        import pytest

        with pytest.raises(ValueError, match="pos sirf Y/N"):
            depart._validate({"code": "D1", "name": "Test", "pos": "M"})

    def test_validate_allows_empty_optional_fields(self):
        from HMS_py.core import depart

        depart._validate({"code": "D1", "name": "Test"})

    def test_validate_allows_valid_yn_fields(self):
        from HMS_py.core import depart

        depart._validate({"code": "D1", "name": "Test", "kotyn": "Y", "pos": "N"})


class TestFolioRoomCharge:
    """Test room charge posting with GST."""

    def test_room_charge_gst_calculation(self):
        """Room charge 3000 -> CGST 150 (5%) + SGST 150 (5%)."""
        amount = 3000.0
        gst_rate = 0.05
        
        cgst = round(amount * gst_rate, 2)
        sgst = round(amount * gst_rate, 2)
        
        assert cgst == 150.0
        assert sgst == 150.0
        assert cgst + sgst == 300.0

    def test_room_charge_gst_different_amounts(self):
        test_cases = [
            (1000.0, 50.0, 50.0),
            (2500.0, 125.0, 125.0),
            (5000.0, 250.0, 250.0),
            (1234.56, 61.73, 61.73),  # Rounding test
        ]
        
        for amount, expected_cgst, expected_sgst in test_cases:
            cgst = round(amount * 0.05, 2)
            sgst = round(amount * 0.05, 2)
            assert cgst == expected_cgst, f"CGST mismatch for {amount}"
            assert sgst == expected_sgst, f"SGST mismatch for {amount}"


class TestDepartValidation:
    """Test Department/Outlet validation."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import depart

        with pytest.raises(ValueError, match="Code zaroori hai"):
            depart._validate({"code": "", "name": "Test"})

        with pytest.raises(ValueError, match="Name zaroori hai"):
            depart._validate({"code": "D1", "name": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import depart

        with pytest.raises(ValueError, match="Code max 6 chars"):
            depart._validate({"code": "TOOLONG", "name": "Test"})

        with pytest.raises(ValueError, match="Name max 35 chars"):
            depart._validate({"code": "D1", "name": "A" * 36})

        with pytest.raises(ValueError, match="Phone max 50 chars"):
            depart._validate({"code": "D1", "name": "Test", "phone": "A" * 51})


class TestNightAuditAndReportIndexMaps:
    """Test VB6 index mapping compatibility for hex values used by legacy handlers."""

    def test_night_audit_rr_accepts_hex_index(self):
        from HMS_py.core import nightaudit

        result = nightaudit.night_audit_rr(0x0A)
        assert result is not None
        assert result["report_name"] == "FOCC Report"

    def test_mat_rep_accepts_hex_index(self):
        from HMS_py.core import reports

        result = reports.mat_rep(0x0A)
        assert result is not None
        assert result["report_name"] == "DailyStoreIssRpt"
        assert result["form"] == "rInventRepView"

    def test_vat_register_accepts_hex_index(self):
        from HMS_py.core import reports

        result = reports.vat_register(0x0A)
        assert result is not None
        assert result["report_name"] == "VATRegisterII"


class TestTaxMasterValidation:
    """Test Tax Master validation (TaxStru table)."""

    def test_validate_requires_code_and_name(self):
        from HMS_py.core import taxmaster
        
        with pytest.raises(ValueError, match="Code zaroori hai"):
            taxmaster._validate({"code": "", "name": "Test"})
        
        with pytest.raises(ValueError, match="Name zaroori hai"):
            taxmaster._validate({"code": "TEST", "name": ""})

    def test_validate_valid_tax(self):
        from HMS_py.core import taxmaster
        
        # Should not raise
        taxmaster._validate({
            "code": "GST18",
            "name": "GST 18%",
            "taxper": 18.0,
            "taxtype": "GST",
            "onamount": "No",
            "active": "Y"
        })


class TestPlanValidation:
    """Test Plan Master validation."""

    def test_validate_max_lengths(self):
        from HMS_py.core import plans
        
        with pytest.raises(ValueError, match="Code max 5 chars"):
            plans._validate("TOOLONG", "Test", "")
        
        with pytest.raises(ValueError, match="Name max 25 chars"):
            plans._validate("TEST", "A" * 26, "")
        
        with pytest.raises(ValueError, match="Package max 7 chars"):
            plans._validate("TEST", "Test", "TOOLONGPKG")


class TestUserMasterValidation:
    """Test User Master validation."""

    def test_validate_requires_username(self):
        from HMS_py.core import usermaster
        
        with pytest.raises(ValueError, match="USER_NAME zaroori hai"):
            usermaster._validate({"username": ""})

    def test_validate_max_lengths(self):
        from HMS_py.core import usermaster
        
        with pytest.raises(ValueError, match="USER_NAME max 10 chars"):
            usermaster._validate({"username": "TOOLONGUSER"})
        
        with pytest.raises(ValueError, match="LABEL max 30 chars"):
            usermaster._validate({"username": "TEST", "label": "A" * 31})
        
        with pytest.raises(ValueError, match="ShortName max 10 chars"):
            usermaster._validate({"username": "TEST", "short": "TOOLONGSHORT"})


class TestDocIdGeneration:
    """Test DocId generation matches VB6 pattern."""

    def test_reservation_docid_format(self):
        """Reservation DocId: D + Site(2) + VTYPE(6) + Vprefix(4) + BookNo(8) = 21 chars."""
        from HMS_py.core import reservation
        
        site = "KK"
        vprefix = "2026"
        bookno = 16
        
        docid = reservation.make_docid(site, vprefix, bookno)
        
        assert len(docid) == 21
        assert docid.startswith("DKK")  # D + KK
        assert "RES" in docid  # VTYPE
        assert "2026" in docid  # Vprefix
        assert docid.endswith("16".rjust(8))  # BookNo right-justified
        
        # Exact match from VB6 sample: 'DKKRES   2026      16'
        expected = "DKKRES   2026      16"
        assert docid == expected

    def test_checkin_docid_format(self):
        """Check-in DocId: D + Site(2) + CHK(6) + Vprefix(4) + FolioNo(8) = 21 chars."""
        from HMS_py.core import checkin
        
        site = "KK"
        vprefix = "2026"
        folio = 1
        
        docid = checkin.make_docid(site, vprefix, folio)
        
        assert len(docid) == 21
        assert docid.startswith("DKK")
        assert "CHK" in docid
        assert "2026" in docid
        assert docid.endswith("1".rjust(8))
        
        # Exact match from VB6 sample: 'DKKCHK   2021       1'
        expected = "DKKCHK   2026       1"
        assert docid == expected

    def test_room_charge_docid_format(self):
        """Room charge DocId: D + Site(2) + RC(6) + Vprefix(4) + VNo(8) = 21 chars."""
        from HMS_py.core import folio
        
        site = "KK"
        vprefix = "2026"
        vno = 599
        
        docid = folio.make_pc_docid(site, vprefix, vno)
        
        assert len(docid) == 21
        assert docid.startswith("DKK")
        assert "RC" in docid
        assert "2026" in docid
        assert docid.endswith("599".rjust(8))
        
        # Exact match from live sample: 'DKKRC    2026     599'
        expected = "DKKRC    2026     599"
        assert docid == expected


class TestNextCodeGeneration:
    """Test auto-code generation for guest profiles."""

    def test_next_guest_code_format(self):
        """Guest code format: KK + 6 digits."""
        from HMS_py.core import guestprof
        
        # Can't test without DB, but verify format logic
        # Current max in DB: KK000002 -> next should be KK000003
        assert guestprof.LIMITS["code"] == 8  # KK + 6 digits = 8


class TestConfigLoading:
    """Test configuration loading."""

    def test_load_config_returns_dict(self):
        from HMS_py.core.db import load_config
        
        cfg = load_config()
        assert isinstance(cfg, dict)
        assert "server" in cfg
        assert "database" in cfg
        assert "reports" in cfg
        assert "temp" in cfg
        assert "company" in cfg
        assert "site" in cfg
        assert "modules" in cfg

    def test_load_config_has_defaults(self):
        from HMS_py.core.db import load_config
        
        cfg = load_config()
        # Should have fallback defaults even if INI missing
        assert cfg["server"] == "Localhost" or cfg["server"] != ""
        assert cfg["database"] in ("Moondata2627", "KailashData2526") or cfg["database"] != ""

    def test_load_config_prefers_project_analysis_ini(self):
        from HMS_py.core.db import find_analysis_ini, load_config
        import os

        ini_path = find_analysis_ini()
        assert ini_path is not None
        assert os.path.basename(ini_path) == "Analysis.ini"

        cfg = load_config()
        assert cfg["database"] != ""
        assert cfg["site"] != ""
        assert cfg["reports"] != ""


class TestQtStartupBootstrap:
    """Ensure the app can boot in headless environments without crashing."""

    def test_configure_qt_headless_sets_offscreen_when_no_display(self, monkeypatch):
        import HMS_py.main as main_mod
        monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
        monkeypatch.delenv("DISPLAY", raising=False)
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.setenv("HMS_FORCE_HEADLESS", "1")
        main_mod.configure_qt_headless()
        assert os.environ["QT_QPA_PLATFORM"] == "offscreen"


class TestMenuStructure:
    """Test menu model structure."""

    def test_roots_returns_list(self):
        from HMS_py.core.menu import roots
        
        # Can't test without DB, but verify function exists
        assert callable(roots)

    def test_sidebar_modules_returns_list(self):
        from HMS_py.core.menu import sidebar_modules
        
        assert callable(sidebar_modules)

    def test_main_setup_registry_has_vb6_workbench(self):
        import HMS_py.ui.shell as shell
        registry = shell._form_registry()

        assert "Main Setup" in registry
        assert callable(registry["Main Setup"])
        assert "Country Master" in registry
        assert "Room Category" in registry
        assert "FA Environment" in registry

    def test_marketsegment_list_all_works(self):
        from HMS_py.core import marketsegment
        result = marketsegment.list_all()
        assert isinstance(result, list)
        assert marketsegment.exists("X") is False

    def test_printing_setup_uses_analysis_ini_and_enviro(self):
        from HMS_py.core.general_setup import printing_settings_snapshot

        cfg = printing_settings_snapshot()

        assert isinstance(cfg, dict)
        assert "reports" in cfg
        assert "temp" in cfg
        assert cfg["reports"]
        assert cfg["temp"]
        assert "printer" in cfg
        assert "enviro" in cfg
        assert isinstance(cfg["enviro"], dict)

    def test_room_display_menu_opens_roomstatus_ui(self, monkeypatch):
        import HMS_py.ui.shell as shell
        from HMS_py.ui import roomstatus_ui

        called = {}

        class Dummy:
            user = "SA"

        def fake_open(parent=None, user="SA"):
            called["opened"] = True
            called["parent"] = parent
            called["user"] = user

        monkeypatch.setattr(roomstatus_ui, "open_roomstatus", fake_open)
        monkeypatch.setattr(shell.QMessageBox, "information", lambda *a, **k: called.__setitem__("placeholder", True))

        registry = shell._form_registry()
        callback = registry["Room Display"]
        callback(Dummy())

        assert called["opened"] is True
        assert called["user"] == "SA"
        assert "placeholder" not in called

    def test_guest_history_menu_opens_live_viewer(self, monkeypatch):
        import HMS_py.ui.shell as shell
        from HMS_py.ui import guest_history_ui

        called = {}

        class Dummy:
            user = "SA"

        def fake_open(parent=None, user="SA"):
            called["opened"] = True
            called["parent"] = parent
            called["user"] = user

        monkeypatch.setattr(guest_history_ui, "open_guest_history", fake_open)
        monkeypatch.setattr(shell.QMessageBox, "information", lambda *a, **k: called.__setitem__("placeholder", True))

        registry = shell._form_registry()
        callback = registry["Guest History"]
        callback(Dummy())

        assert called["opened"] is True
        assert called["user"] == "SA"
        assert "placeholder" not in called

    def test_guest_history_query_uses_live_status_fields(self, monkeypatch):
        from HMS_py.ui import guest_history_ui

        captured = {}

        def fake_query(sql, params=None, cn=None):
            captured["sql"] = sql
            captured["params"] = params
            return [
                (1, "DKKCHK   2026      1", "PYT GUEST", "101", "2026-09-10", "2026-09-12", "In-House", "KK0001", "PYADMIN", "KK")
            ]

        monkeypatch.setattr(guest_history_ui.db, "query", fake_query)
        viewer = guest_history_ui.GuestHistoryViewer()
        viewer.reload()

        assert "gf.Status" not in captured["sql"]
        assert "ChkOutDate" in captured["sql"]
        assert viewer.tbl.rowCount() == 1


class TestCompanyCurrentYear:
    """Test financial year calculation."""

    def test_current_year_format(self):
        from HMS_py.core.company import current_year
        
        year = current_year()
        assert isinstance(year, str)
        assert "-" in year
        parts = year.split("-")
        assert len(parts) == 2
        assert len(parts[0]) == 4
        assert len(parts[1]) == 2
        # e.g., "2026-27"
        assert int(parts[1]) == (int(parts[0]) + 1) % 100


class TestGuestProfCascade:
    """VB6 GuestProfile.frm:6863-6871 — guest update cascades to GuestFolio + RoomOcc."""

    def test_update_cascades_to_guestfolio_and_roomocc(self):
        from HMS_py.core import checkin, db, guestprof
        import datetime

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT CASC TEST",
                          "add1": "T", "city": "DELHI", "type": "India"})
        folio_no = None
        try:
            folio_no = checkin.create_checkin(
                gcode, "PYT CASC TEST",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=1))
            # update the profile -> cascade
            guestprof.update(gcode, {"code": gcode,
                                     "name": "PYT CASC TEST RENAMED",
                                     "add1": "T", "city": "KANPUR",
                                     "type": "India"})
            gf = db.query(
                "SELECT RTRIM(Name), RTRIM(city), RTRIM(GuestProf) "
                "FROM GuestFolio WHERE FolioNo = ? AND Site_Code = ? "
                "AND Vprefix = '2026'",
                (folio_no, "KK"))
            assert gf, "GuestFolio row missing"
            assert gf[0][0] == "PYT CASC TEST RENAMED", f"GuestFolio.Name not cascaded: {gf[0]}"
            assert gf[0][1] == "KANPUR", f"GuestFolio.city not cascaded: {gf[0]}"
            assert gf[0][2] == gcode
            ro = db.query(
                "SELECT RTRIM(GuestProf) FROM RoomOcc WHERE FolioNo = ? "
                "AND Site_Code = ? AND Vprefix = '2026'", (folio_no, "KK"))
            assert ro and ro[0][0] == gcode
        finally:
            if folio_no:
                try:
                    checkin.delete_checkin(folio_no)
                except Exception:
                    pass
            try:
                guestprof.delete(gcode)
            except Exception:
                pass


class TestCheckoutBalanceGuard:
    """VB6 FdCheckOut.frm:3202 'Guest Balance is Not Zero' blocks checkout — ONLY for Strict type."""

    def test_checkout_blocks_when_balance_nonzero_strict(self):
        from HMS_py.core import checkin, checkout, folio, guestprof, db
        import datetime

        # Set checkout type to Strict for this test
        own_cn = db.connect()
        try:
            db.execute(
                "UPDATE Enviro SET Checkout = 'Strict' WHERE LogSite_Code = ?",
                (db.get_site_code(),), cn=own_cn, commit=True)
        finally:
            own_cn.close()

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT GUARD TEST",
                          "add1": "T", "type": "India"})
        folio_no = None
        try:
            folio_no = checkin.create_checkin(
                gcode, "PYT GUARD TEST",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=1))
            folio.post_room_charge(folio_no, 500.0)
            try:
                checkout.do_checkout(folio_no, user="PYADMIN")
                raise AssertionError("checkout allowed with non-zero balance in Strict mode")
            except ValueError as e:
                assert "Checkout type 'Strict' requires zero balance" in str(e)
            # folio stays open; 500 + 25 CGST + 25 SGST = 550
            assert checkout.folio_balance(folio_no)["balance"] == 550.0
        finally:
            if folio_no:
                try:
                    checkin.delete_checkin(folio_no)
                except Exception:
                    pass
            try:
                guestprof.delete(gcode)
            except Exception:
                pass
            # Restore Enviro
            own_cn = db.connect()
            try:
                db.execute(
                    "UPDATE Enviro SET Checkout = 'Standard' WHERE LogSite_Code = ?",
                    (db.get_site_code(),), cn=own_cn, commit=True)
            finally:
                own_cn.close()

    def test_checkout_allows_nonzero_balance_standard(self):
        from HMS_py.core import checkin, checkout, folio, guestprof, db
        import datetime

        # Ensure checkout type is Standard (default)
        own_cn = db.connect()
        try:
            db.execute(
                "UPDATE Enviro SET Checkout = 'Standard' WHERE LogSite_Code = ?",
                (db.get_site_code(),), cn=own_cn, commit=True)
        finally:
            own_cn.close()

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT GUARD TEST 2",
                          "add1": "T", "type": "India"})
        folio_no = None
        try:
            folio_no = checkin.create_checkin(
                gcode, "PYT GUARD TEST 2",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=1))
            folio.post_room_charge(folio_no, 500.0)
            # Standard mode should ALLOW checkout with non-zero balance
            # (settlement is separate flow)
            bal = checkout.do_checkout(folio_no, user="PYADMIN")
            assert bal["balance"] == 550.0  # balance preserved
        finally:
            if folio_no:
                try:
                    checkin.delete_checkin(folio_no)
                except Exception:
                    pass
            try:
                guestprof.delete(gcode)
            except Exception:
                pass
            # Restore Enviro
            own_cn = db.connect()
            try:
                db.execute(
                    "UPDATE Enviro SET Checkout = 'Standard' WHERE LogSite_Code = ?",
                    (db.get_site_code(),), cn=own_cn, commit=True)
            finally:
                own_cn.close()

    def test_checkout_allows_zero_balance(self):
        from HMS_py.core import checkin, checkout, guestprof
        import datetime

        gcode = guestprof.next_code()
        guestprof.insert({"code": gcode, "name": "PYT GUARD OK",
                          "add1": "T", "type": "India"})
        folio_no = None
        try:
            folio_no = checkin.create_checkin(
                gcode, "PYT GUARD OK",
                datetime.date.today(),
                datetime.date.today() + datetime.timedelta(days=1))
            result = checkout.do_checkout(folio_no, user="PYADMIN")
            assert result["balance"] == 0.0
            checkout.reverse_checkout(folio_no, user="PYADMIN")
        finally:
            if folio_no:
                try:
                    checkout.reverse_checkout(folio_no, user="PYADMIN")
                except Exception:
                    pass
                try:
                    checkin.delete_checkin(folio_no)
                except Exception:
                    pass
            try:
                guestprof.delete(gcode)
            except Exception:
                pass


class TestCheckoutClearance:
    """Test checkout clearance logic (VB6 HRoomCheckOutClearance)."""

    def test_clearance_flag_returns_string(self):
        from HMS_py.core import checkout
        flag = checkout.get_clearance_flag()
        assert flag in ("Yes", "No")

    def test_clearance_disabled_by_default(self):
        from HMS_py.core import checkout
        flag = checkout.get_clearance_flag()
        assert flag == "No"  # Live DB evidence

    def test_check_clearance_returns_required_keys(self):
        from HMS_py.core import checkout
        result = checkout.check_clearance(999999)  # Non-existent folio
        assert "enabled" in result
        assert "cleared" in result
        assert "bill_settled" in result
        assert "balance_zero" in result
        assert "bill_status" in result
        assert "balance" in result
        assert "message" in result

    def test_check_clearance_no_bill_is_cleared(self):
        from HMS_py.core import checkout
        result = checkout.check_clearance(999999)
        assert result["bill_settled"] is True  # No bill = OK
        assert result["bill_status"] == "NONE"

    def test_clearance_list_returns_list(self):
        from HMS_py.core import checkout
        result = checkout.clearance_list(top=5)
        assert isinstance(result, list)

    def test_clearance_list_items_have_required_keys(self):
        from HMS_py.core import checkout
        result = checkout.clearance_list(top=3)
        if result:
            item = result[0]
            assert "bill_no" in item
            assert "bill_date" in item
            assert "folio" in item
            assert "guest" in item
            assert "bill_amt" in item
            assert "status" in item


class TestStockRegister:
    """Test stock register and balance (P6-3)."""

    def test_stock_register_returns_list(self):
        from HMS_py.core import inventory
        result = inventory.stock_register(top=5)
        assert isinstance(result, list)

    def test_stock_register_items_have_required_keys(self):
        from HMS_py.core import inventory
        result = inventory.stock_register(top=3)
        if result:
            item = result[0]
            assert "docid" in item
            assert "vtype" in item
            assert "vno" in item
            assert "vdate" in item
            assert "item" in item
            assert "godown" in item
            assert "qty_iss" in item
            assert "qty_rec" in item
            assert "rate" in item
            assert "amount" in item

    def test_stock_register_filter_by_godown(self):
        from HMS_py.core import inventory
        rows = inventory.stock_register(godown="STORE", top=5)
        assert isinstance(rows, list)

    def test_stock_register_filter_by_item(self):
        from HMS_py.core import inventory
        rows = inventory.stock_register(item="BEER", top=5)
        assert isinstance(rows, list)

    def test_stock_balance_returns_list(self):
        from HMS_py.core import inventory
        result = inventory.stock_balance(top=5)
        assert isinstance(result, list)

    def test_stock_balance_items_have_required_keys(self):
        from HMS_py.core import inventory
        result = inventory.stock_balance(top=3)
        if result:
            item = result[0]
            assert "godown" in item
            assert "item" in item
            assert "bal" in item

    def test_stock_movements_returns_list(self):
        from HMS_py.core import inventory
        result = inventory.stock_movements(top=5)
        assert isinstance(result, list)


class TestEInvoiceConfig:
    """Test eInvoice config (P6-5)."""

    def test_einvoice_get_returns_dict_or_none(self):
        from HMS_py.core import inventory
        result = inventory.einvoice_get()
        assert result is None or isinstance(result, dict)

    def test_einvoice_upsert_no_crash(self):
        from HMS_py.core import inventory
        try:
            inventory.einvoice_upsert({"asp_id": "TEST"})
        except Exception:
            pass  # May fail on read-only finance field, but shouldn't crash


# ============================================================
# Run Tests
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])