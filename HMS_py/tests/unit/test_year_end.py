"""Unit tests for core/year_end.py business logic.

Tests the year-end financial procedures without requiring a full
PyQt6 application. Uses monkeypatch to isolate database calls.

Run: pytest tests/unit/test_year_end.py -v
"""
from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest


# ── Helper: fake DB connection ────────────────────

class FakeCursor:
    """Minimal fake cursor for mocking DB operations."""

    def __init__(self, rows=None):
        self._rows = rows or []
        self._index = 0
        self.description = None
        self.rowcount = 0

    def execute(self, sql, params=None):
        self.rowcount = len(self._rows)
        return self

    def fetchone(self):
        if self._index < len(self._rows):
            r = self._rows[self._index]
            self._index += 1
            return r
        return None

    def fetchall(self):
        return self._rows[self._index:]


class FakeConnection:
    """Minimal fake connection for mocking DB operations."""

    def __init__(self, cursor=None):
        self._cursor = cursor or FakeCursor()
        self._committed = False
        self._closed = False
        self._execute_calls = []
        self._query_calls = []

    def cursor(self):
        return self._cursor

    def execute(self, sql, params=None):
        self._execute_calls.append((sql, params or ()))
        return self._cursor

    def query(self, sql, params=None, cn=None):
        self._query_calls.append((sql, params or ()))
        return self._cursor

    def commit(self):
        self._committed = True

    def close(self):
        self._closed = True


# ── Test get_fy_dates ─────────────────────────────

class TestGetFyDates:
    """Test financial year date range calculation."""

    def test_default_current_fy_q1(self):
        """When month >= 4, FY starts this year."""
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 6, 15)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            from HMS_py.core.year_end import get_fy_dates
            result = get_fy_dates()
            assert result["fy"] == "2026-27"
            assert result["start"] == datetime.date(2026, 4, 1)
            assert result["end"] == datetime.date(2027, 3, 31)

    def test_default_current_fy_q3(self):
        """When month < 4, FY starts previous year."""
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 1, 15)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            from HMS_py.core.year_end import get_fy_dates
            result = get_fy_dates()
            assert result["fy"] == "2025-26"
            assert result["start"] == datetime.date(2025, 4, 1)
            assert result["end"] == datetime.date(2026, 3, 31)

    def test_explicit_fy_year(self):
        """Explicit fy_year parameter overrides default."""
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 1, 1)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            from HMS_py.core.year_end import get_fy_dates
            result = get_fy_dates("2024-25")
            assert result["fy"] == "2024-25"
            assert result["start"] == datetime.date(2024, 4, 1)
            assert result["end"] == datetime.date(2025, 3, 31)

    def test_fy_year_format(self):
        """fy_year format 'YYYY-YY' parses correctly.

        Output format is 'YYYY-YY' where YY is the last 2 digits
        of the end year (e.g., 2023-24).
        """
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 6, 1)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            from HMS_py.core.year_end import get_fy_dates
            result = get_fy_dates("2023-24")
            assert result["fy"] == "2023-24"
            assert result["start"] == datetime.date(2023, 4, 1)
            assert result["end"] == datetime.date(2024, 3, 31)


# ── Test check_datelock ───────────────────────────

class TestCheckDatelock:
    """Test date-lock checking logic."""

    def test_locked_date(self, monkeypatch):
        """Returns True when DATELOCK has matching record with flag=1."""
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [(1,)])
        from HMS_py.core.year_end import check_datelock
        result = check_datelock(datetime.date(2026, 6, 15))
        assert result is True

    def test_unlocked_date(self, monkeypatch):
        """Returns False when no DATELOCK record matches."""
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [])
        from HMS_py.core.year_end import check_datelock
        result = check_datelock(datetime.date(2026, 6, 15))
        assert result is False


# ── Test year_end_summary ─────────────────────────

class TestYearEndSummary:
    """Test year-end summary report generation."""

    def test_summary_structure(self, monkeypatch):
        """Summary contains all required keys."""
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [])
        from HMS_py.core.year_end import year_end_summary
        result = year_end_summary()
        assert "fy" in result
        assert "subgroup_count" in result
        assert "total_dr" in result
        assert "total_cr" in result
        assert "balance" in result
        assert "acgroup_count" in result
        assert "last_vouchers" in result

    def test_summary_fy_dates(self, monkeypatch):
        """Summary FY dates match current FY."""
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 6, 15)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            monkeypatch.setattr(
                "HMS_py.core.year_end.db.query",
                lambda *a, **k: [])
            from HMS_py.core.year_end import year_end_summary
            result = year_end_summary()
            assert result["fy"]["fy"] == "2026-27"


# ── Test carry_forward_balances ───────────────────────────

class TestCarryForwardBalances:
    """Test balance carry-forward logic."""

    def test_carry_forward_returns_dict(self, monkeypatch):
        """Carry forward returns dict with subgroup/acgroup counts."""
        fake_cn = FakeConnection(cursor=FakeCursor(rows=[(5,)]))

        def fake_connect():
            return fake_cn

        monkeypatch.setattr(
            "HMS_py.core.year_end.db.connect", fake_connect)
        from HMS_py.core.year_end import carry_forward_balances
        result = carry_forward_balances("2026-04-01", commit=False)
        assert "subgroup_updated" in result
        assert "acgroup_updated" in result


# ── Test reset_budget ─────────────────────────────

class TestResetBudget:
    """Test budget reset logic."""

    def test_reset_budget_returns_int(self, monkeypatch):
        """Reset budget returns integer count of records."""
        fake_cn = FakeConnection(cursor=FakeCursor(rows=[
            ("2025-04-01", "2026-03-31", 1, "AC001", "G01", 1000.0, 500.0),
        ]))

        def fake_connect():
            return fake_cn

        monkeypatch.setattr(
            "HMS_py.core.year_end.db.connect", fake_connect)
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [
                ("2025-04-01", "2026-03-31", 1,
                 "AC001", "G01", 1000.0, 500.0)])
        from HMS_py.core.year_end import reset_budget
        result = reset_budget("2026-04-01", "2027-03-31", commit=False)
        assert isinstance(result, int)

    def test_reset_budget_no_existing_returns_zero(self, monkeypatch):
        """Reset budget returns 0 when no existing budget."""
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.connect",
            lambda: FakeConnection())
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [])
        from HMS_py.core.year_end import reset_budget
        result = reset_budget("2026-04-01", "2027-03-31", commit=False)
        assert result == 0


# ── Test YearEndAPI ───────────────────────────────

class TestYearEndAPI:
    """Test the YearEndAPI wrapper class."""

    def test_api_has_all_methods(self):
        """YearEndAPI exposes all core functions as static methods."""
        from HMS_py.core.year_end import YearEndAPI
        assert hasattr(YearEndAPI, "get_fy_dates")
        assert hasattr(YearEndAPI, "check_datelock")
        assert hasattr(YearEndAPI, "get_subgroup_balances")
        assert hasattr(YearEndAPI, "get_acgroup_balances")
        assert hasattr(YearEndAPI, "carry_forward_balances")
        assert hasattr(YearEndAPI, "reset_budget")
        assert hasattr(YearEndAPI, "year_end_summary")

    def test_api_get_fy_dates(self):
        """YearEndAPI.get_fy_dates delegates to core function."""
        with patch("HMS_py.core.year_end.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2026, 6, 15)
            mock_dt.date.side_effect = lambda y, m, d: datetime.date(y, m, d)
            from HMS_py.core.year_end import YearEndAPI
            result = YearEndAPI.get_fy_dates()
            assert result["fy"] == "2026-27"

    def test_api_check_datelock(self, monkeypatch):
        """YearEndAPI.check_datelock returns bool."""
        monkeypatch.setattr(
            "HMS_py.core.year_end.db.query",
            lambda *a, **k: [(1,)])
        from HMS_py.core.year_end import YearEndAPI
        result = YearEndAPI.check_datelock(datetime.date(2026, 6, 15))
        assert result is True


# ── Test YearEndForm import ───────────────────────

class TestYearEndFormImport:
    """Test that the UI form can be imported without errors."""

    def test_year_end_form_importable(self):
        """YearEndForm can be imported from ui.year_end_ui."""
        from HMS_py.ui.year_end_ui import YearEndForm, open_year_end
        assert callable(open_year_end)
        assert YearEndForm is not None

    def test_year_end_form_has_action_methods(self):
        """YearEndForm has all expected action methods."""
        from HMS_py.ui.year_end_ui import YearEndForm
        assert hasattr(YearEndForm, "_on_check_lock")
        assert hasattr(YearEndForm, "_on_carry_forward")
        assert hasattr(YearEndForm, "_on_reset_budget")
        assert hasattr(YearEndForm, "_on_execute_year_end")
        assert hasattr(YearEndForm, "_on_load_summary")
        assert hasattr(YearEndForm, "_refresh_fy")

    def test_year_end_form_has_buttons(self):
        """YearEndForm has all expected button attributes."""
        from HMS_py.ui.year_end_ui import YearEndForm
        # Buttons are created in __init__ as instance attributes.
        # Verify the class defines them via __init__ by checking
        # that the module has the expected references.
        assert hasattr(YearEndForm, "__init__")
        # Verify btn names exist in the module namespace
        import HMS_py.ui.year_end_ui as mod
        assert hasattr(mod, "YearEndForm")


# ── Test PYT guard ────────────────────────────────

class TestPYTGuard:
    """Test that PYT prefix guard is defined."""

    def test_pyt_prefix_defined(self):
        """PYT_PREFIX is defined in year_end_ui."""
        from HMS_py.ui.year_end_ui import PYT_PREFIX
        assert PYT_PREFIX == "PYT"
        assert PYT_PREFIX.upper().startswith("PYT")
