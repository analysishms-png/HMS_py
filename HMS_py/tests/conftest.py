"""Pytest configuration for HMS_py tests."""
import os
import sys
import pytest
from datetime import date, timedelta

# Add the actual project root to path so imports like 'HMS_py.*' resolve.
# __file__ is .../HMS_py/HMS_py/tests/conftest.py, so we need to go up three
# levels to reach the top-level project directory: .../HMS_py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

# Test database connection (uses same config as main app)
from HMS_py.core.db import load_config, connect

@pytest.fixture(scope="session")
def db_config():
    """Load test database configuration."""
    return load_config()

@pytest.fixture(scope="session")
def db_connection(db_config):
    """Create a database connection for the test session."""
    cn = connect(db_config)
    yield cn
    cn.close()

@pytest.fixture(scope="function")
def db_transaction(db_connection):
    """Create a transaction that rolls back after each test."""
    # Start transaction
    cursor = db_connection.cursor()
    cursor.execute("BEGIN TRANSACTION")
    
    yield db_connection
    
    # Rollback
    cursor.execute("ROLLBACK")
    cursor.close()

@pytest.fixture(scope="function")
def clean_db(db_transaction):
    """Provide a clean database state for each test."""
    # Clean up any existing PYT* test data
    from tests.fixtures.test_data import cleanup_test_data
    cleanup_test_data(db_transaction)
    yield db_transaction
    # Cleanup after test
    cleanup_test_data(db_transaction)

# ============================================================
# Core Module Fixtures
# ============================================================

@pytest.fixture
def auth_module():
    from HMS_py.core import auth
    return auth

@pytest.fixture
def company_module():
    from HMS_py.core import company
    return company

@pytest.fixture
def country_module():
    from HMS_py.core import country
    return country

@pytest.fixture
def state_module():
    from HMS_py.core import state
    return state

@pytest.fixture
def city_module():
    from HMS_py.core import city
    return city

@pytest.fixture
def area_module():
    from HMS_py.core import area
    return area

@pytest.fixture
def room_category_module():
    from HMS_py.core import roomcategory
    return roomcategory

@pytest.fixture
def room_master_module():
    from HMS_py.core import roommaster
    return roommaster

@pytest.fixture
def room_status_module():
    from HMS_py.core import roomstatus
    return roomstatus

@pytest.fixture
def guestprof_module():
    from HMS_py.core import guestprof
    return guestprof

@pytest.fixture
def reservation_module():
    from HMS_py.core import reservation
    return reservation

@pytest.fixture
def checkin_module():
    from HMS_py.core import checkin
    return checkin

@pytest.fixture
def checkout_module():
    from HMS_py.core import checkout
    return checkout

@pytest.fixture
def folio_module():
    from HMS_py.core import folio
    return folio

@pytest.fixture
def nightaudit_module():
    from HMS_py.core import nightaudit
    return nightaudit

@pytest.fixture
def pos_module():
    from HMS_py.core import pos
    return pos

@pytest.fixture
def inventory_module():
    from HMS_py.core import inventory
    return inventory

@pytest.fixture
def plans_module():
    from HMS_py.core import plans
    return plans

@pytest.fixture
def taxmaster_module():
    from HMS_py.core import taxmaster
    return taxmaster

@pytest.fixture
def paymenttype_module():
    from HMS_py.core import paymenttype
    return paymenttype

@pytest.fixture
def marketsegment_module():
    from HMS_py.core import marketsegment
    return marketsegment

@pytest.fixture
def businesssource_module():
    from HMS_py.core import businesssource
    return businesssource

@pytest.fixture
def gueststatus_module():
    from HMS_py.core import gueststatus
    return gueststatus

@pytest.fixture
def forexmaster_module():
    from HMS_py.core import forexmaster
    return forexmaster

@pytest.fixture
def ledger_module():
    from HMS_py.core import ledger
    return ledger

@pytest.fixture
def acgroup_module():
    from HMS_py.core import acgroup
    return acgroup

@pytest.fixture
def fixcharge_module():
    from HMS_py.core import fixcharge
    return fixcharge

@pytest.fixture
def unit_module():
    from HMS_py.core import unit
    return unit

@pytest.fixture
def item_module():
    from HMS_py.core import item
    return item

@pytest.fixture
def sundry_module():
    from HMS_py.core import sundry
    return sundry

@pytest.fixture
def narr_module():
    from HMS_py.core import narr
    return narr

@pytest.fixture
def depart_module():
    from HMS_py.core import depart
    return depart

@pytest.fixture
def venue_module():
    from HMS_py.core import venue
    return venue

@pytest.fixture
def packagemaster_module():
    from HMS_py.core import packagemaster
    return packagemaster

@pytest.fixture
def seasonmaster_module():
    from HMS_py.core import seasonmaster
    return seasonmaster

@pytest.fixture
def companymaster_module():
    from HMS_py.core import companymaster
    return companymaster

@pytest.fixture
def banquet_masters_module():
    from HMS_py.core import banquet_masters
    return banquet_masters

@pytest.fixture
def pos_masters_module():
    from HMS_py.core import pos_masters
    return pos_masters

@pytest.fixture
def hr_masters_module():
    from HMS_py.core import hr_masters
    return hr_masters

@pytest.fixture
def members_masters_module():
    from HMS_py.core import members_masters
    return members_masters

@pytest.fixture
def general_setup_module():
    from HMS_py.core import general_setup
    return general_setup

@pytest.fixture
def expenseentry_module():
    from HMS_py.core import expenseentry
    return expenseentry

@pytest.fixture
def reports_module():
    from HMS_py.core import reports
    return reports

# ============================================================
# Test Data Fixtures
# ============================================================

@pytest.fixture
def test_guest():
    from tests.fixtures.test_data import get_test_guest
    return get_test_guest(0)

@pytest.fixture
def test_guests():
    from tests.fixtures.test_data import TEST_GUESTS
    return TEST_GUESTS

@pytest.fixture
def test_room():
    from tests.fixtures.test_data import get_test_room
    return get_test_room(0)

@pytest.fixture
def test_rooms():
    from tests.fixtures.test_data import TEST_ROOMS
    return TEST_ROOMS

@pytest.fixture
def test_room_categories():
    from tests.fixtures.test_data import TEST_ROOM_CATEGORIES
    return TEST_ROOM_CATEGORIES

@pytest.fixture
def test_reservation():
    from tests.fixtures.test_data import get_test_reservation
    return get_test_reservation(0)

@pytest.fixture
def test_reservations():
    from tests.fixtures.test_data import TEST_RESERVATIONS
    return TEST_RESERVATIONS

@pytest.fixture
def test_checkin():
    from tests.fixtures.test_data import get_test_checkin
    return get_test_checkin(0)

@pytest.fixture
def test_checkins():
    from tests.fixtures.test_data import TEST_CHECKINS
    return TEST_CHECKINS

@pytest.fixture
def test_folio_charges():
    from tests.fixtures.test_data import TEST_FOLIO_CHARGES
    return TEST_FOLIO_CHARGES

@pytest.fixture
def test_payments():
    from tests.fixtures.test_data import TEST_PAYMENTS
    return TEST_PAYMENTS

@pytest.fixture
def test_countries():
    from tests.fixtures.test_data import TEST_COUNTRIES
    return TEST_COUNTRIES

@pytest.fixture
def test_states():
    from tests.fixtures.test_data import TEST_STATES
    return TEST_STATES

@pytest.fixture
def test_cities():
    from tests.fixtures.test_data import TEST_CITIES
    return TEST_CITIES

@pytest.fixture
def test_areas():
    from tests.fixtures.test_data import TEST_AREAS
    return TEST_AREAS

@pytest.fixture
def test_companies():
    from tests.fixtures.test_data import TEST_COMPANIES
    return TEST_COMPANIES

@pytest.fixture
def test_market_segments():
    from tests.fixtures.test_data import TEST_MARKET_SEGMENTS
    return TEST_MARKET_SEGMENTS

@pytest.fixture
def test_business_sources():
    from tests.fixtures.test_data import TEST_BUSINESS_SOURCES
    return TEST_BUSINESS_SOURCES

@pytest.fixture
def test_guest_statuses():
    from tests.fixtures.test_data import TEST_GUEST_STATUSES
    return TEST_GUEST_STATUSES

@pytest.fixture
def test_payment_types():
    from tests.fixtures.test_data import TEST_PAYMENT_TYPES
    return TEST_PAYMENT_TYPES

@pytest.fixture
def test_taxes():
    from tests.fixtures.test_data import TEST_TAXES
    return TEST_TAXES

@pytest.fixture
def test_plans():
    from tests.fixtures.test_data import TEST_PLANS
    return TEST_PLANS

@pytest.fixture
def test_users():
    from tests.fixtures.test_data import TEST_USERS
    return TEST_USERS

# ============================================================
# Date Fixtures
# ============================================================

@pytest.fixture
def today():
    return date.today()

@pytest.fixture
def tomorrow():
    return date.today() + timedelta(days=1)

@pytest.fixture
def next_week():
    return date.today() + timedelta(days=7)

@pytest.fixture
def date_range():
    """Return (start, end) for a 3-night stay."""
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=3)
    return start, end

# ============================================================
# Pytest Configuration
# ============================================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no DB)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (with DB)"
    )
    config.addinivalue_line(
        "markers", "database: Database tests (schema, CRUD)"
    )
    config.addinivalue_line(
        "markers", "regression: Full regression tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (>5s)"
    )
    config.addinivalue_line(
        "markers", "vb6_compare: Tests comparing VB6 vs Python behavior"
    )

def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on path."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)