# Test Fixtures for HMS_py
# Deterministic test data - use PYT* prefix for all test records

# ============================================================
# GUEST FIXTURES
# ============================================================
TEST_GUESTS = [
    {
        "code": "PYT-GUEST-001",
        "name": "PYT Test Guest One",
        "add1": "123 Test Street",
        "add2": "Test Area",
        "city": "KK0002",  # INDIA
        "type": "India",
        "phone": "9876543210",
        "mobile": "9876543210",
        "email": "pyt.guest001@test.com",
        "nationality": "INDIAN",
    },
    {
        "code": "PYT-GUEST-002",
        "name": "PYT Test Guest Two",
        "add1": "456 Test Avenue",
        "add2": "Test Colony",
        "city": "KK0002",
        "type": "India",
        "phone": "9876543211",
        "mobile": "9876543211",
        "email": "pyt.guest002@test.com",
        "nationality": "INDIAN",
    },
    {
        "code": "PYT-GUEST-FOREIGN",
        "name": "PYT Foreign Guest",
        "add1": "789 International Blvd",
        "add2": "Diplomatic Enclave",
        "city": "KK0002",
        "type": "Foreign",
        "phone": "+1-555-0001",
        "mobile": "+1-555-0001",
        "email": "pyt.foreign@test.com",
        "nationality": "AMERICAN",
    },
]

# ============================================================
# ROOM FIXTURES
# ============================================================
TEST_ROOMS = [
    {
        "code": "PYT-101",
        "name": "PYT Test Room 101",
        "catcode": "PYT-DLX",  # Deluxe
        "floor": "1",
        "bedtype": "Double",
        "phone": "101",
        "status": "Vacant",
        "smoking": "No",
        "active": "Y",
    },
    {
        "code": "PYT-102",
        "name": "PYT Test Room 102",
        "catcode": "PYT-SUT",  # Suite
        "floor": "1",
        "bedtype": "King",
        "phone": "102",
        "status": "Vacant",
        "smoking": "No",
        "active": "Y",
    },
    {
        "code": "PYT-201",
        "name": "PYT Test Room 201",
        "catcode": "PYT-STD",  # Standard
        "floor": "2",
        "bedtype": "Twin",
        "phone": "201",
        "status": "Vacant",
        "smoking": "Yes",
        "active": "Y",
    },
]

# Room Categories needed for test rooms
TEST_ROOM_CATEGORIES = [
    {"code": "PYT-DLX", "name": "PYT Deluxe", "rate": 5000.00},
    {"code": "PYT-SUT", "name": "PYT Suite", "rate": 10000.00},
    {"code": "PYT-STD", "name": "PYT Standard", "rate": 3000.00},
]

# ============================================================
# RESERVATION FIXTURES
# ============================================================
from datetime import date, timedelta

TODAY = date.today() + timedelta(days=1)  # Avoid today for arrival tests
TEST_RESERVATIONS = [
    {
        "guest_name": "PYT Res Guest 1",
        "arr_date": TODAY + timedelta(days=1),
        "dep_date": TODAY + timedelta(days=3),
        "adults": 2,
        "rooms": 1,
        "rate": 5000.00,
        "remarks": "PYT Test reservation 1",
    },
    {
        "guest_name": "PYT Res Guest 2",
        "arr_date": TODAY + timedelta(days=5),
        "dep_date": TODAY + timedelta(days=7),
        "adults": 1,
        "rooms": 1,
        "rate": 3000.00,
        "remarks": "PYT Test reservation 2",
    },
    {
        "guest_name": "PYT Res Guest 3",
        "arr_date": TODAY + timedelta(days=10),
        "dep_date": TODAY + timedelta(days=12),
        "adults": 3,
        "rooms": 2,
        "rate": 8000.00,
        "remarks": "PYT Test reservation 3 - group",
    },
]

# ============================================================
# CHECK-IN / FOLIO FIXTURES
# ============================================================
TEST_CHECKINS = [
    {
        "guestprof": "PYT-GUEST-001",
        "name": "PYT CheckIn Guest 1",
        "arr_date": TODAY,
        "dep_date": TODAY + timedelta(days=2),
        "city": "KK0002",
        "bookingdocid": "",  # Walk-in
        "roomno": "",  # Auto-assign
    },
    {
        "guestprof": "PYT-GUEST-002",
        "name": "PYT CheckIn Guest 2",
        "arr_date": TODAY,
        "dep_date": TODAY + timedelta(days=1),
        "city": "KK0002",
        "bookingdocid": "",  # Will link after reservation created
        "roomno": "PYT-101",
    },
]

# ============================================================
# FOLIO CHARGES FIXTURES
# ============================================================
TEST_FOLIO_CHARGES = [
    {"paycode": "KKRMCH", "amount": 5000.00, "description": "Room Charge"},
    {"paycode": "KKRMCH", "amount": 3000.00, "description": "Room Charge"},
    {"paycode": "KKFOOD", "amount": 1500.00, "description": "Restaurant"},
    {"paycode": "KKTELE", "amount": 200.00, "description": "Telephone"},
    {"paycode": "KKLAUN", "amount": 500.00, "description": "Laundry"},
]

# ============================================================
# PAYMENT FIXTURES
# ============================================================
TEST_PAYMENTS = [
    {"paycode": "KKCASH", "amount": 5000.00, "mode": "Cash"},
    {"paycode": "KKCARD", "amount": 3000.00, "mode": "Credit Card"},
    {"paycode": "KKUPI", "amount": 2000.00, "mode": "UPI"},
]

# ============================================================
# MASTER DATA FIXTURES (for lookups)
# ============================================================
TEST_COUNTRIES = [
    {"code": "PYT-IND", "name": "PYT India", "short": "IND", "type": "India", "nationality": "Indian"},
    {"code": "PYT-USA", "name": "PYT United States", "short": "USA", "type": "Foreign", "nationality": "American"},
]

TEST_STATES = [
    {"code": "PYT-MH", "name": "PYT Maharashtra", "short": "MH", "country": "PYT-IND"},
    {"code": "PYT-DL", "name": "PYT Delhi", "short": "DL", "country": "PYT-IND"},
]

TEST_CITIES = [
    {"code": "PYT-MUM", "name": "PYT Mumbai", "short": "BOM", "zip": "400001", "state": "PYT-MH"},
    {"code": "PYT-DEL", "name": "PYT Delhi", "short": "DEL", "zip": "110001", "state": "PYT-DL"},
]

TEST_AREAS = [
    {"code": "PYT-AND", "name": "PYT Andheri", "city": "PYT-MUM"},
    {"code": "PYT-CPR", "name": "PYT Connaught Place", "city": "PYT-DEL"},
]

TEST_COMPANIES = [
    {"code": "PYT-CORP", "name": "PYT Corporation", "short": "PYTC", "contact": "Test Contact", "phone": "9999999999"},
    {"code": "PYT-AGNT", "name": "PYT Travel Agent", "short": "PYTA", "contact": "Agent Contact", "phone": "8888888888"},
]

TEST_MARKET_SEGMENTS = [
    {"code": "PYT-CORP", "name": "PYT Corporate"},
    {"code": "PYT-LEIS", "name": "PYT Leisure"},
    {"code": "PYT-GOVT", "name": "PYT Government"},
]

TEST_BUSINESS_SOURCES = [
    {"code": "PYT-WEB", "name": "PYT Website"},
    {"code": "PYT-WALK", "name": "PYT Walk-in"},
    {"code": "PYT-AGNT", "name": "PYT Agent"},
]

TEST_GUEST_STATUSES = [
    {"code": "PYT-VIP", "name": "PYT VIP"},
    {"code": "PYT-REG", "name": "PYT Regular"},
    {"code": "PYT-NEW", "name": "PYT New"},
]

TEST_PAYMENT_TYPES = [
    {"code": "PYT-CSH", "name": "PYT Cash", "type": "Cash"},
    {"code": "PYT-CRD", "name": "PYT Credit Card", "type": "Card"},
    {"code": "PYT-UPI", "name": "PYT UPI", "type": "Digital"},
]

TEST_TAXES = [
    {"code": "PYT-GST", "name": "PYT GST 18%", "taxper": 18.0, "taxtype": "GST", "onamount": "No", "active": "Y"},
    {"code": "PYT-CGS", "name": "PYT CGST 9%", "taxper": 9.0, "taxtype": "CGST", "onamount": "No", "active": "Y"},
    {"code": "PYT-SGS", "name": "PYT SGST 9%", "taxper": 9.0, "taxtype": "SGST", "onamount": "No", "active": "Y"},
]

TEST_PLANS = [
    {"code": "PYT-CP", "name": "PYT Continental Plan", "total": 1000.0, "package": "CP"},
    {"code": "PYT-MAP", "name": "PYT Modified American Plan", "total": 2000.0, "package": "MAP"},
    {"code": "PYT-AP", "name": "PYT American Plan", "total": 3000.0, "package": "AP"},
]

# ============================================================
# USER FIXTURES
# ============================================================
TEST_USERS = [
    {"username": "PYT-ADMIN", "label": "PYT Administrator", "short": "ADMIN", "active": "Y", "password": "test123"},
    {"username": "PYT-FRONT", "label": "PYT Front Desk", "short": "FRONT", "active": "Y", "password": "test123"},
    {"username": "PYT-MGR", "label": "PYT Manager", "short": "MGR", "active": "Y", "password": "test123"},
    {"username": "PYT-INACTIVE", "label": "PYT Inactive User", "short": "INACT", "active": "N", "password": "test123"},
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_test_guest(index=0):
    """Get a test guest by index."""
    return TEST_GUESTS[index % len(TEST_GUESTS)]

def get_test_room(index=0):
    """Get a test room by index."""
    return TEST_ROOMS[index % len(TEST_ROOMS)]

def get_test_reservation(index=0):
    """Get a test reservation by index."""
    return TEST_RESERVATIONS[index % len(TEST_RESERVATIONS)]

def get_test_checkin(index=0):
    """Get a test check-in by index."""
    return TEST_CHECKINS[index % len(TEST_CHECKINS)]

def cleanup_test_data(cn=None):
    """Clean up all PYT* test data from database.
    Run after test suite to maintain clean state.
    """
    from HMS_py.core import db
    
    # Delete in reverse dependency order
    tables = [
        ("BookingCancelDetails", "BookingDocID"),
        ("Booking", "GuestName"),
        ("GuestFolio", "Name"),
        ("RoomOcc", "RoomNo"),  # RoomNo like PYT-*
        ("PayCharge", "Comments"),
        ("FOMBillDetails", "Guestname"),
        ("FolioLog", "U_Name"),
        ("BookingLog", "U_Name"),
        ("GuestProf", "Code"),
        ("RoomMast", "RoomNo"),
        ("RoomCatMast", "Code"),
        ("UserMast", "USER_NAME"),
        ("Country", "Code"),
        ("State", "Code"),
        ("City", "CityCode"),
        ("AreaMast", "AreaCODE"),
        ("CompanyMast", "Code"),
        ("PlanMast", "Code"),
        ("TaxMast", "TaxCode"),
        ("PaymentTypeMast", "Code"),
        ("MarketSegment", "Code"),
        ("BusinessSource", "Code"),
        ("GuestStatus", "Code"),
    ]
    
    for table, name_col in tables:
        try:
            db.execute(
                f"DELETE FROM {table} WHERE {name_col} LIKE 'PYT%'",
                cn=cn, commit=True
            )
        except Exception:
            pass  # Table might not exist or column different