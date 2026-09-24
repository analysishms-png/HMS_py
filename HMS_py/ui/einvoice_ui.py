"""E-Invoice UI Module."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional


def generate_einvoice(parent=None, doc_id: str = "",
                       guest_name: str = "",
                       amount: float = 0.0) -> dict:
    """Generate an e-invoice."""
    from HMS_py.core.einvoice import EInvoiceGenerator
    gen = EInvoiceGenerator(mock=True)
    if doc_id and guest_name and amount > 0:
        return gen.generate_invoice(doc_id, guest_name, amount)
    return {"error": "Missing required fields"}


def open_einvoice_browser(parent=None) -> str:
    """Open e-invoice browser."""
    from HMS_py.core.einvoice import generate_einvoice_report
    # Get recent invoices (mock data for now)
    return generate_einvoice_report([])


if __name__ == "__main__":
    import sys
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    result = generate_einvoice(doc_id="RES20260001",
                                guest_name="Test Guest",
                                amount=3000.00)
    print(result)
