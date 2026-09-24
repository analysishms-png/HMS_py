"""URL percent-encoding helpers (VB6 Functions.bas port).

Thin stdlib urllib.parse wrappers so SMS/eInvoice callers have a single
import for encode/decode. Pure functions; no DB, no GUI.
"""
from __future__ import annotations

from urllib.parse import quote_plus, unquote_plus


def encode_url(value) -> str:
    """Percent-encode a value for query strings (VB6 URL-encode; space -> '+')."""
    if value is None:
        return ""
    return quote_plus(str(value), safe="")


def decode_url(value) -> str:
    """Decode a percent-encoded value ('+' treated as space)."""
    if value is None:
        return ""
    return unquote_plus(str(value))
