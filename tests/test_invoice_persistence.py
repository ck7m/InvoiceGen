import os
import datetime
from decimal import Decimal
import pytest
from src.domain.models import Invoice, InvoiceItem, Customer, CompanySettings
from src.db.repository import InvoiceRepository
from src.services.numbering import InvoiceNumberService, get_current_financial_year

def test_financial_year_calculation():
    # April 2026 -> 2026-27
    d1 = datetime.date(2026, 4, 1)
    assert get_current_financial_year(d1) == "2026-27"

    # August 2026 -> 2026-27
    d2 = datetime.date(2026, 8, 16)
    assert get_current_financial_year(d2) == "2026-27"

    # March 2027 -> 2026-27
    d3 = datetime.date(2027, 3, 31)
    assert get_current_financial_year(d3) == "2026-27"

    # April 2027 -> 2027-28
    d4 = datetime.date(2027, 4, 1)
    assert get_current_financial_year(d4) == "2027-28"

    # January 2026 -> 2025-26
    d5 = datetime.date(2026, 1, 15)
    assert get_current_financial_year(d5) == "2025-26"

def test_invoice_auto_numbering():
    d = datetime.date(2026, 8, 16)
    
    # First invoice in empty system
    first_num = InvoiceNumberService.generate_next_number([], prefix="SKN", dt=d)
    assert first_num == "SKN/2026-27/001"

    # Next invoice when existing numbers present
    existing = ["SKN/2026-27/001", "SKN/2026-27/002", "SKN/2025-26/050"]
    next_num = InvoiceNumberService.generate_next_number(existing, prefix="SKN", dt=d)
    assert next_num == "SKN/2026-27/003"

    # Handles gaps and custom strings
    existing_with_gaps = ["SKN/2026-27/005", "CUSTOM_INV_123"]
    next_num_gap = InvoiceNumberService.generate_next_number(existing_with_gaps, prefix="SKN", dt=d)
    assert next_num_gap == "SKN/2026-27/006"

def test_invoice_persistence_and_history(tmp_path):
    db_file = str(tmp_path / "persistence_test.db")
    repo = InvoiceRepository(db_path=db_file)

    # Save invoice 1
    inv1 = Invoice(
        invoice_number="SKN/2026-27/001",
        invoice_date="2026-08-16",
        customer=Customer(customer_name="Apollo Hospitals", customer_address="Main Road, Guntur"),
        items=[
            InvoiceItem(
                serial_number=1,
                description="Network Switch 24-Port",
                hsn_sac="85176290",
                quantity=Decimal("2.00"),
                rate=Decimal("15000.00"),
                cgst_percent=Decimal("9.00"),
                sgst_percent=Decimal("9.00"),
            )
        ],
    )
    id1 = repo.save_invoice(inv1)
    assert id1 > 0

    # Save invoice 2
    inv2 = Invoice(
        invoice_number="SKN/2026-27/002",
        invoice_date="2026-08-17",
        customer=Customer(customer_name="Grand Cyber Tech", customer_address="IT Park, Vijayawada"),
        items=[
            InvoiceItem(
                serial_number=1,
                description="Fiber Patch Cable 10m",
                hsn_sac="85444299",
                quantity=Decimal("5.00"),
                rate=Decimal("1200.00"),
                cgst_percent=Decimal("9.00"),
                sgst_percent=Decimal("9.00"),
            )
        ],
    )
    id2 = repo.save_invoice(inv2)
    assert id2 > 0

    # List all invoices
    invoices = repo.list_invoices()
    assert len(invoices) == 2
    assert invoices[0]["invoice_number"] == "SKN/2026-27/002"  # ordered by ID desc
    assert invoices[1]["invoice_number"] == "SKN/2026-27/001"
    assert invoices[0]["item_count"] == 1

    # Search by customer name
    results = repo.list_invoices(search_query="Apollo")
    assert len(results) == 1
    assert results[0]["customer_name"] == "Apollo Hospitals"

    # Search by invoice number
    results = repo.list_invoices(search_query="002")
    assert len(results) == 1
    assert results[0]["invoice_number"] == "SKN/2026-27/002"

    # Get all registered invoice numbers
    all_numbers = repo.get_all_invoice_numbers()
    assert "SKN/2026-27/001" in all_numbers
    assert "SKN/2026-27/002" in all_numbers

    # Reopen invoice 1
    loaded_inv1 = repo.get_invoice_by_number("SKN/2026-27/001")
    assert loaded_inv1 is not None
    assert loaded_inv1.customer.customer_name == "Apollo Hospitals"
    assert len(loaded_inv1.items) == 1
    assert loaded_inv1.items[0].description == "Network Switch 24-Port"
    assert loaded_inv1.grand_total == Decimal("35400.00")

    # Delete invoice 1
    deleted = repo.delete_invoice("SKN/2026-27/001")
    assert deleted is True

    # Verify deleted
    assert repo.get_invoice_by_number("SKN/2026-27/001") is None
    assert len(repo.list_invoices()) == 1
